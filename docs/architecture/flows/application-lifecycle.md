# Flow: 应用启动、关闭与电源事件

## 这条流程保证什么

服务启动时建立录音、电源通知和托盘运行环境；正常关闭时请求停止录音；Windows 休眠/恢复时尽量释放并
重新建立 Loopback 设备。用户可以从托盘管理当前用户登录自启，自启后端不接管已经启动的进程。

## 外部参与者和触发条件

- 命令行 `peekapi` 或打包后的 `peekapi.exe` 启动 Uvicorn。
- FastAPI lifespan 驱动后台资源的启动和清理。
- Windows 发送 suspend/resume 通知。
- 托盘菜单可重启录音或直接退出进程。
- 用户从托盘启用或禁用“登录时自动启动”；Windows 在下一次用户登录时读取 HKCU Run。

## 稳定的状态变化

1. lifespan 配置日志并请求启动全局录音器。
2. 应用注册 callback 型电源通知，并在托盘窗口中安装备用消息处理器。
3. 托盘在 daemon 线程运行；HTTP 服务开始接收请求。
4. 首个 suspend 通知将状态标为 suspended，只发送停止信号而不等待录音线程退出；重复通知被忽略。
5. 首个 resume 通知请求启动录音；旧线程仍在退出时登记一次延迟重启。请求未抛异常后才清除 suspended，
   重复通知被忽略。
6. 正常 lifespan 退出再次请求停止录音。

## 登录自启与旧任务迁移

1. 开发模式中的托盘自启项不可用；打包程序按 HKCU Run 是否精确指向当前 exe 展示勾选状态。
2. 首次启用先核对同名注册表值与 `\PeekAPI` 旧任务归属；同名但目标不属于 PeekAPI 时拒绝修改。
3. 没有旧任务时写入并回读验证 HKCU Run；重复启用会把同源旧路径更新为当前 exe。
4. 存在同源旧任务时先写入并验证 HKCU Run，再删除任务。普通删除被拒绝时只为这次迁移请求 UAC；删除
   失败或用户取消时恢复启用前的注册表值，避免两个启动入口同时丢失。
5. 禁用只删除明确属于 PeekAPI 的 HKCU Run 值，当前进程继续运行；之后登录不再自动启动。

## 失败时的语义

- 电源通知注册失败只记录 warning，服务仍能运行，但休眠恢复能力下降。
- 音频设备失败由录音线程进入延迟重连，不应直接终止 HTTP 服务。
- 恢复启动抛出异常时保留 suspended，使后续 resume 通知仍可重试。
- 底层录音调用在 Modern Standby 下能否及时响应停止事件仍需实机验证，见
  [PLAN-0017](../../plans/todo/0017-fix-recorder-lifecycle-races.md)。
- 托盘退出使用 `os._exit(0)`，不会执行 lifespan 清理。
- 自启查询或修改失败只记录 warning 并刷新托盘菜单，不终止 HTTP 服务或录音线程。
- HKCU Run 只负责用户登录时启动，不提供崩溃重启、恢复供电后拉起或 watchdog。

## 相关决定与实现

- [ADR-0002: 使用 FastAPI 与 Uvicorn](../../adr/0002-use-fastapi-and-uvicorn.md)
- [ADR-0005: 使用双重 Windows 电源通知机制](../../adr/0005-handle-suspend-resume-events.md)
- [ADR-0007：使用 HKCU Run 管理 Windows 用户登录自启](../../adr/0007-use-hkcu-run-for-logon-autostart.md)
- [`server.py`](../../../src/peekapi/server.py)、[`record.py`](../../../src/peekapi/record.py)、[`power_events.py`](../../../src/peekapi/power_events.py)、[`autostart.py`](../../../src/peekapi/autostart.py)
