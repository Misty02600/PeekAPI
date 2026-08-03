# PLAN-0013: 添加用户空闲时间端点

## 状态

已完成

## 完成时间

2026-02-09

## 最后结果和当前行为

`GET /idle` 通过 Win32 `GetLastInputInfo` 返回 `idle_seconds` 和带时区的 `last_input_time`，并遵循公开/私密模式控制。

## 怎么验证的

`tests/unit/test_idle.py` 与服务器路由测试覆盖时间计算、JSON 格式和私密模式。

## 审批与提交

- Git 提交：`a66096f`
- 审批记录：历史任务已合入主线；迁移来源未保留独立审批文本。

## 文档同步到哪里

[项目总览](../../architecture/overview.md)。

## 已知缺口和后续事项

仅支持 Windows；跨平台事项见 [PLAN-0001](../todo/0001-linux-support.md)。

## 相关文档

- [`idle.py`](../../../src/peekapi/idle.py)
