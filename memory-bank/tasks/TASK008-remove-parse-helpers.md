# [TASK008] 移除手动类型校验函数

**Status:** Completed
**Added:** 2026-01-26
**Updated:** 2026-01-26

## Original Request

使用 FastAPI 后，可以不再使用自己写的 `parse_float` 等类型校验吗？

## Thought Process

### 背景分析

在 Flask 时代，请求参数都是字符串类型，需要手动解析和校验：

```python
# Flask 方式 - 需要手动处理
r = request.args.get("r")  # 返回 str | None
r_float = parse_float(r, default=0)  # 手动转换
```

FastAPI 迁移后，已经使用了 Pydantic 和 Query 参数：

```python
# FastAPI 方式 - 自动类型转换和校验
r: float = Query(default=0, description="模糊半径")
```

### 当前代码分析

**server.py 中的 `parse_float` 定义：**
```python
def parse_float(value: str | None, default: float = 0) -> float:
    try:
        return float(value) if value is not None else default
    except (TypeError, ValueError):
        return default
```

**现状：** 这个函数**没有被任何地方调用**！

FastAPI 的 Query 参数已经自动处理了：
- ✅ 类型转换 (str → float)
- ✅ 默认值 (default=0)
- ✅ 类型校验（非法值返回 422 错误）

### 结论

**可以安全移除 `parse_float` 函数。**

FastAPI 的类型系统提供了更强大的功能：
1. 自动类型转换
2. 自动参数校验
3. 自动生成 OpenAPI 文档
4. 422 Unprocessable Entity 错误响应（比静默使用默认值更规范）

## Implementation Plan

- [x] 1.1 确认 `parse_float` 函数没有被使用
- [x] 1.2 删除 `parse_float` 函数定义
- [x] 1.3 检查是否有其他类似的手动解析函数
- [x] 1.4 删除相关的单元测试
- [x] 1.5 运行测试确保代码正常

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks
| ID  | Description           | Status   | Updated    | Notes                  |
| --- | --------------------- | -------- | ---------- | ---------------------- |
| 1.1 | 确认函数未被使用      | Complete | 2026-01-26 | grep 确认无调用        |
| 1.2 | 删除 parse_float 函数 | Complete | 2026-01-26 | 已删除第 44-48 行      |
| 1.3 | 检查其他解析函数      | Complete | 2026-01-26 | 无其他解析函数         |
| 1.4 | 删除相关单元测试      | Complete | 2026-01-26 | 删除 TestParseFloat 类 |
| 1.5 | 运行测试              | Complete | 2026-01-26 | 85 测试全部通过        |

## Progress Log

### 2026-01-26
- 创建任务
- 分析了 `parse_float` 函数的定义和使用情况
- 确认该函数在 FastAPI 迁移后已成为死代码
- FastAPI 的 Query 参数自动处理了类型转换和校验

### 2026-01-26 (实施)
- 删除 `server.py` 中的 `parse_float` 函数（第 44-48 行）
- 运行测试发现 3 个测试失败（测试了已删除的函数）
- 删除 `test_server.py` 中的 `TestParseFloat` 测试类
- 再次运行测试，85 测试全部通过
- 任务完成

## 附加说明

### FastAPI 类型校验行为

当用户传入无效参数时，FastAPI 会自动返回 422 错误：

```json
GET /screen?r=abc

{
  "detail": [
    {
      "loc": ["query", "r"],
      "msg": "value is not a valid float",
      "type": "type_error.float"
    }
  ]
}
```

这比 Flask 方式的静默转换更符合 API 设计规范。
