# Docling Baseline Qualification Built-in Representation Handler Plan Review - DS - 2026-06-15

Verdict: `BLOCKED`

Review target:

- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-20260615.md`

Truth sources checked:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-handler-routing-decision-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-implementation-controller-judgment-20260615.md`

## Findings

| ID | Severity | Path | Section | Reason | Fix |
|---|---|---|---|---|---|
| DS-F1 | High / blocking | `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-20260615.md` | §10 Manifest Plan For First Evidence Gate; §11 Output Overwrite Policy | The plan makes the first-wave manifest include S1 `reference_existing_json` entries whose output paths are existing JSONs, while §11 says "any existing manifest output path must raise before writing." This is internally contradictory with §6, which says `reference_existing_json` remains validation-only and is not rewritten. An implementation worker would have to choose whether to block S1 references or silently weaken no-clobber. That is not code-generation-ready and can make the later evidence manifest impossible to execute as written. | Amend §11 to define no-clobber over write-producing entries only: `handled` and `blocked`. `reference_existing_json` entries must be validated as existing read-only references and excluded from overwrite/no-clobber write-target checks. Add required tests for: existing reference JSON accepted without rewrite; existing handled/blocked output rejected by default; mixed manifest preflight rejects existing write target before any write; `--allow-overwrite` applies only to write-producing entries. |

## Boundary Review

- FundDocumentRepository / production boundary: no blocking issue besides DS-F1. The plan keeps implementation inside `fund_agent/fund/documents/candidates/`, forbids repository/source/cache modifications, forbids `cache/pdf`, and forbids Service/UI/Host/renderer/quality-gate integration.
- EID HTML render: no raw XML/source truth escalation found. The plan keeps EID HTML as `eid_xbrl_html_render_candidate`, blocked by default for S4/S5/S6 unless later discovery accepts render artifacts.
- Docling: lazy import, local artifact path, socket-block default and no model-download intent are present. Implementation review must still verify the concrete socket-block mechanism and failure mapping.
- pdfplumber: planned as candidate-internal, fake-tested, and not a production parser replacement. Tests are scoped away from real annual-report PDF body reads.
- Source policy/readiness: plan preserves EID single-source/no fallback, `NOT_READY`, no field correctness, no taxonomy compatibility, no source truth, no baseline qualification and no readiness/release claim.

## Residual Risks

- `--docling-no-socket-block` is listed as a future-authorized escape hatch. The implementation gate must not exercise it and should make its use auditable if implemented.
- The plan allows tiny synthetic PDFs "if needed"; implementation review should verify tests do not read real annual-report PDF bodies and do not touch production-shaped `cache/pdf`.
- Current control docs lag newer accepted routing judgments. This is already recorded as a controller residual and is not the blocker for this plan review.

## Implementation Gate Decision

Do not enter `Built-in Candidate Representation Route Handler No-live Implementation Gate` yet.

Required before implementation:

1. Amend the overwrite/no-clobber policy to exclude `reference_existing_json` from write-target no-clobber checks.
2. Add the specific no-live test requirements listed in DS-F1.
3. Request targeted DS re-review of DS-F1.
