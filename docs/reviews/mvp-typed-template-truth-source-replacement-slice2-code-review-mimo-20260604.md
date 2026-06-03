# MVP typed template truth-source replacement Slice 2 code review (AgentMiMo)

## Gate context

- Gate: `MVP typed template truth-source replacement gate`
- Classification: `heavy`
- Slice: Slice 2 — parse template doc into current untyped manifest
- Review date: 2026-06-04
- Reviewer: AgentMiMo

## Verdict

**PASS**

## Review target files

- `fund_agent/fund/template/contracts.py` (staged + unstaged changes)
- `tests/fund/template/test_contracts.py` (unstaged changes)
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md` (untracked)

## Findings

### F1 — RuntimeWarning on `uv run python -m` CLI validation (LOW / non-blocking)

The controller observed a `runpy RuntimeWarning` when running `uv run python -m fund_agent.fund.template.contracts --validate-template-doc`. The warning is:

```text
<frozen runpy>:128: RuntimeWarning: 'fund_agent.fund.template.contracts' found in sys.modules
after import of package 'fund_agent.fund.template', but prior to execution of
'fund_agent.fund.template.contracts'; this may result in unpredictable behaviour
```

**Root cause**: `fund_agent/fund/template/__init__.py` imports from `contracts`, so when `runpy` tries to execute `contracts` as `__main__`, the module is already in `sys.modules`. This is a standard Python packaging edge case, not a logic error.

**Assessment**: Non-blocking. The CLI output is correct (`template_contract_manifest=valid template_id=fund-analysis-template-v1 chapters=8`) and exit code is `0`. The warning does not affect correctness. This is a known `runpy` behavior when a submodule is both imported by its package and executed as `__main__`. A future slice could add a `contracts/__main__.py` entry or use `if __name__ == "__main__"` guard with `__init__.py` import deferral to suppress, but this is cosmetic and out of Slice 2 scope.

**Severity**: LOW

### F2 — No other blocking findings

All other review checks pass cleanly. See detailed analysis below.

## Detailed analysis

### 1. Template truth source: Python authored content removed

`contracts.py` no longer contains any Python-authored `_CHAPTERS`, `_lens`, `_chapter` or similar constant content. The old Python-authored `TemplateContractManifest` construction from hardcoded constants is fully replaced by `_load_template_contract_manifest_from_path()` which reads and parses `docs/fund-analysis-template-draft.md`.

**Verdict**: PASS

### 2. Exactly one TEMPLATE_CONTRACT_MANIFEST_JSON extraction with stdlib json parse

`_parse_template_contract_manifest_json()` (line 306-337):
- Uses `_extract_template_manifest_blocks()` to find all blocks delimited by `TEMPLATE_CONTRACT_MANIFEST_JSON` / `END_TEMPLATE_CONTRACT_MANIFEST_JSON` markers
- Rejects zero blocks (`"缺少 TEMPLATE_CONTRACT_MANIFEST_JSON 区块"`)
- Rejects multiple blocks (`"TEMPLATE_CONTRACT_MANIFEST_JSON 区块必须 exactly one"`)
- Rejects empty block (`"TEMPLATE_CONTRACT_MANIFEST_JSON 区块不能为空"`)
- Uses `json.loads(block)` for strict stdlib JSON parse
- Rejects non-dict top-level (`"顶层必须是 JSON object"`)
- Rejects unknown top-level keys via `_reject_unknown_keys()`

**Verdict**: PASS

### 3. Fail-closed validation coverage

| Failure mode | Implementation | Test coverage |
|---|---|---|
| Missing block | `_parse_template_contract_manifest_json` raises ValueError | `test_template_doc_parser_fails_closed_for_missing_empty_duplicate_or_malformed_json` (parametrized) |
| Duplicate blocks | Same | Same test, parametrized case |
| Empty block | Same | Same test, parametrized case |
| Non-JSON block | Same, catches `json.JSONDecodeError` | Same test, parametrized case |
| Unknown top-level keys | `_reject_unknown_keys(parsed, _TOP_LEVEL_KEYS, "manifest")` | `test_template_doc_parser_rejects_unknown_keys_at_nested_levels` (manifest level) |
| Unknown chapter keys | `_require_exact_keys(raw_chapter, _CHAPTER_KEYS, path)` | Same test (chapter level) |
| Unknown lens keys | `_require_exact_keys(raw_rule, _LENS_RULE_KEYS, rule_path)` | Same test (lens level) |
| Unknown item keys | `_require_exact_keys(raw_entry, ...)` per field | Same test (must_answer, must_not_cover, required_output_items levels) |
| Chapter ID drift (index != chapter_id) | `if chapter_id != index: raise ValueError` | `test_template_doc_parser_rejects_chapter_id_id_text_and_lens_drift` |
| Public chapter IDs drift | `public_chapter_ids != _EXPECTED_PUBLIC_CHAPTER_IDS` | Same test |
| Stable ID shape | `_validate_entry_id()` checks `chN.<field>.item_XX` pattern | Same test |
| Empty text | `_read_required_string()` rejects empty/whitespace | Same test |
| Unsupported lens key | `lens_key not in _SUPPORTED_LENS_KEYS` | Same test |
| Lens key/fund_type mismatch | `fund_type != lens_key` | Same test |
| Unsupported priority | `_read_optional_priority()` closed-set check | Same test |
| Unsupported when_evidence_missing | Closed-set check against `_REQUIRED_OUTPUT_MISSING_BEHAVIORS` | Same test |
| Nested blocks/malformed markers | `_extract_template_manifest_blocks()` validates nesting | Tested via parametrized cases |

**Verdict**: PASS — comprehensive fail-closed coverage at all levels.

### 4. Untyped projection public API compatibility

The following public APIs are preserved with identical signatures and behavior:

- `load_template_contract_manifest() -> TemplateContractManifest` — now reads from template doc, returns same dataclass
- `get_chapter_contract(chapter_id: int) -> ChapterContract` — unchanged behavior
- `resolve_preferred_lens(chapter_id: int, fund_type: FundType) -> TemplateLensRule` — unchanged behavior
- `validate_template_contract_manifest(manifest: TemplateContractManifest) -> None` — unchanged behavior

Dataclasses `TemplateContractManifest`, `ChapterContract`, `TemplateLensRule` are unchanged in shape.

`test_current_untyped_manifest_projects_slice1_template_json_values` validates that the parsed manifest projects the same values as the canonical template JSON, field by field.

**Verdict**: PASS

### 5. Deterministic renderer/default behavior

No renderer, default `analyze/checklist`, or Service code was modified. `contracts.py` only changes the manifest source; the public dataclass API consumed by renderer and Service is unchanged.

**Verdict**: PASS — no behavioral change.

### 6. Cache/path/CLI validation safety

- `_load_template_contract_manifest_from_path()` resolves path to absolute via `Path(path).resolve()` and keys `lru_cache(maxsize=16)` by path string
- `_clear_template_contract_manifest_cache()` exposed as private helper for test isolation
- Tests using `tmp_path` call `_clear_template_contract_manifest_cache()` before and after via `_write_template_markdown()`
- No `importlib.reload()` workaround
- CLI validation path: `--validate-template-doc` reads default template path, no provider/network access
- `_DEFAULT_TEMPLATE_PATH` uses `_REPO_ROOT` (4 levels up from file) which is correct for the project structure

**Verdict**: PASS

### 7. Test coverage for Slice 2 plan requirements

| Slice 2 plan requirement | Test(s) |
|---|---|
| Missing/duplicated/malformed JSON block | `test_template_doc_parser_fails_closed_for_missing_empty_duplicate_or_malformed_json` (4 parametrized cases) |
| Unknown keys at every level | `test_template_doc_parser_rejects_unknown_keys_at_nested_levels` (6 parametrized cases) |
| Chapter ID drift | `test_template_doc_parser_rejects_chapter_id_id_text_and_lens_drift` (8 parametrized cases) |
| Stable ID/text shape | Same test (id drift, text empty cases) |
| preferred_lens key/priority validation | Same test (unsupported key, fund_type mismatch, unsupported priority) |
| Cache clearing/path behavior | `test_template_doc_parser_cache_is_path_keyed_and_clearable` |
| Current 8-chapter projection | `test_load_template_contract_manifest_returns_eight_contiguous_chapters`, `test_current_untyped_manifest_projects_slice1_template_json_values` |
| No-provider local validation command | `test_template_contracts_module_cli_validate_template_doc` |
| Every chapter has non-empty fields | `test_every_chapter_has_non_empty_contract_fields` |
| Every fund type resolves lens | `test_every_supported_fund_type_resolves_lens_for_every_chapter` |
| Manifest validation fail-closed | `test_validate_template_contract_manifest_fails_closed_for_invalid_cases` (6 cases) |
| Chapter contract content tests | `test_get_chapter_contract_zero_returns_cover_contract`, `test_current_stage_contract_...`, `test_active_fund_chapter_3_...`, `test_core_risk_contract_...` |
| Lens fallback failure | `test_resolve_preferred_lens_fails_without_exact_or_default_fallback` |

Total: 31 tests, all passing.

**Verdict**: PASS

### 8. Evidence artifact credibility

The evidence artifact (`docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md`):
- Lists all three changed files correctly
- Documents the implementation summary accurately
- Records validation commands and outputs (31 passed, ruff clean, git diff --check clean)
- Lists non-goals preserved correctly
- Notes residual risks (typed manifest still in `typed_contracts.py` until Slice 3)
- Evidence artifact's own validation outputs match what I independently observed

**Verdict**: PASS — credible and accurate.

### 9. Scope check — no creep

No evidence of scope creep into:
- `typed_contracts.py` — not modified
- README / design / control docs — not modified
- Renderer / Service / Host / Agent code — not modified
- Provider / runtime / budget — not modified
- Multi-year / score / golden / readiness — not modified
- Deterministic default behavior — not modified
- Agent runtime implementation — not modified

Only the three files listed in Slice 2 scope were modified.

**Verdict**: PASS

## Validation commands and results

### Pytest

```bash
uv run pytest tests/fund/template/test_contracts.py -q
```

Output: `31 passed in 0.69s` — exit code `0`

### Ruff

```bash
uv run ruff check fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py
```

Output: `All checks passed!` — exit code `0`

### Git diff check

```bash
git diff --check -- fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md
```

Output: empty (no whitespace errors) — exit code `0`

### CLI validation

```bash
uv run python -m fund_agent.fund.template.contracts --validate-template-doc
```

Output: `template_contract_manifest=valid template_id=fund-analysis-template-v1 chapters=8` — exit code `0` (with non-blocking RuntimeWarning, see F1)

## Residual risks

1. **RuntimeWarning on CLI invocation** (LOW): Cosmetic only; output and exit code are correct. Can be addressed in a future non-blocking polish slice if desired.

2. **Typed manifest projection still deferred** (expected): `typed_contracts.py` still owns typed sidecar truth. This is Slice 3 responsibility, not a Slice 2 finding.

3. **Evidence artifact is untracked**: `git diff --check` does not inspect untracked file contents. This is expected per Slice 2 scope; the artifact will be staged with the implementation.

## Summary

Slice 2 implementation correctly replaces Python-authored contract truth with strict template JSON parsing. All 31 tests pass, ruff is clean, git diff --check is clean, CLI validation returns correct output. The RuntimeWarning is a known Python packaging edge case and does not affect correctness. No scope creep detected. No blocking findings.
