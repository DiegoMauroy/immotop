# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['..\\src\\Main.py', '..\\src\\Immotop.py', '..\\src\\Immotop_data_json.py', '..\\src\\Config_data_json.py', '..\\src\\Tools\\Scrape.py', '..\\src\\Tools\\Files_tools.py', '..\\src\\Tools\\Dictionnary_tools.py', '..\\src\\Tools\\Pydantic.py', '..\\src\\Tools\\Converts.py'],
    pathex=[],
    binaries=[],
    datas=[('..\\Inputs\\translate_to_url.json', ".")],
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
    name='Immotop_1_1',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
