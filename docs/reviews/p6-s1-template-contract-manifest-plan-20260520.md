# P6-S1 Template Contract Manifest Plan - 2026-05-20

## Verdict

P6-S1 plan drafted. The implementation should create a machine-readable template contract manifest in the Fund Capability layer, using `docs/fund-analysis-template-draft.md` as the source document but not parsing Markdown comments at runtime.

下一 gate：`P6-S1 plan review`。

## Problem

`docs/design.md` defines `CHAPTER_CONTRACT` as a core mechanism: every chapter has `must_answer`, `must_not_cover`, `required_output_items`, and `preferred_lens`. The current renderer emits 8 chapters, but those contracts remain embedded as human-facing Markdown comments in `docs/fund-analysis-template-draft.md`.

P5 closed the main quality-gate gap, but FQ5 still only checks `preferred_lens_resolvability`. It cannot verify that a real chapter contract exists, that all 8 chapter contracts are complete, or that each supported `FundType` can resolve a usable lens for each chapter.

## Design Decision

Do not parse `docs/fund-analysis-template-draft.md` at runtime in P6-S1.

Instead, add a curated Capability manifest that copies the current template contract into typed Python data structures. Reasons:

- The template file is a writer-facing Markdown draft with HTML comments, free-form bullet text, nested `preferred_lens` blocks, and occasional inline metadata such as `facets_any` / `priority`.
- A runtime parser would either be brittle or require building a small DSL parser before any product behavior improves.
- Repository rules require code to be the current implementation truth; the machine contract should be explicit, tested, and importable by Capability modules.
- P6-S1 only establishes the contract surface. It does not yet perform full contract audit or rewrite renderer output.

The template draft remains the human source used to curate the manifest. The manifest becomes the code-consumed source for P6-S2/P6-S3/P6-S5.

## Target Files

Implementation files:

- `fund_agent/fund/template/contracts.py`
- `fund_agent/fund/template/__init__.py`

Tests:

- `tests/fund/template/test_contracts.py`

Docs:

- `fund_agent/fund/README.md`
- `tests/README.md` if test taxonomy needs an entry for template contract tests

Do not modify `render_template_report(...)` in P6-S1 except for import/export wiring if needed. Renderer alignment is P6-S2.

P6-S1 production code must not import renderer private constants such as `_CHAPTER_TITLES`. The manifest should carry its own chapter titles as the P6 machine-contract title source. P6-S2 will decide whether renderer should reuse those public manifest titles or expose a public chapter-splitting helper.

## Public Contract

Add dataclasses in `fund_agent/fund/template/contracts.py`:

- `TemplateLensRule`
  - `fund_type: FundType | Literal["default"]`
  - `statements: tuple[str, ...]`
  - `facets_any: tuple[str, ...]`
  - `priority: str | None`
- `ChapterContract`
  - `chapter_id: int`
  - `title: str`
  - `narrative_mode: str`
  - `must_answer: tuple[str, ...]`
  - `must_not_cover: tuple[str, ...]`
  - `required_output_items: tuple[str, ...]`
  - `preferred_lens: Mapping[str, TemplateLensRule]`
- `TemplateContractManifest`
  - `template_id: str`
  - `source_path: str`
  - `chapters: tuple[ChapterContract, ...]`

Add functions:

- `load_template_contract_manifest() -> TemplateContractManifest`
- `get_chapter_contract(chapter_id: int) -> ChapterContract`
- `resolve_preferred_lens(chapter_id: int, fund_type: FundType) -> TemplateLensRule`
- `validate_template_contract_manifest(manifest: TemplateContractManifest) -> None`

All functions need complete Chinese docstrings. Exceptions should fail closed:

- missing chapter id -> `ValueError`
- duplicate chapter id -> `ValueError`
- chapter count not exactly 8 or ids not `0..7` -> `ValueError`
- missing required fields -> `ValueError`
- unsupported lens key -> `ValueError`
- `resolve_preferred_lens(...)` cannot find fund type and no default -> `ValueError`

## Schema Rules

1. Chapter ids are integers `0..7`, matching current renderer headings and `docs/design.md` section 3.1.
2. Titles must match `docs/design.md` section 3.1 and the current 0-7 chapter headings in `docs/fund-analysis-template-draft.md`.
3. Lens keys must reuse existing `FundType` values:
   - `index_fund`
   - `active_fund`
   - `bond_fund`
   - `enhanced_index`
   - `qdii_fund`
   - `fof_fund`
4. `default` is allowed as fallback lens only where the template actually defines it.
5. `must_answer`, `must_not_cover`, and `required_output_items` must be non-empty for all chapters.
6. P6-S1 should preserve template wording without inventing new contract text.

## Minimal Manifest Content

P6-S1 must cover all 8 chapters. It is acceptable to copy the full contract text manually from `docs/fund-analysis-template-draft.md` into Python tuples. To keep the first slice reviewable, `ITEM_RULE` should not be implemented here; it remains P6-S4.

For each chapter, include:

- `narrative_mode`
- complete `must_answer`
- complete `must_not_cover`
- complete `required_output_items`
- preferred_lens entries present in the template

If a chapter has no `default` lens, `resolve_preferred_lens(...)` should require a concrete supported `FundType`.

## Tests

Add tests that prove:

1. `load_template_contract_manifest()` returns exactly 8 chapters with ids `0..7`.
2. Chapter titles match `docs/design.md` section 3.1 and no production code imports renderer private constants.
3. Every chapter has non-empty `narrative_mode`, `must_answer`, `must_not_cover`, `required_output_items`, and `preferred_lens`.
4. Every supported `FundType` resolves a lens for every chapter, either exact or default fallback.
5. Invalid manifest cases fail closed:
   - duplicate chapter id
   - missing chapter id
   - empty `must_answer`
   - unsupported lens key
6. `get_chapter_contract(0)` returns the contract for 第 0 章 and includes a known output item such as `下一步最小验证问题`.

Suggested command:

```bash
.venv/bin/python -m pytest tests/fund/template/test_contracts.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

## Non-goals

- Do not add contract audit to `run_programmatic_audit(...)`; that is P6-S3.
- Do not modify report output structure; that is P6-S2.
- Do not parse `ITEM_RULE`; that is P6-S4.
- Do not upgrade quality gate FQ5 yet; that is P6-S5.
- Do not introduce LLM audit, Evidence Confirm, or PDF evidence re-search.
- Do not auto-fix duplicate `016492`.
- Do not auto-map thermometer values to `valuation_state`.

## Review Focus

Plan review should challenge:

- Whether a Python manifest is the right first machine source instead of parsing Markdown.
- Whether the schema is too broad or too narrow for P6-S2/P6-S3/P6-S5.
- Whether `FundType` reuse fully avoids new template-specific type names.
- Whether fail-closed validation catches realistic manifest drift.
- Whether P6-S1 stays inside Capability and avoids Service/UI ownership creep.
- Whether the manifest becomes the machine contract title source without depending on renderer private implementation details.

## Plan Review Patch

Controller plan review found that the original title check could push implementation toward importing renderer private `_CHAPTER_TITLES` or maintaining two unowned title sources. The plan is patched as follows:

- `contracts.py` owns P6 machine-contract chapter titles.
- Production code must not import renderer private constants.
- Tests should validate titles against design/template expectations, not by coupling contract code to renderer internals.
- Renderer title alignment remains P6-S2.
