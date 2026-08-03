# PLAN-0015: 添加设备信息端点与设备名覆盖

## 状态

已完成

## 完成时间

2026-02-10

## 最后结果和当前行为

`GET /info` 通过固定 PowerShell CIM/WMI 查询返回主机名、电脑型号、主板、CPU 和显卡列表；`device_name` 可覆盖响应主机名，命令失败时降级为 Unknown/空列表并记录 warning。

## 怎么验证的

`tests/unit/test_system_info.py` 和服务器测试覆盖单/多设备、超时、JSON 失败、配置覆盖和私密模式。

## 审批与提交

- Git 提交：`0df4ce1`
- 审批记录：历史任务已合入主线；迁移来源未保留独立审批文本。

## 文档同步到哪里

[项目总览](../../architecture/overview.md)。

## 已知缺口和后续事项

每次请求串行执行多个 PowerShell 命令，最坏延迟较高；跨平台事项见 [PLAN-0001](../todo/0001-linux-support.md)。

## 相关文档

- [`system_info.py`](../../../src/peekapi/system_info.py)
