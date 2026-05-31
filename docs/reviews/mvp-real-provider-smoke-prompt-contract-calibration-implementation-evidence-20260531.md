# MVP real provider smoke prompt-contract calibration implementation evidence

日期：2026-05-31

Gate：MVP real provider smoke acceptance rerun with prompt-contract calibration
Role：implementation worker

## Self-check
- Current gate / role：只执行 implementation handoff，不启动 gateflow，不写 plan，不 review，不 commit/push/PR/merge/release。
- Source of truth：`docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-plan-20260531.md`、plan fix、controller judgment 和允许文件清单。
- Scope boundary：仅修改 approved plan allowed files；未修改 control docs、design docs、template、golden/fixtures/score/quality gate、Host/Agent/dayu 或 PR state。
- Stop condition：未触发需要放松安全边界、无限 retry、存储 unsafe provider data 或无法分类失败的停止条件。

## Changed files
- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md`
- `reports/mvp-local-acceptance/20260531-prompt-contract-calibration/`

## Implemented slices
- Slice A：writer prompt 前置短协议，强调固定三段、exact required_output marker、allowed anchor/missing marker、候选 facet 固定未断言句式和长度优先级；parser 继续 fail-closed。
- Slice B：auditor line protocol 继续 fail-closed，并改为严格三段解析；parse failure 仍 blocked。
- Slice C：repair/regenerate 保持 bounded；上一轮 issue ids/messages/required corrections 已通过 typed repair context 带入；timeout 不进入 repair loop。
- Slice D：`ChapterFailureCategory` 增加 `llm_timeout` 和 `audit_rule_too_strict`；`ChapterRunResult.failure_category` 成为 CLI first_failed_category 唯一来源。
- Slice E：完成本地验证和脱敏 smoke evidence；当前 shell 无真实 provider env，real provider smoke 记录为 validation blocked。

## Contract changes
- Writer prompt：降低认知负担，不改变安全 parser；marker/anchor/missing/non_asserted facet/length/incomplete finish reason 防护保留。
- Auditor protocol：只接受 `PASS|chapter|no issues` 或三段 `BLOCKING|...` / `REVIEWABLE|...` / `INFO|...` 行协议；额外分隔符归入 parse failure。
- Repair/regenerate：每章最大 writer attempts 仍为 `1 + max_repair_attempts`；regenerate 输入只包含脱敏、限长的 previous issues 和确定性 corrections。
- Failure taxonomy：timeout 独立为 `llm_timeout`；非 timeout provider runtime 仍为 `provider_runtime`；programmatic pass 且 LLM 可解析失败、无 parse failure、无 fact gap 时归 `audit_rule_too_strict`。

## Validation
| Command | Result | Notes |
|---|---|---|
| `uv run ruff check .` | PASS | All checks passed |
| `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_provider.py tests/ui/test_cli.py -q` | PASS | 170 passed |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS | 1154 passed, total coverage 91.80% |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS | exit 0; stdout 24636 bytes; stderr 358 bytes |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS | exit 0; stdout 1544 bytes; stderr 362 bytes |
| isolated missing-config `--use-llm` smoke | PASS | exit 1; stdout empty; stderr `LLM provider 配置错误：missing FUND_AGENT_LLM_PROVIDER` |
| `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | BLOCKED | provider env absent in current shell; recorded `provider_config_missing_in_validation_shell` equivalent as skipped evidence |
| secret leak scan | PASS | No secret-bearing hits after evidence creation |

## Real provider smoke evidence
| Field | Value |
|---|---|
| command_label | real-provider-smoke-006597-2024 |
| exit_code | skipped_env_unavailable |
| stdout | empty |
| orchestration_status | not_run |
| final_assembly_status | not_run |
| first_failed_chapter_id | none |
| first_failed_phase | provider_config_validation_shell |
| first_failed_stop_reason | provider_config_missing_in_validation_shell |
| first_failed_category | provider_runtime |

## Chapter matrix
| Chapter | Status | Stop reason | Category | Attempt count |
|---|---|---|---|---|
| 1 | not_run | provider_config_missing_in_validation_shell | provider_runtime | 0 |
| 2 | not_run | provider_config_missing_in_validation_shell | provider_runtime | 0 |
| 3 | not_run | provider_config_missing_in_validation_shell | provider_runtime | 0 |
| 4 | not_run | provider_config_missing_in_validation_shell | provider_runtime | 0 |
| 5 | not_run | provider_config_missing_in_validation_shell | provider_runtime | 0 |
| 6 | not_run | provider_config_missing_in_validation_shell | provider_runtime | 0 |

## Secret hygiene
- API key/header/full prompt/full draft/full provider response stored：no
- Secret scan command：`rg -n "sk-[A-Za-z0-9]|Authorization|Bearer|api_key|FUND_AGENT_LLM_API_KEY|full provider|writer user|draft markdown|full prompt|full draft|full provider response" reports/mvp-local-acceptance/20260531-prompt-contract-calibration docs/reviews/mvp-real-provider-smoke-prompt-contract-calibration-implementation-evidence-20260531.md`
- Secret scan result：PASS；only safe policy-label hits in this evidence section, no secret-bearing value, header value, prompt body, draft body, provider response body or env dump.

## Docs decision
- Docs decision: no README update needed because runtime behavior and public usage commands are unchanged.

## Residual risks
- Real provider smoke could not run in this shell because provider config/auth env was absent; code path remains fail-closed and missing-config smoke passed.
- Actual provider output may still expose writer prompt-contract, auditor parse, auditor rule-too-strict, timeout, fact-gap or provider-runtime blockers; these now have top-level `ChapterRunResult.failure_category` for precise next entry.

## Next minimal gate
- If provider env is supplied：rerun real provider smoke and classify first failure using `first_failed_category` from CLI stderr.
- If real provider still fails with `llm_timeout`：Provider runtime budget tuning gate.
- If it fails with `prompt_contract`：Writer prompt contract calibration follow-up.
- If it fails with `audit_parse`：Auditor protocol calibration follow-up.
- If it fails with `audit_rule_too_strict`：Auditor rubric calibration gate.
- Completion status：implementation complete; acceptance still blocked by provider_config_missing_in_validation_shell in this validation shell.
