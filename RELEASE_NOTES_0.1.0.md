## iOS Developer Mode Helper 0.1.0

First release of the portable Windows helper for making the iOS Developer Mode setting available over USB.

### Features

- Simple Windows GUI with USB device selection.
- Read the device's actual Developer Mode state.
- Reveal the Developer Mode setting on supported iPhones and iPads.
- Clear on-device activation instructions and bounded device operations.
- Optional JSON command-line output.
- Standalone EXE: no Python, Mac, Xcode, or virtual machine required.

### Getting started

Install Apple Devices/Apple Mobile Device support on Windows, connect and unlock the device, then confirm its trust prompt. Run the helper and click **Reveal setting**. Finish activation in **Settings → Privacy & Security → Developer Mode**, including restart and confirmation on the device. Use **Check status** afterwards.

### Downloads

- **`-windows-x64.zip`**: recommended portable package with the application, documentation, license, and corresponding source.
- **`-windows-x64.exe`**: application only.
- **`-source.zip`**: full source package, build instructions, and dependency notices/source archives.
- **`SHA256SUMS.txt`**: download checksums.

### Compatibility and validation

Targets Windows 10/11 x64 and iPhone/iPad running iOS/iPadOS 16 or later with Developer Mode support. Apple USB drivers are required. The GUI and standalone status check were verified on a real Windows/iPhone setup, and the unit tests and frozen runtime self-test passed. Other device/OS combinations are not comprehensively tested.

Revealing the setting does not enable Developer Mode by itself. The executable is unsigned. No Windows ARM64 or x86 package is provided in this release.

### Documentation and license

See the repository README for requirements, usage, troubleshooting, and build instructions. The project is GPL-3.0-or-later and uses [pymobiledevice3](https://github.com/doronz88/pymobiledevice3). Apple's [Developer Mode guide](https://developer.apple.com/documentation/xcode/enabling-developer-mode-on-a-device) describes the on-device confirmation steps.
