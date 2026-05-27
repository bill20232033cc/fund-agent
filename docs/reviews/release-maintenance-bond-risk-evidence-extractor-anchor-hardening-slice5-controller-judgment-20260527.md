# Bond Risk Evidence Extractor / Anchor Hardening Slice 5 Controller Judgment

> Date: 2026-05-27
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Controller role: Gateflow controller
> Gate: Slice 5 score applicability and P1 registration
> Decision: accepted for local Slice 5 checkpoint

## Self-Check

- Current role: controller only; implementation, code review, fix, and re-review were delegated.
- Branch: `codex/local-reconciliation`.
- Scope: score applicability and P1 registration only. No quality gate edit, snapshot edit, data extractor edit, golden promotion, Service/UI change, PR, push, merge, approve, or mark-ready work.
- Source of truth: accepted plan Slice 5, Slice 4 controller judgment, Slice 5 implementation artifact, MiMo/DS reviews, fix artifact, and DS re-review.
- Stop conditions: none remain. The accepted value-present finding was fixed and re-reviewed.

## Accepted Implementation

Slice 5 completes the score-side semantics for `bond_risk_evidence.v1`.

Accepted behavior:

- `bond_risk_evidence` is registered in `FIELD_PRIORITY_BY_NAME` as `P1`.
- Exact `bond_fund` holdings replacement now checks the same-fund same-year `bond_risk_evidence` snapshot row.
- Complete positive evidence with:
  - `bond_risk_contract_status="satisfied"`
  - all seven groups in `bond_risk_satisfied_groups`
  - `value_present=True`
  - `anchor_present=True`
  emits no `bond_risk_evidence_missing` issue.
- Missing, absent, malformed, missing-status, `contract_status="missing"`, `value_present=False`, `anchor_present=False`, duplicate, weak, ambiguous, or partial rows remain fail-closed.
- `required_evidence_groups` remains the full ordered seven-group contract for every emitted issue.
- `missing_evidence_groups` is dynamic for partial rows and lists only unsatisfied groups when the structured row is well formed.
- Score consumes Slice 4 structured fields only and does not parse free-form `note`.
- Non-bond funds ignore `bond_risk_evidence`; unknown/conflicting fund types remain fail-closed and do not infer type from the bond-risk row.

## Review Finding Disposition

MiMo review: PASS, no blocking findings.

DS review: PASS with residuals. Controller accepted one finding for current-slice fix:

- `value_present=False` inconsistent row could otherwise be treated as satisfied when structured fields claimed `satisfied`.

Fix accepted and completed:

- `_bond_risk_unsatisfied_groups` now checks `value_present` before trusting `anchor_present`, contract status, or structured group fields.
- Added a regression test proving `value_present=False`, `anchor_present=True`, `contract_status="satisfied"`, and all seven satisfied groups still emits `bond_risk_evidence_missing` with all seven missing groups and `baseline_blocking=True`.

DS re-review: PASS.

Deferred residuals:

- Per-group anchor validation remains outside Slice 5 because snapshot exposes field-level anchor presence, not per-group anchor booleans. Owner: Slice 6 real validation and possible future snapshot contract hardening.
- Multiple same-fund same-year `bond_risk_evidence` rows fail closed as all-seven missing. Accepted conservative behavior.
- Logic duplication between field applicability decisions and score applicability issues remains a future refactor opportunity, not a correctness issue.

## Validation Evidence

Controller reran:

- `uv run pytest tests/fund/test_extraction_score.py -q`
  - Result: `55 passed in 0.73s`
- `uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py`
  - Result: `All checks passed!`
- `git diff --check`
  - Result: passed

Workers and reviewers also reported the Slice 5 checks passing.

## Boundary Judgment

Hard constraints remain intact:

- No FQ0-FQ6 threshold, severity, or meaning changed.
- No quality-gate source code changed.
- No `FundDocumentRepository` bypass; score consumes snapshot records only.
- Missing, weak, ambiguous, malformed, or anchorless evidence remains blocking.
- Weak qualitative evidence is not promoted to quantitative evidence.
- No golden corpus promotion or baseline promotion.
- No QDII, FOF, 110020, release readiness, Host/Agent/dayu, PR, push, merge, approve, or mark-ready work.
- No explicit parameters hidden in `extra_payload`.
- UI -> Service -> Host -> Agent boundary is unchanged.

## Decision

Slice 5 is accepted for local checkpoint. Proceed to Slice 6 real `006597 / 2024` repository smoke, extraction snapshot, extraction score, and quality gate validation.
