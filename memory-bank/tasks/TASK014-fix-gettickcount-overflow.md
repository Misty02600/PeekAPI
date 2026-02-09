# [TASK014] - 修复 GetTickCount 溢出问题

**Status:** Pending
**Added:** 2026-02-10
**Updated:** 2026-02-10
**Priority:** High

## Original Request

`GetTickCount` 默认 `restype` 是有符号 `c_int`，在系统运行超过约 24.9 天后会变成负数，或在 49.7 天左右发生回绕，导致 `idle_seconds` 计算错误甚至为负数。

## 问题分析

### 当前代码

```python
# idle.py 第 38-40 行
current_tick = ctypes.windll.kernel32.GetTickCount()
idle_ms = current_tick - lii.dwTime
idle_seconds = idle_ms / 1000.0
```

### 问题

1. `ctypes.windll.kernel32.GetTickCount()` 默认返回类型是 `c_int`（有符号 32 位）
2. `GetTickCount` 实际返回 `DWORD`（无符号 32 位），范围 0 ~ 4,294,967,295
3. 当值超过 2,147,483,647（约 24.9 天）时，Python 会将其解释为负数
4. 49.7 天后发生回绕（wrap around），导致计算错误

### 影响

- 系统运行超过 ~25 天后，`idle_seconds` 可能变为负数
- 用户操作时间显示错误
- 多主机选择功能（nonebot-plugin-peek TASK003）依赖此端点，会导致选择错误主机

## Implementation Plan

### 方案 A：使用 GetTickCount64（推荐）

```python
def get_idle_info() -> tuple[float, datetime]:
    lii = LASTINPUTINFO()
    lii.cbSize = sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))

    # 使用 GetTickCount64 避免溢出（返回 64 位无符号整数）
    GetTickCount64 = ctypes.windll.kernel32.GetTickCount64
    GetTickCount64.restype = ctypes.c_uint64
    current_tick = GetTickCount64()

    # dwTime 仍是 32 位，需处理回绕
    # 计算差值时考虑 dwTime 可能比 current_tick 的低 32 位大（回绕情况）
    current_tick_32 = current_tick & 0xFFFFFFFF
    if current_tick_32 >= lii.dwTime:
        idle_ms = current_tick_32 - lii.dwTime
    else:
        # 回绕：dwTime 在 current_tick 回绕之前设置
        idle_ms = (0xFFFFFFFF - lii.dwTime) + current_tick_32 + 1

    idle_seconds = idle_ms / 1000.0
    last_input_time = datetime.now(_BEIJING_TZ) - timedelta(seconds=idle_seconds)

    return idle_seconds, last_input_time
```

### 方案 B：设置 restype 并处理回绕

```python
def get_idle_info() -> tuple[float, datetime]:
    lii = LASTINPUTINFO()
    lii.cbSize = sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))

    # 设置正确的返回类型
    GetTickCount = ctypes.windll.kernel32.GetTickCount
    GetTickCount.restype = ctypes.c_uint  # 无符号 32 位
    current_tick = GetTickCount()

    # 处理 32 位回绕
    if current_tick >= lii.dwTime:
        idle_ms = current_tick - lii.dwTime
    else:
        idle_ms = (0xFFFFFFFF - lii.dwTime) + current_tick + 1

    idle_seconds = idle_ms / 1000.0
    last_input_time = datetime.now(_BEIJING_TZ) - timedelta(seconds=idle_seconds)

    return idle_seconds, last_input_time
```

### 推荐方案

采用 **方案 A**，使用 `GetTickCount64`：
- Windows Vista+ 都支持
- 代码更清晰
- 避免 49.7 天回绕问题

## Progress Tracking

**Overall Status:** Not Started - 0%

### Subtasks

| ID  | Description                      | Status      | Updated    | Notes             |
| --- | -------------------------------- | ----------- | ---------- | ----------------- |
| 1   | 修改 idle.py 使用 GetTickCount64 | Not Started | 2026-02-10 |                   |
| 2   | 添加 32 位回绕处理               | Not Started | 2026-02-10 | dwTime 仍是 32 位 |
| 3   | 添加单元测试覆盖边界情况         | Not Started | 2026-02-10 |                   |
| 4   | 更新文档                         | Not Started | 2026-02-10 |                   |

## Progress Log

### 2026-02-10
- 创建任务
- 分析问题根因
- 设计修复方案
