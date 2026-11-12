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
  form.append('stencil_guide', stencilGuide ? '1' : '0');
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
let pickerOpen = false;
async function openImagePicker() {
  if (pickerOpen) return;
  if (!window.showOpenFilePicker) { $('file').click(); return; }
  pickerOpen = true;
  try {
    const [handle] = await window.showOpenFilePicker({
      id: `${document.documentElement.dataset.app}-images`,
      multiple: false,
      excludeAcceptAllOption: true,
      types: [{description: 'Images', accept: {
        'image/png': ['.png'], 'image/jpeg': ['.jpg', '.jpeg'],
        'image/webp': ['.webp'], 'image/bmp': ['.bmp'],
      }}],
    });
    if (handle) choose(await handle.getFile());
  } catch (error) {
    if (error.name !== 'AbortError') {
      // Embedded browsers and restrictive policies can reject the enhanced picker.
      $('file').click();
    }
  } finally { pickerOpen = false; }
}
$('dropzone').addEventListener('click', event => {
  if (event.target === $('file')) return;
  event.preventDefault();
  openImagePicker();
});
$('dropzone').addEventListener('keydown', event => {
  if (event.key === 'Enter' || event.key === ' ') {event.preventDefault(); openImagePicker();}
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
const defaults = {colors: 6, smoothing: 60, speckle: 0, mode: 'binary', threshold: 160,
  background: '#ffffff', tolerance: 20, fitting: 'spline', quality: '1600', upscale: '1',
  width_mm: 100, minimum_mm: 0.5, transparent: true, trim: true, invert: false};
const profiles = {
  standard: {},
  logo: {smoothing: 35, quality: '3200'},
  stencil: {speckle: 4, minimum_mm: 1},
  shirt: {width_mm: 230, minimum_mm: 1},
  cap: {width_mm: 85, minimum_mm: 0.8},
  cup: {width_mm: 65, minimum_mm: 0.8},
};
const profileNotes = {
  logo: 'Keeps fine details and sharper corners.',
  stencil: 'Orange marks in the detail guide flag enclosed areas that may need bridges.',
  shirt: 'Starts at 230 mm wide. Check against your garment.',
  cap: 'Starts at 85 mm wide. Check against the available panel.',
  cup: 'Starts at 65 mm wide. Check against the usable area of your cup.',
};
const profileKey = 'vector-studio-cutting-profile-v1';
let stencilGuide = false;
let savedProfile;
try {
  const stored = JSON.parse(localStorage.getItem(profileKey));
  if (stored && stored.settings && controls.every(id => Object.hasOwn(stored.settings, id))) {
    savedProfile = stored;
  }
} catch {}
if (savedProfile) $('profile').add(new Option('My profile', 'saved'));

function applyProfile(name) {
  const settings = name === 'saved' ? savedProfile.settings : profiles[name];
  if (!settings) return;
  controls.forEach(id => {
    const value = settings[id] ?? defaults[id];
    if ($(id).type === 'checkbox') $(id).checked = value === true;
    else $(id).value = value;
  });
  stencilGuide = name === 'stencil' || (name === 'saved' && savedProfile.stencilGuide === true);
  $('profile').value = name;
  $('profile-note').textContent = profileNotes[name] || '';
  $('preview-mode').value = stencilGuide ? 'guide' : 'filled';
  queue();
}
controls.forEach(id => $(id).addEventListener('input', () => {
  $('profile').value = 'custom';
  $('profile-note').textContent = stencilGuide ? profileNotes.stencil : '';
  queue();
}));
$('profile').addEventListener('change', event => applyProfile(event.target.value));
$('save-profile').addEventListener('click', () => {
  if (controls.some(id => !$(id).checkValidity())) {
    $('profile-note').textContent = 'Check the settings before saving.';
    return;
  }
  const settings = Object.fromEntries(controls.map(id =>
    [id, $(id).type === 'checkbox' ? $(id).checked : $(id).value]));
  try {
    const profile = {settings, stencilGuide};
    localStorage.setItem(profileKey, JSON.stringify(profile));
    if (!savedProfile) $('profile').add(new Option('My profile', 'saved'));
    savedProfile = profile;
    $('profile').value = 'saved';
    $('profile-note').textContent = 'My profile saved in this browser.';
  } catch {
    $('profile-note').textContent = 'This browser could not save the profile.';
  }
});
$('convert').addEventListener('click', convert);
$('reset').addEventListener('click', () => applyProfile('standard'));
$('preview-mode').addEventListener('change', showPreview);
$('zoom').addEventListener('change', () => {
  document.querySelectorAll('.canvas').forEach(canvas => {
    canvas.style.setProperty('--zoom', $('zoom').value);
    canvas.classList.toggle('zoomed', $('zoom').value !== '1');
  });
});
labels();
