# Provider/LLM L4 Negative/Fail-closed Evidence

Date: 2026-06-13

Gate: `Provider/LLM L4 Negative/Fail-closed Evidence Gate`

Status: `EVIDENCE_READY_FOR_REVIEW_NOT_READY`

## Scope

This evidence gate executed the accepted no-live Provider/LLM L4
negative/fail-closed evidence matrix from
`docs/reviews/mvp-provider-llm-l4-negative-fail-closed-sub-plan-20260613.md`.

This gate did not run live provider/LLM, network, PDF, FDR, source, analyze,
checklist, readiness, release, PR, push, merge, cleanup or external-state
commands. It did not modify source, tests, runtime behavior, manifest, fixture,
golden-answer content, README or design truth.

Release/readiness remains `NOT_READY`.

## Inputs

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth; source access, fallback and layer-boundary constraints. |
| `docs/current-startup-packet.md` | Current L4 evidence gate and `NOT_READY` posture. |
| `docs/implementation-control.md` | Control truth for active gate and deferred gates. |
| `docs/design.md` | Design truth for explicit opt-in `--use-llm` and EID single-source/no fallback. |
| `docs/reviews/mvp-provider-llm-l4-negative-fail-closed-sub-plan-controller-judgment-20260613.md` | Accepted plan basis. |
| `fund_agent/config/llm.py` | Provider config fail-closed behavior and diagnostic fallback fields. |
| `fund_agent/services/llm_provider.py` | Provider runtime failure mapping and safe diagnostics. |
| `fund_agent/services/fund_analysis_service.py` | Service fail-closed hosted LLM path and no deterministic fallback. |
| `fund_agent/services/execution_contract.py` | Explicit request/runtime fields and deterministic fallback prohibition. |
| `fund_agent/services/chapter_orchestrator.py` | Provider failure propagation and no source acquisition boundary. |
| `fund_agent/services/agent_bridge.py` | Service-to-Agent projection boundary. |
| `fund_agent/services/llm_run_artifacts.py` | Artifact allowlist/redaction. |
| `fund_agent/services/final_chapter_assembler.py` | Final assembly boundary. |
| `fund_agent/agent/`, `fund_agent/host/` | Agent/Host boundary code. |
| `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/chapter_auditor.py` | Fund-layer LLM primitives source-access guard. |
| `tests/config/`, `tests/services/`, `tests/agent/`, `tests/host/` | No-live negative/fail-closed tests. |

## Commands

| Command | Result | Evidence use |
|---|---:|---|
| `git status --branch --short` | exit 0 | Branch/status preflight; branch was `feat/mvp-llm-incomplete-run-artifacts`, ahead 50, with existing untracked residue families. |
| `git status --short` | exit 0 | Confirmed visible untracked residue families are pre-existing and not current gate source/test/runtime edits. |
| `git diff --check` | exit 0 | Whitespace validation before evidence write. |
| `rg --files fund_agent/config fund_agent/services fund_agent/agent fund_agent/host fund_agent/fund tests/config tests/services tests/agent tests/host` | exit 0 | Path-existence/preflight; accepted source/test surfaces exist. |
| `rg -n "analyze_with_llm\|analyze_with_llm_hosted\|analyze_with_llm_execution\|build_fund_llm_execution_request\|build_chapter_llm_clients\|OpenAICompatibleChapterLLMClient\|ChapterOrchestratorLLMClients\|HostRuntimeRunner\|run_agent_report\|write_llm_incomplete_run_artifacts\|write_llm_run_artifacts" fund_agent tests` | exit 0 | L4 path map for Service/Host/Agent/Fund/provider/artifact route. |
| `rg -n "fund_agent\\.fund\\.documents\|FundDocumentRepository\|Eastmoney\|CNINFO\|fund-company\|fund_company\|AnnualReportSource\|AnnualReportSourceOrchestrator\|download\|downloader\|pdf\|PDF\|cache\|source helper\|source_helper\|fallback_used\|fallback" fund_agent/config fund_agent/services fund_agent/agent fund_agent/host tests/config tests/services tests/agent tests/host` | exit 0 | Scoped source-access guard. |
| Same source-access guard over `fund_agent/fund/chapter_writer.py fund_agent/fund/chapter_auditor.py` | exit 0 | Fund writer/auditor primitive source-access guard. |
| `rg -n "deterministic fallback\|fallback to deterministic\|partial/blocked 不回退\|不回退 deterministic\|fail-closed\|fail closed\|LLMProviderTimeoutError\|LLMProviderNetworkError\|LLMProviderRateLimitError\|LLMProviderMalformedResponseError\|LLMProviderRuntimeError\|provider_runtime\|llm_timeout\|llm_network_error\|llm_rate_limited\|llm_malformed_response" fund_agent/services fund_agent/agent tests/services tests/agent` | exit 0 | Provider failure no deterministic/source fallback and fail-closed classification evidence. |
| `rg -n "SYSTEM_PROMPT_CANARY\|USER_PROMPT_CANARY\|RAW_AUDITOR_RESPONSE_CANARY\|RAW_RESPONSE_CANARY\|PROVIDER_RESPONSE_CANARY\|Authorization\|Bearer\|sk-\|raw provider\|raw_response\|provider body\|PDF body\|cache body\|source body\|annual report body\|prompt.*canary" tests/services fund_agent/services` | exit 0 | Artifact/redaction and sensitive payload guard. |
| `env -u FUND_AGENT_LLM_PROVIDER ... -u FUND_AGENT_LLM_MAX_OUTPUT_CHARS uv run pytest ... -q` | exit 0, `238 passed in 1.11s` | No-live L4 test matrix with provider env cleared. |
| `uv run ruff check ...` | exit 0, `All checks passed!` | Lint validation for scoped L4 code/test paths. |

The pytest command cleared ambient `FUND_AGENT_LLM_*` variables and used current
no-live tests with fakes/mocks. This evidence does not accept any real provider
credential, provider HTTP call or network access.

## Evidence Matrix

| Row | Evidence observed | Disposition |
|---|---|---|
| L4-N0 Control boundary | Startup/control docs identify this active gate as no-live L4 evidence under accepted plan `0772a6e`; release/readiness remains `NOT_READY`. | PASS |
| L4-N1 Forbidden import/source access static guard | Scoped static guard found no blocking provider/LLM production-path import/use of `FundDocumentRepository`, `fund_agent.fund.documents`, Eastmoney, CNINFO or annual-report source orchestrator. Lexical matches are classified below. | PASS_WITH_INTERPRETATION |
| L4-N2 Provider failure no deterministic fallback | Execution contract rejects `deterministic_fallback_allowed=True`; Service LLM tests cover missing writer/auditor block and partial LLM result not falling back to deterministic report. | PASS |
| L4-N3 Provider failure no source fallback | Provider/runtime failure tests and static guards show failures map to provider/runtime diagnostics and Service/Agent fail-closed paths, not annual-report source fallback. | PASS_WITH_STATIC_LIMIT |
| L4-N4 Service boundary no source acquisition | Service LLM path constructs typed execution/provider clients and Host operation; direct annual-report source/PDF/cache references in scoped Service results are docstring boundary, thermometer cache, diagnostics or tests. | PASS_WITH_INTERPRETATION |
| L4-N5 Host boundary no source acquisition | Host tests and code remain lifecycle-oriented. `FundDocumentRepository` appears in a forbidden-key style assertion, not Host source acquisition. | PASS |
| L4-N6 Agent boundary no direct source acquisition | Agent runtime tests pass; Agent LLM runtime maps provider failures to blocked runtime states. Agent README/source-helper lexical matches are boundary statements. | PASS_WITH_INTERPRETATION |
| L4-N7 Artifact/redaction no source cache body leakage | Redaction/canary tests show prompts, raw provider payload, Authorization/Bearer/sk-style secrets and raw response fields are excluded from diagnostics/artifacts. | PASS |
| L4-N8 Failure classification/residuals | Timeout/network/rate-limit/malformed/http-error provider failures are covered by no-live tests. 401/403 provider-response classification remains residual. | PASS_WITH_RESIDUAL |
| L4-N9 Lexical match disposition | `cache`, `pdf`, `download`, `fallback` matches are classified as config constants, thermometer code/tests, boundary docstrings, safe diagnostics, final-assembly text fallback, Agent line fallback, or tests asserting absence. | PASS_WITH_INTERPRETATION |
| L4-N10 Final disposition | Bounded no-live negative/fail-closed evidence passed; no release/readiness/live/source-expansion claim is accepted. | PASS_NOT_READY |

## Source-access Guard Disposition

| Match class | Disposition | Reason |
|---|---|---|
| `fund_agent/services/fund_analysis_service.py` module/docstrings saying Service does not read annual-report files/PDF/cache/source helper | ACCEPT_BOUNDARY_STATEMENT | Explicitly states the boundary; not source access. |
| `fund_agent/services/chapter_orchestrator.py`, `fund_agent/services/final_chapter_assembler.py`, `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/chapter_auditor.py` boundary docstrings | ACCEPT_BOUNDARY_STATEMENT | State no repository/PDF/cache/source-helper access. |
| `fund_agent/config/paths.py` and `tests/config/test_paths.py` cache/PDF constants | ACCEPT_OUTSIDE_PROVIDER_FAILURE_PATH | Config path constants and path tests are not provider/LLM source fallback. |
| `fund_agent/services/thermometer_service.py` and thermometer tests | ACCEPT_OUTSIDE_L4_PROVIDER_SOURCE_POLICY | Thermometer market data cache/fallback is outside annual-report provider/LLM source fallback. |
| `repair_timeout_fallback_used` in config/provider/orchestrator/artifacts | ACCEPT_PROVIDER_DIAGNOSTIC_FALLBACK | This is provider timeout diagnostic fallback to writer timeout, not annual-report source fallback. |
| `fallback_lines` and final-assembly `fallback` strings | ACCEPT_TEXT_FALLBACK | Text conclusion fallback is not source acquisition or deterministic report fallback after provider failure. |
| Tests containing forbidden terms `cache`, `pdf`, `downloader`, `FundDocumentRepository`, `Authorization`, `Bearer`, `sk-` | ACCEPT_TEST_GUARD | These tests assert boundary/redaction behavior or forbidden-key absence. |
| `FundDocumentRepository`, Eastmoney, CNINFO in scoped provider/LLM production paths | NO_BLOCKING_MATCH_OBSERVED | No blocking production-path import/use observed in the scoped L4 route. |

## Failure / Redaction Evidence

| Risk | Evidence | Disposition |
|---|---|---|
| Deterministic fallback allowed by contract | `QualityPolicyDeclaration` and runtime fail-closed policy reject `deterministic_fallback_allowed=True`; tests cover rejection. | PASS |
| Missing writer/auditor or partial LLM result falls back to deterministic report | Service LLM tests include `test_missing_writer_or_auditor_blocks_without_deterministic_fallback` and `test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness`. | PASS |
| Provider timeout/network/rate-limit/malformed/http-error becomes non-fail-closed | Provider/orchestrator/Agent tests map these to runtime categories and fail-closed terminal states. | PASS |
| Provider failure invokes annual-report source fallback | Static source guard and failure tests show provider failure handling remains in provider/runtime/orchestration diagnostics; no annual-report fallback path was observed. | PASS_WITH_STATIC_LIMIT |
| Raw prompt/provider/credential/header leakage | LLM provider, chapter orchestrator and incomplete-run artifact tests assert Authorization/Bearer/sk/provider body/raw_response/prompt canaries are removed. | PASS |
| Source/PDF/cache body leakage | No source/PDF/cache body is accepted in artifact schema; current evidence is static/no-live and does not inspect private cache bodies. | PASS_WITH_STATIC_LIMIT |
| 401/403 provider-response classification | No dedicated current no-live 401/403 mock classification evidence was accepted. | RESIDUAL |

## Accepted Facts

| Fact | Disposition |
|---|---|
| Accepted no-live L4 matrix commands completed successfully. | ACCEPT |
| Provider/LLM source-policy negative paths have bounded no-live evidence for fail-closed handling without deterministic fallback. | ACCEPT_WITH_NO_LIVE_LIMIT |
| Scoped provider/LLM production paths did not show blocking direct annual-report source/FDR/PDF/cache/Eastmoney/CNINFO access. | ACCEPT_STATIC_GUARD_FACT |
| Provider diagnostic fallback fields are not annual-report source fallback. | ACCEPT |
| Artifact/redaction tests support exclusion of prompts, raw provider payload, credentials and raw responses. | ACCEPT_NO_LIVE_FACT |
| 401/403 provider-response classification remains residual. | ACCEPT_RESIDUAL |
| Release/readiness remains `NOT_READY`. | ACCEPT_CONTROL_FACT |

## Rejected Claims

| Claim | Disposition | Reason |
|---|---|---|
| This evidence proves live provider/LLM availability. | REJECT | No live provider/network command was run. |
| This evidence proves LLM content quality or chapter acceptance. | REJECT | Current evidence is negative/fail-closed only. |
| This evidence proves release/MVP/PR readiness. | REJECT | Readiness remains `NOT_READY`; PR/external-state gates are separate. |
| This evidence authorizes source expansion, Eastmoney, CNINFO or fund-company fallback. | REJECT | Current source policy remains EID single-source/no fallback. |
| This evidence authorizes provider default/runtime budget/retry/fallback semantic changes. | REJECT | No implementation gate accepted these changes. |
| This evidence authorizes cleanup/archive/ignore, push, PR, merge or mark-ready. | REJECT | Separate gates/authorization only. |
| A clean/static lexical guard proves all future source-policy behavior. | REJECT | Static guard is bounded evidence only. |

## Residuals

| Residual | Classification | Owner | Next handling |
|---|---|---|---|
| 401/403 provider-response classification remains unproven. | provider classification residual | Provider/runtime owner | Defer unless controller requires closure before live. |
| Live provider/LLM execution remains unrun. | live/provider residual | User/controller + provider runtime owner | Separate controlled live provider/LLM gate only. |
| LLM content quality / chapter acceptance remains unaccepted. | content-quality residual | Provider/runtime + chapter owners | Separate live/content acceptance gate only if authorized. |
| Source/PDF/cache body leak absence is static/schema/test-limited, not private body-read proof. | evidence-scope residual | Controller/evidence owner | Only expand under a separate source/cache-body evidence gate if needed. |
| Release/readiness remains unproven. | readiness blocker | Release owner/controller | Separate readiness/release gate only. |
| Existing untracked artifact/report residue remains visible. | artifact hygiene residual | Artifact owners/controller | Separate artifact disposition/cleanup gate only. |

## Conclusion

The accepted no-live L4 negative/fail-closed evidence matrix passed.

This supports a bounded conclusion: current provider/LLM source-policy negative
paths have no-live evidence that provider/runtime failures fail closed without
deterministic report fallback or annual-report source fallback, and scoped
provider/LLM production paths do not show blocking direct annual-report
source/FDR/PDF/cache/Eastmoney/CNINFO access.

It does not prove live provider availability, LLM output quality, release
readiness, PR readiness, or future source-policy behavior outside the scoped
matrix.

Recommended next entry:

`Provider/LLM L4 Negative/Fail-closed Evidence Review Gate`

Deferred entries:

- controlled live provider/LLM execution;
- no-live 401/403 provider-response mock evidence;
- release/readiness execution or claim;
- PR/push/merge/mark-ready;
- cleanup/archive/ignore disposition;
- golden-answer promotion;
- fixture or manifest expansion;
- source expansion or fallback design.
