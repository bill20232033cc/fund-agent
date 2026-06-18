# MVP typed template contract Slice 4 Ch3 evidence-conditional must_not_cover controller judgment

## Controller Self-Check

- Role: controller; implementation, fix follow-up and reviews were delegated to tmux workers.
- Gate: `MVP typed template contract Slice 4 Ch3-first evidence-conditional must_not_cover implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Scope boundary: Fund-layer typed programmatic audit for Ch3 evidence-conditional `must_not_cover`, focused tests, README sync and review artifacts only.
- Explicit non-goals preserved: no live provider probe, no provider/default/runtime/budget/endpoint change, no Agent runtime/tool-loop implementation, no Service/Host/CLI change, no score/golden/readiness/promotion change, no deterministic analyze/checklist behavior change, no direct document/PDF/cache/source-helper access, no `extra_payload` business params.

## Accepted Artifacts

- Implementation evidence: `docs/reviews/mvp-typed-template-contract-slice4-ch3-evidence-conditional-must-not-cover-implementation-evidence-20260603.md`.
- DS code review: `docs/reviews/mvp-typed-template-contract-slice4-ch3-evidence-conditional-must-not-cover-code-review-ds-20260603.md`.
- MiMo code review: `docs/reviews/mvp-typed-template-contract-slice4-ch3-evidence-conditional-must-not-cover-code-review-mimo-20260603.md`.
- Controller judgment: this file.

## Accepted Implementation

Slice 4 is accepted.

The implementation adds Ch3-first typed programmatic enforcement for `ch3.must_not_cover.item_04`:

- `chapter_auditor.py` now runs a typed `MustNotCoverClause` path before the legacy phrase-extraction path.
- The typed path is limited to `ch3.must_not_cover.item_04`.
- The typed predicate is driven by `EvidenceAvailability` through `ch3.requirement.actual_behavior_reviewed`, with `missing / unavailable / unreviewed` activating the clause.
- Positive or quasi-positive Ch3 style/consistency claims such as `言行一致`, `风格稳定`, `风格一致`, `基本一致`, `未见明显不一致`, `倾向一致`, `变化不大` and `基本稳定` block with stable issue id `programmatic:C2:ch3.must_not_cover.item_04`.
- Required labels and explicit evidence-gap statements are allowed only in the narrow Slice 0 contexts and only when explicit availability activates the predicate.
- Missing `EvidenceAvailability` does not create silent pass: unsafe positive or quasi-positive Ch3 claims fail closed, and allowed-context exceptions are not applied without explicit availability.
- The old global phrase-extraction path skips the typed Ch3 style clause text to avoid duplicate enforcement and the original false positive path. Other `must_not_cover` clauses keep their existing enforcement.
- `contract_rules.py` classifies the Ch3 style clause as `typed_programmatic_evidence_conditional` instead of narrative-only.

## Controller-Detected Fix

Before review, controller ran an additional fail-closed probe and found that the first worker pass allowed `言行一致性判断：言行一致。` to pass when `ChapterWriterInput.evidence_availability` was absent. This was accepted as a blocking implementation gap and sent back to the same implementation worker.

The fix added:

- fail-closed typed clause enforcement when availability is absent;
- `test_ch3_positive_consistency_claim_blocks_without_evidence_availability`;
- evidence artifact residual text clarifying that safe label/gap exemptions require explicit availability.

Controller reran the same no-availability probe after the fix. Result: `fail` with issue id `programmatic:C2:ch3.must_not_cover.item_04`.

## Validation

Controller reran:

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/fund/audit/test_audit_programmatic.py
```

Result: `86 passed in 0.88s`.

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py
```

Result: `16 passed in 0.76s`.

```bash
uv run ruff check fund_agent/fund tests/fund
```

Result: `All checks passed!`.

```bash
git diff --check -- fund_agent/fund/README.md fund_agent/fund/audit/contract_rules.py fund_agent/fund/chapter_auditor.py fund_agent/fund/template/typed_contracts.py tests/README.md tests/fund/audit/test_audit_programmatic.py tests/fund/test_chapter_auditor.py docs/reviews/mvp-typed-template-contract-slice4-ch3-evidence-conditional-must-not-cover-implementation-evidence-20260603.md
```

Result: exited `0`.

Secret/prompt leak scan over touched implementation, tests, README and evidence files found only existing field names, fake model names, README safety descriptions, recorded scan command text and existing LLM request field names. No API key, Authorization header, raw provider request/response, prompt body, draft body or raw PDF text was found.

## Review Disposition

DS review result: PASS, no blocking findings.

MiMo review result: PASS, no blocking findings.

Non-blocking residuals accepted:

- Test helper duplication for Ch3 typed audit fixtures is acceptable in this slice. A shared fixture can be introduced if future typed audit slices reuse the pattern.
- The predicate uses the aggregate `ch3.requirement.actual_behavior_reviewed`; finer-grained evidence attribution can be added later if needed.
- Quote matching is intentionally narrow and adjacent-line only; this errs fail-closed and matches Slice 0 first-slice scope.
- Current Ch3 availability remains single-year and keeps cross-period style evidence `unreviewed`; multi-year evidence remains future design-only scope.
- Typed manifest loading can be cached later if batch audit performance becomes material.

## Controller Decision

Accepted locally. The implementation satisfies Slice 4 acceptance criteria:

- existing C2 forbidden content tests continue to pass;
- evidence-conditional typed clause is active when availability predicate is missing/unavailable/unreviewed;
- evidence-disabled clause does not run when availability is explicit and predicate is not active;
- required labels and explicit evidence-gap statements are allowed only in narrow contexts;
- positive and quasi-positive Ch3 consistency/style claims block under missing/unreviewed evidence;
- programmatic audit remains authoritative and cannot be disabled by `audit_focus`;
- stable issue ids are tied to `clause_id`;
- old phrase extraction no longer duplicates the typed Ch3 style clause;
- provider/runtime/live probe/Agent runtime/score/golden/readiness non-goals are preserved.

## Next Gate

The next planned typed-template slice is `MVP typed template contract Slice 5 per-chapter audit_focus bounded semantic audit implementation gate`.

Do not enter provider runtime, PASS-only live probe, Agent runtime/tool-loop, score-loop, golden/readiness or template truth replacement from this Slice 4 checkpoint.
