"""Integrazione con un server FTPS locale e certificati verificati, non Aruba."""

from datetime import datetime, timedelta, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import logging
from pathlib import Path
import secrets
import shutil
import ssl
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch
from urllib.request import urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import deploy_site as deploy

try:
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import TLS_FTPHandler
    from pyftpdlib.ioloop import IOLoop
    from pyftpdlib.servers import FTPServer
    HAS_SERVER = True
except ImportError:
    HAS_SERVER = False


@unittest.skipUnless(HAS_SERVER, 'Installa requirements-test.txt per le prove FTPS locali')
class RealFTPSIntegration(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        remote = self.root / 'remote'
        web = remote / 'www.simonevacca.it'
        (web / 'assets').mkdir(parents=True)
        (web / 'index.html').write_text('<html>Simone Vacca, old version</html>')
        (web / 'keep.txt').write_text('external file, keep unchanged')
        source = self.root / 'source'
        (source / 'assets').mkdir(parents=True)
        for name in deploy.PUBLIC_FILES:
            (source / name).write_text('<html>Simone Vacca, new version</html>' if name == 'index.html' else 'new ' + name)
        (source / 'assets/favicon.svg').write_text('<svg/>')
        self.output, self.backup = self.root / 'dist', self.root / 'backup'
        self.release = deploy.build_release(source, self.output, 'b' * 40)
        self.web = web

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, 'localhost')])
        now = datetime.now(timezone.utc)
        certificate = (x509.CertificateBuilder().subject_name(subject).issuer_name(subject)
                       .public_key(key.public_key()).serial_number(x509.random_serial_number())
                       .not_valid_before(now - timedelta(minutes=1)).not_valid_after(now + timedelta(hours=1))
                       .add_extension(x509.SubjectAlternativeName([x509.DNSName('localhost')]), critical=False)
                       .sign(key, hashes.SHA256()))
        cert_path, key_path = self.root / 'server.crt', self.root / 'server.key'
        cert_path.write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
        key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        self.context = ssl.create_default_context(cafile=str(cert_path))
        self.cert_path, self.key_path = cert_path, key_path
        self.username, self.password = 'local-test', secrets.token_urlsafe(24)
        authorizer = DummyAuthorizer()
        authorizer.add_user(self.username, self.password, str(remote), perm='elradfmwMT')

        class Handler(TLS_FTPHandler):
            def log(self, *_args, **_kwargs):
                pass

        Handler.authorizer = authorizer
        Handler.certfile, Handler.keyfile = str(cert_path), str(key_path)
        Handler.tls_control_required = Handler.tls_data_required = True
        logging.getLogger('pyftpdlib').setLevel(logging.CRITICAL)
        self.loop = IOLoop()
        self.server = FTPServer(('127.0.0.1', 0), Handler, ioloop=self.loop)
        logging.getLogger('pyftpdlib').setLevel(logging.CRITICAL)
        self.port = self.server.socket.getsockname()[1]
        self.thread = Thread(target=self.server.serve_forever, kwargs={'timeout': .05, 'handle_exit': False}, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)

    def stop_server(self):
        self.server.close_all()
        self.thread.join(timeout=5)
        self.loop.close()

    def connect(self, context):
        ftp = deploy.SessionReuseFTP(context=context, timeout=5)
        self.addCleanup(ftp.close)
        ftp.connect('localhost', self.port)
        ftp.auth()
        ftp.login(self.username, self.password)
        ftp.prot_p()
        return ftp

    def test_backup_publish_and_restore_over_verified_tls(self):
        ftp = self.connect(self.context)
        root = deploy.locate_root(ftp, '', 'https://www.simonevacca.it')
        self.assertEqual(root, '/www.simonevacca.it')
        manifest = deploy.backup_site(ftp, self.release, self.backup)
        self.assertEqual((self.web / 'index.html').read_text(), '<html>Simone Vacca, old version</html>')
        deploy.deploy_release(ftp, self.output, self.backup)
        for name in self.release['files']:
            self.assertEqual((self.web / name).read_bytes(), (self.output / 'site' / name).read_bytes())
        self.assertEqual((self.web / 'keep.txt').read_text(), 'external file, keep unchanged')
        deploy.restore_site(ftp, manifest, self.backup)
        self.assertEqual((self.web / 'index.html').read_text(), '<html>Simone Vacca, old version</html>')
        self.assertTrue((self.web / 'app.js').exists())  # i file nuovi non vengono eliminati
        self.assertFalse(list(self.web.rglob('.sv-upload-*')))

    def test_untrusted_certificate_is_refused(self):
        with self.assertRaises(ssl.SSLCertVerificationError):
            self.connect(ssl.create_default_context())

    def test_public_https_checks_homepage_and_assets(self):
        class QuietHTTP(SimpleHTTPRequestHandler):
            def log_message(self, *_args):
                pass

        public = self.root / 'https-public'
        shutil.copytree(self.output / 'site', public)
        server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHTTP, directory=str(public)))
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(self.cert_path, self.key_path)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            # Si aggiunge solo la CA del server di prova: TLS resta verificato.
            with patch.object(deploy, 'urlopen', side_effect=lambda url, timeout: urlopen(url, timeout=timeout, context=self.context)):
                deploy.verify_public(self.output, f'https://localhost:{server.server_port}')
                (public / 'app.js').write_bytes(b'old version still online')
                with patch.object(deploy.time, 'sleep'), self.assertRaises(deploy.DeployError):
                    deploy.verify_public(self.output, f'https://localhost:{server.server_port}')
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == '__main__':
    unittest.main()
