# ADR-0005: 使用双重 Windows 电源通知机制

## 状态

已采纳

## 日期

2026-03-12

## 当时遇到了什么

Windows Modern Standby/休眠后曾出现应用停止且没有 Python 异常或正常关闭日志。仅依赖 pystray 窗口消息的方案不能可靠收到所有电源事件，WASAPI 设备挂起也需要在恢复后重建。

## 最后决定

以 `PowerRegisterSuspendResumeNotification` 的 callback 作为主要通知来源，保留 pystray `WM_POWERBROADCAST` 处理器作为备用；两个来源共用锁和 suspended 标记，休眠前停止录音，恢复后重新启动。

## 为什么这样选

callback 不依赖窗口消息循环，备用消息处理器又能覆盖不同桌面事件路径；共用状态可以对重复通知去重。

## 没有采用的方案

- 只依赖 pystray `WM_POWERBROADCAST`。
- 使用外部 watchdog 在进程退出后重启。
- 只增加退出诊断而不主动释放音频设备。

## 带来的影响

ctypes callback 与参数必须保持强引用；Windows 可在任意线程调用回调，录音生命周期因此成为跨线程协调问题。电源回调时间有限，不能把耗时收尾无限放在回调内。

## 落实与确认

双重通知在提交 `13ca6c7` 落实。长期 Modern Standby 验证尚未完成，当前录音启停还有竞态，因此“已采纳”不表示风险已经闭环；见 PLAN-0016 与 PLAN-0017。

## 相关文档

- [Application Lifecycle Flow](../architecture/flows/application-lifecycle.md)
- [`power_events.py`](../../src/peekapi/power_events.py)
- [PLAN-0016](../plans/todo/0016-validate-sleep-crash.md)
- [PLAN-0017](../plans/todo/0017-fix-recorder-lifecycle-races.md)
