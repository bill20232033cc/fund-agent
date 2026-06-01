# release-maintenance bond positive-risk evidence plan — DS Plan Review

> Date: 2026-05-27
> Reviewer: AgentDS
> Gate: `release-maintenance bond positive-risk evidence gate`
> Target artifact: `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-20260527.md`
> Role: independent plan review only; no implementation, no evidence CLI, no production code change, no commit/push/PR

## Verdict

**PASS_WITH_FINDINGS**

## Review Basis

Truth sources consulted:
- `AGENTS.md` (including Gate 轻重分类 rules added by truth-preflight repair)
- `docs/design.md` current sections
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point
- `docs/reviews/release-maintenance-bond-positive-risk-truth-preflight-20260527.md`
- `fund_agent/fund/extraction_score.py` (bond_risk_evidence.v1 groups, issue ID generation, score JSON payload)
- `fund_agent/fund/extraction_snapshot.py` (output path conventions)
- `fund_agent/ui/cli.py` (CLI option verification)
- `fund_agent/services/quality_gate_service.py` (default output dir)
- `fund_agent/services/extraction_score_service.py` (default output dir)

## Findings

### F1 — MEDIUM: Wrong summary filename in Step A inspection table

**Location**: Plan section 3, Step A inspection table, row 2

**Observed**: Table references path
```
reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/summary.json
```

**Expected**: `summary.md`

**Evidence**: `fund_agent/fund/extraction_snapshot.py:440`:
```python
summary_path = resolved_output_dir / "summary.md"
```

The plan does hedge with "or equivalent summary path printed by CLI," which gives the evidence runner a fallback, but the concrete path is factually wrong and could cause the runner to look for a non-existent file before noticing the CLI-printed path.

**Required fix**: Change `summary.json` to `summary.md` in the inspection table.

### F2 — LOW: Step B keyword list does not cover `drawdown_stress` group

**Location**: Plan section 3, Step B inspection script `KEYWORDS` tuple

**Observed**: Keywords include terms for all six other `bond_risk_evidence.v1` groups but omit drawdown/stress-related terms:
- Missing: `"回撤"`, `"波动率"`, `"压力测试"`, `"最大回撤"`, `"波动"`

The `drawdown_stress` group (`extraction_score.py:222-231`) requires evidence of:
> 最大回撤、波动率、压力测试阈值状态，或带来源锚点的回撤/压力计算

**Impact**: Initial repository inspection may miss sections relevant to drawdown/stress evidence. The plan notes that keywords can be broadened ("If the script output is too broad, rerun with narrower keywords"), but gives no guidance on widening. The evidence runner will need to independently notice this gap.

**Recommendation**: Either add drawdown/stress keywords to the initial list, or add a note explicitly flagging `drawdown_stress` as a group whose keywords may need widening if the initial scan finds no candidate sections.

### F3 — INFO (confirmed): CLI commands are valid and output paths resolve correctly

**Verification**:
- `fund-analysis extraction-snapshot --run-id ... --fund-code 006597 --report-year 2024`: valid CLI options. Without `--output-dir`, defaults to `reports/extraction-snapshots/<run_id>/` (confirmed at `extraction_snapshot.py:436`).
- `fund-analysis extraction-score --snapshot-path ... --errors-path ... --golden-answer-path ...`: valid CLI options. Without `--output-dir`, defaults to `snapshot_path.parent` (confirmed at `extraction_score.py:1075`), which resolves to the same run directory.
- `fund-analysis quality-gate --score-path ...`: valid CLI option. Without `--output-dir`, defaults to `score_path.parent` (confirmed at `quality_gate_service.py:21`).

Output paths in the plan's inspection table all resolve correctly to `reports/extraction-snapshots/bond-positive-risk-006597-2024-20260527/`.

### F4 — INFO (confirmed): `bond_risk_evidence.v1` groups match code exactly

**Verification against `extraction_score.py:172-255`**:

| Plan group | Code group_id | baseline_blocking |
|---|---|---|
| `duration_rate_risk` | `duration_rate_risk` | `True` |
| `credit_risk` | `credit_risk` | `True` |
| `leverage_liquidity` | `leverage_liquidity` | `True` |
| `asset_allocation_holdings_mix` | `asset_allocation_holdings_mix` | `True` |
| `drawdown_stress` | `drawdown_stress` | `True` |
| `redemption_share_pressure` | `redemption_share_pressure` | `True` |
| `convertible_bond_equity_exposure` | `convertible_bond_equity_exposure` | `True` |

All 7 groups present. All `baseline_blocking=True`. The plan's concrete satisfying examples for each group (section 2) align with the code's `required_evidence` strings.

### F5 — INFO (confirmed): Score applicability issue ID format matches code

**Plan expects**: `score-applicability:006597:2024:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1`

**Code generates** (`extraction_score.py:1807`):
```python
f"score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}"
```

With `fund_code="006597"`, `report_year="2024"`, `field_name="holdings_snapshot"`, `issue_code="bond_risk_evidence_missing"`, `contract_id="bond_risk_evidence.v1"` → exact match.

`missing_evidence_groups` is populated as a field in `ScoreApplicabilityIssue` (`extraction_score.py:497`) and serialized into `score.json` via `asdict()` at `extraction_score.py:2944-2946`. ✓

## Criteria-by-Criteria Assessment

### 1. Startup Packet and scope obedience — PASS

- Target limited to `006597` / `2024` with `bond_risk_evidence_missing.baseline_blocking=true` ✓
- No golden promotion, QDII probing, FOF taxonomy, release readiness, extractor implementation ✓
- Non-goals section (plan §1) correctly enumerates forbidden scope ✓

### 2. Acceptable evidence criteria — PASS (with F2 note)

- Evidence contract grounded in `bond_risk_evidence.v1` groups from code ✓
- Concrete satisfying examples provided for each of the 7 groups ✓
- What-cannot-satisfy list clearly excludes category labels, unanchored prose, PDF/cache access ✓
- `data_gap` and `extractor/evidence-anchor` classifications are distinct and well-defined ✓
- F2: keyword gap for `drawdown_stress` in Step B is a minor incompleteness, not a criteria failure

### 3. Evidence commands and inspection steps — PASS (with F1 fix needed)

- All CLI commands verified against actual CLI definitions ✓
- Output path resolution confirmed correct without explicit `--output-dir` ✓
- Step B script accesses through `FundDocumentRepository`, not direct PDF/cache/source ✓
- Step B script uses `getattr` defensively on section/table attributes ✓
- F1: `summary.json` must be `summary.md`

### 4. Classification matrix — PASS

- Four states clearly distinguished: sufficient, insufficient, disclosure gap, extractor/evidence-anchor ✓
- Stop-condition table covers code/test changes, boundary violations, source failures, truth contradictions ✓
- Extractor/evidence-anchor state explicitly says "Do not weaken FQ2F/FQ4 or suppress the replacement issue" ✓
- Controller actions after reviews correctly scoped: disposition only, no promotion ✓

### 5. Artifact disposition — PASS

- `--help` file: "do not delete, stage, rename, inspect for evidence, or promote" ✓
- `AGENTS.md`: noted as user/controller-added, do not modify ✓
- Preflight artifact: left unmodified ✓
- Other untracked review artifacts: not staged or modified ✓

### 6. Two-review requirement — PASS

- Section 8 explicitly requires two independent plan reviews before any evidence run ✓
- Re-review loop defined for fixed findings ✓
- Controller judgment required before evidence CLI authorization ✓
- Reviewer prompt constraints specified (not controllers, not implementers) ✓

## Required Patch Before Plan Acceptance

1. In section 3 Step A inspection table, row 2: change `summary.json` to `summary.md`.

Optional recommendation (does not block acceptance):
- In section 3 Step B, either add drawdown/stress keywords (`"回撤"`, `"波动率"`, `"压力测试"`, `"最大回撤"`) to the `KEYWORDS` tuple, or add an explicit note that `drawdown_stress` may require keyword widening after initial scan.

## Re-review

Not required after F1 fix if no other changes are made. F2 is an observation, not a blocking defect — the plan already allows keyword adjustment on rerun.

If the plan author chooses to address F2 by modifying keywords, a re-review is still not required; the change is too narrow to warrant a full re-review cycle.
