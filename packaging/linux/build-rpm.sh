#!/usr/bin/env bash
# Builds blockr-<version>-1.x86_64.rpm from the PyInstaller Linux binary.
#
# Prerequisites:
#   1. Build the binary first:  pyinstaller packaging/linux/blockr-linux.spec
#   2. Install fpm + rpmbuild:
#        Fedora/RHEL: sudo dnf install ruby ruby-devel gcc make rpm-build
#        Debian/Ubuntu (cross-building an rpm): sudo apt install rpm ruby ruby-dev build-essential
#      then: sudo gem install --no-document fpm
#
# Usage (from the project root):
#   ./packaging/linux/build-rpm.sh [version]

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

fpm -s dir -t rpm \
    -n blockr \
    -v "$VERSION" \
    --description "Block distracting websites at the system level via the hosts file." \
    --url "https://blockr.joelkajubi.site" \
    --maintainer "Joel Kajubi <joelkajubi2@gmail.com>" \
    --license "MIT" \
    --category "Applications/Utilities" \
    --depends "polkit" \
    --package "$ROOT/dist/blockr-${VERSION}-1.x86_64.rpm" \
    -C "$STAGE" \
    usr/bin/blockr usr/share/applications/blockr.desktop usr/share/pixmaps/blockr.png

echo "Built dist/blockr-${VERSION}-1.x86_64.rpm"
