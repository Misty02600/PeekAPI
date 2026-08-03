# PLAN-0012: 修复无控制台打包后的托盘启动

## 状态

已完成

## 完成时间

2026-02-03

## 最后结果和当前行为

loguru 只在 `sys.stderr` 可用时添加控制台 sink；PyInstaller `console=False` 环境改为只写文件日志，不再因向 `None` 输出而在托盘出现前退出。

## 怎么验证的

重新打包后由用户确认应用和托盘均能正常启动。

## 审批与提交

- Git 提交：`f4bcbea`
- 审批记录：用户完成打包实机确认。

## 文档同步到哪里

[应用生命周期 Flow](../../architecture/flows/application-lifecycle.md) 与
[ADR-0003](../../adr/0003-use-pyinstaller-onefolder.md)。

## 已知缺口和后续事项

托盘模块自动化覆盖仍较低。

## 相关文档

- [`logging.py`](../../../src/peekapi/logging.py)
- [`system_tray.py`](../../../src/peekapi/system_tray.py)
