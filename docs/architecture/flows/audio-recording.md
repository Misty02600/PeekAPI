# Flow: 音频采集与 `/record`

## 这条流程保证什么

后台线程持续保存最近一段系统 Loopback 音频；公开模式下，客户端可以取得该缓冲区某一时刻的单声道 PCM_16 WAV 快照。

## 外部参与者和触发条件

- lifespan、托盘或电源处理器请求启动或停止 `AudioRecorder`。
- soundcard 通过 WASAPI 访问默认扬声器的 Loopback 设备。
- 客户端发送 `GET /record`。

## 稳定的状态变化

1. 启动请求在状态锁内建立固定长度缓冲并发布 daemon 采集线程；如果上一代线程仍在退出，则只登记一次
   延迟重启，由上一代线程退出时消费。
2. 线程定位默认扬声器，打开 Loopback recorder；失败时标记不健康并延迟重试。
3. 每个约 100ms 的音频块取第一声道、应用增益、裁剪并转为 `int16`。
4. 样本在锁保护下进入环形缓冲，超过时长的旧样本自动丢弃。
5. `/record` 先检查公开模式，再复制缓冲快照并用 soundfile 编码 WAV。

## 失败时的语义

- 私密模式返回 403。
- WAV 编码失败时 `get_audio()` 返回 `None`，路由返回 500。
- 缓冲为空时仍返回 HTTP 200 和空 WAV，无法区分启动期与设备故障，见 [PLAN-0018](../../plans/todo/0018-report-recorder-health.md)。
- 停止通过每代独立的事件通知采集线程；普通关闭最多等待 3 秒，受时限约束的电源 callback 不等待。
- 如果底层录音调用一直不返回，延迟重启必须继续等待旧线程退出，Modern Standby 下的行为仍在
  [PLAN-0017](../../plans/todo/0017-fix-recorder-lifecycle-races.md) 中验证。

## 相关决定与实现

- [ADR-0004: 使用 soundfile 生成 WAV](../../adr/0004-use-soundfile-for-wav.md)
- [ADR-0005: 使用双重 Windows 电源通知机制](../../adr/0005-handle-suspend-resume-events.md)
- [`record.py`](../../../src/peekapi/record.py)
