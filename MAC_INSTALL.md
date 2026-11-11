# Install Vector Studio Cutting Lab on a Mac

[Back to README](README.md) · [Windows instructions](INSTALL.md)

## What you need

An **Apple Silicon Mac (M1, M2, M3, M4 or newer)** running macOS 11 or later, and internet access for setup. This script installer does not support Intel Macs or iPads. Initial installation needs free space for a private Python environment and its packages; allow about 1 GB during setup.

No Homebrew, Git, Rust, administrator password, or separately installed Python is needed. Setup downloads its own Python 3.12 using Astral's uv. It keeps everything in your account, without changing your normal Python, PATH, shell settings, or security settings.

## Install — no commands to type

1. Open [Vector Studio on GitHub](https://github.com/CBDesignS/vector-studio). Choose **Code → Download ZIP**.
2. Double-click the ZIP to extract the **entire project**. Keep all the folders together.
3. Open the extracted folder, then open **macos**.
4. Double-click **Install.command** and click **Install** in the confirmation box.
5. Leave the Terminal window open while it downloads components and checks the app. Wait for **Installed successfully**.
6. On your Desktop, double-click **Vector Studio Cutting Lab.command**. Your browser opens the app.

Setup brings its confirmation and completion dialogs forward. If a macOS permission prompt appears during setup, answer it before continuing. Terminal opens automatically to show progress; you do not type commands into it. If macOS asks whether Terminal may access Desktop or Downloads, allow access to those folders to install from Downloads and create the desktop shortcuts. If you decline, setup may stop; rerun after granting the relevant folder access.

The installer folder must remain alongside `app.py`, `requirements.txt`, `static`, `templates`, and `tests`. Downloading just `Install.command` will not work.

## If macOS blocks the first launch

These are unsigned scripts, not an Apple-notarised app. Depending on your macOS version, an initial **Control-click → Open** may be enough. If macOS still blocks it, review the notice in **System Settings → Privacy & Security** and follow [Apple's instructions for opening an app from an unknown developer](https://support.apple.com/en-gb/guide/mac-help/mh40616/mac), only if you trust this download. Do not disable Gatekeeper or remove quarantine attributes globally; setup does neither.

The repository marks `.command` files executable and the provided project ZIP preserves those permissions. If a different downloader strips permissions and Finder reports that the file cannot execute, use the supplied ZIP and macOS's built-in Archive Utility instead. If it still fails, send us the message; a typed command should not be part of the normal setup.

## Run and stop

Double-click **Vector Studio Cutting Lab.command** on the Desktop. It opens the same local browser app as Windows, normally at `http://127.0.0.1:5179`. If that port is occupied, the launcher chooses a free one and prints its address.

Keep its Terminal window open. Close it, confirming termination if asked, or press **Control+C** to stop the app. Closing only the browser tab does not stop the server. Nothing runs at login and no background service is installed. After setup, image conversion works offline; images stay on the Mac. Browser folder memory depends on browser support; Safari may use its ordinary image chooser.

## Update or repair

Close every app console window. Download and extract a newer complete ZIP, open its `macos` folder, and double-click **Install.command** again. Click **Install** to confirm replacing app files.

Setup updates the same folder, checks/downloads its private Python, installs the required packages, runs real conversion tests, and refreshes the desktop shortcuts. It does not create a folder for each version. Mac setup offers update/repair or Cancel; for a clean installation, uninstall first, then install the new download. There is no automatic rollback. A failed setup can leave a partial private environment; rerunning setup normally completes it.

## Uninstall

1. Close all Vector Studio console windows.
2. Double-click **Uninstall Vector Studio Cutting Lab.command** on the Desktop. Alternatively, open the extracted project's `macos` folder and double-click **Uninstall.command**.
3. Review the folder in the confirmation box and click **Uninstall**, or **Cancel** to keep it.

This permanently removes `~/Library/Application Support/VectorStudioCuttingLab`, including its private Python, packages, and **any personal files you saved inside that folder**, plus this app's matching desktop launchers. Move personal files elsewhere first. Your system Python, the source download, browser preferences, other applications, and exported SVGs outside that folder are kept. Removal works offline.

## Where things are stored

| Item | Location |
| --- | --- |
| App, private environment, Python runtime | `~/Library/Application Support/VectorStudioCuttingLab` |
| Start and uninstall shortcuts | Desktop, as `.command` files with the Cutting Lab icon |
| Installer source | `macos/` in the extracted project |

Uninstall refuses unrecognised installation folders or redirected installation paths. It manages only the standard folder in the current account. It never removes a shared Python installation.

## Troubleshooting

| Message or problem | What to do |
| --- | --- |
| Intel Mac not supported | This first Mac installer targets Apple Silicon only. It will stop without attempting a source build. |
| Download or package installation failed | Check internet access, close the app, and rerun Install.command. GitHub and PyPI must be reachable. |
| Desktop permission denied | Allow the requested folder access in macOS Privacy & Security, then rerun setup. |
| App is running | Close every app console window, then retry setup/removal. |
| Another setup or removal may be running | Close that window first. After a forced termination, an empty `~/Library/Application Support/.VectorStudioCuttingLab-maintenance` folder can remain. With no setup/app running, use Finder's **Go → Go to Folder** to open its parent and remove only that empty lock folder, or send us the message for help. |
| Environment is damaged | Run Install.command again. If repair still fails, uninstall from the extracted ZIP and install afresh. |

## Downloads and verification

Bootstrap downloads **uv 0.13.7** from [Astral's official GitHub release](https://github.com/astral-sh/uv/releases/tag/0.13.7) and checks the archive against its pinned SHA-256 before running it. uv downloads a managed Python 3.12 from Astral's python-build-standalone distribution and uses checksummed metadata. App dependencies come from PyPI, with binary packages required; no compiler is installed. See [uv's Python management documentation](https://docs.astral.sh/uv/guides/install-python/).

This is the first Mac installer release. Automated tests cover file placement and safeguards; the GitHub Mac check covers shell syntax and real tracing dependencies. Interactive Finder, privacy permissions, desktop launching, and uninstall confirmation still require testing on a normal Mac. It is not signed or notarised by Apple.
