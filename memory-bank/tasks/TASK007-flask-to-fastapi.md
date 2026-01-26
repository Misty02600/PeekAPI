# TASK007 - 将 Flask 重构为 FastAPI

**Status:** Completed
**Added:** 2026-01-26
**Updated:** 2026-01-26

## Original Request

将项目的 Flask 重构为 FastAPI，提升 API 性能和现代化程度。

## Thought Process

### 为什么要迁移到 FastAPI？

1. **性能优势** - FastAPI 基于 Starlette 和 ASGI，天然支持异步处理，性能远超 Flask (WSGI)
2. **现代 Python 特性** - 支持类型提示、Pydantic 数据验证
3. **自动生成 API 文档** - 内置 Swagger UI 和 ReDoc
4. **更好的并发处理** - 异步 I/O 对截图和录音请求更高效
5. **活跃的社区** - FastAPI 是目前增长最快的 Python Web 框架

### 当前 Flask 使用分析

**文件：** `src/peekapi/server.py`

**现有路由：**

| 路由      | 方法      | 功能     |
| --------- | --------- | -------- |
| `/screen` | GET       | 截图服务 |
| `/record` | GET       | 录音服务 |
| `/check`  | GET, POST | 健康检查 |

**特点：**
- 使用 `request.remote_addr` 获取客户端 IP
- 使用 `request.args.get()` 获取查询参数
- 使用 `send_file()` 返回二进制流
- 在线程中运行 Flask 服务器

### 迁移要点

1. **依赖替换**
   - 移除：`flask`
   - 添加：`fastapi`, `uvicorn[standard]`

2. **路由迁移**
   - `@app.route()` → `@app.get()` / `@app.post()`
   - `request.args.get()` → 函数参数或 Query()
   - `send_file()` → `Response()` 或 `StreamingResponse`
   - `request.remote_addr` → `Request.client.host`

3. **服务器启动**
   - Flask `app.run()` → Uvicorn `uvicorn.run()`
   - 考虑使用 `uvicorn.Config` + `uvicorn.Server` 进行更精细控制

4. **异步考虑**
   - 截图和录音操作可保持同步（CPU 密集型）
   - FastAPI 会自动在线程池中运行同步端点

## Implementation Plan

### 1. 依赖管理

- [x] 更新 `pyproject.toml`：移除 `flask`，添加 `fastapi` 和 `uvicorn`
- [x] 运行 `uv sync` 更新依赖

### 2. 服务器重构 (`server.py`)

- [x] 导入 FastAPI 相关模块
- [x] 创建 FastAPI app 实例
- [x] 迁移 `/screen` 路由
- [x] 迁移 `/record` 路由
- [x] 迁移 `/check` 路由
- [x] 更新 `start_app()` 函数使用 Uvicorn

### 3. 响应处理

- [x] 实现 JPEG 图像响应（替代 send_file）
- [x] 实现 WAV 音频响应（替代 send_file）
- [x] 确保正确的 Content-Type 头

### 4. 日志集成

- [x] 确保 Uvicorn 日志与 loguru 集成
- [x] 保持现有日志格式

### 5. 文档更新

- [x] 更新 `techContext.md` 中的依赖表
- [x] 更新 README.md（如需要）

### 6. 测试验证

- [x] 运行现有单元测试
- [x] 手动测试所有端点
- [x] 验证 Swagger 文档 `/docs`
- [x] 检查打包流程是否正常

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks

| ID  | Description | Status   | Updated    | Notes                  |
| --- | ----------- | -------- | ---------- | ---------------------- |
| 7.1 | 更新依赖    | Complete | 2026-01-26 | fastapi + uvicorn      |
| 7.2 | 迁移路由    | Complete | 2026-01-26 | 所有路由已迁移         |
| 7.3 | 响应处理    | Complete | 2026-01-26 | Response 类正确使用    |
| 7.4 | 日志集成    | Complete | 2026-01-26 | Uvicorn log_level 设置 |
| 7.5 | 文档更新    | Complete | 2026-01-26 | -                      |
| 7.6 | 测试验证    | Complete | 2026-01-26 | 28 tests passed        |

## Progress Log

### 2026-01-26

- 确认 Flask 到 FastAPI 迁移已完成
- `server.py` 已使用 FastAPI 框架：
  - 使用 `FastAPI` 实例替代 Flask app
  - 使用 `@app.get()` / `@app.post()` 装饰器
  - 使用 `Query()` 处理查询参数
  - 使用 `Response` 返回各种媒体类型
  - 使用 `Request.client.host` 获取客户端 IP
  - 使用 `uvicorn.run()` 启动服务器
  - 添加 `lifespan` 生命周期管理
- `pyproject.toml` 依赖已更新（fastapi, uvicorn）
- 测试文件已适配 FastAPI (`TestClient`)
- 修复了 `test_favicon_file_not_found` 测试的 mock 问题
- 所有 28 个服务器测试通过

## References

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [从 Flask 迁移到 FastAPI](https://fastapi.tiangolo.com/alternatives/)
- [Uvicorn 文档](https://www.uvicorn.org/)
