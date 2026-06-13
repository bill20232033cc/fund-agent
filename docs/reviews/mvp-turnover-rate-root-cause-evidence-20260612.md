# Turnover Rate Extraction/Traceability Root-cause Evidence Gate

Date: 2026-06-12

Gate: `Turnover rate extraction/traceability root-cause evidence gate`

Classification: `standard`

Status: evidence artifact

## Verdict

Primary disposition: `EVIDENCE_INSUFFICIENT`.

The accepted evidence lineage proves that `manager.turnover_rate` reached the
quality gate as a missing extraction with no value and no anchor, and that the
score and quality-gate warnings are internally consistent with that snapshot
row.

The accepted evidence lineage does not contain same-source annual-report body
text or a same-lineage `§8` excerpt. Therefore this gate cannot prove whether the
root cause is source disclosure absence or an extractor miss. Implementation is
not authorized by this evidence gate.

## Scope

This gate only reads accepted local artifacts and current source/test files
needed to interpret the artifact chain. It does not modify source, tests,
runtime behavior, source policy, provider/LLM behavior, fallback behavior,
golden promotion, release state, PR state, cleanup state, or readiness state.

No live EID, network, PDF, FDR, provider, LLM, analyze, checklist, golden,
readiness, release, curl, DNS, or socket command was run.

## Workspace Guard

Commands run:

```bash
git branch --show-current
git status --short
git diff --check
```

Observed state:

- current branch: `feat/mvp-llm-incomplete-run-artifacts`;
- tracked diff check passed with no output;
- visible changes are untracked artifacts only, including this evidence artifact
  and the preceding planning artifact;
- pre-existing unrelated untracked residue remains untouched and is not used as
  source proof.

## Accepted Lineage Check

Accepted identity evidence:

- `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md`

Accepted run id:

- `analyze-004393-2025-20260612T090735116031Z`

Hash/size verification:

| Artifact | Expected size / SHA-256 from accepted evidence | Observed size / SHA-256 | Lineage status |
| --- | --- | --- | --- |
| `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.json` | `3302` / `a63e7a82d47cce6de1208e7aa4684895a72556f4474733e5121fdb23cdca665d` | `3302` / `a63e7a82d47cce6de1208e7aa4684895a72556f4474733e5121fdb23cdca665d` | matched |
| `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.md` | `1460` / `be3082051b8d28f7d00454fb5a539723a5754db8cb90030cf7e0ce1a42a5d503` | `1460` / `be3082051b8d28f7d00454fb5a539723a5754db8cb90030cf7e0ce1a42a5d503` | matched |
| `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/score.json` | `147520` / `bb66ed889d10aca62a5a11a7e58fd9752f77562cc3c7e2850efbc20dc9ac14b5` | `147520` / `bb66ed889d10aca62a5a11a7e58fd9752f77562cc3c7e2850efbc20dc9ac14b5` | matched |
| `reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/snapshot.jsonl` | `26925` / `f5e0fd3783f0ede807d1f9797644e2a81c48b214d831325baf75f497b0e8230f` | `26925` / `f5e0fd3783f0ede807d1f9797644e2a81c48b214d831325baf75f497b0e8230f` | matched |

Command evidence:

```bash
wc -c reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.json reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.md reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/score.json reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/snapshot.jsonl
shasum -a 256 reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.json reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.md reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/score.json reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/snapshot.jsonl
```

## Raw Snapshot Row

Accepted snapshot row:

| Field | Value |
| --- | --- |
| `run_id` | `analyze-004393-2025-20260612T090735116031Z` |
| `fund_code` | `004393` |
| `fund_name` | `安信企业价值优选混合A` |
| `report_year` | `2025` |
| `field_group` | `manager` |
| `field_name` | `turnover_rate` |
| `extraction_mode` | `missing` |
| `value_present` | `false` |
| `anchor_present` | `false` |
| `section_id` | `null` |
| `page` | `null` |
| `table_id` | `null` |
| `row_id` | `null` |
| `note` | `§8 未披露可规则化抽取的换手率` |
| `selected_source` | `eid` |
| `source_mode` | `single_source_only` |
| `fallback_enabled` | `false` |
| `fallback_used` | `false` |
| `source_provenance_reason` | `primary_source_success_no_fallback` |

This proves the quality warning is downstream of a missing `turnover_rate`
snapshot row. It does not by itself prove the annual report actually lacks a
numeric turnover-rate disclosure, because the artifact row records the extractor
result, not the source body.

## Score and Quality-gate Consistency

Accepted `score.json` field row:

| Field | Value |
| --- | --- |
| `field_group` | `manager` |
| `field_name` | `turnover_rate` |
| `priority` | `P1` |
| `records` | `1` |
| `covered_records` | `0` |
| `traceable_records` | `0` |
| `coverage_rate` | `0.0` |
| `traceability_rate` | `0.0` |
| `status` | `fail` |

Accepted `score.json` fund row:

| Field | Value |
| --- | --- |
| `fund_code` | `004393` |
| `fund_name` | `安信企业价值优选混合A` |
| `app_category` | `国内股票类` |
| `records` | `16` |
| `p0_status` | `pass` |
| `p1_status` | `fail` |
| `p1_failed_fields` | `["turnover_rate"]` |
| `status` | `fail` |

Accepted `quality_gate.json` issues:

| Rule | Severity | Field/Fund | Evidence meaning |
| --- | --- | --- | --- |
| `FQ2` | `warn` | `turnover_rate` | P1 field has `coverage_rate=0.0` and `traceability_rate=0.0` |
| `FQ2F` | `warn` | `004393` | fund-level derivative warning from failed P1 field `turnover_rate` |
| `FQ0` | `info` | `004393` | `year_not_covered`; deferred strict golden 2025 issue, not turnover root cause |

Consistency finding:

- Snapshot has `value_present=false` and `anchor_present=false`.
- Score reports `covered_records=0` and `traceable_records=0`.
- Quality gate reports `FQ2/warn` and derivative `FQ2F/warn`.
- This supports the scoring/quality-gate interpretation; it does not support a
  score interpretation bug.

## Same-source Disclosure Availability

Repository search for the accepted run id and accepted quality-gate path found
only the accepted quality artifacts and review references. The run directory
contains:

- `golden_set.json`
- `snapshot.jsonl`
- `score.json`
- `score.md`
- `quality_gate.md`
- `quality_gate.json`

No same-lineage source body, parsed annual-report section, or `§8` source
excerpt is present in the accepted artifact lineage.

This matters because `source disclosure absent` and `extractor missed disclosed
value` require the same original source body. A snapshot note saying
`§8 未披露可规则化抽取的换手率` is extractor output evidence, not independent source
disclosure evidence.

## Hypothesis Disposition

| Hypothesis | Disposition | Basis |
| --- | --- | --- |
| H1 source disclosure absent | `UNPROVEN` | Same-lineage source body or `§8` excerpt is absent from accepted artifacts. Snapshot note alone is not source-disclosure proof. |
| H2 extractor missed disclosed value | `UNPROVEN` | Same-lineage source body is absent, so there is no direct evidence that a numeric disclosure existed and was missed. |
| H3 mapping or field-normalization loss | `NOT_SUPPORTED_IN_ACCEPTED_SNAPSHOT_TO_SCORE_CHAIN` | Accepted snapshot has the expected `field_group=manager`, `field_name=turnover_rate`, and one score record consumes that same field. This rejects a snapshot-to-score field-name loss, but it does not prove whether any pre-snapshot extractor/bundle value existed and was lost before the accepted snapshot row. |
| H4 anchor or traceability loss | `NOT_SUPPORTED_IN_ACCEPTED_SNAPSHOT_TO_SCORE_CHAIN` | Accepted snapshot has no value and no anchor. This is not a pure snapshot-level anchor-loss shape, but it does not prove whether anchors existed before snapshot and were dropped before the accepted row was emitted. |
| H5 quality-score interpretation issue | `REJECT` | Raw snapshot row and score row are consistent: missing value/no anchor maps to zero coverage/traceability and P1 fail. Quality-gate `FQ2/FQ2F` follows current rule semantics. |

## Root-cause Decision

Primary root-cause disposition: `EVIDENCE_INSUFFICIENT`.

The current accepted lineage is sufficient to prove:

1. `turnover_rate` reached the snapshot as missing.
2. Scoring correctly counted zero coverage and zero traceability for that row.
3. Quality gate correctly surfaced `FQ2/warn` and derivative `FQ2F/warn` from
   the failed P1 field.

The current accepted lineage is not sufficient to prove:

1. the EID annual report lacks a numeric turnover-rate disclosure; or
2. the extractor missed a numeric turnover-rate disclosure.

It also does not fully prove or disprove pre-snapshot extractor/bundle mapping
or anchor loss. It only shows that no such loss is visible inside the accepted
snapshot-to-score-to-quality-gate chain.

Therefore no code implementation gate should open from this evidence alone.

## Next Entry Recommendation

Recommended next entry:

`Turnover rate same-source disclosure evidence gate`

Purpose:

- collect or identify same-lineage source text for the accepted
  `004393 / 2025 / eid / single_source_only` annual report;
- inspect only the relevant `§8` source excerpt for numeric turnover-rate
  disclosure;
- decide between `SOURCE_ABSENT_CONFIRMED` and
  `EXTRACTOR_MISSED_DISCLOSED_VALUE`;
- open a narrow implementation gate only if same-source evidence proves the
  disclosed value existed and the extractor failed to extract it.

Boundary:

- still no source policy change;
- no Eastmoney, fund-company website, CNINFO, fallback, broad PDF corpus, golden
  promotion, provider/LLM, release/readiness, PR, cleanup, delete, archive or
  ignore work;
- if a live EID or repository source-body command is required, it must be a
  separately bounded controlled evidence command and must record source lineage
  before being used as proof.
