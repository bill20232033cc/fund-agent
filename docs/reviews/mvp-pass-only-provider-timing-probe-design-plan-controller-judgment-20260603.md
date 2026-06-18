# MVP PASS-only provider timing probe design plan controller judgment

- Role: controller
- Gate: `MVP PASS-only provider timing probe design gate`
- Classification: heavy
- Date: 2026-06-03
- Verdict: accepted as design-only

## Inputs

- Plan: `docs/reviews/mvp-pass-only-provider-timing-probe-design-plan-20260603.md`
- Reviews:
  - `docs/reviews/mvp-pass-only-provider-timing-probe-design-plan-review-a-20260603.md`
  - `docs/reviews/mvp-pass-only-provider-timing-probe-design-plan-review-b-20260603.md`
- Prior judgment:
  - `docs/reviews/mvp-post-repair-provider-endpoint-disposition-evidence-slice-controller-judgment-20260603.md`
- Code facts read for feasibility:
  - `fund_agent/services/llm_provider.py`
  - `fund_agent/fund/chapter_auditor.py`

## Judgment

The plan is accepted as a design-only gate. Both independent reviews returned PASS with no blocking findings.

This judgment does not authorize a live PASS-only probe. The next gate must first pin an exact evidence harness contract, including temporary script path/content or dev-only helper, exact synthetic request fields, output schema, config-clone method, thresholding rules and secret-scan command.

## Controller Answers

1. Accepted probe name: `single-attempt current-timeout PASS-only probe`. It must not be called a default-budget probe.
2. Attempt policy: future harness may clone the loaded config in memory with `timeout_max_attempts=1` and `timeout_backoff_seconds=0`, using the current effective auditor timeout seconds. This is probe-local measurement policy only, not a provider default/runtime behavior change.
3. Synthetic `ChapterAuditLLMRequest` fields authorized for the future harness:
   - `chapter_id=0`
   - `fund_code="PASS_ONLY_PROBE"`
   - `report_year=0`
   - `system_prompt="Return exactly PASS."`
   - `user_prompt="PASS"`
   - `draft_markdown="PASS"`
   - `allowed_fact_ids=()`
   - `allowed_anchor_ids=()`
   - `audit_focus=()`
4. No-body evidence rule: future harness must use allowlist output by construction. It may compute `len(response.raw_text)` and must then discard the response object. It must not serialize response objects, exception reprs, diagnostics objects wholesale, request body, response body, prompt body beyond documented PASS literals, request id, provider values, model values, key values, headers or endpoint paths.
5. A PASS-only timeout only authorizes a future disposition design gate. It does not authorize endpoint/config/default/runtime changes.
6. Borderline threshold: if `elapsed_ms >= 0.8 * timeout_seconds * 1000`, classify a success as `ambiguous_near_timeout`, not as a clean endpoint-health refutation.

## Next Entry Point

Start `MVP PASS-only timing probe evidence harness contract gate`.

This next gate is still design/control first. It may define the exact temporary one-shot script or dev-only helper and output schema. It still must not run a live PASS-only probe until controller judgment accepts the exact command and artifact destination.

## Guardrails

- No source code, tests, provider endpoint, provider config, provider timeout defaults, retry defaults, prompt contract, auditor rule, CHAPTER_CONTRACT, score-loop, quality gate, golden/readiness, final assembly, deterministic analyze/checklist behavior, PR/release state or fail-closed behavior changed.
- The future harness must bypass Service analyze/orchestrator/report assembly and must not create report or retained LLM run artifacts.
- Any endpoint/config/default/runtime change remains a separate heavy gate.

## Accepted Checkpoint

Accepted once the plan, reviews, controller judgment and control/startup sync are committed locally.
