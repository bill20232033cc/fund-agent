# MVP LLM acceptance volatility and diagnostic evidence reconciliation design plan controller judgment

## Controller Self-Check

- Role: phaseflow/gateflow controller.
- Gate: `MVP LLM acceptance volatility and diagnostic evidence reconciliation design gate`.
- Classification: heavy.
- Current step: design/plan review judgment.
- Scope: accept or reject the design/plan artifact; no source/test/config/runtime/provider/default/auditor/template/score/golden/readiness implementation.
- Inputs reviewed: design/plan, DS review, MiMo review, 120s evidence artifact and judgment, default resumed retained artifact summary, 120s retained artifact summary, `docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md`.

## Judgment

**Accepted as the design/plan for diagnostic evidence reconciliation.** DS and MiMo both returned PASS with no blocking findings.

Accepted plan decisions:

- The 120s auditor-only diagnostic does not justify provider timeout default changes or further direct timeout increases.
- The current failure surface is not a single Ch2 auditor-budget issue: the same retained run shows Ch1/Ch4 `audit_rule_too_strict`, Ch5 writer timeout, Ch6 `unknown_anchor`, and Ch2 diagnostic attribution inconsistency.
- The Ch2 inconsistency is same-source evidence: terminal chapter classification reports `llm_timeout`, while serialized runtime diagnostics expose a non-timeout auditor row and prior programmatic repair context.
- More live provider probes should not proceed until the retained diagnostic lineage is trustworthy enough to interpret terminal failure rows.
- PASS-only timing and split-audit probes remain deferred and require later design gates.
- Ch3 calibration implementation remains deferred until runtime/audit/anchor volatility is legible.

## Review Disposition

DS review: PASS with four non-blocking findings.

- Full regression should be added to completion evidence for the next implementation gate.
- Attempt-level `attempts[].runtime_diagnostics` lineage should be covered, not only chapter-level summaries.
- CLI first-failed output should receive explicit regression coverage if `_first_failed_runtime_diagnostic()` matching changes.
- Future `audit_focus` design must conform to the already-accepted template typed contract redesign semantics.

Controller disposition: accepted as mandatory amendments for the next implementation/design handoffs. No plan repair is required because these findings refine implementation acceptance criteria without changing the sequencing decision.

MiMo review: PASS with one major advisory, three minor findings and positive confirmations.

- Major advisory: Ch2 "diagnostic attribution gap" is likely a narrow serializer/lineage code bug where prior audit diagnostics shadow terminal exception diagnostics.
- Minor: `request_id` and `status_code` need explicit safe-field scoping.
- Minor: `prompt_cost_diagnostic` sub-fields should be explicitly included or excluded by the safe evidence contract.
- Minor: next implementation gate classification may be `standard` if the fix remains narrow and does not change public CLI diagnostic semantics or retained artifact schema in a breaking way.

Controller disposition: accepted. I keep the next gate classification at `heavy` for planning because retained incomplete-run artifact schema and CLI first-failed diagnostics are public fail-closed evidence surfaces. The implementation slice may be narrowed inside that heavy gate; if the plan proves it is purely serializer-internal and non-breaking, the controller can down-classify before implementation.

## Accepted Next Gate

Start:

`MVP typed diagnostic serialization repair implementation gate`

Initial classification:

`heavy`

Reason: the next work touches retained artifact diagnostic semantics and possibly CLI safe first-failed summaries, which are part of fail-closed observability. Classification can be revisited only if the implementation plan proves the change is a non-breaking, serializer-internal fix.

Required amendments for the next gate:

- Frame the root cause hypothesis as a likely diagnostic serialization/lineage bug, not as a provider-budget root cause.
- Add or preserve scalar consistency fields such as `diagnostic_consistency_status`, `terminal_runtime_diagnostic_present`, `terminal_stop_reason`, `terminal_failure_category`, and related terminal lineage fields only if they remain safe and non-secret.
- Cover both chapter-level and `attempts[]` runtime diagnostic lineage.
- Preserve prompt-contract diagnostics as separate from provider runtime diagnostics.
- Add CLI first-failed regression coverage if representative diagnostic selection changes.
- Include full `uv run pytest` in implementation completion evidence, or record a controller-approved reason for not running it.
- Explicitly scope `request_id` as opaque and removable if it embeds provider/account/model/region data; `status_code` must remain a standard HTTP status integer only.
- Explicitly include or exclude `prompt_cost_diagnostic` sub-fields under the existing safe allowlist.
- Do not run live provider in the implementation gate.
- Do not change timeout defaults, auditor rules, prompt contracts, deterministic analyze/checklist, final assembly, score-loop, provider endpoint config, or fail-closed behavior.

## Acceptance Evidence

| Purpose | Artifact |
|---|---|
| Design/plan | `docs/reviews/mvp-llm-acceptance-volatility-diagnostic-evidence-reconciliation-design-plan-20260603.md` |
| DS plan review | `docs/reviews/mvp-llm-acceptance-volatility-diagnostic-evidence-reconciliation-design-plan-review-ds-20260603.md` |
| MiMo plan review | `docs/reviews/mvp-llm-acceptance-volatility-diagnostic-evidence-reconciliation-design-plan-review-mimo-20260603.md` |
| 120s evidence | `docs/reviews/mvp-ch2-auditor-timeout-120s-evidence-20260603.md` |
| 120s evidence controller judgment | `docs/reviews/mvp-ch2-auditor-timeout-120s-evidence-controller-judgment-20260603.md` |

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, provider base URL value, model value, raw prompt body, raw provider response, raw audit response, writer draft body, repair draft body, markdown report body, raw PDF text or raw parsed annual-report text.
