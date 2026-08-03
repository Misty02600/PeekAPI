# Flow: 截图请求

## 这条流程保证什么

在隐私和 API key 规则允许的前提下，对请求时的主显示器或虚拟桌面进行截图，可选高斯模糊后返回 JPEG。

## 外部参与者和触发条件

客户端发送 `GET /screen?r=<radius>&k=<api-key>`；FastAPI、运行时配置、mss 与 Pillow 参与处理。

## 稳定的状态变化

1. FastAPI 解析 `r`，服务拒绝 NaN/Inf 等非有限值。
2. 私密模式直接拒绝请求。
3. 当 `r` 低于配置阈值且 API key 非空时，校验 `k`。
4. mss 截取主显示器或全部显示器组成的虚拟屏幕。
5. `r > 0` 时应用高斯模糊，再以 quality 95 编码 JPEG。
6. 请求不修改持久状态，图像只在本次处理期间存在。

## 失败时的语义

- 非有限半径或低模糊截图密钥错误返回 401。
- 私密模式返回 403；截图函数返回空数据时返回 500。
- 未处理的 mss/Pillow 异常按服务器错误处理。
- 响应不含前台应用显示信息；该状态通过独立的
  [`/foreground` 流程](foreground-application.md) 查询，不改变本流程。

## 相关实现

- [`server.py`](../../../src/peekapi/server.py)
- [`screenshot.py`](../../../src/peekapi/screenshot.py)
