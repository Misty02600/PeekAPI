# [TASK016] - 修复休眠/息屏后应用被终止

**Status:** In Progress
**Added:** 2026-03-03
**Updated:** 2026-03-03

## Original Request

用户报告：电脑休眠息屏后再打开，PeekAPI 应用被自动终止，需要手动重新启动。

## 调查结果

### 日志分析
- 所有日志文件（14 个）只有启动记录，**没有任何关闭/错误/异常记录**
- 说明进程是被**强制终止的**（hard kill），而非 Python 层面的崩溃
- 如果是正常退出，应有 `PeekAPI 已关闭` 日志
- 如果是 Python 异常，loguru 会捕获并记录

### Windows 事件分析
- 系统使用 **S0 Modern Standby（连接待机）**，不支持传统 S3 Sleep
- 系统频繁进入/退出连接待机（原因：Idle Timeout, Power Button, Lid）
- **无 Application Error 事件**（排除程序崩溃）
- **无 Event ID 41（意外关机）**（排除系统层面异常）

### 根因分析

最可能的原因是 **soundcard 库的 WASAPI COM 调用在 Modern Standby 期间失败**：

1. `soundcard` 库使用 Windows WASAPI（COM 接口）进行 Loopback 录音
2. Modern Standby 期间音频设备会被系统挂起/释放
3. WASAPI COM 调用在设备无效状态下可能触发 `AUDCLNT_E_DEVICE_INVALIDATED` 错误
4. 虽然 Python 层面有 try/except，但如果 C 扩展层面发生 Access Violation（如操作已释放的 COM 对象），**Python 的异常处理无法捕获原生层面的崩溃**
5. 这导致整个进程被操作系统直接终止，没有任何日志输出

次要可能原因：
- Modern Standby 深度休眠转换时系统释放资源
- Uvicorn 的网络 socket 在待机期间失效

## Thought Process

### 方案评估

**方案 A: 监听 Windows 电源事件（推荐）**
- 通过 `WM_POWERBROADCAST` 消息监听休眠/唤醒事件
- 在系统休眠前：主动停止录音，释放 WASAPI 设备
- 在系统唤醒后：重新初始化录音设备
- **优势**: pystray 已经创建了一个顶级窗口，且有 `_message_handlers` 机制，可以直接注入 `WM_POWERBROADCAST` 处理器，无需额外依赖
- 只需要 `ctypes`（标准库），不需要 `pywin32`

**方案 B: 使用 watchdog 进程自动重启**
- 外部守护进程监控 PeekAPI，崩溃后自动重启
- 不解决根因，只是治标

**方案 C: 添加全局异常处理和信号处理**
- 使用 `faulthandler` 模块捕获 C 层面崩溃
- 添加 SIGTERM/SIGINT 信号处理
- 可以记录更多信息，但无法阻止崩溃

### 选定方案（V2 — 双重机制）

第一次修复（仅 WM_POWERBROADCAST）无效，因为：
- pystray 运行在 daemon 线程中，Modern Standby → Hibernate 转换时 daemon 线程已被冻结
- WM_POWERBROADCAST 不一定能被 daemon 线程中的窗口接收
- faulthandler 的 crash log 为空，证明不是原生崩溃而是进程被系统终止

V2 采用**双重机制**：

**主要机制: PowerRegisterSuspendResumeNotification (DEVICE_NOTIFY_CALLBACK)**
- 使用 ctypes 调用 `powrprof.PowerRegisterSuspendResumeNotification`
- 注册内核级回调函数，不依赖窗口消息循环
- 能可靠接收 Modern Standby (S0) 和 Hibernate (S4) 的通知
- 回调在 lifespan 中注册（主线程），不在 daemon 线程中

**备用机制: WM_POWERBROADCAST (pystray 消息处理器)**
- 仍然注入 pystray 的 `_message_handlers`
- 作为辅助/备用

### V3 增强：诊断机制（2026-03-09）

对根因分析的进一步推理表明，**最可能的真实原因是系统在夜间重启**（而非 WASAPI 崩溃）：
- faulthandler 空 → 排除 native crash
- 无 Python 异常日志 → 排除 Python 异常
- 无 "PeekAPI 已关闭" 日志 → 排除 lifespan 正常关闭
- 无 "用户退出应用" 日志 → 排除手动退出
- **仅剩两种可能：系统重启 或 OS 直接 TerminateProcess**

为明确区分原因，添加三个诊断机制到 `server.py`：
1. **atexit handler** — 写入 `peekapi_exit_diagnostic.log`，检测 Python 正常退出是否被触发
2. **心跳文件** — 每 30 秒写入 UTC 时间戳到 `peekapi_heartbeat.txt`
3. **启动时 uptime 对比** — 比较系统 uptime 和上次心跳时间距，自动判断：
   - uptime < 心跳间隔 → **系统重启**
   - uptime >= 心跳间隔且进程消失 → **进程被 OS 终止**

## Implementation Plan

- [x] 调查并定位根因
- [x] 创建 `power_events.py` 模块 V1（WM_POWERBROADCAST）
- [x] 修改 `system_tray.py`，注入电源事件处理器到 pystray
- [x] 修改 `server.py`，启用 faulthandler
- [x] V1 测试：一晚息屏后仍被终止，V1 无效
- [x] 重写 `power_events.py` V2（PowerRegisterSuspendResumeNotification + WM_POWERBROADCAST 双重机制）
- [x] 修改 `server.py`，在 lifespan 中注册内核级电源回调
- [x] V3：添加诊断机制（atexit、心跳、uptime 对比）
- [ ] 部署后一晚测试：查看日志判断真实原因

## Progress Tracking

**Overall Status:** In Progress - 90%

### Subtasks
| ID    | Description                   | Status      | Updated    | Notes                                          |
| ----- | ----------------------------- | ----------- | ---------- | ---------------------------------------------- |
| 16.1  | 日志和事件分析                | Complete    | 2026-03-03 | 确认是 hard kill，非 Python 异常               |
| 16.2  | 根因定位                      | Complete    | 2026-03-03 | WASAPI COM 在 Modern Standby 下失效            |
| 16.3  | 创建 power_events.py V1       | Complete    | 2026-03-03 | 仅 WM_POWERBROADCAST — 无效                    |
| 16.4  | 修改 system_tray.py           | Complete    | 2026-03-03 | 注入 WM_POWERBROADCAST + icon.visible 修复     |
| 16.5  | 启用 faulthandler             | Complete    | 2026-03-03 | crash log 为空，确认非原生崩溃                 |
| 16.6  | V1 一晚测试                   | Complete    | 2026-03-04 | **失败** — 程序仍被终止                        |
| 16.7  | power_events.py V2 (双重机制) | Complete    | 2026-03-04 | PowerRegisterSuspendResumeNotification + WM_PB |
| 16.8  | server.py 注册内核级回调      | Complete    | 2026-03-04 | 在 lifespan 中 register_power_notification     |
| 16.9  | V3 诊断机制                   | Complete    | 2026-03-09 | atexit + 心跳 + uptime 对比                    |
| 16.10 | 部署测试                      | Not Started | 2026-03-09 | 等待一晚验证 + 查看诊断日志                    |

## Progress Log

### 2026-03-03
- 分析了 14 个日志文件，确认所有日志只有启动记录无关闭/错误记录
- 通过 Windows 事件查看器确认系统使用 S0 Modern Standby
- 确认无 Application Error 和意外关机事件
- 研究了 pystray _win32.py 源码，发现可直接注入 `_message_handlers`
- 研究了 WASAPI 在 Modern Standby 下的行为，确认 `AUDCLNT_E_DEVICE_INVALIDATED` 是已知问题
- 实现 V1：通过 pystray 的 message handler 监听 WM_POWERBROADCAST
- 修复 icon.visible 问题（pystray 自定义 setup 回调需要手动设置）

### 2026-03-04
- **V1 失败**：一晚息屏后程序仍被终止
- crash log 为空 → 不是原生层崩溃
- 没有电源事件日志 → WM_POWERBROADCAST 根本未被接收
- 分析原因：pystray 在 daemon 线程中运行，Modern Standby → Hibernate 转换时 daemon 线程的窗口消息循环无法接收广播消息
- 确认系统支持 Hibernate (S4)，Modern Standby 长时间后会自动转入 Hibernate
- 重写 power_events.py V2：使用 PowerRegisterSuspendResumeNotification 注册内核级回调
- 主要机制不依赖窗口消息循环，直接由 Windows 内核调用
- 回调函数线程安全（使用 threading.Lock）
- 保留 WM_POWERBROADCAST 作为备用机制
- 所有检查通过：ruff ✅, basedpyright ✅, pytest 113 ✅
- 已打包部署，等待一晚测试验证
