# QDII Replacement Post-019172 Disposition Decision

> Date: 2026-05-27
> Worker: AgentCodex decision/planning worker, not controller
> Gate: `QDII replacement post-019172 disposition decision gate`
> Scope: decision artifact only. No evidence run. No code/test/production changes. No commit.
> Artifact: `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-20260527.md`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Startup Packet current gate | `QDII replacement fallback 019172 evidence accepted locally` |
| Startup Packet next entry point | `QDII replacement post-019172 disposition decision gate; must use init-agents / tmux multi-agent flow` |
| This artifact gate | `QDII replacement post-019172 disposition decision gate` |
| Latest accepted checkpoint | `d2fdbdb docs: accept qdii fallback 019172 evidence` |
| Design truth | `docs/design.md` current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point |

This artifact follows the Startup Packet next entry point. It is not a gate switch. This worker is not the controller, did not dispatch review agents, did not run evidence, and did not authorize any promotion.

The `init-agents` workflow requirement is preserved as a controller obligation for the next handoff: the controller must use tmux pane discovery before sending DS / GLM review prompts and before any later plan or evidence gate.

## 2. Accepted QDII Replacement Attempts

| fund_code | Candidate | Source provenance | Quality status | Blockers | Terminal classification | promotion_disposition |
|---|---|---|---|---|---|---|
| `096001` | 大成标普500等权重指数(QDII)A人民币 / 2024 | Public generated outputs record `resolved_source_name=eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, `source_strategy=primary_then_fallback`. | `quality_gate_status=block`; `issue_count=10`. | P0 `nav_benchmark_performance` coverage / traceability and evidence-anchor failure; FQ4 missing-field-rate `42.9%`; P1 gaps: `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`. `manager_strategy_text` passed. | `quality_blocked_after_provenance` | `not_promoted` |
| `040046` | 华安纳斯达克100ETF联接(QDII)A / 2024 | Public generated outputs record `resolved_source_name=eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, `source_strategy=primary_then_fallback`. | `quality_gate_status=block`; `issue_count=7`. | No P0 failed fields; FQ4 missing-field-rate `35.7%` exceeds threshold `35.0%`; P1 gaps: `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`. `manager_strategy_text` passed. | `quality_blocked_after_provenance` | `not_promoted` |
| `019172` | 摩根纳斯达克100指数(QDII)人民币A / 2024 | Public generated outputs record `resolved_source_name=eastmoney`, `fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`, `source_strategy=primary_then_fallback`. | `quality_gate_status=block`; `issue_count=9`. | P0 `manager_strategy_text` coverage / traceability `0.0% / 0.0%`; FQ4 missing-field-rate `35.7%`; P1 gaps: `turnover_rate`, `holdings_snapshot`, `share_change`. | `quality_blocked_after_provenance` | `not_promoted` |

Disposition summary:

- All three accepted attempts have eligible public fallback provenance.
- All three remain quality-blocked after provenance.
- None is replacement-ready, baseline-ready, golden-ready, scoring-ready, source-safe-promoted, clean-denominator-promoted, or accepted as durable corpus input.
- The repeated block pattern is enough to require a disposition decision before further probing; it is not enough to silently skip the accepted enumeration order or change taxonomy.

## 3. Option Comparison After Three Quality-Blocked Candidates

### Option A: Continue To Next Equity-QDII Fallback Candidate

Candidate order from `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md` puts `021539` / 华安法国CAC40ETF发起式联接(QDII)A after `096001`, `040046`, and `019172`.

Arguments for:

- It respects the accepted enumeration order instead of selecting a new row by preference.
- `021539` remains a non-FOF overseas equity QDII by the accepted enumeration table.
- It does not require resolving QDII-FOF taxonomy, `013308` naming/category conflict, or bond QDII asset-class fitness before the next move.
- It can be bounded as a plan-first, single-candidate gate with `provenance_unknown`, `quality_unknown`, and `promotion_disposition=not_promoted` until reviewed evidence proves otherwise.

Arguments against:

- Three consecutive eligible-provenance QDII candidates have already quality-blocked.
- Two of the three block on FQ4 at `35.7%`, only slightly above the threshold, and two show P0 failures in different fields. This suggests a likely QDII report-quality / extraction / applicability gap rather than a simple one-off bad candidate.
- Continuing without a hard stop condition would become blind probing and would not improve core usable v1.

Decision implication:

- Option A is acceptable only as one reviewed plan gate for exactly `021539` / 2024, not as an open-ended evidence loop.

### Option B: Open Taxonomy / Asset-Class Fitness Gate

Possible scope: QDII-FOF eligibility, `013308` naming/category conflict, or bond QDII asset-class fitness.

Arguments for:

- It directly addresses candidate-class ambiguity instead of continuing through similar QDII rows.
- It may clarify whether QDII-FOF, a category-conflict row, or bond QDII should ever satisfy the current QDII replacement slot.

Arguments against:

- It would not produce a near-term replacement candidate for the accepted overseas equity QDII slot.
- The accepted enumeration table already excludes QDII-FOF unless taxonomy gate and ranks bond QDII below equity QDII because of asset-class mismatch.
- Opening taxonomy now could skip `021539` without decision evidence that the remaining non-FOF equity QDII path is exhausted.

Decision implication:

- Option B should remain a fallback path if `021539` plan/evidence is rejected or quality-blocked in the same structural pattern.

### Option C: Stop QDII Replacement And Record Coverage Blocked

Possible scope: record QDII replacement coverage as blocked, then route to another blocker such as FOF/taxonomy or bond positive-risk evidence.

Arguments for:

- It avoids spending more evidence cycles on likely structural QDII quality gaps.
- It may better advance core usable v1 if other blockers have clearer acceptance paths or higher user-value impact.

Arguments against:

- It would leave the accepted equity-QDII enumeration order partially untested, with `021539` still next and no accepted evidence showing it fails.
- It would convert three failed candidates into a slot-level stop without testing the next accepted non-FOF equity QDII row.
- It risks prematurely treating QDII coverage as impossible when the only accepted fact is that three candidates are quality-blocked.

Decision implication:

- Option C is premature before one bounded `021539` plan gate, unless the controller explicitly prioritizes a different blocker for core usable v1.

## 4. First-Principles Judgment

The goal is not to maximize the number of attempted rows. The goal is to establish a small baseline corpus that is usable, traceable, and not promoted on weak evidence.

From first principles:

- Source eligibility alone is insufficient. All three candidates reached eligible fallback provenance, yet all failed quality.
- Repeated QDII blocks are a signal about report-quality / extraction / applicability fit. The process should not keep probing blindly.
- The accepted enumeration order is still decision evidence. Skipping the next non-FOF equity-QDII row requires a reason stronger than fatigue with the previous failures.
- A bounded, reviewed, plan-first gate for the next row is the smallest move that respects both constraints.

Therefore, this artifact recommends one more bounded equity-QDII fallback plan gate for `021539` / 2024, with strict stop conditions. It does not recommend immediate evidence. It does not recommend promotion. It does not recommend taxonomy changes.

## 5. Recommended Next Entry Point

Recommended next entry point:

`QDII replacement fallback candidate evidence plan gate for 021539`

Required constraints for that next gate:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state it follows this disposition decision, not a gate switch.
- Produce a plan artifact before any evidence run.
- Select exactly one candidate: `021539` / report year `2024`.
- Treat `021539` as `provenance_unknown`, `quality_unknown`, and `promotion_disposition=not_promoted` until a reviewed evidence gate proves otherwise.
- Do not run `020712`, active QDII, QDII-FOF, `013308`, bond QDII, `017641`, `096001`, `040046`, or `019172` in that plan gate.
- Preserve accepted states for `096001`, `040046`, and `019172`: eligible public fallback provenance, quality `block`, terminal `quality_blocked_after_provenance`, `promotion_disposition=not_promoted`.
- Preserve the accepted source-failure taxonomy: fallback is eligible only for `not_found` or `unavailable`; `schema_drift`, `identity_mismatch`, and `integrity_error` must fail closed.
- Reuse generated public output reading for provenance; do not infer provenance from stdout-only or internal files.
- Include explicit terminal matrix rows for P0 quality block, FQ4 / non-P0 quality block, provenance incomplete, fail-closed source failure, CLI mismatch, and not-run states.

Stop conditions:

- Stop at plan review if reviewers find the `021539` row is not the accepted next non-FOF equity-QDII candidate.
- Stop at plan review if the proposed commands require direct PDF/cache/source-helper/downloader/source-adapter access.
- Stop before quality if public generated provenance is missing, incomplete, or fail-closed.
- Stop before any promotion if quality gate blocks on P0, FQ4, applicability, or any equivalent report-usability rule.
- If `021539` is quality-blocked after eligible provenance, stop the QDII replacement probing loop and require a new disposition gate. That gate should choose between QDII extraction/applicability diagnosis, taxonomy/asset-class fitness, or recording QDII coverage blocked and routing to another v1 blocker.
- Do not continue automatically to `020712` or later candidates.

Rationale:

- `021539` is the next accepted non-FOF overseas equity QDII row after three failed attempts.
- A plan-first gate preserves review discipline and prevents unreviewed evidence execution.
- A single-candidate cap prevents blind probing while still avoiding an unsupported skip over accepted enumeration order.

## 6. Preserved Exclusions And Pending Conflicts

These states remain unchanged:

- `017641` remains excluded. It has accepted complete eligible fallback provenance but quality-blocked terminal disposition and is not promoted.
- QDII-FOF rows remain excluded unless a separate taxonomy gate accepts QDII-FOF for this replacement slot.
- `013308` remains a naming/category conflict and must not enter evidence without a separate reviewed taxonomy/controller decision.
- Bond QDII candidates remain asset-class fitness pending and must not enter evidence without explicit controller acceptance that bond QDII can satisfy this equity-QDII replacement need.

This artifact does not decide taxonomy, asset-class fitness, QDII-FOF eligibility, `013308`, bond QDII, baseline/golden status, or durable corpus state.

## 7. Explicit Non-Goals And Prohibitions

This decision artifact prohibits:

- running `fund-analysis` evidence commands;
- running `analyze`, `checklist`, `extraction-snapshot`, `extraction-score`, or `quality-gate`;
- changing production code, tests, renderer, FQ0-FQ6, Service, CLI, `FundDocumentRepository`, source strategy, source-helper fallback semantics, taxonomy, extractor, Host, Agent, Dayu runtime, golden files, baseline fixtures, durable corpus state, clean denominator, or report-quality corpus;
- changing README, `docs/design.md`, or `docs/implementation-control.md`;
- direct PDF/cache/source-helper/downloader/source-adapter inspection;
- external web probing;
- promoting any candidate to durable baseline, clean denominator, fixture, report-quality corpus, golden answer corpus, accepted replacement, source-safe state, or scoring-ready state;
- committing, pushing, opening PRs, merging, deleting branches, or mutating GitHub state.

## 8. Review Matrix

The controller must use `init-agents` / tmux discovery before actual handoff. This worker did not dispatch agents.

| Stage | Agent | Required artifact |
|---|---|---|
| Decision review 1 | AgentDS | `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-review-ds-20260527.md` |
| Decision review 2 | AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-review-glm-20260527.md` |
| Controller judgment | Controller | `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-controller-judgment-20260527.md` |

Review focus:

- confirm Startup Packet replay and that this is not a gate switch;
- confirm the three accepted candidate summaries match accepted evidence and controller judgments;
- challenge whether one more `021539` plan gate is justified after three quality-blocked attempts;
- confirm the recommendation is plan-first and single-candidate only;
- confirm `provenance_unknown`, `quality_unknown`, and `promotion_disposition=not_promoted` are preserved for `021539`;
- confirm exclusions for `017641`, QDII-FOF, `013308`, and bond QDII are preserved;
- confirm no code/test/renderer/FQ0-FQ6/Service/CLI/FundDocumentRepository/source strategy/taxonomy/extractor/Host/Agent/Dayu/golden/baseline changes or promotions are authorized.

## 9. Validation

| Command | Exit code | Result |
|---|---:|---|
| `git diff --check` | 0 | passed |
