# PLAN-0014: 修复 idle tick count 回绕

## 状态

已完成

## 完成时间

2026-02-10

## 最后结果和当前行为

系统运行时间显式使用 `GetTickCount64` 的 64 位返回值，并按无符号 32 位边界处理 `LASTINPUTINFO.dwTime` 回绕，避免长时间运行后出现负空闲时间。

## 怎么验证的

`tests/unit/test_idle.py` 覆盖大 tick 值与回绕边界。

## 审批与提交

- Git 提交：`a66096f`
- 审批记录：历史任务已合入主线；迁移来源未保留独立审批文本。

## 文档同步到哪里

[项目总览](../../architecture/overview.md)。

## 已知缺口和后续事项

`dwTime` 只有 32 位，无法无歧义表达超过一次完整回绕周期的输入历史。

## 相关文档

- [`idle.py`](../../../src/peekapi/idle.py)
