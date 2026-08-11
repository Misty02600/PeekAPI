import os
import subprocess

import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as Item

from .autostart import (
    AutostartError,
    disable_autostart,
    enable_autostart,
    is_autostart_enabled,
    is_packaged_app,
)
from .config import config
from .constants import ICON_PATH, LOG_DIR
from .logging import logger
from .power_events import setup_power_event_handler
from .record import recorder


def create_icon():
    """创建托盘图标，如果找不到就生成默认图标"""
    if os.path.exists(ICON_PATH):
        return Image.open(ICON_PATH)
    else:
        logger.warning(f"图标文件不存在: {ICON_PATH}，使用默认图标")
        image = Image.new("RGB", (64, 64), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle([16, 16, 48, 48], fill="black")
        return image


def set_public(_icon, _item):
    if not config.basic.is_public:
        config.basic.is_public = True
        logger.info("模式已切换: 公开")


def set_private(_icon, _item):
    if config.basic.is_public:
        config.basic.is_public = False
        logger.info("模式已切换: 私密")


def restart_recording(_icon, _item):
    recorder.stop_recording()
    recorder.start_recording()


def open_log_folder(_icon, _item):
    """打开日志文件夹"""
    subprocess.run(["explorer", str(LOG_DIR)])


def _is_autostart_checked(_item):
    try:
        return is_autostart_enabled()
    except AutostartError as error:
        logger.warning(f"无法查询登录自启状态: {error}")
        return False


def toggle_autostart(icon, _item):
    try:
        if is_autostart_enabled():
            disable_autostart()
            logger.info("已禁用登录时自动启动")
        else:
            migrated = enable_autostart()
            if migrated:
                logger.info("已迁移旧计划任务并启用登录时自动启动")
            else:
                logger.info("已启用登录时自动启动")
    except AutostartError as error:
        logger.warning(f"切换登录自启失败: {error}")
    finally:
        icon.update_menu()


def exit_app(icon, _item):
    """退出应用"""
    logger.info("用户退出应用")
    icon.stop()
    os._exit(0)


def _on_tray_ready(icon):
    """托盘图标就绪后的回调，用于注册电源事件处理器"""
    icon.visible = True
    setup_power_event_handler(icon)


def start_system_tray():
    """启动托盘菜单"""
    icon_image = create_icon()

    # 创建托盘图标
    icon = pystray.Icon(
        "ChieriBotPeekAPI",
        icon=icon_image,
        menu=pystray.Menu(
            Item(
                "模式切换",
                pystray.Menu(
                    Item(
                        "公开",
                        set_public,
                        checked=lambda item: config.basic.is_public,
                        radio=True,
                    ),
                    Item(
                        "私密",
                        set_private,
                        checked=lambda item: not config.basic.is_public,
                        radio=True,
                    ),
                ),
            ),
            Item("重启录音", restart_recording),
            Item(
                "登录时自动启动",
                toggle_autostart,
                checked=_is_autostart_checked,
                enabled=is_packaged_app(),
            ),
            Item("打开日志", open_log_folder),
            Item("退出", exit_app),
        ),
    )

    icon.run(setup=_on_tray_ready)
