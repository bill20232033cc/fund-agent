# DS Review — 004393 / 2025 Same-year Reviewed Golden Content Plan

Date: 2026-06-13

Gate: `004393 / 2025 Same-year Reviewed Golden Content Planning Gate`

Reviewer: AgentDS (adversarial plan review)

Verdict: `PASS_WITH_REQUIRED_CHANGES`

## 1. Review Scope

This review challenges the plan artifact
`docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-plan-20260613.md`
against the accepted prior facts, source authority boundaries, evidence
sufficiency rules, and `NOT_READY` preservation requirements.

Read set:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-plan-20260613.md`
- `docs/reviews/mvp-strict-golden-2025-answer-evidence-controller-judgment-20260613.md`
- `docs/reviews/mvp-004393-2025-same-year-evidence-intake-source-authority-decision-controller-judgment-20260613.md`
- `docs/reviews/mvp-markdown-golden-answer-schema-build-tooling-implementation-controller-judgment-20260613.md`

No source, test, runtime, golden answer, fixture promotion, live EID, network,
PDF, FDR, provider, LLM, analyze, checklist, readiness, release, PR, push,
merge, stage, commit, or cleanup actions were performed for this review.

## 2. Findings

### 2.1 Required Changes (Blocking)

| # | Severity | Finding | Evidence | Required Change |
|---|----------|---------|----------|-----------------|
| R1 | HIGH | Candidate row input dependency is unresolved. The next evidence gate requires "controller-provided candidate row source artifact" (plan §6 read set, §12 stop condition), but neither this planning gate nor the proposed evidence gate produces candidate rows. The evidence gate is no-live (plan §10: no EID/network/PDF commands), so it cannot extract rows from the 2025 annual report. The plan creates a process deadlock: the evidence gate needs candidate rows to start, but no upstream gate produces them. | Plan §6 read set lists "controller-provided candidate row source artifact, if any" as input. Plan §12 first stop condition: "no controller-provided or reviewed candidate same-year row source exists." Plan §10 disallows live EID/network/PDF/FDR commands. The plan write set (§7) does not include candidate row production. | Add an explicit prerequisite: before the evidence gate opens, the controller must produce a candidate row source artifact under `docs/reviews/` (not under `reports/golden-answers/`). Or, alternatively, split the evidence gate into two sub-gates: (a) a controlled-live candidate row extraction sub-gate that reads the 2025 annual report through EID single-source to produce candidate rows, followed by (b) the no-live row-acceptance evidence gate. The current plan implies candidate rows will materialize from an unspecified source; this is not acceptable for a planning gate that gates the next entry. |
| R2 | MEDIUM | Defer rule conflates "evidence does not exist in report" with "evidence not yet read." Plan §8 defer rules list "same-year evidence is unavailable, not directly read" as a single defer trigger without distinguishing the two cases. A row deferred because the annual report lacks the disclosure has a different future disposition (permanent skip) than a row deferred because the report has not been read yet (re-reviewable). Conflating them creates ambiguous residuals that cannot be correctly routed to future gates. | Plan §8: "Defer rows where same-year evidence is unavailable, not directly read, too ambiguous, or dependent on a future extractor/source contract." | Split the defer trigger: (a) `DEFER_NOT_READ`: same-year annual report is known to exist but the relevant section has not been read — re-reviewable in a future gate. (b) `DEFER_NOT_DISCLOSED`: the annual report does not contain this disclosure — may become a permanent skip after confirmation. (c) `DEFER_AMBIGUOUS`: evidence exists but is too ambiguous for row acceptance. Each defer class must produce a distinct residual that the evidence artifact tracks separately. |

### 2.2 Non-blocking Findings

| # | Severity | Finding | Evidence | Recommendation |
|---|----------|---------|----------|----------------|
| N1 | LOW | Low-confidence acceptance escape hatch lacks controller acknowledgment. Plan §8 confidence rules state "low rows should normally be deferred unless the evidence artifact records why a low confidence row is still acceptable." While DS/MiMo reviewers can independently challenge low-confidence rows in the evidence gate, the plan does not require explicit controller acknowledgment for any accepted low-confidence row. This creates a path where low-confidence rows could accumulate across multiple evidence gates without controller-level scrutiny. | Plan §8: "low: disclosure is ambiguous, partial or formatting-sensitive; low rows should normally be deferred unless the evidence artifact records why a low confidence row is still acceptable." | Add a requirement: any low-confidence row that the evidence gate accepts must be explicitly flagged for controller acknowledgment in the controller judgment for that gate. The evidence artifact may recommend acceptance, but only the controller judgment can finalize it. |
| N2 | LOW | Cross-year structural facts are not addressed. Plan §8 row-local evidence criteria states "one row cannot inherit proof from another row unless the shared source line explicitly covers both values." This is correct for year-specific data. However, fund-level structural attributes (fund_name, fund_type, benchmark) are definitionally cross-year and would appear in both 2024 and 2025 annual reports. The plan does not provide guidance on whether a 2025 row for `fund_type` must cite the 2025 annual report or whether it can rely on the fund's registration-level type that does not change year-over-year. Without guidance, reviewers may unnecessarily reject structurally stable rows or, conversely, accept year-specific rows under a misapplied structural exemption. | Plan §8 source rules: "2024 rows, cross-year narrative facts, product smoke output, fixture state, preflight gaps or source availability facts cannot supply row truth." This prohibits 2024 rows as truth for 2025, but fund_type field is cross-year by definition. | Add a structural-attribute rule: fields whose value is fund-registration-level (fund_name, fund_type, benchmark_index, inception_date) and that are not expected to change year-over-year may be accepted under `report_year: 2025` metadata if the 2025 annual report confirms no change. The source citation must still point to the 2025 annual report. This preserves the same-year source requirement while acknowledging that structural attributes are definitionally stable. |
| N3 | LOW | Temp-path validation does not require cleanup verification. Plan §10 allows optional build smoke under `/private/tmp` but does not require the evidence gate to verify that temp files were cleaned up after smoke testing. On macOS, `/private/tmp` is system-wide `/tmp`; while collision risk is low for uniquely named files, the plan should close the loop. | Plan §10: "If optional build smoke is run, it must not use default output paths and must not overwrite tracked `reports/golden-answers/golden-answer.json`." No cleanup requirement. | Add to validation matrix: after optional build smoke, verify that no temp artifact remains under `/private/tmp` that could be mistaken for tracked output. |
| N4 | LOW | Evidence gate verification scope is not explicitly bounded. Plan §5 says the next gate should "verify each row against direct same-year evidence," implying primary source verification. But plan §10 limits validation to manual row-shape inspection, duplicate identity check, and optional parser smoke — none of which verify that the `expected_value` actually matches the cited annual report source. The evidence gate's actual verification is row-shape and consistency checking; primary source verification (comparing expected_value against the annual report text) requires reading the annual report, which is no-live. The plan should not use "verify" language that implies a capability the no-live gate cannot deliver. | Plan §5: "verify each row against direct same-year evidence." Plan §10 validation matrix: row-shape inspection, duplicate identity check, parser/build smoke. | Reword §5 purpose to: "review candidate rows for shape compliance, metadata correctness, duplicate rejection, and source format validity; reviewers independently assess whether the cited source text plausibly supports the expected_value given the annual report disclosure." This accurately bounds what a no-live review gate can do. |

## 3. Positive Findings

The following plan elements are correctly specified and well-defended:

| # | Element | Rationale |
|---|---------|-----------|
| P1 | Historical probe-only prohibition (§9) is explicit and correctly bounded. Historical 2025 probe rows are limited to one negative fact and cannot seed accepted rows without re-review through the Markdown-first path. This aligns with the accepted source-authority decision. | Correct. |
| P2 | Source-text inference rejection (§8) is consistently applied. `source` is accepted only as human evidence text, not machine identity authority. `report_year` cannot be inferred from heading text, source text, or file name (§8). This closes the inference loophole identified in prior controller judgments. | Correct. |
| P3 | Tracked-output protection (§7, §10, §12) is comprehensive. The disallowed write set explicitly enumerates `reports/golden-answers/golden-answer-prefill-reviewed.md`, `reports/golden-answers/golden-answer.json`, fixture promotion state files, source files, tests, and runtime outputs. Stop conditions trigger if any operation would write tracked golden content. The temp-path smoke uses `/private/tmp` only. | Correct. |
| P4 | `NOT_READY` preservation is consistent across all sections. Non-goals (§2), still-not-accepted (§4), next gate purpose (§5), residuals (§13), and stop conditions (§12) all preserve `NOT_READY`. No section claims or implies readiness improvement from this line of work. | Correct. |
| P5 | Row-local evidence criteria (§8) are correctly specified. "One row cannot inherit proof from another row unless the shared source line explicitly covers both values." This prevents transitive acceptance where Row A's source is incorrectly cited for Row B. | Correct. |
| P6 | Reject rules (§8) cover all known non-truth sources: 2024 rows, probe-only artifacts, product smoke output, arbitrary residue, source fallback, fixture promotion state, and inferred source text. No known non-truth source class is omitted. | Correct. |
| P7 | Confidence classification (§8) uses a three-tier system (high/medium/low) with per-tier criteria grounded in evidence characteristics rather than reviewer sentiment. The criteria reference disclosure clarity, selection ambiguity, and formatting sensitivity — verifiable properties of the source. | Correct. |
| P8 | Fallback source prohibition (§2, §4, §8) covers Eastmoney, fund-company, and CNINFO. This aligns with the current EID single-source operational policy and the accepted source-authority decision that rejected fallback as source authority for golden content. | Correct. |
| P9 | Read-as-proof disallow list (§6) correctly excludes arbitrary untracked residue, product narrative output, 2024 golden rows, and quality gate status as row truth. | Correct. |
| P10 | Write set (§7) correctly separates evidence artifacts (allowed) from tracked golden content (disallowed). Candidate rows stay in `docs/reviews/` until a later implementation/write gate authorizes tracked content update. | Correct. |

## 4. Adversarial Failure Pass

The following failure modes were considered and the plan either prevents them or the residual is acceptable:

| Failure mode | Plan defense | Assessment |
|---|---|---|
| Reviewer accepts a row because source text "looks plausible" without verifying against the annual report | No-live constraint means primary source verification is impossible in the evidence gate. Reviewers can only check row shape and source format. See finding N4. | Acceptable as bounded scope if N4 is addressed. |
| Candidate rows are placed in `reports/golden-answers/` by accident | §7 disallowed write set explicitly lists both golden answer paths. §12 stop condition triggers on any tracked golden content write. | Adequate. |
| Build smoke overwrites tracked golden JSON | §10 requires temp paths only, explicitly forbids default output paths and tracked overwrites. | Adequate. |
| Low-confidence rows accumulate and become de-facto accepted content | Reviewers (DS/MiMo) independently challenge each row. Finding N1 recommends controller acknowledgment for low-confidence rows. | Adequate with N1. |
| 2024 golden rows are silently reused for 2025 | §8 reject rules: "Reject rows sourced from 2024." §4 still-not-accepted: "2024 golden rows as 2025 evidence" explicitly listed. §6 disallowed read-as-proof. | Adequate. Triple-covered. |
| Historical probe rows are promoted without re-review | §9 prohibits promotion: "must not be used as accepted row evidence unless the next evidence gate re-reads the underlying same-year evidence." §12 stop condition. | Adequate. |
| Fixture promotion is triggered as a side effect | §2 non-goals, §7 disallowed write set, §12 stop conditions all exclude fixture promotion. | Adequate. |
| Someone runs `golden-build` with default paths during evidence gate | §10 validation matrix: "must not use default output paths." §12 stop condition: "validation requires … tracked golden-build output writes." | Adequate. |
| Source text is used to infer `report_year` | §8: "Do not infer report_year from heading text, source text or file name." Also rejected in accepted build-tooling implementation judgment. | Adequate. |
| Candidate row input never materializes, deadlocking the evidence gate | §12 first stop condition covers this, but the plan does not specify who produces candidate rows or when. See finding R1. | NOT adequate. Requires R1. |

## 5. Residuals

| Residual | Owner | Destination |
|---|---|---|
| Candidate row input dependency (R1) | Plan author / controller | Must be resolved before evidence gate opens. |
| Defer class conflation (R2) | Plan author | Must be split in plan amendment. |
| Low-confidence controller acknowledgment (N1) | Controller / evidence gate owner | Optional hardening for evidence gate. |
| Cross-year structural attribute guidance (N2) | Plan author | Optional clarification. |
| Temp-path cleanup verification (N3) | Evidence gate owner | Optional hardening. |
| Evidence gate verification scope wording (N4) | Plan author | Recommended rewording. |

## 6. Final Recommendation

The plan is structurally sound in its core design: it correctly prohibits historical probe rows, 2024 golden rows, fallback sources, source-text inference, arbitrary residue, and fixture promotion as truth sources. It consistently preserves `NOT_READY` and protects tracked golden content from unauthorized writes. The row acceptance criteria, confidence classification, and reject rules are comprehensive and align with all accepted prior facts.

However, the plan has one blocking gap (R1): it describes an evidence gate that requires candidate rows as input but does not specify how those candidate rows will be produced. Since the evidence gate is no-live and cannot extract rows from the 2025 annual report, and neither this planning gate nor any prior accepted gate produces candidate rows, the process deadlocks. This must be resolved before the evidence gate can proceed.

R2 (defer class conflation) is a correctness concern for residual tracking and should also be addressed before the evidence gate opens.

**Recommendation**: Return to controller with `PASS_WITH_REQUIRED_CHANGES`. After R1 and R2 are addressed in a plan amendment, the evidence gate may open. Non-blocking findings N1-N4 are recommended hardening but do not block the gate.

**Next gate after amendment**: `004393 / 2025 Same-year Reviewed Golden Content Evidence Gate`, contingent on R1 resolution (candidate row availability) and R2 resolution (defer class split).
