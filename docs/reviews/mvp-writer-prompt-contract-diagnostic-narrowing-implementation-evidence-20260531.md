# MVP writer prompt contract diagnostic narrowing implementation evidence

日期：2026-05-31

Gate：`MVP writer prompt contract diagnostic narrowing gate`

角色：Gateflow implementation worker。

## Self-check

- Current gate / role：只执行 plan 批准的最小脱敏诊断扩展；不做 prompt 修复、不改 safety contract、不 commit/push/PR/merge/release。
- Source of truth：已读取 `AGENTS.md`、本 gate plan、MiMo/GLM plan review、上一 gate controller judgment/evidence、writer/orchestrator/CLI 相关代码。
- Scope boundary：只触碰允许文件和本 evidence/reports；未修改 golden/fixtures/score/quality gate/Host/Agent/dayu/provider config/auth/PR 状态。
- Stop condition：未保存完整 prompt、完整 draft、完整 provider response、API key、Authorization header；未放松 anchor、ITEM_RULE、candidate facet、forbidden phrase、missing semantics 或 no-fallback 边界。

## Changed files

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-implementation-evidence-20260531.md`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/`

## Implemented slices

- Slice A：新增 Service 层 `ChapterPromptContractDiagnostic` 脱敏摘要和 `failure_subcategory`，accepted 章节为 `None`；writer blocked 和 prompt-contract audit blocked 按 8 类 taxonomy 与固定 precedence 派生主子类。
- Slice A：writer 结果仅额外携带 `response_chars`、`finish_reason`、`max_output_chars` 标量；不改变 parser acceptance 行为。
- Slice A：`issue_id_prefix_counts` 统一剥离 raw anchor/missing/facet/phrase/location/hash suffix，只保存安全 prefix 和整数计数。
- Slice A：candidate facet assertion 只计数并保持 blocked；forbidden phrase 只计数并保持 blocked。
- Slice B：CLI incomplete stderr 追加 scalar `first_failed_subcategory=<value>`；stdout fail-closed 行为不变。
- Slice C：新增 `serialize_chapter_prompt_contract_diagnostics()` 安全序列化 helper，只输出章节状态、分类、计数和标量，不输出 prompt/draft/raw response。

## Diagnostic schema fields

- `failure_subcategory`
- `prompt_contract_diagnostics`
- `schema_version`
- `chapter_id`
- `phase`
- `attempt_index`
- `primary_subcategory`
- `issue_reason_counts`
- `issue_id_prefix_counts`
- `required_structure_missing_count`
- `required_output_missing_count`
- `unknown_anchor_count`
- `invalid_marker_count`
- `forbidden_phrase_count`
- `candidate_facet_assertion_count`
- `response_length_incomplete_count`
- `response_chars`
- `max_output_chars`
- `finish_reason`
- `accepted_draft_present`

## Validation

| Command | Result | Notes |
|---|---|---|
| `uv run ruff check .` | PASS | All checks passed |
| `uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py -q` | PASS | 137 passed |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS | 1169 passed, total coverage 91.83% |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS | exit 0; stdout 24636 bytes |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS | exit 0; stdout 1544 bytes |
| isolated missing-config `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | PASS | exit 1; stdout empty; stderr `missing FUND_AGENT_LLM_PROVIDER` |
| real provider `006597 / 2024 --use-llm` | NOT RUN | By instruction, real provider rerun is left to controller |
| secret scan over new docs/reports artifacts | PASS | No secret-bearing value, prompt body, draft body or provider response body found |

## Evidence files

- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/deterministic-analyze.stdout`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/deterministic-analyze.stderr`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/deterministic-analyze.exitcode`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/deterministic-checklist.stdout`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/deterministic-checklist.stderr`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/deterministic-checklist.exitcode`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/missing-config-use-llm.stdout`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/missing-config-use-llm.stderr`
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/missing-config-use-llm.exitcode`

## Sanitized chapter/phase matrix

Real provider was not run by this implementation worker, so no live provider chapter/phase matrix was generated. Unit coverage verifies the matrix shape and first-failed payload through `serialize_chapter_prompt_contract_diagnostics()` without prompt/draft/raw-response serialization.

## First failed category/subcategory

No real-provider first failed chapter was produced in this worker run. Controller rerun should use the new scalar fields:

- CLI stderr: `first_failed_subcategory=<subcategory>`
- Service diagnostic: `ChapterRunResult.failure_subcategory`
- Safe JSON helper: `serialize_chapter_prompt_contract_diagnostics(result)`

## Docs decision

No README update was made. The gate is an internal diagnostic extension, deterministic user commands are unchanged, and the user-provided allowed touch list did not include README files.

## Residual risks / next entrance

- Real provider rerun remains controller-owned.
- If controller rerun still fails with `prompt_contract`, the next entrance is determined by the first failed `failure_subcategory` using the plan mapping.
- If controller rerun fails with provider runtime instead, route to provider runtime diagnostics rather than prompt repair.
