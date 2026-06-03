# MVP typed template contract Slice 0 calibration/precondition evidence — AgentDS review

## Reviewer Self-Check

- Role: AgentDS independent reviewer only. No implementation, no source/test/control/design/template truth edits, no commit/push/PR.
- Gate: `MVP typed template contract Slice 0 calibration/precondition gate`.
- Classification: `heavy`.
- Target artifact: `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md`.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-controller-judgment-20260603.md`, and scoped code files `fund_agent/fund/chapter_auditor.py`, `fund_agent/fund/audit/contract_rules.py`, `fund_agent/fund/template/contracts.py`, `fund_agent/fund/template/renderer.py`.
- Verified source code line references in the evidence document against current code on disk.
- Actions intentionally not taken: no code/test/control/design edits, no live probe, no commit/push/PR.

## Conclusion

**PASS** — no blocking findings.

The Slice 0 calibration evidence artifact satisfies all eight hard preconditions from the accepted typed-template planning controller judgment (precondition 8 applies to Slice 6, not Slice 0). All claims are grounded in same-source code evidence that matches the current state of the repository. The taxonomy, allowed-context matching rules, required-output block criteria, and future-slice preconditions are complete and internally consistent.

Residual risks are noted below; none are blocking for this gate.

---

## Criteria Review

### 1. Hard Preconditions from Controller Judgment

**Precondition 1** (output form): Satisfied. Section 1 declares output form as "reference markdown only" and explicitly defers fixture/test-data module creation to Slice 4. Suggested future fixture shapes (`tests/fund/fixtures/ch3_polarity_cases.py`) are offered as forward guidance, not as Slice 0 deliverables. The distinction between reference artifact and future reusable module is clear.

**Precondition 2** (deterministic allowed_contexts matching): Satisfied. Section 3 defines matching rules for `required_label`, `evidence_gap_statement`, `quote`, and `anchor_caption` with explicit structural/lexical conditions (colon position, gap markers, quote introducers, anchor marker format). The rules explicitly forbid LLM judgment. The "Explicitly Not Allowed As Context" subsection closes common loophole patterns (generic hedges, `证据不足` whitelisting later positives, required label + conclusion on same line).

**Precondition 3** (C2 code path / root cause): Satisfied. Section 4 correctly identifies the emitting path as `chapter_auditor.py:_audit_must_not_cover()` → `_must_not_cover_phrases()` → `_clean_must_not_cover_fragment()`. The root cause is accurately characterized: global substring matching over extracted phrase fragments with no concept of allowed contexts, evidence availability, or assertion polarity. Code line references verified against current disk state.

**Precondition 4** (coverage rules / duplicate enforcement): Satisfied. Section 4 correctly distinguishes three separate paths: `_FORBIDDEN_CONTENT_RULES` (contract_rules.py:185, Ch3 entries cover only 性格/人品/动机), `_MUST_NOT_COVER_COVERAGE_RULES` (contract_rules.py:197, Ch3 style clause routed as `narrative_guidance`), and `chapter_auditor.py` runtime phrase extraction (global substring match that bypasses both declarations). The validation at contract_rules.py:674 preventing simultaneous programmatic + non-programmatic declaration is correctly cited. Section 8 extends this into explicit future Slice 4 requirements for deduplication.

**Precondition 5** (renderer degradation preservation): Satisfied. Section 6 maps all six relevant renderer functions with verified line references: `_render_chapter_3()` at 1086, `_chapter_3_consistency_summary_line()` at 1140, `_chapter_3_style_stability_line()` at 1162, `_chapter_3_consistency_rollup_line()` at 1180, `_chapter_3_dimension_line()` at 1202, `_chapter_3_next_minimum_validation_line()` at 1233. The section correctly notes the current coarse default (`_is_active_fund()` checking only `classified_fund_type == "active_fund"`) and requires future typed semantics to formalize rather than fork this path.

**Precondition 6** (explicit reviewed mapping, no fuzzy matching): Satisfied. Section 7 enumerates four matching prohibitions (fuzzy, substring, embedding/LLM, auto-normalization beyond whitespace) and requires fail-closed for unmapped strings. Suggested id style is labeled "not implemented here."

**Precondition 7** (issue-id serializer impact): Satisfied. Section 8 explicitly requires serializer and retained artifact impact analysis before issue-id format changes. The unresolved-items list correctly defers the exact stable format decision to controller/Slice 4.

**Precondition 8** (Slice 6 Ch7 bundle decision): Not applicable to Slice 0. This precondition binds Slice 6 implementation, not the calibration artifact. The evidence correctly does not attempt to resolve it.

### 2. Output Form: Reference Markdown vs Future Fixture Ownership

Clear. Section 1 states Slice 0 is "reference markdown only" and explains why fixture module creation would violate the docs-only scope. The forward-looking fixture shape suggestions use "Suggested future fixture shape, not created in Slice 0" language, which correctly separates aspiration from deliverable.

### 3. Deterministic allowed_contexts Matching Without LLM Judgment

Well-specified. Each context (`required_label`, `evidence_gap_statement`, `quote`, `anchor_caption`) has:
- Positive conditions for allowance (structural/lexical tests)
- Negative examples showing what is blocked
- An explicit prohibition on LLM-based semantic inspection (Section 3 final bullet: "Retained provider/auditor text must not be inspected semantically by an LLM to decide context")

The `required_label` rules correctly handle the key edge case: label text containing forbidden phrases is allowed only when the post-colon content is non-assertive, and the label + positive conclusion on the same line is explicitly blocked.

### 4. Ch3 C2 Code Path / Root Cause Identification

Verified accurate. Key claims confirmed against current code:

| Evidence claim | Code location | Verification |
|---|---|---|
| `audit_chapter_programmatic()` aggregates `_audit_must_not_cover()` | chapter_auditor.py:342-353 | Confirmed: `_audit_must_not_cover(input_data)` in issues tuple at line 347 |
| `_audit_must_not_cover()` iterates must_not_cover clauses, extracts phrases, matches in markdown | chapter_auditor.py:557-584 | Confirmed: substring match loop at lines 572-583 |
| `_must_not_cover_phrases()` removes negative prefix, splits, keeps fragments >= 4 chars | chapter_auditor.py:741-761 | Confirmed: regex removal + split + length filter at lines 754-760 |
| `_clean_must_not_cover_fragment()` strips generic words, does not preserve polarity | chapter_auditor.py:798-814 | Confirmed: stopword stripping at lines 811-814 |
| `_FORBIDDEN_CONTENT_RULES` Ch3 entries are 性格/人品/动机 only | contract_rules.py:185-195 | Confirmed: lines 188-189 |
| Ch3 style clause in `_MUST_NOT_COVER_COVERAGE_RULES` is `narrative_guidance` | contract_rules.py:276-281 | Confirmed: lines 276-281 with rationale about lacking stable low-false-positive markers |
| Overlap validation between programmatic + non-programmatic | contract_rules.py:674-717 | Confirmed: overlap check at lines 708-711 raises ValueError |

The root cause characterization is accurate: `_audit_must_not_cover()` does global substring matching without awareness of allowed contexts, evidence availability, or assertion polarity. The retained artifact field references (`issue_id=programmatic:C2:言行一致:db9a79f992`, `chapter_id=3`, `failure_category=prompt_contract`, `failure_subcategory=code_bug_other`, `stop_reason=repair_budget_exhausted`) are cited as safe diagnostic fields without raw prompt/provider content, consistent with the gate's allowed evidence scope.

### 5. RequiredOutputItem Behavior: Gap vs Block vs Delete-if-not-applicable

Well-distinguished. The three behaviors have clear, mutually exclusive conditions:

- `render_evidence_gap`: item is still required, missing evidence can be safely disclosed, output = label + gap statement + next verification question
- `block`: item cannot be truthfully rendered even as gap, would force unsupported judgment, or missing state is unreviewed for a contractually-reviewed item. Block means fail closed.
- `delete_if_not_applicable`: conditional item with deterministically false predicate + typed reason + traceability. Explicitly forbidden for active-fund Ch3 consistency/style labels.

Section 6 preserves the existing active-fund Ch3 renderer degradation and correctly requires formalization rather than replacement. The current limitation note (coarse `_is_active_fund()` default) is factual and properly scoped as "preserve as fact, not as final design."

### 6. Slice 1 Adapter Mapping: Explicit Reviewed Only, No Fuzzy Matching

Section 7 enumerates four explicit prohibitions and a fail-closed rule for unmapped strings. The suggested id style is labeled as forward-looking suggestion only. Public chapter id constraint (`0-7`) and Ch2 internal subcontract constraint are preserved.

### 7. Slice 4 Duplicate Enforcement and Issue-ID Serializer Impact

Section 8 makes four explicit required decisions for Slice 4, covering:
- Migration of Ch3 clause out of global phrase extraction
- Continued role of `_FORBIDDEN_CONTENT_RULES`
- Consistent update of `_MUST_NOT_COVER_COVERAGE_RULES`
- Prohibition on dual enforcement (old phrase extraction + new typed clause)

The unresolved items list correctly defers to controller/Slice 4: scope of `_audit_must_not_cover()` migration, exact issue id format, fixture module path, and scope of quote/anchor-caption context engine. Issue-id serializer impact is called out explicitly.

### 8. Non-Goals Compliance

Section 10 lists 11 non-goals and 7 safety constraints, all consistent with the controller judgment's unauthorized items. The self-check header additionally confirms no source/test/control/design edits. No violations detected.

---

## Residual Risks (Non-Blocking)

| # | Risk | Severity | Notes |
|---|---|---|---|
| R1 | Allowed-context matching rules are specified but not implemented; edge cases may emerge at Slice 4 | Low | The rules are deterministic and narrow; implementation should add parameterized tests for each edge case in the taxonomy |
| R2 | `_MUST_NOT_COVER_COVERAGE_RULES` narrative-guidance declaration and `chapter_auditor.py` phrase extraction create a genuine architectural tension that Slice 4 must resolve | Medium | Section 8 explicitly addresses this; resolution quality depends on Slice 4 design |
| R3 | Issue-id migration from `phrase:hash` to `clause_id` impacts retained artifact compatibility | Medium | Section 8 flags this as unresolved; the precondition requires impact analysis before implementation, which is correctly deferred |
| R4 | Current `_is_active_fund()` coarse default may mask cases where an active fund actually has reviewed style evidence | Low | Section 6 correctly notes this as a current limitation to preserve, not a final design; future `EvidenceAvailability` should replace the coarse default |
| R5 | The forward-looking fixture shape in Section 1 is suggestive only; Slice 4 is not bound by it | Low | Acceptable for a calibration artifact; Slice 4 owns the final encoding |

---

## Verifier Matrix Confirmation

All rows in Section 9 verifier matrix are consistent with the evidence body above. The review checklist items at the bottom of Section 9 can all be answered affirmatively based on the evidence presented and code verification:

- [x] `未见明显不一致` classified as quasi-positive and blocking under missing/unreviewed evidence (Section 2, hard rule)
- [x] Required labels allowed only before colon with non-assertive post-colon text (Section 3, `required_label`)
- [x] Artifact avoids LLM judgment for allowed-context matching (Section 3, explicit prohibition; Section 3 final bullet)
- [x] Root-cause section cites same-source code (Section 4, verified line references)
- [x] Distinguishes `_FORBIDDEN_CONTENT_RULES`, `_MUST_NOT_COVER_COVERAGE_RULES`, and `chapter_auditor.py` runtime phrase extraction (Section 4)
- [x] RequiredOutputItem prevents silent deletion of active-fund Ch3 labels (Section 5, delete_if_not_applicable prohibition)
- [x] Future Slice 4 note requires duplicate-enforcement avoidance and serializer impact analysis (Section 8)

---

## Validation

```bash
git diff --check -- docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-review-ds-20260603.md
```

Secret-safety statement: this review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
