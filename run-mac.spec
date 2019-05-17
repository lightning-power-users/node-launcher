# -*- mode: python -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=['/Users/pierre/src/node-launcher'],
    binaries=[],
    datas=[
        ('node_launcher/gui/assets/*.png', 'assets')
    ] + collect_data_files('shiboken2', include_py_files=True, subdir='support')
    + collect_data_files('PySide2', include_py_files=True, subdir='support'),
    hiddenimports=['setuptools'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Node.Launcher.app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    runtime_tmpdir=None,
    console=False
)

app = BUNDLE(
    exe,
    name='Node Launcher.app',
    icon='AppIcon.icns',
    bundle_identifier=None,
    info_plist={
        'NSPrincipleClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'NSHighResolutionCapable': 'True',
        'NSRequiresAquaSystemAppearance': 'True',
        'LSUIElement': 1
    }
)
