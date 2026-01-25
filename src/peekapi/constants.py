"""路径常量定义"""

import sys
from pathlib import Path


def _get_base_dir() -> Path:
    """获取基础目录：打包后为 exe 目录，开发时为项目根目录"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent.parent


def _get_icon_path() -> Path:
    """获取图标路径

    打包后：从 PyInstaller 临时目录 (_MEIPASS) 获取
    开发时：从项目根目录获取
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "peekapi.ico"
    return _get_base_dir() / "peekapi.ico"


# 常量
BASE_DIR = _get_base_dir()
CONFIG_PATH = BASE_DIR / "config.toml"
ICON_PATH = _get_icon_path()
LOG_DIR = BASE_DIR / "logs"

# 确保配置文件存在
if not CONFIG_PATH.exists():
    CONFIG_PATH.write_text("")
