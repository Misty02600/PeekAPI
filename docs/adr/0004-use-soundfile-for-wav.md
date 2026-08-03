# ADR-0004: 使用 soundfile 生成 WAV

## 状态

已采纳

## 日期

2026-01-26

## 当时遇到了什么

环形缓冲中的 NumPy `int16` 样本需要转换为 HTTP 可返回的 WAV；原实现使用标准库 `wave` 手动设置文件头并写入字节。

## 最后决定

使用 soundfile 把 NumPy 数组写入具备 `name = "audio.wav"` 的 `BytesIO`，输出单声道 PCM_16 WAV。

## 为什么这样选

soundfile 直接接受 NumPy 数组，减少手工维护声道、位深、采样率和帧写入代码，并与现有音频处理依赖契合。

## 没有采用的方案

- 继续使用标准库 `wave`。
- 返回原始 PCM 让客户端解释。
- 改用 FLAC/OGG 等压缩格式。

## 带来的影响

soundfile/libsndfile 成为运行和打包依赖；内存对象的格式识别依赖文件名提示或显式格式。HTTP 媒体类型保持 `audio/wav`。

## 落实与确认

已在提交 `483c74b` 落实；单元和真实录音集成测试验证采样率、声道、格式和样本。

## 相关文档

- [Audio Recording Flow](../architecture/flows/audio-recording.md)
- [PLAN-0006](../plans/done/0006-use-soundfile.md)
- [`record.py`](../../src/peekapi/record.py)
