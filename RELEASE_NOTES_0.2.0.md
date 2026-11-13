## iOS Developer Mode Helper 0.2.0 — Windows and Linux

- Adds a native, portable **Linux x86_64** executable with the same GUI and USB device actions as Windows. Python is bundled.
- Adds terminal JSON output, Linux-specific usbmuxd troubleshooting, and a useful message when no desktop display is available.
- Keeps the Windows x64 executable and updates both platforms to 0.2.0.
- Adds Linux builds, frozen CLI/GUI smoke tests, a clean Ubuntu runtime check, archive permission checks, and privacy checks to CI.
- Updates the English README with Linux setup, downloads and troubleshooting.

### Choose a download

| Platform | Recommended package |
| --- | --- |
| Windows 10/11 x64 | `iOS-Developer-Mode-Helper-0.2.0-windows-x64.zip` |
| Linux x86_64 (glibc 2.35+) | `iOS-Developer-Mode-Helper-0.2.0-linux-x86_64.tar.gz` |

Standalone binaries, platform-specific source ZIPs, and `SHA256SUMS.txt` are also attached. Linux source and Windows source include the dependency notices collected on their respective build hosts. Extract the Linux archive and run `./iOS-Developer-Mode-Helper`; install/start `usbmuxd` first. See the README for commands.

Linux automated checks run on Ubuntu 22.04, including a real packaged GUI under Xvfb and a clean runtime without Python. Physical iPhone/iPad USB activation on Linux has not yet been tested. ARM64, 32-bit Linux, and Alpine/musl are not supported by the attached Linux binary.

**Reveal setting** exposes the Developer Mode switch. Activation still requires the device's own Settings, restart and confirmation. The executable is unsigned. Version 0.1.1's packaging privacy fix is retained.

If this tool helped you, a ⭐ on the repository would be greatly appreciated. Thank you!
