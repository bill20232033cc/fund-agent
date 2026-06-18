# Provider/LLM Chapter 3 Item 01 Fact-gap Disposition Controller Judgment

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 3 Item 01 Fact-gap Disposition Gate`.

This controller judgment accepts or rejects the disposition artifact for the current Chapter 3 item 01 `missing_required_facts` / `fact_gap` state. It does not implement a code fix, update source behavior, run live/provider/network/source/PDF/readiness/release/PR commands, or change EID source policy, provider defaults, repair budget, annual-period LLM route, Docling/parser policy, fallback policy or external state.

Release/readiness remains `NOT_READY`. Annual-report access remains EID single-source/no-fallback.

## Evidence Reviewed

- Disposition artifact: `docs/reviews/provider-llm-chapter3-item01-fact-gap-disposition-20260614.md`
- DS review: `docs/reviews/provider-llm-chapter3-item01-fact-gap-disposition-review-ds-20260614.md`
- MiMo review: `docs/reviews/provider-llm-chapter3-item01-fact-gap-disposition-review-mimo-20260614.md`
- Truth/control:
  - `AGENTS.md`
  - `docs/current-startup-packet.md`
  - `docs/implementation-control.md`
  - `docs/design.md`
  - `docs/fund-analysis-template-draft.md`
- Accepted prior judgments:
  - `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-controller-judgment-20260614.md`
  - `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-controller-judgment-20260614.md`
  - `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`
  - `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`
- Safe runtime metadata from:
  - `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/manifest.json`
  - `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/summary.json`
  - `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-02.json`
  - `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-03.json`

Forbidden body/payload reads were not used for this judgment.

## Accepted Current Facts

- `ch3.required_output.item_01` currently declares `when_evidence_missing="block"` in the canonical template truth source.
- The prior Chapter 3 item 01 provider-before `ValueError` / `code_bug` path has been fixed and accepted as no longer current.
- The latest accepted safe runtime metadata records Chapter 3 as:
  - `status=blocked`
  - `stop_reason=missing_required_facts`
  - `failure_category=fact_gap`
  - issue `3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01`
- Chapter 2 is accepted in the same live metadata; Chapter 3 is now the first failed chapter.
- The run remains incomplete: `orchestration_status=partial`, `final_assembly_status=incomplete`, and Chapter 3 has no accepted draft or conclusion.
- Current Route C remains explicit opt-in, provider-backed and fail-closed.
- Current `analyze-annual-period` remains deterministic and is not a multi-period LLM chapter-writing route.
- Current chapter repair budget remains one regenerate attempt per chapter and is not product-calibrated.
- EID remains the only operational annual-report source path; no fallback source is authorized.
- Release/readiness remains `NOT_READY`.

## Review Finding Disposition

| Finding | Source | Disposition | Controller rationale |
| --- | --- | --- | --- |
| Disposition correctly classifies current Chapter 3 item 01 `fact_gap` as accepted fail-closed residual. | DS, MiMo | ACCEPT | This follows directly from template item 01 `block` policy and safe runtime metadata. |
| Disposition correctly rejects the prior `ValueError` / `code_bug` as current root cause. | DS, MiMo | ACCEPT | The old code-bug path was fixed and live-confirmed as no longer reproduced. |
| Disposition correctly rejects immediate implementation and routes to required-output policy planning. | DS, MiMo | ACCEPT | Remaining question is product/template policy, not unexplained code behavior. |
| Disposition preserves EID single-source/no-fallback and `NOT_READY`. | DS, MiMo | ACCEPT | No fallback/readiness/release claim is made. |
| Verdict string is verbose / non-standard. | DS F1, MiMo F1 | ACCEPT_AS_NONBLOCKING_PRESENTATION_FINDING | The semantic verdict is clear and supported. No artifact amendment is required for this gate. Future artifacts may use shorter verdict identifiers. |
| Chapter 2 historical `failure_subcategory` distinction is elided. | DS F2 | ACCEPT_AS_NONBLOCKING_PRESENTATION_FINDING | The disposition uses terminal state for routing, which is correct. Historical non-null `failure_subcategory` on an accepted chapter does not change current first-failed classification. |
| Scope statement mentions future design items such as annual-period LLM route and Docling/parser policy. | MiMo F2 | ACCEPT_AS_NONBLOCKING_CLARITY_FINDING | These are explicitly listed as non-changes/non-goals. The wording is conservative and does not authorize work in those areas. |
| Broader Chapter 3 required-output items should remain visible for policy planning awareness. | MiMo F3 | ACCEPT_AS_INFO | The disposition already defers broader typed required-output audit/policy questions. |

## Accepted / Rejected / Residual Table

| Item | Decision | Basis | Next handling |
| --- | --- | --- | --- |
| Chapter 3 item 01 current fact-gap state | ACCEPTED_RESIDUAL | Template `block` policy plus safe metadata `required_output_block:ch3.required_output.item_01` | Carry as current LLM completion blocker |
| Prior Chapter 3 item 01 provider-before `ValueError` / `code_bug` | REJECT_AS_CURRENT_ROOT_CAUSE | Accepted post-fix evidence shows current fact-gap instead | Historical only |
| Immediate code implementation gate | REJECT | No current code-bug root cause is proven; behavior is accepted fail-closed policy | Do not implement directly from this gate |
| More no-live diagnostic evidence before disposition | REJECT | Existing accepted no-live and bounded live chain is sufficient to classify current state | Not needed for this disposition |
| Bounded live re-evidence now | REJECT | Current blocker is already directly identified by accepted live metadata | No live next gate |
| Required-output policy planning | ACCEPT_AS_NEXT_GATE | Product/template policy must decide hard block vs evidence-gap rendering vs minimum verification question | Proceed to policy planning |
| Source fallback / Eastmoney / fund-company / CNINFO expansion | REJECT | EID single-source/no-fallback remains current policy | Not a valid remedy |
| Release/readiness / MVP-ready / LLM path ready | REJECT | Incomplete final assembly and blocked Chapter 3 | Preserve `NOT_READY` |

## Control-doc Update Recommendation

After checkpointing this controller judgment, update:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Next entry point:

`Provider/LLM Chapter 3 Required-output Policy Planning Gate`

Required next-gate boundaries:

- planning only unless a later reviewed gate authorizes implementation;
- no live/provider/network/source/PDF/FDR/analyze/checklist/readiness/release/PR command;
- no source acquisition policy or fallback change;
- no provider default or repair budget change;
- no annual-period LLM route design;
- preserve EID single-source/no-fallback and `NOT_READY`.

## Final Verdict

VERDICT: ACCEPT_AS_FAIL_CLOSED_RESIDUAL_READY_FOR_REQUIRED_OUTPUT_POLICY_PLANNING_GATE_NOT_READY

Chapter 3 item 01 fact-gap is accepted as the current intentional fail-closed blocker. The next mainline gate is required-output policy planning, not implementation or live re-evidence. Release/readiness remains `NOT_READY`.
