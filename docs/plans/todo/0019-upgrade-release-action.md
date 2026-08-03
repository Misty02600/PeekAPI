# PLAN-0019：升级 GitHub Release action

## 状态

讨论中

## 最后更新

2026-08-02

## 背景与目标

把 Release workflow 从仍声明 Node.js 20 运行时的 `softprops/action-gh-release@v2` 升级到维护中的 v3
系列，并验证 Release 创建/更新、说明正文和附件上传行为不变。

2026-07-17 重新发布 `v0.3.1` 时 workflow 虽然成功，但 runner 发出旧 Node.js 运行时弃用提示并使用兼容
运行时。继续依赖兼容层会增加未来发布失败风险。

## 已确认的事实和约束

- `.github/workflows/release.yml` 当前使用 `softprops/action-gh-release@v2`，并依赖 changelog body、固定附件
  路径和 `contents: write` 权限。
- v2 分支的 `action.yml` 仍声明 `node20`；截至 2026-08-02，上游最新 GitHub Release 为
  [v3.0.2](https://github.com/softprops/action-gh-release/releases/tag/v3.0.2)。
- 现有 workflow 支持以相同标签重新运行并替换同名附件；升级不能无意改变 Release 名称、说明或 ZIP 命名。
- 创建测试标签和 Release 属于外部写入，必须由用户明确授权；不能为了验证文档计划自行发布。

## 技术路线草案

1. 阅读上游 v2 到 v3 的迁移说明和输入变化，确认当前使用的 `name`、`body`、`files` 与 token 方式仍兼容。
2. 在 `@v3`、精确版本 `@v3.0.2` 或提交 SHA 之间选择引用策略；安全性与可重复性更强的固定版本/提交会
   增加后续人工升级成本。
3. 只修改 action 引用及确有必要的输入，保留版本校验、git-cliff、PyInstaller、ZIP 路径和权限设置。
4. 先做 YAML/静态检查；获得用户授权后，用下一正式版本或明确的临时 prerelease 标签验证完整发布。
5. 对比升级前后的 Release 名称、正文、附件名、附件内容和重新运行语义，再更新 release flow。

## 取舍与待决问题

- 引用浮动主版本、精确版本还是 commit SHA。
- 使用下一正式版本自然验证，还是创建可清理的 prerelease；后者更快但会产生额外外部状态。
- 是否把第三方 actions 的固定策略统一扩展到同一 workflow 的其他步骤；这可能超出本计划范围。

## 希望最后是什么样

- Release workflow 不再依赖 Node.js 20 兼容执行。
- 版本校验、changelog、Windows onefolder ZIP 和 GitHub Release 行为保持不变。
- action 引用策略清楚，后续能判断何时以及如何继续升级。

## 做到什么算完成

- workflow 使用经审查的 v3 action 引用。
- 获批测试标签或下一版本成功生成并上传 Windows ZIP。
- Release 更新、说明正文和附件命名符合现有约定。
- release flow 同步最终行为，用户确认并成功提交后移入 `done/`。

## 涉及范围

- `.github/workflows/release.yml`
- `docs/architecture/flows/release.md`
- 必要时补充 action 版本管理说明

## 怎么验证

先对 workflow 做 YAML 与差异审查；外部验证必须在用户授权后触发。运行完成后检查 job 日志不再出现
Node.js 20 警告，并下载附件核对名称、ZIP 结构、exe 与 `config.toml`。重复发布验证需要另行明确授权。

## 实施确认

- 决定：未确认

## 讨论记录

### 2026-08-02

- 核对当前 workflow、v2 action 运行时与上游 v3.0.2，形成升级和外部验证边界。
- 将旧 `待办` 升级为 `讨论中`，尚未修改 workflow 或创建标签。

## 相关文档

- [Release Flow](../../architecture/flows/release.md)
- [PLAN-0010](../done/0010-automate-github-release.md)
- [softprops/action-gh-release v3.0.2](https://github.com/softprops/action-gh-release/releases/tag/v3.0.2)
