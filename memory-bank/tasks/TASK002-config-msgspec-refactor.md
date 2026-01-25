# [TASK002] - 重构 Config 模块使用 msgspec

**Status:** Completed
**Added:** 2026-01-25
**Updated:** 2026-01-25
**Priority:** Medium

## Original Request

重构当前项目 config 模块，从 Pydantic 迁移到更轻量的 msgspec。

**补充需求：**
1. 直接导入 Struct 使用（`from msgspec import Struct`）
2. 优化大量 property 的写法
3. 将图标路径和配置路径作为常量，放入 constants 模块

## Thought Process

### 当前实现分析

当前 [config.py](../../src/peekapi/config.py) 使用 Pydantic BaseModel：

```python
from pydantic import BaseModel

class BasicConfig(BaseModel):
    is_public: bool = True
    api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 1920

class Config(BaseModel):
    basic: BasicConfig = BasicConfig()
    screenshot: ScreenshotConfig = ScreenshotConfig()
    record: RecordConfig = RecordConfig()
```

**当前问题：大量重复的 property**
```python
@property
def api_key(self) -> str:
    return self.basic.api_key

@property
def host(self) -> str:
    return self.basic.host

# ... 还有很多类似的
```

### 为什么迁移到 msgspec

| 方面 | Pydantic | msgspec |
|------|----------|---------|
| 性能 | 较慢 | 快 10-50 倍 |
| 包大小 | ~2MB | ~200KB |
| 启动时间 | 较长 | 极短 |
| 依赖 | 多 | 无依赖 |
| TOML 支持 | 需 tomllib | 内置 `msgspec.toml` |

msgspec 优势：
- 更快的序列化/反序列化
- 更小的打包体积（对 exe 打包有利）
- 内置 TOML 解码支持
- 类型验证同样严格

---

## msgspec 文档调研

### Struct 基础特性

**1. 默认可变（Mutable by Default）**

msgspec Struct **默认是可变的**，可以直接修改属性：

```python
from msgspec import Struct

class Point(Struct):
    x: float
    y: float

p = Point(1.0, 2.0)
p.x = 3.0  # ✅ 默认可变，可以直接修改
```

只有设置 `frozen=True` 才会变成不可变：

```python
class Point(Struct, frozen=True):
    x: float
    y: float

p = Point(1.0, 2.0)
p.x = 3.0  # ❌ AttributeError: immutable type: 'Point'
```

**结论：** `is_public` 的运行时修改无需特殊处理，Struct 默认就支持。

### 默认值设置

**2. 三种默认值方式**

```python
from msgspec import Struct, field

class Example(Struct):
    # 1. 静态默认值 - 直接赋值
    a: int = 1

    # 2. 动态默认值 - 使用 field(default_factory=...)
    b: uuid.UUID = field(default_factory=uuid.uuid4)

    # 3. 空可变集合的语法糖 - [], {}, set(), bytearray()
    c: list[int] = []  # 等同于 field(default_factory=list)
```

**注意：** 非空可变集合（如 `[1, 2, 3]`）不能直接作为默认值，需要用 `default_factory`。

### TOML 解码

**3. msgspec.toml 用法**

```python
from msgspec import Struct
from msgspec import toml as msgspec_toml

class Config(Struct):
    host: str = "0.0.0.0"
    port: int = 1920

# 解码 TOML 到指定类型
content = b'host = "127.0.0.1"\nport = 8080'
cfg = msgspec_toml.decode(content, type=Config)
# Config(host='127.0.0.1', port=8080)

# 缺失字段使用默认值
cfg = msgspec_toml.decode(b'', type=Config)
# Config(host='0.0.0.0', port=1920)
```

**TOML 限制：**
- TOML 不支持 `null` 值，不能序列化 `None`
- 解码时缺失字段会使用默认值

### 嵌套 Struct

**4. 嵌套结构自动解析**

```python
class BasicConfig(Struct):
    host: str = "0.0.0.0"
    port: int = 1920

class Config(Struct):
    basic: BasicConfig = BasicConfig()

# 自动解析嵌套结构
content = b'[basic]\nhost = "127.0.0.1"'
cfg = msgspec_toml.decode(content, type=Config)
# Config(basic=BasicConfig(host='127.0.0.1', port=1920))
```

### Struct 配置选项

**5. 常用配置选项**

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `frozen` | `False` | 是否不可变 |
| `kw_only` | `False` | 所有字段是否仅限关键字参数 |
| `omit_defaults` | `False` | 编码时是否省略默认值 |
| `forbid_unknown_fields` | `False` | 是否禁止未知字段 |
| `rename` | `None` | 字段重命名策略 |
| `array_like` | `False` | 是否编码为数组而非对象 |
| `gc` | `True` | 是否参与垃圾回收 |

### `__getattr__` 兼容性

**6. 自定义方法**

msgspec Struct 支持添加自定义方法，包括 `__getattr__`：

```python
class Config(Struct):
    basic: BasicConfig
    screenshot: ScreenshotConfig

    def __getattr__(self, name: str):
        for sub in (self.basic, self.screenshot):
            try:
                return getattr(sub, name)
            except AttributeError:
                continue
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
```

**注意：** `__getattr__` 只在正常属性查找失败后调用，不会影响已定义的字段。

---

## 具体实现方案

### 迁移要点

1. **直接导入 Struct**
   ```python
   from msgspec import Struct
   from msgspec import toml as msgspec_toml

   class BasicConfig(Struct):
       is_public: bool = True
   ```

2. **TOML 解析**
   ```python
   def load(cls) -> "Config":
       if not CONFIG_PATH.exists():
           return cls()
       content = CONFIG_PATH.read_bytes()
       if not content:
           return cls()
       return msgspec_toml.decode(content, type=cls)
   ```

3. **属性访问** - Struct 默认可变，`is_public` 可以直接修改，无需特殊处理

### Property 优化方案

**方案 A：移除 property，直接访问嵌套属性**
```python
# 调用方改为
config.basic.api_key
config.screenshot.radius_threshold
```
- ✅ 最简洁，无冗余代码
- ❌ 需要修改所有调用点

**方案 B：使用 `__getattr__` 动态代理**
```python
class Config(Struct):
    basic: BasicConfig
    screenshot: ScreenshotConfig
    record: RecordConfig

    def __getattr__(self, name: str):
        for sub in (self.basic, self.screenshot, self.record):
            try:
                return getattr(sub, name)
            except AttributeError:
                continue
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")
```
- ✅ 保持 `config.api_key` 的调用方式
- ✅ 无需手写每个 property
- ⚠️ IDE 自动补全可能受影响

**方案 C：混合方案**
- 常用属性保留 property
- 不常用的通过嵌套访问
- 运行时状态（`is_public`）单独管理

**采用：方案 A** - 移除所有 property，直接访问嵌套属性，代码最简洁

### Constants 模块设计

创建 `src/peekapi/constants.py`：

```python
import sys
from pathlib import Path

def _get_base_dir() -> Path:
    """获取基础目录：打包后为 exe 目录，开发时为项目根目录"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent.parent

def _get_icon_path() -> Path:
    """获取图标路径

    打包后：从 PyInstaller 临时目录 (_MEIPASS) 获取
    开发时：从项目根目录获取
    """
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "peekapi.ico"
    return _get_base_dir() / "peekapi.ico"

# 常量
BASE_DIR = _get_base_dir()
CONFIG_PATH = BASE_DIR / "config.toml"
ICON_PATH = _get_icon_path()
LOG_DIR = BASE_DIR / "logs"
```

### 最终 config.py 示例

```python
from msgspec import Struct
from msgspec import toml as msgspec_toml

from .constants import CONFIG_PATH


class BasicConfig(Struct):
    """基础配置"""
    is_public: bool = True
    api_key: str = ""
    host: str = "0.0.0.0"
    port: int = 1920


class ScreenshotConfig(Struct):
    """截图配置"""
    radius_threshold: int = 3
    main_screen_only: bool = False


class RecordConfig(Struct):
    """录音配置"""
    duration: int = 20
    gain: float = 20.0


class Config(Struct):
    """主配置类

    采用方案 A：直接访问嵌套属性
    - config.basic.is_public
    - config.basic.api_key
    - config.screenshot.radius_threshold
    - config.record.duration
    """
    basic: BasicConfig = BasicConfig()
    screenshot: ScreenshotConfig = ScreenshotConfig()
    record: RecordConfig = RecordConfig()

    @classmethod
    def load(cls) -> "Config":
        """读取并解析 config.toml 配置"""
        if not CONFIG_PATH.exists():
            CONFIG_PATH.write_text("")
            return cls()

        content = CONFIG_PATH.read_bytes()
        if not content:
            return cls()

        return msgspec_toml.decode(content, type=cls)


config = Config.load()
```

### 调用点修改清单

采用方案 A 需要修改所有调用点：

| 原调用 | 新调用 |
|--------|--------|
| `config.is_public` | `config.basic.is_public` |
| `config.api_key` | `config.basic.api_key` |
| `config.host` | `config.basic.host` |
| `config.port` | `config.basic.port` |
| `config.radius_threshold` | `config.screenshot.radius_threshold` |
| `config.main_screen_only` | `config.screenshot.main_screen_only` |
| `config.duration` | `config.record.duration` |
| `config.gain` | `config.record.gain` |

---

## Implementation Plan

- [ ] 1.1 创建 constants.py 模块（路径常量）
- [ ] 1.2 添加 msgspec 依赖，移除 pydantic
- [ ] 1.3 重写配置类为 msgspec Struct（直接导入，移除所有 property）
- [ ] 1.4 使用 msgspec.toml 解析配置文件
- [ ] 1.5 更新所有调用点（方案 A：直接访问嵌套属性）
- [ ] 1.6 更新其他模块的导入（ICON_PATH 等）
- [ ] 1.7 测试配置加载和默认值
- [ ] 1.8 更新记忆库文档

## Progress Tracking

**Overall Status:** Completed - 100%

### Subtasks

| ID | Description | Status | Updated | Notes |
|----|-------------|--------|---------|-------|
| 1.1 | 创建 constants.py | Complete | 2026-01-25 | BASE_DIR, CONFIG_PATH, ICON_PATH, LOG_DIR |
| 1.2 | 更新依赖 | Complete | 2026-01-25 | +msgspec, -pydantic via uv |
| 1.3 | 重写配置类 | Complete | 2026-01-25 | 嵌套 Struct 需 frozen=True 作为默认值 |
| 1.4 | 使用 msgspec.toml | Complete | 2026-01-25 | 替换 tomllib |
| 1.5 | 更新调用点 | Complete | 2026-01-25 | server.py, system_tray.py, record.py |
| 1.6 | 更新导入 | Complete | 2026-01-25 | ICON_PATH, LOG_DIR 从 constants 导入 |
| 1.7 | 测试 | Complete | 2026-01-25 | 所有模块导入成功 |
| 1.8 | 更新文档 | Complete | 2026-01-25 | techContext.md, progress.md |

## Progress Log

### 2026-01-25
- 创建任务记录
- 分析当前 Pydantic 实现
- 对比 msgspec 优势
- 制定迁移计划
- 补充：直接导入 Struct、property 优化方案、constants 模块设计
- **修正**：Struct 默认可变，无需 frozen=False
- 补充 msgspec 文档调研，包含完整实现细节
- **决策**：采用方案 A（移除 property，直接访问嵌套属性）
- **修正**：`_get_icon_path()` 开发环境应使用 `_get_base_dir()` 而非 `Path()`
- 添加调用点修改清单

### 2026-01-25 实施
- 创建 constants.py 模块
- 使用 uv 更新依赖：`uv remove pydantic; uv add msgspec`
- 重写 config.py 为 msgspec Struct
- **发现问题**：嵌套 Struct 作为默认值需要设置 `frozen=True`
- 修复：BasicConfig, ScreenshotConfig, RecordConfig 添加 `frozen=True`
- 更新 server.py 调用点和导入
- 更新 system_tray.py 调用点和导入
- 更新 record.py 调用点
- 测试所有模块导入成功
- 更新 techContext.md 和 progress.md

## References

- [msgspec 文档](https://jcristharif.com/msgspec/)
- [msgspec Structs](https://jcristharif.com/msgspec/structs.html)
- [msgspec Supported Types](https://jcristharif.com/msgspec/supported-types.html)
- 当前实现: [src/peekapi/config.py](../../src/peekapi/config.py)
