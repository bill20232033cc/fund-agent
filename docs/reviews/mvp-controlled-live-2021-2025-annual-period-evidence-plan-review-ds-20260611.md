# MVP controlled live 2021-2025 annual-period evidence plan review - DS

## Review Scope

- Reviewer: AgentDS, independent plan reviewer.
- Gate: `controlled live 2021-2025 annual-period evidence planning gate`.
- Reviewed artifact: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-20260611.md`.
- Truth inputs: `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`.
- Review mode: static plan review only. No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands were run. No source, test, runtime, design, control or startup doc modifications were made.

## Verdict

`ACCEPT_WITH_FINDINGS`

## Focus Question Answers

### 1. Is the future live command matrix bounded enough for a controlled live evidence gate?

Yes. The matrix defines four evidence steps (E0–E3), each with explicit allowed commands, acceptance evidence, and stop conditions. Only E2 reaches live EID/network/PDF/FDR. The primary sample is a single fund/year pair; E3 explicitly prohibits iteration and requires a controller amendment for any second sample. The matrix is reviewable and its blast radius is explicit.

### 2. Does it preserve EID single-source and prevent Eastmoney, fund-company/CDN, CNINFO or fallback re-entry?

Yes. The plan lists all four as non-goals, includes Eastmoney/fund-company/CNINFO/fallback in E2 stop conditions, and includes them in the negative-action checklist. The proposed command uses the accepted product path through `FundDocumentRepository`, which currently enforces `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`. The `--valuation-state unavailable` flag avoids external valuation source access.

### 3. Is quality-gate-policy warn acceptable as evidence-only control without claiming product default behavior changed?

Yes. `quality_gate_policy=block` remains the product default per `docs/design.md` lines 841–842. The plan uses `--quality-gate-policy warn` as an explicit CLI override for a single evidence run, which is a parameter the CLI already exposes. The plan states this is evidence-only, captures quality gate status transparently in the evidence schema, and does not claim the default changed. The acceptance criteria explicitly call this out for reviewer scrutiny.

### 4. Is primary sample 004393 / 2025 / 2021-2025 acceptable given only 2024 small-golden proof is currently accepted?

Yes, with the plan's own caveats. The plan correctly states that 004393/2024 small-golden proof only proves EID/FDR acquisition, PDF integrity, and parser viability for 2024 — not for 2025, and not for the multi-year path. Using a known-good fund code as a first live sample is a reasonable risk reduction. The plan does not claim 2024 proof validates 2025. E2 evidence classification correctly separates target-year failure from prior-year degradation. The plan's honesty about the limitation is appropriate for a planning artifact.

### 5. Are stop conditions and evidence artifact schema sufficient for controller judgment without raw PDF/report content?

Yes. The stop conditions cover all critical failure modes: source policy violation (non-EID), boundary violation (bypassing FundDocumentRepository), identity mismatch, scope creep (LLM/provider/golden/readiness/release), and raw data capture. The evidence schema captures metadata sufficient for classification: exit code, byte counts, year-level provenance table with failure categories, cross-year fact summary, negative-action checklist, and residual table. The controller can judge product-path behavior, source policy compliance, and year-level outcomes from metadata alone, without raw PDF text or full report body.

## Findings

| Severity | Location | Disposition |
|---|---|---|
| MODERATE | Plan §E3, lines 125–129 | The plan says the execution worker must "stop and report the classification" when target-year 2025 is unavailable, but does not specify what minimal evidence artifact the worker should produce (e.g., truncated schema with E0/E1 results plus unavailability classification). The execution gate worker would benefit from an explicit artifact expectation for this path. Recommend the execution gate plan or controller amendment define a truncated artifact template for target-year-unavailable. |
| LOW | Plan §Evidence Artifact Schema, lines 131–166 | The future evidence artifact schema covers only E2 output. E0 and E1 produce preflight evidence (branch, HEAD, CLI help output) that the execution gate controller needs as preconditions. The schema section should cross-reference that E0/E1 results must be recorded in the same evidence artifact or an adjacent preflight artifact. |
| LOW | Plan §E2, lines 86–123 | The command `--quality-gate-policy warn` is justified in the acceptance criteria section, but the command matrix itself does not include a brief inline reminder that `block` remains the product default and `warn` is a CLI override for this evidence run only. Adding one sentence in the command rationale would reduce future misreading risk. |

## Accepted Residuals / Deferred Candidates

| Residual | Classification | Rationale |
|---|---|---|
| Multi-year narrative writer/reporting | Deferred candidate | Explicitly listed as deferred entry; correct for this planning gate |
| Structured-data source identity extension | Deferred candidate | Explicitly listed as deferred entry; correct |
| Coverage measurement environment hygiene | Deferred candidate | Explicitly listed as deferred entry; correct |
| Release-readiness residual acceptance evidence | Deferred candidate | Explicitly listed as deferred entry; correct |
| Single-sample limitation (no alternate without controller amendment) | Accepted residual | Appropriate for a first controlled live evidence gate; the amendment requirement prevents data hunting |
| E0/E1 preflight results not integrated into E2 evidence schema | Accepted residual | Addressed in LOW finding above; does not block acceptance |

## Validation Performed

- **Static contract verification**: Compared plan claims against `AGENTS.md` source policy (§年报来源 fallback 策略), `docs/design.md` current state (EID single-source, small-golden scope, QualityGatePolicy defaults, multi-year productization), `docs/current-startup-packet.md` gate scope and non-goals, and `docs/implementation-control.md` current gate and residual state.
- **Scope boundary check**: Verified the plan does not authorize implementation, source policy change, provider/LLM reconfiguration, golden/readiness promotion, release state change, or residue cleanup. All four non-goal categories align with the current startup packet and implementation control non-goal reminders.
- **Stop condition coverage**: Verified each evidence step has at least one stop condition, E2 has the most comprehensive set (5 conditions), and E3 adds a meta-level stop against uncontrolled iteration.
- **Evidence schema completeness check**: Verified the schema captures provenance (source, mode, fallback flags), year-level classification, cross-year fact scope, and negative-action attestation — sufficient for controller judgment without raw content.

## Explicit Statement

No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands were run during this review. No source, test, runtime, design, control, or startup doc files were modified.
