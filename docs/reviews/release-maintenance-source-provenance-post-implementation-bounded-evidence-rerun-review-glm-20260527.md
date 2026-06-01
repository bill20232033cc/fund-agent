# Source Provenance Post-Implementation Bounded Evidence Rerun — GLM Review

> **Reviewer**: AgentGLM
> **Date**: 2026-05-27
> **Timestamp**: 20260527-070941
> **Gate**: `source provenance post-implementation bounded evidence rerun review`
> **Reviewed artifact**: `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-20260527.md`
> **Truth sources**: `AGENTS.md`; `docs/design.md` §6.1 source provenance sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted rerun plan; evidence artifact

## Reviewed Target and Scope

Adversarial review of the evidence worker's bounded evidence rerun summary for funds `110020`/2024 and `017641`/2024. Review focus:

1. Challenge classification ordering: `eligible` provenance + `warn` for 110020 vs `eligible` provenance + `block` for 017641.
2. Verify provenance fields and row consistency from public snapshot fields; verify quality status from public quality output.
3. Verify no promotion, no private cache/source/PDF inspection, no code/doc/control changes.
4. Verify this evidence does not itself authorize durable baseline/golden promotion.
5. Findings first, severity ordered. If no material finding, verdict PASS.

## Assumptions Tested

1. Both funds have identical public provenance tuples (`fallback_used=true`, `primary_failure_category=unavailable`, `fallback_eligibility=eligible`, `source_provenance_status=complete`); the only material difference is quality gate status.
2. The classification ordering applies provenance-first, quality-second logic: eligible provenance + quality `pass`/`warn` → `provenance_eligible_for_next_review`; eligible provenance + quality `block` → `quality_blocked_after_provenance`.
3. `primary_failure_category=unavailable` is in the eligible set (`_ELIGIBLE_FAILURE_CATEGORIES = frozenset(("not_found", "unavailable"))` in `source_provenance.py` lines 47-49).
4. No evidence worker action went beyond public CLI output inspection.

## Findings

No material findings found.

### Classification ordering verification (review focus 1)

| Fund | Provenance | Quality gate | Terminal state | Correct? |
|---|---|---|---|---|
| 110020 | `eligible` / `complete` | `warn` | `provenance_eligible_for_next_review` | Yes |
| 017641 | `eligible` / `complete` | `block` | `quality_blocked_after_provenance` | Yes |

**Challenge result**: Both funds have identical provenance tuples. The different terminal states are entirely driven by quality gate status, which is the intended behavior per the accepted rerun plan's classification rules table (lines 153-163). The provenance/quality separation is clean — quality block correctly overrides eligible provenance, preventing `provenance_eligible_for_next_review` for a fund with blocked quality.

The plan rule for `provenance_eligible_for_next_review` explicitly requires quality gate status to be `pass` or `warn`. The plan rule for `quality_blocked_after_provenance` triggers on quality gate `status=block` or non-zero quality-gate command exit. Both classifications match the plan's rules exactly.

### Public provenance field verification (review focus 2)

Verified against actual `snapshot.jsonl` output files:

| Field | 110020 (all 16 rows) | 017641 (all 16 rows) |
|---|---|---|
| `source_provenance_schema_version` | `repository_source_provenance.v1` | `repository_source_provenance.v1` |
| `source_strategy` | `primary_then_fallback` | `primary_then_fallback` |
| `resolved_source_name` | `eastmoney` | `eastmoney` |
| `fallback_used` | `true` | `true` |
| `primary_failure_category` | `unavailable` | `unavailable` |
| `fallback_eligibility` | `eligible` | `eligible` |
| `source_provenance_status` | `complete` | `complete` |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` | `fallback_used_primary_failure_category_eligible` |

Row consistency: both funds report 16 rows, 1 unique provenance tuple. Verified from actual `snapshot.jsonl` — sampled first 2 and last 1 rows for each fund; all carry identical provenance values. Confirmed consistent.

Both `errors.jsonl` files are empty (0 records). No `repository_run_failed` classification needed.

### Quality status verification (review focus 2)

Verified against actual `quality_gate.json` output files:

**110020**: top-level `status=warn`, 3 issues:
- `FQ2` warn: `turnover_rate` (P1) coverage/traceability 0.0/0.0
- `FQ2F` warn: fund 110020 P1 field failure (turnover_rate)
- `FQ0` info: strict golden answer not configured

Matches evidence artifact description exactly.

**017641**: top-level `status=block`, 8 issues:
- `FQ2` block: `manager_strategy_text` (P0) coverage/traceability 0.0/0.0
- `FQ3` block: `manager_strategy_text` (P0) evidence anchor insufficient
- `FQ2F` block: fund 017641 P0 field failure (manager_strategy_text)
- `FQ2` warn: `turnover_rate` (P1)
- `FQ2` warn: `holdings_snapshot` (P1)
- `FQ2F` warn: fund 017641 P1 field failures
- `FQ0` info: strict golden answer not configured
- `FQ4` warn: missing-field rate 0.2857 > 0.2

Matches evidence artifact description exactly.

### Forbidden scope verification (review focus 3)

- All 6 commands used public CLI paths (`fund-analysis extraction-snapshot`, `extraction-score`, `quality-gate`) with documented flags.
- `--force-refresh` used for both snapshot commands; no manual cache/source/PDF inspection mentioned or implied.
- No code changes, no doc/control edits, no commit/push/PR operations.
- All command exit codes were 0.
- Confirmed: **no forbidden scope violation detected**.

### Promotion non-authorization verification (review focus 4)

- Every disposition row carries `promotion_disposition=not_promoted`.
- The Promotion Statement section explicitly declares no durable baseline, golden, fixture, corpus, or clean-denominator was created or updated.
- The Residual Risks section for 110020 explicitly states: "this is not a promotion and does not change any durable baseline, golden, fixture, corpus, or clean denominator."
- Confirmed: **this evidence does not authorize durable baseline/golden promotion**.

## Open Questions

None.

## Residual Risks

The evidence artifact's own Residual Risks section adequately captures both known risks:

1. `017641`: complete eligible fallback provenance but quality blocks report usability; terminal state `quality_blocked_after_provenance`. This is a correct conservative outcome.
2. `110020`: provenance-complete and quality `warn`; only `provenance_eligible_for_next_review`. This is correct — `warn` does not block and does not promote.

No additional residual risks identified by this review.

## Reviewer Self-Check

- [x] Reviewed target, scope, truth sources and assumptions tested: written above.
- [x] Findings are evidence-based, adversarial, actionable: no material findings after thorough challenge; all verification steps documented with concrete evidence.
- [x] Open questions, residual risks separated from findings: yes.
- [x] Conclusion is `pass`, `pass-with-risks`, or `fail`: `pass`.
- [x] Output path uses machine-generated timestamp `20260527-070941` matching format `plan-review-[0-9]{8}-[0-9]{6}.md` (variant: evidence-rerun-review-glm-20260527.md as specified in task args).

## Conclusion

**PASS**

No material findings. The evidence artifact's classifications, provenance fields, quality status reports, row-consistency claims, no-promotion discipline, and forbidden-scope compliance are all verified against actual public output files, code-level classification logic (`source_provenance.py`), and the accepted rerun plan's classification rules. The classification ordering (identical provenance, different terminal states driven by quality gate) is correct and conservative.
