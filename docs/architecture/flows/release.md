# Flow: 版本发布

## 这条流程保证什么

一个与项目版本一致的 `v*` 标签可以在 Windows runner 上生成可独立运行的 onefolder ZIP，并创建或更新同名 GitHub Release。

## 外部参与者和触发条件

- Commitizen/uv 更新项目版本并创建标签。
- 推送 `v*` 标签触发 `.github/workflows/release.yml`。
- git-cliff、PyInstaller、zip-release 和 action-gh-release 生成说明与产物。

## 稳定的状态变化

1. workflow 检出完整历史，从项目元数据和标签分别读取版本。
2. 两个版本不一致时立即失败。
3. git-cliff 生成当前版本说明。
4. PyInstaller 根据 `peekapi.spec` 构建 `dist/peekapi/`。
5. 目录被压缩为 `PeekAPI-v<version>-windows.zip`。
6. GitHub Release 被创建或更新，并上传同名附件。

## 失败时的语义

- 版本校验、构建或压缩失败时不会上传新的 Release 附件。
- 强制移动已有标签会重新触发 workflow，并可能替换同名附件；这属于高风险恢复操作。
- `softprops/action-gh-release@v2` 当前依赖兼容运行时，升级事项见 [PLAN-0019](../../plans/todo/0019-upgrade-release-action.md)。

## 相关决定与实现

- [ADR-0003: 使用 PyInstaller onefolder](../../adr/0003-use-pyinstaller-onefolder.md)
- [`.github/workflows/release.yml`](../../../.github/workflows/release.yml)
- [`peekapi.spec`](../../../peekapi.spec)
