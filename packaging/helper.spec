from pathlib import Path
import os
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
pyz = PYZ(a.pure)
if one_dir:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=name,
              debug=False, strip=False, upx=False, console=False,
              version=str(root / "packaging" / "version_info.txt"))
    coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name=name)
else:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name=name,
              debug=False, strip=False, upx=False, console=False,
              version=str(root / "packaging" / "version_info.txt"))
