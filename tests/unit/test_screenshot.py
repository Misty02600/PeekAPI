"""截图模块测试"""

import io
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image


class TestScreenshot:
    """截图功能测试"""

    @pytest.fixture
    def mock_mss(self):
        """模拟 mss 截图库"""
        # 创建 100x100 的测试图像数据 (RGB)
        width, height = 100, 100
        rgb_data = b"\xff\x00\x00" * (width * height)  # 红色像素

        mock_img = MagicMock()
        mock_img.size = (width, height)
        mock_img.rgb = rgb_data

        mock_sct = MagicMock()
        mock_sct.monitors = [
            {"top": 0, "left": 0, "width": 200, "height": 100},  # 全部屏幕
            {"top": 0, "left": 0, "width": 100, "height": 100},  # 主屏幕
        ]
        mock_sct.grab.return_value = mock_img
        mock_sct.__enter__ = MagicMock(return_value=mock_sct)
        mock_sct.__exit__ = MagicMock(return_value=False)

        with patch("peekapi.screenshot.mss.mss", return_value=mock_sct):
            yield mock_sct

    def test_screenshot_returns_bytes(self, mock_mss):
        """验证截图返回字节数据"""
        from peekapi.screenshot import screenshot

        result = screenshot(radius=0, main_screen_only=True)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_screenshot_returns_valid_jpeg(self, mock_mss):
        """验证返回有效的 JPEG 格式（检查魔数）"""
        from peekapi.screenshot import screenshot

        result = screenshot(radius=0, main_screen_only=True)

        # JPEG 文件以 \xff\xd8\xff 开头
        assert result[:3] == b"\xff\xd8\xff", "返回的不是有效的 JPEG 格式"

    def test_screenshot_can_open_as_image(self, mock_mss):
        """验证返回的数据可以作为图像打开"""
        from peekapi.screenshot import screenshot

        result = screenshot(radius=0, main_screen_only=True)
        img = Image.open(io.BytesIO(result))

        assert img.format == "JPEG"
        assert img.size == (100, 100)

    def test_screenshot_main_screen_only(self, mock_mss):
        """验证 main_screen_only=True 使用 monitors[1]"""
        from peekapi.screenshot import screenshot

        screenshot(radius=0, main_screen_only=True)

        # 验证 grab 被调用时使用了 monitors[1]（主屏幕）
        mock_mss.grab.assert_called_once()
        called_monitor = mock_mss.grab.call_args[0][0]
        assert called_monitor == mock_mss.monitors[1]

    def test_screenshot_all_screens(self, mock_mss):
        """验证 main_screen_only=False 使用 monitors[0]"""
        from peekapi.screenshot import screenshot

        screenshot(radius=0, main_screen_only=False)

        # 验证 grab 被调用时使用了 monitors[0]（全部屏幕）
        mock_mss.grab.assert_called_once()
        called_monitor = mock_mss.grab.call_args[0][0]
        assert called_monitor == mock_mss.monitors[0]

    def test_screenshot_with_blur_calls_filter(self, mock_mss):
        """验证 radius > 0 时调用 filter 方法"""
        from peekapi.screenshot import screenshot

        with patch("PIL.Image.Image.filter") as mock_filter:
            # 返回原图以完成后续处理
            mock_filter.return_value = Image.new("RGB", (100, 100), color="red")

            screenshot(radius=10, main_screen_only=True)

            # 验证 filter 被调用
            mock_filter.assert_called_once()

    def test_screenshot_no_blur_radius_zero(self, mock_mss):
        """验证 radius=0 时不调用 filter 方法"""
        from peekapi.screenshot import screenshot

        with patch("PIL.Image.Image.filter") as mock_filter:
            screenshot(radius=0, main_screen_only=True)

            # 验证 filter 未被调用
            mock_filter.assert_not_called()

    def test_screenshot_blur_applies_gaussian(self, mock_mss):
        """验证模糊使用 GaussianBlur 滤镜"""
        from PIL import ImageFilter

        from peekapi.screenshot import screenshot

        with patch("PIL.Image.Image.filter") as mock_filter:
            mock_filter.return_value = Image.new("RGB", (100, 100), color="red")

            screenshot(radius=15, main_screen_only=True)

            # 获取传入 filter 的参数
            call_args = mock_filter.call_args[0][0]
            assert isinstance(call_args, ImageFilter.GaussianBlur)
