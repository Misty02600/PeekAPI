"""用户空闲时间模块测试"""

import sys
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest


class TestGetIdleInfo:
    """get_idle_info 函数测试"""

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_idle_info_returns_tuple(self):
        """验证返回类型为 (float, datetime) 元组"""
        from peekapi.idle import get_idle_info

        result = get_idle_info()

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], float)
        assert isinstance(result[1], datetime)

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_idle_info_returns_non_negative_seconds(self):
        """验证空闲秒数为非负数"""
        from peekapi.idle import get_idle_info

        idle_seconds, _ = get_idle_info()

        assert idle_seconds >= 0

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_idle_info_returns_valid_datetime(self):
        """验证最后操作时间是有效的日期时间"""
        from peekapi.idle import get_idle_info

        _, last_input_time = get_idle_info()

        # 检查是否有时区信息
        assert last_input_time.tzinfo is not None
        # 检查时间不能超过当前时间太多
        now = datetime.now(timezone(timedelta(hours=8)))
        assert last_input_time <= now

    @pytest.mark.skipif(sys.platform != "win32", reason="仅 Windows 平台支持")
    def test_get_idle_info_consistency(self):
        """验证空闲秒数和最后操作时间的一致性"""
        from peekapi.idle import get_idle_info

        idle_seconds, last_input_time = get_idle_info()

        # 计算从最后操作时间到现在的时间差
        now = datetime.now(timezone(timedelta(hours=8)))
        calculated_idle = (now - last_input_time).total_seconds()

        # 允许 1 秒的误差（由于执行时间）
        assert abs(calculated_idle - idle_seconds) < 1.0


class TestIdleInfoMocked:
    """使用 mock 的空闲时间测试（跨平台）"""

    def test_get_idle_info_with_mocked_windows_api(self):
        """测试使用 mock 的 Windows API"""
        mock_windll = MagicMock()

        # 模拟 GetTickCount64 返回 10000ms (10秒)
        mock_get_tick_count_64 = MagicMock(return_value=10000)
        mock_windll.kernel32.GetTickCount64 = mock_get_tick_count_64

        # LASTINPUTINFO.dwTime 模拟返回 5000ms (5秒前的最后输入)
        # 这意味着空闲时间为 10000 - 5000 = 5000ms = 5秒
        def mock_get_last_input_info(lii_ref):
            lii_ref._obj.dwTime = 5000
            return True

        mock_windll.user32.GetLastInputInfo.side_effect = mock_get_last_input_info

        with patch("peekapi.idle.ctypes.windll", mock_windll):
            from peekapi.idle import get_idle_info

            idle_seconds, last_input_time = get_idle_info()

            # 验证空闲时间约为 5 秒
            assert abs(idle_seconds - 5.0) < 0.1

            # 验证最后输入时间
            assert isinstance(last_input_time, datetime)

    def test_get_idle_info_handles_32bit_wraparound(self):
        """测试 32 位回绕情况（dwTime 在回绕前设置，current_tick 在回绕后）"""
        mock_windll = MagicMock()

        # 模拟 GetTickCount64 返回值：假设已超过 49.7 天
        # current_tick 的低 32 位为 1000（刚回绕后）
        # 即 current_tick = 0x100000000 + 1000 = 4294968296
        current_tick_64 = 0x100000000 + 1000  # 回绕后 1 秒
        mock_get_tick_count_64 = MagicMock(return_value=current_tick_64)
        mock_windll.kernel32.GetTickCount64 = mock_get_tick_count_64

        # dwTime 在回绕前设置，假设为 0xFFFFFFFF - 4000 = 4294963295
        # 即在回绕前 4 秒
        dwTime_before_wrap = 0xFFFFFFFF - 4000

        def mock_get_last_input_info(lii_ref):
            lii_ref._obj.dwTime = dwTime_before_wrap
            return True

        mock_windll.user32.GetLastInputInfo.side_effect = mock_get_last_input_info

        with patch("peekapi.idle.ctypes.windll", mock_windll):
            from peekapi.idle import get_idle_info

            idle_seconds, last_input_time = get_idle_info()

            # 预期空闲时间：从 dwTime 到回绕点 (4001ms) + 回绕后到 current_tick (1000ms)
            # = (0xFFFFFFFF - dwTime) + current_tick_32 + 1
            # = 4001 + 1000 = 5001ms = 5.001 秒
            expected_idle_ms = (0xFFFFFFFF - dwTime_before_wrap) + 1000 + 1
            expected_idle_seconds = expected_idle_ms / 1000.0

            assert abs(idle_seconds - expected_idle_seconds) < 0.1
            assert isinstance(last_input_time, datetime)

    def test_get_idle_info_large_tick_count(self):
        """测试大 tick count 值（接近 32 位上限但未回绕）"""
        mock_windll = MagicMock()

        # 模拟系统运行接近 49.7 天，current_tick 接近 32 位上限
        current_tick_64 = 0xFFFFF000  # 接近 32 位最大值
        mock_get_tick_count_64 = MagicMock(return_value=current_tick_64)
        mock_windll.kernel32.GetTickCount64 = mock_get_tick_count_64

        # dwTime 为 current_tick - 3000（3 秒前）
        dwTime = current_tick_64 - 3000

        def mock_get_last_input_info(lii_ref):
            lii_ref._obj.dwTime = dwTime
            return True

        mock_windll.user32.GetLastInputInfo.side_effect = mock_get_last_input_info

        with patch("peekapi.idle.ctypes.windll", mock_windll):
            from peekapi.idle import get_idle_info

            idle_seconds, last_input_time = get_idle_info()

            # 预期空闲时间：3 秒
            assert abs(idle_seconds - 3.0) < 0.1
            assert isinstance(last_input_time, datetime)
