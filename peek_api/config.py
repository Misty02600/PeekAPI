import tomllib

class Config:
    CONFIG_FILE = "config.toml"

    def __init__(self):
        """读取并解析 config.toml 配置"""
        with open(self.CONFIG_FILE, "rb") as f:
            cfg = tomllib.load(f)

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
        self.duration = record.get("duration", 8)
        self.gain = record.get("gain", 20.0)

# 全局配置实例
config = Config()