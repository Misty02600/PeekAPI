# Flow: 前台应用查询

## 这条流程保证什么

在公开模式下即时查询 Windows 前台应用的用户可读显示名；查询失败被表达为 JSON 空值，不泄露窗口
标题、完整路径或 PID。

## 外部参与者和触发条件

客户端发送 `GET /foreground`；FastAPI、Windows 前台窗口/进程 API 和可执行文件版本资源参与处理。

## 稳定的状态变化

1. 私密模式在任何前台窗口采样前拒绝请求。
2. 服务取得前台窗口所属 PID，并以有限查询权限打开进程。
3. 服务读取可执行文件路径，仅在进程内用于版本资源查询和文件名回退。
4. 服务按版本资源声明的语言与代码页查询字符串；`Translation` 缺失时从实际 `StringTable` 键恢复查询
   列表，并优先当前用户 UI 语言。
5. 显示名依次选择有效的 `FileDescription`、`ProductName` 和可执行文件 basename。
6. 成功打开的进程句柄始终关闭；请求不写入持久状态，也不缓存查询结果。
7. 有效名称返回为 `{"application": "..."}`；没有有效名称返回为 `{"application": null}`。

## 失败时的语义

- 私密模式返回 403，且不采样前台窗口。
- 无前台窗口、进程访问受限、路径或版本资源查询失败均返回 200 与 `application: null`。
- 非预期的服务错误仍按 FastAPI 服务器错误处理。
- `/screen` 不调用本流程；客户端分别请求截图和应用名时，两次采样不保证原子一致。

## 相关决定与实现

- [ADR-0006](../../adr/0006-expose-foreground-application-endpoint.md)
- [`foreground.py`](../../../src/peekapi/foreground.py)
- [`server.py`](../../../src/peekapi/server.py)
