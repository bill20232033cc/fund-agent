# MVP fund report template typed contract redesign controller judgment

## Controller Decision

- Gate: `MVP fund report template typed contract redesign gate`
- Phase: `MVP typed template and internalized agent execution phase`
- Classification: `heavy`
- Decision: `accepted as design-only future template/audit contract architecture`
- Design artifact: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md`
- Reviews: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-ds-20260602.md`; `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-mimo-20260602.md`
- Fix evidence: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-review-fix-evidence-20260602.md`
- Re-reviews: `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-rereview-ds-20260602.md`; `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-rereview-mimo-20260602.md`

This gate accepts a future design direction only. It does not authorize code changes, template truth replacement, `contracts.py` changes, auditor changes, provider budget changes, score-loop wiring, deterministic fallback, stdout partial-report behavior, quality gate changes, golden/readiness changes, retained report mutation, or any current-fact wording that says the typed redesign is implemented.

## Accepted Future Design

1. Typed `ChapterContract` is accepted as the future contract surface for Fund template semantics, while current chapter ids remain `0-7`.
2. `EvidenceAvailability` is accepted as a derived supplemental availability view over same-source `ChapterFactProjection`, not a replacement unless a later gate accepts that.
3. Evidence-conditional `must_not_cover` is accepted for the retained Ch3 failure mode, with `allowed_contexts`, partial availability handling, and Chinese polarity/quasi-positive feasibility as mandatory preconditions before implementation.
4. `RequiredOutputItem.when_evidence_missing` is accepted as the missing/degrade mechanism; overlapping `MustAnswerClause` fallback is deferred.
5. Chapter 0 consuming Chapter 7 is accepted only with fail-closed final assembly when required body chapters are not accepted.
6. Per-chapter `audit_focus` is accepted only for bounded LLM semantic audit emphasis and repair hint grouping; it cannot disable programmatic blockers.

## Rejected Or Deferred

- Ch2 structural split, `0+9` / `0+10` numbering, public chapter count changes, independent Ch2 subchapter ids, and exact chapter renumbering are deferred to a separate structural gate.
- `first_class_facets` and facet-respect programmatic wiring are deferred to a separate facet wiring / programmatic audit gate.
- `source_strength_by_requirement` is deferred unless a later gate defines strength levels, relation to data-tier availability, and audit semantics.
- External draft timeout percentage/root-cause allocations are rejected for this gate. Ch2/Ch4/Ch6 timeout evidence remains provider runtime gate evidence because retained diagnostics show `small_prompt_provider_timeout`.
- Direct 5Y PDF/raw text injection into LLM context, provider budget changes, score-loop wiring, quality gate changes, final judgment taxonomy changes, golden/readiness changes, migration timelines, and acceptance-rate targets are rejected for this gate.

## Review Finding Disposition

Both independent reviewers concluded the fixed design passes.

| Finding group | Controller disposition | Re-review status |
|---|---|---|
| DS F1-F8 | Accepted for design fix; fixed through added preconditions, deferrals, and handoff criteria | `fixed` |
| MiMo F1-F12 | Accepted for design fix; fixed through audit_focus boundary, EvidenceAvailability relationship, allowed_contexts, Ch2/Ch7 safeguards, and scope isolation | `fixed` |

No accepted finding remains unresolved. No new blocker was introduced by the design fix.

## Residuals And Owners

| Residual | Owner / destination |
|---|---|
| Chinese assertion polarity / quasi-positive detection feasibility | Mandatory precondition before any polarity-bearing `MustNotCoverClause` implementation gate |
| Programmatic matching boundaries for `allowed_contexts` | Future typed contract schema or Ch3-only calibration plan |
| Programmatic audit extensions for data availability matching, evidence-gap declarations, cross-chapter consistency, and facet respect | Separate programmatic audit extension gates |
| Ch2/Ch4/Ch6 provider runtime timeout | Future provider runtime budget calibration gate |
| Ch2 structural split or public chapter count change | Separate structural template gate |
| `first_class_facets` | Separate facet wiring / programmatic audit gate |
| Multi-year annual evidence scope | Future multi-year annual evidence scope design gate; no raw multi-year PDF prompt injection authorized |

## Next Entry Point

The phase should proceed to `MVP internalized Agent engine/tool-loop contract execution design gate`, using this accepted template/audit contract design as future-design input. That next gate remains design/review only unless separately authorized, and it must not implement Agent runner/tool-loop, typed contracts, Ch3 calibration, provider budget, multi-year evidence, or score-loop changes.

## Controller Self-Check

- Role: controller judgment and truth-sync only.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, external redesign draft, retained 006597 artifact, Gate 1 design/review/fix/re-review artifacts.
- Scope boundary: docs/reviews judgment and minimal design/control/startup sync; no code, template truth replacement, runtime, provider, score, golden, quality gate, report, or retained artifact changes.
- Stop conditions: none; re-reviews report all accepted findings fixed.
- Next action: sync `docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md` as accepted future design, then create an accepted local checkpoint.
