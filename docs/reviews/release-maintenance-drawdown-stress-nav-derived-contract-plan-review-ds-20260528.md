# Drawdown Stress NAV-Derived Contract Plan Review - DS Replacement

Date: 2026-05-28

Reviewer: DS/GLM replacement

Gate: second plan review after one reviewer FAIL

Work unit: `drawdown_stress evidence contract / NAV-derived risk metric design gate`

Reviewed target: `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-20260528.md`

Existing review considered: `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-mimo-20260528.md`

Conclusion: FAIL

## Worker Self-Check

- Current role is plan review worker only. I did not start `$gateflow` / `/gateflow`, did not enter implementation, and did not commit / push / PR / closeout.
- Source of truth read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, target plan, MiMo review, latest 006597 snapshot / score / quality gate artifacts, and required NAV / extractor / model / snapshot / score code.
- Scope boundary: review artifact only. I added only this review artifact and did not modify production code, tests, fixtures, plan, control doc, baseline/golden data, release state, or GitHub state.
- Evidence basis: static code/doc/artifact review plus local NAV cache inspection. No tests were run because this is plan review.
- Stop condition: the plan still contains unresolved source-basis, schema/version, derived-anchor, and score-provenance decisions that decide whether this gate can safely implement anything beyond a fail-closed capability check.

## Assumptions Tested

1. Current NAV source can prove total-return / cumulative / adjusted basis for 006597 / 2024.
2. Current `bond_risk_evidence.v1` anchor validation can represent a derived NAV anchor without pretending it is an annual-report anchor.
3. Current snapshot / score contract can machine-check group-level derived provenance for `drawdown_stress`.
4. The plan is code-generation-ready for implementation rather than a controller decision / blocked-with-decision artifact.

## Direct Evidence Summary

- `fund_agent/fund/data/nav_data.py` calls `ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")` and `NavDataResult` only exposes `records`, `source`, `cached`, `unavailable`, and `unavailable_reason`.
- Local cache for 006597 contains `source=akshare`, `updated_at=2026-05-19T05:07:11.758531+00:00`, and raw rows with `净值日期`, `单位净值`, `日增长率`; it does not expose cumulative NAV, adjusted NAV, total-return flag, dividend adjustment basis, or provider methodology.
- `fund_agent/fund/extractors/models.py` fixes `BondRiskEvidenceSchemaVersion` to `bond_risk_evidence.v1`; `BondRiskEvidenceAnchorRef.section_id` is non-null `str`; validation rejects empty `section_id` and says accepted / weak groups need at least one parseable annual-report anchor.
- `fund_agent/fund/extraction_snapshot.py` builds the `bond_risk_evidence` row from `_first_annual_report_anchor(...)`; `nav_data` snapshot has `anchor_present=false` and only note text like `source=nav_cache; cached=True; records=1802`.
- `fund_agent/fund/extraction_score.py` decides unsatisfied bond-risk groups from row-level `value_present`, `anchor_present`, `bond_risk_contract_status`, and four group-set fields; it does not validate per-group source kind, calculation method, period, or provenance.
- Latest 006597 snapshot shows `bond_risk_contract_status="partial"`, satisfied groups excluding `drawdown_stress`, `bond_risk_weak_groups=["drawdown_stress"]`, and `nav_data` traceability `0%`.
- Latest 006597 score emits `bond_risk_evidence_missing`, `baseline_blocking=true`, `missing_evidence_groups=["drawdown_stress"]`; latest quality gate projects this as `FQ2F/warn`.

## Findings

### DS-P1-未修复-[严重]-当前NAV来源不能证明total-return basis，计划不应进入解除blocker实现

- **Plan位置**: `Contract Decision`、`NAV-Derived Metric Method`、`Implementation Slices If Approved / Slice 1`、`Blocking Questions For Controller`、`Plan Conclusion`
- **问题类型**: open question 未收敛 / 契约缺失 / 不可直接实施
- **计划当前写法**: 计划先声明 `drawdown_stress` may accept NAV-derived quantitative evidence，并规划 NAV normalization、calculator、bond-risk extension、snapshot/score、quality gate 六个实现 slices；但又把 controller 是否接受 derived source、NAV source allowlist、当前 provider 不支持 total-return 时是否停止列为 blocking questions。
- **为什么有问题**: 这些不是实现细节，而是决定本 gate 是否能解除 006597 blocker 的前置事实。当前本地 provider 只证明可拿到 `单位净值走势`，无法证明总收益 / 累计 / 复权口径；用户 handoff 也明确如果 current provider only has ambiguous unit NAV / daily growth basis，则不应 implement unblocking。
- **直接证据**: `fund_agent/fund/data/nav_data.py` 固定 akshare indicator 为 `单位净值走势`；`NavDataResult` 不包含 `series_type`、`adjustment_basis`、`origin_source_name`、`cache_updated_at`；006597 cache sample 只有 `净值日期` / `单位净值` / `日增长率`。计划自身也承认 current cache row does not by itself establish dividend-adjusted / cumulative total-return series。
- **影响**: implementation agent 可能完成一整套 derived metric / model / score 改造后，才发现真实数据仍必须 fail-closed；更严重的是可能把 unadjusted unit NAV 或 ambiguous `日增长率` 复合结果当作投资者最大回撤，绕过当前正确保留的 `drawdown_stress` blocker。
- **建议改法和验证点**: 将当前 plan 改为 controller decision / blocked-with-decision：在现有 provider 无法证明 total-return / cumulative / adjusted basis 前，不进入解除 blocker 的实现。若 controller 仍想推进，应先批准一个独立 source capability evidence gate，只允许通过统一 `FundNavDataAdapter` 证明字段、来源、调整口径和缓存 metadata；验证必须包含 `单位净值` + `日增长率` present but no total-return proof => fail-closed，006597 仍输出 `missing_evidence_groups=["drawdown_stress"]`。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 严重

### DS-P2-未修复-[高]-derived anchor与`bond_risk_evidence.v1`年报锚点校验冲突，缺少版本/迁移策略

- **Plan位置**: `Required Contract Fields / Anchor format`、`Slice 3: Bond-Risk Contract Extension`
- **问题类型**: 契约缺失 / public contract change / 不可直接实施
- **计划当前写法**: 计划要求保留现有 `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>` anchor grammar，同时让 NAV-derived anchor 使用 `section_id=None`、`page_number=None`、`table_id=None`，并扩展 `BondRiskEvidenceAnchorRef` 添加 source/provenance 字段。
- **为什么有问题**: 当前 v1 模型把 group anchor 明确定义为年报锚点引用；validator 对所有 anchor 统一要求非空 `section_id` 和可解析 group anchor id。直接把 `section_id=None` 塞进 v1 会验证失败；为了通过而伪造年报章节会破坏证据语义。
- **直接证据**: `BondRiskEvidenceSchemaVersion = Literal["bond_risk_evidence.v1"]`；`BondRiskEvidenceAnchorRef.section_id: str`；`_validate_bond_risk_anchor_refs()` 在 `not anchor.section_id` 时 raise；`_validate_bond_risk_group_anchor_refs()` 错误信息要求 accepted / weak 组有可解析年报锚点。
- **影响**: 计划交给 implementation 后，要么导致模型校验失败，要么诱导实现放宽 v1 validator，造成旧 annual-report anchor、derived anchor、external API anchor 混在同一个 public contract 内不可审计。
- **建议改法和验证点**: 计划必须先明确 schema/version strategy：新增 `bond_risk_evidence.v2`，或明确 v1 backward-compatible extension 的字段、parser、serializer、old-row fail-closed、snapshot/score 兼容规则。derived anchor 校验必须 source-kind-aware：annual report 仍要求 `section_id`；public NAV / derived anchor 必须要求 `source_kind`、`source_name`、`provenance_ref`、period/window/observation metadata。测试必须覆盖 annual anchor missing section fail、derived anchor accepted、derived anchor missing provenance fail、old v1 rows behavior。
- **修复风险（低/中/高）**: 高
- **严重程度（低/中/高/严重）**: 高

### DS-P3-未修复-[高]-snapshot/score只信任行级group set，无法机器校验`drawdown_stress` derived provenance

- **Plan位置**: `Snapshot / Score / Quality Gate Decision`、`Slice 5: Snapshot / Score Traceability`
- **问题类型**: 契约缺失 / 测试缺口 / 过度耦合
- **计划当前写法**: 计划说 score 可在 snapshot row declares group satisfied 且有 traceable annual or derived provenance 时接受 `drawdown_stress`，并把 snapshot schema 写成 “Either add generic anchor_source_kind fields, or add bond-risk-specific fields such as ...”。
- **为什么有问题**: 当前 score 并不读取 group record、metric、calculation method、source kind 或 provenance；它只读 row-level `anchor_present` 和 group sets。计划也没有强制 per-group projection，因此无法证明 `drawdown_stress` 的 satisfied 状态来自 contract-valid NAV metric，而不是一个带任意年报 anchor 的 row-level group-set 改写。
- **直接证据**: `_build_bond_risk_evidence_record()` 使用 `_first_annual_report_anchor(extracted_field.anchors)` 产生整行 `anchor_present`；snapshot 只输出 `bond_risk_satisfied_groups` / `missing` / `weak` / `ambiguous`；`_bond_risk_unsatisfied_groups()` 只检查 `value_present`、`anchor_present`、`bond_risk_contract_status` 和四个 group-set 字段。
- **影响**: blocker removal 可能退化成 “snapshot 声称 satisfied 即通过”，而不是 score 能独立验证 derived provenance。这样会把 fail-closed 责任推给上游构造者，违背当前 scoring gate 的机器可审计意图。
- **建议改法和验证点**: 计划应定义必需的 per-group machine-checkable schema，而不是 optional choice。例如为每组输出 `source_kind`、`anchor_ids`、`calculation_method`、`provenance_status`、`period_start/end`、`observation_count`、`adjustment_basis`、`data_quality_status`。score 对 `drawdown_stress` 必须校验 group-level provenance accepted、anchor exists、fund/year/window match、weak/ambiguous absent。测试必须覆盖 row-level `anchor_present=true` 但 drawdown provenance missing/malformed => blocker remains。
- **修复风险（低/中/高）**: 高
- **严重程度（低/中/高/严重）**: 高

### DS-P4-未修复-[中]-计划把source capability、contract migration、metric calculation、score acceptance绑成一个实现序列

- **Plan位置**: `Implementation Slices If Approved`、`Tests And Validation Matrix`、`Stop Conditions`
- **问题类型**: 切片过粗 / 非最优方案 / residual risk 未收敛
- **计划当前写法**: 六个 slices 从 NAV normalization 一路推进到 calculator、bond-risk model、DataExtractor composition、snapshot/score、quality gate real validation；Slice 1 末尾才说如果没有可靠 total-return source 则 stop。
- **为什么有问题**: 该 work unit 当前的第一性问题是 “能否证明 NAV source basis”。在这个事实未成立前，后续 schema extension、calculator、score acceptance 都是条件性设计，不应作为同一个 implementation handoff。把这些绑定在一起会让 implementation agent 过早修改 public contract 与 score semantics。
- **直接证据**: `docs/implementation-control.md` next entry point 允许定义 separate contract，但要求 do not claim blocker解除 without quantitative evidence or reviewed contract change；用户 handoff进一步明确 no extractor web scraping/cache reads、current ambiguous basis should not implement unblocking。计划的 `Blocking Questions For Controller` 仍保留三个会改变 scope / architecture / contract 的问题。
- **影响**: 即使实现严格 fail-closed，也会在没有 unblock capability 的情况下扩大模型和 snapshot/score变更面；review 会被迫同时审 source proof、schema migration、calculator correctness、score semantics，增加返工和误放行风险。
- **建议改法和验证点**: 将计划拆成先决 gate：`NAV source capability / adjusted basis decision`。该 gate 只产出证据和 fail-closed typed source result，不改 `bond_risk_evidence` satisfaction / score acceptance。只有 controller 接受 source capability 后，再写第二个 implementation-ready plan 处理 schema/version、derived anchors、per-group snapshot/score 和 real 006597 validation。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

## Relationship To MiMo Review

I independently confirm MiMo's material FAIL findings. I refine the conclusion slightly stronger on source basis: based on current local code and cache evidence, the gate should not proceed to implementation for unblocking unless controller first supplies or approves a separate source-capability decision proving total-return / cumulative / adjusted NAV.

## Open Questions

1. Controller 是否要把本 gate转换为 `blocked-with-decision/no implementation`，保留 006597 `drawdown_stress` blocker，直到有 total-return/cumulative/adjusted NAV source proof？
2. 如果未来接受 NAV-derived evidence，schema 是升级为 `bond_risk_evidence.v2`，还是在 v1 中做 source-kind-aware extension？两者的 old-row fail-closed 策略是什么？
3. Snapshot 是否应直接暴露 serialized per-group evidence records，还是新增最小 per-group provenance projection 字段？score 的权威输入必须先裁决。

## Residual Risks

- NAV-derived drawdown is acceptable in principle only if source basis and provenance are explicit；当前 006597 provider evidence 不满足该条件。
- Legacy `nav_cache` rows may remain valid for raw `nav_data` availability but should be ineligible for risk evidence until refreshed or migrated with explicit provenance.
- Keeping schema name `bond_risk_evidence.v1` while adding derived/external anchors risks downstream tooling treating annual-report and derived provenance as interchangeable.

Suggested tracking destination: same work unit controller judgment. Recommended disposition is blocked-with-decision or plan fix / re-review before any implementation.

## Controller Decision Placeholder

| Finding | Suggested disposition | Controller decision |
|---|---|---|
| DS-P1 | accepted | TBD |
| DS-P2 | accepted | TBD |
| DS-P3 | accepted | TBD |
| DS-P4 | accepted | TBD |

## Final Conclusion

FAIL.

The plan has the right fail-closed intent and correctly refuses to upgrade qualitative `控制回撤` text. It is not implementation-ready because the current NAV source does not prove total-return / cumulative / adjusted basis, the v1 anchor contract cannot yet represent derived anchors, and snapshot/score cannot machine-check group-level derived provenance. This gate should be converted to controller decision / blocked-with-decision, or narrowed to a source-capability proof gate before any contract-unblocking implementation.
