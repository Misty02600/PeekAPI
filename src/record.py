import collections
import io
import logging
import threading
import wave

import numpy as np
import soundcard as sc

from .config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioRecorder:
    def __init__(self, rate=44100, channels=1, duration=8, gain=1):
        """
        :param rate: 录音采样率 (Hz)
        :param channels: 声道数
        :param duration: 环形缓冲区存储的录音时长（秒）
        :param gain: 录音增益
        """
        self.rate = rate
        self.channels = channels
        self.duration = duration
        self.gain = gain

        # 计算环形缓冲区大小 (samples)
        self.buffer_size = int(self.rate * self.duration)
        self.buffer = collections.deque(maxlen=self.buffer_size)

        self.is_recording = False
        self.record_thread = None

    def start_recording(self):
        """启动录音线程"""
        if self.is_recording:
            logger.warning("录音已在进行中，忽略本次启动请求。")
            return

        self.is_recording = True

        self.buffer_size = int(self.rate * self.duration)
        self.buffer = collections.deque(maxlen=self.buffer_size)

        self.record_thread = threading.Thread(target=self._record_main_loop, daemon=True)
        self.record_thread.start()
        logger.info(f"录音线程已启动: 环形缓冲 {self.duration}秒, 增益={self.gain}倍")

    def _record_main_loop(self):
        """录音线程的主循环，持续写入最新音频到环形缓冲区"""
        default_speaker = sc.default_speaker()
        logger.info(f"使用默认扬声器: {default_speaker.name}")

        mic = sc.get_microphone(include_loopback=True, id=str(default_speaker.id))

        frames_per_block = self.rate // 10

        with mic.recorder(samplerate=self.rate) as recorder:
            while self.is_recording:
                data = recorder.record(frames_per_block)
                if data.size == 0:
                    continue

                max_volume = np.max(np.abs(data))
                logger.debug(f"当前音频最大音量: {max_volume}")

                amplified = data[:, 0] * self.gain * 32767.0
                amplified = np.clip(amplified, -32768, 32767)
                audio_int16 = amplified.astype(np.int16)

                self.buffer.extend(audio_int16.flatten())

        logger.info("录音线程停止")

    def get_audio(self):
        """获取最近 `duration` 秒的音频数据，返回 BytesIO (WAV)"""
        if not self.buffer:
            logger.warning("缓冲区为空，返回空WAV")
            empty_audio = io.BytesIO()
            with wave.open(empty_audio, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.rate)
                wf.writeframes(b'')
            empty_audio.seek(0)
            return empty_audio

        try:
            current_buffer = list(self.buffer)
            logger.info(f"当前缓冲区大小: {len(current_buffer)} 样本")

            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.rate)
                audio_data = np.array(current_buffer, dtype=np.int16).tobytes()
                wf.writeframes(audio_data)

            wav_io.seek(0)
            size = len(wav_io.getvalue())
            logger.info(f"生成音频文件大小: {size} 字节")
            return wav_io

        except Exception as e:
            logger.error(f"生成音频文件失败: {e}")
            return None

    def stop_recording(self):
        """手动停止录音"""
        if not self.is_recording:
            logger.warning("当前没有在录音，无需停止")
            return

        logger.info("正在停止录音...")
        self.is_recording = False

recorder = AudioRecorder(duration=config.duration, gain=config.gain)
