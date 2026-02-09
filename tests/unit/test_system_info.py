"""系统信息模块测试"""

import socket
import sys
from unittest.mock import MagicMock, patch

import pytest


class TestGetSystemInfo:
    """get_system_info 函数测试"""

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_system_info_returns_dict(self):
        """验证返回类型为字典"""
        from peekapi.system_info import get_system_info

        result = get_system_info()

        assert isinstance(result, dict)
        assert "hostname" in result
        assert "computer_model" in result
        assert "motherboard" in result
        assert "cpu" in result
        assert "gpus" in result

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_system_info_hostname_default(self):
        """验证默认使用系统主机名"""
        from peekapi.system_info import get_system_info

        result = get_system_info()

        # 不传参数时应该使用系统主机名
        assert result["hostname"] == socket.gethostname()

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_system_info_hostname_override(self):
        """验证 device_name 覆盖主机名"""
        from peekapi.system_info import get_system_info

        custom_name = "MyCustomDevice"
        result = get_system_info(device_name_override=custom_name)

        assert result["hostname"] == custom_name

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_system_info_hostname_empty_string_uses_system(self):
        """验证空字符串使用系统主机名"""
        from peekapi.system_info import get_system_info

        result = get_system_info(device_name_override="")

        assert result["hostname"] == socket.gethostname()

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_system_info_gpus_is_list(self):
        """验证 gpus 是列表类型"""
        from peekapi.system_info import get_system_info

        result = get_system_info()

        assert isinstance(result["gpus"], list)

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_system_info_all_fields_are_strings(self):
        """验证除 gpus 外所有字段都是字符串"""
        from peekapi.system_info import get_system_info

        result = get_system_info()

        assert isinstance(result["hostname"], str)
        assert isinstance(result["computer_model"], str)
        assert isinstance(result["motherboard"], str)
        assert isinstance(result["cpu"], str)


class TestSystemInfoMocked:
    """使用 mock 的系统信息测试（跨平台）"""

    def test_get_system_info_with_mocked_powershell(self):
        """测试使用 mock 的 PowerShell 调用"""
        mock_run = MagicMock()

        # 模拟 PowerShell 返回的 JSON
        def side_effect(args, **kwargs):
            cmd = args[2] if len(args) > 2 else ""
            result = MagicMock()
            result.returncode = 0

            if "Win32_ComputerSystem" in cmd:
                result.stdout = '{"Model": "TestModel"}'
            elif "Win32_BaseBoard" in cmd:
                result.stdout = '{"Manufacturer": "TestMfg", "Product": "TestBoard"}'
            elif "Win32_Processor" in cmd:
                result.stdout = '{"Name": "TestCPU"}'
            elif "Win32_VideoController" in cmd:
                result.stdout = '{"Name": "TestGPU"}'
            else:
                result.stdout = "{}"

            return result

        mock_run.side_effect = side_effect

        with patch("peekapi.system_info.subprocess.run", mock_run):
            from peekapi.system_info import get_system_info

            result = get_system_info("MockedHost")

            assert result["hostname"] == "MockedHost"
            assert result["computer_model"] == "TestModel"
            assert result["motherboard"] == "TestMfg TestBoard"
            assert result["cpu"] == "TestCPU"
            assert result["gpus"] == ["TestGPU"]

    def test_get_system_info_handles_powershell_failure(self):
        """测试 PowerShell 失败时返回 Unknown"""
        mock_run = MagicMock()
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""

        with patch("peekapi.system_info.subprocess.run", mock_run):
            from peekapi.system_info import get_system_info

            result = get_system_info("TestHost")

            assert result["hostname"] == "TestHost"
            assert result["computer_model"] == "Unknown"
            assert result["motherboard"] == "Unknown"
            assert result["cpu"] == "Unknown"
            assert result["gpus"] == []

    def test_get_system_info_handles_multiple_gpus(self):
        """测试多显卡情况"""
        mock_run = MagicMock()

        def side_effect(args, **kwargs):
            cmd = args[2] if len(args) > 2 else ""
            result = MagicMock()
            result.returncode = 0

            if "Win32_VideoController" in cmd:
                result.stdout = '[{"Name": "GPU1"}, {"Name": "GPU2"}]'
            else:
                result.stdout = '{"Model": "Test", "Manufacturer": "Test", "Product": "Test", "Name": "Test"}'

            return result

        mock_run.side_effect = side_effect

        with patch("peekapi.system_info.subprocess.run", mock_run):
            from peekapi.system_info import get_system_info

            result = get_system_info()

            assert result["gpus"] == ["GPU1", "GPU2"]

    def test_get_system_info_handles_timeout(self):
        """测试 PowerShell 超时情况"""
        import subprocess

        mock_run = MagicMock()
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="test", timeout=10)

        with patch("peekapi.system_info.subprocess.run", mock_run):
            from peekapi.system_info import get_system_info

            result = get_system_info("TestHost")

            # 超时时应返回 Unknown
            assert result["hostname"] == "TestHost"
            assert result["computer_model"] == "Unknown"


class TestInfoRouteIntegration:
    """Server /info 路由集成测试"""

    @pytest.fixture
    def app_client(self):
        """创建 FastAPI 测试客户端"""
        from io import BytesIO

        from fastapi.testclient import TestClient

        with patch("peekapi.server.recorder") as mock_recorder:
            with patch("peekapi.server.config") as mock_config:
                # 设置默认配置
                mock_config.basic.is_public = True
                mock_config.basic.device_name = ""
                mock_config.basic.api_key = ""
                mock_config.basic.host = "127.0.0.1"
                mock_config.basic.port = 8000
                mock_config.screenshot.radius_threshold = 10
                mock_config.screenshot.main_screen_only = True

                # Mock recorder
                mock_audio = BytesIO(b"RIFF" + b"\x00" * 40)
                mock_audio.seek(0)
                mock_recorder.get_audio.return_value = mock_audio

                from peekapi.server import app

                client = TestClient(app, raise_server_exceptions=False)

                yield {
                    "client": client,
                    "config": mock_config,
                    "recorder": mock_recorder,
                }

    def test_info_route_public_mode(self, app_client):
        """测试公开模式下 /info 返回成功"""
        with patch("peekapi.server.get_system_info") as mock_info:
            mock_info.return_value = {
                "hostname": "TestPC",
                "computer_model": "TestModel",
                "motherboard": "TestBoard",
                "cpu": "TestCPU",
                "gpus": ["TestGPU"],
            }

            response = app_client["client"].get("/info")

            assert response.status_code == 200
            data = response.json()
            assert data["hostname"] == "TestPC"
            assert data["cpu"] == "TestCPU"

    def test_info_route_private_mode(self, app_client):
        """测试私密模式下 /info 返回 403"""
        app_client["config"].basic.is_public = False

        response = app_client["client"].get("/info")

        assert response.status_code == 403
        assert "瑟瑟中" in response.content.decode("utf-8")

    def test_info_route_uses_device_name_config(self, app_client):
        """测试 /info 使用配置的 device_name"""
        app_client["config"].basic.device_name = "ConfiguredName"

        with patch("peekapi.server.get_system_info") as mock_info:
            mock_info.return_value = {"hostname": "ConfiguredName"}

            app_client["client"].get("/info")

            # 验证调用时传入了配置的 device_name
            mock_info.assert_called_once_with("ConfiguredName")
