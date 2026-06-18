# Controlled Live EID Helper Repair And Retry Planning Gate Plan Review DS - 2026-06-11

Verdict: PASS

## Review Scope

This review evaluates the plan `docs/reviews/mvp-controlled-live-eid-helper-repair-and-retry-planning-gate-plan-20260611.md` against the review questions, current code facts in `fund_agent/fund/documents/models.py`, `scripts/controlled_live_eid_failure_branch_observation.py`, the accepted controller judgment `docs/reviews/mvp-controlled-live-eid-failure-branch-evidence-gate-controller-judgment-20260610.md`, and the control truth in `docs/current-startup-packet.md`.

## Findings

### F1 — Design.md stale wording references identity_status/integrity_status (Informational)

`docs/design.md` line 678 states: "当前 `AnnualReportSourceMetadata` 支持... identity status 和 integrity status"。The current `AnnualReportSourceMetadata` in `fund_agent/fund/documents/models.py` has no such fields. This stale wording in design.md is the likely root cause of the helper script's original overclaim.

The plan line 279 correctly identifies this as a separate docs-sync gate concern and explicitly forbids fixing it by adding production fields. This is the right call: the repair must remove the helper overclaim, not "complete" the model to match stale docs.

**Severity**: Informational. Does not block Stage A. A future docs-sync gate should reconcile design.md line 678 with the current model.

**Disposition**: Accept plan as-is. The plan correctly treats this as out of scope.

### F2 — Optional test would add meaningful no-live coverage (Low)

The plan leaves the no-live regression test (`tests/scripts/test_controlled_live_eid_failure_branch_observation.py`) as an optional controller decision. The test is scoped to construct fake report/metadata objects in memory and call `_safe_report_payload()` directly, without touching `main()`, `_run_observation()`, `FundDocumentRepository`, or any live code path.

The three mandatory validation commands (ruff, py_compile, git diff) are sufficient to verify the repair is syntactically valid and only touches allowed files. However, they do not verify that `_safe_report_payload()` no longer accesses non-existent attributes at runtime — py_compile does import resolution but does not execute the function body.

The optional test would close this gap: it would prove that the repaired `_safe_report_payload()` can serialize a fake report object without AttributeError, and that the output JSON contains the expected safe scalar fields and omits `identity_status` / `integrity_status`.

**Severity**: Low. The repair is a two-line deletion plus an optional one-line addition of an existing field — the risk of a typo or misspelled attribute is low but non-zero.

**Disposition**: Recommend accepting the optional test file. It is no-live, narrowly scoped, and adds deterministic proof that the repair works without requiring live acquisition. If the controller rejects it, the three mandatory commands are still sufficient for a PASS verdict on Stage A given the trivial nature of the repair.

### F3 — No findings on core safety checks (Positive confirmation)

All five mandatory safety checks pass:

1. **Forbid direct live rerun in Stage A**: Confirmed. Lines 135-139 explicitly forbid `uv run python scripts/controlled_live_eid_failure_branch_observation.py` in Stage A. Line 169-170 states "Stage B is not authorized by this plan." Stage B requires separate explicit user authorization after Stage A completion and controller judgment.

2. **Repair limited to removing/replacing non-existent metadata reads**: Confirmed. Lines 53-56 remove only `identity_status` and `integrity_status` from `_safe_report_payload()`. Line 57 forbids replacement with new production model fields. Line 58 forbids adding to `AnnualReportSourceMetadata`. Lines 103-114 give exact allowed source changes. The optional `discovery_contract_version` addition uses an existing model field (`discovery_contract_version: str | None = None` at models.py:71) — this is safe.

3. **Avoid adding identity_status/integrity_status to production metadata**: Confirmed. Line 21 explicitly forbids it. Lines 278-279 treat stale design.md wording as a separate docs-sync gate concern. The models.py dataclass (`AnnualReportSourceMetadata`) is not in the allowed files list.

4. **Preserve EID single-source MVP and ac6bbe9 no-live proof**: Confirmed. Lines 12-13 explicitly preserve both. Lines 68-69 keep target constants unchanged (`006597 / 2024`). Line 218 preserves `ac6bbe9` as no-live proof regardless of Stage B outcome. The helper script uses `EidAnnualReportSource` with `AnnualReportSourceOrchestrator((eid_source,))` — single EID source only. No fallback source is added.

5. **Validation commands no-live and sufficient**: Confirmed. Ruff check (lint), py_compile (syntax + import resolution), and git diff --check (allowed files only) are all no-live. For a repair that deletes two dictionary entries, these three commands are sufficient.

6. **Allowed files and stop conditions precise enough**: Confirmed. Lines 84-89 list exact allowed files. Optional test file is bounded by lines 95-98 with explicit prohibition against calling `main()`, `_run_observation()`, `FundDocumentRepository`, or any live code. Stop conditions cover pre-implementation (lines 242-246), Stage A implementation (lines 248-254), pre-Stage B (lines 256-261), and Stage B execution (lines 263-269).

## Cross-Check: Controller Judgment Alignment

The plan correctly inherits from the controller judgment's accepted facts:

- The live command was consumed exactly once for `006597 / 2024` — the plan does not reuse it.
- Helper crashed in `_safe_report_payload(report)` after `load_annual_report()` returned — the plan repairs exactly that function.
- `identity_status` and `integrity_status` are not current model fields — the plan removes those reads from the helper.
- The prior attempt is explicitly not accepted live success evidence or failure-branch proof — the plan preserves that status.
- `ac6bbe9` remains accepted no-live proof — the plan preserves it.

## Cross-Check: EID Single-Source Policy

The helper script constructs `EidAnnualReportSource` with `AnnualReportSourceOrchestrator((eid_source,))` — a single-element tuple containing only the EID source. The plan keeps this unchanged. No Eastmoney, CNINFO, or fund-company route is introduced. The script uses `force_refresh=True` with gate-local temporary cache isolation — no production cache contamination.

The plan's non-goal section (lines 19-24) explicitly forbids adding non-EID sources, changing source policy, fallback eligibility, or EID single-source semantics.

## Residuals

| Residual | Owner | Notes |
|---|---|---|
| design.md line 678 stale `identity status` / `integrity status` wording | future docs-sync gate | Not a blocker. Plan correctly defers. |
| Live natural occurrence of five modeled failure categories remains unproven | future evidence owner | `ac6bbe9` remains accepted code-behavior proof. |
| Optional test file is controller decision | controller | Recommend accept — adds meaningful no-live coverage. |
| Stage B live retry not authorized by this plan | controller / user | Requires separate explicit authorization. |

No live execution performed: yes
