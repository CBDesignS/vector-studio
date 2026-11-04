"""Local raster-to-SVG studio. Run with: python app.py"""
import io
import math
import tempfile
import warnings
import base64
import copy
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from threading import Lock

from flask import Flask, jsonify, render_template, request, send_from_directory
from PIL import Image, ImageOps, ImageChops, ImageFilter, UnidentifiedImageError
import vtracer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024
Image.MAX_IMAGE_PIXELS = 20_000_000
trace_lock = Lock()
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)


def choice(name, default, options):
    value = request.form.get(name, default)
    if value not in options:
        raise ValueError(f'Invalid {name}.')
    return value


def flag(name, default='0'):
    return choice(name, default, ('0', '1')) == '1'


def detail_guide(mask, width_mm, minimum_mm):
    """Raster estimate only: highlight thin foreground and narrow internal gaps."""
    mask = mask.copy()
    mask.thumbnail((768, 768), Image.Resampling.NEAREST)
    requested = max(3, int(round(minimum_mm * mask.width / width_mm)) | 1)
    kernel = min(31, requested)
    # Padding avoids treating canvas edges as infinitely thick features.
    pad = kernel
    padded = ImageOps.expand(mask, border=pad, fill=0)
    opened = padded.filter(ImageFilter.MinFilter(kernel)).filter(ImageFilter.MaxFilter(kernel))
    closed = padded.filter(ImageFilter.MaxFilter(kernel)).filter(ImageFilter.MinFilter(kernel))
    crop = (pad, pad, pad + mask.width, pad + mask.height)
    thin = ImageChops.subtract(mask, opened.crop(crop))
    gaps = ImageChops.subtract(closed.crop(crop), mask)
    marks = ImageChops.lighter(thin, gaps)
    guide = Image.new('RGBA', mask.size, (0, 0, 0, 0))
    guide.paste((35, 60, 46, 255), mask=mask)
    guide.paste((225, 65, 54, 255), mask=marks)
    output = io.BytesIO()
    guide.save(output, format='PNG')
    return ('data:image/png;base64,' + base64.b64encode(output.getvalue()).decode(),
            marks.getbbox() is not None, requested > kernel)


def finish_svg(svg, size, width_mm, remove_background, background):
    root = ET.fromstring(svg)
    for path in list(root):
        if path.tag != f'{{{SVG}}}path':
            continue
        fill = path.get('fill', '').lower()
        if not path.get('d', '').strip() or (remove_background and fill == background.lower()):
            root.remove(path)
            continue
        path.set('fill-rule', 'evenodd')
    paths = root.findall(f'{{{SVG}}}path')
    if not paths:
        raise ValueError('No artwork remains. Adjust threshold or background tolerance.')
    if any(not p.get('d', '').rstrip().upper().endswith('Z') for p in paths):
        raise ValueError('Tracing produced an open path. Try a different curve setting.')
    root.set('viewBox', f'0 0 {size[0]} {size[1]}')
    root.set('width', f'{width_mm:g}mm')
    height_mm = width_mm * size[1] / size[0]
    root.set('height', f'{height_mm:.4f}mm')
    root.set('version', '1.1')
    outline = copy.deepcopy(root)
    for path in outline:
        path.set('fill', 'none')
        path.set('stroke', '#244e3c')
        path.set('stroke-width', '1')
        path.set('vector-effect', 'non-scaling-stroke')
    return (ET.tostring(root, encoding='unicode'),
            ET.tostring(outline, encoding='unicode'), len(paths), height_mm)


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
        speckle = number('speckle', 0, 0, 64)
        mode = choice('mode', 'binary', ('color', 'binary'))
        fitting = choice('fitting', 'spline', ('spline', 'polygon'))
        threshold = number('threshold', 160, 1, 254)
        tolerance = number('tolerance', 20, 0, 100)
        width_mm = number('width_mm', 100, 5, 2000, integer=False)
        minimum_mm = number('minimum_mm', 0.5, 0.1, 5, integer=False)
        quality = int(choice('quality', '1600', ('1600', '3200')))
        upscale = int(choice('upscale', '1', ('1', '2', '4')))
        transparent = flag('transparent', '1')
        invert = flag('invert')
        trim = flag('trim', '1')
        background = request.form.get('background', '#ffffff')
        if not re.fullmatch(r'#[0-9a-fA-F]{6}', background):
            raise ValueError('Invalid background color.')
        bg_rgb = tuple(int(background[i:i+2], 16) for i in (1, 3, 5))
        notices = []
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(upload.read())) as source:
                if source.format not in ('PNG', 'JPEG', 'WEBP', 'BMP'):
                    raise ValueError('Use a PNG, JPEG, WebP, or BMP image.')
                image = ImageOps.exif_transpose(source).convert('RGBA')
                original_size = image.size
                image.thumbnail((quality, quality), Image.Resampling.LANCZOS)
        reduced = original_size != image.size
        if reduced:
            notices.append(f'Large image reduced to fit {quality} px.')
        source_alpha = image.getchannel('A').point(lambda x: 255 if x >= 128 else 0)
        matte = Image.new('RGBA', image.size, (*bg_rgb, 255))
        image = Image.alpha_composite(matte, image).convert('RGB')
        if mode == 'binary':
            gray = image.convert('L')
            mask = gray.point(lambda x: 255 if (x >= threshold if invert else x < threshold) else 0)
            mask = ImageChops.darker(mask, source_alpha)
            image = ImageOps.invert(mask).convert('RGB')
        else:
            # Snap the selected background range to one exact color before tracing.
            channels = image.split()
            matches = [ch.point(lambda v, target=target: 255 if abs(v-target) <= tolerance else 0)
                       for ch, target in zip(channels, bg_rgb)]
            matched = ImageChops.darker(ImageChops.darker(matches[0], matches[1]), matches[2])
            mask = ImageOps.invert(matched)
            if transparent:
                image.paste(bg_rgb, mask=matched)
        if not mask.getbbox():
            raise ValueError('No artwork found. Adjust threshold or background tolerance.')
        if trim:
            box = mask.getbbox()
            image = image.crop(box)
            mask = mask.crop(box)
        source_trace_size = image.size
        if upscale > 1:
            scale = min(upscale, quality / max(image.size))
            if scale > 1:
                image = image.resize(tuple(max(1, round(n * scale)) for n in image.size), Image.Resampling.LANCZOS)
                if mode == 'binary':
                    image = image.convert('L').point(lambda x: 255 if x >= 128 else 0).convert('RGB')
                notices.append('Detail boost interpolates pixels; it cannot reconstruct missing artwork.')
        # Bound concurrent native tracing work; each request has isolated files.
        if not trace_lock.acquire(blocking=False):
            return jsonify(error='A conversion is already running. Try again shortly.'), 429
        try:
            with tempfile.TemporaryDirectory(prefix='vector-studio-') as folder:
                inp, out = Path(folder) / 'input.png', Path(folder) / 'output.svg'
                image.save(inp)
                vtracer.convert_image_to_svg_py(
                    str(inp), str(out), colormode=mode, hierarchical='cutout',
                    mode=fitting, color_precision=precision,
                    corner_threshold=smoothing, filter_speckle=speckle,
                    layer_difference=16, length_threshold=4.0,
                    max_iterations=10, splice_threshold=45, path_precision=3,
                )
                svg = out.read_text(encoding='utf-8')
        finally:
            trace_lock.release()
        # Binary tracing already uses real compound paths for holes.
        if mode == 'binary' and not transparent:
            root = ET.fromstring(svg)
            ET.SubElement(root, f'{{{SVG}}}rect', {'width': str(image.width), 'height': str(image.height), 'fill': '#ffffff'})
            root.insert(0, root[-1])
            del root[-1]
            svg = ET.tostring(root, encoding='unicode')
            notices.append('White backing is enabled: it creates an extra cut rectangle. Use transparency for cutting.')
        svg, outline, paths, height_mm = finish_svg(
            svg, image.size, width_mm, transparent and mode == 'color', background)
        guide = None
        if mode == 'binary':
            guide, thin, limited = detail_guide(mask, width_mm, minimum_mm)
            if thin:
                notices.append('Red detail-guide marks estimate thin features or narrow gaps; inspect before cutting.')
            if limited:
                notices.append('Detail guide range is capped at this size; increase output width for a more accurate estimate.')
        else:
            notices.append('Color paths are separate layers; inspect them in Design Space. The detail guide is for single-color mode.')
        return jsonify(svg=svg, outline=outline, guide=guide, notices=notices,
                       width=image.width, height=image.height, source_width=source_trace_size[0],
                       width_mm=width_mm, height_mm=round(height_mm, 2), paths=paths,
                       resized=reduced, bytes=len(svg.encode('utf-8')))
    except (ValueError, UnidentifiedImageError, OSError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        return jsonify(error=str(exc) if isinstance(exc, ValueError)
                       else 'This image cannot be read. Try a smaller PNG or JPEG.'), 400
    except Exception:
        app.logger.exception('Tracing failed')
        return jsonify(error='Tracing failed. Try a smaller image or fewer colors.'), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
