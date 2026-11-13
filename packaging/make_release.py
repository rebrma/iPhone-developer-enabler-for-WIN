"""Package native binaries and matching sources using an explicit file allowlist."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import shutil
import sys
import tarfile
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
DOCS = ("README.md", "PUBLISHING.md", f"RELEASE_NOTES_{VERSION}.md", "LICENSE", "THIRD_PARTY_NOTICES.md")
FILES = ("devmode-helper.pyw", "pyproject.toml", "requirements.txt", "requirements-lock.txt",
         "build.ps1", "build-linux.sh", ".gitignore", ".gitattributes", *DOCS)
DIRECTORIES = ("ios_devmode_helper", "tests", "packaging", ".github", "third_party")


def source_files(root: Path):
    paths = [root / name for name in FILES]
    for directory in DIRECTORIES:
        paths.extend(path for path in (root / directory).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path.suffix not in (".pyc", ".pyo"))
    for path in sorted(paths):
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("Source archive may only include regular project files")
        yield path


def portable_tar(target: Path, entries: list[tuple[Path, str]]) -> None:
    with tarfile.open(target, "w:gz", format=tarfile.USTAR_FORMAT) as archive:
        for path, name in entries:
            info = archive.gettarinfo(str(path), arcname=name)
            # Never serialize the build host's user/group names or identifiers.
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = 0
            info.mode = 0o755 if name == "iOS-Developer-Mode-Helper" else 0o644
            with path.open("rb") as content:
                archive.addfile(info, content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--platform", choices=("windows-x64", "linux-x86_64"),
                        default="windows-x64" if sys.platform == "win32" else "linux-x86_64")
    args = parser.parse_args()
    if not args.exe.is_file():
        parser.error("Build the native executable first")
    linux = args.platform == "linux-x86_64"
    header = args.exe.read_bytes()[:20]
    if linux and (header[:6] != b"\x7fELF\x02\x01" or header[18:20] != b"\x3e\x00"):
        parser.error("Linux x86_64 packaging requires an ELF64 AMD64 binary")
    if not linux and header[:2] != b"MZ":
        parser.error("Windows packaging requires a PE executable")
    args.out.mkdir(parents=True, exist_ok=True)
    stem = f"iOS-Developer-Mode-Helper-{VERSION}-{args.platform}"
    source = args.out / f"{stem}-source.zip"
    exe = args.out / (stem if linux else f"{stem}.exe")
    portable = args.out / (f"{stem}.tar.gz" if linux else f"{stem}.zip")
    with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in source_files(ROOT):
            archive.write(path, Path("ios-devmode-helper") / path.relative_to(ROOT))
    shutil.copyfile(args.exe, exe)
    if linux:
        exe.chmod(0o755)
    entries = [(exe, "iOS-Developer-Mode-Helper" if linux else "iOS-Developer-Mode-Helper.exe"),
               (source, source.name), *((ROOT / name, name) for name in DOCS)]
    if linux:
        portable_tar(portable, entries)
    else:
        with zipfile.ZipFile(portable, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path, name in entries:
                archive.write(path, name)
    hashes = []
    for path in (exe, source, portable):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.append(f"{digest}  {path.name}")
        print(f"{path.name}: {path.stat().st_size} bytes")
    (args.out / f"SHA256SUMS-{args.platform}.txt").write_text("\n".join(hashes) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
