# NAV Source Capability / Adjusted Basis Plan Review - GLM

Date: 2026-05-28

Reviewer: GLM

Role: adversarial plan review worker, not controller

Gate: `NAV source capability / adjusted basis evidence gate`

Gate classification: `standard`

Reviewed targets:

- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-20260528.md`
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-evidence-20260528.md`

Conclusion: **PASS_WITH_FINDINGS**

## Worker Self-Check - Start

- Status: pass.
- Current role is specialist review worker only. I did not start `$gateflow` / `/gateflow`, did not restart from plan, and did not enter implementation.
- Source of truth read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, prior drawdown contract controller judgment, DS plan review, latest `006597 / 2024` snapshot / score / quality-gate artifacts, and current NAV boundary code (`nav_data.py`, `data_extractor.py`, `extraction_snapshot.py`).
- Scope boundary: write one durable review artifact only. No production code, tests, score, quality gate, schema, golden fixture, release / PR state, Host / Agent / dayu, QDII / FOF / `110020`, or blocker removal.
- Completion signal: this artifact with explicit `conclusion: PASS / PASS_WITH_FINDINGS / FAIL`, gateflow-format findings, and suggested controller disposition.

## Assumptions Tested

1. The plan correctly proves that the current adapter cannot supply adjusted / cumulative / total-return basis.
2. The plan's `blocked_pending_source_adapter` conclusion is the minimum safe outcome, not premature.
3. The evidence artifact's direct SQLite read does not violate the AGENTS.md unified boundary rule.
4. The proposed future fields and failure classification are sufficient, not over-designed, and do not still lack identity/provenance coverage.
5. The plan correctly preserves `drawdown_stress` blocker status, FQ0-FQ6, score/quality/golden semantics.

## Direct Evidence Verification

### Current Adapter Cannot Prove Adjusted Basis

Verified through independent code review:

- `fund_agent/fund/data/nav_data.py:72` hardcodes `ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")`. No alternate indicator or method exists in the current adapter.
- `NavDataResult` (line 99-117) exposes only `fund_code`, `records`, `source`, `cached`, `unavailable`, `unavailable_reason`. No `nav_type`, `adjustment_basis`, `series_type`, `origin_source_name`, `retrieved_at`, or provider methodology.
- `_load_cached_sync()` (line 285-306) selects only `payload_json` from SQLite, discarding stored `source` and `updated_at`.
- `_save_cached_sync()` (line 308-343) stores `source="akshare"` and `updated_at` but the cache hit path (line 251-256) returns `source="nav_cache"` without origin metadata.

Verified through latest 006597 artifacts:

- Snapshot record 17: `nav_data` has `value_present=true`, `anchor_present=false`, `note="source=nav_cache; cached=True; records=1802"`.
- Bond risk evidence record 15: `bond_risk_contract_status="partial"`, `bond_risk_weak_groups=["drawdown_stress"]`, all six other groups satisfied.
- Score: `nav_data` coverage `1.0` but traceability `0.0`, status `fail`.
- Quality gate: `warn` with FQ2F warning for bond risk evidence.

**Assessment**: The plan's core capability assessment is factually correct. The current adapter proves raw unit NAV availability for 006597 but cannot prove adjusted / cumulative / total-return basis.

### Blocked Pending Source Adapter Is Correct Minimum Conclusion

The plan recommends `capability_decision_recommendation = blocked_pending_source_adapter`. This is the correct fail-closed conclusion because:

1. Current provider returns `单位净值走势` (unit NAV trend) only.
2. `日增长率` is ambiguous: the adapter does not document whether this rate is dividend-adjusted, total-return-equivalent, or raw daily change.
3. Using raw `单位净值` for max drawdown would compute drawdown on unit NAV rather than investor-return basis, potentially understating actual investor loss experience.
4. `docs/implementation-control.md` explicitly requires "do not claim blocker解除 without a proven adjusted NAV source and reviewed derived-evidence contract".

The plan correctly does not authorize implementation, schema changes, score changes, or blocker removal.

## Findings

### GLM-F1-[低]-evidence 直接 SQLite read 不违反 AGENTS.md 统一文档边界，但应显式标记为调查用途

- **Plan位置**: evidence artifact "NAV SQLite Read-Only Metadata" 节
- **问题类型**: 边界合规 / 调查证据合规
- **Evidence 当前写法**: evidence worker 使用 `sqlite3.connect(f"file:{path}?mode=ro", uri=True)` 直接读取 NAV 缓存的 `source` 和 `updated_at` 字段，以证明 cache 存储了 metadata 但 adapter result 在 cache hit 时丢弃了这些信息。
- **为什么是低风险**:
  - AGENTS.md 的统一边界规则专门针对"基金文档的存取"和"生产年报 PDF 访问必须经过 `FundDocumentRepository`"。NAV 缓存是外部市场数据适配器 (`FundNavDataAdapter`) 自身管理的缓存，不属于文档仓库层。
  - 该读取是只读调查 (`?mode=ro`)，发生在 capability evidence gate 的证据收集阶段，不是生产代码路径。
  - 读取的目的是证明公共接口的信息损失——这本身就是本 gate 的核心证据之一。
- **为什么仍需标记**:
  - AGENTS.md 更广泛的原则是"禁止直接操作文件系统"和"证据必须可溯源"。直接读取适配器内部存储可能被视为绕过公共接口。
  - 如果未来 production code 复制此模式直接读缓存，则违反统一边界精神。
- **直接证据**: `AGENTS.md` "对基金文档的存取，都应该只通过统一的文档仓库接口" 明确限定"基金文档"；`FundDocumentRepository` 规则限定"生产年报 PDF 访问"；NAV 数据是 `FundNavDataAdapter` 管理的外部数据缓存，不在这两条规则覆盖范围内。
- **建议改法**: evidence artifact 已在 "Allowed smoke and cache metadata check" 标题下限定用途。建议 controller 在 judgment 中确认：(a) 本次 SQLite 只读调查不违反统一文档边界；(b) 未来 adapter 增强必须通过公共接口暴露 cache metadata，不应依赖直接 SQLite 访问作为 production 路径。
- **Suggested disposition**: `accepted_as_investigation_only`; controller judgment 明确标注生产代码不得复制此模式。
- **修复风险**: 低
- **严重程度**: 低

### GLM-F2-[低]-future fields 表缺少 dividend_adjustment_status 显式字段声明

- **Plan位置**: plan artifact "Current Provider And Fields" 与 "Provenance And Anchor Fields To Require" 两节
- **问题类型**: 字段覆盖完整性 / 信息遗漏
- **Plan 当前写法**: "Current Provider And Fields" 列出 `NavDataResult` 不暴露 `dividend_adjustment_status`；但 "Provenance And Anchor Fields To Require" 的 typed result 字段列表中没有包含 `dividend_adjustment_status`。
- **为什么需要注意**: `adjustment_basis` (cumulative / provider-adjusted / total-return / unadjusted / unknown) 可能隐含了分红调整状态，但两者不是完全等价的概念：`adjustment_basis` 描述的是 NAV 序列的计算口径，`dividend_adjustment_status` 描述的是分红是否被纳入或如何被纳入。例如一个 `cumulative` 系列可能包含分红再投资，但具体再投资方法需要单独记录。
- **直接证据**: Plan 自身在 "Current Provider And Fields" 中明确将 `dividend_adjustment_status` 列为缺失字段，但在 future requirement 中遗漏。
- **建议改法**: 未来 gate 在定义 typed NAV source result 时，应明确 `dividend_adjustment_status` 是被 `adjustment_basis` 吸收（例如当 `adjustment_basis=total_return_nav` 时隐含分红已调整），还是需要独立字段。这不是本 gate 的 blocking 问题，因为本 gate 只产出 blocked 结论，但应在 future gate 入口条件中记录。
- **Suggested disposition**: `noted_for_future_gate`; future gate 入口条件补充此字段决策点。
- **修复风险**: 低
- **严重程度**: 低

### GLM-F3-[信息]-failure classification 与 AGENTS.md 年报来源 fallback 分类对齐良好

- **Plan位置**: plan artifact "Failure Classification" 节
- **问题类型**: 设计一致性确认
- **Assessment**: Plan 提出的 7 种 failure classification (`not_found`, `source_unavailable`, `schema_drift`, `identity_mismatch`, `adjustment_basis_unknown`, `insufficient_history`, `integrity_error`) 与 AGENTS.md 年报来源 fallback 的 5 种分类 (`not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`) 在概念和语义上对齐。新增的 `adjustment_basis_unknown` 和 `insufficient_history` 是 NAV/risk-evidence 专用的合理扩展，不与已有分类冲突。

### GLM-F4-[信息]-gate slicing 与 DS-P4 建议一致

- **Plan位置**: plan artifact "Future Gate Slicing" 节
- **问题类型**: 架构一致性确认
- **Assessment**: Plan 将未来工作拆分为三个窄 gate (NAV Source Repository/Adapter Capability → Derived Drawdown Evidence Contract Schema → Risk Metric Calculator And 006597 Validation)，与 DS review 的 DS-P4 finding 建议完全一致。先决 source capability gate 不改 `bond_risk_evidence` satisfaction / score acceptance 的约束正确反映了 blocked-with-decision 的 fail-closed 语义。

## Preservation Verification

### drawdown_stress Blocker Status

- Plan conclusion is `blocked_pending_source_adapter`.
- Plan explicitly states: "If adjusted basis cannot be proven, derived max drawdown / volatility must not satisfy `drawdown_stress`."
- No implementation, schema, score, quality gate, golden fixture, or blocker removal is authorized.
- **Verified**: blocker correctly preserved.

### FQ0-FQ6 Semantics

- Plan does not propose any changes to quality gate rules.
- Evidence artifact confirms latest quality gate status is `warn` with FQ2F warning.
- **Verified**: FQ0-FQ6 unchanged.

### Score / Quality / Golden

- Plan does not propose any changes to score acceptance, quality gate semantics, or golden fixture status.
- Latest score keeps `bond_risk_evidence_missing.baseline_blocking=true` with `missing_evidence_groups=["drawdown_stress"]`.
- **Verified**: score / quality / golden unchanged.

## Residual Risks

- Legacy `nav_cache` remains useful for raw `nav_data` availability but is ineligible for risk evidence until basis and provenance are explicit. Plan correctly identifies this.
- Future provider may expose cumulative or adjusted NAV, but this must be proven through code and tests before score or quality semantics change. Plan correctly identifies this.
- Current snapshot/score projection cannot machine-check per-group NAV-derived provenance. This belongs to a later schema/projection gate after source capability passes. Plan correctly defers this to Gate 2.
- `006597 / 2024` remains blocked for baseline/golden purposes by `drawdown_stress` until adjusted basis and derived evidence contract are both accepted. Plan correctly preserves this.

## Open Questions For Controller

1. Controller 是否确认 GLM-F1 的 SQLite 只读调查不违反 AGENTS.md 统一文档边界，并明确生产代码不得复制此模式？
2. Future gate 入口是否需要补充 `dividend_adjustment_status` 字段决策点？

## Finding Summary

| Finding | Severity | Suggested Disposition | Blocking |
|---|---|---|---|
| GLM-F1: evidence SQLite 直接读取边界合规 | 低 | `accepted_as_investigation_only`; controller 标注生产不得复制 | 否 |
| GLM-F2: future fields 缺少 `dividend_adjustment_status` | 低 | `noted_for_future_gate`; future gate 补充决策点 | 否 |
| GLM-F3: failure classification 与 AGENTS.md 对齐 | 信息 | 确认 | 否 |
| GLM-F4: gate slicing 与 DS-P4 一致 | 信息 | 确认 | 否 |

## Final Conclusion

**PASS_WITH_FINDINGS**

The plan and evidence are well-constructed and factually correct. The core capability assessment — that the current adapter proves raw unit NAV availability but cannot prove adjusted / cumulative / total-return basis — is independently verified through code review and artifact inspection. The `blocked_pending_source_adapter` conclusion is the correct minimum safe outcome. The proposed future gate slicing is sound and consistent with prior DS review findings.

Two low-severity findings are noted but do not block acceptance: (1) the evidence SQLite direct read is acceptable as investigation-only evidence but should not be replicated in production code; (2) the future fields list should address `dividend_adjustment_status` as a decision point for the next gate.

The plan correctly preserves all blocker status, score/quality/golden semantics, FQ0-FQ6 rules, and does not authorize implementation or blocker removal.

Suggested controller disposition: accept plan and evidence with noted findings; proceed to next gate (`NAV repository/source adapter adjusted-basis contract gate`) only when controller is ready to open a narrow Fund-layer data capability gate.

## Worker Self-Check - Completion

- Status: pass.
- I produced the requested durable review artifact only.
- I did not modify production code, tests, score, quality gate, schema, golden fixture, design/control truth, release / PR state, or unrelated untracked files.
- I did not commit, push, create PR, merge, or close out the gate.
- Review conclusion is PASS_WITH_FINDINGS: core assessment correct, two low-severity findings noted, blocker preserved.
