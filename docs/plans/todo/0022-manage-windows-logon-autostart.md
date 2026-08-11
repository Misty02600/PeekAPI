# PLAN-0022：由 PeekAPI 管理 Windows 登录自启

| 状态 | 最后更新 |
|---|---|
| 进行中 | 2026-08-11 |

## 背景

PeekAPI 是依赖当前用户桌面、系统托盘和 WASAPI Loopback 的 Windows 桌面应用，应在用户登录后启动，
不适合注册为 Session 0 Windows 服务。当前仓库只负责启动应用本身，登录自启由本机手工创建的计划任务
承担，发布包没有可重复的安装、查询或卸载入口。

2026-08-10 的本机调查确认，现有 `\PeekAPI` 任务设置了 `StopIfGoingOnBatteries=True`。应用在
2026-08-09 09:34 由该任务启动后，系统于 10:49 切换到电池供电，任务结果最终为 `0x8007042B`
（进程被异常终止）；任务没有失败重启，也不会在恢复供电后再次触发。自启定义由部署者手工维护，已经
实际造成运行策略与应用目标不一致。

参考实现为本机 v2rayN 7.16.6（提交 `12abf383e95d285f318976ee655ce70055105e8e`）的
[`AutoStartupHandler`](https://github.com/2dust/v2rayN/blob/12abf383e95d285f318976ee655ce70055105e8e/v2rayN/ServiceLib/Handler/AutoStartupHandler.cs)：
管理员路径通过 `Microsoft.Win32.TaskScheduler.TaskService` 构造任务定义对象并调用
`RegisterTaskDefinition`，即使用 .NET 对 Windows Task Scheduler COM API 的封装，不是手写 XML；
非管理员路径写入当前用户的 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`。Windows 最终可以
把任务定义导出为 XML，但 XML 是任务定义的持久化与交换表示，不代表 v2rayN 以 XML 创建任务。官方同时
支持对象 API [`RegisterTaskDefinition`](https://learn.microsoft.com/en-us/windows/win32/taskschd/taskfolder-registertaskdefinition)、
PowerShell `ScheduledTasks` 对象命令以及
[`Task Scheduler XML schema`](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-schema)。

## 当前设计与缺陷

### 相关实现与当前行为

- `src/peekapi/__main__.py::main` 直接启动 Uvicorn，没有安装或卸载命令。
- `src/peekapi/system_tray.py::start_system_tray` 提供模式、录音、日志和退出菜单，没有自启状态入口。
- `src/peekapi/constants.py::_get_base_dir` 在 PyInstaller 模式下以 `sys.executable` 所在目录作为运行目录，
  可以据此定位待注册的 `peekapi.exe`。
- `peekapi.spec` 生成 onefolder 便携发布，目录可能被用户移动；任何持久自启记录都会保存注册时的绝对路径。
- 项目没有 `pywin32` 或 `comtypes` COM 客户端依赖；现有 `pywin32-ctypes` 是间接依赖，不能提供
  v2rayN 使用的 Task Scheduler 对象模型。`system_info.py` 已有隐藏窗口调用 PowerShell 的项目先例。

### 缺陷机制、证据与影响

- 触发条件：用户希望 PeekAPI 随登录运行，或发布目录、机器、电源策略发生变化。
- 机制：仓库不拥有自启定义 → 用户手工创建外部任务 → 任务默认值、程序路径和恢复策略可能漂移 →
  应用可能不启动、重复启动，或在电源切换时被系统终止。
- 证据：本机日志、Kernel-Power 105 事件、计划任务定义和 `LastTaskResult` 已形成同一时间线；这是实际运行
  证据，不是仅根据源码推断。
- 影响边界：只影响登录启动和外部进程生命周期，不替代现有 suspend/resume 通知、录音设备重建与
  PLAN-0016 的 Modern Standby 验证。应用已经运行时，HTTP、截图和录音路径不应因本计划改变。

## 技术路线

### 目标行为与约束

- 系统托盘提供可查询、可切换的“登录时自动启动”入口；未打包的开发模式不允许把 `.venv` Python
  解释器误注册为长期启动目标。
- 自启状态由新的 `src/peekapi/autostart.py` 独占读写，托盘只调用其查询、启用和禁用接口，不直接拼接
  注册表操作。
- 已确认使用 Python 标准库 `winreg` 管理
  `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 中名为 `PeekAPI` 的 `REG_SZ` 值；值数据是加引号的
  当前打包 exe 绝对路径。稳定运行路径不创建计划任务、不调用 Task Scheduler API，也不生成任务 XML。
- 启用操作幂等：重复启用会把目标更新为当前 `peekapi.exe`，不会创建多个定义；禁用只删除明确属于
  PeekAPI 的注册，不触碰其他应用任务。
- 升级或启动新版不自动修改现有 `\PeekAPI` 计划任务；用户首次在托盘启用登录自启时才读取动作目标。
  目标是当前或可识别的旧 PeekAPI 可执行文件时才迁移；一次性迁移通过
  `schtasks.exe /Query /TN \PeekAPI /XML` 读取定义，用标准库 `xml.etree.ElementTree` 核对 `Exec/Command`。
  确认归属后先写入并回读验证 HKCU Run，再用 `schtasks.exe /Delete /TN \PeekAPI /F` 注销旧任务；注销失败
  且旧任务需要管理员权限时，通过 PowerShell `Start-Process -Verb RunAs` 发起一次 UAC 删除；用户取消或
  注销仍失败时恢复原注册表值并保留旧任务。XML 只用于读取旧任务，不用于创建新任务。目标不匹配或无法
  确认归属时，不修改 HKCU Run，并给出日志，避免重复启动或仅凭同名任务删除外部状态。
- 无论选用哪种注册后端，都必须允许电池供电，并且不得因 AC/DC 切换停止正在运行的 PeekAPI。
- 注册失败只影响自启设置，必须记录可操作的错误并保持当前 HTTP 服务和录音线程存活。
- 本计划只建立登录自启和现有错误任务迁移，不承诺异常退出自动重启，不引入 Windows 服务或外部
  watchdog；这些行为会改变 PLAN-0016 尚未确定的进程恢复契约。

### 实施步骤

| 顺序 | 改动 | 主要实现位置或符号 | 关键约束 | 预期结果 |
|---:|---|---|---|---|
| 1 | 用 `winreg` 实现自启状态查询、启用和禁用，并用 `schtasks.exe` 完成一次性旧任务迁移 | 新增 `src/peekapi/autostart.py` | Windows 专用；使用 HKCU Run；开发模式拒绝注册；先安全注销同源旧任务再写注册表 | 应用拥有单一自启管理边界 |
| 2 | 增加可勾选托盘菜单并刷新状态 | `src/peekapi/system_tray.py::start_system_tray` | 菜单线程中的失败不能终止服务；展示的是系统实际注册状态 | 用户无需手工打开任务计划程序 |
| 3 | 覆盖后端、路径、迁移和失败语义 | 新增 `tests/unit/test_autostart.py`，必要时补充托盘测试 | mock 所有注册表、PowerShell 或进程调用；测试不修改开发机真实自启项 | 自动化证明控制流与安全边界 |
| 4 | 在打包产物上验证真实 Windows 注册 | `peekapi.spec` 产物与 Windows Task Scheduler/注册表 | 使用固定构建身份；验证登录、电池切换、重复启用和禁用 | 发布形态的自启行为可复现 |
| 5 | 同步稳定部署和生命周期说明 | `docs/architecture/overview.md`、`docs/architecture/flows/application-lifecycle.md`，必要时新增 ADR | 只在方案确认和实测后写成稳定事实 | 文档不把计划行为误写成已实现行为 |

## 实施进度

- 当前工作：等待重新登录与 AC/DC 切换实机验收。
- 已确认：迁移只由用户启用操作触发；迁移采用“写入并验证新注册项 → 注销旧任务 → 失败时恢复原值”的
  顺序；旧任务拒绝普通用户删除时才请求一次 UAC，取消授权仍按相同规则回滚。
- 已完成：自启后端、托盘开关与目标测试；全量测试、ruff、格式、basedpyright 和 onefolder
  冒烟通过；正式产物已更新并恢复服务。无提权迁移按预期回滚，UAC 路径随后成功删除旧任务
  并写入 HKCU Run；真实禁用与重新启用期间 `/check` 均返回 200，最终保持启用。
- 下一步：重新登录确认 Windows 从 HKCU Run 启动当前 exe；完成一次 AC→电池切换，确认原 PID 和
  `/check` 持续存活。
- 阻塞：暂无。

## 完成标准与验证

| 验收项 | 覆盖条件或输入 | 预期结果 | 验证方式 |
|---|---|---|---|
| 开发模式保护 | 从源码或 `.venv` 运行并请求启用 | 明确拒绝，不写注册表、不创建任务 | `tests/unit/test_autostart.py` mock 断言 |
| 首次启用 | 从 PyInstaller onefolder 运行，系统没有 PeekAPI 自启项 | 在 HKCU Run 创建一个指向当前 exe 的 `PeekAPI` 值 | Windows 集成检查注册表 |
| 重复启用与目录变化 | 已存在同源定义，再次启用；或把发布目录移动后重新启用 | 不产生重复项，绝对路径更新为当前 exe | 单元测试加打包产物实测 |
| 旧任务迁移安全 | 存在动作指向 PeekAPI 的 `\PeekAPI` 任务；另测同名但目标不匹配的任务 | 前者按确认方案迁移，后者拒绝覆盖并记录原因 | mock 任务定义；本机迁移前后导出对比 |
| 电池切换 | 登录自启后从 AC 切换到电池 | 原 PeekAPI PID 继续存活，`/check` 返回 200 | 目标 Windows 机事件时间线、PID 与 HTTP 检查 |
| 禁用 | 自启已启用后从托盘关闭 | 只删除 PeekAPI 自己的定义，当前进程继续运行 | 单元测试与真实系统检查 |
| 失败隔离 | 注册表访问失败、旧计划任务无法安全迁移或注册值损坏 | 托盘操作给出日志，HTTP 与录音不退出 | mock 异常并执行 `/check` 回归 |
| 全量回归 | 目标单元测试通过 | 现有 API、录音、电源通知和托盘行为不退化 | `just test`、`just lint`、`just check` |

## 已确认事项

- 2026-08-10 · D-001：采用当前用户 HKCU Run 作为唯一稳定自启后端，不新增 COM 依赖、不用 XML 创建
  计划任务；现有 `\PeekAPI` 计划任务只作为一次性迁移来源安全注销。
- 2026-08-11 · D-002：升级或启动不自动迁移；由用户启用操作触发。先写入并验证 HKCU Run，再注销旧
  任务；注销失败时恢复注册表原值，避免迁移失败同时丢失两个自启入口。

## 相关文档

- [PLAN-0016：核验休眠后进程终止问题](0016-validate-sleep-crash.md)
- [PLAN-0017：修复录音启停与电源恢复竞态](0017-fix-recorder-lifecycle-races.md)
- [ADR-0005：使用双重 Windows 电源通知机制](../../adr/0005-handle-suspend-resume-events.md)
- [ADR-0007：使用 HKCU Run 管理 Windows 用户登录自启](../../adr/0007-use-hkcu-run-for-logon-autostart.md)
- [应用启动、关闭与电源事件](../../architecture/flows/application-lifecycle.md)
