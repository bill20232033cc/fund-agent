# MVP typed template truth-source replacement plan review — AgentDS

## Worker self-check

- Role: AgentDS plan review worker only.
- Gate: `MVP typed template truth-source replacement gate`; classification `heavy`.
- Actions taken: read the plan, both controller judgments (aggregate deepreview and Slice 8), `AGENTS.md`, `docs/design.md` (typed contract sections), `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, `contracts.py`, `typed_contracts.py`, `chapter_contract_constraints.py`, `evidence_availability.py`, `chapter_writer.py`, `chapter_auditor.py`.
- Actions intentionally not taken: no implementation, no file edits, no provider/live probe, no `$gateflow` or `/gateflow`, no commit/push/PR.

## Verdict: BLOCKED

Three blocking findings must be resolved before implementation. No other finding independently blocks, but the cumulative weight of high/medium findings would independently justify BLOCKED.

---

## Blocking Findings

### B1. Missing concrete JSON schema for the canonical block

**Severity**: BLOCKING
**Evidence**: Plan decision 2 (lines 127-137) describes fields the JSON "must include" at a narrative level: `schema_version`, `template_id`, per-chapter `must_answer`/`must_not_cover`/`required_output_items`, Ch3 predicate with `applies_when`, Ch2 internal subcontracts, and missing-evidence behavior. No JSON Schema, example snippet, or field-level specification is provided.

**Impact**: Without a concrete schema, the following are unknowable before implementation begins:

- Whether all current `_CURRENT_TEXT_MAPPING` data (8 chapters × ~50+ clause texts + stable ids + per-clause metadata) can fit in a single maintainable JSON block.
- Whether the JSON model for `must_answer` / `must_not_cover` / `required_output_items` carries both text and stable id, or just text (with ids derived positionally), or just ids (with text looked up from `contracts.py`).
- What the per-clause JSON shape is for `MustNotCoverClause` with optional `applies_when` predicate and `allowed_contexts`.
- Whether `preferred_lens` rules are embedded per-chapter or deduplicated at the manifest level.
- The estimated size of the JSON block (current template doc is ~1000 lines; per-chapter prose contracts plus lens rules are ~400+ lines of structured data).
- Whether a single HTML comment block is a practical container for this volume of JSON.

**Recommended fix**: Add a concrete JSON Schema or a complete example JSON block (one chapter with all typed fields, plus the Ch3 predicate, plus one Ch2 subcontract) to the plan. The schema must be the contract — reviewers and implementers must be able to mechanically verify that all current typed data can round-trip through it.

### B2. Underspecified projection path from template JSON → typed manifest when `_CURRENT_TEXT_MAPPING` is removed

**Severity**: BLOCKING
**Evidence**: Plan decision 5 (lines 163-173) says to remove `_CURRENT_TEXT_MAPPING` and six code-authored functions from `typed_contracts.py`. Decision 3 (Slice 3, lines 220-233) says `load_typed_template_contract_manifest()` should "Load typed data from the parsed template document." But the plan does not specify the bridging mechanism:

- If the template JSON contains both text AND stable ids (e.g., `{"clause_id": "ch0.must_answer.item_01", "text": "用一句话定义..."}`), then `typed_contracts.py` no longer needs `_CURRENT_TEXT_MAPPING` — it reads ids directly from JSON. But `contracts.py` Parser (decision 4) would also parse the same JSON to produce the untyped `ChapterContract` tuples — raising the question of whether `contracts.py` should also read stable ids from JSON or continue to use positional ordering.

- If the template JSON does NOT contain stable ids, then `_CURRENT_TEXT_MAPPING` (or an equivalent mapping) must still exist somewhere to assign stable ids to text entries. The plan says to remove it — leaving no mechanism for id assignment.

- The plan says `contracts.py` returns untyped `TemplateContractManifest` (which has `tuple[str, ...]` for `must_answer`, no stable ids). But `typed_contracts.py` needs stable ids to construct `MustAnswerClause(clause_id=..., text=...)`. If `typed_contracts.py` receives only the untyped manifest from `contracts.py`, it still needs a text→id mapping.

**Evidence from current code**: `typed_contracts.py:719` — `_assert_exact_text_mapping(chapter.must_answer, text_mapping.must_answer)` — validates exact text match before projection. `typed_contracts.py:686` — `_project_chapter()` reads `_CURRENT_TEXT_MAPPING[chapter.chapter_id]` by chapter id, then maps each text entry to its stable id. If `_CURRENT_TEXT_MAPPING` is removed, this whole path breaks.

**Impact**: The implementer would need to DESIGN the text→id bridging mechanism as part of Slice 2-3 implementation, which is a planning responsibility for a `heavy` gate. Two plausible resolutions with different trade-offs:

- Option A: JSON carries `clause_id` + `text` for every clause. `contracts.py` Parser extracts text tuples; `typed_contracts.py` reads ids directly from JSON. This makes the JSON self-contained but large.
- Option B: `contracts.py` Parser extracts untyped text tuples; `typed_contracts.py` applies a reduced mapping (ids only, no duplicate text) against the untyped tuples by positional index. This keeps JSON smaller but preserves an implicit code-authored ordering dependency.

**Recommended fix**: Decide and document the bridging mechanism explicitly in the plan. If Option A, show the per-clause JSON shape in the schema artifact (see B1). If Option B, clarify that a reduced positional mapping is the only remaining code-authored truth and justify why it doesn't constitute parallel truth.

### B3. `evidence_availability.py` Literal type coupling to requirement ids is not addressed

**Severity**: BLOCKING
**Evidence**: `evidence_availability.py:37-63` defines `EvidenceRequirementId` as a `Literal` type with 24 specific string values (e.g., `"ch2.must_answer.item_01"`, `"ch3.requirement.actual_behavior_reviewed"`). `evidence_availability.py:67` materializes `_KNOWN_REQUIREMENT_IDS = frozenset(get_args(EvidenceRequirementId))`. `evidence_availability.py:344-366` — `_validate_typed_requirement_ids()` checks that all requirement ids referenced by the typed manifest's `applies_when` predicates and `internal_subcontracts` are in `_KNOWN_REQUIREMENT_IDS`.

After this gate:
- The template JSON becomes the truth source for typed contract data, including Ch3 predicate requirement_ids and Ch2 subcontract requirement_ids.
- If the JSON accidentally contains a requirement id NOT in `_KNOWN_REQUIREMENT_IDS`, `derive_evidence_availability()` fails at validation time.
- If the JSON OMITS a requirement id that `_CH2_REQUIREMENT_SPECS` or `_CH3_REQUIREMENT_SPECS` (lines 180-246) expects, the specs reference dead ids.

The plan says `evidence_availability.py` "reads typed requirement ids from projected typed manifest" (line 60) and that behavior is unchanged. But it doesn't address whether:

1. `EvidenceRequirementId` Literal should be relaxed to `str` (since ids now come from an external JSON document, not from code-reviewed constants).
2. `_CH2_REQUIREMENT_SPECS` and `_CH3_REQUIREMENT_SPECS` should be validated against the template JSON at load time.
3. The hardcoded requirement id strings in `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES` (line 254-258) should be cross-referenced with the JSON.

**Impact**: If the template JSON and `evidence_availability.py`'s hardcoded Literal type drift apart (e.g., a template edit renames a requirement id), the system fails at runtime with a ValueError — which is fail-closed. But the plan doesn't specify WHERE this coupling is validated (at template parse time? at `derive_evidence_availability()` time?), and whether the Literal type should be maintained as a compile-time guard or relaxed.

**Recommended fix**: Decide and document: (a) keep `EvidenceRequirementId` as a strict Literal and validate template JSON requirement ids against it at manifest load time, OR (b) relax to `str` and rely on runtime validation. If (a), add this validation to the parser requirements in decision 4. If (b), update `evidence_availability.py`'s type and validation in Slice 4.

---

## High-Severity Findings

### H1. Slice 1 sequencing: template doc is edited as truth source before any code reads it

**Severity**: HIGH
**Evidence**: Plan Slice 1 (lines 187-201) adds the canonical JSON block and replaces per-chapter `CHAPTER_CONTRACT` blocks with `CHAPTER_CONTRACT_REF` — before Slice 2 implements the parser. Between Slice 1 and Slice 2 acceptance:

- `contracts.py` still reads from Python `_CHAPTERS` constants (line 151-755).
- `typed_contracts.py` still projects from `contracts.py` via `_CURRENT_TEXT_MAPPING`.
- The template doc has the JSON block but no code path reads it.
- The per-chapter `CHAPTER_CONTRACT` blocks have been replaced with `CHAPTER_CONTRACT_REF` — so if a human reads the template doc to understand a chapter's contract, they see a short reference instead of the full contract.

**Impact**: This intermediate state creates confusion: the template doc claims to be the truth source but no code treats it as such. If the gate is interrupted after Slice 1, the repo is in an inconsistent state.

**Recommended fix**: Either (a) reorder: implement parser first (add JSON block + parser in Slice 1, then remove per-chapter duplication in a later slice after validation confirms the parser produces identical output), or (b) add a Slice 1 validation step: manually verify that the JSON block, when parsed by a temporary validation script, produces the same data as the current `contracts.py` manifest, before accepting the Slice 1 checkpoint.

### H2. Per-chapter `CHAPTER_CONTRACT_REF` replacement loses human-readable contract locality

**Severity**: HIGH
**Evidence**: Plan decision 3 (lines 138-150) replaces each per-chapter structured `CHAPTER_CONTRACT` block with a short `CHAPTER_CONTRACT_REF` pointing to the canonical JSON. The current per-chapter blocks (e.g., template doc lines 99-160 for Ch0, 188-240 for Ch1) serve as inline documentation for template editors. After replacement, a template editor looking at Ch3 would see:

```text
<!-- CHAPTER_CONTRACT_REF chapter_id: 3 source: TEMPLATE_CONTRACT_MANIFEST_JSON END_CHAPTER_CONTRACT_REF -->
```

instead of the full `must_answer`, `must_not_cover`, `required_output_items`, and `preferred_lens` for Ch3.

**Impact**: The template doc becomes less useful as a human-editable document. The plan acknowledges this risk (line 365) but defers to controller: "If controller requires locality, keep one canonical manifest and add non-authoritative chapter refs only." This is the right framing, but the review must flag that the current plan defaults to removing locality — and the controller should explicitly confirm this choice before implementation.

**Recommended fix**: Add an explicit controller decision point: either accept the locality loss (template is machine-authorable, humans read the JSON), or keep per-chapter contracts as non-authoritative generated comments (adds maintenance burden but preserves readability). The current plan's recommendation (remove duplication) is defensible but should be a conscious trade-off, not an implementation default.

### H3. Parser must validate `preferred_lens` structure but plan doesn't specify lens JSON shape

**Severity**: HIGH
**Evidence**: Plan decision 4 parser requirements (lines 154-160) say "fail closed if title/narrative/must_answer/must_not_cover/required_output/preferred_lens/audit_focus are empty where current validation requires non-empty." The current `preferred_lens` per chapter is a `Mapping[str, TemplateLensRule]` with 6-7 entries per chapter (default + 6 fund types), each containing `fund_type`, `statements` (tuple of strings), `facets_any` (tuple of strings), `priority` (optional string). The plan does not specify:

- How `preferred_lens` is represented in JSON (nested object per fund type? Array of objects with `fund_type` key?).
- Whether `facets_any` with shared values (e.g., `("宽基指数基金", "行业/主题指数基金", "策略指数基金")` appears 7 times across all chapters) should be deduplicated or repeated.
- Whether lens priority values must match the closed set `("core", "high", "medium", "low")` that `contracts.py:23-25` already enforces.

**Impact**: The parser validation for `preferred_lens` cannot be fully specified without knowing the JSON shape. This could lead to an implementation that passes parser validation but produces lens data that downstream consumers (`resolve_preferred_lens()`, `_project_lens_rules()`) reject.

**Recommended fix**: Include the `preferred_lens` JSON shape in the schema artifact (see B1). The parser must enforce the same lens key set and priority closed set that `contracts.py` currently enforces.

---

## Medium-Severity Findings

### M1. `source_manifest` validation (decision 6) needs a negative test case in the validation matrix

**Severity**: MEDIUM
**Evidence**: Plan decision 6 (lines 176-178): "If supplied, validate that its untyped projection equals the parsed template document's untyped projection." The validation matrix (lines 263-314) covers template consistency, typed contracts, writer/auditor, service boundary, and renderer no-regression — but includes no test for "pass `source_manifest` with stale/different data and confirm ValueError."

**Impact**: Without this test, a future code change could weaken the `source_manifest` validation and silently reintroduce a parallel truth path.

**Recommended fix**: Add a test case to the Slice 3 or Slice 4 validation matrix: "call `load_typed_template_contract_manifest(source_manifest=stale_manifest)` and assert ValueError."

### M2. `lru_cache` on template file reads: test clearing mechanism unspecified

**Severity**: MEDIUM
**Evidence**: Plan decision 7 (line 179-180): "Use a small `lru_cache` for parsed template document reads if needed. The cache must be clearable in tests." No mechanism is specified.

**Impact**: Tests that modify the template JSON (e.g., to test malformed-input handling) could get stale cached parses from previous tests. If the clearing mechanism is not designed upfront, test authors may resort to `importlib.reload()` or other fragile patterns.

**Recommended fix**: Specify the clearing mechanism — e.g., a module-level `_clear_template_manifest_cache()` function, or an `@lru_cache` on a function that takes an explicit `path` parameter (so tests can use a tempfile path). Add a test in Slice 2 that demonstrates cache clearing.

### M3. `fund_agent/fund/template/__init__.py` export alignment is mentioned but not specified

**Severity**: MEDIUM
**Evidence**: Plan Slice 3 allowed files (line 221): "`fund_agent/fund/template/__init__.py` if exports require alignment." The current `typed_contracts.py` `__all__` (lines 1272-1294) exports `_CURRENT_TEXT_MAPPING` internal types (`_TextIdMapping`, `_ChapterTextMapping`) which would be removed. But `__init__.py` may or may not re-export them — the plan doesn't check.

**Impact**: Low risk of breakage (removed types would cause ImportError if re-exported), but the plan should confirm whether `__init__.py` currently re-exports any of the to-be-removed symbols.

**Recommended fix**: Grep `__init__.py` for imports from `typed_contracts` and confirm no to-be-removed symbols are re-exported. Document the result in the plan.

### M4. The plan's JSON-block-as-HTML-comment approach doesn't address Markdown linters/validators

**Severity**: MEDIUM
**Evidence**: The plan proposes `<!-- TEMPLATE_CONTRACT_MANIFEST_JSON { ... } END_TEMPLATE_CONTRACT_MANIFEST_JSON -->`. Some Markdown linters or renderers may strip or mangle large HTML comments. The current template doc already uses HTML comments for `CHAPTER_CONTRACT` blocks, so the pattern is established — but the new block is a single large JSON blob, not structured key-value pairs.

**Impact**: If a future tool or CI step processes the template doc through a Markdown formatter that rewraps or truncates long HTML comments, the JSON could be corrupted. Since the parser fails closed on malformed JSON, this would be caught — but it could be a frustrating debugging experience.

**Recommended fix**: Add a CI guard: `git diff --check -- docs/fund-analysis-template-draft.md` or a custom check that the JSON block parses successfully. The validation matrix already includes `git diff --check` (line 307) which catches whitespace issues but not content corruption.

---

## Low-Severity Findings

### L1. The completion report format (lines 369-379) includes "dirty worktree note confirming unrelated untracked artifacts were not staged or modified" — but git doesn't enforce this

**Severity**: LOW
**Evidence**: The plan requires a completion report note about dirty worktree. This is a process requirement, not a code requirement — it relies on the implementer's discipline.

**Impact**: Minimal. The controller judgment already checks worktree state. But the plan could strengthen this by requiring `git status --short` output in the implementation evidence artifact.

**Recommended fix**: Add to implementation evidence requirements: "include `git status --short` output showing only allowed files are modified."

### L2. The plan's docs/control sync (Slice 5) includes `fund_agent/fund/README.md` and `tests/README.md` updates but the current `current-startup-packet.md` line 166 prohibits modifying `docs/fund-analysis-template-draft.md`

**Severity**: LOW
**Evidence**: `docs/current-startup-packet.md:166` — "Do not modify `docs/fund-analysis-template-draft.md`." This is a residual prohibition from the additive-sidecar phase. The current plan explicitly modifies this file (Slice 1). The startup packet must be updated to remove this prohibition — and Slice 5 (docs sync) covers `docs/current-startup-packet.md`. The plan is internally consistent; this finding is only to confirm the prohibition is intentionally lifted.

**Impact**: None if Slice 5 correctly updates the startup packet. The finding is a reminder, not a defect.

**Recommended fix**: In Slice 5, explicitly note that the "Do not modify `docs/fund-analysis-template-draft.md`" prohibition in the startup packet is replaced with the new truth-source arrangement.

---

## Review-Focus Cross-Check

### 1. Is the plan code-generation-ready?

**NO** (due to B1, B2, B3). File ownership, slice structure, tests, and stop conditions are well-specified. But the JSON schema — the single most critical implementation artifact — is described only narratively. An implementer cannot write the parser or the template JSON without first designing the schema, which is a planning responsibility.

### 2. Is the canonical JSON block the best/pragmatic way?

**YES**, with the caveat from H2. Using a single JSON block in an HTML comment avoids creating a new file, keeps the template doc as the single file to edit, and enables strict parsing. The alternative (separate JSON file) would create a new file that could drift from the template doc. The current approach is pragmatic. The locality trade-off (H2) should be explicitly confirmed.

### 3. Does the plan preserve public chapter ids 0-7, Ch2 internal-only subcontracts, deterministic renderer/default analyze/checklist, current --use-llm typed path semantics and fail-closed behavior?

**YES**. These are explicitly listed as non-goals (lines 25-32), enforced by stop conditions (lines 347-358), and baked into the parser requirements (decision 4: "fail closed if public chapter ids are not exactly 0..7"). The classification table (lines 50-69) correctly labels these as "Current implemented fact — Preserve exactly."

### 4. Does it prevent parallel truth in contracts.py/typed_contracts.py and make malformed template edits fail closed?

**PARTIALLY** — the intent is clear, but B2 shows that the mechanism for eliminating `_CURRENT_TEXT_MAPPING` as a parallel truth is underspecified. The parser fail-closed requirements (decision 4) are thorough: missing/duplicated/empty/non-JSON/unknown keys/chapter id drift/empty fields all fail closed. Good.

### 5. Does it clearly separate current implemented facts vs accepted future design vs deferred/rejected content?

**YES**. The classification table (lines 50-69) is explicit and complete. Non-goals (lines 24-32) are comprehensive. The docs/control sync decision (lines 316-326) correctly updates status labels.

### 6. Does it avoid Agent runtime, multi-year runtime, provider budget/default/runtime, score-loop, Ch2 public split, quality/golden/readiness promotion, and unrelated dirty artifacts?

**YES**. All are explicitly listed as non-goals. The allowed files list (lines 73-91) excludes Agent/Host packages, provider config, and score/golden/readiness code. The prohibited files list (lines 93-100) reinforces this.

### 7. Are validation commands sufficient and scoped, with no live provider probes?

**YES**. All validation commands are `pytest` or `ruff` or `git diff --check` based. No `curl`, no API key usage, no network calls. The full regression command (lines 299-301) covers the typed family end-to-end.

---

## Open Questions Requiring Controller Decision

1. **JSON schema**: Who designs it — planner (now) or implementer (during Slice 1)? Recommend planner provides it now (see B1).
2. **Text→id bridging**: Option A (JSON carries ids) or Option B (positional mapping in code)? Recommend Option A for self-contained truth (see B2).
3. **Per-chapter locality**: Remove `CHAPTER_CONTRACT` prose blocks or keep as non-authoritative generated comments? Recommend remove to avoid ambiguity, per plan's own recommendation (see H2).
4. **`EvidenceRequirementId` Literal type**: Keep as strict guard or relax to `str`? Recommend keep as strict guard with cross-validation (see B3).

---

## Residual Risks After Acceptance

- The JSON block in a Markdown HTML comment could be corrupted by Markdown tooling (M4). Mitigated by parser fail-closed behavior.
- The `source_manifest` compatibility path could be weakened by a future change without test coverage (M1). Mitigated by adding the recommended negative test.
- Template doc edits that add new chapters (e.g., a future Ch8 for appendix) would cause the parser to reject the manifest because chapter ids must be exactly 0-7. This is correct fail-closed behavior, but the error message should guide the editor to the right gate.
