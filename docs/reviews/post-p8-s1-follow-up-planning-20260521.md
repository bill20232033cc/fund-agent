# Post-P8-S1 Follow-up Planning（2026-05-21）

## Current State

P8-S1 `must_answer` audit contract implementation and controller review are complete.

Accepted commits:

- `f3bbfc9`：P8-S1 must_answer audit contract plan/review
- `5f5a7a6`：P8-S1 must_answer coverage implementation
- `601e72c`：P8-S1 controller review artifact and control-doc gate update

Latest verified baseline:

```text
pytest -> 329 passed
ruff check -> passed
git diff --check -> passed
tracked worktree clean
```

## Residual Reconciliation

### Closed by P8-S1

`R1. must_answer Audit Consumption` is closed for the deterministic contract-routing slice.

Current fact:

- `ContractAuditCoverageManifest` covers all 45 current `CHAPTER_CONTRACT.must_answer` questions.
- Current routing is 44 `covered_by_required_item`, 1 `narrative_guidance`, 0 `programmatic_marker`.
- `ProgrammaticContractRules` remains the deterministic C2 marker model.
- Non-programmatic coverage is documented as routing/observability, not C2 semantic proof.

Remaining future work from this area:

- LLM semantic audit, evidence confirm, and structured-data availability remain separate future audit slices.
- C2 marker granularity can be revisited only when a specific required item proves too broad in practice.

### Next Highest Priority

`R2. Renderer preferred_lens Application` is now the next design item.

Current code facts:

- `preferred_lens` is machine-readable and validated in `fund_agent/fund/template/contracts.py`.
- `resolve_preferred_lens(chapter_id, fund_type)` is consumed by extraction score / quality gate to prove template applicability.
- `run_extraction_score()` records per-chapter lens resolution facts in `fund_quality`.
- `render_template_report()` does not resolve chapter-specific lens rules or use them to change deterministic report emphasis.
- Current renderer text contains generic phrases such as “再应用对应 preferred_lens” and “先看基金类型、业绩基准、成本底座和 preferred_lens”, but those phrases are not actual lens application.

## Controller Decision

Proceed to:

```text
P8-S2 renderer preferred_lens application design
```

This must be a design-first slice.

Rationale:

- Renderer output is user-visible and feeds programmatic audit input.
- `preferred_lens` is currently only an applicability fact; applying it to report output changes template semantics.
- A naive implementation that pastes lens strings into Markdown would create visible meta-instructions, not better fund analysis.
- The renderer is deterministic MVP template filling, not an LLM prompt runtime, so lens application must be representable as deterministic rendering choices or a structured planning artifact.

## P8-S2 Design Scope

Goal:

- Define how `preferred_lens` affects deterministic template rendering without leaking raw lens instructions into the final report.

Required design decisions:

1. Application level
   - chapter planning only
   - visible section wording
   - item ordering
   - evidence requirement hints
   - audit/quality-gate applicability only

2. Contract ownership
   - whether lens application belongs in `template/contracts.py`, `template/renderer.py`, or a new `template/lens_application.py`
   - how to keep Capability ownership clear and avoid Service/UI/Engine coupling

3. Renderer input/output contract
   - whether `TemplateRenderInput` should require explicit `fund_type`
   - whether fund type should be read from `structured_data.basic_identity.value["classified_fund_type"]`
   - whether `TemplateRenderResult` should expose structured lens application facts for later audit

4. Deterministic behavior
   - what exact output differences should exist for at least two fund types
   - which chapters are first affected
   - how missing or unsupported fund type fails closed

5. Audit and docs
   - what C2 proves after lens application, if anything
   - how README/design distinguish “lens as generation guidance” from raw visible report text

## Initial Preferred Approach For P8-S2 Plan

Use a structured `LensApplicationPlan` rather than dumping `TemplateLensRule.statements` into Markdown.

Recommended shape:

- Capability-owned module, likely `fund_agent/fund/template/lens_application.py`.
- Public helper such as `build_lens_application_plan(fund_type, chapter_ids=...)`.
- Plan entries include:
  - `chapter_id`
  - resolved `lens_key`
  - `used_default`
  - normalized `primary_focus`
  - optional deterministic `watch_variable_label`
  - optional deterministic `risk_focus_label`
  - source `TemplateLensRule` for traceability, but not raw-rendered by default
- `render_template_report()` consumes the plan to select existing sentence slots, not to append a new explanatory section.

Suggested first deterministic output differences:

- Chapter 0 “当前最值得盯住的变量”
  - `active_fund`: 基金经理、超额收益稳定性、言行一致性
  - `index_fund`: 跟踪误差、费率、规模/流动性
  - `bond_fund`: 信用风险、久期稳定性、最大回撤
- Chapter 1 “看这类基金最先看什么”
  - use normalized lens focus labels instead of the literal word `preferred_lens`

Non-goals:

- Do not implement LLM writing.
- Do not paste raw `lens:` statements into report Markdown.
- Do not alter `CHAPTER_CONTRACT` content in this slice unless the design proves it necessary.
- Do not make Service/UI choose lens behavior.
- Do not weaken quality gate FQ5; it remains applicability, not renderer-compliance proof.

## Acceptance Criteria For P8-S2 Plan/Review

- Plan includes a concrete first-slice output contract with exact chapters and fields affected.
- Plan defines fail-closed behavior for missing/unsupported `classified_fund_type`.
- Plan explains why the implementation belongs in Capability template code.
- Plan includes targeted tests for at least two fund types showing intentionally different renderer output while preserving:
  - 8章 structure
  - evidence appendix
  - `ProgrammaticAuditInput`
  - current C2 required marker behavior
- Plan states whether docs to update are `fund_agent/fund/README.md`, `docs/design.md`, `tests/README.md`, or all three.

## Deferred Items

These remain behind P8-S2 unless user reprioritizes:

- `P8-S3 source fallback policy design`
- `P8-S4 preflight quality gate optimization design`
- LLM semantic audit / evidence confirm for non-programmatic `must_answer`
- Further C2 marker granularity hardening

## Next Gate

```text
P8-S2 renderer preferred_lens application design plan/review
```
