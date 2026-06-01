# Source Provenance Bounded Evidence Classification Plan Review — AgentMiMo

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-plan-20260527.md`
> Checkpoint: `a0de731 feat: expose source provenance in snapshots`
> Truth sources: `AGENTS.md`, `docs/design.md` §2/§6.1, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, current accepted artifacts, `docs/reviews/` evidence chain

---

## 1. Review Scope

Per the review focus prompt, this review checks:

1. Commands are bounded to public CLI for exactly `110020`/2024 and `017641`/2024.
2. Classification uses only public provenance fields and quality outputs, not downstream success as fallback proof.
3. Terminal states cover unknown metadata, fail-closed, repository failure, quality block after provenance, eligible for later review, `not_promoted`.
4. No code changes, no PDF/cache/source helper access, no source strategy change, no renderer/FQ/default CLI/Host/Agent/dayu/golden/baseline promotion.
5. Output hygiene and tracked summary artifact are adequate.
6. If plan needs revision before evidence, state exact required changes.

---

## 2. Gate Alignment Check

### 2.1 Startup Packet Replay

The plan's Startup Packet table (lines 9-20) correctly reproduces the current state from `docs/implementation-control.md`:

| Field | Plan | Control doc | Match |
|---|---|---|---|
| Branch | `codex/local-reconciliation` | same | ✅ |
| Current phase | `release maintenance` | same | ✅ |
| Current gate | `source provenance public-output implementation accepted locally` | same | ✅ |
| Next entry point | `post-implementation source provenance bounded evidence classification gate; must use init-agents / tmux multi-agent flow` | same | ✅ |
| Latest checkpoint | `a0de731` | same | ✅ |

**Verdict**: Startup Packet replay is accurate.

### 2.2 Next Entry Point Alignment

The control doc (line 340-348) specifies:

> `post-implementation source provenance bounded evidence classification gate`
> - Run only bounded public `fund-analysis extraction-snapshot`, `extraction-score`, and `quality-gate` commands for `110020` / 2024 and `017641` / 2024.
> - Keep `110020` and `017641` outside the clean denominator unless public provenance explicitly proves eligible fallback and a reviewed evidence gate accepts the classification.

The plan's "Allowed next-gate scope" section (lines 22-29) correctly reproduces these constraints verbatim.

**Verdict**: Next entry point alignment is correct.

---

## 3. Command Bounding Check

### 3.1 Fund Codes and Year

The plan targets exactly two funds:
- `110020` / 2024 (index slot, previously fallback-blocked)
- `017641` / 2024 (QDII slot, previously fallback-blocked)

This matches the control doc's residual tracking for index/QDII source recovery.

### 3.2 CLI Commands

The plan specifies exactly six bounded commands (lines 142-149):
- `fund-analysis extraction-snapshot` for each fund
- `fund-analysis extraction-score` for each fund
- `fund-analysis quality-gate` for each fund

All commands use only the public `fund-analysis` CLI. No internal Python imports, no `FundDocumentRepository` calls, no PDF/cache access.

### 3.3 Output Paths

All outputs land under `reports/extraction-snapshots/`, `reports/scoring-runs/`, and `reports/quality-gate-runs/` — directories that are git-ignored. Run IDs include the date and fund code for isolation.

**Verdict**: Commands are correctly bounded to public CLI for exactly the two specified funds. ✅

---

## 4. Classification Logic Check

### 4.1 Public Provenance Fields

The plan lists the following classification inputs (lines 63-77):
- `fallback_used`
- `primary_failure_category`
- `fallback_eligibility`
- `source_provenance_status`
- `source_provenance_reason`
- Supporting context: `source_provenance_schema_version`, `source_strategy`, `resolved_source_name`
- Quality output: `quality_gate.json` status

Cross-checking against the implementation in `fund_agent/fund/source_provenance.py` and `fund_agent/fund/extraction_snapshot.py`:

| Plan field | Implementation field | Present in snapshot JSONL |
|---|---|---|
| `fallback_used` | `fallback_used: bool` | ✅ |
| `primary_failure_category` | `primary_failure_category: str \| None` | ✅ |
| `fallback_eligibility` | `fallback_eligibility: str` | ✅ |
| `source_provenance_status` | `source_provenance_status: str` | ✅ |
| `source_provenance_reason` | `source_provenance_reason: str` | ✅ |
| `source_provenance_schema_version` | `source_provenance_schema_version: str` | ✅ |
| `source_strategy` | `source_strategy: str` | ✅ |
| `resolved_source_name` | `resolved_source_name: str` | ✅ |

**Verdict**: All listed fields are real implementation fields present in the public snapshot JSONL. ✅

### 4.2 Prohibition on Downstream Success as Fallback Proof

The plan includes a strict negative rule (lines 114-117):

> Successful extraction, a populated `snapshot.jsonl`, a populated `score.json`, or a non-blocking quality gate is not evidence of fallback eligibility. Fallback eligibility is proved only by public provenance fields showing `fallback_used=true`, an eligible `primary_failure_category`, and `fallback_eligibility="eligible"`.

This directly aligns with:
- `AGENTS.md` hard constraint: "年报来源 fallback 必须显式按失败分类决策"
- `docs/design.md` §6.1: "`schema_drift`, `identity_mismatch`, `integrity_error` 仍必须 fail-closed"
- Control doc line 325: "`fallback_used=true` with missing `primary_failure_category` must classify as `unknown_public_metadata_absent`, never `eligible`"

**Verdict**: The negative rule is correct and sufficient. ✅

### 4.3 Forbidden Scope

The plan's forbidden scope (lines 175-189) covers:
- Source code changes ✅
- Test changes ✅
- Design/control doc changes ✅
- PDF, cache, source-helper, downloader, source adapter, source strategy access ✅
- `FundDocumentRepository` source strategy / fallback semantics changes ✅
- Renderer changes ✅
- FQ0-FQ6 / quality-gate policy changes ✅
- Default `analyze` / `checklist` behavior changes ✅
- Golden, baseline, strict golden, curated fixture, clean denominator promotion ✅
- Host/Agent/dayu runtime work ✅
- Web/search replacement evidence ✅
- Commit, push, PR operations ✅

**Verdict**: Forbidden scope is comprehensive and aligns with the gate's non-goals. ✅

---

## 5. Terminal States Check

The plan defines six terminal states (lines 82-112):

| Terminal state | Covers | Adequate? |
|---|---|---|
| `repository_run_failed` | Command non-zero exit or missing output files | ✅ |
| `provenance_unknown_public_metadata_absent` | Missing provenance fields, `fallback_eligibility="unknown_public_metadata_absent"` | ✅ Covers unknown metadata |
| `provenance_fail_closed` | `primary_failure_category` is `schema_drift`/`identity_mismatch`/`integrity_error`, or `fallback_eligibility="fail_closed"` | ✅ Covers fail-closed |
| `quality_blocked_after_provenance` | Provenance eligible but `quality_gate.json` status = `block` | ✅ Covers quality block after provenance |
| `provenance_eligible_for_next_review` | All of: `fallback_used=true`, eligible `primary_failure_category`, `fallback_eligibility="eligible"`, `source_provenance_status="complete"`, quality gate `pass`/`warn` | ✅ Covers eligible for later review |
| `not_promoted` | Final promotion disposition for every row | ✅ Covers not promoted |

The reviewer's checklist requires terminal states to cover:
1. Unknown metadata → `provenance_unknown_public_metadata_absent` ✅
2. Fail-closed → `provenance_fail_closed` ✅
3. Repository failure → `repository_run_failed` ✅
4. Quality block after provenance → `quality_blocked_after_provenance` ✅
5. Eligible for later review → `provenance_eligible_for_next_review` ✅
6. Not promoted → `not_promoted` ✅

**Verdict**: All required terminal states are covered. ✅

---

## 6. Output Hygiene Check

### 6.1 Tracked Artifact

The plan specifies exactly one tracked summary artifact (line 53):
- `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-20260527.md`

This follows the established `docs/reviews/` naming convention.

### 6.2 Generated Output Reference

The plan correctly identifies generated outputs as references-only (lines 57-59):
- `snapshot.jsonl`, `summary.md`, `errors.jsonl` under snapshot dirs
- `score.json`, `score.md`, `golden_set.json` under score dirs
- `quality_gate.json`, `quality_gate.md` under quality gate dirs

All under `reports/` which is git-ignored.

### 6.3 Evidence Summary Shape

The plan specifies (lines 163-171):
- Startup Packet replay ✅
- Exact command table with exit codes ✅
- Per-fund: output paths, provenance fields, quality gate status, issue count, terminal state, `promotion_disposition=not_promoted` ✅
- Denominator decision table ✅
- Generated-output hygiene note ✅
- Explicit statement that successful extraction was not used as fallback eligibility evidence ✅

**Verdict**: Output hygiene is adequate. ✅

---

## 7. Design Boundary Check

Per `docs/design.md` §12, the plan review must check:

| Check | Result |
|---|---|
| Violates §1.3 non-goals? | No. Evidence classification only, no promotion. ✅ |
| Maintains `UI -> Service -> Host -> Agent` boundary? | Yes. Uses public CLI only, no internal module access. ✅ |
| Production annual report access only via `FundDocumentRepository`? | Yes. Plan does not access PDF/cache/source helpers. ✅ |
| No Host/tool loop/LLM/Evidence Confirm in current deterministic path? | Correct. Pure CLI evidence run. ✅ |
| `pyproject.toml` engineering baseline? | Not affected. No code changes. ✅ |
| License/repo hygiene? | Not affected. No code changes. ✅ |
| Dayu four-layer as rule source? | Yes. No six-layer or three-layer reintroduction. ✅ |
| Success signal verifiable without false acceptance? | Yes. Strict negative rule prevents downstream success from proving eligibility. ✅ |

**Verdict**: All design boundary checks pass. ✅

---

## 8. Consistency With Prior Evidence Chain

The plan's gate objective references two previously fallback-blocked rows:
- `110020` / 2024 — index slot, previously fallback-blocked / source-unknown
- `017641` / 2024 — QDII slot, previously fallback-blocked / source-unknown

Cross-checking with accepted evidence:
- Control doc line 305: "`110020` / index and `017641` / QDII remain fallback-blocked" ✅
- Control doc line 316: same classification in corpus v1 ✅
- Control doc line 324: "Both rows are classified `unrecoverable_safe_path`" ✅
- Control doc line 325: "next safe path is additive public source provenance output" ✅

The plan correctly positions this gate as the post-implementation follow-up to the source provenance implementation, using the newly implemented public provenance fields to re-classify these rows.

**Verdict**: Consistent with prior evidence chain. ✅

---

## 9. Reviewer Matrix Check

The plan's reviewer matrix (lines 128-136) assigns:
- Plan review: AgentMiMo + AgentGLM ✅
- Evidence run: AgentCodex or assigned worker ✅
- Evidence review: AgentMiMo + AgentGLM ✅
- Controller judgment: AgentCodex controller ✅

Each stage has a required artifact path. The `init-agents` tmux protocol is mentioned.

**Verdict**: Reviewer matrix is adequate. ✅

---

## 10. Findings

No blocking findings.

### 10.1 Low / Informational

None. The plan is well-structured and complete.

---

## 11. Conclusion

**PASS**

The plan correctly aligns with the current gate, control doc next entry point, and design boundaries. Commands are bounded to exactly two funds via public CLI. Classification uses only public provenance fields and quality outputs with a strict negative rule against downstream success as fallback proof. All six required terminal states are covered. Output hygiene is adequate with one tracked summary artifact and git-ignored generated outputs. No forbidden scope is introduced. No revision is required before evidence execution.
