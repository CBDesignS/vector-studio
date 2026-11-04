# Vector Studio

A local Flask + VTracer image-to-SVG app. All frontend assets are local; there are no paid APIs, accounts, external fonts, or runtime network calls. After installing dependencies, it works offline.

**Built and tested with 64-bit Python 3.12.** Python 3.11 is also accepted by the installer. Newer Python versions are not selected for this app because the pinned VTracer native package requires a compatible wheel. You can keep your newer Python and install 3.12 alongside it; Vector Studio uses its own environment. See [Python version guidance](INSTALL.md#python-312-is-the-recommended-version).

## Windows installer (recommended)

**[Full Windows installation guide → INSTALL.md](INSTALL.md)** — download, setup, desktop shortcut, updates, repair, uninstall, and troubleshooting.

On GitHub, click **Code → Download ZIP** to get all installer and app files together.

1. Download the project ZIP and **extract the entire ZIP** into a folder.
2. Double-click `Install.cmd`. Do not run it from inside the ZIP.
3. Setup checks for 64-bit Python 3.11/3.12. If missing, it asks before installing Python 3.12 with Windows Package Manager. Review any installer or agreement prompts yourself. If Windows Package Manager is unavailable, setup explains how to install Python manually.
4. Confirm the app setup and dependency download. Setup copies the app to `%LOCALAPPDATA%\VectorStudio`, creates its own Python environment, installs the packages, runs the checks, and creates a **Vector Studio** desktop shortcut.
5. Double-click the shortcut. It starts the local app and opens your default browser on a free local port. Keep the console window open; close it or press Ctrl+C to stop the server. Each launch starts a separate instance.

No Git, Node.js, Rust, paid API, or administrator account is needed for the normal per-user installation. Internet access is required for initial downloads. The batch files use a process-only PowerShell execution policy option; they do not change your saved Windows policy. Organization policies may still prevent scripts or installations.

Rerun the installed `Install.cmd` to check or repair dependencies. To update the app, extract a newer project ZIP and run its `Install.cmd` (close the running app first). Existing app source files are replaced after confirmation; this is not an automatic updater or a rollback installer.

For a read-only component check, open PowerShell in the extracted folder and run:

```powershell
powershell.exe -NoProfile -File .\windows\Install.ps1 -CheckOnly
```

To uninstall, close the app and remove `%LOCALAPPDATA%\VectorStudio` and the desktop shortcut. Python is left installed because other applications may use it. This is a script-based installer, not a signed `.exe` or an Add/Remove Programs package. Windows may show a downloaded-file warning; follow your normal security policies.

The manual setup instructions below remain available for developers and macOS/Linux users.

## 1. Install Python

Use **Python 3.12 (64-bit)** with pip to match the tested setup. Python 3.11 is also accepted by the installer. Keep any newer Python installation; install 3.12 alongside it if needed. On Windows, adding Python to PATH is optional for the installer, which also discovers standard installation locations.

For manual setup when multiple versions are installed, select 3.12 explicitly on Windows:

```powershell
py -3.12 -m venv .venv
```

On macOS/Linux, use `python3.12 -m venv .venv` when that interpreter is available. The generic `python` command below is suitable only if it resolves to a compatible version.

## 2. Open a terminal in this folder

Create a virtual environment:

```powershell
python -m venv .venv
```

## 3. Install dependencies

Windows PowerShell (no activation required):

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS / Linux:

```sh
.venv/bin/python -m pip install -r requirements.txt
```

Dependency installation requires internet access once. If pip cannot find a VTracer wheel, use Python 3.11 or 3.12 rather than a newer Python version. Building VTracer from source requires Rust.

## 4. Start the app

Windows:

```powershell
.\.venv\Scripts\python.exe app.py
```

macOS / Linux:

```sh
.venv/bin/python app.py
```

Open **http://127.0.0.1:5000** in your browser. Keep the terminal open; press Ctrl+C to stop. The server listens only on this computer, with Flask debugging disabled. This is a local development app, not a public hosting setup.

## 5. Trace an image

1. Drop a PNG, JPEG, WebP, or BMP into the upload area, or click to browse.
2. The image converts automatically. Adjust the sliders to update the preview after a short pause.
3. Choose full color or black and white. Color precision is disabled in black-and-white mode.
4. Click **Download SVG** to save the current result. Downloads remain disabled while settings are pending, so you never download an out-of-date trace.

### Settings

| Control | VTracer option | Meaning |
| --- | --- | --- |
| Color precision | `color_precision`, 1–8 | Significant bits per channel. Lower values combine more colors; this is not an exact palette-size setting. |
| Curve smoothing | `corner_threshold`, 0–180 | Higher corner thresholds classify fewer bends as corners, creating a softer trace. This does not guarantee a particular path count. |
| Remove speckles | `filter_speckle`, 0–64 | Discards small patches; higher values remove more fine details. |
| Trace mode | `colormode` | Color or binary black-and-white tracing. |

Logos, icons, and flat illustrations generally trace more cleanly than photographs. Transparent PNG input is preserved when normalizing to RGBA; edge appearance depends on the source and VTracer's tracing. SVGs are displayed through image elements, not injected as page markup.

## How the code fits together

1. `templates/index.html`: accessible upload area, settings, comparison panels, and download control.
2. `static/style.css`: responsive layout, checkerboard previews, and local system fonts.
3. `static/app.js`: file selection, preview object URLs, debounced updates, serialized requests, stale-result protection, and SVG download.
4. `app.py`: validates image data and settings, applies EXIF orientation, normalizes to PNG, calls VTracer, and returns SVG JSON. Each conversion uses temporary files that are removed afterward.

Uploads are limited to 12 MB and 20 million decoded pixels. Images larger than 1600 px on either side are proportionally reduced before tracing. One conversion runs at a time; additional clients receive a retry message. There is no persistent image storage. A complex trace can take time; there is no hard execution timeout on native tracing.

## Run the checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The checks use real VTracer conversions and cover both modes, invalid input, settings bounds, and request limits.

VTracer's Python API is pinned to `0.6.15` because newer development versions use a different configuration API. Reference: https://pypi.org/project/vtracer/0.6.15/
