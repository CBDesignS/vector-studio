# Vector Studio

**Remembered upload folder:** on browsers supporting `showOpenFilePicker` (such as desktop Chrome/Edge), the image chooser uses a consistent picker ID so the browser can reopen the last selected directory. The Cutting Lab shortcut now prefers **http://127.0.0.1:5179**, separate from the original app on port 5178. Browser privacy settings, private browsing, or clearing site data can reset folder history. Unsupported browsers use the ordinary file chooser and its own folder-history behavior. Drag and drop is unchanged. See [Chrome's picker documentation](https://developer.chrome.com/docs/capabilities/web-apis/file-system-access#specifying_a_suggested_directory_and_filename).

**Appearance:** choose **System**, **Light**, or **Dark** from the header. System is the default and follows your Windows/browser preference live. Each app remembers its own choice in a local preference cookie, including when its launch port changes. Image and SVG colors are unchanged; the preview uses a pale checkerboard to keep black cutting artwork visible.

## Cutting Lab

Cutting Lab is now the default version of Vector Studio on the **cricut-cutting-v2** branch. It makes SVG artwork for cutting machines. The older `main` branch remains available separately.

## Download and install

Download the **whole project ZIP** from [the default branch](https://github.com/CBDesignS/vector-studio), then extract it. Keep the folders together; do not download just one installer file.

| Computer | Double-click to install | Instructions |
| --- | --- | --- |
| Windows PC | `windows/Install.cmd` | [Windows guide](INSTALL.md) |
| Apple Silicon Mac (M1 or newer) | `macos/Install.command` | [Mac guide](MAC_INSTALL.md) |

The `windows` and `macos` folders keep platform-specific setup, run, and uninstall files separate. Shared app files stay in the project root. Moving the installer files this way does not require separate copies of the app.

**Mac setup:** downloads a private Python 3.12 and the tracing packages without Homebrew or administrator rights, then creates desktop **Run** and **Uninstall** shortcuts. No terminal commands need to be typed. macOS may ask for permission to open the downloaded script or access Desktop; see the Mac guide. Intel Macs and iPads are not supported by this installer.

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

Eleven backend tests cover real VTracer conversion, compound-path holes in binary and color modes, transparent inputs, physical sizing, optional backing, preview separation, invalid settings, upload limits, and launcher behavior. No new dependencies were added.

A local Flask + VTracer image-to-SVG app. All frontend assets are local; there are no paid APIs, accounts, external fonts, or runtime network calls. After installing dependencies, it works offline.

**Built and tested with 64-bit Python 3.12.** Python 3.11 is also accepted by the installer. Newer Python versions are not selected for this app because the pinned VTracer native package requires a compatible wheel. You can keep your newer Python and install 3.12 alongside it; Vector Studio uses its own environment. See [Python version guidance](INSTALL.md#python-312-is-the-recommended-version).

## Windows installer (recommended)

**[Full Windows installation guide → INSTALL.md](INSTALL.md)** — download, setup, desktop shortcut, updates, repair, uninstall, and troubleshooting.

On GitHub, click **Code → Download ZIP** to get all installer and app files together.

1. Download the project ZIP and **extract the entire ZIP** into a folder.
2. Double-click `windows/Install.cmd`. Do not run it from inside the ZIP.
3. Setup checks for 64-bit Python 3.11/3.12. If missing, it asks before installing Python 3.12 with Windows Package Manager. Review any installer or agreement prompts yourself. If Windows Package Manager is unavailable, setup explains how to install Python manually.
4. Confirm the app setup and dependency download. Setup copies the app to `%LOCALAPPDATA%\VectorStudioCuttingLab`, creates its own Python environment, installs the packages, runs the checks, and creates a **Vector Studio Cutting Lab** desktop shortcut.
5. Double-click the Cutting Lab shortcut. It starts the local app and opens your default browser, normally on port 5179. Keep the console window open; close it or press Ctrl+C to stop the server. Each launch starts a separate instance.

No Git, Node.js, Rust, paid API, or administrator account is needed for the normal per-user installation. Internet access is required for initial downloads. The batch files use a process-only PowerShell execution policy option; they do not change your saved Windows policy. Organization policies may still prevent scripts or installations.

**Updates and removal (package 2.1.0):** close the app, extract a newer ZIP outside the installation folder, and run its `windows/Install.cmd`. Setup detects an existing installation and offers **1: Update/repair**, **2: Clean reinstall**, or **3: Cancel**. Normal updates replace app files in the same `%LOCALAPPDATA%\VectorStudioCuttingLab` folder; they do not create nested version folders. Clean reinstall asks again before deleting that edition's entire folder. The original and Cutting Lab remain separate. See [update instructions](INSTALL.md#update-repair-or-clean-reinstall).

For a read-only component check, open PowerShell in the extracted folder and run:

```powershell
powershell.exe -NoProfile -File .\windows\Install.ps1 -CheckOnly
```

To uninstall, close the app and run `windows/Uninstall.cmd` from this edition's installation folder or extracted ZIP, or choose its **Uninstall** entry in Windows Start after running the updated installer. Confirm the displayed folder before removal. The app folder, private environment, and matching shortcuts are removed; Python and the other edition are kept. Move personal files out of the app folder first. See [uninstall instructions](INSTALL.md#uninstall). This is a script-based installer, not an Add/Remove Programs package.

The manual setup instructions below remain available for developers and Linux users. Mac users can use the [double-click installer](MAC_INSTALL.md).

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
