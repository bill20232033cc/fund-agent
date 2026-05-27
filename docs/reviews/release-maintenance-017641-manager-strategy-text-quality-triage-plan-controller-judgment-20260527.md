# 017641 Manager Strategy Text Quality Triage Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `017641 manager_strategy_text extraction/quality triage gate`
> Plan artifact: `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `110020 reviewed coverage candidate evidence accepted locally` |
| Startup Packet next entry point | `017641 manager_strategy_text extraction/quality triage gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `110020 reviewed coverage candidate evidence local accepted commit`; current HEAD before this judgment was `cc26004` |

This gate did not switch away from the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Plan Summary

The accepted plan keeps `017641` / 2024 outside durable baseline, clean denominator, fixture, report-quality corpus, and golden answer corpus. It treats the current state as:

- `fund_type_slot=qdii_fund`
- source provenance complete after eligible fallback with `primary_failure_category=unavailable`
- quality gate `block`
- blocking cluster: `FQ2 manager_strategy_text P0`, `FQ3 manager_strategy_text P0`, and `FQ2F P0 field failure`
- `promotion_disposition=not_promoted`

The plan correctly rejects direct extractor implementation as premature. A quality-gate block is a symptom, not same-source root-cause evidence. The next minimal step is a public-only evidence triage gate using existing `fund-analysis extraction-snapshot`, `extraction-score`, and `quality-gate` commands through repository-backed production paths.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-review-mimo-20260527.md` | `PASS` |
| AgentGLM | `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-review-glm-20260527.md` | `PASS_WITH_FINDINGS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| GLM F1: policy/taxonomy candidate path should explicitly compare against current `design.md` P0 applicability | **accepted as next-gate guidance** | The plan already forbids taxonomy redesign in this gate, but the evidence worker must record current P0 applicability before classifying a policy/taxonomy issue. |
| GLM F2: manual public-output inspection step could be inconsistent | **accepted as mitigated** | The plan requires field-level status from `snapshot.jsonl`, `score.json`, and `score.md`, plus exact FQ issue records; the next evidence review must verify this granularity. |
| GLM F3: `fund_type_slot=qdii_fund` provenance | **informational** | Accepted evidence already records the QDII slot; no plan change is required. |

No blocking finding remains. No re-review is required.

## Accepted Next Entry Point

`017641 manager_strategy_text public-only evidence triage gate`

Required evidence-gate constraints:

- Use only public CLI commands and accepted artifacts.
- Keep generated outputs in ignored report paths; track only a summary evidence artifact.
- Classify into exactly one terminal state: `extractor_gap_requires_implementation_plan`, `disclosure_data_gap_not_baseline_ready`, `policy_taxonomy_issue_requires_design_plan`, `replacement_or_exclusion_required`, or `reject_exclude_due_to_evidence_violation`.
- Preserve `promotion_disposition=not_promoted`.
- Stop on command failure, provenance tuple regression, insufficient public evidence, reviewer `BLOCK`, direct PDF/cache/source-helper access, source strategy mutation, quality-gate weakening, or promotion attempt.

## Validation

- `git diff --check` passed before controller judgment.
- This gate is docs/control/review only; no source or test code changed.

## Non-Goals Preserved

No renderer, FQ0-FQ6, Service/CLI default behavior, source strategy, `FundDocumentRepository`, extractor logic, Host/Agent/dayu runtime, golden corpus, durable baseline, or GitHub state was changed.
