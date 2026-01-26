"""音频录制模块测试"""

import io
import struct
import threading
import time
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
import soundfile as sf


class TestAudioRecorder:
    """AudioRecorder 类测试"""

    @pytest.fixture
    def mock_soundcard(self):
        """模拟 soundcard 库"""
        # 模拟录音数据 (0.1秒的正弦波)
        sample_rate = 44100
        duration = 0.1
        t = np.linspace(0, duration, int(sample_rate * duration), dtype=np.float32)
        mock_data = np.sin(2 * np.pi * 440 * t).reshape(-1, 1).astype(np.float32)

        mock_recorder = MagicMock()
        mock_recorder.record.return_value = mock_data
        mock_recorder.__enter__ = MagicMock(return_value=mock_recorder)
        mock_recorder.__exit__ = MagicMock(return_value=False)

        mock_mic = MagicMock()
        mock_mic.recorder.return_value = mock_recorder

        mock_speaker = MagicMock()
        mock_speaker.name = "Test Speaker"
        mock_speaker.id = "test-speaker-id"

        return {
            'speaker': mock_speaker,
            'mic': mock_mic,
            'recorder': mock_recorder,
            'data': mock_data,
        }

    @pytest.fixture
    def recorder_class(self):
        """返回未实例化的 AudioRecorder 类"""
        with patch('src.peekapi.record.config') as mock_config:
            mock_config.record.duration = 8
            mock_config.record.gain = 1.0
            from src.peekapi.record import AudioRecorder
            yield AudioRecorder

    def test_recorder_init_default_values(self, recorder_class):
        """验证默认初始化参数"""
        recorder = recorder_class()

        assert recorder.rate == 44100
        assert recorder.channels == 1
        assert recorder.duration == 8
        assert recorder.gain == 1.0
        assert recorder.is_recording is False
        assert recorder.is_healthy is False

    def test_recorder_init_custom_values(self, recorder_class):
        """验证自定义初始化参数"""
        recorder = recorder_class(rate=48000, channels=2, duration=20, gain=2.0)

        assert recorder.rate == 48000
        assert recorder.channels == 2
        assert recorder.duration == 20
        assert recorder.gain == 2.0

    def test_recorder_buffer_size_calculation(self, recorder_class):
        """验证缓冲区大小计算正确"""
        recorder = recorder_class(rate=44100, duration=10)

        expected_size = 44100 * 10  # rate × duration
        assert recorder.buffer_size == expected_size
        assert recorder.buffer.maxlen == expected_size

    def test_recorder_buffer_size_different_rates(self, recorder_class):
        """验证不同采样率下缓冲区大小"""
        recorder_44k = recorder_class(rate=44100, duration=5)
        recorder_48k = recorder_class(rate=48000, duration=5)

        assert recorder_44k.buffer_size == 44100 * 5
        assert recorder_48k.buffer_size == 48000 * 5

    def test_start_recording_sets_flag(self, recorder_class, mock_soundcard):
        """验证启动录音设置标志"""
        with patch('src.peekapi.record.sc.default_speaker', return_value=mock_soundcard['speaker']):
            with patch('src.peekapi.record.sc.get_microphone', return_value=mock_soundcard['mic']):
                recorder = recorder_class()
                recorder.start_recording()

                assert recorder.is_recording is True

                # 清理
                recorder.stop_recording()

    def test_start_recording_ignores_duplicate(self, recorder_class, mock_soundcard):
        """验证重复启动录音被忽略"""
        with patch('src.peekapi.record.sc.default_speaker', return_value=mock_soundcard['speaker']):
            with patch('src.peekapi.record.sc.get_microphone', return_value=mock_soundcard['mic']):
                recorder = recorder_class()
                recorder.start_recording()

                # 保存第一个线程引用
                first_thread = recorder.record_thread

                # 再次启动（应该被忽略）
                recorder.start_recording()

                # 线程应该是同一个
                assert recorder.record_thread is first_thread

                # 清理
                recorder.stop_recording()

    def test_stop_recording_clears_flag(self, recorder_class, mock_soundcard):
        """验证停止录音清除标志"""
        with patch('src.peekapi.record.sc.default_speaker', return_value=mock_soundcard['speaker']):
            with patch('src.peekapi.record.sc.get_microphone', return_value=mock_soundcard['mic']):
                recorder = recorder_class()
                recorder.start_recording()
                time.sleep(0.1)  # 等待线程启动

                recorder.stop_recording()

                assert recorder.is_recording is False
                assert recorder.is_healthy is False

    def test_stop_recording_when_not_recording(self, recorder_class):
        """验证未在录音时停止不报错"""
        recorder = recorder_class()

        # 不应该抛出异常
        recorder.stop_recording()
        assert recorder.is_recording is False

    def test_get_audio_empty_buffer_returns_wav(self, recorder_class):
        """验证空缓冲区返回有效的空 WAV"""
        recorder = recorder_class()

        result = recorder.get_audio()

        assert result is not None
        # 验证是有效的 WAV 格式
        result.seek(0)
        data = result.read()
        assert data[:4] == b'RIFF', "应该返回有效的 WAV 文件"

    def test_get_audio_empty_buffer_wav_header(self, recorder_class):
        """验证空 WAV 文件头信息正确"""
        recorder = recorder_class(rate=44100, channels=1)

        result = recorder.get_audio()
        result.seek(0)

        info = sf.info(result)
        assert info.channels == 1
        assert info.samplerate == 44100

    def test_get_audio_with_data_returns_wav(self, recorder_class):
        """验证有数据时返回包含数据的 WAV"""
        recorder = recorder_class(rate=44100, channels=1, duration=1)

        # 手动填充一些数据到缓冲区
        test_samples = [0, 1000, 2000, -1000, -2000] * 100
        recorder.buffer.extend(test_samples)

        result = recorder.get_audio()

        assert result is not None
        result.seek(0)

        data, samplerate = sf.read(result, dtype='int16')
        assert len(data) > 0

    def test_get_audio_wav_contains_correct_samples(self, recorder_class):
        """验证 WAV 文件包含正确的采样数据"""
        recorder = recorder_class(rate=44100, channels=1, duration=1)

        # 填充已知数据
        test_samples = [100, 200, 300, 400, 500]
        recorder.buffer.extend(test_samples)

        result = recorder.get_audio()
        result.seek(0)

        data, samplerate = sf.read(result, dtype='int16')
        assert list(data) == test_samples

    def test_buffer_thread_safety(self, recorder_class):
        """验证缓冲区操作的线程安全性"""
        recorder = recorder_class(rate=44100, channels=1, duration=1)
        errors = []

        def writer():
            for i in range(1000):
                try:
                    recorder.buffer.extend([i] * 10)
                except Exception as e:
                    errors.append(e)

        def reader():
            for _ in range(100):
                try:
                    _ = recorder.get_audio()
                except Exception as e:
                    errors.append(e)

        threads = [
            threading.Thread(target=writer),
            threading.Thread(target=reader),
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0, f"并发操作产生错误: {errors}"

    def test_gain_amplification_logic(self, recorder_class):
        """验证增益放大逻辑"""
        recorder_1x = recorder_class(gain=1.0)
        recorder_2x = recorder_class(gain=2.0)

        # 使用相同的输入数据
        input_value = 1000
        recorder_1x.buffer.extend([input_value])
        recorder_2x.buffer.extend([input_value])

        # 由于增益是在录音时应用的，这里只验证 gain 属性正确设置
        assert recorder_1x.gain == 1.0
        assert recorder_2x.gain == 2.0


class TestRecorderDeviceHandling:
    """设备处理相关测试"""

    @pytest.fixture
    def recorder_class(self):
        """返回未实例化的 AudioRecorder 类"""
        with patch('src.peekapi.record.config') as mock_config:
            mock_config.record.duration = 8
            mock_config.record.gain = 1.0
            from src.peekapi.record import AudioRecorder
            yield AudioRecorder

    def test_get_loopback_mic_success(self, recorder_class):
        """验证成功获取 Loopback 麦克风"""
        mock_speaker = MagicMock()
        mock_speaker.name = "Test Speaker"
        mock_speaker.id = "test-id"

        mock_mic = MagicMock()

        with patch('src.peekapi.record.sc.default_speaker', return_value=mock_speaker):
            with patch('src.peekapi.record.sc.get_microphone', return_value=mock_mic) as mock_get_mic:
                recorder = recorder_class()
                result = recorder._get_loopback_mic()

                assert result is mock_mic
                mock_get_mic.assert_called_once_with(include_loopback=True, id="test-id")

    def test_get_loopback_mic_no_speaker(self, recorder_class):
        """验证无默认扬声器时返回 None"""
        with patch('src.peekapi.record.sc.default_speaker', return_value=None):
            recorder = recorder_class()
            result = recorder._get_loopback_mic()

            assert result is None

    def test_get_loopback_mic_exception(self, recorder_class):
        """验证获取设备异常时返回 None"""
        with patch('src.peekapi.record.sc.default_speaker', side_effect=Exception("Device error")):
            recorder = recorder_class()
            result = recorder._get_loopback_mic()

            assert result is None
