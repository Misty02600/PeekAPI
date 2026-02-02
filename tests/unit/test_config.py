"""配置模块测试"""

from msgspec import toml

from peekapi.config import BasicConfig, Config, RecordConfig, ScreenshotConfig


class TestBasicConfig:
    """BasicConfig 测试"""

    def test_default_values(self):
        """测试默认值"""
        config = BasicConfig()
        assert config.is_public is True
        assert config.api_key == ""
        assert config.host == "0.0.0.0"
        assert config.port == 1920

    def test_custom_values(self):
        """测试自定义值"""
        config = BasicConfig(
            is_public=False,
            api_key="my-secret-key",
            host="127.0.0.1",
            port=8080,
        )
        assert config.is_public is False
        assert config.api_key == "my-secret-key"
        assert config.host == "127.0.0.1"
        assert config.port == 8080

    def test_is_public_mutable(self):
        """测试 is_public 可在运行时修改"""
        config = BasicConfig()
        assert config.is_public is True
        config.is_public = False
        assert config.is_public is False


class TestScreenshotConfig:
    """ScreenshotConfig 测试"""

    def test_default_values(self):
        """测试默认值"""
        config = ScreenshotConfig()
        assert config.radius_threshold == 3
        assert config.main_screen_only is False

    def test_custom_values(self):
        """测试自定义值"""
        config = ScreenshotConfig(radius_threshold=10, main_screen_only=True)
        assert config.radius_threshold == 10
        assert config.main_screen_only is True


class TestRecordConfig:
    """RecordConfig 测试"""

    def test_default_values(self):
        """测试默认值"""
        config = RecordConfig()
        assert config.duration == 20
        assert config.gain == 20.0

    def test_custom_values(self):
        """测试自定义值"""
        config = RecordConfig(duration=60, gain=5.5)
        assert config.duration == 60
        assert config.gain == 5.5


class TestConfig:
    """Config 主配置类测试"""

    def test_default_nested_values(self):
        """测试嵌套默认值"""
        config = Config()
        # 验证嵌套对象被正确创建
        assert isinstance(config.basic, BasicConfig)
        assert isinstance(config.screenshot, ScreenshotConfig)
        assert isinstance(config.record, RecordConfig)

        # 验证嵌套默认值
        assert config.basic.is_public is True
        assert config.screenshot.radius_threshold == 3
        assert config.record.duration == 20

    def test_toml_decode_empty(self):
        """测试空 TOML 文件加载（使用全部默认值）"""
        content = b""
        config = toml.decode(content, type=Config)

        assert config.basic.is_public is True
        assert config.basic.api_key == ""
        assert config.screenshot.radius_threshold == 3
        assert config.record.duration == 20

    def test_toml_decode_partial(self):
        """测试部分 TOML 配置（部分覆盖默认值）"""
        content = b"""
[basic]
is_public = false
api_key = "secret"

[record]
duration = 60
"""
        config = toml.decode(content, type=Config)

        # 被覆盖的值
        assert config.basic.is_public is False
        assert config.basic.api_key == "secret"
        assert config.record.duration == 60

        # 保持默认的值
        assert config.basic.host == "0.0.0.0"
        assert config.basic.port == 1920
        assert config.screenshot.radius_threshold == 3
        assert config.record.gain == 20.0

    def test_toml_decode_full(self, sample_config_content):
        """测试完整 TOML 配置"""
        content = sample_config_content.encode()
        config = toml.decode(content, type=Config)

        assert config.basic.is_public is False
        assert config.basic.api_key == "test-key-123"
        assert config.basic.host == "127.0.0.1"
        assert config.basic.port == 8080
        assert config.screenshot.radius_threshold == 5
        assert config.screenshot.main_screen_only is True
        assert config.record.duration == 30
        assert config.record.gain == 15.0

    def test_nested_access_pattern(self):
        """测试嵌套访问模式 config.basic.is_public"""
        config = Config()

        # 直接嵌套访问
        assert config.basic.is_public is True
        assert config.screenshot.main_screen_only is False
        assert config.record.gain == 20.0

        # 修改嵌套值
        config.basic.is_public = False
        assert config.basic.is_public is False

    def test_config_instances_independent(self):
        """测试多个 Config 实例相互独立"""
        config1 = Config()
        config2 = Config()

        config1.basic.is_public = False
        config1.record.duration = 999

        # config2 不受影响
        assert config2.basic.is_public is True
        assert config2.record.duration == 20
