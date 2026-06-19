# FundDisclosureDocument S6 Field-family Extraction Plan

## 1. Controller Preflight

- Branch: `funddisclosure-s6-field-family-plan`
- Base surface: `origin/main` plus local S5 closeout commit `8d9d977`
- PR #25 disposition: PR #25 has been merged into `origin/main` at merge commit `874511e`; the prior control wording that PR #25 remained draft/open is stale and must be corrected by this gate's controller closeout.
- Current workspace residue: existing untracked research/review/tooling files remain out of scope; this gate does not delete, move, ignore, promote, stage, or classify them.
- Active gate: `FundDisclosureDocument S6 Field-family Extraction Planning Gate`
- Classification adjustment: current control doc labels this as `standard planning gate`, but actual S6 implementation touches processor contract shape, candidate-boundary consumption semantics, and field-family result projection. Implementation must therefore be treated as `heavy` unless the implementation scope is reduced to documentation-only or missing-only behavior.

## 2. Current Code Facts

1. `FundDataExtractor.extract(..., disclosure_intermediate=...)` already has an explicit opt-in route for `active_fund + annual_report + fund_disclosure_document.v1`.
2. The route still loads the annual report through `FundDocumentRepository`, classifies fund type from `ParsedAnnualReport`, and only then dispatches to `FundProcessorRegistry`.
3. `FundDisclosureDocumentProcessor` is registered and reachable, but currently returns six fully-gapped `missing` field families.
4. `FundDisclosureDocumentIntermediate` currently exposes only identity, `source_provenance`, `candidate_boundary`, `failure_class`, `document_kind`, and `intermediate_kind`; it does not expose `sections`, `paragraph_blocks`, `table_blocks`, or `cells`.
5. Concrete `FundDisclosureDocument` stores section/paragraph/table/cell locator structures internally, but the processor must not import or type-check the concrete candidate class.
6. `FundFieldFamilyResult` requires every `accepted` or `partial` field family to carry at least one public `EvidenceAnchor`.
7. Current public `EvidenceAnchor.source_kind` is limited to `annual_report`, `external_api`, and `derived`; it has no candidate-only source kind.
8. `admit_disclosure_intermediate()` currently treats non-`None` `candidate_boundary` as admitted-but-blocked: processor can inspect the object, but result-level `contract_status` becomes `blocked`.
9. `StructuredFundDataBundle` does not preserve `candidate_boundary`; allowing candidate-only processor values to project into the bundle would erase the consumer-visible warning unless a separate contract change is accepted.

## 3. Goal

Implement the first reviewed, deterministic `FundDisclosureDocumentProcessor` field-family extraction slice without changing source truth, parser replacement, readiness, repository behavior, live access, or upper-layer consumers.

The S6 target is not "make FundDisclosureDocument production-ready". The target is to move from "registered but all missing" to "processor can produce bounded candidate-only field-family evidence under an explicit, reviewed contract".

## 4. Non-goals

- No non-active fund processors.
- No default production path consumption of `FundDisclosureDocument`.
- No Service/UI/Host/renderer/quality-gate/LLM prompt direct consumption of candidate JSON, Docling output, EID HTML render, or raw parser artifacts.
- No expansion of `FundDocumentRepository`, source fallback, live EID/PDF/network behavior, cache behavior, or raw XML/XBRL handling.
- No source truth, full field correctness, parser replacement, golden promotion, readiness, release, or PR-ready claim.
- No cleanup of unrelated untracked files.

## 5. Required Design Decision Before Implementation

S6 cannot safely be implemented as "just parse more fields" because two current contracts block that path:

1. The processor contract does not expose the candidate document content.
2. Candidate-only extraction cannot be projected into `StructuredFundDataBundle` without preserving `candidate_boundary`.

Therefore S6 implementation must use this split:

- **S6-A: internal processor content contract.** Add a narrow structural protocol in `fund_agent/fund/processors/contracts.py` for FDD sections, paragraph blocks, table blocks, cells, and document content collections. The protocol must describe only normalized locator/value fields already present on `FundDisclosureDocument`; it must not import `fund_agent.fund.documents.candidates`.
- **S6-B: direct processor extraction.** Implement deterministic candidate-only field-family evidence extraction inside `FundDisclosureDocumentProcessor`. This may return `partial` field families for direct processor callers, but it must preserve candidate-only boundary and must not claim source truth.
- **S6-C: facade projection decision.** Keep `FundDataExtractor` candidate-boundary projection fail-closed in this implementation slice unless a separate reviewed contract explicitly adds consumer-visible candidate boundary to the bundle or otherwise prevents candidate-only values from masquerading as production facts.

## 6. Implementation Slice A: Content Protocol

Allowed files:

- `fund_agent/fund/processors/contracts.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`

Required changes:

1. Add structural protocols for:
   - `FundDisclosureSectionLike`
   - `FundDisclosureParagraphBlockLike`
   - `FundDisclosureCellLike`
   - `FundDisclosureTableBlockLike`
2. Extend `FundDisclosureDocumentIntermediate` with readonly collection attributes:
   - `sections`
   - `paragraph_blocks`
   - `table_blocks`
3. Keep the protocols generic and candidate-internal:
   - no import from `fund_agent.fund.documents.candidates`
   - no import of Docling, PDF, EID helper, cache, network, provider, Service/UI/Host, renderer, or quality gate modules
4. Update test stubs with empty tuple defaults so existing guard tests still represent an admitted no-content intermediate.

Acceptance checks:

- Existing processor tests still pass.
- Static import-boundary test confirms `fund_disclosure_processor.py` does not import concrete candidate modules.
- A new test proves a stub with the new content attributes satisfies `FundDisclosureDocumentIntermediate`.

## 7. Implementation Slice B: Candidate-only Field-family Evidence Extraction

Allowed files:

- `fund_agent/fund/processors/fund_disclosure_processor.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`

Required behavior:

1. Add a module-level configuration table mapping the six field-family IDs to section/table keyword groups and chapter IDs.
2. Implement deterministic selectors over normalized `heading_path`, `heading_text`, table captions, row labels, column headers, and paragraph text.
3. The selector must produce candidate evidence records, not final investment judgments:
   - section/table/block/cell IDs
   - normalized heading path
   - short excerpt or cell text
   - locator stability
   - candidate source path
4. For each field family:
   - if no matching locator exists, return current `missing` family shape with `field_family_missing`
   - if one or more matching locators exist, return `partial`, `extraction_mode="direct"`, and value shaped as `{"candidate_evidence": [...], "candidate_only": True, "source_truth_status": "not_proven", "field_correctness_status": "not_proven"}`
5. Evidence anchors for partial families must not imply field correctness:
   - `source_kind` remains `annual_report` only because the underlying public source is the annual report
   - `row_locator` and `note` must explicitly include candidate locator path and `candidate_only/not_proven`
   - no `EvidenceSourceKind` expansion is allowed in this slice
6. Candidate-boundary result semantics:
   - if `candidate_boundary is not None`, preserve the current result-level blocked consumption semantics unless S6 plan review explicitly accepts a different contract
   - direct processor result may contain partial field families for evidence-harness inspection, but `contract_status="blocked"` means not consumable as production structured facts
7. Non-candidate internal stubs with `candidate_boundary=None` may return `partial`/`missing` result status for contract tests, but this must not be used to claim concrete FDD production readiness.

Acceptance checks:

- A no-content admitted intermediate returns six `missing` families.
- A content-bearing intermediate returns at least one `partial` field family with candidate evidence value and anchor note containing `candidate_only/not_proven`.
- Matching is deterministic and independent of input tuple order where order is not semantically meaningful.
- Unknown/nonmatching sections do not silently populate a field family.
- `candidate_boundary` is preserved on result and does not become readiness proof.
- Result-level gaps remain only cross-field-family gaps; local missing/partial gaps stay on the field family.

## 8. Implementation Slice C: Facade Leak Guard

Allowed files:

- `fund_agent/fund/data_extractor.py`
- `tests/fund/test_data_extractor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`

Required behavior:

1. Keep `FundDataExtractor.extract(..., disclosure_intermediate=concrete_candidate)` fail-closed while `candidate_boundary` is present and consumer-visible bundle boundary is absent.
2. Add or update a test proving candidate-only partial processor output is not projected into `StructuredFundDataBundle`.
3. Document that S6 processor extraction is direct processor/evidence-harness capability only; facade consumption remains blocked for concrete candidate-only FDD until a separate boundary-preserving facade contract is accepted.
4. Sync README/design wording only after code behavior is implemented and verified.

Acceptance checks:

- Existing S5 explicit opt-in route tests still pass.
- New leak-guard test fails if candidate-only field-family values appear in returned bundle without a consumer-visible boundary.
- README/design state:
  - S6 direct processor can extract bounded candidate-only field-family evidence
  - default production facade remains parsed annual report path
  - explicit candidate facade remains fail-closed for concrete candidate-boundary input
  - no source truth/parser replacement/readiness/release

## 9. Required Validation Matrix

Run after implementation:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
uv run ruff check fund_agent/fund/processors/contracts.py fund_agent/fund/processors/fund_disclosure_processor.py fund_agent/fund/data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
git diff --check
```

Optional only if touched behavior escapes these files:

```bash
uv run pytest tests/fund
```

## 10. Review Focus

Plan review must specifically challenge:

1. Whether returning `partial` field families under result-level `blocked` is an acceptable direct-processor evidence-harness shape.
2. Whether the anchor strategy using `source_kind="annual_report"` plus candidate-only note is sufficiently fail-closed, or whether S6 must first add a separate internal candidate locator model instead.
3. Whether any selector keyword group is too heuristic to be accepted without field-correctness evidence.
4. Whether facade projection must remain blocked until `StructuredFundDataBundle` preserves candidate boundary.
5. Whether implementation classification must be escalated from `standard` to `heavy`.

## 11. Stop Condition

This planning gate stops after:

1. plan artifact is written,
2. independent/adversarial plan review is completed,
3. controller judgment accepts, amends, or blocks the plan.

No S6 implementation, PR mutation, push, merge, source truth claim, parser replacement claim, readiness claim, release claim, or unrelated cleanup is authorized by this artifact alone.
