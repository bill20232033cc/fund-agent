# Review: Quality Warning Issue Identity Evidence Gate

Date: 2026-06-12

Reviewer: MiMo

Gate: `Quality warning issue identity evidence gate`

Review target: `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md`

Accepted basis: `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-quality-warning-issue-root-cause-plan-controller-judgment-20260612.md`

## 1. Verdict

**PASS**

## 2. Findings

| # | Severity | Finding | Evidence | Recommendation |
|---:|---|---|---|---|
| MIMO-QI-001 | info | Static code mapping line numbers are approximate but within correct function range | Evidence §8 cites `quality_gate.py:600-606` for FQ2; actual FQ2 warn logic is at lines 577 and 603. Similarly `quality_gate.py:650-656` for FQ2F is at lines 639 and 653 | No action; line references are close enough for traceability and verified against source |
| MIMO-QI-002 | info | E3 command boundary does not explicitly state that stdout/stderr were captured to the tmp directory files | Evidence §4 shows header facts from stdout but does not restate the capture verification step after the command completed | No action; the header facts and artifact identity table prove the capture occurred; the command redirect syntax is explicit |

No blocking or warning findings.

## 3. Review Focus Assessment

### 3.1 Issue Identity Sufficiency

The evidence artifact establishes accepted identity for all three quality-gate issues:

| Issue | Rule | Severity | Evidence chain |
|---|---|---|---|
| FQ2/warn turnover_rate | `FQ2` | `warn` | score.json field row: `coverage_rate=0.0`, `traceability_rate=0.0`, `status=fail`, `priority=P1`; code mapping at `extraction_score.py:51` (P1 priority) and `quality_gate.py:603` (FQ2 warn) |
| FQ2F/warn 004393 | `FQ2F` | `warn` | score.json fund row: `p1_failed_fields=["turnover_rate"]`, `p1_status=fail`; code mapping at `quality_gate.py:653` (FQ2F warn); correctly identified as aggregate derivative of FQ2, not a separate root cause |
| FQ0/info year_not_covered | `FQ0` | `info` | score.json correctness summary: `coverage_reason=year_not_covered`, `coverage_scope=year_not_covered`; code mapping at `quality_gate.py:470` (FQ0/info); existing test at `test_quality_gate.py:634-697` confirms semantics |

All three identities are supported by: (a) current-gate live run score.json content with path+hash+size lineage, (b) static code mapping to quality gate rule logic, (c) existing deterministic tests confirming rule semantics. The evidence is sufficient.

### 3.2 Path-exists-only Rejection and Lineage

The evidence correctly:

1. **E1 no-live lineage check**: Ran `rg` over four accepted prior artifacts and found that none contain the three issue rows or path+hash+size/run identity sufficient to accept them. Correctly concluded `BLOCKED_BY_ARTIFACT_LINEAGE_GAP`.
2. **Rejected arbitrary `reports/` residue**: Per the accepted root-cause plan, path-exists-only use of mutable untracked `reports/` residue is explicitly rejected as proof.
3. **Established lineage via current-gate live run**: E3 produced a controlled live reproduction with:
   - Exact command with all parameters
   - Temp capture directory with explicit path
   - Exit code, stdout size, stderr size
   - quality_gate_status, quality_gate_issues, quality_gate_json, quality_gate_md paths
   - SHA-256 hash and size for all four artifacts (quality_gate.json, quality_gate.md, score.json, snapshot.jsonl)
   - Header facts from stdout (fund_code, target_year, canonical_years, available_years, etc.)

Lineage is complete and auditable. The artifacts are not staged and not promoted as source truth or release evidence.

### 3.3 NOT_READY Preservation

Release/readiness remains **`NOT_READY`**. The evidence artifact:

- Does not claim readiness, golden promotion, additional live samples, or broader provider/LLM acceptance
- Does not expand the live command into broader readiness/sample/provider claims
- Does not modify source, tests, runtime behavior, or external state
- Explicitly lists all deferred entries (strict golden 2025, additional live sample, provider/LLM, cleanup, PR/release)

The NOT_READY state is correctly preserved.

### 3.4 Next Mainline Recommendation

The recommended next mainline `Turnover rate extraction/traceability root-cause planning gate` is reasonable:

- FQ2/warn and FQ2F/warn are both derived from `turnover_rate` P1 coverage/traceability failure
- This is the primary actionable blocker for the quality warnings
- Root-cause evidence must precede implementation/fix
- The gate is correctly scoped to extraction/traceability, not broader readiness

The deferred entries are correctly ordered:

1. `Strict golden 2025 coverage/promotion planning gate` — correctly deferred; FQ0/info is informational and not an extractor failure
2. Additional controlled live sample gate — correctly deferred
3. Provider/LLM readiness gate — correctly deferred
4. Cleanup/delete/archive/import/ignore gate — correctly deferred
5. PR/push/merge/mark-ready/release gate — correctly deferred

## 4. Residuals

| Residual | Owner | Blocks readiness? |
|---|---|---|
| `turnover_rate` P1 coverage/traceability failure | Fund extractor / traceability owner | Yes |
| `FQ2F` aggregate fund-level warning | Quality gate + Fund extractor owner | Yes |
| Strict golden current-year coverage gap | golden/readiness owner | Yes for readiness/promotion |
| Broader live sample coverage not proven | release/evidence owner | Yes for broader readiness |
| PR/release/readiness state unchanged | release owner/controller | Yes |

## 5. Final Recommendation

The evidence artifact is accepted. It correctly establishes accepted issue identity candidates for the three quality-gate issues (FQ2/warn turnover_rate, FQ2F/warn 004393 derived from turnover_rate, FQ0/info year_not_covered), rejects path-exists-only residue with proper current-gate lineage, preserves NOT_READY, and recommends a reasonable next mainline gate.

No blocking or warning findings. Two info-level observations noted but do not require action.

Release/readiness remains **`NOT_READY`**.
