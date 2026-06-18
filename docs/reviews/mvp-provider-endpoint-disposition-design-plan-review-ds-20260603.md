# MVP provider endpoint disposition design plan — AgentDS review

- Role: AgentDS, independent plan reviewer, not controller
- Gate: `MVP provider endpoint disposition design/evidence gate`
- Classification: heavy
- Date: 2026-06-03
- Inputs: plan under review, AGENTS.md, docs/design.md, docs/implementation-control.md, docs/current-startup-packet.md, typed diagnostic serialization repair controller judgment, both retained summary.json artifacts

This review does not change the plan, authorize a live provider run, or change any provider default/runtime/endpoint/config.

## Verdict

**PASS.** No blocking findings. Four non-blocking findings for controller consideration.

## Review Matrix

### 1. Post-repair live evidence necessity and authorization sufficiency

**Finding: PASS.** The plan correctly establishes that post-repair live evidence is needed before any endpoint disposition.

Both retained artifacts (`006597-2024-20260602T220325Z` and `006597-2024-20260602T224137Z`) lack the terminal consistency fields added by the typed diagnostic serialization repair:

- `diagnostic_consistency_status`
- `terminal_runtime_diagnostic_present`
- `terminal_stop_reason`
- `terminal_failure_category`
- `terminal_runtime_operation`
- `terminal_repair_attempt_index`
- `terminal_issue_class`

I verified both `summary.json` files directly. Neither contains any of these fields. The pre-repair classification is correct.

The plan's scope for the next evidence gate — exactly one default-budget live run with no config/default/runtime changes — is the minimal sufficient step. The stop conditions (on config fail, on missing artifact, on secret-scan hit) are correctly fail-safe. The validation pipeline (json.tool × 2 + rg secret scan) is executable and covers the critical safety surface.

The evidence extraction requirements (section 5.1) and PASS criteria (section 5.2) correctly distinguish diagnostic adequacy from report acceptance: an exit-1 run can still satisfy the evidence gate if terminal consistency fields are present and secret-scan is clean.

### 2. Presence-only readiness: secret safety and command executability

**Finding: PASS, with one non-blocking observation.**

The allowed/forbidden output taxonomy (section 3) is comprehensive and correctly constrains to `present|absent` for all sensitive values. The command in section 3 is a single `python -c` one-liner that:
- Reads env vars without printing values
- Calls the existing `load_llm_provider_config_from_env()` function
- Maps `LLMProviderConfigError` messages to coarse categorical labels via substring matching, never echoing the raw error text

**Non-blocking observation NB-1:** The `except` block's safe error mapping uses simple `in text` substring checks ordered by specificity. If `LLMProviderConfigError` ever produces a message that simultaneously mentions multiple fields (e.g., "missing FUND_AGENT_LLM_PROVIDER and invalid base URL"), only the first matching branch will fire. This is low-risk for the current error class surface but the controller may want to document that the command assumes single-field-error messages from `load_llm_provider_config_from_env()`.

### 3. Old artifacts as pre-repair: correctness and historical usability

**Finding: PASS.**

The plan's table (section 2) correctly labels both retained artifacts as `pre-repair schema`. This matches the controller judgment: "Typed diagnostic serialization repair is accepted locally" and both artifacts predate the repair commit.

The plan also correctly states that old artifacts can still support historical hypotheses (volatility, operation/prompt-size correlation) but cannot settle terminal lineage consistency. This is a precise and useful distinction. For example:
- The default run (`T220325Z`) shows Ch2 auditor timeout at ~758 tokens under 60s × 2 — a valid historical prompt-size observation
- The 120s run (`T224137Z`) shows Ch2 `failure_category=llm_timeout` but the only Ch2 runtime diagnostic row has `chapter_failure_category=prompt_contract` and `finish_reason=stop` — the known attribution gap from prior gates

The plan avoids using either artifact to make terminal consistency claims that the schema doesn't support. This is correct.

### 4. Root-cause classification matrix: same-source, sufficient, non-conflating

**Finding: PASS, with one non-blocking observation.**

The matrix (section 6) has 8 hypotheses, each with supporting/refuting evidence columns and a disposition column. The hypotheses are:

| # | Hypothesis | Correctly separated from |
|---|-----------|------------------------|
| 1 | Endpoint-wide latency | Budget (4), operation-specific (3), provider-specific (2) |
| 2 | Provider-specific latency | Endpoint-wide (1), budget (4) |
| 3 | Operation-specific latency | Budget (4), endpoint-wide (1) |
| 4 | Budget insufficiency | Prompt-size (5), endpoint (1) |
| 5 | Prompt/output-size correlation | Budget (4), audit (6) |
| 6 | Audit/content failure | Anchor (7), Ch3 (8), endpoint (1) |
| 7 | Anchor/contract failure | Audit (6), Ch3 (8) |
| 8 | Ch3 C2/content failure | Audit (6), anchor (7), endpoint (1) |

Each hypothesis references specific same-source fields (e.g., `provider_runtime_category=timeout`, `approx_prompt_tokens`, `failure_category=audit_rule_too_strict`). The classification rule at the bottom of section 6 — "if terminal consistency is missing in a post-repair artifact, classify the artifact as diagnostic-defective" — is a proper fail-safe that prevents root-cause selection from incomplete fields.

**Non-blocking observation NB-2:** Hypothesis 3 (operation-specific latency) notes that "mixed writer/auditor timeout in same run weakens operation-specific claim," and hypothesis 1 (endpoint-wide) notes that "only one operation/chapter times out while other similar-cost calls accept" refutes endpoint-wide. The boundary between "operation-specific" and "endpoint-wide with sporadic success" is not fully sharpened. When only one chapter shows timeout but with different prompt sizes than accepted chapters, the matrix doesn't give clear tie-breaking guidance. This is a residual interpretation risk for the evidence gate, not a plan defect.

### 5. Probe ordering correctness

**Finding: PASS.**

The ordering (section 7) is:
1. Presence-only readiness
2. One default-budget post-repair live evidence slice
3. Diagnostic adequacy decision
4. PASS-only timing probe (conditional on runtime latency without broad endpoint failure)
5. Split-audit probe (conditional on operation-clustered latency)
6. Timeout default change (conditional on stable budget insufficiency evidence from probes)
7. Provider endpoint/config change (conditional on endpoint-wide/provider-specific instability surviving probes)

This ordering is conservative and correct. Each step has explicit preconditions that reference prior evidence. The preconditions for timeout default change and provider endpoint change (sections in 7) both require controller to open a separate heavy gate — this correctly prevents evidence-only work from drifting into implementation.

The PASS-only timing probe preconditions (must not produce report content artifacts, must record only timing/status class/timeout category/coarse operation label) correctly constrain what a PASS-only probe can observe, preventing accidental report-content leakage into endpoint health measurements.

### 6. Open questions: controller-resolvable, no blockers

**Finding: PASS.**

The three open questions (section 11):

1. **Exactly one live run or additional reviewer plan first?** This is a controller authorization question. The plan has sufficient design justification for exactly one run. An additional reviewer plan before a live call would add defense-in-depth but is not required by the current gate's evidence baseline.

2. **If all chapters accept, stop at volatility evidence or also run PASS-only timing?** This is a sequencing question that depends on what evidence the run produces. The plan correctly defers it to controller judgment rather than hardcoding a branch. If all chapters accept unexpectedly, the controller can decide in situ whether endpoint health characterization is still needed.

3. **Minimum evidence threshold for provider endpoint/config disposition?** This is a policy question. The plan frames two options (two runs with broad failures vs one run + PASS-only probe) which both require multiple evidence points. Either option is conservative.

None of these questions blocks the plan's acceptance or the next evidence gate's execution. They are all resolvable by controller judgment at the appropriate sequencing point.

## Non-Blocking Findings Summary

| ID | Section | Finding | Controller action |
|----|---------|---------|-------------------|
| NB-1 | 3 | Presence-only error mapping assumes single-field `LLMProviderConfigError` messages | Accept as-is or add a note about the single-field assumption |
| NB-2 | 6 | Boundary between operation-specific and endpoint-wide hypotheses is fuzzy when only one chapter times out | Accept as residual interpretation risk for the evidence gate |
| NB-3 | 4 | Allowed fields list includes `prompt_cost_diagnostic` containing individual `anchor_id` values; the restriction to aggregate counts/chars is stated separately under "Conditionally allowed" rather than inline | Controller may want to restate the aggregate-only rule closer to the allowed fields list in the evidence gate instructions |
| NB-4 | 8 | No-goals section omits an explicit statement that the evidence gate must not introduce `terminal_repair_attempt_index` / `terminal_issue_class` interpretation before the serialization repair is proven under live provider | Accept as implicit (the plan already requires post-repair artifact validation); no plan change needed |

## Residual Risk Assessment

- **Risk R1 (evidence artifact not produced):** Mitigated by the plan's explicit stop condition and the existing `--use-llm` incomplete-artifact retention behavior. If no artifact is produced, the evidence gate stops and records stdout/stderr diagnostics.
- **Risk R2 (secret leakage via error messages):** Mitigated by the presence-only command's safe error mapping and the forbidden-output taxonomy. The `LLMProviderConfigError` surface is narrow and controlled.
- **Risk R3 (diagnostic-defective post-repair artifact):** Mitigated by the classification rule in section 6. If terminal consistency fields are absent from a post-repair run, the artifact is classified as diagnostic-defective and no endpoint disposition proceeds.
- **Risk R4 (acceptance volatility misinterpreted as endpoint instability):** Mitigated by the matrix's separation of hypotheses 6 (audit/content failure) and 7 (anchor/contract failure) from endpoint/budget hypotheses. Cross-run volatility in audit or anchor results routes to calibration gates, not endpoint disposition.

## Artifact Completeness

The plan covers all required sections for a heavy gate design/evidence plan:
- Scope and evidence baseline
- Secret safety constraints for provider config
- Safe evidence field taxonomy (allowed/forbidden)
- Post-repair evidence necessity argument with explicit slice specification
- Root-cause classification matrix
- Probe ordering with preconditions
- No-goals
- Acceptance matrix for the future evidence gate
- Next gate recommendation with classification and scope
- Blocking open questions

No sections are missing or underspecified for the gate's purpose.

## Endorsement

The plan is accepted as an adequate design/evidence basis for the next gate (`MVP post-repair provider endpoint disposition evidence slice`). The next gate should proceed as evidence-only, heavy, with exactly one default-budget live run after presence-only readiness passes. The non-blocking findings do not require plan changes and can be resolved by controller notation or in the evidence gate instructions.
