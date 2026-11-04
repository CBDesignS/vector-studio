# Vector Studio

## Cutting Lab — experimental branch

This is **cricut-cutting-v2**, an experimental version aimed at SVG artwork for cutting machines. The working `main` branch is unchanged. The Windows installer uses a separate `%LOCALAPPDATA%\VectorStudioCuttingLab` folder and **Vector Studio Cutting Lab** desktop shortcut, so you can test it alongside the original app.

Open [this branch](https://github.com/CBDesignS/vector-studio/tree/cricut-cutting-v2), choose **Code → Download ZIP**, extract the whole ZIP, and run **Install.cmd**. See [INSTALL.md](INSTALL.md).

### What changed

- **Transparency on by default**, with a checkbox to keep a background instead.
- **Single-color cut mode** defaults to keeping small details. Threshold and inversion controls let you choose dark or light artwork.
- **Real holes in filled paths**, rather than white overlays. Color mode uses cutout geometry and removes the selected background color throughout the artwork; pick the color and adjust tolerance. It is color-key removal, not automatic subject recognition.
- **Trim empty margins** and set the exported SVG width in **millimetres**. Height is proportional. With trim off, width includes the canvas margins. Confirm imported size in Design Space.
- **Filled / cut boundaries / small-detail guide** views and zoom. These are previews; the download always contains filled artwork, never the preview strokes or guide marks.
- **Small-detail guide** highlights estimated thin foreground areas and narrow gaps in red at the requested physical size. It uses raster morphology, so corners may be marked and details may be missed. It is not an exact cutter simulation. Material, blade, and weeding technique still matter.
- Choose **smooth curves or straight segments**, **1600/3200 px** processing, and optional **2×/4× interpolation** for tiny source images. Interpolation cannot reconstruct missing artwork. Higher quality can take longer and use more memory.

For the football trophy, start with single-color mode, transparency on, speckles at 0, and try threshold and 4× detail boost. Automatic tracing still cannot reliably redraw individual laces or force a stand into ideal geometry. A node editor and automatic geometry reconstruction are not included in this experiment.

### Cutting workflow

1. Upload artwork and inspect the filled SVG against the original.
2. Adjust threshold, smoothing, and speckle filtering; choose the intended width.
3. Inspect **Cut boundaries** for unwanted islands and holes. Try **Small-detail guide** in single-color mode; red marks are advisory.
4. Download and import the SVG into Cricut Design Space. Verify the dimensions, layer count, and cut preview before a small test cut. This branch has not yet been verified on a physical Cricut.

Transparency off intentionally adds/keeps a background shape that may itself cut. Color layers can have coincident boundaries; inspect layer behavior in Design Space. Existing transparency is composited onto the selected background color before tracing; with transparency enabled, that color is then removed. Color-key removal also removes intentional artwork of that same color.

### Validation

Ten backend tests cover real VTracer conversion, compound-path holes in binary and color modes, transparent inputs, physical sizing, optional backing, preview separation, invalid settings, upload limits, and launcher behavior. No new dependencies were added.

A local Flask + VTracer image-to-SVG app. All frontend assets are local; there are no paid APIs, accounts, external fonts, or runtime network calls. After installing dependencies, it works offline.

**Built and tested with 64-bit Python 3.12.** Python 3.11 is also accepted by the installer. Newer Python versions are not selected for this app because the pinned VTracer native package requires a compatible wheel. You can keep your newer Python and install 3.12 alongside it; Vector Studio uses its own environment. See [Python version guidance](INSTALL.md#python-312-is-the-recommended-version).

## Windows installer (recommended)

**[Full Windows installation guide → INSTALL.md](INSTALL.md)** — download, setup, desktop shortcut, updates, repair, uninstall, and troubleshooting.

On GitHub, click **Code → Download ZIP** to get all installer and app files together.

1. Download the project ZIP and **extract the entire ZIP** into a folder.
2. Double-click `Install.cmd`. Do not run it from inside the ZIP.
3. Setup checks for 64-bit Python 3.11/3.12. If missing, it asks before installing Python 3.12 with Windows Package Manager. Review any installer or agreement prompts yourself. If Windows Package Manager is unavailable, setup explains how to install Python manually.
4. Confirm the app setup and dependency download. Setup copies the app to `%LOCALAPPDATA%\VectorStudioCuttingLab`, creates its own Python environment, installs the packages, runs the checks, and creates a **Vector Studio Cutting Lab** desktop shortcut.
5. Double-click the Cutting Lab shortcut. It starts the local app and opens your default browser on a free local port. Keep the console window open; close it or press Ctrl+C to stop the server. Each launch starts a separate instance.

No Git, Node.js, Rust, paid API, or administrator account is needed for the normal per-user installation. Internet access is required for initial downloads. The batch files use a process-only PowerShell execution policy option; they do not change your saved Windows policy. Organization policies may still prevent scripts or installations.

Rerun the installed `Install.cmd` to check or repair dependencies. To update the app, extract a newer project ZIP and run its `Install.cmd` (close the running app first). Existing app source files are replaced after confirmation; this is not an automatic updater or a rollback installer.

For a read-only component check, open PowerShell in the extracted folder and run:

```powershell
powershell.exe -NoProfile -File .\windows\Install.ps1 -CheckOnly
```

To uninstall, close the app and remove `%LOCALAPPDATA%\VectorStudioCuttingLab` and the desktop shortcut. Python is left installed because other applications may use it. This is a script-based installer, not a signed `.exe` or an Add/Remove Programs package. Windows may show a downloaded-file warning; follow your normal security policies.

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

Logos, icons, and flat illustrations generally trace more cleanly than photographs. Transparent pixels are excluded in single-color mode; color mode uses the selected background key as described above. SVGs are displayed through image elements, not injected as page markup.

## How the code fits together

1. `templates/index.html`: accessible upload area, settings, comparison panels, and download control.
2. `static/style.css`: responsive layout, checkerboard previews, and local system fonts.
3. `static/app.js`: file selection, preview object URLs, debounced updates, serialized requests, stale-result protection, and SVG download.
4. `app.py`: validates image data and settings, applies EXIF orientation, normalizes to PNG, calls VTracer, and returns SVG JSON. Each conversion uses temporary files that are removed afterward.

Uploads are limited to 12 MB and 20 million decoded pixels. Images larger than the selected 1600/3200 px limit are proportionally reduced before tracing. One conversion runs at a time; additional clients receive a retry message. There is no persistent image storage. A complex trace can take time; there is no hard execution timeout on native tracing.

## Run the checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The checks use real VTracer conversions and cover both modes, invalid input, settings bounds, and request limits.

VTracer's Python API is pinned to `0.6.15` because newer development versions use a different configuration API. Reference: https://pypi.org/project/vtracer/0.6.15/
