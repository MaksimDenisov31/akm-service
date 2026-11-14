import ftplib
from pathlib import Path
import tempfile
import unittest
from deploy_hostiman import collect_files, upload_files, REMOTE_DIRECTORY


class FakeFTP:
    def __init__(self):
        self.directories = {REMOTE_DIRECTORY}
        self.current = ''
        self.uploads = {}
        self.renames = []

    def cwd(self, value):
        target = value if value == REMOTE_DIRECTORY else self.current + '/' + value
        if target not in self.directories:
            raise ftplib.error_perm('550 Missing directory')
        self.current = target

    def pwd(self):
        return self.current

    def mkd(self, name):
        self.directories.add(self.current + '/' + name)

    def storbinary(self, command, stream):
        self.uploads[(self.current, command[5:])] = stream.read()

    def voidcmd(self, command):
        pass

    def size(self, name):
        return len(self.uploads[(self.current, name)])

    def rename(self, source, target):
        self.renames.append((self.current, source, target))


class DeploymentTests(unittest.TestCase):
    def create_site(self, root):
        (root / 'assets').mkdir()
        for name in ('index.html', 'style.css', 'app.js', 'assets/hero.jpg'):
            (root / name).write_bytes(b'test')

    def test_upload_scope_and_entrypoint_last(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_site(root)
            ftp = FakeFTP()
            upload_files(ftp, collect_files(root))
            self.assertEqual(ftp.renames[-1][2], 'index.html')
            self.assertEqual(len(ftp.renames), 4)
            self.assertTrue(all(item[0].startswith(REMOTE_DIRECTORY) for item in ftp.renames))

    def test_missing_asset_blocks_deployment(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                collect_files(Path(directory))

    def test_hidden_secret_blocks_deployment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.create_site(root)
            (root / '.env').write_text('example-only')
            with self.assertRaises(ValueError):
                collect_files(root)


if __name__ == '__main__':
    unittest.main()
