# P6-S4 ITEM_RULE Manifest Implementation - 2026-05-20

## Verdict

P6-S4 implementation completed locally. This slice adds the first deterministic `ITEM_RULE` manifest in the Fund Capability layer without wiring it into audit gates, quality gates, Service, Engine, UI, or CLI.

No commit or push was performed.

## Scope Implemented

- Added `fund_agent/fund/template/item_rules.py`
  - typed dataclasses:
    - `TemplateItemRule`
    - `TemplateItemRuleManifest`
    - `TemplateItemRuleDecision`
  - type aliases for mode, missing behavior, and decision status
  - built-in manifest with exactly four current template draft conditional rules
  - `load_template_item_rule_manifest()`
  - `get_template_item_rule(...)`
  - `validate_template_item_rule_manifest(...)`
  - `evaluate_template_item_rule(...)`
  - `evaluate_template_item_rules(...)`
  - `rendered_segment_present(...)`

- Updated `fund_agent/fund/template/__init__.py`
  - exported ITEM_RULE dataclasses and helpers
  - preserved lazy renderer exports; no renderer eager import was introduced

- Added `tests/fund/template/test_item_rules.py`
  - manifest shape and exact rule ids
  - source fidelity for titles, condition text, and facet labels
  - validation fail-closed cases
  - deterministic fund type evaluation
  - explicit facet compatibility and conflict checks
  - optional mode via local fixture only
  - segment marker helper using unique markers rather than ordinary prose

- Updated current implementation docs
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## Key Decisions

- `ITEM_RULE` lives in `fund_agent/fund/template/item_rules.py`, as a sibling manifest to `contracts.py`.
- `CHAPTER_CONTRACT.required_output_items` remains unchanged.
- The built-in manifest contains no optional rules because the current template draft has no explicit `mode: optional` ITEM_RULE block.
- Optional behavior is supported by schema/evaluator and covered by a local test fixture.
- Evaluation uses only standard `FundType` and explicit facet labels supplied by the caller.
- Known explicit facets are validated against `_FACET_FUND_TYPE_MAP`; conflicts such as `bond_fund + 指数增强基金` raise `ValueError`.
- Unknown explicit facets do not trigger rules in P6-S4.
- `segment_markers_any` uses unique section markers such as `#### 跟踪误差分析`, not ordinary prose markers such as `跟踪指数`.

## Boundary Checks

- No LLM call added.
- No semantic NLP added.
- No PDF or evidence re-search added.
- No audit gate or quality gate integration added.
- No Service, Engine, UI, CLI behavior changes.
- No fund document filesystem access added.
- No `extra_payload` introduced.
- Did not modify `docs/design.md`, control docs, or `docs/fund-analysis-template-draft.md`.

## Verification

Final verification results:

```text
.venv/bin/python -m pytest tests/fund/template/test_item_rules.py tests/fund/template/test_contracts.py tests/fund/template/test_renderer.py -q
38 passed

.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py -q
16 passed

.venv/bin/python -m pytest tests/ -q
237 passed

.venv/bin/python -m ruff check .
All checks passed!

git diff --check
passed
```

During implementation, the first targeted template test run failed because the duplicate-rule-id test fixture replaced the first rule instead of preserving it and adding a duplicate. The test fixture was corrected; no production code change was needed for that failure.

## Files Changed

- `fund_agent/fund/template/item_rules.py`
- `fund_agent/fund/template/__init__.py`
- `tests/fund/template/test_item_rules.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p6-s4-implementation-20260520.md`

## Residual Risk

P6-S4 proves ITEM_RULE applicability and segment marker policy, but it does not prove renderer support for triggered conditional sections. Renderer/audit consumption remains intentionally out of scope for this slice.
