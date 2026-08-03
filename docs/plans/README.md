# Plans

`todo/` 保存已经进入主动规划但尚未完成的计划；`done/` 只保存已经确认并有成功提交证据的结果。只有构想
但还没有开始核查和技术路线讨论的内容留在本地 `docs/scratch/`，不分配 PLAN 编号。

## 讨论中

| Plan | 目标 |
|---|---|
| [PLAN-0001](todo/0001-linux-support.md) | 评估并实现 Linux 支持 |
| [PLAN-0016](todo/0016-validate-sleep-crash.md) | 核验 Windows 长时间休眠恢复 |
| [PLAN-0018](todo/0018-report-recorder-health.md) | 让录音 API 表达设备健康状态 |
| [PLAN-0019](todo/0019-upgrade-release-action.md) | 升级 GitHub Release action |

## 进行中

| Plan | 目标 |
|---|---|
| [PLAN-0017](todo/0017-fix-recorder-lifecycle-races.md) | 修复录音启停与电源恢复竞态 |
| [PLAN-0020](todo/0020-add-foreground-application-endpoint.md) | 新增前台应用查询端点 |
| [PLAN-0021](todo/0021-unify-version-metadata.md) | 统一项目、HTTP 与 Windows 产物的版本元数据 |

## 已完成

| Plan | 结果 |
|---|---|
| [PLAN-0002](done/0002-config-msgspec-refactor.md) | msgspec 配置重构 |
| [PLAN-0003](done/0003-loguru-logging.md) | 统一 loguru 日志 |
| [PLAN-0004](done/0004-add-tests.md) | 建立测试体系 |
| [PLAN-0005](done/0005-optimize-packaging.md) | 优化 PyInstaller 打包 |
| [PLAN-0006](done/0006-use-soundfile.md) | 使用 soundfile 生成 WAV |
| [PLAN-0007](done/0007-migrate-fastapi.md) | Flask 迁移到 FastAPI |
| [PLAN-0008](done/0008-remove-parse-helpers.md) | 移除手动参数解析 |
| [PLAN-0009](done/0009-optimize-recorder-api.md) | 优化录音类接口 |
| [PLAN-0010](done/0010-automate-github-release.md) | 自动发布 Windows ZIP |
| [PLAN-0011](done/0011-fix-ci-quality-checks.md) | 修复 CI 质量检查 |
| [PLAN-0012](done/0012-fix-tray-startup.md) | 修复无控制台托盘启动 |
| [PLAN-0013](done/0013-add-idle-endpoint.md) | 添加空闲时间端点 |
| [PLAN-0014](done/0014-fix-idle-tick-overflow.md) | 修复 tick 回绕 |
| [PLAN-0015](done/0015-add-system-info-endpoint.md) | 添加设备信息端点 |

## 生命周期

1. 只有构想时写入被 Git ignore 的 `docs/scratch/`，不创建 PLAN。
2. 开始核查代码和技术路线后，在 `todo/` 创建状态为 `讨论中` 的计划，记录事实、路线、取舍、成功标准、
   验证思路和是否确认实施。
3. 用户确认进入实施且实际工作开始后，仍留在 `todo/` 并改为 `进行中`，持续记录当前方案、下一步、阻塞、
   验证、审批和提交状态。
4. 实现与文档完成后先验证并请用户确认。只有获批改动成功提交后才能移入 `done/`。
5. done 文档只保留最终行为、验证、审批/提交、文档同步位置和仍存在的缺口。
