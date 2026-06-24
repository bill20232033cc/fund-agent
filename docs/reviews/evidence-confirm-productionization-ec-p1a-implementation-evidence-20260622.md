# Evidence Confirm Productionization EC-P1A Implementation Evidence

## Gate

- Work unit: `Evidence Confirm Productionization Program`
- Gate: `EC-P1A ParsedAnnualReport Locator-contract No-live Materializer Implementation Gate`
- Branch: `evidence-confirm-productionization`
- Accepted plan commit: `5954bba`
- Role: implementation worker only
- Completion status: `IMPLEMENTATION_COMPLETE_NOT_READY`

## Exact Scope

Implemented only the accepted no-live Fund-layer materializer over already-loaded `ParsedAnnualReport` fields.

In scope:

- Added `fund_agent/fund/evidence_confirm_sources.py`.
- Added `EvidenceConfirmReferenceBuildRequest`, `EvidenceConfirmReferenceBuildResult`, and `EvidenceConfirmReferenceBuildIssue`.
- Added `build_annual_report_evidence_confirm_references(request)`.
- Added constants:
  - `SUPPORTED_TABLE_ID_RE = r"^page-(?P<page_number>[1-9][0-9]*)-table-(?P<table_index>0|[1-9][0-9]*)$"`
  - `SUPPORTED_ROW_LOCATOR_RE = r"^row-(?P<row_index>0|[1-9][0-9]*)$"`
  - `DEFAULT_MAX_SECTION_EXCERPT_CHARS = 1200`
- Materialized only `annual_report` anchors into existing `annual_report_excerpt / annual_report` references.
- Enforced fail-closed behavior for wrong year, missing section, unsupported table id, page mismatch, missing/duplicate table, unsupported row locator, out-of-range row, empty section excerpt, and missing/negative source-truth admission.
- Added no-live tests for locator behavior, source-truth admission, V2 piping, and import isolation.
- Updated Fund/test README entries for the new no-live materializer and test surface.

Out of scope / not changed:

- No `FundDocumentRepository` instantiation.
- No live/network/PDF/provider/LLM command.
- No Service/UI/Host/renderer/quality-gate behavior change.
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion.
- No source fallback behavior change.
- No V1/V2 Evidence Confirm behavior change.
- No PR mutation, push, commit, mark-ready, merge, release or readiness transition.

## Changed Files

- `fund_agent/fund/evidence_confirm_sources.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/evidence-confirm-productionization-ec-p1a-implementation-evidence-20260622.md`

`fund_agent/fund/evidence_confirm.py` and `tests/fund/test_evidence_confirm.py` were not modified.

Unrelated pre-existing untracked residue was ignored:

- `docs/code-wiki.md`
- `docs/codewiki.md`
- `docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md`
- `docs/liu-chenggang-dayu-ai-coding-roadmap-20260614.md`
- `docs/next-development-phaseflow.md`
- `docs/tmux-agent-memory-store.md`
- `scripts/claude_mimo_simple.py`
- `scripts/review-artifact.sh`

## Validation

Command:

```bash
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q
```

Output:

```text
.................................................................        [100%]
65 passed in 1.15s
```

Command:

```bash
uv run ruff check fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py
```

Output:

```text
All checks passed!
```

Command:

```bash
git diff --check -- fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py fund_agent/fund/README.md tests/README.md docs/reviews/evidence-confirm-productionization-ec-p1a-implementation-evidence-20260622.md
```

Output:

```text
<no output>
```

## Residual Risks

| Residual | Classification | Owner / Destination |
|---|---|---|
| Compatibility `page-{page_number}-table-{table_index}` may not cover live annual-report structures. | covered by later approved slice | EC-P2 repository-bounded live source/PDF evidence gate |
| Current extractor anchors may use richer row locators than zero-based `row-N`. | covered by later approved slice | EC-P2 / later documents-model locator gate |
| Section excerpt bound can truncate long qualitative support. | covered by later approved slice | EC-P2 live evidence and later semantic/materializer gates |
| Source-truth admission is limited to current EID single-source metadata fields available on `ParsedAnnualReport`. | covered by later approved slice | EC-P2 repository-bounded source/PDF evidence gate |
| Semantic entailment, Service/UI/renderer/quality-gate integration, production default, and release/readiness remain unimplemented. | assigned to later work unit | EC-P4 through EC-P11 |

## Completion

EC-P1A implementation and tests are complete locally. Release/readiness remains `NOT_READY`.
