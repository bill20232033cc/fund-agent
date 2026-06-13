# Provider/LLM L4 Negative/Fail-closed Evidence Sub-plan

Date: 2026-06-13

Gate: `Provider/LLM L4 Negative/Fail-closed Evidence Sub-plan Gate`

Status: `PLAN_READY_FOR_REVIEW_NOT_READY`

## Scope

This is a planning-only gate for Provider/LLM L4 negative/fail-closed evidence.

The plan defines a future no-live evidence gate to prove that the explicit
opt-in provider-backed `--use-llm` path preserves source-policy boundaries under
negative/provider-failure scenarios:

- no Eastmoney/CNINFO/fund-company fallback is reintroduced;
- provider/LLM layers do not directly access `FundDocumentRepository`, PDF,
  cache, source helper or downloader surfaces;
- provider/LLM failures do not fall back to deterministic report generation or
  annual-report source fallback;
- incomplete/error artifacts do not retain source cache/PDF body, raw provider
  payload, prompts, headers or credentials;
- current EID single-source/no-fallback source policy remains unchanged.

This gate does not execute the future evidence commands. It does not run live
provider/LLM, network, PDF, FDR, source, analyze, checklist, readiness, release,
PR, push, merge, cleanup or external-state commands. It does not modify source,
tests, runtime behavior, manifest, fixture, golden-answer content, README or
design truth.

Release/readiness remains `NOT_READY`.

## Goals

| Goal | Disposition |
|---|---|
| Plan no-live negative/fail-closed evidence for source-policy safety in the `--use-llm` path. | ACCEPT |
| Distinguish annual-report source fallback from diagnostic-only provider fields such as `repair_timeout_fallback_used`. | ACCEPT |
| Verify future evidence can show provider/LLM failures remain fail-closed and do not fall back to deterministic/source paths. | ACCEPT |
| Preserve EID single-source/no fallback. | ACCEPT |
| Preserve `NOT_READY`. | ACCEPT |

## Non-goals

| Non-goal | Reason |
|---|---|
| Execute live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands. | Planning-only boundary. |
| Prove live provider availability. | L4 is no-live negative/source-policy evidence only. |
| Prove LLM content quality or chapter acceptance. | Requires separate live/content evidence if authorized. |
| Prove release/MVP/PR readiness. | Readiness gates remain separate and `NOT_READY`. |
| Change source policy, provider defaults, runtime budget, retry or fallback semantics. | Requires separate implementation/design gate. |
| Reopen Eastmoney, CNINFO or fund-company fallback design. | Current policy remains EID single-source/no fallback. |
| Add or modify tests/source/runtime. | This plan only defines future evidence; implementation gaps become blockers/residuals. |
| Cleanup/archive/ignore artifacts. | Separate artifact disposition gate only. |

## Truth Inputs

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth; source access, fallback and layer-boundary constraints. |
| `docs/current-startup-packet.md` | Current active gate, accepted checkpoint and `NOT_READY` posture. |
| `docs/implementation-control.md` | Control truth for current L4 planning gate and deferred gates. |
| `docs/design.md` | Design truth for `--use-llm`, Route C and EID single-source/no-fallback policy. |
| `docs/reviews/mvp-provider-llm-l3-no-live-static-contract-evidence-controller-judgment-20260613.md` | Accepted L3 facts, rejected claims and residuals. |
| `docs/reviews/mvp-provider-llm-l3-ready-state-disposition-controller-judgment-20260613.md` | Accepted route to L4 negative/fail-closed planning. |

## Future Read Scope

| Path | Purpose |
|---|---|
| `fund_agent/config/llm.py` | Provider config fail-closed behavior and env validation. |
| `fund_agent/services/llm_provider.py` | Provider runtime failure mapping and safe diagnostics. |
| `fund_agent/services/fund_analysis_service.py` | Service fail-closed hosted LLM path and no deterministic fallback. |
| `fund_agent/services/execution_contract.py` | Explicit request/runtime fields and no `extra_payload` route. |
| `fund_agent/services/chapter_orchestrator.py` | Provider failure propagation and no source acquisition. |
| `fund_agent/services/agent_bridge.py` | Service-to-Agent projection and no source acquisition. |
| `fund_agent/services/llm_run_artifacts.py` | Artifact allowlist/redaction and no raw provider/source/PDF/cache body. |
| `fund_agent/services/final_chapter_assembler.py` | Final assembly boundary and no source/cache/PDF access. |
| `fund_agent/host/` | Host lifecycle boundary and no business/source acquisition. |
| `fund_agent/agent/` | Agent body runner boundary and no repository/source helper access. |
| `fund_agent/fund/chapter_writer.py` | Writer protocol fail-closed behavior. |
| `fund_agent/fund/chapter_auditor.py` | Auditor protocol fail-closed behavior. |
| `tests/config/`, `tests/services/`, `tests/agent/`, `tests/host/` | No-live config, provider, Service, artifact, Agent and Host negative evidence tests. |

## Evidence Matrix

| Row | Evidence target | Future method | Allowed conclusion | Forbidden conclusion |
|---|---|---|---|---|
| L4-N0 | Control boundary | Read current startup/control/design and L3/L3-disposition controller judgments. | L4 no-live negative/fail-closed evidence may proceed. | Live provider/LLM or readiness is authorized. |
| L4-N1 | Forbidden import/source access static guard | `rg` scoped provider/LLM Service/Host/Agent layers for source/FDR/PDF/cache/fallback terms. | No blocking scoped production-path import/use is observed, or lexical matches are conservatively classified. | Source policy can expand or fallback is safe. |
| L4-N2 | Provider failure no deterministic fallback | Read/tests for provider runtime errors, timeout, malformed response, 4xx/5xx and blocked output in Service/orchestrator/Agent. | Provider/LLM failure remains fail-closed and does not emit deterministic markdown as fallback. | LLM path output quality is accepted. |
| L4-N3 | Provider failure no source fallback | Static/test evidence that provider failures do not call annual-report source fallback, Eastmoney/CNINFO/fund-company route, `FundDocumentRepository`, PDF cache, downloader or source helper. | Provider failure handling is isolated from source acquisition. | Source negative/failure branches are live-proven. |
| L4-N4 | Service boundary no source acquisition | Static guard over Service LLM path and boundary tests. | Service-owned LLM orchestration consumes typed inputs and provider clients; it does not directly acquire annual reports/PDF/source fallback. | Service can bypass `FundDocumentRepository` or source policy. |
| L4-N5 | Host boundary no source acquisition | Static guard and Host tests. | Host remains lifecycle-only and business/source opaque. | Host can inspect fund/source/PDF fields. |
| L4-N6 | Agent boundary no direct source acquisition | Static guard and Agent tests. | Agent body runner uses injected Fund writer/auditor/tool protocol and does not directly acquire annual-report source/PDF/cache. | Agent has full production source/tool-loop authority. |
| L4-N7 | Artifact/redaction no source cache body leakage | Redaction tests and static artifact allowlist read. | Incomplete/error artifacts exclude raw provider payload, prompts, credentials, headers, source cache/PDF body and raw annual-report body. | Artifacts prove readiness or content quality. |
| L4-N8 | Failure classification/residuals | Compare observed current classifications with L3 residuals. | 401/403 provider-response classification may remain residual unless dedicated no-live mock evidence exists. | Current evidence proves all provider classifications. |
| L4-N9 | Lexical match disposition | Review every match from source-access guard. | `cache/pdf/download/fallback` matches are accepted only if non-source, diagnostic-only, config-only, docstring boundary or test guard. | Any lexical clean result alone proves no future source-policy risk. |
| L4-N10 | Final disposition | Summarize accepted facts, blockers and residuals. | Accept bounded no-live negative/fail-closed evidence or block with exact missing evidence path. | Release/readiness/PR/source expansion is authorized. |

## Future No-live Commands

These commands are for the future evidence gate only. Do not run them in this
planning gate.

```bash
git status --branch --short
git status --short
git diff --check
```

```bash
rg --files fund_agent/config fund_agent/services fund_agent/agent fund_agent/host fund_agent/fund tests/config tests/services tests/agent tests/host
```

```bash
rg -n "analyze_with_llm|analyze_with_llm_hosted|analyze_with_llm_execution|build_fund_llm_execution_request|build_chapter_llm_clients|OpenAICompatibleChapterLLMClient|ChapterOrchestratorLLMClients|HostRuntimeRunner|run_agent_report|write_llm_incomplete_run_artifacts|write_llm_run_artifacts" fund_agent tests
```

```bash
rg -n "fund_agent\\.fund\\.documents|FundDocumentRepository|Eastmoney|CNINFO|fund-company|fund_company|AnnualReportSource|AnnualReportSourceOrchestrator|download|downloader|pdf|PDF|cache|source helper|source_helper|fallback_used|fallback" fund_agent/config fund_agent/services fund_agent/agent fund_agent/host tests/config tests/services tests/agent tests/host
```

```bash
rg -n "fund_agent\\.fund\\.documents|FundDocumentRepository|Eastmoney|CNINFO|fund-company|fund_company|AnnualReportSource|AnnualReportSourceOrchestrator|download|downloader|pdf|PDF|cache|source helper|source_helper|fallback_used|fallback" fund_agent/fund/chapter_writer.py fund_agent/fund/chapter_auditor.py
```

```bash
rg -n "deterministic fallback|fallback to deterministic|partial/blocked 不回退|不回退 deterministic|fail-closed|fail closed|LLMProviderTimeoutError|LLMProviderNetworkError|LLMProviderRateLimitError|LLMProviderMalformedResponseError|LLMProviderRuntimeError|provider_runtime|llm_timeout|llm_network_error|llm_rate_limited|llm_malformed_response" fund_agent/services fund_agent/agent tests/services tests/agent
```

```bash
rg -n "SYSTEM_PROMPT_CANARY|USER_PROMPT_CANARY|RAW_AUDITOR_RESPONSE_CANARY|RAW_RESPONSE_CANARY|PROVIDER_RESPONSE_CANARY|Authorization|Bearer|sk-|raw provider|raw_response|provider body|PDF body|cache body|source body|annual report body|prompt.*canary" tests/services fund_agent/services
```

```bash
env -u FUND_AGENT_LLM_PROVIDER -u FUND_AGENT_LLM_MODEL -u FUND_AGENT_LLM_BASE_URL -u FUND_AGENT_LLM_API_KEY_ENV_VAR -u FUND_AGENT_LLM_API_KEY -u FUND_AGENT_LLM_TIMEOUT_SECONDS -u FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS -u FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS -u FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS -u FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS -u FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS -u FUND_AGENT_LLM_MAX_OUTPUT_CHARS uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py tests/agent/test_service_bridge.py tests/host/test_runtime_runner.py -q
```

```bash
uv run ruff check fund_agent/config/llm.py fund_agent/services/llm_provider.py fund_agent/services/execution_contract.py fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/agent_bridge.py fund_agent/services/llm_run_artifacts.py fund_agent/services/final_chapter_assembler.py fund_agent/agent fund_agent/host tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent tests/host
```

## Future Evidence Handling Rules

| Evidence condition | Required disposition |
|---|---|
| `FundDocumentRepository`, `fund_agent.fund.documents`, Eastmoney or CNINFO appears in scoped provider/LLM production path. | `BLOCKER_UNEXPECTED_SOURCE_ACCESS` unless proven outside route or doc/test-only. |
| `download`, `pdf`, `cache`, `fallback` appears only in config constants, thermometer code, docstrings, safe diagnostics or tests asserting absence. | `ACCEPT_NON_BLOCKING_LEXICAL_MATCH` with row-by-row explanation. |
| Provider failure tests show deterministic fallback report is emitted. | `BLOCKER_PROVIDER_FAILURE_DETERMINISTIC_FALLBACK`. |
| Provider failure tests/static read show annual-report source fallback or source helper invocation. | `BLOCKER_PROVIDER_FAILURE_SOURCE_FALLBACK`. |
| Incomplete artifacts contain prompt, raw provider payload, credentials, headers, source/PDF/cache body or annual-report body. | `BLOCKER_SENSITIVE_OR_SOURCE_BODY_LEAK`. |
| 401/403 provider-response classification remains untested. | Residual only, not blocker for L4 source-policy evidence, unless controller requires classification closure before live. |
| Future pytest/ruff command fails. | Block evidence acceptance; record failing command and route to implementation or test-fix planning gate. |
| `rg --files` shows accepted test paths do not exist. | Stop and route to `Provider/LLM L4 Static Read-preflight Gate`. |

## Failure Classification And Residuals

| Failure / risk | Future evidence classification | Expected disposition |
|---|---|---|
| Missing/invalid provider config | `CONFIG_FAIL_CLOSED` | Accept if env/config tests show no provider construction and no source fallback. |
| Provider timeout/network/429/5xx/malformed response | `PROVIDER_RUNTIME_FAIL_CLOSED` | Accept if fail-closed diagnostics occur without deterministic/source fallback. |
| Non-auth 4xx rejected request | `PROVIDER_REQUEST_REJECTED` | Accept only as plan-level classification unless current runtime has a distinct enum. |
| 401/403 provider-response | `AUTH_RESPONSE_UNPROVEN` or `AUTH_BLOCKED` if dedicated mock exists | Residual unless dedicated no-live mock evidence exists. |
| Direct provider/LLM source/PDF/cache/FDR access | `UNEXPECTED_SOURCE_ACCESS` | Blocker. |
| Eastmoney/CNINFO/fund-company fallback in LLM path | `SOURCE_POLICY_REGRESSION` | Blocker. |
| Deterministic report fallback after LLM failure | `DETERMINISTIC_FALLBACK_REGRESSION` | Blocker. |
| Source/PDF/cache body or raw provider payload retained | `SENSITIVE_OR_SOURCE_BODY_LEAK` | Blocker. |
| Release/readiness claim from L4 evidence | `READINESS_OVERCLAIM` | Blocker for review acceptance. |

## Allowed Conclusions

| Conclusion | Limit |
|---|---|
| The scoped no-live evidence shows provider/LLM source-policy negative paths fail closed. | Only if static guards and tests pass. |
| Provider/LLM failure handling does not reintroduce deterministic/source fallback in the tested no-live matrix. | No live/provider availability claim. |
| Provider/LLM layers do not directly access annual-report source/PDF/cache surfaces in scoped production paths. | Static/code-test scope only. |
| Artifact redaction excludes raw provider/prompt/source/PDF/cache body in tested incomplete-run cases. | No report content quality claim. |
| 401/403 provider-response classification remains residual if no dedicated mock evidence exists. | Not a blocker to source-policy L4 unless controller says otherwise. |
| Release/readiness remains `NOT_READY`. | Mandatory. |

## Forbidden Conclusions

| Forbidden conclusion | Reason |
|---|---|
| L4 no-live evidence proves live provider/LLM availability. | No live provider/network command is authorized. |
| L4 no-live evidence proves LLM content quality or chapter acceptance. | Negative/fail-closed evidence only. |
| L4 no-live evidence proves release/MVP/PR readiness. | Readiness remains separate and `NOT_READY`. |
| Source fallback, Eastmoney, CNINFO or fund-company fallback is authorized. | Current policy remains EID single-source/no fallback. |
| Provider defaults, runtime budget, retry or fallback semantics may change. | Requires implementation/design gate. |
| Artifact/report cleanup or ignore changes are authorized. | Separate artifact disposition gate only. |
| A clean lexical `rg` result proves all future source-policy behavior. | Static guard is bounded evidence, not universal proof. |

## Stop Conditions And Blockers

| Stop condition | Required action |
|---|---|
| Any future command attempts live provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR. | Stop; mark gate invalid/out of boundary. |
| Any real provider credential or ambient `FUND_AGENT_LLM_*` participates in future pytest run. | Stop; rerun only with env-cleared command if still authorized. |
| Any scoped provider/LLM production path imports or calls `FundDocumentRepository`, annual-report source helper, PDF downloader/cache, Eastmoney or CNINFO. | Stop; `BLOCKED`, route to implementation planning. |
| Any provider failure path falls back to deterministic report generation. | Stop; `BLOCKED`, route to Service/Agent fail-closed implementation planning. |
| Any provider failure path invokes annual-report fallback/source expansion. | Stop; `BLOCKED`, route to source-policy regression planning. |
| Any artifact retains prompt/raw provider payload/credentials/header/source body/PDF body/cache body. | Stop; `BLOCKED`, route to artifact redaction implementation planning. |
| Existing no-live tests do not cover the required negative behavior. | Mark as residual or blocker; do not infer behavior from unrelated passing tests. |
| Evidence path or test path is missing. | Route first to static read-preflight or implementation/test planning, not evidence acceptance. |
| Any conclusion implies readiness/release/PR/source expansion. | Reject conclusion; preserve `NOT_READY`. |

## Future Artifact / Write Set

Future evidence gate may write only:

| Path | Purpose |
|---|---|
| `docs/reviews/mvp-provider-llm-l4-negative-fail-closed-evidence-20260613.md` | No-live L4 evidence artifact. |
| `docs/reviews/mvp-provider-llm-l4-negative-fail-closed-evidence-review-ds-20260613.md` | DS review. |
| `docs/reviews/mvp-provider-llm-l4-negative-fail-closed-evidence-review-mimo-20260613.md` | MiMo review. |
| `docs/reviews/mvp-provider-llm-l4-negative-fail-closed-evidence-controller-judgment-20260613.md` | Controller judgment. |

No source/tests/runtime/design/README/fixture/manifest/golden files may be
modified by the evidence gate.

## Review Checklist

| Question | Expected answer |
|---|---|
| Does the plan preserve EID single-source/no fallback? | Yes |
| Does the plan keep all evidence no-live? | Yes |
| Does the plan distinguish provider diagnostic fallback fields from annual-report source fallback? | Yes |
| Does the plan require static guard plus tests, not pytest alone? | Yes |
| Does the plan keep 401/403 provider-response classification conservative? | Yes |
| Does the plan reject readiness/release/PR/source expansion claims? | Yes |
| Does the plan define blockers for direct source/PDF/cache access and fallback regressions? | Yes |

## Next Entry Recommendation

Recommended next mainline entry:

`Provider/LLM L4 Negative/Fail-closed Evidence Gate`

Use the exact future no-live command matrix above. If `rg --files` or static
reads show that the scoped code/test paths cannot support the matrix, route
first to:

`Provider/LLM L4 Static Read-preflight Gate`

The preflight gate should identify exact missing evidence/test surfaces without
modifying source/tests/runtime and should preserve EID single-source/no fallback
and `NOT_READY`.

Deferred entries:

- controlled live provider/LLM execution;
- no-live 401/403 provider-response mock evidence, unless controller requires closure before live;
- implementation/test-fix gate for any blocker found by L4 evidence;
- release/readiness execution or claim;
- PR/push/merge/mark-ready;
- cleanup/archive/ignore disposition;
- golden-answer promotion;
- fixture or manifest expansion;
- source expansion or fallback design.
