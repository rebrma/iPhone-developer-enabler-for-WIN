from pathlib import Path
import runpy
import tarfile
import tempfile
import unittest

packaging = runpy.run_path(str(Path(__file__).resolve().parents[1] / "packaging/make_release.py"))


class ReleasePackagingTests(unittest.TestCase):
    def test_linux_archive_permissions_and_anonymous_ownership(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "fixture-binary"
            binary.write_bytes(b"fixture")
            archive = root / "portable.tar.gz"
            packaging["portable_tar"](archive, [(binary, "iOS-Developer-Mode-Helper"), (binary, "README.md")])
            with tarfile.open(archive) as data:
                for item in data.getmembers():
                    self.assertEqual((item.uid, item.gid, item.uname, item.gname), (0, 0, "", ""))
                self.assertEqual(data.getmember("iOS-Developer-Mode-Helper").mode, 0o755)
                self.assertEqual(data.getmember("README.md").mode, 0o644)
