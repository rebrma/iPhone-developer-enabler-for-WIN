"""Exercise the real frozen Linux CLI and desktop window without a phone."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("executable", type=Path)
    parser.add_argument("--screenshot", type=Path, required=True)
    args = parser.parse_args()
    exe = str(args.executable.resolve())
    headless = {k: v for k, v in os.environ.items() if k not in {"DISPLAY", "WAYLAND_DISPLAY"}}
    result = subprocess.run([exe, "--self-test"], env=headless, text=True, capture_output=True, timeout=60, check=True)
    assert json.loads(result.stdout)["ok"]
    result = subprocess.run([exe], env=headless, text=True, capture_output=True, timeout=30)
    assert result.returncode == 2 and "--list" in json.loads(result.stderr)["error"], result.stderr
    result = subprocess.run([exe, "--list"], env={**headless, "USBMUXD_SOCKET_ADDRESS": "/tmp/helper-fixture-no-socket"},
                            text=True, capture_output=True, timeout=30)
    assert result.returncode == 2 and "usbmuxd" in json.loads(result.stderr)["error"], result.stderr
    args.screenshot.parent.mkdir(parents=True, exist_ok=True)
    with args.screenshot.with_suffix(".log").open("w") as log:
        app = subprocess.Popen([exe], stdout=log, stderr=log)
        try:
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                assert app.poll() is None, "Frozen GUI exited before creating its window"
                found = subprocess.run(["xdotool", "search", "--onlyvisible", "--name", "^iOS Developer Mode Helper$"],
                                       text=True, capture_output=True)
                if found.returncode == 0:
                    time.sleep(2)
                    subprocess.run(["scrot", str(args.screenshot)], check=True, timeout=15)
                    break
                time.sleep(0.25)
            else:
                raise AssertionError("Frozen GUI did not create a visible window")
        finally:
            app.terminate()
            try:
                app.wait(timeout=10)
            except subprocess.TimeoutExpired:
                app.kill()
                app.wait()
    print("Frozen CLI, Linux errors, and GUI smoke checks: PASS (no physical device test)")


if __name__ == "__main__":
    main()
