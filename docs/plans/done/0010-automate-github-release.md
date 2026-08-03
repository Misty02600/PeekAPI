# PLAN-0010: 自动发布 Windows ZIP

## 状态

已完成

## 完成时间

2026-02-09

## 最后结果和当前行为

推送 `v*` 标签会触发 Windows Release workflow，校验项目与标签版本、生成 changelog、构建 PyInstaller onefolder、压缩 ZIP 并创建或更新 GitHub Release。

## 怎么验证的

多个版本标签已成功发布；`v0.3.1` 的重新发布也成功生成并替换 Windows ZIP。

## 审批与提交

- Git 提交：`973ecd7`、`784915c`、`eb54c79`
- 审批记录：发布流程与 `v0.3.1` 重新发布均由用户明确执行/确认。

## 文档同步到哪里

[Release Flow](../../architecture/flows/release.md) 与 [ADR-0003](../../adr/0003-use-pyinstaller-onefolder.md)。

## 已知缺口和后续事项

action 的 Node.js 运行时升级见 [PLAN-0019](../todo/0019-upgrade-release-action.md)。

## 相关文档

- [`.github/workflows/release.yml`](../../../.github/workflows/release.yml)
