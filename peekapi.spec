# -*- mode: python ; coding: utf-8 -*-
# 使用方法: uv run pyinstaller peekapi.spec

import shutil
from pathlib import Path

a = Analysis(
    ['run.py'],
    datas=[('peekapi.ico', '.')],
    hiddenimports=[
        'msgspec', 'msgspec.toml',
        'soundcard', 'soundcard.mediafoundation',
        'soundfile',
        'numpy', 'numpy.core',
        'PIL._tkinter_finder', 'pystray._win32', 'loguru',
    ],
    excludes=['setuptools', 'tkinter', 'unittest', 'pydoc', 'difflib'],
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries=True,
    name='peekapi',
    upx=True,
    console=False,
    icon='peekapi.ico',
    version='version_info.txt',
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    upx=True,
    upx_exclude=['vcruntime140.dll', 'vcruntime140_1.dll', 'python*.dll', 'api-ms-*.dll', 'ucrtbase.dll'],
    name='peekapi',
)

# 复制配置文件到 exe 同级
shutil.copy('config.toml', Path('dist/peekapi/config.toml'))
