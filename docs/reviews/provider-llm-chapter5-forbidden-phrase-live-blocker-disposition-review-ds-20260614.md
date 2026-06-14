# Provider/LLM Chapter 5 Forbidden-phrase Live-blocker Disposition — DS Review

Date: 2026-06-14

Role: AgentDS disposition reviewer

Gate: `Provider/LLM Chapter 5 Forbidden-phrase Live-blocker Disposition Gate`

Target: `docs/reviews/provider-llm-chapter5-forbidden-phrase-live-blocker-disposition-20260614.md`

Verdict: `PASS`

## Findings

### F1: attempt-level issue extraction path mismatch (non-blocking)

The target cites issue id `5:llm_contract_violation:writer:forbidden_phrase:7` from chapter-05.json safe metadata. My independent `jq` extraction at `.attempts[0].issues[]` and `.attempts[1].issues[]` returned empty arrays. The issue likely lives at a different JSON path (e.g., top-level `.issues` or `.runtime_diagnostics`) rather than nested under `attempts[].issues[]`.

This does not affect the root-cause classification, which is anchored on top-level `summary.json` and `chapter-05.json` fields — all of which agree with the target. The issue id is illustrative, not load-bearing for the disposition.

### F2: source-level symbol search described but not in reviewer allowed-command list (procedural note)

The target's evidence review table includes "Static symbol search over `fund_agent` and `tests` for `forbidden_phrase` / forbidden wording routes" classified as "Candidate no-live evidence map only." The target is transparent about this and uses it only as a candidate map — the classification itself is based on safe runtime metadata, not on source content. No remediation needed.

### F3: redaction_policy null in summary.json (non-blocking)

The target references redaction policy from `manifest.json`. My `jq` extraction found `redaction_policy: null` in `summary.json`. The controller judgment at `4fb5284` separately confirmed `policy_id=llm_incomplete_artifact_redaction.v1` from `manifest.json`. The target does not claim to have read `manifest.json`, and the redaction policy fact is not material to the root-cause classification. No impact.

## Review Questions

### 1. Is the root-cause classification supported by accepted live evidence and safe metadata?

**Yes.** The classification `LLM_OUTPUT_POLICY_NONCOMPLIANCE_AFTER_REPAIR_ATTEMPT` is supported by:

- `summary.json` first_failed: `chapter_id=5`, `category=audit_parse`, `subcategory=forbidden_phrase`, `runtime_operation=auditor`, `provider_attempt_count=0`, `stop_reason=llm_contract_violation`
- `chapter-05.json`: `status=blocked`, `attempts_count=2`
- Attempt-level metadata in the target (Section 3): attempt 0 writer drafted but auditor blocked with `audit_parse` / `forbidden_phrase`; attempt 1 writer itself blocked with `writer:forbidden_phrase` before reaching audit
- Accepted controller judgment at `4fb5284`: confirms Chapter 6 accepted, Chapter 5 is current first failed blocker

The evidence chain is direct and same-source: the exact runtime artifact that produced the Chapter 5 blocker is the sole evidence basis. No indirect or cross-artifact inference is used.

### 2. Is direct implementation correctly rejected for this gate?

**Yes.** Five hypotheses (H1–H5) are open, spanning prompt contract, LLM behavior, repair context, taxonomy alignment, and repair-budget intent. None is resolved. Direct implementation without knowing which hypothesis is correct would be premature and could target the wrong layer. The rejection follows the established Chapter 6 invalid-marker and Chapter 2 L1 precedents: disposition → diagnostic evidence → fix plan → fix implementation → bounded live re-evidence.

### 3. Is the recommended next gate `Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence Gate` appropriate?

**Yes.** The recommended next gate:

- Follows the established gateflow pattern (disposition → no-live diagnostic evidence)
- Correctly scopes to no-live evidence only, not implementation
- Lists appropriate allowed source paths for reading (writer, auditor, repair, runner, orchestrator, targeted tests)
- Explicitly forbids live/provider/LLM/network commands, source/test/runtime changes, source policy/provider default/repair budget/annual-period route/fallback changes
- Preserves `NOT_READY`

The five hypotheses (H1–H5) provide a complete decomposition for the diagnostic evidence gate to resolve.

### 4. Does the artifact avoid live/provider/readiness/source-policy/fallback/PR overclaim?

**Yes.** Verified across all sections:

| Section | Check |
|---|---|
| §1 Scope | Explicitly disclaims implementation, live command, provider/source policy change, repair budget change, readiness, PR/release state |
| §6 Rejected/Deferred | Rejects direct implementation, additional live command, provider readiness, source acquisition/fallback change, readiness/release/PR claim |
| §7 Next gate | Forbids live/provider/LLM/network/PDF/FDR/source/acquisition commands; forbids source/test/runtime change in diagnostic gate; forbids source policy/provider default/repair budget/annual-period route/fallback change |
| §8 Residuals | Preserves `NOT_READY`; provider response classification remains unproven |
| §9 Verdict | `NOT_READY` in verdict string |

No section claims or implies ready-state, release-state, PR-state, source-policy change, fallback enablement, provider classification, or live stability.

### 5. Are residuals and hypotheses complete enough for the next evidence gate?

**Yes.** The five hypotheses cover the diagnostic space:

- H1 (prompt contract omission) → tests whether Chapter 5 prompt explicitly forbids the phrase
- H2 (LLM violation, writer correctly blocks) → tests writer validation behavior
- H3 (repair context missing specificity) → tests what `ChapterRepairContext` carries after audit forbidden phrase
- H4 (taxonomy mismatch) → tests whether auditor and writer classify the same wording through different paths
- H5 (budget intent) → tests whether 1-repair budget producing terminal fail-closed is accepted product behavior

Residuals are properly noted: Chapter 2 L1 non-terminal metadata as monitoring residual, provider response classification unproven, `NOT_READY` preserved.

## Cross-check Summary

| Item | Controller claim | DS independent verification | Match? |
|---|---|---|---|
| first_failed chapter_id=5 | ✓ | jq confirmed: chapter_id=5 | ✓ |
| first_failed category=audit_parse | ✓ | jq confirmed: audit_parse | ✓ |
| first_failed subcategory=forbidden_phrase | ✓ | jq confirmed: forbidden_phrase | ✓ |
| provider_attempt_count=0 | ✓ | jq confirmed: 0 | ✓ |
| chapter-05 status=blocked | ✓ | jq confirmed: blocked | ✓ |
| chapter-05 attempts_count=2 | ✓ | jq confirmed: 2 | ✓ |
| chapter-06 status=accepted | ✓ | jq confirmed: accepted, attempts_count=1 | ✓ |
| git diff --check passed | ✓ | git diff --check: no output | ✓ |
| No live/provider overclaim | ✓ | Verified across all sections | ✓ |
| NOT_READY preserved | ✓ | Verified across all sections | ✓ |

## Final Verdict

`PASS`

The root-cause classification `LLM_OUTPUT_POLICY_NONCOMPLIANCE_AFTER_REPAIR_ATTEMPT` is supported by direct same-source safe metadata from the accepted runtime artifact. Direct implementation is correctly rejected. The recommended next gate `Provider/LLM Chapter 5 Forbidden-phrase No-live Diagnostic Evidence Gate` follows the established gateflow pattern. No live/provider/readiness/source-policy/fallback/PR overclaim detected. Residuals and hypotheses are complete enough for the next evidence gate. F1–F3 are non-blocking procedural notes.
