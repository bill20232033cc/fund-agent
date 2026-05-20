# P6-S4 Plan Rereview Controller Judgment - 2026-05-20

## Verdict

P6-S4 plan is accepted for implementation.

Initial review `docs/reviews/plan-review-20260520-152213.md` found two implementation blockers:

1. Explicit facet input could silently override an already classified `FundType`.
2. `segment_markers_any` used ordinary prose phrases that could produce false segment-present positives.

The plan has been amended in `docs/reviews/p6-s4-item-rule-manifest-plan-20260520.md`.

下一 gate：`P6-S4 implementation`。

## Closure Evidence

### Finding 1 Closed

The plan now requires a deterministic `_FACET_FUND_TYPE_MAP` and evaluator behavior:

- known explicit facets must be compatible with the provided `fund_type`
- conflicting facet/fund type input fails closed with `ValueError`
- unknown explicit facets do not trigger rules in P6-S4
- tests must cover `bond_fund + 指数增强基金` raising and `enhanced_index + 指数增强基金` triggering expected rules

This preserves the project rule that fund type judgment precedes more general analysis.

### Finding 2 Closed

The plan now restricts `segment_markers_any` to unique section markers, not ordinary prose:

- `#### 指数编制规则与成分股`
- `#### 基金经理投资哲学`
- `#### 超额收益分年度拆解`
- `#### 跟踪误差分析`

The plan explicitly rejects ordinary markers such as `跟踪指数`, `投资哲学`, `选股标准`, `超额收益稳定性`, and `日均偏离度`, and requires a test proving prose containing `跟踪指数` does not count as a segment.

## Accepted Implementation Constraints

- Keep ITEM_RULE in Capability `fund_agent/fund/template/item_rules.py`.
- Built-in manifest must include exactly the four current template draft ITEM_RULE blocks, all conditional.
- Support optional mode through schema/evaluator and test fixture only; do not invent built-in optional rules.
- Do not wire ITEM_RULE into `run_programmatic_audit(...)`, quality gate, Service, Engine, UI, or CLI.
- Do not change `docs/design.md`, control docs, or `docs/fund-analysis-template-draft.md` in implementation.
- Do not read fund documents, PDFs, caches, or repositories.
- Do not introduce `extra_payload`.
- Preserve lazy renderer exports in `fund_agent/fund/template/__init__.py`.

## Required Verification

Implementation must run:

```bash
.venv/bin/python -m pytest tests/fund/template/test_item_rules.py tests/fund/template/test_contracts.py tests/fund/template/test_renderer.py -q
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

## Residual Risk

P6-S4 proves ITEM_RULE applicability policy and segment markers, but it does not prove the renderer actually implements triggered conditional sections. That remains a later renderer/audit integration slice.
