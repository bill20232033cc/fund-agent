# Code Review

## Scope

- Mode: current changes
- Branch: `codex/local-reconciliation`
- Base: `main`
- Output file: `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-review-glm-20260527.md`
- Included scope:
  - `fund_agent/fund/extraction_score.py` (workspace unstaged)
  - `fund_agent/fund/quality_gate.py` (workspace unstaged)
  - `tests/fund/test_extraction_score.py` (workspace unstaged)
  - `tests/fund/test_quality_gate.py` (workspace unstaged)
  - `fund_agent/fund/README.md` (workspace unstaged)
  - `tests/README.md` (workspace unstaged)
  - `docs/reviews/release-maintenance-bond-lens-score-applicability-implementation-evidence-20260527.md` (untracked)
- Excluded scope: all committed changes relative to main; untracked files unrelated to this gate
- Parallel review coverage: 无；单 reviewer 全链路走读

## Truth Sources Aligned

| Source | Alignment |
|---|---|
| AGENTS.md | 未违反；无架构边界、模块边界或流程规则冲突 |
| Design plan (`release-maintenance-bond-lens-score-applicability-design-plan-20260527.md`) | 实现与设计一致；所有 8.2/8.3 步骤均已落地 |
| Controller judgment (`release-maintenance-bond-lens-score-applicability-design-plan-controller-judgment-20260527.md`) | 所有 finding disposition 均已满足 |
| implementation-control.md Startup Packet | 未越界；scope 限制在允许文件集合内 |

## Findings

未发现实质性问题。

以下为已确认但不构成 material defect 的观察点：

### O1-已确认-[低]-raw_total_field_count 语义边界

- **入口/函数**: `_fund_field_applicability_decisions`
- **文件(行号)**: `fund_agent/fund/extraction_score.py` ~L1657
- **输入场景**: 债券基金 snapshot 同时包含指数质量字段（理论上不太可能）
- **实际分支**: `bond_fund` 分支
- **预期行为**: `raw_total_field_count` 代表"应用债券排除前的字段数"
- **实际行为**: `raw_total_field_count` 是 `_records_after_index_applicability` 的结果，即已过滤指数质量字段后的计数。"原始"语义是"债券适用性过滤前"而非"所有适用性过滤前"
- **直接证据**: L1657 `raw_records = _records_after_index_applicability(records, ...)`，然后 L1662 `raw_total_field_count = len(raw_records)`
- **影响**: 对纯债券基金（不会携带指数质量字段），raw 和 applicable 之间只差 holdings_snapshot 一条记录，语义无歧义。对同时携带指数质量字段的异常 bond_fund 样本，raw 计数不含指数字段，但 `FieldApplicabilityDecision` 的职责是解释债券排除的 delta，而非指数排除的 delta。当前实现行为自洽。
- **建议改法和验证点**: 无需改动。若未来需要展示"全原始"计数，可在 decision 中增加 `unfiltered_total_field_count` 字段。
- **修复风险（低）**: 不修复无风险。
- **严重程度（低）**: 不影响 correctness；对实际 bond_fund 样本无歧义。

### O2-已确认-[低]-derive 函数重复按基金分组

- **入口/函数**: `derive_field_applicability_decisions`, `derive_score_applicability_issues`
- **文件(行号)**: `fund_agent/fund/extraction_score.py` L873-L880, L902-L905
- **输入场景**: 任意 snapshot 记录集合
- **实际分支**: 主循环
- **预期行为**: 两个函数独立工作
- **实际行为**: 两个函数各自执行一次 `records_by_fund` 分组，遍历相同的记录集合
- **直接证据**: L873 `records_by_fund: dict[str, list[Mapping[str, object]]] = {}` 和 L902 相同代码
- **影响**: 评分链路非热路径；重复 O(n) 分组对 correctness 无影响，对性能无实际影响
- **建议改法和验证点**: 若后续合并调用点，可提取共享的 `records_by_fund`。当前不影响 gate。
- **修复风险（低）**: 不修复无风险。
- **严重程度（低）**: 纯 style/efficiency 观察。

### O3-已确认-[低]-issue_id 验证不检查 report_year 段

- **入口/函数**: `_validate_score_applicability_issue_id`
- **文件(行号)**: `fund_agent/fund/quality_gate.py` L1180-L1184
- **输入场景**: 外部提供的 `score.json` 中 `score_applicability_issues`
- **实际分支**: 正常验证路径
- **预期行为**: 验证 issue_id 的确定性格式
- **实际行为**: 只校验前缀 `score-applicability:{fund_code}:` 和后缀 `:{field_name}:{issue_code}:{contract_id}`；中间 `report_year` 段允许任意内容
- **直接证据**: L1180 `expected_prefix = f"score-applicability:{fund_code}:"` 和 L1183 `expected_suffix = f":{field_name}:{issue_code}:{contract_id}"`
- **影响**: issue_id 由同一系统的 `_score_applicability_issue_id` 确定性生成，report_year 由 `_fund_report_year_text` 返回 `str(year)` 或 `"unknown-year"`。外部篡改或损坏的 report_year 段不会被检出，但 `report_year` 字段本身已被 `_required_applicability_text` 独立验证为非空字符串。风险可忽略。
- **建议改法和验证点**: 无需改动。若未来需要严格校验，可解析中间段并匹配 `\d{4}|unknown-year`。
- **修复风险（低）**: 不修复无风险。
- **严重程度（低）**: 不影响 correctness。

## Adversarial Failure Pass

### 债券排除条件精确性

走读 `_is_bond_holdings_replacement_record_for_type`（L2010-L2035）：只有 `field_name == "holdings_snapshot"` 且 `fund_type == "bond_fund"` 同时满足时返回 True。`fund_type` 优先使用 `classified_fund_type` 参数；参数为 None 时通过 `use_record_fund_type` 回退到记录自身类型。所有调用点均传入 `_unique_optional_text` 解析的 fund_type 和 `use_record_fund_type=False`，确保冲突类型不被逐条记录绕过。

### Fail-closed 验证

未知类型（空字符串、缺失）经 `_unique_optional_text` 返回 `None` → `_is_bond_holdings_replacement_record_for_type` 返回 False → holdings_snapshot 留在分母 → 不生成 bond issue。冲突类型同理。测试 `test_unknown_or_conflicted_fund_type_keeps_holdings_fail_closed` 覆盖了这两种场景。

### 006597 anti-mis-pass

实现 evidence 记录：
- Before: `missing_field_rate=0.357` (FQ4 block >= 0.35)
- After: `missing_field_rate=0.308` (FQ4 warn >= 0.20) + FQ2F/warn `bond_risk_evidence_missing`
- Gate: `block` → `warn`（未 pass）

状态变化可解释：block 源于权益持仓类别错误导致的虚高缺失率；warn 源于实际适用的 P1 缺失（holder_structure, share_change, turnover_rate）加上替代风险证据缺口。FQ4 阈值本身未变。满足设计 plan section 5.4 全部 5 条要求。

### FQ4 阈值不变

`_missing_rate_issues` 未被修改。`FundQualityRow.missing_field_rate` 仍然是 applicable rate（适用性过滤后）。债券排除只改变分母内容，不改变阈值代码。测试 `test_run_quality_gate_preserves_fq4_thresholds_with_score_applicability_issue` 验证了 FQ4 block 在 0.35 阈值处仍然触发。

### 旧 score.json 兼容

`quality_gate.py` L291 `score_payload.get("score_applicability_issues", [])` — 缺键返回空列表，不触发任何新逻辑。测试 `test_run_quality_gate_treats_missing_score_applicability_issues_as_empty` 验证了旧 payload gate status 不变。

### 回归面

- active fund: `test_active_fund_keeps_holdings_snapshot_applicable` — holdings_snapshot 仍在分母，不生成 bond issue
- index/enhanced: `test_index_and_enhanced_keep_holdings_snapshot_applicable` — holdings_snapshot 仍在分母
- 现有评分集成: `test_run_extraction_score_writes_score_outputs` — 新增空数组断言 + markdown 新 section 存在断言

## Open Questions

- 无。

## Residual Risk

- `bond_risk_evidence.v1` 契约已声明但当前所有 bond_fund 样本均触发 `bond_risk_evidence_missing`。正向债券风险提取/evidence 输入不在本 gate scope。这是已知的有意设计选择，不是实现缺陷。
- `baseline_blocking=true` 在 score JSON 中输出但 durable baseline/golden 提升仍是 future gate consumer。同上。
- active/index/enhanced 回归测试未显式断言 `derive_field_applicability_decisions` 返回空元组；但行为已通过分母正确性隐式证明。

## Reviewer Self-Check

- [x] Review mode、base、scope 和 source evidence 已写清
- [x] 无 finding 绑定到具体 code location 或 explicit behavior（三个观察点均已确认非 material defect）
- [x] Adversarial pass、open questions、residual risk 和未覆盖区域已记录
- [x] Output path 位于 `docs/reviews/` 且格式正确

## Verdict

**PASS_WITH_FINDINGS**

三个观察点均为低严重度，不影响 correctness、stability 或 maintainability。无需 re-review。

实现与设计 plan、controller judgment 和 evidence artifact 完全对齐。所有关键安全属性（fail-closed、anti-mis-pass、FQ4 阈值不变、旧 payload 兼容）已被代码和测试正确覆盖。71 tests passed。
