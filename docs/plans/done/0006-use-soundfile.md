# PLAN-0006: 使用 soundfile 生成 WAV

## 状态

已完成

## 完成时间

2026-01-26

## 最后结果和当前行为

录音导出使用 soundfile 把 NumPy `int16` 样本写为单声道 PCM_16 WAV，替代标准库 `wave` 的手工文件头与字节写入。

## 怎么验证的

`tests/unit/test_record.py` 和 `tests/integration/test_record_real.py` 验证格式、采样率、声道和样本。

## 审批与提交

- Git 提交：`483c74b`
- 审批记录：历史任务已合入主线；迁移来源未保留独立审批文本。

## 文档同步到哪里

[ADR-0004](../../adr/0004-use-soundfile-for-wav.md) 与 [Audio Recording Flow](../../architecture/flows/audio-recording.md)。

## 已知缺口和后续事项

设备不健康时的 HTTP 语义见 [PLAN-0018](../todo/0018-report-recorder-health.md)。

## 相关文档

- [`record.py`](../../../src/peekapi/record.py)
