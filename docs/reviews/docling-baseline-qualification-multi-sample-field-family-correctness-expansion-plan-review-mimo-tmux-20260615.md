# Docling Multi-sample Field-family Correctness Expansion Plan Review (MiMo) - 2026-06-15

Gate: `Docling Multi-sample Field-family Correctness Expansion Plan Review Gate`
Role: AgentMiMo review worker
Release/readiness: `NOT_READY`

## 1. Scope

Review of `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md` for:

- Boundary language preserves `NOT_READY`, candidate-only status, `field_correctness_status=not_proven`, no source truth, no full correctness and no parser replacement
- S4/S5/S6 use existing accepted/local candidate artifacts only and do not use untracked residue as proof
- EID HTML remains blocked/deferred; raw XML/taxonomy claims are absent
- Evidence gate cannot mutate `FundDocumentRepository`, parser, source policy, `EvidenceAnchor`, Service/Host/UI/renderer/quality gate, LLM route, tests or runtime
- Acceptance thresholds do not overgeneralize S1 or pdfplumber comparator outcomes
- Plan can be handed to an evidence worker without inventing source ownership or schema

## 2. Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md` | Plan under review |
| `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-controller-judgment-20260615.md` | Accepted pilot controller judgment |
| `docs/reviews/docling-baseline-qualification-review-provenance-remediation-controller-judgment-20260615.md` | Provenance remediation controller judgment |
| `docs/current-startup-packet.md` | Current startup packet |
| `docs/implementation-control.md` | Control truth |
| `AGENTS.md` | Rule truth source |

## 3. Findings

### Finding F01: "Reviewed" definition ambiguity for blocked families (Severity: low)

**Section:** Section 8, per-sample threshold

**Observation:** Per-sample threshold `pass` requires "at least 4 applicable families are reviewed and all applicable family results are `pass` or accepted `not_applicable`; no family `fail`; no more than 1 family `blocked`." The word "reviewed" is not explicitly defined in relation to `blocked` families. If `blocked` counts as "reviewed", a sample could pass with 3 `pass` + 1 `not_applicable` + 1 `blocked` + 1 `blocked` (but the second `blocked` would fail the "no more than 1 blocked" rule). If `blocked` does not count as "reviewed", a sample with 4 `pass` + 2 `blocked` would have "6 reviewed" which satisfies the threshold. The ambiguity is minor because the "no more than 1 family `blocked`" clause constrains the outcome regardless, but explicit definition would prevent evidence-worker interpretation drift.

**Risk:** Low. The blocking constraint on `blocked` families provides sufficient guardrail.

**Required fix:** None. Suggest the evidence worker define its "reviewed" interpretation in the Markdown evidence summary for traceability.

### Finding F02: S4/S5/S6 reference availability is load-dependent (Severity: low)

**Section:** Section 3, Sample Matrix Design; Section 9, step 7

**Observation:** S4/S5/S6 are marked "Required if reference load is available without live." Step 7 says: "If this would require live/network acquisition not already authorized, mark that sample `blocked_reference_unavailable` and do not proceed with fact review for that sample." This correctly handles the case where the annual report is not in the local repository cache. However, the plan does not specify how to determine whether the repository load would require live access before attempting it. The `FundDocumentRepository.load_annual_report()` call itself may trigger network access if the cache is cold. The evidence worker must verify cache state or accept the repository's fail-closed behavior.

**Risk:** Low. The `blocked_reference_unavailable` stop condition and the per-sample `blocked` verdict handle this correctly. The evidence worker should use `force_refresh=False` (as in the S1 pilot) and accept the repository's cached-state response.

**Required fix:** None. The evidence worker should document the repository load attempt result in the `samples[]` `repository_load` field.

### Finding F03: `partial_match` for `product_contract_profile` long text (Severity: low)

**Section:** Section 4 and Section 8

**Observation:** `product_contract_profile` allows `partial_match` for long text "only when the reference excerpt confirms the same clause without omitted contradicting text." Per-family verdict `partial` is "only allowed for `product_contract_profile` long text when every partial fact has bounded excerpts and no contradiction." The term "bounded excerpts" is not formally defined. Different evidence workers may interpret the length or specificity of a "bounded excerpt" differently.

**Risk:** Low. The constraint "no omitted contradicting text" is the stronger guardrail. "Bounded excerpts" adds a secondary quality bar that is unlikely to be misinterpreted in practice.

**Required fix:** None. The evidence worker should include the exact excerpt comparison in the fact's `review_note` field.

## 4. Required Amendments

None. All findings are low severity with no blocking impact on evidence execution. The plan is sufficient for handoff to an evidence worker.

## 5. Deferred Risks

| Risk | Status | Next handling |
| --- | --- | --- |
| S4/S5/S6 may all be `blocked_reference_unavailable` if repository cache is cold for those samples. | deferred risk | Evidence gate will produce `blocked_not_ready` verdict; controller decides whether to authorize a bounded live acquisition gate. |
| `not_applicable` requires same-source annual-report review, which itself requires the reference to be loaded. | accepted design | If reference loads but a family is genuinely absent, the evidence worker records `not_applicable` with `family_applicability_reason`. If reference cannot load, the sample is `blocked_reference_unavailable`. The two-level check is correct. |
| Fact count limit (5 per family, 90 total) may not capture all error modes for a given sample. | accepted residual | Broader coverage is a future gate concern; current plan is a bounded expansion pilot. |

## 6. Verdict

`PASS_READY_FOR_EVIDENCE_GATE_NOT_READY`

The plan correctly preserves `NOT_READY` and candidate-only status throughout. Boundary language is consistent across goal, schema, thresholds, stop conditions and next gates. S4/S5/S6 use only existing accepted/local candidate artifacts. EID HTML remains blocked/deferred. The evidence gate is explicitly prohibited from mutating repository, parser, source policy, `EvidenceAnchor`, Service/Host/UI/renderer/quality gate, LLM route, tests or runtime. Acceptance thresholds do not overgeneralize S1 or pdfplumber comparator outcomes. The plan provides sufficient schema, workflow and completion-report format for an evidence worker to execute without inventing source ownership or schema.

No required amendments. The plan is ready for evidence gate handoff.
