"""Produce an explicit source archive and a portable release, without build/cache data."""
from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0"
FILES = ("devmode-helper.pyw", "pyproject.toml", "requirements.txt", "requirements-lock.txt",
         "build.ps1", "README.md", "PUBLISHING.md", "RELEASE_NOTES_0.1.0.md",
         "LICENSE", "THIRD_PARTY_NOTICES.md", ".gitignore")
DIRECTORIES = ("ios_devmode_helper", "tests", "packaging", ".github", "third_party")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--exe", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not args.exe.is_file():
        parser.error("Build the executable first")
    args.out.mkdir(parents=True, exist_ok=True)
    source = args.out / f"iOS-Developer-Mode-Helper-{VERSION}-source.zip"
    exe = args.out / f"iOS-Developer-Mode-Helper-{VERSION}-windows-x64.exe"
    portable = args.out / f"iOS-Developer-Mode-Helper-{VERSION}-windows-x64.zip"
    paths = [ROOT / name for name in FILES]
    for directory in DIRECTORIES:
        paths.extend(path for path in (ROOT / directory).rglob("*")
                     if path.is_file() and "__pycache__" not in path.parts and path.suffix not in (".pyc", ".pyo"))
    with zipfile.ZipFile(source, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            archive.write(path, Path("ios-devmode-helper") / path.relative_to(ROOT))
    shutil.copyfile(args.exe, exe)
    with zipfile.ZipFile(portable, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(exe, "iOS-Developer-Mode-Helper.exe")
        archive.write(source, source.name)
        for name in ("README.md", "PUBLISHING.md", "RELEASE_NOTES_0.1.0.md", "LICENSE", "THIRD_PARTY_NOTICES.md"):
            archive.write(ROOT / name, name)
    hashes = []
    for path in (exe, source, portable):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.append(f"{digest}  {path.name}")
        print(f"{path.name}: {path.stat().st_size} bytes")
    (args.out / "SHA256SUMS.txt").write_text("\n".join(hashes) + "\n", encoding="ascii")


if __name__ == "__main__":
    main()
