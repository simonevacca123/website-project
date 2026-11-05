"""Pacchetto pubblico, backup e pubblicazione via FTPS esplicito (TLS verificato).

Usa solo la libreria standard. Le credenziali si leggono dall'ambiente e non
vengono scritte nei manifest, negli artefatti o nei messaggi di errore.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import ftplib
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import ssl
import sys
import time
from urllib.parse import quote, urlsplit
from urllib.request import urlopen
from uuid import uuid4


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_FILES = ('index.html', 'style.css', 'app.js', 'contenuti.js')
ASSET_TYPES = {'.svg', '.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif', '.ico', '.woff', '.woff2'}
MAX_FILE_SIZE = 32 * 1024 * 1024


class DeployError(Exception):
    pass


def digest(data):
    return hashlib.sha256(data).hexdigest()


def public_path(name):
    path = PurePosixPath(name)
    if (not name or path.is_absolute() or '..' in path.parts
            or any(part.startswith('.') for part in path.parts)
            or any(c in name for c in '\r\n\\') or path.as_posix() != name):
        raise DeployError('Percorso non consentito nel pacchetto pubblico.')
    if name not in PUBLIC_FILES and not (
            len(path.parts) > 1 and path.parts[0] == 'assets' and path.suffix.lower() in ASSET_TYPES):
        raise DeployError('File non autorizzato nel pacchetto pubblico: ' + name)
    return name


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def build_release(source, output, revision):
    if not revision or not all(c in '0123456789abcdef' for c in revision) or len(revision) not in (40, 64):
        raise DeployError('La versione deve essere lo SHA completo del commit.')
    source, output = Path(source).resolve(), Path(output).resolve()
    if output == source or source.is_relative_to(output):
        raise DeployError('La cartella di output deve essere distinta dai sorgenti.')
    assets = source / 'assets'
    if not assets.is_dir() or assets.is_symlink():
        raise DeployError('Cartella assets mancante o non valida.')
    names = list(PUBLIC_FILES)
    for item in sorted(assets.rglob('*')):
        if item.is_symlink():
            raise DeployError('Link simbolico non consentito in assets.')
        if item.is_file():
            names.append(public_path(item.relative_to(source).as_posix()))
    if 'assets/favicon.svg' not in names:
        raise DeployError('Favicon mancante.')
    # Legge e valida tutti i file prima di modificare gli output generati.
    files = {}
    for name in names:
        item = source / name
        if item.is_symlink() or not item.is_file():
            raise DeployError('File pubblico mancante o non valido: ' + name)
        data = item.read_bytes()
        if not data or len(data) > MAX_FILE_SIZE:
            raise DeployError('File pubblico vuoto o troppo grande: ' + name)
        files[name] = data
    stage = output / 'site'
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    for name, data in files.items():
        target = stage / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    manifest = {'version': 1, 'revision': revision, 'files': {n: digest(d) for n, d in files.items()}}
    write_json(output / 'manifest.json', manifest)
    return manifest


def load_release(output):
    output = Path(output)
    manifest = json.loads((output / 'manifest.json').read_text())
    files = manifest['files']
    if not files or not set(PUBLIC_FILES).issubset(files):
        raise DeployError('Manifest pubblico incompleto.')
    for name, expected in files.items():
        public_path(name)
        item = output / 'site' / name
        if item.is_symlink() or digest(item.read_bytes()) != expected:
            raise DeployError('Pacchetto modificato dopo la preparazione: ' + name)
    return manifest


class SessionReuseFTP(ftplib.FTP_TLS):
    """Riutilizza la sessione TLS anche sui server che lo richiedono per i dati."""

    def ntransfercmd(self, cmd, rest=None):
        conn, size = ftplib.FTP.ntransfercmd(self, cmd, rest)
        if self._prot_p:
            try:
                conn = self.context.wrap_socket(conn, server_hostname=self.host, session=self.sock.session)
            except Exception:
                conn.close()
                raise
        return conn, size


@contextmanager
def connection():
    missing = [name for name in ('FTP_SERVER', 'FTP_USERNAME', 'FTP_PASSWORD') if not os.environ.get(name)]
    if missing:
        raise DeployError('Mancano i GitHub Actions Secrets: ' + ', '.join(missing))
    host = os.environ['FTP_SERVER'].strip()
    if any(c in host for c in '/:@\r\n ') or not host:
        raise DeployError('FTP_SERVER deve contenere solo il nome del server, senza ftp://, porta o cartella.')
    try:
        port = int(os.environ.get('FTP_PORT') or '21')
    except ValueError:
        raise DeployError('FTP_PORT deve essere un numero.') from None
    ftp = SessionReuseFTP(context=ssl.create_default_context(), timeout=30, encoding='utf-8')
    try:
        ftp.connect(host, port)
        ftp.auth()
        ftp.login(os.environ['FTP_USERNAME'], os.environ['FTP_PASSWORD'])
        ftp.prot_p()
        ftp.set_pasv(True)
        yield ftp
    finally:
        ftp.close()


def names_in_directory(ftp):
    try:
        return {name for name, _facts in ftp.mlsd() if name not in ('.', '..')}
    except ftplib.error_perm as error:
        if str(error)[:3] not in ('500', '501', '502', '504'):
            raise
        return {PurePosixPath(name.rstrip('/')).name for name in ftp.nlst()}


def read_remote(ftp, name):
    original = ftp.pwd()
    path = PurePosixPath(public_path(name))
    try:
        for part in path.parts[:-1]:
            if part not in names_in_directory(ftp):
                return None
            ftp.cwd(part)
        if path.name not in names_in_directory(ftp):
            return None
        data = io.BytesIO()

        def receive(block):
            if data.tell() + len(block) > MAX_FILE_SIZE:
                raise DeployError('File remoto troppo grande per il backup: ' + name)
            data.write(block)

        ftp.retrbinary('RETR ' + path.name, receive)
        return data.getvalue()
    finally:
        ftp.cwd(original)


def is_our_index(data):
    if data is None:
        return False
    text = data.decode('utf-8', errors='replace').lower()
    return 'simone' in text and 'vacca' in text and '<html' in text


def locate_root(ftp, directory, site_url):
    if directory:
        if any(c in directory for c in '\r\n\\'):
            raise DeployError('FTP_SERVER_DIR non valida.')
        ftp.cwd(directory)
        index = read_remote(ftp, 'index.html')
        if index is not None and not is_our_index(index):
            raise DeployError('La directory configurata contiene un altro sito: pubblicazione fermata.')
        return ftp.pwd()
    start = ftp.pwd()
    hostname = urlsplit(site_url).hostname
    if not hostname:
        raise DeployError('SITE_URL non valida.')
    domain = hostname.removeprefix('www.')
    candidates = ('.', 'www.' + domain, domain, '/www.' + domain, '/' + domain)
    matches = set()
    for candidate in candidates:
        ftp.cwd(start)
        try:
            ftp.cwd(candidate)
        except ftplib.error_perm as error:
            if str(error)[:3] == '550':
                continue
            raise
        if is_our_index(read_remote(ftp, 'index.html')):
            matches.add(ftp.pwd())
    ftp.cwd(start)
    if len(matches) != 1:
        raise DeployError('Cartella pubblica non identificabile in modo univoco. Imposta la variabile GitHub FTP_SERVER_DIR dal pannello Aruba.')
    root = matches.pop()
    ftp.cwd(root)
    return root


def backup_site(ftp, release, backup):
    backup = Path(backup)
    if backup.exists():
        raise DeployError('La cartella di backup esiste già: non viene sovrascritta.')
    backup.mkdir(parents=True)
    manifest = {'version': 1, 'revision': release['revision'], 'root': ftp.pwd(),
                'created_at': datetime.now(timezone.utc).isoformat(), 'files': {}}
    for name in release['files']:
        data = read_remote(ftp, name)
        manifest['files'][name] = digest(data) if data is not None else None
        if data is not None:
            target = backup / 'files' / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    # Il manifest completo viene scritto soltanto se il backup è riuscito.
    write_json(backup / 'manifest.json', manifest)
    return manifest


def load_backup(backup):
    backup = Path(backup)
    manifest = json.loads((backup / 'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        public_path(name)
        if expected is not None and digest((backup / 'files' / name).read_bytes()) != expected:
            raise DeployError('Backup non integro: ' + name)
    return manifest


def upload_atomic(ftp, name, data):
    path = PurePosixPath(public_path(name))
    original = ftp.pwd()
    temporary = '.sv-upload-' + uuid4().hex
    try:
        for part in path.parts[:-1]:
            if part not in names_in_directory(ftp):
                ftp.mkd(part)
            ftp.cwd(part)
        ftp.storbinary('STOR ' + temporary, io.BytesIO(data))
        ftp.rename(temporary, path.name)
    finally:
        try:
            # Può rimuovere solo il file temporaneo appena creato da questo upload.
            ftp.delete(temporary)
        except ftplib.error_perm:
            pass
        ftp.cwd(original)


def restore_site(ftp, manifest, backup, selected=None):
    ftp.cwd(manifest['root'])
    names = selected if selected is not None else list(manifest['files'])
    for name in sorted(names, key=lambda n: (n == 'index.html', n)):
        if manifest['files'][name] is not None:
            data = (Path(backup) / 'files' / name).read_bytes()
            upload_atomic(ftp, name, data)
            if digest(read_remote(ftp, name) or b'') != manifest['files'][name]:
                raise DeployError('Ripristino da verificare: ' + name)
    # File nuovi e file estranei non vengono eliminati automaticamente.


def deploy_release(ftp, output, backup):
    release = load_release(output)
    previous = load_backup(backup)
    if release['revision'] != previous['revision'] or set(release['files']) != set(previous['files']):
        raise DeployError('Backup e pacchetto non corrispondono alla stessa pubblicazione.')
    ftp.cwd(previous['root'])
    for name, expected in previous['files'].items():
        data = read_remote(ftp, name)
        if (digest(data) if data is not None else None) != expected:
            raise DeployError('Il sito è cambiato dopo il backup: ripetere la procedura senza sovrascrivere modifiche esterne.')
    changed = []
    try:
        for name in sorted(release['files'], key=lambda n: (n == 'index.html', n)):
            if release['files'][name] == previous['files'][name]:
                print('Già aggiornato:', name, flush=True)
                continue
            data = (Path(output) / 'site' / name).read_bytes()
            # Registra anche il file corrente: un errore può arrivare dopo RNTO.
            changed.append(name)
            upload_atomic(ftp, name, data)
            if digest(read_remote(ftp, name) or b'') != release['files'][name]:
                raise DeployError('Verifica del file caricato non riuscita: ' + name)
            print('Verificato:', name, flush=True)
    except Exception:
        try:
            restore_site(ftp, previous, backup, changed)
            print('Ripristinati dal backup i file preesistenti coinvolti nel trasferimento.', flush=True)
        except Exception:
            print('::error::Ripristino automatico incompleto. Usa il backup salvato prima del deploy.', flush=True)
        raise


def verify_public(output, site_url):
    release = load_release(output)
    parsed = urlsplit(site_url)
    if parsed.scheme != 'https' or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise DeployError('SITE_URL deve essere un indirizzo HTTPS del sito, senza credenziali o parametri.')
    for attempt in range(4):
        try:
            for name, expected in release['files'].items():
                path = '' if name == 'index.html' else quote(name)
                url = site_url.rstrip('/') + '/' + path + '?deploy=' + release['revision']
                with urlopen(url, timeout=20) as response:
                    if response.status != 200 or digest(response.read(MAX_FILE_SIZE + 1)) != expected:
                        raise DeployError('Il sito pubblico non mostra ancora la versione caricata.')
            print('Verifica HTTPS superata: i file online corrispondono al commit.', flush=True)
            return
        except Exception:
            if attempt == 3:
                raise DeployError('Verifica HTTPS fallita: controlla cartella pubblica, dominio e cache. Il controllo FTPS è distinto dalla visibilità sul sito.') from None
            time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'backup', 'deploy', 'restore', 'verify'])
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    parser.add_argument('--backup', type=Path, default=ROOT / 'backups' / 'predeploy')
    args = parser.parse_args()
    try:
        site_url = os.environ.get('SITE_URL', 'https://www.simonevacca.it')
        if args.command == 'build':
            result = build_release(ROOT, args.output, os.environ.get('DEPLOY_REVISION', ''))
            print('Pacchetto pubblico pronto:', len(result['files']), 'file.')
        elif args.command == 'verify':
            verify_public(args.output, site_url)
        else:
            with connection() as ftp:
                if args.command == 'backup':
                    release = load_release(args.output)
                    locate_root(ftp, os.environ.get('FTP_SERVER_DIR', '').strip(), site_url)
                    backup_site(ftp, release, args.backup)
                    print('Backup completato. Nessun file remoto modificato.')
                elif args.command == 'deploy':
                    deploy_release(ftp, args.output, args.backup)
                else:
                    restore_site(ftp, load_backup(args.backup), args.backup)
                    print('Ripristinati i file presenti nel backup; nessun file estraneo eliminato.')
    except DeployError as error:
        print('::error::' + str(error), file=sys.stderr)
        return 1
    except ssl.SSLCertVerificationError:
        print('::error::Certificato FTPS non verificabile. Usa il nome server ufficiale Aruba; la verifica TLS resta attiva.', file=sys.stderr)
        return 1
    except ftplib.error_perm as error:
        code = str(error)[:3]
        message = 'Credenziali FTP rifiutate: verifica FTP_USERNAME e FTP_PASSWORD.' if code == '530' else 'Operazione FTPS rifiutata: verifica accesso, permessi e cartella sul pannello Aruba.'
        print('::error::' + message, file=sys.stderr)
        return 1
    except Exception:
        print('::error::Operazione interrotta. Verifica connessione FTPS esplicita, porta, configurazione e artefatto di backup. Nessuna credenziale viene mostrata.', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
