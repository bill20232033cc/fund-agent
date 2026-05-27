# Bond Risk Evidence Extractor / Anchor Hardening — Plan Review

> Date: 2026-05-27
> Reviewer: AgentDS
> Gate: plan review for `bond risk evidence extractor / anchor hardening design gate`
> Reviewed target: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
> Review type: evidence-based adversarial plan review
> Verdict: **PASS_WITH_FINDINGS** — 3 findings, none blocking

## Worker Self-Check

### Before Start

- Self-check: pass
- Role confirmed: review worker only, not controller, not implementer.
- Current gate confirmed: plan review for bond risk evidence extractor / anchor hardening design gate.
- External-state boundary confirmed: no workflow command, no skill, no implementation, no review artifact outside this path, no staging, no commit, no PR, no golden promotion.
- Dirty scope: pre-existing untracked files only; this review writes only the allowed artifact path.
- Source evidence read: AGENTS.md, docs/design.md, docs/implementation-control.md, docs/reviews/repo-review-20260527-225303.md, docs/reviews/release-maintenance-bond-positive-risk-evidence-20260527.md, docs/reviews/release-maintenance-bond-positive-risk-evidence-controller-judgment-20260527.md, fund_agent/fund/extraction_score.py, fund_agent/fund/extraction_snapshot.py, fund_agent/fund/data_extractor.py, fund_agent/fund/extractors/models.py, fund_agent/fund/quality_gate.py (relevant sections).

### Before Completion

- Self-check: pass
- Findings are evidence-based and reference specific plan lines, code lines, and source documents.
- No blocking findings; 3 non-blocking findings with residual risk ownership.
- Review does not recommend plan rejection, scope expansion, or gate reclassification.

---

## Executive Summary

The plan correctly identifies root cause, respects all architecture boundaries, preserves FQ0-FQ6 semantics, and handles the seven evidence groups with appropriate evidence-strength distinctions. The implementation slice ordering is logical, and stop conditions are explicit and safe.

Three findings below require controller attention before implementation:
1. `bond_risk_evidence` field priority in scoring is unaddressed (UNMAPPED default may silently exclude it from coverage/traceability scoring).
2. Extractor fund-type gating boundary is split between intent and specification — non-bond funds may produce unnecessary extraction work.
3. `required_evidence_groups` in plan's `ScoreApplicabilityIssue` is always all seven groups, but `missing_evidence_groups` is dynamic; this interaction is correct but the plan should make the invariant explicit.

---

## Findings

### 01-未修复-Medium-bond_risk_evidence 字段优先级未注册

**位置**: plan Slice 4, `SNAPSHOT_FIELD_ORDER` 扩展；`extraction_score.py:41-58` (`FIELD_PRIORITY_BY_NAME`)

**证据**:

- Plan line 541 要求在 `SNAPSHOT_FIELD_ORDER` 中添加 `("risk", "bond_risk_evidence")`。
- 当前 `FIELD_PRIORITY_BY_NAME` (extraction_score.py:41-58) 定义了所有 16 个 snapshot 字段的 P0/P1/P2 优先级。未注册字段默认归入 `UNKNOWN_FIELD_PRIORITY` (`"UNMAPPED"`)。
- Plan line 392 明确 `comparable_values={}` for v1，Line 542 要求 `_comparable_values_for_field` 保持 `bond_risk_evidence` non-comparable——这覆盖了 correctness 分母，但未覆盖 coverage/traceability 分母。
- Plan 未说明 `bond_risk_evidence` 应分配 P0、P1、P2 还是有意保持 UNMAPPED。
- 若保持 UNMAPPED，`fund_quality_records` 中该字段的 coverage/traceability 不会进入任何优先级分组，`score.md` 的 field breakdown 中会缺失该字段的质量信息。
- 若分配 P1（与 `holdings_snapshot` 同级），coverage/traceability 阈值会正常应用，traceability < 90% 会触发 P1 watch。对 `006597` 而言七个组全部满足时 coverage/traceability 应为 100%，不会触发误报。

**风险**: plan 的 validation matrix line 683-684 期望 coverage 统计正确，但未注册优先级的字段在 score 中不可观测。实现 worker 可能在不知情时留下盲区。

**建议**: 在 Slice 4 plan 中显式声明 `bond_risk_evidence` 的 FIELD_PRIORITY。建议 P1（与 `holdings_snapshot` 同级），但覆盖率/traceability 对 `bond_risk_evidence` 的实际意义需要定义：`value_present` = `contract_status != "missing"`，`anchor_present` = 存在至少一个 group-level anchor。

### 02-未修复-Low-非债券基金的 bond_risk_evidence 抽取边界未明确

**位置**: plan Slice 2 extractor 与 Slice 3 bundle 集成之间

**证据**:

- Plan line 479 定义 extractor 函数签名为 `extract_bond_risk_evidence(report: ParsedAnnualReport) -> ExtractedField[BondRiskEvidenceValue]`，未提及 fund type gating。
- Plan line 514 要求 `FundDataExtractor.extract(...)` 调用 `extract_bond_risk_evidence(report)`，该调用在 `extract()` 内部对所有基金执行。
- `FundDataExtractor.extract()` (data_extractor.py:153-211) 当前对所有基金执行同一组 extractor 调用，只在 `_tracking_error_for_fund_type` 处按基金类型裁剪。
- 若 `extract_bond_risk_evidence` 对非 `bond_fund` 执行，它仍需遍历 `ParsedAnnualReport` 的所有 section/table 查找七组证据，可能发现无关文本并误判为 weak/ambiguous，或正确返回全 missing。
- Plan Slice 4 line 565 测试用例提到 "Non-bond funds may produce missing/not-applicable field"，暗示非债券基金也会调用 extractor。

**风险**: 低。最坏情况是非债券基金的额外解析开销和潜在误判。但 plan 的 score Slice 5 line 595 有 fail-closed gating（非 `bond_fund` 不消费该字段），实际安全网已存在。

**建议**: 在 Slice 2 extractor 入口添加 fund type early exit：若 `report.key` 或 report section 中的基金类别不是债券基金，立即返回 `extraction_mode="missing"` 的 `ExtractedField`，避免不必要的全量 section 遍历。或者在 Slice 3 集成点明确是否在 `FundDataExtractor.extract()` 中按 `classified_fund_type` 条件调用。

### 03-未修复-Low-`required_evidence_groups` 不变性与 `missing_evidence_groups` 动态性的交互应显式声明

**位置**: plan Slice 5, extraction_score.py:1778-1779 (current) 与 plan line 407-409

**证据**:

- 当前 `_bond_risk_evidence_missing_issue` (extraction_score.py:1753, 1778-1779) 将 `required_evidence_groups` 和 `missing_evidence_groups` 都设为全部七组。
- Plan line 407-409: "If some groups remain missing/weak/ambiguous, emit `bond_risk_evidence_missing` with only those unsatisfied groups in `missing_evidence_groups`."
- Plan line 409: "`required_evidence_groups` remains all seven groups."
- 这个设计是正确的（required 始终是全部七组，missing 动态反映当前缺口），但 plan 没有显式声明 `required_evidence_groups` 是契约级不变量，而 `missing_evidence_groups` 是实例级动态值。未来 reader 可能误以为两组应该同步变化。

**风险**: 低。当前代码结构和 plan 描述均已暗示这个不变性。显式声明可防止未来维护者误将 `required_evidence_groups` 也缩减为仅未满足组。

**建议**: 在 Slice 5 invariants 中添加一条：`required_evidence_groups` 始终等于 `BOND_RISK_EVIDENCE_GROUPS` 的全部 group_id，不与 `missing_evidence_groups` 联动缩减。

---

## Residual Risks & Test Gaps

以下为 plan 已识别或 plan review 新发现的 residual risks，不构成 blocking findings：

| # | Risk | Owner | Mitigation |
|---|------|-------|-----------|
| R1 | 当前 parser 可能无法暴露足够精确的 repo/leverage 表格行定位 | Slice 2 stop condition (plan line 501-502) | Plan 已设置安全默认：不满足时保持 weak，不升级为 pass |
| R2 | 当前年报不含 max drawdown / volatility 定量指标 | Slice 5 行为 (plan line 300-305) | Plan 已确认 drawdown 定性文本只能保持 weak |
| R3 | Snapshot schema 扩展（explicit dataclass fields）是 public contract 变更 | Slice 4 stop condition (plan line 567-569) | Plan 设置 stop 回到 controller；note-only fallback 存在但格式未定义 |
| R4 | 真实 `006597` multi-share-class redemption 选择可能仍然 ambiguous | Slice 6 stop condition (plan line 641) | Plan 要求残差诚实报告，不掩盖 |
| R5 | `bond_risk_evidence` 字段加入 snapshot 会改变 field count，质量 gate 的 FQ4 缺失率计算可能受影响 | Plan line 734 已识别 | Plan 要求 test 断言 FQ0-FQ6 期望效果不变，是充分的缓解措施 |
| R6 | `BondRiskEvidenceAnchorRef` 不包含 `document_year` 字段；`document_year` 从 anchor_id format 可派生但不是显式字段 | Plan line 164-170 vs 208 | Low risk; anchor_id format `bond-risk:<fund_code>:<report_year>:...` 已包含年份 |
| R7 | 测试需要 synthetic `ParsedAnnualReport` fixture；当前 fixture 基础设施是否支持构造 bond-fund-specific section/table 待验证 | Slice 2 tests | 实现 worker 需要先验证现有 test fixtures 能否支持，否则需要在 Slice 2 内建测试固件 |

## Cross-Reference Checklist

按照 AGENTS.md 和 docs/design.md §12 的 Plan Review 设计边界检查：

| 检查项 | 状态 |
|--------|------|
| 不违反 §1.3 非目标 | PASS — plan 明确排除 golden promotion, Host/Agent, QDII/FOF, renderer rewrite, 阈值降低 |
| 保持四层边界 `UI -> Service -> Host -> Agent` | PASS — 所有修改在 `fund_agent/fund/` (Agent 层基金能力)；不创建 Host/Agent 包 |
| 生产年报访问仅通过 `FundDocumentRepository` / `FundDataExtractor` | PASS — extractor 接收 `ParsedAnnualReport`，不直接访问 PDF/cache/source |
| 不误拼接 Host/tool loop/LLM/Evidence Confirm/extra_payload | PASS — 所有参数显式声明为 typed dataclass；无 `extra_payload` |
| 遵守工程基线 | PASS — Python >=3.11, setuptools, 显式依赖，无新外部依赖 |
| 测试覆盖率策略 | PASS — plan 要求 CI global `--cov-fail-under=50`，新增模块目标 >=80% |
| License/repo hygiene | N/A — 不涉及 pyproject.toml 或 LICENSE 变更 |
| 不重新引入六层或三层口径 | PASS — 所有引用使用四层 `UI -> Service -> Host -> Agent` |
| Success signal 可验证且不激励错误接受 | PASS — weak evidence 不能 pass; 七个组的满足规则有明确证据强度要求 |

## Source-of-Truth Alignment

| Source | Plan alignment |
|--------|---------------|
| `AGENTS.md` 硬约束 | PASS — 中文响应，第一性原理，同源证据，`FundDocumentRepository` 边界，显式参数，基金类型优先，fail-closed fallback |
| `docs/design.md` 架构边界 | PASS — 修改在 Agent 层 `fund_agent/fund` 内；不改变确定性执行链路 |
| `docs/implementation-control.md` 当前 gate | PASS — 正确引用 Startup Packet current gate = `bond positive-risk evidence accepted locally`，next entry point 匹配 |
| `docs/reviews/repo-review-20260527-225303.md` F1 | PASS — plan 直接解决 repo review 的 F1 high finding (bond extractor/anchor 缺失) |
| Controller judgment accepted constraints | PASS — 全部五条 controller constraint 均已体现在 plan 中 |

## Evidence Group Contract Review

逐组验证 plan 的 satisfaction rule 是否与已接受证据一致：

| Group | Plan rule | Controller constraint alignment | Verdict |
|-------|-----------|-------------------------------|---------|
| `duration_rate_risk` | 定性直接策略文本 → accepted | 无冲突 | PASS |
| `credit_risk` | 评级分布表 → quantitative_direct；定性策略单独 → weak | 无冲突 | PASS |
| `leverage_liquidity` | 策略文本单独 → weak；必须有实际 repo/leverage/liquidity 数据锚点 | 对齐 controller F2 (DS), F1 (MiMo) | PASS |
| `asset_allocation_holdings_mix` | 表格锚点必需；quantitative_direct | 无冲突 | PASS |
| `drawdown_stress` | 定性 control intent → weak；只有 max drawdown/volatility → accepted | 对齐 controller F1 (DS), F2 (MiMo) | PASS |
| `redemption_share_pressure` | 需要 share class 明确选择；ambiguous → 不满足 | 对齐 controller F3 (MiMo) | PASS |
| `convertible_bond_equity_exposure` | 显式 absence → accepted_absence；quantitative_absence | 无冲突 | PASS |

---

## Conclusion

PASS_WITH_FINDINGS. Plan is code-generation-ready after controller acknowledges or accepts the three non-blocking findings above. No blocking issues identified. Implementation may proceed when controller approves.
