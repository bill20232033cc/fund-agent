# Provider/LLM Chapter 3 Required-output Policy Plan Controller Judgment

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 3 Required-output Policy Planning Gate`.

This controller judgment accepts or rejects the planning artifact for `ch3.required_output.item_01` policy. It does not implement code, modify tests/runtime behavior, update source acquisition policy, run live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands, or change release/PR state.

Release/readiness remains `NOT_READY`. EID remains the only operational annual-report source path; no fallback is authorized.

## Evidence Reviewed

- Plan artifact: `docs/reviews/provider-llm-chapter3-required-output-policy-plan-20260614.md`
- DS review: `docs/reviews/provider-llm-chapter3-required-output-policy-plan-review-ds-20260614.md`
- MiMo review: `docs/reviews/provider-llm-chapter3-required-output-policy-plan-review-mimo-20260614.md`
- Truth/control:
  - `AGENTS.md`
  - `docs/current-startup-packet.md`
  - `docs/implementation-control.md`
  - `docs/design.md`
  - `docs/fund-analysis-template-draft.md`
- Accepted prior judgment:
  - `docs/reviews/provider-llm-chapter3-item01-fact-gap-disposition-controller-judgment-20260614.md`

No forbidden body/payload/live/source reads were used for this judgment.

## Accepted Current Facts

- Current Chapter 3 item 01 fact-gap is an accepted intentional fail-closed residual, not a current code bug.
- Current canonical template policy for `ch3.required_output.item_01` is `when_evidence_missing="block"`.
- Chapter 3 item 01 is a descriptive required output: `基金经理基本信息`.
- Chapter 3 items 02-05 already use `render_evidence_gap`; item 06 uses `render_minimum_verification_question`.
- Existing typed writer mechanics already support `render_evidence_gap`.
- Existing writer validation can block unsafe gap rendering when approved gap wording is missing.
- Final assembly is safe only when required body chapters are accepted with accepted draft/conclusion; incomplete or blocked body chapters must not be assembled.
- Current Route C remains explicit opt-in and fail-closed.
- Current deterministic `analyze/checklist` and deterministic `analyze-annual-period` paths are unchanged.
- EID single-source/no-fallback and `NOT_READY` remain mandatory guardrails.

## Review Finding Disposition

| Finding | Source | Disposition | Controller rationale |
| --- | --- | --- | --- |
| Policy recommendation to change item 01 to `render_evidence_gap` is sound. | DS, MiMo | ACCEPT | It exposes a visible evidence gap without inventing manager facts and aligns item 01 with nearby Chapter 3 policy. |
| No parser/writer/final assembler code change should be needed for enum support. | DS, MiMo | ACCEPT | Existing typed behavior and writer validation already support `render_evidence_gap`; implementation should remain narrow unless tests prove otherwise. |
| EvidenceAvailability mapping must remain unchanged. | DS, MiMo | ACCEPT | Same-source requirements for `structured.basic_identity` and `structured.portfolio_managers` remain required. |
| Missing EvidenceAvailability envelope must remain fail-closed. | DS, MiMo | ACCEPT | This distinguishes missing reviewed facts from broken contract plumbing. |
| Slice 3 final assembly assertion may over-specify full 8-chapter output if the test is only partial. | MiMo F1 | ACCEPT_WITH_CONTROLLER_AMENDMENT | Implementation gate must either build a full fake accepted 1-6 body run and assert full assembly `0..7`, or narrow the assertion to the actual scoped result without claiming full-report readiness. |
| Slice 3 should explicitly cover unsafe Chapter 3 evidence-gap output blocking final assembly. | MiMo F2 | ACCEPT_WITH_CONTROLLER_AMENDMENT | Implementation gate must add a dedicated negative service-level assertion or prove an existing test directly covers unsafe Chapter 3 output causing incomplete assembly/no report markdown. |
| Slice 4 docs search is broad. | MiMo F3 | ACCEPT_AS_NONBLOCKING_GUARDRAIL | Treat the search as discovery only; update only item 01 hard-block statements if found. |
| Missing-evidence reason wording changes are reasonable. | MiMo F4 | ACCEPT | New wording aligns with `render_evidence_gap`. |
| Negative degradation issue classification should follow writer-output validation, not `required_output_block`. | MiMo F5, DS F6 | ACCEPT | Implementation must assert the current validation mapping rather than reuse the old preflight block issue. |
| Test rename should remove the old hard-block test name. | DS advisory | ACCEPT_AS_IMPLEMENTATION_NOTE | Avoid duplicated near-identical tests. |

## Controller Amendments For Implementation Gate

The plan is accepted with the following binding implementation-gate amendments:

1. Slice 3 must explicitly choose one test shape:
   - full fake Route C body run: all required body chapters 1-6 accepted, then assert full final assembly includes chapters `0,1,2,3,4,5,6,7`; or
   - scoped/partial test: assert only the scoped readiness/result and do not claim full-report assembly.
2. The implementation gate must include or identify a direct negative service-level assertion that unsafe Chapter 3 item 01 output keeps final assembly incomplete and report markdown absent.
3. Slice 4 broad `rg` search is discovery only. It does not authorize broad documentation edits. Update only item 01 hard-block statements if they exist.
4. Keep the missing EvidenceAvailability envelope fail-closed. Do not degrade missing contract plumbing to evidence gap.

## Accepted / Rejected / Residual Table

| Item | Decision | Basis | Next handling |
| --- | --- | --- | --- |
| Change `ch3.required_output.item_01` from `block` to `render_evidence_gap` | ACCEPT | Aligns with Chapter 3 items 02-05 and preserves safe visible gap behavior | No-live implementation gate |
| Change item 01 to `render_minimum_verification_question` | REJECT | Item 01 is descriptive manager basic information, not follow-up-only process item | Do not implement |
| Keep item 01 hard block as final product policy | REJECT_FOR_CURRENT_MAINLINE | It blocks full Chapter 3 for a known evidence gap where safe gap rendering is available | Historical current policy only until implementation |
| Source fallback / Eastmoney / CNINFO / fund-company expansion | REJECT | EID single-source/no-fallback remains current policy | Not authorized |
| Provider default, repair budget, annual-period LLM route, Docling/parser policy changes | REJECT | Out of scope and not needed for item 01 policy | Separate future gates only |
| Live re-evidence after implementation | DEFER | Requires separate bounded live gate authorization and implementation acceptance first | Later evidence gate |
| Release/readiness / MVP-ready / LLM path ready | REJECT | Planning gate and no-live implementation cannot prove readiness | Preserve `NOT_READY` |

## Next Gate Recommendation

Proceed to:

`Provider/LLM Chapter 3 Required-output Policy No-live Implementation Gate`

Allowed implementation scope:

- `docs/fund-analysis-template-draft.md`
- `tests/fund/template/test_typed_contracts.py`
- `tests/agent/test_runner.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/fund/test_evidence_availability.py`
- conditional narrow documentation update only if item 01 hard-block prose exists

Forbidden scope:

- live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands;
- writer/auditor markdown, raw prompt, provider payload/response, source/cache/PDF body or final report body reads;
- source acquisition policy or fallback changes;
- provider default, repair budget, annual-period LLM route, Docling/parser policy changes;
- control-doc updates by implementation worker;
- stage/commit/push/PR/merge by implementation worker.

Required validation:

- focused no-live template projection test;
- evidence availability mapping test;
- Agent runner positive/negative item 01 degradation tests plus missing-envelope fail-closed test;
- Service final assembly positive and negative readiness tests per controller amendments;
- focused regression bundle over affected tests;
- ruff on touched Python files;
- `git diff --check`.

## Control-doc Update Recommendation

After checkpointing this planning judgment, update:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Next entry point:

`Provider/LLM Chapter 3 Required-output Policy No-live Implementation Gate`

## Final Verdict

VERDICT: ACCEPT_WITH_CONTROLLER_AMENDMENTS_READY_FOR_NO_LIVE_POLICY_IMPLEMENTATION_GATE_NOT_READY

The plan is accepted. Implementation may proceed only within the amended no-live scope above. Release/readiness remains `NOT_READY`.
