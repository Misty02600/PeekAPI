"""CLI 入口脚本"""
import sys
import ctypes
import logging


def enable_console() -> None:
    """在 Windows 上附加控制台"""
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    if not kernel32.AllocConsole():
        error_code = ctypes.get_last_error()
        raise ctypes.WinError(error_code)

    sys.stdout = open('CONOUT$', 'w')
    sys.stderr = open('CONOUT$', 'w')
    sys.stdin = open('CONIN$', 'r')

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.stream = sys.stderr


def main() -> None:
    """无控制台启动"""
    from .server import start_app
    start_app()


def main_console() -> None:
    """带控制台启动"""
    enable_console()
    main()


if __name__ == "__main__":
    if "--console" in sys.argv:
        main_console()
    else:
        main()
