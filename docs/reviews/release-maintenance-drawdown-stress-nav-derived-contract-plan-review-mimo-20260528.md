# Drawdown Stress NAV-Derived Contract Plan Review - MiMo

Date: 2026-05-28

Reviewer: MiMo

Gate: plan review

Work unit: `drawdown_stress evidence contract / NAV-derived risk metric design gate`

Reviewed target: `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-20260528.md`

Conclusion: FAIL

## Worker Self-Check

- Current gate / role: plan review worker only; I did not start `$gateflow` / `/gateflow`, did not enter implementation, and did not commit / push / PR / closeout.
- Source of truth read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, target plan, latest `006597` snapshot / score / quality gate artifacts under `reports/*bond-risk-crosscheck-suffix-006597-2024-20260528*`, and relevant NAV / extractor / model / snapshot / score / quality gate code.
- Scope boundary: review artifact only. No production code, tests, fixtures, baseline/golden promotion, release state, external mutation, or unrelated dirty files touched.
- Evidence basis: static code/doc review plus local artifact/cache inspection. No tests were run because this is plan review.
- Stop condition: plan has material unresolved contract/source decisions and is not implementation-handoff-ready.

## Evidence Read

- Latest snapshot `reports/extraction-snapshots/bond-risk-crosscheck-suffix-006597-2024-20260528/snapshot.jsonl` shows `bond_risk_contract_status="partial"`, satisfied groups excluding `drawdown_stress`, `bond_risk_weak_groups=["drawdown_stress"]`, and `nav_data` with `source=nav_cache; cached=True; records=1802`.
- Latest score `reports/scoring-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/score.json` still emits `issue_code="bond_risk_evidence_missing"`, `baseline_blocking=true`, `missing_evidence_groups=["drawdown_stress"]`.
- Latest quality gate `reports/quality-gate-runs/bond-risk-crosscheck-suffix-006597-2024-20260528/quality_gate.json` remains `status="warn"` with projected `FQ2F` / `reason="bond_risk_evidence_missing"`.
- Local NAV cache for `006597` is from `akshare`, updated `2026-05-19T05:07:11.758531+00:00`, and the raw sample contains `净值日期`, `单位净值`, `日增长率`; no cumulative / adjusted / total-return series type metadata is exposed by current `NavDataResult`.

## Findings

### P1-未修复-[严重]-controller blocking decisions未收敛但plan仍建议进入implementation
- **Plan位置**: `Contract Decision`、`Implementation Slices If Approved`、`Blocking Questions For Controller`、`Plan Conclusion`
- **问题类型**: open question 未收敛 / 不可直接实施 / 架构边界
- **计划当前写法**: plan 先声明 `drawdown_stress` may accept NAV-derived quantitative evidence，并列出 6 个 implementation slices；但末尾仍把是否接受 `public_nav_series_derived`、NAV source allowlist、provider 不支持 total-return 时是否停止列为 controller blocking questions。
- **为什么有问题**: 这三个问题决定 public evidence contract、source strategy、baseline blocker 是否可能解除，不能交给 implementation agent 在实现中自行选择。Gateflow plan rules 要求 blocking open questions 在 implementation 前解决；用户 handoff 也明确 `public_nav_series_derived` 只能在 typed contract / provenance / total-return basis / derived anchor / fail-closed policy 显式时原则接受，且 current provider ambiguous 时 blocker 必须保留。
- **直接证据**: plan lines 102-121 直接做 contract decision；lines 521-525 又列出同一决策为 blocking questions；lines 547-549 只条件性推荐 implementation。`docs/implementation-control.md` 当前 gate allowed scope 是 plan/review before implementation，并要求不得 claim blocker 解除 without quantitative evidence or reviewed contract change。
- **影响**: implementation worker 可能在 controller 尚未裁决 source class 和 allowlist 前改模型、snapshot、score，造成 public contract 漂移；也可能在 provider 实际只支持 ambiguous NAV 时仍推进后续 schema/score 改造，最后产生大范围返工。
- **建议改法和验证点**: 先把 plan 改成二选一的 controller decision artifact：A. controller 接受 `public_nav_series_derived` 并明确 allowlist / fail-closed policy / schema path 后，才进入 implementation；B. current provider 无法证明 total-return basis 时，本 work unit 结论为 `blocked-with-decision/no implementation`，保持 006597 blocker。re-review 前必须删除或裁决这三个 blocking questions。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 严重

### P2-未修复-[高]-derived anchor方案与当前bond_risk_evidence.v1校验直接冲突且未定义schema版本策略
- **Plan位置**: `Required Contract Fields` / `Anchor format` / `Snapshot / Score / Quality Gate Decision`
- **问题类型**: 契约缺失 / public contract change / 不可直接实施
- **计划当前写法**: plan 要“keep existing stable anchor_id grammar”，同时扩展 `BondRiskEvidenceAnchorRef`，让 NAV-derived anchor 使用 `section_id=None`，并继续把 `source_anchor_ids` 放入 `BondRiskEvidenceGroupRecord`。
- **为什么有问题**: 当前 `BondRiskEvidenceAnchorRef.section_id` 是非空 `str`，validator 明确拒绝空 section_id；`BondRiskEvidenceValue` docstring 和校验语义也把 v1 描述为年报可追溯证据。derived/external anchor 会改变 public contract、snapshot schema 和 score acceptance semantics，不能在 `bond_risk_evidence.v1` 内靠字段追加含混处理。
- **直接证据**: `fund_agent/fund/extractors/models.py` 中 `BondRiskEvidenceAnchorRef.section_id: str`；`_validate_bond_risk_anchor_refs()` 在 section_id 为空时 raise `section_id 不能为空`；`_validate_bond_risk_group_anchor_refs()` 对 accepted/weak 组要求至少一个可解析锚点。plan lines 164-169 明确要求 NAV-derived `section_id=None`。
- **影响**: 按 plan 直接实现会要么无法通过现有 validator，要么为通过 validator 伪造 annual-report section_id，破坏证据语义；若静默放宽 v1，则旧 score/snapshot/fixtures 无法区分 annual-report anchor 与 derived anchor，review 也无法确认 blocker 是被严格解除还是被 schema 漏洞绕过。
- **建议改法和验证点**: controller 应要求 plan 明确 schema/version strategy：例如新增 `bond_risk_evidence.v2` 或显式 `bond_risk_evidence.v1` backward-compatible extension，并定义 parser、serializer、snapshot migration、old-row fail-closed behavior。derived anchor 校验必须写成 source-kind-aware invariant：annual_report 仍要求 section_id；public_nav_series/derived 必须要求 provenance_ref、source_name、period/window/observation metadata。测试必须覆盖 old v1 rows、missing section_id annual anchor、derived anchor accepted、derived anchor missing provenance fail-closed。
- **修复风险（低/中/高）**: 高
- **严重程度（低/中/高/严重）**: 高

### P3-未修复-[高]-`日增长率` compounding仍是ambiguous return basis，plan缺少先验证source capability的停止切片
- **Plan位置**: `Why Current NAV Data Is Not Sufficient By Itself`、`NAV-Derived Metric Method`、`Slice 1`
- **问题类型**: 契约缺失 / 非最优方案 / 切片过粗
- **计划当前写法**: plan 承认当前 006597 cache only shows `单位净值` and `日增长率`，并允许“source-provided daily return compounded only if adapter documents total-return-equivalent”；Slice 1 再尝试 normalize raw records and provenance。
- **为什么有问题**: 当前 production adapter 调用 `ak.fund_open_fund_info_em(..., indicator="单位净值走势")`，`NavDataResult` 只暴露 records/source/cached/unavailable，cache hit 时还把 origin source / updated_at 隐藏在 result 外。`日增长率` 是否包含分红再投资不是代码事实；用它复合仍不能证明 total-return basis。plan 应先做 source capability decision/spike，而不是同时规划 provenance dataclass、calculator、bond-risk model、snapshot、score 变更。
- **直接证据**: `fund_agent/fund/data/nav_data.py` lines 72-76 固定 indicator 为 `单位净值走势`；`NavDataResult` lines 99-117 无 series_type / adjustment_basis / origin metadata；cache read lines 299-306 只返回 payload_json。local `006597` cache sample contains `净值日期`, `单位净值`, `日增长率` only. plan lines 191-196 将 daily return compounding列为 conditional accepted equivalent，但未给出当前 provider 如何证明该条件。
- **影响**: implementation 可能写出数学正确但财务口径错误的 max drawdown/volatility，尤其分红附近会把 unadjusted unit NAV 的下跳误当作投资者回撤；也可能完成大量 downstream contract work 后才发现真实 006597 仍必须 fail-closed。
- **建议改法和验证点**: 把 Slice 1 改成“source capability / no-production-contract decision slice”：只通过 unified data boundary 检查可用字段、origin metadata、series_type/adjustment_basis，并输出 controller decision。若 current provider 只能提供 `单位净值` 或 ambiguous `日增长率`，本 work unit 应停止为 blocked/no implementation，保留 `missing_evidence_groups=["drawdown_stress"]`。测试必须包含 `日增长率` present but no total-return proof => fail-closed，不得 satisfy group。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

### P4-未修复-[高]-snapshot/score acceptance条件不足以验证per-group derived provenance
- **Plan位置**: `Snapshot / Score / Quality Gate Decision`、`Slice 5`
- **问题类型**: 契约缺失 / 测试缺口 / overcoupling
- **计划当前写法**: score “may treat drawdown_stress as satisfied only when the snapshot row declares the group satisfied and has traceable annual or derived provenance”；snapshot 可选 “generic anchor_source_kind fields” 或 bond-risk-specific fields。
- **为什么有问题**: 当前 score 只检查 `value_present`、`anchor_present`、`bond_risk_contract_status` 和四组 group-set 字段；它不会读取 group-level metric/provenance，也不会证明 `drawdown_stress` 的 satisfied 状态来自 accepted NAV-derived metric。plan 允许“snapshot row declares group satisfied”作为核心条件，但没有定义 score 必须验证 per-group provenance 与 anchor_id/source_anchor_ids 一致。
- **直接证据**: `fund_agent/fund/extraction_score.py` `_bond_risk_unsatisfied_groups()` 只消费 `anchor_present`、`bond_risk_contract_status`、`bond_risk_satisfied_groups`、`bond_risk_missing_groups`、`bond_risk_weak_groups`、`bond_risk_ambiguous_groups`。`fund_agent/fund/extraction_snapshot.py` `_build_bond_risk_evidence_record()` 当前只用 `_first_annual_report_anchor(...)` 决定 `anchor_present`，没有 group-level provenance projection。plan lines 296-309 未给出 required snapshot schema 或 per-group score invariant。
- **影响**: 一条带任意 annual anchor 的 snapshot row 只要把 `drawdown_stress` 放入 satisfied_groups，就可能让 score 停止 emitting blocker；这会把 fail-closed policy 变成 trust-the-snapshot，而不是可审计的 evidence contract。
- **建议改法和验证点**: plan 应指定最小机器可校验 schema，例如 `bond_risk_group_sources` / `bond_risk_group_provenance_status` / `bond_risk_group_calculation_methods` / `bond_risk_group_anchor_ids` 的 per-group projection，或直接 snapshot serialized group records。score 必须对 `drawdown_stress` 校验：source_kind in allowed, calculation_method accepted, provenance_status accepted, period/window/fund/year match, referenced anchor exists, weak/ambiguous absent。测试必须覆盖 row-level `anchor_present=true` 但 drawdown provenance missing => blocker remains。
- **修复风险（低/中/高）**: 高
- **严重程度（低/中/高/严重）**: 高

## Open Questions

1. Controller 是否接受 `public_nav_series_derived` 作为 `drawdown_stress` source class？若接受，是否必须升级 schema version 或允许 v1 extension？
2. Current provider 是否能通过 unified `FundNavDataAdapter` 提供 cumulative / adjusted / total-return-equivalent series with explicit metadata？若不能，本 gate 是否应以 blocked/no implementation 结束？
3. Snapshot contract 是否应该暴露 per-group evidence records，而不是继续用 row-level `anchor_present` + group-set fields？

## Residual Risks

- NAV-derived metrics are defensible only after source basis is proven. Until then, all real 006597 outcomes must keep `drawdown_stress` weak / unsatisfied.
- Existing legacy `nav_cache` rows may be useful for raw availability but should be ineligible for risk evidence unless refreshed or migrated with explicit provenance.
- If schema stays `bond_risk_evidence.v1`, downstream tooling may treat annual-report and derived anchors as compatible when their audit semantics differ.

Suggested tracking destination: same work unit, plan fix / re-review before implementation; if provider source proof fails, controller decision artifact should close this gate as blocked with owner for a future NAV source contract gate.

## Controller Decision Placeholder

| Finding | Suggested disposition | Controller decision |
|---|---|---|
| P1 | accepted | TBD |
| P2 | accepted | TBD |
| P3 | accepted | TBD |
| P4 | accepted | TBD |

## Final Conclusion

FAIL.

This plan has the right safety instincts, especially preserving weak qualitative drawdown text and requiring fail-closed NAV provenance. It is not yet implementation-ready because the decisive source-class, return-basis, schema-version, and per-group provenance contracts remain unresolved.
