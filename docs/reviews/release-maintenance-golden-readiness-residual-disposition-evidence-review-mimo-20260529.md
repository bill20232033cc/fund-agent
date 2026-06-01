# Code Review

## Scope

- Mode: current changes
- Branch: codex/local-reconciliation
- Base: HEAD (uncommitted files only)
- Output file: `docs/reviews/release-maintenance-golden-readiness-residual-disposition-evidence-review-mimo-20260529.md`
- Included scope:
  - `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
  - `docs/reviews/release-maintenance-golden-readiness-residual-disposition-implementation-evidence-20260529.md`
  - Accepted plan commit `fc2582f` (`docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-20260529.md`)
- Excluded scope: runtime code, tests, score/quality/snapshot, golden fixtures, FQ0-FQ6, Host/Agent/dayu, PR/release state
- Parallel review coverage: 无

## Review Context

Reviewer: AgentMiMo review worker. Not controller. Verifying Slice A manifest and evidence against accepted plan `fc2582f` and preflight blockers. Verdict is `accepted` or `required-fixes`.

## Verification Checkpoints

| Checkpoint | Result |
|---|---|
| promotion_manifest=false | PASS — `promotion_manifest: false` |
| Every promotion_allowed=false | PASS — all 12 entries have `promotion_allowed: false` |
| Decisions are single enum | PASS — all values in `{needs_fixture_promotion_gate, blocked_until_policy, defer_from_v1}`; no slash-combined values |
| 017641 replacement_disposition=replace | PASS — manifest entry has `replacement_disposition: "replace"` |
| 006597 no bond blocker | PASS — `current_blockers` is `["strict_golden_not_configured", "fixture_promotion_absent"]`; no `bond_risk_evidence_missing` |
| 006597 bond closure invariant preserved | PASS — evidence doc § "How To Keep 006597 Bond Blocker Closed" and drawdown metric controller judgment referenced |
| Evidence artifact paths exist | PASS — all 14 unique paths verified on disk |
| No runtime/score/quality/golden fixture changes | PASS — `git diff --stat HEAD` and `git diff HEAD -- '*.py'` show no output; only two docs/JSON files are uncommitted |
| JSON syntax valid | PASS — `python -m json.tool` succeeded |
| Entry count matches plan | PASS — 12 entries = 12 disposition matrix rows |
| blocks_minimum_v1 values match plan | **FINDING** — see below |
| Validation rationale sufficient | PASS — evidence doc cites JSON parser, self-check, `git diff --check`; docs/JSON-only scope justifies no full ruff/pytest |

## Findings

### 01-未修复-中-QDII global entry blocks_minimum_v1 does not match plan

- **入口/函数**: manifest entry `fund_or_slot="GLOBAL"`, `current_blockers=["qdii_replacement_hard_stop"]`
- **文件(行号)**: `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` line 60; plan table row 2 at line 220
- **输入场景**: manifest is consumed by future gate or controller judgment that reads `blocks_minimum_v1` to determine whether QDII hard stop blocks the minimum v1 path
- **实际分支**: manifest sets `blocks_minimum_v1: true` for the QDII global entry
- **预期行为**: plan disposition matrix (line 220) explicitly specifies `blocks_minimum_v1: false` for the QDII global row, consistent with the plan's Golden v1 Minimum Viable Scope (line 39): "golden v1 不继续追求 QDII / FOF / 110020 纳入 v1；三者均 `defer_from_v1`... 但不得阻塞最小 v1 的 fixture-promotion path"
- **实际行为**: `blocks_minimum_v1` is `true`, meaning QDII hard stop would block the minimum v1 path, contradicting the plan's explicit minimum-v1 exclusion of QDII
- **直接证据**: plan line 220: `| GLOBAL | qdii_replacement_hard_stop | ... | true | false | false |` (blocks_v1=true, blocks_minimum_v1=false). Manifest line 60: `"blocks_minimum_v1": true`. The evidence document self-check (line 65) reports `blocks_minimum_v1=as_planned` but the actual value disagrees with the plan
- **影响**: 错误状态 — a future gate or preflight reading `blocks_minimum_v1=true` for QDII would incorrectly block the minimum v1 fixture-promotion path, even though the plan explicitly excludes QDII from minimum v1 blocking
- **建议改法和验证点**: change manifest line 60 from `"blocks_minimum_v1": true` to `"blocks_minimum_v1": false`. Re-run self-check to confirm `blocks_minimum_v1` values match plan table exactly
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## Open Questions

- 无。

## Residual Risk

- Evidence document self-check output (line 65) reports `blocks_minimum_v1=as_planned` but the QDII global value disagrees with the plan. The self-check script logic may not have compared actual values against the plan table row-by-row; it may have used a different interpretation of "as_planned". If the self-check script is reused in future gates, its comparison logic should be verified.
- The plan's disposition table (lines 221-223) shows `quality_gate_warn` as a warning-level item in the `current_blockers` column for 004393, 004194, and 006597. The manifest omits this from `current_blockers` but captures the intent in `decision_reason`. This is a semantic difference in how warnings are tracked, not a correctness issue — the manifest schema's `current_blockers` field is intended for hard blockers. No action required, but future manifest consumers should be aware that `decision_reason` may contain additional context beyond `current_blockers`.
