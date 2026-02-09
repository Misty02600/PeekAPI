# Active Context - PeekAPI

## 当前工作重点

项目处于稳定运行状态，核心功能已完成，CI 检查全部通过。当前关注点：
- CI/CD 配置优化（已完成）
- 添加设备信息端点 (`/info`)（已完成）
- Linux 平台支持（计划中）
- GitHub Release 自动发布（计划中）

## 最近变更

- 2026-02-10: 完成设备信息端点 (`/info`)
  - 使用 PowerShell WMI 查询硬件信息
  - 返回主机名、电脑型号、主板、CPU、显卡
  - 支持 device_name 配置覆盖主机名
- 2026-02-09: 添加用户空闲时间端点 (`/idle`)
  - 使用 Windows GetLastInputInfo API 获取最后操作时间
  - 返回空闲秒数和最后操作时间 (ISO 格式)
- 2026-02-03: 修复 exe 打包后系统托盘图标不显示问题
  - 根因：`console=False` 模式下 `sys.stderr` 为 `None`，日志写入导致崩溃
  - 修复：在 `logging.py` 中添加 stderr 可用性检测
- 2026-02-02: CI 代码检查全面修复（ruff、basedpyright、pytest 全部通过）
  - 修复导入路径：`src.peekapi` → `peekapi`
  - 修复类型问题：`sys._MEIPASS`、`pytest.mark.skipif`
  - 删除未使用导入和变量
  - 修复测试逻辑（favicon、record 端点）
  - 日志 sink 改用 `sys.stderr`
- 2026-02-02: CI 配置更新（测试环境改为 Windows）
- 2026-01-28: 优化 PyInstaller 打包配置（excludes 列表精简、清理脚本）
- 2026-01-26: Flask 重构为 FastAPI，移除 parse_float 死代码，优化录音类

## 当前状态

### 已完成功能
- ✅ 屏幕截图 API (`/screen`)
- ✅ 音频录制 API (`/record`)
- ✅ 用户空闲时间 API (`/idle`)
- ✅ 健康检查 API (`/check`)
- ✅ 系统托盘管理
- ✅ 公开/私密模式切换
- ✅ API 密钥验证
- ✅ 高斯模糊处理
- ✅ 多显示器支持
- ✅ 音频设备自动重连
- ✅ Windows 通知
- ✅ 日志系统 (loguru)
- ✅ exe 打包支持
- ✅ FastAPI 重构（替代 Flask）
- ✅ 单元测试（84 测试通过）
- ✅ CI 代码检查（ruff、pyright、pytest 全通过）

### 计划中
- 📋 Linux 平台支持
- 📋 GitHub Release 自动发布 EXE

## 下一步行动

1. 推送代码到 GitHub，验证 CI 通过
2. 评估 Linux 支持方案
3. 配置 GitHub Release 自动发布

## 活跃决策

### 决策 1: 测试导入路径
- **状态**: 已解决
- **问题**: 测试文件使用 `src.peekapi` 导入路径导致 CI 失败
- **解决方案**: 统一使用 `peekapi` 作为包名导入

### 决策 2: Linux 支持方案
- **状态**: 规划中
- **问题**: winotify 是 Windows 专用，需要替换
- **选项**:
  - 使用跨平台通知库
  - 根据平台条件导入

## 需要注意的事项

1. **配置文件位置** - exe 模式和开发模式路径不同
2. **音频设备** - 需要有默认扬声器才能录音
3. **API 安全** - 生产环境应设置 api_key
4. **CI 环境** - 测试在 Windows 上运行（音频/显示器依赖）

## 阻塞问题

当前无阻塞问题。

## 重要参考

- README.md - 项目说明和 API 文档
- config.toml - 配置示例
- pyproject.toml - 依赖管理
- .github/workflows/ci.yml - CI 配置
