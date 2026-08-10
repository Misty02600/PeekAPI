# PLAN-0020：新增前台应用查询端点

## 状态

已完成

## 完成时间

2026-08-10

## 最后结果和当前行为

`GET /foreground` 在公开模式下即时返回传统 Windows 桌面程序的用户可读前台应用名；无法识别时返回
`{"application": null}`，私密模式在采样前返回 403。`/screen` 不采样前台应用，也不增加响应头。

查询模块使用有限进程查询权限取得可执行文件路径，依次选择版本资源中的 `FileDescription`、
`ProductName` 和可执行文件 basename。版本资源存在 `Translation` 时按其声明读取；缺失时在节点边界内
枚举实际 `StringTable` 键。当前用户 UI 语言优先，名称会拒绝空白、控制字符、不可打印值和超过 256 字符
的内容，成功打开的进程句柄始终关闭。

响应使用显式 `ForegroundResponse` schema，因此 `application` 字段始终存在，值为字符串或 JSON
`null`。

## 怎么验证的

- `tests/unit/test_foreground.py` 覆盖无窗口、PID/进程访问失败、路径查询失败、句柄释放、版本资源缺失、
  `Translation` 缺失回退、畸形节点、多语言排序、字段优先级、Unicode、名称过滤和 basename 回退。
- `tests/unit/test_server.py` 覆盖字符串与空值响应、私密模式采样短路、OpenAPI 必填字段和 `/screen` 隔离。
- 第二笔提交快照的 `58` 个 foreground/服务器聚焦测试与 `133` 个单元测试通过；Ruff format/check 和
  BasedPyright 通过。
- 隔离的 Python 3.11 环境运行 5 个前台路由与 OpenAPI 测试通过，覆盖 `TypedDict` 的最低版本兼容性。
- Windows 实机读取 `Code.exe` 的版本资源得到 `Visual Studio Code`。

## 审批与提交

- 用户确认：已确认独立 `GET /foreground` 方案，并放行本次实现与本地提交。
- Git 提交：本次功能提交。

## 文档同步到哪里

- [ADR-0006](../../adr/0006-expose-foreground-application-endpoint.md)
- [项目总览](../../architecture/overview.md)
- [前台应用查询 Flow](../../architecture/flows/foreground-application.md)
- [截图请求 Flow](../../architecture/flows/screen-request.md)

## 已知缺口和后续事项

- 首版不承诺 MSIX/UWP 包显示名与任务管理器一致；需要时单独规划 WinRT 包元数据。
- 分别请求截图和应用名只能尽量接近，不能保证两次采样原子一致。
- nonebot-plugin-peek 的消费端适配由其独立计划继续跟踪。

## 相关文档

- [`foreground.py`](../../../src/peekapi/foreground.py)
- [`server.py`](../../../src/peekapi/server.py)
- [nonebot-plugin-peek 配套计划](https://github.com/Misty02600/nonebot-plugin-peek/blob/main/docs/plans/todo/0006-show-foreground-application-in-peek.md)
