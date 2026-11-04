const $ = id => document.getElementById(id);
const controls = ['colors', 'smoothing', 'speckle', 'mode', 'threshold', 'invert',
  'transparent', 'trim', 'background', 'tolerance', 'fitting', 'quality', 'upscale', 'width_mm', 'minimum_mm'];
let file = null, sourceUrl = null, svgUrl = null, outlineUrl = null, guideUrl = null, revision = 0, timer, busy = false;
const formatBytes = bytes => bytes < 1024 ? `${bytes} B` : `${(bytes / 1024).toFixed(1)} KB`;

function labels() {
  $('colors-value').textContent = `${$('colors').value} bits`;
  $('smoothing-value').textContent = `${$('smoothing').value}°`;
  $('speckle-value').textContent = `${$('speckle').value} px`;
  $('colors').disabled = $('mode').value === 'binary';
  $('binary-controls').hidden = $('mode').value !== 'binary';
  $('color-controls').hidden = $('mode').value !== 'color';
  $('threshold-value').textContent = $('threshold').value;
  $('tolerance-value').textContent = $('tolerance').value;
  $('smoothing').disabled = $('fitting').value === 'polygon';
}
function showPreview() {
  const mode = $('preview-mode').value;
  const url = mode === 'outline' ? outlineUrl : mode === 'guide' ? guideUrl : svgUrl;
  $('result').src = url || svgUrl || '';
  if (mode === 'guide' && !guideUrl && svgUrl) message('Small-detail guide is available in single-color mode. Showing filled artwork.');
}
function invalidate() {
  revision++;
  $('download').classList.add('disabled');
  $('download').setAttribute('aria-disabled', 'true');
  $('download').removeAttribute('href');
}
function message(text, error = false) {
  $('message').textContent = text;
  $('message').classList.toggle('error', error);
}
function queue() {
  labels(); invalidate(); clearTimeout(timer);
  if (file) {
    $('status').textContent = 'Changes pending…';
    timer = setTimeout(convert, 500);
  }
}
function choose(selected) {
  if (!selected) return;
  if (!/\.(png|jpe?g|webp|bmp)$/i.test(selected.name)) {
    message('Please choose a PNG, JPEG, WebP, or BMP image.', true); return;
  }
  if (selected.size > 12 * 1024 * 1024) {
    message('Choose an image smaller than 12 MB.', true); return;
  }
  file = selected;
  if (sourceUrl) URL.revokeObjectURL(sourceUrl);
  sourceUrl = URL.createObjectURL(file);
  $('original').src = sourceUrl;
  $('original').hidden = false;
  $('original-empty').hidden = true;
  $('original-meta').textContent = formatBytes(file.size);
  $('filename').textContent = file.name;
  $('filename').title = file.name;
  $('result').hidden = true; $('result-empty').hidden = false;
  $('result-meta').textContent = 'Resolution independent';
  $('convert').disabled = false;
  message('Image loaded. Finding your curves…');
  queue();
}
async function convert() {
  clearTimeout(timer);
  if (!file) return;
  // Serialize requests instead of abandoning native work when sliders move.
  if (busy) return;
  busy = true;
  const requestedRevision = revision;
  const selectedFile = file;
  $('status').textContent = 'Tracing…';
  $('convert').disabled = true;
  const form = new FormData();
  form.append('image', selectedFile);
  controls.forEach(id => form.append(id, $(id).type === 'checkbox' ? ($(id).checked ? '1' : '0') : $(id).value));
  try {
    const response = await fetch('/api/vectorize', {method: 'POST', body: form});
    const data = await response.json();
    if (requestedRevision !== revision) return;
    if (!response.ok) throw new Error(data.error || 'Conversion failed. Try again.');
    if (svgUrl) URL.revokeObjectURL(svgUrl);
    if (outlineUrl) URL.revokeObjectURL(outlineUrl);
    svgUrl = URL.createObjectURL(new Blob([data.svg], {type: 'image/svg+xml'}));
    outlineUrl = URL.createObjectURL(new Blob([data.outline], {type: 'image/svg+xml'}));
    guideUrl = data.guide;
    showPreview(); $('result').hidden = false; $('result-empty').hidden = true;
    $('result-meta').textContent = `${data.width_mm} × ${data.height_mm} mm · ${data.paths} paths · ${formatBytes(data.bytes)}`;
    $('download').href = svgUrl;
    $('download').download = selectedFile.name.replace(/\.[^.]+$/, '') + '.svg';
    $('download').classList.remove('disabled');
    $('download').setAttribute('aria-disabled', 'false');
    $('status').textContent = 'Your SVG is ready';
    message(data.notices.length ? data.notices.join(' ') : 'Your SVG is ready. Inspect boundaries, confirm the size in Design Space, then make a test cut.');
  } catch (error) {
    if (requestedRevision === revision) {
      $('status').textContent = 'Try again';
      message(error.message || 'Could not connect to the local app.', true);
    }
  } finally {
    busy = false; $('convert').disabled = !file;
    if (requestedRevision !== revision) convert();
  }
}
$('file').addEventListener('change', event => choose(event.target.files[0]));
$('dropzone').addEventListener('keydown', event => {
  if (event.key === 'Enter' || event.key === ' ') {event.preventDefault(); $('file').click();}
});
['dragenter', 'dragover'].forEach(type => $('dropzone').addEventListener(type, event => {
  event.preventDefault(); $('dropzone').classList.add('dragging');
}));
$('dropzone').addEventListener('dragleave', () => $('dropzone').classList.remove('dragging'));
$('dropzone').addEventListener('drop', event => {
  event.preventDefault(); $('dropzone').classList.remove('dragging'); choose(event.dataTransfer.files[0]);
});
window.addEventListener('dragover', event => event.preventDefault());
window.addEventListener('drop', event => event.preventDefault());
controls.forEach(id => $(id).addEventListener('input', queue));
$('convert').addEventListener('click', convert);
$('reset').addEventListener('click', () => {
  Object.entries({colors: 6, smoothing: 60, speckle: 0, mode: 'binary', threshold:160,
    background:'#ffffff', tolerance:20, fitting:'spline', quality:'1600', upscale:'1', width_mm:100, minimum_mm:0.5}).forEach(([id, value]) => $(id).value = value);
  $('transparent').checked = true; $('trim').checked = true; $('invert').checked = false;
  queue();
});
$('preview-mode').addEventListener('change', showPreview);
$('zoom').addEventListener('change', () => {
  document.querySelectorAll('.canvas').forEach(canvas => {
    canvas.style.setProperty('--zoom', $('zoom').value);
    canvas.classList.toggle('zoomed', $('zoom').value !== '1');
  });
});
labels();
