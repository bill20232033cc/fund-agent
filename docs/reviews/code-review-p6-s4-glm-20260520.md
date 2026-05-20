# Code Review

## Scope

- Mode: current changes
- Branch: main
- Base: main
- Output file: `docs/reviews/code-review-p6-s4-glm-20260520.md`
- Included scope: P6-S4 ITEM_RULE manifest — `fund_agent/fund/template/item_rules.py` (new), `fund_agent/fund/template/__init__.py`, `tests/fund/template/test_item_rules.py` (new), `fund_agent/fund/README.md`, `tests/README.md`
- Excluded scope: contracts.py, renderer.py, audit_programmatic.py, Service/UI/CLI, docs/design.md, docs/fund-analysis-template-draft.md
- Parallel review coverage: 无，单 reviewer 全量走读

## Findings

未发现实质性问题。

**备注（非 finding）**：`_validate_template_item_rule` 中有三个校验路径无直接测试 case 覆盖——empty `facets_any` on conditional (line 362-363)、facet maps to fund_type not in `fund_types_any` (line 404-409)、empty `fund_types_any` (line 364-365)。但这些路径在内置 manifest 加载时已被 `_BUILT_IN_RULE_IDS` 精确匹配和 `_validate_rule_facets` 间接覆盖；plan 列出的 6 项 fail-closed 测试要求均已满足（实际覆盖 8 项）。不作为 finding 报告。

## Architecture Boundary Review

Pass. `item_rules.py` 只依赖 `fund_type.py`（FundType）和 `template/contracts.py`（load_template_contract_manifest），不依赖 renderer、audit、Service、UI 或 CLI。`__init__.py` 新增的 import 不引入 cycle：audit import 后 renderer 未加载（lazy `__getattr__` 保持有效），`item_rules` 通过 `__init__.py` 传递加载但不形成反向依赖。

## Import Cycle Verification

```text
contracts.py ← item_rules.py                           ✅ 无 cycle
contracts.py ← __init__.py ← (外部调用)                  ✅ 无 cycle
audit_programmatic.py → chapter_blocks.py, contracts.py  ✅ 不导入 item_rules/renderer
```

Python 验证：`import audit_programmatic` 后 `item_rules` 已加载（通过 `__init__.py` 传递），但 `renderer` 未加载。无 cycle。

## Built-in Manifest Exactness

| Plan Rule | chapter_id | mode | fund_types_any | segment_markers_any | Verified |
|---|---|---|---|---|---|
| chapter_1_index_constituents | 1 | conditional | index_fund, enhanced_index | #### 指数编制规则与成分股, ...（仅指数基金） | ✅ |
| chapter_1_manager_philosophy | 1 | conditional | active_fund | #### 基金经理投资哲学, ...（仅主动基金） | ✅ |
| chapter_2_alpha_yearly_breakdown | 2 | conditional | active_fund, enhanced_index | #### 超额收益分年度拆解, ...（仅主动基金和指数增强） | ✅ |
| chapter_2_tracking_error_analysis | 2 | conditional | index_fund, enhanced_index | #### 跟踪误差分析, ...（仅指数基金） | ✅ |

所有 item_title、when_text、facets_any、fund_types_any、segment_markers_any 与 plan 的 `Built-in Manifest Content` 逐条核对一致。`_BUILT_IN_RULE_IDS` 确保增删规则时 validation fail closed。

## Evaluation Correctness

| Fund Type | Render Rules | Verified |
|---|---|---|
| index_fund | index_constituents, tracking_error | ✅ |
| enhanced_index | index_constituents, alpha_yearly, tracking_error | ✅ |
| active_fund | manager_philosophy, alpha_yearly | ✅ |
| bond_fund | (none) | ✅ |
| qdii_fund | (none) | ✅ |
| fof_fund | (none) | ✅ |

Facet conflict: `bond_fund + 指数增强基金` → `ValueError` ✅
Compatible facet: `enhanced_index + 指数增强基金` → triggered ✅
Unknown facet: `index_fund + 用户自定义标签` → ignored, no trigger ✅

## Segment Marker Safety

- `_FORBIDDEN_SEGMENT_MARKERS` rejects 跟踪指数、投资哲学、选股标准、超额收益稳定性、日均偏离度 ✅
- `rendered_segment_present("正文提到跟踪指数...")` → False ✅
- `rendered_segment_present("#### 跟踪误差分析\n\n...")` → True ✅
- No false positive from ordinary prose ✅

## Scope Compliance

- `docs/design.md` not modified ✅
- `docs/fund-analysis-template-draft.md` not modified ✅
- No audit integration (`run_programmatic_audit` untouched) ✅
- No quality gate changes ✅
- No Service/UI/CLI changes ✅
- No PDF/cache/document access ✅

## Open Questions

- 无

## Residual Risk

- `item_rules.py` 通过 `__init__.py` 传递加载到所有 import `fund_agent.fund.template` 的调用方。MVP 无影响，但若 `item_rules` 模块体积增长或增加重 I/O，应考虑与 renderer 同样的 lazy `__getattr__` 策略。
- `_validate_explicit_facets` 对未知 facet 静默忽略。plan 明确要求此行为（P6-S4 不对未知 facet raise），但后续 slice 若需更严格的 facet 校验应重新评估。
- ITEM_RULE manifest 不接入程序审计。后续 P6-S5 或 audit 集成 slice 需要决定是否新增规则码或扩展 C2。
