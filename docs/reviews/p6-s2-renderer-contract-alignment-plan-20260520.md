# P6-S2 Renderer Contract Alignment Plan - 2026-05-20

## Verdict

P6-S2 plan drafted. Implementation should align the current template renderer with the P6-S1 machine contract by making contract-owned chapter id/title the renderer-facing public surface and by exposing stable rendered chapter blocks that downstream P6-S3 contract audit can locate.

下一 gate：`P6-S2 plan review`。

## Inputs

- Design truth: `docs/design.md`
- Control doc: `docs/implementation-control.md`
- P6 backlog: `docs/reviews/post-p5-follow-up-planning-20260520.md`
- P6-S1 accepted implementation commit: `a1fa26a`
- P6-S1 controller judgment: `docs/reviews/p6-s1-code-review-controller-judgment-20260520.md`

## Current Code Facts

`fund_agent/fund/template/contracts.py` now owns the machine-readable `CHAPTER_CONTRACT` manifest:

- `TemplateContractManifest.chapters` covers chapter ids `0..7`.
- `ChapterContract` exposes `chapter_id`, `title`, `narrative_mode`, `must_answer`, `must_not_cover`, `required_output_items`, and `preferred_lens`.
- `load_template_contract_manifest()`, `get_chapter_contract(...)`, `resolve_preferred_lens(...)`, and `validate_template_contract_manifest(...)` are public exports through `fund_agent.fund.template`.
- The module explicitly states it does not depend on renderer private constants.

`fund_agent/fund/template/renderer.py` still has a renderer-private title source:

- `_CHAPTER_TITLES` is defined privately and used by `_render_chapter_0(...)` through `_render_chapter_7(...)`.
- `render_template_report(...)` builds a tuple of 8 chapter strings plus the `## 证据与出处` appendix, joins them into `report_markdown`, and returns `TemplateRenderResult`.
- `TemplateRenderResult` currently exposes only `report_markdown`, `audit_input`, and `evidence_anchors`; it does not expose per-chapter ids, titles, contracts, heading text, body text, or character ranges.
- `_missing_anchor_reference(...)` also reads `_CHAPTER_TITLES`, so missing evidence appendix text has a second dependency on private titles.

`tests/fund/template/test_renderer.py` currently locks user-visible Markdown compatibility:

- It asserts exact 8 headings such as `# 0. 投资要点概览` and `# 7. 是否值得持有——最终判断`.
- It asserts `report_markdown.count("\n# ") == 7` and `report_markdown.startswith("# 0. 投资要点概览")`.
- It verifies rendered output still passes `run_programmatic_audit(...)` for P1/P2/P3/L1/R1/R2.
- It verifies evidence anchor formatting, missing evidence appendix entries, non-annual source labeling, missing-data wording, final judgment restrictions, and forbidden trading terms.

Risk in the current state:

- There are two chapter-title sources: contract manifest titles and renderer `_CHAPTER_TITLES`.
- Downstream code cannot locate chapter blocks without reparsing headings ad hoc.
- Any P6-S3 contract audit would either duplicate Markdown parsing or rely on renderer private details.
- P1 programmatic audit currently has its own partial title tuple in `fund_agent/fund/audit/audit_programmatic.py`; P6-S2 should not refactor audit behavior, but this drift is a review focus for P6-S3.

## Design Goals

P6-S2 should make the renderer contract-aligned while preserving current Markdown output.

Goals:

- Use the P6-S1 public manifest as the single renderer title source.
- Expose stable chapter id/title metadata for each rendered report chapter.
- Provide a public Markdown chapter-splitting helper that can parse current report Markdown into chapter blocks associated with `ChapterContract`.
- Add rendered blocks to `TemplateRenderResult` so P6-S3 can audit exact chapter text without rebuilding parser logic.
- Preserve current report Markdown headings, appendix, evidence lines, audit input compatibility, and Service/UI behavior.

Non-goals:

- Do not implement `ITEM_RULE`.
- Do not implement contract audit or add new audit rule codes.
- Do not upgrade quality gate FQ5.
- Do not add LLM audit, Evidence Confirm, PDF re-search, or evidence matching.
- Do not change Service/UI behavior.
- Do not rewrite report prose or change existing Markdown structure except internal title sourcing.
- Do not refactor `fund_agent/fund/audit/audit_programmatic.py` unless a tiny import/export adjustment is strictly necessary; contract-aware audit belongs to P6-S3.

## Target Public Contract

Add a renderer-side dataclass in `fund_agent/fund/template/renderer.py`:

`RenderedChapterBlock`

- `chapter_id: int`
- `title: str`
- `heading: str`
- `markdown: str`
- `body_markdown: str`
- `contract: ChapterContract`

Semantics:

- `chapter_id` and `title` must come from `ChapterContract`.
- `heading` is the exact Markdown heading line, for example `# 2. R=A+B-C 收益归因`.
- `markdown` is the exact rendered block including the heading.
- `body_markdown` is the block content after the first heading line, stripped only of the surrounding newlines needed for block extraction.
- `contract` is the manifest contract for the same chapter id.

Add public helpers:

`get_template_chapter_heading(chapter_id: int) -> str`

- Returns `# {chapter_id}. {title}` using `get_chapter_contract(chapter_id)`.
- Raises `ValueError` through the contract accessor when chapter id is unsupported.
- Must have complete Chinese docstring with Args/Returns/Raises.

`split_rendered_chapter_blocks(report_markdown: str) -> tuple[RenderedChapterBlock, ...]`

- Parses only top-level template chapter headings matching `# {id}. {title}`.
- Returns exactly chapters `0..7` in order.
- Associates every returned block with the public `ChapterContract`.
- Excludes the `## 证据与出处` appendix from chapter 7 body; appendix remains part of `report_markdown`.
- Raises `ValueError` fail-closed when:
  - `report_markdown` is empty or whitespace-only.
  - any chapter id is missing, duplicated, out of order, or outside `0..7`.
  - a heading id exists but title does not match the manifest contract title.
  - non-template top-level `#` heading appears in the rendered report.

Extend `TemplateRenderResult`:

- Add `chapter_blocks: tuple[RenderedChapterBlock, ...]`.
- Append `chapter_blocks` after the existing fields in the dataclass to minimize public construction churn; the repo currently constructs `TemplateRenderResult(...)` only inside `renderer.py`, but the type is publicly exported.
- Existing fields must remain unchanged: `report_markdown`, `audit_input`, `evidence_anchors`.
- `render_template_report(...)` should populate `chapter_blocks` from the final `report_markdown` by calling `split_rendered_chapter_blocks(report_markdown)`, so the public split helper and renderer output share one code path.

Implementation notes:

- Replace `_CHAPTER_TITLES` with contract-based title access. A private helper such as `_chapter_title(chapter_id: int) -> str` is acceptable only if it calls `get_chapter_contract(...)`.
- `_render_chapter_0(...)` through `_render_chapter_7(...)` should call `get_template_chapter_heading(chapter_id)` or a small wrapper, not index a local title tuple.
- `_missing_anchor_reference(...)` should use `get_chapter_contract(chapter_index).title`.
- If type annotations need `ChapterContract`, import it explicitly from `contracts.py`.
- If downstream users may need the type alias noted in P6-S1 review, exporting `LensKey` is optional and not required for this slice.
- Every new function/class needs a complete Chinese docstring. Complex parsing logic needs concise Chinese inline comments explaining the boundary between 8 report chapters and the appendix.

## File Scope

Implementation files allowed:

- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/template/__init__.py`
- `fund_agent/fund/template/contracts.py` only if a tiny public helper is demonstrably cleaner than importing existing accessors; do not change manifest content.

Tests allowed:

- `tests/fund/template/test_renderer.py`
- `tests/fund/template/test_contracts.py` only for export/helper coverage if needed.

Docs allowed during implementation:

- `fund_agent/fund/README.md` because `fund_agent/fund/template/` behavior changes.
- `tests/README.md` because renderer tests will cover chapter block contract alignment.
- `docs/implementation-control.md` only after implementation/review acceptance, by controller or an explicitly authorized bookkeeping step.

Files not allowed in P6-S2 implementation:

- Service/UI code.
- `fund_agent/fund/audit/audit_programmatic.py` except for a strictly mechanical import/export need approved in review.
- Quality gate, extraction, fund type, document repository, or CLI code.
- Template source wording in `docs/fund-analysis-template-draft.md`.

## Test Strategy

Extend existing renderer tests, preserving current assertions.

Required test additions:

1. Contract title sourcing
   - Render a report and assert every `chapter_block.title` equals `get_chapter_contract(chapter_id).title`.
   - Assert rendered headings are exactly `# {chapter_id}. {contract.title}`.
   - Do not import or inspect renderer private `_CHAPTER_TITLES`.

2. Chapter block shape
   - Assert `result.chapter_blocks` has exactly 8 blocks with ids `0..7`.
   - Assert each block has a non-empty `markdown`, `body_markdown`, `heading`, and `contract`.
   - Assert `result.chapter_blocks[2].contract.required_output_items` is available, proving P6-S3 can reach the contract from the block.

3. Public splitter compatibility
   - Call `split_rendered_chapter_blocks(result.report_markdown)` and assert it equals or field-matches `result.chapter_blocks`.
   - Assert the appendix `## 证据与出处` is not swallowed into chapter 7 `body_markdown`.
   - Assert joining block markdown with blank lines remains a prefix of `report_markdown`, preserving existing Markdown layout.

4. Fail-closed parser paths
   - Missing chapter heading raises `ValueError`.
   - Duplicate chapter heading raises `ValueError`.
   - Wrong title for a valid chapter id raises `ValueError`.
   - Out-of-order chapter ids raise `ValueError`.
   - Unexpected top-level `#` heading raises `ValueError`.

5. Markdown compatibility
   - Keep current tests that assert exact headings, count of `\n# `, evidence anchors, missing-data wording, forbidden terms, and audit compatibility.
   - Add an explicit assertion that `result.audit_input.report_markdown == result.report_markdown` still holds after adding `chapter_blocks`.
   - Add an explicit assertion that the existing `report_markdown`, `audit_input`, and `evidence_anchors` fields remain accessible with the same semantics after `chapter_blocks` is added.

Suggested validation commands for implementation agent:

```bash
.venv/bin/python -m pytest tests/fund/template/test_contracts.py tests/fund/template/test_renderer.py -q
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

## Implementation Steps

1. Import the manifest accessors in `renderer.py`.
   - Add `ChapterContract` and `get_chapter_contract` imports.
   - Avoid importing any private state from `contracts.py`.

2. Add `RenderedChapterBlock`.
   - Place it near `TemplateRenderResult`.
   - Include full Chinese class docstring.

3. Add `get_template_chapter_heading(chapter_id)`.
   - Build headings from `get_chapter_contract(chapter_id).title`.
   - Use it in every `_render_chapter_*` heading.

4. Remove renderer title drift.
   - Delete `_CHAPTER_TITLES`.
   - Update `_missing_anchor_reference(...)` to read the title from `get_chapter_contract(chapter_index)`.

5. Implement `split_rendered_chapter_blocks(report_markdown)`.
   - Use a compiled top-level chapter heading regex such as `^#\s+(\d+)\.\s+(.+?)\s*$`.
   - Treat `## 证据与出处` and lower-level headings as non-chapter content.
   - Validate exact ids `0..7`, order, no duplicates, and title equality with contract.
   - Return immutable tuple of `RenderedChapterBlock`.

6. Populate `TemplateRenderResult.chapter_blocks`.
   - After `report_markdown` is built and wording validation passes, call the splitter.
   - Pass the blocks into the result.
   - Keep `audit_input` exactly as before.

7. Export the new public surface.
   - Add `RenderedChapterBlock`, `get_template_chapter_heading`, and `split_rendered_chapter_blocks` to `fund_agent/fund/template/__init__.py`.

8. Update tests.
   - Extend `tests/fund/template/test_renderer.py` with the required tests above.
   - Keep current fixture builders and current Markdown compatibility assertions.
   - Do not add tests that inspect renderer private variables.

9. Update docs after tests pass.
   - Update `fund_agent/fund/README.md` to say renderer now returns per-chapter `RenderedChapterBlock` values associated with `CHAPTER_CONTRACT`.
   - Update `tests/README.md` renderer test entry to mention contract-aligned chapter block coverage.
   - Do not update `docs/implementation-control.md` until implementation/review acceptance unless controller explicitly asks.

## Review Focus

Reviewers should focus on:

- Does renderer use contract manifest titles instead of maintaining a second title tuple?
- Does `RenderedChapterBlock` provide enough location surface for P6-S3 without embedding audit behavior?
- Does Markdown output remain byte-for-byte compatible for existing headings, evidence lines, appendix, and audit input?
- Does `split_rendered_chapter_blocks(...)` fail closed on malformed Markdown instead of silently returning partial blocks?
- Does the implementation avoid Service/UI changes and avoid changing programmatic audit behavior?
- Are tests proving no dependency on private `_CHAPTER_TITLES` by using public contract accessors?

## Risks And Guardrails

- Parser overreach: Keep splitter limited to current renderer Markdown, not a general Markdown parser.
- Audit scope creep: Do not inspect `must_answer`, `must_not_cover`, or `required_output_items` content in P6-S2. Only attach contracts to blocks.
- Compatibility regression: Adding `chapter_blocks` must not alter `report_markdown` or `ProgrammaticAuditInput`.
- Appendix boundary: Ensure `## 证据与出处` stays outside chapter 7 block so P6-S3 can audit chapter 7 prose separately from global evidence appendix.
- Drift with audit `_REQUIRED_CHAPTER_TITLES`: Record as P6-S3 review focus; do not refactor audit in this slice.

## Open Questions

- Should `RenderedChapterBlock` include character offsets (`start_index`, `end_index`) in addition to `markdown`? Current plan does not require offsets because exact block Markdown is enough for P6-S3 deterministic audit. Add offsets only if plan review decides location precision needs them now.
- Should `split_rendered_chapter_blocks(...)` live in `renderer.py` or a new `chapter_blocks.py`? Current plan keeps it in `renderer.py` to minimize files and because it parses renderer-owned Markdown.
