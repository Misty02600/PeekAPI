# [TASK004] - 为项目编写单元测试

**Status:** Pending
**Added:** 2026-01-25
**Updated:** 2026-01-25
**Priority:** Medium

## Original Request

为项目编写单元测试。

## Thought Process

### 当前测试状态

- 无测试文件存在
- pyproject.toml 中无 pytest 依赖
- 仅有手动测试

### 项目模块分析

| 模块 | 可测试性 | 测试重点 |
|------|----------|----------|
| config.py | ✅ 高 | TOML 解析、默认值、类型验证 |
| constants.py | ✅ 高 | 路径计算逻辑 |
| screenshot.py | ⚠️ 中 | 需要 mock mss |
| record.py | ⚠️ 中 | 需要 mock soundcard |
| server.py | ⚠️ 中 | Flask 测试客户端 |
| system_tray.py | ❌ 低 | GUI 相关，难以自动化 |

### 测试框架选择

**pytest** - Python 主流测试框架
- 简洁的断言语法
- 强大的 fixture 机制
- 丰富的插件生态

**pytest-cov** - 覆盖率报告

### 目录结构设计

```
tests/
├── __init__.py
├── conftest.py          # 共享 fixtures
├── test_config.py       # 配置模块测试
├── test_constants.py    # 常量模块测试
├── test_screenshot.py   # 截图模块测试（mock）
├── test_record.py       # 录音模块测试（mock）
└── test_server.py       # API 端点测试
```

### 测试用例规划

**test_config.py:**
- 空文件加载默认值
- 完整 TOML 解析
- 部分配置覆盖默认值
- 嵌套属性访问
- is_public 运行时修改

**test_constants.py:**
- 开发环境路径计算
- 打包环境路径计算（mock sys.frozen）

**test_server.py:**
- GET /health 返回 200
- POST /health 返回 200
- GET /screenshot 返回图片
- GET /audio 返回 WAV
- API Key 验证（私密模式）

---

## Implementation Plan

- [ ] 1.1 添加测试依赖（pytest, pytest-cov）
- [ ] 1.2 创建 tests/ 目录结构
- [ ] 1.3 编写 conftest.py（共享 fixtures）
- [ ] 1.4 编写 test_config.py
- [ ] 1.5 编写 test_constants.py
- [ ] 1.6 编写 test_server.py（Flask 测试客户端）
- [ ] 1.7 编写 test_screenshot.py（mock mss）
- [ ] 1.8 编写 test_record.py（mock soundcard）
- [ ] 1.9 配置 pytest（pyproject.toml）
- [ ] 1.10 运行测试并检查覆盖率
- [ ] 1.11 更新记忆库文档

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks

| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | 添加测试依赖 | Not Started | - | pytest, pytest-cov |
| 1.2 | 创建目录结构 | Not Started | - | tests/ |
| 1.3 | conftest.py | Not Started | - | 临时配置文件 fixture |
| 1.4 | test_config.py | Not Started | - | 核心测试 |
| 1.5 | test_constants.py | Not Started | - | 路径逻辑测试 |
| 1.6 | test_server.py | Not Started | - | API 测试 |
| 1.7 | test_screenshot.py | Not Started | - | mock mss |
| 1.8 | test_record.py | Not Started | - | mock soundcard |
| 1.9 | pytest 配置 | Not Started | - | pyproject.toml |
| 1.10 | 运行测试 | Not Started | - | 覆盖率报告 |
| 1.11 | 更新文档 | Not Started | - | progress.md |

## Progress Log

### 2026-01-25
- 创建任务记录
- 分析项目模块可测试性
- 设计测试目录结构和用例规划

## References

- [pytest 文档](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Flask 测试](https://flask.palletsprojects.com/en/3.0.x/testing/)
