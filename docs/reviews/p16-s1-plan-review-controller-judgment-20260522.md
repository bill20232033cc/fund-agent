# P16-S1 Plan Review Controller Judgment（2026-05-22）

## Verdict

`ACCEPTED_READY_FOR_EVIDENCE_ACQUISITION_IMPLEMENTATION`

Controller accepts `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` without requiring a plan revision.

The next gate is:

```text
P16-S1 enhanced-index production golden candidate evidence acquisition implementation
```

This next gate may produce an evidence artifact only. It must not edit production golden files unless a later reviewed golden implementation gate is opened.

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` | Plan under review |
| `docs/reviews/p16-s1-plan-review-mimo-20260522.md` | Independent plan review |
| `docs/reviews/p16-s1-plan-review-glm-20260522.md` | Independent plan review |
| `docs/reviews/post-p15-follow-up-plan-review-controller-judgment-20260522.md` | P16-S1 entry constraints |
| `docs/reviews/p15-s1a-code-review-controller-judgment-20260522.md` | Accepted P15 negative evidence result |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |

Excluded inputs remain excluded: `docs/design0522.md`, `docs/implementation-control0522.md`, and `docs/repo-audit-20260521.md` are not current truth for this gate.

## First-principles Judgment

The plan answers the narrow question assigned by post-P15 controller judgment: whether selected-fund enhanced-index candidates can be evaluated for future production golden evidence through the current P13/P14 `index_profile` / `tracking_error` extraction and comparable path.

It preserves the core evidence invariant: fund document identity, extracted structured data, rejected evidence, and future golden eligibility must all come from the same Fund Capability boundary through `FundDocumentRepository` and/or `FundDataExtractor`. It does not infer `tracking_error` from target/limit language, manager narrative, benchmark-only text, external index data, or calculations.

The plan also keeps sequencing correct:

```text
plan-review -> evidence acquisition artifact -> reviewed acceptance -> separate golden implementation gate
```

## Reviewer Verdicts

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS_WITH_FINDINGS` | Accepted; findings are low/info and do not require plan revision |
| AgentGLM | `PASS_WITH_FINDINGS` | Accepted; findings are info-level implementation constraints |

Both reviewers verified the five candidates against `docs/code_20260519.csv`, accepted the stable CSV-order evaluation plan, confirmed source fallback taxonomy and fail-closed handling, and found no golden sequencing violation.

## Finding Dispositions

| Finding | Source | Disposition | Controller ruling |
|---|---|---|---|
| Candidate ordering does not explicitly optimize production value or shortest evidence loop | MiMo F1, GLM F3 | Accepted as non-blocking | The CSV-stable ordering is more auditable under the allowed inputs. Because all five candidates must be classified, order affects efficiency but not correctness. No plan revision required. |
| CSV "category" wording could be confused with structured fund type | MiMo F2 | Accepted as non-blocking | Future implementation must continue treating CSV category/name as candidate-selection facts only. Golden eligibility requires structured `classified_fund_type`. |
| Per-candidate `source_blocker` optionality is implicit | MiMo F3 | Accepted as non-blocking | Future implementation should populate `source_blocker` only when access, identity, or source validation fails; successful records should explicitly mark blocker as absent or empty. |
| Evidence-acquisition artifact path is concrete | MiMo F4 | Accepted as positive confirmation | Future implementation should use `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md`. |
| `index_profile.source_tier` is not a design-defined field name | GLM F1 | Accepted as implementation constraint | Future evidence artifact must map `index_profile` subfields to actual extractor output. If `source_tier` has no code field, use the actual field/provenance name and record the plan-to-implementation mapping. |
| Fund-type mismatch lacks a dedicated classification row | GLM F2 | Accepted as implementation constraint | Future evidence artifact must record actual `classified_fund_type`; if it is not `enhanced_index`, mark the candidate not eligible for golden rows and preserve the mismatch as a per-candidate blocker. |

## Implementation Gate Constraints

The next implementation handoff must require:

1. Create only `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` unless a separately reviewed false-negative requires a later extractor slice.
2. Evaluate exactly `004194`, `005313`, `017644`, `019918`, and `019923` in the accepted order.
3. Use only `FundDocumentRepository.load_annual_report()` and/or `FundDataExtractor.extract()` for annual-report access.
4. Record selected CSV row, report year, report kind, document identity, repository source metadata, fallback status, and actual `classified_fund_type` before field evidence conclusions.
5. Classify source blockers using `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, and `integrity_error`; only `not_found` and `unavailable` may allow repository-owned fallback.
6. Evaluate `index_profile` and `tracking_error` separately.
7. Accept `tracking_error` only for direct observed disclosure with observed value, period label, annualization support, `source_type="direct_disclosure"`, `calculation_method="disclosed"`, parseable value, provenance, and complete anchor.
8. Fail closed for target/limit text, manager narrative, benchmark-only `tracking_error`, standard-deviation-only text, ambiguous/unparseable values, incomplete anchors, source contract failures, identity mismatch, and integrity errors.
9. Treat `001548` production `tracking_error` as still blocked and `161725` as fixture-only.
10. Do not edit golden files, source code, tests, README, design/control truth, selected CSV, RR-13 data, branches, PRs, or external state in this evidence-acquisition gate.

## Control Update

`docs/implementation-control.md` should record plan acceptance, reviewer verdicts, this controller judgment, and set the next entry point to P16-S1 evidence acquisition implementation.

## Validation

Controller validation to run before commit:

```bash
git diff --check HEAD
```
