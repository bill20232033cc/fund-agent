# Post-P16 Follow-up Plan Review Controller Judgment（2026-05-22）

## Verdict

`ACCEPT_POST_P16_PLANNING_AND_PROCEED_TO_P17-S1_PLAN_REVIEW`

Controller accepts `docs/reviews/post-p16-follow-up-planning-20260522.md` as the post-P16 next-phase selection artifact. The next gate is:

```text
P17-S1 tracking_error extractor ambiguity boundary and note consistency plan/review
```

This is the best next step from first principles because P15/P16 already established that production `tracking_error` golden rows remain blocked without direct observed disclosure evidence. The remaining near-term quality risk is not a lack of external data or a golden expansion opportunity; it is whether the Fund Capability extractor fails closed consistently and explains ambiguous / conflicting / incomplete `tracking_error` mentions with precise, auditable notes.

## Inputs

| Artifact | Result |
|---|---|
| `docs/reviews/post-p16-follow-up-planning-20260522.md` | Recommends P17-S1 extractor ambiguity boundary hardening |
| `docs/reviews/post-p16-follow-up-plan-review-mimo-20260522.md` | `PASS_WITH_FINDINGS` |
| `docs/reviews/post-p16-follow-up-plan-review-glm-20260522.md` | `PASS_WITH_FINDINGS` |
| `docs/design.md` | Design truth for boundaries and non-goals |
| `docs/implementation-control.md` | Control truth for current gate, residuals, and phase history |

Excluded local drafts remain out of scope and were not used as controller evidence: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Review Synthesis

Both reviewers independently confirm the planning premise:

- Fund Capability has a separable `tracking_error` extraction / classification boundary in `fund_agent/fund/extractors/performance.py`.
- Current behavior contains a broad early-return risk around ambiguous target / actual mentions.
- `"tracking_error_ambiguous"` is reused for distinct failure modes.
- The recommended P17-S1 scope stays inside Fund Capability and does not smuggle in production golden rows, external index data, calculated tracking error, Dayu runtime, LLM audit, Evidence Confirm, or Service/UI/Engine source access.

No reviewer raised a blocking issue. The findings are accepted as entry constraints for P17-S1 plan/review, not as reasons to redo post-P16 selection.

## Finding Decisions

| Finding | Decision | Controller rationale |
|---|---|---|
| F1 note semantic reuse: line-level ambiguity and table/text inconsistency share `"tracking_error_ambiguous"` | Accepted as P17-S1 plan constraint | Precise blocker semantics directly serve the design goal of traceable, deterministic evidence handling. P17-S1 plan must require separate notes or an explicitly equivalent typed reason for these two failure modes. |
| F2 multi-match suppression returns `None` without explicit blocker semantics | Accepted as P17-S1 plan constraint | Silent fail-closed behavior is safer than false acceptance, but it is not sufficiently auditable. P17-S1 plan must either make multi-match suppression explicit or document why it remains a residual with an owner. |
| F3 text extraction has an internal early-return in addition to top-level ambiguous precheck | Accepted as P17-S1 implementation constraint | The root risk is broad suppression of later valid direct-looking disclosure. P17-S1 plan must require checking both early-return locations, not only the top-level precheck. |
| F4 `source_type` / `calculation_method` are success-path fields and unavailable when value is missing | Accepted as wording clarification | P17-S1 plan should phrase missing-path consistency in terms of `note` / `extraction_mode`; success-path `source_type` and `calculation_method` must remain explicit and stable. |
| Need fixture snippets for each blocker type | Accepted as plan-review expectation | P17-S1 plan must list deterministic test cases for target/limit, narrative, benchmark-only, standard-deviation-only, ambiguous, incomplete-anchor, multi-match, table/text inconsistency, and valid direct-looking non-regression. |

## Accepted P17-S1 Entry Constraints

The next planning artifact must:

1. Inspect current code facts before proposing edits.
2. Keep annual-report access through `FundDocumentRepository` / `FundDataExtractor`.
3. Stay within Fund Capability extractor and focused tests unless documentation triggers require README updates.
4. Explicitly classify or record residual ownership for:
   - target / limit / control text;
   - manager narrative;
   - benchmark-only text;
   - standard-deviation-only text;
   - ambiguous or unparseable values;
   - incomplete anchors;
   - table/text inconsistent values;
   - multi-match suppression;
   - valid direct-looking disclosure after an earlier ambiguous line.
5. Require tests that prove broad early-return no longer suppresses later valid direct-looking disclosure in the same bounded input.
6. Avoid all production golden edits and preserve the P15/P16 no-direct-disclosure blocker for `001548`, `004194`, `005313`, `017644`, `019918`, and `019923`.
7. Avoid calculated tracking error, external index adapters, methodology / constituents extraction, QDII subtype redesign, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, tool loop, source CSV mutation, and `extra_payload` for explicit parameters.

## Control Update

`docs/implementation-control.md` is updated to:

- mark post-P16 follow-up planning as accepted;
- set the current gate to `P17-S1 tracking_error extractor ambiguity boundary plan-review`;
- record the planning and review artifacts;
- assign reviewer findings to P17-S1 plan constraints.

## Next Handoff

Create `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md` as a specialist planning artifact. Do not edit source code, tests, golden files, README, design/control truth, selected CSV, RR-13 data, or external GitHub state during this plan gate.
