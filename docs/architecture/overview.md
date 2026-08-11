# 项目架构

## 先建立一个印象

PeekAPI 是部署在 Windows 桌面上的本地 HTTP 服务，为受信调用方提供当前屏幕、前台应用显示名、最近
一段 Loopback 系统音频、用户空闲时间和硬件信息。它管理本机采集、隐私模式和桌面生命周期，不负责
公网穿透、用户账户、远程控制或业务数据持久化。

## 逻辑组件与实现映射

| 逻辑组件 | 职责与边界 | 依赖方向或主要协作 | 拥有的数据或状态 | 主要实现位置 |
|---|---|---|---|---|
| HTTP 与权限入口 | 暴露 `/screen`、`/record`、`/idle`、`/foreground`、`/info`、`/check`，决定参数校验、隐私与密钥边界及 HTTP 响应；不直接实现硬件采集 | 读取运行配置并调用截图、录音和 Windows 状态查询组件；lifespan 调用桌面生命周期组件 | FastAPI 应用与 lifespan 编排，不拥有采集数据 | [`server.py`](../../src/peekapi/server.py) |
| 屏幕采集 | 选择主显示器或虚拟桌面，按请求应用高斯模糊并编码 JPEG；不保存截图 | 由 HTTP 入口调用，依赖 mss 与 Pillow | 无跨请求状态 | [`screenshot.py`](../../src/peekapi/screenshot.py) |
| 音频采集与快照 | 持续读取默认扬声器的 WASAPI Loopback，维护最近一段样本并编码 WAV | 由 lifespan、托盘和电源协调组件请求启停，由 HTTP 入口读取快照；依赖 soundcard、NumPy、soundfile | 录音意图、健康标记、采集线程、设备会话和环形缓冲 | [`record.py`](../../src/peekapi/record.py) |
| 桌面生命周期与控制 | 启动托盘、切换公开/私密模式、处理退出与录音重启，并把 Windows 休眠/恢复事件转换为录音启停请求 | 与 HTTP lifespan 和音频组件双向协作；依赖 pystray 与 Win32 电源通知 | 进程内公开状态、suspended 去重状态、回调与注册句柄引用 | [`server.py`](../../src/peekapi/server.py)、[`system_tray.py`](../../src/peekapi/system_tray.py)、[`power_events.py`](../../src/peekapi/power_events.py) |
| 登录自启管理 | 查询和切换当前用户登录自启，并安全迁移同源旧计划任务；不负责异常退出重启或服务化 | 由托盘调用；依赖 `winreg`、`schtasks.exe`，仅在旧管理员任务删除被拒绝时请求一次 UAC | HKCU Run 的 `PeekAPI` 值；迁移期间临时协调旧任务与注册表状态 | [`autostart.py`](../../src/peekapi/autostart.py)、[`system_tray.py`](../../src/peekapi/system_tray.py) |
| Windows 状态查询 | 查询最后输入时间、前台应用显示名和设备硬件信息；不缓存结果，不读取前台窗口标题 | 由 HTTP 入口调用；依赖 Win32 API、可执行文件版本资源与 PowerShell CIM/WMI | 无跨请求业务状态 | [`idle.py`](../../src/peekapi/idle.py)、[`foreground.py`](../../src/peekapi/foreground.py)、[`system_info.py`](../../src/peekapi/system_info.py) |
| 运行基础 | 解码 TOML 配置，确定开发/打包路径并配置日志 | 被所有运行组件读取；配置在导入时加载 | `config` 可变对象、运行路径、日志文件 | [`config.py`](../../src/peekapi/config.py)、[`constants.py`](../../src/peekapi/constants.py)、[`logging.py`](../../src/peekapi/logging.py) |
| 构建与发布 | 管理版本、PyInstaller onefolder、Windows ZIP 和 GitHub Release | 读取项目元数据并打包运行组件；标签触发 Release workflow | Git 历史、标签、构建产物与 Release 附件 | [`pyproject.toml`](../../pyproject.toml)、[`peekapi.spec`](../../peekapi.spec)、[Release workflow](../../.github/workflows/release.yml) |

依赖方向以 HTTP 和桌面生命周期为编排层，采集与 Windows 查询组件不反向构造 HTTP 响应。音频组件是
主要的跨线程状态所有者；公开模式保存在可变运行配置中，电源事件模块只拥有休眠去重与系统回调状态。

## 最重要的质量目标和约束

- 隐私边界明确：私密模式拒绝敏感端点，低模糊截图按配置校验 API key；新增元数据也必须复用同一边界。
- 桌面设备短暂失效后服务进程仍可存活并尝试恢复采集，且任意时刻最多一个线程访问 WASAPI。
- 发布 ZIP 解压即可运行，配置文件保持在 exe 同级并可直接编辑。
- 登录自启只登记打包后的当前用户 exe；迁移失败或取消 UAC 时保留旧任务，不影响当前服务进程。
- 硬件相关逻辑通过 mock 做单元测试，真实截图、录音、打包和休眠恢复留给 Windows 环境验证。
- 当前运行实现是 Windows 专用的 Python 3.11+ 应用；Linux/macOS 导入和运行都不受保证。

## 平时怎么运行和部署

开发时使用 `uv run peekapi`。发布时推送与项目版本一致的 `v*` 标签，由 Windows GitHub Actions runner
构建 PyInstaller onefolder 目录并发布 `PeekAPI-v<version>-windows.zip`；用户解压、编辑
`config.toml` 后运行 `peekapi.exe`。需要登录自启时从托盘启用；移动发布目录后再次启用以更新绝对路径。

## 数据和状态放在哪里

| 数据或状态 | 位置与生命周期 |
|---|---|
| 配置 | exe 同级或开发工作目录的 `config.toml`；启动导入时解码，运行中切换的公开状态不会写回文件 |
| 最近音频 | `AudioRecorder` 的固定长度内存缓冲；重启录音时清空，进程退出后消失 |
| 截图 | 仅存在于单次 `/screen` 请求的内存中，不落盘 |
| 电源与线程状态 | 进程内锁、线程引用、健康标记和 suspended 标记；不跨进程恢复 |
| 登录自启 | 当前用户 HKCU Run 的 `PeekAPI` 字符串值；保存打包 exe 的绝对路径，禁用时删除 |
| 设备信息、空闲时间与前台应用 | 每次请求即时查询，不缓存；前台应用只保留在单次 `/foreground` 响应中 |
| 日志 | exe 同级或开发工作目录的 `logs/`，按日轮转并默认保留 7 天 |
| 构建与发布 | `build/`、`dist/` 和 GitHub Release；本地生成目录不属于运行时数据 |

## 关键流程和决定

- [应用启动、关闭与电源事件](flows/application-lifecycle.md)
- [音频采集与 `/record`](flows/audio-recording.md)
- [截图请求](flows/screen-request.md)
- [前台应用查询](flows/foreground-application.md)
- [版本发布](flows/release.md)
- [ADR 索引](../adr/README.md)
- [ADR-0007：使用 HKCU Run 管理 Windows 用户登录自启](../adr/0007-use-hkcu-run-for-logon-autostart.md)

## 已知风险或还不确定的地方

- 录音停止与恢复仍有回调阻塞和旧线程竞态，见 [PLAN-0017](../plans/todo/0017-fix-recorder-lifecycle-races.md)。
- `/record` 无法区分尚无样本与录音设备长期故障，见 [PLAN-0018](../plans/todo/0018-report-recorder-health.md)。
- Modern Standby 的长时间实机验证尚未闭环，见 [PLAN-0016](../plans/todo/0016-validate-sleep-crash.md)。
- 跨平台支持需要先确定可承诺的功能矩阵并隔离 Windows 适配，见 [PLAN-0001](../plans/todo/0001-linux-support.md)。
- `/foreground` 首版只从传统桌面可执行文件的版本资源和 basename 推导显示名，不保证 MSIX/UWP 名称与
  任务管理器完全一致，见 [ADR-0006](../adr/0006-expose-foreground-application-endpoint.md)。
- 当前工作区正在统一项目、HTTP 与 Windows 产物的版本来源，见 [PLAN-0021](../plans/todo/0021-unify-version-metadata.md)。
