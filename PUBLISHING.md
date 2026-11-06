# Publishing on GitHub

The prepared upload kit has two directories:

```text
01-repository/ios-devmode-helper/    Source files to upload to the repository
02-release-assets/                 Finished files to attach to a release
```

## 1. Create the repository

Open [github.com/new](https://github.com/new). Use `ios-devmode-helper` as the repository name, choose the visibility, and leave GitHub's README, .gitignore, and license generation disabled: these files are already provided.

Suggested description:

> Portable Windows helper to reveal the iOS Developer Mode setting and check its status over USB.

## 2. Upload the source

On the empty repository page, select **uploading an existing file**. For an existing repository, use **Add file → Upload files**.

Open `01-repository/ios-devmode-helper/` in File Explorer. Drag its **contents** into the upload area, including `.github` and `.gitignore`. Commit the upload to `main` with a message such as `Initial release`.

`README.md`, `LICENSE`, `build.ps1`, and `ios_devmode_helper/` must appear at the repository root. Upload extracted files rather than a ZIP archive. The release assets belong in the next step.

Reference: [GitHub file upload documentation](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository).

## 3. Create release v0.1.0

Open **Releases → Draft a new release** (or **Create a new release**). Create tag `v0.1.0` targeting `main`; set the title to `iOS Developer Mode Helper 0.1.0`.

Copy the contents of [RELEASE_NOTES_0.1.0.md](RELEASE_NOTES_0.1.0.md) into the description. Attach all four files from `02-release-assets/`:

| File | Purpose |
| --- | --- |
| `iOS-Developer-Mode-Helper-0.1.0-windows-x64.exe` | Standalone application |
| `iOS-Developer-Mode-Helper-0.1.0-windows-x64.zip` | Portable package with documentation, license and corresponding source |
| `iOS-Developer-Mode-Helper-0.1.0-source.zip` | Complete source package with dependency notices and upstream source archives |
| `SHA256SUMS.txt` | Checksums for the three downloads |

Wait for the attachments to finish uploading, then click **Publish release**. Share the release page with colleagues.

Reference: [GitHub release management documentation](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository).

## Included documentation

- [README.md](README.md): requirements, download/install steps, usage, troubleshooting, CLI, privacy, and builds.
- [RELEASE_NOTES_0.1.0.md](RELEASE_NOTES_0.1.0.md): ready-to-paste release description.
- [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) and [LICENSE](LICENSE): attribution and license terms.

The automatic GitHub **Source code** download contains the repository snapshot. Attach the supplied `-source.zip` as well: it additionally contains the generated dependency notices and upstream source archives. The provided EXE is unchanged; the upload kit refreshes the documentation and packaging.
