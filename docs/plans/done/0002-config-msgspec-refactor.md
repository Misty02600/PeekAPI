# PLAN-0002: 使用 msgspec 重构配置层

## 状态

已完成

## 完成时间

2026-01-25

## 最后结果和当前行为

配置层使用可变的嵌套 `msgspec.Struct`，`config.toml` 直接解码为类型化对象；调用方通过 `config.basic`、`config.screenshot`、`config.record` 访问，公开模式只在当前进程内修改。

## 怎么验证的

`tests/unit/test_config.py` 覆盖默认值、部分/完整 TOML 和类型错误。

## 审批与提交

- Git 提交：`fc3c520`
- 审批记录：历史任务已合入主线；迁移来源未保留独立审批文本。

## 文档同步到哪里

[ADR-0001](../../adr/0001-use-msgspec-config.md) 与 [Architecture Overview](../../architecture/overview.md)。

## 已知缺口和后续事项

字段范围约束和配置热更新尚未实现。

## 相关文档

- [`config.py`](../../../src/peekapi/config.py)
