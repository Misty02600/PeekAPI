# PeekAPI 开发者概览

本指南面向维护者和贡献者，概述核心模块、数据流、配置项与运行方式，帮助快速理解并扩展 PeekAPI。

## 架构与数据流
- 入口：`run.py` 启动 Flask 服务并拉起托盘、录音线程，可通过 `--console` 显示控制台。
- 配置：`src/config.py` 解析 `config.toml`，暴露全局 `config` 与 `ICON_PATH`。
- 服务：`src/server.py` 定义 `/screen`、`/record`、`/check`，负责权限校验、模糊度判断和文件返回。
- 截图：`src/screenshot.py` 使用 `mss` 捕获屏幕，`Pillow` 高斯模糊，返回 JPEG 字节流。
- 录音：`src/record.py` 基于 `soundcard` 以默认扬声器回采（loopback），环形缓冲最近音频，导出 WAV。
- 托盘：`src/system_tray.py` 基于 `pystray`/`winotify`，切换公开/私密模式、重启录音、退出应用。

## 目录结构（关键文件）
- `run.py`：程序入口，处理 `--console`，启动应用。
- `src/config.py`：配置读取与默认值；冻结态从可执行目录读取 `config.toml`。
- `src/server.py`：Flask 应用与路由、通知、线程启动。
- `src/screenshot.py`：屏幕抓取与模糊处理。
- `src/record.py`：音频采集、增益、WAV 导出。
- `src/system_tray.py`：托盘菜单与通知。
- `config.toml`：运行时配置（见下）。

## API 端点
- `/screen` (GET)
  - 参数：`r` 高斯模糊半径；`k` 低模糊密钥。
  - 权限：当 `r < radius_threshold` 且 `k != api_key` → 401；`is_public` 为 false → 403。
  - 成功：`200`，`image/jpeg`。
- `/record` (GET)
  - 返回最近 `duration` 秒音频的 WAV；私密模式 403，采集异常 500。
- `/check` (GET/POST)
  - 健康检查，返回 200。
- `/favicon.ico`
  - 返回托盘图标；缺失时 204。

## 配置项（config.toml）
```toml
[basic]
is_public = true    # 启动默认是否公开模式
api_key = "Imkei"   # 低模糊截图密钥
host = "0.0.0.0"    # 监听 IP
port = 1920         # 监听端口

[screenshot]
radius_threshold = 3     # 低于该值需要 api_key
main_screen_only = false # true 时仅截主显示器

[record]
duration = 20  # 环形缓冲秒数
gain = 20      # 线性增益倍数
```
- 未找到配置文件时会创建空文件并使用默认值。
- 冻结（PyInstaller）后从可执行目录读取配置与图标。

## 运行与调试
1. Python 版本：>= 3.11。
2. 安装依赖：`pip install -e .` 或 `pip install -r <poetry 导出文件>`。
3. 启动：`python run.py`；如需控制台输出，使用 `python run.py --console`。
4. 访问：`http://<host>:<port>/screen`、`/record`、`/check`。
5. 托盘：提供公开/私密切换、录音重启、退出；切换会直接修改内存中的 `config.is_public`。

## 平台与依赖注意事项
- 主要面向 Windows（使用 `winotify`、`pystray` Windows 托盘、`soundcard` loopback）。
- 关键依赖：Flask、mss、Pillow、soundcard、pystray、winotify、numpy、wave（stdlib）。
- 录音依赖默认扬声器 loopback，若环境无回采通道需调整 `soundcard` 设备。

## 观察到的行为与改进线索
- 错误处理：路由返回中文文本；`server.start_app` 仅日志记录异常，必要时可增加告警或退出码。
- 安全性：低模糊截图依赖 `api_key`，高模糊允许匿名；可考虑限流或更细粒度权限。
- 日志：默认 `INFO`，如需排查可提升 `record.py` 的日志级别或追加文件日志。
- 打包：`pyproject.toml` 已包含 `pyinstaller` dev 依赖，可按需生成单文件可执行。
