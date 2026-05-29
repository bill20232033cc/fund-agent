# Fixture Promotion State Manifest Plan Review

Reviewer: AgentMiMo
Date: 2026-05-29
Timestamp: 20260529-130003

## Reviewed Target

`docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md`

Plan authored by AgentCodex planning worker for the `fixture promotion state manifest gate`.

## Scope

Adversarial plan review against user requirements: schema fields, fixture_state enum, consumption of 12-entry residual manifest, 006597 bond resolved but fixture absent/not_promoted, QDII/FOF/110020 deferred/blocked not ready, no promotion/golden fixture/FQ/score/quality changes, validation policy.

## Source Of Truth Verified

- `AGENTS.md` — gate classification, hard constraints, no promotion without independent gate
- `docs/design.md` — current architecture boundary
- `docs/implementation-control.md` — next entry point, allowed scope, non-goals
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` — 12-entry residual manifest (2 GLOBAL + 10 fund/slot)
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json` — 10 preflight rows, static disposition manifest with source paths
- `docs/reviews/release-maintenance-golden-readiness-residual-disposition-controller-judgment-20260529.md`
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md`
- `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md`
- `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md`
- `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md`

## Assumptions Tested

| # | Assumption | Evidence | Verdict |
|---|---|---|---|
| 1 | Preflight has exactly 10 fund/slot rows | Preflight `rows[]` has 10 entries: 004393, 004194, 017641, 006597, 110020, 096001, 040046, 019172, 021539, FOF_SLOT | Confirmed |
| 2 | Residual manifest has exactly 2 GLOBAL + 10 fund/slot | Manifest JSON `entries[]` has 12 entries; 2 GLOBAL + 10 fund/slot | Confirmed |
| 3 | All residual entries have `promotion_allowed=false` | All 12 entries verified | Confirmed |
| 4 | 006597 bond_risk_evidence_missing is resolved | Preflight row `resolved_items[]` contains `bond_risk_evidence_missing`; current blockers are `strict_golden_not_configured` + `fixture_promotion_absent` only | Confirmed |
| 5 | QDII rows are deferred/blocked | 096001/040046/019172/021539: residual `decision=defer_from_v1`, preflight `readiness=blocked` | Confirmed |
| 6 | 017641 is not a v1 candidate | Residual `decision=defer_from_v1`, `replacement_disposition=replace` | Confirmed |
| 7 | FOF_SLOT is deferred | Residual `decision=defer_from_v1`, preflight `fixture_promotion_state=absent` | Confirmed |
| 8 | 110020 is deferred | Residual `decision=defer_from_v1`, 5 blockers preserved | Confirmed |
| 9 | 006597 source paths match static disposition | Static disposition: snapshot=`reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl`, score=`reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`, quality_gate=`reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json` | Partial — see Finding 1 |
| 10 | Fixture state enum forbids `promoted` | Plan explicitly forbids `promoted` and `promotion_allowed=true` | Confirmed |
| 11 | No promotion/golden/score/quality/runtime change in scope | Plan scope is docs/reviews JSON + evidence only | Confirmed |

## Findings

### 01-unfixed-medium-006597 source_quality_gate_path in plan example uses wrong directory

- **位置**: Schema > Entry object fields example (line 124), and 006597 Bond Evidence Handling > source paths (line 229)
- **问题类型**: 不可直接实施 / 契约缺失
- **当前写法**: Plan example specifies `source_quality_gate_path: "reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json"`. Bond Evidence Handling section repeats this path.
- **反例/失败场景**: `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/` directory contains only `snapshot.jsonl`, `summary.md`, and `errors.jsonl`. No `quality_gate.json` exists there. The correct path is `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json` as recorded in the preflight static disposition manifest.
- **为什么有问题**: The plan's Consumption Algorithm step 5 instructs implementation to "copy source paths from static disposition entry when applicable," which would yield the correct path. However, the plan's own example JSON and Bond Evidence Handling section explicitly specify the wrong directory. An implementation worker following the example literally would write a non-existent path into the manifest.
- **直接证据**:
  - Preflight static disposition entry for 006597: `"quality_gate_path": "reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json"` (line ~96 of preflight JSON)
  - Plan line 124: `"source_quality_gate_path": "reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json"`
  - Filesystem check: `ls reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/` → `errors.jsonl snapshot.jsonl summary.md` (no quality_gate.json)
  - Filesystem check: `ls reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/` → `quality_gate.json` exists
- **影响**: Implementation agent may write incorrect path into manifest JSON. Schema/self-check would catch it if file-existence validation is added, but the plan's self-check list does not include "verify source paths point to existing files."
- **建议改法和验证点**:
  1. Fix plan example JSON line 124: change `source_quality_gate_path` to `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`
  2. Fix Bond Evidence Handling section line 229: change quality_gate path to `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`
  3. Add to validation checklist: "all source paths point to existing files on disk"
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 02-unfixed-low-Required Current Row Mapping uses ambiguous "required" for source paths

- **位置**: Required Current Row Mapping table (lines 196-206)
- **问题类型**: 不可直接实施
- **当前写法**: Table uses "small-baseline snapshot/score/quality paths required", "bond-risk-drawdown-nav snapshot/score/quality paths required", "QDII candidate paths required", "source paths must be null", "reviewed-candidate paths required" without specifying concrete path values.
- **反例/失败场景**: Implementation worker must cross-reference the Consumption Algorithm step 5 ("copy source paths from static disposition entry when applicable") and the static disposition manifest entries to derive actual paths. This works but creates ambiguity — the table appears to be the authoritative row-by-row specification but defers to the algorithm.
- **为什么有问题**: The plan's Consumption Algorithm provides the mechanism, but the row mapping table — which reviewers use to verify correctness — does not confirm concrete values. This makes review verification harder.
- **直接证据**: Lines 196-206 use "required" for 9 of 10 rows. Only 006597 has concrete paths (which are wrong per Finding 1). FOF_SLOT correctly specifies "source paths must be null."
- **影响**: Low — the algorithm is clear and the static disposition manifest provides authoritative paths. But it increases the chance of implementation error for rows where paths are not explicitly listed.
- **建议改法和验证点**: Add a column or note indicating the source path values come from `static_disposition_manifest.entries[]` keyed by `(fund_code, report_year)`. No code change needed.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Architecture Boundary Review

Plan scope is explicitly limited to `docs/reviews` JSON + evidence artifact. No code, runtime, preflight, Host/Agent/dayu, or service boundary is touched. The plan correctly identifies classification as `heavy` because it defines a durable baseline/golden fixture promotion state control-plane schema. No boundary violation found.

## Best-Practice Review

The plan's two-slice approach (JSON manifest + evidence artifact) followed by controller judgment (Slice C) follows the project's gate pattern. The validation commands are appropriate for JSON-only scope. The plan correctly defers parser/validation code to a future gate. No deviation found.

## Optimal-Solution Review

The plan is the most direct path: consume existing preflight + residual manifests, produce a state ledger JSON, and record evidence. No simpler or safer alternative was identified.

## Overengineering Review

The schema includes 13 fields per entry. All fields serve the state-ledger purpose. No unnecessary abstraction found.

## Overcoupling Review

The plan produces two independent artifacts (JSON + evidence markdown) with no code dependency. The JSON manifest does not couple to runtime or preflight consumption. No overcoupling found.

## Open Questions

No blocking open question.

Non-blocking for future controller decision:

- Whether a future preflight should consume this manifest. Plan recommends a separate `manifest runtime/preflight consumption gate` if desired.

## Residual Risks

| Risk | Severity | Tracking |
|---|---|---|
| Source path self-check does not verify file existence on disk | Low | Add to future validation checklist or self-check script |
| `fixture_state` enum allows both `deferred_from_v1` and `blocked` for the same logical state; recommended mapping uses `deferred_from_v1` but `blocked` is also valid | Low | Acceptable — plan's recommended mapping is clear |

## Reviewer Self-Check

- [x] Reviewed target and scope clearly stated
- [x] Source of truth and assumptions tested documented
- [x] Findings are evidence-based, adversarial, and actionable
- [x] Open questions and residual risks separated from findings
- [x] Conclusion is one of: pass / pass-with-risks / fail
- [x] Output path uses system-clock timestamp and matches `docs/reviews/` format

## Conclusion

**accepted-with-required-fixes**

The plan is well-structured, correctly consumes the 12-entry residual manifest, properly handles 006597 bond resolution with fixture state remaining absent, correctly defers QDII/FOF/110020, and maintains all hard constraints (no promotion, no golden fixture changes, no FQ/score/quality changes).

One medium-severity finding requires fix before implementation: the `source_quality_gate_path` for 006597 in the plan's example JSON and Bond Evidence Handling section points to `reports/extraction-snapshots/...` but the correct path (per preflight static disposition and filesystem verification) is `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`. Fix the two plan lines, add file-existence validation to the self-check, and the plan is handoff-ready.
