# Docling EvidenceAnchor Mapping Evidence Review (AgentMiMo) - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Evidence Gate`
Role: AgentMiMo evidence reviewer
Release/readiness: `NOT_READY`

## 1. Scope

Review `docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md` against binding constraints:

- evidence artifact 是否没有夸大 Docling baseline/source-truth/readiness
- control/startup 当前入口是否和 evidence gate 一致
- S1 current envelope vs S1 full JSON schema residual 是否表达清楚
- table/cell zero-yield 是否被清楚转成 next gate，不是静默通过
- no-live boundary 是否完整，未触碰 Service/Host/UI/renderer/quality gate

## 2. Validation Commands

| Command | Result |
| --- | --- |
| `git diff -- docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md docs/current-startup-packet.md docs/implementation-control.md` | no diff (clean) |
| `uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q` | `12 passed in 0.45s` |

## 3. Finding Matrix

### F1: Baseline/Source-truth/Readiness Claim Check

**Status: PASS_NO_FINDING**

Evidence artifact Section 7 explicitly lists what this evidence does NOT support: source truth, full field correctness, table/cell production anchor readiness, Docling baseline promotion, production parser replacement, repository/parser/Service/Host/UI/renderer/quality-gate behavior change, readiness/release/PR state. Section 9 verdict is `ACCEPT_PARTIAL_HEADING_ONLY_MAPPING_EVIDENCE_NOT_READY`. Every mapped output retains `candidate_only=True`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"` by construction. No claim overstates.

### F2: Control/Startup Entry Consistency

**Status: PASS_NO_FINDING**

- `docs/implementation-control.md` line 47: active gate = `Docling EvidenceAnchor Mapping Evidence Gate`
- `docs/current-startup-packet.md` line 23: current active gate = `Docling EvidenceAnchor Mapping Evidence Gate`
- Evidence artifact gate name = `Docling EvidenceAnchor Mapping Evidence Gate`

All three are consistent.

### F3: S1 Current Envelope vs S1 Full JSON Schema Residual

**Status: PASS_NO_FINDING**

Evidence artifact Section 2 clearly states:
- S1 full JSON input path exists but `project_candidate_representation()` rejects it with `ValueError: unsupported candidate representation schema_version`
- S1 current envelope is used for direct mapping
- S1 full JSON is recorded as blocked for this mapping gate

Section 8 residual #2 explicitly flags: "S1 full JSON is not a current candidate envelope schema" with recommended next handling: decide whether to regenerate/export full S1 as `candidate_annual_report_representation.v1` or keep current-envelope-only mapping evidence. The distinction is clear and not conflated.

### F4: Table/Cell Zero-yield Disposition

**Status: FINDING - NON_BLOCKING**

Evidence artifact Section 3 mapping result matrix shows:
- Total direct mapped: `102` (all `heading` type)
- Total blocked: `23473`
- Mapped types: `heading` only
- Table/cell yield: effectively zero

Section 8 residual #1 explicitly states: "Table/cell mapping yield is effectively zero on accepted real artifacts" with recommended next handling `Docling EvidenceAnchor Mapping Section-context Enrichment Planning Gate`.

**Finding**: The zero-yield is correctly surfaced as a residual with explicit next gate, not silently passed through. However, the **severity** of the zero-yield could be more explicitly quantified in the evidence body. The mapping yield ratio (102/23575 = 0.43%) is a critical signal that the current mapping helper cannot produce production-useful anchors from real artifacts without section-context enrichment. The evidence records the fact but does not explicitly flag this as the primary blocking constraint for any downstream anchor-consuming design. This is a clarity improvement, not a correctness issue.

**Disposition**: ACCEPTED_AS_CLARITY_RESIDUAL; does not block this gate.

### F5: No-live Boundary Completeness

**Status: PASS_NO_FINDING**

Evidence artifact Section 1 states the gate did not run:
- Docling conversion
- live/network/EID/FDR/PDF/source acquisition
- provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands

Section 1 also states it did not change:
- code, source policy, `FundDocumentRepository`, parser behavior, production `EvidenceAnchor` schema, Service, Host, UI, renderer or quality gate behavior

Section 6 validation commands are all local: `git status`, `git diff --check`, `python -m json.tool`, inline Python mapping dry-run. No network, no production path, no external service call. Boundary is complete.

### F6: Dominant Failure Mode Clarity

**Status: FINDING - NON_BLOCKING**

Evidence artifact Section 5 identifies the dominant failure mode as "section-context shape mismatch" and Section 8 residual #3 notes "real headings often use numeric `2.1` etc." The mapping helper requires explicit `§` tokens or closed keyword families for section context.

**Finding**: The evidence does not quantify the ratio of `missing_section_context` to `unstable_section_context` across samples in a summary form. The per-sample numbers are visible in the matrix (e.g., S1: 4270 missing vs 3 unstable), but a consolidated view would strengthen the signal that this is overwhelmingly a missing-context problem (not an unstable-context problem). This is a presentation improvement, not a data gap.

**Disposition**: ACCEPTED_AS_CLARITY_RESIDUAL; does not block this gate.

### F7: Startup Packet Accuracy

**Status: PASS_NO_FINDING**

`docs/current-startup-packet.md` line 25 states: "Implementation judgment ... accepted `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` and `tests/fund/documents/test_docling_evidence_anchor_mapping.py`: mapping tests `12 passed`, adjacent candidate tests `24 passed`, ruff passed, and coverage for `evidence_anchor_mapping.py` is `87%`."

Test run confirms `12 passed` matches. The startup packet accurately reflects the current state and does not overstate mapping evidence.

## 4. Cross-check: Evidence vs Controller Judgment

The no-live implementation controller judgment (`docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-controller-judgment-20260616.md`) recommended the next gate as:

> run no-live candidate mapping against accepted Docling candidate artifacts; record mapped/blocked anchor candidate counts and representative locator samples; preserve candidate-only and NOT_READY

The evidence artifact does exactly this: runs mapping against S1/S4/S5/S6, records counts (102 mapped / 23473 blocked), records representative samples (Section 4 mapped, Section 5 blocked), and preserves NOT_READY. Scope alignment is exact.

## 5. Residual Summary

| Finding | Severity | Disposition |
| --- | --- | --- |
| F4: zero-yield severity not explicitly quantified as primary blocking constraint | non-blocking | ACCEPTED_AS_CLARITY_RESIDUAL |
| F6: missing vs unstable context ratio not consolidated | non-blocking | ACCEPTED_AS_CLARITY_RESIDUAL |

No blocking findings.

## 6. Verdict

```text
VERDICT: PASS_WITH_FINDINGS_NOT_READY
```

Rationale: The evidence artifact is factually correct, does not overstate Docling baseline/source-truth/readiness, maintains complete no-live boundary, correctly surfaces table/cell zero-yield as a residual with explicit next gate, and is consistent with control/startup truth. Two non-blocking clarity improvements are noted but do not affect the validity of the evidence or gate decision.
