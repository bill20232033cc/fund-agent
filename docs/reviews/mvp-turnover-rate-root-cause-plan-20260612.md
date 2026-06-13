# Turnover Rate Extraction/Traceability Root-cause Planning Gate

Date: 2026-06-12

Gate: `Turnover rate extraction/traceability root-cause planning gate`

Classification: `standard`

Status: planning artifact

## Objective

Determine why accepted quality evidence reports `turnover_rate` with
`coverage_rate=0.0`, `traceability_rate=0.0`, `status=fail`, and why that creates
the accepted `FQ2/warn turnover_rate` plus derivative `FQ2F/warn 004393`.

This gate does not decide a code fix. It defines the evidence path that must
separate source absence, extraction miss, mapping loss, anchor loss, and score
interpretation before implementation is authorized.

## Inputs Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/extractors/manager_ownership.py`
- `fund_agent/fund/extraction_snapshot.py`
- `tests/fund/extractors/test_manager_ownership.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`

## Non-goals

- No source, test, runtime, provider, LLM, readiness, release, PR, fallback, or
  source-acquisition policy changes.
- No live EID, network, PDF download, FDR, provider, LLM, analyze, checklist,
  golden, readiness, release, curl, DNS, or socket command.
- No cleanup, delete, archive, import, ignore, stage, commit, push, PR, or merge.
- Do not use arbitrary report residue as proof. Only accepted, hash-matched
  evidence lineage may be used.
- Do not fold strict golden 2025 coverage, additional controlled-live sample
  evidence, release-readiness rollup, or provider/LLM readiness into this gate.

## Current Facts

### Control-truth Facts

- `docs/current-startup-packet.md` and `docs/implementation-control.md` identify
  the current gate as `Turnover rate extraction/traceability root-cause planning
  gate`.
- The preceding `Quality Warning Issue Identity Evidence Gate` is accepted at
  local checkpoint `08cdfe1`.
- Accepted identities include:
  - `FQ2/warn` for field `turnover_rate`.
  - derivative `FQ2F/warn` for fund `004393`.
  - `FQ0/info` with `year_not_covered`, which is deferred to strict golden
    2025 coverage/promotion planning and is not a turnover extractor root cause.

### Accepted Evidence Facts

The accepted identity evidence reports:

- Field score:
  - `field_group=manager`
  - `field_name=turnover_rate`
  - `priority=P1`
  - `records=1`
  - `covered_records=0`
  - `traceable_records=0`
  - `coverage_rate=0.0`
  - `traceability_rate=0.0`
  - `status=fail`
- Fund score for `004393`:
  - `p0_status=pass`
  - `p1_status=fail`
  - `p1_failed_fields=["turnover_rate"]`
  - `status=fail`

### Repo Facts

- `turnover_rate` is classified as `P1` in
  `fund_agent/fund/extraction_score.py`.
- `score_snapshot_records` counts coverage from record value coverage and
  traceability from `anchor_present`.
- A `P1` field-level fail creates `FQ2/warn` in
  `fund_agent/fund/quality_gate.py`.
- A `P1` fund-level fail creates derivative `FQ2F/warn` in
  `fund_agent/fund/quality_gate.py`.
- The current extractor path for turnover rate is:
  `extract_manager_ownership` -> `_build_turnover_rate` ->
  `StructuredFundDataBundle.turnover_rate` -> extraction snapshot field
  `manager.turnover_rate` -> extraction score -> quality gate.
- `_build_turnover_rate` has three meaningful branches:
  - no rate and no basis: missing field with no anchors;
  - basis-only: missing extraction mode with basis value and basis anchor;
  - rate present: direct extraction with rate value and anchors.
- `extraction_snapshot.py` includes `("manager", "turnover_rate")` in snapshot
  field order and derives `anchor_present` from whether an anchor exists.

## Hypotheses To Separate

| Hypothesis | What It Means | Evidence Required | Next Action If Proven |
| --- | --- | --- | --- |
| H1 source disclosure absent | The same accepted source lineage lacks a numeric turnover-rate disclosure. Basis-only disclosure remains absent under the current contract. | Hash-matched accepted snapshot/score plus same-lineage source excerpt showing no numeric turnover-rate disclosure in the relevant annual-report section. | No narrow code fix. Record residual/disposition and keep implementation closed. |
| H2 extractor missed disclosed value | The same accepted source lineage contains a numeric turnover-rate disclosure, but `_build_turnover_rate` did not produce a direct value. | Same-lineage source excerpt with numeric disclosure plus extractor/snapshot result showing missing or non-direct output. | Open narrow extractor implementation gate. |
| H3 mapping or field-normalization loss | The extractor produced the right semantic value, but the bundle, snapshot, or field name mapping lost it before scoring. | Compare extractor output, bundle field, and snapshot row for `manager.turnover_rate`; show value exists before snapshot but is absent or renamed in snapshot/score. | Open narrow mapping/snapshot implementation gate. |
| H4 anchor or traceability loss | The value exists but the anchor was dropped or not represented as `anchor_present=true`. | Show direct value with no anchor in snapshot, or anchors present before snapshot but lost in snapshot. | Open narrow anchor propagation implementation gate. |
| H5 quality-score interpretation issue | Snapshot row is correct, but scoring or quality-gate interpretation incorrectly produces zero coverage/traceability or warning severity. | Raw snapshot row has expected value/anchor while score row still reports zero or wrong status; compare against scoring thresholds and P1 warning rules. | Open narrow scoring/quality-gate implementation gate. |

## Evidence Gate Plan

### E0. Boundary and State Check

Run only local non-live state checks:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
```

Expected result: only the current planning artifact may be new for this gate.
Pre-existing unrelated untracked residue is not proof and must not be cleaned.

### E1. Accepted Evidence Lineage Check

Use `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md` as
the accepted evidence index. If the evidence artifact points to score, snapshot,
or quality-gate output files, first verify file size and SHA-256 against the
accepted artifact.

Decision rule:

- If size/hash match: the file may be used as accepted evidence lineage.
- If size/hash mismatch: do not use it; record `EVIDENCE_LINEAGE_MISMATCH`.
- If the file is missing: do not substitute arbitrary reports residue; record
  `EVIDENCE_LINEAGE_MISSING`.

### E2. Raw Snapshot and Score Row Extraction

From the accepted, hash-matched snapshot and score artifacts only, extract:

- Snapshot row where:
  - `fund_code == "004393"`
  - `report_year == 2025`
  - `field_group == "manager"`
  - `field_name == "turnover_rate"`
- Fields to record:
  - `extraction_mode`
  - `value`
  - `value_present`
  - `anchor_present`
  - `section_id`
  - `page`
  - `row_locator`
  - `note`
  - source provenance fields, if present
- Score rows to record:
  - field row for `manager.turnover_rate`
  - fund row for `004393`

Controller requirement: explicitly state whether the accepted score summary is
consistent with the raw snapshot row. If it is inconsistent, route to H5 before
considering source or extractor changes.

### E3. Static Chain Comparison

Compare the raw row against current code semantics:

- `extraction_mode=missing`, `value_present=false`, `anchor_present=false`:
  source absence or extractor miss remains unresolved until same-lineage source
  disclosure is checked.
- `extraction_mode=missing` with basis-only value/anchor:
  confirm whether current contract intentionally treats basis-only as not
  covering `turnover_rate`; if score still reports zero traceability, check H5.
- `extraction_mode=direct`, `value_present=false`:
  investigate value normalization or snapshot coverage logic.
- `extraction_mode=direct`, `value_present=true`, `anchor_present=false`:
  investigate anchor loss.
- extractor output direct with anchors, but snapshot row missing or renamed:
  investigate mapping/field-normalization loss.

### E4. Same-source Disclosure Check

Only inspect source text that is tied to the accepted evidence lineage.

Allowed evidence:

- same-lineage parsed annual-report section or source excerpt already recorded
  by the accepted artifacts;
- deterministic local fixture/excerpt whose provenance is explicitly tied to the
  accepted evidence path;
- a separately authorized controlled source-disclosure evidence gate, if the
  same-source body is not available locally.

Disallowed evidence:

- arbitrary PDFs, report directories, cache residue, or generated reports that
  are not hash/provenance matched to the accepted identity evidence;
- live source acquisition in this gate.

Decision rule:

- If same-lineage source text lacks numeric turnover-rate disclosure, classify
  H1.
- If same-lineage source text contains numeric turnover-rate disclosure and the
  extractor output is missing, classify H2.
- If source text cannot be established, classify `EVIDENCE_INSUFFICIENT` and do
  not open implementation.

### E5. Root-cause Disposition

The evidence gate must end with exactly one primary disposition:

| Disposition | Meaning | Next Gate |
| --- | --- | --- |
| `SOURCE_ABSENT_CONFIRMED` | Accepted source did not disclose a numeric turnover-rate value under current contract. | No implementation. Open residual/disposition or reporting-plan gate only if needed. |
| `EXTRACTOR_MISSED_DISCLOSED_VALUE` | Source disclosed the value; extractor failed to extract it. | Narrow extractor implementation gate. |
| `MAPPING_LOSS_CONFIRMED` | Extractor/bundle had value; snapshot/field mapping lost it. | Narrow mapping/snapshot implementation gate. |
| `ANCHOR_LOSS_CONFIRMED` | Value survived but traceability anchor was lost. | Narrow anchor propagation implementation gate. |
| `SCORE_INTERPRETATION_CONFIRMED` | Snapshot row was correct but score/gate interpreted it incorrectly. | Narrow score/quality-gate implementation gate. |
| `EVIDENCE_INSUFFICIENT` | Same-source evidence cannot prove source absence or code failure. | Controlled evidence collection gate, not implementation. |

## Narrow Implementation Entry Criteria

Implementation may open only if the evidence gate proves H2, H3, H4, or H5.

Allowed implementation surfaces must be selected by proven root cause:

- H2 extractor miss:
  - `fund_agent/fund/extractors/manager_ownership.py`
  - `tests/fund/extractors/test_manager_ownership.py`
  - relevant extractor fixtures only if already used by this extractor test path
- H3 mapping loss:
  - `fund_agent/fund/extraction_snapshot.py`
  - `tests/fund/test_extraction_snapshot.py`
- H4 anchor loss:
  - `fund_agent/fund/extractors/manager_ownership.py`
  - `fund_agent/fund/extraction_snapshot.py`
  - corresponding extractor/snapshot tests
- H5 score interpretation issue:
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/quality_gate.py`, only if issue construction semantics are
    proven wrong
  - corresponding score/quality-gate tests

Explicitly excluded from implementation:

- `FundDocumentRepository` source acquisition behavior;
- Eastmoney, CNINFO, fund-company website fallback;
- provider/LLM runtime;
- readiness/release/PR state;
- broad golden expansion beyond the accepted MVP sample path.

## Review Requirements For Evidence Gate

The root-cause evidence artifact should be independently reviewed by at least two
available reviewers. Reviews must check:

- whether source evidence is same-lineage, not arbitrary residue;
- whether each hypothesis is either proven, rejected, or left unresolved with a
  named blocker;
- whether any proposed implementation entry is directly supported by evidence;
- whether `FQ2F/warn 004393` is treated as derivative of field-level
  `turnover_rate`, not as a separate root cause;
- whether `FQ0/info year_not_covered` remains deferred to strict golden 2025
  planning and does not contaminate turnover root-cause analysis.

## Next Gate Recommendation

Next entry: `Turnover rate extraction/traceability root-cause evidence gate`.

Do not open implementation yet. Current accepted evidence proves issue identity
and score impact, but it does not yet prove whether the zero
coverage/traceability comes from source disclosure absence, extractor miss,
mapping loss, anchor loss, or score interpretation. Implementation is authorized
only after the evidence gate proves a code-rooted disposition.
