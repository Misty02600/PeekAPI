# PLAN-0020：新增前台应用查询端点

## 状态

进行中

## 最后更新

2026-08-02

## 目标和成功标准

新增独立 `GET /foreground`，返回传统 Windows 桌面程序的用户可读前台应用名，同时保持 `/screen` 和
其他现有端点契约不变。

- 公开模式返回 `{"application": "..."}` 或 `{"application": null}`，私密模式在采样前返回 403。
- 名称依次取自 `FileDescription`、`ProductName` 和可执行文件 basename，不读取窗口标题。
- Win32 查询失败降级为空值，进程句柄始终关闭。
- 单元测试、路由回归、Ruff、BasedPyright 和 Windows 实机验证通过。

## 当前方案

- `src/peekapi/foreground.py` 隔离前台窗口、进程路径和版本资源查询，应用名最大 256 字符，拒绝空白、
  控制字符和不可打印值。
- 版本资源按当前用户 UI 语言优先，再按资源声明顺序查询；先查全部 `FileDescription`，再查
  `ProductName`，最后回退 basename。
- `GET /foreground` 复用 `/idle`、`/info` 的公开/私密模式边界，不新增密钥；无法识别时返回稳定 JSON
  schema，而不是 204 或 500。
- `/screen` 不采样前台应用，也不增加响应头。调用方需要截图和应用名时分别请求，时序属于 best effort。

## 现在做到哪里

- Windows 查询模块和 `/foreground` 路由已经实现。
- 查询模块、JSON 字符串/空值、私密模式短路和 `/screen` 隔离测试已经补齐。
- README、architecture overview、独立 runtime flow 和 ADR 已同步。
- Ruff format/check、BasedPyright、122 个 unit 测试与 54 个前台应用相关测试通过；真实 `Code.exe`
  解析为 `Visual Studio Code`，当前前台 Codex 解析为 `Codex`。
- 全量实机测试未稳定全绿：首次运行 136 项通过，真实录音缓冲测试在设备初始化前连续取得空 WAV；该用例
  单独复跑通过。再次运行在实机设备阶段挂起；排除录音实测后 127 项通过，但真实截图在当前静态画面下
  模糊前后 JPEG 完全相同。两项失败都不经过 `/foreground` 代码路径。

## 涉及文件

- `src/peekapi/foreground.py`
- `src/peekapi/server.py`
- `tests/unit/test_foreground.py`
- `tests/unit/test_server.py`
- `README.md`
- `docs/architecture/overview.md`
- `docs/architecture/flows/foreground-application.md`
- `docs/architecture/flows/screen-request.md`
- `docs/adr/0006-expose-foreground-application-endpoint.md`

## 接下来要做

1. 等待用户验收当前 PeekAPI 改动。
2. 在音频设备已经开始产出且桌面存在可模糊内容时，按需复跑两个实机集成用例；不在本计划中改动录音
   或截图测试策略。
3. 插件侧由其独立 PLAN-0006 后续实施。

## 还需要决定什么

- MSIX/UWP 包显示名与任务管理器分组不在首版范围；如果未来要求完全一致，需要单独规划 WinRT 包元数据。
- PeekAPI 与插件的两次请求没有原子一致性；先观察实际效果，再决定是否需要成对重试或采样时间戳。

## 阻碍

- 可重复的软件验证已通过；完整 pytest 仍受真实录音设备启动时序和当前桌面图像内容影响，暂时不能提供
  单次全绿证据。

## 怎么验证

- 单元测试覆盖无窗口、PID/进程访问失败、路径查询失败、版本资源缺失、字段优先级、Unicode、多语言排序、
  不安全字符串、basename 回退和句柄释放。
- TestClient 覆盖应用名、`null`、私密模式 403，并反向确认 `/screen` 不采样也不返回应用响应头。
- Windows 实机直接读取运行中的 `Code.exe`，期望 `Visual Studio Code`。
- 已通过：`uv run pytest tests/unit -n auto`（122 项）、相关测试（54 项）、
  `uv run ruff format --check .`、`uv run ruff check .`、`uv run basedpyright`。
- 全量 pytest 证据：首次 136 通过、1 个录音实机断言失败且单独复跑通过；后续实机套件出现一次挂起，
  排除录音实测后为 127 通过、1 个依赖当前画面的模糊截图断言失败。

## 审批与提交

- 用户确认：已确认实施，等待改动验收
- Git 提交：未提交

## 进展记录

### 2026-08-02

- 用户确认先实施 PeekAPI 侧，并接受独立 `GET /foreground` 方向。
- 完成 Windows 前台应用解析、路由、测试与长期文档同步；插件代码未改动。
- 完成全仓库 Ruff 与 BasedPyright、完整 unit 测试和 Windows 实机名称解析；记录两个既有真实设备测试的
  非确定性结果，未越界修改录音或截图实现。

## 相关文档

- [ADR-0006](../../adr/0006-expose-foreground-application-endpoint.md)
- [前台应用查询 Flow](../../architecture/flows/foreground-application.md)
- [截图请求 Flow](../../architecture/flows/screen-request.md)
- [nonebot-plugin-peek 配套计划](https://github.com/Misty02600/nonebot-plugin-peek/blob/main/docs/plans/todo/0006-show-foreground-application-in-peek.md)
