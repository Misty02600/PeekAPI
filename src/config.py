import os
import sys
import tomllib

def get_icon_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "peekapi.ico")
    else:
        return os.path.join(os.path.dirname(__file__), "peekapi.ico")

def get_config_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), "config.toml")
    else:
        return os.path.join(os.path.dirname(__file__), "config.toml")

class Config:
    CONFIG_FILE = get_config_path()

    def __init__(self):
        """读取并解析 config.toml 配置"""
        if not os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                f.write("")

        with open(self.CONFIG_FILE, "rb") as f:
            cfg = tomllib.load(f) if f.read() else {}

        # 基础配置
        basic = cfg.get("basic", {})
        self.is_public = basic.get("is_public", True)
        self.api_key = basic.get("api_key", "Imkei")
        self.host = basic.get("host", "127.0.0.1")
        self.port = basic.get("port", 1920)

        # 截图配置
        screenshot = cfg.get("screenshot", {})
        self.radius_threshold = screenshot.get("radius_threshold", 3)
        self.main_screen_only = screenshot.get("main_screen_only", False)

        # 录音配置
        record = cfg.get("record", {})
        self.duration = record.get("duration", 20)
        self.gain = record.get("gain", 20.0)

config = Config()
ICON_PATH = get_icon_path()
