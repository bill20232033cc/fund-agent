# Code Review — P6-S4 ITEM_RULE Manifest Slice

## Scope

- Mode: current changes
- Branch: main (unstaged workspace changes)
- Base: main
- Output file: `docs/reviews/code-review-p6-s4-mimo-20260520.md`
- Included scope: P6-S4 ITEM_RULE manifest slice
  - `fund_agent/fund/template/item_rules.py` — ITEM_RULE dataclasses, built-in manifest, evaluator, segment helper (new)
  - `fund_agent/fund/template/__init__.py` — eager item_rules exports, lazy renderer preserved
  - `tests/fund/template/test_item_rules.py` — 8 test functions covering manifest shape, source fidelity, fail-closed, evaluation, optional fixture, segment markers (new)
  - `fund_agent/fund/README.md` — ITEM_RULE documentation
  - `tests/README.md` — test coverage documentation
- Excluded scope: Service/Engine/UI/CLI behavior, audit gate, quality gate, fund documents, PDF/cache access, renderer conditional sections, design.md, control docs, template draft
- Parallel review coverage: 无

## Findings

未发现实质性问题。

## Detailed Review Evidence

### 1. Built-in manifest exactly four current conditional rules

`_MANIFEST` at `item_rules.py:122-180` contains exactly four rules:

| rule_id | chapter | item_title | mode | fund_types_any |
|---|---|---|---|---|
| `chapter_1_index_constituents` | 1 | 指数编制规则与成分股 | conditional | index_fund, enhanced_index |
| `chapter_1_manager_philosophy` | 1 | 基金经理投资哲学 | conditional | active_fund |
| `chapter_2_alpha_yearly_breakdown` | 2 | 超额收益分年度拆解 | conditional | active_fund, enhanced_index |
| `chapter_2_tracking_error_analysis` | 2 | 跟踪误差分析 | conditional | index_fund, enhanced_index |

All four match the template draft (`docs/fund-analysis-template-draft.md`) ITEM_RULE blocks exactly. No invented optional rules exist in the built-in manifest.

`_validate_builtin_manifest_rule_ids` at line 555 enforces exact rule ID set match against `_BUILT_IN_RULE_IDS`, preventing additions or removals without code change.

- **Pass.**

### 2. No invented optional rules; optional only via fixture support

- All four built-in rules have `mode="conditional"`, `missing_behavior="delete_segment"`.
- `TemplateItemRuleMode` supports `"optional"` at the type level.
- `_validate_template_item_rule` enforces `optional → render_unavailable` and `conditional → delete_segment` (lines 358-361).
- Test `test_optional_fixture_renders_unavailable_without_builtin_optional_rule` uses a local `_optional_rule()` fixture to prove optional evaluation works without polluting the built-in manifest.
- **Pass.**

### 3. Facet-to-fund-type conflict fail-closed

- `_FACET_FUND_TYPE_MAP` at line 44 maps 7 facet labels to 3 FundType values.
- `_validate_explicit_facets` at line 451 raises `ValueError` when a known facet maps to a different FundType than provided.
- Test `test_evaluate_template_item_rule_validates_explicit_facets_against_fund_type` verifies: compatible facet triggers, conflicting facet (`bond_fund` + `指数增强基金`) raises ValueError, unknown facet silently does not trigger.
- `_validate_rule_facets` at line 388 validates that every configured facet maps to a FundType in `fund_types_any`.
- **Pass.**

### 4. Segment markers unique and not ordinary prose

- `_FORBIDDEN_SEGMENT_MARKERS` at line 40: `{"跟踪指数", "投资哲学", "选股标准", "超额收益稳定性", "日均偏离度"}`.
- `_validate_rule_segment_markers` at line 412 rejects markers in the forbidden set.
- All four rules use `#### {item_title}` and `{item_title}（...）` format — unique section headings, not ordinary prose.
- `rendered_segment_present` at line 315: literal substring check only, no regex, no NLP.
- Test `test_rendered_segment_present_uses_unique_markers_not_ordinary_prose` verifies ordinary prose returns False, unique heading markers return True.
- **Pass.**

### 5. No audit gate/quality gate integration

- `item_rules.py` imports: `fund_type.py`, `contracts.py`. No imports from `fund_agent.fund.audit`, `fund_agent.services`, `fund_agent.engine`, `fund_agent.ui`, `fund_agent.cli`.
- No new audit rule codes added. No changes to `audit_programmatic.py` or `contract_rules.py`.
- No quality gate changes.
- **Pass.**

### 6. No Service/Engine/UI/CLI behavior expansion

Changed files do not include:
- `fund_agent/services/`
- `fund_agent/engine/`
- `fund_agent/ui/`
- `fund_agent/cli.py`

- **Pass.**

### 7. No fund document/PDF/cache access

- `item_rules.py` imports only `fund_type.py` and `contracts.py`. No filesystem, PDF, cache, or document repository imports.
- **Pass.**

### 8. No extra_payload

- All three dataclasses (`TemplateItemRule`, `TemplateItemRuleManifest`, `TemplateItemRuleDecision`) use explicit typed fields. No dict/Any payload.
- **Pass.**

### 9. Public exports preserve lazy renderer behavior

- `__init__.py` diff shows item_rules exports are added as **eager** imports (lines 17-30), same pattern as `chapter_blocks`.
- Renderer exports remain in `_RENDERER_EXPORTS` set with `__getattr__` lazy loading (lines 32-59).
- No change to the lazy loading mechanism. Import cycle `__init__ → renderer → audit → chapter_blocks → contracts` still avoided.
- Verified: `from fund_agent.fund.template import render_template_report` triggers lazy load correctly.
- **Pass.**

### 10. Import cycle audit

Dependency graph:
```
contracts.py    fund_type.py
  ↑                ↑
  └── item_rules.py ──┘
        ↑
  __init__.py (eager)
```

- `item_rules.py` imports from `contracts.py` and `fund_type.py` only. No cycle.
- `__init__.py` imports `item_rules` eagerly; renderer stays lazy. No cycle.
- `audit/` modules do not import `item_rules`. No cycle.
- **Pass.**

### 11. Deterministic evaluation correctness

`evaluate_template_item_rule` at line 247:

- `_validate_fund_type(fund_type)` — fail-closed on unsupported type.
- `_validate_template_item_rule(rule, ...)` — fail-closed on malformed rule.
- `_validate_explicit_facets(fund_type, facets)` — fail-closed on conflicting facets.
- `fund_type in rule.fund_types_any` — primary trigger.
- `any(facet in rule.facets_any for facet in supported_facets)` — secondary trigger from compatible explicit facets.
- Conditional untriggered → `status="delete"`.
- Optional untriggered → `status="render"`.
- No NLP, no inference, no LLM.
- **Pass.**

### 12. Test coverage

| Plan requirement | Test | Pass? |
|---|---|---|
| Exact 4 conditional rules | `test_load_template_item_rule_manifest_returns_exact_four_conditional_rules` | Yes |
| Source fidelity (titles, facets) | `test_template_item_rule_manifest_preserves_source_titles_and_facets` | Yes |
| Public export lookup | `test_template_item_rule_public_exports_can_get_rule_by_id` | Yes |
| Fail-closed (9 scenarios) | `test_validate_template_item_rule_manifest_fails_closed_for_invalid_cases` | Yes |
| Deterministic evaluation by fund type | `test_evaluate_template_item_rules_by_fund_type_without_semantic_nlp` | Yes |
| Explicit facet validation | `test_evaluate_template_item_rule_validates_explicit_facets_against_fund_type` | Yes |
| Optional fixture (no built-in) | `test_optional_fixture_renders_unavailable_without_builtin_optional_rule` | Yes |
| Unique segment markers | `test_rendered_segment_present_uses_unique_markers_not_ordinary_prose` | Yes |
| Unsupported fund type | `test_evaluate_template_item_rule_rejects_unsupported_fund_type` | Yes |

9 test functions total. 237/237 full suite passes. Ruff clean.

- **Pass.**

### 13. Fail-closed validation coverage

`validate_template_item_rule_manifest` covers 13 failure conditions from the plan:

| Condition | Line | Verified? |
|---|---|---|
| Empty template_id | 230 | Yes |
| Empty source_path | 232 | Yes |
| Duplicate rule_id | 236 | Yes |
| Unknown chapter_id | 350 | Yes |
| Empty item_title | 353 | Yes |
| Unsupported mode | 354 | Yes |
| conditional + render_unavailable | 358 | Yes |
| optional + delete_segment | 360 | Yes |
| conditional empty facets_any | 362 | Yes |
| Unsupported facet | 402 | Yes |
| Facet maps to wrong fund_type | 405 | Yes |
| Unsupported fund_type | 447 | Yes |
| Empty segment_markers_any | 425 | Yes |
| Ordinary prose marker | 430 | Yes |
| Built-in rule ID set drift | 568 | Yes |

- **Pass.**

## Open Questions

- 无。

## Residual Risk

- `evaluate_template_item_rule` re-validates the rule against the full manifest on every call (line 268). Same pattern as P6-S3 `load_programmatic_contract_rules()`. Fine for current usage; cache if batch evaluation becomes hot.
- `rendered_segment_present` does not verify that the marker appears within the correct chapter block — it checks the full markdown. This is acceptable because segment markers are unique headings that should not appear in other chapters, but a future chapter-aware check could tighten this.
- `_SUPPORTED_FUND_TYPES` is a separate source of truth from `FundType` in `fund_type.py`. If a new FundType is added to `fund_type.py` but not to `_SUPPORTED_FUND_TYPES`, validation will reject it. The risk is low because `_SUPPORTED_FUND_TYPES` is checked at validation time and will surface immediately.

## Conclusion

PASS.

The P6-S4 implementation correctly adds a machine-readable ITEM_RULE manifest with exactly four conditional rules matching the template draft. Deterministic evaluation by FundType and explicit facets works without NLP or LLM. Facet-to-fund-type conflicts fail closed. Segment markers use unique section headings, not ordinary prose. No audit gate, quality gate, Service, Engine, UI, or CLI integration. No fund document/PDF/cache access. Lazy renderer exports preserved. 237/237 tests pass, ruff clean.
