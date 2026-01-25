# [TASK001] - 支持 Linux 平台

**Status:** Pending
**Added:** 2026-01-25
**Updated:** 2026-01-25
**Priority:** High

## Original Request

根据 README.md 中的 Todo 项：支持 Linux 平台

## Thought Process

### 问题分析

当前项目使用了以下 Windows 专用组件：

1. **winotify** - Windows 通知库
   - 用于显示系统通知
   - 需要替换为跨平台方案

2. **soundcard** - 音频库
   - Loopback 录音在不同平台实现不同
   - 需要测试 Linux 兼容性

3. **pystray** - 系统托盘
   - 本身支持 Linux
   - 但行为可能不同

### 可能方案

1. **通知系统替换**
   - 选项 A: 使用 plyer（跨平台）
   - 选项 B: 根据平台条件导入
   - 选项 C: 移除通知功能（Linux 版本）

2. **音频录制**
   - 测试 soundcard 在 Linux 的表现
   - 可能需要 PulseAudio/PipeWire 支持

## Implementation Plan

- [ ] 1.1 研究跨平台通知库选项
- [ ] 1.2 测试 soundcard 在 Linux 的兼容性
- [ ] 1.3 创建平台检测模块
- [ ] 1.4 实现条件导入
- [ ] 1.5 Linux 环境测试
- [ ] 1.6 更新文档

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks

| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | 研究跨平台通知库选项 | Not Started | - | plyer, notify2 等 |
| 1.2 | 测试 soundcard Linux 兼容性 | Not Started | - | 需要 Linux 环境 |
| 1.3 | 创建平台检测模块 | Not Started | - | sys.platform 判断 |
| 1.4 | 实现条件导入 | Not Started | - | 依赖 1.1-1.3 结果 |
| 1.5 | Linux 环境测试 | Not Started | - | 完整功能测试 |
| 1.6 | 更新文档 | Not Started | - | README, 安装说明 |

## Progress Log

### 2026-01-25
- 创建任务记录
- 分析现有代码中的 Windows 依赖
- 制定初步实施计划

## References

- [README.md Todo 项](../README.md)
- [docs/plan.md](../../docs/plan.md) - 如存在详细方案
