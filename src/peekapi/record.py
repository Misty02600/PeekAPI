import collections
import io
import threading
import time

import numpy as np
import soundcard as sc
import soundfile as sf

from .config import config
from .constants import MAX_CONSECUTIVE_ERRORS, RECONNECT_DELAY_SECONDS
from .logging import logger


class AudioRecorder:
    """
    音频录制器，使用环形缓冲区持续录制系统音频（Loopback）。

    Attributes:
        rate: 录音采样率 (Hz)
        duration: 环形缓冲区存储的录音时长（秒）
        gain: 录音增益
        is_healthy: 录音线程是否健康运行，用于外部监控
    """

    def __init__(self, rate: int = 44100, duration: int = 8, gain: float = 1.0) -> None:
        self.rate = rate
        self.duration = duration
        self.gain = gain

        self.buffer_size = int(self.rate * self.duration)
        self.buffer: collections.deque[np.int16] = collections.deque(
            maxlen=self.buffer_size
        )

        self.is_recording = False
        self.is_healthy = False  # 标记录音线程是否正常工作
        self.record_thread: threading.Thread | None = None
        self._lock = threading.Lock()

    def start_recording(self) -> None:
        """启动录音线程。如果已在录音则忽略。"""
        if self.is_recording:
            logger.warning("录音已在进行中，忽略本次启动请求。")
            return

        self.is_recording = True
        self.is_healthy = False

        with self._lock:
            self.buffer_size = int(self.rate * self.duration)
            self.buffer = collections.deque(maxlen=self.buffer_size)

        self.record_thread = threading.Thread(
            target=self._record_main_loop, daemon=True
        )
        self.record_thread.start()
        logger.info(f"录音线程已启动: 环形缓冲 {self.duration}秒, 增益={self.gain}倍")

    def _get_loopback_mic(self):
        """
        获取系统默认扬声器的 Loopback 麦克风设备。

        Returns:
            soundcard 麦克风对象，失败返回 None
        """
        try:
            default_speaker = sc.default_speaker()
            if default_speaker is None:
                logger.error("未找到默认扬声器")
                return None
            logger.debug(f"使用默认扬声器: {default_speaker.name}")
            mic = sc.get_microphone(include_loopback=True, id=str(default_speaker.id))
            return mic
        except Exception as e:
            logger.error(f"获取 Loopback 设备失败: {e}")
            return None

    def _record_main_loop(self):
        """
        录音线程的主循环。

        持续写入最新音频到环形缓冲区，支持设备断开后自动重连。
        """
        consecutive_errors = 0
        frames_per_block = self.rate // 10

        while self.is_recording:
            mic = self._get_loopback_mic()
            if mic is None:
                consecutive_errors += 1
                if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                    logger.error(
                        f"连续 {consecutive_errors} 次获取设备失败，等待 {RECONNECT_DELAY_SECONDS} 秒后重试"
                    )
                self.is_healthy = False
                time.sleep(RECONNECT_DELAY_SECONDS)
                continue

            try:
                with mic.recorder(samplerate=self.rate) as recorder:
                    logger.info("录音设备已连接，开始采集音频")
                    consecutive_errors = 0
                    self.is_healthy = True

                    while self.is_recording:
                        try:
                            data = recorder.record(frames_per_block)
                            if data.size == 0:
                                continue

                            max_volume = np.max(np.abs(data))
                            logger.debug(f"当前音频最大音量: {max_volume}")

                            amplified = data[:, 0] * self.gain * 32767.0
                            amplified = np.clip(amplified, -32768, 32767)
                            audio_int16 = amplified.astype(np.int16)

                            with self._lock:
                                self.buffer.extend(audio_int16.flatten())

                        except Exception as e:
                            # 录音过程中出错（如设备断开），跳出内层循环重新获取设备
                            logger.warning(f"录音采集异常，尝试重新连接设备: {e}")
                            self.is_healthy = False
                            break

            except Exception as e:
                # 设备打开失败（如睡眠唤醒后设备失效）
                logger.warning(
                    f"打开录音设备失败，{RECONNECT_DELAY_SECONDS} 秒后重试: {e}"
                )
                self.is_healthy = False
                consecutive_errors += 1
                time.sleep(RECONNECT_DELAY_SECONDS)

        self.is_healthy = False
        logger.info("录音线程停止")

    def get_audio(self) -> io.BytesIO | None:
        """
        获取最近 `duration` 秒的音频数据。

        Returns:
            BytesIO: WAV 格式的音频数据，失败返回 None
        """
        with self._lock:
            if not self.buffer:
                logger.debug("缓冲区为空，返回空WAV")
                empty_audio = io.BytesIO()
                empty_audio.name = "audio.wav"  # soundfile 需要通过 name 属性推断格式
                sf.write(
                    empty_audio,
                    np.array([], dtype=np.int16),
                    self.rate,
                    subtype="PCM_16",
                )
                empty_audio.seek(0)
                return empty_audio

            current_buffer = list(self.buffer)

        logger.debug(f"当前缓冲区大小: {len(current_buffer)} 样本")

        try:
            audio_data = np.array(current_buffer, dtype=np.int16)

            wav_io = io.BytesIO()
            wav_io.name = "audio.wav"  # soundfile 需要通过 name 属性推断格式
            sf.write(wav_io, audio_data, self.rate, subtype="PCM_16")

            wav_io.seek(0)
            size = len(wav_io.getvalue())
            logger.debug(f"生成音频文件大小: {size} 字节")
            return wav_io

        except Exception as e:
            logger.error(f"生成音频文件失败: {e}")
            return None

    def stop_recording(self) -> None:
        """手动停止录音。"""
        if not self.is_recording:
            logger.debug("当前没有在录音，无需停止")
            return

        logger.info("正在停止录音...")
        self.is_recording = False
        self.is_healthy = False


recorder = AudioRecorder(duration=config.record.duration, gain=config.record.gain)
