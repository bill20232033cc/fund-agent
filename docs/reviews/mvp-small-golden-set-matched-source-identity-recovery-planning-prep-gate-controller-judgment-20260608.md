# Controller Judgment: Matched Annual-Report Source Identity Recovery Planning/Prep Gate

## Judgment

Accepted locally.

This heavy planning/prep gate accepts the revised code-generation-ready plan:

- `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-20260608.md`

It does not accept matched annual-report source identity for any row. It does not accept exact/numeric extractor correctness. It does not authorize source/PDF/network/live acquisition.

## Basis

Current control truth was verified before this gate:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Slice C Option 1 source identity acquisition is accepted and found no matched annual-report source identity.
- Slice C Option 2 parser/fixture mechanics is accepted and preserves all five rows as `synthetic/unmatched`.
- Exact/numeric extractor correctness remains blocked.
- Slice E first no-live Agent body-chapter mechanics remains current code fact.
- Full production Agent runtime, multi-year runtime, score-loop, provider/default/runtime change, golden/readiness promotion, live acceptance, release and PR state changes remain future scope.

## Review Results

- Review A: `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-review-a-20260608.md` initially failed on two blocking findings.
- Review B: `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-review-b-20260608.md` initially failed on five findings.
- Re-review A: `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-rereview-a-20260608.md` resolved schema/status mapping but found one residual manual PDF boundary issue.
- Re-review B: `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-rereview-b-20260608.md` passed.
- Re-review A2: `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-rereview-a2-20260608.md` passed.

## Accepted Decisions

1. Source identity recovery remains a planning/prep outcome only in this gate.
2. Manual docs-only evidence intake may record user-provided official metadata, locator/id, and user-provided checksum, but must not read, parse, hash, or inspect PDF files.
3. Any future PDF/network/source acquisition must be separately authorized and must go through `FundDocumentRepository` or a separately accepted `FundDocumentRepository`-compatible intake boundary.
4. Local PDF path plus checksum without official locator/id cannot establish matched identity.
5. Source identity must map to the existing evidence contract, including `ReportSourceDocument.document_type=annual_report`, `identity_status=verified_annual_report`, `source_failure_category=none`, `fallback_allowed=false`, `fallback_used=false`, and populated `review_artifact_refs`.
6. Row-field unlock is keyed by `fund_code + report_year + field_name + sub_field`; tabular or repeated fields require a stable locator such as `metric_id`, `table_id`, or `row_locator`.
7. Retained excerpts must be minimal and cannot include full PDFs, whole pages, whole chapters, whole tables, broad extracts, or cumulative reconstruction of a substantial annual-report section.

## Residuals And Owners

| Residual | Owner | Next gate |
|---|---|---|
| No matched source identity has been recovered for the five rows. | Controller/user | `matched-source manual evidence intake gate` or `matched-source FundDocumentRepository acquisition evidence gate` after explicit authorization. |
| Source identity manifest schema and fixture projection are not implemented. | Future implementation worker | Future source identity implementation/evidence gate. |
| Exact/numeric extractor correctness remains blocked. | Controller | Future row-field exact/numeric correctness implementation gate after accepted matched identity and field anchors. |
| Golden/readiness promotion remains unauthorized. | Controller/user | Separate future promotion gate only. |

## Stop Conditions Preserved

The accepted plan does not authorize:

- live LLM, retry, endpoint/DNS/curl/socket/provider probe;
- `FundDocumentRepository` live access, PDF download, network, fallback, akshare, EID;
- extractor/provider/default/runtime/budget/config changes;
- exact/numeric correctness acceptance;
- golden/readiness promotion;
- Chapter calibration, Agent runtime expansion, multi-year runtime, score-loop, PR/release;
- use of arbitrary untracked workspace residue as source truth.

## Validation

- `git diff --check -- docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-20260608.md docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-review-a-20260608.md docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-review-b-20260608.md docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-rereview-a-20260608.md docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-rereview-b-20260608.md` passed before final judgment.

## Next Entry Point

Stop after local accepted checkpoint unless the user explicitly authorizes one of:

1. `matched-source manual evidence intake gate`.
2. `matched-source FundDocumentRepository acquisition evidence gate`.
3. A separate non-extractor phase.
