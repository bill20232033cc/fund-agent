# MVP typed template contract implementation planning plan — DS review

## Worker Self-Check

- Role: independent plan reviewer (DS), not controller, not implementation worker.
- Gate: `MVP typed template contract implementation planning gate`.
- Classification: `heavy`.
- Review target: `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`, `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md`, `docs/reviews/mvp-fund-report-template-typed-contract-redesign-controller-judgment-20260602.md`.
- Output: this review artifact only.
- Actions intentionally not taken: no source code edit, no test edit, no control/design/template/startup doc edit, no commit, no push, no PR, no live provider run.
- Truth status: this is a review opinion for controller consumption. It does not authorize implementation or change accepted design truth.

## Review Summary

The plan correctly maps all seven accepted future design decisions into eight implementation slices with clear acceptance criteria, named tests, validation commands, and a verifier matrix. No criterion-level violation was found. Two non-blocking findings are recorded below; neither justifies rejecting the plan.

**Final verdict: PASS.**

## Criterion-by-Criterion Review

### C1: Public chapter ids 0–7 preserved; Ch2 internal subcontracts non-public

**Finding: PASS, no findings.**

Plan evidence:
- Slice 1 explicitly constrains the typed manifest to "exact chapter ids 0-7, no duplicates, no unknown dependency ids, Ch2 subcontracts cannot have public chapter ids" (line 122).
- Slice 1 tests include `test_typed_manifest_rejects_ch2_public_subchapter_ids` (line 136).
- Migration plan: "Keep Ch2 performance/attribution/cost as internal typed subcontracts under public chapter id 2" (line 386).
- Risk matrix explicitly flags "Ch2 internal subcontracts leak into public chapter ids or artifacts as new chapters" as High/Medium with concrete mitigation (line 399).
- Verifier matrix: "artifacts and matrices still show Ch2 only" (line 437).

The plan keeps public chapter count at 8 (ids 0–7), treats Ch2 subcontracts (`performance`, `attribution`, `cost`) as internal typed organization only, and includes validation tests that reject top-level Ch2 subchapter ids. No `0+9` or `0+10` structure is accepted.

### C2: Deterministic analyze/checklist defaults and --use-llm fail-closed semantics unchanged

**Finding: PASS, no findings.**

Plan evidence:
- Non-goals list "Do not change deterministic analyze/checklist defaults" (line 417).
- Slice 7 acceptance criteria: "fund-analysis analyze default does not read LLM config or typed LLM provider config" and "fund-analysis checklist remains deterministic" (lines 337–338).
- Slice 7 tests: `test_default_analyze_unchanged_with_typed_contract_modules_present` (line 348).
- Migration plan: "Preserve deterministic fund-analysis analyze/checklist output behavior" (line 387) and "Preserve --use-llm fail-closed semantics: incomplete result means exit code 1, empty stdout, no deterministic fallback" (line 388).
- Risk matrix: "Incomplete LLM result falls back to deterministic" rated High/Low with mitigation through existing fail-closed tests (line 406).

Every slice that touches behavior includes an explicit acceptance criterion that current deterministic defaults are unchanged. The incomplete-LLM path keeps exit 1 + empty stdout + no fallback.

### C3: EvidenceAvailability derived from same-source ChapterFactProjection, not document/PDF/provider reads

**Finding: PASS, no findings.**

Plan evidence:
- Slice 2: "Derive availability only from ChapterFactProjection / ChapterFactInput facts, anchors, missing reasons, ReportDataGap-like structures already present, and typed contract requirement ids" (line 157).
- Slice 2 acceptance criteria: "Availability derivation is pure and same-source: no repository, PDF/cache/source helper, Service, Host, provider, retained report, or filesystem reads" (line 166).
- Slice 2 tests: `test_derivation_does_not_call_document_repository` (line 178).
- Target architecture: Fund owns EvidenceAvailability but "Fund tools must not read Service/Host, provider config, CLI flags, raw filesystem documents, PDF cache, source helpers, or dayu runtime" (line 47).
- Verifier matrix: "Unit tests with fake ChapterFactProjection; monkeypatch/fake proving no FundDocumentRepository, PDF/cache/source helper, Service, Host, or provider call" (line 432).

The derivation boundary is clearly stated as same-source/pure, with explicit prohibitions on document/PDF/provider/filesystem reads, and a specific test that asserts no repository call.

### C4: Auditor fail-closed/programmatic-first; audit_focus does not disable blockers

**Finding: PASS, no findings.**

Plan evidence:
- Slice 4: "Keep current programmatic blockers always-on; audit_focus does not disable C2, L1, marker, anchor, item-rule, forbidden advice, or missing/degrade checks" (line 233).
- Slice 4 tests: `test_audit_focus_cannot_disable_programmatic_must_not_cover` (line 249).
- Slice 5: "Programmatic audit produces identical blockers with full, reduced, or unrelated audit_focus" (line 272).
- Slice 5 tests: `test_programmatic_blocker_fires_even_when_focus_omits_must_not_cover_boundary` (line 280).
- Design requirement table: "audit_focus as bounded semantic audit emphasis only; never disables programmatic blockers" (line 41).
- Risk matrix: "audit_focus accidentally disables programmatic blockers" rated High/Medium with "Programmatic audit independent of focus; tests run blockers with reduced focus" (line 400).

The plan enforces programmatic-first at multiple layers: Slice 4 keeps current blockers always-on, Slice 5 adds tests proving focus doesn't suppress blockers, and the risk matrix tracks this as a high-impact risk with explicit mitigation.

### C5: No provider-runtime, PASS-only live probe, Agent runtime, multi-year runtime, score-loop, golden/readiness, or template truth replacement

**Finding: PASS, no findings.**

Plan evidence:
- Explicit out-of-scope block lists all prohibited items (lines 68–78).
- Non-goals section reinforces each prohibition (lines 411–422).
- Migration plan: "Do not migrate execution mechanics into Agent in this typed-template implementation family" (line 389).
- Migration plan: "Do not replace docs/fund-analysis-template-draft.md or current contracts.py as the source used by deterministic rendering until a later controller gate accepts that migration" (line 383).
- Risk matrix row: "Provider-runtime timeout work is mixed into typed contract implementation" rated Medium/Medium with mitigation through non-goals and review checklist (line 407).
- Risk matrix row: "Typed contract becomes a second template truth competing with docs/fund-analysis-template-draft.md" rated High/Medium with mitigation (line 398).

Every prohibited scope item is explicitly listed as a non-goal. The plan treats typed contracts as additive sidecar modules, not template truth replacement. Agent runtime, multi-year runtime, provider budget/default changes, score-loop, and golden/readiness are all explicitly excluded.

### C6: Slices are code-generation-ready with clear files, acceptance criteria, tests, and verifier matrix

**Finding: PASS, one non-blocking observation (see N1 below).**

Plan evidence:
- 8 slices, each with: Purpose, Implementation work, Acceptance criteria, Tests (named), Validation commands (exact bash).
- Candidate files table (lines 57–66) maps each area to likely changed/added files.
- Verifier matrix (lines 425–443) maps all 14 accepted design requirements to direct expected evidence.
- Reviewer checklist (lines 446–464) with 15 yes/no questions.
- Risk matrix (lines 395–409) with 12 risks rated for impact/likelihood with named mitigation and owner.
- Suggested gate sequence (lines 465–476) in dependency order.

Each slice includes enough specificity (exact test names, exact validation commands) that an implementation worker can proceed without inventing architecture. The dependency chain (Slice 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8) is logical and respects prerequisites.

## Findings

### Blocking Findings

None.

### Non-Blocking Findings

#### N1: Slice 0 output artifact type is ambiguous

Slice 0 is described as producing "a planning/evidence artifact, not runtime code" (line 91). It defines "allowed-context fixture categories," "item-level block criteria," and Chinese polarity/quasi-positive fixture cases. However, the plan does not specify whether this artifact is:

- (a) A standalone markdown document that subsequent slice implementers must manually interpret, or
- (b) A code-level fixture module (e.g., `tests/fund/fixtures/polarity_fixtures.py`) that Slice 4 can import and test against.

If the answer is (a), Slice 4's implementer must re-interpret the calibration document into code, introducing a translation risk between the accepted calibration and the implementation. If (b), the plan should state the expected module path and import relationship.

**Recommendation:** Clarify in Slice 0 whether the output includes a shared fixture/test-data module consumable by Slice 4, or accept that Slice 4's implementer will produce the programmatic encoding of the calibration as part of Slice 4 implementation (with Slice 0 serving as the accepted reference document).

**Severity:** Non-blocking. The gate-based sequential acceptance model (controller must accept Slice 0 before Slice 4 starts) provides a control point. The controller can reject Slice 0 if it is insufficiently concrete for downstream consumption.

#### N2: Ch3 root-cause ambiguity is carried forward but not resolved by the plan

Both the accepted design (Decision 3) and the controller judgment state that Ch3's retained failure mode (`programmatic:C2` / `code_bug_other` at `言行一致`) requires root-cause determination: is it a C2 rule problem, a writer boundary problem, or a typed contract clause mapping problem? The plan's Slice 4 implements evidence-conditional `must_not_cover` as if the root cause is contract-shape (missing evidence predicates). But the startup packet (line 139) explicitly says "Ch3-only calibration must first decide whether the C2 rule, writer boundary, or typed contract clause mapping is root cause."

Slice 4 could be built on a wrong root-cause assumption. If the true root cause is a C2 rule implementation bug (`code_bug_other`) rather than a contract-shape gap, evidence-conditional wrapping may not fix the failure — it could mask it.

**Recommendation:** Add an explicit gate precondition: before Slice 4 implementation, run a Ch3-only diagnostic that isolates the C2 rule behavior from the contract-shape behavior (e.g., a targeted test showing whether the current C2 checker blocks `言行一致` when evidence is explicitly marked as missing in a typed predicate). If the diagnostic shows the C2 rule itself is buggy, a separate C2 fix gate should precede Slice 4.

**Severity:** Non-blocking at plan-review stage, but becomes blocking before Slice 4 implementation. The plan correctly sequences Slice 0 (calibration) before Slice 4 (implementation), which provides a natural check point. Controller should verify this during Slice 0 acceptance.

## Residuals

| Residual | Why not blocking | Recommended owner |
|---|---|---|
| Slice 0 artifact ambiguity (N1) | Controller gate between Slice 0 and Slice 4 prevents implementation on ambiguous input | Controller during Slice 0 acceptance |
| Ch3 root-cause assumption (N2) | Slice 0 calibration + Slice 4 implementation gating provides a check point; C2 rule itself is not changed by this plan | Controller during Slice 0/Slice 4 transition |
| No integration test plan across slices | Each slice has unit-level tests; cross-slice integration (typed contract + availability + must_not_cover + writer prompt) is tested only indirectly through Slice 7 facade wiring. The verifier matrix partially covers this through its "direct evidence" column | Future Slice 7 implementation gate |
| Typed contract ↔ current `_CHAPTERS` adapter failure modes | Migration plan says adapter "must fail closed if a current natural-language item has no typed id" (line 384) but doesn't specify the failure surface (construction-time? import-time? first-use?). This is acceptable for a plan — implementation gate should specify | Future Slice 1 implementation gate |

## Verdict

**PASS.** The plan preserves all required invariants (chapter ids 0–7, Ch2 internal subcontracts only, deterministic defaults, --use-llm fail-closed, EvidenceAvailability same-source derivation, programmatic-first audit, audit_focus non-disabling). It avoids all prohibited scope (provider-runtime, PASS-only probe, Agent runtime, multi-year runtime, score-loop, golden/readiness, template truth replacement). Each slice is code-generation-ready with specific files, named tests, acceptance criteria, and validation commands. The two non-blocking findings (N1, N2) are addressable at the Slice 0/4 transition without plan restructuring.

## Validation

```bash
git diff --check -- docs/reviews/mvp-typed-template-contract-implementation-planning-plan-review-ds-20260603.md
```

Secret-safety statement: this review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, or hidden provider config value.
