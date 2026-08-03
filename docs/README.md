# 项目知识

这里保存 PeekAPI 可随代码提交、长期维护的项目知识。旧 `memory-bank/` 已停用，不再并行维护第二套事实来源。

## 从哪里开始

- [Architecture](architecture/README.md)：先建立系统边界和逻辑组件心智模型，再按运行流程深入。
- [Architecture Decisions](adr/README.md)：查看讨论中及已经确认的长期技术决策与取舍。
- [Plans](plans/README.md)：查看讨论中、进行中和已经完成的工作。
- `docs/scratch/`：被全局 Git ignore 的本地构想、审查和临时分析，不作为长期事实来源。

## 内容边界

- 当前、可验证的系统事实写入 `architecture/`。
- 为什么选择某个长期方案写入 `adr/`；是否已经落实单独记录。
- 只有构想、尚未开始核查和技术路线讨论的内容写入本地 `scratch/`，不分配 PLAN 编号。
- 已经开始主动规划但尚未完成的工作写入 `plans/todo/`，状态为 `讨论中` 或 `进行中`。
- 只有经过确认且已有成功提交的工作才进入 `plans/done/`。
- 临时发现确认后提升到 architecture、ADR 或 plan，并清理已经闭环的 scratch 草稿。

代码、测试和可复现行为与文档冲突时，以前者为准，同时修正文档。
