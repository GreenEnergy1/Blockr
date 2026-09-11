# -*- mode: python ; coding: utf-8 -*-
#
# Build (on macOS, run from the PROJECT ROOT — not this directory):
#   pip install pyinstaller PyQt6
#   pyinstaller packaging/mac/blockr-mac.spec
#
# Output: dist/Blockr.app
#
# Paths below are relative to THIS spec file (PyInstaller resolves them
# that way, not relative to the current working directory).

a = Analysis(
    ['../../blockr.py'],
    pathex=[],
    binaries=[],
    datas=[('../../icon.icns', '.'), ('../../icon.png', '.')],
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
    [],
    exclude_binaries=True,
    name='Blockr',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../../icon.icns',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Blockr',
)

app = BUNDLE(
    coll,
    name='Blockr.app',
    icon='../../icon.icns',
    bundle_identifier='com.joelkajubi.blockr',
    info_plist={
        'CFBundleName': 'Blockr',
        'CFBundleDisplayName': 'Blockr',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': True,
        'NSHumanReadableCopyright': 'Blockr',
        'LSMinimumSystemVersion': '11.0',
    },
)
