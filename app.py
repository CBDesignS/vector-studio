"""Local raster-to-SVG studio. Run with: python app.py"""
import io
import math
import tempfile
import warnings
from pathlib import Path
from threading import Lock

from flask import Flask, jsonify, render_template, request, send_from_directory
from PIL import Image, ImageOps, UnidentifiedImageError
import vtracer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 20_000_000
trace_lock = Lock()


def number(name, default, low, high, integer=True):
    try:
        value = float(request.form.get(name, default))
    except (ValueError, TypeError):
        raise ValueError(f'Invalid {name}.')
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'{name} must be between {low} and {high}.')
    return int(value) if integer else value


@app.get('/')
def index():
    return render_template('index.html')


@app.get('/favicon.ico')
def favicon():
    return send_from_directory(Path(app.static_folder) / 'icons', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.errorhandler(413)
def too_large(_):
    return jsonify(error='Choose an image smaller than 12 MB.'), 413


@app.post('/api/vectorize')
def vectorize():
    upload = request.files.get('image')
    if not upload:
        return jsonify(error='Choose an image first.'), 400
    try:
        precision = number('colors', 6, 1, 8)
        smoothing = number('smoothing', 60, 0, 180)
        speckle = number('speckle', 4, 0, 64)
        mode = request.form.get('mode', 'color')
        if mode not in ('color', 'binary'):
            raise ValueError('Choose color or black and white.')
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(upload.read())) as source:
                if source.format not in ('PNG', 'JPEG', 'WEBP', 'BMP'):
                    raise ValueError('Use a PNG, JPEG, WebP, or BMP image.')
                image = ImageOps.exif_transpose(source).convert('RGBA')
                original_size = image.size
                image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        # Bound concurrent native tracing work; each request has isolated files.
        if not trace_lock.acquire(blocking=False):
            return jsonify(error='A conversion is already running. Try again shortly.'), 429
        try:
            with tempfile.TemporaryDirectory(prefix='vector-studio-') as folder:
                inp, out = Path(folder) / 'input.png', Path(folder) / 'output.svg'
                image.save(inp)
                vtracer.convert_image_to_svg_py(
                    str(inp), str(out), colormode=mode, hierarchical='stacked',
                    mode='spline', color_precision=precision,
                    corner_threshold=smoothing, filter_speckle=speckle,
                    layer_difference=16, length_threshold=4.0,
                    max_iterations=10, splice_threshold=45, path_precision=3,
                )
                svg = out.read_text(encoding='utf-8')
        finally:
            trace_lock.release()
        return jsonify(svg=svg, width=image.width, height=image.height,
                       resized=original_size != image.size, bytes=len(svg.encode('utf-8')))
    except (ValueError, UnidentifiedImageError, OSError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        return jsonify(error=str(exc) if isinstance(exc, ValueError)
                       else 'This image cannot be read. Try a smaller PNG or JPEG.'), 400
    except Exception:
        app.logger.exception('Tracing failed')
        return jsonify(error='Tracing failed. Try a smaller image or fewer colors.'), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
