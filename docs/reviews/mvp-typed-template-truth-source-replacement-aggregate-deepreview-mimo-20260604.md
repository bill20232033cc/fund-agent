# MVP Typed Template Truth-Source Replacement Gate — Aggregate Deepreview

**Reviewer**: AgentMiMo (aggregate reviewer only)
**Date**: 2026-06-04
**Scope**: Complete truth-source replacement gate diff from plan checkpoint `266e18f` through current HEAD `42243b9` (Slices 1-5)
**Verdict**: **PASS** — no blocking findings

---

## Review Scope

- Commits `3c2b237..42243b9` (4 commits: Slices 2-5; Slice 1 committed at `3c2b237`)
- Changed implementation/doc/test artifacts for Slices 1-5
- Key implementation files: `docs/fund-analysis-template-draft.md`, `fund_agent/fund/template/contracts.py`, `fund_agent/fund/template/typed_contracts.py`, `tests/fund/template/test_contracts.py`, `tests/fund/template/test_typed_contracts.py`, `tests/fund/template/test_chapter_contract_constraints.py`, `tests/fund/test_evidence_availability.py`, `tests/services/test_chapter_orchestrator.py`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`, `tests/README.md`
- All 5 slice implementation evidence artifacts and controller judgments

---

## Required Read Set — Validation

| Artifact | Read | Notes |
|---|---|---|
| `AGENTS.md` | Yes | Agent execution rules authority; no conflicts found with gate changes |
| Plan doc `mvp-typed-template-truth-source-replacement-plan-20260603.md` | Yes | 5-slice plan; gate scope and sequencing verified |
| Controller judgment `mvp-typed-template-truth-source-replacement-plan-controller-judgment-20260603.md` | Yes | Plan accepted; constraints verified |
| Slice 1-5 implementation evidence | Yes (all 5) | Each slice: worker self-check, changed files, validation commands, non-goals, residual risks |
| Slice 1-5 controller judgments | Yes (all 5) | All 5 slices received ACCEPT verdicts |
| Slice 1-5 code reviews (AgentDS + AgentMiMo) | Yes (all 10) | All PASS or PASS-WITH-RISKS, no blocking findings |
| Git diff `3c2b237..HEAD` | Yes | 4 commits, ~4700 lines added, ~750 lines removed across implementation + artifacts |
| Current implementation files | Yes | Full source of `contracts.py` (1117 lines), `typed_contracts.py` (1157 lines), template doc (2067 lines) |
| All test files | Yes | `test_contracts.py` (760 lines), `test_typed_contracts.py` (526 lines), `test_chapter_contract_constraints.py` (148 lines), `test_evidence_availability.py` (405 lines), `test_chapter_orchestrator.py` (3073 lines) |
| Docs/control/startup/READMEs | Yes (all 5) | Full source reviewed for overclaim patterns |

---

## Review Focus Findings

### 1. Single Authored Template Truth Source

**Status**: PASS

`docs/fund-analysis-template-draft.md` contains exactly one `TEMPLATE_CONTRACT_MANIFEST_JSON` HTML comment block (lines 6-1443). This is the sole authored contract source. The git diff confirms removal of all Python-authored truth from both modules:

- `contracts.py`: Removed `_CHAPTERS` constant (8 chapters of Python-authored `ChapterContract` data), replaced with strict JSON parsing from template doc
- `typed_contracts.py`: Removed `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping`, `_AUDIT_FOCUS_BY_CHAPTER`, `_CH3_STYLE_EVIDENCE_UNREVIEWED`, missing behavior/reason helpers, internal subcontract construction, and predicate/context helpers (~630 lines removed)

Grep for residual code-authored truth patterns (`_CHAPTERS`, `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping`, `_AUDIT_FOCUS_BY_CHAPTER`, `_CH3_STYLE_EVIDENCE`) returns zero matches in current `contracts.py` or `typed_contracts.py`.

The per-chapter visible `CHAPTER_CONTRACT_REF` blocks in the template doc are non-authoritative references only (confirmed by Slice 1 implementation evidence and template doc lines 1541-1544, 1669-1673, etc.).

### 2. contracts.py and typed_contracts.py Both Project from Same Template JSON

**Status**: PASS

Both modules share the same template doc path (`_DEFAULT_TEMPLATE_PATH` → `docs/fund-analysis-template-draft.md`) and the same JSON parser entry point:

- `contracts.py` line 165: `load_template_contract_manifest()` → `_load_template_contract_manifest_from_path(_DEFAULT_TEMPLATE_PATH)` → `_parse_template_contract_manifest_json(template_text)` → `_project_untyped_manifest(raw_manifest)`
- `typed_contracts.py` line 242-246: `load_typed_template_contract_manifest()` → calls `load_template_contract_manifest()` for comparison, then calls `_load_raw_template_contract_manifest()` which re-invokes the same parser

Both fail closed on malformed/missing/unknown/drift cases:
- `contracts.py`: `_require_exact_keys`, `_require_exact_string`, `_reject_unknown_keys`, `_validate_entry_id`, `_validate_applies_when`, `_validate_internal_subcontracts` — all raise `ValueError`
- `typed_contracts.py`: `validate_typed_template_contract_manifest`, `_validate_typed_chapter_contract`, `_validate_non_empty_unique_clause_ids`, `_validate_required_output_items`, `_validate_preferred_lens`, `_validate_dependencies`, `_validate_audit_focus`, `_validate_internal_subcontracts`, `_validate_evidence_predicate` — all raise `ValueError`

### 3. source_manifest in typed_contracts.py is Validation-Only

**Status**: PASS

`typed_contracts.py` line 226-244: `load_typed_template_contract_manifest(source_manifest=None)`:
- `source_manifest` parameter is optional
- When provided, it is only compared against the freshly loaded manifest: `if source_manifest is not None and source_manifest != current_manifest: raise ValueError("source_manifest 与当前模板文档投影不一致")`
- Typed fields are always projected from `_load_raw_template_contract_manifest()` (the canonical JSON), never from `source_manifest`
- The parameter serves as a staleness check for callers who already hold an untyped manifest

### 4. EvidenceRequirementId / EvidenceAvailability Coupling

**Status**: PASS

Bidirectional fail-closed coupling confirmed:

- `evidence_availability.py` defines `EvidenceRequirementId` Literal (24 members) → `_KNOWN_REQUIREMENT_IDS` frozenset (line 67)
- `typed_contracts.py` imports `_KNOWN_REQUIREMENT_IDS` via private accessor `_known_evidence_requirement_ids()` (lines 934-948), validates it is a frozenset
- `typed_contracts.py` uses the guard in two paths: `_validate_evidence_predicate` (line 737-744) and `_validate_internal_subcontracts` (line 894-931)
- `evidence_availability.py` reverse-validates via `_validate_typed_requirement_ids(manifest)` (lines 344-366): collects all requirement_ids from typed manifest and verifies each exists in `_KNOWN_REQUIREMENT_IDS`

No hidden parallel truth: the `EvidenceRequirementId` Literal is the single source; both modules derive from it and cross-check at runtime.

### 5. Public Chapter IDs Stay 0-7; Ch2 Subcontracts Remain Internal

**Status**: PASS

- `contracts.py` line 28: `_EXPECTED_CHAPTER_IDS = tuple(range(8))`, line 237-238: `chapter_ids != _EXPECTED_CHAPTER_IDS` raises
- `typed_contracts.py` line 24: `EXPECTED_PUBLIC_CHAPTER_IDS = tuple(range(8))`, line 290-291: validation
- Template doc JSON `public_chapter_ids: [0,1,2,3,4,5,6,7]` (line 12-20)
- Ch2 internal subcontracts (`performance`, `attribution`, `cost`) validated by:
  - `contracts.py` lines 723-755: `_validate_internal_subcontracts` — `chapter_id != 2 and raw_subcontracts` raises, `public_chapter_id is not None` raises
  - `typed_contracts.py` lines 872-931: `_validate_internal_subcontracts` — same guards plus requirement_id cross-validation
- Template doc Ch2 `internal_subcontracts` all have `public_chapter_id: null` (lines 554-589)

### 6. Docs/Control/Startup/READMEs Reflect Current vs Future/Deferred Correctly

**Status**: PASS

Reviewed all 5 documentation files for overclaim patterns. Key assertions verified:

- `docs/design.md` line 5: Explicitly lists "typed template truth-source replacement Slices 1-4 已把 canonical JSON 变成 authored truth source" as current code fact, while listing Agent runtime, multi-year runtime, provider/runtime defaults, score-loop, golden/readiness as "未改变"
- `docs/design.md` line 182: "仍未实现 / 非目标" section correctly lists deferred items
- `docs/implementation-control.md` line 9: Current status correctly identifies Slice 5 as "docs/control sync only — no code changes, no runtime changes"
- `docs/implementation-control.md` line 62: "本 Slice 5 不再修改代码、测试源码或模板文档"
- `docs/current-startup-packet.md` line 22: "do not enter phaseflow stabilization, provider/runtime/live probe, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/push/release"
- `fund_agent/fund/README.md` line 136: Correctly states non-goals for truth-source replacement
- `tests/README.md`: Template test descriptions updated to reflect new truth source

Grep for Agent runtime / multi-year / provider smoke / score-loop / golden readiness / PR release in docs returns only correctly qualified references (as future/residual/non-goal), no overclaim.

### 7. Deterministic Analyze/Checklist, Renderer, Quality Gate, Provider/Runtime Defaults Unchanged

**Status**: PASS

The diff touches only `contracts.py`, `typed_contracts.py`, their tests, and documentation. No changes to:
- `fund_agent/fund/analysis/` (deterministic analyze/checklist)
- `fund_agent/fund/template/renderer.py` (template rendering)
- `fund_agent/fund/audit/` (quality gate FQ0-FQ6)
- `fund_agent/services/` (Service wiring, provider construction)
- `fund_agent/host/` (Host runtime)
- Provider timeout/retry/diagnostic code

Implementation evidence for all 5 slices confirms "non-goals preserved" sections listing unchanged components.

### 8. Tests Prove Parser/Projection/Consumer Behavior and Fail-Closed Paths

**Status**: PASS

Slice implementation evidence confirms:
- Slice 2: 31 tests pass (contracts parser, fail-closed, cache, CLI)
- Slice 3: 45 tests pass (typed projection, removal of code-authored truth, cross-validation)
- Slice 4: 46 typed tests + 171 consumer tests pass (LensKey guard, chapter_contract_constraints, evidence_availability cross-validation, orchestrator typed path)
- Slice 5: 46 targeted template tests pass + docs self-check (26 required assertions, 11 forbidden overclaim patterns)

All tests use fakes/stubs/monkeypatch — no live provider/network/repository/PDF/cache/source helper access confirmed by import boundary enforcement tests in `test_evidence_availability.py` and `test_chapter_orchestrator.py`.

**Environment note**: Local test execution failed due to Python 3.14 environment lacking `httpx` dependency (project requires Python 3.11 per `tests/README.md`). This is a local environment issue, not a code defect. All slice implementation evidence artifacts contain exact pytest output confirming test passage during gate execution.

---

## Adversarial Failure Pass

| Attack Vector | Result | Evidence |
|---|---|---|
| Residual code-authored truth in contracts.py | **BLOCKED** | Grep returns zero matches for `_CHAPTERS`, `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, etc. |
| Residual code-authored truth in typed_contracts.py | **BLOCKED** | Grep returns zero matches. All typed fields project from raw JSON via `_project_typed_chapter` |
| Malformed template JSON accepted | **BLOCKED** | `_parse_template_contract_manifest_json` rejects non-object, empty, unknown keys; `_extract_template_manifest_blocks` rejects nesting/missing END |
| Missing template doc silently defaults | **BLOCKED** | `OSError` caught and re-raised as `ValueError` (contracts.py line 284-285, typed_contracts.py line 343-344) |
| Duplicate TEMPLATE_CONTRACT_MANIFEST_JSON blocks | **BLOCKED** | `_extract_template_manifest_blocks` raises if `len(blocks) > 1` (line 322-323) |
| Unknown chapter keys accepted | **BLOCKED** | `_require_exact_keys` on `_CHAPTER_KEYS` (contracts.py line 452) |
| Ch2 subcontract leaks as public chapter | **BLOCKED** | `public_chapter_id is not None` raises (contracts.py line 752-753, typed_contracts.py line 900-901) |
| Unknown EvidenceRequirementId in typed contract | **BLOCKED** | `_validate_evidence_predicate` and `_validate_internal_subcontracts` check against `_KNOWN_REQUIREMENT_IDS` |
| source_manifest used to generate typed fields | **BLOCKED** | `source_manifest` only compared for equality, never used for projection (typed_contracts.py line 243-244) |
| Parallel template truth source created | **BLOCKED** | Both modules use same `_DEFAULT_TEMPLATE_PATH` and same parser; no secondary source exists |
| Overclaim of implemented features in docs | **BLOCKED** | Docs self-check passed (26 required assertions, 11 forbidden patterns); grep confirms no unqualified claims |

---

## Findings

### LOW-1: Private import of `_KNOWN_REQUIREMENT_IDS` across module boundary

**Severity**: LOW
**File**: `fund_agent/fund/template/typed_contracts.py:934-948`
**Evidence**: `_known_evidence_requirement_ids()` imports `_KNOWN_REQUIREMENT_IDS` (private symbol) from `evidence_availability.py`
**Impact**: Cross-module private import creates implicit coupling. If `_KNOWN_REQUIREMENT_IDS` is renamed or refactored, `typed_contracts.py` will break at runtime (caught by `isinstance` guard, but still a maintenance concern).
**Mitigation**: The `isinstance` check on line 946 provides fail-closed behavior. The coupling is intentional and bidirectionally validated. This is an acceptable internal implementation detail for a within-package import.
**Decision**: Non-blocking. Consistent with Slice 3 and Slice 4 review findings.

### LOW-2: Test environment requires Python 3.11 + httpx

**Severity**: LOW
**File**: `tests/README.md` (CI configuration)
**Evidence**: Local pytest execution fails with `ModuleNotFoundError: No module named 'httpx'` on Python 3.14. Project specifies Python 3.11 with `uv sync --extra dev --frozen`.
**Impact**: Tests cannot be run in arbitrary Python environments. This is by design (project pins Python 3.11).
**Decision**: Non-blocking. Not a code defect; consistent with project CI configuration.

### LOW-3: `lru_cache` on `_load_template_contract_manifest_from_path_cached` may mask template doc mutations during long-lived processes

**Severity**: LOW
**File**: `fund_agent/fund/template/contracts.py:267-268`
**Evidence**: `@lru_cache(maxsize=16)` caches manifest by resolved path key. If template doc is mutated in-process, stale manifest is served until cache is cleared.
**Impact**: In the current architecture, template doc is static (committed to repo). Cache clearing is exposed via `_clear_template_contract_manifest_cache()` for tests. No production scenario triggers in-process template mutation.
**Decision**: Non-blocking. Pre-existing pattern, not introduced by this gate.

---

## Open Questions

None. All review focus items resolved satisfactorily.

---

## Residual Risks

1. **EvidenceRequirementId closed-set drift**: If the template JSON adds new `requirement_ids` in `applies_when` predicates or `internal_subcontracts` that are not in the `EvidenceRequirementId` Literal, validation will fail at load time. This is fail-closed by design but requires coordinated updates to both the template JSON and `evidence_availability.py`.

2. **Template doc JSON size**: The canonical JSON block is ~1437 lines of formatted JSON embedded in a Markdown HTML comment. Future chapters or expanded contracts will increase this further. No immediate concern but worth monitoring.

3. **Untyped vs typed projection divergence**: Both `contracts.py` (untyped) and `typed_contracts.py` (typed) parse the same JSON but with different projection logic. Untyped projects `must_answer`/`must_not_cover` as `tuple[str, ...]` (text only); typed projects full structured objects with ids, predicates, and metadata. A template JSON change that passes untyped validation could theoretically fail typed validation. The `source_manifest` comparison in `load_typed_template_contract_manifest` mitigates this for callers who first load untyped.

---

## Validation Reviewed

| Validation | Method | Result |
|---|---|---|
| Template JSON is sole authored source | Grep + diff analysis | Confirmed — no residual code-authored truth |
| Both modules parse same JSON | Source code tracing | Confirmed — same `_DEFAULT_TEMPLATE_PATH` and parser |
| Fail-closed on malformed/missing/unknown | Adversarial failure pass | All 11 attack vectors blocked |
| source_manifest is validation-only | Source code tracing | Confirmed — comparison only, no field generation |
| EvidenceRequirementId bidirectional coupling | Source code tracing | Confirmed — Literal → frozenset → cross-validation both directions |
| Public chapter ids 0-7 preserved | Validation code + template JSON | Confirmed |
| Ch2 subcontracts remain internal | Validation code + template JSON | Confirmed |
| Docs reflect current vs future correctly | Grep for overclaim patterns + self-check | Confirmed — 26 assertions, 11 forbidden patterns pass |
| No deterministic/renderer/quality gate changes | Diff analysis | Confirmed — only template contract files changed |
| Tests prove behavior without live access | Import boundary enforcement tests | Confirmed |
| All 5 slices independently reviewed and accepted | Controller judgments | All ACCEPT |

---

## Uncovered Areas

1. **Live test execution**: Tests could not be re-executed in this review session due to environment mismatch (Python 3.14 vs 3.11). Review relied on slice implementation evidence artifacts containing exact pytest output. This is acceptable for an aggregate review but a fresh test run in the correct environment would provide additional confidence.

2. **Template doc content correctness**: This review verified that the JSON block is parsed and validated correctly, but did not independently verify that every `must_answer` text, `must_not_cover` text, `required_output_item` text, `preferred_lens` statement, and `audit_focus` value in the JSON matches the original template intent. This was covered by Slice 1 review (which compared JSON projection against original per-chapter contracts).

3. **Downstream consumer behavior with new typed contracts**: This review verified the typed contract module itself and the orchestrator typed path, but did not trace every downstream consumer (e.g., renderer, auditor prompt injection, quality gate) through the full execution path. This was covered by Slice 4 consumer regression tests (171 tests pass).

---

## Conclusion

**Verdict: PASS** — no blocking findings.

The MVP typed template truth-source replacement gate successfully moves all authored template contract truth from Python code into the canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` block in `docs/fund-analysis-template-draft.md`. Both `contracts.py` and `typed_contracts.py` project from the same JSON with comprehensive fail-closed validation. All 5 slices were independently reviewed and accepted. Documentation correctly distinguishes current implementation from future/deferred architecture. No blocking findings, no overclaim, no residual code-authored truth.

3 LOW findings identified (private import coupling, test environment requirement, cache behavior) — all non-blocking and consistent with prior slice reviews.
