# EC-P4 Service/UI/Renderer/Quality-Gate Integration Plan Review

> Reviewer: AgentMiMo (planreview)
> Date: 2026-06-22 21:21 Asia/Shanghai
> Gate: plan review
> Classification: heavy
> Reviewed target: `docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md`

---

## Verdict

**PASS_WITH_FINDINGS**

The plan is code-generation-ready with minor refinements. No AGENTS.md boundary violations, no provider-backed semantic default, no release/readiness overclaim. Seven findings, four medium severity.

---

## Summary

The plan correctly resolves all five goal-confirmation open questions, defines six small slices with explicit allowed files and stop conditions, and preserves `NOT_READY`. The ECQ taxonomy is cleanly separated from FQ rules. Semantic entailment remains no-live injected-client. The renderer non-rendering decision is deliberate and well-reasoned.

Main weaknesses: (1) internal state-machine contradiction on `policy="off"` summary behavior; (2) missing runner-exception handling in the main state machine; (3) ambiguous checklist developer-override support; (4) test validation command gap.

---

## Findings

### F-01 | Medium | State machine / Section "State machine" step 3

**Issue**: Internal contradiction on `policy="off"` behavior. Step 3 says "create `not_run` summary only if needed for quality-gate/CLI reporting; otherwise leave result field `None`." But step 3 also says "If Evidence Confirm policy is `off`, do not call runner." Meanwhile Slice 1 (line 327) requires `ECQ0/info` when "summary absent or status `not_run`", which needs a summary object. If the summary is `None`, quality gate integration cannot emit `ECQ0`.

**Why it matters**: Implementation will be ambiguous — should Slice 1's `_evidence_confirm_quality_gate_issues()` handle `summary=None` as `ECQ0/not_run`, or must Service always produce a summary object? The goal confirmation (line 30) says current production path has no EC result field, implying `None` is the default absence. If `None` means `not_run`, the quality gate helper must special-case it. If a summary must always exist, the state machine step 3 wording is wrong.

**Required fix**: Clarify one of two consistent positions:
- (A) `summary=None` means "EC not requested"; quality gate helper emits `ECQ0/info` with `reason="not_requested"` when summary is `None`. Service does not allocate a summary for `policy="off"`.
- (B) Service always creates a summary (either from runner result or `not_run` with reason); result field is never `None` when quality gate runs.

Option (A) is preferred because it preserves the current "no EC field" default for product mode.

**Suggested owner**: Plan author.

### F-02 | Medium | State machine / not in Section "State machine"

**Issue**: The main state machine (Section "State machine") does not describe runner-exception handling. Slice 2 (line 376) says "Runner exceptions must be converted to fail summary; if policy block then block, if warn then warn summary." This is an important fail-closed behavior but is only documented in the Slice 2 section, not in the canonical state machine.

**Why it matters**: The state machine is the authoritative contract. If runner exception handling is only in a slice description, an implementer following the state machine alone would miss the fail-closed conversion. An unhandled async exception from the injected runner could propagate as an unstructured `RuntimeError` to CLI.

**Required fix**: Add a step between current steps 4 and 5 in the state machine: "If the runner raises, convert to fail-closed `EvidenceConfirmProductionSummary` with `status="fail"`, `not_run_reason="runner_exception:<class_name>"`; if policy is `block`, raise `EvidenceConfirmBlockedError`; if policy is `warn`, continue with the fail summary."

**Suggested owner**: Plan author.

### F-03 | Medium | Section "CLI public interface" / checklist coverage

**Issue**: Slice 3 says "Add matching support to `checklist` if the current checklist command can safely construct developer overrides; otherwise explicitly limit to `analyze` and add a failing-plan-review note for checklist coverage. Preferred: support both commands with identical validation." The current `checklist` method (line 719 of `fund_analysis_service.py`) passes the request directly to `_run_analysis_core()` without accessing `developer_overrides`. The plan does not resolve whether checklist will actually support `--evidence-confirm-policy` in the first implementation pass.

**Why it matters**: If checklist support is deferred, tests must explicitly prove the flag is rejected or ignored for checklist. If checklist is supported, the plan must specify how checklist constructs developer overrides (the current checklist path does not validate or reject developer overrides — it just passes the request through). Leaving this ambiguous risks an implementer either skipping checklist tests or inventing an ad-hoc override construction.

**Required fix**: Make an explicit decision:
- (A) Slice 3 includes checklist with `--evidence-confirm-policy`, requiring a new `--mode developer_override` path for checklist (or reusing the analyze path). Add test: `checklist --mode developer_override --evidence-confirm-policy warn` works.
- (B) Slice 3 is analyze-only; add a stop condition: "Stop if checklist requires developer override surface not yet implemented." Document checklist EC as a deferred slice.

Option (B) is safer given the current codebase; option (A) is preferred if the implementation can reuse the analyze override path.

**Suggested owner**: Plan author / Slice 3 implementer.

### F-04 | Medium | Section "Tests / Validation Commands"

**Issue**: The validation commands (line 582-586) do not include `tests/fund/test_evidence_confirm_production.py` in the pytest invocation. Slice 1 allowed files (line 286) list `tests/fund/test_evidence_confirm_production.py` as a test module. The `git diff --check` command does include it, but the actual test run does not.

**Why it matters**: If Slice 1 creates `test_evidence_confirm_production.py`, the validation commands must run it. Omitting it means the completion signal "Focused Fund tests pass" could be satisfied without running the new summary-type tests.

**Required fix**: Add `tests/fund/test_evidence_confirm_production.py` to the first pytest command, or clarify that it is a subset of `tests/fund/test_evidence_confirm_sources.py`.

**Suggested owner**: Plan author.

### F-05 | Low | Section "Contract / Schema / State-Machine" / EvidenceConfirmProductionSummary

**Issue**: The `not_run_reason: str | None` field only documents `"policy=off"` as a possible value. Other reasons exist or may arise: runner exception, missing projection, repository initialization failure, invalid request. The plan does not enumerate these.

**Why it matters**: Implementers may invent inconsistent reason strings. Quality gate `ECQ0` message invariant requires `reason=<not_run_reason>`, so reason string consistency matters for machine-readable issue output.

**Required fix**: Either enumerate a closed set of `not_run_reason` values (e.g., `Literal["policy_off", "runner_exception", "invalid_request", ...]`), or document that the field is free-form but must be stable across runs for the same failure mode.

**Suggested owner**: Plan author.

### F-06 | Low | Section "Implementation Decisions" / Duplicated repository load

**Issue**: The plan acknowledges "Duplicated repository load may be inefficient under opt-in EC" as a residual (line 631). The state machine step 4 calls the runner with `force_refresh`, which triggers `FundDocumentRepository.load_annual_report()`. If the extractor in step 2 already loaded the same report, this is a redundant I/O operation.

**Why it matters**: Under `evidence_confirm_policy="block"`, every `analyze` call would load the annual report twice. For opt-in developer mode this is acceptable, but the plan should document whether the runner should accept an already-loaded `ParsedAnnualReport` to avoid the duplicate. The current `EvidenceConfirmRepositoryRunRequest` does not have a `parsed_report` field (unlike `EvidenceConfirmReferenceBuildRequest`), so the runner always loads from repository.

**Required fix**: Accept for opt-in first slice. Document in Slice 2 that the runner always loads from repository and that optimization (passing already-loaded report) belongs to a future performance gate. Alternatively, add an optional `parsed_report` field to `EvidenceConfirmRepositoryRunRequest` for pre-loaded cases.

**Suggested owner**: Fund documents owner / Slice 2 implementer.

### F-07 | Low | Section "Contract / Schema" / EvidenceConfirmProductionSummary status field

**Issue**: The `status: EvidenceConfirmProductionStatus` field uses `Literal["pass", "warn", "fail", "not_run"]`. The invariants say "deterministic_status='fail' implies status='fail'" and "deterministic_status='warn' implies status='warn'". But the relationship between `pathway_status` and `status` is not specified. Can `pathway_status="fail"` with `deterministic_status="not_applicable"` produce `status="fail"`?

**Why it matters**: The `status` field is what CLI and quality gate consume. If the mapping from sub-statuses to aggregate `status` is underspecified, implementers may produce inconsistent aggregates.

**Required fix**: Add an invariant: "status is derived from the worst of pathway_status and deterministic_status (and semantic_status in later slices), with fail > warn > pass > not_run." Or specify that `status` is computed by `summary_from_repository_result()` using a defined precedence.

**Suggested owner**: Plan author.

---

## Open Questions

1. Should `EvidenceConfirmProductionSummary` include a `source_provenance` safe summary (source, selected_source, fallback_used, metadata_admitted) for CLI display? The current plan omits it, but the goal confirmation mentions "V2 status and repository/pathway status are visible."

2. The `ECQ*` issue ID format is `evidence-confirm:{fund_code}:{report_year}:{rule_code}:{reason}`. Should this include a timestamp or run id for deduplication across multiple runs?

3. Slice 5 says "Accept an optional EvidenceSemanticResult only from injected test/future caller path." Should the production summary type reserve semantic fields now (which it does via `semantic_status`), or should Slice 1's summary type omit them entirely and add them in Slice 5?

---

## Residual Risks

| Risk | Severity | Disposition |
|---|---|---|
| Default-on policy would trigger repository/PDF work on every analyze call | High | Deferred to default-decision gate; plan correctly chooses opt-in |
| EC-P2 single live sample does not prove general source/PDF correctness | Medium | Deferred to readiness matrix gate; plan correctly does not claim |
| Semantic provider quality is unproven | Medium | Future provider-backed semantic gate; plan correctly defers |
| Renderer section wording could confuse audit metadata with investment conclusion | Low | EC-P4 non-rendering; plan correctly defers |
| ECQ taxonomy may need calibration after implementation evidence | Low | Start additive and provisional |
| Duplicated repository load under opt-in EC | Low | Accept for opt-in; optimize after evidence |
| Existing untracked workspace residue | Low | Out of scope for EC-P4 |

---

## Required Follow-up Gate

No new gate required beyond what the plan already defines. The six slices, their stop conditions, and the docs-sync slice are sufficient. Implementation should proceed through the plan's slice order.

If finding F-03 resolves to option (B) (checklist deferred), a follow-up checklist-EC slice gate will be needed before claiming full CLI coverage.
