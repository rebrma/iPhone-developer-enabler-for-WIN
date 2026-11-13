# iOS Developer Mode Helper

A portable Windows utility that makes the **Developer Mode** setting available on a USB-connected iPhone or iPad and checks whether Developer Mode is enabled.

**No Mac, Xcode, virtual machine, or separate Python installation is needed to run the Windows executable.** Apple USB device support must be installed on the PC.

The **Reveal setting** button exposes the switch. You finish enabling Developer Mode on the device, including its restart and confirmation. **Check status** reports the actual state separately.

I WILL GLADLY THANKS FOR STAR IF THAT HELP :)

## Requirements

| Component | Requirement |
| --- | --- |
| Computer | Windows 10 or Windows 11, x64 |
| Device | iPhone or iPad running iOS/iPadOS 16 or later with Developer Mode support |
| Connection | A USB cable supporting data transfer |
| Apple software | Apple Devices, or an existing working Apple Mobile Device installation supplied with iTunes |
| Device access | Unlock the device and accept **Trust This Computer** when prompted |

Start with [Apple's Windows connection instructions](https://support.apple.com/en-us/108643). The device should be recognized by Apple's software before using this helper.

These are compatibility targets, not a claim that every hardware and OS combination has been tested. The packaged app has been checked on a real Windows/iPhone setup. iPad and other Windows/device combinations need further testing. There is no native Windows ARM64 or 32-bit build in this release.

## Download and run

1. Open this repository's **Releases** page.
2. Download `iOS-Developer-Mode-Helper-0.1.1-windows-x64.zip` and extract it to a writable folder, such as a folder under Documents.
3. Double-click `iOS-Developer-Mode-Helper.exe`.

The separate `iOS-Developer-Mode-Helper-0.1.1-windows-x64.exe` asset is the same standalone application. The ZIP also contains the license, documentation, and corresponding source archive.

The executable is unsigned. Its SHA-256 digest is listed in the release's `SHA256SUMS.txt`. Check the downloaded EXE in PowerShell:

```powershell
Get-FileHash .\iOS-Developer-Mode-Helper-0.1.1-windows-x64.exe -Algorithm SHA256
```

Compare the result with the matching filename in `SHA256SUMS.txt`.

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
| No USB device is listed | Confirm that Apple Devices recognizes the phone; try another data cable or USB port, then refresh. |
| Apple device support is unavailable | Install or repair Apple Devices/Apple Mobile Device support, then reconnect. |
| A trust or pairing error appears | Unlock the device and accept its trust prompt, then retry. See [Apple's explanation of device trust](https://support.apple.com/en-us/109054). |
| The request times out | Keep the device unlocked, reconnect, and retry. The default operation timeout is 20 seconds. |
| Reveal succeeds but status remains disabled | Complete the on-device switch, restart, and confirmation steps. Revealing the setting alone does not enable it. |
| Several phones are connected | Choose one explicitly. The GUI shows a masked identifier suffix to distinguish entries. |
| The device or OS is unsupported | This helper targets iPhone/iPad on iOS/iPadOS 16+. Other Apple device families are rejected. |

The helper does not require you to remove the device passcode. It does not install apps or automatically reboot the phone.

## Command line

The packaged GUI executable supports JSON output through `--output`. Without this option, a windowed executable may have no visible console output.

Run a status check from the directory containing the downloaded EXE:

```powershell
Start-Process -FilePath .\iOS-Developer-Mode-Helper-0.1.1-windows-x64.exe -ArgumentList '--status --output status.json' -WorkingDirectory (Get-Location).Path -Wait
Get-Content .\status.json
```

Equivalent source commands:

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

The helper uses [pymobiledevice3](https://github.com/doronz88/pymobiledevice3), pinned to version **11.43.1**. Apple's Windows device service provides the USB transport. The library establishes a trusted lockdown session and sends the reveal request to `com.apple.amfi.lockdown`.

The request makes the setting visible; the user completes activation on the device. Status checks query the device's reported Developer Mode state. The GUI runs device operations in a background worker with bounded timeouts.

## Privacy and local data

- The application sends no telemetry and does not upload device information.
- The GUI masks device identifiers. The explicit CLI `--list` command returns full IDs for device selection; treat saved output as local device data.
- Pairing can create local trust records managed by pymobiledevice3 and Apple's device services. Those records stay on the PC and are not included in distributed packages.
- Building downloads dependencies and source archives from PyPI. Running the packaged helper does not require a build environment.

## Run from source

Install [Python 3.13 x64](https://www.python.org/downloads/windows/) with Tk support. From the repository root:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe devmode-helper.pyw
```

Run the tests with:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The unit tests use mocked devices. They cover device selection, timeout handling, supported device classes, connection cleanup, and the distinction between revealing the switch and enabling the mode. They do not certify every iOS release.

## Build a standalone EXE

The original release was built with Python **3.13.7 x64** and [PyInstaller](https://pyinstaller.org/) **6.22.3**.

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

The included [GitHub Actions workflow](.github/workflows/windows.yml) runs the Windows build and uploads its results as an Actions artifact. It does not publish a release or need a connected iPhone. See [PUBLISHING.md](PUBLISHING.md) for manual upload steps.

## License and acknowledgements

This project is licensed under **GPL-3.0-or-later**; see [LICENSE](LICENSE). It relies on the work of the [pymobiledevice3 contributors](https://github.com/doronz88/pymobiledevice3).

See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for dependency notices. The corresponding source release includes the helper's source, build instructions, dependency inventory, license texts, and exact upstream source archives for pymobiledevice3 and PyInstaller. Keep the source and notices available when redistributing the binaries.

Apple device drivers are installed separately and are not redistributed. This is an independent project, not an Apple product.
