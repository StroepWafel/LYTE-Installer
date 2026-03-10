# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for LYTE Installer

import os

# Branding assets - preserve folder structure
branding_dir = 'branding'
branding_datas = []
if os.path.isdir(branding_dir):
    for root, dirs, files in os.walk(branding_dir):
        for f in files:
            src = os.path.join(root, f)
            rel = os.path.relpath(src, branding_dir)
            dest_dir = os.path.join('branding', os.path.dirname(rel)) if os.path.dirname(rel) else 'branding'
            branding_datas.append((src, dest_dir))

# Uninstaller (built first by build script)
uninstaller_path = os.path.join('dist', 'Uninstall LYTE.exe')
uninstaller_datas = []
if os.path.isfile(uninstaller_path):
    uninstaller_datas = [(uninstaller_path, '.')]

# Checkbox checkmark icon
checkmark_svg = os.path.join('src', 'ui', 'checkmark.svg')
checkmark_datas = [(checkmark_svg, 'src/ui')] if os.path.isfile(checkmark_svg) else []

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=branding_datas + uninstaller_datas + checkmark_datas,
    hiddenimports=['PySide6', 'requests'],
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
    name='LYTE_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='branding/ico/install.ico' if os.path.isfile('branding/ico/install.ico') else None,
    uac_admin=True,
)
