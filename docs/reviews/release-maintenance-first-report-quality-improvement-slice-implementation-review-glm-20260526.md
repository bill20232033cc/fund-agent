# Gate D First Report-Quality Improvement Slice Implementation Review (AgentGLM) - 2026-05-26

## Scope

This review covers the uncommitted diff on branch `codex/local-reconciliation` for the `active_fund` Chapter 3 turnover/style-consistency data-gap wording contract implementation.

Accepted plan: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-20260526.md`

Controller judgment: `docs/reviews/release-maintenance-first-report-quality-improvement-slice-plan-controller-judgment-20260526.md`

No source, tests, README, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixture, report output, commit, push, PR, or destructive git work was performed in this review gate. All commands were read-only.

## Verdict

**PASS_WITH_FINDINGS**

All findings are informational or minor. No material correctness or boundary violations detected. Implementation is safe to proceed to commit after findings are acknowledged.

## Findings

### F1 (Informational) — Safe option correctly chosen and explicitly verified

**File:** `tests/fund/audit/test_audit_programmatic.py:901-938`

The plan originally called for adding a `ContractRequiredItemRule` for `换手率/风格变化证据缺口说明与下一步最小验证问题` and expanding `required_item_texts` tuples to include it. The controller judgment authorized the safe option: defer any runtime `ContractRequiredItemRule` that current renderer cannot satisfy.

The implementation correctly:

- Did NOT add the new `ContractRequiredItemRule`.
- Did NOT add `换手率/风格变化证据缺口说明与下一步最小验证问题` to `required_output_items` in `contracts.py`.
- Kept `required_item_texts` as single-element tuples: `("言行一致性判断",)` and `("风格稳定性判断",)`.
- Added test `test_active_fund_chapter_3_gap_contract_does_not_add_unconditional_required_item()` that explicitly asserts no such rule exists and verifies the safe option is in place.

This satisfies the mandatory Gate D preflight from the controller judgment.

### F2 (Informational) — Wording strings consistent across all three layers

**Files:** `docs/fund-analysis-template-draft.md`, `fund_agent/fund/template/contracts.py`, `fund_agent/fund/audit/contract_rules.py`

Grep verification confirms exact string match across all three layers for:

- `must_answer` entry 1: `言行一致性判断：说的和做的一样吗？主动基金如缺少已复核的换手率或风格变化证据，不得据此判断言行一致。`
- `must_answer` entry 2: `风格稳定性判断：跨期风格是否漂移？主动基金必须基于已复核的换手率或风格变化证据。`
- `must_not_cover` entry: `不在换手率或风格变化证据缺失、不可用、未复核时，推断主动基金风格稳定、风格一致或言行一致。`

Update order was followed: template draft → contracts.py → contract_rules.py.

### F3 (Informational) — `docs/design.md` not updated; rationale correct

**Decision:** No update needed.

The implementation only clarifies evidence-precondition wording on existing `must_answer` entries and adds one `must_not_cover` entry. It does not change chapter structure, IDs, titles, lens keys, fund types, or any design-level architecture. Per the plan's step 6, a narrow wording clarification that restates existing §5.4.3 missing-fact downgrade semantics does not require a design-doc structural update.

### F4 (Minor / Accepted Architecture) — Template-draft ↔ contracts.py drift is process-dependent

There is no automated test that cross-references `docs/fund-analysis-template-draft.md` strings against `fund_agent/fund/template/contracts.py` strings. Drift between human truth (template draft) and machine truth (contracts.py) is caught only by manual review process.

This is a pre-existing architectural decision, not introduced by this slice. The three-layer grep consistency check performed in this review confirms current alignment. A future gate could consider adding a template-draft parser test, but this is out of scope for the current slice.

### F5 (Informational) — Data-gap wording test strengthened correctly

**File:** `tests/fund/test_report_evidence.py:274-293`

The `required_report_wording` was extended from the short anchor phrase to the full sentence:

```text
当前 slice 未复核换手率，不能据此判断风格稳定、风格一致或言行一致；下一步最小验证问题：复核年报§8换手率及跨期行业配置/持仓集中度变化后，风格稳定性和言行一致性判断是否仍成立？
```

The test now asserts three substrings: (1) the insufficiency prohibition, (2) the style-consistency prohibition, and (3) the next minimum validation question. This matches the plan exactly and does not change projection behavior.

## Review Focus Area Answers

### 1. Does safe option really avoid default analyze/runtime audit behavior changes?

Yes. No new `ContractRequiredItemRule` was added. The `must_answer` coverage routes remain `covered_by_required_item` with single existing required items. The new `must_not_cover` entry uses `narrative_guidance` (non-programmatic, not enforced by C2). The explicit test at `test_audit_programmatic.py:901` verifies no unconditional required item was introduced. Default `fund-analysis analyze` behavior is unchanged.

### 2. Does wording contract remain testable without renderer changes?

Yes. All four test functions operate on contract/audit/evidence layers:

- `test_contracts.py:test_active_fund_chapter_3_contract_requires_reviewed_turnover_or_style_change_before_stability_claim` — verifies wording in manifest and safe-option invariants.
- `test_audit_programmatic.py:test_active_fund_chapter_3_gap_contract_does_not_add_unconditional_required_item` — verifies coverage routes and safe option.
- `test_audit_programmatic.py:test_contract_audit_coverage_manifest_covers_every_must_not_cover` — verifies coverage count updated to 25 and new rule present.
- `test_report_evidence.py:test_extraction_mode_missing_produces_data_gap_ref` — verifies data-gap wording preservation.

No renderer import or call exists in any changed test.

### 3. Are tests sufficient to catch drift between template draft, contracts.py, and audit rules?

Tests verify machine-truth consistency (contracts.py ↔ contract_rules.py) thoroughly. Template-draft ↔ contracts.py drift is process-dependent (see F4). The implementation adds no new drift risk beyond the pre-existing architecture.

### 4. Any issue with not updating docs/design.md?

No issue (see F3).

### 5. Boundary: no renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu/repository/source/fixture/report output changes?

Clean. Seven files changed, all within allowed scope:

- `docs/fund-analysis-template-draft.md` — template truth
- `fund_agent/fund/README.md` — minimal docs sync
- `fund_agent/fund/audit/contract_rules.py` — audit coverage routes
- `fund_agent/fund/template/contracts.py` — machine truth
- `tests/fund/audit/test_audit_programmatic.py` — audit tests
- `tests/fund/template/test_contracts.py` — contract tests
- `tests/fund/test_report_evidence.py` — evidence tests

Boundary verification:

- `git diff --name-only HEAD`: only the 7 allowed files.
- `git diff HEAD -- fund_agent/fund/template/renderer.py fund_agent/services ...`: empty.
- `rg` for out-of-scope references in changed files: only existing assertions that symbols are NOT present.
- `ruff check`: all checks passed.
- `git diff --check`: no whitespace issues.

## Open Questions

None material.

## Residual Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Renderer does not yet emit the new wording contract. | Accepted residual | Future renderer/report-writing gate will add `ContractRequiredItemRule` when product output is ready. Current contract is declaration-level only. |
| `narrative_guidance` coverage is non-programmatic; C2 does not enforce the new `must_not_cover` at runtime. | Accepted residual | By design per controller judgment. Future renderer gate must add programmatic enforcement. |
| Template-draft ↔ contracts.py drift risk is process-dependent. | Pre-existing | Not introduced by this slice. Future gate could add automated cross-reference test. |
| `ReportDataGapOverride.required_report_wording` carries the full sentence but projection behavior is unchanged. | Low | Test verifies wording is preserved through projection. No schema change required. |

## Acceptance Commands Run

```text
uv run pytest tests/fund/template/test_contracts.py tests/fund/audit/test_audit_programmatic.py tests/fund/test_report_evidence.py
  → 83 passed in 0.74s

uv run pytest tests/fund/template tests/fund/audit tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
  → 190 passed in 0.72s

uv run ruff check fund_agent/fund/template/contracts.py fund_agent/fund/audit/contract_rules.py tests/fund/template/test_contracts.py tests/fund/audit/test_audit_programmatic.py tests/fund/test_report_evidence.py
  → All checks passed!

git diff --check HEAD
  → (no output, clean)

git diff --name-only HEAD
  → 7 allowed files only

git diff HEAD -- fund_agent/fund/template/renderer.py fund_agent/services fund_agent/ui fund_agent/fund/quality_gate.py fund_agent/fund/extraction_score.py fund_agent/fund/documents
  → (empty, no out-of-scope changes)
```

## Controller Recommendation

Proceed to commit. All findings are informational or minor pre-existing architecture notes. The safe option is correctly implemented and explicitly verified by dedicated tests. No boundary violations detected. The implementation is a minimal, well-scoped wording contract hardening that preserves deterministic MVP behavior.
