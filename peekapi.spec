# -*- mode: python ; coding: utf-8 -*-
# PeekAPI PyInstaller Spec File
# 使用方法: uv run pyinstaller peekapi.spec

import shutil
from pathlib import Path

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('peekapi.ico', '.')],
    hiddenimports=[
        # msgspec 相关
        'msgspec',
        'msgspec.toml',

        # soundcard 相关
        'soundcard',
        'soundcard.mediafoundation',

        # soundfile 相关
        'soundfile',

        # numpy 核心
        'numpy',
        'numpy.core',

        # 其他
        'PIL._tkinter_finder',
        'pystray._win32',
        'loguru',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'setuptools',       # 打包工具
        'tkinter',          # GUI 库
        'unittest',         # 测试库
        'pydoc',            # 文档工具
        'difflib',          # 代码对比
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='peekapi',
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
    icon='peekapi.ico',
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[
        # 这些 DLL 不能被 UPX 压缩
        'vcruntime140.dll',
        'vcruntime140_1.dll',
        'python*.dll',
        'api-ms-*.dll',
        'ucrtbase.dll',
    ],
    name='peekapi',
)

# 复制用户文件到输出目录（exe 同级）
dist_dir = Path('dist/peekapi')
shutil.copy('config.toml', dist_dir / 'config.toml')

# ===== 清理不需要的文件以减少体积 =====
internal_dir = dist_dir / '_internal'
if internal_dir.exists():
    import glob

    # 删除 .pyi 类型提示文件
    for pyi in internal_dir.rglob('*.pyi'):
        pyi.unlink()

    # 删除 __pycache__ 目录
    for cache in internal_dir.rglob('__pycache__'):
        if cache.is_dir():
            shutil.rmtree(cache, ignore_errors=True)

    # 删除测试相关目录
    for test_dir in ['tests', 'test', 'testing']:
        for d in internal_dir.rglob(test_dir):
            if d.is_dir():
                shutil.rmtree(d, ignore_errors=True)

    print("清理完成: 已删除 .pyi, __pycache__, 和测试目录")

