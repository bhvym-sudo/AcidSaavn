# AcidSaavn.spec
block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('core/*', 'core'),
        ('ui/*', 'ui'),
        ('utils/*', 'utils')
    ],
    hiddenimports=[
        'requests',
        'PyQt5',
        'ffpyplayer.player',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,  # Include binaries in the EXE
    a.zipfiles,  # Include zipfiles in the EXE
    a.datas,     # Include data files in the EXE
    [],
    name='AcidSaavn-z3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None  # If you have an icon file, you can replace None with 'your_icon.ico'
)