# TASK015 - 添加设备信息端点与主机名配置

**Status:** Completed
**Added:** 2026-02-09
**Updated:** 2026-02-10

## Original Request
用户希望通过 API 获取设备硬件信息（主机名、型号、主板、CPU、显卡），并希望在配置文件中添加一个选项，如果设置了该选项，API 返回的主机名将使用配置值替代系统真实主机名。

## Thought Process
用户需要了解运行服务的宿主机硬件情况，用于多设备管理或展示。
考虑到跨平台兼容性和轻量化，决定使用 PowerShell 命令获取 Windows WMI 信息，无需额外依赖。
配置项 `device_name` 添加到 `[basic]` 节中，留空则使用系统主机名。

## Implementation Plan
- [x] Update `README.md` to document the new `/info` endpoint and `device_name` config.
- [x] Create `src/peekapi/system_info.py` to handle PowerShell commands and parsing.
- [x] Update `src/peekapi/config.py` to include `device_name` field.
- [x] Add `/info` route in `src/peekapi/server.py`.
- [x] Add unit tests for system info retrieval and config override.

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks
| ID  | Description            | Status   | Updated    | Notes                          |
| --- | ---------------------- | -------- | ---------- | ------------------------------ |
| 1   | Update Documentation   | Complete | 2026-02-10 | README, TASK 文件              |
| 2   | Implement System Info  | Complete | 2026-02-10 | system_info.py 使用 PowerShell |
| 3   | Implement Config Logic | Complete | 2026-02-10 | device_name 字段               |
| 4   | Add API Endpoint       | Complete | 2026-02-10 | /info 路由                     |
| 5   | Add Unit Tests         | Complete | 2026-02-10 | 13 测试通过                    |

## Progress Log
### 2026-02-10
- Implemented `system_info.py` module with PowerShell WMI queries
- Added `device_name` config option to `BasicConfig`
- Added `/info` endpoint to `server.py`
- Created comprehensive unit tests (13 tests)
- Fixed existing mock test for `test_idle.py` (GetTickCount64 compatibility)
- All 106 tests pass
- ruff and basedpyright checks pass
