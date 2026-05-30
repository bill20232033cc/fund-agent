# MVP Gate 4 Slice 4D provider construction plan decision

日期：2026-05-30
角色：phaseflow / gateflow controller
Gate：`MVP Gate 4 Slice 4D: production LLM provider construction plan gate`
分类：`heavy`

## Verdict

**PLAN ACCEPTED WITH CONTROLLER AMENDMENTS**

`docs/reviews/mvp-gate4-provider-construction-plan-20260530.md` 可作为 Slice 4D implementation source plan，但 implementation worker 必须遵守本文 amendments。本文不授权直接 push / PR / merge / release，不授权 Host/Agent/dayu，不授权 final judgment、quality/FQ、golden、score、snapshot、manifest 或 promotion 变更。

## Review Inputs

- Plan: `docs/reviews/mvp-gate4-provider-construction-plan-20260530.md`
- MiMo review: `docs/reviews/mvp-gate4-provider-construction-plan-review-mimo-20260530.md`
- GLM review: `docs/reviews/mvp-gate4-provider-construction-plan-review-glm-20260530.md`
- Control truth: `docs/current-startup-packet.md`, `docs/implementation-control.md`
- Design truth: `docs/design.md`
- Prior decision: `docs/reviews/mvp-gate4-cli-use-llm-controller-judgment-20260530.md`

## Controller Amendments

### A1. Provider Choice Signed Off

Controller accepts `openai_compatible` HTTP chat-completions over existing `httpx` as the MVP provider protocol.

This is a protocol-family decision, not a default vendor/model decision. Implementation must not hard-code a default model, default base URL, default vendor, or fallback provider. Deployment must explicitly provide provider/model/base URL/API key through typed env config.

If implementation discovers the target runtime cannot use an OpenAI-compatible chat-completions endpoint, stop before code changes and return to controller/user for provider policy decision.

### A2. Audit Prompt Boundary

The provider adapter must not reconstruct, extend, or duplicate the Gate 2 `SEVERITY|LOCATION|MESSAGE` audit protocol.

`ChapterAuditLLMRequest.user_prompt` is the frozen Gate 2 audit prompt truth. The adapter may package `system_prompt`, `user_prompt` and `draft_markdown` into the provider request body, but must not invent another audit protocol layer or modify the protocol text. If the adapter needs to include `draft_markdown`, it must do so without changing `request.user_prompt` semantics.

### A3. `ChapterOrchestrationPolicy.max_output_chars` Confirmed

`ChapterOrchestrationPolicy` already has `max_output_chars: int = 12000`; Slice 4D may pass `config.max_output_chars` into it. No pre-work in `chapter_orchestrator.py` is needed for this field.

### A4. API Key Empty String Is Missing

`load_llm_provider_config_from_env()` must treat an empty or whitespace-only API key env value as missing and raise `LLMProviderConfigError`. It must never construct `LLMProviderConfig(api_key="")`, and errors/repr must never print the secret value.

### A5. CLI Temporary Unavailable Error Removal

Slice 4D2 should remove the temporary CLI-only `LLMProviderUnavailableError` class and `LLM_PROVIDER_UNAVAILABLE_MESSAGE` constant introduced by Slice 4C. Provider fail-closed paths should use typed config/construction/runtime errors from `fund_agent.config.llm` and `fund_agent.services.llm_provider`.

The CLI may keep a local helper named `_build_llm_clients_or_fail()`, but after 4D2 it must return `(ChapterOrchestratorLLMClients, ChapterOrchestrationPolicy)` and no longer have `NoReturn` semantics.

### A6. Config Import Path

Do not re-export the new LLM config types from `fund_agent/config/__init__.py` in Slice 4D1. Use direct imports from `fund_agent.config.llm`, matching the current `fund_agent.config.paths` import style. If future config package conventions change, handle that in a separate consistency gate.

### A7. Runtime Error Detail

Provider runtime errors may include safe operational detail such as HTTP status code and request-id header if present. They must not include API key values, Authorization headers, prompt bodies, full response bodies, or user secrets.

### A8. Design/Control Timing

`docs/design.md`, `docs/current-startup-packet.md` and `docs/implementation-control.md` may be updated in Slice 4D3 only after implementation and review acceptance for the provider-backed path. Do not write provider construction as current code fact during 4D1 or 4D2 evidence.

## Accepted Slice Sequence

1. **4D1: typed config and provider factory**
   - Add `fund_agent/config/llm.py`.
   - Add `fund_agent/services/llm_provider.py`.
   - Add config/provider tests using fake env and `httpx.MockTransport`.
   - Do not change CLI behavior yet.

2. **4D2: CLI `--use-llm` provider-backed wiring**
   - Replace the temporary fail-closed helper with typed config/factory construction.
   - Call `FundAnalysisService().analyze_with_llm(...)` only when config/client construction succeeds.
   - Preserve deterministic default `analyze` and `checklist`.

3. **4D3: docs/control sync and full regression**
   - Update user/dev/config/test docs and design/control startup only after 4D1/4D2 implementation reviews pass.
   - Keep Host/Agent/dayu deferred.

## Residuals

- No retry/backoff policy in MVP; provider runtime errors fail closed.
- One model is used for writer and auditor in MVP; split writer/auditor model config is a future gate.
- No live provider smoke in pytest. Any live smoke must be manual or a separate explicitly authorized evidence gate.
- Chapter 0/7 LLM polish, Evidence Confirm, Host/Agent/dayu and full `FundToolService` remain future gates.

## Next Entry Point

`MVP Gate 4 Slice 4D1: typed LLM config and provider factory implementation gate`
