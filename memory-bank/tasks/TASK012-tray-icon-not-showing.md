# [TASK012] - 系统托盘图标不显示 Bug

**Status:** Completed ✅
**Added:** 2026-02-03
**Updated:** 2026-02-03
**Completed:** 2026-02-03

## Original Request

运行 exe 后系统托盘没有图标。

## Thought Process

这是一个打包后才出现的问题，经过调试发现：

### 调查过程

1. **确认问题**：直接 `just run` 运行正常有图标，打包后的 exe 无图标
2. **启用控制台调试**：临时设置 `console=True` 重新打包，发现程序能正常运行
3. **定位根因**：问题出在 `console=False` 模式下

### 根本原因

在 PyInstaller 打包的无窗口模式（`console=False`）下：
- `sys.stdout` 和 `sys.stderr` 都为 `None`
- `logging.py` 中 `logger.add(sink=sys.stderr, ...)` 尝试向 `None` 写入日志
- 这导致程序在启动时立即崩溃，托盘图标根本没有机会显示

### 解决方案

在添加控制台日志前检测 `sys.stderr` 是否可用：

```python
# 控制台日志（仅在 stderr 可用时添加，无窗口模式下 stderr 为 None）
if sys.stderr is not None:
    logger.add(
        sink=sys.stderr,
        format="{time:HH:mm:ss} [{level}] {message}",
        level="INFO",
        colorize=True,
    )
```

## Implementation Plan

- [x] 1.1 复现问题 - 打包并运行 exe，确认问题存在
- [x] 1.2 检查日志 - 发现 logs 目录不存在，程序根本没运行
- [x] 1.3 控制台运行 - 设置 console=True 发现程序能正常运行
- [x] 1.4 验证图标路径 - 确认图标文件在 _internal 目录正确位置
- [x] 1.5 修复问题 - 在 logging.py 中添加 stderr 检测
- [x] 1.6 验证修复 - 重新打包测试成功

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks
| ID  | Description  | Status   | Updated    | Notes                 |
| --- | ------------ | -------- | ---------- | --------------------- |
| 1.1 | 复现问题     | Complete | 2026-02-03 | 确认 exe 无图标       |
| 1.2 | 检查日志     | Complete | 2026-02-03 | logs 目录不存在       |
| 1.3 | 控制台运行   | Complete | 2026-02-03 | console=True 时正常   |
| 1.4 | 验证图标路径 | Complete | 2026-02-03 | 图标在 _internal 目录 |
| 1.5 | 修复问题     | Complete | 2026-02-03 | 添加 stderr 检测      |
| 1.6 | 验证修复     | Complete | 2026-02-03 | 测试通过              |

## Progress Log

### 2026-02-03
- 任务创建
- 确认问题：直接运行有图标，exe 无图标
- 启用 console=True 调试，发现程序能正常运行
- 定位根因：sys.stderr 在无窗口模式下为 None
- 修复 logging.py，添加 stderr 可用性检测
- 恢复 console=False，重新打包
- 用户测试成功，任务完成

## 相关文件

- `src/peekapi/logging.py` - **已修复** - 添加 stderr 检测
- `peekapi.spec` - PyInstaller 打包配置
