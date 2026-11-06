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


def collect() -> None:
    DEST.mkdir(exist_ok=True)
    packages = []
    for dist in sorted(metadata.distributions(), key=lambda d: d.metadata["Name"].lower()):
        name = dist.metadata["Name"]
        version = dist.version
        licenses = []
        for entry in dist.files or []:
            parts = Path(str(entry)).parts
            if ".." in parts:
                continue
            leaf = parts[-1].lower()
            if not (leaf.startswith(("license", "licence", "copying", "notice")) or "licenses" in parts):
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
