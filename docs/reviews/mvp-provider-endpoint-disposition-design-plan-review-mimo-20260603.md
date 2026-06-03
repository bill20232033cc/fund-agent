# MVP provider endpoint disposition design/evidence plan review — MiMo

## Reviewer

- AgentMiMo, independent adversarial plan reviewer
- Gate: `MVP provider endpoint disposition design/evidence gate`
- Classification: heavy
- Date: 2026-06-03

## Plan Under Review

`docs/reviews/mvp-provider-endpoint-disposition-design-plan-20260603.md`

## Inputs Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-provider-endpoint-disposition-design-plan-20260603.md`
- `docs/reviews/mvp-typed-diagnostic-serialization-repair-implementation-controller-judgment-20260603.md`
- `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json`
- `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7/summary.json`

## Challenge 1: Exactly One Default-Budget Live Run 是否过早

**Question**: Should the plan require synthetic readiness or no-live design before allowing one live run?

**Analysis**: The plan already layers two safety checks before any live call:

1. Presence-only provider config readiness (Section 3) validates env vars without touching the provider.
2. Stop conditions (Section 5.1) abort on config validation failure, missing artifact, or secret scan failure.

The rationale for requiring at least one post-repair live artifact is sound: the typed diagnostic serialization repair changed terminal lineage and consistency fields, but no live artifact has yet proved those fields under real provider behavior. Old artifacts (pre-repair schema) cannot settle terminal lineage consistency. Without post-repair evidence, endpoint disposition would rely on incomplete fields — the plan correctly classifies such artifacts as "diagnostic-defective for endpoint disposition" rather than picking root cause from incomplete data.

The plan does not authorize the live run itself; a controller must approve the evidence slice gate (Section 10). This is appropriate for a heavy gate.

**Finding**: Non-blocking. The one-run-before-disposition design is proportionate given the repair-to-evidence dependency. Synthetic readiness alone cannot prove post-repair terminal lineage under real provider behavior.

## Challenge 2: Presence-Only Python One-Liner Secret Safety

**Question**: Could the one-liner leak API key env var target name or URL shape details?

**Analysis**: The one-liner (Section 3) outputs only:

- `present|absent` for required env var names
- `present|absent` for `FUND_AGENT_LLM_API_KEY_ENV_VAR` (name only)
- `present|absent` for `effective_api_key_value` (name only)
- `config_validation: pass|fail`
- `config_error_class: LLMProviderConfigError`
- `config_error_field`: coarse reason only

The `safe` variable in the error handler maps exception text to one of 7 generic labels: `missing FUND_AGENT_LLM_PROVIDER`, `missing FUND_AGENT_LLM_MODEL`, `missing FUND_AGENT_LLM_BASE_URL`, `missing API key value`, `unsupported provider`, `invalid base URL shape`, or `invalid typed config`. None of these labels include the actual env var target value, provider base URL, model value, or API key value.

The `config_error_field` output for `invalid base URL shape` does not print the URL itself — only the coarse label. The custom env var name is only printed if it matches one of the public variable names (`FUND_AGENT_LLM_API_KEY_ENV_VAR`), which is already a public constant in the codebase.

The one-liner is not executable as-is for secret extraction. It reads env vars and prints presence/absent only.

**Finding**: Non-blocking. The one-liner is safe. No secret, URL shape, or custom env var target value is printed.

## Challenge 3: Post-Repair Complete Acceptance Without Retained Artifact

**Question**: If a post-repair run fully accepts all chapters, is the evidence capture sufficient?

**Analysis**: The plan addresses this case in two places:

- Section 5.1: "Stop after exactly one retained artifact is produced." Combined with Section 5.2's PASS condition: "retained artifact exists for incomplete live result, or accepted result is explicitly recorded as no incomplete artifact expected."
- Section 10: "If the post-repair default run accepts all body chapters, should the next gate stop at recording acceptance volatility evidence, or still run PASS-only timing to characterize endpoint health?" — left as a blocking open question for the controller.

The `FundLLMAnalysisResult` currently only triggers artifact retention for incomplete results. A fully accepted run produces the final report via stdout and exits 0 — no `reports/llm-runs/` artifact is written. The plan correctly identifies this gap and requires explicit recording of the accepted result.

However, the plan could be stronger on what "explicitly recorded" means for a complete-acceptance outcome. Specifically:
- Exit code, stdout byte count, `orchestration_status`, `final_assembly_status` should be captured even for a complete run.
- The controller should record whether the run produced any stderr diagnostics (progress, phase events) that could inform volatility analysis.

**Finding**: Non-blocking, but a residual observation for the evidence gate controller. The plan should specify minimum capture fields for a complete-acceptance outcome (exit code, orchestration/final assembly status, stderr diagnostic count) even when no incomplete artifact is produced.

## Challenge 4: Provider Endpoint/Config Disposition Threshold

**Question**: Is the disposition threshold too weak or too strong?

**Analysis**: The plan defines preconditions for provider endpoint/config change (Section 7):

- Presence-only readiness passes
- Post-repair default artifact shows endpoint-wide or provider-specific instability, not just one chapter/auditor timeout
- PASS-only timing or equivalent endpoint health evidence supports endpoint-level latency
- Config change candidate is defined without printing secret values
- Controller opens a heavy implementation gate

The probe ordering (Section 7) requires multiple evidence layers before disposition:
1. Presence-only config readiness
2. One default-budget post-repair live evidence slice
3. Diagnostic adequacy check
4. PASS-only timing probe (if runtime latency but not broad failure)
5. Split-audit probe (if auditor-specific failure)
6. Timeout default change (only after targeted probes)
7. Provider endpoint/config change (only after endpoint-wide evidence)

This is appropriately cautious. A single chapter timeout does not trigger endpoint disposition. The threshold requires evidence of broad instability across operations/chapters, validated through targeted probes.

The plan correctly separates operation-specific latency (→ split-audit or timeout tuning) from endpoint-wide instability (→ provider change). The `root-cause classification matrix` (Section 6) provides explicit refuting evidence for each hypothesis, preventing premature disposition.

**Finding**: Non-blocking. The threshold is proportionate. It requires multi-layer evidence and prevents single-chapter timeout from triggering endpoint change.

## Challenge 5: Hidden Provider Default Tuning / PASS-Only / Split-Audit / Ch3 Backdoors

**Question**: Does the plan contain implicit backdoors for provider default tuning, PASS-only direct run, split-audit direct run, or Ch3 implementation?

**Analysis**: The plan's no-go list (Section 8) explicitly prohibits:

- Do not change provider default timeout
- Do not change writer, auditor, prompt contract, CHAPTER_CONTRACT or audit rules
- Do not implement Ch3 calibration
- Do not connect `chapter_generation_score` or score-loop
- Do not change FQ0-FQ6 quality gate, golden/readiness, fixture promotion or release state
- Do not relax fail-closed behavior
- Do not turn live incomplete result into deterministic fallback
- Do not emit stdout partial reports from incomplete `--use-llm` runs
- Do not add provider fallback or multi-provider selection
- Do not use old pre-repair artifacts as proof of post-repair terminal consistency

The probe ordering (Section 7) requires separate design gates for each probe type:

- PASS-only timing probe: "separate design/controller judgment accepts exact command and artifact destination"
- Split-audit probe: "default post-repair evidence shows auditor-specific failure" as precondition
- Timeout default change: "controller opens a heavy implementation gate"
- Provider endpoint/config change: "controller opens a heavy provider disposition implementation/config gate"

Ch3 is explicitly separated throughout: Section 6 root-cause table routes Ch3 C2/content failure to "Separate Ch3 calibration gate; do not solve via provider runtime tuning." Section 8 prohibits Ch3 implementation.

No backdoors found. Each probe type requires explicit controller authorization and appropriate gate classification.

**Finding**: Non-blocking. No hidden backdoors. The plan maintains strict separation between evidence collection and any behavioral change.

## Challenge 6: Safe Evidence Fields Width

**Question**: Are the safe evidence fields too wide, especially `prompt_cost_diagnostic aggregate`, `request_id`, and `error_type`?

**Analysis**:

### `prompt_cost_diagnostic`

The plan (Section 4) marks `prompt_cost_diagnostic.component_costs` and aggregate `anchor_cost_rows` / `fact_cost_rows` counts and character sizes as "conditionally allowed only when needed for prompt/output-size correlation." The plan adds: "Do not use full anchor IDs or full fact IDs unless a later controller explicitly accepts them as safe. Aggregate them into counts and character-size totals."

However, the existing 120s auditor-only artifact (`reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7/summary.json`) already contains full anchor IDs and fact IDs in its Ch5 `prompt_cost_diagnostic` — e.g., `chapter-anchor:006597:2024:ch5:annual_report:§2:dad2b086` and `chapter-fact:006597:2024:ch5:structured.basic_identity`. These IDs contain fund code, year, chapter, section, and table identifiers.

The plan's recommendation to aggregate is correct, but the "conditionally allowed" phrasing does not explicitly require aggregation as a precondition. The existing artifact already violates the aggregation recommendation. This is a minor inconsistency: the plan acknowledges the risk ("Do not use full anchor IDs") but the conditionally allowed section does not enforce it.

Risk assessment: The IDs in existing artifacts contain fund code (006597), year (2024), chapter (ch5), annual report section (§2), and table references. These are not secrets — they are diagnostic metadata. The risk is misattribution or confusion, not secret exposure. The plan's aggregation recommendation is good hygiene but not a safety blocker.

### `request_id`

The plan explicitly states: "`request_id` is currently a safe opaque scalar in the serializer contract, but this gate should not use it for attribution because provider-specific request IDs may encode deployment or routing details in future providers. It may be retained in artifacts but should be omitted from human evidence."

This is correct. The current retained artifacts have `request_id: null`, so no actual risk exists today. The plan's forward-looking guidance is appropriate.

### `error_type`

The plan allows `error_type` as a safe field. Current retained artifacts show `error_type: "ReadTimeout"` (from httpx). This is a generic Python exception class name — it does not contain endpoint, URL, or provider-specific details. Safe.

**Finding**: Non-blocking. The `prompt_cost_diagnostic` conditionally allowed section should note that existing artifacts already contain full anchor/fact IDs and that the aggregation recommendation applies to future evidence extraction from those artifacts. The `request_id` and `error_type` fields are safe.

## Disposition

**PASS. No blocking findings.**

The plan is well-structured and addresses all 6 challenge areas:

1. One default-budget live run is not premature; it is gated by presence-only readiness, stop conditions, and controller authorization.
2. The presence-only one-liner is safe; it prints presence/absent only, no secrets.
3. Evidence capture for complete-acceptance outcomes is addressed; a minor residual for the controller to specify minimum capture fields.
4. Provider disposition threshold is proportionate; it requires multi-layer evidence and prevents single-chapter timeout from triggering endpoint change.
5. No hidden backdoors exist; each probe type requires explicit controller authorization.
6. Safe evidence fields are appropriately bounded; `prompt_cost_diagnostic` has a minor inconsistency with existing artifact content.

## Non-Blocking Residual Observations

| # | Observation | Recommended disposition |
|---|---|---|
| R1 | Complete-acceptance outcome capture: the plan should specify minimum fields (exit code, orchestration/final assembly status, stderr diagnostic count) for a run that produces no incomplete artifact | Evidence gate controller records these fields explicitly |
| R2 | `prompt_cost_diagnostic` conditionally allowed: existing 120s artifact already contains full anchor/fact IDs; the aggregation recommendation should note this applies to future evidence extraction from existing artifacts | Evidence gate controller enforces aggregation when extracting from existing artifacts |
| R3 | Blocking open questions (Section 11): the three questions are appropriate for controller resolution but the plan could suggest default answers | Controller resolves; defaults of "one run sufficient", "record acceptance volatility", "one default plus PASS-only probe" seem reasonable |

## Secret Safety

This review contains no API key, Authorization header, Bearer token, cookie, password, provider base URL value, model value, raw prompt body, raw provider response, raw audit response, writer draft body, repair draft body, markdown report body, raw PDF text or raw parsed annual-report text.
