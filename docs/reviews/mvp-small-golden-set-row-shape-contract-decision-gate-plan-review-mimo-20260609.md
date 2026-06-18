# Plan Review: Row-shape Contract Decision Gate Plan

## Reviewed Target

`docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260609.md`

## Scope

Adversarial review of the row-shape contract decision gate plan for retained `manager`, `risk`, `006597` bond top holding, and `110020` target ETF holding residuals. Focus: heavy classification justification, additive contract sequencing, wrong-surface avoidance, no-goal completeness, exact/numeric correctness deferral, and implementation slice readiness.

## Assumptions Tested

1. Heavy classification is required and justified.
2. Additive contracts must precede tests and extractor fixes for all four residuals.
3. Current extractor surfaces (`fund_manager`, `style_positioning`, `bond_risk_evidence`, equity `top_holdings`) are correctly identified as semantically insufficient.
4. Non-goals cover all prohibited actions per AGENTS.md and control truth.
5. Exact/numeric correctness is not prematurely accepted.
6. Slices, unlock rules, stop conditions, residual owners, and next entry are code-generation-ready.

## Source Evidence Read

- `AGENTS.md`: Gate classification rules (lines 52-57), hard constraints (lines 68-81), module boundaries (lines 89-139).
- `docs/current-startup-packet.md` §2: Current mainline, next entry point, current gate status.
- `docs/implementation-control.md` top: Current gate closeout (`row-field correctness test extension gate` accepted locally), next entry point.
- `docs/design.md`: Slice E, FundDocumentRepository, extractor/source/golden boundaries (rg snippets).
- `docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-controller-judgment-20260609.md`: Prior accepted equity-like holdings gate.
- `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-controller-judgment-20260609.md`: Prior gap decision.
- `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`: Retained excerpt oracle shapes for all five rows.
- `tests/fund/test_small_golden_set_extractor_correctness.py`: Current xfail residuals and test structure.
- `fund_agent/fund/extractors/profile.py`: `fund_manager` scalar, `style_positioning` surface.
- `fund_agent/fund/extractors/holdings_share_change.py`: `top_holdings` equity-only surface.
- `fund_agent/fund/extractors/bond_risk_evidence.py`: Chapter 6 seven-group evidence contract.
- `fund_agent/fund/extractors/manager_ownership.py`: Strategy/turnover/holding surface, no identity/tenure.

---

## Findings

### 01-未修复-低-risk 特征契约未显式覆盖多章节锚点来源

- **位置**: Contract Decisions By Residual, `risk` 行
- **问题类型**: 契约欠规格
- **当前写法**: `risk` 契约路由描述 anchor 为 `§2.2` 和 sometimes `§4.4.1`；Recommended contract route 说 "anchors, and source sections"。
- **反例/失败场景**: 实施 agent 在 Slice D 实现 risk 特征抽取时，只从 `§2.2` 抽取，遗漏 `§4.4.1` 的特殊风险/控制条款（如 006597 的 "操作中强调信用风险和流动性风险控制"）。测试可能通过（因为 `§2.2` 文本匹配），但契约未完整覆盖 retained oracle。
- **为什么有问题**: retained excerpt JSON 明确记录 `006597` 的 `risk.anchor = PDF p5 §2.2 and p21 §4.4.1`。契约描述 "sometimes `§4.4.1`" 过于模糊，实施 agent 可能将其视为可选。
- **直接证据**: retained excerpt JSON `006597` row: `risk.anchor = "PDF p5 §2.2 and p21 §4.4.1"`; plan Contract Decisions table risk 行 anchor 描述。
- **影响**: 实施 agent 生成不完整的 risk 特征契约实现；测试可能因只覆盖 §2.2 而通过，但遗漏 §4.4.1 特殊风险条款。
- **建议改法和验证点**: 在 risk 契约路由中显式列出 per-fund anchor sections：对 `006597` 必须同时覆盖 `§2.2` 和 `§4.4.1`；其余四只基金只需 `§2.2`。Slice D 实现应保留所有 retained anchor sections 作为 source sections 输出。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 02-未修复-低-经理角色字段可能被规范化丢失状态修饰语

- **位置**: Slice C: Manager Additive Extractor Contract, Required invariants 第 3 条
- **问题类型**: 契约欠规格
- **当前写法**: "`role` is preserved as disclosed text and not normalized into active-only status unless explicitly reviewed."
- **反例/失败场景**: 实施 agent 将 "基金经理（已离任）" 规范化为 "基金经理"，丢失离任状态信息。004194 的 retained oracle 有两位经理，其中王平的 role 明确标注 "基金经理（已离任）"。如果 role 被规范化，测试 assertion 可能通过（因为只检查 name 和 start_date），但语义信息丢失。
- **为什么有问题**: retained excerpt JSON 明确记录 `004194` manager.expected[1].role = "基金经理（已离任）"。plan 的 invariant 说 "not normalized into active-only status"，但未明确 role 值中包含的状态修饰语（如 "（已离任）"）必须原样保留。
- **直接证据**: retained excerpt JSON `004194` row: `manager.expected[1] = {"name": "王平", "role": "基金经理（已离任）", "start_date": "2017-03-03", "end_date": "2024-12-31"}`。
- **影响**: 实施 agent 可能规范化 role 字段，导致离任经理的语义信息丢失；后续 golden/readiness promotion 时可能产生回归。
- **建议改法和验证点**: 在 Slice C Required invariants 中明确 "role 值必须原样保留 retained oracle 中的状态修饰语（如 '（已离任）'），不做任何 trim 或 normalize"。测试应 assert exact role string match。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 03-未修复-低-Slice B 合成 parsed report 构造指导可更具体

- **位置**: Slice B: Test-only Same-source Contract Guards, Allowed changes 第 1 条
- **问题类型**: 不可直接实施
- **当前写法**: "Add helpers only for minimal §4.1.2, §2.2, §4.4.1, §8.6, and §8.2 synthetic parsed report sections/tables built from oracle values."
- **反例/失败场景**: 实施 agent 不确定如何从 retained oracle values 构造 minimal `ParsedAnnualReport`。例如，§4.1.2 经理表的 parsed table 结构是什么？列名是中文还是英文？是否需要 `ParsedTable` 对象还是只需 text sections？如果构造不当，测试 helper 可能无法驱动 extractor 路径。
- **为什么有问题**: plan 假设实施 agent 能从 retained excerpt JSON 的 expected values 和 anchor 信息推断出 parsed report 的 minimal 构造方式。但 retained excerpts 只有短 field-scoped 文本片段，不是完整的 parsed table 结构。实施 agent 可能需要参考现有 test helper（如 `_build_report_from_oracle_row()`）来理解构造模式。
- **直接证据**: retained excerpt JSON 中 manager/risk/holdings 的 excerpt 字段是短文本片段，不是 parsed table 结构；现有 test helper `_build_report_from_oracle_row()` 在 `test_small_golden_set_extractor_correctness.py` 中已有 parsed report 构造模式。
- **影响**: 实施 agent 可能在 Slice B 花费额外时间理解 parsed report 构造方式，或构造出不正确的 test helper。
- **建议改法和验证点**: 在 Slice B 中补充一句："参考现有 `_build_report_from_oracle_row()` helper 的构造模式；新增 helper 应遵循相同的 section/table 构造约定。"
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

---

## Open Questions

None. All three findings are informational/low severity and do not require controller decisions before implementation.

## Residual Risks

| Risk | Suggested tracking |
|---|---|
| §4.1.2 经理表的 parsed table 结构可能因基金而异（单经理 vs 多经理、有无离任） | Slice C implementation gate; test should cover both patterns |
| §2.2 risk 特征文本可能因基金类型不同而有不同结构（纯文本 vs 含特殊风险条款） | Slice D implementation gate; test should cover at least one multi-section case |
| 合成 parsed report 构造可能需要比 plan 预期更多的 test infrastructure | Slice B implementation gate; controller may need to authorize test helper expansion |

## Conclusion

**PASS**

The plan is well-structured and code-generation-ready. Heavy classification is correctly justified per AGENTS.md (public extractor output contract changes). The plan correctly requires additive contracts before tests/fixes for all four residuals, correctly avoids reusing wrong current surfaces, has complete non-goals, correctly defers exact/numeric correctness, and provides sufficiently specific slices, unlock rules, stop conditions, residual owners, and next entry.

The three findings are all low severity and informational. None blocks implementation. The plan can proceed to independent DS review and controller judgment.
