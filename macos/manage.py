"""Install Mac app files and verified dependencies. No action on import."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys

APP_FOLDER = 'VectorStudioCuttingLab'
MARKER = 'vector-studio-cutting-lab:macos:1'
VERSION = '2.1.0'
FILES = (
    'app.py', 'launcher.py', 'requirements.txt', 'README.md', 'INSTALL.md',
    'MAC_INSTALL.md', '.gitignore', 'templates/index.html', 'static/app.js',
    'static/style.css', 'static/cutting.css', 'static/theme.js', 'static/theme.css',
    'static/icons/icon.svg', 'static/icons/app.ico', 'static/icons/favicon.ico',
    'static/icons/app-192.png', 'static/icons/app-512.png', 'tests/test_app.py',
    'macos/Setup.sh', 'macos/manage.py', 'macos/Install.command',
    'macos/Run.command', 'macos/Uninstall.command',
)


def validate_target(target, home):
    expected = home / 'Library' / 'Application Support' / APP_FOLDER
    if target != expected or not target.is_absolute():
        raise ValueError('Only the standard per-user app folder can be managed.')
    for part in (home / 'Library', expected.parent, expected):
        if part.is_symlink():
            raise ValueError('Linked installation folders are not supported.')
    marker = target / '.vector-studio-macos'
    if marker.is_symlink() or marker.read_text().strip() != MARKER:
        raise ValueError('The app installation record is missing or invalid.')


def copy_sources(source, target):
    # Read and validate the full allowlist before replacing any installed source.
    contents = {}
    for relative in FILES:
        src = source / relative
        dst = target / relative
        if src.is_symlink() or not src.is_file():
            raise ValueError(f'Missing or linked source file: {relative}')
        for part in (dst, *dst.parents):
            if part == target:
                break
            if part.is_symlink():
                raise ValueError(f'Linked destination refused: {relative}')
        contents[relative] = src.read_bytes()
    for relative, data in contents.items():
        dst = target / relative
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        if dst.suffix in ('.command', '.sh'):
            dst.chmod(0o755)


def desktop_launcher(action):
    return ('#!/bin/bash\n# VectorStudioCuttingLab managed desktop launcher\n'
            'exec /bin/bash "$HOME/Library/Application Support/'
            f'{APP_FOLDER}/macos/Setup.sh" {action}\n')


def create_shortcuts(home):
    desktop = home / 'Desktop'
    if not desktop.is_dir() or desktop.is_symlink():
        raise ValueError('Desktop folder is unavailable. Allow Desktop access and rerun setup.')
    entries = {'Vector Studio Cutting Lab.command': 'run',
               'Uninstall Vector Studio Cutting Lab.command': 'uninstall'}
    for name in entries:
        path = desktop / name
        if path.is_symlink() or (path.exists() and
                '# VectorStudioCuttingLab managed desktop launcher\n' not in path.read_text()):
            raise ValueError(f'A different file already uses this desktop name: {name}')
    for name, action in entries.items():
        path = desktop / name
        path.write_text(desktop_launcher(action))
        path.chmod(0o755)


def install(source, target, uv, home=None):
    import fcntl  # macOS only; helper tests can import other functions on Windows.
    home = Path.home() if home is None else home
    validate_target(target, home)
    with (target / '.vector-studio-running.lock').open('ab') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('The app is running. Close its console window first.') from None
        copy_sources(source, target)
        python = target / '.venv' / 'bin' / 'python'
        # uv checks/creates the same environment; no global pip or PATH changes.
        if not python.exists():
            subprocess.run([str(uv), 'venv', str(target / '.venv'),
                            '--python', sys.executable, '--no-config'], check=True)
        subprocess.run([str(uv), 'pip', 'install', '--python', str(python),
                        '--only-binary', ':all:', '--index-url', 'https://pypi.org/simple',
                        '-r', str(target / 'requirements.txt'), '--no-config'], check=True)
        subprocess.run([str(uv), 'pip', 'check', '--python', str(python), '--no-config'], check=True)
        subprocess.run([str(python), '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                       cwd=target, check=True)
        create_shortcuts(home)
        (target / '.vector-studio-version.json').write_text(json.dumps(
            {'app_id': 'cutting-lab', 'version': VERSION, 'platform': 'macos'}, indent=2))
        print(f'Installed Vector Studio Cutting Lab {VERSION} in {target}', flush=True)


if __name__ == '__main__':
    if sys.platform != 'darwin':
        raise SystemExit('This installer is for macOS only.')
    try:
        install(*(Path(arg).absolute() for arg in sys.argv[1:]))
    except Exception as exc:
        print(f'Installation stopped: {exc}', file=sys.stderr)
        raise SystemExit(1)
