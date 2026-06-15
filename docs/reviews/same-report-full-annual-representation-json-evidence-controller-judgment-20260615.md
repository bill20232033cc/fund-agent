# Same-report Full Annual-report Representation JSON Evidence Controller Judgment

Date: 2026-06-15

Gate: `Same-report Full Annual-report Representation JSON Evidence Gate`

Role: controller

Verdict: `ACCEPT_PARTIAL_JSON_COMPARISON_READY_FOR_BOUNDED_EID_HTML_DISCOVERY_GATE_NOT_READY`

Readiness state: `NOT_READY`

## 1. Scope

This judgment closes the evidence gate requested after the controller correction that a complete route test requires full annual-report representation JSON, not partial descriptive evidence.

Accepted evidence artifact:

- `docs/reviews/same-report-full-annual-representation-json-evidence-20260615.md`

Accepted representation JSON artifacts:

- `reports/representation-json/004393_2025_docling_full.json`
- `reports/representation-json/004393_2025_pdfplumber_full.json`
- `reports/representation-json/004393_2025_eid_html_render_full.json`

Reviews:

- DS: `docs/reviews/same-report-full-annual-representation-json-evidence-review-ds-20260615.md`
- MiMo: `docs/reviews/same-report-full-annual-representation-json-evidence-review-mimo-20260615.md`

This judgment does not authorize production parser replacement, `FundDocumentRepository` behavior change, source policy change, field correctness claim, source truth claim, taxonomy compatibility claim, readiness/release/PR state change, stage, commit, push or merge.

## 2. Accepted Current Facts

| Route | Accepted status | Controller disposition |
|---|---|---|
| Docling | Full local same-report representation JSON exists for `004393 / 2025`; 65 pages, 213 headings, 95 tables, 3493 cells. | Accepted as candidate representation evidence only. |
| pdfplumber | Full local same-report baseline JSON exists for `004393 / 2025`; 65 pages, 8 located sections, 92 tables, 3640 cells. | Accepted as local no-live baseline evidence only. It is not a production `FundDisclosureDocument` schema. |
| EID HTML render | Same-report full JSON is blocked because no local accepted `004393 / 2025` HTML render artifact exists and live/network discovery was not authorized. | Accepted as correct blocked JSON; no URL was fabricated. |

The final route state is `PARTIAL_JSON_COMPARISON_ONLY_NOT_READY`, not tri-route comparable evidence.

## 3. Review Disposition

| Source | Finding | Disposition | Rationale |
|---|---|---|---|
| DS F1 | Docling `section_count=13` while actual `sections` array has 25 entries; metric definition is ambiguous. | ACCEPT_AS_NONBLOCKING_RESIDUAL | This does not invalidate the full JSON artifact. The next schema/planning gate must define section-count semantics: chapter-level sections versus all section/grouping nodes. |
| DS F2-F8 | Hash/provenance, local source, EID block, boundary, byte-size, failure taxonomy and next-gate observations. | ACCEPT | These findings support acceptance and do not require evidence rewrite. |
| MiMo F1 | Docling metrics table omits `has_content_hash`. | ACCEPT_AS_NONBLOCKING_RESIDUAL | The JSON contains the field; evidence table omission does not affect verdict. Future evidence should list all `summary_metrics` keys. |
| MiMo F2 | pdfplumber metrics table omits `has_content_hash` and `has_url_or_source_locator`. | ACCEPT_AS_NONBLOCKING_RESIDUAL | The JSON contains the fields; evidence table omission does not affect verdict. Future evidence should list all `summary_metrics` keys. |

No blocking findings remain.

## 4. Blocked Claims

The following claims remain blocked:

- full tri-route comparable JSON evidence;
- same-report `004393 / 2025` EID HTML render availability;
- raw XML direct download;
- field correctness;
- taxonomy compatibility;
- source truth;
- production `FundDisclosureDocument` schema;
- parser replacement;
- readiness/release/PR readiness.

## 5. Accepted Residuals

| Residual | Owner | Next handling |
|---|---|---|
| EID HTML same-report full JSON missing. | Fund documents/source research owner | Requires bounded same-report EID HTML render discovery gate with explicit live/network authorization. |
| Docling section metric ambiguity. | Fund documents/schema owner | Define chapter-level versus all-node section semantics in candidate schema/planning gate. |
| Evidence table omitted some `summary_metrics` fields. | Evidence owner | Carry as reporting residual; no artifact rewrite required. |
| pdfplumber full JSON is an evidence export, not a repeatable contract. | Fund documents/parser owner | Future planning should decide whether a bounded repository-internal export contract is needed. |
| Docling/pdfplumber JSON are not source truth. | Fund documents/extractor owner | Future projection/extractor gates must validate facts before CHAPTER_CONTRACT consumption. |

## 6. Controller Decision

The evidence gate is accepted with nonblocking residuals.

The corrected testing principle is accepted:

> Complete route comparison requires same-report full annual-report representation JSON artifacts, or explicit blocked JSON artifacts with exact blocker reasons.

Current evidence produced two full local JSON artifacts and one correct blocked JSON artifact. Therefore the correct next primary gate is not hybrid implementation planning. The missing third route must be addressed first if tri-route comparison remains the goal.

Primary next gate:

`Bounded Same-report EID HTML Render Discovery Gate`

This next gate requires explicit live/network authorization. Without that authorization, the controller should stop at the current accepted partial JSON evidence and keep `Hybrid FundDisclosureDocument Candidate Source Planning Gate` deferred.

## 7. Deferred Entries

- Pdfplumber Full Representation Export Contract Planning Gate.
- Hybrid FundDisclosureDocument Candidate Source Planning Gate.
- FundDisclosureDocument Candidate Schema Planning Gate.
- Docling section/paragraph semantics planning gate.
- Docling model artifact provenance acceptance gate.
- Field correctness validation gate.
- Taxonomy compatibility gate.
- Raw XML endpoint proof gate only if a public endpoint is discovered.
- Readiness/release/PR gates.

## 8. Validation

Required validation:

- `git diff --check`

Controller result after writing this judgment and scoped control sync: pending.

## 9. Final Verdict

`VERDICT: ACCEPT_PARTIAL_JSON_COMPARISON_READY_FOR_BOUNDED_EID_HTML_DISCOVERY_GATE_NOT_READY`

