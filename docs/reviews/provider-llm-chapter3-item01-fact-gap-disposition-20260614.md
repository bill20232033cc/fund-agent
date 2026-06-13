# Provider/LLM Chapter 3 Item 01 Fact-gap Disposition

Date: 2026-06-14

## 1. Scope

Gate: `Provider/LLM Chapter 3 Item 01 Fact-gap Disposition Gate`.

This disposition classifies the current Chapter 3 item 01 `missing_required_facts` / `fact_gap` state after the accepted Chapter 2 L1 post-fix bounded live evidence. It does not implement a fix, does not run live/provider/network/source/PDF/readiness/release/PR commands, and does not change source policy, provider defaults, repair budget, annual-period LLM route, Docling/parser policy, fallback policy or release state.

Release/readiness remains `NOT_READY`. Annual-report access remains EID single-source/no-fallback.

## 2. Evidence Reviewed

Truth/control:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`
- `docs/fund-analysis-template-draft.md`

Accepted prior judgments:

- `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-required-output-item01-missing-evidence-no-live-fix-implementation-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-item01-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter2-l1-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`

Safe runtime metadata from the accepted Chapter 2 L1 post-fix live run:

- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/manifest.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/summary.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-02.json`
- `reports/llm-runs/004393-2025-20260613T201900Z-host_run_4a531cbe94604e4/chapters/chapter-03.json`

Forbidden reads were not used: writer Markdown, auditor feedback Markdown, raw prompts, provider payloads/responses, source/cache/PDF bodies and final report body.

## 3. Accepted Current Facts

| Fact | Classification | Basis |
| --- | --- | --- |
| Current active gate is Chapter 3 item 01 fact-gap disposition. | Control fact | `docs/current-startup-packet.md`, `docs/implementation-control.md` |
| `ch3.required_output.item_01` now declares `when_evidence_missing="block"`. | Template truth fact | `docs/fund-analysis-template-draft.md`; accepted implementation judgment |
| The prior provider-before `ValueError` / `code_bug` root cause for item 01 was fixed at template truth source, not masked in Service/runner. | Accepted implementation fact | Item 01 no-live fix controller judgment |
| Post-fix live evidence accepted that Chapter 3 item 01 no longer reproduces provider-before `ValueError` / `code_bug`; it blocks as `missing_required_facts` / `fact_gap`. | Accepted live evidence fact | Item 01 post-fix live controller judgment |
| Latest accepted Chapter 2 L1 post-fix live evidence has Chapter 2 accepted and first failed chapter equal to Chapter 3. | Accepted live evidence fact | Chapter 2 L1 post-fix controller judgment and safe metadata |
| In the latest safe metadata, Chapter 3 has `status=blocked`, `stop_reason=missing_required_facts`, `failure_category=fact_gap`, and issue `3:missing_required_facts:writer:required_output_block:ch3.required_output.item_01`. | Runtime metadata fact | `summary.json`, `chapters/chapter-03.json` |
| The run remains incomplete: `orchestration_status=partial`, `final_assembly_status=incomplete`. | Runtime metadata fact | `manifest.json`, `summary.json` |
| Chapter 3 accepted draft/conclusion is absent in this run. | Runtime metadata fact | `summary.json` |
| Current Route C remains explicit opt-in and fail-closed; default deterministic path is unchanged. | Design/control fact | `docs/design.md`, `docs/implementation-control.md` |
| Current `analyze-annual-period` is deterministic, not multi-period LLM route. | Design/control fact | `docs/design.md`, `docs/implementation-control.md` |
| Current repair budget remains one regenerate attempt per chapter and is not product-calibrated. | Design/control fact | `docs/design.md`, `docs/implementation-control.md` |

## 4. Disposition Decision

The current Chapter 3 item 01 fact-gap is accepted as an intentional fail-closed residual, not as a current code bug.

Rationale:

1. The old failure mode was provider-before `ValueError` / `code_bug` caused by missing `when_evidence_missing` policy. That root cause has already been fixed and live-confirmed as no longer reproduced.
2. The current failure mode is the explicit template policy for `ch3.required_output.item_01`: manager basic information is required, and missing reviewed evidence blocks Chapter 3 writer output.
3. The safe runtime metadata directly matches that policy: `required_output_block:ch3.required_output.item_01`, `missing_required_facts`, `fact_gap`, and no accepted Chapter 3 draft/conclusion.
4. Treating this as a successful full LLM route would be incorrect because final assembly is incomplete and Chapter 3 has no accepted conclusion.
5. Treating this as an immediate implementation bug would also be incorrect because the current behavior is the accepted fail-closed policy.

Therefore the gate decision is:

`ACCEPT_AS_FAIL_CLOSED_RESIDUAL_AND_ROUTE_TO_POLICY_PLANNING`

## 5. Accepted / Rejected / Deferred Table

| Item | Decision | Basis | Next handling |
| --- | --- | --- | --- |
| Chapter 3 item 01 current fact-gap classification | ACCEPTED_RESIDUAL | Template item 01 says `block`; safe metadata reports `required_output_block:ch3.required_output.item_01` | Track as current LLM completion blocker |
| Prior Chapter 3 item 01 provider-before `ValueError` / `code_bug` path | REJECT_AS_CURRENT_ROOT_CAUSE | Accepted post-fix live evidence shows fact-gap instead of code-bug | Historical root cause only |
| Need for immediate no-live code fix | REJECT | Current behavior is accepted fail-closed template policy, not unexplained code behavior | No implementation gate directly from this disposition |
| Need for more no-live diagnostics before any decision | REJECT_FOR_CURRENT_DISPOSITION | Existing no-live + bounded live chain is enough to classify current state | Additional diagnostics may be scoped inside future policy planning only if needed |
| Need for bounded live re-evidence now | REJECT | Latest accepted live metadata already identifies the current blocker; another live run would not decide policy | No live gate next |
| Product question: should Chapter 3 render an evidence-gap section instead of blocking whole Chapter 3 when manager basic info is missing? | DEFER_AS_POLICY_CANDIDATE | This changes template required-output semantics and report completeness behavior | Separate no-live template/required-output policy planning gate |
| Multi-period disclosure LLM route as a way to supply missing manager facts | DEFER | Design truth says annual-period LLM route is future; current route is single-year `--use-llm` | Future heavy route design gate only |
| Source fallback / Eastmoney / fund-company / CNINFO expansion | REJECT | AGENTS/control truth preserve EID single-source/no-fallback | Not a valid remedy in this phase |
| Release/readiness / MVP-ready / LLM path ready claim | REJECT | Exit incomplete, Chapter 3 blocked, no final assembly | Preserve `NOT_READY` |

## 6. Residuals

| Residual | Owner | Current blocker? | Next gate |
| --- | --- | --- | --- |
| Chapter 3 item 01 blocks Chapter 3 when manager basic information lacks reviewed evidence. | Fund template/product policy owner + controller | Blocks full LLM completion; not a code-bug blocker | `Provider/LLM Chapter 3 Required-output Policy Planning Gate` |
| Chapter 3 has no accepted draft/conclusion in current live metadata. | Provider/LLM Route C owner + controller | Blocks final assembly and readiness | Same policy planning gate; later implementation only if policy changes |
| Whether missing manager basic info should degrade to an evidence-gap paragraph or minimum verification question. | Fund template/product policy owner | Policy open question | Same policy planning gate |
| Broader typed required-output null/missing behavior audit for other items. | Fund template owner | Not current blocker for item 01 | Deferred template coverage-hardening gate |
| Multi-period disclosure LLM evidence injection for annual/semi-annual/quarterly corpus. | Service/Fund/Agent route owner | Not current gate blocker | Future heavy design gate |
| Full provider/LLM completion, content quality, additional samples, PR/release/readiness. | Release owner / controller / user authorization | Blocks readiness claim | Later readiness/release gates only |

## 7. Control-doc Update Recommendation

After review and controller acceptance, update:

- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Recommended next entry point:

`Provider/LLM Chapter 3 Required-output Policy Planning Gate`

Recommended next gate boundaries:

- no implementation unless the planning gate explicitly accepts a policy change;
- no live/provider/network/source/PDF/FDR/readiness/release/PR command;
- no source fallback and no source acquisition policy change;
- no repair budget change;
- no annual-period LLM route design;
- preserve EID single-source/no-fallback and `NOT_READY`.

The policy planning gate should decide whether item 01 should remain a hard block, degrade to an evidence-gap rendering, or produce a minimum verification question, and must state how each option affects final assembly readiness and investor-safety constraints.

## 8. Final Verdict

VERDICT: ACCEPT_AS_FAIL_CLOSED_RESIDUAL_READY_FOR_REQUIRED_OUTPUT_POLICY_PLANNING_GATE_NOT_READY

Chapter 3 item 01 fact-gap is accepted as the current intentional fail-closed blocker. It is not release/readiness proof, not provider/LLM completion proof, and not authorization for fallback, live re-run, repair budget change or immediate implementation.
