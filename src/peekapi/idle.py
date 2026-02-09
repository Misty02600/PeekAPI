"""用户空闲时间检测模块

使用 Windows GetLastInputInfo API 获取用户最后操作电脑的时间。
"""

import ctypes
from ctypes import Structure, c_uint, sizeof
from datetime import datetime, timedelta, timezone

# 北京时间时区
_BEIJING_TZ = timezone(timedelta(hours=8))


class LASTINPUTINFO(Structure):
    """Windows LASTINPUTINFO 结构体"""

    _fields_ = [
        ("cbSize", c_uint),
        ("dwTime", c_uint),
    ]


def get_idle_info() -> tuple[float, datetime]:
    """
    获取用户空闲时间信息

    Returns:
        tuple[float, datetime]: (空闲秒数, 最后操作时间)

    Note:
        最后操作时间使用北京时间（UTC+8）
    """
    lii = LASTINPUTINFO()
    lii.cbSize = sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))

    # GetTickCount 返回系统启动后的毫秒数
    current_tick = ctypes.windll.kernel32.GetTickCount()
    idle_ms = current_tick - lii.dwTime
    idle_seconds = idle_ms / 1000.0

    # 计算最后操作时间
    last_input_time = datetime.now(_BEIJING_TZ) - timedelta(seconds=idle_seconds)

    return idle_seconds, last_input_time
