# 配置说明

`fund_agent/config` 当前只维护静态仓库默认路径。`fund_agent/config/paths.py` 是默认 CSV、golden answer、snapshot、quality gate 和 cache 目录的唯一常量入口。

当前配置包不提供运行时配置系统：

- 不读取环境变量或 workspace 配置文件
- 不读取 `config/prompts`
- 不装配 prompt manifest、scene registry、Host、Agent tool loop 或外部 Dayu runtime
- 不覆盖 CLI 或 Service 中显式传入的参数

`fund_agent/config/prompts/{base,scenes,tasks}` 如果在本地存在，只是惰性占位目录，不代表生产主链路已经接入 prompt、scene 或 task manifest。Fund 作为 Agent 层基金能力包，其 CHAPTER_CONTRACT、preferred_lens 和 ITEM_RULE 仍在 `fund_agent/fund/template` 的 typed manifest 中维护。

常用用户入口见项目根目录 `README.md`。后续如果引入 workspace override、环境变量覆盖或 prompt manifest，必须先经过设计裁决，并同步更新 `docs/design.md`、本文件和相关测试。后续如配置 Host/Agent runtime，Host 必须使用 `dayu.host`，Agent 执行内核必须使用 `dayu.engine`。
