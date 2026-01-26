"""共享测试 fixtures"""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """创建临时目录，测试结束后自动清理"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def temp_config_file(temp_dir):
    """创建临时配置文件"""
    config_path = temp_dir / "config.toml"
    config_path.write_text("")
    return config_path


@pytest.fixture
def sample_config_content():
    """示例配置内容"""
    return """
[basic]
is_public = false
api_key = "test-key-123"
host = "127.0.0.1"
port = 8080

[screenshot]
radius_threshold = 5
main_screen_only = true

[record]
duration = 30
gain = 15.0
"""
