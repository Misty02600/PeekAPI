"""路径和应用常量定义"""

import sys
from pathlib import Path


def _get_base_dir() -> Path:
    """获取基础目录：打包后为 exe 目录，开发时为运行目录"""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path.cwd()


def _get_icon_path() -> Path:
    """获取图标路径：打包后从 _MEIPASS，开发时为运行目录"""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "peekapi.ico"
    return _get_base_dir() / "peekapi.ico"


# 常量
BASE_DIR = _get_base_dir()
CONFIG_PATH = BASE_DIR / "config.toml"
ICON_PATH = _get_icon_path()
LOG_DIR = BASE_DIR / "logs"

# 录音相关常量
RECONNECT_DELAY_SECONDS = 2.0  # 设备重连延迟（秒）
MAX_CONSECUTIVE_ERRORS = 5     # 最大连续错误次数

# 应用信息
APP_ID = "PeekAPI"

# 确保配置文件存在
if not CONFIG_PATH.exists():
    CONFIG_PATH.write_text("")
