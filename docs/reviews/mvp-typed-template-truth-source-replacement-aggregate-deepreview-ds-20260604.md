# MVP typed template truth-source replacement aggregate deepreview (AgentDS)

## Reviewer self-check

- Role: AgentDS aggregate reviewer only for `MVP typed template truth-source replacement gate`.
- Classification: `heavy`.
- Review scope: complete diff from plan checkpoint `266e18f` through current HEAD `42243b9` (Slices 1-5).
- Actions taken: read all required context (AGENTS.md, plan, controller judgment, Slice 1-5 implementation evidence, code reviews, controller judgments); read complete implementation files (`docs/fund-analysis-template-draft.md`, `contracts.py`, `typed_contracts.py`, `evidence_availability.py`, `design.md`, `implementation-control.md`, `current-startup-packet.md`, `fund_agent/fund/README.md`, `tests/README.md`); read consumer test files; ran independent validation (full test suite, template validation command, grep verification of removed symbols, structured field absence check).
- Actions intentionally not taken: no edit, no implementation, no fix, no commit, no push, no PR, no phaseflow stabilization, no real LLM smoke, no provider/runtime/live probe, no Agent runtime, no multi-year runtime, no score-loop, no golden/readiness.

## Verdict

**PASS** — no blocking findings.

---

## 1. Single Authored Template Truth Source

### Evidence

The canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` block in `docs/fund-analysis-template-draft.md` (lines 6-124+) is the sole authored contract source. Independent verification:

- Exactly 1 canonical JSON block (2 markers: start + end).
- 8 `CHAPTER_CONTRACT_REF` blocks, each chapter_id 0-7, all pointing `source: TEMPLATE_CONTRACT_MANIFEST_JSON`.
- Zero old `CHAPTER_CONTRACT` structured blocks remain.
- Zero `must_answer:`, `must_not_cover:`, `required_output_items:`, `preferred_lens:` structured fields outside the canonical JSON block (grep confirmed).
- `CHAPTER_GOAL`, `ITEM_RULE`, body scaffolding, evidence anchor guidance, and audit appendices preserved.

### Code-authored truth removal

All code-authored typed truth has been removed from `typed_contracts.py`:

- `_CURRENT_TEXT_MAPPING` (~300 lines): **removed**.
- `_TextIdMapping`, `_ChapterTextMapping`: **removed**.
- `_AUDIT_FOCUS_BY_CHAPTER`: **removed**.
- `_CH3_STYLE_EVIDENCE_UNREVIEWED`: **removed**.
- `_required_output_missing_behavior()`, `_required_output_missing_reason()`: **removed**.
- `_build_internal_subcontracts()`: **removed**.
- `_must_not_cover_predicate()`, `_must_not_cover_allowed_contexts()`: **removed**.
- `_assert_exact_text_mapping()`, `_project_chapter()` and its four `_project_*` helpers: **removed**.
- Python-authored `_CHAPTERS`, `_lens()`, `_chapter()` contract truth from `contracts.py`: **removed**.

Grep for all removed symbol names in both `contracts.py` and `typed_contracts.py` returned zero matches.

### Remaining code-only content

Code-level constants that remain are **closed-set domains, schema versions, validation literals, parser markers, and error messages** — not authored contract content:

- `_TEMPLATE_ID`, `_TYPED_TEMPLATE_ID`, `_SCHEMA_VERSION`, `_SOURCE_PATH` — validation constants.
- `_EXPECTED_CHAPTER_IDS`, `_EXPECTED_PUBLIC_CHAPTER_IDS` — invariant guard.
- `_TEMPLATE_BLOCK_START`, `_TEMPLATE_BLOCK_END` — parser markers.
- `_TOP_LEVEL_KEYS`, `_CHAPTER_KEYS`, `_CLAUSE_KEYS`, etc. — schema validation key sets.
- `_REQUIRED_OUTPUT_MISSING_BEHAVIORS`, `_EVIDENCE_STATUSES`, `_ALLOWED_CONTEXTS` — closed-set domain literals.
- `_FIELD_ID_SEGMENTS` — id format validator mapping.
- `_SUPPORTED_FUND_TYPES`, `_SUPPORTED_LENS_KEYS`, `_SUPPORTED_LENS_PRIORITIES` — derived from `FundType` Literal.

**Finding: PASS.** No code-authored stable id/text/missing behavior/audit_focus/subcontract/predicate truth remains.

---

## 2. Both Projections Share Same JSON Truth, Fail Closed

### Evidence

Both `contracts.py` and `typed_contracts.py` ultimately parse the same canonical JSON via `_parse_template_contract_manifest_json()`:

- `contracts.py`: `_load_template_contract_manifest_from_path_cached()` → `_parse_template_contract_manifest_json()` → `_project_untyped_manifest()`.
- `typed_contracts.py`: `_load_raw_template_contract_manifest()` → calls `contracts_module._load_template_contract_manifest_from_path()` (validates untyped projection) → then calls `contracts_module._parse_template_contract_manifest_json()` (same parser) → `_project_typed_chapter()`.

### Fail-closed coverage

Parser fail-closed paths verified:

| Failure case | contracts.py | typed_contracts.py |
|---|---|---|
| Missing canonical block | `ValueError` (contracts.py:321) | Propagated via `_load_raw_template_contract_manifest` |
| Duplicate canonical block | `ValueError` (contracts.py:323) | Same |
| Empty block | `ValueError` (contracts.py:327) | Same |
| Non-JSON block | `ValueError` (contracts.py:331) | Same |
| Non-object top-level | `ValueError` (contracts.py:335) | Same |
| Unknown top-level keys | `ValueError` via `_reject_unknown_keys` (contracts.py:336) | Same |
| Unknown chapter keys | `ValueError` via `_require_exact_keys` (contracts.py:452) | Via typed projection shape checks |
| Chapter id drift (not 0-7) | `ValueError` (contracts.py:238, 432) | `ValueError` (typed_contracts.py:291) |
| Chapter id ≠ position | `ValueError` (contracts.py:456) | N/A (typed uses chapter_id from JSON) |
| Stable id drift (`chN.field.item_NN`) | `ValueError` (contracts.py:899) | Prefix check (typed_contracts.py:687) |
| Empty must_answer/must_not_cover | `ValueError` via `_read_non_empty_array` | `ValueError` (typed_contracts.py:679) |
| Lens key drift | `ValueError` (contracts.py:666) | `ValueError` (typed_contracts.py:811) |
| Lens fund_type ≠ key | `ValueError` (contracts.py:672) | `ValueError` (typed_contracts.py:810) |
| Missing behavior without reason | `ValueError` (contracts.py:627-630) | `ValueError` (typed_contracts.py:787-788) |
| Allowed_contexts without applies_when | `ValueError` (contracts.py:578) | `ValueError` (typed_contracts.py:713) |
| applies_when without allowed_contexts | `ValueError` (contracts.py:580) | `ValueError` (typed_contracts.py:711) |
| Unknown evidence status | `ValueError` (contracts.py:786) | `ValueError` (typed_contracts.py:749) |
| Unknown allowed context | `ValueError` (contracts.py:583) | `ValueError` (typed_contracts.py:716) |
| Unknown audit_focus | N/A (untyped sidecar check) | `ValueError` (typed_contracts.py:869) |
| Ch2 subcontract public_chapter_id non-null | `ValueError` (contracts.py:753) | `ValueError` (typed_contracts.py:901) |
| Non-Ch2 chapter has subcontracts | `ValueError` (contracts.py:755) | `ValueError` (typed_contracts.py:888) |
| Unknown evidence requirement id | N/A (untyped) | `ValueError` (typed_contracts.py:743) |
| Unknown subcontract requirement id | N/A (untyped sidecar check) | `ValueError` (typed_contracts.py:918-931) |
| Stale source_manifest | N/A | `ValueError` (typed_contracts.py:244) |
| Ch0 not consuming Ch7 | N/A | `ValueError` (typed_contracts.py:847) |
| Ch0 independent_action_source=true | N/A | `ValueError` (typed_contracts.py:849) |

### Validation command

```bash
uv run python -m fund_agent.fund.template.contracts --validate-template-doc
```

Exit 0, output: `template_contract_manifest=valid template_id=fund-analysis-template-v1 chapters=8`. Known non-blocking LOW: emits `runpy` RuntimeWarning on stderr (Python packaging artifact, not parser issue).

### Test results

```text
uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q
46 passed

uv run pytest (full typed family)
217 passed
```

**Finding: PASS.** Both projections share identical canonical JSON truth and fail closed across all 20+ malformed/unknown/drift paths.

---

## 3. source_manifest Is Validation-Only

### Evidence

`load_typed_template_contract_manifest(source_manifest: TemplateContractManifest | None = None)`:

- `source_manifest=None` (production path): skips check, proceeds directly to template-JSON-based projection (typed_contracts.py:243).
- `source_manifest` supplied: compares equality with `load_template_contract_manifest()` (current untyped projection from template JSON). If unequal → `ValueError("source_manifest 与当前模板文档投影不一致")` (typed_contracts.py:244). If equal → skips to template-JSON-based projection.
- At no point does `source_manifest` populate any typed field. All typed fields come exclusively from `_load_raw_template_contract_manifest()` → `_project_typed_chapter()`.

Negative test (`test_stale_source_manifest_raises_value_error` in `test_typed_contracts.py`): passes a deliberately stale/different `source_manifest` and asserts `ValueError`.

**Finding: PASS.** `source_manifest` cannot generate typed fields independent of template doc.

---

## 4. EvidenceRequirementId Coupling and Consumer Regression

### EvidenceRequirementId guard

`EvidenceRequirementId` remains a strict `Literal` type alias in `evidence_availability.py` (lines 37-63) with exactly 24 values (12 Ch2 clause/output ids + 12 Ch3 requirement/output ids). `_KNOWN_REQUIREMENT_IDS = frozenset(get_args(EvidenceRequirementId))`.

Validation at two layers:

1. **Manifest load**: `_validate_evidence_predicate()` (typed_contracts.py:738-743) validates every template JSON `applies_when.requirement_ids` value against `_known_evidence_requirement_ids()`. Unknown id → `ValueError`.
2. **Runtime**: `_validate_typed_requirement_ids()` in `derive_evidence_availability()` (existing guard, unchanged).

### Consumer regression

Slice 4 added cross-validation tests:

- `test_evidence_availability_ch2_specs_match_typed_manifest` — verifies every `_CH2_REQUIREMENT_SPECS` key is present in typed manifest Ch2 clause/output ids.
- `test_evidence_availability_ch3_specs_match_typed_manifest` — verifies Ch3 `_CH3_REQUIREMENT_SPECS`, `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID`, `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`, `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES` against typed manifest.
- `test_orchestrator_typed_path_wiring` — Service typed path verifies required output ids/text and `audit_focus` from typed manifest projection.

### chapter_contract_constraints.py

Unchanged (no source modification). Tests confirm default wrappers use `must_answer` / `must_not_cover` from parsed untyped manifest and overlays still resolve.

### No hidden parallel truth

All EvidenceAvailability derivation still reads from same-source `ChapterFactProjection` and typed `EvidenceRequirementId` Literal. No new parallel truth source was introduced. No repository/PDF/cache/source helper/network access was added.

**Finding: PASS.** EvidenceRequirementId coupling preserved; consumer regression prevented; no hidden parallel truth.

---

## 5. Public Chapter IDs 0-7; Ch2 Subcontracts Internal

### Evidence

- `public_chapter_ids` in canonical JSON: exactly `[0,1,2,3,4,5,6,7]`.
- `_EXPECTED_PUBLIC_CHAPTER_IDS` in both `contracts.py` and `typed_contracts.py`: `list(range(8))` / `tuple(range(8))`.
- Both `validate_template_contract_manifest()` and `validate_typed_template_contract_manifest()` assert chapters.length == 8 and ids == (0,1,2,3,4,5,6,7).
- Ch2 `internal_subcontracts`: exactly `["performance", "attribution", "cost"]`, all with `public_chapter_id: null`.
- `_validate_internal_subcontracts()` (contracts.py:754) and `_validate_internal_subcontracts()` (typed_contracts.py:887) reject non-Ch2 chapters with subcontracts.
- `typed_contracts.py:892-893` enforces subcontract_ids must be exactly `("performance", "attribution", "cost")`.

**Finding: PASS.** No Ch2 public split; no public chapter id change.

---

## 6. Docs/Control/Startup/READMEs Reflect Current State

### design.md (v2.3 → current)

- Status line updated: typed template truth-source replacement Slices 1-4 now classified as current implementation fact (line 5).
- `contracts.py` and `typed_contracts.py` described as parsing/projecting/validating from canonical template JSON.
- Agent runtime, multi-year runtime, provider/runtime defaults, score-loop, golden/readiness remain future/deferred.
- No overclaim of unimplemented capabilities.

### implementation-control.md (v2.4)

- Current gate updated to Slice 5 Documentation/control sync.
- Startup Packet section updated with current truth-source facts.
- Slices 1-4 checkpoints recorded.
- Explicit: "本 Slice 5 不再修改代码、测试源码或模板文档".
- All deferred gates preserved: Agent runtime, multi-year, provider budget, score-loop, etc.

### current-startup-packet.md

- Current gate status reflects Slice 5 in progress.
- Current implementation facts section (Section 3) updated: "Template truth-source replacement Slices 1-4 have implemented the current template contract authority".
- All accepted commits listed through Slice 4 checkpoint `e613876`.
- Prohibited actions preserved.

### fund_agent/fund/README.md

- Updated imports show `load_template_contract_manifest` and `load_typed_template_contract_manifest` as stable public API.
- Code example updated with current imports.
- No overclaim of future capabilities.

### tests/README.md

- `test_contracts.py` and `test_typed_contracts.py` entries updated to describe parsing from canonical `TEMPLATE_CONTRACT_MANIFEST_JSON`.
- Existing entries for all consumer test files preserved with accurate descriptions.

### Consistency check

```bash
git diff --check -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md tests/README.md
# exit 0
```

**Finding: PASS.** Docs consistently describe current/future/deferred states. No Agent runtime/multi-year/provider/score/golden/readiness overclaim.

---

## 7. Deterministic analyze/checklist, Renderer, Quality Gate Unchanged

### Evidence

- No changes to `fund_agent/fund/template/renderer.py`, `fund_agent/services/fund_analysis_service.py` (deterministic path), `fund_agent/fund/audit/`, `fund_agent/services/quality_gate_service.py`, or `fund_agent/fund/analysis/`.
- `contracts.py` projection preserves exact same `TemplateContractManifest` shape — untyped `ChapterContract` with same `must_answer`, `must_not_cover`, `required_output_items` texts, `preferred_lens`, `title`, `narrative_mode`.
- Renderer, quality gate, and deterministic analysis consume `ChapterContract` API — unchanged.
- Service explicit `--use-llm` typed path wires same `typed_template_path="typed_template_contract"` — unchanged.
- Public chapter ids remain 0-7.
- No provider/runtime default changes.
- No PR/release/external state changes.

**Finding: PASS.** Deterministic behavior, renderer, quality gate, provider defaults unchanged.

---

## 8. Tests Prove Behavior Without Live Provider

### Test coverage summary

| Test file | Tests | Coverage |
|---|---|---|
| `tests/fund/template/test_contracts.py` | 31 | Parser, projection, malformed, cache, validate command |
| `tests/fund/template/test_typed_contracts.py` | 15 | Typed projection, code-truth removal, stale source_manifest, fail-closed |
| `tests/fund/template/test_chapter_contract_constraints.py` | 4+ | Wrapper, overlay resolution |
| `tests/fund/test_evidence_availability.py` | 10+ | Same-source derivation, Ch2/Ch3 spec cross-validation |
| `tests/fund/test_chapter_writer.py` | 30+ | Typed required output, evidence gap, block |
| `tests/fund/test_chapter_auditor.py` | 25+ | Programmatic audit, typed must_not_cover, audit_focus |
| `tests/services/test_chapter_orchestrator.py` | 15+ | Service typed path, EvidenceAvailability wiring |

All 217 tests pass. All use fake/double/memory fixtures. No test accesses:
- Live provider / network / API keys
- Real document repository / PDF / cache / source helpers
- Real file system (template path tests use temp dirs with cache clearing)
- Real env vars (LLM config tests use fake env mapping)

### Adversarial failure pass

Tested adversarial scenarios:

1. **Malformed JSON injection**: `test_malformed_json_block_*` — unparseable, empty, non-object, truncated all fail closed.
2. **Unknown key injection**: `test_unknown_*_keys_*` — unknown top-level, chapter-level, clause-level keys all fail closed.
3. **ID drift**: `test_chapter_id_drift_*`, `test_stable_id_mismatch_*` — reordered, missing, wrong-prefix ids fail closed.
4. **Lens drift**: `test_lens_key_drift_*`, `test_lens_fund_type_mismatch_*` — unsupported key, key≠fund_type fail closed.
5. **Missing behavior inconsistency**: behavior without reason, reason without behavior both fail closed.
6. **Predicate/context mismatch**: applies_when without allowed_contexts, and vice versa, both fail closed.
7. **Stale source_manifest**: non-None value not matching current projection → `ValueError`.
8. **Unknown requirement id**: id not in `_KNOWN_REQUIREMENT_IDS` guard → `ValueError`.
9. **Subcontract leakage**: Ch2 subcontract with non-null `public_chapter_id` → `ValueError`.
10. **Non-Ch2 subcontract**: any other chapter with `internal_subcontracts` → `ValueError`.
11. **Ch0 independence**: `independent_action_source=true` → `ValueError`.
12. **Ch0 wrong dependency**: `consumes_chapter_conclusions` not `[7]` → `ValueError`.
13. **Duplicate clause id**: duplicate across chapters or within chapter → `ValueError`.
14. **Template JSON change drives projection**: test proves modifying JSON changes typed manifest; malformed JSON after change fails closed.

**Finding: PASS.** Tests prove parser/projection/consumer behavior and all fail-closed paths without live provider/network/repository/PDF/cache/source helper access.

---

## Adversarial Failure Pass

Beyond the tested adversarial scenarios above, the following architectural failure modes were evaluated:

1. **Silent JSON parse degradation**: If the canonical JSON block is corrupted by external Markdown tooling (e.g., auto-formatters), the `json.loads()` call fails with `JSONDecodeError` → `ValueError`. Mitigation: strict stdlib `json` parser, no fuzzy/YAML/Markdown inference.

2. **JSON-prose semantic drift**: If a human edits chapter body prose after the canonical JSON without updating the JSON, the code still validates strict JSON shape but cannot detect semantic mismatch between JSON clause text and body prose. Mitigation: per-chapter `CHAPTER_CONTRACT_REF` blocks contain no structured clause text (summary-only, non-authoritative), so there is no duplicated truth to drift against. If body prose contradicts JSON clause semantics, the discrepancy is the same class of problem as any template edit without code update — it requires author discipline, not runtime detection.

3. **EvidenceRequirementId stale coupling**: If `EvidenceRequirementId` Literal changes without updating the canonical JSON, manifest load fails closed (unknown requirement id in `applies_when.requirement_ids` or Ch2 subcontract `requirement_ids`). If canonical JSON changes without updating `EvidenceRequirementId`, `_validate_typed_requirement_ids()` at runtime catches unknown ids. The double guard (manifest load + runtime) ensures bidirectional drift is detected.

4. **Cache poisoning**: If `lru_cache` returns a stale manifest after template file edit, the test helper `_clear_template_contract_manifest_cache()` clears it. Production only reads the immutable default path; a file change requires process restart or explicit cache clear. No `importlib.reload()` workaround is needed.

5. **Double JSON parse inconsistency**: Both `contracts.py` and `typed_contracts.py` call `_parse_template_contract_manifest_json()` on the same file content. If the file changes between the two calls (TOCTOU), the untyped manifest validation in `_load_raw_template_contract_manifest()` (called first) would catch the change before typed projection. In practice, both reads happen within the same synchronous call stack, making TOCTOU unlikely.

6. **source_manifest bypass**: `source_manifest` is checked for equality with current untyped projection but never used to populate typed fields. Even if a caller passes a crafted but equal manifest, typed fields still come from template JSON. No bypass path exists.

**Finding: PASS.** Six adversarial failure modes evaluated; all have fail-closed behavior or accepted mitigations.

---

## LOW / Informational Findings

These are non-blocking findings carried forward from Slice 2-5 reviews, verified as still present and non-blocking:

1. **L1 — runpy RuntimeWarning**: `python -m fund_agent.fund.template.contracts --validate-template-doc` emits `RuntimeWarning: 'fund_agent.fund.template.contracts' found in sys.modules after import of package...` on stderr. Exit code is 0, validation passes. Root cause: Python runpy/package import order. Impact: cosmetic only. Does not affect parser correctness.

2. **L2 — Missing JSON key → KeyError not ValueError**: Some deep field access paths in `typed_contracts.py` projectors use `data[key]` before `_read_required_*` helpers, which could surface `KeyError` instead of `ValueError` if the key is missing. However, Slice 2 `contracts.py` parser validates all keys at the untyped projection level first (via `_require_exact_keys` at every object level). A missing key at the typed projection stage means the untyped validation passed but the typed projector has a bug — still fail-closed either way.

3. **L3 — Orphan `missing_evidence_reason`**: `_validate_required_output_items` (typed_contracts.py:789) checks `item.missing_evidence_reason is not None and not item.missing_evidence_reason.strip()`, but does not check `item.when_evidence_missing is None and item.missing_evidence_reason is not None`. An orphan reason is stored in the dataclass but never consumed by writer/auditor (they only read reason when behavior is non-null). No functional impact. contracts.py:632-633 catches this at the untyped projection level.

4. **L4 — Double file read**: `_load_raw_template_contract_manifest()` reads the template file twice — once via `contracts_module._load_template_contract_manifest_from_path()` (which reads + parses + validates untyped projection), then again directly via `template_path.read_text()`. The second read is needed to get the raw JSON for typed projection. Performance impact is negligible (small Markdown file, cached at OS level). Could be optimized by returning raw JSON from the untyped path, but this would change the untyped API.

5. **L5 — Ch2 subcontract requirement_ids AND coupling**: `_validate_internal_subcontracts()` (typed_contracts.py:912-931) requires every subcontract requirement_id to be in BOTH `known_chapter_requirement_ids` AND `known_evidence_requirement_ids`. This is strict AND logic — if a future evidence-availability refactor removes an id from `_KNOWN_REQUIREMENT_IDS` without removing it from Ch2 subcontracts, manifest load fails. Current data satisfies both constraints. The plan explicitly accepted this coupling as intended fail-closed behavior.

6. **L6 — Private path parameter no traversal guard**: `_load_raw_template_contract_manifest(path=...)` accepts an arbitrary path. Not exposed in public API; production always uses `None` → default constant. No path traversal risk in current usage.

7. **L7 — Ch3 reverse cross-validation partial**: Slice 4 `test_evidence_availability_ch3_specs_match_typed_manifest` proves typed manifest Ch3 output ids are covered by base specs or actual-behavior output ids (forward direction). Reverse direction (every spec id is present in typed manifest) is not fully asserted. Current data is consistent; a future evidence-availability cleanup may add bidirectional equality.

8. **L8 — Service monkeypatch uses hardcoded requirement ids**: `test_orchestrator_typed_path_wiring` uses stable `EvidenceRequirementId` literal values for two availability spot checks. These are contract-stable ids, not implementation details. The test also validates required output ids/text and `audit_focus` from `typed_by_id`.

**Finding: PASS (informational).** Eight LOW findings, all non-blocking, all previously reviewed and accepted by controllers.

---

## Residual Risks

1. **JSON-Markdown authorability**: The canonical JSON block (several hundred lines of strict JSON) is embedded in a Markdown HTML comment. External Markdown tooling (formatters, linters, editors) could corrupt the JSON. Mitigation accepted: strict `json.loads()` parser, JSON-path error messages, no-provider validation command, focused parser tests. If corruption occurs, it fails closed at manifest load.

2. **Prose-JSON semantic drift**: The template doc still contains chapter body prose, `CHAPTER_GOAL`, and `ITEM_RULE` blocks outside the canonical JSON. If an author updates body prose semantics without updating the JSON clause texts, the parser cannot detect semantic drift. This is the same risk as any prose-only template — the JSON canonical block eliminates code parallel truth but does not eliminate prose-JSON drift. Mitigation: non-authoritative `CHAPTER_CONTRACT_REF` blocks with summary-only content prevent structured-field-level duplication.

3. **EvidenceRequirementId Literal maintenance**: Adding/removing requirement ids requires coordinated changes to `EvidenceRequirementId` Literal, `_CH2_REQUIREMENT_SPECS` / `_CH3_REQUIREMENT_SPECS` private dicts, and the canonical JSON. The dual manifest-load + runtime guard ensures bidirectional drift is caught, but the maintenance surface is spread across three files (`evidence_availability.py`, `typed_contracts.py`, template doc).

4. **Unrelated workspace artifacts**: Multiple unrelated untracked artifacts remain in the worktree. All Slice 1-5 controllers explicitly noted these must not be staged by this gate.

---

## Open Questions

None. All review focus areas (1-8) have been verified with direct evidence.

---

## Validation Reviewed

### Independent commands executed

| Command | Result |
|---|---|
| `uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q` | 217 passed |
| `uv run python -m fund_agent.fund.template.contracts --validate-template-doc` | Exit 0, manifest valid |
| `rg -n "_CURRENT_TEXT_MAPPING\|_TextIdMapping\|..." fund_agent/fund/template/typed_contracts.py` | Zero matches |
| `rg -n "must_answer:" docs/fund-analysis-template-draft.md` | Zero matches (no structured contract duplication) |
| `rg -c "TEMPLATE_CONTRACT_MANIFEST_JSON" docs/fund-analysis-template-draft.md` | 10 (2 markers + 8 refs) |
| `rg "CHAPTER_CONTRACT_REF" docs/fund-analysis-template-draft.md` | 8 blocks, ids 0-7 |
| `git diff --check -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md tests/README.md` | Exit 0 |

### Review artifacts reviewed

- Slice 1-5 implementation evidence artifacts (5 files).
- Slice 1-5 DS code reviews (5 files).
- Slice 1-5 MiMo code reviews (5 files).
- Slice 1-5 controller judgments (5 files).
- Plan (`mvp-typed-template-truth-source-replacement-plan-20260603.md`).
- Plan controller judgment.
- AGENTS.md, design.md, implementation-control.md, current-startup-packet.md, fund_agent/fund/README.md, tests/README.md.

---

## Uncovered Areas

1. **Real LLM smoke**: No `--use-llm` provider invocation was run. This is expected — the gate explicitly excludes provider/runtime/live probe. Test coverage uses fake LLM clients.

2. **Multi-year evidence**: No cross-year evidence validation. The gate preserves current single-year behavior.

3. **Performance benchmarking**: No performance comparison before/after truth-source replacement. The double file read (L4) is a known LOW, and the lru_cache on untyped path mitigates repeated reads.

4. **Concurrent access**: No test for concurrent `load_template_contract_manifest()` + `load_typed_template_contract_manifest()` calls. The synchronous call stack makes TOCTOU between the two reads unlikely in practice.

5. **Large-template edge cases**: The template doc is currently ~2000 lines. If future chapters or subcontracts expand the canonical JSON significantly, parser performance and Markdown readability may degrade. Current size is manageable.

---

## Completion Status

Aggregate deepreview complete. Verdict: **PASS** with no blocking findings.

The full truth-source replacement gate (Slices 1-5) successfully:

- Established `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` as the sole authored template contract truth source.
- Removed all code-authored typed truth (~600+ lines) from `contracts.py` and `typed_contracts.py`.
- Preserved public chapter ids 0-7, Ch2 internal subcontracts, deterministic behavior, renderer, quality gate, and provider defaults.
- Implemented fail-closed parser/projection/validation across 20+ malformed/unknown/drift paths.
- Verified consumer regression with 217 passing tests, zero live provider dependencies.
- Synchronized design/control/startup/README docs to reflect current state without overclaiming future capabilities.
- Eight LOW findings acknowledged, all non-blocking, all previously reviewed and accepted.
