# DS-role Review: Turnover Rate Root-cause Evidence Gate

Date: 2026-06-12

Review target: `docs/reviews/mvp-turnover-rate-root-cause-evidence-20260612.md`

Reviewer role: AgentDS-role

Verdict: `PASS_WITH_AMENDMENTS`

## Findings

| ID | Severity | Finding | Controller disposition |
| --- | --- | --- | --- |
| `DS-RC-001` | none | Accepted lineage verification is sufficient. `quality_gate.json/md`, `score.json`, and `snapshot.jsonl` size/SHA-256 match the identity evidence, and only the accepted run directory is used. | Accepted. |
| `DS-RC-002` | none | Raw snapshot, score, and quality rows support the evidence conclusion. Snapshot row has `manager.turnover_rate`, `extraction_mode=missing`, `value_present=false`, `anchor_present=false`, EID single-source/no-fallback. Score and quality issues correspond. | Accepted. |
| `DS-RC-003` | none | `EVIDENCE_INSUFFICIENT` is defensible because accepted lineage has no same-lineage source body, parsed annual-report section, or `§8` excerpt. Snapshot note is not source-body proof. | Accepted. |
| `DS-RC-004` | none | H3/H4/H5 are correctly scoped to the accepted snapshot-to-score chain; `FQ2F/warn 004393` is derivative of `turnover_rate`. | Accepted, with MiMo wording amendment to avoid full pre-snapshot rejection. |
| `DS-RC-005` | low | Evidence artifact should record workspace guard commands and validation results before controller acceptance. | Accepted and amended in evidence artifact. |

## Residuals

- H1/H2 remain unresolved without same-lineage `§8` source excerpt.
- `FQ2F/warn 004393` is derivative, not an independent root cause.
- `FQ0/info year_not_covered` remains deferred to strict golden 2025
  coverage/promotion planning.

## Final Recommendation

Do not open implementation. Next entry should be
`Turnover rate same-source disclosure evidence gate`. If source-body retrieval
requires live EID/FDR access, it must be separately bounded and must record
source lineage before being used as proof.
