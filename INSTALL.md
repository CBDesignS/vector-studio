# Windows installation guide

[Back to README](README.md) · [Mac installation guide](MAC_INSTALL.md)

**New folder layout:** all Windows setup, run, and uninstall files now live in `windows/`. Keep this folder beside the shared app files. Old desktop shortcuts are refreshed by setup; root-level launchers left by an older installed version may remain for compatibility. You do not need to remove the old installation before choosing Update/repair.

**Upload-folder memory:** the Cutting Lab shortcut now prefers `http://127.0.0.1:5179`, separately from the original version on port 5178. Supported browsers such as desktop Chrome/Edge can reopen the last selected image directory. The first selection uses the browser's default folder. Keep using the same browser/profile and the printed app address. If port 5179 is occupied, the launcher falls back to a free port and prints a notice; folder memory may differ on that address. Unsupported browsers use their standard file picker. Clearing browser data or using private mode can reset remembered folders. Only the image you select is read; this feature does not scan or upload your directory.

**Identify this version:** Cutting Lab has an **amber scissors icon** in the browser, app header, and desktop shortcut. The original Vector Studio uses a **green vector-node icon**. To update an existing Cutting Lab installation, download a fresh ZIP from `cricut-cutting-v2`, extract it, close the app, and rerun `windows/Install.cmd`. Setup copies the icon files and refreshes its desktop shortcut. Restart the app/browser tab afterward; Windows may take a moment to refresh its icon cache.

## Cutting Lab (default version)

Download the current version from [cricut-cutting-v2](https://github.com/CBDesignS/vector-studio/tree/cricut-cutting-v2), then choose **Code → Download ZIP**. Run `windows/Install.cmd` from the extracted folder. It installs separately as **Vector Studio Cutting Lab**, leaving your original Vector Studio installation and shortcut in place.

Use transparency on for normal cut files. In single-color mode, white spaces become real holes. In color mode, the selected background color is removed everywhere, including intentional artwork of that color. Inspect **Cut boundaries**, confirm SVG size in millimetres, then import into Design Space and verify dimensions and layers. Preview strokes and red detail marks are never included in the downloaded SVG. The small-detail guide is an estimate from the thresholded raster before tracing; it is not a guarantee of cutting performance.

The original installation has been reported working by the user. The tracing has been checked by the user in Cricut Design Space. A physical Cricut cut and the revised installer flow still need testing.

## Requirements

Use 64-bit Windows 10 or Windows 11 and an internet connection for initial setup. Python 3.11 or 3.12 is required; setup checks for it and asks before installing Python 3.12 if missing. No Git, Node.js, Rust, paid API, or administrator account is needed for the normal per-user installation.

### Python 3.12 is the recommended version

This app was built and tested with **64-bit Python 3.12**. The installer also accepts Python 3.11. It deliberately does not select newer versions because the pinned VTracer 0.6.15 native package needs a compatible prebuilt wheel; a newer Python installation alone does not satisfy this app's setup requirements.

**Already have a newer Python installed? Keep it.** Accept the installer's offer to install Python 3.12 alongside it. Setup uses a compatible interpreter to create Vector Studio's separate `.venv` environment. It does not uninstall your existing Python or intentionally change your system's default Python version. If compatible Python 3.11 is already present, setup may use it rather than installing 3.12.

If installing Python manually, choose **64-bit Python 3.12**, include pip, and rerun `windows/Install.cmd`.

## Download and install

1. Sign in to GitHub and open [CBDesignS/vector-studio](https://github.com/CBDesignS/vector-studio).
2. Click **Code → Download ZIP**.
3. Right-click the downloaded ZIP and choose **Extract All**. Keep all project files together.
4. Open the extracted project folder, open `windows`, and double-click `Install.cmd`. Do not run it from inside the ZIP.
5. If Python is missing, confirm whether to install Python 3.12 using Windows Package Manager. Review any package or agreement prompts yourself. If Windows Package Manager is unavailable, install 64-bit Python 3.12 from [python.org](https://www.python.org/downloads/windows/), include pip, and rerun setup.
6. Confirm the app setup and dependency download when prompted.
7. Wait for the checks to pass and the **Installed successfully** message.

Setup copies the app into `%LOCALAPPDATA%\VectorStudioCuttingLab`, creates a separate Python environment, installs Flask, Pillow, VTracer and their dependencies, runs app checks including actual SVG conversions, and creates a **Vector Studio Cutting Lab** desktop shortcut. Nothing is installed without the setup prompts being accepted. You can delete the extracted download folder after successful installation.

## Run and stop

Double-click **Vector Studio Cutting Lab** on your desktop. A console window starts the server and opens your default browser. Keep the console open while using the app. Close it or press **Ctrl+C** to stop the server.

If the browser does not open automatically, copy the local address printed in the console into your browser. The launcher prefers port 5179 and falls back to a free port only if it is unavailable. Each shortcut launch starts a separate instance; close extra console windows if needed.

You can also run `%LOCALAPPDATA%\VectorStudioCuttingLab\windows\Run.cmd` directly. The app listens only on this computer and works offline after dependencies are installed. It does not run at Windows sign-in or install a background service.

## Check components without installing

Open PowerShell in the extracted project folder and run:

```powershell
powershell.exe -NoProfile -File .\windows\Install.ps1 -CheckOnly
```

This reports the compatible Python installation and whether the app dependencies are ready. It does not install anything, copy files, or create a shortcut. If your Windows policy blocks scripts, follow your organization’s policy or use the [manual setup](README.md#1-install-python).

## Update, repair, or clean reinstall

This package is **2.1.0**. Each edition uses one fixed folder: `%LOCALAPPDATA%\VectorStudioCuttingLab`. Updates do **not** create nested folders or a separate folder for every version. Original Vector Studio and Cutting Lab use different folders and can stay installed together.

Close the app's console window, download the new ZIP from this edition's branch, extract it **outside the installation folder**, and run its `windows/Install.cmd`. When an existing installation is found, setup asks:

1. **Update/repair:** replace app files in the same folder and keep the private Python environment. Dependencies are checked and repaired when needed.
2. **Clean reinstall:** remove this edition's previous app folder, then install a fresh copy. A second confirmation is required. Move any personal files stored inside the app folder elsewhere first; the entire folder will be deleted.
3. **Cancel:** leave the installation alone. Pressing Enter also cancels.

Use option 1 for normal updates. To repair the current version, you can run the installed `windows/Install.cmd` and select option 1. Clean reinstall must run from a separate extracted ZIP because setup cannot delete the folder it is running from.

Setup records the installed package version. Older installations are recognized by their app files and private environment and appear as earlier/unversioned. This is a manual update process without automatic rollback; if a clean installation fails after removal, rerun setup to finish installing. Setup manages only this edition's standard folder and refuses unrecognized contents or linked folders. Close all running app instances before updating or removing it.

## Uninstall

1. Close this edition's console window.
2. Open **Uninstall** for this edition from its Windows Start folder, or double-click `windows/Uninstall.cmd` in its installation folder. You can also run `windows/Uninstall.cmd` from a newly extracted ZIP of the **same edition**, including to remove an older installation.
3. Check the folder displayed and type **y** to confirm. Enter or **n** cancels.

The script removes `%LOCALAPPDATA%\VectorStudioCuttingLab`, including its private Python environment and **any personal files saved inside it**, plus matching desktop and Start menu shortcuts. It keeps your installed Python, the other edition, downloaded source ZIPs, browser preferences, and files outside the app folder. No administrator account is needed for normal per-user removal.

Start menu entries are created when you run this updated installer. The app is not registered in Windows Add/Remove Programs. Custom/manual installations outside the standard folder must be removed manually; the script deliberately refuses to delete arbitrary locations.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Setup reports missing files | Extract the complete ZIP. Do not download only `windows/Install.cmd` or the PowerShell script. |
| Python installation fails | Review the Windows Package Manager message. Alternatively install 64-bit Python 3.12 from python.org with pip, then rerun setup. |
| Dependency download fails | Check internet access and any organization download restrictions, then rerun setup. Setup requires prebuilt packages and does not install a compiler. |
| Shortcut is missing | Read the setup error. If the app checks passed, try `windows/Run.cmd` in the installation folder. |
| Browser shows a connection error | Check that the console is still open and use the exact local address it prints. |
| Scripts are blocked by organization policy | Ask your administrator or use the manual setup if permitted. Setup does not override organization policies. |

This is a script-based installer, not a signed `.exe`. The batch file uses a process-only PowerShell execution policy option and does not change your saved Windows policy. Windows may show a downloaded-file warning; follow your normal security policies.

## Verification status

Eleven app tests pass, including real color and black-and-white tracing and the desktop launcher test. PowerShell syntax, read-only component discovery, and removal safeguards have been checked. Uninstall self-removal was exercised in a disposable workspace folder with shortcut removal mocked; real desktop/Start shortcut removal and junction handling still need a normal Windows test. A complete first-time Windows installation, Python download, and desktop shortcut creation still need testing on a regular Windows installation.

