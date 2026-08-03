# PLAN-0005: 优化 PyInstaller 打包

## 状态

已完成

## 完成时间

2026-02-02

## 最后结果和当前行为

版本控制中的 `peekapi.spec` 生成无控制台 onefolder 目录，收集图标、配置和动态依赖；用户可直接编辑 exe 同级 `config.toml`。

## 怎么验证的

历史发布构建和打包实机验证覆盖启动、托盘、截图、录音与文件日志。

## 审批与提交

- Git 提交：`483c74b`、`0770633`
- 审批记录：历史任务已合入主线；迁移来源未保留独立审批文本。

## 文档同步到哪里

[ADR-0003](../../adr/0003-use-pyinstaller-onefolder.md) 与 [Release Flow](../../architecture/flows/release.md)。

## 已知缺口和后续事项

依赖与 PyInstaller 升级仍需发布构建验证；当前工作区的版本元数据重构尚未提交。

## 相关文档

- [`peekapi.spec`](../../../peekapi.spec)
