# P19 Design Update（2026-05-22）

## Verdict

`ACCEPTED_WITH_CORRECTIONS`

P19 thermometer independent-development inputs are fused into `docs/design.md` without overwriting existing v2.2/P17 facts.

## Inputs

| Input | Role |
|---|---|
| `docs/p19-thermometer-technical-proposal.md` | Thermometer methodology and module proposal |
| `docs/design-md-v22-changes.md` | Proposed design.md changes |
| `docs/p19-phase-definition.md` | Phase-level thermometer plan input |
| `docs/design.md` | Existing design truth, already v2.2 after P17 |

## Accepted Changes

- Updated v2.2 header summary to state P19 independent thermometer development while preserving the current public-page query as transitional code fact.
- Updated §1.3 non-goals: current Youzhiyouxing public-page scraping is not a long-term source of truth; automatic `valuation_state` mapping remains gated and can only enter through P19-S3 or a later dedicated gate.
- Updated §6.3 external data: added P19 self-owned thermometer target using akshare + CSIndex/akshare index valuation interfaces, with explicit target modules.
- Added §11 "温度计设计" covering design decisions, algorithm, bands, supported indexes, module boundaries, core types, analyze integration gate, disclaimer, and non-goals.
- Renumbered the existing plan-review boundary checklist to §12 so future plan reviews still inherit the design-boundary hard checks.
- Added four design-decision rows for thermometer source, method, weighting, and gated `valuation_state` integration.

## Corrections Against Input

| Input claim | Controller correction |
|---|---|
| "v2.1 → v2.2" | Current `docs/design.md` was already v2.2 after P17. This update is a v2.2 fusion, not a downgrade/re-version. |
| P19 overall includes automatic `analyze` integration | Automatic `valuation_state` mapping is accepted only as P19-S3 scope. P19-S1/S2 may compute readings and candidates but must not silently change `analyze`. |
| Use Youzhiyouxing page to validate direction | Allowed as comparison/research only, not as production truth. |
| New modules listed as code locations | Written as P19 target modules, not current implementation facts. |

## Design Boundary Rationale

First principles: a thermometer that changes analysis conclusions becomes an input to the investor decision path. Therefore the durable design must separate three concerns:

1. data truth and calculation (`P19-S1/S2`),
2. presentation and disclaimers (`fund-analysis thermometer`),
3. automatic effect on analysis judgment (`P19-S3`).

This prevents the project from replacing one fragile implicit dependency, public-page scraping, with another implicit dependency, silent valuation-state injection.

## Residuals For P19 Plan Review

- Verify actual akshare all-A PE/PB availability, field names, missing-value behavior, and historical coverage before implementation.
- Estimate first-run historical backfill time and storage size before choosing parquet dependency.
- Define acceptable deviation against Youzhiyouxing as direction-first, not exact-value parity.
- Decide whether `pyarrow` or `fastparquet` is added, or whether P19-S1 should start with a simpler cache format before parquet.
