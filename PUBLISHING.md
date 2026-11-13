# Publishing Windows and Linux releases

Both platforms are built from the same versioned source commit. Release 0.2.0 includes Windows x64 and Linux x86_64 packages.

## Build and verify

1. Update the version in `pyproject.toml` and `packaging/version_info.txt`, add matching release notes, and update README download examples.
2. Push the source. Wait for both the [Windows](.github/workflows/windows.yml) and [Linux](.github/workflows/linux.yml) workflows to pass for that exact commit.
3. Download the `iOS-Developer-Mode-Helper-windows-x64` and `iOS-Developer-Mode-Helper-linux-x86_64` Actions artifacts. The separate `linux-smoke-evidence` artifact is test evidence, not a release download.
4. Verify each platform's `SHA256SUMS-<platform>.txt`. Combine their six entries into one `SHA256SUMS.txt` and verify the combined manifest before publishing.

The workflows run tests and frozen-runtime/privacy checks. Linux also checks the packaged GUI under Xvfb and a clean Ubuntu runtime without Python. A successful build does not establish compatibility with every physical iPhone or distribution.

For local builds, see the README. Produce packages with `packaging/make_release.py --exe <native-executable> --out dist/release --platform windows-x64` or `--platform linux-x86_64`. The Linux TAR preserves executable permissions and clears the build host's ownership metadata.

## Publish on GitHub

Open [Releases](https://github.com/rebrma/iPhone-developer-enabler-for-WIN/releases) and draft a release for tag `v0.2.0`, targeting the exact tested commit. Use the title **iOS Developer Mode Helper 0.2.0 — Windows and Linux** and the contents of [RELEASE_NOTES_0.2.0.md](RELEASE_NOTES_0.2.0.md).

Attach these seven files:

| File | Purpose |
| --- | --- |
| `iOS-Developer-Mode-Helper-0.2.0-windows-x64.exe` | Standalone Windows application |
| `iOS-Developer-Mode-Helper-0.2.0-windows-x64.zip` | Windows app, documentation and corresponding source |
| `iOS-Developer-Mode-Helper-0.2.0-windows-x64-source.zip` | Windows build source, notices and upstream source archives |
| `iOS-Developer-Mode-Helper-0.2.0-linux-x86_64` | Standalone Linux ELF executable |
| `iOS-Developer-Mode-Helper-0.2.0-linux-x86_64.tar.gz` | Linux app, documentation and corresponding source; recommended Linux download |
| `iOS-Developer-Mode-Helper-0.2.0-linux-x86_64-source.zip` | Linux build source, notices and upstream source archives |
| `SHA256SUMS.txt` | Checksums for all six downloads |

Wait until every upload finishes, verify the uploaded hashes, then publish and mark the release as latest. Source ZIPs are platform-specific because the generated dependency inventories and license files differ. Keep both beside the binaries; GitHub's automatic source snapshot does not contain generated dependency notices or upstream archives.

GitHub reference: [Managing releases](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

## Privacy

Only upload the generated release files. Never upload the build environment, `work/`, pairing records, SSH keys, device-output JSON, or local logs. The source packager uses an explicit allowlist, excludes cached bytecode, and does not include `.git` or credentials. Keep the packaged privacy check enabled.
