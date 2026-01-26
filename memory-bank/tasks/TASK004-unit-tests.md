# [TASK004] - 为项目编写单元测试

**Status:** Completed
**Added:** 2026-01-25
**Updated:** 2026-01-25
**Priority:** Medium

## Original Request

为项目编写单元测试。

## Thought Process

### 当前测试状态

- ✅ 测试框架已配置（pytest 9.0.2, pytest-cov 7.0.0）
- ✅ 63 个测试用例，全部通过
- ✅ 代码覆盖率 75%

### 项目模块分析

| 模块 | 可测试性 | 测试重点 | 覆盖率 |
|------|----------|----------|--------|
| config.py | ✅ 高 | TOML 解析、默认值、类型验证 | 100% |
| constants.py | ✅ 高 | 路径计算逻辑 | 94% |
| screenshot.py | ⚠️ 中 | 需要 mock mss | 100% |
| record.py | ⚠️ 中 | 需要 mock soundcard | 85% |
| server.py | ⚠️ 中 | Flask 测试客户端 | 76% |
| system_tray.py | ❌ 低 | GUI 相关，难以自动化 | 36% |
| logging.py | ❌ 低 | 日志配置 | 45% |

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

## 截图模块测试详细方案 (test_screenshot.py)

### 模块分析

**screenshot.py 功能：**
1. 使用 `mss` 库截取屏幕
2. 支持全部屏幕 (`monitors[0]`) 或主屏幕 (`monitors[1]`)
3. 可选高斯模糊处理 (PIL.ImageFilter)
4. 输出 JPEG 格式字节流

### Mock 策略

需要 mock `mss.mss()` 返回的截图对象：

```python
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_mss():
    """模拟 mss 截图"""
    mock_img = MagicMock()
    mock_img.size = (1920, 1080)
    # 创建假的 RGB 数据 (1920 * 1080 * 3 字节)
    mock_img.rgb = b'\x00\x80\xff' * (1920 * 1080)  # 蓝色像素

    mock_sct = MagicMock()
    mock_sct.monitors = [
        {"top": 0, "left": 0, "width": 3840, "height": 1080},  # 全部
        {"top": 0, "left": 0, "width": 1920, "height": 1080},  # 主屏
    ]
    mock_sct.grab.return_value = mock_img
    mock_sct.__enter__ = MagicMock(return_value=mock_sct)
    mock_sct.__exit__ = MagicMock(return_value=False)

    with patch('src.peekapi.screenshot.mss.mss', return_value=mock_sct):
        yield mock_sct
```

### 测试用例

| 测试 | 说明 |
|------|------|
| `test_screenshot_returns_jpeg` | 验证返回 JPEG 格式（检查魔数 `\xff\xd8\xff`） |
| `test_screenshot_main_screen_only` | 验证 `main_screen_only=True` 使用 `monitors[1]` |
| `test_screenshot_all_screens` | 验证 `main_screen_only=False` 使用 `monitors[0]` |
| `test_screenshot_with_blur` | 验证 `radius > 0` 时应用模糊 |
| `test_screenshot_no_blur` | 验证 `radius = 0` 时不模糊 |

---

## 音频模块测试详细方案 (test_record.py)

### 模块分析

**record.py 功能：**
1. 后台线程持续录音（Loopback 系统音频）
2. 环形缓冲区存储最近 N 秒音频
3. 自动重连断开的设备
4. 输出 WAV 格式

### Mock 策略

需要 mock `soundcard` 库：

```python
from unittest.mock import MagicMock, patch
import numpy as np

@pytest.fixture
def mock_soundcard():
    """模拟 soundcard 库"""
    # 模拟录音数据 (0.1秒的静音)
    mock_data = np.zeros((4410, 1), dtype=np.float32)

    mock_recorder = MagicMock()
    mock_recorder.record.return_value = mock_data
    mock_recorder.__enter__ = MagicMock(return_value=mock_recorder)
    mock_recorder.__exit__ = MagicMock(return_value=False)

    mock_mic = MagicMock()
    mock_mic.recorder.return_value = mock_recorder

    mock_speaker = MagicMock()
    mock_speaker.name = "Test Speaker"
    mock_speaker.id = "test-id"

    with patch('src.peekapi.record.sc.default_speaker', return_value=mock_speaker):
        with patch('src.peekapi.record.sc.get_microphone', return_value=mock_mic):
            yield {
                'speaker': mock_speaker,
                'mic': mock_mic,
                'recorder': mock_recorder,
                'data': mock_data,
            }
```

### 测试用例

| 测试 | 说明 |
|------|------|
| `test_recorder_init` | 验证初始化参数正确设置 |
| `test_recorder_buffer_size` | 验证缓冲区大小 = rate × duration |
| `test_start_recording` | 验证启动录音后 `is_recording = True` |
| `test_stop_recording` | 验证停止录音后 `is_recording = False` |
| `test_get_audio_returns_wav` | 验证返回有效 WAV（检查魔数 `RIFF`） |
| `test_get_audio_empty_buffer` | 验证空缓冲区返回空 WAV |
| `test_gain_amplification` | 验证增益放大逻辑 |
| `test_device_reconnect` | 验证设备断开后重连（mock 异常） |

### 集成测试注意事项

音频测试可分为两类：

1. **单元测试（mock）**：测试业务逻辑，不依赖真实硬件
2. **集成测试（可选）**：需要真实音频设备，标记为 `@pytest.mark.integration`

```python
@pytest.mark.integration
@pytest.mark.skipif(not has_audio_device(), reason="No audio device")
def test_real_audio_recording():
    """集成测试：真实录音"""
    ...
```

---

## Implementation Plan

- [x] 1.1 添加测试依赖（pytest, pytest-cov）
- [x] 1.2 创建 tests/ 目录结构
- [x] 1.3 编写 conftest.py（共享 fixtures）
- [x] 1.4 编写 test_config.py（13 个测试用例）
- [x] 1.5 编写 test_constants.py（7 个测试用例）
- [ ] 1.6 编写 test_server.py（Flask 测试客户端）
- [ ] 1.7 编写 test_screenshot.py（mock mss）
- [ ] 1.8 编写 test_record.py（mock soundcard）
- [x] 1.9 配置 pytest（pyproject.toml）
- [ ] 1.10 运行测试并检查覆盖率
- [ ] 1.11 更新记忆库文档

## Progress Tracking

**Overall Status:** In Progress - 50%

### Subtasks

| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | 添加测试依赖 | ✅ Complete | 2026-01-25 | pytest 9.0.2, pytest-cov 7.0.0 |
| 1.2 | 创建目录结构 | ✅ Complete | 2026-01-25 | tests/__init__.py |
| 1.3 | conftest.py | ✅ Complete | 2026-01-25 | temp_dir, sample_config fixtures |
| 1.4 | test_config.py | ✅ Complete | 2026-01-25 | 13 个测试，全部通过 |
| 1.5 | test_constants.py | ✅ Complete | 2026-01-25 | 7 个测试，全部通过 |
| 1.6 | test_server.py | Not Started | - | API 端点测试 |
| 1.7 | test_screenshot.py | Not Started | - | 见上方详细方案 |
| 1.8 | test_record.py | Not Started | - | 见上方详细方案 |
| 1.9 | pytest 配置 | ✅ Complete | 2026-01-25 | pyproject.toml |
| 1.10 | 运行测试 | In Progress | 2026-01-25 | 20/20 passed |
| 1.11 | 更新文档 | Not Started | - | progress.md |

## Progress Log

### 2026-01-25
- 创建任务记录
- 分析项目模块可测试性
- 设计测试目录结构和用例规划
- ✅ 添加 pytest, pytest-cov 开发依赖
- ✅ 创建 tests/ 目录和 conftest.py
- ✅ 实现 test_config.py（13 个测试用例）
- ✅ 实现 test_constants.py（7 个测试用例）
- ✅ 配置 pyproject.toml pytest 设置
- ✅ 运行测试：20 passed in 0.19s
- 📝 补充截图/音频测试详细实施文档
- 📝 分析音频模块内存占用（默认 20 秒约 8.4 MB）

## References

- [pytest 文档](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Flask 测试](https://flask.palletsprojects.com/en/3.0.x/testing/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
