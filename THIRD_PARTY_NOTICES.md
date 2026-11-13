# Third-party notices

The runtime dependency is pinned in `requirements.txt`:

- **pymobiledevice3 11.43.1**, Copyright its contributors, licensed under **GPL-3.0-or-later**. Source and license: <https://github.com/doronz88/pymobiledevice3>

A packaged distribution must retain this project license and the license notices of pymobiledevice3 and all transitive packages collected into the executable. Python and Tcl/Tk are supplied under their respective licenses.

`build.ps1` (Windows) or `build-linux.sh` (Linux) generates `third_party/inventory.json` and copies available dependency license texts into `third_party/licenses/`, including the Python and Tcl/Tk notices. The inventory describes the platform's build environment; not every installed package is embedded in the executable. The GUI executable also embeds these license texts. Each platform's source ZIP contains its matching inventory and notices.

The accompanying source archive includes this helper's complete source and build scripts, the dependency lock file, and exact upstream source archives for pymobiledevice3 and PyInstaller under `third_party/sources/`. `third_party/sources.json` records their public download URLs and verified SHA-256 digests. No upstream source has been modified. PyInstaller's bootloader distribution exception is retained with its license.

Apple USB drivers on Windows and usbmuxd on Linux are prerequisites installed separately; no Apple driver or Xcode binaries are redistributed. This is an independent project, not an Apple product.
