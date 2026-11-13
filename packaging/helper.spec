from pathlib import Path
import os
import sys
from PyInstaller.utils.hooks import copy_metadata

root = Path(SPECPATH).parent
name = "iOS-Developer-Mode-Helper"
one_dir = os.environ.get("DEVMODE_BUILD_LAYOUT") == "onedir"
datas = copy_metadata("pymobiledevice3")
datas += [(str(root / "LICENSE"), "."), (str(root / "README.md"), "."),
          (str(root / "third_party" / "licenses"), "third_party/licenses"),
          (str(root / "third_party" / "inventory.json"), "third_party")]
a = Analysis([str(root / "devmode-helper.pyw")], pathex=[str(root)],
             binaries=[], datas=datas, hiddenimports=[], hookspath=[],
             runtime_hooks=[], excludes=[], noarchive=False)
# Notice files are data, not Python runtime modules. Never package cached
# bytecode from dependency metadata: its co_filename can expose build paths.
a.datas = [entry for entry in a.datas if not (
    entry[0].replace('\\', '/').startswith('third_party/licenses/') and
    ('__pycache__' in entry[0] or entry[0].lower().endswith(('.pyc', '.pyo')))
)]
pyz = PYZ(a.pure)
options = dict(debug=False, strip=False, upx=False, console=sys.platform != "win32")
if sys.platform == "win32":
    options["version"] = str(root / "packaging" / "version_info.txt")
if one_dir:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=name,
              **options)
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=name)
else:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name=name,
              **options)
