# Evidence Confirm Productionization RR-09 Product CLI EC Fail / Quality-gate Residual Disposition Plan

Verdict token:

`RR_09_RESIDUAL_DISPOSITION_PLAN_READY_NOT_READY`

## 1. Goal / Motivation / Success Signal

**Goal**: Disposition two PR-40 post-merge material release residuals before any release claim, producing a code-generation-ready plan that tells the next controller whether RR-09 needs implementation, narrower evidence, quality-gate adjustment, or continued NOT_READY routing.

**Residual 1**: Default product CLI `fund-analysis analyze` emits `evidence_confirm_status=fail` for four of five RR-S2 samples under `policy=warn` — 53 checked facts per sample, 32–39 failed (60–74% fail rate).

**Residual 2**: `017641 / 2024` (QDII) exits 2 with `quality_gate_status=block` before Evidence Confirm summary emission.

**Success signal**: One accepted disposition from the decision tree (section 7) with residual owner assignment and reclassification from "material release blocker" to either "accepted known product behavior," "scoped code fix needed," or "routed to narrower extraction gate."

## 2. Non-goals / Boundaries

- No implementation, review, commit, push, tag, release, or control-doc edit in this artifact.
- No checklist Evidence Confirm support (deferred with owner per RR-S4 `ACCEPT_RR_S4_CHECKLIST_DEFERRAL`).
- No report-body Evidence Confirm rendering (deferred with owner per RR-S6 `ACCEPT_RR_S6_REPORT_BODY_OPTION_A`).
- No provider-backed semantic default-on production switch (deferred per RR-S3 bounded evidence only, release boundary residual routing).
- No source fallback policy change (EID `single_source_only` stays).
- No `FundDocumentRepository` bypass, direct PDF/cache/parser access, provider path expansion.
- No tag/release/readiness claim.
- Keep deterministic V2 authoritative; provider-backed semantic is enhancement only.

## 3. First-principles Judgment and Direct Evidence

### 3.1 The product pipeline ordering — direct code evidence

From `fund_agent/services/fund_analysis_service.py` lines 1198–1217 (`_run_analysis_core`):

```python
# Line 1198: Evidence Confirm runs FIRST
evidence_confirm_summary = await self._run_evidence_confirm_if_enabled(
    structured_data=structured_data,
    policy=_effective_evidence_confirm_policy(resolved_contract, command_source=...),
    force_refresh=request.force_refresh,
)
# Line 1206: Quality gate runs SECOND, consuming EC summary for ECQ projection
quality_gate_result, quality_gate_not_run_reason = _run_quality_gate_if_enabled(
    structured_data=structured_data,
    resolved_contract=resolved_contract,
    command_source=request.command_source,
    evidence_confirm_summary=evidence_confirm_summary,  # ← EC summary feeds quality gate
)
# Lines 1212–1217: If quality gate blocks, raise QualityGateBlockedError
if resolved_contract.quality_gate_policy == "block":
    if quality_gate_result is None:
        _raise_evidence_confirm_block_if_required(evidence_confirm_summary)
        raise QualityGateNotRunBlockedError(...)
    if quality_gate_result.status == GATE_STATUS_BLOCK:
        raise QualityGateBlockedError(quality_gate_result)  # ← EC summary NOT carried
```

**The actual ordering is: Evidence Confirm → Quality Gate → render.**

Key implications:

1. **Evidence Confirm always runs when policy is `warn` or `block`** — it runs before quality gate, independently of quality gate status. The EC summary is computed and passed to quality gate for ECQ issue projection.
2. **Quality gate consumes the EC summary** for ECQ0-ECQ4 projection (`_run_quality_gate_if_enabled` receives `evidence_confirm_summary` parameter at line 1210).
3. **`QualityGateBlockedError` drops the EC summary** — at line 1217, only `quality_gate_result` is passed to the exception constructor (see §3.4 for `QualityGateBlockedError` class definition). The `evidence_confirm_summary` variable is in scope but not attached to the exception.
4. **Evidence Confirm policy defaults to `warn`** for product `analyze` (resolved at `_resolve_analysis_contract`, line ~1590). Under `warn`, `_raise_evidence_confirm_block_if_required` does NOT block — it only raises when policy=`block` AND status=`fail`.

### 3.2 What `evidence_confirm_status=fail` means

Deterministic V2 (`fund_agent/fund/evidence_confirm.py`) evaluates five dimensions per fact:
- `anchor_precision` — can numeric tokens in the fact value be found in the anchor excerpt?
- `source_support` — does the reference have a valid source kind?
- `missing_evidence` — is the fact missing required evidence?
- `proof_boundary` — does the source meet proof-standard requirements?
- `value_match` — does the fact value match the anchored source text?

The RR-S2 **runner** used `build_live_section_smoke_projection` with deliberately section-only anchors, checking only 1 fact per sample. The **product CLI** checks 53 facts per sample using the full `analyze` projection with actual structured extraction anchors.

From RR-S2: `field_correctness_proven=false` for every sample. Anchor precision in the product path depends on extractor output granularity. If the extractor attaches section-level anchors rather than table-cell-level anchors, V2's `anchor_precision` and `value_match` dimensions will fail for most facts — correctly, because a section-level excerpt cannot confirm a specific numeric field value.

**First-principles classification**: The 60–74% fail rate is most likely a **structural consequence of current extractor anchor granularity**, not a V2 scoring defect or a projection bug. V2 is working correctly: it reports `fail` because it genuinely cannot confirm most field values against their anchors. This is the truth — and `warn` is the correct policy for this truth state.

### 3.3 The `fail` under `warn` — hypotheses, not conclusions

Three hypotheses compete for R1-R4 root cause. The plan must route to evidence-first disposition before any branch can claim "intended behavior" for release.

**H1 (structural anchor precision)**: The 60–74% fail rate is a structural consequence of current extractor anchor granularity. If the extractor attaches section-level anchors rather than table/paragraph/cell-level anchors, deterministic V2 cannot confirm specific field values against coarse excerpts. Under this hypothesis, the fail rate tells the truth about current anchor precision, and `warn` is the correct policy to avoid blocking useful reports.

**H2 (V2 scoring false-positive)**: Specific dimension checks (e.g., `value_match` string normalization, `anchor_precision` numeric token extraction) may produce false failures against valid anchors. Under this hypothesis, a narrow V2 scoring fix would reduce fail rates without weakening genuine checks.

**H3 (projection/contract defect)**: The projection fed to Evidence Confirm may include facts that lack corresponding anchors, or anchors that don't reference the correct source location. Under this hypothesis, the fix is in projection assembly (`chapter_facts.py`) or extractor anchor attachment.

**Current evidence does not distinguish H1 from H2 or H3.** The RR-S2 runner used a deliberately reduced smoke projection (1 fact per sample, section-only anchors, `v2_anchor_precision_warn_section_only_smoke`). The product CLI uses the full `analyze` projection (53 facts per sample). The fact-level dimension breakdown for the product path is not available in any accepted artifact.

**H1 is the strongest prior** (consistent with `field_correctness_proven=false`, consistent with `warn` being the accepted default, consistent with the known gap between section-level and field-level anchors), but it is **not fact-level proven**. The plan must require evidence-first disposition: diagnostic confirmation of root cause before accepting any branch for release.

**What is known with certainty**: Under `warn` policy, the system correctly does NOT block report generation. The safe CLI summary reports status without exposing internals. The `warn` default was explicitly accepted by the productionization default-on policy gate. These are code facts, not hypotheses.

### 3.4 Why `017641 / 2024` emits no user-visible EC summary — propagation defect

From RR-S2: `017641 / 2024` exits 2 with `quality_gate_status=block`. No EC summary is emitted in CLI output.

From the pipeline ordering (§3.1), Evidence Confirm **does execute** for `017641 / 2024` — `_run_evidence_confirm_if_enabled()` runs at line 1198, BEFORE quality gate at line 1206. The `evidence_confirm_summary` is computed and passed to `_run_quality_gate_if_enabled()` for ECQ projection. But when quality gate status is `block` and policy is `block`, `QualityGateBlockedError(quality_gate_result)` is raised at line 1217.

`QualityGateBlockedError` (lines 604–630) stores only `quality_gate_result`. It does NOT carry `evidence_confirm_summary`. Compare with `EvidenceConfirmBlockedError` (lines 659–687) which DOES carry `evidence_confirm_summary`.

```python
# QualityGateBlockedError — drops EC summary
class QualityGateBlockedError(ValueError):
    def __init__(self, quality_gate_result: QualityGateResult) -> None:
        self.quality_gate_result = quality_gate_result
        self.policy: QualityGatePolicy = "block"
        # evidence_confirm_summary NOT stored

# EvidenceConfirmBlockedError — carries EC summary (contrast)
class EvidenceConfirmBlockedError(ValueError):
    def __init__(self, evidence_confirm_summary: EvidenceConfirmProductionSummary) -> None:
        self.evidence_confirm_summary = evidence_confirm_summary
        self.policy: EvidenceConfirmProductionPolicy = "block"
```

**The missing user-visible EC summary is an exception-contract propagation defect.** Evidence Confirm runs, computes a summary, and the summary is dropped by `QualityGateBlockedError` rather than being carried through to CLI output. This is NOT a "never ran" problem — it's a "ran but lost" problem.

**The quality gate block itself (exit 2) is a separate concern.** The QDII fund's structured extraction triggers quality gate `block`. That may be correct QDII product behavior (QDII reports have different disclosure standards) or a QDII applicability defect. These two concerns (propagation defect vs block correctness) must be dispositioned separately.

The RR-S2 runner proved the source/PDF pathway works for `017641 / 2024` (runner status `pass`, EID source, fallback disabled/unused). This confirms the repository pathway is intact; the failure is in the product pipeline's exception contract.

### 3.5 Design doc alignment

`docs/design.md` §1.1: "确定性 MVP 主链路...由结构化抽取、确定性分析、模板渲染、程序审计和 quality gate 组成" — quality gate is a first-class gate.

`docs/design.md` §2.2: quality gate evaluates `StructuredFundDataBundle` before rendering. Evidence Confirm is additive, running after extraction in the productionization default-on integration.

`docs/implementation-control.md` Current Truth Guardrails: "默认 product `fund-analysis analyze` 在结构化抽取后运行 repository-bounded Evidence Confirm with `warn` policy."

Current behavior is fully consistent with accepted design and accepted EC-P4 Service/UI/renderer/quality-gate integration.

## 4. Current Residual Inventory

| # | Residual | Source evidence | Current classification | Root cause status |
|---|---|---|---|---|
| R1 | `004393 / 2025` EC `fail` under `warn` (53 checked, 34 failed) | RR-S2 product CLI table | Material release blocker | Not fact-level proven. Competing hypotheses H1/H2/H3 (§3.3). Requires evidence-first root-cause confirmation. |
| R2 | `004194 / 2024` EC `fail` under `warn` (53 checked, 35 failed) | RR-S2 product CLI table | Material release blocker | Same as R1 |
| R3 | `006597 / 2024` EC `fail` under `warn` (53 checked, 32 failed) | RR-S2 product CLI table | Material release blocker | Same as R1 |
| R4 | `110020 / 2024` EC `fail` under `warn` (53 checked, 39 failed) | RR-S2 product CLI table | Material release blocker | Same as R1 |
| R5a | `017641 / 2024` quality gate `block` (exit 2) | RR-S2 product CLI table | Material release blocker | Quality gate QDII block merits root-cause investigation (§3.4) |
| R5b | `017641 / 2024` missing user-visible EC summary on blocked path | RR-S2 product CLI table + code | Material release blocker | `QualityGateBlockedError` drops EC summary; propagation defect (§3.4) |
| R6 | Release/readiness `NOT_READY` | All RR-S1 through RR-S8 | Blocker | Carried until R1-R5 dispositioned |

## 5. Affected Files/Modules (If Implementation Becomes Necessary)

**Evidence Confirm / scoring:**
- `fund_agent/fund/evidence_confirm.py` — V2 deterministic evaluation, dimension scoring
- `fund_agent/fund/evidence_confirm_production.py` — `EvidenceConfirmProductionSummary`
- `fund_agent/fund/evidence_confirm_runner.py` — repository-bounded runner

**Extractor / anchor path:**
- `fund_agent/fund/extraction/extractor.py` — `FundDataExtractor.extract()`
- `fund_agent/fund/processors/` — processor pipeline per fund type, anchor attachment

**Quality gate:**
- `fund_agent/services/quality_gate_service.py` — FQ0-FQ6 rules, QDII applicability
- `fund_agent/services/fund_analysis_service.py` — pipeline ordering, exception propagation

**Tests:**
- `tests/fund/test_evidence_confirm.py` — V1/V2 unit tests
- `tests/services/test_fund_analysis_service.py` — Service integration
- `tests/services/test_quality_gate_service.py` — Quality gate rules

## 6. Current Anchor Granularity Fact (Diagnostic Prerequisite)

Before deciding whether R1-R4 require code fixes, the implementation worker must establish fact-level failure root cause. This is a diagnostic step, not a code change.

### Static diagnostic (no authorization required):

```bash
uv run pytest tests/fund/test_evidence_confirm.py -q --tb=short
```

Confirms V2 scoring is correct for fixture projections. Does NOT explain why production projections fail.

### Live diagnostic (requires explicit user authorization — loads through FundDocumentRepository):

```bash
uv run python -c "
# For one selected sample, dump fact-level dimension results
# Uses FundDocumentRepository only; does NOT read raw PDF/cache/parser/provider
"
```

**Authorization required**: loads annual reports through `FundDocumentRepository` → EID network + PDF processing.

## 7. Explicit Implementation Decision Tree

```
RR-09: Product CLI EC fail + 017641 quality-gate block / blocked-path EC summary loss
│
├─ R1-R4 (EC fail under warn for four samples — 60-74% fail rate)
│  │
│  ├── Branch A: EVIDENCE-FIRST DISPOSITION
│  │   Decision: EC fail under warn is intended behavior. Deterministic V2 works
│  │   correctly for current extractor anchor granularity. warn policy correctly
│  │   allows report generation while honestly reporting that many facts cannot be
│  │   confirmed at field level. The fail rate reflects a structural limitation
│  │   (anchor precision), not a code defect.
│  │   Action: Reclassify R1-R4 from "material release blocker" to "accepted known
│  │   product behavior." Document user-facing semantics.
│  │   Owner: Product owner / controller.
│  │   Release impact: Does NOT independently block release. warn policy + honest
│  │   fail status is the correct and safe default for current anchor precision.
│  │   Requires: Fact-level diagnostic evidence that the dominant failures are
│  │   genuine anchor/projection precision gaps, not V2 false positives or wrong
│  │   source attachment.
│  │
│  ├── Branch B: CODE FIX — NARROWER ROOT-CAUSE EVIDENCE
│  │   Decision: Investigate whether specific dimension/fact-type patterns produce
│  │   false failures. If provable false-positive pattern found, apply narrow fix
│  │   to V2 scoring or projection assembly.
│  │   Scope: evidence_confirm.py + chapter_facts.py projection assembly.
│  │   Must NOT: weaken V2 thresholds, change source policy, bypass repository.
│  │   Release impact: Code fix must be reviewed, tested, committed.
│  │
│  └── Branch C: ROUTE TO NARROWER EXTRACTION GATE
│     Decision: Current anchor granularity is fundamentally insufficient. Route to
│     new work unit that improves extractor anchor precision, then re-evaluate.
│     Release impact: NOT_READY blocked on new work unit completion + re-evidence.
│     This defers release indefinitely.
│
├─ R5a (017641 / 2024 quality-gate/QDII block correctness)
│  │
│  ├── Branch D: QUALITY-GATE/QDII DISPOSITION
│  │   Decision: QDII fund quality-gate block is expected product behavior. Quality
│  │   gate correctly blocks when mandatory structured fields are unavailable for
│  │   QDII annual reports (which have different disclosure standards).
│  │   Action: Reclassify R5a from "material release blocker" to "accepted known
│  │   product limitation for QDII funds."
│  │   Owner: Quality gate owner / QDII product owner / controller.
│  │   Release impact: QDII fund unavailability is a product limitation, not a
│  │   release blocker for non-QDII funds.
│  │   Requires: Static/no-live FQ rule evidence proving the block is the intended
│  │   QDII applicability outcome.
│  │
│  └── Branch E: QUALITY-GATE FIX FOR 017641
│     Decision: Investigate whether the quality-gate block is caused by a
│     QDII-specific scoring defect (e.g., mandatory field rule incorrectly
│     applied to QDII). If defect found, apply narrow fix.
│     Scope: quality_gate_service.py QDII applicability + extractor QDII coverage.
│     Release impact: Fix must be reviewed, tested, committed.
│
├─ R5b (017641 / 2024 blocked-path EC summary propagation)
│  │
│  └── Branch F: BLOCKED-PATH EC SUMMARY PROPAGATION FIX
│      Decision: Evidence Confirm already runs before quality gate and feeds ECQ
│      projection, but `QualityGateBlockedError` carries only `quality_gate_result`.
│      The already-computed safe EC summary is therefore unavailable to the CLI
│      blocked-output handler.
│      Action: Narrow implementation plan to carry optional safe
│      `EvidenceConfirmProductionSummary` through `QualityGateBlockedError` and
│      echo it in CLI blocked output.
│      Must preserve: exit code 2, `quality_gate_status=block`, no report body,
│      no excerpts/paths/provider payloads, and no change to quality-gate decision.
│      Release impact: Requires implementation, focused tests, review, and
│      accepted evidence before R5b can be closed.
│
└── Default: CONTINUED NOT_READY
   If no branch is chosen or diagnostic is inconclusive, record explicit
   NOT_READY with reason. No code change, no release claim.
```

### Recommended sequencing:

- **R1-R4 first**: Run fact-level diagnostic evidence before accepting Branch A. V2 likely reports real anchor/projection precision gaps, but release disposition must not depend on prior alone.
- **R5a separately**: Decide whether the QDII quality-gate block is correct from static/no-live FQ rule evidence. Do not change quality gate unless direct rule evidence proves a QDII applicability defect.
- **R5b separately**: Treat missing user-visible EC summary on quality-gate-blocked output as a narrow propagation/exception-contract residual. If confirmed, plan a focused implementation that carries the already-computed safe summary through the blocked path.
- **No combined zero-code closeout**: RR-09 cannot close by claiming EC did not execute or by merging R5a/R5b into one QDII limitation. Release/readiness stays `NOT_READY` until the selected branch evidence and any required implementation are accepted.

## 8. Small Implementation Slices (Only If Branch B, E, or F Is Chosen)

### Branch B slices (narrower root-cause evidence for EC fail):

**Slice B-1: Diagnostic — fact-level dimension failure distribution**
- Allowed files: diagnostic script only (read-only access to `FundDocumentRepository`)
- Objective: For one sample, dump each fact's dimension-level pass/fail with anchor context.
- Prerequisites: User authorizes one repository-bounded live load.
- Expected output: CSV with `fact_id, dimension, status, anchor_section_id, anchor_excerpt_preview`.
- Stop condition: Pattern identified OR confirmed all failures are genuine given current anchors.

**Slice B-2: Targeted V2 scoring fix**
- Allowed files: `fund_agent/fund/evidence_confirm.py` (scoring logic only)
- Objective: Fix specific proven false-positive pattern from B-1.
- Tests: Add no-live regression test reproducing the false-positive, then verify fix.
- Command: `uv run pytest tests/fund/test_evidence_confirm.py -q --tb=short`

**Slice B-3: Re-evidence with fix (requires live authorization)**
- Command: `uv run fund-analysis analyze <code> --report-year <year> --valuation-state unavailable --force-refresh`
- Assertion: Fixed facts now pass; genuinely unconfirmable facts still fail.

### Branch E slices (quality-gate fix for 017641):

**Slice E-1: Diagnostic — 017641 quality gate failure root cause**
- Allowed files: read-only access to `quality_gate_service.py`, `extractor.py`
- Objective: Identify which FQ rule triggers `block` and whether it's correct for QDII.
- Prerequisites: User authorizes one repository-bounded live extraction for `017641 / 2024`.

**Slice E-2: Narrow quality-gate applicability fix**
- Allowed files: `fund_agent/services/quality_gate_service.py` (QDII applicability only)
- Objective: Fix QDII-specific incorrect rule application.
- Tests: `uv run pytest tests/services/test_quality_gate_service.py -q --tb=short`

### Branch F slices (blocked-path EC summary propagation):

**Slice F-1: Exception contract and CLI blocked-output propagation**
- Allowed files: `fund_agent/services/fund_analysis_service.py`, `fund_agent/ui/cli.py`, `tests/services/test_fund_analysis_service.py`, `tests/ui/test_cli.py`
- Objective: Carry optional safe `EvidenceConfirmProductionSummary` on `QualityGateBlockedError` and echo the same compact Evidence Confirm summary in the CLI quality-gate-blocked path.
- Invariants: Preserve exit code 2, preserve `quality_gate_status=block`, suppress report body, do not expose excerpts, file paths, PDF/cache/source internals, provider payloads, or raw fact-level diagnostics.
- Tests:
  - Service regression: quality-gate block can carry the already-computed Evidence Confirm summary.
  - CLI regression: blocked output includes quality gate summary plus safe Evidence Confirm summary.
  - CLI negative regression: absent summary preserves current quality-gate-only blocked output.
- Command: `uv run pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q --tb=short`

## 9. Exact Allowed Future Commands

### Commands requiring explicit live/PDF/provider authorization:

| Command | Requires authorization for | Blocking if not authorized? |
|---|---|---|
| `uv run fund-analysis analyze <code> --report-year <year> --valuation-state unavailable --force-refresh` | Repository-bounded EID + PDF through `FundDocumentRepository` | Yes — diagnostic cannot run |
| Any Python script loading through `FundDocumentRepository` | Same as above | Yes |
| Provider/LLM commands | Provider network access | Yes — and cannot override deterministic V2 |

### Commands that do NOT require authorization (no-live/static only):

```bash
# Test baselines
uv run pytest tests/fund/test_evidence_confirm.py -q --tb=short
uv run pytest tests/services/test_fund_analysis_service.py -q --tb=short
uv run pytest tests/services/test_quality_gate_service.py -q --tb=short

# Static checks
uv run ruff check fund_agent/
git diff --check

# Code search (read-only)
rg -n "evidence_confirm_status\|QualityGateBlockedError\|017641\|_raise_evidence_confirm_block" fund_agent/
rg -n "RR-09\|RR_S2\|evidence_confirm.*fail" docs/reviews/evidence-confirm-productionization-release-boundary-residual-routing-20260623.md
```

## 10. Tests/Validation Matrix

### For Branch A and D (evidence-first/static disposition):

| # | Check | Command | Expected assertion |
|---|---|---|---|
| V1 | V2 no-live tests | `uv run pytest tests/fund/test_evidence_confirm.py -q --tb=short` | All pass (current baseline) |
| V2 | Service integration | `uv run pytest tests/services/test_fund_analysis_service.py -q --tb=short` | All pass |
| V3 | warn policy non-blocking | Code inspection `fund_agent/services/fund_analysis_service.py:_raise_evidence_confirm_block_if_required` | Not called when policy=warn |
| V4 | Safe summary in stderr | Code inspection of CLI entry | Safe summary lines; no paths/URLs/payloads |
| V5 | Artifact self-consistency | `rg "RR_09_RESIDUAL_DISPOSITION_PLAN_READY_NOT_READY" docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md` | Verdict token present |
| V6 | Reference integrity | `rg "RR-S2\|RR-S4\|RR-S6\|release-boundary-residual-routing\|design.md\|implementation-control.md" docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md` | All referenced artifacts and docs cited |
| V7 | Whitespace | `git diff --check -- docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md` | No errors |

### For Branch B (code fix):

| # | Check | Command | Expected assertion |
|---|---|---|---|
| V8 | Pre-fix baseline | `uv run pytest tests/fund/test_evidence_confirm.py -q --tb=short` | All pass |
| V9 | New regression (red) | `uv run pytest tests/fund/test_evidence_confirm.py::<new> -q` | Fails (reproduces false-positive) |
| V10 | Post-fix (green) | `uv run pytest tests/fund/test_evidence_confirm.py -q --tb=short` | All pass |
| V11 | Lint | `uv run ruff check fund_agent/fund/evidence_confirm.py` | No errors |

### For Branch E (quality-gate fix):

| # | Check | Command | Expected assertion |
|---|---|---|---|
| V12 | Pre-fix quality gate | `uv run pytest tests/services/test_quality_gate_service.py -q --tb=short` | All pass |
| V13 | Post-fix | Same command | All pass including QDII-specific |
| V14 | Non-QDII unaffected | Same command | Non-QDII behavior unchanged |

### For Branch F (blocked-path EC summary propagation fix):

| # | Check | Command | Expected assertion |
|---|---|---|---|
| V15 | Service blocked exception contract | `uv run pytest tests/services/test_fund_analysis_service.py -q --tb=short` | `QualityGateBlockedError` can carry optional safe EC summary without changing quality-gate status |
| V16 | CLI blocked output | `uv run pytest tests/ui/test_cli.py -q --tb=short` | quality-gate blocked output includes safe EC summary when present, preserves exit 2 and no report body |
| V17 | Safe absent-summary fallback | `uv run pytest tests/ui/test_cli.py -q --tb=short` | existing quality-gate-only blocked output remains unchanged when EC summary is absent |

## 11. Docs/Control Sync Decision

This planning artifact must NOT edit control docs. Future sync (after RR-09 disposition is accepted) must:

- Update `docs/current-startup-packet.md` §2 to record RR-09 disposition verdict.
- Update `docs/implementation-control.md` "Next entry point" to post-RR-09 gate.
- If Branch A and/or D are accepted: reclassify only the covered residuals (`R1-R4` and/or `R5a`) from "material release blocker" to the accepted disposition stated by the evidence.
- If Branch B or E: create implementation artifacts under `docs/reviews/`.
- If Branch F: record the accepted blocked-path propagation implementation evidence and preserve the separate R5a quality-gate/QDII disposition.
- Preserve `NOT_READY` unless a separate release authorization gate explicitly changes it.
- Not rewrite PR-40 merge history or claim tag/release.

## 12. Residual Risks and Owners

| Risk | Class | Owner | Destination |
|---|---|---|---|
| R1-R4 accepted as known behavior (Branch A) | `accepted` | Product owner / controller | Final release disposition gate |
| R1-R4 require code fix (Branch B) | `needs_implementation` | Evidence Confirm V2 owner | RR-09 implementation gate |
| R1-R4 require extraction work (Branch C) | `routed_to_new_work_unit` | Extractor/processor owner | New extraction precision work unit |
| R5a accepted as QDII limitation (Branch D) | `accepted` | Quality gate / QDII owner | Final release disposition gate |
| R5a requires quality-gate fix (Branch E) | `needs_implementation` | Quality gate owner | RR-09 implementation gate |
| R5b blocked-path EC summary propagation fix (Branch F) | `needs_implementation` | Service/UI owner | RR-09 implementation gate |
| Diagnostic may reveal deeper systemic gap | `needs-more-evidence` | Controller | If diagnostic reveals systemic gap, escalate to Branch C |
| 60-74% fail rate accepted without diagnostic confirmation of root cause | `accepted_with_residual_uncertainty` | Evidence Confirm owner | First-principles classification is strong but not live-diagnostic-proven; acceptable for planning, not for release proof |
| Release/readiness remains `NOT_READY` throughout RR-09 | `tracked` | Controller | Carried to next gate |
| Checklist, report-body, provider-backed defaults | `deferred_with_owner` | Respective owners | Separate future gates |
| Additional fund samples beyond the five RR-S2 samples | `uncovered` | Controller | Separate expansion gate |

## 13. Completion Report Format

```text
artifact path: docs/reviews/evidence-confirm-productionization-rr-09-product-cli-ec-fail-quality-gate-residual-plan-20260623.md
verdict token: RR_09_RESIDUAL_DISPOSITION_PLAN_READY_NOT_READY
checks:
  V1: <result>
  V2: <result>
  V3: <result>
  V4: <result>
  V5: <result>
  V6: <result>
  V7: <result>
residuals:
  R1-R4: <Branch A/B/C decision>
  R5a: <Branch D/E decision>
  R5b: <Branch F decision or explicit deferral owner>
  R6: NOT_READY carried forward
```

## 14. Why This Plan Is Not Over-designed

- The plan does not propose changing the Evidence Confirm engine, source policy, or quality gate semantics. It starts from the hypothesis that the system is working correctly and the residuals reflect genuine structural limitations, not defects.
- The decision tree has exactly six branches, each mapping to one concrete action. There is no "design a new Evidence Confirm dimension," "build an anchor enrichment pipeline," or "refactor the quality gate framework."
- Implementation slices (B-1/B-2/B-3, E-1/E-2, F-1) are deliberately narrow: diagnostic-only first where root cause is unproven, then minimal targeted fix constrained to the affected modules.
- The plan no longer depends on a combined zero-code A+D closeout. It separates R5a quality-gate correctness from R5b blocked-path EC summary propagation.
- No new abstraction, module, contract, CLI flag, or config key is proposed.
- The plan explicitly lists which commands require user authorization and which don't, preventing accidental live/PDF/provider access.
- The plan honestly flags that the first-principles classification (Branch A) is not live-diagnostic-proven — it's a strong inference from accepted evidence, not a proof. This is acceptable for planning but must be acknowledged as residual uncertainty.

Completion token: `RR_09_RESIDUAL_DISPOSITION_PLAN_READY_NOT_READY`
