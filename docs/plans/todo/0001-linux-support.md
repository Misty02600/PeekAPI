# PLAN-0001：评估并实现 Linux 支持

## 状态

讨论中

## 最后更新

2026-08-02

## 背景与目标

重新评估截图、Loopback 音频、托盘、空闲时间、设备信息和电源事件在 Linux 上的支持范围，先确定可以
长期承诺的功能矩阵，再建立平台适配边界。不可用功能应明确降级，不能因为 Windows 专用模块在导入期
失败而让整个 HTTP 服务无法启动。

跨平台是早期目标，但旧计划把主要障碍归因于已经移除的 winotify，已不能指导当前实现。

## 已确认的事实和约束

- `server.py` 在模块导入时直接加载录音、托盘、电源事件、空闲时间和设备信息模块；其中多个模块使用
  `ctypes.windll`、PowerShell、`subprocess.CREATE_NO_WINDOW` 或 WASAPI 语义。
- 截图组件基于 mss/Pillow，具备跨平台可能性，但显示器枚举、无桌面会话和 CI headless 行为尚未验证。
- soundcard 在 Linux 上依赖 PulseAudio/PipeWire 环境，Loopback 设备发现和 Windows 当前语义并不等价。
- pystray 本身支持多个平台，但 Linux 桌面、系统托盘协议和纯服务器环境不一定可用；电源通知当前完全
  依赖 Windows API。
- CI 只在 Ubuntu 执行静态检查；应用导入、最小启动和 API 测试仍全部在 Windows runner 上完成。
- 当前 README 和架构明确承诺 Windows 专用。Linux 支持不能以破坏 Windows 打包或现有端点语义为代价。

## 技术路线草案

1. 先定义 Windows、Linux 桌面和 Linux headless 三种环境的功能矩阵，逐项决定 `/check`、`/screen`、
   `/record`、`/idle`、`/info`、托盘和电源恢复是完整支持、降级支持还是明确不可用。
2. 把平台检测和 Windows 专用能力隔离到可延迟导入的适配边界；HTTP 入口依赖能力接口或明确的
   unavailable 实现，不直接导入无法在 Linux 初始化的 API。
3. 保持 `/check` 和应用最小启动可用；不支持的敏感端点使用稳定状态码和说明，而不是 ImportError 或
   进程崩溃。具体采用 501、503 还是从路由表禁用，需要先确定兼容策略。
4. 分别验证截图、音频和托盘的 Linux 后端。只有实机或可复现环境确认后才承诺功能，不把第三方库宣称的
   跨平台支持直接写成项目能力。
5. 使用环境标记或可选依赖缩小平台依赖面，并在 Linux CI 增加包导入、应用构造和最小 HTTP 行为测试；
   Windows CI 与发布构建继续作为完整功能门槛。

## 取舍与待决问题

- 第一阶段只保证服务可启动和稳定降级，还是必须同时交付截图或音频等实用能力。
- Linux 音频以 PulseAudio monitor、PipeWire 还是 soundcard 的现有抽象为基线；是否允许平台能力差异。
- Linux 无托盘环境是正常 headless 模式还是配置错误，公开/私密状态由什么入口管理。
- 不支持端点返回 501、503、404，还是通过启动配置完全禁用；这会影响客户端兼容与 OpenAPI 描述。
- 是否提供 Linux 打包产物，以及它是否属于本计划首期范围。

## 希望最后是什么样

- 有一份基于真实验证的功能矩阵，明确各平台支持和降级边界。
- Windows 专用模块不再阻止 Linux 导入和最小启动。
- Linux 至少能够运行健康检查，并对不可用端点给出稳定、可解释的行为。
- Windows 现有截图、录音、托盘、电源恢复和 onefolder 发布没有回归。

## 做到什么算完成

- Linux CI 或真实环境完成包导入、应用启动与最小 API 验证。
- Windows 专用依赖延迟到对应能力内部，不再污染跨平台入口。
- 每个端点和桌面功能都有已验证的支持等级与失败语义。
- Windows 全量测试和打包验证通过。
- README 与 architecture 同步真实平台支持范围，用户确认实施结果并成功提交。

## 涉及范围

- `src/peekapi/server.py` 及新的平台能力边界。
- `src/peekapi/screenshot.py`、`record.py`、`idle.py`、`system_info.py`、`power_events.py`、`system_tray.py`。
- `pyproject.toml`、CI workflow、平台单元/集成测试、README 与 architecture。

## 怎么验证

1. 在 Linux runner 上执行安装、`import peekapi.server`、FastAPI 应用构造和 `/check` 测试。
2. 按功能矩阵分别验证可用端点与不可用端点的状态码、响应说明和日志。
3. 在带桌面与音频服务的 Linux 实机或容器外环境验证计划承诺的截图、音频与托盘能力。
4. 在 Windows 执行 `just test`、`just lint`、`just check` 和 `just build`，并抽查现有端点与托盘行为。

## 实施确认

- 决定：未确认

## 讨论记录

### 2026-08-02

- 按当前源码重新核查平台依赖，移除旧计划中已经不存在的 winotify 前提。
- 将计划从旧 `待办` 升级为 `讨论中`，先确定功能矩阵与降级契约，再决定实现范围。

## 相关文档

- [项目架构](../../architecture/overview.md)
- [`server.py`](../../../src/peekapi/server.py)
- [`power_events.py`](../../../src/peekapi/power_events.py)
