#!/bin/bash
# Finder entry points call this script. Compatible with macOS's Bash 3.2.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd -P)"
SOURCE="$(cd "$HERE/.." && pwd -P)"
ACTION="${1:-install}"
TARGET="$HOME/Library/Application Support/VectorStudioCuttingLab"
MARKER='vector-studio-cutting-lab:macos:1'
TITLE='Vector Studio Cutting Lab'
WORK=''
MAINTENANCE=''

message() {
  /usr/bin/osascript - "$1" <<'APPLESCRIPT'
use framework "AppKit"
use scripting additions

on run argv
  set dialogApp to current application's NSApplication's sharedApplication()
  dialogApp's setActivationPolicy:(current application's NSApplicationActivationPolicyAccessory)
  dialogApp's activateIgnoringOtherApps:true
  display dialog (item 1 of argv) with title "Vector Studio Cutting Lab" buttons {"OK"} default button "OK"
end run
APPLESCRIPT
}
confirm() {
  /usr/bin/osascript - "$1" "$2" <<'APPLESCRIPT'
use framework "AppKit"
use scripting additions

on run argv
  set dialogApp to current application's NSApplication's sharedApplication()
  dialogApp's setActivationPolicy:(current application's NSApplicationActivationPolicyAccessory)
  dialogApp's activateIgnoringOtherApps:true
  display dialog (item 1 of argv) with title "Vector Studio Cutting Lab" buttons {"Cancel", (item 2 of argv)} default button (item 2 of argv) cancel button "Cancel"
end run
APPLESCRIPT
}
cleanup() {
  # Only delete our mktemp directory, never a caller-supplied path.
  if [[ -n "$WORK" && "$WORK" == "${TMPDIR:-/tmp/}"vector-studio.* && -d "$WORK" && ! -L "$WORK" ]]; then
    /bin/rm -rf -- "$WORK"
  fi
  if [[ -n "$MAINTENANCE" ]]; then /bin/rmdir "$MAINTENANCE" 2>/dev/null || true; fi
}
trap cleanup EXIT
trap 'message "Setup stopped. Read the Terminal window for details. You can close it and try again; downloaded images and SVGs outside the app folder are untouched." || true' ERR
[[ "$(/usr/bin/uname -s)" == Darwin ]] || { echo 'This setup is for macOS only.'; exit 1; }
[[ "$ACTION" == install || "$ACTION" == run || "$ACTION" == uninstall ]] || exit 1
if [[ "$(/usr/bin/uname -m)" != arm64 ]]; then
  if [[ "$(/usr/sbin/sysctl -n hw.optional.arm64 2>/dev/null || true)" == 1 ]]; then
    exec /usr/bin/arch -arm64 /bin/bash "$HERE/Setup.sh" "$ACTION"
  fi
  message 'This installer currently supports Apple Silicon Macs (M1 or newer), not Intel Macs.'; exit 1
fi
[[ "$(/usr/bin/sw_vers -productVersion | /usr/bin/cut -d. -f1)" -ge 11 ]] || exit 1
[[ "$HOME" == /* && "$HOME" != / ]] || exit 1
# Refuse redirected parents so removal cannot escape this account's app folder.
for part in "$HOME/Library" "$HOME/Library/Application Support" "$TARGET" "$TARGET/runtime" "$TARGET/.venv"; do
  if [[ -L "$part" || ( -e "$part" && ! -d "$part" ) ]]; then
    message "Cannot manage a linked or non-folder installation path: $part"; exit 1
  fi
done
if [[ -e "$TARGET" ]]; then
  if [[ -L "$TARGET/.vector-studio-macos" || ! -f "$TARGET/.vector-studio-macos" || "$(/bin/cat "$TARGET/.vector-studio-macos")" != "$MARKER" ]]; then
    message "The folder $TARGET has no valid installation record. Nothing will be changed."; exit 1
  fi
  if [[ -L "$TARGET/.vector-studio-running.lock" ]]; then message 'The app lock is a link. Nothing will be changed.'; exit 1; fi
fi

if [[ "$ACTION" == run ]]; then
  if [[ ! -x "$TARGET/.venv/bin/python" ]]; then message 'Run Install.command from the complete extracted download first.'; exit 1; fi
  cd "$TARGET"
  exec "$TARGET/.venv/bin/python" launcher.py
fi

if [[ "$ACTION" == uninstall && ! -e "$TARGET" ]]; then
  message 'Vector Studio Cutting Lab is already absent.'; exit 0
fi
# Serialize setup/removal without killing any processes. A crash may leave this
# empty directory behind; the guide explains how to report that condition.
/bin/mkdir -p "$HOME/Library/Application Support"
MAINTENANCE="$HOME/Library/Application Support/.VectorStudioCuttingLab-maintenance"
if ! /bin/mkdir "$MAINTENANCE"; then
  MAINTENANCE=''; message 'Another setup or removal may be running. Close it before trying again. If none is running, see MAC_INSTALL.md.'; exit 1
fi
if [[ -f "$TARGET/.vector-studio-running.lock" ]] && /usr/sbin/lsof -t "$TARGET/.vector-studio-running.lock" >/dev/null 2>&1; then
  message 'Close all Vector Studio console windows before updating or removing it.'; exit 1
fi

if [[ "$ACTION" == uninstall ]]; then
  confirm "Remove $TITLE? This permanently deletes $TARGET, its private Python and any personal files INSIDE that folder. Files elsewhere and your system Python are kept." 'Uninstall' || exit 0
  if [[ -f "$TARGET/.vector-studio-running.lock" ]] && /usr/sbin/lsof -t "$TARGET/.vector-studio-running.lock" >/dev/null 2>&1; then
    message 'The app is still running. Close its console window before removing it.'; exit 1
  fi
  # Exact, fixed per-user target; never accept a path argument for deletion.
  [[ "$TARGET" == "$HOME/Library/Application Support/VectorStudioCuttingLab" && ! -L "$TARGET" ]] || exit 1
  for name in 'Vector Studio Cutting Lab.command' 'Uninstall Vector Studio Cutting Lab.command'; do
    shortcut="$HOME/Desktop/$name"
    if [[ -f "$shortcut" && ! -L "$shortcut" ]] && /usr/bin/grep -q '^# VectorStudioCuttingLab managed desktop launcher$' "$shortcut"; then
      /bin/rm -- "$shortcut"
    fi
  done
  cd "$HOME"
  /bin/rm -rf -- "$TARGET"
  message 'Vector Studio Cutting Lab has been removed. Your source download and exported SVGs outside its app folder were kept.'
  exit 0
fi

for file in app.py launcher.py requirements.txt tests/test_app.py macos/manage.py macos/Install.command macos/Run.command macos/Uninstall.command; do
  [[ -f "$SOURCE/$file" ]] || { message 'Extract the entire project ZIP and keep all its folders together.'; exit 1; }
done
confirm "Install or update $TITLE in $TARGET? Setup downloads a private Python 3.12 and the tracing packages. Existing app files are replaced in the same folder. No administrator password or Homebrew is needed." 'Install' || exit 0
/bin/mkdir -p "$TARGET"
printf '%s\n' "$MARKER" > "$TARGET/.vector-studio-macos"
WORK="$(/usr/bin/mktemp -d "${TMPDIR:-/tmp/}vector-studio.XXXXXX")"
UV_VERSION='0.13.7'
UV_SHA256='81b811b57e4624df7ed3aac148e0359100d9962f3d9dce00aec533dc2e086731'
echo 'Downloading and verifying the Python setup tool...'
/usr/bin/curl --fail --location --retry 3 --connect-timeout 15 --max-time 180 --retry-max-time 240 --proto '=https' --proto-redir '=https' --tlsv1.2 \
  "https://github.com/astral-sh/uv/releases/download/$UV_VERSION/uv-aarch64-apple-darwin.tar.gz" -o "$WORK/uv.tar.gz"
printf '%s  %s\n' "$UV_SHA256" "$WORK/uv.tar.gz" | /usr/bin/shasum -a 256 -c -
/usr/bin/tar -xzf "$WORK/uv.tar.gz" -C "$WORK"
UV="$WORK/uv-aarch64-apple-darwin/uv"
export UV_PYTHON_INSTALL_DIR="$TARGET/runtime"
export UV_PYTHON_INSTALL_BIN=0
export UV_NO_CONFIG=1
export UV_NO_CACHE=1
export UV_HTTP_TIMEOUT=60
export PYTHONNOUSERSITE=1
unset PYTHONHOME PYTHONPATH || true
echo 'Preparing private Python 3.12...'
"$UV" python install 3.12 --no-bin --no-config --no-progress
PYTHON="$("$UV" python find 3.12 --managed-python --no-python-downloads --no-config)"
"$PYTHON" "$HERE/manage.py" "$SOURCE" "$TARGET" "$UV"
message 'Installed successfully. Double-click Vector Studio Cutting Lab on your Desktop. Keep its Terminal window open while using the app. The Uninstall shortcut removes this edition.'
