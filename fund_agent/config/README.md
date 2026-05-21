# 配置说明

`fund_agent/config` 当前只是配置命名空间占位，保留给后续稳定配置入口使用。

当前主链路没有运行时 prompt manifest、scene registry 或外部 Dayu config 装配：

- `fund-analysis analyze` 不读取 `config/prompts`
- Service 不解析 scene 或 task prompt
- Fund Capability 的 CHAPTER_CONTRACT / preferred_lens / ITEM_RULE 在 `fund_agent/fund/template` 的 typed manifest 中维护

当前用户可配置项通过 CLI 参数显式传入，常用入口见项目根目录 `README.md`。

后续如果引入配置文件或 prompt manifest，必须先经过设计裁决，并同步更新 `docs/design.md`、本文件和相关测试。
