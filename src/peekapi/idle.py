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

    # 使用 GetTickCount64 避免 49.7 天溢出问题
    GetTickCount64 = ctypes.windll.kernel32.GetTickCount64
    GetTickCount64.restype = ctypes.c_uint64
    current_tick = GetTickCount64()

    # dwTime 是 32 位，需要处理回绕
    # 取 current_tick 的低 32 位与 dwTime 比较
    current_tick_32 = current_tick & 0xFFFFFFFF
    if current_tick_32 >= lii.dwTime:
        idle_ms = current_tick_32 - lii.dwTime
    else:
        # 回绕情况：dwTime 在 GetTickCount 回绕之前设置
        idle_ms = (0xFFFFFFFF - lii.dwTime) + current_tick_32 + 1

    idle_seconds = idle_ms / 1000.0

    # 计算最后操作时间
    last_input_time = datetime.now(_BEIJING_TZ) - timedelta(seconds=idle_seconds)

    return idle_seconds, last_input_time
