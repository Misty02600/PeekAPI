import sys
import ctypes
import logging
from src.server import start_app

def enable_console_debug():
    """动态附加控制台并修复日志流"""
    # 1. 附加控制台
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    if not kernel32.AllocConsole():
        error_code = ctypes.get_last_error()
        raise ctypes.WinError(error_code)

    # 2. 重定向标准流
    sys.stdout = open('CONOUT$', 'w')
    sys.stderr = open('CONOUT$', 'w')
    sys.stdin = open('CONIN$', 'r')

    # 3. 修复日志模块的流
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            # 替换为当前有效的 sys.stderr
            handler.stream = sys.stderr

if __name__ == "__main__":
    if "--debug" in sys.argv:
        enable_console_debug()
        print("=== 调试模式已启动 ===")

    # 启动主程序
    start_app()