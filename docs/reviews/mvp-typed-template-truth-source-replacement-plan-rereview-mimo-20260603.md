# MVP typed template truth-source replacement plan re-review — AgentMiMo

## Reviewer self-check

- Role: AgentMiMo plan re-review worker only.
- Gate: `MVP typed template truth-source replacement gate`; classification `heavy`.
- Actions taken: read plan (including fix addendum), fix evidence, AgentDS review, AgentMiMo review, `fund_agent/fund/template/__init__.py`.
- Actions intentionally not taken: no `/gateflow`, no implementation, no fix, no commit, no provider/runtime/live probe.

## Verdict: PASS-WITH-RISKS

All three DS blocking findings (B1/B2/B3) are resolved with concrete, implementation-ready decisions. All six MiMo findings (F1–F6) are fixed. Two residual risks remain (DS H1 partial mitigation, DS M4 tooling risk) — both have documented mitigations and neither blocks implementation.

---

## Re-review focus findings

### Focus 1: DS B1 — JSON schema/shape concrete enough? **FIXED**

**Evidence**: Plan fix addendum lines 192–374 now specifies:

- Exact top-level keys with types and constraints (`schema_version`, `template_id`, `source_template_id`, `source_path`, `public_chapter_ids`, `chapters`).
- Exact chapter object keys with types (`chapter_id`, `title`, `narrative_mode`, `must_answer`, `must_not_cover`, `required_output_items`, `preferred_lens`, `audit_focus`, `consumes_chapter_conclusions`, `independent_action_source`, `internal_subcontracts`).
- Per-clause shape: `id` (stable authored id) + `text` (exact Chinese text).
- `must_not_cover` extension: `applies_when` (null or evidence predicate object) + `allowed_contexts` array.
- Evidence predicate shape: `predicate_id`, `requirement_ids`, `required_statuses`, `description`.
- `required_output_items` shape: `id`, `text`, `when_evidence_missing` (null or closed-set string), `missing_evidence_reason`.
- `preferred_lens` rule shape: `fund_type`, `statements`, `facets_any`, `priority` (null or closed-set).
- Ch2 internal subcontract shape: `subcontract_id`, `title`, `requirement_ids`, `public_chapter_id` (must be null).
- Representative JSON snippet covering Ch2 (normal chapter + internal subcontract) and Ch3 (evidence predicate + `allowed_contexts`).

**Assessment**: Sufficient for implementation. An implementer can mechanically construct the full JSON and parser from this specification. The unknown-key rejection rule at every object level covers the schema completeness enforcement.

### Focus 2: DS B2 — Text/id bridging explicit and no parallel truth? **FIXED**

**Evidence**: Plan fix addendum lines 376–382 explicitly chooses DS Option A:

- JSON carries stable `id` plus exact `text` for every `must_answer`, `must_not_cover`, and `required_output_items` entry.
- `contracts.py` parses the same JSON and projects only ordered `text` tuples into untyped `ChapterContract`.
- `typed_contracts.py` parses the same JSON and projects `id` + `text` into typed dataclasses.
- `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping` are removed as authored truth.
- Positional ids derived in code are explicitly forbidden.

**Assessment**: No parallel truth remains. Both untyped and typed projections derive from the same parsed JSON document. The bridging mechanism is fully specified.

### Focus 3: DS B3 — EvidenceRequirementId coupling and validation decided? **FIXED**

**Evidence**: Plan fix addendum lines 384–398:

- Decision: keep `EvidenceRequirementId` as a strict `Literal` guard.
- Validation timing: manifest load/projection must fail closed if any template JSON `applies_when.requirement_ids` or `internal_subcontracts[].requirement_ids` value is not in `_KNOWN_REQUIREMENT_IDS`.
- Runtime guard: `_validate_typed_requirement_ids()` remains as second line of defense.
- Tests required: malformed template JSON with unknown requirement id fails at typed manifest load; missing required Ch2/Ch3 evidence requirement from template JSON fails cross-validation test.
- Strict Literal values remain unchanged unless a separate evidence-availability contract gate accepts the change.

**Assessment**: Coupling is explicitly acknowledged and managed. Fail-closed at both load time and runtime. The guard is intentional, not accidental coupling.

### Focus 4: Direct high/medium issues

#### chapter_contract_constraints scope — **FIXED**

**Evidence**: Plan lines 400–408 (fix addendum) + lines 73–78 (allowed files). Module is explicitly in regression scope. Implementation rule: do not change constraint semantics; update only stale wording if parser breaks wrapper comparison. `tests/fund/template/test_chapter_contract_constraints.py` required to prove default constraints still wrap parsed manifest.

**Verified**: `__init__.py` (read during this review) does not import from `chapter_contract_constraints.py`, confirming it is a standalone consumer, not re-exported. No hidden coupling.

#### CHAPTER_CONTRACT_REF locality/authorability decision — **FIXED**

**Evidence**: Plan fix addendum lines 410–420. Controller-facing decision: single canonical JSON is authoritative; per-chapter `CHAPTER_CONTRACT_REF` blocks must not duplicate structured fields. Authorability mitigations: fail-closed parser errors with JSON path, no-provider validation command, tests for missing/duplicated/malformed blocks.

**Assessment**: The locality loss is a conscious trade-off, not an oversight. The mitigation (JSON-path error messages + validation command) is practical. This is the right default for a `heavy` gate eliminating parallel truth.

#### source_manifest negative test — **FIXED**

**Evidence**: Plan fix addendum lines 424–428. `source_manifest` is validation-only; production callers pass `None`. Negative test required: pass stale/different `source_manifest` and assert `ValueError`.

**Assessment**: The compatibility-only framing is clear. The negative test prevents silent reintroduction of a parallel source path.

#### Cache strategy — **FIXED**

**Evidence**: Plan fix addendum lines 430–435. `lru_cache` keyed by explicit path argument. Private `_clear_template_manifest_cache()` helper for tests. Tests use temp path or clear cache. Explicit `importlib.reload()` avoidance. Template metadata reading does not weaken annual report/PDF rule.

**Assessment**: The path-keyed cache design is testable and avoids the fragile patterns DS M2 flagged.

#### `__init__.py` export check — **FIXED**

**Evidence**: Plan fix addendum lines 437–440 states current `__init__.py` does not re-export `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping`, `_AUDIT_FOCUS_BY_CHAPTER`, or removed helpers.

**Verified independently**: Reading `fund_agent/fund/template/__init__.py` confirms this — the file exports from `contracts.py`, `typed_contracts.py`, `chapter_blocks.py`, `item_rules.py`, and `lens_application.py`. The `__all__` list (lines 83–129) contains none of the to-be-removed symbols. Fix evidence claim is accurate.

#### Test-file precheck — **FIXED**

**Evidence**: Plan fix addendum lines 442–445 and plan lines 586–590. Pre-implementation check command provided. If any referenced file is missing, update validation matrix or create focused test file.

#### preferred_lens shape — **FIXED**

**Evidence**: Plan fix addendum lines 240–245. `preferred_lens` is an object keyed by lens key (including `default`). Each value has `fund_type`, `statements` (array of strings), `facets_any` (array), `priority` (null or closed-set `core`/`high`/`medium`/`low`). Representative snippet shows `default` and `index_fund` entries.

**Assessment**: Parser can mechanically validate the lens shape. Priority closed set matches `contracts.py:23-25`.

### Focus 5: Confirm no new risks

**Confirmed**: The plan fix addendum introduces no new scope. Non-goals remain comprehensive (lines 24–33): no Agent runtime, no provider/runtime/live probe, no multi-year, no score-loop, no Ch2 public split, no quality/golden/readiness, no unrelated dirty artifact staging. The fix addendum only resolves the identified gaps within the existing gate scope.

---

## Residual risks (not blocking)

### DS H1 — Slice 1 sequencing: partial mitigation

**Status**: Partially mitigated, not eliminated. The plan now requires (line 457): "if Slice 1 is reviewed separately before Slice 2 parser code, include a temporary manual JSON parse/equality check in implementation evidence." This prevents accepting Slice 1 on visual inspection alone, but the intermediate state (template doc claims truth, no code reads it) still exists briefly.

**Assessment**: Acceptable for plan acceptance. The explicit evidence requirement is a sufficient guard. Full elimination would require resequencing slices, which is disproportionate effort for a transient intermediate state.

### DS M4 — Large JSON in Markdown HTML comment: residual tooling risk

**Status**: Mitigated by parser fail-closed tests and no-provider validation, not eliminated. If Markdown tooling corrupts the HTML comment, the parser will reject it deterministically.

**Assessment**: Acceptable. The corruption scenario is low-probability and fail-closed behavior ensures it cannot silently introduce bad data.

---

## DS B1/B2/B3 and MiMo F1/F2/F3 status summary

| Finding | Status |
|---|---|
| DS B1 — JSON schema concrete | **Fixed** |
| DS B2 — Text/id bridging | **Fixed** (Option A chosen) |
| DS B3 — EvidenceRequirementId coupling | **Fixed** (strict Literal + load-time validation) |
| MiMo F1 — chapter_contract_constraints scope | **Fixed** |
| MiMo F2 — JSON block size/authorability | **Fixed** (controller decision: accept cost; mitigation: JSON-path errors + validation command) |
| MiMo F3 — Prose-vs-JSON contradiction risk | **Fixed** (controller decision: ref-only blocks; no clause summaries outside JSON) |
| MiMo F4 — source_manifest parallel truth | **Fixed** (validation-only, production None, negative test) |
| MiMo F5 — Test-file existence precheck | **Fixed** |
| MiMo F6 — __init__.py exports | **Fixed** (verified: no to-be-removed symbols re-exported) |

---

## Verdict rationale

The plan fix addendum addresses all three DS blocking findings with concrete, mechanically verifiable specifications. The JSON schema is now implementation-ready (B1). The text/id bridging is explicitly decided with no parallel truth (B2). The EvidenceRequirementId coupling is acknowledged, kept as intentional strict guard, and validated at load time (B3). All MiMo findings are resolved, including the previously unscoped `chapter_contract_constraints.py` (F1) and the `__init__.py` export confirmation (F6, independently verified).

The two residual risks (H1 partial mitigation, M4 tooling risk) have documented mitigations and do not block implementation. The plan is code-generation-ready.

**Verdict: PASS-WITH-RISKS** — implementation may proceed.
