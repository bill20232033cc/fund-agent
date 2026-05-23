# P8-S2 Renderer Preferred Lens Application Design Plan（2026-05-21）

## Scope

P8-S2 addresses the Post-P7 residual:

> `preferred_lens` is machine-readable and validated, but `render_template_report()` does not actually use it to change deterministic report emphasis.

This is a design-first slice. The goal is not to paste raw `lens:` statements into Markdown. The goal is to apply lens facts through deterministic renderer slots so the final report behaves differently for different fund types while preserving the 8章 template contract and programmatic audit compatibility.

## Current Code Facts

- `TemplateLensRule` and `resolve_preferred_lens(chapter_id, fund_type)` live in `fund_agent/fund/template/contracts.py`.
- `resolve_preferred_lens(...)` is already consumed by extraction score / quality gate to prove template applicability.
- `render_template_report()` currently reads `classified_fund_type` from `structured_data.basic_identity.value`, but only renders generic text:
  - Chapter 0: “本报告先识别基金类型，再应用对应 preferred_lens。”
  - Chapter 1: “先看基金类型、业绩基准、成本底座和 preferred_lens。”
- `TemplateRenderResult` currently exposes `report_markdown`, `audit_input`, `evidence_anchors`, and `chapter_blocks`.
- `FundAnalysisService` already fails before rendering if P1 structured data lacks a valid `classified_fund_type`.
- Renderer unit tests still cover a direct missing-data path where `basic_identity.value` can be `None`; that path verifies explicit data insufficiency rendering and audit compatibility.

## Design Decision

Implement a Capability-owned structured lens application layer:

```text
fund_agent/fund/template/lens_application.py
```

Do not put renderer-specific focus labels into `contracts.py`; `contracts.py` remains the CHAPTER_CONTRACT source. Do not move this logic to Service/UI/Engine; lens application is a template rendering concern inside Fund Capability.

New public model:

- `LensApplicationPlan`
- `LensChapterApplication`
- `build_lens_application_plan(fund_type: FundType, chapter_ids: tuple[int, ...] = tuple(range(8)))`

`TemplateRenderResult` should expose:

- `lens_application_plan: LensApplicationPlan | None`

Renderer should consume the plan for deterministic wording in existing slots. It should not append a new “preferred_lens” section and should not render raw `TemplateLensRule.statements`.

## Lens Application Contract

### `LensChapterApplication`

Fields:

- `chapter_id: int`
- `lens_key: LensKey`
- `used_default: bool`
- `primary_focus: str`
- `watch_variable_label: str | None`
- `risk_focus_label: str | None`
- `source_statements: tuple[str, ...]`

### `LensApplicationPlan`

Fields:

- `fund_type: FundType`
- `chapters: tuple[LensChapterApplication, ...]`

Validation:

- `fund_type` must be one of the standard `FundType` values.
- `chapter_ids` must be non-empty, unique, and within `0..7`.
- Every requested chapter must resolve through `resolve_preferred_lens(...)`.
- Unknown fund type, unknown chapter id, duplicate chapter id, or missing lens fallback raises `ValueError`.

## Normalized Focus Labels

P8-S2 first slice uses deterministic normalized labels keyed by standard fund type.

| fund_type | primary_focus | watch_variable_label | risk_focus_label |
|---|---|---|---|
| `active_fund` | 基金经理、超额收益稳定性、言行一致性 | 基金经理言行一致性与超额收益稳定性 | 基金经理变更、风格漂移或超额收益失效 |
| `index_fund` | 跟踪误差、费率、规模/流动性 | 跟踪误差、费率和规模流动性 | 跟踪误差扩大、规模过小或流动性恶化 |
| `bond_fund` | 信用风险、久期稳定性、最大回撤 | 信用风险、久期稳定性和最大回撤 | 信用风险暴露、久期漂移或回撤失控 |
| `enhanced_index` | 超额收益稳定性、跟踪误差、费率 | 指数增强超额收益来源与跟踪误差 | 增强失效、跟踪误差扩大或费率侵蚀 |
| `qdii_fund` | 汇率风险、跨境市场暴露、成本 | 汇率风险、跟踪或管理能力和费率 | 汇率波动、跨境市场暴露或流动性风险 |
| `fof_fund` | 底层基金配置、双重费率、组合分散度 | 底层基金配置、双重费率和分散度 | 底层基金重叠、双重费率或配置失衡 |

`default` lens may resolve for a chapter, but the normalized labels come from the requested standard fund type. This avoids rendering generic “default” wording when the fund type itself is known.

## Renderer Output Contract

P8-S2 changes only two existing slots:

1. Chapter 0 required item `当前最值得盯住的变量`
   - Current generic output: `数据不足，当前未提供独立变量识别输入。`
   - New output shape: `{watch_variable_label}。当前公开输入仍需后续证据验证。`

2. Chapter 1 required item `看这类基金最先看什么`
   - Current generic output: `先看基金类型、业绩基准、成本底座和 preferred_lens。`
   - New output shape: `先看{primary_focus}。`

Renderer must also remove visible literal `preferred_lens` wording from the final report. This phrase may remain in code/docstrings/tests where it describes the mechanism, but not in user-visible report Markdown.

No other chapter output changes in P8-S2.

## Missing / Unsupported Fund Type Behavior

Two paths must remain distinct:

1. Service path:
   - `FundAnalysisService` already validates `classified_fund_type` before rendering.
   - P8-S2 does not duplicate Service policy there.

2. Direct renderer path:
   - If `basic_identity.value` is present but `classified_fund_type` is missing or unsupported, `render_template_report()` raises `ValueError`.
   - If `basic_identity.value` is `None`, renderer keeps the existing explicit missing-data behavior and sets `lens_application_plan=None`.

Rationale:

- A present identity without fund type means the renderer would falsely claim lens application while unable to choose one.
- A fully missing identity fixture is already used to prove missing-data rendering and audit compatibility; forcing it to raise would unnecessarily break that existing boundary.

## Implementation Plan

### S1. Add Lens Application Module

Files:

- `fund_agent/fund/template/lens_application.py`
- `fund_agent/fund/template/__init__.py`
- `tests/fund/template/test_contracts.py` or new `tests/fund/template/test_lens_application.py`

Add:

- `LensChapterApplication`
- `LensApplicationPlan`
- `build_lens_application_plan(...)`

Tests:

- Every standard `FundType` builds an 8-chapter plan.
- Invalid fund type fails closed.
- Duplicate chapter ids fail closed.
- Unknown chapter id fails closed.
- At least one default fallback is represented with `used_default=True` when a chapter lacks exact lens.

### S2. Wire Renderer

Files:

- `fund_agent/fund/template/renderer.py`
- `tests/fund/template/test_renderer.py`

Behavior:

- Resolve fund type from `structured_data.basic_identity.value["classified_fund_type"]`.
- Build `LensApplicationPlan` once in `render_template_report(...)`.
- Pass the plan to chapter rendering helpers, or resolve Chapter 0/1 labels before calling helpers.
- Expose `lens_application_plan` on `TemplateRenderResult`.
- Use Chapter 0 and Chapter 1 plan entries for the exact output contract above.
- Keep `ProgrammaticAuditInput` shape unchanged.

Tests:

- `active_fund` render contains “基金经理言行一致性与超额收益稳定性” in Chapter 0 and “先看基金经理、超额收益稳定性、言行一致性” in Chapter 1.
- `index_fund` render contains “跟踪误差、费率和规模流动性” in Chapter 0 and “先看跟踪误差、费率、规模/流动性” in Chapter 1.
- Active and index fixtures assert exact Chapter 0/1 lens-dependent slot text differs as intended.
- Do not require whole-report diff to be limited to those slots: self-consistent fixtures may also differ in non-target factual fields such as Chapter 6 `stress_test_result.fund_type`.
- If comparing report differences, compare only the relevant required item lines inside `chapter_blocks[0]` and `chapter_blocks[1]`.
- Report Markdown does not contain literal `preferred_lens`.
- Existing 8章 structure, evidence appendix, `ProgrammaticAuditInput`, and C2 audit pass are preserved.
- Present `basic_identity` missing `classified_fund_type` raises `ValueError`.
- Fully missing `basic_identity.value` still renders explicit missing-data path and returns `lens_application_plan=None`.

### S3. Docs

Files:

- `fund_agent/fund/README.md`
- `docs/design.md`
- `tests/README.md`
- `docs/implementation-control.md`

Updates:

- Explain that `preferred_lens` is applied through normalized deterministic renderer slots.
- State that raw `lens:` statements are not rendered.
- Clarify FQ5 remains applicability, not renderer compliance.
- Record P8-S2 implementation/review status after acceptance.

## Non-Goals

- Do not implement LLM writing.
- Do not paste raw `TemplateLensRule.statements` into reports.
- Do not change `CHAPTER_CONTRACT` must_answer / required_output_items.
- Do not change Service, UI, Engine, document repository, PDF parser, extraction score, or quality gate behavior.
- Do not change audit issue schema or `ProgrammaticAuditInput`.
- Do not broaden lens output beyond Chapter 0 and Chapter 1 in P8-S2.

## Verification

Targeted:

```bash
pytest tests/fund/template/test_renderer.py tests/fund/template/test_contracts.py tests/fund/audit/test_audit_programmatic.py -q
```

Full:

```bash
pytest
ruff check
git diff --check
```

## Acceptance Criteria

- P8-S2 implementation has an explicit `LensApplicationPlan`.
- Renderer uses lens plan in Chapter 0 and Chapter 1 only.
- At least `active_fund` and `index_fund` produce intentionally different deterministic report emphasis.
- Final report Markdown no longer contains visible literal `preferred_lens`.
- Missing/unsupported fund type behavior is covered by tests.
- Full suite remains green.

## Deferred Questions

- Whether later slices should use lens to alter evidence requirements.
- Whether C2 should eventually verify renderer compliance with the selected lens.
- Whether `fund_quality` should record renderer lens compliance after a future report-output audit exists.
