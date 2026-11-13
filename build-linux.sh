#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ "$(uname -s)" != Linux || "$(uname -m)" != x86_64 ]]; then
    echo 'This build targets Linux x86_64.' >&2
    exit 1
fi
export PIP_CACHE_DIR="$PWD/work/pip-cache"
export PYINSTALLER_CONFIG_DIR="$PWD/work/pyinstaller-cache"
export PYTHONDONTWRITEBYTECODE=1
export DEVMODE_BUILD_LAYOUT=onefile
"${PYTHON:-python3}" -c 'import sys; assert sys.version_info[:2] == (3, 13), "Use Python 3.13 with Tk support"'
"${PYTHON:-python3}" -m venv .venv-build
python=.venv-build/bin/python
"$python" -m pip install --disable-pip-version-check -r requirements-lock.txt
"$python" -m pip check
"$python" -m unittest discover -s tests -v
"$python" packaging/collect_notices.py
"$python" -m PyInstaller --noconfirm --distpath dist/onefile --workpath build/onefile packaging/helper.spec
"$python" packaging/check_privacy.py dist/onefile/iOS-Developer-Mode-Helper
env -u DISPLAY -u WAYLAND_DISPLAY dist/onefile/iOS-Developer-Mode-Helper --self-test --output build/onefile/frozen-self-test.json
"$python" -c 'import json; from pathlib import Path; assert json.loads(Path("build/onefile/frozen-self-test.json").read_text())["ok"]'
sha256sum dist/onefile/iOS-Developer-Mode-Helper > dist/onefile/iOS-Developer-Mode-Helper.sha256
echo 'Linux executable built; unit tests, frozen runtime and privacy checks passed.'
