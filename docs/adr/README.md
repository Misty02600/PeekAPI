# Architecture Decision Records

ADR 只记录会长期影响架构、依赖、部署或跨模块协作的决定。编号一旦使用就保持稳定；已采纳或未采纳的决定不重写历史，只修正链接、错字或状态关系。

## 当前有效

| ADR | 状态 | 日期 | 决定 |
|---|---|---|---|
| [0001](0001-use-msgspec-config.md) | 已采纳 | 2026-01-25 | 使用 msgspec 管理 TOML 配置 |
| [0002](0002-use-fastapi-and-uvicorn.md) | 已采纳 | 2026-01-26 | 使用 FastAPI 与 Uvicorn 提供 HTTP API |
| [0003](0003-use-pyinstaller-onefolder.md) | 已采纳 | 2026-01-26 | 使用 PyInstaller onefolder 发布 Windows 应用 |
| [0004](0004-use-soundfile-for-wav.md) | 已采纳 | 2026-01-26 | 使用 soundfile 生成 WAV |
| [0005](0005-handle-suspend-resume-events.md) | 已采纳 | 2026-03-12 | 使用双重 Windows 电源通知机制协调录音 |
| [0006](0006-expose-foreground-application-endpoint.md) | 已采纳 | 2026-08-02 | 用独立端点查询前台应用显示名 |
| [0007](0007-use-hkcu-run-for-logon-autostart.md) | 已采纳 | 2026-08-11 | 使用 HKCU Run 管理 Windows 用户登录自启 |

## 讨论中

当前没有讨论中的 ADR。

## 已替代

当前没有已替代的 ADR。

## 未采纳

当前没有未采纳的 ADR。

可用状态为 `讨论中`、`已采纳`、`已替代`、`未采纳`。是否已经在代码中落实写在 ADR 的“落实与确认”，
不把 `Implemented` 当成决策状态。只有构想时留在 scratch；普通实施路线进入 plan；已经形成可评审且
具有架构意义的提案进入 ADR。
