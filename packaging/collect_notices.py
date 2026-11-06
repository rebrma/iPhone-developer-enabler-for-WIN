"""Collect installed dependency licenses and pinned upstream source archives.

Run with the build environment; nothing is read from device/pairing directories.
"""
from __future__ import annotations

import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import shutil
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "third_party"


def is_license_entry(entry: str) -> bool:
    parts = Path(entry).parts
    lower = [part.lower() for part in parts]
    if not parts or ".." in parts or "__pycache__" in lower:
        return False
    if Path(entry).suffix.lower() in {".pyc", ".pyo", ".pyd", ".dll", ".so"}:
        return False
    metadata_license = any(
        part.endswith(".dist-info") and "licenses" in lower[index + 1:]
        for index, part in enumerate(lower)
    )
    return metadata_license or lower[-1].startswith(("license", "licence", "copying", "notice"))


def collect() -> None:
    DEST.mkdir(exist_ok=True)
    # Only this generated directory is refreshed. Remove stale files from older
    # collectors so a previous build cannot silently reintroduce bytecode caches.
    license_root = (DEST / "licenses").resolve()
    if not license_root.is_relative_to(ROOT.resolve()) or license_root == ROOT.resolve():
        raise ValueError("License output must remain inside the project")
    for old in license_root.rglob("*") if license_root.exists() else []:
        if old.is_symlink():
            raise ValueError("Symlinks are not allowed in generated license output")
        if old.is_file():
            old.unlink()
    packages = []
    for dist in sorted(metadata.distributions(), key=lambda d: d.metadata["Name"].lower()):
        name = dist.metadata["Name"]
        version = dist.version
        licenses = []
        for entry in dist.files or []:
            parts = Path(str(entry)).parts
            if not is_license_entry(str(entry)):
                continue
            source = Path(dist.locate_file(entry))
            if not source.is_file():
                continue
            relative = Path("licenses") / f"{name}-{version}" / Path(*parts)
            target = DEST / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            licenses.append(relative.as_posix())
        packages.append({"name": name, "version": version,
                         "license": dist.metadata.get("License-Expression") or dist.metadata.get("License", "See upstream"),
                         "project_urls": dist.metadata.get_all("Project-URL") or [],
                         "license_files": licenses})
    runtime = DEST / "licenses" / "Python-and-Tcl-Tk"
    runtime.mkdir(parents=True, exist_ok=True)
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if python_license.is_file():
        shutil.copyfile(python_license, runtime / "Python-LICENSE.txt")
    for license_path in (Path(sys.base_prefix) / "tcl").glob("*/license*"):
        if license_path.is_file():
            shutil.copyfile(license_path, runtime / f"{license_path.parent.name}-{license_path.name}.txt")
    (DEST / "inventory.json").write_text(json.dumps(packages, indent=2, ensure_ascii=False), encoding="utf-8")

    sources = []
    for name in ("pymobiledevice3", "pyinstaller"):
        version = metadata.version(name)
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=45) as response:
            release = json.load(response)
        item = next(value for value in release["urls"] if value["packagetype"] == "sdist")
        filename = item["filename"]
        if Path(filename).name != filename:
            raise ValueError("Unexpected source archive filename")
        target = DEST / "sources" / filename
        target.parent.mkdir(exist_ok=True)
        expected = item["digests"]["sha256"]
        if not target.exists() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            with urllib.request.urlopen(item["url"], timeout=90) as response:
                content = response.read()
            if hashlib.sha256(content).hexdigest() != expected:
                raise ValueError(f"Source digest mismatch: {name}")
            target.write_bytes(content)
        sources.append({"name": name, "version": version, "file": f"sources/{filename}",
                        "url": item["url"], "sha256": expected})
    (DEST / "sources.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
    print(f"Collected {len(packages)} dependency notices and {len(sources)} source archives.")


if __name__ == "__main__":
    collect()
