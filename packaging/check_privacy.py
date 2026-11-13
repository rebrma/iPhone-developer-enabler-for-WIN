"""Check decompressed onefile content for local build identity and cached notices.

This is a regression gate, not a general-purpose secret scanner. It never prints
the identity strings it searches for. Run the build on the same host as this check.
"""
from __future__ import annotations
import argparse
import io
import os
import re
from pathlib import Path
import zipfile


def identity_markers(root: Path) -> list[bytes]:
    strings = [str(root.resolve()), str(root.resolve()).replace('\\', '/')]
    username = os.environ.get('USERNAME') or os.environ.get('USER', '')
    # Generic CI/system names also occur in unmodified third-party binaries.
    if len(username) >= 5 and username.casefold() not in {'runner', 'runneradmin', 'admin', 'administrator', 'system'}:
        strings.append(username)
    computer = os.environ.get('COMPUTERNAME', '')
    if len(computer) >= 6:
        strings.append(computer)
    return [value.encode(encoding).lower() for value in strings
            for encoding in ('utf-8', 'utf-16le', 'utf-16be')]


def inspect_blob(data: bytes, name: str, markers: list[bytes]) -> list[str]:
    problems = []
    lowered = data.lower()
    # Match an identity, not a prefix of an unrelated public project/user name.
    if any(marker in lowered and re.search(rb'(?<![a-z0-9_])' + re.escape(marker) + rb'(?![a-z0-9_])', lowered) for marker in markers):
        problems.append(f'Local build identity in {name}')
    normalized = name.replace('\\', '/')
    if normalized.startswith('third_party/licenses/') and (
        '__pycache__' in normalized or normalized.lower().endswith(('.pyc', '.pyo'))
    ):
        problems.append(f'Cached bytecode in notices: {name}')
    if data.startswith(b'PK\x03\x04'):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for item in archive.infolist():
                if not item.is_dir():
                    problems.extend(inspect_blob(archive.read(item), f'{name}!/{item.filename}', markers))
    return problems


def check(exe: Path) -> list[str]:
    from PyInstaller.archive.readers import CArchiveReader
    markers = identity_markers(Path(__file__).resolve().parents[1])
    problems = inspect_blob(exe.read_bytes(), exe.name, markers)
    archive = CArchiveReader(str(exe))
    for name, entry in archive.toc.items():
        problems.extend(inspect_blob(archive.extract(name), name, markers))
        if entry[-1] == 'z':
            pyz = archive.open_embedded_archive(name)
            for module in pyz.toc:
                data = pyz.extract(module, raw=True)
                if data is not None:
                    problems.extend(inspect_blob(data, f'{name}!/{module}', markers))
    return problems


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('executable', type=Path)
    args = parser.parse_args()
    problems = check(args.executable)
    for problem in problems:
        print(problem)
    print('Packaged privacy check: ' + ('FAIL' if problems else 'PASS'))
    raise SystemExit(1 if problems else 0)
