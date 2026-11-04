// Run in <head> so the saved appearance is applied before the page paints.
(() => {
  const root = document.documentElement;
  const key = `appearance_${root.dataset.app || 'vector-studio'}`;
  const allowed = ['system', 'light', 'dark'];
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference = 'system';
  try {
    const saved = document.cookie.split('; ').find(part => part.startsWith(`${key}=`));
    const value = saved ? decodeURIComponent(saved.slice(key.length + 1)) : 'system';
    if (allowed.includes(value)) preference = value;
  } catch { /* A blocked cookie should never prevent the app from loading. */ }
  function apply() {
    root.dataset.appearance = preference;
    root.dataset.theme = preference === 'system' ? (system.matches ? 'dark' : 'light') : preference;
  }
  apply();
  if (system.addEventListener) system.addEventListener('change', apply);
  else system.addListener(apply);
  document.addEventListener('DOMContentLoaded', () => {
    const select = document.getElementById('appearance');
    select.value = preference;
    select.addEventListener('change', () => {
      preference = allowed.includes(select.value) ? select.value : 'system';
      try {
        // Cookies survive changing local ports; separate keys keep both apps independent.
        document.cookie = `${key}=${encodeURIComponent(preference)}; Max-Age=31536000; Path=/; SameSite=Strict`;
      } catch { /* Continue with this session's choice when storage is blocked. */ }
      apply();
    });
  });
})();
