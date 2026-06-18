# Docling Dedicated Extractor Template-field Mapping Plan - 2026-06-17

Status: `HANDOFF_READY_NOT_READY`
Gate: `Docling Dedicated Extractor Template-field Mapping Planning Gate`
Classification: `heavy`
Role: planning worker
Release/readiness: `NOT_READY`
Verdict: `PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`

## Goal / Motivation / Success Signal

Goal: stop the current Docling baseline-qualification residual-closure route and switch to direct development of a Docling-specialized extractor that maps annual-report candidate representation into analysis-report template target fields.

Motivation:

- The accepted residual-closure evidence checkpoint `edf1c68` proves the current baseline-judgment route is blocked by missing comparable producer diagnostics and cannot interpret `13 / 4` vs `10 / 7`.
- Continuing to optimize residual closure is no longer the shortest route to baseline usefulness.
- The product need is not "prove Docling is a parser baseline"; it is "produce enough template target fields, with anchors and fail-closed gaps, for report generation."

Success signal for the next implementation gate:

- Add a no-live Docling dedicated extractor that consumes already projected `CandidateRepresentationDocument`.
- Output a stable template-field candidate bundle keyed to current `StructuredFundDataBundle` / `SNAPSHOT_FIELD_ORDER` target fields.
- Preserve `ExtractedField`-style value/anchor/mode semantics and candidate-only status.
- Cover an initial field subset that directly serves report-template facts and already appears in accepted Docling artifacts.
- Provide focused unit tests using synthetic `CandidateRepresentationDocument` objects, not live PDF/Docling execution.

## First-principles Judgment

The previous route asked: "Can Docling be promoted or judged as a baseline through residual closure?" That requires source truth, comparable producer diagnostics, and stable baseline criteria. Current evidence says this route cannot close without a new diagnostic replay authorization gate.

The new route asks a different question: "Given a Docling candidate document representation, can we extract template target fields better than the current generic parser path for selected fields?" This is implementable without source-truth promotion because it produces candidate field facts with explicit anchors and fail-closed status.

Therefore the next gate should not continue baseline verdict work. It should build the smallest dedicated extractor surface that makes Docling useful as an extractor input while preserving all proof boundaries.

## Non-goals / Boundary

This plan does not authorize:

- Docling baseline promotion;
- production parser replacement;
- source truth acceptance;
- full field correctness claim;
- direct Service/UI/Host/renderer/quality-gate use of Docling;
- direct PDF/cache/source-helper access;
- live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR commands;
- fresh Docling conversion or repository reload;
- changes to `docs/design.md`, `docs/implementation-control.md`, README, or release/readiness state in the implementation gate.

The next implementation remains no-live and candidate-only:

- `candidate_only=true`;
- `source_truth_status=not_proven`;
- release/readiness remains `NOT_READY`.

## Direct Code Evidence

Current target field surface:

- `fund_agent/fund/data_extractor.py` defines `StructuredFundDataBundle`.
- `fund_agent/fund/extraction_snapshot.py` defines `SNAPSHOT_FIELD_ORDER` and comparable subfields.
- Existing extractors return `ExtractedField[T]` plus `EvidenceAnchor` from `fund_agent/fund/extractors/models.py`.

Current Docling candidate surface:

- `fund_agent/fund/documents/candidates/representation_models.py` defines `CandidateRepresentationDocument`, sections, text blocks, tables, cells, locators, and candidate-only status.
- `fund_agent/fund/documents/candidates/representation_projection.py` projects accepted JSON-like candidate envelopes into `CandidateRepresentationDocument`.
- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` maps candidate locators into candidate anchor fields but intentionally does not produce production `EvidenceAnchor`.

Current architecture constraint:

- `docs/design.md` keeps Docling as Fund documents internal candidate input and requires facts to pass through self-owned extractor / EvidenceAnchor / fail-closed classification before template/report consumption.

## Target Field Scope

Initial implementation should not attempt full template coverage. It should cover a high-value, low-ambiguity field subset mapped to existing report-template needs:

| Field group | Target field | Source section/table family | Output |
|---|---|---|---|
| `profile` | `basic_identity.fund_name` | `§2` profile table or text | `ExtractedField[dict]` candidate subfield |
| `profile` | `basic_identity.fund_code` | `§2` profile table or text | `ExtractedField[dict]` candidate subfield |
| `profile` | `basic_identity.management_company` | `§2` profile table | `ExtractedField[dict]` candidate subfield |
| `profile` | `basic_identity.custodian` | `§2` profile table | `ExtractedField[dict]` candidate subfield |
| `profile` | `product_profile.investment_objective` | `§2` profile/objective text or key-value table | candidate subfield |
| `profile` | `product_profile.investment_scope` | `§2` profile/objective text or key-value table | candidate subfield |
| `profile` | `benchmark.benchmark_text` | `§2` benchmark row/text | candidate subfield |
| `profile` | `risk_characteristic_text.risk_characteristic_text` | `§2` risk characteristic row/text | candidate subfield |
| `profile` | `fee_schedule.management_fee` | `§7` fee subsection/table | candidate subfield |
| `profile` | `fee_schedule.custody_fee` | `§7` fee subsection/table | candidate subfield |
| `manager` | `portfolio_managers` | `§4` manager table | candidate list value |
| `manager` | `turnover_rate` | `§8` turnover table/text when present | candidate subfield |
| `manager` | `manager_alignment` | `§10` manager holding table | candidate subfield |
| `holdings` | `holdings_snapshot` first equity/bond/target-fund holding rows | `§8` holding tables | candidate subfields |
| `performance` | `nav_benchmark_performance` | `§3` performance table | candidate subfields |
| `performance` | `tracking_error` | `§3` actual tracking error disclosure only | candidate value or fail-closed missing |

Fields not covered in the first implementation must be emitted as explicit missing candidate fields, not silently omitted.

Default target field paths are exact dot-notation strings:

```python
DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS = (
    "basic_identity.fund_name",
    "basic_identity.fund_code",
    "basic_identity.management_company",
    "basic_identity.custodian",
    "product_profile.investment_objective",
    "product_profile.investment_scope",
    "benchmark.benchmark_text",
    "risk_characteristic_text.risk_characteristic_text",
    "fee_schedule.management_fee",
    "fee_schedule.custody_fee",
    "nav_benchmark_performance.nav_growth_rate",
    "nav_benchmark_performance.benchmark_return_rate",
    "tracking_error.value_text",
    "portfolio_managers",
    "turnover_rate",
    "manager_alignment.manager_holding_range",
    "holdings_snapshot.top_holdings",
    "holdings_snapshot.bond_top_holdings",
    "holdings_snapshot.target_fund_holdings",
    "manager_strategy_text",
    "holder_structure",
    "share_change",
    "bond_risk_evidence",
)
```

The first implementation may directly extract only the subset listed in the table above. Paths not implemented in the first pass, including `manager_strategy_text`, `holder_structure`, `share_change`, and `bond_risk_evidence`, must still be emitted with `extraction_mode="missing"` and stable missing notes.

## Proposed Implementation Files

Allowed implementation files:

- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`
- `docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md`

Optional only if export is required by tests:

- `fund_agent/fund/documents/candidates/__init__.py`

No implementation change to `FundDataExtractor` in this gate.

Reason: direct production integration would make Docling a parser replacement path before the dedicated extractor has field-level no-live evidence. The safe transition is to build the extractor contract first, then authorize integration in a later gate.

## Contract Design

Create module `template_field_extraction.py` with:

```python
DOCLING_TEMPLATE_FIELD_SCHEMA_VERSION = "docling_template_field_candidates.v1"

@dataclass(frozen=True, slots=True)
class CandidateTemplateField:
    field_group: str
    field_path: str
    value: object | None
    extraction_mode: Literal["direct", "missing"]
    anchors: tuple[CandidateTemplateFieldAnchor, ...]
    note: str | None
    candidate_only: bool
    source_truth_status: Literal["not_proven"]

@dataclass(frozen=True, slots=True)
class CandidateTemplateFieldAnchor:
    source_kind: Literal["annual_report"]
    document_year: int
    section_id: str | None
    page_number: int | None
    table_id: str | None
    row_locator: str | None
    note: str

@dataclass(frozen=True, slots=True)
class DoclingTemplateFieldExtractionResult:
    schema_version: str
    fund_code: str
    document_year: int
    candidate_only: bool
    source_truth_status: Literal["not_proven"]
    fields: tuple[CandidateTemplateField, ...]
    missing_field_paths: tuple[str, ...]
    blocked_field_paths: tuple[str, ...]
    diagnostics: dict[str, object]
```

Public function:

```python
def extract_docling_template_fields(
    document: CandidateRepresentationDocument,
    *,
    target_field_paths: tuple[str, ...] = DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS,
) -> DoclingTemplateFieldExtractionResult:
    ...
```

Invariants:

- Reject non-Docling source kinds unless explicitly supported later.
- Reject any document whose candidate/source truth/parser replacement status is not `not_proven` / `not_authorized`.
- Every target field path must produce exactly one `CandidateTemplateField`.
- Missing values use `extraction_mode="missing"`, `value=None`, `anchors=()`, and a stable note.
- Direct values require at least one anchor.
- No field may claim source truth or readiness.

Relationship to `evidence_anchor_mapping.py`:

- `template_field_extraction.py` consumes `CandidateRepresentationDocument` directly.
- It does not consume `CandidateEvidenceAnchorMappingResult`.
- It may reuse the same section/table/cell locator concepts, but it must not duplicate production `EvidenceAnchor` creation or return production `EvidenceAnchor`.
- `CandidateTemplateFieldAnchor` is a candidate-only anchor shape. Its `source_kind="annual_report"` mirrors annual-report semantics only; consumers must use the parent `candidate_only=true` and `source_truth_status="not_proven"` fields to prevent production-anchor promotion.
- A later integration gate may define a reviewed projection from accepted candidate template fields to production `ExtractedField` / `EvidenceAnchor`; that projection is not authorized here.

## Matching Rules

Use deterministic field rules, not LLM and not fuzzy whole-document search.

Rule families:

- key-value table rule: match row labels and adjacent value cells in `CandidateTableBlock.cells`;
- text label rule: match label prefixes in `CandidateTextBlock.normalized_text`;
- table-family guarded rule: require section/table context for fee, manager holding, holdings, performance, and tracking-error fields;
- fail-closed tracking-error rule: accept only actual disclosed tracking error, not target/limit/manager narrative;
- fail-closed hierarchy rule: holdings aggregate/child fields require row/column context; value equality alone is insufficient.

Normalization:

- trim whitespace;
- compact repeated spaces/newlines;
- preserve Chinese punctuation where it carries meaning;
- for percentages and money values, keep original text in this gate; numeric normalization can be a later slice.

## Implementation Slices

### Slice 1 - Contract and field registry

Allowed changes:

- add dataclasses and `DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS`;
- add validation helpers for candidate-only invariants;
- add missing-field construction.

Tests:

- invalid source/proof statuses fail closed;
- every target field path emits exactly one field;
- missing fields are explicit and not omitted.

### Slice 2 - Profile and fee fields

Allowed changes:

- implement deterministic key-value and label matching for profile fields, benchmark, risk text, management fee, custody fee;
- construct candidate anchors from table/text locators.

Tests:

- synthetic `§2` profile table extracts identity/objective/scope/benchmark/risk;
- synthetic `§7` fee table extracts management/custody fee;
- ambiguous or wrong-section fee rows remain missing.

### Slice 3 - Performance, manager, holdings skeleton

Allowed changes:

- implement initial no-live mappings for performance table, actual tracking error, manager table, manager holding alignment, and first holdings rows;
- fail closed for ambiguous hierarchy and target/limit tracking-error text.

Tests:

- `§3` performance table extracts nav and benchmark return;
- tracking-error target text is rejected;
- manager and holdings rows require section/table context;
- S6-F041/S6-F049/S6-F050 style fail-closed constraints are preserved.

## Validation Commands

Required implementation validation:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py -q
```

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

```text
git diff --check -- fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py docs/reviews/docling-dedicated-extractor-template-field-mapping-implementation-evidence-20260617.md
```

## Docs Decision

No README/design/control update in the implementation gate.

Reason: the implementation remains candidate-only and internal to Fund documents candidate extraction. It does not yet change user-facing CLI, production `FundDataExtractor`, parser policy, report renderer, or release/readiness state.

Design/control sync should occur only after a later integration/evidence gate accepts the extractor as part of a production or opt-in report-generation path.

## Residual Risks

- This does not prove source truth or field correctness against real annual reports.
- This does not decide Docling baseline qualification.
- This does not integrate into `FundDataExtractor` or report generation.
- Numeric normalization and unit conversion are intentionally deferred unless required by the initial tests.
- Multi-year, QDII, FOF, and full CHAPTER_CONTRACT coverage remain future scope.

## Next Gate

Recommended next gate:

`Docling Dedicated Extractor Template-field Mapping No-live Implementation Gate`

Implementation worker stop condition:

- stop after writing the allowed implementation files and implementation evidence;
- do not run live/source acquisition;
- do not update design/control/readiness/release;
- do not claim baseline/source truth/parser replacement/full correctness.

VERDICT: `PLAN_READY_FOR_NO_LIVE_IMPLEMENTATION_NOT_READY`
