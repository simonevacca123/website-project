"""Prove del pacchetto e del trasferimento senza connessioni all'hosting reale."""

import ftplib
import json
from pathlib import Path
import posixpath
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import deploy_site as deploy


class MemoryFTP:
    def __init__(self, files):
        self.files = dict(files)
        self.directories = {'/'}
        for name in files:
            parent = posixpath.dirname(name)
            while parent != '/':
                self.directories.add(parent)
                parent = posixpath.dirname(parent)
        self.current = '/'
        self.writes = []
        self.upload_count = 0
        self.fail_upload = None

    def path(self, name):
        return posixpath.normpath(posixpath.join(self.current, name))

    def pwd(self):
        return self.current

    def cwd(self, name):
        target = self.path(name)
        if target not in self.directories:
            raise ftplib.error_perm('550 Directory unavailable')
        self.current = target

    def mlsd(self):
        names = set()
        for name in set(self.files) | self.directories:
            if name != self.current and posixpath.dirname(name) == self.current:
                names.add(posixpath.basename(name))
        return [(name, {}) for name in sorted(names)]

    def retrbinary(self, command, callback):
        callback(self.files[self.path(command.removeprefix('RETR '))])

    def storbinary(self, command, stream):
        self.upload_count += 1
        if self.upload_count == self.fail_upload:
            self.fail_upload = None
            raise OSError('Test: transfer interrupted')
        target = self.path(command.removeprefix('STOR '))
        self.files[target] = stream.read()
        self.writes.append(('upload', target))

    def rename(self, source, target):
        self.files[self.path(target)] = self.files.pop(self.path(source))
        self.writes.append(('rename', self.path(target)))

    def delete(self, name):
        if not name.startswith('.sv-upload-'):
            raise AssertionError('Tentativo di cancellare un file non temporaneo')
        if self.path(name) not in self.files:
            raise ftplib.error_perm('550 File unavailable')
        del self.files[self.path(name)]

    def mkd(self, name):
        self.directories.add(self.path(name))


class DeploymentTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.output = self.root / 'dist'
        self.backup = self.root / 'backup'
        self.source.mkdir()
        (self.source / 'assets').mkdir()
        for name in deploy.PUBLIC_FILES:
            (self.source / name).write_text('<html>Simone Vacca</html>' if name == 'index.html' else 'new ' + name)
        (self.source / 'assets/favicon.svg').write_text('<svg/>')
        self.release = deploy.build_release(self.source, self.output, 'a' * 40)
        self.old_files = {
            '/www.simonevacca.it/index.html': b'<html><title>Simone Vacca</title>old</html>',
            '/www.simonevacca.it/style.css': b'old css',
            '/www.simonevacca.it/app.js': b'old js',
            '/www.simonevacca.it/contenuti.js': b'old config',
            '/www.simonevacca.it/assets/favicon.svg': b'<svg>old</svg>',
            '/www.simonevacca.it/unrelated.txt': b'must remain',
        }
        self.ftp = MemoryFTP(self.old_files)
        self.remote_root = '/www.simonevacca.it'

    def prepare_backup(self):
        deploy.locate_root(self.ftp, '', 'https://www.simonevacca.it')
        return deploy.backup_site(self.ftp, self.release, self.backup)

    def test_build_only_public_files_and_repeatable(self):
        (self.source / '.env').write_text('EXAMPLE=not-for-publication')
        (self.source / 'README.md').write_text('internal guide')
        again = deploy.build_release(self.source, self.output, 'a' * 40)
        self.assertEqual(again, self.release)
        names = {p.relative_to(self.output / 'site').as_posix() for p in (self.output / 'site').rglob('*') if p.is_file()}
        self.assertEqual(names, set(deploy.PUBLIC_FILES) | {'assets/favicon.svg'})
        self.assertEqual(deploy.load_release(self.output), self.release)

    def test_asset_secrets_and_symbolic_links_rejected(self):
        for name in ['.env', 'private.key', 'notes.md']:
            with self.subTest(name=name):
                target = self.source / 'assets' / name
                target.write_text('example')
                with self.assertRaises(deploy.DeployError):
                    deploy.build_release(self.source, self.output, 'a' * 40)
                target.unlink()
        (self.source / 'assets/link.svg').symlink_to(self.source / 'index.html')
        with self.assertRaises(deploy.DeployError):
            deploy.build_release(self.source, self.output, 'a' * 40)

    def test_lab_publication_is_explicit_and_complete(self):
        (self.source / 'lab').mkdir()
        (self.source / 'lab/index.html').write_text('<html>Laboratorio</html>')
        with self.assertRaises(deploy.DeployError):
            deploy.build_release(self.source, self.output, 'a' * 40)
        (self.source / 'lab/lab.js').write_text('console.log("lab");')
        (self.source / 'lab/private.txt').write_text('internal notes')
        manifest = deploy.build_release(self.source, self.output, 'a' * 40)
        self.assertTrue(set(deploy.LAB_FILES).issubset(manifest['files']))
        self.assertNotIn('lab/private.txt', manifest['files'])

    def test_path_traversal_and_private_paths_rejected(self):
        for name in ['../index.html', '/index.html', 'assets/../.env', 'assets/secret.pem', 'README.md', 'assets/a\n.svg']:
            with self.subTest(name=name), self.assertRaises(deploy.DeployError):
                deploy.public_path(name)

    def test_detects_existing_site_without_guessing(self):
        root = deploy.locate_root(self.ftp, '', 'https://www.simonevacca.it')
        self.assertEqual(root, self.remote_root)
        self.assertFalse(self.ftp.writes)

    def test_ambiguous_or_foreign_site_is_refused(self):
        self.ftp.files['/index.html'] = b'<html>Simone Vacca duplicate</html>'
        with self.assertRaises(deploy.DeployError):
            deploy.locate_root(self.ftp, '', 'https://www.simonevacca.it')
        self.ftp.files[self.remote_root + '/index.html'] = b'<html>Another website</html>'
        with self.assertRaises(deploy.DeployError):
            deploy.locate_root(self.ftp, self.remote_root, 'https://www.simonevacca.it')

    def test_backup_is_complete_and_read_only(self):
        manifest = self.prepare_backup()
        self.assertEqual(self.ftp.files, self.old_files)
        self.assertFalse(self.ftp.writes)
        self.assertEqual(set(manifest['files']), set(self.release['files']))
        self.assertEqual(deploy.load_backup(self.backup), manifest)
        self.assertEqual((self.backup / 'files/style.css').read_bytes(), b'old css')
        with self.assertRaises(deploy.DeployError):
            deploy.backup_site(self.ftp, self.release, self.backup)

    def test_backup_read_failure_cannot_be_used_to_deploy(self):
        self.ftp.cwd(self.remote_root)
        with patch.object(self.ftp, 'retrbinary', side_effect=ftplib.error_perm('550 Read denied')):
            with self.assertRaises(ftplib.error_perm):
                deploy.backup_site(self.ftp, self.release, self.backup)
        self.assertFalse((self.backup / 'manifest.json').exists())
        self.assertFalse(self.ftp.writes)

    def test_deploy_verifies_files_and_updates_index_last(self):
        self.prepare_backup()
        deploy.deploy_release(self.ftp, self.output, self.backup)
        for name in self.release['files']:
            self.assertEqual(self.ftp.files[self.remote_root + '/' + name], (self.output / 'site' / name).read_bytes())
        self.assertEqual(self.ftp.files[self.remote_root + '/unrelated.txt'], b'must remain')
        renamed = [path for operation, path in self.ftp.writes if operation == 'rename']
        self.assertEqual(renamed[-1], self.remote_root + '/index.html')
        self.assertFalse(any('.sv-upload-' in p for p in self.ftp.files))

    def test_interrupted_upload_restores_previous_files(self):
        self.prepare_backup()
        self.ftp.fail_upload = 3
        with self.assertRaises(OSError):
            deploy.deploy_release(self.ftp, self.output, self.backup)
        self.assertEqual(self.ftp.files, self.old_files)

    def test_remote_edit_after_backup_blocks_all_writes(self):
        self.prepare_backup()
        self.ftp.files[self.remote_root + '/style.css'] = b'changed externally'
        with self.assertRaises(deploy.DeployError):
            deploy.deploy_release(self.ftp, self.output, self.backup)
        self.assertFalse(self.ftp.writes)

    def test_corrupt_backup_or_release_blocks_writes(self):
        self.prepare_backup()
        (self.backup / 'files/style.css').write_bytes(b'damaged')
        with self.assertRaises(deploy.DeployError):
            deploy.deploy_release(self.ftp, self.output, self.backup)
        (self.backup / 'files/style.css').write_bytes(b'old css')
        (self.output / 'site/app.js').write_bytes(b'damaged')
        with self.assertRaises(deploy.DeployError):
            deploy.deploy_release(self.ftp, self.output, self.backup)
        self.assertFalse(self.ftp.writes)

    def test_missing_assets_are_created_without_deleting_old_content(self):
        del self.ftp.files[self.remote_root + '/assets/favicon.svg']
        self.ftp.directories.remove(self.remote_root + '/assets')
        manifest = self.prepare_backup()
        self.assertIsNone(manifest['files']['assets/favicon.svg'])
        deploy.deploy_release(self.ftp, self.output, self.backup)
        self.assertEqual(self.ftp.files[self.remote_root + '/assets/favicon.svg'], b'<svg/>')
        deploy.restore_site(self.ftp, manifest, self.backup)
        self.assertEqual(self.ftp.files[self.remote_root + '/index.html'], self.old_files[self.remote_root + '/index.html'])
        self.assertIn(self.remote_root + '/assets/favicon.svg', self.ftp.files)

    def test_missing_credentials_stop_before_connection(self):
        with patch.dict(deploy.os.environ, {}, clear=True), patch.object(deploy, 'SessionReuseFTP') as client:
            with self.assertRaises(deploy.DeployError):
                with deploy.connection():
                    pass
            client.assert_not_called()


if __name__ == '__main__':
    unittest.main()
