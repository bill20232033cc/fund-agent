# P6-S5 Quality Gate FQ5 Upgrade Implementation - 2026-05-20

## Verdict

P6-S5 implementation completed locally. FQ5 now reports deterministic template contract applicability as `resolved / not_applicable / mismatch` through `score.json` and `quality_gate.json`, while preserving old `match` compatibility as `resolved`.

No commit or push was performed.

## Scope Implemented

- Updated `fund_agent/fund/extraction_score.py`
  - imports public `CHAPTER_CONTRACT` helpers:
    - `load_template_contract_manifest`
    - `resolve_preferred_lens`
  - imports public `ITEM_RULE` helpers:
    - `load_template_item_rule_manifest`
    - `evaluate_template_item_rules`
  - added `PreferredLensChapterResolution`
  - added `ItemRuleDecisionSummary`
  - extended `FundQualityRow` with:
    - `contract_template_id`
    - `item_rule_template_id`
    - `preferred_lens_chapters`
    - `preferred_lens_unresolved_chapter_ids`
    - `item_rule_decisions`
  - replaced generation-time static `active_equity_fund` lens key with manifest-backed `active_fund`
  - marks missing fund type and money-market category as `not_applicable`
  - marks multi-value `classified_fund_type`, App category conflict, unsupported fund type, lens resolution failure, or ITEM_RULE evaluator failure as `mismatch`

- Updated `fund_agent/fund/quality_gate.py`
  - kept input boundary as score JSON only
  - added `QualityGateRuleResult`
  - added `QualityGateResult.rule_results` with default empty tuple for old fake/test construction compatibility
  - normalizes legacy `preferred_lens_status="match"` to `resolved`
  - emits FQ5 `rule_results` for every `fund_quality` row
  - emits FQ5/block issue only for `mismatch`

- Updated focused tests
  - `tests/fund/test_extraction_score.py`
  - `tests/fund/test_quality_gate.py`

- Updated docs
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## Boundary Checks

- `quality_gate.py` still does not import template manifests, renderer, audit modules, Service, Engine, UI, PDFs, cache, or fund documents.
- `quality_gate.py` still only consumes `score.json`.
- No report Markdown parsing was added.
- No LLM audit, Evidence Confirm, semantic NLP, PDF/cache/document access, Service/UI/Engine/CLI behavior change, or `extra_payload` was introduced.
- ITEM_RULE facts are stored as evaluator decisions only and do not claim renderer compliance.

## Verification

```text
.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
33 passed

.venv/bin/python -m pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
22 passed

.venv/bin/python -m pytest tests/fund/template/test_contracts.py tests/fund/template/test_item_rules.py -q
16 passed

.venv/bin/python -m pytest tests/ -q
246 passed

.venv/bin/python -m ruff check .
All checks passed!

git diff --check
passed
```

During implementation, the Service/CLI regression initially failed because test fakes constructed `QualityGateResult` without the new field. `rule_results` now defaults to `()`, preserving constructor compatibility without changing UI/CLI behavior.

## Files Changed

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p6-s5-implementation-20260520.md`

## Residual Risk

FQ5 now proves manifest applicability only. It does not prove renderer output follows the resolved lens, contains required labels, or correctly renders/deletes conditional ITEM_RULE sections. Those remain renderer/audit concerns.
