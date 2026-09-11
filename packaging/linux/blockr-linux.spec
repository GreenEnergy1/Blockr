# -*- mode: python ; coding: utf-8 -*-
#
# Build (on Linux, run from the PROJECT ROOT — not this directory):
#   pip install pyinstaller PyQt6
#   pyinstaller packaging/linux/blockr-linux.spec
#
# Output: dist/blockr
#
# Build on the OLDEST distro/glibc you need to support (e.g. Ubuntu 22.04),
# since PyInstaller links against the host's glibc and the binary won't run
# on systems with an older glibc than the one it was built on.

a = Analysis(
    ['../../blockr.py'],
    pathex=[],
    binaries=[],
    datas=[('../../icon.png', '.')],
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
)
