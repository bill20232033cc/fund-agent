# P4 Aggregate Re-Review - AgentMiMo

## Scope

- Mode: current changes
- Branch: `main`
- Base: `main` (workspace changes)
- Output file: `docs/reviews/p4-aggregate-rereview-mimo-20260519.md`
- Included scope:
  - `fund_agent/fund/extraction_score.py` — per-fund scoring (`fund_scores`)
  - `fund_agent/fund/quality_gate.py` — per-fund P0/P1 blocking (`FQ2F`)
  - `tests/fund/test_extraction_score.py` — aggregate vs per-fund divergence test
  - `tests/fund/test_quality_gate.py` — single fund P0 block even when field aggregate passes
  - `tests/services/test_extraction_score_service.py` — Service delegation
  - `tests/services/test_quality_gate_service.py` — Service delegation
  - `tests/ui/test_cli.py` — CLI integration
  - `README.md`, `fund_agent/fund/README.md`, `tests/README.md` — doc sync
  - `docs/implementation-control.md`, `docs/implementation-control-p4.md` — control docs
  - Style-positioning field reconciliation sanity: `fund_agent/fund/extractors/profile.py`, `fund_agent/fund/extractors/manager_ownership.py`, `fund_agent/fund/analysis/consistency_check.py`, `fund_agent/fund/template/renderer.py`, `fund_agent/services/fund_analysis_service.py`, `docs/golden-answer-template.md`, and related tests
- Excluded scope:
  - `reports/golden-answers/` — user-edited markdown, not required to be fully regenerated
  - `launchd/`, `scripts/` — local tooling, not production code
- Key artifacts read:
  - `docs/reviews/p4-aggregate-deepreview-controller-judgment-20260519.md`
  - `docs/reviews/p4-design-control-code-reconciliation-20260519.md`
  - `docs/reviews/style-positioning-field-reconciliation-20260519.md`

## Verdict

**PASS**

Blocking finding F1 from the previous aggregate deepreview (score/quality gate lacking per-fund granularity) has been closed. The implementation correctly handles the key scenario: field-level aggregate scores can pass while a single fund's P0 fields fail, and the quality gate now blocks on per-fund P0 failure. Style-positioning field contract reconciliation is clean.

## Findings

未发现实质性问题。

### F1 closure verification

Previous blocking finding F1 required:
- `score.json` to include per-fund quality summary — **done**: `ExtractionScoreResult.fund_scores` with `fund_code / fund_name / app_category / records / p0_status / p1_status / status / p0_failed_fields / p1_failed_fields`
- `quality_gate` to generate issues from per-fund P0/P1 status — **done**: `_evaluate_fund_score()` produces `FQ2F/block` for P0 fail, `FQ2F/warn` for P1 fail, with `fund_code` on each issue
- P0 per-fund fail to trigger block — **done**: `_aggregate_gate_status()` returns `block` if any issue has `SEVERITY_BLOCK`
- Test covering "multi-fund aggregate pass, single fund P0 fail still blocks" — **done**: `test_score_fund_records_exposes_single_fund_p0_failure_when_aggregate_can_pass` and `test_run_quality_gate_blocks_single_fund_p0_failure_even_when_field_aggregate_passes`

### Adversarial pass findings (all non-blocking)

**A1. `_aggregate_status` returns `fail` on empty rows**

- **入口/函数**: `extraction_score.py:796` `_aggregate_status()`
- **文件(行号)**: `extraction_score.py:809`
- **输入场景**: A fund with zero P0 fields in its snapshot records
- **实际分支**: `if not rows: return STATUS_FAIL`
- **预期行为**: A fund with no P0 fields should arguably have `p0_status="pass"` (nothing to fail)
- **实际行为**: Returns `fail`, which means a fund missing an entire priority group is treated as failing that group
- **直接证据**: Line 809-810
- **影响**: Low. In practice, all 14 snapshot fields are generated per fund, so empty P0 rows is not a realistic scenario. If it did occur, the gate would conservatively block — safe direction.
- **建议改法和验证点**: Could document this as intentional conservative behavior. No code change needed for current P4 scope.
- **修复风险（低/中/高）**: Low
- **严重程度（低）**: Low

**A2. `FQ2F` vs `FQ2` rule code naming**

- **入口/函数**: `quality_gate.py:265` `_evaluate_fund_score()`
- **文件(行号)**: `quality_gate.py:267`
- **输入场景**: Fund-level P0 failure
- **实际分支**: Uses `FQ2F` as rule code
- **预期行为**: Controller judgment asked whether FQ2F should be a separate rule code or merged into FQ2 with `fund_code` differentiation
- **实际行为**: FQ2F is a separate rule code, clearly distinguishing fund-level from field-level issues
- **直接证据**: Line 267 `rule_code="FQ2F"`
- **影响**: None. Separate code is clearer for downstream consumers. Both approaches are valid.
- **建议改法和验证点**: Current approach is acceptable. No change needed.
- **修复风险（低/中/高）**: N/A
- **严重程度（低）**: Info

**A3. No per-fund coverage/traceability detail in fund_scores**

- **入口/函数**: `extraction_score.py:533` `_build_fund_score_row()`
- **文件(行号)**: `extraction_score.py:554-555`
- **输入场景**: Fund with P0 fail due to low coverage on a specific field
- **实际分支**: `FundScoreRow` only stores `p0_failed_fields` (field names), not per-field coverage/traceability rates
- **预期行为**: Downstream consumers might want to know *how* bad a field is, not just that it failed
- **实际行为**: Only field names are stored; rates are available in `field_scores` but not cross-referenced in `fund_scores`
- **直接证据**: `FundScoreRow` dataclass at lines 107-131 has no rate fields
- **影响**: Minimal. Field-level rates exist in `field_scores` and can be cross-referenced by `field_name`. Current `fund_scores` is sufficient for blocking decisions.
- **建议改法和验证点**: If per-fund detail is needed, cross-reference `field_scores` by field name. No change needed for current gate logic.
- **修复风险（低/中/高）**: N/A
- **严重程度（低）**: Info

### Style-positioning field reconciliation sanity

The `style_positioning` field migration from `manager_strategy_text` to `product_profile` is clean:

1. `profile.py:43-45` — `style_positioning` patterns defined in `_FIELD_PATTERNS` for §2 extraction
2. `profile.py:359` — `_build_product_profile()` calls `_extract_field(report, "style_positioning")` and includes it in `product_profile.value`
3. `profile.py:381-408` — `_derive_style_positioning()` fallback from `investment_objective` is correctly scoped
4. `manager_ownership.py` — No `style_positioning` in `_FIELD_PATTERNS`; `manager_strategy_text` only outputs `strategy_summary` and `market_outlook`
5. `consistency_check.py` — Investment style dimension reads from `product_profile.style_positioning` first, falls back to `manager_strategy_text.strategy_summary`
6. `renderer.py` — Chapter 3 displays style positioning from `product_profile`
7. `golden-answer-template.md` — Template row updated to `product_profile | style_positioning`

All related tests pass: `test_profile.py` (§2 table reading), `test_manager_ownership.py` (no style_positioning in §4), `test_consistency_check.py` (product_profile-based style check), `test_renderer.py` (template rendering), `test_golden_prefill.py` (golden prefill).

## Open Questions

None. All three re-review questions from the reconciliation doc have been answered:

1. **`fund_scores` sufficiency**: Yes, `p0_status / p1_status / p0_failed_fields / p1_failed_fields` is sufficient for blocking decisions. Field-level rates can be cross-referenced from `field_scores`.
2. **FQ2F vs FQ2**: Separate code is acceptable and clearer. No change needed.
3. **`analyze` integration deferral**: Yes, still deferrable. Current skeleton explicitly does not change the report main chain (P4-S4 control doc §7.3). RR-15 tracks this as a deferred design gap with owner `quality gate integration slice`.

## Residual Risks

| ID | Risk | Status | Owner |
|---|---|---|---|
| P4-AGG-R1 | score/gate lacking per-fund granularity | **closed** | N/A |
| P4-AGG-R2 | quality gate not integrated into `analyze` main chain | deferred, tracked | quality gate integration slice |
| P4-AGG-R3 | FQ1/FQ4/FQ5 not implemented | deferred, tracked | quality gate rules slice |
| P4-AGG-R4 | correctness auto-comparison not implemented | deferred, tracked | correctness slice after reviewed golden JSON |
| P4-AGG-R5 | 004393 known_failure note dead code | cleanup | extractor refinement |
| P4-AGG-R6 | quality_gate / golden_answer boundary tests | partial fix / deferred | test hardening |
| P4-AGG-R7 | `_normalize_extraction_mode` unknown mode silent degradation | cleanup | extraction snapshot cleanup |
| P4-AGG-R8 | `golden_prefill` confidence length heuristic | cleanup | golden prefill cleanup |

## Tests Run

```bash
# P4 aggregate tests (score + quality gate + service + CLI)
.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py tests/ui/test_cli.py -q
# Result: 20 passed

# Style-positioning related tests
.venv/bin/python -m pytest tests/fund/extractors/test_profile.py tests/fund/extractors/test_manager_ownership.py tests/fund/analysis/test_consistency_check.py tests/fund/template/test_renderer.py tests/fund/test_golden_prefill.py tests/services/test_fund_analysis_service.py -q
# Result: 40 passed

# Full test suite
.venv/bin/python -m pytest tests/ -q
# Result: 166 passed

# Lint
.venv/bin/python -m ruff check fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_extraction_score_service.py
# Result: All checks passed!

# Whitespace
git diff --check
# Result: clean
```
