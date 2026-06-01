# MVP provider runtime timeout hardening plan controller judgment

日期：2026-05-31

Gate：`MVP provider runtime timeout hardening plan gate`

角色：Phaseflow controller。本文记录 plan/review 裁决，不实现代码，不 push、不创建或更新 PR、不 merge、不 release。

## Judgment

结论：`accepted_for_implementation`

真实 provider smoke timeout 已复现，且位置可变。后续实现应按 accepted plan 处理 provider runtime timeout hardening，而不是重新归因 provider auth/config、放松 writer/auditor contract 或引入 deterministic fallback。

## Evidence

- Plan：`docs/reviews/mvp-provider-runtime-timeout-hardening-plan-20260531.md`
- MiMo review：`docs/reviews/mvp-provider-runtime-timeout-hardening-plan-review-mimo-20260531.md`
- GLM review：`docs/reviews/mvp-provider-runtime-timeout-hardening-plan-review-glm-20260531.md`
- MiMo re-review：`docs/reviews/mvp-provider-runtime-timeout-hardening-plan-rereview-mimo-20260531.md`
- GLM re-review：`docs/reviews/mvp-provider-runtime-timeout-hardening-plan-rereview-glm-20260531.md`
- Timeout rerun judgment：`docs/reviews/mvp-real-provider-smoke-timeout-rerun-controller-judgment-20260531.md`

MiMo / GLM initial review raised blocking issues around diagnostic placement and Fund Protocol propagation. Controller accepted those findings. Revised plan moved diagnostics to Service layer, explicitly forbids Fund Protocol request/response/signature changes, and defines orchestrator enrichment. Both re-reviews are `PASS`.

## Accepted Plan Boundaries

Implementation is allowed to modify only:

- `fund_agent/config/llm.py`
- `fund_agent/services/llm_provider.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/__init__.py` only if diagnostic type export is necessary
- `fund_agent/ui/cli.py`
- related tests listed in the plan
- docs listed in the plan only for current env / CLI wording sync

Implementation must not modify:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- Fund-layer LLM request/response dataclasses or Protocol signatures
- golden / fixtures / score / quality gate / snapshot / promotion / manifest
- `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`
- `docs/fund-analysis-template-draft.md`, `AGENTS.md`
- Host/Agent/dayu files

## Required Implementation Semantics

- Timeout-only bounded retry; no retry for rate limit, malformed response, network, prompt_contract, audit_parse, fact_gap or code_bug.
- `timeout_max_attempts` and `timeout_backoff_seconds` are typed env config fields.
- Retry count is per `_complete()` call; writer/auditor may share the same client instance but retry counters are not shared across calls.
- Provider-level diagnostics carry only provider-safe fields and no chapter identity.
- Orchestrator enriches diagnostics with chapter identity and maps `provider_runtime_category` to `chapter_failure_category`.
- CLI incomplete message must include a safe first failed chapter summary: id/status/stop_reason.
- No deterministic fallback; stdout remains empty on LLM incomplete/failure.
- Default deterministic `analyze/checklist` remains unchanged.

## Next Step

派发 implementation worker 按 accepted plan 实现，并产出：

`docs/reviews/mvp-provider-runtime-timeout-hardening-implementation-evidence-20260531.md`

Implementation completion must include ruff, targeted tests, full coverage, missing-config smoke, deterministic smoke, real provider `006597 / 2024 --use-llm` rerun, diagnostic JSON and secret scan.
