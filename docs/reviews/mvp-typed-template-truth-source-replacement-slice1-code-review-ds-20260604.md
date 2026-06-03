# MVP typed template truth-source replacement Slice 1 code review (AgentDS)

## Reviewer self-check

- Role: AgentDS code review worker only for `MVP typed template truth-source replacement gate`, Slice 1.
- Classification: `heavy`.
- CWD: `/Users/maomao/fund-agent`.
- Actions taken: read all required context (plan, controller judgment, contracts.py, typed_contracts.py, template draft, evidence artifact); ran independent validation commands using `uv run python` and `git diff --check`.
- Actions intentionally not taken: no edit, no implementation, no fix, no commit, no PR, no push, no provider/runtime/live probe.
- Scope boundary: review Slice 1 template document only; parser, typed projection, consumer regression, and doc sync are deferred to later slices.

## Review context

- Plan accepted by controller 2026-06-03 with DS/MiMo re-review verdicts `PASS-WITH-RISKS`.
- Slice 1 scope: add canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` block to `docs/fund-analysis-template-draft.md`; replace eight per-chapter structured `CHAPTER_CONTRACT` blocks with non-authoritative `CHAPTER_CONTRACT_REF` blocks.
- Allowed files: `docs/fund-analysis-template-draft.md` only (source code, tests, docs, control files deferred to later slices).
- Review target files: `docs/fund-analysis-template-draft.md` (diff), `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md`.

## Findings

### Finding 1 — PASS: Exactly one canonical JSON block, strict JSON parse, public chapter ids 0–7

Independent validation confirms:
- Exactly 1 `TEMPLATE_CONTRACT_MANIFEST_JSON` block in the template document.
- Block content is strict JSON, parses with stdlib `json.loads()` without error.
- `public_chapter_ids` is exactly `[0,1,2,3,4,5,6,7]`.
- `chapters` array has exactly 8 entries with `chapter_id` values `[0,1,2,3,4,5,6,7]` in order.
- All top-level keys match the plan schema exactly: `schema_version`, `template_id`, `source_template_id`, `source_path`, `public_chapter_ids`, `chapters`. No unknown keys at top level or chapter level.
- `schema_version` = `"typed_chapter_contract.v1"`, `template_id` = `"fund-analysis-template-typed-v1"`, `source_template_id` = `"fund-analysis-template-v1"`, `source_path` = `"docs/fund-analysis-template-draft.md"`.

**Severity**: none (pass).

### Finding 2 — PASS: Stable id + exact text for must_answer, must_not_cover, required_output_items

Every `must_answer`, `must_not_cover`, and `required_output_items` entry carries:
- `id`: stable authored id with correct `ch{N}.{field}.item_{NN}` prefix.
- `text`: exact authored Chinese text.

Cross-validated against current `contracts.py` untyped manifest: all 47 must_answer texts, 34 must_not_cover texts, and 45 required_output texts match exactly in order.

**Severity**: none (pass).

### Finding 3 — PASS: Preferred_lens, audit_focus, dependencies, subcontracts, predicate, missing behavior/reasons

- `preferred_lens`: present for all 8 chapters. Key equals `fund_type` in every rule. Ch1 has no `default` key but covers all 6 FundType values explicitly — consistent with current `contracts.py`. All `statements` non-empty.
- `audit_focus`: present for all chapters, non-empty, all values from closed set `AuditFocusLiteral`. Ch0 = `["final_judgment", "chapter_structure"]`, Ch2 = `["r_abc", "evidence_anchors"]`, Ch3 = `["manager_consistency", "evidence_anchors"]`, etc. — all match current `_AUDIT_FOCUS_BY_CHAPTER`.
- `consumes_chapter_conclusions`: Ch0 consumes `[7]`; all other chapters consume `[]`.
- `independent_action_source`: Ch0 = `false`; all others = `false`.
- Ch2 `internal_subcontracts`: exactly 3 — `performance`, `attribution`, `cost` — all with `public_chapter_id: null`. All `requirement_ids` reference existing clause/output ids within Ch2. No other chapter has internal subcontracts.
- Ch3 `ch3.must_not_cover.item_04` predicate: `predicate_id` = `"ch3.evidence.manager_behavior_style_unreviewed"`, `requirement_ids` = `["ch3.requirement.actual_behavior_reviewed"]`, `required_statuses` = `["missing", "unavailable", "unreviewed"]`, `description` non-empty. `allowed_contexts` = `["required_label", "evidence_gap_statement", "quote", "anchor_caption"]`.
- No other `must_not_cover` items have non-null `applies_when` — only ch3.item_04 has an evidence predicate.
- `when_evidence_missing` / `missing_evidence_reason` consistency: all Ch2 `required_output_items` have `"block"` with non-empty reason; Ch3 items 02-05 have `"render_evidence_gap"` with non-empty reason; Ch3 item 06 has `"render_minimum_verification_question"` with non-empty reason; Ch3 item 01 and all Ch0/1/4/5/6/7 items have `null` behavior with `null` reason. No inconsistent behavior/reason pairs found.

**Severity**: none (pass).

### Finding 4 — PASS: Eight CHAPTER_CONTRACT_REF blocks, zero old CHAPTER_CONTRACT blocks, no structured duplication

- 8 `CHAPTER_CONTRACT_REF` blocks found, one per chapter (ids 0–7).
- 0 old `CHAPTER_CONTRACT` structured blocks found (confirmed via regex).
- No structured contract fields (`must_answer:`, `must_not_cover:`, `required_output_items:`, `preferred_lens:`) found outside the canonical JSON block (verified after removing the ref blocks from the scan area).
- 8 `CHAPTER_GOAL` blocks preserved.
- 8 `ITEM_RULE` blocks preserved.
- Audit appendices (附录 A, 附录 B) preserved.
- Chapter titles, body scaffolding, evidence anchor guidance preserved.

**Severity**: none (pass).

### Finding 5 — PASS: JSON untyped and typed projections match current accepted loaders

Independent cross-validation confirms:
- JSON projection → `load_template_contract_manifest()`: every chapter's `title`, `narrative_mode`, `must_answer` texts, `must_not_cover` texts, `required_output_items` texts, and `preferred_lens` (keys, fund_type, statements, facets_any, priority) match exactly.
- JSON projection → `load_typed_template_contract_manifest()`: every chapter's typed clauses (id + text), required output items (id + text + behavior + reason), preferred_lens rules, audit_focus, dependencies, independent_action_source, and internal_subcontracts match exactly.
- The evidence artifact's temporary manual validation is credible: it provides exact commands and output lines showing 10 PASS results. My independent re-execution confirms all 28 validation checks pass.

**Severity**: none (pass).

### Finding 6 — PASS: No scope creep

Verified:
- Only 2 files changed: `docs/fund-analysis-template-draft.md` (modified, +1473/-403 lines) and the evidence artifact (new untracked).
- No source code, tests, README, design/control/startup, provider/runtime, Agent/Host, renderer, quality gate, baseline/golden changes.
- No deterministic `analyze` / `checklist` behavior claims.
- No public Ch2 split; public chapter ids remain 0–7.
- No Agent runtime, multi-year runtime, provider budget/default/runtime, score-loop, golden/readiness promotion references in the template diff.
- No unrelated untracked artifacts staged or modified.
- `git diff --check` exits 0 (no whitespace issues).

**Severity**: none (pass).

### Finding 7 — OBSERVATION: Temporary validation dependency on code-based manifest

The evidence artifact generated the canonical JSON by reading `load_typed_template_contract_manifest()` from current code. This is the correct approach for Slice 1 — the JSON is a snapshot of current accepted typed truth. The equivalence validation proves the JSON matches what code currently projects. However, this means the JSON's authority depends on the independent cross-validation (Finding 5 above) rather than being independently authored.

Until Slice 2 implements the parser that reads the template document as truth source (and Slice 3 removes code-authored truth), this is expected intermediate state. The plan explicitly accounts for this risk in the controller judgment: "if Slice 1 edits the template document before Slice 2 parser exists, implementation evidence must include a temporary manual JSON parse/equality check."

**Severity**: informational, no fix required for Slice 1 checkpoint. Resolved by Slice 2–3 implementation.

### Finding 8 — OBSERVATION: Ch1 no-default lens pattern

Ch1 `preferred_lens` has no `"default"` key — it instead provides explicit lenses for all 6 FundType values (`index_fund`, `active_fund`, `bond_fund`, `enhanced_index`, `qdii_fund`, `fof_fund`). This matches current `contracts.py` Ch1 behavior exactly. When Slice 2 implements the parser, `validate_template_contract_manifest()` will correctly validate that every fund type has an exact lens match (no `default` fallback needed because all types are covered).

**Severity**: informational, no fix required.

## Validation commands and exact results

### Command 1: git diff --check

```bash
git diff --check -- docs/fund-analysis-template-draft.md
```

Result: exit 0, no output (no whitespace issues).

### Command 2: Independent JSON validation script

Executed a comprehensive 28-check validation script using `uv run python`. The script verified:

- canonical block count and strict JSON parse (checks B1–B2)
- top-level keys exact match (check B3)
- header field values (check B4)
- public_chapter_ids = [0..7] (check B5)
- chapter count and ids (check B6)
- no unknown chapter keys (check B7)
- non-empty required fields (check B8)
- must_answer/must_not_cover id+text shape (check B9)
- required_output_items full shape (check B10)
- preferred_lens key == fund_type (check B11)
- Ch0 consumes Ch7, not independent (check B12)
- Ch2 internal subcontracts correctness (check B13)
- only Ch2 has subcontracts (check B13b)
- Ch3 predicate and allowed_contexts (check B14)
- only Ch3.item_04 has non-null applies_when (check B14b)
- zero old CHAPTER_CONTRACT blocks (check B15)
- 8 CHAPTER_CONTRACT_REF blocks (check B16)
- no structured contract fields outside JSON (check B17)
- JSON projection == current untyped manifest (check B18)
- JSON projection == current typed manifest (check B19)
- audit_focus values in closed set (check B20)
- Ch2 subcontract requirement_ids reference existing ids (check B21)
- only Ch0 consumes conclusions (check B22)
- CHAPTER_GOAL blocks preserved (check B24)
- audit appendices preserved (check B26)
- Ch2 missing behavior correctness (check B27)
- Ch3 missing behavior correctness (check B28)

Result: all 28 checks PASS.

### Command 3: Edge case verification

```bash
uv run python -c "
# verified: lens key coverage, applies_when/allowed_contexts consistency,
# when_evidence_missing/missing_evidence_reason consistency, title/narrative_mode match,
# Ch1 no-default pattern
"
```

Result: zero warnings, zero mismatches.

### Command 4: Scoped file status

```bash
git status --short -- docs/fund-analysis-template-draft.md docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md
```

Result: only the intended two files appear.

### Command 5: Diff stats

```bash
git diff --stat -- docs/fund-analysis-template-draft.md
```

Result: `1 file changed, 1473 insertions(+), 403 deletions(-)`.

## Evidence artifact review

The evidence artifact at `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md` is complete and credible:

- Worker self-check present, stating role and scope boundaries.
- Changed files listed (exactly the 2 allowed files).
- Implemented plan items enumerated with specific verification claims.
- Generation approach documented (helper script, failure/recovery note).
- Validation commands provided with exact output and exit codes.
- Non-goals preserved section present.
- Residual risks identified (Slice 2 parser dependency, authorability, unrelated artifacts).
- Completion status: complete, no stop conditions hit.

## Verdict

**PASS**

No blocking findings. The Slice 1 template document implementation is complete and correct:

1. Exactly one canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` JSON block with strict schema.
2. Public chapter ids 0–7 preserved; Ch2 internal subcontracts with `public_chapter_id: null`.
3. All clause texts, ids, preferred_lens, audit_focus, dependencies, predicates, and missing behavior/reasons match current accepted typed contract state.
4. Eight `CHAPTER_CONTRACT_REF` blocks replace old structured `CHAPTER_CONTRACT` blocks; zero duplication outside canonical JSON.
5. JSON untyped and typed projections independently verified to match current loaders.
6. No scope creep: only allowed files changed; no deterministic/renderer/Agent/runtime/provider/multi-year/score-loop claims.
7. Evidence artifact complete with self-check, validation commands/results, non-goals, residuals.

The two observations (temporary code-dependency for JSON generation, Ch1 no-default lens pattern) are informational and do not block this checkpoint. Both are resolved by planned Slice 2–3 implementation.

## Residual risks carried forward

- Slice 2 parser not yet implemented; template JSON authority currently verified by temporary manual cross-validation rather than by production parser fail-closed path.
- Large JSON in Markdown comment remains authorability-sensitive; strict parser/validation with JSON-path errors (planned in Slice 2) is the accepted mitigation.
- Unrelated untracked artifacts in workspace must remain unstaged by this gate.
