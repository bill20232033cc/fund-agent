# Post-P15 Follow-up Plan Review Controller Judgment（2026-05-22）

## Verdict

`ACCEPTED_PROCEED_TO_P16-S1_ENHANCED_INDEX_PRODUCTION_GOLDEN_CANDIDATE_EVIDENCE_PLAN_REVIEW`

Controller accepts `docs/reviews/post-p15-follow-up-planning-20260522.md` as the next-phase selection record.

The next gate is:

```text
P16-S1 enhanced-index production golden candidate evidence plan-review
```

This is a plan-review gate only. It must not edit source code, tests, golden files, selected CSV, `docs/design.md`, or `docs/implementation-control.md`, and it must not open production golden rows. Any future evidence acquisition must remain inside the `FundDocumentRepository` / `FundDataExtractor` boundary.

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/post-p15-follow-up-planning-20260522.md` | Next-phase selection artifact |
| `docs/reviews/post-p15-follow-up-plan-review-mimo-20260522.md` | Independent plan review |
| `docs/reviews/post-p15-follow-up-plan-review-glm-20260522.md` | Independent plan review |
| `docs/reviews/p15-s1a-code-review-controller-judgment-20260522.md` | Accepted P15 negative evidence result |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |

Excluded inputs remain excluded: `docs/design0522.md`, `docs/implementation-control0522.md`, and `docs/repo-audit-20260521.md` are not treated as current design/control truth for this gate.

## First-principles Judgment

P15-S1A established, through the project-owned annual-report repository and extractor boundary, that `001548` 2024 has no direct observed `tracking_error` disclosure suitable for production golden rows. Continuing to push `001548` would violate fail-closed evidence discipline and would turn target/limit or narrative text into a correctness oracle.

The selected P16-S1 path is the shortest path that still serves the product objective: close the real selected-fund enhanced-index production evidence gap for conditional P1 fields introduced by P13/P14. It adds no new runtime architecture, does not introduce calculated tracking error or external index adapters, and keeps root-cause evidence and extraction behavior inside the same Fund Capability boundary.

## Reviewer Verdicts

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | Accepted; all findings are non-blocking and carried into P16-S1 constraints |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted; all findings are non-blocking and carried into P16-S1 constraints |

Both reviewers confirmed:

- Do not continue production `tracking_error` golden work for `001548` without new reviewed direct observed disclosure evidence.
- `004194`, `005313`, `017644`, `019918`, and `019923` are selected-fund enhanced-index candidates from `docs/code_20260519.csv`.
- `161725` remains deterministic fixture coverage only, not production selected-fund evidence.
- Golden sequencing remains correct: plan-review before evidence acquisition, evidence acceptance before any golden implementation.

## Finding Dispositions

| Finding | Source | Disposition | Controller ruling |
|---|---|---|---|
| Candidate evaluation order is not specified | MiMo F1, GLM F1 | Accepted | P16-S1 plan must define an explicit candidate evaluation order and the ordering principle. The default should prefer shortest evidence loop and highest production value while still covering all five candidates unless a source blocker is recorded. |
| `index_profile` benchmark-context contract is less explicit than `tracking_error` direct-disclosure contract | MiMo F2, GLM F3 | Accepted | P16-S1 plan must enumerate which `index_profile` subfields can accept benchmark-context evidence under current extractor semantics, and what anchor/provenance is sufficient for each. |
| Annual-report source/download failures need explicit handling | MiMo F3 | Accepted | P16-S1 plan must record per-candidate source availability before evidence classification and use the existing taxonomy: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`. Only `not_found` and `unavailable` may allow fallback; contract/integrity failures fail closed. |
| "also listed in research notes" lacks a concrete source path | GLM F2 | Accepted as cleanup constraint | P16-S1 plan should rely on `docs/code_20260519.csv` as the candidate source of truth, or cite a concrete auxiliary file path. Uncited research-note wording should be removed from future handoff artifacts. |
| Extractor early-return false-negative routing is precise | GLM F4 | Accepted as positive confirmation | If a candidate shows direct-looking disclosure suppressed by current extraction behavior, route it to a separate evidence-backed extractor refinement slice before any golden edit. |

## P16-S1 Entry Constraints

The P16-S1 plan artifact must:

1. Cover `004194`, `005313`, `017644`, `019918`, and `019923`.
2. Define candidate evaluation order and stop budget.
3. Use only `FundDocumentRepository.load_annual_report()` and/or `FundDataExtractor.extract()` for annual-report access.
4. Identify each candidate by fund code, annual-report year, report kind, fund type, and selected-fund source row before evidence classification.
5. Classify `index_profile` and `tracking_error` evidence separately.
6. Require direct observed disclosure for `tracking_error`: observed value, period label, annualization support, `source_type="direct_disclosure"`, `calculation_method="disclosed"`, and complete annual-report anchor.
7. Fail closed for target/limit text, manager narrative, benchmark-only `tracking_error`, standard-deviation-only text, ambiguous text, unparseable values, incomplete anchors, identity mismatch, schema drift, and integrity errors.
8. Keep calculated tracking error, external index adapters, methodology extraction, constituents extraction, E1-E3, Evidence Confirm, Dayu runtime, Host, Engine, and tool loop out of this gate.
9. Separate future evidence acquisition from future golden implementation.

## Control Update

`docs/implementation-control.md` should be updated to record this acceptance and set the next entry point to P16-S1 plan-review.

## Validation

Controller validation to run before commit:

```bash
git diff --check HEAD
```
