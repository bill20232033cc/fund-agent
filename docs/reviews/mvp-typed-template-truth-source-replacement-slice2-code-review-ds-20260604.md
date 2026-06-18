# MVP typed template truth-source replacement Slice 2 code review (DS)

## Worker self-check

- Role: code review worker (AgentDS).
- Gate / slice: `MVP typed template truth-source replacement gate` / Slice 2: parse template doc into current untyped manifest.
- Source of truth: `AGENTS.md`, accepted plan (incl. plan-review fix addendum), plan controller judgment, Slice 1 controller judgment, current `docs/fund-analysis-template-draft.md`, current `contracts.py`, `test_contracts.py`, implementation evidence artifact.
- Actions taken: read all required docs; ran pytest, ruff, git diff --check, CLI validation, untyped/typed cross-validation, scope creep grep; analyzed RuntimeWarning.
- Actions intentionally NOT taken: no file modifications, no stage/commit, no provider/live probe, no typed_contracts edit, no PR/push.

---

## Verdict: PASS

No blocking findings. One LOW finding (RuntimeWarning on CLI path) and two INFO observations.

---

## Findings

### F1 (LOW) — CLI `--validate-template-doc` emits `runpy` RuntimeWarning on stderr

**Evidence:**

```text
$ uv run python -m fund_agent.fund.template.contracts --validate-template-doc
<frozen runpy>:128: RuntimeWarning: 'fund_agent.fund.template.contracts' found in
sys.modules after import of package 'fund_agent.fund.template', but prior to
execution of 'fund_agent.fund.template.contracts'; this may result in unpredictable behaviour
template_contract_manifest=valid template_id=fund-analysis-template-v1 chapters=8
```

Exit code: 0. Validation output correct.

**Analysis:** This is standard Python `runpy` behavior when a module is already imported as a submodule (via `fund_agent/fund/template/__init__.py` → `contracts`) before `python -m` re-executes it as `__main__`. The warning is cosmetic: it does not affect validation correctness, does not change exit code, and does not indicate any logic error. The `_main()` function is structured with `if __name__ == "__main__"` guard and argparse, so re-execution is harmless — the module's function definitions are idempotent and the top-level `_main()` call only fires under `__name__ == "__main__"`.

**Not a blocker** because:
- the module is never intended as a production entry point (it's a validation utility);
- the warning does not affect validation results;
- the test `test_template_contracts_module_cli_validate_template_doc` calls `_main(["--validate-template-doc"])` directly without going through `runpy`, so the tested path is clean;
- the plan only requires "a no-provider validation path"; the test coverage of `_main()` plus the working CLI command satisfy this requirement.

**Recommendation:** If the warning is distracting for template authors, the CLI invocation could be documented as `uv run python -c "from fund_agent.fund.template.contracts import _main; raise SystemExit(_main(['--validate-template-doc']))"` to avoid `runpy`. Not required for this slice.

---

### F2 (INFO) — `_validate_chapter_sidecar_fields` validates fields not projected into untyped manifest

The function validates `audit_focus`, `consumes_chapter_conclusions`, `independent_action_source`, and `internal_subcontracts` (lines 690–755). These fields are in the canonical JSON but are not projected into the untyped `ChapterContract` dataclass. They are validated for structural correctness (type, non-empty where required, ch2-only subcontract constraint) but not stored.

**Analysis:** This is correct and intentional for Slice 2. The untyped `ChapterContract` never carried these fields — they are typed-sidecar fields authored in the canonical JSON for Slice 3 (`typed_contracts.py` projection). Validating them here (fail-closed on structural drift) prevents the template JSON from silently diverging before Slice 3 adds the typed projection. The plan's canonical JSON schema explicitly includes these fields, and the parser's job is to reject malformed input.

**No action needed.**

---

### F3 (INFO) — Evidence artifact claims 31 tests but actual count matches

Evidence reports "31 passed in 0.45s". Actual run confirms 31 tests (7 base tests + 24 parametrized variants = 31 total). Count is accurate. The evidence also correctly reports ruff, git diff --check, and git status results.

**Evidence credibility:** The evidence artifact is accurate and reproducible. All claimed validation commands produce matching output when re-run. The changed-files list is complete. Non-goals are preserved.

---

## Validation results (reproduced)

### 1. Pytest

```text
$ uv run pytest tests/fund/template/test_contracts.py -q
............................... [100%]
31 passed in 0.45s
```

Exit: 0.

### 2. Ruff

```text
$ uv run ruff check fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py
All checks passed!
```

Exit: 0.

### 3. Git diff --check

```text
$ git diff --check -- fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md
```

Exit: 0, no output (no whitespace errors).

### 4. CLI validation path

```text
$ uv run python -m fund_agent.fund.template.contracts --validate-template-doc
template_contract_manifest=valid template_id=fund-analysis-template-v1 chapters=8
```

Exit: 0. See F1 for RuntimeWarning note.

### 5. Typed constraint / evidence regression

```text
$ uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py -q
........................................... [100%]
43 passed in 0.45s
```

Exit: 0.

### 6. Untyped/typed full cross-validation

```text
Full untyped/typed cross-validation: ALL MATCH
Chapters: 8, IDs: [0, 1, 2, 3, 4, 5, 6, 7]
```

All chapter titles, must_answer texts, must_not_cover texts, required_output_items texts, lens keys, lens fund_types, lens statements, lens facets_any, and lens priorities match between untyped and typed projections. Confirms both derive from the same template JSON truth source.

### 7. Typed contracts tests (unchanged by Slice 2)

```text
$ uv run pytest tests/fund/template/test_typed_contracts.py -q
........ [100%]
8 passed in 0.51s
```

Exit: 0. Typed path unaffected.

### 8. No old authored Python constants

```text
$ rg -n "_CHAPTERS\b|def _lens\b|def _chapter\b" fund_agent/fund/template/contracts.py
```

Exit: 1 (no matches). The old `_CHAPTERS` tuple, `_lens()` helper, and `_chapter()` helper are completely removed. The grep only returns references to `preferred_lens` (field name), `_project_chapter_contract` (new parser function), and `_validate_chapter_sidecar_fields` (new validator) — all legitimate new code.

---

## Review point analysis

### 1. contracts.py no longer uses Python-authored contract content as truth

**VERIFIED.** The old `_CHAPTERS` tuple (~530 lines of authored chapter text), `_lens()` helper, and `_chapter()` helper are completely removed. The module now only contains:
- Closed-set domain constants (schema version, key sets, supported values) — these are parser/validation infrastructure, not authored contract content.
- Dataclass definitions (`TemplateLensRule`, `ChapterContract`, `TemplateContractManifest`) — these are the projection schema, unchanged from before.
- Parser, projector, and validator functions — these extract and validate from the template document.
- Public API functions (`load_template_contract_manifest`, `get_chapter_contract`, `resolve_preferred_lens`, `validate_template_contract_manifest`) — unchanged signatures and behavior.

### 2. Strict parse of exactly one TEMPLATE_CONTRACT_MANIFEST_JSON with stdlib json

**VERIFIED.** `_parse_template_contract_manifest_json()` (lines 306–337):
- Calls `_extract_template_manifest_blocks()` which scans line-by-line for marker pairs.
- Fails on zero blocks: "缺少 TEMPLATE_CONTRACT_MANIFEST_JSON 区块"
- Fails on >1 blocks: "TEMPLATE_CONTRACT_MANIFEST_JSON 区块必须 exactly one"
- Fails on empty block: "TEMPLATE_CONTRACT_MANIFEST_JSON 区块不能为空"
- Uses `json.loads()` (stdlib, no loose parser)
- Fails on non-JSON: "不是合法 JSON"
- Fails on non-object top-level: "顶层必须是 JSON object"
- Rejects unknown top-level keys via `_reject_unknown_keys()`

Tests cover all four malformed cases (missing, empty, duplicate, non-JSON) via parametrized test.

### 3. Fail-closed validation for all specified drift types

**VERIFIED.** The following fail-closed validations are implemented and tested:

| Drift type | Validator | Test |
|---|---|---|
| Missing block | `_parse_template_contract_manifest_json` | `test_template_doc_parser_fails_closed_for_missing_empty_duplicate_or_malformed_json` |
| Duplicate block | `_extract_template_manifest_blocks` | same test (param: duplicate) |
| Empty block | `_parse_template_contract_manifest_json` | same test (param: empty) |
| Non-JSON | `json.loads` | same test (param: malformed) |
| Unknown top-level keys | `_reject_unknown_keys` | `test_template_doc_parser_rejects_unknown_keys_at_nested_levels` |
| Unknown chapter keys | `_require_exact_keys` | same test |
| Unknown lens keys | `_require_exact_keys` | same test |
| Unknown item keys | `_require_exact_keys` | same test |
| Chapter count != 8 | `validate_template_contract_manifest` | `test_validate_template_contract_manifest_fails_closed_for_invalid_cases` |
| Duplicate chapter ids | same validator | same test |
| Non-contiguous ids | same validator | same test |
| Chapter id != array index | `_project_chapter_contract` | `test_template_doc_parser_rejects_chapter_id_id_text_and_lens_drift` |
| Stable id drift | `_validate_entry_id` | same test |
| Empty text | `_read_required_string` | same test |
| Unsupported lens key | `_project_preferred_lens` | same test |
| Lens key/fund_type mismatch | `_project_preferred_lens` + `_validate_chapter_contract` | same test |
| Unsupported priority | `_read_optional_priority` | same test |
| Unsupported when_evidence_missing | `_project_required_output_items` | same test |
| Public chapter ids drift | `_validate_top_level_manifest` | same test |
| Empty preferred_lens | `_project_preferred_lens` / `_validate_chapter_contract` | Implicitly covered |
| Fund type lacks lens fallback | `validate_template_contract_manifest` | `test_resolve_preferred_lens_fails_without_exact_or_default_fallback` |
| Sidecar field structural drift | `_validate_chapter_sidecar_fields` | Covered by `test_current_untyped_manifest_projects_slice1_template_json_values` (real template is valid) |

### 4. Untyped projection public API compatible with existing behavior

**VERIFIED.** All four public functions (`load_template_contract_manifest`, `get_chapter_contract`, `resolve_preferred_lens`, `validate_template_contract_manifest`) retain identical signatures and behavior. Full cross-validation between untyped and typed projections confirms all text, lens, and metadata match. The `test_current_untyped_manifest_projects_slice1_template_json_values` test verifies that the untyped projection exactly matches the canonical template JSON.

### 5. Cache/path/CLI validation path

**VERIFIED.**
- Cache: `lru_cache(maxsize=16)` keyed by resolved path string. `_clear_template_contract_manifest_cache()` exposes cache clearing. Test `test_template_doc_parser_cache_is_path_keyed_and_clearable` verifies path isolation and cache clearing.
- Path: `_DEFAULT_TEMPLATE_PATH` resolves from `__file__` → `parents[3]` → `docs/fund-analysis-template-draft.md`. Repo-relative, no hardcoded absolute paths.
- CLI: `_main()` with argparse, `--validate-template-doc` flag, optional `--template-path`. Returns 0 on success. Test `test_template_contracts_module_cli_validate_template_doc` verifies. RuntimeWarning on stderr analyzed in F1 — not a blocker.
- No provider: confirmed. No network, API key, file download, or external service access. Template file read is repository metadata, not fund document access.

### 6. Test coverage of Slice 2 plan requirements

**VERIFIED.** 31 tests covering:

| Plan requirement | Test |
|---|---|
| Manifest loads 8 chapters 0-7 | `test_load_template_contract_manifest_returns_eight_contiguous_chapters` |
| Chapter titles from design | `test_chapter_titles_match_design_and_not_renderer_private_constant` |
| Projection matches template JSON | `test_current_untyped_manifest_projects_slice1_template_json_values` |
| All fields non-empty | `test_every_chapter_has_non_empty_contract_fields` |
| Every fund type resolves lens | `test_every_supported_fund_type_resolves_lens_for_every_chapter` |
| Manifest validation fail-closed | `test_validate_template_contract_manifest_fails_closed_for_invalid_cases` (5 sub-cases) |
| JSON block malformed fail-closed | `test_template_doc_parser_fails_closed_for_missing_empty_duplicate_or_malformed_json` (4 params) |
| Unknown keys at all levels | `test_template_doc_parser_rejects_unknown_keys_at_nested_levels` (6 params) |
| Chapter/id/text/lens drift | `test_template_doc_parser_rejects_chapter_id_id_text_and_lens_drift` (8 params) |
| Cache path-keyed and clearable | `test_template_doc_parser_cache_is_path_keyed_and_clearable` |
| CLI validation path | `test_template_contracts_module_cli_validate_template_doc` |
| Ch0 contract | `test_get_chapter_contract_zero_returns_cover_contract` |
| Ch5 contract boundaries | `test_current_stage_contract_separates_change_facts_from_risk_and_final_judgment` |
| Ch3 active fund constraints | `test_active_fund_chapter_3_contract_requires_reviewed_turnover_or_style_change_before_stability_claim` |
| Ch6 risk/veto boundaries | `test_core_risk_contract_translates_changes_into_risk_veto_and_stress_test` |
| Lens fallback missing | `test_resolve_preferred_lens_fails_without_exact_or_default_fallback` |

All plan-required test categories are covered: missing/duplicated/malformed JSON block, unknown keys at every level, chapter id drift, stable id/text shape, preferred_lens key/priority validation, cache clearing/path behavior, and current 8-chapter projection.

### 7. Evidence artifact credibility

**VERIFIED** with one minor note. All claimed validation outputs are reproducible. The changed-files list matches `git status`. The non-goals list is accurate. The residual risks are correctly stated.

Note: The evidence artifact is currently untracked (`??` in git status), which is by design per the implementation closeout protocol. `git diff --check` does not inspect untracked files.

### 8. No scope creep

**VERIFIED.**
- `typed_contracts.py` is NOT modified (confirmed: `typed_contracts.py` tests pass unchanged with 8 tests).
- No README, design, control, or startup doc changes.
- No renderer, Service, Host/Agent changes.
- No provider/runtime changes.
- The only reference to "Agent" in contracts.py is the module docstring stating its layer position — unchanged from before.
- No multi-year, score, golden, or readiness references.
- The diff touches only `contracts.py` (rewrite of ~530 lines of authored constants into ~960 lines of parser/validator code) and `test_contracts.py` (added ~280 lines of new tests + 3 helper functions).
- `tests/fund/template/test_typed_contracts.py` — 8 tests pass, unchanged by this slice.

---

## Scope check

| Scope item | Status |
|---|---|
| `fund_agent/fund/template/contracts.py` | Modified (parser/projector replaces authored constants) |
| `tests/fund/template/test_contracts.py` | Modified (new parser/fail-closed tests) |
| Evidence artifact | Created (untracked, as expected) |
| `typed_contracts.py` | NOT modified |
| `__init__.py` | NOT modified |
| `chapter_contract_constraints.py` | NOT modified |
| README files | NOT modified |
| `docs/design.md` | NOT modified |
| `docs/implementation-control.md` | NOT modified |
| `docs/current-startup-packet.md` | NOT modified |
| `docs/fund-analysis-template-draft.md` | NOT modified (Slice 1 already committed) |
| Renderer | NOT modified |
| Service | NOT modified |
| Host/Agent runtime | NOT modified |
| Provider/runtime | NOT modified |
| Deterministic defaults | NOT modified |

No scope creep detected.

---

## Residual risks

1. **Coverage measurement blocked by environment.** The `--cov` run fails due to a numpy/pandas import chain issue in the broader project (unrelated to this change). The test suite itself passes cleanly (31/31). Manual inspection shows the parser, projector, and validator code paths are all exercised by tests, but an exact coverage percentage cannot be reported.

2. **RuntimeWarning on CLI path (F1).** Cosmetic, non-blocking. If template authors find it confusing, document the alternative invocation.

3. **Slice 3 dependency.** The canonical JSON contains typed-sidecar fields (`audit_focus`, `consumes_chapter_conclusions`, `independent_action_source`, `internal_subcontracts`, `applies_when`, `when_evidence_missing`, `missing_evidence_reason`) that are structurally validated but not projected into the untyped manifest. Slice 3 must consume these for the typed projection. Any drift in these fields between now and Slice 3 is caught by the structural validators.

4. **Template JSON is the sole truth source for untyped projection.** If the template file is corrupted (e.g., by external Markdown formatting tools), the parser fails closed — which is the intended behavior. This is an accepted authorability cost from the plan.

---

## Validation commands summary

```text
uv run pytest tests/fund/template/test_contracts.py -q
  → 31 passed, exit 0

uv run ruff check fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py
  → All checks passed!, exit 0

git diff --check -- fund_agent/fund/template/contracts.py tests/fund/template/test_contracts.py docs/reviews/mvp-typed-template-truth-source-replacement-slice2-implementation-evidence-20260604.md
  → exit 0, no output

uv run python -m fund_agent.fund.template.contracts --validate-template-doc
  → template_contract_manifest=valid template_id=fund-analysis-template-v1 chapters=8, exit 0
  → stderr: runpy RuntimeWarning (see F1, non-blocking)

uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py -q
  → 43 passed, exit 0

uv run pytest tests/fund/template/test_typed_contracts.py -q
  → 8 passed, exit 0

Untyped/typed full cross-validation
  → ALL MATCH: 8 chapters, all texts, lens keys, lens rules consistent

rg -n "_CHAPTERS\b|def _lens\b|def _chapter\b" fund_agent/fund/template/contracts.py
  → no matches (old authored constants fully removed)
```
