# PLAN-0007: 从 Flask 迁移到 FastAPI

## 状态

已完成

## 完成时间

2026-01-26

## 最后结果和当前行为

HTTP 服务使用 FastAPI/Uvicorn，路由签名负责参数转换与 OpenAPI 描述，lifespan 协调录音、电源通知和托盘启动/清理。

## 怎么验证的

服务器单元测试通过 `TestClient` 覆盖端点、权限和响应类型。

## 审批与提交

- Git 提交：`91e7073`
- 审批记录：历史任务已合入主线；迁移来源未保留独立审批文本。

## 文档同步到哪里

[ADR-0002](../../adr/0002-use-fastapi-and-uvicorn.md) 与 [Application Lifecycle Flow](../../architecture/flows/application-lifecycle.md)。

## 已知缺口和后续事项

托盘强制退出仍绕过 lifespan 清理。

## 相关文档

- [`server.py`](../../../src/peekapi/server.py)
