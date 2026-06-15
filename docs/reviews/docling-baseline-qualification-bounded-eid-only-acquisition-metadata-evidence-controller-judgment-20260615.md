# Docling Baseline Qualification Bounded EID-only Acquisition Metadata Evidence Controller Judgment - 2026-06-15

Gate: `Bounded EID-only Sample Acquisition Metadata Evidence Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the metadata-only EID lookup gate for required Docling baseline qualification sample gaps S4/S5/S6.

This judgment does not authorize PDF download/write/hash, cache writes, `FundDocumentRepository` execution, Docling conversion, pdfplumber export, field correctness comparison, source-truth promotion, production parser replacement, source policy change, provider/LLM/analyze/checklist/golden/readiness/release/PR commands, push or PR.

## 2. Artifacts Reviewed

- Evidence: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-20260615.md`
- DS-role initial review: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-review-ds-20260615.md`
- MiMo-role review: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-review-mimo-20260615.md`
- DS-role targeted re-review: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-rereview-ds-20260615.md`
- Plan: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-plan-20260615.md`
- Plan controller judgment: `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-plan-controller-judgment-20260615.md`
- Current truth docs: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

## 3. Accepted Evidence Facts

| Sample | Controller disposition | Basis |
|---|---|---|
| S4 `006597 / 2024` | ACCEPT as `eid_metadata_matched_no_download` | Official EID `validate_fund.do` returned `isSuccess=true`, `fundId=5755`; `advanced_search_report.do` returned exactly one annual-report row with `fundCode=006597`, `fundId=5755`, `fundShortName=国泰利享中短债债券`, `reportYear=2024`, `reportCode=FB010010`, `reportDesp=年度报告`, `tableName=PDF`, `uploadInfoId=1253099`. |
| S5 `017641 / 2024` | ACCEPT as `eid_metadata_matched_no_download` | Official EID `validate_fund.do` returned `isSuccess=true`, `fundId=12471`; `advanced_search_report.do` returned exactly one annual-report row with `fundCode=017641`, `fundId=12471`, `fundShortName=摩根标普500指数发起式(QDII)`, `reportYear=2024`, `reportCode=FB010010`, `reportDesp=年度报告`, `tableName=PDF`, `uploadInfoId=1256369`. |
| S6 `110020 / 2024` | ACCEPT as `eid_metadata_matched_no_download` | Official EID `validate_fund.do` returned `isSuccess=true`, `fundId=2855`; `advanced_search_report.do` returned exactly one annual-report row with `fundCode=110020`, `fundId=2855`, `fundShortName=易方达沪深300ETF联接`, `reportYear=2024`, `reportCode=FB010010`, `reportDesp=年度报告`, `tableName=PDF`, `uploadInfoId=1249587`. |

Accepted only for metadata identity:

- official EID metadata/search is publicly reachable for S4/S5/S6;
- exact metadata identity can be established without non-EID fallback;
- each required sample has a concrete EID annual-report `uploadInfoId`;
- artifact-capture planning may use these metadata rows as candidate capture inputs.

## 4. Review Disposition

| Finding | Source | Controller disposition | Closure |
|---|---|---|---|
| Initial evidence missed independent `fund_name / fund_short_name`; accepted plan §4.4 would otherwise require `identity_partly_matched`. | DS-role review | ACCEPT_AS_BLOCKING_FINDING | Closed by evidence amendment adding same-endpoint `fundShortName` supplement and DS targeted re-review `PASS`. |
| Metadata gate stayed within `validate_fund.do` and `advanced_search_report.do`; no PDF body/hash/cache write. | DS-role / MiMo-role reviews | ACCEPT | Closed. |
| Evidence does not claim source truth, field correctness, PDF acquisition, Docling baseline proof or readiness. | DS-role / MiMo-role reviews | ACCEPT | Closed. |
| S4 no longer relies on local `_eid` filename; S5/S6 no longer rely on local non-EID PDFs. | MiMo-role review | ACCEPT | Closed. |
| S3 hash gap remains outside this required-target metadata gate. | DS-role / MiMo-role reviews | ACCEPTED_RESIDUAL | Carry forward. |

No unresolved blocking finding remains.

## 5. Rejected Or Deferred Claims

| Claim | Disposition | Reason |
|---|---|---|
| S4/S5/S6 PDFs are downloaded, cached or hash-verified. | REJECT | This gate did not request `instance_show_pdf_id.do`, did not download PDF bytes and did not compute PDF hash. |
| S4/S5/S6 can be used as full Docling/pdfplumber representation inputs now. | REJECT | Local EID-controlled PDF artifacts are still absent for these samples. |
| Metadata match proves field correctness or source truth. | REJECT | Metadata identity is not PDF content, table value, fact provenance or field correctness proof. |
| Metadata match proves Docling baseline qualification. | REJECT | Baseline qualification still requires EID-controlled artifact capture and representation/export/comparison evidence. |
| Non-EID fallback may be used for missing samples. | REJECT | Current source policy is EID single-source/no fallback; CNINFO, fund-company, Eastmoney and akshare are not allowed. |
| S3 hash gap must be resolved in this gate. | DEFER | Prior controller accepted S3 as local EID candidate with hash residual; current gate's required set is S4/S5/S6. |

## 6. Residual Risks

| Residual | Status | Owner | Next handling |
|---|---|---|---|
| PDF bytes/hash/integrity for S4/S5/S6 unproven. | open | Controller / evidence worker | Separate `Bounded EID-only Sample Acquisition Artifact Capture Planning Gate`, then explicit artifact-capture evidence gate if accepted. |
| S3 hash gap. | accepted residual | Controller / export planning owner | Carry to export planning or artifact-capture gate if controller reopens it. |
| Control docs lag behind latest accepted gate chain. | open | Controller | Scoped control sync after accepted checkpoint; do not mix into this evidence gate. |
| Workspace still contains unrelated tracked `AGENTS.md` diff and untracked residue. | accepted residual | Controller / artifact owners | Do not stage unrelated files; handle via separate disposition/sync gates. |

## 7. Next Gate Recommendation

Recommended next gate:

`Bounded EID-only Sample Acquisition Artifact Capture Planning Gate`

Purpose:

- decide exact write set and cache/artifact paths for S4/S5/S6 EID-controlled PDFs;
- define PDF request, integrity check, byte-size/hash recording and cache write rules;
- preserve EID single-source/no fallback;
- keep Docling/pdfplumber conversion out until PDFs are captured and accepted;
- preserve `NOT_READY`.

Do not proceed directly to artifact capture execution, Docling conversion, pdfplumber export, field correctness comparison, production integration or readiness.

## 8. Validation

```text
git diff --check
passed
```

## 9. Final Verdict

`VERDICT: ACCEPT_METADATA_EVIDENCE_READY_FOR_ARTIFACT_CAPTURE_PLANNING_NOT_READY`
