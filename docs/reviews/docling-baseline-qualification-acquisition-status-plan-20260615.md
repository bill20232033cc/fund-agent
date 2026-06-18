# Docling Baseline Qualification Acquisition Status Plan - 2026-06-15

Status: `READY_FOR_PLAN_REVIEW_NOT_READY`
Gate: `Docling Baseline Qualification Acquisition Status Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Scope

This planning gate prepares Gate 0 for Docling baseline qualification. It does not qualify Docling as a baseline candidate, does not run conversion, does not acquire reports, and does not compare field correctness.

The plan answers only:

- which S1-S6 sample artifacts are already accepted inputs;
- which local files are merely visible candidates;
- which samples need bounded EID-only acquisition;
- which samples lack pdfplumber full representation JSON;
- which field families have reviewed/golden reference coverage candidates;
- which samples have EID HTML render availability accepted or unclassified;
- which next gate should run first.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md` targeted guardrail search
- `docs/reviews/docling-baseline-qualification-plan-20260615.md`
- `docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md`
- `docs/reviews/same-report-full-annual-representation-json-evidence-controller-judgment-20260615.md`
- `docs/reviews/bounded-same-report-eid-html-render-discovery-controller-judgment-20260615.md`
- Manual evidence intake controller judgments for small-golden rows:
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-004393-controller-judgment-20260608.md`
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-batch-004194-006597-110020-017641-controller-judgment-20260609.md`
  - `docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-controller-judgment-20260609.md`
- Local metadata-only file inventory:
  - `reports/representation-json/*`
  - `reports/docling-route-a/*`
  - `cache/pdf/*`
  - `cache/documents/parsed_reports/*`
  - `tests/fixtures/fund/small_golden_set/*/expected_fields.json`

No PDF body, network, FDR, Docling conversion, pdfplumber export, provider/LLM, analyze/checklist/golden/readiness/release/PR command was run.

## 3. Current Accepted Facts

| Fact | Status | Boundary |
|---|---|---|
| Current mainline is `Docling Baseline Qualification Acquisition Status Planning Gate`. | ACCEPTED | Planning-only. |
| Release/readiness remains `NOT_READY`. | ACCEPTED | No readiness or PR claim. |
| Production annual-report source policy remains EID single-source/no-fallback. | ACCEPTED | No Eastmoney, CNINFO or fund-company fallback. |
| Docling remains candidate-only. | ACCEPTED | No production parser replacement or source-truth claim. |
| EID HTML render source kind remains `eid_xbrl_html_render_candidate`. | ACCEPTED | Not raw XML/XBRL instance proof. |
| S1 `004393 / 2025` has accepted Docling, pdfplumber and EID HTML full representation JSONs. | ACCEPTED | Representation evidence only, not field correctness. |
| S2-S6 local cache and fixture files are visible. | METADATA_ONLY | Visibility is not accepted source provenance or baseline-qualification input. |

## 4. Sample Matrix Acquisition Status

| Sample | Fund / year | Profile role | Local artifact visibility | Current accepted status | Acquisition status decision |
|---|---|---|---|---|---|
| S1 | `004393 / 2025` 安信企业价值优选混合A | Active fund seed | EID PDF cache visible; parsed cache visible; three full representation JSONs visible and accepted. | `accepted_tri_route_representation_seed` | `accepted_local_artifact`; no acquisition needed for Gate 0, but field-family reference coverage remains partial. |
| S2 | `004393 / 2024` 安信企业价值优选混合A | Same fund prior year | EID-labeled PDF cache visible; parsed cache visible; small-golden expected fields visible; manual source identity accepted docs-only. | `visible_local_candidate_with_manual_identity` | `needs_no_live_local_provenance_acceptance`; bounded acquisition only if local EID provenance cannot be accepted. |
| S3 | `004194 / 2024` 招商中证1000指数增强A | Enhanced index | EID-labeled PDF cache visible; parsed cache visible; small-golden expected fields visible; manual source identity accepted docs-only. | `visible_local_candidate_with_manual_identity` | `needs_no_live_local_provenance_acceptance`; bounded acquisition only if local EID provenance cannot be accepted. |
| S4 | `006597 / 2024` 国泰利享中短债债券A | Bond fund | EID-labeled PDF cache visible; parsed cache visible; small-golden expected fields visible; manual source identity accepted docs-only. | `visible_local_candidate_with_manual_identity` | `needs_no_live_local_provenance_acceptance`; bounded acquisition only if local EID provenance cannot be accepted. |
| S5 | `017641 / 2024` 摩根标普500指数(QDII)人民币A | QDII | PDF cache visible but not EID-labeled; parsed cache visible; small-golden expected fields visible; manual evidence accepted docs-only with residual uncertainty. | `visible_local_candidate_non_eid_provenance_unaccepted` | `needs_bounded_eid_only_acquisition_or_replacement`; do not use non-EID local PDF as active sample input. |
| S6 | `110020 / 2024` 易方达沪深300ETF联接A | Index / ETF-linked | PDF cache visible but not EID-labeled; parsed cache visible; small-golden expected fields visible; manual evidence accepted docs-only with residual uncertainty. | `visible_local_candidate_non_eid_provenance_unaccepted` | `needs_bounded_eid_only_acquisition_or_replacement`; do not use non-EID local PDF as active sample input. |

## 5. Representation Artifact Status

| Sample | Docling full JSON | pdfplumber full JSON | EID HTML render full JSON | Decision |
|---|---|---|---|---|
| S1 `004393 / 2025` | Accepted: `reports/representation-json/004393_2025_docling_full.json` | Accepted: `reports/representation-json/004393_2025_pdfplumber_full.json` | Accepted: `reports/representation-json/004393_2025_eid_html_render_full.json` | Can seed later Gates A-D, still not field truth. |
| S2 `004393 / 2024` | Missing | Missing | Unclassified | Needs local provenance acceptance, then pdfplumber export planning/execution; Docling conversion remains later. |
| S3 `004194 / 2024` | Missing | Missing | Unclassified | Same as S2. |
| S4 `006597 / 2024` | Missing | Missing | Unclassified | Same as S2. |
| S5 `017641 / 2024` | Missing | Missing | Unclassified | First requires EID-only acquisition or replacement. |
| S6 `110020 / 2024` | Missing | Missing | Unclassified | First requires EID-only acquisition or replacement. |

## 6. Reference Fact Coverage Status

Reference facts must stay separate from route agreement. Docling/pdfplumber/EID HTML agreement cannot become field correctness proof.

| Sample group | Visible reference candidates | Current accepted status for baseline qualification | Required next handling |
|---|---|---|---|
| S1 `004393 / 2025` | Accepted tracked golden content exists for a limited seven-row current surface. | Partial only; field-family manifest not yet established for Docling baseline scoring. | Build a field-family reference coverage manifest before any field correctness gate. |
| S2-S6 small-golden 2024 rows | `tests/fixtures/fund/small_golden_set/*/expected_fields.json` visible; manual evidence intake artifacts exist. | Candidate reference material only for this route; prior judgments explicitly did not unlock exact/numeric correctness or field-level expected values for baseline qualification. | Plan a same-report reference-fact coverage gate that maps each field family to accepted reference basis or marks it out of scope. |

Minimum field-family buckets for the coverage manifest:

- fund identity / share class;
- fund type and preferred lens;
- manager profile / manager holding;
- portfolio holdings;
- performance / return and benchmark;
- fees / costs;
- turnover applicability;
- risk / drawdown / bond or QDII-specific disclosures;
- index/enhanced-index methodology and tracking;
- financial statement tables.

## 7. EID HTML Render Availability Status

| Sample | Status | Handling |
|---|---|---|
| S1 `004393 / 2025` | Accepted same-report EID HTML render JSON. | Available for later route comparison as `eid_xbrl_html_render_candidate`. |
| S2-S6 | Unclassified. | Do not fabricate URLs or assume availability. Later bounded EID HTML availability evidence may run only with explicit live/network authorization. Until then, later comparisons must degrade to Docling/pdfplumber-only for those samples. |

## 8. Proposed Gate Sequence

### Gate 0A. Local Artifact Provenance Status Evidence

Goal: classify visible local S1-S6 artifacts without reading PDF bodies or running repository/parser/conversion commands.

Allowed commands:

- `git branch --show-current`
- `git status --short`
- `ls -lh <explicit sample paths>`
- `stat <explicit sample paths>`
- `python -m json.tool <explicit metadata JSON> > /dev/null`
- `jq <metadata-only allowlisted queries> <explicit JSON>`
- `git diff --check`

Metadata allowlist:

- top-level keys and file byte size;
- sample identity keys: `fund_code`, `report_year`, `document_kind`, `source_kind`, `source_boundary`;
- source-provenance metadata keys: source URL/id/hash/status fields when already present in metadata JSON;
- representation summary keys only: `summary_metrics`, counts, booleans, hashes and status labels.

Forbidden:

- PDF body read, PDF parse, Docling conversion, pdfplumber export, `FundDocumentRepository`, EID/FDR/network/live commands, non-EID fallback, provider/LLM, analyze/checklist/golden/readiness/release/PR.

Output:

- `docs/reviews/docling-baseline-qualification-local-artifact-provenance-status-evidence-20260615.md`

Expected classification:

- S1: `accepted_local_artifact`
- S2-S4: `local_eid_candidate_needs_controller_acceptance`
- S5-S6: `needs_bounded_eid_only_acquisition_or_replacement`

### Gate 0B. Bounded EID-only Acquisition Planning / Execution

Goal: only if Gate 0A cannot accept S5-S6 or any S2-S4 local artifact, plan and then execute bounded EID-only acquisition for missing active samples.

Hard rule:

- No Eastmoney, CNINFO, fund-company website or other fallback. If EID cannot provide the sample, choose `replace_required` or `out_of_scope`, not fallback.

Output:

- Planning artifact first.
- Evidence artifact only after explicit live/network authorization.

### Gate 0C. Pdfplumber Full Representation Export Planning / Execution

Goal: after all active samples have accepted EID-controlled local annual-report artifacts, produce repeatable pdfplumber full representation JSON for S2-S6.

Boundary:

- The export route must be owned by Fund documents / `FundDocumentRepository` internals or by a separately accepted repository-internal diagnostic runner.
- No Service/UI/Host/renderer/quality gate may directly read PDF files or parser internals.
- No worker may perform ad hoc direct PDF filesystem body reads outside the accepted export runner.

Forbidden:

- Docling conversion and field correctness scoring.

Output:

- Planning artifact first.
- Export evidence artifact and JSON outputs only after plan acceptance.

### Gate 0D. Same-report Reference Fact Coverage Planning

Goal: classify field-family reference coverage by sample before any Docling correctness comparison.

Rules:

- Existing `expected_fields.json` files and manual intake artifacts are reference candidates, not automatic truth.
- Field correctness scope must include only accepted sample/field-family pairs.
- Missing reference families become `not_scorable_for_field_correctness`, not route failure.

### Gate 0E. EID HTML Render Availability Planning / Evidence

Goal: classify EID HTML render availability for S2-S6 only if tri-route comparison is still required.

Rules:

- No fabricated HTML render URLs.
- No raw XML/XBRL proof claim.
- If not authorized or unavailable, later evidence must run two-route comparison for that sample.

## 9. Stop Conditions

Stop and return to controller if:

- a worker treats visible cache files as accepted EID provenance without controller evidence;
- S5/S6 require non-EID fallback to stay in the matrix;
- any plan requires PDF body reads before explicit evidence authorization;
- route agreement is used as field truth;
- Docling output is described as source truth, production baseline or readiness proof;
- Service/UI/Host/renderer/quality gate direct consumption of parser/Docling/XBRL artifacts appears;
- any live/network/EID/FDR/PDF/Docling conversion/pdfplumber export/manual reference review command is needed before the corresponding accepted evidence gate.

## 10. Validation

Planning-gate validation:

```text
git diff --check
```

Next evidence-gate validation will be defined by Gate 0A and must stay metadata-only unless separately authorized.

## 11. Review Checklist

Reviewers should check:

- Does the plan keep Docling candidate-only and `NOT_READY`?
- Does it separate local file visibility from accepted source provenance?
- Does it avoid non-EID fallback?
- Does it keep S5/S6 from using non-EID-labeled local PDFs without EID acceptance?
- Does it separate reference facts from route agreement?
- Does it avoid Docling conversion, pdfplumber export, manual review and live commands in this planning gate?
- Does it keep all future implementation inside Fund documents / `FundDocumentRepository` boundaries?

## 12. Next Gate Recommendation

Immediate next gate:

`Docling Baseline Qualification Acquisition Status Plan Review Gate`

If review passes, proceed to:

`Docling Baseline Qualification Local Artifact Provenance Status Evidence Gate`

Do not proceed directly to bounded EID acquisition, pdfplumber export, Docling conversion, field correctness comparison or production integration.

## 13. Final Verdict

`VERDICT: READY_FOR_PLAN_REVIEW_NOT_READY`
