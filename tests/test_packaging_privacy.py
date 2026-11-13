from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
notices = runpy.run_path(str(ROOT / 'packaging/collect_notices.py'))
privacy = runpy.run_path(str(ROOT / 'packaging/check_privacy.py'))


class PackagingPrivacyTests(unittest.TestCase):
    def test_notice_collector_preserves_license_but_rejects_compiled_cache(self):
        include = notices['is_license_entry']
        self.assertTrue(include('example-1.0.dist-info/licenses/LICENSE'))
        self.assertTrue(include('example-1.0.dist-info/licenses/AUTHORS.py'))
        self.assertFalse(include('example-1.0.dist-info/licenses/__pycache__/AUTHORS.cpython-313.pyc'))
        self.assertFalse(include('packaging/licenses/__init__.py'))

    def test_privacy_gate_rejects_personal_path_inside_cached_payload(self):
        scan = privacy['inspect_blob']
        name = 'third_party/licenses/example/__pycache__/AUTHORS.cpython-313.pyc'
        payload = b'C:\\Users\\fixture-builder\\project\\AUTHORS.py'
        result = scan(payload, name, [b'fixture-builder'])
        self.assertTrue(any('Local build identity' in problem for problem in result))
        self.assertTrue(any('Cached bytecode' in problem for problem in result))
        self.assertEqual(scan(b'Copyright Example Contributors', 'LICENSE', [b'fixture-builder']), [])
        self.assertEqual(scan(b'https://example.invalid/fixturebuilderx/repo', 'README', [b'fixturebuilder']), [])
