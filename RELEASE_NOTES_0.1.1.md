## iOS Developer Mode Helper 0.1.1

### Packaging privacy fix

- Excludes compiled Python cache files from bundled dependency notices. Version 0.1.0 accidentally included cache metadata containing the local build path and Windows username.
- Refreshes generated notice files so stale caches cannot reappear in subsequent builds.
- Adds a build-time check of decompressed executable content for local build identity and cached notice bytecode.
- Refreshes the English README, source packages, and download checksums.

Application behavior is unchanged: select a USB iPhone/iPad, check Developer Mode status, and reveal its setting. Finish activation on the device. Use this release instead of the previous 0.1.0 packages.

### Requirements and downloads

Targets Windows 10/11 x64 with Apple USB device support, and iPhone/iPad on iOS/iPadOS 16 or later. The executable is unsigned. Compatibility with every device and OS combination has not been tested.

- **`-windows-x64.zip`**: portable application, documentation, license, and corresponding source.
- **`-windows-x64.exe`**: standalone application.
- **`-source.zip`**: helper and build source, dependency notices, and upstream source archives.
- **`SHA256SUMS.txt`**: download checksums.

See the repository README for the complete setup and usage guide. The project is GPL-3.0-or-later and uses [pymobiledevice3](https://github.com/doronz88/pymobiledevice3).
