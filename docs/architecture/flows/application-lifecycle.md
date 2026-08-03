# Flow: 应用启动、关闭与电源事件

## 这条流程保证什么

服务启动时建立录音、电源通知和托盘运行环境；正常关闭时请求停止录音；Windows 休眠/恢复时尽量释放并重新建立 Loopback 设备。

## 外部参与者和触发条件

- 命令行 `peekapi` 或打包后的 `peekapi.exe` 启动 Uvicorn。
- FastAPI lifespan 驱动后台资源的启动和清理。
- Windows 发送 suspend/resume 通知。
- 托盘菜单可重启录音或直接退出进程。

## 稳定的状态变化

1. lifespan 配置日志并请求启动全局录音器。
2. 应用注册 callback 型电源通知，并在托盘窗口中安装备用消息处理器。
3. 托盘在 daemon 线程运行；HTTP 服务开始接收请求。
4. 首个 suspend 通知将状态标为 suspended 并请求停止录音；重复通知被忽略。
5. 首个 resume 通知清除 suspended 并请求启动录音；重复通知被忽略。
6. 正常 lifespan 退出再次请求停止录音。

## 失败时的语义

- 电源通知注册失败只记录 warning，服务仍能运行，但休眠恢复能力下降。
- 音频设备失败由录音线程进入延迟重连，不应直接终止 HTTP 服务。
- 当前停止等待与恢复启动的成功判定不完整，可能阻塞 callback 或恢复后无录音，见 [PLAN-0017](../../plans/todo/0017-fix-recorder-lifecycle-races.md)。
- 托盘退出使用 `os._exit(0)`，不会执行 lifespan 清理。

## 相关决定与实现

- [ADR-0002: 使用 FastAPI 与 Uvicorn](../../adr/0002-use-fastapi-and-uvicorn.md)
- [ADR-0005: 使用双重 Windows 电源通知机制](../../adr/0005-handle-suspend-resume-events.md)
- [`server.py`](../../../src/peekapi/server.py)、[`record.py`](../../../src/peekapi/record.py)、[`power_events.py`](../../../src/peekapi/power_events.py)
