# Source Provenance Bounded Evidence Classification — Evidence Review (AgentMiMo)

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Role: evidence reviewer
> Gate: `source provenance bounded evidence classification review`

## Reviewed Target

- Evidence artifact: `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-20260527.md`
- Accepted plan: `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-plan-20260527.md`

## Review Scope

1. Evidence worker followed accepted command bounds for `110020` / 2024 and `017641` / 2024.
2. Classification uses only public provenance fields plus public quality outputs.
3. Terminal states are valid; no fallback eligibility inferred from extraction/score/quality success.
4. Denominator and promotion discipline: every row `not_promoted`; no baseline/golden/clean denominator promotion.
5. No source/test/design/control-doc code changes were made by worker; generated outputs remain ignored.

## Source Of Truth

- `AGENTS.md` — fallback strategy (§年报来源 fallback 策略), fail-closed rules
- `docs/design.md` — §6.1 / source provenance public-output contract: if `fallback_used=true` but metadata does not persist `primary_failure_category`, `fallback_eligibility` must be `unknown_public_metadata_absent`
- `docs/implementation-control.md` — Startup Packet / Current Gate / Next Entry Point
- Accepted plan artifact — exact run IDs, output paths, classification rules, forbidden scope, denominator rules

## Assumptions Tested

1. Worker ran exactly the 6 bounded CLI commands — no more, no fewer.
2. Worker did not access `FundDocumentRepository`, source helpers, downloader internals, PDF/cache, or non-public metadata.
3. Classification logic follows the plan's terminal-state vocabulary and rule precedence.
4. `primary_failure_category` is indeed `null` / absent in current public snapshot output.
5. Both rows are classified `not_promoted` and excluded from clean denominator.
6. Worker did not modify source code, tests, `docs/design.md`, or `docs/implementation-control.md` (except legitimate gate state transition).
7. Generated outputs were written only to `.gitignore`-d report directories.
8. Quality gate JSON fields match what the evidence artifact reports.

## Verification Results

### 1. Command Bounds

Evidence artifact lists exactly 6 commands matching the plan's "Validation Commands For Evidence Worker" section (lines 154–161). All exit codes are 0. No additional commands were run. **PASS.**

### 2. Public Provenance Fields Only

Evidence artifact reads from:
- `snapshot.jsonl` — public provenance fields: `fallback_used`, `primary_failure_category`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason`, `source_provenance_schema_version`, `source_strategy`, `resolved_source_name`
- `quality_gate.json` — `status`, `issue_count`, `issues` (rule codes and severity)

Cross-checked actual `snapshot.jsonl` for both funds: all 16 rows per fund contain identical provenance values matching the evidence artifact exactly. Cross-checked actual `quality_gate.json` for both funds: 110020 status=`warn`/3 issues, 017641 status=`block`/8 issues — matches evidence artifact exactly.

Evidence boundary statement explicitly excludes `FundDocumentRepository`, source helpers, downloader internals, PDF/cache, private exceptions, web/search, non-public metadata. **PASS.**

### 3. Terminal States

Both rows classified `provenance_unknown_public_metadata_absent`. This is a valid terminal state from the plan's vocabulary. Classification logic is correct:

- `fallback_used=true` ✓
- `primary_failure_category=null` ✓
- `fallback_eligibility=unknown_public_metadata_absent` ✓
- `source_provenance_status=incomplete` ✓
- `source_provenance_reason=fallback_used_primary_failure_category_absent` ✓

Per design.md §6.1: "若 `fallback_used=true` 但当前元数据未持久化 `primary_failure_category`，`fallback_eligibility` 必须为 `unknown_public_metadata_absent`，不得推断为 `eligible`。" Implementation correctly produces this behavior; evidence worker correctly classifies it.

For 017641, evidence worker correctly stops at `provenance_unknown_public_metadata_absent` before considering `quality_blocked_after_provenance`, because provenance did not first prove fallback eligibility. **PASS.**

### 4. No Fallback Eligibility From Extraction/Score/Quality Success

Evidence artifact explicitly states: "Successful extraction, populated `snapshot.jsonl`, populated `score.json`, and quality-gate completion were not used as fallback eligibility evidence." Both classification basis sections reinforce this. **PASS.**

### 5. Denominator And Promotion Discipline

| Fund | Year | Terminal state | Quality | Denominator | Promotion |
|---|---|---|---|---|---|
| 110020 | 2024 | `provenance_unknown_public_metadata_absent` | `warn` | Excluded | `not_promoted` |
| 017641 | 2024 | `provenance_unknown_public_metadata_absent` | `block` | Excluded | `not_promoted` |

No baseline, golden answer, strict golden, curated fixture, or clean denominator promotion occurred. **PASS.**

### 6. No Source/Test/Design/Control-Doc Code Changes

`git diff --name-only a0de731..HEAD` shows:
- `docs/implementation-control.md` — gate state transition (expected)
- `docs/reviews/` — plan reviews, controller judgment, evidence plan (accepted gate artifacts)

`git status --short` shows untracked:
- `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-20260527.md` — this evidence artifact (expected, worker's only tracked output)
- Other unrelated untracked files

No source code, test, `docs/design.md`, renderer, source strategy, Host/Agent/dayu, or baseline/golden/fixture state was changed by the worker. **PASS.**

### 7. Generated Output Hygiene

Worker reports `git status --short` for the six generated output directories returned no tracked or untracked entries, consistent with `.gitignore` handling. The only intended tracked artifact is the evidence summary file. **PASS.**

## Findings

No material findings. All review scope items pass verification against actual generated outputs, source-of-truth constraints, and the accepted plan's bounds.

## Open Questions

None.

## Residual Risks

None for this gate. The `provenance_unknown_public_metadata_absent` terminal state is a known structural gap: `AnnualReportSourceMetadata` does not propagate `primary_failure_category` into the public snapshot path. This is correctly acknowledged in both the plan (line 42) and the evidence artifact. Closing this gap requires a future implementation change to persist `primary_failure_category` from repository source metadata — that is outside this gate's scope.

## Reviewer Self-Check

- [x] Reviewed target, scope, source of truth, and assumptions tested are specified.
- [x] Findings are evidence-based, adversarial, actionable; no style/nit/speculation.
- [x] Open questions, residual risks, and tracking destination are separated from findings.
- [x] Conclusion is one of `pass`, `pass-with-risks`, `fail`.
- [x] Output path uses system-clock timestamp and matches artifact path format.

## Conclusion

**PASS.** The evidence worker correctly followed all accepted command bounds, classified using only public provenance fields and public quality outputs, applied valid terminal states, enforced denominator and promotion discipline, and made no forbidden code or document changes. No material findings.
