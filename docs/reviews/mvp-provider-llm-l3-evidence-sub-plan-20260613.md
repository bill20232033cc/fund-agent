# Provider/LLM L3 Evidence Sub-plan

Date: 2026-06-13

Gate: `Provider/LLM L3 Evidence Sub-plan Gate`

Status: `PLAN_READY_FOR_REVIEW_NOT_READY`

## Scope

This is a planning-only gate for L3 provider/LLM evidence.

The plan targets the explicit opt-in `--use-llm` Route C path and defines how to
produce bounded L3 evidence without changing runtime behavior.

This gate does not execute provider/LLM/live/network/PDF/FDR/analyze/checklist/
readiness/release commands. It does not modify source, tests, runtime behavior,
golden-answer content, fixtures, promotion manifests, design, README, release
state, PR state, cleanup, push, merge or external state.

Release/readiness remains `NOT_READY`.

## Goals

| Goal | Disposition |
|---|---|
| Plan no-live/static/contract evidence for current provider-backed `--use-llm` path. | ACCEPT |
| Verify evidence boundaries for config, Service request/runtime plan, Host wrapper, Agent body runner, Fund writer/auditor protocol, provider failure mapping and artifact redaction. | ACCEPT |
| Define future controlled live provider/LLM execution boundaries if static evidence later justifies it. | ACCEPT_WITH_FUTURE_GATE |
| Preserve EID single-source/no-fallback source policy. | ACCEPT |
| Preserve `NOT_READY`. | ACCEPT |

## Non-goals

| Non-goal | Reason |
|---|---|
| Execute provider/LLM/live/network/PDF/FDR/analyze/checklist/readiness/release commands. | This is planning-only. |
| Prove provider/LLM readiness. | L3 evidence is unrun. |
| Prove release/MVP readiness. | Readiness gates remain separate and `NOT_READY`. |
| Change provider default, runtime budget, retry, fallback or source policy. | Runtime/source policy changes require separate reviewed gates. |
| Reintroduce Eastmoney, CNINFO or fund-company fallback. | Current operational source remains EID single-source/no fallback. |
| Promote golden/fixture/manifest content. | Separate golden/fixture gates only. |
| Cleanup/archive/ignore artifacts. | Separate artifact disposition gate only. |
| PR/push/merge/mark-ready. | External-state actions require explicit authorization. |

## Truth Inputs

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth and gate boundary. |
| `docs/current-startup-packet.md` | Current active gate and `NOT_READY` posture. |
| `docs/implementation-control.md` | Control truth for accepted checkpoints and residuals. |
| `docs/design.md` | Design truth for current `--use-llm` Route C boundary. |
| `docs/reviews/mvp-controlled-live-provider-evidence-plan-controller-judgment-20260613.md` | Accepted L0-L2/L5 plan and L3/L4 deferral. |
| `docs/reviews/mvp-controlled-live-provider-evidence-execution-controller-judgment-20260613.md` | Accepted bounded live L0-L2/L5 facts and L3/L4 residuals. |
| `docs/reviews/mvp-live-evidence-ready-state-disposition-refresh-after-provider-execution-controller-judgment-20260613.md` | Accepted next entry and planning-only L3 boundary. |

## Static Read Scope

| Path | Purpose |
|---|---|
| `fund_agent/config/llm.py` | Typed env config and fail-closed validation. |
| `fund_agent/services/llm_provider.py` | OpenAI-compatible provider adapter and failure mapping. |
| `fund_agent/services/fund_analysis_service.py` | Service `--use-llm` orchestration and request validation. |
| `fund_agent/services/execution_contract.py` | Typed LLM execution request/runtime contract. |
| `fund_agent/services/chapter_orchestrator.py` | Service-to-Agent/Fund orchestration and stop reasons. |
| `fund_agent/services/agent_bridge.py` | Service bridge to Agent runner. |
| `fund_agent/services/llm_run_artifacts.py` | Incomplete LLM artifact safety/redaction. |
| `fund_agent/host/runtime.py` | Host lifecycle/deadline wrapper behavior. |
| `fund_agent/agent/runner.py` | Agent body runner contract. |
| `fund_agent/fund/chapter_writer.py` | Fund writer typed protocol. |
| `fund_agent/fund/chapter_auditor.py` | Fund auditor typed protocol. |
| `fund_agent/ui/cli.py` | CLI opt-in surface and fail-closed exit behavior. |
| `tests/config/test_llm_config.py` | Config evidence tests. |
| `tests/services/test_llm_provider.py` | Provider adapter evidence tests. |
| `tests/services/test_execution_contract.py` | Execution contract evidence tests. |
| `tests/services/test_fund_analysis_service_llm.py` | Service LLM route evidence tests. |
| `tests/services/test_chapter_orchestrator.py` | Orchestration/failure evidence tests. |
| `tests/services/test_llm_run_artifacts.py` | Redaction/artifact safety evidence tests. |
| `tests/agent/*` and `tests/host/*` | Agent/Host boundary evidence tests. |

## Evidence Matrix

| Row | Evidence target | Method | Allowed conclusion | Forbidden conclusion |
|---|---|---|---|---|
| L3-S0 | Control boundary | Read current control docs and accepted judgments. | L3 plan/static evidence may proceed. | Provider/LLM execution is authorized. |
| L3-S1 | Static path map | `rg`/file reads over CLI, Service, Host, Agent, Fund and provider adapter. | `--use-llm` path is explicit opt-in and provider-backed. | Default deterministic path uses provider. |
| L3-S2 | Config contract | Read config code and run config tests in future no-live gate. | Required env/config validation is fail-closed. | Provider is ready live. |
| L3-S3 | Execution request/runtime contract | Read Service/contract code and run execution/service tests in future no-live gate. | Request/runtime plan fields are typed and explicit. | Runtime behavior should change. |
| L3-S4 | Provider adapter contract | Read adapter and run provider adapter tests in future no-live gate. | OpenAI-compatible adapter maps errors to typed safe diagnostics. | Live provider availability is proven. |
| L3-S5 | Agent/Fund protocol contract | Read Agent/Fund protocols and run no-live orchestration/agent tests. | Writer/auditor consume typed protocols and fail closed on contract gaps. | LLM content quality is accepted. |
| L3-S6 | Diagnostics/artifact safety | Read artifact writer and run artifact tests. | Incomplete artifacts exclude prompts/raw provider payload/credentials. | Artifacts prove readiness. |
| L3-S7 | Unexpected source access guard | Static import/grep guard over provider/LLM layers. | Provider/LLM layer avoids source/PDF/cache/fallback access. | Source policy can expand. |
| L3-LIVE-FUTURE | Future controlled live provider/LLM execution | Separate gate only after static evidence acceptance and explicit authorization. | Future live command can be planned with strict limits. | Current gate may execute live provider/LLM. |

## Failure Classification

| Failure | Classification | Disposition |
|---|---|---|
| Missing or invalid provider config | `CONFIG_FAIL_CLOSED` | Accept only as fail-closed evidence; not readiness proof. |
| Missing API key env or 401/403 | `AUTH_BLOCKED` | Do not retry; do not store key/header/body. |
| Network, 5xx or 429 provider failure | `PROVIDER_UNAVAILABLE` | No deterministic fallback; record typed safe category only. |
| Non-auth 4xx, invalid model or bad endpoint | `PROVIDER_REQUEST_REJECTED` | Fail closed; no retry; safe diagnostic only; not readiness proof. |
| Timeout | `LLM_TIMEOUT` | Respect configured policy; future live must use single attempt. |
| Malformed JSON or missing `choices[0].message.content` | `PROVIDER_SCHEMA_DRIFT` | Fail closed. |
| Audit protocol parse failure or typed contract mismatch | `LLM_CONTRACT_VIOLATION` | Fail closed; blocker for acceptance. |
| Empty/incomplete/model-blocked output | `MODEL_OUTPUT_BLOCKED` | May use existing repair budget only; no budget expansion. |
| Host/Agent bridge mismatch | `CONTRACT_MISMATCH` | Blocker until separately fixed. |
| Direct PDF/cache/source/fallback/Eastmoney/CNINFO access from provider/LLM layer | `UNEXPECTED_SOURCE_ACCESS` | Blocker; source policy violation. |
| Credential, prompt, raw provider payload or header leakage | `SENSITIVE_DATA_LEAK` | Blocker; stop immediately. |

## Allowed Commands

Current planning/review gate:

```bash
git status --branch --short
git status --short
git diff --check
rg -n "<pattern>" AGENTS.md docs/current-startup-packet.md docs/implementation-control.md docs/design.md docs/reviews fund_agent tests README.md
rg --files fund_agent tests
sed -n '<range>p' <allowed-text-file>
```

Future no-live static/contract evidence gate may authorize:

```bash
rg -n "analyze_with_llm|build_fund_llm_execution_request|build_chapter_llm_clients|HostRunResult|run_agent_report|OpenAICompatibleChapterLLMClient|ChapterLLMRequest|ChapterAuditLLMRequest|write_llm_run_artifacts" fund_agent tests
rg -n "fund_agent\\.fund\\.documents|FundDocumentRepository|Eastmoney|CNINFO|fallback_used|download|cache|pdf" fund_agent/config fund_agent/services fund_agent/agent fund_agent/host tests/config tests/services tests/agent tests/host
rg -n "MockTransport|_provider_client|FUND_AGENT_LLM_|monkeypatch|transport=httpx.MockTransport|raw provider|prompt.*canary|RAW_AUDITOR_RESPONSE_CANARY|SYSTEM_PROMPT_CANARY|USER_PROMPT_CANARY" tests/config tests/services
uv run pytest tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent/test_runner.py tests/agent/test_service_bridge.py tests/host/test_runtime_runner.py -q
uv run ruff check fund_agent/config/llm.py fund_agent/services/llm_provider.py fund_agent/services/execution_contract.py fund_agent/services/fund_analysis_service.py fund_agent/services/chapter_orchestrator.py fund_agent/services/agent_bridge.py fund_agent/services/llm_run_artifacts.py fund_agent/agent fund_agent/host tests/config/test_llm_config.py tests/services/test_llm_provider.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/agent tests/host
```

Future no-live evidence guardrails:

- Real provider credentials must not participate in the test run.
- Provider/network HTTP must not occur.
- Provider interactions must be local fakes or injected mocks such as
  `httpx.MockTransport`.
- Any real network/provider attempt is a `BLOCKER` and must stop the evidence
  gate.
- Tests must not rely on ambient `FUND_AGENT_LLM_*` from the user environment;
  they must clear, override or monkeypatch provider env as local test data.
- The static `rg` rows above are part of the future no-live evidence matrix for
  L3-S1 and L3-S7; pytest/ruff alone are not sufficient to close those rows.

## Future Controlled Live Provider/LLM Gate

This plan does not authorize future live execution. If later authorized by a
separate accepted gate, use a single sample and strict limits.

Candidate command template:

```bash
uv run fund-analysis analyze 004393 --report-year 2025 --use-llm --quality-gate-policy warn --valuation-state unavailable --no-llm-progress
```

Required future live limits:

| Limit | Value |
|---|---|
| Global timeout | 15 minutes |
| Provider single-request timeout | no more than 60 seconds |
| Provider attempts | `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS=1` |
| Retry | 0 |
| stdout/stderr retention | no more than 80 lines or 12 KiB per command |
| Artifact retention | exit code, safe run id, Host terminal status, chapter matrix, safe runtime categories, redaction result |
| Forbidden retention | raw prompts, raw provider payload, headers, credentials, API keys, tokens, raw PDF/cache body, accepted final report body |

Future live stop conditions:

- credential, raw prompt, raw provider body, header or token leakage;
- unexpected Eastmoney/CNINFO/fallback/source/cache/PDF access;
- `fallback_used=true`;
- provider retry beyond 0;
- sample broader than exact authorized sample;
- release/readiness claim;
- accepted final report body written as evidence artifact;
- provider/LLM evidence used to alter source policy.

## Forbidden Commands / Actions

- `fund-analysis analyze`
- `fund-analysis checklist`
- `fund-analysis analyze-annual-period`
- provider/LLM live calls
- network probes
- PDF/FDR/source/cache helper calls
- readiness/release/checklist/score-loop/golden promotion commands
- cleanup/archive/ignore
- stage/commit/push/PR/merge/mark-ready unless the controller is committing accepted planning artifacts
- reading PDF bodies, raw provider payload, credentials, headers, tokens or local private cache body
- modifying source/tests/runtime/design/README/fixtures/manifest/golden

## Artifact / Write Set

Current planning gate write set:

| Path | Purpose |
|---|---|
| `docs/reviews/mvp-provider-llm-l3-evidence-sub-plan-20260613.md` | Plan artifact. |
| `docs/reviews/mvp-provider-llm-l3-evidence-sub-plan-review-ds-20260613.md` | DS plan review. |
| `docs/reviews/mvp-provider-llm-l3-evidence-sub-plan-review-mimo-20260613.md` | MiMo plan review. |
| `docs/reviews/mvp-provider-llm-l3-evidence-sub-plan-controller-judgment-20260613.md` | Controller judgment. |

Control-doc sync after accepted checkpoint may update:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Future no-live evidence gate must use separate evidence/review/controller
artifacts. Future live evidence gate must use a separate accepted plan and
explicit authorization.

## Review Checklist

| Question | Expected answer |
|---|---|
| Does the plan keep L3 as planning/static evidence, not readiness proof? | Yes |
| Does it preserve `NOT_READY`? | Yes |
| Does it cover config, request/runtime plan, provider adapter, Host/Agent bridge, Fund writer/auditor, artifact redaction and source-access guard? | Yes |
| Does every failure category fail closed or defer safely? | Yes |
| Does it forbid source policy drift, Eastmoney/CNINFO/fallback and direct PDF/cache access? | Yes |
| Does it define future live command/timeout/retry/retention/redaction/stop conditions without authorizing execution now? | Yes |
| Does it avoid release/readiness, PR, cleanup, golden/fixture/manifest claims? | Yes |

## Acceptance Criteria

| Criterion | Required result |
|---|---|
| Plan is executable as a future no-live static/contract evidence gate. | PASS |
| Each matrix row has input paths, method, allowed conclusion and forbidden conclusion. | PASS |
| All failure categories have fail-closed or deferred dispositions. | PASS |
| Future live provider/LLM execution is isolated behind a separate gate. | PASS |
| Future no-live evidence uses fake env / mocked provider transport and no network. | PASS |
| Provider/LLM readiness remains unproven. | PASS |
| Release/readiness remains `NOT_READY`. | PASS |

## Next Entry Recommendation

Recommended next mainline entry:

`Provider/LLM L3 No-live Static/Contract Evidence Gate`

This next gate may run only the accepted no-live static/contract validation
matrix after this plan is reviewed and accepted.

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
