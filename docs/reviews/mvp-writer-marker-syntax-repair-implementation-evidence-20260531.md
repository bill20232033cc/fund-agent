# MVP writer marker syntax repair implementation evidence

日期：2026-05-31

Gate：`MVP writer marker syntax repair gate`

角色：Gateflow implementation worker。

## Self-check

- Current gate / role：只执行已批准的最小 marker syntax repair；不做 controller judgment、不 commit/push/PR/merge/release。
- Source of truth：已读取 `AGENTS.md`、本 gate plan、MiMo/GLM plan review、上一 gate controller judgment/evidence、control/startup/design/template 文档，以及 writer / orchestrator / CLI / tests 相关代码。
- Scope boundary：只修改 writer prompt guidance 和本 gate 回归测试 / evidence；未修改 parser acceptance、allowed missing reasons、candidate facet、golden、fixtures、score、quality gate、final judgment、Host/Agent/dayu、provider auth/config 或 PR 状态。
- Stop condition：未保存完整 prompt、完整 draft、完整 provider response、API key 或 auth header；未运行真实 provider。

## Changed files

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-writer-marker-syntax-repair-implementation-evidence-20260531.md`
- `reports/mvp-local-acceptance/20260531-writer-marker-syntax-repair/`

## Implemented scope

- Writer prompt 中的 missing marker guidance 从 Markdown code-span 改为 explicit contract block。
- Contract block 紧邻 allowed missing reason token list，包含 exact form、placeholder 必须替换、不得输出 placeholder、不得加冒号周围空格、不得改大小写/翻译/全角冒号、不得包反引号或 code fence、不得在 marker 内加入说明/JSON/标签。
- `chapter.missing_reasons` 为空时，prompt 明确本章不得输出 missing marker，但仍可用“未披露 / 数据不足 / 下一步最小验证问题”表达缺口。
- 保持 `_MISSING_MARKER_RE`、`_invalid_marker_issues()`、`_parse_missing_markers()` 行为不变：只接受 `<!-- missing:<allowed_reason> -->`，未知 reason 和污染语法继续 fail-closed。
- `candidate_facet_assertion` 未修复、未放松，仍由现有诊断路径监控并阻断。
- CLI / serialization 仅补充安全回归断言；没有输出 prompt、draft、provider response 或 secret。

## Regression coverage

- Writer prompt tests 覆盖 explicit missing marker contract、allowed reason token list、placeholder / spacing / translation / backtick / code fence 禁止规则。
- Writer parser tests 覆盖合法 exact marker、unknown reason，以及 spacing、case、fullwidth colon、placeholder 未替换等非法 missing marker 仍阻断。
- Orchestrator tests 覆盖 invalid missing marker 与 unknown reason 均归类为 `prompt_contract.invalid_marker`，诊断只保存 issue prefix 和计数，不保存 raw suffix。
- Candidate facet assertion 测试保持 blocked。
- CLI fail-closed 测试继续断言 failed `--use-llm` stdout empty，stderr 只含 safe first-failed scalars。

## Validation

| Command | Result |
|---|---|
| `uv run ruff check .` | PASS, all checks passed |
| `uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py tests/config/test_llm_config.py tests/services/test_llm_provider.py -q` | PASS, 200 passed |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, 1176 passed, total coverage 91.84% |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS, exit 0 |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS, exit 0 |
| isolated missing-config `env -u FUND_AGENT_LLM_PROVIDER -u FUND_AGENT_LLM_BASE_URL -u FUND_AGENT_LLM_API_KEY -u FUND_AGENT_LLM_MODEL uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | PASS fail-closed, exit 1, missing provider config only |
| real provider `006597 / 2024 --use-llm` | NOT RUN, left to controller per instruction |
| `git diff --check` | PASS |

## Secret scan

Scoped scan target for this gate:

- `docs/reviews/mvp-writer-marker-syntax-repair-implementation-evidence-20260531.md`
- `reports/mvp-local-acceptance/20260531-writer-marker-syntax-repair/`

Result：PASS. No secret-bearing value, full prompt, full draft, provider response body or key material is present in the new gate artifact/report path.

## Residual risks / next entrance

- Real provider validation remains controller-owned.
- If controller rerun still fails with `prompt_contract.invalid_marker`, use the safe diagnostic matrix to decide whether another marker guidance gate is warranted.
- If first failure becomes `candidate_facet_assertion`, route to `MVP candidate facet assertion repair gate`; this implementation intentionally did not treat candidate facet assertion as pass.
