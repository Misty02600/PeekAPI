# [TASK013] - 添加用户空闲时间端点

**Status:** Completed
**Added:** 2026-02-09
**Updated:** 2026-02-09

## Original Request

为项目添加端点，获取用户最后操作电脑的时间。

## Thought Process

### 背景分析

PeekAPI 是一个本地 API 服务，目前提供：
- `/screen` - 屏幕截图
- `/record` - 系统音频录制
- `/check` - 健康检查

用户希望添加一个新端点，用于获取用户最后操作电脑的时间（空闲时间检测）。

### 技术方案

在 Windows 上，可以使用 Win32 API `GetLastInputInfo` 来获取用户最后一次输入事件（键盘或鼠标）的时间。使用 Python 的 `ctypes` 模块调用此 API。

**核心代码思路：**
```python
import ctypes
from ctypes import Structure, windll, c_uint, sizeof
from datetime import datetime

class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]

def get_idle_time() -> tuple[float, datetime]:
    """
    获取用户空闲时间
    返回: (空闲秒数, 最后操作时间)
    """
    lii = LASTINPUTINFO()
    lii.cbSize = sizeof(LASTINPUTINFO)
    windll.user32.GetLastInputInfo(ctypes.byref(lii))

    # GetTickCount 返回系统启动后的毫秒数
    current_tick = windll.kernel32.GetTickCount()
    idle_ms = current_tick - lii.dwTime
    idle_seconds = idle_ms / 1000.0

    last_input_time = datetime.now() - timedelta(seconds=idle_seconds)
    return idle_seconds, last_input_time
```

### 端点设计

**端点**: `GET /idle`

**响应格式** (JSON):
```json
{
    "idle_seconds": 123.456,
    "last_input_time": "2026-02-09T22:50:00+08:00"
}
```

**权限控制**:
- 与其他端点一致，受 `is_public` 模式控制
- 私密模式下拒绝请求

## Implementation Plan

- [x] 1.1 创建 `idle.py` 模块，实现 `get_idle_info()` 函数
- [x] 1.2 在 `server.py` 中添加 `/idle` 端点
- [x] 1.3 添加单元测试
- [x] 1.4 更新 README 文档

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks

| ID  | Description       | Status   | Updated    | Notes                       |
| --- | ----------------- | -------- | ---------- | --------------------------- |
| 1.1 | 创建 idle.py 模块 | Complete | 2026-02-09 | 使用 Win32 GetLastInputInfo |
| 1.2 | 添加 /idle 端点   | Complete | 2026-02-09 | 遵循现有端点模式            |
| 1.3 | 添加单元测试      | Complete | 2026-02-09 | 9 个测试全部通过            |
| 1.4 | 更新 README 文档  | Complete | 2026-02-09 | 添加 API 说明               |

## Progress Log

### 2026-02-09
- 创建任务文件
- 完成技术方案设计
- 确定使用 Windows GetLastInputInfo API
- ✅ 创建 `src/peekapi/idle.py` 模块
- ✅ 在 `server.py` 添加 `/idle` 端点
- ✅ 创建 `tests/unit/test_idle.py` 测试文件
- ✅ 在 `test_server.py` 添加 `/idle` 端点测试
- ✅ 更新 README.md 添加 API 说明
- ✅ 所有测试通过（33 passed）
- 任务完成
