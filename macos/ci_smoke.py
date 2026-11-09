"""Run real private-runtime installation in a disposable CI fixture, without dialogs."""
from pathlib import Path
import hashlib
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

source = Path(__file__).resolve().parents[1]
setup = (source / 'macos/Setup.sh').read_text()
version = re.search(r"UV_VERSION='([^']+)'", setup)[1]
expected = re.search(r"UV_SHA256='([^']+)'", setup)[1]
if sys.platform != 'darwin':
    raise SystemExit('This smoke test requires an Apple Silicon Mac runner.')
with tempfile.TemporaryDirectory(prefix='vector-studio-ci-') as temp:
    fixture = Path(temp)
    archive = fixture / 'uv.tar.gz'
    url = f'https://github.com/astral-sh/uv/releases/download/{version}/uv-aarch64-apple-darwin.tar.gz'
    urllib.request.urlretrieve(url, archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == expected
    with tarfile.open(archive) as tar:
        tar.extractall(fixture, filter='data')
    uv = fixture / 'uv-aarch64-apple-darwin/uv'
    home = fixture / 'Test Account With Spaces'
    target = home / 'Library/Application Support/VectorStudioCuttingLab'
    target.mkdir(parents=True)
    (home / 'Desktop').mkdir()
    (target / '.vector-studio-macos').write_text('vector-studio-cutting-lab:macos:1\n')
    env = dict(os.environ, UV_PYTHON_INSTALL_DIR=str(target / 'runtime'),
               UV_PYTHON_INSTALL_BIN='0', UV_NO_CONFIG='1', UV_NO_CACHE='1')
    subprocess.run([str(uv), 'python', 'install', '3.12', '--no-bin'], env=env, check=True)
    python = subprocess.check_output([str(uv), 'python', 'find', '3.12', '--managed-python',
                                      '--no-python-downloads'], env=env, text=True).strip()
    command = [python, '-c',
               'import runpy,sys; from pathlib import Path; '
               'm=runpy.run_path(sys.argv[1]); '
               'm["install"](*(Path(x) for x in sys.argv[2:5]), home=Path(sys.argv[5]))',
               str(source / 'macos/manage.py'), str(source), str(target), str(uv), str(home)]
    subprocess.run(command, env=env, check=True)
    subprocess.run(command, env=env, check=True)  # update/repair, same paths
    assert (target / '.vector-studio-version.json').is_file()
    assert not (target / 'windows').exists()
    for path in (home / 'Desktop').glob('*.command'):
        assert path.stat().st_mode & 0o111
    print('PASS: private Python bootstrap, install, repair, tracing, and desktop launcher files.')
