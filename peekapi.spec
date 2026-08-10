# -*- mode: python ; coding: utf-8 -*-
# 使用方法: uv run pyinstaller peekapi.spec

import shutil
from importlib.metadata import version
from pathlib import Path

from packaging.version import Version
from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringStruct,
    StringTable,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

app_version = version('peekapi')
release = Version(app_version).release
windows_version = (*release[:4], *(0 for _ in range(4 - len(release[:4]))))

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=windows_version,
        prodvers=windows_version,
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo([
            StringTable(
                '040904B0',
                [
                    StringStruct('CompanyName', 'PeekAPI'),
                    StringStruct('FileDescription', 'Screen Capture & Audio Recording API'),
                    StringStruct('FileVersion', app_version),
                    StringStruct('InternalName', 'peekapi'),
                    StringStruct('LegalCopyright', 'MIT License'),
                    StringStruct('OriginalFilename', 'peekapi.exe'),
                    StringStruct('ProductName', 'PeekAPI'),
                    StringStruct('ProductVersion', app_version),
                ],
            )
        ]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])]),
    ],
)

a = Analysis(
    ['run.py'],
    datas=[('peekapi.ico', '.'), *copy_metadata('peekapi')],
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
    version=version_info,
)

coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas,
    upx=True,
    upx_exclude=['vcruntime140.dll', 'vcruntime140_1.dll', 'python*.dll', 'api-ms-*.dll', 'ucrtbase.dll'],
    name='peekapi',
)

# 复制配置文件到 exe 同级
shutil.copy('config.toml', Path(DISTPATH) / 'peekapi/config.toml')
