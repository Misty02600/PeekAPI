# PLAN-0004: 建立单元与集成测试体系

## 状态

已完成

## 完成时间

2026-01-26

## 最后结果和当前行为

项目使用 pytest、pytest-cov、httpx 和 mock，分为 `tests/unit` 与 `tests/integration`；硬件依赖在单元测试隔离，真实截图和 Loopback 留给集成测试。

## 怎么验证的

CI 在 Windows Python 3.11–3.13 运行 pytest/coverage，并在 Ubuntu 运行 Ruff 与 BasedPyright。

## 审批与提交

- Git 提交：`3bfefa7`，CI 完善见 `39c6170`、`374fca2`
- 审批记录：历史任务已合入主线；迁移来源未保留独立审批文本。

## 文档同步到哪里

[Architecture Overview](../../architecture/overview.md) 与各 source/flow guide 的验证入口。

## 已知缺口和后续事项

电源状态转换缺少独立测试，见 [PLAN-0017](../todo/0017-fix-recorder-lifecycle-races.md)。

## 相关文档

- [`tests/`](../../../tests)
- [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml)
