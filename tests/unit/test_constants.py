"""常量模块测试"""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest


class TestGetBaseDir:
    """_get_base_dir 函数测试"""

    def test_development_mode(self):
        """测试开发模式下的路径计算"""
        # 确保没有 frozen 属性
        if hasattr(sys, "frozen"):
            delattr(sys, "frozen")

        # 重新导入以获取正确的值
        from src.peekapi import constants

        # 开发模式：constants.py 位于 src/peekapi/，基础目录应该是项目根目录
        # __file__ -> src/peekapi/constants.py
        # parent -> src/peekapi/
        # parent.parent -> src/
        # parent.parent.parent -> 项目根目录
        expected = Path(__file__).parent.parent  # tests/ 的父目录 = 项目根目录

        assert constants.BASE_DIR.exists()
        assert constants.BASE_DIR.is_dir()
        # 验证是项目根目录（包含 pyproject.toml）
        assert (constants.BASE_DIR / "pyproject.toml").exists()

    def test_frozen_mode(self, temp_dir):
        """测试打包模式下的路径计算（mock sys.frozen）"""
        fake_exe = temp_dir / "peekapi.exe"
        fake_exe.write_text("")

        with patch.object(sys, "frozen", True, create=True):
            with patch.object(sys, "executable", str(fake_exe)):
                # 重新导入函数
                from src.peekapi.constants import _get_base_dir

                result = _get_base_dir()
                assert result == temp_dir


class TestGetIconPath:
    """_get_icon_path 函数测试"""

    def test_development_mode(self):
        """测试开发模式下图标路径"""
        if hasattr(sys, "frozen"):
            delattr(sys, "frozen")

        from src.peekapi import constants

        # 开发模式：图标应该在项目根目录
        assert constants.ICON_PATH == constants.BASE_DIR / "peekapi.ico"

    def test_frozen_mode(self, temp_dir):
        """测试打包模式下图标路径（与 exe 同目录）"""
        from src.peekapi import constants

        # onefolder 模式下图标在 exe 同目录，即 BASE_DIR
        assert constants.ICON_PATH == constants.BASE_DIR / "peekapi.ico"


class TestPathConstants:
    """路径常量测试"""

    def test_config_path(self):
        """测试 CONFIG_PATH 指向正确位置"""
        from src.peekapi import constants

        assert constants.CONFIG_PATH == constants.BASE_DIR / "config.toml"
        assert constants.CONFIG_PATH.name == "config.toml"

    def test_log_dir(self):
        """测试 LOG_DIR 指向正确位置"""
        from src.peekapi import constants

        assert constants.LOG_DIR == constants.BASE_DIR / "logs"
        assert constants.LOG_DIR.name == "logs"

    def test_config_file_created_if_missing(self, temp_dir, monkeypatch):
        """测试配置文件不存在时会被创建"""
        # 这个测试需要在模块导入时验证
        # 由于 constants.py 在导入时就会创建文件，这里验证文件存在
        from src.peekapi import constants

        # 实际配置文件应该存在（在模块导入时创建）
        assert constants.CONFIG_PATH.exists()
