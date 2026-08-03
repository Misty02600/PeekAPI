# PLAN-0016：核验休眠后进程终止问题

## 状态

讨论中

## 最后更新

2026-08-02

## 背景与目标

在目标 Windows 机器上使用可追溯的打包产物完成长时间 Modern Standby/休眠恢复验证，确认进程、HTTP API
和实际录音是否恢复。失败时要能区分系统重启、进程退出、服务存活但录音线程未恢复，以及录音设备恢复
但缓冲仍无样本。

提交 `13ca6c7` 已加入双重电源通知，但历史记录没有留下可提交的整夜验证证据，不能仅凭代码已经合入就
宣告问题闭环。

## 已确认的事实和约束

- [ADR-0005](../../adr/0005-handle-suspend-resume-events.md) 已采纳 callback 型
  `PowerRegisterSuspendResumeNotification` 与 pystray `WM_POWERBROADCAST` 备用路径。
- 当前源码没有旧 Memory Bank 曾声称存在的 atexit、心跳文件和 uptime 对比诊断，验证不能依赖这些
  不存在的机制。
- 当前工作区的 `record.py` 会等待旧线程最多 3 秒并拒绝在旧线程仍存活时启动，但电源 callback 仍同步
  调用停止和启动，也无法判断启动是否成功；这些风险由 [PLAN-0017](0017-fix-recorder-lifecycle-races.md)
  继续处理。
- `/check` 只证明 HTTP 服务存活；`/record` 返回 200 和 WAV 也不保证其中已有真实样本。
- 最终证据依赖目标 Windows 机器、实际电源策略和较长等待时间，无法完全由普通单元测试替代。

## 技术路线草案

1. 先完成或明确处置 PLAN-0017，固定待验证的提交、版本、配置、电源模式和 PyInstaller 产物哈希。
2. 在休眠前记录系统时间、系统 uptime、PeekAPI PID、版本、最近日志位置，以及 `/check` 和含真实样本的
   `/record` 基线。
3. 执行约定时长的 Modern Standby/休眠；恢复后立即记录系统事件、PID、HTTP 可用性、录音健康日志和
   WAV 样本数，形成单一时间线。
4. 进程消失时用 Windows 启动时间和事件日志区分系统重启与单进程终止；进程存活但无音频时继续区分
   录音线程、设备重连和空缓冲。
5. 将结论、必要日志摘要和复现条件写回本计划；稳定行为同步 ADR-0005 与 application lifecycle flow。

## 取舍与待决问题

- 最低休眠时长和需要重复的次数；一次整夜通过能否作为闭环证据。
- 是否先增加最小诊断信息（PID、启动时间、录音状态），还是仅依赖现有日志与 Windows 事件。
- 成功标准要求原 PID 保持不变，还是允许系统重启后由外部机制恢复服务；当前项目尚无自动拉起契约。
- PLAN-0017 未完成时是否允许先做探索性验证，还是避免产生无法解释的结果。

## 希望最后是什么样

- 休眠前后有明确时间线、构建身份、日志和 API/音频结果。
- 成功时能证明原服务进程和实际音频采集均恢复，而不只是一项健康检查返回 200。
- 失败时证据足以归类为系统重启、进程终止、线程未恢复或设备/缓冲问题。
- 已确认结论同步回 ADR 与稳定生命周期流程。

## 做到什么算完成

- PLAN-0017 已完成或其残余风险已明确写入本次验证限制。
- 至少一次约定时长的休眠/恢复测试保存构建身份、时间点和必要日志摘要。
- 恢复后 `/check` 成功，`/record` 返回可解析且包含实际样本的 WAV。
- 失败场景能够按上述类别定位，必要诊断另建计划而不是继续猜测。
- 用户确认验证结论并成功提交完成记录后移入 `done/`。

## 涉及范围

- Windows 目标机、PyInstaller 发布产物与系统事件日志。
- `src/peekapi/power_events.py`、`record.py`、`server.py` 的可观察行为。
- `docs/adr/0005-handle-suspend-resume-events.md` 与 application lifecycle flow。

## 怎么验证

按技术路线保存前后两组 PID、uptime、HTTP 响应、WAV 元数据/样本数和日志；使用同一构建至少执行一次
约定时长的 Modern Standby/休眠恢复。若结果不确定，不把计划标记完成，而是补齐缺失诊断后重测。

## 实施确认

- 决定：未确认

## 讨论记录

### 2026-08-02

- 复核当前源码与历史 Memory Bank，确认旧记录提到的诊断机制并不存在。
- 将任务从结果导向的旧 `待办` 升级为带证据协议和失败分类的 `讨论中`验证计划。

## 相关文档

- [ADR-0005](../../adr/0005-handle-suspend-resume-events.md)
- [Application Lifecycle Flow](../../architecture/flows/application-lifecycle.md)
- [PLAN-0017](0017-fix-recorder-lifecycle-races.md)
