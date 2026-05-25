# Release Maintenance ReportEvidenceBundle Typed Model / Projection Implementation Plan Controller Judgment

> Date: 2026-05-25
> Branch: `codex/v0-release-readiness-plan`
> Gate: `typed ReportEvidenceBundle model/projection implementation plan review`
> Controller status: accepted locally; next gate is `ReportEvidenceBundle typed model/projection implementation`

## Step Self-Check

- Current role: controller. This artifact records plan-review disposition, acceptance rationale, residual ownership, and next implementation scope.
- Source of truth: `AGENTS.md`, `docs/design.md` current architecture and §5.4 / §5.4.1 / §5.4.2 / §5.4.3 / §7.2 / §7.3 / §7.4, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, and accepted S2 bundle candidate plan / controller judgment.
- Reviewed implementation plan: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md`.
- Independent reviews: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-review-mimo-20260525.md`, `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-review-ds-20260525.md`.
- Re-reviews after plan patch: `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-rereview-mimo-20260525.md`, `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-rereview-ds-20260525.md`.
- Scope boundary: this judgment does not implement code, tests, renderer, FQ0-FQ6, Host/Agent runtime, Dayu runtime, fixture promotion, push, PR, or external state change.

## Verdict

**ACCEPTED FOR IMPLEMENTATION GATE.**

The patched implementation plan is code-generation-ready for a narrow typed model/projection slice. It chooses concrete file ownership, follows current frozen slotted dataclass style, defines executable value domains and field tables, specifies projection from `StructuredFundDataBundle`, and includes validation tests for negative states and boundary discipline.

The plan is accepted because it advances the product toward a real report-quality fact/evidence contract while preserving current production boundaries: no renderer change, no FQ0-FQ6 behavior change, no source helper access, no parallel extraction path, no Host/Agent package, and no `dayu.host` / `dayu.engine`.

## Accepted Implementation Scope

The next gate may implement only:

| File | Allowed work |
|---|---|
| `fund_agent/fund/report_evidence.py` | Typed Literal domains, frozen slotted dataclasses, explicit projection context, deterministic id helpers, projection from `StructuredFundDataBundle`, preferred-lens projection, validation helpers, and derived review status. |
| `tests/fund/test_report_evidence.py` | Focused unit tests using fake `StructuredFundDataBundle` objects only. |
| `fund_agent/fund/README.md` | Minimal sync only if implementation changes `fund_agent/fund/`; keep it current-state oriented. |

The implementation gate must not touch Service, renderer, FQ0-FQ6 behavior, extraction source adapters, repository internals, Host/Agent packages, Dayu runtime, fixtures, scoring-run outputs, or durable baseline state.

## Finding Disposition

| Finding set | Source | Disposition | Owner / gate |
|---|---|---|---|
| `SourceFailureCategory` included values outside S2 contract | MiMo F-1 | Fixed. Re-review confirmed domain now aligns with S2 and excludes `data_gap` / `not_applicable`. | Closed for plan; implementation test/enum validation required. |
| Missing `accepted_baseline` cannot-be-derived test | MiMo F-2 | Fixed. Re-review confirmed test 21 plus `attempted_review_status` validation. | Closed for plan. |
| Dataclass field specs incomplete | DS F-1; MiMo F-3 | Fixed. Re-review confirmed full field tables for all 12 dataclasses. | Closed for plan. |
| Projection context required/default fields unclear | DS F-2 | Fixed. Re-review confirmed constructor contract is explicit. | Closed for plan. |
| Chapter id conversion ambiguous | DS F-3 | Fixed. Re-review confirmed `f"chapter_{chapter_id}"` with `0..7` validation. | Closed for plan. |
| Mode/value contradiction behavior ambiguous | DS F-4 | Fixed. Re-review confirmed rejected-bundle behavior is required. | Closed for plan. |
| Anchor normalization/dedup/id sequence unclear | DS F-5 | Fixed. Re-review confirmed three-phase pipeline. | Closed for plan. |
| `ReportDataGapOverride` fields missing | DS F-6 | Fixed. Re-review confirmed field table. | Closed for plan. |
| `DerivedCalculation` scope / coverage risk | DS F-7 | Fixed. Re-review confirmed shape-only deferral and residual owner. | Future calculation-source gate. |

## Required Validation For Implementation

The implementation gate must run at least:

```text
python -m pytest tests/fund/test_report_evidence.py
python -m pytest --cov=fund_agent.fund.report_evidence --cov-report=term-missing tests/fund/test_report_evidence.py
python -m pytest tests/fund/test_report_evidence.py tests/fund/template/test_lens_application.py tests/fund/test_extraction_snapshot.py
python -m ruff check fund_agent/fund/report_evidence.py tests/fund/test_report_evidence.py
rg -n "extra_payload|extra_payloads|dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|AnnualReportPdfAdapter|documents\\.sources|download|cache_path|\\.pdf" fund_agent/fund/report_evidence.py tests/fund/test_report_evidence.py
git diff --check
```

Coverage target: `fund_agent.fund.report_evidence` should reach at least 80% line coverage in the focused coverage command. If it does not, the implementation review must list exact uncovered lines, reason, owner, and whether acceptance is still justified.

## Stop Conditions

Stop and return to controller if implementation requires any of:

- direct PDF/cache/source helper/downloader access;
- calling `FundDocumentRepository` inside the projection layer;
- a new extraction path parallel to `FundDataExtractor`;
- `extra_payload`, `extra_payloads`, `**kwargs`, or free dicts for explicit business parameters;
- renderer or v0 8-chapter output changes;
- FQ0-FQ6 behavior changes;
- fixture promotion or durable baseline selection;
- `nav_data` report facts before a separate source-contract slice;
- `fund_agent/host`, `fund_agent/agent`, `dayu.host`, or `dayu.engine`;
- fallback masking for `schema_drift`, `identity_mismatch`, or `integrity_error`;
- treating active-fund Chapter 3 turnover/style-stability as automatic extraction work instead of explicit data-gap / wording constraint first.

## Residuals

| Residual | Owner / next gate | Required handling |
|---|---|---|
| `nav_data` mapping | future `nav_data` source-contract slice | Keep excluded from first implementation. |
| Manual review Markdown evidence | curated-fixture gate | Do not promote JSON fixtures yet. |
| `external_official` | future Repository-style official-source interface gate | Keep metadata-only; no ad hoc network/API access. |
| `accepted_baseline` | curated-fixture / durable-baseline gate | Domain may exist, but first slice must not derive it. |
| `DerivedCalculation` population | future calculation-source gate | First slice only defines shape/default empty tuple. |
| FOF pure coverage | fund-type taxonomy or corpus second pass | Cannot claim complete fund-type baseline coverage yet. |
| Fallback source category | source reliability gate | `110020`, `017641`, and `017970` stay excluded while category is unknown. |

## Validation

```text
rg -n "Conclusion: \\*\\*PASS|RESOLVED|已解决|SourceFailureCategory|accepted_baseline|ReportDataGapOverride|ReportEvidenceProjectionContext|DerivedCalculation" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-rereview-mimo-20260525.md docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-rereview-ds-20260525.md
rg -n "fund_agent/fund/report_evidence.py|tests/fund/test_report_evidence.py|SourceFailureCategory|accepted_baseline|ReportDataGapOverride|ReportEvidenceProjectionContext|FundDocumentRepository|extra_payload|dayu\\.host|dayu\\.engine|renderer|FQ0-FQ6" docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-plan-20260525.md
git diff --check
```

Result: passed.
