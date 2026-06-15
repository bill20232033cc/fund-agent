# Same-report Document Representation Quality Comparison Plan Review - MiMo

Date: 2026-06-14

Verdict: `PASS_WITH_FINDINGS`

## Findings

| Severity | ID | Evidence | Risk | Recommended fix |
|---|---|---|---|---|
| medium | MIMO-F1 | Section 7 requires `fund_code`, `report_year`, `report_type`, EID `idStr` and PDF repository identity, with title/name optional and `report_send_date` supporting only. | Identity gate may still allow comparing EID HTML for one announcement instance against repository PDF for a corrected or alternate annual report with the same fund/year/type. | Require repository/EID source metadata where available: EID URL or identifier, report code/name, upload/detail id, correction number or content hash. If unavailable, route to `identity_partly_matched` and forbid a winner decision. |
| medium | MIMO-F2 | Section 13 says future evidence may run bounded Docling local parse if installed and current pdfplumber through Fund documents; section 4 says do not run parsers. | Controller may read this as contradictory: parser execution forbidden now versus parser execution allowed later. | Split wording: this planning gate runs no parsers; the later explicitly authorized evidence gate may run bounded parser comparison commands under Fund documents / FDR boundary. |
| low | MIMO-F3 | Section 12 includes route-strength verdicts and `IDENTITY_MATCHING_BLOCKED_NOT_READY`, but no explicit mixed/partial identity verdict. | If some samples are exact and some are partial, controller lacks a precise mixed-result verdict. | Add `PARTIAL_IDENTITY_ONLY_NO_WINNER_NOT_READY` or require per-sample verdict plus aggregate verdict rules. |
| low | MIMO-F4 | Section 10 includes `cell_text` and section 12 requires comparisons, while the plan only generally says not to call values correct. | Reviewers/controllers may treat richer rendered text coverage as semantic correctness. | Require comparison tables to include a `not_field_correctness` marker or footer and labels such as `rendered_text_observed`, not `value_correct`. |

## Residuals

- Plan appropriately forbids code changes, dependency install, production parser replacement, provider/LLM/readiness/release/PR, raw XML, field correctness, taxonomy and source-truth claims.
- EID HTML is kept as `eid_xbrl_html_render_candidate`, not raw XML/XBRL instance.
- Docling/pdfplumber are kept inside Fund documents / `FundDocumentRepository` boundary, but the future evidence gate must restate exact commands and stop rules before execution.
- Same-report comparison cannot resolve ordinary non-REIT coverage unless Tier A identity match is actually available.
- Quality comparison remains document-representation evidence only; implementation planning must still decide schema/module ownership separately.

## Final Recommendation

Accept with amendments. Before controller acceptance, tighten identity matching around repository/EID source metadata and clarify parser-execution wording between the current planning gate and future explicitly authorized evidence gate. Keep release/readiness `NOT_READY`; next step remains plan review closeout, then a bounded evidence gate only if separately authorized.
