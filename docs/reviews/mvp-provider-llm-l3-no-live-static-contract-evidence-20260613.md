# Provider/LLM L3 No-live Static/Contract Evidence

Date: 2026-06-13

Gate: `Provider/LLM L3 No-live Static/Contract Evidence Gate`

Status: `EVIDENCE_READY_FOR_REVIEW_NOT_READY`

## Scope

This evidence gate executed the accepted no-live static/contract matrix from
`docs/reviews/mvp-provider-llm-l3-evidence-sub-plan-20260613.md`.

This gate did not run live provider/LLM commands. It did not run network, PDF,
FDR, source, analyze, checklist, readiness, release, PR, push, merge, cleanup or
external-state commands. It did not modify source, tests, runtime behavior,
manifest, fixture, golden-answer content, README or design truth.

Release/readiness remains `NOT_READY`.

## Inputs

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth and no-direct-source/no-fallback boundary. |
| `docs/current-startup-packet.md` | Active gate and `NOT_READY` posture. |
| `docs/implementation-control.md` | Control truth for current gate and allowed write set. |
| `docs/design.md` | Design truth for explicit opt-in provider-backed `--use-llm` route. |
| `docs/reviews/mvp-provider-llm-l3-evidence-sub-plan-controller-judgment-20260613.md` | Accepted plan/controller basis for this matrix. |
| `fund_agent/config/llm.py` | Typed provider config and fail-closed env validation surface. |
| `fund_agent/services/llm_provider.py` | OpenAI-compatible provider adapter and safe diagnostic mapping. |
| `fund_agent/services/fund_analysis_service.py` | Service-owned LLM request/runtime assembly and Host entry. |
| `fund_agent/services/execution_contract.py` | Typed execution request/runtime contract. |
| `fund_agent/services/chapter_orchestrator.py` | Service orchestration to Agent/Fund body execution. |
| `fund_agent/services/agent_bridge.py` | Service bridge to Agent body runner. |
| `fund_agent/services/llm_run_artifacts.py` | Incomplete-run artifact redaction and safe payload writer. |
| `fund_agent/agent/`, `fund_agent/host/` | Agent/Host boundary code under static/contract validation. |
| `tests/config/`, `tests/services/`, `tests/agent/`, `tests/host/` | No-live contract tests with fake env/mocks. |

## Commands

| Command | Result | Evidence use |
|---|---:|---|
| `git status --branch --short` | exit 0 | Branch preflight; tracked diff was clean before evidence write; existing untracked residue remained visible. |
| `git diff --name-only` | exit 0, empty | Ancillary read-only preflight; not part of the accepted L3 matrix command set. Confirmed no tracked diff before evidence write. |
| `rg -n "analyze_with_llm\|build_fund_llm_execution_request\|build_chapter_llm_clients\|HostRunResult\|run_agent_report\|OpenAICompatibleChapterLLMClient\|ChapterLLMRequest\|ChapterAuditLLMRequest\|write_llm_run_artifacts" fund_agent tests` | exit 0 | L3-S1 static path map. |
| `rg -n "fund_agent\\.fund\\.documents\|FundDocumentRepository\|Eastmoney\|CNINFO\|fallback_used\|download\|cache\|pdf" fund_agent/config fund_agent/services fund_agent/agent fund_agent/host tests/config tests/services tests/agent tests/host` | exit 0 | L3-S7 source-access guard. |
| `rg -n "MockTransport\|_provider_client\|FUND_AGENT_LLM_\|monkeypatch\|transport=httpx.MockTransport\|raw provider\|prompt.*canary\|RAW_AUDITOR_RESPONSE_CANARY\|SYSTEM_PROMPT_CANARY\|USER_PROMPT_CANARY" tests/config tests/services` | exit 0 | Fake-env/mock-provider/redaction guard. |
| `env -u FUND_AGENT_LLM_PROVIDER ... -u FUND_AGENT_LLM_MAX_OUTPUT_CHARS uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py tests/agent/test_service_bridge.py tests/host/test_runtime_runner.py -q` | exit 0, `238 passed in 1.11s` | No-live L3 static/contract test matrix with provider env cleared. |
| `uv run ruff check fund_agent/config/llm.py fund_agent/services/llm_provider.py fund_agent/services/execution_contract.py fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/agent_bridge.py fund_agent/services/llm_run_artifacts.py fund_agent/agent fund_agent/host tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent tests/host` | exit 0, `All checks passed!` | Lint validation for L3 contract paths. |

The pytest command intentionally cleared ambient `FUND_AGENT_LLM_*`
environment variables. Provider interactions in the tested provider adapter are
local mocks such as `httpx.MockTransport`; no real provider credential or live
provider/network call is accepted by this evidence.

## Evidence Matrix

| Row | Evidence observed | Disposition |
|---|---|---|
| L3-S0 Control boundary | Startup/control docs identify this active gate as no-live static/contract evidence; accepted sub-plan controller judgment forbids live provider/LLM and preserves `NOT_READY`. | PASS |
| L3-S1 Static path map | Static search traces explicit `--use-llm`/Route C path through Service request assembly, provider client builder, Host result projection, Agent runner, Fund writer/auditor typed requests and incomplete artifact writer. | PASS |
| L3-S2 Config contract | `tests/config/test_llm_config.py` passed under env-cleared execution; config tests cover provider value, required env, timeout ceilings/backoff/output char limits and API key handling. | PASS |
| L3-S3 Execution request/runtime contract | `tests/services/test_execution_contract.py` and `tests/services/test_fund_analysis_service_llm.py` passed; request/runtime plan fields are typed and explicit, with request validation before provider construction. | PASS |
| L3-S4 Provider adapter contract | `tests/services/test_llm_provider.py` passed using `httpx.MockTransport`; provider responses and failures map to typed safe diagnostics without live provider access. | PASS |
| L3-S5 Agent/Fund protocol contract | `tests/services/test_chapter_orchestrator.py`, `tests/agent/test_runner.py`, `tests/agent/test_service_bridge.py` and `tests/host/test_runtime_runner.py` passed; writer/auditor protocols are typed and fail closed through Service/Agent/Host tests. | PASS |
| L3-S6 Diagnostics/artifact safety | `tests/services/test_llm_run_artifacts.py` passed; canary checks cover prompt/raw provider payload exclusion from incomplete-run artifacts. | PASS |
| L3-S7 Unexpected source access guard | Static guard found no provider/LLM-layer import of `fund_agent.fund.documents`, `FundDocumentRepository`, Eastmoney or CNINFO in the scoped L3 provider paths. Matches for `cache`, `pdf`, `download` are lexical references in config path constants, thermometer cache code/tests, README/guard comments, redaction/fallback diagnostic fields, or tests asserting these terms are not leaked. | PASS_WITH_INTERPRETATION |

## Source-access Guard Disposition

| Observed match class | Disposition | Reason |
|---|---|---|
| `fund_agent/services/llm_provider.py` `repair_timeout_fallback_used` fields | ACCEPT_NON_SOURCE | This is provider timeout diagnostic fallback, not annual-report source fallback. |
| `fund_agent/services/llm_run_artifacts.py` `repair_timeout_fallback_used` serialization | ACCEPT_NON_SOURCE | This persists safe diagnostic metadata only. |
| `fund_agent/services/fund_analysis_service.py` docstring stating Service does not read repository/PDF/cache/helper | ACCEPT_GUARD | The match is an explicit boundary statement, not access. |
| `fund_agent/services/chapter_orchestrator.py` and `final_chapter_assembler.py` module docstrings | ACCEPT_GUARD | The matches state no repository/PDF/cache/source-helper access. |
| `fund_agent/config/paths.py` default cache constants and `tests/config/test_paths.py` | ACCEPT_OUTSIDE_PROVIDER_LLM | Config path constants are not provider/LLM source acquisition. |
| `fund_agent/services/thermometer_service.py` and thermometer tests | ACCEPT_OUTSIDE_L3_PROVIDER_ROUTE | Thermometer cache behavior is outside the L3 provider/LLM route and not annual-report PDF/source fallback. |
| Tests containing forbidden terms such as `cache`, `pdf`, `downloader` | ACCEPT_GUARD | These tests assert forbidden source/cache/PDF terms are not introduced into LLM request/runtime payloads. |
| `FundDocumentRepository`, Eastmoney, CNINFO | NO_BLOCKING_PROVIDER_MATCH | No scoped provider/LLM production path import/use was observed. |

## Failure Classification Evidence

| Failure class from accepted plan | Evidence status | Disposition |
|---|---|---|
| `CONFIG_FAIL_CLOSED` | Config tests passed under fake env values and env-cleared command shell. | ACCEPT_NO_LIVE |
| `AUTH_BLOCKED` | Missing API key/config fail-closed behavior is covered by config/service tests. Current no-live evidence does not separately prove 401/403 provider-response classification. | ACCEPT_PARTIAL_WITH_RESIDUAL |
| `PROVIDER_UNAVAILABLE` | Provider tests cover unavailable/429/5xx-style diagnostics through mocked transport. | ACCEPT_NO_LIVE |
| `PROVIDER_REQUEST_REJECTED` | Provider tests cover non-auth 4xx rejected request behavior through mocked transport. This is accepted as the plan-level classification for rejected provider requests, not as a distinct current runtime enum. | ACCEPT_NO_LIVE_WITH_CLASSIFICATION_LIMIT |
| `LLM_TIMEOUT` | Provider timeout/retry diagnostics are covered by provider tests and config timeout controls. | ACCEPT_NO_LIVE |
| `PROVIDER_SCHEMA_DRIFT` | Provider tests cover malformed/missing provider response shape through mocked responses. | ACCEPT_NO_LIVE |
| `LLM_CONTRACT_VIOLATION` | Orchestrator/service/agent contract tests passed. | ACCEPT_NO_LIVE |
| `MODEL_OUTPUT_BLOCKED` | Orchestrator and service fail-closed tests passed. | ACCEPT_NO_LIVE |
| `CONTRACT_MISMATCH` | Service/Host/Agent boundary tests passed. | ACCEPT_NO_LIVE |
| `UNEXPECTED_SOURCE_ACCESS` | Static source-access guard found no blocking provider/LLM direct source access. | ACCEPT_NO_LIVE_WITH_STATIC_LIMIT |
| `SENSITIVE_DATA_LEAK` | Artifact canary tests passed; prompts/raw provider payload are excluded. | ACCEPT_NO_LIVE |

## Accepted Facts

| Fact | Disposition |
|---|---|
| The current `--use-llm` path is explicit opt-in and provider-backed under Service-owned request/runtime assembly. | ACCEPT_STATIC_CONTRACT_FACT |
| The no-live L3 matrix passed with provider env cleared and local mock provider transport. | ACCEPT_NO_LIVE_FACT |
| Current provider adapter tests exercise OpenAI-compatible request/response/error mapping without live provider calls. | ACCEPT_NO_LIVE_FACT |
| Incomplete LLM run artifact tests support redaction of prompts and raw provider payload canaries. | ACCEPT_NO_LIVE_FACT |
| Static guard did not find a blocking annual-report source/PDF/cache/fallback import or Eastmoney/CNINFO use in scoped provider/LLM production paths. | ACCEPT_STATIC_GUARD_FACT |
| Release/readiness remains `NOT_READY`. | ACCEPT_CONTROL_FACT |

## Rejected Claims

| Claim | Disposition | Reason |
|---|---|---|
| This evidence proves live provider/LLM availability. | REJECT | No live provider/LLM execution was run. |
| This evidence proves LLM content quality or chapter acceptance. | REJECT | Tests use fakes/mocks and contract assertions only. |
| This evidence proves release/MVP readiness. | REJECT | Readiness gates remain separate and `NOT_READY`. |
| This evidence authorizes provider default/config/runtime budget changes. | REJECT | No source/runtime behavior was changed. |
| This evidence authorizes source fallback, Eastmoney, CNINFO or additional acquisition. | REJECT | Source policy remains EID single-source/no fallback. |
| This evidence authorizes PR, push, merge, cleanup, archive or ignore changes. | REJECT | External-state and artifact-disposition gates remain separate. |

## Residuals

| Residual | Classification | Owner | Next handling |
|---|---|---|---|
| Live provider/LLM execution remains unrun. | provider/live residual | User/controller + provider runtime owner | Separate controlled live provider/LLM gate only with explicit authorization. |
| LLM content quality remains unaccepted. | quality/content residual | Provider/runtime + chapter owners | Separate live/content acceptance evidence if authorized. |
| L4 negative/fail-closed source behavior remains unplanned/unrun. | source negative evidence residual | Source evidence owner | Separate negative/fail-closed L4 evidence sub-plan. |
| Release/readiness remains unproven. | readiness blocker | Release owner/controller | Separate readiness/release gate only; current state remains `NOT_READY`. |
| Existing untracked artifact/report residue remains visible. | artifact hygiene residual | Artifact owners/controller | Separate artifact disposition/cleanup gate only. |
| 401/403 provider-response classification remains unproven by this no-live matrix. | provider classification residual | Provider/runtime owner | Future no-live mock evidence or implementation gate only if controller accepts it as necessary. |

## Conclusion

The accepted no-live L3 static/contract matrix passed.

This supports a bounded conclusion: the current explicit opt-in provider-backed
`--use-llm` path has no-live static/contract evidence for typed config, Service
request/runtime assembly, provider adapter diagnostics, Host/Agent/Fund protocol
boundaries, artifact redaction and static source-access guardrails.

It does not prove live provider availability, LLM output quality, release
readiness, source expansion or PR readiness.

Recommended next entry:

`Provider/LLM L3 No-live Static/Contract Evidence Review Gate`

Deferred entries:

- controlled live provider/LLM execution;
- negative/fail-closed L4 evidence sub-plan;
- additional live sample expansion;
- release/readiness execution or claim;
- PR/push/merge/mark-ready;
- cleanup/archive/ignore disposition;
- golden-answer promotion;
- fixture or manifest expansion;
- source expansion or fallback design.
