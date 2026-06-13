# Turnover Rate Regulatory Applicability Narrow Fix Planning Gate

Date: 2026-06-12

Gate: `Turnover rate regulatory applicability narrow fix planning gate`

Classification: `standard`

Status: planning artifact

## Objective

Plan the smallest code change that prevents non-applicable `turnover_rate`
snapshot rows from entering P1 coverage/traceability scoring, while preserving
`FQ2/FQ2F` warning semantics for future reports where `turnover_rate` is truly
applicable.

This is a planning artifact only. It does not modify source, tests, runtime
behavior, source acquisition policy, release/readiness state or PR state.

## Accepted Inputs

- Quality warning identity evidence accepted `FQ2/warn turnover_rate` and
  derivative `FQ2F/warn 004393`:
  `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md`
- Root-cause evidence accepted the snapshot-to-score-to-quality chain as
  internally consistent but source/extractor unresolved:
  `docs/reviews/mvp-turnover-rate-root-cause-evidence-controller-judgment-20260612.md`
- Regulatory applicability evidence accepted
  `REGULATORY_APPLICABILITY_SCORING_GAP_CONFIRMED`:
  `docs/reviews/mvp-turnover-rate-regulatory-applicability-evidence-controller-judgment-20260612.md`

## Root-cause Decision

The accepted warning identity remains real for the current code path, but the
root cause is not extractor failure by default.

Root cause for `004393 / 2025`:

`turnover_rate` scoring/applicability is too broad for pre-effective-date annual
reports and non-annual reports.

## Cutoff Decision For This Fix

Use report-year semantics for the first narrow fix:

- `report_year < 2026`: `turnover_rate` is not applicable.
- `report_year >= 2026`: `turnover_rate` remains applicable unless explicit
  non-annual report metadata says otherwise.

Rationale:

- current snapshot scoring has stable `report_year` on every row;
- current quality-gate sample path is annual-report based and does not carry a
  durable `publication_date` or template version;
- the regulatory evidence proves `004393 / 2025` is pre-effective under
  report-year semantics;
- publication-date or source-template-version cutoff would require additional
  source metadata and is not the smallest safe fix.

Non-annual report rule:

- if a future snapshot row carries explicit report-kind metadata such as
  `document_kind`, `report_type` or `source_kind`, and that value is not
  `annual_report`, `turnover_rate` should be excluded as not applicable;
- implementation may only consume report-kind metadata that is explicitly
  present on the snapshot row and already defined as row-level metadata;
- it must not infer report kind from anchors, source provenance, file names,
  paths, fund source names or untracked artifacts;
- absent row-level report-kind metadata must not be guessed. The current
  annual-report path can rely on `report_year` alone.

## Planned Implementation Surface

Allowed source file:

- `fund_agent/fund/extraction_score.py`

Allowed tests:

- `tests/fund/test_extraction_score.py`
- `tests/services/test_fund_analysis_service.py`

Documentation follow-up:

- inspect `fund_agent/fund/README.md`; update only if it documents quality score
  field applicability or `turnover_rate` quality semantics.

Explicitly excluded:

- `fund_agent/fund/extractors/manager_ownership.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/quality_gate.py`
- repository/cache/downloader/source acquisition modules
- fallback, Eastmoney, CNINFO, fund-company website, provider/LLM, golden,
  readiness, release, PR and cleanup surfaces

## Code-generation-ready Plan

### Step 1. Add Turnover Applicability Constants

In `fund_agent/fund/extraction_score.py`, add explicit constants near existing
field/applicability constants:

- `TURNOVER_RATE_FIELD_NAME = "turnover_rate"`
- `TURNOVER_RATE_DISCLOSURE_EFFECTIVE_REPORT_YEAR = 2026`
- `TURNOVER_RATE_APPLICABILITY_CONTRACT_ID = "turnover_rate_disclosure_applicability.v1"`
- `TURNOVER_RATE_PRE_EFFECTIVE_REASON = "turnover_rate_pre_effective_report_year"`
- `TURNOVER_RATE_NON_ANNUAL_REASON = "turnover_rate_non_annual_report"`
- `APPLICABILITY_STATUS_NOT_APPLICABLE_EXCLUDED = "not_applicable_excluded"`
- `DENOMINATOR_EFFECT_EXCLUDED_NO_REPLACEMENT_ISSUE = "excluded_no_replacement_issue"`

Keep `FIELD_PRIORITY_BY_NAME["turnover_rate"] = "P1"` unchanged. Applicability
must be decided before scoring, not by weakening the field priority.

### Step 2. Add A Single Applicability Helper

Add private helper:

`_is_non_applicable_turnover_rate_record(record: Mapping[str, object]) -> bool`

Rules:

1. return `False` unless `field_name == "turnover_rate"`;
2. if explicit report-kind metadata exists and is not annual:
   - check `document_kind`, `report_type`, then `source_kind`;
   - values such as `quarterly_report`, `interim_report`, `semiannual_report`,
     `q1_report`, `q2_report`, `q3_report`, `quarterly` are non-applicable;
   - value `annual_report` is annual;
3. parse `report_year` with existing snapshot integer validation semantics;
4. return `True` when `report_year < 2026`;
5. fail closed when `report_year` is missing or invalid: return `False` and let
   existing validation/score paths surface the malformed row.

Do not infer non-annual status from filenames, paths, fund code, report text or
untracked residue.

### Step 3. Exclude Non-applicable Turnover Rows From Scoring

Extend `_scorable_records(...)` with:

```python
and not _is_non_applicable_turnover_rate_record(record)
```

Expected effect:

- field aggregate scoring excludes pre-2026 `turnover_rate`;
- fund-level `p1_failed_fields` excludes pre-2026 `turnover_rate`;
- `derive_fund_quality_records` excludes pre-2026 `turnover_rate` from
  `missing_p1_fields` and `missing_field_rate`;
- `quality_gate.py` naturally stops emitting `FQ2/FQ2F` for that non-applicable
  row because no failed P1 score row/fund score remains.

Implementation requirement:

- the exclusion must be applied through the shared `_scorable_records(...)`
  path;
- implementation evidence must explicitly verify the effect reaches all three
  consumers:
  - `score_snapshot_records`;
  - `score_fund_records`;
  - `derive_fund_quality_records`.

### Step 4. Emit Field Applicability Decisions For Observability

Extend `derive_field_applicability_decisions(...)` via
`_fund_field_applicability_decisions(...)` so non-applicable `turnover_rate`
rows produce a `FieldApplicabilityDecision`.

Important implementation detail:

- remove or narrow the current early return that exits when
  `holdings_snapshot` is absent; `turnover_rate` decisions must still be emitted
  when no holdings decision exists.

Decision shape:

- `field_name="turnover_rate"`
- `applicability_status="not_applicable_excluded"`
- `reason_code`:
  - `turnover_rate_pre_effective_report_year` for `report_year < 2026`
  - `turnover_rate_non_annual_report` for explicit non-annual report-kind metadata
- `replacement_field_name=None`
- `contract_id="turnover_rate_disclosure_applicability.v1"`
- `denominator_effect="excluded_no_replacement_issue"`
- `excluded_non_applicable_fields=("turnover_rate",)`
- `replacement_issue_ids=()`

Do not emit `ScoreApplicabilityIssue` for this expected non-applicability. There
is no replacement evidence requirement analogous to bond risk evidence.

### Step 5. Preserve Existing Warn Semantics For Applicable Rows

Do not change `quality_gate.py`.

Keep existing manually constructed score behavior:

- if `score.json` contains a failed P1 `turnover_rate` field row and fund-level
  `p1_failed_fields=["turnover_rate"]`, quality gate should still emit
  `FQ2/warn` and derivative `FQ2F/warn`;
- this preserves future applicable-report warning semantics.

## Test Plan

### Unit Tests In `tests/fund/test_extraction_score.py`

Add or update tests:

1. `test_turnover_rate_pre_2026_is_excluded_from_scoring_denominator`
   - input: active fund, `report_year=2025`, missing `turnover_rate`;
   - expect:
     - `score_snapshot_records` has no `turnover_rate` row;
     - `score_fund_records(...)[0].p1_failed_fields == ()`;
     - `derive_fund_quality_records(...)[0].missing_p1_fields == ()`;
     - one `FieldApplicabilityDecision` with
       `reason_code="turnover_rate_pre_effective_report_year"`;
     - `derive_score_applicability_issues(...) == ()`.

2. `test_turnover_rate_pre_2026_exclusion_does_not_suppress_unrelated_p1_failures`
   - input: active fund, `report_year=2025`, missing `turnover_rate` plus another
     unrelated missing applicable P1 field such as `holder_structure`;
   - expect:
     - `turnover_rate` is excluded;
     - unrelated P1 failure remains visible in field score, fund score and
       fund quality.

3. `test_turnover_rate_2026_missing_remains_p1_fail`
   - input: active fund, `report_year=2026`, missing `turnover_rate`;
   - expect:
     - field score row exists for `turnover_rate`;
     - priority remains `P1`;
     - coverage/traceability fail;
     - fund-level `p1_failed_fields == ("turnover_rate",)`;
     - no non-applicable decision.

4. `test_turnover_rate_explicit_non_annual_report_kind_is_excluded`
   - input: missing `turnover_rate`, `report_year=2026`, explicit
     row-level `document_kind="quarterly_report"` or equivalent;
   - expect:
     - excluded from scoring;
     - decision reason `turnover_rate_non_annual_report`.

5. `test_turnover_rate_unknown_report_year_fails_closed`
   - input: missing/invalid `report_year` on `turnover_rate`;
   - expect:
     - no non-applicable exclusion is silently applied;
     - existing validation raises or keeps the record scorable according to
       current malformed-row behavior.

6. Existing bond/index applicability tests must continue to pass, and
   implementation should add a focused assertion if the early-return refactor in
   `_fund_field_applicability_decisions(...)` risks suppressing existing
   bond/index decisions.

### Service Test In `tests/services/test_fund_analysis_service.py`

Update the existing missing-turnover service test that currently expects
`FQ2/FQ2F` for missing turnover:

- keep the deterministic missing extracted field;
- keep `rabc_attribution.status == "missing"` and report note assertions;
- for the default pre-effective report year, assert no `FQ2` with
  `field_name == "turnover_rate"` and no derivative `FQ2F` caused by
  `turnover_rate`.

Do not remove the quality-gate semantics test in `tests/fund/test_quality_gate.py`
that manually supplies a failed `turnover_rate` score row. That test should
continue proving future applicable rows warn rather than block.

Implementation evidence must explicitly record that this manual failed-score
test still passes, because it protects the future applicable-report
`FQ2/FQ2F` semantics.

## Validation Matrix For Implementation Gate

Run after implementation:

```bash
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/services/test_fund_analysis_service.py -q
uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py tests/services/test_fund_analysis_service.py
git status --short
git status --branch --short
git diff --name-only
git diff --check
```

No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness or
release command is part of the implementation gate.

## Acceptance Criteria

Implementation can be accepted only if:

- pre-2026 `turnover_rate` no longer creates field-level P1 fail or derivative
  fund-level fail;
- pre-2026 `turnover_rate` exclusion does not suppress unrelated applicable P1
  failures in the same record set;
- 2026+ applicable `turnover_rate` missing rows still create P1 fail;
- explicit non-annual report-kind metadata excludes `turnover_rate`;
- field applicability decisions explain the exclusion;
- no replacement `ScoreApplicabilityIssue` is emitted for expected
  non-applicability;
- existing index/bond applicability behavior remains unchanged;
- existing quality-gate `FQ2/FQ2F` semantics remain unchanged for failed score
  rows that are truly applicable.

## Next Entry Recommendation

Next entry:

`Turnover rate regulatory applicability narrow fix implementation gate`

Implementation should use the allowed write set above and should not open
extractor, source acquisition, fallback, provider/LLM, strict golden,
release/readiness, PR or cleanup work.
