# Code Review: return_attribution.v1 Source-truth Slice 3 Anchor/Gap Hardening

## Review Metadata

- Reviewer: AgentMiMo
- Gate: `FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction Implementation Gate - Slice 3`
- Classification: heavy
- Implementation evidence: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice3-implementation-evidence-20260620.md`
- Plan: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-plan-20260620.md`
- Slice 2 controller: `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice2-code-review-controller-judgment-20260620.md`
- Verdict: `PASS`

## Changed Files

- `fund_agent/fund/processors/fund_disclosure_processor.py` — 1 cleanup (redundant assignment consolidation)
- `tests/fund/processors/test_fund_disclosure_processor.py` — 2 new tests
- `docs/reviews/funddisclosuredocument-return-attribution-source-truth-extraction-slice3-implementation-evidence-20260620.md` — new evidence doc

## Findings

No blocking or non-blocking findings.

### Review Checklist

**1. Table-cell tracking-error reject test covers table path and does not alter accepted value semantics.**

`test_return_attribution_source_truth_rejects_table_cell_tracking_error_target_context` (line 2019) constructs a single table cell with label `"跟踪误差控制目标"` and value `"不超过4.00%"`. This exercises the table-cell path through `_collect_return_attribution_table_value_candidates()` with target/control rejection context. Assertions confirm `status="missing"`, `value={}`, `anchors=()`, and `field_family_missing` gap — no public tracking_error value is emitted. The existing `test_return_attribution_source_truth_tracking_error_actual_disclosure_value` (line 1948, Slice 2) continues to pass unchanged, confirming accepted value semantics are preserved. **Verified.**

**2. NAV/benchmark ambiguity test asserts existing fail-closed gap behavior correctly.**

`test_return_attribution_source_truth_nav_ambiguous_pairs_fail_closed` (line 1890) constructs two same-column NAV/benchmark pairs at row_index 0 and row_index 1. This exercises the ambiguity detection path in `_build_return_attribution_nav_benchmark_value()`. Assertions confirm `status="missing"`, `value={}`, `anchors=()`, gap codes `{"ambiguous_table_or_locator", "field_family_missing"}`, and that `ambiguous_table_or_locator` gap has `source_field_path={"nav_benchmark_performance"}`. This correctly asserts the fail-closed behavior: multiple valid same-row pairs trigger ambiguity rather than arbitrary selection. **Verified.**

**3. Redundant assignment cleanup preserves proof-positive candidate suppression and proof-missing candidate behavior.**

The old code (Slice 2) was:
```python
return_attribution_evidence = _select_return_attribution_candidate_evidence(intermediate)
return_attribution_evidence = (
    () if return_attribution_source_truth is not None else return_attribution_evidence
)
```

The new code consolidates to:
```python
return_attribution_evidence = (
    ()
    if return_attribution_source_truth is not None
    else _select_return_attribution_candidate_evidence(intermediate)
)
```

Semantically identical. When `return_attribution_source_truth is not None` (proof-positive), evidence is `()`. When `None` (proof-missing), the candidate selector runs. The pattern now matches `product_essence_evidence` (lines 773-777). All 20 existing return_attribution tests pass without modification, confirming no behavioral change. **Verified.**

**4. No public value shape/status/schema/source/facade/docs/other-family/parser replacement/readiness changes.**

- No function or class signatures added/removed/changed.
- No `EvidenceSourceKind`, `EvidenceAnchor`, `FundFieldFamilyResult`, `FundProcessorResult` schema changes.
- No status semantics, extraction_mode, source_kind, or source_provenance changes.
- No facade, docs, README, design.md, or other field family changes.
- No parser replacement or readiness claims.
- Only files changed: processor (1 cleanup), tests (2 additions), evidence doc (new).
- **Verified.**

## Validation Reviewed

| Check | Evidence claim | Reproduced |
|-------|---------------|------------|
| `uv run pytest tests/fund/processors/test_fund_disclosure_processor.py` | 135 passed in 0.93s | 135 passed in 0.86s |
| `uv run ruff check` | All checks passed! | All checks passed! |
| `git diff --check` | PASS: no output | PASS: no output |

All validation claims in the evidence document are reproduced and confirmed.

## Residual Risks

- Same-value duplicate disclosures from different stable locators remain accepted with the first locator (carried from Slice 2). Owner: future field-specific evidence/refinement gate if real-report evidence proves unsafe.
- Real-report field correctness remains unproven. Owner: later evidence gate.
- Facade projection regression and docs/design/README sync remain out of scope. Owner: later Slice 4 or docs/facade sync gate.
- `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain missing for FDD source-truth direct extraction. Owner: separate future gates.

## Required Fixes

None.

## Recommendation

Slice 3 is a minimal, correct hardening pass: two focused fail-closed tests and one cosmetic cleanup. No scope creep, no contract changes, no regressions.

**Recommendation token: `CODE_REVIEW_PASS_NOT_READY`**
