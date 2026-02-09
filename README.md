# **PeekAPI**

提供当前电脑屏幕截图和录音获取的本地 API，托盘一键切换公开/隐私模式和重启录音

## **API 说明**

| **端点**      | **方法**   | **功能**         | **参数**                                   | **成功返回**                                                                  | **失败返回**                                                                                                                        |
| ------------- | ---------- | ---------------- | ------------------------------------------ | ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **`/screen`** | `GET`      | 获取屏幕截图     | - `r`（高斯模糊半径）<br>- `k`（API 密钥） | - `200 OK`，返回 `image/jpeg` 截图                                            | - `401 Unauthorized`：配置了 `api_key` 且低模糊度密钥错误<br>- `403 Forbidden`：私密模式<br>- `500 Internal Server Error`：截图失败 |
| **`/record`** | `GET`      | 获取最近录音     | 无                                         | - `200 OK`，返回 `audio/wav` 录音文件                                         | - `403 Forbidden`：私密模式<br>- `500 Internal Server Error`：录音失败                                                              |
| **`/idle`**   | `GET`      | 获取用户空闲时间 | 无                                         | - `200 OK`，返回 JSON：`{"idle_seconds": 123.456, "last_input_time": "..."}`  | - `403 Forbidden`：私密模式                                                                                                         |
| **`/info`**   | `GET`      | 获取设备信息     | 无                                         | - `200 OK`，返回 JSON：`{"hostname": "PC", "cpu": "Intel...", "gpus": [...]}` | - `403 Forbidden`：私密模式                                                                                                         |
| **`/check`**  | `GET/POST` | 检查是否运行     | 无                                         | - `200 OK`                                                                    | 无                                                                                                                                  |

## **使用**

### **使用发布版本**
- 下载 [release](https://github.com/Misty02600/PeekAPI/releases) 的 PeekAPI.zip 并解压
- 根据[配置](#配置)修改 `config.toml` 文件
- 运行 `peekapi.exe`
- 若电脑无公网且在远程电脑调用API，需要搭配 frp 使用
- 日志文件存储在 `logs` 文件夹，可通过系统托盘菜单"打开日志"快速访问

### **开发环境运行**
1. 安装 Python >= 3.11 和 [uv](https://github.com/astral-sh/uv)
2. 克隆仓库并安装依赖：
   ```bash
   uv sync
   ```
3. 运行程序：
   ```bash
   uv run peekapi
   ```

### **打包**
```bash
uv sync --group dev
uv run pyinstaller peekapi.spec
```

打包后的文件在 `dist/peekapi/` 目录，包含：
- `peekapi.exe` - 主程序
- `config.toml` - 配置文件
- `peekapi.ico` - 图标（可自定义）
- `_internal/` - 依赖文件

## **配置**

**示例**

```toml
[basic]
is_public = true   # 程序启动时默认是否为公开模式
device_name = ""   # 设备名称，留空则使用系统主机名
api_key = ""       # 低模糊度下获取截图的key，留空则不需要key
host = "0.0.0.0"   # 监听IP
port = 1920        # 监听端口

[screenshot]
radius_threshold = 3      # 高斯模糊半径阈值，低于该值时调用/screen需要api_key
main_screen_only = false  # 多显示器下是否只截取主显示器

[record]
duration = 20  # 录音时长（秒）
gain = 20      # 音量增益倍数
```

**说明**

| **参数**               | **说明**                                           | **默认值**  |
| ---------------------- | -------------------------------------------------- | ----------- |
| **`is_public`**        | 程序启动时默认是否为公开模式                       | `true`      |
| **`device_name`**      | 设备名称，留空则使用系统主机名                     | `""`        |
| **`api_key`**          | 低模糊度下获取截图的密钥，留空则不需要key          | `""`        |
| **`host`**             | 监听 IP                                            | `"0.0.0.0"` |
| **`port`**             | 监听端口                                           | `1920`      |
| **`radius_threshold`** | 高斯模糊半径阈值，低于该值时获取截屏需要 `api_key` | `3`         |
| **`main_screen_only`** | 多显示器下是否只截取主显示器                       | `false`     |
| **`duration`**         | 录音时间（秒）                                     | `20`        |
| **`gain`**             | 音量增益倍数                                       | `20`        |

