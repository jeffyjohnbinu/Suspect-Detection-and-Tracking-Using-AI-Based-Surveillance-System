# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['cnn_face_recognize.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\jeffy\\anaconda3\\envs\\suspect_cnn\\Lib\\site-packages\\face_recognition_models\\models', 'face_recognition_models\\models')],
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
    name='cnn_face_recognize',
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
