# **PeekAPI**

提供当前电脑屏幕截图和录音获取的本地 API，托盘一键切换公开/隐私模式和重启录音

## **API 说明**

| **端点**    | **方法**    | **功能**      | **参数**  | **成功返回**  | **失败返回**  |
|------------|------------|--------------|-----------|--------------|--------------|
| **`/screen`** | `GET` | 获取屏幕截图 | - `r`（高斯模糊半径）<br>- `k`（API 密钥） | - `200 OK`，返回 `image/jpeg` 截图 | - `401 Unauthorized`：低模糊度密钥错误<br>- `403 Forbidden`：私密模式<br>- `500 Internal Server Error`：截图失败 |
| **`/record`** | `GET` | 获取最近录音 | 无 | - `200 OK`，返回 `audio/wav` 录音文件 | - `403 Forbidden`：私密模式<br>- `500 Internal Server Error`：录音失败 |
| **`/check`** | `GET/POST` | 检查是否运行 | 无 | - `200 OK` | 无 |

## **使用**

- 下载 [release](https://github.com/Misty02600/PeekAPI/releases) 的 PeekAPI.exe，在同级目录创建 `config.toml` 文件，根据[配置](#配置)写入内容，运行程序。
- 若电脑无公网且在远程电脑调用API，需要搭配 frp 使用。
- 可以使用 `PeekAPI.exe --console` 运行以显示控制台输出。

## **配置**

**示例**

```toml
[basic]
is_public = true   # 程序启动时默认是否为公开模式
api_key = "Imkei"  # 低模糊度下获取截图的key
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

| **参数**            | **说明**                                      | **默认值**       |
|--------------------|------------------------------------------|---------------|
| **`is_public`**    | 程序启动时默认是否为公开模式               | `true`        |
| **`api_key`**      | 低模糊度下获取截图的密钥                    | `"Imkei"`     |
| **`host`**         | 监听 IP                                    | `"127.0.0.1"` |
| **`port`**         | 监听端口                                  | `1920`        |
| **`radius_threshold`** | 高斯模糊半径阈值，低于该值时获取截屏需要 `api_key` | `3`           |
| **`main_screen_only`** | 多显示器下是否只截取主显示器               | `false`       |
| **`duration`**     | 录音时间（秒）                            | `20`          |
| **`gain`**        | 音量增益倍数                              | `20`          |


## **许可证**

本项目采用 MIT 许可证。

## **鸣谢**

参考了 [ChieriBot peek API](https://github.com/chinosk6/ChieriBot_peek_API) 的代码
