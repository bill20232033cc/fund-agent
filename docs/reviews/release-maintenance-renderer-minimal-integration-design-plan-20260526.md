# Renderer Minimal Integration Design Plan

> Date: 2026-05-26
> Role: Controller
> Gate: renderer minimal integration design
> Status: Revised after initial plan review
> Scope: design-only; no renderer implementation authorized

## Evidence Basis

This plan is based on the accepted dev-only chapter audit closeout:

- `docs/reviews/release-maintenance-dev-only-chapter-audit-small-baseline-closeout-20260526.md`
- latest accepted local commit: `f5b91ad`

The accepted evidence proves enough to design a minimal renderer integration because:

- The Fund-layer CHAPTER_CONTRACT sidecar has one material executable requirement for `active_fund` Chapter 3 turnover / style-consistency evidence.
- The dev-only writing audit passed the active-fund Chapter 3 positive, missing-evidence, and compatible `data_gap` controls after one false-positive tuning fix.
- The false-positive case was reproduced, fixed, and covered by regression test.
- The current deterministic MVP, FQ0-FQ6 quality gate, Service/CLI defaults, Host/Agent runtime, Dayu runtime, and repository/source helpers remained unchanged.

The evidence does not authorize implementation yet because:

- Chapter 2 enhanced-index and Chapter 6 bond constraints remain deferred `config_only`, not material renderer requirements.
- The small baseline still lacks clean index, QDII, and pure FOF coverage.
- The current proof is a dev-only audit proof, not a renderer output compatibility proof.
- No plan review has yet accepted the exact renderer input/output contract, test matrix, and no-product-behavior-change boundary.

## Design Goal

Define the smallest future renderer output contract that aligns with the accepted active-fund Chapter 3 writing-audit wording constraints without rewriting the report or changing product quality gates.

The target is not to run the dev-only audit inside the product path. The target is to ensure that, in a later implementation gate, the deterministic renderer can emit Chapter 3 wording that is safe under the already accepted contract.

## Minimal Future Output Contract

For `fund_type_slot == "active_fund"` and Chapter 3 only:

1. If the renderer lacks reviewed turnover-rate or style-change evidence for active-fund Chapter 3, it must not emit a positive claim that the fund's style is stable, style-consistent, or words/actions are consistent.
2. If the renderer uses an insufficiency fallback for that missing evidence, it must include:
   - an explicit insufficiency phrase: `证据不足`
   - an explicit non-inference phrase equivalent to: `不能据此判断风格稳定、风格一致或言行一致`
   - one next minimum validation question that asks for review of annual-report §8 turnover and cross-period holdings / concentration / allocation changes.
3. If future reviewed evidence exists, positive style-consistency wording may only be emitted when it is backed by resolvable evidence anchors in the input contract.

The minimum acceptable future Chapter 3 fallback wording should be semantically equivalent to:

```text
风格稳定性判断：证据不足，当前缺少已复核的换手率或跨期风格变化证据，不能据此判断风格稳定、风格一致或言行一致。
下一步最小验证问题：复核年报§8换手率及跨期行业配置/持仓集中度变化后，风格稳定性和言行一致性判断是否仍成立？
```

This exact wording is a design target, not an implementation change in this gate.

## Proposed Future Implementation Slice

The later implementation gate should be narrow:

- File scope: `fund_agent/fund/template/renderer.py` and focused renderer tests only.
- Render scope: `_render_chapter_3()` only.
- Fund scope: active-fund Chapter 3 only.
- Behavior scope: deterministic wording only; do not add runtime audit execution to `render_template_report()`.
- Input scope: reuse existing renderer inputs and current structured analysis outputs; do not add a new Service input, renderer input field, `ReportEvidenceBundle` projection, or audit call in this slice.

The v1 evidence decision rule must be conservative:

- With current renderer inputs, active-fund Chapter 3 has no explicit reviewed turnover/style-evidence status available to `_render_chapter_3()`.
- Therefore the next implementation must treat active-fund Chapter 3 as the missing-reviewed-evidence path by default and use the insufficiency wording.
- A future positive reviewed-evidence path requires a separate input-contract design gate before implementation.

Preferred future implementation route:

1. Detect active-fund identity from `TemplateRenderInput.structured_data.basic_identity.value["classified_fund_type"]`.
2. For active funds, replace the current generic Chapter 3 style-stability fallback with the accepted insufficiency + non-inference + next-question wording.
3. Keep non-active-fund Chapter 3 output unchanged unless a later fund-type gate accepts a separate contract.
4. For the active-fund missing-reviewed-evidence path, prevent all positive Chapter 3 style-consistency claims from `consistency_result` summary lines and dimension reasons from being emitted as accepted conclusions.
5. Preserve non-judgmental factual lines such as manager identity, disclosed strategy text, holdings snapshot, and manager alignment disclosure.
6. Add focused tests asserting active-fund Chapter 3 contains required insufficiency wording and does not contain unsupported positive stability / style-consistency / words-actions-consistency wording when reviewed evidence is absent.

Non-preferred routes for the next implementation gate:

- Do not invoke `audit_report_writing_bundle()` from renderer.
- Do not project `ReportEvidenceBundle` inside renderer.
- Do not add Service/CLI flags or change `fund-analysis analyze` / `checklist` defaults.
- Do not expand Chapter 2 / Chapter 6 material constraints.
- Do not change FQ0-FQ6 quality gate semantics.

## Boundary Matrix

| Area | Decision |
|---|---|
| Renderer 8-chapter structure | Must remain unchanged |
| Product default `analyze` / `checklist` | Entrypoints, parameters, exit codes, Service control flow, and quality-gate policy must remain unchanged; the future implementation may only change active-fund Chapter 3 missing-evidence report text after an output-changing implementation gate accepts it |
| FQ0-FQ6 quality gate | Must remain unchanged |
| Dev-only report-writing audit | Remains dev-only; not called from product path |
| Host/Agent/dayu runtime | Out of scope |
| `FundDocumentRepository` / PDF / cache / source helpers | Out of scope |
| Scratch outputs / durable fixtures | Out of scope |
| Chapter 2 / Chapter 6 constraints | Deferred, config-only |

## Test Strategy For Future Implementation Gate

Required focused tests:

- Active-fund Chapter 3 with missing turnover/style evidence emits `证据不足`.
- Active-fund Chapter 3 emits the non-inference phrase `不能据此判断风格稳定、风格一致或言行一致`.
- Active-fund Chapter 3 emits a next minimum validation question referencing §8 turnover and cross-period style evidence.
- Active-fund Chapter 3 missing-evidence path does not emit positive style-stability / style-consistency claim.
- Active-fund Chapter 3 with a green/aligned `ConsistencyCheckResult` still suppresses unsupported `风格一致` / `言行一致` accepted-conclusion wording when reviewed turnover/style evidence is absent.
- Rendered active-fund Chapter 3 is wrapped as a `ChapterDraftSurrogate` and passed to `audit_report_writing_bundle()` in test-only mode with a compatible `data_gap`; the result must not emit `unsupported_stability_claim` or `insufficient_evidence_wording_missing`.
- Existing renderer chapter count and headings remain unchanged.
- `result.audit_input.chapter_blocks == result.chapter_blocks` remains true.
- Evidence appendix remains present, and Chapter 3 missing-evidence appendix references such as `[M3]` or an equivalent Chapter 3 evidence boundary are not lost.
- Forbidden investment advice validation remains effective.
- Existing ITEM_RULE and preferred_lens renderer tests remain passing.

Required adjacent tests:

- `uv run pytest tests/fund/template/test_renderer.py`
- `uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py`
- `uv run pytest tests/fund/template`
- `uv run ruff check fund_agent/fund/template/renderer.py tests/fund/template/test_renderer.py`
- `git diff --check`

Required dev-only confidence check:

- Build a `ChapterDraftSurrogate` from the future rendered Chapter 3 active-fund text and run `audit_report_writing_bundle()` in test-only validation. This must remain outside the product path and must not be called by renderer, Service, CLI, or FQ0-FQ6.

## Implementation Gate Entry Conditions

A future implementation gate may start only after:

- This design plan receives at least two independent plan reviews.
- Controller judgment accepts or revises every review finding.
- `docs/design.md` records this as an accepted future design, not a current implementation fact.
- `docs/implementation-control.md` marks the next entry point as a renderer minimal implementation gate with the exact file/test scope.
- The implementation gate repeats the hard bans: no Service/CLI/FQ0-FQ6/default analyze/checklist behavior changes, no Host/Agent/dayu, no repository/source helper integration, no durable fixture promotion.
- The implementation gate explicitly states that it is output-changing only for active-fund Chapter 3 missing-reviewed-evidence text, while preserving default entrypoints, parameters, exit codes, Service control flow, FQ0-FQ6 semantics, and 8-chapter structure.

## Residual Risks

- The renderer currently has only generic Chapter 3 fallback wording. The later implementation must avoid expanding behavior beyond the accepted active-fund Chapter 3 text contract.
- Existing `ConsistencyCheckResult` wording may still contain positive language in future real inputs. The implementation gate must inspect the exact renderer output and suppress unsupported accepted-conclusion claims in active-fund Chapter 3 missing-reviewed-evidence path.
- This plan does not solve clean index/QDII/FOF coverage, Chapter 2/6 material contracts, or broader natural-language claim coverage.
