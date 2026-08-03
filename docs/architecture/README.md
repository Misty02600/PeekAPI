# 从哪里开始看 PeekAPI

## 先记住

- PeekAPI 是运行在 Windows 桌面上的本地 HTTP 服务，不负责公网穿透、账户或远程控制。
- FastAPI 路由统一执行隐私与截图密钥检查，再调用截图、录音和 Windows 状态查询组件。
- 录音器拥有线程、设备会话和内存缓冲；lifespan、托盘与电源通知共同请求它启停。
- 配置、日志和发布产物落盘，截图与最近音频以外的业务数据不持久化。

## 阅读路线

| 想了解什么 | 从这里开始 |
|---|---|
| 系统边界、逻辑组件、依赖与状态所有权 | [Overview](overview.md) |
| 启动、关闭和休眠恢复 | [Application Lifecycle Flow](flows/application-lifecycle.md) |
| 音频如何进入 `/record` | [Audio Recording Flow](flows/audio-recording.md) |
| 截图鉴权与图像响应 | [Screen Request Flow](flows/screen-request.md) |
| `/foreground` 如何取得应用名 | [Foreground Application Flow](flows/foreground-application.md) |
| 标签如何生成 Release | [Release Flow](flows/release.md) |
| 长期技术取舍 | [ADR 索引](../adr/README.md) |
| 尚未闭环的工作 | [Plans](../plans/README.md) |

当前系统规模不需要 C4 图；如果组件或部署边界明显增加，再补最小必要视图。

## 源码追溯

原有按目录和单文件组织的 guide 不再作为长期文档入口。需要从架构定位实现时，先看
[项目总览](overview.md) 的“逻辑组件与实现映射”，再直接阅读其中链接的真实源码。
