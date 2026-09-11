#!/usr/bin/env bash
# Builds Blockr-<version>.dmg from the PyInstaller macOS app bundle.
# Must run on macOS (uses hdiutil, which is built in — no extra installs).
#
# Prerequisite:
#   pyinstaller packaging/mac/blockr-mac.spec
#
# Usage (from the project root):
#   ./packaging/mac/build-dmg.sh [version]

set -euo pipefail

VERSION="${1:-1.0.0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
APP="$ROOT/dist/Blockr.app"
DMG="$ROOT/dist/Blockr-${VERSION}.dmg"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

if [ ! -d "$APP" ]; then
    echo "error: dist/Blockr.app not found — run pyinstaller packaging/mac/blockr-mac.spec first" >&2
    exit 1
fi

cp -R "$APP" "$STAGE/"
ln -s /Applications "$STAGE/Applications"

rm -f "$DMG"
hdiutil create -volname "Blockr" -srcfolder "$STAGE" -ov -format UDZO "$DMG"

echo "Built dist/Blockr-${VERSION}.dmg"
echo
echo "Note: this build is unsigned. On first launch, macOS Gatekeeper will"
echo "block it — users need to right-click Blockr.app > Open, or you can"
echo "codesign + notarize with an Apple Developer account before shipping."
