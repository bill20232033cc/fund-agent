# Source Provenance Bounded Evidence Classification — AgentGLM Review

> Date: 2026-05-27
> Role: AgentGLM evidence reviewer
> Evidence artifact: `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-plan-20260527.md`
> Truth sources: `AGENTS.md`, `docs/design.md` current design sections (§2, §6.1 provenance), `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point
> Reviewer timestamp: `20260527-061340`

## Reviewed Target and Scope

Review the evidence worker's classification output for bounded provenance evidence run covering `110020` / 2024 and `017641` / 2024. Verify:

1. Evidence worker followed accepted command bounds for both funds.
2. Classification uses only public provenance fields plus public quality outputs.
3. Terminal states are valid and no fallback eligibility is inferred from extraction/score/quality success.
4. Denominator and promotion discipline: every row `not_promoted`; no baseline/golden/clean denominator promotion.
5. No source/test/design/control-doc code changes were made by worker; generated outputs remain ignored.
6. Challenge terminal-state selection for 017641 quality block versus `provenance_unknown_public_metadata_absent` ordering.
7. Surface findings ordered by severity with file/path references.

## Assumptions Tested

1. The six CLI commands in the evidence artifact match the accepted plan's validation commands exactly.
2. Public snapshot provenance fields (`fallback_used`, `primary_failure_category`, `fallback_eligibility`, `source_provenance_status`, `source_provenance_reason`, `source_provenance_schema_version`, `source_strategy`, `resolved_source_name`) are the sole basis for provenance classification.
3. Quality gate `status`, `issue_count`, and rule codes are the sole quality inputs.
4. `primary_failure_category=null` with `fallback_used=true` implies `fallback_eligibility=unknown_public_metadata_absent`, per plan rule 3 and design.md §6.1.
5. Classification evaluates provenance before quality (sequential waterfall); `quality_blocked_after_provenance` requires provenance to first prove eligibility.
6. No promotion of baseline, golden, strict golden, curated fixture, or clean denominator is permitted in this gate.

## Verification Results

### 1. Command Bounds

Evidence artifact commands 1–6 match the accepted plan's "Validation Commands For Evidence Worker" exactly:

- Fund codes: `110020` and `017641` only. ✅
- Run IDs: `source-provenance-bounded-110020-2024-20260527` and `source-provenance-bounded-017641-2024-20260527`. ✅
- Output directories: under `reports/extraction-snapshots/`, `reports/scoring-runs/`, `reports/quality-gate-runs/` with matching run-ID subdirectories. ✅
- All six exit codes are 0. ✅
- No extra commands were run beyond the six bounded commands. ✅

### 2. Public Provenance Field Verification

Verified against actual snapshot JSONL files:

**110020 / 2024** — `reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/snapshot.jsonl`:
| Field | Claimed | Actual | Match |
|---|---|---|---|
| `fallback_used` | `true` | `true` | ✅ |
| `primary_failure_category` | `null` | `null` | ✅ |
| `fallback_eligibility` | `unknown_public_metadata_absent` | `unknown_public_metadata_absent` | ✅ |
| `source_provenance_status` | `incomplete` | `incomplete` | ✅ |
| `source_provenance_reason` | `fallback_used_primary_failure_category_absent` | `fallback_used_primary_failure_category_absent` | ✅ |
| `source_provenance_schema_version` | `repository_source_provenance.v1` | `repository_source_provenance.v1` | ✅ |
| `source_strategy` | `primary_then_fallback` | `primary_then_fallback` | ✅ |
| `resolved_source_name` | `eastmoney` | `eastmoney` | ✅ |

**017641 / 2024** — `reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/snapshot.jsonl`:
All fields match identically to the claimed values. ✅

Snapshot row counts: evidence claims 16 rows per fund; actual `wc -l` confirms 16 lines per snapshot JSONL. ✅

### 3. Quality Gate Verification

**110020**: Evidence claims `status=warn`, `issue_count=3`. Actual JSON confirms. ✅
Issue summary claimed: `FQ2/warn turnover_rate`, `FQ2F/warn 110020`, `FQ0/info strict golden not configured`.
Actual JSON issues: `FQ2/warn turnover_rate`, `FQ2F/warn None 110020`, `FQ0/info None 110020`. Semantic match confirmed — the `FQ0/info` rule message content corresponds to "strict golden not configured". ✅

**017641**: Evidence claims `status=block`, `issue_count=8`. Actual JSON confirms. ✅
Issue summary claimed: `FQ2/block manager_strategy_text`, `FQ3/block manager_strategy_text`, `FQ2/warn turnover_rate`, `FQ2/warn holdings_snapshot`, `FQ2F/block 017641`, `FQ2F/warn 017641`, `FQ0/info strict golden not configured`, `FQ4/warn high missing-field rate`.
Actual JSON issues match all 8 entries semantically. ✅

### 4. Terminal-State Verification

**110020 / 2024**: `provenance_unknown_public_metadata_absent`. ✅

Classification basis: `fallback_used=true`, `primary_failure_category=null`, `fallback_eligibility=unknown_public_metadata_absent`. Matches plan rule 3 exactly. The `warn` quality status is non-blocking but does not prove fallback eligibility. Correct.

**017641 / 2024**: `provenance_unknown_public_metadata_absent`. ✅

Classification basis: identical provenance profile to 110020. Quality status is `block` (8 issues including `FQ2/block` and `FQ3/block` on `manager_strategy_text`). However, because provenance classification resolves to `unknown_public_metadata_absent` first, the quality block does not promote the terminal state to `quality_blocked_after_provenance`. Correct per plan rule ordering.

### 5. Terminal-State Challenge: 017641 Quality Block vs. Provenance Ordering

The review scope specifically asked to challenge the terminal-state selection for 017641.

**Challenge**: 017641 has quality status `block` with 8 issues. Could `quality_blocked_after_provenance` be the correct terminal state instead of `provenance_unknown_public_metadata_absent`?

**Analysis**: Plan rule 5 (`quality_blocked_after_provenance`) requires: "Public provenance explicitly proves fallback eligibility, but `quality_gate.json` has `status=block`." The critical prerequisite is that provenance *explicitly proves* fallback eligibility. For 017641:
- `fallback_eligibility=unknown_public_metadata_absent` — provenance does NOT prove eligibility.
- `primary_failure_category=null` — no eligible category is established.
- `source_provenance_status=incomplete` — provenance is incomplete.

Since provenance did not prove eligibility, rule 5 cannot fire regardless of quality status. The sequential classification (provenance before quality) means `provenance_unknown_public_metadata_absent` is the correct terminal state.

The evidence artifact's classification basis for 017641 states: "The row therefore stops at `provenance_unknown_public_metadata_absent` before any `quality_blocked_after_provenance` classification can apply. The quality gate is `block`, but public provenance did not first prove fallback eligibility." This is a correct and well-reasoned statement.

**Verdict**: Terminal state for 017641 is correct. No issue found.

### 6. No Fallback Eligibility Inferred from Downstream Success

Evidence artifact's Evidence Boundary Statement (line 129) correctly states: "Successful extraction, populated `snapshot.jsonl`, populated `score.json`, and quality-gate completion were not used as fallback eligibility evidence." The classification logic only uses public provenance fields to determine eligibility, not extraction/score/quality success. ✅

### 7. Denominator and Promotion Discipline

| Fund | Terminal state | Promotion disposition | Clean denominator |
|---|---|---|---|
| 110020 | `provenance_unknown_public_metadata_absent` | `not_promoted` | Excluded ✅ |
| 017641 | `provenance_unknown_public_metadata_absent` | `not_promoted` | Excluded ✅ |

Both rows are `not_promoted`. No baseline, golden answer, strict golden, curated fixture, or clean denominator promotion occurred. ✅

### 8. Source/Test/Design/Control Hygiene

`git diff HEAD` against `*.py`, `*.toml`, `docs/design.md`, `docs/implementation-control.md`, `tests/`, `AGENTS.md`: no changes. ✅

`git status --short`: only untracked files under `docs/reviews/` and `docs/tmux-agent-memory-store.md`. The evidence summary artifact is the only intended new tracked file. ✅

Generated output directories confirmed to exist under `reports/` (gitignored). No tracked generated outputs. ✅

### 9. Evidence Boundary Compliance

Evidence artifact states it did not inspect or call `FundDocumentRepository`, source helpers, downloader internals, PDF/cache internals, private source exceptions, web/search, or non-public repository metadata. This is consistent with the accepted plan's forbidden scope. ✅

## Findings

No material findings.

All verification checks passed:
- Commands match accepted plan bounds exactly.
- Provenance fields verified against actual snapshot JSONL data.
- Quality gate outputs verified against actual JSON data.
- Terminal states correctly applied per plan classification rules.
- 017641 terminal-state challenge resolved: `provenance_unknown_public_metadata_absent` is correct because provenance must prove eligibility before quality evaluation can override.
- No fallback eligibility inferred from downstream success.
- All rows `not_promoted`; no denominator promotion.
- No source code, test, design, or control-doc changes.
- Generated outputs remain in gitignored directories.

## Open Questions

None.

## Residual Risks

1. **Future provenance propagation**: The current implementation does not propagate `primary_failure_category` into public snapshots. Both bounded rows therefore classify as `provenance_unknown_public_metadata_absent`. A future implementation change that persists `primary_failure_category` would allow these rows to be re-classified. This is an expected design constraint, not a defect. Tracking: future gate decision on source metadata propagation.

2. **017641 quality block deferred**: The `block` quality status for 017641 (8 issues including `manager_strategy_text` coverage/traceability failures) remains unresolved but is correctly outside this gate's scope. Tracking: future quality remediation gate.

## Final Conclusion

**PASS**

The evidence worker followed all accepted command bounds, used only public provenance fields and public quality outputs for classification, correctly applied terminal states for both funds (including the defensible `provenance_unknown_public_metadata_absent` classification for 017641 despite its quality block), maintained strict `not_promoted` discipline with no denominator promotion, made no source/test/design/control changes, and kept generated outputs in gitignored directories.
