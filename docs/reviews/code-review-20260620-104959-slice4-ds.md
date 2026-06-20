# FundDisclosureDocument manager_profile.v1 Slice 4 Code Review

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Slice 4 Code Review Gate`
- Role: AgentDS, review-only
- Review target:
  - `tests/fund/test_data_extractor.py`
  - `docs/design.md`
  - `fund_agent/fund/README.md`
  - `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice4-implementation-evidence-20260620.md`
- Plan: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-20260620.md`
- Controller judgment: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-plan-controller-judgment-20260620.md`
- Latest accepted checkpoint: `6c30386`
- Review artifact: `docs/reviews/code-review-20260620-104959-slice4-ds.md`
- Verdict: **PASS_WITH_FINDINGS**

## Validation Re-executed

```
uv run pytest tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
194 passed in 0.91s
```

```
uv run ruff check tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!
```

```
git diff --check -- tests/fund/test_data_extractor.py tests/fund/processors/test_fund_disclosure_processor.py docs/design.md fund_agent/fund/README.md
<no output — whitespace check passed>
```

```
git diff --stat -- ':(exclude)docs/' ':(exclude)*.md' ':(exclude)tests/'
<no output — zero production code changed>
```

## Review Question Answers

### Q1: Does the positive FDD facade regression prove projection?

**PASS.** `test_explicit_disclosure_source_truth_manager_profile_projects_to_bundle` (line 1226) uses `FundProcessorRegistry.create_default()` with a proof-positive `_manager_profile_source_truth_disclosure_intermediate()` (source_truth_admission present). It asserts all five `manager_profile.v1` public bundle fields:

- `portfolio_managers`: `extraction_mode="direct"`, value matches `portfolio_manager_tenure_list.v1` shape with name/role/start_date/source_anchor, anchors non-empty
- `turnover_rate`: `extraction_mode="direct"`, value has turnover_rate + turnover_basis, anchors non-empty
- `manager_alignment`: `extraction_mode="direct"`, value has manager_holding + employee_holding + `judgment=None`, anchors non-empty
- `manager_strategy_text`: `extraction_mode="direct"`, value has strategy_summary + market_outlook, anchors non-empty
- `holdings_snapshot`: `extraction_mode="direct"`, value has top_holdings (with Chinese column headers), top_holdings_status, top_holdings_source, industry_distribution, industry_distribution_status, anchors non-empty

Also asserts other field families (`investor_return`, `holder_structure`, `share_change`, `bond_risk_evidence`) remain `None`, confirming no cross-family leak.

The fixture content is well-structured: paragraph blocks for strategy/outlook/alignment, table blocks for roster/turnover/holdings/industry. Values match the plan's Section 4 public value shape exactly.

### Q2: Does the negative facade regression prove candidate-only stays missing?

**PASS.** `test_explicit_disclosure_candidate_only_manager_profile_stays_missing` (line 1317) uses the same registry with `_manager_profile_candidate_only_disclosure_intermediate()` (source_truth_admission=None). Same content, no proof. All five bundle fields:

- `value is None` for all five
- `anchors == ()` for all five
- `extraction_mode == "missing"` for all five
- `portfolio_managers.note` is `"field_not_in_family:manager_profile.v1:portfolio_managers"`

This proves the proof-missing path does not consume or surface candidate evidence as field values or anchors. The note format is consistent with the existing FDD missing-path convention used by `test_explicit_disclosure_non_candidate_admitted_produces_missing_bundle`.

### Q3: Do docs accurately state current implemented facts?

**PASS.** `docs/design.md` (v2.29 → v2.30) and `fund_agent/fund/README.md` consistently state:

- `product_essence.v1`, `return_attribution.v1`, AND `manager_profile.v1` have proof-positive FDD source-truth direct extraction ✓
- `manager_profile.v1` projects to `StructuredFundDataBundle` via the explicit FDD facade route ✓
- `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain unimplemented for FDD source-truth ✓
- Candidate evidence remains `candidate_only / not_proven / NOT_READY` ✓
- No real-report correctness, parser replacement, EvidenceSourceKind expansion, Service/UI/Host/renderer/quality-gate consumption, golden/readiness, or release claims ✓

The docs changed from "其它四个" (four remaining) → "其它三个" (three remaining) wherever the remaining field families were listed, correctly reflecting that manager_profile.v1 moved from unimplemented to implemented. No overclaim detected.

### Q4: Did implementation stay inside allowed files?

**PASS.** Only three files were modified:
- `tests/fund/test_data_extractor.py` — test additions only
- `docs/design.md` — design truth sync only
- `fund_agent/fund/README.md` — package docs sync only

Zero production code was changed. No production facade code, processor code, parser replacement, `EvidenceSourceKind`/`EvidenceAnchor` expansion, Service/UI/Host/renderer/quality-gate consumption changes. The `implementation evidence` artifact is untracked and not committed.

## Findings

### F1 LOW: Evidence residual #6 misstated as "fixed"

- **File**: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice4-implementation-evidence-20260620.md`, line 66
- **Finding**: The residual table says "fixed in current slice" for "Candidate evidence remains candidate_only / not_proven / NOT_READY and is not consumed as source truth." This boundary is intentionally preserved, not "fixed" (which implies a prior defect was corrected).
- **Severity**: LOW — documentation wording only, no behavior impact.
- **Recommendation**: Change "fixed in current slice" to "preserved in current slice" or "maintained in current slice."

### F2 LOW: Positive facade regression does not explicitly assert current_stage/core_risk field-family separation

- **File**: `tests/fund/test_data_extractor.py`, `test_explicit_disclosure_source_truth_manager_profile_projects_to_bundle`
- **Finding**: Binding amendment #5 requires "Add or preserve regression that current_stage.v1 and core_risk.v1 remain public missing and do not receive holdings_snapshot from this gate." The test asserts `investor_return`, `holder_structure`, `share_change`, and `bond_risk_evidence` are `None`, but does not test `current_stage.v1` / `core_risk.v1` explicitly. Since these families do not have individual bundle-level fields in `StructuredFundDataBundle`, and the FDD processor tests (`test_fund_disclosure_processor.py`) already cover field-family isolation, this is adequate but worth noting.
- **Severity**: LOW — the risk of `holdings_snapshot` leaking to non-existent bundle fields is negligible, and processor-layer tests provide defense in depth.
- **Recommendation**: No action required; processor-level field-family isolation tests are sufficient.

### F3 INFO: `_DisclosureParagraph` stub lives in facade test, not shared

- **File**: `tests/fund/test_data_extractor.py`, lines 698-707
- **Finding**: The new `_DisclosureParagraph` dataclass is defined locally in the facade test file. If processor tests (`test_fund_disclosure_processor.py`) need a paragraph stub for similar scenarios, duplication may occur. Currently processor tests do not have a comparable stub and rely on different fixture construction; keeping the facade stub independent is valid test isolation.
- **Severity**: INFO — no action needed.

### F4 INFO: Implementation evidence timing variance

- **File**: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice4-implementation-evidence-20260620.md`, line 38
- **Finding**: Evidence records `194 passed in 0.89s`; re-execution produced `194 passed in 0.91s`. This is normal timing variance on the same hardware.
- **Severity**: INFO — no discrepancy.

### F5 INFO: Fixture section_anchor uses same value for all manager_profile cells

- **File**: `tests/fund/test_data_extractor.py`, `_manager_profile_cell()` at line 2041
- **Finding**: `_manager_profile_cell()` hardcodes `section_anchor="section-manager"` for all cells regardless of table context. Turnover and holdings cells also receive `section_anchor="section-manager"` through this helper. This is a test fixture detail that does not affect test correctness because the FDD processor uses `heading_path`, `table_id`, and other fields (not `section_anchor` alone) for content routing.
- **Severity**: INFO — no action needed.

## Scope Boundary Verification

| Boundary | Status |
|---|---|
| No production facade code changed | ✓ PASS |
| No parser replacement | ✓ PASS |
| No EvidenceSourceKind expansion | ✓ PASS |
| No EvidenceAnchor expansion | ✓ PASS |
| No Service/UI/Host/renderer/quality-gate consumption | ✓ PASS |
| No real-report correctness claim | ✓ PASS |
| No readiness/release claim | ✓ PASS |
| No live/PDF/FDR/Docling/provider/LLM evidence required | ✓ PASS |
| No unrelated field families implemented | ✓ PASS |
| Candidate-only/not_proven/NOT_READY preserved | ✓ PASS |
| No staging/commit/push/PR | ✓ PASS |

## Residual Risks (accepted for this gate)

- Real-report manager-profile field correctness remains unproven → future evidence gate
- `holdings_snapshot` is disclosed data only; not current-stage or core-risk interpretation → future field-family gates
- Broader holdings shapes (all-stock, bond, QDII/FOF) remain outside Slice 4 → future refinement
- Manager alignment judgment remains `None` by design → later analysis gate
- `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` FDD source-truth extraction unimplemented → subsequent gates
- Candidate evidence remains candidate_only / not_proven / NOT_READY → preserved, not consumed

## Verdict

**PASS_WITH_FINDINGS** — Slice 4 facade regression, docs sync, and scope boundary verification all pass. No blocking issues. Findings F1 (wording) and F2 (regression breadth) are LOW severity and do not require rework before gate acceptance.
