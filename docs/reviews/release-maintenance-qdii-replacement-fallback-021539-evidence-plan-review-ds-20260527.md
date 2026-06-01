# QDII Replacement Fallback 021539 Evidence Plan — DS Independent Plan Review

> Date: 2026-05-27
> Reviewer: AgentDS (independent plan review only; no implementation, no commit, no push, no PR)
> Target: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-plan-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Control doc current gate | `QDII replacement post-019172 disposition decision accepted locally` |
| Control doc next entry point | `QDII replacement fallback candidate evidence plan gate for 021539; must use init-agents / tmux multi-agent flow` |
| This review gate | `QDII replacement fallback candidate evidence plan gate for 021539` |
| Latest accepted checkpoint | `bdae33c docs: accept qdii post 019172 disposition` |
| Accepted controller judgment | `docs/reviews/release-maintenance-qdii-replacement-post-019172-disposition-decision-controller-judgment-20260527.md` |

This review follows the Startup Packet next entry point. It is a plan review, not an evidence review, not a controller judgment.

## Criterion-by-Criterion Assessment

### C1: Startup Packet next entry point follow, not gate switch

**PASS.** Plan §1 line 11 replays `QDII replacement fallback candidate evidence plan gate for 021539; must use init-agents / tmux multi-agent flow`, which matches control doc line 29 and the post-019172 disposition controller judgment line 56. Plan line 24 declares `This plan follows the Startup Packet next entry point. It is not a gate switch.` The init-agents requirement is correctly preserved as a controller obligation (lines 26, 308).

### C2: Plan-only, no evidence/fund-analysis authorization

**PASS.** Plan line 6: `Scope: plan artifact only. No evidence run.` Plan §4 (lines 62–71) explicitly prohibits all `fund-analysis` subcommands. Plan §15 (lines 337–352) enumerates stop conditions covering every evidence command, PDF/cache/helper access, and external web probing. No evidence command is authorized.

### C3: 021539 / 2024 only, pre-state provenance_unknown / quality_unknown / not_promoted

**PASS.** Plan §2 table (lines 36–44) selects exactly `021539` / `2024`, with `provenance_unknown`, `quality_unknown`, `promotion_disposition=not_promoted`. Line 39: `one bounded fallback QDII replacement evidence candidate`. Lines 46–47 explicitly deny source-safe, scoring-ready, baseline-ready, golden-ready, or promoted status. No other candidate is planned for evidence.

### C4: Preserved accepted states for 096001, 040046, 019172

**PASS.** Plan §3 table (lines 52–56) preserves all three with eligible complete public fallback provenance, `quality_gate_status=block`, terminal `quality_blocked_after_provenance`, and `promotion_disposition=not_promoted`. Cross-checked against post-019172 disposition decision artifact §2 (lines 29–31):

- `096001`: P0 `nav_benchmark_performance`, FQ4 42.9%, P1 gaps, `manager_strategy_text` passed. ✓
- `040046`: P0 pass, FQ4 35.7%, P1 gaps. ✓
- `019172`: P0 `manager_strategy_text` 0.0%/0.0%, FQ4 35.7%, P1 gaps. ✓

No weakening, rerunning, or reinterpretation is authorized. Plan lines 58–59 correctly state none is replacement-ready or promoted.

### C5: Prohibition of 020712, active QDII, QDII-FOF, 013308, bond QDII, 017641, 096001, 040046, 019172, and subsequent candidates

**PASS.** Plan line 71 prohibits all named categories in the plan gate. Plan §12 (lines 272–276) preserves exclusions for `017641`, QDII-FOF, `013308`, and bond QDII with explicit rationale for each. Plan §15 lines 346–348 repeat the prohibition. Plan §11 (lines 262–264) establishes hard stop after a quality-blocked `021539` to prevent automatic continuation to later candidates.

Edge case check: `013308` is correctly preserved as "pending" with naming/category conflict (line 274), not silently included or excluded. `active QDII` (006282, 007280) is covered by the "active QDII" prohibition in line 71.

### C6: Future evidence plan shape — public CLI + generated summary.md/snapshot.jsonl provenance discipline, provenance-before-score/quality, fail-closed semantics

**PASS.**

- **CLI preflight**: Plan §5 (lines 77–91) plans `--help` verification of `extraction-snapshot`, `extraction-score`, and `quality-gate` flags before evidence execution, with `cli_flag_mismatch_not_run` stop behavior. ✓
- **Explicit public commands**: Plan §6 (lines 107–141) specifies exact `uv run fund-analysis` commands with explicit paths, run-id, and ignored output directories. ✓
- **Generated file provenance**: Plan §7 (lines 152–172) requires reading public provenance from generated `summary.md` and `snapshot.jsonl`, with stdout-vs-file conflict resolution favoring generated files. ✓
- **Provenance before quality**: Plan §8 line 177: `Source provenance must be interpreted before score, quality status, replacement usefulness, or any promotion language.` Plan §9 line 206: `Quality interpretation is allowed only after source provenance reaches an eligible state.` ✓
- **Fail-closed semantics**: Plan §8 lines 179–183 enumerate `schema_drift`, `identity_mismatch`, `integrity_error` as fail-closed with stop-before-score/quality. Plan lines 187–200 enumerate eligible and ineligible fallback conditions, matching AGENTS.md lines 227–237 and the controller judgment line 68. ✓
- **Non-eligible cases**: Plan lines 192–200 explicitly reject: missing `primary_failure_category`, incomplete provenance tuple, unknown fallback category, missing `fallback_eligibility`, internal-file-only provenance, command-success-only, stdout-only. ✓

### C7: Terminal matrix completeness including FQ4/non-P0 block + P0 pass row

**PASS.** Plan §10 (lines 242–258) contains 13 terminal rows:

| Row | Present |
|---|---|
| CLI help flag mismatch | ✓ line 246 |
| Snapshot command non-zero exit | ✓ line 247 |
| Public snapshot outputs missing | ✓ line 248 |
| Provenance missing/incomplete (two variants) | ✓ line 249 |
| Fail-closed source (schema_drift/identity_mismatch/integrity_error) | ✓ line 250 |
| Ineligible/unknown fallback | ✓ line 251 |
| Score command non-zero exit | ✓ line 252 |
| Quality-gate command non-zero exit | ✓ line 253 |
| P0 block on manager_strategy_text (two variants) | ✓ line 254 |
| P0 block on another field | ✓ line 255 |
| **FQ4/non-P0 structural quality block + P0 pass** | ✓ line 256 |
| Warn with P1 residuals only | ✓ line 257 |
| Pass | ✓ line 258 |

Every row keeps `promotion_disposition=not_promoted`. The FQ4/non-P0 + P0-pass row is explicitly present (line 256), matching the accepted `040046` evidence pattern where P0 passed but FQ4 blocked at 35.7%.

### C8: Hard stop after 021539 quality-block, new disposition gate required

**PASS.** Plan §11 (lines 262–264): `If a later accepted 021539 evidence gate quality-blocks after eligible provenance, automatic QDII probing stops. The next step must be a new disposition gate that chooses between QDII extraction/applicability diagnosis, taxonomy / asset-class fitness, or recording QDII coverage as blocked.` This matches the controller judgment line 70 exactly. The stop applies to `020712`, active QDII, QDII-FOF, `013308`, bond QDII, and all later candidates. The requirement is also restated in the future evidence expectations (line 302).

### C9: Exclusions preserved, code/test/renderer/FQ0-FQ6/Service/CLI/FundDocumentRepository/source strategy/taxonomy/extractor/Host/Agent/Dayu/golden/baseline changes and promotion prohibited

**PASS.** Plan §12 (lines 270–277) preserves exclusions with individual rationale. Plan §15 (lines 339–352) enumerates stop conditions covering every prohibited change category:

- code, tests, renderer, FQ0-FQ6, Service, CLI, default behavior ✓
- `FundDocumentRepository`, source strategy, source-helper fallback semantics ✓
- taxonomy, extractor, Host, Agent, Dayu ✓
- golden files, baseline fixtures, corpus state ✓
- promotion to durable baseline, clean denominator, fixture, report-quality corpus, golden answer corpus, accepted replacement, source-safe, scoring-ready ✓
- commit, push, PR, merge, branch deletion, GitHub mutation ✓

Line 349–350 also prohibits editing `docs/implementation-control.md` or `docs/design.md`, which the controller judgment (line 72) requires.

### C10: Validation limited to git diff --check

**PASS.** Plan §16 (lines 366–371) specifies only `git diff --check` with required result `pass`. No other validation command, linter, test runner, or code analysis is specified or authorized. This is consistent with a docs-only plan artifact that changes no code.

## Findings

### F1 (low): Naming ambiguity — "evidence plan" in gate name and file name

**Evidence**: The gate name `QDII replacement fallback candidate evidence plan gate for 021539` and file name `release-maintenance-qdii-replacement-fallback-021539-evidence-plan-20260527.md` embed "evidence" in a plan artifact name. This pattern was previously flagged as DS F2 in the post-019172 disposition decision review (`release-maintenance-qdii-replacement-post-019172-disposition-decision-review-ds-20260527.md`) and accepted as low by the controller with the note that "Startup Packet and handoff must explicitly prohibit evidence until reviewed acceptance."

**Why material (low)**: The same naming pattern recurs in a new artifact. A future worker reading only the file name and gate name could misinterpret this as authorizing evidence execution. The plan mitigates this with explicit plan-only prohibitions in §4 and §15, and the control doc handoff provides additional guard. However, the recurrence suggests the naming convention itself should be reconsidered — for example, using `plan` without `evidence` in the gate name (e.g., `021539 evidence plan gate` → `021539 plan gate`).

**Required next action**: None required for this review gate. The controller may consider renaming future plan-gate artifacts to avoid the ambiguity, or accept the recurring pattern with the same mitigation as before.

### F2 (low): Forward-looking quality classification guidance borders on pre-scripting evidence outcomes

**Evidence**: Plan §9 lines 217–238 detail specific quality classification scenarios, including:
- Line 219: `If manager_strategy_text is missing because public disclosure genuinely lacks manager strategy discussion, classify as disclosure_data_gap_not_baseline_ready only when the public evidence supports that conclusion.`
- Lines 236–238: False-positive suspicion handling with `false_positive_suspicion=true` conditions and required next actions.

**Why low**: These are explicitly framed as future evidence gate instructions, not current evidence findings. The plan repeatedly states it does not run evidence (§4, §15). The guidance is anchored to public generated outputs and does not authorize code/taxonomy/extractor changes. However, the level of detail — specifying exact terminal classifications based on hypothetical evidence states — creates a slight risk that a future evidence runner treats these as predetermined conclusions rather than as a checklist of scenarios to evaluate against actual evidence.

**Required next action**: None. The future evidence worker must independently evaluate actual public generated outputs against the terminal matrix; these scenario descriptions are reference guidance only.

## Review Summary

All 10 review criteria pass. Two low findings are identified:

- **F1 (low)**: Recurring naming ambiguity where "evidence plan" appears in a plan-only artifact name. Same pattern as prior DS F2, previously accepted by controller.
- **F2 (low)**: Detailed quality classification guidance in §9 borders on pre-scripting evidence outcomes, though all references are clearly marked as future evidence instructions.

No blocking or material finding prevents plan acceptance. The plan correctly:
- follows the Startup Packet next entry point (not a gate switch);
- is strictly plan-only with no evidence authorization;
- targets exactly `021539` / 2024 with `provenance_unknown` / `quality_unknown` / `not_promoted`;
- preserves `096001`, `040046`, `019172` accepted states without weakening;
- prohibits all excluded and subsequent candidates;
- mandates public CLI + generated-file provenance discipline with provenance-before-quality ordering and fail-closed semantics;
- provides a complete terminal matrix including the FQ4/non-P0 + P0-pass row;
- establishes hard stop after `021539` quality-block with new disposition gate requirement;
- preserves all exclusions and prohibits all code/test/infrastructure/promotion changes;
- limits validation to `git diff --check`.

## Validation

| Command | Exit code | Result |
|---|---:|---|
| `git diff --check` | 0 | passed |
