# **PeekAPI - 本地截图与录音 API 服务**

PeekAPI 提供屏幕截图和录音获取的本地 API，并支持系统托盘通知。适用于远程访问截图或录音数据的场景。

## **API 说明**

| **端点** | **方法** | **功能** | **参数** | **成功返回** | **失败返回** |
| ---- | ---- | ---- | ---- | ---- | ---- |
| /screen | GET | 获取屏幕截图 | r（截图半径，可选），k（API 密钥，可选） | 200 OK，返回 image/jpeg 截图 | 401 Unauthorized（无权限）、500 Internal Server Error（截图失败） |
| /record | GET | 获取最近录音 | 无 | 200 OK，返回 audio/wav 录音文件 | 403 Forbidden（访问受限）、500 Internal Server Error（录音获取失败） |
| /check | GET/POST | 服务器健康检查 | 无 | 200 OK | 无 |
| /favicon.ico | GET | 获取应用图标 | 无 | 200 OK，返回 .ico 图标 | 204 No Content（图标不存在） |

## **API 详细说明**

### **1. 获取屏幕截图**

```http
GET /screen?r=3&k=Imkei
```

**参数**

- r（可选）：截图半径，影响截图区域，默认 0
- k（可选）：API 访问密钥，若 r 低于 radius_threshold，则需要提供密钥
**返回**

- 成功：200 OK，返回 image/jpeg 格式的截图文件
- 失败：401 Unauthorized：截图请求未提供 API 密钥或权限不足403 Forbidden：API 未开启公共访问（is_public = false）500 Internal Server Error：截图失败
### **2. 获取录音**

```http
GET /record
```

**返回**

- 成功：200 OK，返回 audio/wav 格式的录音文件
- 失败：403 Forbidden：API 访问权限受限（is_public = false）500 Internal Server Error：录音功能异常或无法获取录音数据
### **3. 服务器健康检查**

```h
GET /check
```

或

```http
POST /check
```

**返回**

- 成功：200 OK，表示服务器正常运行
### **4. 获取应用图标**

```http
GET /favicon.ico
```

**返回**

- 成功：200 OK，返回 .ico 格式的应用图标
- 失败：204 No Content：图标不存在或无法加载
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
| host | 监听 IP | "0.0.0.0" |
| port | API 监听端口 | 1920 |
| radius_threshold | 截图权限半径阈值，低于该值需要 api_key | 3 |
| main_screen_only | 是否仅截取主屏幕 | false |
| duration | 录音时间（秒） | 20 |
| gain | 录音增益大小 | 20 |

## **许可证**

本项目采用 MIT 许可证，详情请见 `LICENSE`。