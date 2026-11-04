# Windows installation guide

[Back to README](README.md)

## Testing the Cutting Lab branch

Download this experimental version from [cricut-cutting-v2](https://github.com/CBDesignS/vector-studio/tree/cricut-cutting-v2), then choose **Code → Download ZIP**. Run `Install.cmd` from the extracted folder. It installs separately as **Vector Studio Cutting Lab**, leaving your original Vector Studio installation and shortcut in place.

Use transparency on for normal cut files. In single-color mode, white spaces become real holes. In color mode, the selected background color is removed everywhere, including intentional artwork of that color. Inspect **Cut boundaries**, confirm SVG size in millimetres, then import into Design Space and verify dimensions and layers. Preview strokes and red detail marks are never included in the downloaded SVG. The small-detail guide is an estimate from the thresholded raster before tracing; it is not a guarantee of cutting performance.

The original installation has been reported working by the user. This new branch has automated geometry tests, but still needs a full Windows install test and a physical Cricut test.

## Requirements

Use 64-bit Windows 10 or Windows 11 and an internet connection for initial setup. Python 3.11 or 3.12 is required; setup checks for it and asks before installing Python 3.12 if missing. No Git, Node.js, Rust, paid API, or administrator account is needed for the normal per-user installation.

### Python 3.12 is the recommended version

This app was built and tested with **64-bit Python 3.12**. The installer also accepts Python 3.11. It deliberately does not select newer versions because the pinned VTracer 0.6.15 native package needs a compatible prebuilt wheel; a newer Python installation alone does not satisfy this app's setup requirements.

**Already have a newer Python installed? Keep it.** Accept the installer's offer to install Python 3.12 alongside it. Setup uses a compatible interpreter to create Vector Studio's separate `.venv` environment. It does not uninstall your existing Python or intentionally change your system's default Python version. If compatible Python 3.11 is already present, setup may use it rather than installing 3.12.

If installing Python manually, choose **64-bit Python 3.12**, include pip, and rerun `Install.cmd`.

## Download and install

1. Sign in to GitHub and open [CBDesignS/vector-studio](https://github.com/CBDesignS/vector-studio).
2. Click **Code → Download ZIP**.
3. Right-click the downloaded ZIP and choose **Extract All**. Keep all project files together.
4. Open the extracted folder containing `Install.cmd` and double-click it. Do not run it from inside the ZIP.
5. If Python is missing, confirm whether to install Python 3.12 using Windows Package Manager. Review any package or agreement prompts yourself. If Windows Package Manager is unavailable, install 64-bit Python 3.12 from [python.org](https://www.python.org/downloads/windows/), include pip, and rerun setup.
6. Confirm the app setup and dependency download when prompted.
7. Wait for the checks to pass and the **Installed successfully** message.

Setup copies the app into `%LOCALAPPDATA%\VectorStudioCuttingLab`, creates a separate Python environment, installs Flask, Pillow, VTracer and their dependencies, runs app checks including actual SVG conversions, and creates a **Vector Studio Cutting Lab** desktop shortcut. Nothing is installed without the setup prompts being accepted. You can delete the extracted download folder after successful installation.

## Run and stop

Double-click **Vector Studio Cutting Lab** on your desktop. A console window starts the server and opens your default browser. Keep the console open while using the app. Close it or press **Ctrl+C** to stop the server.

If the browser does not open automatically, copy the local address printed in the console into your browser. The launcher chooses a free local port, so the address may change on each launch. Each shortcut launch starts a separate instance; close extra console windows if needed.

You can also run `%LOCALAPPDATA%\VectorStudioCuttingLab\Run.cmd` directly. The app listens only on this computer and works offline after dependencies are installed. It does not run at Windows sign-in or install a background service.

## Check components without installing

Open PowerShell in the extracted project folder and run:

```powershell
powershell.exe -NoProfile -File .\windows\Install.ps1 -CheckOnly
```

This reports the compatible Python installation and whether the app dependencies are ready. It does not install anything, copy files, or create a shortcut. If your Windows policy blocks scripts, follow your organization’s policy or use the [manual setup](README.md#1-install-python).

## Update or repair

To repair missing dependencies, close the app and rerun `Install.cmd` in `%LOCALAPPDATA%\VectorStudioCuttingLab`.

To update the app, download a fresh project ZIP from GitHub, extract it, close the running app, and run the new `Install.cmd`. After confirmation, setup replaces app source files in the installation folder. It checks existing dependencies and installs them if needed. This is a manual update process without automatic rollback.

## Uninstall

1. Close the Vector Studio console window.
2. Delete `%LOCALAPPDATA%\VectorStudioCuttingLab`.
3. Delete the **Vector Studio Cutting Lab** desktop shortcut.

Python is left installed because other applications may use it. The app is not registered in Windows Add/Remove Programs.

## Troubleshooting

| Problem | What to do |
| --- | --- |
| Setup reports missing files | Extract the complete ZIP. Do not download only `Install.cmd` or the PowerShell script. |
| Python installation fails | Review the Windows Package Manager message. Alternatively install 64-bit Python 3.12 from python.org with pip, then rerun setup. |
| Dependency download fails | Check internet access and any organization download restrictions, then rerun setup. Setup requires prebuilt packages and does not install a compiler. |
| Shortcut is missing | Read the setup error. If the app checks passed, try `Run.cmd` in the installation folder. |
| Browser shows a connection error | Check that the console is still open and use the exact local address it prints. |
| Scripts are blocked by organization policy | Ask your administrator or use the manual setup if permitted. Setup does not override organization policies. |

This is a script-based installer, not a signed `.exe`. The batch file uses a process-only PowerShell execution policy option and does not change your saved Windows policy. Windows may show a downloaded-file warning; follow your normal security policies.

## Verification status

Ten app tests pass, including real color and black-and-white tracing and the desktop launcher test. PowerShell syntax and read-only component discovery have been checked. A complete first-time Windows installation, Python download, and desktop shortcut creation still need testing on a regular Windows installation.
