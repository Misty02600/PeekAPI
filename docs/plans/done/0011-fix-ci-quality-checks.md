# PLAN-0011: 修复 CI 质量检查

## 状态

已完成

## 完成时间

2026-02-02

## 最后结果和当前行为

测试统一从 `peekapi` 包导入，清理 Ruff/BasedPyright 问题并修正 mock、skip 和测试预期；CI 分别运行 Ruff、格式、BasedPyright 与 Windows pytest 矩阵。

## 怎么验证的

对应 CI 提交通过；当前 workflow 继续以相同检查作为合并门槛。

## 审批与提交

- Git 提交：`39c6170`、`374fca2`
- 审批记录：历史任务已合入主线；迁移来源未保留独立审批文本。

## 文档同步到哪里

[Architecture Overview](../../architecture/overview.md) 与 [PLAN-0004](0004-add-tests.md)。

## 已知缺口和后续事项

真实硬件与 Modern Standby 仍需要 Windows 专用验证。

## 相关文档

- [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)
