# Controlled Live EID Failure-Branch Evidence Gate Boundary Review - MiMo

## Gate

`controlled live EID failure-branch evidence gate` boundary review

## Reviewer

AgentMiMo (independent review / planning-boundary reviewer)

## Role Constraint

This is not live execution. No network, curl, DNS, sockets, live EID, PDF/FDR acquisition, FundDocumentRepository live acquisition, fallback, provider, LLM, or source-policy changing commands were run. No source/tests/runtime behavior was modified. No stage/commit/push/PR.

## Classification Verdict

**BLOCKED_FOR_PLAN**

Findings require a reviewed controller plan artifact and explicit authorization before live execution.

---

## Review Questions

### Q1: What is the minimum controlled live evidence that can add value beyond accepted no-live evidence without pretending to force real EID failures?

**Finding**: The accepted no-live evidence at checkpoint `ac6bbe9` already proves all five failure categories (`not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`) through `httpx.MockTransport`, `_FakeAnnualReportSource` and `_write_pdf_bytes_atomic`. The accepted live EID/FDR acquisition proof for all five small-golden rows `004393`/`004194`/`006597`/`110020`/`017641`/`2024` proves the happy path (success) against the real EID endpoint.

**Reviewer opinion**: The only live evidence that adds value beyond no-live proof is proving that the real EID endpoint **naturally** exhibits a failure mode during the controlled observation window. This is fundamentally different from no-live evidence: no-live proves "the code handles failures correctly when they occur"; live failure evidence proves "the real endpoint actually produces failures that the code handles." The minimum valuable live evidence would be:

- **One natural `unavailable` observation**: EID endpoint transient timeout or 5xx during the controlled window, proving the real failure path classification propagates correctly end-to-end. This is the most likely natural failure to observe.
- **Not valuable**: Re-running the successful acquisition command (already proven). Forcing artificial failures against the real endpoint (does not prove natural behavior).

**Classification**: Reviewer opinion

---

### Q2: Which failure branches are realistically observable live vs only residual unless EID naturally fails?

| Failure category | Live observable? | Basis |
|---|---|---|
| `not_found` | Only if requesting a fund/year combination that EID legitimately does not have | Low probability for the five small-golden rows that already have accepted 2024 proof; would need a different fund/year request |
| `unavailable` | Most likely natural failure: transient EID service outage, network timeout, DNS failure | Moderate probability; depends on EID infrastructure reliability during observation window |
| `schema_drift` | Extremely unlikely: requires EID to change their API response format during observation | Essentially zero probability in a short observation window |
| `identity_mismatch` | Extremely unlikely: requires EID to return a candidate that contradicts the request | Essentially zero probability for known-good fund codes |
| `integrity_error` | Extremely unlikely: requires EID to return a non-PDF response or corrupted bytes | Essentially zero probability unless EID infrastructure is broken |

**Classification**: Repo fact (from code structure) + reviewer opinion (probability assessment)

---

### Q3: What must be forbidden to prevent reintroducing Eastmoney/CNINFO/fund-company fallback or weekly live CI?

**Repo fact / truth-doc fact**: Current control truth (`docs/implementation-control.md`, `docs/current-startup-packet.md`) explicitly states:
- `selected_source=eid`, `mode=single_source_only`, `fallback_enabled=false`
- Eastmoney, CNINFO, fund-company website/CDN are deferred source candidates only
- `_FALLBACK_ELIGIBLE_CATEGORIES` names `not_found` and `unavailable` but current single-source mode terminates after EID failure

**Reviewer opinion**: The following must be explicitly forbidden in the live gate plan:

1. **No fallback source activation**: Do not construct `EastmoneyAnnualReportSource`, `CninfoAnnualReportSource`, or any non-EID source. The live gate must only observe EID source behavior.
2. **No source-policy change**: Do not modify `sources.py` orchestrator, `selected_source`, `source_mode`, or `fallback_enabled`.
3. **No weekly live CI**: Do not create recurring live EID checks, scheduled tasks, or CI jobs that hit the real EID endpoint.
4. **No new fund/year live requests**: Only use the five small-golden rows with fund/year combinations that already have accepted live acquisition proof (or a very small explicitly authorized extension). Do not open a "try many funds" live sweep.
5. **No fallback-eligibility restoration**: Do not change `_FALLBACK_ELIGIBLE_CATEGORIES` behavior or `AnnualReportSourceFallbackBlockedError` semantics.

**Classification**: Repo fact (current code) + reviewer opinion (forbidden list)

---

### Q4: What exact stop conditions should block live execution?

**Reviewer opinion** (based on accepted planning gate stop conditions):

1. **Stop if live EID succeeds for all requested rows**: No failure branch to observe; the gate produces no new evidence beyond what is already accepted. Log the success as evidence that the happy path still works, then stop.
2. **Stop if fallback would be triggered**: Current code should not trigger fallback in single-source mode, but if a test or observation reveals fallback activation, stop immediately — this contradicts accepted single-source policy.
3. **Stop if source-policy metadata changes**: If the live observation produces metadata where `selected_source != eid`, `source_mode != single_source_only`, or `fallback_enabled != false`, stop.
4. **Stop if the live observation would require reading production PDFs beyond the acquisition boundary**: The gate should only observe the source acquisition + failure classification path, not parse PDF content.
5. **Stop if the observation window expires without natural failure**: Do not extend the window indefinitely waiting for an outage. A bounded observation (e.g., one controlled run) that succeeds is valid evidence of "no natural failure during this window."

**Classification**: Reviewer opinion

---

### Q5: Should this gate proceed directly to live execution, or first require a controller plan artifact and review?

**Reviewer opinion**: **Must first require a controller plan artifact and review.** Reasons:

1. The gate is classified as `heavy` per control truth: it involves source policy, `FundDocumentRepository`/PDF/network/source access, and fallback semantics.
2. The no-live evidence gate was `standard` because it only used MockTransport/fake sources. A live gate touches real infrastructure and has blast radius implications.
3. The existing no-live evidence already proves code correctness for all five categories. A live gate adds marginal value (proving natural endpoint behavior) but carries non-zero risk (accidental fallback activation, source-policy drift, unintended CI entrenchment).
4. The controller plan must explicitly define: exact live command(s), exact fund/year combinations, bounded observation window, stop conditions, evidence artifact shape, and residual classification.

**Classification**: Reviewer opinion

---

## Summary

| Question | Classification | Verdict |
|---|---|---|
| Q1: Minimum valuable live evidence | Reviewer opinion | Only natural `unavailable` adds value; re-running success adds nothing |
| Q2: Realistic live observability | Repo fact + reviewer opinion | `unavailable` is the only realistic live observation; others are near-zero probability |
| Q3: Forbidden actions | Repo fact + reviewer opinion | No fallback, no source-policy change, no weekly CI, no live sweep, no eligibility restoration |
| Q4: Stop conditions | Reviewer opinion | Success = stop, fallback = stop, policy drift = stop, window expired = stop |
| Q5: Plan-first requirement | Reviewer opinion | Heavy gate requires reviewed controller plan before live execution |

## Recommendation

**BLOCKED_FOR_PLAN**: This gate should not proceed to live execution without a reviewed controller plan artifact. The plan should define the exact live observation scope (likely a single re-run of one small-golden row against the real EID endpoint, bounded to one attempt, with explicit stop conditions). Given that the no-live evidence already covers all five failure categories and the live happy path is already proven, the marginal value of a controlled live failure-branch observation is low unless the user has a specific live failure scenario they want to verify.

The most defensible live gate plan would be:
- Exactly one `006597 / 2024 --use-llm` run (or simpler: one EID acquisition-only observation)
- Bounded to one attempt
- If EID succeeds: log success, stop, accept as "no natural failure observed"
- If EID fails with `unavailable`: log the failure classification, verify it propagates correctly, accept as live `unavailable` proof
- If EID fails with any other category: log and stop for manual review
- No fallback activation, no source-policy change, no recurring CI

## Next Entry

Controller should write or commission a reviewed `controlled live EID failure-branch evidence gate plan` artifact. After plan review and controller judgment, the gate may proceed to bounded live execution if explicitly authorized.
