# ADR-0002: 使用 FastAPI 与 Uvicorn

## 状态

已采纳

## 日期

2026-01-26

## 当时遇到了什么

原 HTTP 层使用 Flask，需要手动解析查询参数，也缺少统一的应用生命周期和自动 OpenAPI 描述。服务同时需要返回图片、音频和 JSON，并协调录音与托盘后台资源。

## 最后决定

使用 FastAPI 定义同步路由，使用 Uvicorn 运行 ASGI 服务，并通过 lifespan 启动和停止录音、注册电源事件及启动托盘线程。

## 为什么这样选

路由签名可以统一类型转换、校验和 API 描述；lifespan 为跨模块启动/清理提供单一入口，同时保留同步采集函数。

## 没有采用的方案

- 继续使用 Flask/WSGI。
- 直接使用 Starlette 维护更低层 ASGI 应用。
- 继续手写查询参数解析与响应封装。

## 带来的影响

初始化失败会阻止服务启动；同步采集工作由 FastAPI 的同步端点执行模型承载。托盘强制退出仍会绕过 lifespan 清理。

## 落实与确认

已在提交 `91e7073` 落实，服务测试使用 FastAPI `TestClient` 验证路由和响应语义。

## 相关文档

- [Application Lifecycle Flow](../architecture/flows/application-lifecycle.md)
- [PLAN-0007](../plans/done/0007-migrate-fastapi.md)
- [`server.py`](../../src/peekapi/server.py)
