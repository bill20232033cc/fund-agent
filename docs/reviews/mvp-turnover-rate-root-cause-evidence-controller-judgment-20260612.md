# Controller Judgment: Turnover Rate Extraction/Traceability Root-cause Evidence Gate

Date: 2026-06-12

Gate: `Turnover rate extraction/traceability root-cause evidence gate`

Classification: `standard`

Verdict: `ACCEPT_WITH_AMENDMENTS_NOT_READY`

## Reviewed Artifacts

- Evidence:
  `docs/reviews/mvp-turnover-rate-root-cause-evidence-20260612.md`
- Planning input:
  `docs/reviews/mvp-turnover-rate-root-cause-plan-20260612.md`
- MiMo-role review:
  `docs/reviews/mvp-turnover-rate-root-cause-evidence-review-mimo-20260612.md`
- DS-role review:
  `docs/reviews/mvp-turnover-rate-root-cause-evidence-review-ds-20260612.md`
- Accepted identity input:
  `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md`

## Decision

The evidence gate is accepted for what it proves:

1. the accepted evidence lineage is hash/size matched;
2. the accepted snapshot row for `manager.turnover_rate` is
   `extraction_mode=missing`, `value_present=false`, `anchor_present=false`;
3. the accepted score row consistently reports `coverage_rate=0.0` and
   `traceability_rate=0.0`;
4. the accepted quality gate consistently emits `FQ2/warn turnover_rate` and
   derivative `FQ2F/warn 004393`;
5. `FQ0/info year_not_covered` remains a strict golden 2025 coverage/promotion
   issue and is not a turnover root cause.

The gate does not authorize implementation, because it does not prove a
code-rooted root cause.

## Review Disposition

| Finding | Disposition | Reason |
| --- | --- | --- |
| Accepted lineage verification is sufficient | `ACCEPT` | Size/SHA-256 for `quality_gate.json`, `quality_gate.md`, `score.json`, and `snapshot.jsonl` match the accepted identity evidence. |
| `EVIDENCE_INSUFFICIENT` is defensible | `ACCEPT` | The accepted lineage contains no source body, parsed annual-report section, or same-lineage `§8` excerpt. |
| H3/H4 wording was too strong | `ACCEPT_WITH_REWRITE` | Evidence can reject snapshot-to-score field-name or pure anchor-loss interpretation, but cannot fully reject pre-snapshot extractor/bundle mapping or anchor loss. Evidence artifact was amended accordingly. |
| H5 score interpretation rejection | `ACCEPT` | Raw snapshot, score, and quality-gate rows are internally consistent. |
| Workspace guard should be recorded | `ACCEPT_WITH_REWRITE` | Evidence artifact now records branch/status/diff guard results. |
| Next entry should be same-source disclosure evidence | `ACCEPT` | H1 source absence and H2 extractor miss remain unresolved without source-body evidence. |

## Hypothesis Disposition

| Hypothesis | Controller disposition |
| --- | --- |
| H1 source disclosure absent | `UNPROVEN` |
| H2 extractor missed disclosed value | `UNPROVEN` |
| H3 mapping or field-normalization loss | `NOT_SUPPORTED_IN_ACCEPTED_SNAPSHOT_TO_SCORE_CHAIN`; pre-snapshot loss remains unresolved |
| H4 anchor or traceability loss | `NOT_SUPPORTED_IN_ACCEPTED_SNAPSHOT_TO_SCORE_CHAIN`; pre-snapshot loss remains unresolved |
| H5 quality-score interpretation issue | `REJECT` |

## Residuals

| Residual | Owner | Next gate | Current blocker? |
| --- | --- | --- | --- |
| H1/H2 unresolved | Fund extractor/source-evidence owner | `Turnover rate same-source disclosure evidence gate` | Blocks implementation |
| Pre-snapshot H3/H4 unresolved | Fund extractor/snapshot owner | Same-source disclosure evidence gate, or later narrow implementation gate only if source/pre-snapshot evidence proves code-rooted loss | Blocks implementation |
| `FQ0/info year_not_covered` | Strict golden coverage owner | Strict golden 2025 coverage/promotion planning gate | Does not block turnover root-cause evidence acceptance |

## Next Entry

Recommended next entry:

`Turnover rate same-source disclosure evidence gate`

Entry criteria:

- identify or collect same-lineage source text for
  `004393 / 2025 / eid / single_source_only`;
- inspect only the relevant `§8` source excerpt for numeric turnover-rate
  disclosure;
- decide between `SOURCE_ABSENT_CONFIRMED` and
  `EXTRACTOR_MISSED_DISCLOSED_VALUE`;
- open implementation only if same-source evidence proves a disclosed numeric
  value existed and the extractor failed to extract it.

Boundary:

- no source acquisition policy change;
- no Eastmoney, fund-company website, CNINFO, fallback, provider/LLM, golden
  promotion, release/readiness, PR, cleanup, delete, archive or ignore work;
- if source-body retrieval requires live EID/FDR access, it must be a separately
  bounded controlled evidence command and must record source lineage before the
  output is used as proof.
