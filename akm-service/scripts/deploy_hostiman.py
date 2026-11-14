"""Publish AKM static files over verified FTPS without deleting remote files."""
import argparse
import ftplib
import os
from pathlib import Path, PurePosixPath
import ssl
import sys
import uuid

REMOTE_DIRECTORY = 'www/akm-service.h1n.ru'
SITE_DIRECTORY = Path(__file__).resolve().parents[1] / 'dist'
ALLOWED_EXTENSIONS = {'.html', '.css', '.js', '.json', '.jpg', '.jpeg', '.png', '.webp', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.txt'}


def collect_files(root):
    root = root.resolve()
    for name in ('index.html', 'style.css', 'app.js', 'assets/hero.jpg'):
        if not (root / name).is_file() or not (root / name).stat().st_size:
            raise ValueError('Required site asset missing or empty: ' + name)
    files = []
    for file in root.rglob('*'):
        if file.is_symlink():
            raise ValueError('Symbolic links cannot be deployed')
        if not file.is_file():
            continue
        relative = file.relative_to(root).as_posix()
        if any(part.startswith('.') for part in PurePosixPath(relative).parts):
            raise ValueError('Hidden files cannot be deployed')
        if file.suffix.lower() not in ALLOWED_EXTENSIONS:
            raise ValueError('Unsupported asset extension')
        files.append((file, relative))
    return sorted(files, key=lambda item: (item[1] == 'index.html', item[1]))


def upload_files(ftp, files):
    # Require an existing destination to avoid silently publishing to the wrong folder.
    ftp.cwd(REMOTE_DIRECTORY)
    initial = ftp.pwd()
    token = uuid.uuid4().hex[:12]
    for local, relative in files:
        path = PurePosixPath(relative)
        ftp.cwd(initial)
        for part in path.parts[:-1]:
            try:
                ftp.cwd(part)
            except ftplib.error_perm:
                ftp.mkd(part)
                ftp.cwd(part)
        temporary = '.deploy-' + token + '-' + path.name
        with local.open('rb') as stream:
            ftp.storbinary('STOR ' + temporary, stream)
        ftp.voidcmd('TYPE I')
        if ftp.size(temporary) != local.stat().st_size:
            raise ValueError('Uploaded asset size mismatch')
        ftp.rename(temporary, path.name)
        print('Published: ' + relative, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    files = collect_files(SITE_DIRECTORY)
    if args.check:
        print('Local files verified: ' + str(len(files)))
        return 0
    password = os.environ.get('HOSTIMAN_FTP_PASSWORD', '')
    if not password:
        print('Missing repository secret HOSTIMAN_FTP_PASSWORD. Add it in Settings > Secrets and variables > Actions, then run this workflow again.', file=sys.stderr)
        return 1
    ftp = ftplib.FTP_TLS(context=ssl.create_default_context(), timeout=60)
    try:
        ftp.connect('rufree53.hostiman.ru', 21)
        ftp.login('s280186', password)
        ftp.prot_p()
        ftp.set_pasv(True)
        upload_files(ftp, files)
        print('Deployment complete: http://akm-service.h1n.ru')
    finally:
        ftp.close()
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as error:
        # Avoid logging credentials or arbitrary server replies.
        print('Deployment failed (' + type(error).__name__ + '). Check credentials, FTPS access and destination. No remote deletion was attempted.', file=sys.stderr)
        raise SystemExit(1)
