# Tasks Index - PeekAPI

## 任务状态图例

- 🔄 **In Progress** - 正在进行
- ⏳ **Pending** - 待处理
- ✅ **Completed** - 已完成
- ❌ **Abandoned** - 已放弃

---

## In Progress

*当前无进行中的任务*

---

## Pending

- [TASK001] 支持 Linux 平台 - 替换 Windows 专用依赖，实现跨平台支持

---

## Completed

- [TASK014] 修复 GetTickCount 溢出问题 - ✅ 2026-02-10 完成（使用 GetTickCount64）
- [TASK010] GitHub Release 自动发布 EXE - ✅ 2026-02-10 完成（配置 CI 自动打包并发布到 GitHub Releases）
- [TASK015] 添加设备信息端点 - ✅ 2026-02-10 完成（/info 端点获取硬件信息）
- [TASK013] 添加用户空闲时间端点 - ✅ 2026-02-09 完成（/idle 端点获取用户空闲时间）
- [TASK012] 系统托盘图标不显示 - ✅ 2026-02-03 完成（修复 stderr 为 None 导致崩溃）
- [TASK011] CI 代码检查修复 - ✅ 2026-02-02 完成（ruff、basedpyright、pytest 全部通过）

- [TASK002] 重构 Config 模块使用 msgspec - ✅ 2026-01-25 完成
- [TASK003] 日志系统迁移到 loguru - ✅ 2026-01-25 完成
- [TASK004] 为项目编写单元测试 - ✅ 2026-01-25 完成（63 测试，75% 覆盖率）
- [TASK005] 优化打包流程 - ✅ 2026-01-26 完成（spec 文件 + Windows 版本信息）
- [TASK007] 将 Flask 重构为 FastAPI - ✅ 2026-01-26 完成（28 测试通过）
- [TASK008] 移除手动类型校验函数 - ✅ 2026-01-26 完成（删除 parse_float 死代码）
- [TASK009] 优化录音类 - ✅ 2026-01-26 完成（移除 channels、添加类型提示）

---

## Abandoned

*无放弃的任务*

---

## 任务统计

| 状态        | 数量   |
| ----------- | ------ |
| In Progress | 0      |
| Pending     | 1      |
| Completed   | 13     |
| Abandoned   | 0      |
| **总计**    | **14** |

---

*最后更新: 2026-02-10*
