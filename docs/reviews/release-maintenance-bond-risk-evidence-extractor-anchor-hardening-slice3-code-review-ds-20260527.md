# Bond Risk Evidence Extractor / Anchor Hardening — Slice 3 Code Review

> Date: 2026-05-28
> Role: code review worker (AgentDS)
> Gate: Slice 3 code review after implementation
> Branch: `codex/local-reconciliation`
> Review target:
> - `fund_agent/fund/data_extractor.py`
> - `tests/fund/test_data_extractor.py`

## Worker Self-Check

- Self-check: pass
- Role confirmed: code review worker only. No implementation, edit, commit, push, PR, approve, merge, mark ready, or golden promotion.
- Preserved unrelated dirty/untracked files.
- Validation commands executed and results captured below.

## Validation Results

| Command | Result |
|---|---|
| `uv run pytest tests/fund/test_data_extractor.py -q` | 8 passed in 0.55s |
| `uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py` | All checks passed |

## Review Criteria Assessment

### Criterion 1: StructuredFundDataBundle bond_risk_evidence field

**PASS**

`data_extractor.py:148-150` — `StructuredFundDataBundle` declares:

```python
bond_risk_evidence: ExtractedField[BondRiskEvidenceValue] = field(
    default_factory=_default_bond_risk_evidence_field
)
```

- Field is typed `ExtractedField[BondRiskEvidenceValue]`, not `dict` or `Any`.
- No `extra_payload` anywhere in the bundle, extractor call chain, or test assertions.
- Docstring at line 123 references 模板第6章核心风险.
- Default factory (`_default_bond_risk_evidence_field`, line 81-98) produces `extraction_mode="missing"` with note `bond_risk_evidence_not_extracted` for direct construction paths that bypass production extraction.

### Criterion 2: Single annual report load + explicit classified_fund_type

**PASS**

`data_extractor.py:201` — single `self._repository.load_annual_report(...)` call; no second load.

`data_extractor.py:215` — `classified_fund_type = _classified_fund_type(profile_result.basic_identity)` computed once from profile.

`data_extractor.py:216-219` — passed explicitly to extractor:

```python
bond_risk_evidence = extract_bond_risk_evidence(
    report,
    classified_fund_type=classified_fund_type,
)
```

`data_extractor.py:232-234` — same `classified_fund_type` reused for `_tracking_error_for_fund_type(...)`, consistent with implementation doc claim that the variable is reused rather than recomputed per call site.

### Criterion 3: Source provenance and tracking_error behavior preserved

**PASS**

Source provenance projection remains at `data_extractor.py:242`:

```python
source_provenance=project_public_source_provenance(report.metadata.source),
```

Unchanged from prior implementation. All three source provenance tests pass:
- `test_data_extractor_projects_primary_source_metadata` — eid source maps correctly
- `test_data_extractor_projects_fallback_metadata_as_unknown_when_category_absent` — missing failure category stays unknown
- `test_data_extractor_projects_metadata_primary_failure_category` — failure category propagated

`_tracking_error_for_fund_type(...)` unchanged at lines 303-329; receives same `classified_fund_type` via the now-shared variable. Behavior is identical.

### Criterion 4: Non-bond paths remain not-applicable and avoid scanning seven groups

**PASS**

`bond_risk_evidence.py:125-131` — first statement in `extract_bond_risk_evidence` is an explicit non-bond early return:

```python
if classified_fund_type != _BOND_FUND_TYPE:
    return ExtractedField(
        value=None, anchors=(),
        extraction_mode="missing",
        note=_NOT_APPLICABLE_NOTE,  # "not_applicable_non_bond_fund"
    )
```

`test_data_extractor.py:271-315` (`test_data_extractor_non_bond_bond_risk_evidence_does_not_scan_groups`) monkeypatches `_extract_duration_rate_risk` to raise `AssertionError`, proving that non-bond paths (`110011` classified as `active_fund`) never reach any group extractor.

`_classified_fund_type` at `data_extractor.py:276-301` returns `None` for unknown/missing fund types, and `None != "bond_fund"` triggers the not-applicable path — fail-closed per plan requirement.

### Criterion 5: No Service/UI parameter changes, no direct PDF/cache/source helper, no snapshot/score/quality gate/golden changes

**PASS**

- `FundDataExtractor.__init__` signature unchanged (repository, nav_provider only).
- `FundDataExtractor.extract` signature unchanged (fund_code, report_year, force_refresh).
- No new imports of PDF libraries, cache modules, or source helpers.
- `extract_bond_risk_evidence` receives already-loaded `ParsedAnnualReport`, consistent with extractor contract that extractors do not access documents/sources directly.
- Implementation document confirms only Slice 3 files were touched; no snapshot, score, quality gate, or golden files were modified.

### Criterion 6: Tests sufficient for Slice 3, no overfit or hidden production bugs

**PASS**

8 tests, all passing:

| Test | What it verifies |
|---|---|
| `test_data_extractor_degrades_nav_failure_without_blocking_annual_report` | NAV failure doesn't block extraction; bond_risk_evidence missing for non-bond |
| `test_data_extractor_does_not_mask_repository_failure` | Repository exception propagates, not swallowed |
| `test_structured_bundle_default_source_provenance_is_not_none` | Default provenance + default bond_risk_evidence field for direct construction |
| `test_data_extractor_returns_bundle_with_bond_risk_evidence` | Extraction produces bundle carrying bond_risk_evidence with not_applicable note |
| `test_data_extractor_non_bond_bond_risk_evidence_does_not_scan_groups` | Non-bond guard via monkeypatch of group extractor |
| `test_data_extractor_projects_primary_source_metadata` | eid source provenance projection |
| `test_data_extractor_projects_fallback_metadata_as_unknown_when_category_absent` | Fallback without failure category stays unknown |
| `test_data_extractor_projects_metadata_primary_failure_category` | Primary failure category propagated |

No overfit detected — tests use fake repository (`_FakeRepository`) and fixture annual report, not mocks of internal extractor logic. The monkeypatch test correctly verifies the architectural guard (early return in `extract_bond_risk_evidence`) rather than testing implementation details of individual group extractors.

## Findings

### F1 (LOW): Extraction mode naming mismatch between plan and implementation

**Evidence**:
- Plan (Slice 3 Snapshot JSONL section): `extraction_mode = "partial"` when at least one group has usable evidence.
- `models.py:10`: `ExtractionMode = Literal["direct", "derived", "estimated", "missing"]` — no `"partial"` value.
- `bond_risk_evidence.py:1329`: implementation maps `contract_status="partial"` → `extraction_mode="estimated"`.

**Impact**: Any downstream consumer (Slice 4 snapshot, score) that checks `extraction_mode` sees `"estimated"` instead of `"partial"` for partially satisfied bond risk evidence. `"estimated"` conventionally means "derived/calculated", which is semantically different from "partially available."

**Why not blocking**: Score logic in Slice 5 reads `BondRiskEvidenceValue.contract_status` directly, not `ExtractedField.extraction_mode`. Snapshot field note already encodes contract status. The mismatch is a naming convention issue that Slice 4 should reconcile (either add `"partial"` to `ExtractionMode` or update the plan to accept `"estimated"`).

**Recommendation**: Document the decision in Slice 4 planning — either extend `ExtractionMode` to include `"partial"` or accept `"estimated"` as the canonical mode for partial evidence and update plan text accordingly.

### F2 (INFO): `_classified_fund_type` silently returns None for unrecognized fund types

**Evidence**: `data_extractor.py:276-301` — `_classified_fund_type` checks against a hardcoded set of known fund types. If the profile extractor fails to populate `classified_fund_type` key, or a new fund type is introduced without updating this function, `None` is returned.

**Impact**: `None != "bond_fund"` → bond fund silently gets `not_applicable_non_bond_fund` bond_risk_evidence. This is fail-closed (correct per plan) but the absence is silent — no warning, no log, no error.

**Why not blocking**: Explicit plan requirement: "Unknown or absent `classified_fund_type` must not be treated as bond evidence; it should fail closed to missing/not-applicable." This is by design.

## Residual Risks

| # | Risk | Owner | Mitigation |
|---|---|---|---|
| R1 | Bond_fund extraction path not tested in Slice 3 tests — all 8 tests use `110011` (active_fund). | Slice 2 / Slice 6 | Slice 2 extractor tests cover per-group extraction logic; Slice 6 adds real `006597` integration path. |
| R2 | `StructuredFundDataBundle` direct construction produces `bond_risk_evidence.value=None` (via default factory). Downstream consumers that dereference `.value.contract_status` without a None guard will crash. | Slice 4 / Slice 5 | Snapshot projection and score must handle `value is None` before accessing nested fields. |
| R3 | `_classified_fund_type` hardcoded fund type set may drift from profile extractor's actual output type set. | Maintenance | Consider deriving allowed types from a shared constant in `FundType` or models module. |
| R4 | Snapshot, score, and quality gate integration untested at Slice 3 boundary — new field shape not yet exercised in projection/serialization. | Slice 4 / Slice 5 | Future slices will add snapshot projection tests and score applicability tests. |

## Overall Verdict

**PASS** — no blocking findings.

All six review criteria are satisfied with file:line evidence. Tests pass (8/8), lint passes. One low-severity finding (extraction mode naming) and four residual risks documented. The implementation faithfully executes the Slice 3 plan: bundle field added with typed `ExtractedField[BondRiskEvidenceValue]`, single annual report load preserved, explicit `classified_fund_type` passed, non-bond early return verified, no boundary violations, and no Service/UI/snapshot/score/quality-gate changes.
