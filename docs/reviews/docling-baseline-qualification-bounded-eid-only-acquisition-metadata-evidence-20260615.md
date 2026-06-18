# Docling Baseline Qualification Bounded EID-only Acquisition Metadata Evidence - 2026-06-15

Gate: `Bounded EID-only Sample Acquisition Metadata Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records bounded official EID metadata lookup evidence for the required Docling baseline qualification sample gaps S4/S5/S6.

This gate used only:

- `POST http://eid.csrc.gov.cn/fund/disclose/validate_fund.do`
- `GET http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do`

This gate did not request `instance_show_pdf_id.do`, did not download PDF bytes, did not compute PDF hashes from response bodies, did not write cache files, did not run `FundDocumentRepository`, did not run Docling conversion, did not run pdfplumber export, did not run provider/LLM/analyze/checklist/golden/readiness/release/PR commands, and did not change source policy or production behavior.

## 2. Source Of Truth

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-plan-20260615.md`
- `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-plan-controller-judgment-20260615.md`

Accepted controller routing:

- Required bounded target set: S4 `006597 / 2024`, S5 `017641 / 2024`, S6 `110020 / 2024`.
- Optional S3 `004194 / 2024` is not included in this metadata evidence because the prior controller judgment accepted it as a local EID candidate with hash residual for later export planning.
- Mode: `metadata_only`.

## 3. Preflight

```text
git branch --show-current
feat/mvp-llm-incomplete-run-artifacts

git status --short
 M AGENTS.md
?? .mimocode/
?? docs/audit/
?? docs/code-wiki-and-audit-report-20260613.md
?? docs/dayu-agent-architect-gap-analysis-20260613.md
?? docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md
?? docs/dayu-fund-agent-mvp-gap-discussion-summary-20260613.md
?? docs/learning-roadmap.md
?? docs/liu-chenggang-dayu-ai-coding-roadmap-20260614.md
?? docs/next-development-phaseflow.md
?? docs/reviews/annual-report-docling-parser-discussion-summary-20260613.md
?? docs/reviews/annual-report-document-representation-docling-benchmark-plan-20260614.md
?? docs/reviews/annual-report-document-representation-docling-benchmark-plan-controller-judgment-20260614.md
?? docs/reviews/annual-report-document-representation-docling-benchmark-plan-review-ds-20260614.md
?? docs/reviews/annual-report-document-representation-docling-benchmark-plan-review-mimo-20260614.md
?? docs/reviews/audit-disposition-phaseflow-reconciliation-controller-judgment-20260610.md
?? docs/reviews/csrc-eid-fund-xbrl-official-resource-discovery-evidence-20260614.md
?? docs/reviews/csrc-eid-xbrl-field-correctness-and-taxonomy-blocked-evidence-20260614.md
?? docs/reviews/csrc-eid-xbrl-raw-instance-download-evidence-20260614.md
?? docs/reviews/csrc-eid-xbrl-raw-xml-endpoint-deep-probe-evidence-20260614.md
?? docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md
?? docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-controller-judgment-20260614.md
?? docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-20260614.md
?? docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-review-ds-20260614.md
?? docs/reviews/docling-runtime-local-artifact-no-model-download-containment-proof-evidence-review-mimo-20260614.md
?? docs/reviews/mvp-dayu-host-runtime-governance-adapter-implementation-preflight-20260601.md
?? docs/reviews/mvp-post-eid-artifact-disposition-controller-judgment-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-inventory-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-review-ds-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-startup-judgment-20260609.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-controller-judgment-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-live-evidence-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-ds-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-mimo-20260606.md
?? docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-evidence-20260608.md
?? docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-mimo-review-20260608.md
?? docs/reviews/mvp-small-golden-set-matched-source-retained-excerpt-fixture-planning-prep-gate-plan-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-ds-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-mimo-20260609.md
?? docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md
?? docs/reviews/plan-review-20260609-071706.md
?? docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-20260614.md
?? docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-review-ds-20260614.md
?? docs/reviews/provider-llm-chapter3-missing-required-marker-no-live-diagnostic-evidence-review-mimo-20260614.md
?? docs/reviews/provider-llm-route-stabilization-closeout-controller-judgment-20260614.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/reviews/repo-review-20260527-215953.md
?? docs/reviews/repo-review-20260527-225303.md
?? docs/reviews/repo-review-20260609-130307.md
?? docs/reviews/repo-review-20260609-165959.md
?? docs/reviews/repo-review-20260611-231358.md
?? docs/reviews/workspace-ownership-reconciliation-20260531.md
?? docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md
?? docs/tmux-agent-memory-store.md
?? reports/docling-route-a/
?? reports/live-evidence/
?? reports/manual-llm-smoke/
?? reports/representation-json/
?? reviews/
?? scripts/claude_mimo_simple.py
?? scripts/review-artifact.sh
?? 基金年报/
?? 定性分析模板.md
```

Dirty workspace note: the tracked `AGENTS.md` diff is an unrelated previously rejected rules-sync rewrite and is not used as evidence for this gate. Untracked residue is left untouched.

## 4. Request Method

For each target:

1. Validate fund identity with:
   - method: `POST`
   - URL: `http://eid.csrc.gov.cn/fund/disclose/validate_fund.do`
   - body: `cFundCode=<fund_code>`
2. Search annual-report metadata with:
   - method: `GET`
   - URL: `http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do?aoData=<urlencoded_json>`
   - `aoData` fields:
     - `iDisplayStart=0`
     - `iDisplayLength=10`
     - `fundType=`
     - `reportType=FB010`
     - `reportYear=2024`
     - `fundCompanyShortName=`
     - `fundCode=<fund_code>`
     - `fundShortName=`
     - `startUploadDate=`
     - `endUploadDate=`

No request was sent to `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do`.

Supplemental field check: after DS-role review flagged the accepted-plan requirement for
`fund_name / fund_short_name`, the same `advanced_search_report.do` metadata endpoint was
queried again for the same S4/S5/S6 rows and confirmed row-level `fundShortName` values. The
supplemental query used the same request family and still did not request or download PDF bytes.

## 5. Evidence Matrix

| Sample | Fund/year | validate_fund HTTP | validate content-type / length | validate summary | search HTTP | search content-type / length | Row count | Matched row | Final classification |
|---|---:|---|---|---|---|---|---:|---|---|
| S4 | `006597 / 2024` | `200 OK` | `text/html;charset=UTF-8` / `32` | `isSuccess=true`, `fundId=5755` | `200 OK` | `text/html;charset=UTF-8` / `626` | 1 | `fundCode=006597`, `fundId=5755`, `fundShortName=国泰利享中短债债券`, `organName=国泰`, `reportYear=2024`, `reportCode=FB010010`, `reportDesp=年度报告`, `tableName=PDF`, `uploadInfoId=1253099`, `uploadInfoDetailId=1290497`, `reportName=国泰利享中短债债券型证券投资基金2024年年度报告`, `reportSendDate=2025-03-29` | `eid_metadata_matched_no_download` |
| S5 | `017641 / 2024` | `200 OK` | `text/html;charset=UTF-8` / `33` | `isSuccess=true`, `fundId=12471` | `200 OK` | `text/html;charset=UTF-8` / `625` | 1 | `fundCode=017641`, `fundId=12471`, `fundShortName=摩根标普500指数发起式(QDII)`, `organName=摩根`, `reportYear=2024`, `reportCode=FB010010`, `reportDesp=年度报告`, `tableName=PDF`, `uploadInfoId=1256369`, `uploadInfoDetailId=1293857`, `reportName=摩根标普500指数型发起式证券投资基金(QDII)2024年年度报告`, `reportSendDate=2025-03-31` | `eid_metadata_matched_no_download` |
| S6 | `110020 / 2024` | `200 OK` | `text/html;charset=UTF-8` / `32` | `isSuccess=true`, `fundId=2855` | `200 OK` | `text/html;charset=UTF-8` / `662` | 1 | `fundCode=110020`, `fundId=2855`, `fundShortName=易方达沪深300ETF联接`, `organName=易方达`, `reportYear=2024`, `reportCode=FB010010`, `reportDesp=年度报告`, `tableName=PDF`, `uploadInfoId=1249587`, `uploadInfoDetailId=1286903`, `reportName=易方达沪深300交易型开放式指数发起式证券投资基金联接基金2024年年度报告`, `reportSendDate=2025-03-31` | `eid_metadata_matched_no_download` |

## 6. Official Request URLs

### S4 `006597 / 2024`

```text
POST http://eid.csrc.gov.cn/fund/disclose/validate_fund.do
body: cFundCode=006597

GET http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do?aoData=%5B%7B%22name%22%3A%22iDisplayStart%22%2C%22value%22%3A%220%22%7D%2C%7B%22name%22%3A%22iDisplayLength%22%2C%22value%22%3A%2210%22%7D%2C%7B%22name%22%3A%22fundType%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22reportType%22%2C%22value%22%3A%22FB010%22%7D%2C%7B%22name%22%3A%22reportYear%22%2C%22value%22%3A%222024%22%7D%2C%7B%22name%22%3A%22fundCompanyShortName%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22fundCode%22%2C%22value%22%3A%22006597%22%7D%2C%7B%22name%22%3A%22fundShortName%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22startUploadDate%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22endUploadDate%22%2C%22value%22%3A%22%22%7D%5D
```

### S5 `017641 / 2024`

```text
POST http://eid.csrc.gov.cn/fund/disclose/validate_fund.do
body: cFundCode=017641

GET http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do?aoData=%5B%7B%22name%22%3A%22iDisplayStart%22%2C%22value%22%3A%220%22%7D%2C%7B%22name%22%3A%22iDisplayLength%22%2C%22value%22%3A%2210%22%7D%2C%7B%22name%22%3A%22fundType%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22reportType%22%2C%22value%22%3A%22FB010%22%7D%2C%7B%22name%22%3A%22reportYear%22%2C%22value%22%3A%222024%22%7D%2C%7B%22name%22%3A%22fundCompanyShortName%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22fundCode%22%2C%22value%22%3A%22017641%22%7D%2C%7B%22name%22%3A%22fundShortName%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22startUploadDate%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22endUploadDate%22%2C%22value%22%3A%22%22%7D%5D
```

### S6 `110020 / 2024`

```text
POST http://eid.csrc.gov.cn/fund/disclose/validate_fund.do
body: cFundCode=110020

GET http://eid.csrc.gov.cn/fund/disclose/advanced_search_report.do?aoData=%5B%7B%22name%22%3A%22iDisplayStart%22%2C%22value%22%3A%220%22%7D%2C%7B%22name%22%3A%22iDisplayLength%22%2C%22value%22%3A%2210%22%7D%2C%7B%22name%22%3A%22fundType%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22reportType%22%2C%22value%22%3A%22FB010%22%7D%2C%7B%22name%22%3A%22reportYear%22%2C%22value%22%3A%222024%22%7D%2C%7B%22name%22%3A%22fundCompanyShortName%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22fundCode%22%2C%22value%22%3A%22110020%22%7D%2C%7B%22name%22%3A%22fundShortName%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22startUploadDate%22%2C%22value%22%3A%22%22%7D%2C%7B%22name%22%3A%22endUploadDate%22%2C%22value%22%3A%22%22%7D%5D
```

## 7. Classification Rules Applied

`eid_metadata_matched_no_download` requires:

- `validate_fund.do` parses as JSON-like payload with `isSuccess=true` and non-empty `fundId`;
- `advanced_search_report.do` parses as JSON-like payload with `aaData` list;
- exactly one row satisfies:
  - `fundCode` equals requested fund code;
  - row `fundId` equals validated `fundId`;
  - `fundShortName` is present and does not contradict target fund identity;
  - `reportYear` equals requested report year;
  - `reportCode=FB010010`;
  - `reportDesp=年度报告`;
  - `tableName=PDF`;
  - `uploadInfoId` is present;
  - `reportName` does not contain `摘要`;
  - no attachment path is required.

All three required samples satisfy these metadata-only conditions.

## 8. Blocked Proofs And Residuals

The following are explicitly not proven:

- `not_pdf_download_proof`: no PDF bytes were downloaded.
- `not_pdf_hash_proof`: no PDF hash was computed from response bodies.
- `not_pdf_integrity_proof`: PDF content type and `%PDF-` header were not checked.
- `not_field_correctness_proof`: no PDF, Docling, pdfplumber or HTML table values were compared.
- `not_source_truth`: EID metadata match is not a fund fact truth claim.
- `not_docling_baseline_proof`: Docling baseline qualification still requires full representation export and comparison gates.
- `not_readiness_proof`: release/readiness remains `NOT_READY`.
- `no_repository_behavior_change`: no `FundDocumentRepository` behavior was changed or executed.
- `no_fallback`: no CNINFO, fund-company, Eastmoney, akshare or local non-EID artifact was used.

Residuals:

| Residual | Status | Next handling |
|---|---|---|
| S4/S5/S6 PDF bytes unavailable in EID-controlled local corpus | open | Requires separate `Artifact Capture Evidence Gate` if controller chooses to download/write/hash PDFs. |
| S3 hash gap | accepted residual from prior gate | Carry to export planning or resolve in later bounded artifact capture; not handled in this required-target metadata gate. |
| Control docs still mention prior planning gate in startup/current gate text | control-doc lag | Sync only after controller closeout; do not update in this evidence artifact. |

## 9. Conclusion

Required samples S4/S5/S6 have public official EID annual-report metadata matches for `2024`:

- S4 `006597 / 2024`: `eid_metadata_matched_no_download`
- S5 `017641 / 2024`: `eid_metadata_matched_no_download`
- S6 `110020 / 2024`: `eid_metadata_matched_no_download`

This supports a controller decision to proceed to a separate bounded EID artifact-capture planning/evidence gate if PDF bytes are needed for full representation export. It does not authorize artifact capture, parser execution, Docling conversion, production integration, source-truth claims or readiness claims.

## 10. Validation

```text
git diff --check
passed
```
