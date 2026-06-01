# QDII Replacement Candidate Evidence Plan — Review (AgentDS)

> Date: 2026-05-27
> Reviewer: AgentDS (independent plan reviewer, not controller, not evidence runner)
> Gate: `QDII replacement candidate evidence plan gate`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-plan-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Control doc current gate | `QDII replacement candidate enumeration plan accepted locally` |
| Control doc next entry point | `QDII replacement candidate evidence plan gate; must use init-agents / tmux multi-agent flow` |
| Plan's stated gate | `QDII replacement candidate evidence plan gate` |
| Latest accepted checkpoint | `461ff08 docs: accept qdii replacement enumeration plan` |

The plan correctly replays the Startup Packet from `docs/implementation-control.md` line 29. The stated gate matches the next entry point. No gate switch is attempted. **PASS**.

## Review Findings

### F1 (Low) — `golden_set.json` listed as expected output without `--golden-answer-path`

- **Evidence**: Plan §4 lines 102–106. The plan lists `golden_set.json` as an expected generated path from `extraction-score`, but the planned command does not pass `--golden-answer-path`. Actual CLI help states: `golden_answer_path: strict golden answer JSON 路径；为空时只输出 FQ0 skeleton`.
- **Severity**: Low. Does not block plan acceptance. The evidence runner's preflight will confirm actual output paths. If `golden_set.json` is not generated without `--golden-answer-path`, the evidence runner can remove it from the tracked summary.
- **Recommendation**: Either add a note that `golden_set.json` may not be generated without `--golden-answer-path`, or verify during preflight whether the FQ0 skeleton is written to `golden_set.json` or a different path. No plan patch required for acceptance; controller can accept as informational.

### F2 (Informational) — `quality-gate --score-path` default is a stale hardcoded path

- **Evidence**: Actual CLI help output shows `--score-path` default = `reports/extraction-snapshots/p4-s3b-004393-contro…` (truncated, appears to be a previous run's path). Plan §4 line 109 correctly passes `--score-path` explicitly, avoiding the stale default.
- **Severity**: Informational. The plan's explicit `--score-path` usage is correct and avoids this pitfall. Worth noting in controller judgment as a residual: future evidence runs that omit `--score-path` may silently write to a stale default directory.
- **Recommendation**: Controller may record this as a residual risk. No plan change needed.

### F3 (Informational) — Preflight criteria for `extraction-score` omits `--golden-answer-path`

- **Evidence**: Plan §3 line 59 lists preflight acceptance criteria for `extraction-score` as `--snapshot-path`, `--source-csv`, `--output-dir`, `--errors-path`. The `--golden-answer-path` flag exists in the actual CLI but is not mentioned.
- **Severity**: Informational. The plan does not intend to use golden answer comparison, so omitting it from preflight criteria is consistent. The preflight help command will still reveal the flag; the evidence runner can note its presence without using it.
- **Recommendation**: None required. Not a gap.

## Accepted Strengths

1. **Startup Packet fidelity**. Plan §1 exactly replays the control doc's next entry point. No gate switch, no scope creep.

2. **Candidate discipline**. Plan §2 treats `096001` / 2024 as the single candidate, correctly preserving `provenance_unknown`, `quality_unknown`, and `promotion_disposition=not_promoted`. This matches the controller judgment constraint: "accepted only as the single candidate for the next future evidence plan gate."

3. **Provenance-before-quality ordering**. Plan §5 explicitly requires source provenance interpretation before any quality, promotion, or replacement language. Fail-closed categories (`schema_drift`, `identity_mismatch`, `integrity_error`) are correctly listed with stop semantics. The ineligible-provenance conditions are enumerated precisely (missing `primary_failure_category`, incomplete tuple, unknown fallback eligibility, command-success-without-public-provenance).

4. **`manager_strategy_text` P0 handling**. Plan §6 correctly distinguishes three cases: P0-blocking → `quality_blocked_after_provenance`, genuine disclosure gap → `disclosure_data_gap_not_baseline_ready`, and provenance-ineligible-first → classify by provenance. It does not infer extractor/policy fixes from indirect evidence. No quality interpretation is allowed before eligible provenance.

5. **Terminal state table**. Plan §7 exhaustively enumerates 10 terminal conditions. Every single one has `promotion_disposition=not_promoted`. No durable baseline, golden, source-safe, or promoted state is claimed for any outcome.

6. **Fallback/exclusion preservation**. Plan §8 preserves the accepted fallback order (`040046` → `019172` → remaining equity QDII), the `017641` exclusion, QDII-FOF exclusion, `013308` naming/category conflict, and bond QDII asset-class constraint. All are contingency-only; no fallback execution is authorized.

7. **Boundary compliance**. Plan §11 explicitly prohibits all disallowed actions: no evidence commands, no PDF/cache/source-helper access, no code/test/docs changes, no GitHub mutation. The stop conditions directly mirror the enumeration plan and controller judgment non-goals.

8. **Public CLI only**. All planned commands use the public `fund-analysis` CLI surface (`extraction-snapshot`, `extraction-score`, `quality-gate`). No internal module, source helper, or PDF/cache access is planned.

9. **Preflight stop behavior**. Plan §3 requires the evidence runner to verify CLI flags via `--help` before execution and stop on mismatch with `terminal_classification=cli_flag_mismatch_not_run`. Actual CLI help output confirms all planned flags exist with the expected names and semantics.

10. **Review matrix**. Plan §10 correctly specifies the two-reviewer + controller-judgment + control-doc-update flow using `init-agents` / tmux. The review focus checklist aligns with the controller judgment's required next-gate constraints.

## Required Fixes Before Acceptance

None. All findings are informational or low-severity and do not block plan acceptance for its stated purpose: authorizing a future `096001` evidence plan (not evidence run).

## Residual Risks for Controller Judgment

| Residual | Severity | Notes |
|---|---|---|
| `golden_set.json` may not be generated without `--golden-answer-path` | Low | Evidence runner preflight will confirm. Controller can note in judgment. |
| `quality-gate --score-path` stale default | Low | Plan explicitly passes `--score-path`; only a risk if future runner omits it. |
| `096001` actual CLI behavior with 2024 annual report is unknown | Inherent | This is expected — the whole point of the evidence gate. Not a plan defect. |

## Gate-Specific Yes/No Answers

- **Does this plan follow the current Startup Packet next entry point?** **Yes.** It replays the control doc line 29 exactly.
- **Is `096001` / 2024 the only planned candidate and correctly `provenance_unknown` / `quality_unknown` / `not_promoted`?** **Yes.**
- **Does the plan use only public CLI and include preflight/help mismatch stop behavior?** **Yes.**
- **Is provenance ordered before quality/promotion with fail-closed stops?** **Yes.**
- **Is `manager_strategy_text` P0 handling precise without inferring extractor/policy fixes?** **Yes.**
- **Do all terminal states have `promotion_disposition=not_promoted`?** **Yes.**
- **Are fallback ordering contingency-only and all exclusions preserved?** **Yes.**
- **Does the plan respect all boundary stop conditions?** **Yes.**
- **Are planned commands/paths materially wrong or risky?** **No.** The one minor finding (F1) is resolvable by the planned preflight.

**May this plan be accepted as a plan for a later `096001` evidence run, without authorizing evidence now?** **Yes.** The plan correctly constrains itself to plan-only scope, preserves all required non-goals and exclusions, and provides a complete terminal-state matrix for the future evidence runner. Acceptance of this plan does not authorize any evidence execution, code change, or promotion.
