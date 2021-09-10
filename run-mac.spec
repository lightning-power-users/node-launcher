# -*- mode: python -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

a = Analysis(
    ['run.py'],
    binaries=[
        ('node_launcher/node_set/lib/bin/tor.real', 'node_launcher/node_set/lib/bin/'),
        ('node_launcher/node_set/lib/bin/libevent-2.1.7.dylib', 'node_launcher/node_set/lib/bin/'),
        ('node_launcher/node_set/lib/bin/bitcoind', 'node_launcher/node_set/lib/bin/'),
        ('node_launcher/node_set/lib/bin/lnd', 'node_launcher/node_set/lib/bin/')
    ],
    datas=[
        ('node_launcher/gui/assets/Bitcoin-Icons/png/filled/node*.png', 'node_launcher/gui/assets/Bitcoin-Icons/png/filled/'),
        ],
    hiddenimports=['setuptools'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

# Strip out parts of Qt that we never use. Reduces binary size by tens of MBs. see #4815
qt_bins2remove=('qtweb', 'qt3d', 'qtgame', 'qtdesigner', 'qtquick', 'qtlocation', 'qttest', 'qtxml')
print("Removing Qt binaries:", *qt_bins2remove)
for x in a.binaries.copy():
    for r in qt_bins2remove:
        if x[0].lower().startswith(r):
            a.binaries.remove(x)
            print('----> Removed x =', x)

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
    version='7.0.0',
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
