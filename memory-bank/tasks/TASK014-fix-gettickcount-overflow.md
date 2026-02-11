# [TASK014] - 修复 GetTickCount 溢出问题

**Status:** Completed
**Added:** 2026-02-10
**Updated:** 2026-02-10
**Priority:** High

## Original Request

`GetTickCount` 默认 `restype` 是有符号 `c_int`，在系统运行超过约 24.9 天后会变成负数，或在 49.7 天左右发生回绕，导致 `idle_seconds` 计算错误甚至为负数。

## 问题分析

### 当前代码（修复前）

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

### 采用方案 A：使用 GetTickCount64

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

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks

| ID  | Description                      | Status   | Updated    | Notes                 |
| --- | -------------------------------- | -------- | ---------- | --------------------- |
| 1   | 修改 idle.py 使用 GetTickCount64 | Complete | 2026-02-10 | 使用 c_uint64         |
| 2   | 添加 32 位回绕处理               | Complete | 2026-02-10 | dwTime 仍是 32 位     |
| 3   | 添加单元测试覆盖边界情况         | Complete | 2026-02-10 | 增加 2 个回绕测试用例 |
| 4   | 更新文档                         | Complete | 2026-02-10 | 任务文档已更新        |

## Progress Log

### 2026-02-10
- 创建任务
- 分析问题根因
- 设计修复方案
- 实现 GetTickCount64 修复（方案 A）
- 添加 32 位回绕边界测试用例
  - `test_get_idle_info_handles_32bit_wraparound` - 测试回绕情况
  - `test_get_idle_info_large_tick_count` - 测试接近上限值
- 所有 7 个 idle 测试通过
- 任务完成
