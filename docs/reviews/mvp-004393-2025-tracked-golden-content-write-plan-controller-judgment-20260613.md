# Controller Judgment - 004393 / 2025 Tracked Golden Content Write Planning

Date: 2026-06-13

Gate: `004393 / 2025 Tracked Golden Content Write Planning Gate`

Verdict: `ACCEPT_SOURCE_BODY_VERIFICATION_FIRST_NOT_READY`

## 1. Basis

- Rules truth: `AGENTS.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Startup truth: `docs/current-startup-packet.md`
- Plan: `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-20260613.md`
- MiMo review: `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-review-mimo-20260613.md`
- DS review: `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-review-ds-20260613.md`
- MiMo targeted re-review: `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-rereview-mimo-20260613.md`
- DS targeted re-review: `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-rereview-ds-20260613.md`
- Prior row judgment: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-controller-judgment-20260613.md`

## 2. Controller Decision

The amended plan is accepted.

Direct tracked golden content write implementation is rejected for the current
mainline because the seven accepted rows remain candidate rows with
source-body residuals. Candidate-level acceptance is not sufficient for
correctness-oracle promotion.

The next mainline must verify source body first, but the verification entry is
not automatically authorized to run live EID/network/PDF/FDR commands. It must
start from an explicit access preflight:

- use `FundDocumentRepository.load_annual_report()` or an equivalent
  repository-bounded no-new-live path if already available; or
- obtain separate authorization for a live EID sub-slice before any live access;
  and
- stop if neither path is available or authorized.

Release/readiness remains `NOT_READY`.

## 3. Accepted Plan Facts

| Fact | Disposition | Reason |
|---|---|---|
| Seven rows may proceed only to source-body verification, not tracked write. | ACCEPT | Prior evidence accepted candidate status only and explicitly retained source-body residuals. |
| Two fee rows remain excluded. | ACCEPT | Current template/instructions mark `fee_schedule` as skipped; prior row judgment rejected the fee rows for this route. |
| Source-body verification must be repository-bounded. | ACCEPT | Aligns with `AGENTS.md` and design truth that fund document access goes through the repository boundary. |
| Source-body verification requires no-new-live availability or separately authorized live EID sub-slice. | ACCEPT | Preserves the current gate's no-live boundary and prevents hidden live execution. |
| Row verification must support partial acceptance. | ACCEPT | Golden identity is row-level: `fund_code + report_year + field_name + sub_field`. |
| Field-level match criteria are required. | ACCEPT | Prevents the verification worker from inventing match semantics. |
| Future write implementation must include existing-content preservation, backup/restore safety and value-level cross-checks. | ACCEPT | Prevents unrelated golden truth mutation and transcription drift from verification artifact to tracked JSON. |

## 4. Review Disposition

| Finding | Reviewer | Controller disposition |
|---|---|---|
| Existing-content preservation validation missing. | MiMo F1 | ACCEPTED_AND_RESOLVED. Plan now requires non-target identity and value preservation checks. |
| JSON build command lacked explicit assertions. | MiMo F2 | ACCEPTED_AND_RESOLVED. Plan now asserts build result counts. |
| Source-body verification path did not name repository access. | MiMo F3 | ACCEPTED_AND_RESOLVED. Plan now names `FundDocumentRepository.load_annual_report()` or equivalent repository-bounded path and prohibits direct filesystem PDF reads unless separately authorized. |
| Live/repository access prerequisite was implicit. | DS F1 | ACCEPTED_AND_RESOLVED. Plan now requires no-new-live repository availability or separately authorized live EID sub-slice before verification. |
| All-or-nothing row verification was too coarse. | DS F2 | ACCEPTED_AND_RESOLVED. Plan now uses row-level partial acceptance. |
| Source-body match criteria were undefined. | DS F3 | ACCEPTED_AND_RESOLVED. Plan now defines field-level match criteria. |
| `investment_objective` span-boundary verification could become re-extraction. | DS F4 | ACCEPTED_AND_RESOLVED. Plan now uses normalized verbatim substring confirmation. |
| Future JSON rebuild needed backup/restore and value-level cross-check. | DS F5 | ACCEPTED_AND_RESOLVED. Plan now requires backup/restore safety and value-level cross-check against the source-body verification artifact. |

Both targeted re-reviews returned `PASS`; no unresolved findings remain.

## 5. Boundary Confirmation

This planning gate did not perform or authorize:

- tracked golden answer content edits;
- fixture promotion edits;
- source, test, README, design or runtime behavior changes;
- live EID, network, PDF, FDR, provider, LLM, analyze, checklist, readiness,
  release, PR, push or merge commands;
- cleanup, archive, delete or move actions;
- readiness/release status changes.

## 6. Residuals

| Residual | Owner | Destination |
|---|---|---|
| Seven candidate rows need source-body verification before tracked truth. | Golden content/source owner | `004393 / 2025 Controlled Source-body Verification Gate` |
| Source-body access may require live authorization if no repository-bounded no-new-live access exists. | Controller / evidence owner | Verification gate access preflight or separately authorized live EID sub-slice. |
| Fee rows are rejected for this route. | Golden contract/source owner | Separate fee-row contract/source-owner clarification gate if needed. |
| Fixture promotion remains year-blind/unresolved. | Fixture promotion owner | Separate fixture promotion design/evidence gate. |
| Release/readiness remains `NOT_READY`. | Release owner | Future readiness rollup after content and promotion residuals close. |

## 7. Next Entry

Recommended next mainline entry:

```text
004393 / 2025 Controlled Source-body Verification Gate
```

Entry condition:

- first perform a planning/access-preflight step that determines whether
  repository-bounded no-new-live access is available, or whether the user must
  separately authorize a live EID sub-slice;
- do not run live/network/PDF/FDR commands unless that live sub-slice is
  separately authorized;
- do not open tracked golden content write implementation until a controller
  judgment accepts exact source-body verification for the rows to write.
