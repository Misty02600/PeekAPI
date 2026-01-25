# [TASK003] - 日志系统迁移到 loguru

**Status:** Completed
**Added:** 2026-01-25
**Updated:** 2026-01-25
**Priority:** Medium

## Original Request

日志采用 loguru 库，日志放在单独的一个模块设置。

## Thought Process

### 当前实现分析

当前使用标准库 `logging`，分散在多个模块中：

**server.py:**
```python
import logging

def setup_logging(console: bool = False) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"peekapi_{datetime.now():%Y%m%d}.log"

    handlers = [logging.FileHandler(log_file, encoding='utf-8')]
    if console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=handlers
    )
```

**record.py:**
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# 使用 logger.info(), logger.warning(), logger.error()
```

### 当前问题

1. `logging.basicConfig` 在多处调用，可能互相覆盖
2. 日志配置分散，不统一
3. 标准库 logging 配置繁琐

### 为什么使用 loguru

| 方面 | logging | loguru |
|------|---------|--------|
| 配置 | 繁琐，需要 handler/formatter | 开箱即用 |
| 语法 | `logger.info()` | `logger.info()` 相同 |
| 格式化 | `%s` 或 `.format()` | f-string 风格 |
| 文件轮转 | 需配置 RotatingFileHandler | 内置 `rotation` 参数 |
| 异常追踪 | 需手动配置 | 自动美化异常堆栈 |
| 颜色输出 | 需第三方库 | 内置 |

### 目标设计

创建 `src/peekapi/logging.py` 模块：

```python
"""日志配置模块"""

import sys
from loguru import logger

from .constants import LOG_DIR


def setup_logging(console: bool = False) -> None:
    """配置日志系统

    Args:
        console: 是否同时输出到控制台
    """
    # 移除默认 handler
    logger.remove()

    # 确保日志目录存在
    LOG_DIR.mkdir(exist_ok=True)

    # 文件日志（按日期轮转）
    logger.add(
        LOG_DIR / "peekapi_{time:YYYYMMDD}.log",
        rotation="00:00",  # 每天午夜轮转
        retention="7 days",  # 保留 7 天
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} [{level}] {name}: {message}",
        level="INFO",
    )

    # 控制台输出（可选）
    if console:
        logger.add(
            sys.stderr,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>: {message}",
            level="INFO",
            colorize=True,
        )

    logger.info("PeekAPI 日志系统初始化完成")
```

### 调用点修改

各模块改为从 logging 模块导入 logger：

```python
# 之前
import logging
logger = logging.getLogger(__name__)

# 之后
from .logging import logger
```

---

## Implementation Plan

- [x] 1.1 添加 loguru 依赖
- [x] 1.2 创建 `src/peekapi/logging.py` 模块
- [x] 1.3 更新 server.py（移除 setup_logging，改用 logging 模块）
- [x] 1.4 更新 record.py（使用统一 logger）
- [x] 1.5 检查其他模块是否使用 logging
- [x] 1.6 测试日志输出
- [x] 1.7 更新记忆库文档

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks

| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | 添加 loguru 依赖 | Complete | 2026-01-25 | `uv add loguru` |
| 1.2 | 创建 logging.py 模块 | Complete | 2026-01-25 | setup_logging + logger 导出 |
| 1.3 | 更新 server.py | Complete | 2026-01-25 | 移除原 setup_logging，导入新模块 |
| 1.4 | 更新 record.py | Complete | 2026-01-25 | 替换 logging 为 loguru |
| 1.5 | 检查其他模块 | Complete | 2026-01-25 | 无其他模块使用 logging |
| 1.6 | 测试 | Complete | 2026-01-25 | 控制台彩色输出正常 |
| 1.7 | 更新文档 | Complete | 2026-01-25 | techContext.md |

## Progress Log

### 2026-01-25
- 创建任务记录
- 分析当前 logging 实现（分散在 server.py 和 record.py）
- 设计 loguru 模块结构

### 2026-01-25 实施
- 添加 loguru 依赖 (v0.7.3)
- 创建 `src/peekapi/logging.py` 模块
- 更新 server.py：移除原 setup_logging 函数，导入新 logging 模块
- 更新 record.py：移除 `import logging` 和 `logging.basicConfig`，使用统一 logger
- 检查确认无其他模块使用 logging
- 测试通过：控制台彩色输出正常
- 更新 techContext.md

## References

- [loguru 文档](https://loguru.readthedocs.io/)
- 当前实现: [logging.py](../../src/peekapi/logging.py)
