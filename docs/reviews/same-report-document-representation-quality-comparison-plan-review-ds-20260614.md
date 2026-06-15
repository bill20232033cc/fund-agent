# Same-report Document Representation Quality Comparison Plan Review - DS

Date: 2026-06-14

Verdict: `PASS_WITH_FINDINGS`

## Findings

### DS-F1 - Identity match still allows weak report-level proof

Severity: medium

Evidence: plan section 7 requires `fund_code`, `report_year`, `report_type`, EID `idStr` and PDF repository identity, but `fund_name` / `report_title` are conditional and `report_send_date` is only preferred.

Risk: fund/year/type is insufficient when corrected reports, duplicate announcements, interim variants or title/date mismatches exist. A weak match could compare an EID HTML render against a different PDF artifact.

Recommended fix: tighten `identity_match` to require at least one report-level discriminator per route, such as official title, report id, render URL, send date, content hash or correction/announcement sequence. If unavailable, classify as `identity_partly_matched` or `identity_not_proven`; do not allow a quality winner.

### DS-F2 - Docling boundary needs one explicit ownership sentence

Severity: medium

Evidence: plan section 13 allows bounded Docling local parse on identity-matched sample PDFs if Docling is already installed, while the boundary language relies on Fund documents / `FundDocumentRepository` ownership.

Risk: an evidence worker could interpret this as permission to parse arbitrary local PDF paths after repository resolution, bypassing Fund documents ownership.

Recommended fix: state that Docling may only consume a repository-approved document handle/path produced by the Fund documents boundary for the matched report. No arbitrary local PDF path or untracked PDF may be parsed.

## Nonblocking Residuals

- The plan correctly treats EID as `eid_xbrl_html_render_candidate`, not raw XML/XBRL instance, taxonomy proof, source truth, field correctness proof or readiness proof.
- It preserves `NOT_READY` throughout verdict tokens.
- It keeps pdfplumber and Docling as document-representation candidates, not production parser replacements.
- It does not authorize implementation, dependency install, source policy change, provider/LLM, readiness, release or PR work.
- Sample matrix and stop conditions are sufficient for an evidence worker after identity wording is tightened.
- No contradiction found with the accepted FundDisclosureDocument schema plan or Docling deferred benchmark plan based on the supplied text.

## Final Recommendation

Accept after minor plan revision. Strengthen report-level identity proof before any three-route comparison and clarify the Docling input boundary to prevent parser/path scope drift.
