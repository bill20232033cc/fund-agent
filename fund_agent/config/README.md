# 配置说明

`fund_agent/config` 当前维护两类配置入口：

- `fund_agent/config/paths.py`：默认 CSV、golden answer、snapshot、quality gate 和 cache 目录的唯一常量入口。
- `fund_agent/config/llm.py`：Route C `--use-llm` 路径的 typed LLM env config，只把显式环境变量解析为不可变配置对象。

当前配置包仍不提供通用 workspace/runtime 配置系统：

- 不读取 workspace 配置文件
- 不读取 `config/prompts`
- 不装配 prompt manifest、scene registry、Host、Agent tool loop 或外部 Dayu runtime
- 不覆盖 CLI 或 Service 中显式传入的参数

## LLM env config

`fund_agent.config.llm.load_llm_provider_config_from_env()` 仅服务 `fund-analysis analyze --use-llm` 的显式 opt-in 路径。默认 `analyze` 和 `checklist` 不读取这些环境变量。

| 环境变量 | 必填 | 说明 |
|------|------|------|
| `FUND_AGENT_LLM_PROVIDER` | 是 | 当前仅支持 `openai_compatible` |
| `FUND_AGENT_LLM_MODEL` | 是 | 模型名；无代码默认值 |
| `FUND_AGENT_LLM_BASE_URL` | 是 | OpenAI-compatible base URL；必须是无 query/fragment 的 `http://` 或 `https://` URL |
| `FUND_AGENT_LLM_API_KEY_ENV_VAR` | 否 | API key 所在环境变量名；默认 `FUND_AGENT_LLM_API_KEY` |
| API key env var 的值 | 是 | 空白视为缺失 |
| `FUND_AGENT_LLM_TIMEOUT_SECONDS` | 否 | 默认 `60`，范围 `(0, 300]` |
| `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` | 否 | 默认 `12000`，范围 `(0, 50000]`；本地字符上限，不是 provider token budget |

API key 字段在 `LLMProviderConfig` 的 `repr` 中隐藏；配置错误、provider 构造错误和 provider runtime 错误不得输出 key、Authorization header、prompt body 或完整 response body。pytest 使用 fake env mapping、`httpx.MockTransport` 和 monkeypatch，不需要真实 key，也不访问 live provider。

`fund_agent/config/prompts/{base,scenes,tasks}` 如果在本地存在，只是惰性占位目录，不代表生产主链路已经接入 prompt、scene 或 task manifest。Fund 作为 Agent 层基金能力包，其 CHAPTER_CONTRACT、preferred_lens 和 ITEM_RULE 仍在 `fund_agent/fund/template` 的 typed manifest 中维护。

常用用户入口见项目根目录 `README.md`。后续如果引入 workspace override、prompt manifest、provider fallback、retry/backoff 或 live smoke，必须先经过设计裁决，并同步更新 `docs/design.md`、本文件和相关测试。后续如配置 Host/Agent runtime，Host 必须使用 `dayu.host`，Agent 执行内核必须使用 `dayu.engine`。
