"""截图模块集成测试 - 需要真实显示器"""

import io
import os

import pytest
from PIL import Image

# CI 环境自动跳过
pytestmark = pytest.mark.skipif(
    bool(os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS")),
    reason="集成测试需要真实显示器，CI 环境跳过",
)


class TestScreenshotIntegration:
    """截图功能集成测试"""

    def test_real_screenshot_returns_jpeg(self):
        """真实截图返回有效 JPEG"""
        from peekapi.screenshot import screenshot

        result = screenshot(radius=0, main_screen_only=True)

        assert result is not None
        assert isinstance(result, bytes)
        assert result[:3] == b"\xff\xd8\xff", "应返回有效 JPEG"

    def test_real_screenshot_can_open_as_image(self):
        """真实截图可作为图像打开"""
        from peekapi.screenshot import screenshot

        result = screenshot(radius=0, main_screen_only=True)
        img = Image.open(io.BytesIO(result))

        assert img.format == "JPEG"
        assert img.size[0] > 0
        assert img.size[1] > 0

    def test_real_screenshot_main_screen(self):
        """主屏幕截图"""
        from peekapi.screenshot import screenshot

        result = screenshot(radius=0, main_screen_only=True)
        img = Image.open(io.BytesIO(result))

        assert img.size[0] > 0

    def test_real_screenshot_all_screens(self):
        """全部屏幕截图"""
        from peekapi.screenshot import screenshot

        result = screenshot(radius=0, main_screen_only=False)
        img = Image.open(io.BytesIO(result))

        assert img.size[0] > 0

    def test_real_screenshot_with_blur(self):
        """真实截图带模糊效果"""
        from peekapi.screenshot import screenshot

        result_clear = screenshot(radius=0, main_screen_only=True)
        result_blur = screenshot(radius=10, main_screen_only=True)

        # 模糊后的图片应该和清晰图片不同
        assert result_clear != result_blur

    def test_real_screenshot_size_reasonable(self):
        """截图大小在合理范围内"""
        from peekapi.screenshot import screenshot

        result = screenshot(radius=0, main_screen_only=True)

        # JPEG 截图通常在 100KB - 10MB 之间
        size_kb = len(result) / 1024
        assert 10 < size_kb < 50000, f"截图大小异常: {size_kb:.1f} KB"
