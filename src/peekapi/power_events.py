"""Windows 电源事件处理模块

通过两种机制监听系统休眠/唤醒事件，在休眠前暂停录音设备，
唤醒后重新初始化，防止 WASAPI COM 调用在设备失效状态下导致进程崩溃。

机制 1: RegisterSuspendResumeNotification (DEVICE_NOTIFY_CALLBACK)
  - 不依赖窗口消息循环，直接注册内核级回调
  - 能可靠接收 Modern Standby (S0) 和 Hibernate (S4) 的通知
  - 这是主要机制

机制 2: WM_POWERBROADCAST (注入 pystray 消息处理器)
  - 作为辅助/备用机制
  - 依赖 pystray 的窗口消息循环
"""

import ctypes
import ctypes.wintypes
import threading

from .logging import logger

# region Windows 电源事件常量
WM_POWERBROADCAST = 0x0218
PBT_APMSUSPEND = 0x0004  # 系统即将进入休眠/待机
PBT_APMRESUMESUSPEND = 0x0007  # 系统从休眠/待机恢复（用户活动触发）
PBT_APMRESUMEAUTOMATIC = 0x0012  # 系统从休眠/待机自动恢复
DEVICE_NOTIFY_CALLBACK = 2
# endregion

# region 回调类型定义

# typedef ULONG CALLBACK DEVICE_NOTIFY_CALLBACK_ROUTINE(
#   PVOID Context, ULONG Type, PVOID Setting
# );
DEVICE_NOTIFY_CALLBACK_ROUTINE = ctypes.CFUNCTYPE(
    ctypes.c_ulong,  # return ULONG
    ctypes.c_void_p,  # Context (PVOID)
    ctypes.c_ulong,  # Type (ULONG) — PBT_APMSUSPEND 等
    ctypes.c_void_p,  # Setting (PVOID)
)


class _DEVICE_NOTIFY_SUBSCRIBE_PARAMETERS(ctypes.Structure):
    """DEVICE_NOTIFY_SUBSCRIBE_PARAMETERS 结构体"""

    _fields_ = [
        ("Callback", DEVICE_NOTIFY_CALLBACK_ROUTINE),
        ("Context", ctypes.c_void_p),
    ]


# endregion

# region 全局状态
# 必须保持对回调和结构体的引用，防止被 GC 回收导致野指针
_callback_ref = None
_params_ref = None
_registration_handle = None
_recorder_ref = None
_suspended = False
_lock = threading.Lock()
# endregion


def _on_power_event(context, event_type, setting):
    """
    RegisterSuspendResumeNotification 的回调函数。

    注意：此回调由 Windows 内核在任意线程上调用，必须线程安全。

    Args:
        context: 用户自定义上下文（未使用）
        event_type: 电源事件类型（PBT_APMSUSPEND 等）
        setting: 事件相关设置（未使用）

    Returns:
        0 表示成功
    """
    global _suspended

    try:
        with _lock:
            recorder = _recorder_ref
            if recorder is None:
                return 0

            if event_type == PBT_APMSUSPEND:
                if not _suspended:
                    logger.info("系统即将休眠/待机，正在停止录音设备...")
                    _suspended = True
                    try:
                        recorder.stop_recording()
                        logger.info("录音设备已安全停止")
                    except Exception as e:
                        logger.error(f"停止录音设备时出错: {e}")

            elif event_type in (PBT_APMRESUMESUSPEND, PBT_APMRESUMEAUTOMATIC):
                if _suspended:
                    logger.info("系统已唤醒，正在重新启动录音设备...")
                    _suspended = False
                    try:
                        recorder.start_recording()
                        logger.info("录音设备已重新启动")
                    except Exception as e:
                        logger.error(f"重新启动录音设备时出错: {e}")
    except Exception as e:
        # 回调中的异常不能传播到 Windows 内核
        try:
            logger.error(f"电源事件回调异常: {e}")
        except Exception:
            pass

    return 0


def register_power_notification(recorder) -> bool:
    """
    使用 RegisterSuspendResumeNotification 注册电源事件回调。

    Args:
        recorder: AudioRecorder 实例

    Returns:
        True 如果注册成功，False 如果失败
    """
    global _callback_ref, _params_ref, _registration_handle, _recorder_ref

    _recorder_ref = recorder

    try:
        # 创建回调函数引用（必须保持全局引用！）
        _callback_ref = DEVICE_NOTIFY_CALLBACK_ROUTINE(_on_power_event)

        # 创建参数结构体
        _params_ref = _DEVICE_NOTIFY_SUBSCRIBE_PARAMETERS(
            Callback=_callback_ref,
            Context=None,
        )

        # 调用 RegisterSuspendResumeNotification
        # HPOWERNOTIFY RegisterSuspendResumeNotification(
        #   HANDLE hRecipient,    -- 为 DEVICE_NOTIFY_CALLBACK 类型时指向结构体
        #   DWORD Flags           -- DEVICE_NOTIFY_CALLBACK
        # )
        handle = ctypes.wintypes.HANDLE()
        result = ctypes.windll.powrprof.PowerRegisterSuspendResumeNotification(
            DEVICE_NOTIFY_CALLBACK,
            ctypes.byref(_params_ref),
            ctypes.byref(handle),
        )

        if result == 0:  # ERROR_SUCCESS
            _registration_handle = handle
            logger.info("电源事件回调已注册 (PowerRegisterSuspendResumeNotification)")
            return True
        else:
            logger.warning(
                f"PowerRegisterSuspendResumeNotification 失败，错误码: {result}"
            )
            return False

    except Exception as e:
        logger.warning(f"注册电源事件回调失败: {e}")
        return False


def setup_power_event_handler(icon) -> None:
    """将 WM_POWERBROADCAST 处理器注入到 pystray 图标的消息处理器中。

    作为 RegisterSuspendResumeNotification 的辅助/备用机制。
    要求先调用 register_power_notification 设置 _recorder_ref。

    Args:
        icon: pystray.Icon 实例
    """

    def on_power_broadcast(wparam, lparam):
        """处理 WM_POWERBROADCAST 消息"""
        # 复用同一个回调逻辑
        _on_power_event(None, wparam, None)
        return True

    if hasattr(icon, "_message_handlers"):
        icon._message_handlers[WM_POWERBROADCAST] = on_power_broadcast
        logger.info("WM_POWERBROADCAST 处理器已注入 pystray")
    else:
        logger.warning("无法注入 WM_POWERBROADCAST 处理器: pystray 版本不兼容")
