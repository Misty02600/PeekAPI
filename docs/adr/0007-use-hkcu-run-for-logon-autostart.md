# ADR-0007：使用 HKCU Run 管理 Windows 用户登录自启

## 状态

已采纳

## 日期

2026-08-11

## 当时遇到了什么

PeekAPI 依赖当前用户桌面、系统托盘和 WASAPI Loopback，应在用户登录后运行，不适合作为 Session 0
Windows 服务。此前由部署者手工创建的 `\PeekAPI` 计划任务承担自启，任务中的电池策略曾在 AC 切换到
电池时终止正在运行的进程，发布包又没有统一的查询、启用和禁用入口。

PyInstaller onefolder 发布目录可以移动，自启记录只能保存注册时的绝对 exe 路径；旧计划任务还可能由
管理员创建，因此迁移既要确认外部状态归属，也要处理一次性提权和失败回滚。

## 最后决定

- 只允许打包后的 `peekapi.exe` 启用自启；开发模式不登记 Python 解释器或 `.venv` 路径。
- 以当前用户 `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` 中名为 `PeekAPI` 的 `REG_SZ`
  作为唯一稳定自启后端，值为加引号的当前 exe 绝对路径。
- `autostart.py` 独占注册表与旧任务迁移，托盘只查询和切换状态；重复启用更新当前路径，禁用不退出进程。
- 升级或启动不自动迁移。用户启用时通过 `schtasks.exe /Query /TN \PeekAPI /XML` 读取旧任务，只在唯一
  `Exec/Command` 明确指向 `peekapi.exe` 时迁移。
- 迁移先写入并回读验证 HKCU Run，再删除旧任务。普通用户删除被拒绝时，通过 PowerShell
  `Start-Process -Verb RunAs` 请求一次 UAC；删除或验证失败时恢复原注册表值并保留旧任务。

## 为什么这样选

HKCU Run 与目标生命周期一致：由当前用户登录触发，不需要长期管理员权限，也没有计划任务在电源变化时
终止进程的策略。标准库 `winreg` 足以维护稳定状态，不需要为单一功能增加 Task Scheduler COM 客户端
依赖。保留显式、可回滚的旧任务迁移，可以在不自动改写部署者外部状态的前提下消除重复启动。

## 没有采用的方案

- Windows 服务：无法直接使用目标用户桌面、托盘和 WASAPI Loopback 会话。
- 继续使用计划任务作为稳定后端：需要额外管理电池、权限和任务策略，仍可能意外终止进程。
- 引入 `pywin32`、`comtypes` 或第三方 Task Scheduler 封装：只为一次性迁移增加长期依赖。
- 写入 Startup 文件夹：难以像命名注册表值一样安全地查询、更新和校验单一所有权。

## 带来的影响

- 登录自启仅对当前用户生效；切换 AC/DC 不再由自启后端停止已经运行的 PeekAPI。
- onefolder 目录移动后，用户需要从新位置再次启用，才能更新注册表中的绝对路径。
- 首次迁移管理员创建的旧任务时会出现 UAC；取消后旧任务继续有效，新注册项被回滚。
- 本决定不提供异常退出重启、睡眠恢复拉起、watchdog 或 Windows 服务能力。

## 落实与确认

- 实施：`src/peekapi/autostart.py`、`src/peekapi/system_tray.py`。
- 自动化：`tests/unit/test_autostart.py`、`tests/unit/test_system_tray.py` 覆盖开发模式保护、路径更新、归属
  冲突、迁移顺序、UAC 取消与失败回滚。
- 实机：2026-08-11 将管理员创建的 `\PeekAPI` 任务迁移为 HKCU Run；旧任务消失，禁用与重新启用均不
  中断当前 `/check` 服务。

## 相关文档

- [应用启动、关闭与电源事件](../architecture/flows/application-lifecycle.md)
- [PLAN-0022](../plans/todo/0022-manage-windows-logon-autostart.md)
- [ADR-0003：使用 PyInstaller onefolder 发布 Windows 应用](0003-use-pyinstaller-onefolder.md)
