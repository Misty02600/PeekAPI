import os
import sys
import time

import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as Item
from winotify import Notification

from .config import config
from .record import recorder

ICON_PATH = "peekapi.ico"

def create_icon():
    """ 创建托盘图标，如果找不到就生成默认图标 """
    if os.path.exists(ICON_PATH):
        return Image.open(ICON_PATH)
    else:
        image = Image.new('RGB', (64, 64), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill="black")
        return image

def show_notification(title, message):
    """显示 Windows 通知"""
    toast = Notification(
        app_id="ChieriBotPeekAPI",
        title=title,
        msg=message,
        icon=ICON_PATH,
        duration="short"
    )
    toast.show()

def set_public(icon, item):
    if not config.is_public:
        config.is_public = True
        print("模式已切换", "当前模式：公开")

def set_private(icon, item):
    if config.is_public:
        config.is_public = False
        print("模式已切换", "当前模式：私密")

def restart_recording(icon, item):
    recorder.stop_recording()
    time.sleep(1)
    recorder.start_recording()
    print("已重新启动录音")
    show_notification("重启录音", "录音线程已重新启动")

def exit_app(icon, item):
    """ 退出应用 """
    icon.stop()
    os._exit(0)

def start_system_tray():
    """ 启动托盘菜单 """
    icon_image = create_icon()

    # 创建托盘图标
    icon = pystray.Icon(
        "ChieriBotPeekAPI",
        icon=icon_image,
        menu=pystray.Menu(
            Item("模式切换", pystray.Menu(
                Item("公开", set_public, checked=lambda item: config.is_public, radio=True),
                Item("私密", set_private, checked=lambda item: not config.is_public, radio=True)
            )),
            Item("重启录音", restart_recording),
            Item("退出", exit_app)
        )
    )

    def run_tray():
        try:
            icon.run()
        except Exception as e:
            print(f"托盘错误: {e}")
            show_notification("系统托盘错误", "请手动重启应用")
            sys.exit(1)

    run_tray()