import sys
import tomllib
from pathlib import Path

from pydantic import BaseModel


def get_icon_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "peekapi.ico"
    return Path() / "peekapi.ico"


def get_config_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent / "config.toml"
    return Path() / "config.toml"


class BasicConfig(BaseModel):
    is_public: bool = True
    api_key: str = "Imkei"
    host: str = "0.0.0.0"
    port: int = 1920


class ScreenshotConfig(BaseModel):
    radius_threshold: int = 3
    main_screen_only: bool = False


class RecordConfig(BaseModel):
    duration: int = 20
    gain: float = 20.0


class Config(BaseModel):
    basic: BasicConfig = BasicConfig()
    screenshot: ScreenshotConfig = ScreenshotConfig()
    record: RecordConfig = RecordConfig()

    @classmethod
    def load(cls) -> "Config":
        """读取并解析 config.toml 配置"""
        config_path = get_config_path()
        if not config_path.exists():
            config_path.write_text("")
            return cls()

        with open(config_path, "rb") as f:
            content = f.read()
            if not content:
                return cls()
            cfg = tomllib.loads(content.decode("utf-8"))

        return cls(**cfg)

    # 便捷属性访问
    @property
    def is_public(self) -> bool:
        return self.basic.is_public

    @is_public.setter
    def is_public(self, value: bool):
        self.basic.is_public = value

    @property
    def api_key(self) -> str:
        return self.basic.api_key

    @property
    def host(self) -> str:
        return self.basic.host

    @property
    def port(self) -> int:
        return self.basic.port

    @property
    def radius_threshold(self) -> int:
        return self.screenshot.radius_threshold

    @property
    def main_screen_only(self) -> bool:
        return self.screenshot.main_screen_only

    @property
    def duration(self) -> int:
        return self.record.duration

    @property
    def gain(self) -> float:
        return self.record.gain


config = Config.load()
ICON_PATH = get_icon_path()
