# **PeekAPI**

提供当前电脑屏幕截图和录音获取的本地 API

## **API 说明**

| **端点** | **方法** | **功能** | **参数** | **成功返回** | **失败返回** |
| ---- | ---- | ---- | ---- | ---- | ---- |
| /screen | GET | 获取屏幕截图 | r（截图半径，可选），k（API 密钥，可选） | 200 OK，返回 image/jpeg 截图 | 401 Unauthorized：低模糊度密钥错误 403 Forbidden：私密模式 500 Internal Server Error：截图失败 |
| /record | GET | 获取最近录音 | 无 | 200 OK，返回 audio/wav 录音文件 | 403 Forbidden私密模式、500 Internal Server Error录音失败 |
| /check | GET/POST | 服务器健康检查 | 无 | 200 OK | 无 |

## **配置**

PeekAPI 通过 `config.toml` 进行配置：

```toml
[basic]
is_public = true
api_key = "Imkei"
host = "0.0.0.0"
port = 1920

[screenshot]
radius_threshold = 3
main_screen_only = false

[record]
duration = 20
gain = 20
```

**配置说明**

| **参数** | **说明** | **默认值** |
| ---- | ---- | ---- |
| is_public | 是否允许公开访问 API | true |
| api_key | 访问 API 所需的密钥 | "Imkei" |
| host | 监听 IP | "127.0.0.1" |
| port | API 监听端口 | 1920 |
| radius_threshold | 截图权限半径阈值，低于该值需要 api_key | 3 |
| main_screen_only | 是否仅截取主屏幕 | false |
| duration | 录音时间（秒） | 20 |
| gain | 录音增益大小 | 20 |

## **许可证**

本项目采用 MIT 许可证，详情请见 `LICENSE`。