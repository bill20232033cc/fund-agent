# Release Maintenance Report-Quality Baseline S1 Score-Schema Fixture Draft Controller Judgment

> Date: 2026-05-25
> Branch: `codex/v0-release-readiness-plan`
> Gate: `report-quality-baseline S1 score-schema fixture draft`
> Controller status: accepted locally; next gate is `report-quality-baseline S1 dry-run evidence collection`

## Step Self-Check

- Current role: controller. This artifact records review disposition, acceptance rationale, residual ownership, and gate bookkeeping only.
- Source of truth: `AGENTS.md`, `docs/design.md` current §5.4 / §5.4.1 / §5.4.2 / §5.4.3 / §6.1 / §6.5, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, and S0 controller judgment.
- Reviewed S1 draft: `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md`.
- Independent reviews: `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-review-mimo-20260525.md`, `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-review-ds-20260525.md`.
- Re-reviews after the S1 draft patch: `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-rereview-mimo-20260525.md`, `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-rereview-ds-20260525.md`.
- Scope boundary: no source code, tests, renderer, FQ0-FQ6 quality gate, Host/Agent package, Dayu runtime, tracked fixture promotion, push, PR, or external state change.

## Verdict

**ACCEPTED FOR NEXT GATE.**

The S1 draft satisfies the current control-doc requirements for an observational report-quality scoring schema and dry-run fixture plan. Both independent reviews returned `PASS_WITH_FINDINGS`; the draft was patched to resolve the minor findings; both re-reviews returned `PASS`.

Based on `docs/design.md` and first principles, accepting this draft is appropriate because it converts S0 corpus evidence into a reviewable schema without claiming a complete scorer, without changing the renderer or quality gate, and without allowing uncertain source or type evidence to enter durable baseline selection.

## Accepted Schema Decisions

| Decision | Accepted behavior | Reason |
|---|---|---|
| Scoring style | Issue-based observations, no weighted total | The design goal is root-cause localization, not premature scoring theater. |
| Dimensions | Seven canonical report-quality dimensions plus constrained `chapter_summary` for skipped chapter summaries | Covers `docs/design.md` §5.4.1 while giving all-N/A chapter summaries a precise record shape. |
| Identity split | `document_identity_status` is separate from `type_slot_membership_status` | Prevents `verified_as_annual_report_but_type_gap` from becoming scoring-ready FOF evidence. |
| Source boundary | `repository_derived`, `derived_calculation`, `external_official`, `manual_review`, `unknown`, `probe_only` | Allows uncertainty to be preserved while excluding `unknown` and `probe_only` from durable baseline selection. |
| Failure categories | `data_gap` is field/fact-level; `not_found` remains document/source-level | Avoids conflating valid documents with missing facts. |
| N/A semantics | `N/A` requires `na_reason` or equivalent `reviewer_note`; all-N/A chapters are `skipped`, not passing | Prevents denominator inflation and unreviewed applicability shortcuts. |
| Terminal review states | `rejected`, `deferred`, and `expired` have transition, reversibility, and denominator semantics | Makes lifecycle behavior explicit enough for dry-run review without implementing a state machine. |
| Dry-run location | Machine outputs stay under ignored `reports/scoring-runs/`; only review artifacts and controller judgments are tracked | Preserves the no-fixture-promotion constraint until a later curated-fixture gate. |

## Finding Disposition

| Finding | Source | Disposition | Owner / gate |
|---|---|---|---|
| Terminal review states lacked transition semantics | MiMo F-1 | Fixed. S1 now defines transition source, reversibility, and denominator / durable baseline behavior for `rejected`, `deferred`, and `expired`. | Closed for S1 draft; executable validation deferred to implementation gate. |
| Issue severity ambiguity | MiMo F-2 | Fixed. Issue-object `severity` is required; record-level `severity` remains optional roll-up. | Closed. |
| Validation only checks term presence | MiMo F-3 | Accepted and documented. Value-domain validation is a residual for S2 / later implementation if schema becomes code. | S2 / later implementation. |
| N/A reason missing | DS F-1 | Fixed. `N/A` records must carry `na_reason` or equivalent `reviewer_note`. | Closed. |
| Skipped chapter `dimension` ambiguous | DS F-2 | Fixed. `chapter_summary` is reserved for `skipped` chapter summary records. | Closed. |
| `data_gap` vs `not_found` distinction implicit | DS F-3 | Fixed. S1 now clarifies `data_gap` means fact/field unavailable despite available document/source boundary. | Closed. |
| Example `ignored_run_path` self-reference | DS F-4 | No change required. The field is defined as the local dry-run output path, so the example is intentional and non-blocking. | Closed. |

## Controller Decisions

1. S1 schema draft is accepted as a design/evidence artifact, not as an implementation contract frozen for code.
2. The next gate is **S1 dry-run evidence collection**, not S2 code implementation.
3. The dry-run may use S0-clean candidates such as `004393`, `004194`, or `006597`, but must not include fallback candidates in durable baseline selection unless their upstream failure category is recovered as `not_found` or `unavailable`.
4. FOF remains a `data_gap`; QDII-FOF must not satisfy `fof_fund` coverage unless a separate taxonomy / precedence gate accepts that behavior.
5. Any dry-run output under `reports/scoring-runs/` remains ignored scratch. The tracked result should be a reviewed Markdown evidence artifact under `docs/reviews/`, followed by controller judgment.
6. S2 code work remains blocked until S1 dry-run evidence proves the schema can localize issues without misleading denominator, source-boundary, or type-slot behavior.

## Boundary Confirmation

- No renderer behavior or v0 8-chapter report output changed.
- No FQ0-FQ6 quality-gate behavior changed.
- No LLM audit, Evidence Confirm, repair loop, patch/regenerate, or chapter writer was claimed as implemented.
- No `fund_agent/host` or `fund_agent/agent` package was created.
- No `dayu.host` or `dayu.engine` dependency was introduced.
- No tracked fixture was promoted from local run outputs.
- Annual-report access and future evidence records remain behind `FundDocumentRepository` or public Fund APIs that themselves use it.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| Fallback upstream failure category unknown for `110020`, `017641`, and `017970` | S1 dry-run evidence / source reliability evidence | Recover the original upstream failure category or exclude the candidate before durable baseline selection. |
| FOF coverage is not fulfilled | S1 second pass or fund-type taxonomy gate | Find a pure repository-verified `fof_fund`, or explicitly decide QDII-FOF precedence. |
| Dry-run evidence has not been collected | S1 dry-run evidence collection | Produce ignored scoring-run output plus tracked review artifact; do not promote fixtures. |
| Schema value-domain validation is not executable yet | S2 / later implementation | Add enum / combination validation tests if the schema becomes code. |
| `ReportEvidenceBundle` relation to `StructuredFundDataBundle` remains undecided | S2 bundle candidate | Decide wrap / evolve / coexist before implementation. |
| Anchor naming and bundle review-status derivation remain open | S1 dry-run / S2 | Normalize based on observed dry-run issue localization. |

## Validation

```text
rg -n "chapter_summary|na_reason|Review State Terminal Semantics|source_boundary|unknown_upstream_failure_category|reports/scoring-runs|value-domain validation|not S2 code implementation" docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-rereview-mimo-20260525.md docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-rereview-ds-20260525.md
git diff --check
```

Result: passed.

## Next Entry Point

`report-quality-baseline S1 dry-run evidence collection`
