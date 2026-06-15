# Candidate Representation Schema / Design Plan Review - DS

Date: 2026-06-15

Gate: Candidate Representation Schema / Design Plan Review Gate

Verdict: PASS

## Scope

Reviewed target:

- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-design-plan-20260615.md`

Truth and context checked:

- `AGENTS.md`
- `docs/design.md` relevant FundDisclosureDocument / Docling candidate / EID HTML sections
- `docs/reviews/docling-baseline-qualification-full-representation-export-controller-judgment-20260615.md`
- Current candidate internals for schema-context only: `fund_agent/fund/documents/candidates/models.py`, `fund_agent/fund/documents/candidates/locators.py`, `fund_agent/fund/documents/candidates/representation_export.py`

No plan/source/code artifact was modified by this review.

## Findings

| ID | Severity | Path / section | Reason | Fix | Blocking |
|---|---|---|---|---|---|
| DS-PLAN-1 | Info | Plan §§1-3, §6, §10; controller judgment §§2-7 | The plan preserves `NOT_READY`, keeps Docling/pdfplumber/EID HTML outputs as candidate-only structural evidence, and blocks source truth, field correctness, taxonomy, parser replacement, baseline qualification, readiness and release claims. This matches the controller judgment and `docs/design.md` candidate-source constraints. | Accept as written; do not let later implementation wording weaken these guard fields. | No |
| DS-PLAN-2 | Info | Plan §§4-5 | The plan correctly handles all three routes: `docling_pdf_candidate`, `pdfplumber_pdf_candidate`, and `eid_xbrl_html_render_candidate`. It explicitly keeps EID HTML render as a candidate render artifact with `page_number=null` semantics, not raw XML/XBRL truth. It also preserves route-specific locator differences instead of forcing a lossy common shape. | Accept as written; next implementation planning should turn the route-specific expectations into typed payload tests. | No |
| DS-PLAN-3 | Info | Plan §§3, §5.6, §8, §10; `AGENTS.md` document boundary rules; `docs/design.md` FundDisclosureDocument candidate sections | The plan stays candidate-internal: no public `EvidenceAnchor` schema change, no `FundDocumentRepository` behavior change, no production parser/source policy change, and no direct Service/UI/Host/renderer/quality-gate access. Candidate-to-`EvidenceAnchor.note` mapping is explicitly deferred to a separate acceptance gate. | Accept as written; controller should keep public anchor mapping out of the immediate no-live implementation planning gate unless separately scoped. | No |
| DS-PLAN-4 | Low | Plan §§5, §7, §9, §11 | The plan is sufficient for the next no-live implementation planning gate: it names the enum expansion, common envelope fields, section/table/cell candidate fields, internal note fields, candidate guard values, likely files, validation commands and stop conditions. It is not a direct implementation handoff because exact dataclass/TypedDict names and route-specific payload typing are deliberately left to the next planning slice. | Keep next gate as `Candidate Representation Schema No-live Implementation Planning Gate`; do not skip directly to code implementation. | No |

## Residual Risks

- Existing `fund_agent/fund/documents/candidates/models.py` is still Docling-only. The next planning gate must specify exact type changes and tests for `pdfplumber_pdf_candidate` and `eid_xbrl_html_render_candidate`.
- Locator semantics differ by route: Docling has bbox/page-rich PDF locators, pdfplumber may lack bbox, and EID HTML has URL/DOM/table locator semantics with no PDF page number. Future schema tests must prove these differences are preserved.
- Baseline qualification remains conditional on locator stability, field-family pilot evidence and anchor projection acceptance. This plan does not establish Docling baseline qualification.

## Final Recommendation

PASS. Allow entry to `Candidate Representation Schema No-live Implementation Planning Gate`.

Do not proceed directly to production implementation, production parser replacement, public `EvidenceAnchor` schema changes, readiness, release or PR work from this plan.
