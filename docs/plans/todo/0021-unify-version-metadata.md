# PLAN-0021：统一项目、HTTP 与 Windows 产物的版本元数据

## 状态

进行中

## 最后更新

2026-08-02

## 目标和成功标准

以 uv 管理的项目发行版元数据作为唯一版本来源，让 Commitizen、`peekapi.__version__`、FastAPI OpenAPI、
PyInstaller Windows 文件属性、标签校验和 `uv.lock` 保持一致，删除需要手工同步的版本常量与
`version_info.txt`。

完成时源码和打包环境都能取得同一版本，Windows exe 属性正确，版本 bump 不再通过 amend 和强制移动标签
补救不同步；测试、静态检查和实际构建通过，并有文档、用户确认和成功提交。

## 当前方案

- Commitizen 改用 `version_provider = "uv"`，让版本读写交给项目元数据与 uv lock。
- `peekapi.__version__` 使用 `importlib.metadata.version("peekapi")`，FastAPI 应用直接复用该值。
- `peekapi.spec` 从已安装发行版读取版本，动态构造四段 Windows `VSVersionInfo`，并复制发行版 metadata。
- 删除固定写死 `1.0.0.0` 的 `version_info.txt`；`just bump` 不再额外执行 lock、amend 或强制移动标签。

## 现在做到哪里

- `pyproject.toml`、`justfile`、`src/peekapi/__init__.py`、`server.py`、`peekapi.spec` 已在工作区修改。
- `version_info.txt` 已删除，新增包版本来源测试和 FastAPI 版本一致性测试。
- 尚未完成全量测试、Ruff/BasedPyright、Windows PyInstaller 构建、exe 属性检查和用户确认。

## 涉及文件

- `pyproject.toml`、`uv.lock`、`justfile`
- `src/peekapi/__init__.py`、`src/peekapi/server.py`
- `peekapi.spec`、`version_info.txt`
- `tests/unit/test_version.py`、`tests/unit/test_server.py`
- release flow、ADR-0003 与相关完成计划

## 接下来要做

1. 验证源码树、uv editable install 和打包分析阶段都能读取发行版 metadata。
2. 覆盖正常语义版本、预发布版本和不足四段版本到 Windows `filevers` 的转换。
3. 执行全量测试、格式、Ruff 和 BasedPyright，确认 `uv.lock` 与项目版本一致。
4. 在 Windows 执行 `just build`，检查 exe 文件属性、FastAPI OpenAPI 版本和 ZIP 中的 metadata/config。
5. 根据最终行为更新 release flow 与 ADR-0003 的落实链接，等待用户确认和提交。

## 还需要决定什么

- 在未安装发行版 metadata 的直接源码导入场景中，是明确失败还是提供开发态 fallback。
- `peekapi.spec` 是否必须复制完整发行版 metadata，还是仅动态版本值已经足够。
- 预发布、本地版本和超过四段 release tuple 如何映射到 Windows 四段数字版本。
- action/release 标签策略是否与本计划一起调整；当前应避免与 PLAN-0019 混合范围。

## 阻碍

- Windows exe 文件属性与 onefolder 内容只能通过实际 PyInstaller 构建确认。
- 工作区同时包含 PLAN-0017 的录音生命周期改动和 docs 迁移，提交前需要保持审查范围可辨认。

## 怎么验证

- `uv run pytest tests/unit/test_version.py tests/unit/test_server.py`
- `just test`、`just lint`、`just check`
- `just build` 后检查 `dist/peekapi/peekapi.exe` 的 FileVersion/ProductVersion、启动后的 OpenAPI 版本及配置文件。
- 执行一次不发布的 Commitizen dry run 或等价版本读取检查，确认不会创建或强制移动标签。

## 审批与提交

- 用户确认：未确认
- Git 提交：未提交

## 进展记录

### 2026-08-02

- 根据当前工作区补建计划，记录已经存在的版本来源、spec、测试和 bump 流程改动。
- 明确剩余验证、预发布映射和与 PLAN-0019 的范围边界。

## 相关文档

- [Release Flow](../../architecture/flows/release.md)
- [ADR-0003](../../adr/0003-use-pyinstaller-onefolder.md)
- [PLAN-0005](../done/0005-optimize-packaging.md)
- [PLAN-0010](../done/0010-automate-github-release.md)
