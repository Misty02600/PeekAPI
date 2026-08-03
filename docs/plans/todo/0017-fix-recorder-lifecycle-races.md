# PLAN-0017：修复录音启停与电源恢复竞态

## 状态

进行中

## 最后更新

2026-08-02

## 目标和成功标准

建立调用方可判定结果的录音生命周期，使停止、重复启动、停止中的恢复和电源重复通知具有明确语义。
任意时刻最多一个线程访问 WASAPI；恢复事件结束后录音已经启动，或存在可观察且必然执行的待启动状态；
受时间限制的 Windows 电源 callback 不执行有界时间也无法保证足够短的同步等待。

完成时还必须有自动化状态转换测试、Windows 休眠恢复实机验证、相关 flow 更新、用户确认和成功提交。

## 当前方案

当前工作区已经在 `AudioRecorder` 中加入 `_state_lock`：重复启动会被忽略，旧线程仍存活时拒绝新启动；
停止会清除录音意图并最多等待旧线程 3 秒，线程退出时清理自身引用。这是避免双采集线程的第一步。

后续方案倾向把“期望录音状态”和“当前线程/设备状态”分开建模，让启停方法返回明确结果；电源 callback
只更新期望状态并调度后台协调，不在 Windows 回调线程内 join。旧线程退出后由统一协调逻辑处理待启动
请求，lifespan 与托盘也复用同一套入口。

## 现在做到哪里

- `record.py` 的状态锁、旧线程存活检查、3 秒 join 和线程引用清理已经写入工作区，尚未提交。
- 当前 `start_recording()`、`stop_recording()` 仍返回 `None`，调用方无法区分成功、无操作和被拒绝。
- `power_events.py` 仍在持有模块锁时同步停止/启动，并在确认启动结果前清除 `_suspended`；竞态尚未闭环。
- 现有测试只覆盖基本启停和重复启动，没有覆盖停止超时、立即恢复、电源重复通知和 callback 时间边界。

## 涉及文件

- `src/peekapi/record.py`
- `src/peekapi/power_events.py`
- `src/peekapi/system_tray.py`
- `src/peekapi/server.py`
- `tests/unit/test_record.py` 以及待补充的电源状态测试
- `tests/integration/test_record_real.py`
- application lifecycle 与 audio recording flows

## 接下来要做

1. 明确最小状态集合、状态所有者和启停结果类型，先写能复现当前竞态的状态转换测试。
2. 让启停调用返回成功、无操作、延迟/待处理或失败，并使日志只报告已确认结果。
3. 把停止等待和恢复重启移出 Windows callback；旧线程退出后可靠消费待启动请求。
4. 统一 lifespan、托盘和电源事件调用路径，确认重启录音时是否以及何时清空缓冲。
5. 跑完整质量检查，再在 Windows 实机验证重复通知、立即恢复和 Modern Standby 后的线程数与真实样本。
6. 同步 architecture flow，等待用户确认和提交。

## 还需要决定什么

- 使用显式枚举状态机，还是在现有布尔值上增加 condition/event 与 pending restart；前者语义清楚但改动更大。
- 停止超时后由旧线程退出回调自动重启，还是由专用协调线程/队列重试。
- 正常 shutdown 与 suspend 共用停止接口时，如何保证 shutdown 不会消费待启动请求。
- 重启期间保留旧缓冲还是立即清空；这会影响 `/record` 在恢复窗口内的语义。

## 阻碍

- 自动化测试可以覆盖调度与状态转换，但 WASAPI/Modern Standby 的最终行为仍需要 Windows 实机。
- 本工作区还包含独立的版本元数据重构；提交前需要保持两项计划的文件范围可辨认。

## 怎么验证

- 单元测试覆盖重复启动、停止超时、旧线程退出、立即恢复、pending restart、重复 suspend/resume、异常隔离
  和 callback 不同步等待。
- `tests/integration/test_record_real.py` 确认重复启停后只有一个采集线程且 WAV 有实际样本。
- 执行 `just test`、`just lint`、`just check`；随后在 Windows 实机执行休眠恢复验证。

## 审批与提交

- 用户确认：未确认
- Git 提交：未提交

## 进展记录

### 2026-08-02

- 核对工作区中的部分实现，确认状态锁与 join 只能避免一部分双线程问题，调用结果和 callback 调度仍未解决。
- 按新版 repo-docs 模板补齐当前方案、未闭环机制、验证范围与提交边界。

## 相关文档

- [Application Lifecycle Flow](../../architecture/flows/application-lifecycle.md)
- [Audio Recording Flow](../../architecture/flows/audio-recording.md)
- [ADR-0005](../../adr/0005-handle-suspend-resume-events.md)
- [`record.py`](../../../src/peekapi/record.py)
- [`power_events.py`](../../../src/peekapi/power_events.py)
