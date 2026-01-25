"""配置管理模块"""

from msgspec import Struct, field
from msgspec import toml

from .constants import CONFIG_PATH


class BasicConfig(Struct):
    """基础配置"""

    is_public: bool = True
    api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 1920


class ScreenshotConfig(Struct):
    """截图配置"""

    radius_threshold: int = 3
    main_screen_only: bool = False


class RecordConfig(Struct):
    """录音配置"""

    duration: int = 20
    gain: float = 20.0


class Config(Struct):
    """主配置类"""

    basic: BasicConfig = field(default_factory=BasicConfig)
    screenshot: ScreenshotConfig = field(default_factory=ScreenshotConfig)
    record: RecordConfig = field(default_factory=RecordConfig)

    @classmethod
    def load(cls) -> "Config":
        """读取并解析 config.toml 配置"""
        content = CONFIG_PATH.read_bytes()
        return toml.decode(content, type=cls)


config = Config.load()
