# MVP typed template contract Slice 4 Ch3 evidence-conditional must_not_cover code review DS

## Worker Self-Check

- Role: AgentDS code review worker only. No file edits, stage, commit, push, PR, or live provider probe.
- Gate: `MVP typed template contract Slice 4 Ch3-first evidence-conditional must_not_cover implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, Slice 4 implementation evidence, Slice 0 calibration sections 2/3/4/8/9, full uncommitted diff of all 7 touched files.
- Validation executed: all four commands ran to completion (see Validation Results below).

## Validation Results

| Command | Result |
|---|---|
| `uv run pytest tests/fund/test_chapter_auditor.py tests/fund/audit/test_audit_programmatic.py` | 86 passed in 0.83s |
| `uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py` | 16 passed in 0.47s |
| `uv run ruff check fund_agent/fund tests/fund` | All checks passed |
| `git diff --check -- <touched files>` | exit 0, no whitespace issues |

## Review Focus Findings

### Focus 1: Typed MustNotCoverClause + EvidenceAvailability integration is Ch3-first and additive

**PASS — no findings.**

- `fund_agent/fund/chapter_auditor.py:79-81`: `_TYPED_MUST_NOT_COVER_CLAUSE_IDS` contains only `ch3.must_not_cover.item_04`. No other typed clause ids are present, confirming Ch3-first scope.
- `fund_agent/fund/chapter_auditor.py:193-198`: `_audit_typed_must_not_cover()` gates on exact clause id membership; other typed clauses are silently skipped.
- Integration reads `writer_input.evidence_availability` (which is additive `ChapterWriterInput` field from Slice 2/3) without modifying the existing `ChapterWriterInput` schema.
- Typed sidecar (`typed_contracts.py`) remains additive alongside `contracts.py`; no manifest truth replacement.

### Focus 2: ch3.must_not_cover.item_04 applies from availability predicate

**PASS — no findings.**

- `fund_agent/fund/template/typed_contracts.py:573-577`: Predicate `ch3.evidence.manager_behavior_style_unreviewed` now references single aggregate requirement `ch3.requirement.actual_behavior_reviewed` instead of the former two split requirements (`turnover_rate_reviewed`, `cross_period_style_evidence_reviewed`). This is consistent with Slice 0 calibration which treats "actual behavior/style evidence" as a unified predicate trigger.
- `fund_agent/fund/chapter_auditor.py:242-266`: `_typed_must_not_cover_applies()` resolves each requirement against `EvidenceAvailability`, treats unknown requirement ids as fail-closed (`requirement is None → return True`), and triggers on any match in `required_statuses` (`missing`, `unavailable`, `unreviewed`).
- Blocking behavior is correct: when predicate activates on missing/unavailable/unreviewed status, positive/quasi-positive claims are blocked in `_audit_ch3_style_must_not_cover_clause()`.

### Focus 3: Missing EvidenceAvailability does not create silent pass

**PASS — no findings.**

- `fund_agent/fund/chapter_auditor.py:196-197`: When `writer_input.evidence_availability is None`, the clause is still audited **with `allow_contexts=False`**. This means allowed label/gap exceptions are disabled, and any positive/quasi-positive claim triggers C2 fail-closed.
- `tests/fund/test_chapter_auditor.py:914-935`: `test_ch3_positive_consistency_claim_blocks_without_evidence_availability` explicitly verifies this: `include_evidence_availability=False` for text `言行一致性判断：言行一致。` still results in `status == "fail"` with `issue_id == "programmatic:C2:ch3.must_not_cover.item_04"`.
- No path exists where absent `EvidenceAvailability` causes a silent pass for unsafe claims.

### Focus 4: Required_label and evidence_gap_statement allowed contexts are narrow

**PASS — no findings.**

- `fund_agent/fund/chapter_auditor.py:392-414`: `_is_required_label_context()` only allows when: prefix before first colon matches `_CH3_REQUIRED_LABELS`, and suffix is either empty, a gap statement, or non-assertive. Label followed by positive conclusion (e.g. `言行一致性判断：言行一致。`) is correctly blocked because suffix `言行一致` matches `_CH3_STYLE_CLAIM_PHRASES` and is neither gap nor non-assertive.
- `fund_agent/fund/chapter_auditor.py:453-474`: `_is_evidence_gap_statement_context()` requires BOTH a gap marker AND a denial word; after-denial text is checked via `_contains_reversing_positive_claim()` for reversal markers (`但`, `但是`, `不过`, `然而`, `总体`, `仍`, `依然`) followed by claim phrases.
- `fund_agent/fund/chapter_auditor.py:495-512`: `_contains_reversing_positive_claim()` correctly catches `证据不足，但未见明显不一致` (gap reversal into quasi-positive), while allowing `不能据此判断言行一致` (denial scoping the claim phrase without reversal).
- `fund_agent/fund/chapter_auditor.py:515-537`: `_is_quote_context()` requires claim phrases ENTIRELY inside Chinese quotes or backticks (verified span-by-span in `_claim_phrases_only_inside_quotes`), a quote introducer on same or previous line, and no author conclusion markers or claim phrases in suffix after the last quote.
- `fund_agent/fund/chapter_auditor.py:638-654`: `_line_is_contract_or_anchor_metadata()` filters out `<!-- required_output:...-->`, `<!-- anchor:...-->`, and `> 📎 证据：` lines BEFORE context analysis — anchor captions never reach the claim phrase scanner.
- Slice 0 calibration explicitly forbids generic hedges (`可能`, `倾向`, `目前看`, `未见明显`) as allowed contexts; none appear in the allowed context code.

### Focus 5: Old global phrase extraction no longer duplicates Ch3 style clause

**PASS — no findings.**

- `fund_agent/fund/chapter_auditor.py:651-656`: In `_audit_must_not_cover()`, `_typed_must_not_cover_clause_texts()` returns the exact manifest text of typed clauses, and the global phrase loop skips matching clauses via `if clause in typed_clause_texts: continue`.
- `fund_agent/fund/chapter_auditor.py:205-223`: `_typed_must_not_cover_clause_texts()` only returns text for clauses in `_TYPED_MUST_NOT_COVER_CLAUSE_IDS`, so other `must_not_cover` clauses (Ch2, Ch5, etc.) continue through the old global phrase extraction.
- This eliminates the previous false positive where `言行一致` in a required label or gap statement was caught by the global substring match. The typed path now owns Ch3 style enforcement with proper context awareness.

### Focus 6: audit_focus remains semantic-only

**PASS — no findings.**

- `tests/fund/test_chapter_auditor.py:957-975`: `test_audit_focus_cannot_disable_programmatic_must_not_cover` verifies that quasi-positive `风格稳定性判断：基本稳定。` is blocked even when (or regardless of) audit_focus settings. The test uses standard `_ch3_typed_audit_input()` which includes the typed contract with `audit_focus` fields; the C2 blocker fires regardless.
- The typed must_not_cover code path has no audit_focus gating — `_audit_typed_must_not_cover()` is called unconditionally from `_audit_must_not_cover()`.

### Focus 7: contract_rules coverage route is consistent

**PASS — no findings.**

- `fund_agent/fund/audit/contract_rules.py:279-283`: The Ch3 style clause coverage rule changed from `narrative_guidance` to `typed_programmatic_evidence_conditional` with rationale "由 typed MustNotCoverClause + EvidenceAvailability + allowed_contexts 程序审计覆盖".
- `fund_agent/fund/audit/contract_rules.py:21-28`: New coverage kind `typed_programmatic_evidence_conditional` is added to the literal type and frozenset.
- `fund_agent/fund/audit/contract_rules.py:35-46`: Docstring updated to remove "非程序化" language; coverage kind now describes evidence-conditional routes, not just unconditional marker-based routes.
- No clause is simultaneously `narrative_guidance` and `typed_programmatic_evidence_conditional`.
- `tests/fund/audit/test_audit_programmatic.py:907-911`: Coverage manifest assertion updated to match `typed_programmatic_evidence_conditional`.

### Focus 8: No provider/runtime/default/live probe

**PASS — no findings.**

- All changes are Fund-layer only (`chapter_auditor.py`, `typed_contracts.py`, `contract_rules.py`) plus tests and README.
- No Service/Host/CLI/provider/runtime changes.
- No `extra_payload` business params.
- No direct document/PDF/cache/source-helper access.
- Imports added to `chapter_auditor.py` (`EvidenceAvailability`, `RequirementAvailability`, `MustNotCoverClause`, `TypedChapterContract`, `get_typed_chapter_contract`) are all from existing Fund-layer modules.

### Focus 9: Tests and README/evidence are sufficient

**PASS — no findings.**

Tests cover:
- `test_ch3_required_label_allowed_under_missing_evidence`: label + gap suffix passes ✓
- `test_ch3_explicit_evidence_gap_statement_allowed`: standalone gap statement passes ✓
- `test_ch3_positive_consistency_claim_blocks_when_actual_behavior_unreviewed`: positive claim with availability → blocked ✓
- `test_ch3_positive_consistency_claim_blocks_without_evidence_availability`: positive claim without availability → blocked (fail-closed) ✓
- `test_ch3_quasi_positive_consistency_claim_blocks_when_style_evidence_missing`: `未见明显不一致，整体变化不大` → blocked ✓
- `test_audit_focus_cannot_disable_programmatic_must_not_cover`: `基本稳定` → blocked regardless of audit_focus ✓
- `test_typed_must_not_cover_issue_id_uses_clause_id`: issue_id uses stable clause id, not phrase hash ✓
- Coverage manifest assertion updated ✓

README updates (`fund_agent/fund/README.md:145`, `tests/README.md:707`) accurately describe the new behavior without overclaiming.

## Adversarial Failure Pass

1. **Label laundering**: `言行一致性判断：言行一致。` — label prefix passes label check, but suffix `言行一致` is a claim phrase → `_is_non_assertive_label_suffix` returns False → `_is_required_label_context` returns False → blocked ✓
2. **Gap reversal**: `证据不足，不能判断，但总体仍倾向一致。` — gap markers and denial present, but `_contains_reversing_positive_claim` finds `但` + `倾向一致` → blocked ✓
3. **Quote laundering**: `原文"言行一致"，因此基金经理言行一致。` — claim phrase in quotes ✓, introducer `原文` ✓, but suffix `，因此基金经理言行一致。` has author conclusion marker `因此` → blocked ✓
4. **Missing availability silent pass**: tested explicitly → blocked ✓
5. **audit_focus bypass**: tested explicitly → blocked ✓
6. **Old path duplicate enforcement**: skipped clause text in global path → no duplicate C2 ✓
7. **Unknown requirement id**: `_availability_requirement_or_unreviewed` returns None → `_typed_must_not_cover_applies` returns True (fail-closed) ✓
8. **Multi-phrase sentence**: `基金经理基本一致，整体风格稳定。` — contains both `基本一致` (quasi-positive) and `风格稳定` (positive), `_first_ch3_style_claim_phrase` catches the first, sentence blocked with appropriate issue_id ✓
9. **Anchor caption contamination**: `> 📎 证据：年报§4 显示风格稳定。` — `_line_is_contract_or_anchor_metadata` filters before claim scanning ✓
10. **Required output marker line**: `<!-- required_output:ch3.required_output.item_03 -->` — filtered by `_line_is_contract_or_anchor_metadata` ✓

## Residual Risks (Non-Blocking)

1. **Test helper duplication**: `_ch3_typed_audit_input()` is defined in both `tests/fund/test_chapter_auditor.py` (line 873) and `tests/fund/audit/test_audit_programmatic.py` (line 1791). The versions differ slightly (test_chapter_auditor version has `include_evidence_availability` parameter; test_audit_programmatic version is simpler). This is test-only duplication and doesn't affect production behavior. Future refactoring could extract a shared fixture module per Slice 0 calibration section 1 suggestion.

2. **Single aggregate requirement**: The predicate now uses `ch3.requirement.actual_behavior_reviewed` as a single aggregate instead of the former two split requirements. While this correctly captures the "any actual behavior evidence unreviewed" trigger, it loses the ability to distinguish *which* specific evidence type is missing in the C2 issue message. The current message says "缺少已复核行为/风格证据" which is sufficient for Ch3-first scope; finer-grained attribution could be added in a future gate if needed.

3. **Quote context is adjacent-line only**: `_quote_has_introducer()` checks only the previous line for quote introducers. A quote introducer two lines before the quoted text would not be recognized. This is intentionally narrow per Slice 0 calibration and is not a defect; it errs on the side of blocking.

## Overall Assessment

**No blocking findings.** All 9 review focuses pass. The implementation correctly:

- Adds Ch3-first typed evidence-conditional `must_not_cover` enforcement as an additive Fund-layer path
- Integrates with existing `EvidenceAvailability` for predicate-based activation
- Fails closed when `EvidenceAvailability` is absent
- Implements Slice 0 narrow allowed contexts (required label, evidence gap statement, quote, anchor caption)
- Blocks positive and quasi-positive consistency/style claims under missing/unavailable/unreviewed evidence
- Eliminates old path duplicate enforcement for the typed clause while preserving other must_not_cover clauses
- Keeps audit_focus semantic-only with no programmatic bypass
- Maintains consistent coverage route in contract_rules
- Includes sufficient tests covering happy path, fail-closed, and adversarial cases
- Documents behavior accurately in README files

All four validation commands pass. No secret/prompt leak detected. The implementation is ready for controller judgment.
