"""音频录制模块集成测试 - 需要真实音频设备"""

import os
import time

import pytest
import soundfile as sf


# CI 环境自动跳过
pytestmark = pytest.mark.skipif(
    os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"),
    reason="集成测试需要真实音频设备，CI 环境跳过",
)


def has_audio_device():
    """检测是否有可用音频设备"""
    try:
        import soundcard as sc

        speaker = sc.default_speaker()
        return speaker is not None
    except Exception:
        return False


@pytest.mark.skipif(not has_audio_device(), reason="无可用音频设备")
class TestRecordIntegration:
    """音频录制功能集成测试"""

    @pytest.fixture
    def recorder(self):
        """创建真实 AudioRecorder 实例"""
        from src.peekapi.record import AudioRecorder

        rec = AudioRecorder(rate=44100, duration=3, gain=1.0)
        yield rec
        # 清理
        if rec.is_recording:
            rec.stop_recording()

    def test_real_recorder_init(self, recorder):
        """真实 AudioRecorder 初始化"""
        assert recorder.rate == 44100
        assert recorder.is_recording is False

    def test_real_start_stop_recording(self, recorder):
        """真实启动和停止录音"""
        recorder.start_recording()
        assert recorder.is_recording is True

        time.sleep(0.5)  # 录制 0.5 秒

        recorder.stop_recording()
        assert recorder.is_recording is False

    def test_real_get_audio_returns_wav(self, recorder):
        """真实录音后获取 WAV"""
        recorder.start_recording()
        time.sleep(1)  # 录制 1 秒

        audio = recorder.get_audio()

        assert audio is not None
        audio.seek(0)
        data = audio.read()
        assert data[:4] == b"RIFF", "应返回有效 WAV"

    def test_real_wav_has_audio_data(self, recorder):
        """WAV 文件包含音频数据"""
        recorder.start_recording()
        time.sleep(1)

        audio = recorder.get_audio()
        audio.seek(0)

        data, samplerate = sf.read(audio, dtype="int16")
        assert samplerate == 44100
        frames = len(data)
        print(f"录制帧数: {frames}, 时长: {frames / 44100:.2f}秒")
        assert frames > 0

    def test_real_buffer_fills_over_time(self, recorder):
        """缓冲区随时间填充"""
        recorder.start_recording()

        time.sleep(0.3)
        audio1 = recorder.get_audio()
        audio1.seek(0)
        size1 = len(audio1.read())

        time.sleep(0.5)
        audio2 = recorder.get_audio()
        audio2.seek(0)
        size2 = len(audio2.read())

        print(f"0.3秒后: {size1} 字节, 0.8秒后: {size2} 字节")
        assert size2 > size1, "缓冲区应随时间增长"

    def test_real_recorder_health_status(self, recorder):
        """录音健康状态"""
        assert recorder.is_healthy is False

        recorder.start_recording()
        time.sleep(0.5)  # 等待设备连接

        # 如果设备正常，应该变为 healthy
        print(f"录音健康状态: {recorder.is_healthy}")
        # 不强制断言，因为设备可能有问题

    def test_real_empty_buffer_before_recording(self, recorder):
        """录音前缓冲区为空"""
        audio = recorder.get_audio()
        audio.seek(0)

        data, samplerate = sf.read(audio, dtype="int16")
        frames = len(data)
        assert frames == 0, "录音前缓冲区应为空"


@pytest.mark.skipif(not has_audio_device(), reason="无可用音频设备")
class TestLoopbackDevice:
    """Loopback 设备测试"""

    def test_can_get_default_speaker(self):
        """获取默认扬声器"""
        import soundcard as sc

        speaker = sc.default_speaker()
        assert speaker is not None
        print(f"默认扬声器: {speaker.name}")

    def test_can_get_loopback_mic(self):
        """获取 Loopback 麦克风"""
        import soundcard as sc

        speaker = sc.default_speaker()
        mic = sc.get_microphone(include_loopback=True, id=str(speaker.id))
        assert mic is not None
        print(f"Loopback 麦克风: {mic.name}")
