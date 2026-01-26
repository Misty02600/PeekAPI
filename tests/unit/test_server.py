"""Flask 服务器 API 端点测试"""

import io
from unittest.mock import MagicMock, patch

import pytest


class TestServerRoutes:
    """API 路由测试"""

    @pytest.fixture
    def app_client(self):
        """创建 Flask 测试客户端"""
        # Mock 依赖模块
        with patch('src.peekapi.server.recorder') as mock_recorder:
            with patch('src.peekapi.server.config') as mock_config:
                # 设置默认配置
                mock_config.basic.is_public = True
                mock_config.basic.api_key = ""
                mock_config.basic.host = "127.0.0.1"
                mock_config.basic.port = 8000
                mock_config.screenshot.radius_threshold = 10
                mock_config.screenshot.main_screen_only = True

                # Mock recorder
                mock_audio = io.BytesIO(b'RIFF' + b'\x00' * 40)  # 简化的 WAV
                mock_audio.seek(0)
                mock_recorder.get_audio.return_value = mock_audio

                from src.peekapi.server import app
                app.config['TESTING'] = True

                with app.test_client() as client:
                    yield {
                        'client': client,
                        'config': mock_config,
                        'recorder': mock_recorder,
                    }

    # ============ /check 端点测试 ============

    def test_check_get_returns_ok(self, app_client):
        """GET /check 返回 200 OK"""
        response = app_client['client'].get('/check')

        assert response.status_code == 200
        assert response.data == b'ok'

    def test_check_post_returns_ok(self, app_client):
        """POST /check 返回 200 OK"""
        response = app_client['client'].post('/check')

        assert response.status_code == 200
        assert response.data == b'ok'

    # ============ /screen 端点测试 ============

    def test_screen_public_mode_returns_image(self, app_client):
        """公开模式下 /screen 返回图片"""
        mock_img_data = b'\xff\xd8\xff' + b'\x00' * 100  # JPEG 魔数

        with patch('src.peekapi.server.screenshot', return_value=mock_img_data):
            response = app_client['client'].get('/screen')

        assert response.status_code == 200
        assert response.content_type == 'image/jpeg'

    def test_screen_private_mode_returns_403(self, app_client):
        """私密模式下 /screen 返回 403"""
        app_client['config'].basic.is_public = False

        with patch('src.peekapi.server.screenshot', return_value=b'test'):
            response = app_client['client'].get('/screen')

        assert response.status_code == 403
        assert '瑟瑟中' in response.data.decode('utf-8')

    def test_screen_with_blur_radius(self, app_client):
        """验证模糊半径参数传递"""
        mock_img_data = b'\xff\xd8\xff' + b'\x00' * 100

        with patch('src.peekapi.server.screenshot', return_value=mock_img_data) as mock_screenshot:
            app_client['client'].get('/screen?r=15')

            mock_screenshot.assert_called_once()
            # 第一个参数是 radius
            assert mock_screenshot.call_args[0][0] == 15.0

    def test_screen_invalid_radius_uses_default(self, app_client):
        """无效的模糊半径使用默认值 0"""
        mock_img_data = b'\xff\xd8\xff' + b'\x00' * 100

        with patch('src.peekapi.server.screenshot', return_value=mock_img_data) as mock_screenshot:
            app_client['client'].get('/screen?r=invalid')

            mock_screenshot.assert_called_once()
            assert mock_screenshot.call_args[0][0] == 0  # 默认值

    def test_screen_api_key_required_for_clear_image(self, app_client):
        """高清图片（低模糊）需要 API Key"""
        app_client['config'].basic.api_key = "secret123"
        app_client['config'].screenshot.radius_threshold = 10

        # 请求 r=5（低于阈值），无 API Key
        response = app_client['client'].get('/screen?r=5')

        assert response.status_code == 401
        assert '没有权限' in response.data.decode('utf-8')

    def test_screen_api_key_valid_allows_clear_image(self, app_client):
        """正确的 API Key 允许获取高清图片"""
        app_client['config'].basic.api_key = "secret123"
        app_client['config'].screenshot.radius_threshold = 10
        mock_img_data = b'\xff\xd8\xff' + b'\x00' * 100

        with patch('src.peekapi.server.screenshot', return_value=mock_img_data):
            response = app_client['client'].get('/screen?r=5&k=secret123')

        assert response.status_code == 200

    def test_screen_blurred_image_no_key_required(self, app_client):
        """模糊图片（高模糊）不需要 API Key"""
        app_client['config'].basic.api_key = "secret123"
        app_client['config'].screenshot.radius_threshold = 10
        mock_img_data = b'\xff\xd8\xff' + b'\x00' * 100

        with patch('src.peekapi.server.screenshot', return_value=mock_img_data):
            # r=15 超过阈值，不需要 key
            response = app_client['client'].get('/screen?r=15')

        assert response.status_code == 200

    def test_screen_failure_returns_500(self, app_client):
        """截图失败返回 500"""
        with patch('src.peekapi.server.screenshot', return_value=None):
            response = app_client['client'].get('/screen')

        assert response.status_code == 500
        assert '截图失败' in response.data.decode('utf-8')

    def test_screen_main_screen_only_param(self, app_client):
        """验证 main_screen_only 参数正确传递"""
        mock_img_data = b'\xff\xd8\xff' + b'\x00' * 100
        app_client['config'].screenshot.main_screen_only = True

        with patch('src.peekapi.server.screenshot', return_value=mock_img_data) as mock_screenshot:
            app_client['client'].get('/screen')

            # 第二个参数是 main_screen_only
            assert mock_screenshot.call_args[0][1] is True

    def test_screen_main_screen_only_false(self, app_client):
        """验证 main_screen_only=False 参数传递"""
        mock_img_data = b'\xff\xd8\xff' + b'\x00' * 100
        app_client['config'].screenshot.main_screen_only = False

        with patch('src.peekapi.server.screenshot', return_value=mock_img_data) as mock_screenshot:
            app_client['client'].get('/screen')

            assert mock_screenshot.call_args[0][1] is False

    def test_screen_no_api_key_configured(self, app_client):
        """未配置 API Key 时，低模糊也不需要验证"""
        app_client['config'].basic.api_key = ""  # 空字符串
        app_client['config'].screenshot.radius_threshold = 10
        mock_img_data = b'\xff\xd8\xff' + b'\x00' * 100

        with patch('src.peekapi.server.screenshot', return_value=mock_img_data):
            # r=0 低于阈值，但无 API Key 配置
            response = app_client['client'].get('/screen?r=0')

        assert response.status_code == 200

    def test_screen_radius_equals_threshold(self, app_client):
        """radius 等于阈值时不需要 API Key"""
        app_client['config'].basic.api_key = "secret123"
        app_client['config'].screenshot.radius_threshold = 10
        mock_img_data = b'\xff\xd8\xff' + b'\x00' * 100

        with patch('src.peekapi.server.screenshot', return_value=mock_img_data):
            # r=10 等于阈值，不需要 key（只有 r < threshold 才需要）
            response = app_client['client'].get('/screen?r=10')

        assert response.status_code == 200

    def test_screen_negative_radius(self, app_client):
        """负数 radius 需要 API Key（小于阈值）"""
        app_client['config'].basic.api_key = "secret123"
        app_client['config'].screenshot.radius_threshold = 10

        # r=-5 小于阈值，需要 key
        response = app_client['client'].get('/screen?r=-5')

        assert response.status_code == 401

    def test_screen_wrong_api_key(self, app_client):
        """错误的 API Key 返回 401"""
        app_client['config'].basic.api_key = "secret123"
        app_client['config'].screenshot.radius_threshold = 10

        response = app_client['client'].get('/screen?r=5&k=wrongkey')

        assert response.status_code == 401

    # ============ /record 端点测试 ============

    def test_record_public_mode_returns_audio(self, app_client):
        """公开模式下 /record 返回音频"""
        response = app_client['client'].get('/record')

        assert response.status_code == 200
        assert response.content_type == 'audio/wav'

    def test_record_private_mode_returns_403(self, app_client):
        """私密模式下 /record 返回 403"""
        app_client['config'].basic.is_public = False

        response = app_client['client'].get('/record')

        assert response.status_code == 403
        assert '瑟瑟中' in response.data.decode('utf-8')

    def test_record_failure_returns_500(self, app_client):
        """录音获取失败返回 500"""
        app_client['recorder'].get_audio.return_value = None

        response = app_client['client'].get('/record')

        assert response.status_code == 500
        assert '录音获取失败' in response.data.decode('utf-8')

    def test_record_returns_wav_format(self, app_client):
        """验证返回数据是 WAV 格式"""
        response = app_client['client'].get('/record')

        assert response.status_code == 200
        # WAV 文件以 RIFF 开头
        assert response.data[:4] == b'RIFF'

    def test_record_check_before_public(self, app_client):
        """验证 /record 先获取音频再检查 is_public"""
        app_client['config'].basic.is_public = False

        response = app_client['client'].get('/record')

        # 即使 is_public=False，recorder.get_audio 仍会被调用
        app_client['recorder'].get_audio.assert_called_once()
        assert response.status_code == 403

    # ============ /favicon.ico 端点测试 ============

    def test_favicon_returns_icon_or_204(self, app_client):
        """favicon 返回图标或 204"""
        response = app_client['client'].get('/favicon.ico')

        # 可能返回图标文件或 204（文件不存在时）
        assert response.status_code in [200, 204]

    def test_favicon_file_not_found(self, app_client):
        """图标文件不存在时返回 204"""
        with patch('src.peekapi.server.send_file', side_effect=FileNotFoundError()):
            response = app_client['client'].get('/favicon.ico')

        assert response.status_code == 204

    # ============ 404 测试 ============

    def test_unknown_route_returns_404(self, app_client):
        """未知路由返回 404"""
        response = app_client['client'].get('/unknown')

        assert response.status_code == 404


class TestParseFloat:
    """parse_float 辅助函数测试"""

    def test_parse_float_valid_number(self):
        """有效数字字符串"""
        from src.peekapi.server import parse_float

        assert parse_float("3.14") == 3.14
        assert parse_float("10") == 10.0
        assert parse_float("-5.5") == -5.5

    def test_parse_float_invalid_returns_default(self):
        """无效输入返回默认值"""
        from src.peekapi.server import parse_float

        assert parse_float("invalid") == 0
        assert parse_float(None) == 0
        assert parse_float("") == 0

    def test_parse_float_custom_default(self):
        """自定义默认值"""
        from src.peekapi.server import parse_float

        assert parse_float("invalid", default=5.0) == 5.0
        assert parse_float(None, default=-1) == -1


class TestServerConfiguration:
    """服务器配置测试"""

    def test_app_exists(self):
        """验证 Flask app 实例存在"""
        with patch('src.peekapi.server.recorder'):
            with patch('src.peekapi.server.config'):
                from src.peekapi.server import app
                assert app is not None
                assert app.name == 'src.peekapi.server'
