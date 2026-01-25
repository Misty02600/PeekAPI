# Tech Context - PeekAPI

## 技术栈

### 编程语言
- **Python** >= 3.11, < 3.14

### 核心依赖

| 库 | 版本 | 用途 |
|----|------|------|
| flask | ^3.1.0 | HTTP API 服务器 |
| pillow | ^11.1.0 | 图像处理（模糊、格式转换）|
| mss | ^10.0.0 | 跨平台屏幕截图 |
| pystray | ^0.19.5 | 系统托盘图标 |
| winotify | ^1.1.0 | Windows 通知 |
| soundcard | ^0.4.3 | 音频录制（Loopback）|
| wave | ^0.0.2 | WAV 文件生成 |
| numpy | ^2.0.0 | 音频数据处理 |
| msgspec | ^0.19.0 | 配置解析（TOML）和验证 |
| loguru | ^0.7.0 | 日志系统 |

### 开发依赖

| 库 | 版本 | 用途 |
|----|------|------|
| pyinstaller | ^6.12.0 | 打包为 exe |

### 包管理
- **uv** - 快速的 Python 包管理器

## 开发环境设置

### 前置要求
1. Python >= 3.11
2. uv 包管理器

### 安装步骤
```bash
# 克隆仓库
git clone https://github.com/Misty02600/PeekAPI.git
cd PeekAPI

# 安装依赖
uv sync

# 运行
uv run peekapi
```

### 调试模式
```bash
uv run peekapi --console  # 控制台输出日志
```

## 项目结构

```
PeekAPI/
├── config.toml          # 配置文件
├── pyproject.toml       # 项目配置
├── run.py               # 入口点（用于打包）
├── logs/                # 日志目录
├── src/
│   └── peekapi/
│       ├── __init__.py
│       ├── constants.py # 路径常量
│       ├── config.py    # 配置管理（msgspec Struct）
│       ├── logging.py   # 日志配置（loguru）
│       ├── record.py    # 音频录制
│       ├── screenshot.py # 屏幕截图
│       ├── server.py    # Flask 服务
│       └── system_tray.py # 系统托盘
└── memory-bank/         # 项目记忆库
```

## 配置文件格式

```toml
[basic]
is_public = true   # 启动时默认模式
api_key = ""       # API 密钥
host = "0.0.0.0"   # 监听地址
port = 1920        # 监听端口

[screenshot]
radius_threshold = 3      # 模糊阈值
main_screen_only = false  # 仅主显示器

[record]
duration = 20  # 录音时长（秒）
gain = 20      # 音量增益
```

## 技术约束

### 平台限制
- **当前仅支持 Windows** - winotify 是 Windows 专用
- soundcard 的 Loopback 功能在不同平台实现不同

### 性能考虑
- 录音采样率：44100 Hz
- 截图格式：JPEG (quality=95)
- 环形缓冲区：固定内存占用

### 安全考虑
- API 密钥仅在低模糊度时验证
- 私密模式完全拒绝请求
- 监听 0.0.0.0 需要防火墙配置

## 构建和部署

### 打包为 exe
```bash
uv sync --group dev
uv run pyinstaller --noconsole --onefile --name peekapi --icon peekapi.ico run.py
```

### 部署要求
1. 将 `peekapi.exe` 放到目标目录
2. 在同目录创建 `config.toml`
3. 运行 exe

### 日志
- 日志文件：`logs/peekapi_YYYYMMDD.log`
- 可通过托盘菜单"打开日志"访问

## 已知问题

1. **Linux 平台不支持** - 需要替换 winotify
2. **音频设备断开** - 已实现自动重连机制
3. **多显示器截图** - DPI 缩放可能导致问题
