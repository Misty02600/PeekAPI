# PLAN-0017：修复录音启停与电源恢复竞态

## 状态

进行中

## 最后更新

2026-08-07

## 目标和成功标准

建立调用方可判定结果的录音生命周期，使停止、重复启动、停止中的恢复和电源重复通知具有明确语义。
任意时刻最多一个线程访问 WASAPI；恢复事件结束后录音已经启动，或存在可观察且必然执行的待启动状态；
受时间限制的 Windows 电源 callback 不执行有界时间也无法保证足够短的同步等待。

完成时还必须有自动化状态转换测试、Windows 休眠恢复实机验证、相关 flow 更新、用户确认和成功提交。

## 当前方案

采用最小状态扩展，不引入枚举状态机或专用协调线程：`_state_lock` 串行化缓冲重建、线程创建、引用发布和
`Thread.start()`；每一代 worker 使用独立的 `Event`；旧线程尚未退出时，新的启动请求只设置一次
`_restart_pending`，由旧线程的 `finally` 在确认自身仍是当前代后消费。

停止会同时清除录音意图和待重启标记、设置当前代的停止事件。普通 shutdown 在状态锁外最多等待 3 秒，
Windows 电源 callback 只发送停止信号并立即返回。这样 callback 不受线程退出时长影响，停止后的 resume
仍会在旧线程退出后自动创建且只创建一个新 worker。

## 现在做到哪里

- `record.py` 已实现原子启动发布、每代停止事件、延迟重启和停止取消待重启，尚未提交。
- 确定性 fake worker 测试已覆盖启动事务持锁、停止超时后立即启动、旧线程退出后单次重启，以及再次停止取消重启。
- `power_events.py` 只在启动请求未抛异常后清除 `_suspended`；托盘重启移除了额外 1 秒等待和未经确认的成功日志。
- 电源 callback 使用非等待停止，并增加 suspend/resume 调用语义测试。
- 本机基础 WASAPI 采集与启停集成测试已通过；Modern Standby 尚未验证。

## 涉及文件

- `src/peekapi/record.py`
- `src/peekapi/power_events.py`
- `src/peekapi/system_tray.py`
- `src/peekapi/server.py`
- `tests/unit/test_record.py` 以及待补充的电源状态测试
- `tests/integration/test_record_real.py`
- application lifecycle 与 audio recording flows

## 接下来要做

1. 在 Windows 实机验证重复通知、停止超时后立即恢复和 Modern Standby 后的采集线程数与真实样本。
2. 如调用方确实需要区分“已启动”和“已排队”，再为启停接口增加结果类型，不作为本次竞态修复前置条件。
3. 实机验证后确认 architecture flow 中的平台边界，并按独立文件范围提交。

## 还需要决定什么

- 是否需要公开启停结果类型；当前调用方只需要请求被可靠接受，日志已区分立即启动与延迟重启。
- 恢复窗口内保留旧缓冲是否符合 `/record` 的产品语义；当前仅在新 worker 实际创建时清空。

## 阻碍

- 自动化测试可以覆盖调度与状态转换，但 WASAPI/Modern Standby 的最终行为仍需要 Windows 实机。
- 本工作区还包含独立的版本元数据重构；提交前需要保持两项计划的文件范围可辨认。

## 怎么验证

- 单元测试覆盖重复启动、停止超时、旧线程退出、立即恢复、pending restart、重复 suspend/resume、异常隔离
  和 callback 不同步等待。
- `tests/integration/test_record_real.py` 确认重复启停后只有一个采集线程且 WAV 有实际样本。
- 执行 `just test`、`just lint`、`just check`；随后在 Windows 实机执行休眠恢复验证。

## 审批与提交

- 用户确认：已确认修复 R-001、R-002，并要求避免过度设计（2026-08-06）
- Git 提交：录音生命周期实现随本次提交落地；Modern Standby 实机验证仍待完成

## 进展记录

### 2026-08-07

- 电源 callback 改为只发送停止信号，不再同步等待录音线程退出；普通 shutdown 仍保留最多 3 秒等待。
- 增加非等待停止与 suspend/resume 调用语义测试；130 项单元测试、145 项全量测试、Ruff 与 BasedPyright
  全部通过。SoundCard 0.4.5 仍产生已知的 NumPy `fromstring` 弃用警告，依赖升级不混入本次修复。

### 2026-08-06

- 采用每代 `Event` 加单个 pending restart 的最小方案，闭环停止超时后丢失恢复请求与启动分段发布两个竞态。
- 增加确定性生命周期测试；125 项单元测试、Ruff 与 BasedPyright 全部通过。
- 保留 Windows 实机休眠恢复和 callback 等待边界作为后续验证项。

### 2026-08-02

- 核对工作区中的部分实现，确认状态锁与 join 只能避免一部分双线程问题，调用结果和 callback 调度仍未解决。
- 按新版 repo-docs 模板补齐当前方案、未闭环机制、验证范围与提交边界。

## 相关文档

- [Application Lifecycle Flow](../../architecture/flows/application-lifecycle.md)
- [Audio Recording Flow](../../architecture/flows/audio-recording.md)
- [ADR-0005](../../adr/0005-handle-suspend-resume-events.md)
- [`record.py`](../../../src/peekapi/record.py)
- [`power_events.py`](../../../src/peekapi/power_events.py)
