import sys
import ctypes
import logging
from src.server import start_app

def enable_console():
    """附加控制台"""
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

if __name__ == "__main__":
    if "--console" in sys.argv:
        enable_console()

    start_app()