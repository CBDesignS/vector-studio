# Vector Studio

A local Flask + VTracer image-to-SVG app. All frontend assets are local; there are no paid APIs, accounts, external fonts, or runtime network calls. After installing dependencies, it works offline.

## 1. Install Python

Use Python 3.11 or 3.12 (64-bit), with pip. These versions are recommended for compatibility with VTracer's prebuilt native package. On Windows, enable “Add Python to PATH” during installation.

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
