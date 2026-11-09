#!/bin/bash
HERE="$(cd "$(dirname "$0")" && pwd -P)"
exec /bin/bash "$HERE/Setup.sh" uninstall
