#!/usr/bin/env bash
# Builds blockr_<version>_amd64.deb from the PyInstaller Linux binary.
#
# Prerequisites:
#   1. Build the binary first:  pyinstaller packaging/linux/blockr-linux.spec
#   2. Install fpm:             sudo apt install ruby ruby-dev build-essential
#                                sudo gem install --no-document fpm
#
# Usage (from the project root):
#   ./packaging/linux/build-deb.sh [version]

set -euo pipefail

VERSION="${1:-1.0.0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

if [ ! -f "$ROOT/dist/blockr" ]; then
    echo "error: dist/blockr not found — run pyinstaller packaging/linux/blockr-linux.spec first" >&2
    exit 1
fi

mkdir -p "$STAGE/usr/bin" "$STAGE/usr/share/applications" "$STAGE/usr/share/pixmaps"

install -m 755 "$ROOT/dist/blockr" "$STAGE/usr/bin/blockr"
install -m 644 "$ROOT/packaging/linux/blockr.desktop" "$STAGE/usr/share/applications/blockr.desktop"
install -m 644 "$ROOT/icon.png" "$STAGE/usr/share/pixmaps/blockr.png"

fpm -s dir -t deb \
    -n blockr \
    -v "$VERSION" \
    --description "Block distracting websites at the system level via the hosts file." \
    --url "https://blockr.joelkajubi.site" \
    --maintainer "Joel Kajubi <joelkajubi2@gmail.com>" \
    --license "MIT" \
    --category "utils" \
    --depends "policykit-1" \
    --package "$ROOT/dist/blockr_${VERSION}_amd64.deb" \
    -C "$STAGE" \
    usr/bin/blockr usr/share/applications/blockr.desktop usr/share/pixmaps/blockr.png

echo "Built dist/blockr_${VERSION}_amd64.deb"
