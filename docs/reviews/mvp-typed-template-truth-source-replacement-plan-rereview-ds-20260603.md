# MVP typed template truth-source replacement plan re-review — AgentDS

## Worker self-check

- Gate: `MVP typed template truth-source replacement gate`; classification `heavy`.
- Role: AgentDS plan re-review worker only.
- Actions taken: read accepted plan, fix evidence, DS review, MiMo review, `AGENTS.md`, `__init__.py`; verified test file existence and `chapter_contract_constraints.py` existence.
- Actions intentionally not taken: no implementation, no file edits, no provider/runtime/live probe, no `$gateflow` or `/gateflow`, no commit/push/PR, no controller action.
- CWD: `/Users/maomao/fund-agent`.

## Verdict: PASS-WITH-RISKS

All three DS blocking findings are fixed. All MiMo high/medium findings plus DS high/medium findings have concrete plan decisions. Two residual risks persist and are noted below, neither independently blocking.

---

## DS B1: JSON schema/shape — FIXED

**Original finding**: Missing concrete JSON schema; implementer couldn't write parser without first designing the schema.

**Fix evidence**: Plan lines 191-371 now define exact top-level keys, chapter object keys, per-clause shape, `must_not_cover` clause shape (with `applies_when` + `allowed_contexts`), evidence predicate shape, `required_output_items` shape (with `when_evidence_missing` + `missing_evidence_reason`), `preferred_lens` rule shape, and Ch2 internal subcontract shape. A representative JSON snippet covers one normal chapter plus Ch3 evidence predicate plus Ch2 subcontract.

**Verification**: Schema covers all current typed data fields. The representative snippet is self-consistent. `preferred_lens` shape resolves DS H3: `fund_type`, `statements`, `facets_any`, `priority` with closed set from `contracts.py:23-25`. Unknown keys at any object level must fail closed.

**Residual**: The snippet is illustrative — implementation must author the complete current chapter data. Plan explicitly says "It is invalid to infer omitted current values from code."

---

## DS B2: text/id bridging — FIXED

**Original finding**: Underspecified projection path when `_CURRENT_TEXT_MAPPING` is removed; implementer would need to design the bridging mechanism.

**Fix evidence**: Plan lines 376-382 now explicitly choose DS Option A. JSON carries stable `id` plus exact `text` for every clause/item. `contracts.py` parses same JSON and projects ordered text tuples into untyped `ChapterContract`. `typed_contracts.py` parses same JSON and projects `id` + `text` into typed dataclasses. `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping` removed as authored truth. Positional ids derived in code forbidden.

**Verification**: Single source of truth (template JSON) for both untyped and typed projections. No bridging ambiguity. Code may retain closed-set literal domains, schema-version constants, dataclasses, and parser markers, but not text-to-id mapping or default typed content.

---

## DS B3: EvidenceRequirementId coupling and validation — FIXED

**Original finding**: Plan didn't address whether `EvidenceRequirementId` Literal stays strict, where validation happens, or how requirement specs cross-reference JSON.

**Fix evidence**: Plan lines 384-398 now decide: keep `EvidenceRequirementId` as strict `Literal` guard in `evidence_availability.py`. Manifest load/projection fails closed if any JSON `applies_when.requirement_ids` or `internal_subcontracts[].requirement_ids` is not in `_KNOWN_REQUIREMENT_IDS`. `derive_evidence_availability()` keeps its existing runtime guard as second line. Tests to add: malformed JSON with unknown requirement id fails at typed manifest load; missing Ch2/Ch3 evidence requirement from JSON fails cross-validation; current strict Literal values unchanged unless separate evidence-availability contract gate accepts the change. Explicit requirement specs to cross-validate: `_CH2_REQUIREMENT_SPECS`, `_CH3_REQUIREMENT_SPECS`, `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID`, `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`, `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES`.

**Verification**: Validation timing is explicit: manifest load first, `derive_evidence_availability()` second. Cross-validation tests cover both directions (JSON→code and code→JSON). Drift fails closed at earliest opportunity.

---

## MiMo F1: chapter_contract_constraints scope — FIXED

**Original finding**: Module not in scope or analysis; it's a direct consumer of `load_template_contract_manifest()`.

**Fix evidence**: Plan lines 400-408 now explicitly: include `chapter_contract_constraints.py` in regression scope; prescribe no behavior change if `contracts.py` still returns same `TemplateContractManifest`; if only wording/docstrings become stale, update them; add/update `tests/fund/template/test_chapter_contract_constraints.py` to prove default constraints still wrap `must_answer`/`must_not_cover` from parsed manifest and overlays still resolve.

**Verification**: File exists at `fund_agent/fund/template/chapter_contract_constraints.py`. Test file exists at `tests/fund/template/test_chapter_contract_constraints.py`. Plan allocates this to Slice 4.

---

## MiMo F2/F3 and DS H2: CHAPTER_CONTRACT_REF locality and authorability — FIXED

**Original findings**: Single JSON block hurts human authorability (F2), prose-vs-JSON divergence risk (F3), per-chapter locality loss (H2).

**Fix evidence**: Plan lines 410-420 now: explicit controller-facing decision that single canonical JSON is authoritative; per-chapter `CHAPTER_CONTRACT_REF` blocks must not duplicate structured fields; ref-only blocks with at most a short non-authoritative summary line. Authorability mitigation: fail-closed parser errors with JSON path (e.g., `chapters[3].must_not_cover[3].applies_when.requirement_ids[0]`); no-provider validation path via module CLI or pytest target; tests for missing/duplicated/malformed canonical block and unknown keys.

**Verification**: Decision is now explicit rather than implicit. Authorability cost is acknowledged and accepted. Validation tooling is prescribed.

---

## DS M1 and MiMo F4: source_manifest negative test — FIXED

**Original findings**: No negative test for stale `source_manifest`; `source_manifest` compatibility could reintroduce parallel truth.

**Fix evidence**: Plan lines 424-428 now: `source_manifest` is compatibility-only, production callers pass `None`, non-`None` is validation-only and must not author typed fields. Negative test required: pass stale/different `source_manifest` and assert `ValueError`.

**Verification**: Test requirement is explicit. Production expectation is clear: `None` is the canonical path.

---

## DS M2: cache strategy — FIXED

**Original finding**: `lru_cache` clearing mechanism unspecified for tests.

**Fix evidence**: Plan lines 430-435 now: parse from immutable default repository template path; if `lru_cache` is used, key by explicit path argument; expose private cache clear helper (`_clear_template_manifest_cache()`); tests that mutate temp files use temp path or clear cache; `importlib.reload()` explicitly avoided.

**Verification**: Strategy is concrete and test-safe. Tempfile-path approach is the preferred pattern over reload hacks.

---

## DS M3 and MiMo F6: __init__.py exports — FIXED

**Original finding**: Plan didn't check whether `__init__.py` re-exports to-be-removed symbols.

**Fix evidence**: Plan lines 437-440 now document: current `__init__.py` does not re-export `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping`, `_AUDIT_FOCUS_BY_CHAPTER`, or removed helpers. Keep existing public exports stable.

**Re-review verification**: Read `fund_agent/fund/template/__init__.py` (130 lines). Imports from `typed_contracts` are: `AUDIT_FOCUS_IS_SEMANTIC_ONLY`, `EXPECTED_PUBLIC_CHAPTER_IDS`, `TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION`, `TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID`, `ChapterInternalSubcontract`, `EvidencePredicate`, `MustAnswerClause`, `MustNotCoverClause`, `RequiredOutputItem`, `TypedChapterContract`, `TypedTemplateContractManifest`, `get_typed_chapter_contract`, `load_typed_template_contract_manifest`, `validate_typed_template_contract_manifest`. None of the to-be-removed internal symbols are re-exported. Confirmed.

---

## MiMo F5: test-file precheck — FIXED

**Original finding**: Validation matrices reference test files that may not exist.

**Fix evidence**: Plan lines 442-445 now prescribe pre-implementation check with explicit `rg` command. All 12 referenced test files confirmed to exist via `rg --files tests`:

- `tests/fund/template/test_contracts.py`
- `tests/fund/template/test_typed_contracts.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/template/test_renderer.py`
- `tests/fund/test_evidence_availability.py`
- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/fund/audit/test_audit_programmatic.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_execution_contract.py`
- `tests/ui/test_cli.py`

No missing test files. Validation matrix assertions of coverage are grounded.

---

## DS H3: preferred_lens JSON shape — FIXED (via B1)

**Original finding**: Parser must validate `preferred_lens` structure but plan didn't specify lens JSON shape.

**Fix evidence**: Resolved by B1 schema. Plan lines 240-245 now define `preferred_lens` rule shape: `fund_type` (same as enclosing key), `statements` (non-empty array of strings), `facets_any` (array of strings), `priority` (`null` or one of `core`, `high`, `medium`, `low`). This matches the closed set `contracts.py:23-25` enforces.

---

## Confirmed: no new Agent runtime, provider/runtime/live probe, multi-year, score-loop, Ch2 public split, quality/golden/readiness, unrelated dirty artifact risk

**Verification**:
- Non-goals (plan lines 25-32) explicitly exclude all of the above.
- Classification table (lines 50-69) labels Agent engine/tool-loop migration, multi-year annual evidence, provider runtime calibration as "Accepted future design — Deferred."
- Ch2 public split labeled "Deferred/rejected for this gate — Explicitly disallow."
- `source_strength_by_requirement`, full facet wiring, score-loop labeled "Deferred."
- Allowed files list (lines 73-93) excludes Agent/Host packages, provider config, score/golden/readiness code.
- Validation commands are all `pytest`/`ruff`/`git diff --check` based; no `curl`, no API keys, no network.
- Plan explicitly says (line 8): unrelated untracked artifacts are out of scope and must not be staged.

**No regression found.**

---

## Residual risks (not blocking)

### R1. Slice sequencing: DS H1 partially mitigated

The plan still sequences Slice 1 (template doc edits) before Slice 2 (parser). The fix evidence acknowledges this and requires manual JSON parse/equality evidence if Slice 1 is reviewed separately before Slice 2 parser exists. Full elimination would require resequencing slices, which was not in plan-fix-only scope. The mitigation is adequate: explicit evidence requirement for the intermediate state.

### R2. Markdown tooling vs JSON in HTML comment: DS M4 residual

Large JSON in a Markdown HTML comment could be corrupted by Markdown formatters or linters. The plan mitigates with fail-closed parser tests and no-provider validation, but cannot prevent corruption from external tooling. A CI guard (beyond `git diff --check`) could catch this but is not prescribed in this plan. The current mitigation is reasonable: corruption would fail closed at parse time.

---

## Summary table

| Finding | Severity | Status |
|---|---|---|
| DS B1 — JSON schema | BLOCKING | FIXED |
| DS B2 — text/id bridging | BLOCKING | FIXED |
| DS B3 — EvidenceRequirementId coupling | BLOCKING | FIXED |
| MiMo F1 — chapter_contract_constraints scope | HIGH | FIXED |
| MiMo F2 — JSON authorability | HIGH | FIXED |
| MiMo F3 — prose-vs-JSON risk | MEDIUM | FIXED |
| DS H1 — Slice 1 sequencing | HIGH | MITIGATED (not eliminated) |
| DS H2 — per-chapter locality | HIGH | FIXED |
| DS H3 — preferred_lens shape | HIGH | FIXED (via B1) |
| DS M1 / MiMo F4 — source_manifest test | MEDIUM | FIXED |
| DS M2 — cache strategy | MEDIUM | FIXED |
| DS M3 / MiMo F6 — __init__.py exports | MEDIUM | FIXED |
| DS M4 — Markdown tooling risk | MEDIUM | RESIDUAL |
| MiMo F5 — test-file existence | LOW | FIXED |

---

## Re-review questions

1. **Is the plan now code-generation-ready?** YES. JSON schema is concrete, bridging mechanism is explicit, EvidenceRequirementId coupling is decided, all high/medium findings have plan decisions. An implementer can proceed.

2. **Is there exactly one authored template contract truth source?** YES. The canonical JSON block in `docs/fund-analysis-template-draft.md` is the sole authored source. Both `contracts.py` and `typed_contracts.py` parse/project/validate from it.

3. **Does code still preserve public chapter ids 0-7 and current deterministic behavior?** YES. Enforced by parser fail-closed and stop conditions.

4. **Did any typed field remain authored only in code as parallel truth?** NO. All authored typed content moves to JSON. Code keeps only schema/validation/parsing, not authored data.

5. **Are malformed template edits fail-closed?** YES. Unknown keys, missing blocks, non-JSON, chapter id drift, empty fields — all fail at parse time.

6. **Are Agent runtime, multi-year runtime, provider runtime, score/golden/readiness, and Ch2 public split still out of scope?** YES. Confirmed against non-goals, allowed files, classification table, and validation commands.
