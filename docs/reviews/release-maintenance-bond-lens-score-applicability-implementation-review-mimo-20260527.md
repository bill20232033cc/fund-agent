# Code Review: bond-lens score applicability implementation

## Scope

- Mode: current changes
- Branch: `codex/local-reconciliation`
- Base: `main`
- Output file: `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-review-mimo-20260527.md`
- Included scope:
  - `fund_agent/fund/extraction_score.py` (unstaged)
  - `fund_agent/fund/quality_gate.py` (unstaged)
  - `tests/fund/test_extraction_score.py` (unstaged)
  - `tests/fund/test_quality_gate.py` (unstaged)
  - `fund_agent/fund/README.md` (staged)
  - `tests/README.md` (unstaged)
  - `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-evidence-20260527.md` (untracked)
- Excluded scope: renderer, Service/CLI, Host/Agent/dayu, `FundDocumentRepository`, source strategy, extractor logic, `fund_type.py`, golden/baseline fixtures, FQ0-FQ6 policy/threshold changes, `extra_payload`, GitHub state
- Parallel review coverage: 无
- Truth sources: `AGENTS.md`, `docs/design.md` v2.2, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, `docs/reviews/release-maintenance-bond-lens-score-applicability-design-plan-20260527.md`, `docs/reviews/release-maintenance-bond-lens-score-applicability-design-plan-controller-judgment-20260527.md`
- Verification: `uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` → `71 passed in 0.79s`; `uv run ruff check` → `All checks passed!`

## Findings

### 01-未修复-低-score_applicability issue_id 确定性校验只检查前缀和后缀

- **入口/函数**: `quality_gate.py` `_validate_score_applicability_issue_id()`
- **文件(行号)**: `fund_agent/fund/quality_gate.py:1154-1187`
- **输入场景**: 任何包含 `score_applicability_issues` 的 score.json
- **实际分支**: 校验 `issue_id.startswith(expected_prefix)` 和 `issue_id.endswith(expected_suffix)`
- **预期行为**: 设计计划 §7.2 定义完整格式为 `score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}`，应校验完整结构
- **实际行为**: 只校验 `score-applicability:{fund_code}:` 前缀和 `:{field_name}:{issue_code}:{contract_id}` 后缀，中间的 `report_year` 段可为任意值
- **直接证据**: `quality_gate.py:1180-1184` 构造 `expected_prefix` 和 `expected_suffix`，不包含 `report_year` 段
- **影响**: 畸形 issue_id（如 `score-applicability:006597:WRONG:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1`）会通过校验。实际风险低，因为生成代码确定性产生正确格式，且 focused tests 验证完整 id 文本
- **建议改法和验证点**: 在 `_validate_score_applicability_issue_id` 中增加 `report_year` 段的 presence/format 校验（如 `\d{4}|unknown-year`），或使用完整 `==` 匹配替代 prefix/suffix 检查
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 02-未修复-低-未知 issue_code 被静默丢弃无日志

- **入口/函数**: `quality_gate.py` `_evaluate_score_applicability_issue()`
- **文件(行号)**: `fund_agent/fund/quality_gate.py:923-924`
- **输入场景**: `score_applicability_issues` 包含 `issue_code` 不等于 `bond_risk_evidence_missing` 的行
- **实际分支**: `if issue_code != BOND_RISK_EVIDENCE_MISSING_ISSUE_CODE: return None`
- **预期行为**: 设计计划 §7.1 定义了多种 issue code（`equity_holdings_not_applicable_to_bond`、`bond_risk_anchor_missing`、`bond_risk_data_gap_declared` 等），quality gate 应至少对已知但未处理的 code 发出 info-level 信号
- **实际行为**: 所有非 `bond_risk_evidence_missing` 的 issue code 被静默丢弃，不产生任何 gate issue 或日志
- **直接证据**: `quality_gate.py:923-924` 返回 `None`
- **影响**: 当前无实际影响（extraction_score 只生成 `bond_risk_evidence_missing`）。未来若 extraction_score 新增 issue code 而 quality_gate 未同步更新，该 issue 会静默消失。属于 forward-compatibility 观察点
- **建议改法和验证点**: 对已知但未投影的 issue code 返回 info-level `FQ0` issue 而非 `None`；或添加注释明确这是 intentional forward-compatibility 并说明新增 code 时的同步要求
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

- 无。

## Residual Risk

1. **`bond_risk_evidence.v1` 正面证据路径未实现**: 当前所有 exact `bond_fund` snapshot 均产生 `bond_risk_evidence_missing` issue。正面 bond-risk evidence 输入需未来独立 gate。
2. **`baseline_blocking=true` 消费者未定义**: 当前 baseline/golden promotion 仍被 control doc 阻断，`baseline_blocking` 字段的消费逻辑属未来 gate。
3. **006597 非 holdings P1 残留**: `holder_structure`、`share_change`、`turnover_rate` 仍为 missing，此 gate 不修复 extractor 逻辑。
4. **`_record_is_covered` 对 `holdings_snapshot` 的 status/source allowlist 校验**: 这是一个有价值的 coverage 收紧（避免仅有行业分布时误判为已覆盖），但与 bond-lens 设计同时引入。该变更对 active/index/enhanced 基金也有影响——现有 `value_present=True` 但无 `top_holdings_status` 的记录将不再视为 covered。focused tests 覆盖了此行为，full pytest 通过，但引入时机与 bond-lens scope 重叠，controller 可裁决是否需独立说明。

## Scope Compliance

| Check | Result |
|---|---|
| Allowed files only | PASS — 仅修改 `extraction_score.py`、`quality_gate.py`、focused tests、README sync、evidence artifact |
| Renderer unchanged | PASS |
| FQ0-FQ6 policy/threshold unchanged | PASS — FQ4 阈值 warn>=0.20 / block>=0.35 未变；新增 `CORRECTNESS_COVERAGE_YEAR_NOT_COVERED` 为 info 级别 |
| Service/CLI unchanged | PASS |
| Host/Agent/dayu unchanged | PASS |
| Extractor/fund_type unchanged | PASS |
| Golden/baseline unchanged | PASS |
| `extra_payload` unused | PASS |
| 006597 anti-mis-pass | PASS — gate status 为 `warn` 而非 `pass`；`bond_risk_evidence_missing` issue 显式存在 |
| Old score.json compatibility | PASS — `score_applicability_issues` 缺失时默认空列表 |
| Deterministic issue id | PASS — 格式 `score-applicability:{fund_code}:{report_year}:{field_name}:{issue_code}:{contract_id}` |

## Reviewer Self-Check

- [x] Review mode、base、included/excluded scope 和 source evidence 已写清
- [x] 每个 finding 绑定具体 code location，root cause 使用直接证据
- [x] findings 为 material、可执行，无 style/nit/speculation
- [x] adversarial pass、open questions、residual risk 和未覆盖区域已记录
- [x] output path 位于 `docs/reviews/`
