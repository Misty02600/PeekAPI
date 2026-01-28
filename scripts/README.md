# API 测试脚本

这个目录包含用于测试运行中的 PeekAPI 服务的脚本。

**注意**: 这些脚本通过 HTTP 请求测试 API 端点，需要先启动 PeekAPI 服务！

## 目录结构

```
scripts/
├── README.md              # 本文件
├── __init__.py
├── test_all.py           # 完整 API 测试
├── test_check.py         # 健康检查端点测试
├── test_record.py        # 录音端点测试
└── test_screenshot.py    # 截图端点测试

.sandbox/                  # 测试产物目录（已被 .gitignore 忽略）
├── audio/                 # 保存录音文件
└── screenshots/           # 保存截图文件
```

## 前置条件

1. 启动 PeekAPI 服务：
   ```bash
   python -m peekapi
   # 或者运行打包后的 exe
   ```

2. 确保服务正在运行（默认端口 22334）

## 使用说明

所有脚本都应该从项目根目录运行。

### 完整测试

测试所有 API 端点：

```bash
python -m scripts.test_all

# 测试远程服务
python -m scripts.test_all --host 192.168.1.100

# 带 API 密钥测试
python -m scripts.test_all --api-key YOUR_KEY
```

### 健康检查测试

```bash
python -m scripts.test_check

# 使用 POST 方法
python -m scripts.test_check --method post

# 测试远程服务
python -m scripts.test_check --host 192.168.1.100
```

### 截图 API 测试

```bash
# 基本测试
python -m scripts.test_screenshot

# 添加模糊效果
python -m scripts.test_screenshot --blur 5

# 带 API 密钥获取高清图
python -m scripts.test_screenshot --api-key YOUR_KEY

# 保存截图到本地
python -m scripts.test_screenshot --save

# 测试远程服务
python -m scripts.test_screenshot --host 192.168.1.100
```

### 录音 API 测试

```bash
# 基本测试
python -m scripts.test_record

# 保存录音到本地
python -m scripts.test_record --save

# 测试远程服务
python -m scripts.test_record --host 192.168.1.100
```

## 公共参数

所有测试脚本支持以下公共参数：

| 参数     | 说明               | 默认值    |
| -------- | ------------------ | --------- |
| `--host` | API 服务器主机地址 | 127.0.0.1 |
| `--port` | API 服务器端口     | 22334     |

## 输出位置

当使用 `--save` 参数时，文件保存在 `.sandbox/` 目录下：

- **音频文件**: `.sandbox/audio/api_audio_YYYYMMDD_HHMMSS.wav`
- **截图文件**: `.sandbox/screenshots/api_screenshot_YYYYMMDD_HHMMSS.jpg`

`.sandbox/` 目录已被添加到 `.gitignore`，不会被提交到版本控制。

## 常见问题

### 连接失败

如果看到 "连接失败" 错误，请确保：
1. PeekAPI 服务已启动
2. 服务监听在正确的端口（默认 22334）
3. 防火墙没有阻止连接

### 权限被拒绝

- **401**: 需要 API 密钥或提高模糊半径
- **403**: 服务处于私密模式，需要通过系统托盘切换到公开模式
