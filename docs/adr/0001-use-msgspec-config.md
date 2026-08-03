# ADR-0001: 使用 msgspec 管理 TOML 配置

## 状态

已采纳

## 日期

2026-01-25

## 当时遇到了什么

应用需要从 `config.toml` 加载类型化嵌套配置，并允许托盘在运行时修改公开/私密状态。原配置层依赖 Pydantic 和大量 property，桌面打包场景也关注启动成本与依赖体积。

## 最后决定

使用可变 `msgspec.Struct` 定义分组配置，通过 `msgspec.toml.decode` 解析 TOML；调用方直接访问 `config.basic`、`config.screenshot` 和 `config.record`，运行路径常量放在 `constants.py`。

## 为什么这样选

它保留明确类型和默认值，同时减少代理属性与运行时依赖；公开模式仍能在当前进程内直接切换。

## 没有采用的方案

- 保留 Pydantic 模型和手写 property。
- 用 `__getattr__` 动态代理嵌套字段。
- 使用 `tomllib` 返回普通字典。

## 带来的影响

配置在模块导入时加载，解析失败会阻止应用导入；`is_public` 的运行时修改不会写回 TOML。目前没有额外的字段范围约束。

## 落实与确认

已在提交 `fc3c520` 落实；配置单元测试覆盖默认、部分/完整 TOML 与类型错误。后续修改不得用“已落实”替代本 ADR 的采纳状态。

## 相关文档

- [Architecture Overview](../architecture/overview.md)
- [PLAN-0002](../plans/done/0002-config-msgspec-refactor.md)
- [`config.py`](../../src/peekapi/config.py)
