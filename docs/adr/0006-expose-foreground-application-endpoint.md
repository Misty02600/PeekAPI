# ADR-0006：用独立端点查询前台应用显示名

## 状态

已采纳

## 日期

2026-08-02

## 当时遇到了什么

截图经过高斯模糊后，客户端不一定能快速判断用户正在使用哪个应用。可执行文件 basename 也不是合适的
最终展示值：Visual Studio Code 的进程镜像是 `Code.exe`，但面向用户的应用名是
`Visual Studio Code`。

最初提案准备把应用名附加到 `/screen` 响应头，以便在同一次请求中采样截图和前台状态。用户随后明确
希望把前台应用查询作为 PeekAPI 的独立端点。这个选择使状态查询不再依附于图片传输，但也会引入两次
请求之间的时间差，并把应用信息变成可以单独访问的资源。

窗口标题、完整路径和 PID 会暴露不必要的文档名、网页标题或本机结构。新端点还必须继承 PeekAPI 的
私密模式边界，不能成为绕过现有隐私控制的旁路。

## 最后决定

新增 `GET /foreground`，以 JSON 返回请求处理瞬间的前台应用显示名：

```json
{"application": "Visual Studio Code"}
```

服务端先取得前台进程的可执行文件路径，再从该文件的版本资源中按以下顺序选择首个有效显示值：

1. `FileDescription`；
2. `ProductName`；
3. 可执行文件 basename。

无法取得有效值时返回 `200 OK` 与 `{"application": null}`，表示端点可用但当前状态不可识别；私密模式
在采样前返回 `403 Forbidden`。首版与 `/idle`、`/info` 一样只复用公开/私密模式，不新增 API key 参数。

`/screen` 保持原有纯 `image/jpeg` 契约，不附加前台应用响应头。实现不读取或返回窗口标题，也不返回
完整路径或 PID。

## 为什么这样选

- 独立端点让前台应用成为明确的状态资源，可由截图以外的调用方复用。
- JSON 原生承载 Unicode 与 `null`，不需要为响应头设计百分号编码和非法转义规则。
- `FileDescription` 是版本资源中面向用户描述文件的字段，能让 `Code.exe` 显示为
  `Visual Studio Code`。
- `ProductName` 和 basename 形成逐级回退，使缺少完整版本资源的传统桌面程序仍有可辨识结果。
- 不读取窗口标题，避免暴露网页标题、文档名和聊天内容。
- 状态查询失败返回 `application: null`，不把辅助信息误报为服务故障。

## 没有采用的方案

- 在 `/screen` 响应头附加应用名：采样更接近截图时刻且只增加一次请求，但会把独立状态耦合到图片响应，
  与用户要求的新端点不符。
- 直接返回 `Code.exe` 一类 basename：实现简单，但不能满足面向用户显示应用产品名的目标。
- 返回窗口标题：辨识度更高，但会额外泄露网页标题、文档名和聊天内容。
- 返回完整进程路径或 PID：客户端不需要，且扩大本机信息暴露。
- 由插件维护 `Code.exe` 到产品名的映射：映射不完整、会过期，而且插件不一定运行在被截图主机上。
- 把图片和状态改成统一 JSON、multipart 或 base64：仍然耦合两类资源，并破坏现有图片响应。

## 带来的影响

- 有利：PeekAPI 获得可独立调用、可直接描述缺失值的前台应用状态接口，`/screen` 契约不变。
- 代价：`/peek` 需要向同一主机发起截图和前台应用两个请求；即使并发执行也只保证尽量接近，不能保证
  两次采样原子一致。
- 兼容：旧 PeekAPI 会对 `/foreground` 返回 404；新插件必须把该结果视为无应用信息并继续显示图片。
- 风险：公开模式下任何能访问 PeekAPI 的客户端都能单独查询应用显示名；该端点与 `/idle`、`/info`
  一样以公开/私密模式作为访问边界，不额外要求密钥。
- 边界：首版只承诺传统 Windows 桌面可执行文件的版本资源与 basename 回退，不承诺与任务管理器对
  MSIX/UWP 应用的分组和命名完全一致。

## 落实与确认

- 实施情况：已落实，等待改动验收与 Git 提交
- 代码或测试：[`foreground.py`](../../src/peekapi/foreground.py)、
  [`test_foreground.py`](../../tests/unit/test_foreground.py)、
  [PLAN-0020](../plans/todo/0020-add-foreground-application-endpoint.md)

## 相关文档

- [截图请求 Flow](../architecture/flows/screen-request.md)
- [前台应用查询 Flow](../architecture/flows/foreground-application.md)
- [nonebot-plugin-peek 仓库](https://github.com/Misty02600/nonebot-plugin-peek)
