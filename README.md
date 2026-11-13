# iOS Developer Mode Helper

A portable **Windows and Linux** utility that makes the **Developer Mode** setting available on a USB-connected iPhone or iPad and checks whether Developer Mode is enabled.

**No Mac, Xcode, virtual machine, or separate Python installation is needed to run the packaged application.** Windows needs Apple USB device support; Linux needs `usbmuxd`.

The **Reveal setting** button exposes the switch. You finish enabling Developer Mode on the device, including its restart and confirmation. **Check status** reports the actual state separately.

If this tool helped you, please consider giving the repository a ⭐. I'd really appreciate it!

## Requirements

| Component | Requirement |
| --- | --- |
| Computer | Windows 10/11 x64, or Linux x86_64 with glibc 2.35+ (Ubuntu 22.04 or newer baseline) |
| Device | iPhone or iPad running iOS/iPadOS 16 or later with Developer Mode support |
| Connection | A USB cable supporting data transfer |
| USB support | Windows: Apple Devices or working Apple Mobile Device support from iTunes. Linux: `usbmuxd` and `libusb` |
| Graphical interface | Windows desktop, or Linux X11/XWayland desktop; Linux CLI commands also work without a display |
| Device access | Unlock the device and accept **Trust This Computer** when prompted |

On Windows, start with [Apple's connection instructions](https://support.apple.com/en-us/108643). On Linux, follow the setup below; [usbmuxd](https://github.com/libimobiledevice/usbmuxd) provides the USB transport.

These are compatibility targets, not a claim that every combination has been tested. The Windows USB workflow has previously been checked with a real iPhone. Linux is checked by automated unit tests, frozen CLI/GUI tests and a clean Ubuntu runtime test; a physical Linux/iPhone USB activation has not yet been tested. This release has no ARM64, 32-bit, macOS or Alpine/musl binary.

## Download and run

Get the current packages from **[Releases](https://github.com/rebrma/iPhone-developer-enabler-for-WIN/releases/latest)**.

### Windows

1. Open the Releases page.
2. Download `iOS-Developer-Mode-Helper-0.2.0-windows-x64.zip` and extract it to a writable folder, such as a folder under Documents.
3. Double-click `iOS-Developer-Mode-Helper.exe`.

The separate `iOS-Developer-Mode-Helper-0.2.0-windows-x64.exe` asset is the same standalone application. The ZIP also contains the license, documentation, and corresponding source archive.

The executable is unsigned. Its SHA-256 digest is listed in the release's `SHA256SUMS.txt`. Check the downloaded EXE in PowerShell:

```powershell
Get-FileHash .\iOS-Developer-Mode-Helper-0.2.0-windows-x64.exe -Algorithm SHA256
```

Compare the result with the matching filename in `SHA256SUMS.txt`.

### Linux

Install USB support. On Ubuntu/Debian:

```bash
sudo apt update
sudo apt install usbmuxd libusb-1.0-0
```

The distribution normally starts `usbmuxd` when an Apple USB device is connected. Reconnect and unlock the phone, then accept **Trust This Computer**. Run the helper as your normal desktop user; only package/service administration needs `sudo`.

Download `iOS-Developer-Mode-Helper-0.2.0-linux-x86_64.tar.gz`, then extract and run it:

```bash
mkdir -p ios-devmode-helper
tar -xzf iOS-Developer-Mode-Helper-0.2.0-linux-x86_64.tar.gz -C ios-devmode-helper
cd ios-devmode-helper
./iOS-Developer-Mode-Helper
```

The archive preserves the executable permission and includes documentation, licenses and corresponding sources. Python and Tcl/Tk are bundled. A compatible glibc-based Linux desktop remains required. For the separate raw binary, run `chmod +x iOS-Developer-Mode-Helper-0.2.0-linux-x86_64` before launching it.

To verify a downloaded archive, compare `sha256sum iOS-Developer-Mode-Helper-0.2.0-linux-x86_64.tar.gz` with its entry in `SHA256SUMS.txt`.

## Enable Developer Mode

1. Connect the unlocked iPhone or iPad to the PC with a USB data cable.
2. Accept **Trust This Computer** on the device if prompted. Enter its passcode on the device itself.
3. Click **Refresh**. If several devices are connected, select the intended one.
4. Click **Check status**. If Developer Mode is already enabled, no further action is needed.
5. Otherwise, click **Reveal setting**.
6. On the device, open **Settings → Privacy & Security → Developer Mode** and enable the switch.
7. Confirm the restart. After the device restarts, unlock it and confirm **Turn On** when prompted.
8. Reconnect if necessary, click **Refresh**, select the device, and use **Check status** again.

See [Apple's Developer Mode guide](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device) for the on-device steps.

### Buttons

| Button | What it does |
| --- | --- |
| **Refresh** | Lists devices connected through USB. Wi-Fi devices are excluded. |
| **Check status** | Reads the selected device's Developer Mode state. |
| **Reveal setting** | Asks iOS to make the Developer Mode switch available. This does not confirm that the mode is enabled. |

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| No USB device is listed | Unlock/trust the phone; try another data cable or USB port. On Windows, confirm Apple Devices recognizes it. On Linux, check `usbmuxd`. |
| USB device support is unavailable on Windows | Install or repair Apple Devices/Apple Mobile Device support, then reconnect. |
| USB device support is unavailable on Linux | Install `usbmuxd`, reconnect the phone, and check `systemctl status usbmuxd`. On systemd distributions, start it if needed with `sudo systemctl start usbmuxd`. |
| Linux GUI cannot open | Use an X11 desktop or a Wayland desktop with XWayland. CLI actions below work without a display. |
| Linux says permission denied | Extract onto a filesystem allowing execution; restore the executable bit with `chmod +x`. A `noexec` mount cannot run the binary. |
| Linux says GLIBC version not found or Exec format error | Use x86_64 Linux with glibc 2.35+; this binary is not for ARM64, 32-bit systems or musl. |
| A trust or pairing error appears | Unlock the device and accept its trust prompt, then retry. See [Apple's explanation of device trust](https://support.apple.com/en-us/109054). |
| The request times out | Keep the device unlocked, reconnect, and retry. The default operation timeout is 20 seconds. |
| Reveal succeeds but status remains disabled | Complete the on-device switch, restart, and confirmation steps. Revealing the setting alone does not enable it. |
| Several phones are connected | Choose one explicitly. The GUI shows a masked identifier suffix to distinguish entries. |
| The device or OS is unsupported | This helper targets iPhone/iPad on iOS/iPadOS 16+. Other Apple device families are rejected. |

The helper does not require you to remove the device passcode. It does not install apps or automatically reboot the phone.

## Command line

The packaged Windows GUI executable supports JSON output through `--output`. Without this option, the Windows executable may have no visible console output. Linux prints JSON directly to stdout (errors to stderr); `--output` also works.

Run a status check from the directory containing the downloaded EXE:

```powershell
Start-Process -FilePath .\iOS-Developer-Mode-Helper-0.2.0-windows-x64.exe -ArgumentList '--status --output status.json' -WorkingDirectory (Get-Location).Path -Wait
Get-Content .\status.json
```

Linux, from the extracted directory:

```bash
./iOS-Developer-Mode-Helper --list
./iOS-Developer-Mode-Helper --status
./iOS-Developer-Mode-Helper --reveal --device EXACT_DEVICE_ID
./iOS-Developer-Mode-Helper --self-test
```

Equivalent source commands on either platform:

```powershell
python -m ios_devmode_helper --list
python -m ios_devmode_helper --status --device EXACT_DEVICE_ID
python -m ios_devmode_helper --reveal --device EXACT_DEVICE_ID
python -m ios_devmode_helper --self-test --output self-test.json
```

`--device` takes the exact ID returned by `--list`. It can be omitted when exactly one USB device is connected. `--timeout` sets the operation timeout between 1 and 120 seconds. `--self-test` exercises fixtures and imports the runtime without accessing a device.

Example status result:

```json
{"ok": true, "enabled": true}
```

A successful reveal returns `"revealed": true` and `"enabled": null`, because activation has not been verified. Run a status check after completing the on-device steps.

## How it works

The helper uses [pymobiledevice3](https://github.com/doronz88/pymobiledevice3), pinned to version **11.43.1**. Apple's device service on Windows and `usbmuxd` on Linux provide the USB transport. The library establishes a trusted lockdown session and sends the reveal request to `com.apple.amfi.lockdown`.

The request makes the setting visible; the user completes activation on the device. Status checks query the device's reported Developer Mode state. The GUI runs device operations in a background worker with bounded timeouts.

## Privacy and local data

- The application sends no telemetry and does not upload device information.
- The GUI masks device identifiers. The explicit CLI `--list` command returns full IDs for device selection; treat saved output as local device data.
- Pairing can create local trust records managed by pymobiledevice3 and the platform's device service. Those records stay on the computer and are not included in distributed packages.
- Building downloads dependencies and source archives from PyPI. Running the packaged helper does not require a build environment.

## Run from source

Install [Python 3.13](https://www.python.org/downloads/) with Tk support. On Windows, from the repository root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe devmode-helper.pyw
```

On Linux, install `usbmuxd` and use a Python 3.13 installation with `venv` and Tk support (distro package names vary):

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m ios_devmode_helper
.venv/bin/python -m unittest discover -s tests -v
```

Run the tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The unit tests use mocked devices. They cover device selection, timeout handling, supported device classes, connection cleanup, and the distinction between revealing the switch and enabling the mode. They do not certify every iOS release.

## Build standalone packages

Both release builds use Python **3.13.7 x64** and [PyInstaller](https://pyinstaller.org/) **6.22.3**. Build Windows on Windows and Linux on Linux; PyInstaller is not a cross-compiler.

### Windows build

From PowerShell in the repository root, with Python 3.13 available as `python`:

```powershell
.\build.ps1
```

If `python` points to another interpreter, pass the full Python 3.13 executable path with `-Python`.

The build creates `.venv-build`, installs the pinned `requirements-lock.txt`, runs unit tests, collects dependency notices and source archives, builds the executable, and runs a device-free self-test of the frozen application.

Outputs:

```text
dist/onefile/iOS-Developer-Mode-Helper.exe
dist/onefile/iOS-Developer-Mode-Helper.exe.sha256
```

Use `-OneDir` for a directory bundle when diagnosing packaging issues. To prepare release ZIPs:

```powershell
.\.venv-build\Scripts\python.exe packaging/make_release.py --exe dist/onefile/iOS-Developer-Mode-Helper.exe --out dist/release
```

### Linux build

Use Ubuntu 22.04 x86_64 to match the published glibc baseline. Install Python 3.13 with Tk and venv support, plus `build-essential`, `libusb-1.0-0-dev`, `libtcl8.6` and `libtk8.6`. Then:

```bash
PYTHON=python3.13 bash build-linux.sh
.venv-build/bin/python packaging/make_release.py --exe dist/onefile/iOS-Developer-Mode-Helper --out dist/release --platform linux-x86_64
```

The script creates a project-local build environment, installs locked dependencies, runs tests, collects notices, builds the ELF executable and checks the frozen runtime and packaging privacy. Linux output is `dist/onefile/iOS-Developer-Mode-Helper`. Building on a newer distribution can raise the minimum glibc version; see [PyInstaller's Linux compatibility notes](https://pyinstaller.org/en/stable/usage.html#making-gnu-linux-apps-forward-compatible).

The [Windows](.github/workflows/windows.yml) and [Linux](.github/workflows/linux.yml) workflows build and upload release files as Actions artifacts. Linux additionally opens the frozen GUI under Xvfb and checks a clean Ubuntu runtime without Python. These checks do not access a physical iPhone or publish releases. See [PUBLISHING.md](PUBLISHING.md) for release steps.

## License and acknowledgements

This project is licensed under **GPL-3.0-or-later**; see [LICENSE](LICENSE). It relies on the work of the [pymobiledevice3 contributors](https://github.com/doronz88/pymobiledevice3).

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for dependency notices. The corresponding source release includes the helper's source, build instructions, dependency inventory, license texts, and exact upstream source archives for pymobiledevice3 and PyInstaller. Keep the source and notices available when redistributing the binaries.

Apple device drivers and Linux's `usbmuxd` service are installed separately and are not redistributed. This is an independent project, not an Apple product.
