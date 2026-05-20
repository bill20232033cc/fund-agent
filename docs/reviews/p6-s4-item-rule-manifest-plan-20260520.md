# P6-S4 ITEM_RULE Manifest Plan - 2026-05-20

## Verdict

P6-S4 plan accepted after controller review amendments. This slice should machineize the template `ITEM_RULE` blocks as a deterministic Capability manifest. The first implementation must cover only deterministic `optional` / `conditional` item behavior and must not perform LLM judgment, semantic NLP, PDF evidence re-search, or Service/Engine/UI/CLI behavior changes.

下一 gate：`P6-S4 implementation`。

## Inputs

- Design truth: `docs/design.md`
- P4/P5/P6 control context: `docs/implementation-control-p4.md`
- P6 backlog: `docs/reviews/post-p5-follow-up-planning-20260520.md`
- P6-S1 plan: `docs/reviews/p6-s1-template-contract-manifest-plan-20260520.md`
- P6-S3 plan: `docs/reviews/p6-s3-programmatic-contract-audit-plan-20260520.md`
- P6-S3 accepted judgment: `docs/reviews/p6-s3-code-review-controller-judgment-20260520.md`
- Template source: `docs/fund-analysis-template-draft.md`
- Current code facts:
  - `fund_agent/fund/template/contracts.py`
  - `fund_agent/fund/template/renderer.py`
  - `fund_agent/fund/audit/contract_rules.py`

## Problem Statement

`docs/design.md` defines `ITEM_RULE` as the mechanism that decides whether a conditional template item should be rendered with an explicit unavailable value or removed entirely. The current code has machine-readable `CHAPTER_CONTRACT` and a deterministic C2 audit for required markers, but `ITEM_RULE` is still only human-facing text in `docs/fund-analysis-template-draft.md`.

Current gap:

- The renderer can add deterministic labels/placeholders for required output items, but it cannot prove whether a conditional segment should be present or absent.
- P6-S3 C2 can prove required markers exist, but it does not know that some sections are conditionally applicable only for specific fund facets.
- The template draft says conditional items that are not triggered must be deleted, while non-conditional unavailable fields may render `未披露` / `不适用` / `数据不足`. This policy is not machine-readable.
- Without a typed ITEM_RULE manifest, later audits could confuse "missing because condition not triggered" with "missing because renderer skipped a required item".

P6-S4 should make the current template `ITEM_RULE` blocks importable, validated, and evaluable without changing the product workflow.

## Current Template ITEM_RULE Facts

The current `docs/fund-analysis-template-draft.md` contains four explicit `ITEM_RULE` blocks, all `mode: conditional`:

| chapter | item | condition text | facets_any |
|---:|---|---|---|
| 1 | 指数编制规则与成分股 | 仅对指数基金（含指数增强）输出 | 宽基指数基金, 行业/主题指数基金, 策略指数基金, 指数增强基金 |
| 1 | 基金经理投资哲学 | 仅对主动基金输出 | 主动权益基金（价值风格）, 主动权益基金（均衡风格）, 主动权益基金（成长风格） |
| 2 | 超额收益分年度拆解 | 对主动基金和指数增强基金输出；纯指数基金跳过此项 | 主动权益基金（价值风格）, 主动权益基金（均衡风格）, 主动权益基金（成长风格）, 指数增强基金 |
| 2 | 跟踪误差分析 | 仅对指数基金（含指数增强）输出 | 宽基指数基金, 行业/主题指数基金, 策略指数基金, 指数增强基金 |

No explicit `mode: optional` block currently exists in the template draft. P6-S4 should still model `optional` because it is part of `docs/design.md` and the validation/evaluation code should be ready for future optional rules. The built-in manifest should not invent optional template items that are not present in the draft.

## Non-goals

P6-S4 must not:

- Implement LLM audit, Evidence Confirm, semantic NLP, or PDF evidence re-search.
- Implement full `ITEM_RULE` parsing from Markdown at runtime.
- Upgrade quality gate FQ5 or any quality gate behavior.
- Change Service, Engine, UI, CLI, extraction, fund type recognition, document repository, or annual report access.
- Read fund documents directly from filesystem. This slice should not read annual reports at all.
- Put explicit parameters into `extra_payload`; all inputs must be typed explicit parameters.
- Change `docs/fund-analysis-template-draft.md` or control docs.
- Rewrite renderer prose broadly. Renderer changes are allowed only if needed to add stable segment markers for existing conditional sections, and current renderer does not yet render those conditional sections.
- Treat facet matching as natural-language classification. It must use deterministic mappings from known fund types / explicit facet labels.

## Design Decision: Where The Schema Lives

Add a new Capability module:

```text
fund_agent/fund/template/item_rules.py
```

Rationale:

- `contracts.py` already owns the core `CHAPTER_CONTRACT` manifest and is large. Keeping ITEM_RULE in a sibling module avoids bloating ChapterContract while staying inside the template Capability boundary.
- ITEM_RULE references `ChapterContract` by `chapter_id` but has different evaluation semantics, trigger policy, and render segment markers.
- The module can import public `load_template_contract_manifest()` / `get_chapter_contract(...)` for validation without depending on renderer or audit modules.
- Future slices can import ITEM_RULE from template without creating audit-renderer cycles.

Public exports through `fund_agent/fund/template/__init__.py`:

- `TemplateItemRule`
- `TemplateItemRuleMode`
- `TemplateItemRuleDecision`
- `TemplateItemRuleManifest`
- `load_template_item_rule_manifest`
- `validate_template_item_rule_manifest`
- `evaluate_template_item_rule`
- `evaluate_template_item_rules`

Do not add ITEM_RULE fields to `ChapterContract` in this slice. Instead, validate that every `TemplateItemRule.chapter_id` points to an existing chapter. This keeps P6-S1 contract schema stable.

## Target Schema

Recommended dataclasses in `item_rules.py`:

```python
TemplateItemRuleMode = Literal["optional", "conditional"]
TemplateItemRuleMissingBehavior = Literal["render_unavailable", "delete_segment"]
TemplateItemRuleDecisionStatus = Literal["render", "delete"]

@dataclass(frozen=True, slots=True)
class TemplateItemRule:
    rule_id: str
    chapter_id: int
    item_title: str
    mode: TemplateItemRuleMode
    when_text: str
    facets_any: tuple[str, ...]
    fund_types_any: tuple[FundType, ...]
    segment_markers_any: tuple[str, ...]
    missing_behavior: TemplateItemRuleMissingBehavior

@dataclass(frozen=True, slots=True)
class TemplateItemRuleManifest:
    template_id: str
    source_path: str
    rules: tuple[TemplateItemRule, ...]

@dataclass(frozen=True, slots=True)
class TemplateItemRuleDecision:
    rule_id: str
    chapter_id: int
    item_title: str
    mode: TemplateItemRuleMode
    triggered: bool
    status: TemplateItemRuleDecisionStatus
    missing_behavior: TemplateItemRuleMissingBehavior
    reason: str
```

Schema semantics:

- `rule_id`: stable snake_case-ish identifier, for example `chapter_1_index_constituents`.
- `chapter_id`: chapter containing the rule; must exist in `CHAPTER_CONTRACT`.
- `item_title`: exact template item title from the `ITEM_RULE` block.
- `mode`:
  - `optional`: item may render when data exists; if data is unavailable, render explicit unavailable marker.
  - `conditional`: item renders only when deterministic trigger matches; if trigger does not match, delete the whole segment.
- `when_text`: source wording copied from the template draft.
- `facets_any`: exact facet labels copied from the template draft.
- `fund_types_any`: deterministic standard `FundType` triggers derived from facets.
- `segment_markers_any`: literal unique section markers used to locate the rendered segment when present. These must be stable section titles or labels, not ordinary prose phrases.
- `missing_behavior`:
  - `render_unavailable` for optional.
  - `delete_segment` for conditional.

Also add a module-level facet compatibility map:

```python
_FACET_FUND_TYPE_MAP: Final[dict[str, FundType]] = {
    "宽基指数基金": "index_fund",
    "行业/主题指数基金": "index_fund",
    "策略指数基金": "index_fund",
    "指数增强基金": "enhanced_index",
    "主动权益基金（价值风格）": "active_fund",
    "主动权益基金（均衡风格）": "active_fund",
    "主动权益基金（成长风格）": "active_fund",
}
```

This map is used only to validate explicitly provided facets. It must not infer facets from report text.

## Built-in Manifest Content

The initial built-in manifest should contain exactly the four current conditional rules from the template draft:

```text
chapter_1_index_constituents
chapter_id=1
item_title=指数编制规则与成分股
mode=conditional
facets_any=(宽基指数基金, 行业/主题指数基金, 策略指数基金, 指数增强基金)
fund_types_any=(index_fund, enhanced_index)
segment_markers_any=(#### 指数编制规则与成分股, 指数编制规则与成分股（仅指数基金）)
missing_behavior=delete_segment
```

```text
chapter_1_manager_philosophy
chapter_id=1
item_title=基金经理投资哲学
mode=conditional
facets_any=(主动权益基金（价值风格）, 主动权益基金（均衡风格）, 主动权益基金（成长风格）)
fund_types_any=(active_fund,)
segment_markers_any=(#### 基金经理投资哲学, 基金经理投资哲学（仅主动基金）)
missing_behavior=delete_segment
```

```text
chapter_2_alpha_yearly_breakdown
chapter_id=2
item_title=超额收益分年度拆解
mode=conditional
facets_any=(主动权益基金（价值风格）, 主动权益基金（均衡风格）, 主动权益基金（成长风格）, 指数增强基金)
fund_types_any=(active_fund, enhanced_index)
segment_markers_any=(#### 超额收益分年度拆解, 超额收益分年度拆解（仅主动基金和指数增强）)
missing_behavior=delete_segment
```

```text
chapter_2_tracking_error_analysis
chapter_id=2
item_title=跟踪误差分析
mode=conditional
facets_any=(宽基指数基金, 行业/主题指数基金, 策略指数基金, 指数增强基金)
fund_types_any=(index_fund, enhanced_index)
segment_markers_any=(#### 跟踪误差分析, 跟踪误差分析（仅指数基金）)
missing_behavior=delete_segment
```

The `fund_types_any` mapping is deterministic and intentionally coarse. Do not infer finer-grained facets from report text. If a future extractor provides explicit facet labels, evaluation may accept them as explicit input, but P6-S4 should not derive them with NLP.

Do not include ordinary prose markers such as `跟踪指数`, `投资哲学`, `选股标准`, `超额收益稳定性` or `日均偏离度`. Those strings can appear inside non-ITEM_RULE prose and would make `rendered_segment_present(...)` produce false positives.

## Deterministic Evaluation Rules

Add evaluator functions:

```python
def evaluate_template_item_rule(
    rule: TemplateItemRule,
    *,
    fund_type: FundType,
    facets: tuple[str, ...] = (),
) -> TemplateItemRuleDecision

def evaluate_template_item_rules(
    *,
    fund_type: FundType,
    facets: tuple[str, ...] = (),
) -> tuple[TemplateItemRuleDecision, ...]
```

Rules:

- A rule is triggered if `fund_type in rule.fund_types_any`.
- If explicit `facets` are provided, first validate every known facet against `_FACET_FUND_TYPE_MAP`.
- If a known explicit facet maps to a different `FundType` than the provided `fund_type`, fail closed with `ValueError`.
- Unknown explicit facets should not trigger a rule and should not raise in P6-S4; they should be ignored with a decision reason indicating no supported facet match.
- After compatibility validation, an explicit facet may also trigger a rule if any supported facet is in `rule.facets_any`.
- If no match:
  - `conditional` -> `status="delete"`, `missing_behavior="delete_segment"`.
  - `optional` -> `status="render"`, `missing_behavior="render_unavailable"`.
- If match:
  - both `conditional` and `optional` -> `status="render"`.
- Unsupported `fund_type` should fail closed with `ValueError`.
- Empty explicit facets should not trigger a rule.

This evaluation proves the policy decision: for conditional items, absence of trigger means delete the segment; for optional items, absence of data should render unavailable text.

## Relationship To CHAPTER_CONTRACT And Renderer Labels

P6-S4 must keep these concepts separate:

- `CHAPTER_CONTRACT.required_output_items`: chapter-level required labels audited by P6-S3 C2.
- `ITEM_RULE`: conditional or optional sub-segments that may be rendered or deleted based on deterministic applicability.
- P6-S3 renderer labels are not ITEM_RULE segment markers. They prove required chapter items exist; they do not prove conditional sections were correctly deleted.

Implementation guidance:

- `item_rules.py` validates `chapter_id` against `load_template_contract_manifest()`.
- Do not add the four ITEM_RULE items to `required_output_items`.
- Do not weaken P6-S3 C2 required marker rules when a conditional rule says delete a segment. P6-S3 required markers and P6-S4 conditional segments are independent surfaces.
- Current renderer does not render the four conditional full sections. For P6-S4, this is acceptable if evaluator decisions can prove that inactive conditional segments should be absent, and tests can verify absence/presence expectations on synthetic rendered text.

## Optional Vs Conditional Examples

The built-in manifest has only conditional rules, but implementation should support both modes.

Conditional example:

- Rule: `chapter_1_index_constituents`
- Fund type: `active_fund`
- Decision: `status="delete"`, reason says fund type did not match index/enhanced triggers.
- Expected behavior: rendered report should not contain `指数编制规则与成分股`.

Conditional triggered example:

- Rule: `chapter_1_index_constituents`
- Fund type: `index_fund`
- Decision: `status="render"`.
- Expected behavior: if renderer implements that segment in a later slice, segment must be present or explicitly data-backed. P6-S4 manifest does not require adding the segment now.

Optional support example for tests:

- Use a local test fixture `TemplateItemRule(mode="optional", missing_behavior="render_unavailable")`.
- Fund type not matched or data unavailable still yields `status="render"`.
- Expected behavior: renderer should display `未披露` / `不适用` / `数据不足` instead of deleting the item.

Do not add this optional fixture to the built-in manifest unless the template draft gains an explicit optional ITEM_RULE.

## Segment Presence Helper

Add a deterministic helper:

```python
def rendered_segment_present(markdown: str, rule: TemplateItemRule) -> bool
```

Rules:

- Return true if any `segment_markers_any` literal substring is present.
- No regex inference, no heading parsing beyond literal markers.
- Empty `segment_markers_any` is invalid at manifest validation time.

This helper enables tests and later audits to prove:

- conditional inactive + segment present -> violation
- conditional inactive + segment absent -> correct deletion
- optional unavailable + segment absent -> wrong for optional mode when optional rules exist

P6-S4 should not add a new audit rule code or wire this into `run_programmatic_audit(...)` unless plan review explicitly requests it. The acceptance signal is machine-readable manifest + deterministic evaluation/proof helpers, not a new blocker in the report gate.

## Validation / Fail-closed Behavior

`validate_template_item_rule_manifest(...)` must fail closed when:

- `template_id` or `source_path` is empty.
- Duplicate `rule_id`.
- Unknown `chapter_id`.
- Empty `item_title`.
- Unsupported `mode`.
- `mode="conditional"` but `missing_behavior != "delete_segment"`.
- `mode="optional"` but `missing_behavior != "render_unavailable"`.
- `facets_any` is empty for conditional rules copied from the template.
- Any configured `facets_any` value is not in `_FACET_FUND_TYPE_MAP`.
- Any configured facet maps to a `FundType` that is not listed in the rule's `fund_types_any`.
- `fund_types_any` is empty.
- Any `fund_types_any` value is not a supported `FundType`.
- `segment_markers_any` is empty.
- Built-in manifest omits one of the four current template ITEM_RULE blocks or adds an item not present in the current template draft without a documented source.

`load_template_item_rule_manifest()` should call validation before returning the manifest.

## File-level Implementation Plan

### 1. Add ITEM_RULE module

File: `fund_agent/fund/template/item_rules.py`

Implement:

- dataclasses and type aliases listed above
- built-in manifest with four conditional rules
- `load_template_item_rule_manifest()`
- `validate_template_item_rule_manifest(...)`
- `get_template_item_rule(rule_id: str)`
- `evaluate_template_item_rule(...)`
- `evaluate_template_item_rules(...)`
- `rendered_segment_present(...)`

All new functions/classes need complete Chinese docstrings.

### 2. Export public surface

File: `fund_agent/fund/template/__init__.py`

Export the ITEM_RULE dataclasses/helpers. Preserve the lazy renderer import approach introduced to avoid audit/renderer cycles.

### 3. Tests

File: `tests/fund/template/test_item_rules.py`

Add focused tests:

1. Manifest shape
   - `load_template_item_rule_manifest()` returns exactly four built-in rules.
   - Rule ids are stable and unique.
   - Rules point to chapters 1 and 2 only.

2. Source fidelity
   - Built-in rule item titles and facet labels match current template draft wording.
   - Preserve exact labels such as `指数增强基金` and `主动权益基金（价值风格）`.

3. Validation fail-closed
   - Duplicate rule id raises `ValueError`.
   - Unknown chapter id raises `ValueError`.
   - Conditional rule with `render_unavailable` raises `ValueError`.
   - Optional rule with `delete_segment` raises `ValueError`.
   - Empty marker tuple raises `ValueError`.
   - Unsupported fund type raises `ValueError`.

4. Deterministic evaluation
   - `index_fund` triggers index constituents and tracking error rules.
   - `enhanced_index` triggers index constituents, alpha yearly breakdown, and tracking error rules.
   - `active_fund` triggers manager philosophy and alpha yearly breakdown, and deletes tracking error.
   - `bond_fund`, `qdii_fund`, and `fof_fund` delete all four built-in conditional segments.
   - Explicit facet input can trigger a matching rule without NLP.
   - Conflicting explicit facet input fails closed: `bond_fund` + `指数增强基金` raises `ValueError`.
   - Compatible explicit facet input works: `enhanced_index` + `指数增强基金` triggers enhanced-index rules.

5. Optional fixture behavior
   - A local optional rule fixture evaluates to `render` with `render_unavailable`.
   - This proves optional behavior without inventing a built-in optional rule.

6. Segment presence helper
   - Literal marker present -> true.
   - Marker absent -> false.
   - A normal prose sentence containing `跟踪指数` but not the unique segment heading does not count as segment present.
   - Conditional inactive + marker absent is the expected deletion proof.

Existing tests to run:

- `tests/fund/template/test_contracts.py`
- `tests/fund/template/test_renderer.py`
- `tests/fund/audit/test_audit_programmatic.py`

No Service/UI/CLI tests should need behavior changes. Run the relevant regression tests to prove no behavior changed.

### 4. Docs

Allowed docs for implementation:

- `fund_agent/fund/README.md`
  - Add a short current-implementation note that ITEM_RULE manifest exists for deterministic optional/conditional segment policy.
  - State that current built-in rules are four conditional template segments and are not wired into Service/UI.

- `tests/README.md`
  - Add `tests/fund/template/test_item_rules.py` entry and maintenance rule.

Do not modify:

- `docs/design.md`
- control docs
- `docs/fund-analysis-template-draft.md`

The user explicitly requested no design/control/template draft edits for planning. Implementation should also avoid them unless a later accepted review amends the scope.

## Acceptance Commands

Implementation should run and report:

```bash
.venv/bin/python -m pytest tests/fund/template/test_item_rules.py tests/fund/template/test_contracts.py tests/fund/template/test_renderer.py -q
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

If implementation touches `fund_agent/fund/template/__init__.py`, also run:

```bash
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_renderer.py -q
```

to catch import-cycle regressions.

## Review Focus

Reviewers should check:

- ITEM_RULE schema lives in Capability `template/`, not Service/UI/audit.
- Built-in manifest contains only rules actually present in `docs/fund-analysis-template-draft.md`.
- `conditional` means delete segment when not triggered.
- `optional` means render unavailable placeholder when data is absent.
- Evaluation uses explicit `FundType` / explicit facets only; no semantic NLP.
- Validation fails closed on wrong mode/behavior pairs and malformed rules.
- No fund documents, PDFs, caches, or repository access were added.
- No `extra_payload` was introduced.
- The implementation does not wire ITEM_RULE into quality gate or programmatic audit prematurely.

## Risks And Guardrails

| Risk | Guardrail |
|---|---|
| Confusing P6-S3 required labels with ITEM_RULE segments | Keep ITEM_RULE in `item_rules.py`; use distinct `segment_markers_any`; do not alter C2 required marker rules. |
| Inventing optional built-in rules not present in template | Built-in manifest includes only four current conditional rules; optional behavior is covered by test fixtures. |
| Semantic facet inference | Trigger only by standard `FundType` or explicit facet labels supplied as typed input. |
| Renderer scope creep | Do not add conditional sections in P6-S4 unless plan review explicitly accepts it. |
| Future template drift | Manifest validation and source-fidelity tests should fail when rule ids/items/facets drift. |
| Import cycles via template `__init__` | Preserve lazy renderer exports and keep `item_rules.py` independent of renderer/audit. |

## Rollback Plan

If implementation causes unacceptable regressions:

1. Remove `fund_agent/fund/template/item_rules.py` and its exports.
2. Remove `tests/fund/template/test_item_rules.py` and README mentions.
3. Keep existing `CHAPTER_CONTRACT`, renderer, chapter block splitter, and P6-S3 audit unchanged.
4. Do not touch Service/UI/CLI rollback paths; they should not be modified in this slice.

## Open Questions For Review

- Should ITEM_RULE eventually become part of `TemplateContractManifest`, or remain a sibling manifest? Current plan keeps it sibling to avoid destabilizing P6-S1/P6-S3 contracts.
- Should P6-S5 quality gate consume ITEM_RULE decisions? Current plan says no; P6-S5 can decide after ITEM_RULE manifest is accepted.
- Should a future renderer slice add the four conditional sections for triggered fund types? Current plan only machineizes the rules and proves deletion/render policy; rendering those sections is a separate behavior slice.
