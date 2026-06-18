# MVP typed template truth-source replacement plan review — MiMo

## Reviewer Self-Check

- Role: AgentMiMo plan review worker only.
- Gate: `MVP typed template truth-source replacement gate`; classification `heavy`.
- Actions taken: read plan, AGENTS.md, design.md, implementation-control.md, current-startup-packet.md, fund-analysis-template-draft.md, contracts.py, typed_contracts.py, chapter_contract_constraints.py, evidence_availability.py, chapter_writer.py, chapter_auditor.py, aggregate deepreview controller judgment, slice8 controller judgment.
- Actions intentionally not taken: no `/gateflow`, no implementation, no fix, no commit, no provider/runtime/live probe.

## Findings

### F1 — [HIGH] chapter_contract_constraints.py not in scope or analysis

**Evidence**: The plan lists `fund_agent/fund/template/contracts.py` and `fund_agent/fund/template/typed_contracts.py` as affected files, but never mentions `fund_agent/fund/template/chapter_contract_constraints.py`. This module at lines 130-248 loads the source manifest via `load_template_contract_manifest()`, then validates `source_manifest_template_id` and re-wraps `must_answer`/`must_not_cover` from the source manifest into `ChapterExecutableConstraint` objects. It is a direct consumer of the untyped manifest and will break if `contracts.py` changes its loading semantics without updating this sidecar.

**Impact**: If `contracts.py` changes `load_template_contract_manifest()` to parse from the template doc, `chapter_contract_constraints.py` will still work as long as the returned data matches, but its `validate_chapter_contract_constraint_manifest()` re-loads the manifest at line 266 and compares — any structural change in how the manifest is constructed could cause validation drift. The plan should explicitly confirm this module is either (a) in scope as an affected file or (b) confirmed to need no changes because it only consumes the public API.

**Recommended fix**: Add `fund_agent/fund/template/chapter_contract_constraints.py` to the "Allowed implementation files" list (or explicitly confirm it is a no-change consumer). Add a regression test path: `tests/fund/test_chapter_constraints.py` if it exists, or add a targeted test in Slice 4.

### F2 — [HIGH] JSON block size and authorability risk

**Evidence**: The plan proposes a single canonical JSON block in `docs/fund-analysis-template-draft.md` containing all typed contract data. The current `_CURRENT_TEXT_MAPPING` in `typed_contracts.py` (lines 237-560) alone is ~320 lines of exact Chinese text + stable id pairs. Adding `_AUDIT_FOCUS_BY_CHAPTER`, `_CH3_STYLE_EVIDENCE_UNREVIEWED`, `_build_internal_subcontracts`, `_required_output_missing_behavior`, `_required_output_missing_reason`, `_must_not_cover_predicate`, `_must_not_cover_allowed_contexts`, plus the full per-chapter `must_answer`, `must_not_cover`, `required_output_items`, `preferred_lens` with all 6-7 fund type lenses each — the JSON block would be 1500-2000+ lines of strict JSON embedded in a Markdown HTML comment.

**Impact**: A human author editing the template doc must now maintain a massive JSON block alongside the prose. This is strictly worse than the current arrangement (prose in `.md`, code in `.py`) for human authorability. The JSON block becomes the de facto truth but is harder to read, edit, and review than either the current prose or the current code. Any typo in the JSON (trailing comma, missing quote, wrong stable id) will fail-closed at parse time, which is correct for safety but will create a poor authoring experience.

**Recommended fix**: The plan should explicitly scope what JSON fields are "authored by hand" vs "generated/maintained by tooling." If the intent is that the JSON block is machine-generated from a future authoring tool, state that. If it is hand-authored, the plan should acknowledge the authorability cost and propose a validation tooling slice (e.g., a `validate-template-doc` script) to catch JSON errors before code loads them.

### F3 — [MEDIUM] Prose-vs-JSON internal contradiction risk

**Evidence**: The plan says (Slice 1, line 193): "Keep `CHAPTER_GOAL`, chapter body scaffolding, ITEM_RULE comments, and evidence anchor guidance." And replaces structured `CHAPTER_CONTRACT` blocks with `CHAPTER_CONTRACT_REF`. But the template doc currently has the full `CHAPTER_CONTRACT` prose (must_answer, must_not_cover, required_output_items, preferred_lens) as visible comments alongside the chapter scaffolding (e.g., lines 99-160 for Ch0). After the plan, the prose contract fields disappear and become a JSON block elsewhere.

**Impact**: Human readers of the template doc lose the inline contract context. The `CHAPTER_CONTRACT_REF` ref says "source: TEMPLATE_CONTRACT_MANIFEST_JSON" but doesn't tell the reader what the contract says. This reduces the template doc's self-contained readability. More critically, if anyone edits the prose chapter scaffolding (e.g., adds a new section heading) without updating the JSON, the JSON and prose diverge silently — the parser only validates the JSON, not its relationship to the prose.

**Recommended fix**: The plan should either (a) keep a human-readable summary of each chapter's contract inline (e.g., a short bullet list of must_answer items) alongside the `CHAPTER_CONTRACT_REF`, or (b) explicitly state that the template doc is no longer intended for human authoring of contract terms and that contract editing happens in the JSON block only.

### F4 — [MEDIUM] `source_manifest` compatibility decision may re-introduce parallel truth

**Evidence**: Plan decision 6 (lines 176-177): "Preserve `load_typed_template_contract_manifest(source_manifest: TemplateContractManifest | None = None)` for compatibility, but do not use `source_manifest` to author typed fields. If supplied, validate that its untyped projection equals the parsed template document's untyped projection, then return the canonical typed manifest."

**Impact**: This means the `source_manifest` parameter is kept but its purpose changes from "source of typed fields" to "validation-only cross-check." However, the current `typed_contracts.py` at line 598 uses `source_manifest` as the input to `_project_chapter()`. After the plan, the code must parse the template doc AND optionally compare against a passed-in manifest. This creates two code paths: one from template doc (canonical) and one from in-memory manifest (validation). If the validation path ever diverges from the template doc path, the comparison itself becomes a source of bugs. The plan should clarify: after this gate, is `source_manifest` ever expected to be non-None in production code paths, or is it test-only?

**Recommended fix**: Make `source_manifest` a test-only parameter (e.g., rename to `_source_manifest_for_test_validation`) or remove it entirely. If it must remain for backward compatibility, document that production callers must not pass it.

### F5 — [LOW] Validation commands include test files that may not exist yet

**Evidence**: The tests/validation matrix (lines 269-314) references `tests/fund/template/test_contracts.py`, `tests/services/test_execution_contract.py`, `tests/services/test_fund_analysis_service_llm.py`, `tests/ui/test_cli.py`, `tests/fund/template/test_renderer.py`, `tests/fund/audit/test_audit_programmatic.py`. Some of these may exist from prior gates, but the plan should confirm they exist and pass before implementation begins, not discover missing tests mid-slice.

**Impact**: Low — the implementation slices will create/update tests as needed. But listing non-existent test files in the validation matrix gives a false sense of coverage.

**Recommended fix**: Add a pre-implementation check: "Confirm all referenced test files exist; create empty pass-through tests if any are missing before Slice 2 begins."

### F6 — [LOW] Plan does not address `fund_agent/fund/template/__init__.py` exports

**Evidence**: The affected files list includes `fund_agent/fund/template/__init__.py` "only if exports need no-behavior-change alignment" (line 78). The plan does not specify what exports this module currently has or what might need to change.

**Impact**: Low — the `__init__.py` likely re-exports from `contracts.py` and `typed_contracts.py`. If the public API names are preserved (as the plan states), no change is needed. But the plan should confirm by reading the file.

**Recommended fix**: Read `fund_agent/fund/template/__init__.py` before implementation and confirm no export changes are needed.

### F7 — [INFO] Risks/open questions section correctly identifies key risks

**Evidence**: The plan's risks section (lines 362-367) identifies JSON-prose inconsistency, path/caching issues, per-chapter vs single-block locality, and test assertion updates. These are all valid and well-mitigated.

**Impact**: No action needed — the risk analysis is sound.

## Review Questions Addressed

### Q1: Is the plan code-generation-ready?

**Answer**: Mostly yes, with caveats. The 5 slices have clear file ownership, parser decisions, stop conditions, and checkpoint criteria. The main gap is F1 (missing `chapter_contract_constraints.py` from scope) and F2 (no authoring tooling plan for the JSON block). With those addressed, the plan is code-generation-ready.

### Q2: Is the canonical JSON block the best approach?

**Answer**: It is the most pragmatic single-truth approach, but F2 and F3 highlight real costs. The alternative — per-chapter JSON blocks — would be worse for cross-chapter validation. The single-block approach is defensible if accompanied by a validation tool (F2) and either inline summaries or a clear "contract editing happens in JSON" contract (F3).

### Q3: Does the plan preserve public chapter ids 0-7, deterministic renderer, typed path semantics, and fail-closed behavior?

**Answer**: Yes. The plan explicitly preserves all of these in the non-goals and implementation decisions. The `contracts.py` parser will project to the same `ChapterContract` dataclasses, so renderer/deterministic behavior is unchanged. The typed path receives the same data from the template doc as it currently does from code, so writer/auditor semantics are preserved.

### Q4: Does it prevent parallel truth and fail-closed on malformed edits?

**Answer**: Yes for code parallel truth — `_CURRENT_TEXT_MAPPING` and other code-authored constants are removed. The template doc JSON becomes the sole source. Fail-closed is achieved by strict JSON parsing with unknown-key rejection. However, F3 introduces a new form of "prose vs JSON" parallel truth within the template doc itself.

### Q5: Does it clearly separate current facts vs future design vs deferred?

**Answer**: Yes. The classification table (lines 52-69) is thorough and well-structured. The non-goals are comprehensive.

### Q6: Does it avoid prohibited areas?

**Answer**: Yes. Agent runtime, multi-year runtime, provider budget/default/runtime, score-loop, Ch2 public split, quality/golden/readiness promotion, and dirty artifacts are all explicitly excluded.

### Q7: Are validation commands sufficient?

**Answer**: Yes, with F5 caveat. The commands cover template consistency, typed consumers, writer/auditor, service, deterministic no-regression, and static quality. No live provider probes.

## Verdict

**PASS-WITH-RISKS**

The plan is architecturally sound and code-generation-ready after addressing F1 (scope gap) and acknowledging F2/F3 (authorability costs). No blocking open question remains before implementation, but the controller should decide:

1. Whether `chapter_contract_constraints.py` needs explicit scope inclusion (F1).
2. Whether a template-doc validation tooling slice is needed in this gate or deferred (F2).
3. Whether inline contract summaries accompany `CHAPTER_CONTRACT_REF` (F3).

These are controller judgment calls, not implementation blockers.
