# P6-S5 Quality Gate FQ5 Upgrade Plan - 2026-05-20

## Verdict

P6-S5 plan accepted after amendment. This slice should upgrade FQ5 from the old static `preferred_lens_resolvability` check into a deterministic contract/lens applicability result backed by the P6 `CHAPTER_CONTRACT` and `ITEM_RULE` manifests.

下一 gate：`P6-S5 implementation`。

## Inputs

- Design truth: `docs/design.md`
- P4/P5/P6 control context: `docs/implementation-control-p4.md`
- P6 backlog: `docs/reviews/post-p5-follow-up-planning-20260520.md`
- P6-S4 accepted judgment: `docs/reviews/p6-s4-code-review-controller-judgment-20260520.md`
- Current code facts:
  - `fund_agent/fund/quality_gate.py`
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/template/contracts.py`
  - `fund_agent/fund/template/item_rules.py`
  - `tests/fund/test_quality_gate.py`
  - `tests/fund/test_extraction_score.py`

## Problem Statement

P6 has now made template contracts machine-readable:

- P6-S1: `CHAPTER_CONTRACT` manifest and `resolve_preferred_lens(...)`
- P6-S2: renderer chapter blocks
- P6-S3: deterministic C2 programmatic contract audit
- P6-S4: `ITEM_RULE` manifest and deterministic evaluator

However, quality gate FQ5 still reflects the pre-P6 state:

- `extraction_score.py` derives `preferred_lens_status` using static maps:
  - `PREFERRED_LENS_KEY_BY_FUND_TYPE`
  - `APP_CATEGORY_ALLOWED_FUND_TYPES`
- It does not call `resolve_preferred_lens(...)`.
- It does not expose whether every template chapter can resolve a lens for the identified fund type.
- It does not expose `ITEM_RULE` decisions.
- It currently uses `match / mismatch` wording, while the backlog asks score/gate artifacts to explain `resolved / not_applicable / mismatch`.
- For `active_fund`, the static key is `active_equity_fund`, but the current `CHAPTER_CONTRACT` manifest uses `active_fund`. This is no longer the contract truth.

P6-S5 must make `score.json` and `quality_gate.json` explain the deterministic contract applicability result without claiming that the renderer has complied with those contracts.

## Non-goals

P6-S5 must not:

- Parse rendered report Markdown.
- Inspect `RenderedChapterBlock` or renderer output.
- Call LLM audit, Evidence Confirm, or semantic NLP.
- Read PDF, cache, annual reports, or fund documents directly.
- Re-search evidence.
- Change Service, Engine, UI, CLI behavior.
- Change report rendering behavior.
- Wire `ITEM_RULE` into programmatic audit or quality gate as renderer-compliance enforcement.
- Change `docs/design.md`, control docs, or template draft.
- Put explicit parameters into `extra_payload`.

## Current Code Facts

### `extraction_score.py`

Current `FundQualityRow` contains:

- `fund_code`
- `fund_name`
- `app_category`
- `classified_fund_type`
- `app_category_status`
- `preferred_lens_status`
- `preferred_lens_key`
- missing-field counts/rates
- missing P0/P1 fields
- `reason`

Current FQ5-related helpers:

- `_build_fund_quality_row(...)`
- `_preferred_lens_status(...)`
- `_preferred_lens_reason(...)`
- static `PREFERRED_LENS_KEY_BY_FUND_TYPE`

Current behavior:

- `preferred_lens_status` is `match` if the static map has a key and App category is not conflict.
- `preferred_lens_status` is `mismatch` if fund type is missing, App category conflicts, or static key is missing.
- `score.json` serializes `fund_quality` with `asdict(row)`.
- `score.md` includes `preferred_lens_status` and `preferred_lens_key`.

### `quality_gate.py`

Current gate behavior:

- It only consumes `score.json`.
- It does not import template manifests.
- Missing `fund_quality` remains backward-compatible and emits FQ0/info.
- `_evaluate_fund_quality(...)` creates:
  - FQ1/block for App category conflict
  - FQ4 warn/block for missing-field rate
  - FQ5/block when `preferred_lens_status == "mismatch"`
- `QualityGateIssue` already contains `rule_code`, `severity`, `fund_code`, `message`, `app_category`, `classified_fund_type`, and `preferred_lens_key`.
- `quality_gate.json` currently contains top-level status and issue list only. If FQ5 is resolved or not applicable, there is no explicit FQ5 record in gate JSON.

### Template Manifests

`contracts.py`:

- `load_template_contract_manifest()` validates and returns 8 chapters.
- `resolve_preferred_lens(chapter_id, fund_type)` validates standard `FundType`, returns exact lens or `default`, and raises `ValueError` on unsupported types or missing fallback.
- Current supported fund types:
  - `index_fund`
  - `active_fund`
  - `bond_fund`
  - `enhanced_index`
  - `qdii_fund`
  - `fof_fund`

`item_rules.py`:

- `load_template_item_rule_manifest()` validates exactly four current conditional rules.
- `evaluate_template_item_rules(fund_type=..., facets=())` returns deterministic rule decisions.
- It does not prove renderer compliance and must remain separate from report/audit enforcement in this slice.

## Design Decision

### Dependency Direction

Keep the current boundary:

```text
template/contracts.py, template/item_rules.py
        ↓
extraction_score.py
        ↓ writes score.json
quality_gate.py
        ↓ writes quality_gate.json / quality_gate.md
```

`quality_gate.py` must continue to consume only `score.json`. It should not import `contracts.py`, `item_rules.py`, renderer, audit, Service, Engine, UI, PDFs, or document repositories.

Rationale:

- Capability owns contract/lens/item-rule knowledge.
- `extraction_score.py` is already Capability code that derives fund-level quality facts from snapshot records.
- `quality_gate.py` is the gate consumer of score JSON; it should remain deterministic and artifact-driven.
- This avoids report Markdown parsing and avoids tying quality gate to renderer compliance.

## FQ5 Semantics

Replace FQ5 wording from `preferred_lens_resolvability` with:

```text
FQ5 = template_contract_applicability
```

FQ5 status values in newly generated `score.json`:

| status | Meaning | Gate severity |
|---|---|---|
| `resolved` | A single supported `classified_fund_type` exists; App category is not in conflict; all `CHAPTER_CONTRACT` chapters resolve `preferred_lens`; `ITEM_RULE` evaluator runs successfully for the fund type. | no issue; `quality_gate.json.rule_results` records info |
| `not_applicable` | FQ5 cannot run because no single usable fund type is available or the fund category is explicitly outside the current 8-chapter template scope. This does not prove success. Missing/failed fields are handled by FQ2/FQ4/FQ6. | no blocking issue; `rule_results` records info |
| `mismatch` | Fund type facts are contradictory, or a single fund type exists but conflicts with App category, is unsupported by manifests, fails chapter lens resolution, or fails ITEM_RULE evaluation. | FQ5/block |

Do not keep `match` as a newly generated status. `quality_gate.py` should still accept old `match` and treat it as `resolved` for backward compatibility.

### Not-applicable Rules

Use `not_applicable` only when FQ5 should not claim a contract result:

- `classified_fund_type` is missing after `_unique_optional_text(...)`.
- `app_category` is a known category currently outside the report template scope, such as `货币基金类`.

Use `mismatch` when a usable fund type exists but the system can prove contradiction:

- `classified_fund_type` has conflicting values across rows. This is a deterministic type contradiction, not a template non-applicability case.
- App category is known and conflicts with `classified_fund_type`.
- `classified_fund_type` is present but not one of the current `FundType` values.
- `resolve_preferred_lens(...)` raises for any chapter.
- `evaluate_template_item_rules(...)` raises for the fund type.

This keeps FQ5 from double-blocking ordinary missing-data paths while still blocking contradictory or unsupported contract application.

## Data Model Changes

### `extraction_score.py`

Add status constants:

```python
PREFERRED_LENS_STATUS_RESOLVED = "resolved"
PREFERRED_LENS_STATUS_NOT_APPLICABLE = "not_applicable"
PREFERRED_LENS_STATUS_MISMATCH = "mismatch"
LEGACY_PREFERRED_LENS_STATUS_MATCH = "match"
```

Keep `PREFERRED_LENS_STATUS_MISMATCH = "mismatch"` for existing imports/tests.

Remove generation-time reliance on `PREFERRED_LENS_KEY_BY_FUND_TYPE`. New generated `preferred_lens_key` should be the attempted standard fund type, such as `active_fund`, not the obsolete `active_equity_fund`.

Add dataclasses:

```python
@dataclass(frozen=True, slots=True)
class PreferredLensChapterResolution:
    chapter_id: int
    title: str
    lens_key: str
    used_default: bool

@dataclass(frozen=True, slots=True)
class ItemRuleDecisionSummary:
    rule_id: str
    chapter_id: int
    item_title: str
    triggered: bool
    status: str
    missing_behavior: str
```

Append fields to `FundQualityRow` after existing fields to reduce churn:

```python
contract_template_id: str | None
item_rule_template_id: str | None
preferred_lens_chapters: tuple[PreferredLensChapterResolution, ...]
preferred_lens_unresolved_chapter_ids: tuple[int, ...]
item_rule_decisions: tuple[ItemRuleDecisionSummary, ...]
```

Field meanings:

- `contract_template_id`: `TemplateContractManifest.template_id` when contract manifest was evaluated.
- `item_rule_template_id`: `TemplateItemRuleManifest.template_id` when item rules were evaluated.
- `preferred_lens_chapters`: per-chapter lens resolution facts; empty for `not_applicable` or early mismatch.
- `preferred_lens_unresolved_chapter_ids`: chapter ids that failed to resolve; empty when resolved.
- `item_rule_decisions`: deterministic ITEM_RULE applicability decisions; empty unless a supported fund type reached evaluator.

These fields are facts about manifest applicability, not renderer compliance.

### `quality_gate.py`

Add a rule result surface so `quality_gate.json` can explain FQ5 even when there is no issue:

```python
@dataclass(frozen=True, slots=True)
class QualityGateRuleResult:
    rule_code: str
    severity: str
    fund_code: str | None
    status: str
    message: str
    app_category: str | None = None
    classified_fund_type: str | None = None
    preferred_lens_key: str | None = None
```

Append `rule_results: tuple[QualityGateRuleResult, ...]` to `QualityGateResult`.

`_json_payload(...)` should include:

```json
"rule_results": [
  {
    "rule_code": "FQ5",
    "severity": "info",
    "fund_code": "004393",
    "status": "resolved",
    "message": "...",
    "classified_fund_type": "active_fund",
    "preferred_lens_key": "active_fund"
  }
]
```

`_markdown_payload(...)` should add a short `## Rule Results` section, or at minimum a `## FQ5 Contract Applicability` section. Keep existing issue table unchanged.

Backward-compatible consumers that only read `status` and `issues` should continue working.

## Deterministic Algorithm

### In `extraction_score.py`

Add helper:

```python
def _derive_contract_applicability(
    *,
    classified_fund_type: str | None,
    app_category: str | None,
    app_category_status: str,
    fund_type_reason: str,
) -> tuple[
    str,
    str | None,
    tuple[PreferredLensChapterResolution, ...],
    tuple[int, ...],
    tuple[ItemRuleDecisionSummary, ...],
    str,
    str | None,
    str | None,
]
```

Implementation rules:

0. If `fund_type_reason` says `classified_fund_type 存在冲突值`:
   - status `mismatch`
   - preferred_lens_key is `None`
   - reason preserves the conflicting values
   - do not evaluate manifests further; one stable fund type does not exist

1. If `app_category == "货币基金类"`:
   - status `not_applicable`
   - reason says current 8-chapter template does not apply to money-market funds
   - no manifest evaluation

2. If `classified_fund_type is None`:
   - status `not_applicable`
   - reason includes `fund_type_reason`
   - no manifest evaluation

3. If `app_category_status == "conflict"`:
   - status `mismatch`
   - preferred_lens_key is `classified_fund_type`
   - reason includes App category conflict
   - do not evaluate manifests further; conflict is already deterministic

4. If `classified_fund_type` is not one of the current `FundType` literals:
   - status `mismatch`
   - preferred_lens_key is `classified_fund_type`
   - reason says unsupported fund type

5. Load `load_template_contract_manifest()`.

6. For each chapter in manifest:
   - call `resolve_preferred_lens(chapter.chapter_id, fund_type)`
   - append `PreferredLensChapterResolution`
   - `lens_key = lens.fund_type`
   - `used_default = lens.fund_type == "default"`

7. If any chapter raises:
   - status `mismatch`
   - unresolved ids contain failed chapters
   - reason includes the exception

8. Load `load_template_item_rule_manifest()` and call `evaluate_template_item_rules(fund_type=fund_type, facets=())`.

9. Convert each `TemplateItemRuleDecision` to `ItemRuleDecisionSummary`.

10. If ITEM_RULE evaluation raises:
    - status `mismatch`
    - reason includes the exception

11. Otherwise:
    - status `resolved`
    - preferred_lens_key is `classified_fund_type`
    - reason says all 8 chapters resolved and item rules evaluated deterministically

Do not pass facets from snapshot in P6-S5. Snapshot does not currently expose trusted explicit facet labels, and deriving them would be semantic classification. `facets=()` is intentional.

### In `quality_gate.py`

Add helper:

```python
def _fund_quality_rule_result(row: Mapping[str, object], index: int) -> QualityGateRuleResult
```

Rules:

- Normalize status:
  - old `match` -> `resolved`
  - `resolved` -> `resolved`
  - `not_applicable` -> `not_applicable`
  - `mismatch` -> `mismatch`
  - unknown -> raise `ValueError`
- Return FQ5 rule result for every `fund_quality` row.
- Create FQ5 blocking issue only for normalized `mismatch`.
- Do not create FQ5 issue for `resolved` or `not_applicable`.

This makes `quality_gate.json` explanatory without inflating pass/warn/block status.

## How CHAPTER_CONTRACT And ITEM_RULE Are Used

Use `CHAPTER_CONTRACT` to prove:

- the identified fund type is supported by the current contract manifest
- every template chapter can resolve a preferred lens
- the resolved lens key per chapter is explicit in `score.json`

Use `ITEM_RULE` to prove:

- item rule manifest is valid
- deterministic conditional item decisions can be evaluated for the fund type
- `score.json` can show which conditional segments would be `render` or `delete`

Do not use either manifest to claim:

- renderer output contains required labels
- renderer output deletes inactive ITEM_RULE sections
- report text semantically follows preferred_lens
- evidence supports the rendered assertions

Those are C2/audit/renderer concerns, not FQ5 quality-gate concerns in this slice.

## File-level Implementation Plan

### 1. Update extraction score contract facts

File: `fund_agent/fund/extraction_score.py`

Implement:

- import `FundType`
- import `load_template_contract_manifest`, `resolve_preferred_lens`
- import `load_template_item_rule_manifest`, `evaluate_template_item_rules`
- add status constants and new dataclasses
- extend `FundQualityRow` with contract/item-rule fact fields
- replace static `PREFERRED_LENS_KEY_BY_FUND_TYPE` generation path with manifest-backed `_derive_contract_applicability(...)`
- keep App category compatibility logic
- keep old missing-field accounting unchanged
- update `_score_json_payload(...)` through `asdict(...)`
- update `_score_markdown(...)` Fund Quality table to include:
  - `preferred_lens_status`
  - `preferred_lens_key`
  - resolved chapter ids count or list
  - unresolved chapter ids
  - item rule decisions summary, such as `render=2/delete=2`

Do not read report Markdown, PDFs, caches, or fund documents.

### 2. Update quality gate result surface

File: `fund_agent/fund/quality_gate.py`

Implement:

- `QualityGateRuleResult`
- `QualityGateResult.rule_results`
- `_evaluate_score_payload(...)` returns both issues and rule results, or uses an internal accumulator object
- `_evaluate_fund_quality(...)` emits FQ5 `QualityGateRuleResult` for each row and FQ5 issue only for `mismatch`
- `_json_payload(...)` includes `rule_results`
- `_markdown_payload(...)` includes FQ5 rule results
- preserve old score compatibility:
  - missing `fund_quality` still emits FQ0/info
  - old `preferred_lens_status="match"` means `resolved`
  - old `preferred_lens_status="mismatch"` means `mismatch`
  - missing new nested score fields default to empty values

Do not import template modules in `quality_gate.py`.

### 3. Tests

File: `tests/fund/test_extraction_score.py`

Add/update tests:

1. `derive_fund_quality_records` emits `preferred_lens_status="resolved"` for `active_fund`, and `preferred_lens_key=="active_fund"` instead of old `active_equity_fund`.
2. All current standard fund types resolve across 8 chapters:
   - `index_fund`
   - `active_fund`
   - `bond_fund`
   - `enhanced_index`
   - `qdii_fund`
   - `fof_fund`
3. App category conflict still yields `preferred_lens_status="mismatch"`.
4. Missing `classified_fund_type` yields `preferred_lens_status="not_applicable"` and no chapter/item facts.
5. Multi-value `classified_fund_type` yields `preferred_lens_status="mismatch"`, preserves the conflicting values in `reason`, and no chapter/item facts.
6. Unsupported single fund type, such as `money_market_fund`, yields `mismatch`.
7. `app_category="货币基金类"` yields `not_applicable`.
8. `score.json` includes:
   - `contract_template_id`
   - `item_rule_template_id`
   - `preferred_lens_chapters`
   - `preferred_lens_unresolved_chapter_ids`
   - `item_rule_decisions`
9. `item_rule_decisions` for `active_fund` contain:
   - `chapter_1_manager_philosophy` -> `render`
   - `chapter_2_alpha_yearly_breakdown` -> `render`
   - index/tracking-error conditional rules -> `delete`

File: `tests/fund/test_quality_gate.py`

Add/update tests:

1. New `resolved` FQ5 status produces no FQ5 issue but appears in `quality_gate.json.rule_results`.
2. New `not_applicable` FQ5 status produces no FQ5 issue and appears in `rule_results`.
3. New `mismatch` FQ5 status produces FQ5/block issue and FQ5 rule result.
4. Old `preferred_lens_status="match"` remains compatible and normalizes to `resolved`.
5. Old score without `fund_quality` remains compatible and emits FQ0/info.
6. Unknown FQ5 status raises `ValueError`.
7. Markdown output includes the FQ5 rule result section.
8. Multi-value `classified_fund_type` from score-derived `mismatch` produces FQ5/block and preserves the conflict reason in the issue message.

No Service/UI/CLI tests should need behavior changes.

### 4. Docs

Allowed docs for implementation:

- `fund_agent/fund/README.md`
  - update quality gate section: FQ5 now reports deterministic template contract applicability from score JSON
  - state explicitly that FQ5 does not parse rendered Markdown and does not prove renderer compliance

- `tests/README.md`
  - update test descriptions for `test_extraction_score.py` and `test_quality_gate.py`

Do not modify:

- `docs/design.md`
- `docs/implementation-control*.md`
- `docs/fund-analysis-template-draft.md`

## Acceptance Commands

Implementation should run and report:

```bash
.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
.venv/bin/python -m pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

If implementation touches any template imports, also run:

```bash
.venv/bin/python -m pytest tests/fund/template/test_contracts.py tests/fund/template/test_item_rules.py -q
```

## Risks And Guardrails

| Risk | Guardrail |
|---|---|
| FQ5 overclaims renderer compliance | Store only manifest applicability facts; do not parse report Markdown or chapter blocks. |
| Quality gate starts depending on template modules | Keep manifest imports in `extraction_score.py`; `quality_gate.py` consumes JSON only. |
| Old score.json files break | Normalize old `match` to `resolved`, keep old `mismatch`, keep missing `fund_quality` FQ0/info path. |
| Missing classified fund type double-blocks as FQ5 | Use `not_applicable`; let FQ2/FQ4/FQ6 handle missing extraction quality. |
| Conflicting classified fund type silently passes | Treat multi-value `classified_fund_type` as `mismatch`, preserve conflict values in reason, and verify FQ5/block. |
| Unsupported present fund type silently passes | Use `mismatch` and FQ5/block. |
| ITEM_RULE decisions imply rendered sections exist/deleted | Name fields as decisions/facts and document that renderer compliance is out of scope. |
| Static lens key drift continues | Remove generation-time static preferred lens key map and use `resolve_preferred_lens(...)`. |

## Rollback Plan

If implementation regresses quality gate behavior:

1. Revert `extraction_score.py` changes to the pre-P6-S5 static fund_quality shape.
2. Revert `quality_gate.py` rule result surface and FQ5 normalization.
3. Remove new tests and README updates.
4. Keep P6-S1/S4 template manifests untouched.
5. Existing old-score compatibility path should restore FQ5 behavior to `match / mismatch`.

## Review Focus

Reviewers should verify:

- `quality_gate.py` does not import template manifests or read anything except `score.json`.
- `extraction_score.py` uses public manifest helpers rather than private constants.
- New `score.json` makes FQ5 status explicit as `resolved / not_applicable / mismatch`.
- `quality_gate.json` includes FQ5 rule results even when no FQ5 issue exists.
- `active_fund` resolves to the current contract key `active_fund`, not `active_equity_fund`.
- ITEM_RULE facts are included only as evaluator decisions and are not treated as renderer compliance.
- No LLM, semantic NLP, report Markdown parsing, PDF/cache/document access, Service/UI/Engine/CLI behavior change, or `extra_payload` is introduced.
