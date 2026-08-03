# ADR-0003: 使用 PyInstaller onefolder 发布 Windows 应用

## 状态

已采纳

## 日期

2026-01-26

## 当时遇到了什么

目标用户不应先安装 Python，应用又依赖音频、图像和托盘原生组件，并需要让用户直接编辑 exe 同级的 `config.toml`。

## 最后决定

使用版本控制中的 `peekapi.spec` 生成无控制台的 PyInstaller onefolder 目录，把图标、依赖元数据和配置纳入产物，再以 ZIP 发布。

## 为什么这样选

目录式产物无需 onefile 启动解压，配置文件位置直观，spec 也可由本地与 GitHub Actions 复用。

## 没有采用的方案

- PyInstaller onefile。
- Nuitka。
- cx_Freeze 或 Briefcase。

## 带来的影响

发布目录体积较大；动态导入、原生库和 PyInstaller 升级都可能导致打包回归。无控制台模式要求日志模块兼容 `stderr` 不可用。

## 落实与确认

基础打包在 `483c74b` 落实，版本控制中的 spec 与目录式发布在 `0770633`、`784915c` 继续确认。当前工作区正在统一版本元数据来源，完成前不改变本决策。

## 相关文档

- [Release Flow](../architecture/flows/release.md)
- [PLAN-0005](../plans/done/0005-optimize-packaging.md)
- [`peekapi.spec`](../../peekapi.spec)
