# -*- mode: python ; coding: utf-8 -*-
#
# Build (on Windows, run from the PROJECT ROOT — not this directory):
#   pip install pyinstaller PyQt6
#   pyinstaller packaging\windows\blockr-win.spec
#
# Output: dist\blockr.exe
#
# Paths below are relative to THIS spec file (PyInstaller resolves them
# that way, not relative to the current working directory).

a = Analysis(
    ['../../blockr.py'],
    pathex=[],
    binaries=[],
    # Bundle the icon as a runtime resource too, not just the exe's file
    # icon — this is what lets Blockr set its own taskbar/window icon.
    datas=[('../../icon.ico', '.'), ('../../icon.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='blockr',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['../../icon.ico'],
)
