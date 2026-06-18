# 004393 / 2025 Tracked Golden Content Write Plan

Date: 2026-06-13

Gate: `004393 / 2025 Tracked Golden Content Write Planning Gate`

Role scope: planning worker only.

Verdict: `PLAN_SOURCE_BODY_VERIFICATION_FIRST_NOT_READY`

## Goal

Decide whether the seven accepted candidate rows from the accepted same-year reviewed golden content evidence may proceed toward tracked golden content write, or whether controlled source-body verification must happen first.

## Non-goals

- Do not edit `reports/golden-answers/golden-answer-prefill-reviewed.md`.
- Do not edit `reports/golden-answers/golden-answer.json`.
- Do not edit fixture promotion state.
- Do not edit source, tests, README, `docs/design.md`, `docs/current-startup-packet.md` or `docs/implementation-control.md`.
- Do not run live EID, network, PDF, FDR, provider, LLM, `analyze`, `checklist`, readiness, release, PR, push or merge commands.
- Do not clean, delete, move, archive, stage or commit unrelated residue.
- Do not accept any row as tracked strict golden truth in this planning gate.

## Accepted input facts

- Current control truth says this is a `standard` planning-only gate and that the same-year reviewed golden content evidence accepted seven rows only as candidate rows with source-body residuals.
- `docs/design.md` defines strict correctness identity as `fund_code + report_year + field_name + sub_field`; same-fund cross-year rows may coexist, and missing same-year golden rows must not be substituted with other years.
- `docs/golden-answer-instructions.md` and `docs/golden-answer-template.md` mark `fee_schedule` as skipped for the current comparable contract.
- `fund_agent/fund/golden_answer.py` parses reviewed Markdown, defaults legacy missing `report_year` to 2024 only, emits fund-level and record-level `report_year`, rejects duplicate `(fund_code, report_year, field_name, sub_field)` identities, and rewrites the full strict JSON from the reviewed Markdown input.
- `tests/fund/test_golden_answer.py` covers explicit `report_year: 2025`, same fund across years, duplicate fund-year rejection, duplicate same-year record rejection, and preservation of existing tracked golden rows.
- The accepted same-year reviewed golden content controller judgment states that no primary-source verification claim was accepted because the gate did not read the 2025 annual-report body directly and did not authorize PDF/network/live commands.
- Candidate rows came from `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md`; that artifact is parser-valid and declares `report_year: 2025`.
- Completed plan reviews `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-review-mimo-20260613.md` and `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-review-ds-20260613.md` require amendments for repository-bounded source reads, pre-verification availability/live authorization, row-level partial acceptance, field-level match criteria, explicit JSON build assertions, existing-content preservation, and value-level cross-check/restore safety.

## Row disposition table

| Row | Current accepted disposition | Future write eligibility |
|---|---|---|
| `basic_identity.fund_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | May be considered only after controlled source-body verification confirms exact value and locator. |
| `basic_identity.fund_code` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | May be considered only after controlled source-body verification confirms exact value and locator. |
| `basic_identity.management_company` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | May be considered only after controlled source-body verification confirms exact value and locator. |
| `basic_identity.custodian` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | May be considered only after controlled source-body verification confirms exact value and locator. |
| `basic_identity.inception_date` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | May be considered only after controlled source-body verification confirms exact value and locator. |
| `product_profile.investment_objective` | `ACCEPT_CANDIDATE_WITH_MEDIUM_CONFIDENCE_AND_SOURCE_BODY_RESIDUAL` | May be considered only after controlled source-body verification confirms the candidate value appears verbatim as a normalized substring; keep `medium` unless verification justifies a different reviewed confidence. |
| `benchmark.benchmark_name` | `ACCEPT_CANDIDATE_WITH_SOURCE_BODY_RESIDUAL` | May be considered only after controlled source-body verification confirms formula exactness and locator. |
| `fee_schedule.management_fee` | `REJECT_FOR_THIS_GATE` | Excluded. It must not enter any tracked write scope unless a separate fee-row contract/source-owner clarification gate accepts it. |
| `fee_schedule.custody_fee` | `REJECT_FOR_THIS_GATE` | Excluded. It must not enter any tracked write scope unless a separate fee-row contract/source-owner clarification gate accepts it. |

## Decision: source-body verification first vs direct tracked write implementation

Decision: controlled source-body verification must happen before tracked golden content write.

Rationale:

- Candidate-level acceptance is not enough for a correctness oracle. Golden answer rows drive `FQ1/block` correctness conflicts; writing rows with unclosed source-body residuals would turn plausible candidate values into blocking truth.
- The accepted evidence explicitly says the 2025 annual-report body was not read and no primary-source verification claim was accepted.
- The project rules require numeric and factual judgments to be traceable to source evidence. Current rows have locators, but the body was not verified inside the accepted gate.
- The safest route is to verify exact row values and locators against the 2025 annual-report body through an explicitly authorized controlled gate, then open a separate tracked write implementation gate.

Direct tracked write implementation from candidate-level acceptance is rejected for this gate.

## Proposed implementation/write scope if applicable

This plan does not authorize direct write implementation.

Recommended next gate: `004393 / 2025 Controlled Source-body Verification Gate`.

Prerequisite before opening that gate:

- Confirm the `004393 / 2025` annual-report body is available through `FundDocumentRepository.load_annual_report()` or an equivalent repository-bounded path without new live access; or
- include a separately authorized live EID sub-slice as the first step of the verification gate; and
- stop before verification if neither repository-bounded no-new-live access nor separately authorized live EID access is available.

Minimum controlled source-body verification scope:

- Read only the 2025 annual-report body for `004393` through `FundDocumentRepository.load_annual_report()` or an equivalent repository-bounded path.
- Do not read PDFs or annual-report files directly from the filesystem unless a separate data-source gate explicitly authorizes that access pattern.
- Verify only the seven accepted candidate rows listed above.
- Confirm each row's exact `expected_value`, confidence, and source locator.
- Use row-level partial acceptance: each row may be verified, deferred or rejected independently; one row mismatch must not block independently verified rows.
- For `product_profile.investment_objective`, confirm the candidate value appears verbatim in the source body after whitespace normalization; do not require the verification worker to re-extract or re-litigate full span boundaries.
- For `benchmark.benchmark_name`, confirm formula characters, percentage weights, index names and currency-adjustment wording exactly.
- Keep the two fee rows excluded.
- Write only verification evidence/review/controller artifacts under `docs/reviews/` if that future gate authorizes them.

Field-level match criteria:

- `basic_identity.fund_name`, `basic_identity.management_company` and `basic_identity.custodian`: whitespace-normalized exact match against the source-body table/text value.
- `basic_identity.fund_code`: exact string match to `004393`; no normalization beyond trimming outer whitespace.
- `basic_identity.inception_date`: normalized date equality; the candidate `2022年8月8日` and an equivalent source value normalized to `2022-08-08` may match.
- `product_profile.investment_objective`: source body must contain the candidate value as a contiguous substring after whitespace normalization; this is not a full span re-extraction.
- `benchmark.benchmark_name`: character-exact match after trimming outer whitespace; internal whitespace, operator, punctuation, percentage weight, index name or currency-adjustment wording deviations must be recorded as mismatch diffs.

Conditional future tracked write implementation scope, only after source-body verification controller acceptance:

- Implementation worker allowed write set:
  - `reports/golden-answers/golden-answer-prefill-reviewed.md`
  - `reports/golden-answers/golden-answer.json`
  - `docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-evidence-20260613.md`
- Reviewer/controller write set:
  - `docs/reviews/mvp-004393-2025-tracked-golden-content-write-review-mimo-20260613.md`
  - `docs/reviews/mvp-004393-2025-tracked-golden-content-write-review-ds-20260613.md`
  - `docs/reviews/mvp-004393-2025-tracked-golden-content-write-controller-judgment-20260613.md`
- Content edit shape:
  - Add or update exactly one `## 004393 ...` reviewed Markdown block with fenced `golden-answer-metadata` containing `report_year: 2025`, unless source-body verification explicitly chooses a different merge shape.
  - Include only rows accepted by source-body verification.
  - Exclude all `fee_schedule.*` rows unless a separate accepted fee-row gate exists.
  - Build `reports/golden-answers/golden-answer.json` from the reviewed Markdown path; do not hand-edit JSON.
  - Before rebuilding JSON, create a temporary backup of the current `reports/golden-answers/golden-answer.json` or use an equivalent explicitly authorized Git restoration safety path.
  - After rebuilding JSON, compare each new or updated `004393 / 2025` record value against the accepted source-body verification artifact; restore the prebuild JSON and stop if any value-level cross-check fails.
  - Do not edit fixture promotion state.

## Validation matrix

| Check | Future gate | Command / method | Expected result |
|---|---|---|---|
| Candidate parser smoke | Source-body verification or write planning | `uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import parse_golden_answer_markdown; p=Path('docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md'); funds=parse_golden_answer_markdown(p.read_text(encoding='utf-8')); f=funds[0]; assert f.fund_code=='004393'; assert f.report_year==2025; assert len(f.records)==9; assert len({(r.fund_code,r.report_year,r.field_name,r.sub_field) for r in f.records})==9"` | Candidate source remains parser-valid and same-year. |
| Source-body availability prerequisite | Controlled source-body verification | Confirm `FundDocumentRepository.load_annual_report()` or equivalent repository-bounded path can access `004393 / 2025` without new live access, or confirm the gate includes a separately authorized live EID sub-slice | Verification does not begin unless repository-bounded no-new-live access or separately authorized live access is available. |
| Source-body row verification | Controlled source-body verification | Repository-bounded body read for `004393 / 2025`; row-by-row comparison using the field-level match criteria above | Each row is independently verified, deferred or rejected; verified rows may proceed independently. |
| Fee exclusion | Source-body verification and write implementation | Programmatic row-key check over proposed Markdown/JSON | No `fee_schedule.management_fee` or `fee_schedule.custody_fee` rows unless separate accepted fee gate is cited. |
| Reviewed Markdown parse | Write implementation | `uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import parse_golden_answer_markdown; funds=parse_golden_answer_markdown(Path('reports/golden-answers/golden-answer-prefill-reviewed.md').read_text(encoding='utf-8')); matches=[f for f in funds if f.fund_code=='004393' and f.report_year==2025]; assert len(matches)==1"` | Exactly one `004393 / 2025` fund block is parser-visible. |
| Prebuild JSON backup / restore safety | Write implementation | Copy current `reports/golden-answers/golden-answer.json` to a temporary backup path before build, or record an equivalent explicitly authorized Git restoration safety path | A known-good prebuild JSON can be restored before stopping if build or value cross-check fails. |
| Strict JSON build | Write implementation | `uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import build_golden_answer_json; result=build_golden_answer_json(input_path=Path('reports/golden-answers/golden-answer-prefill-reviewed.md'), output_path=Path('reports/golden-answers/golden-answer.json')); assert result.fund_count > 0; assert result.record_count > 0; print(result)"` | JSON is rebuilt from reviewed Markdown without schema error and with explicit build-result assertions. |
| Strict JSON load | Write implementation | `uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import load_golden_answer_json; funds=load_golden_answer_json(Path('reports/golden-answers/golden-answer.json')); matches=[f for f in funds if f.fund_code=='004393' and f.report_year==2025]; assert len(matches)==1"` | Loader sees the same-year strict golden block. |
| Existing content preservation | Write implementation | After Markdown to JSON rebuild, load baseline JSON from `HEAD` and working-tree JSON; assert every non-target `(fund_code, report_year, field_name, sub_field)` identity and its `expected_value`, `confidence` and `source` are unchanged | Existing non-target fund/year/record identities and values are preserved exactly. |
| Accepted value cross-check | Write implementation | Compare every new or updated `004393 / 2025` record's field, sub_field, expected_value, confidence and source against the accepted source-body verification artifact | Tracked JSON values match source-body verification output exactly; on failure restore prebuild JSON and stop. |
| No tracked-output overwrite accident | Write implementation | Compare `git show HEAD:reports/golden-answers/golden-answer.json` with working tree JSON by `(fund_code, report_year, field_name, sub_field)` and value-level content | Only source-body-accepted `004393 / 2025` keys are added or changed; unrelated existing keys and values are unchanged. |
| Targeted parser/build tests | Write implementation | `uv run pytest tests/fund/test_golden_answer.py -q` | Existing parser/build/year-aware contract remains green. |
| Correctness/gate targeted tests | Write implementation, if affected | `uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` | Score/quality semantics remain year-aware; no readiness claim. |
| Boundary diff check | Write implementation | `git diff --name-only -- reports/golden-answers/golden-answer-prefill-reviewed.md reports/golden-answers/golden-answer.json docs/reviews/mvp-004393-2025-tracked-golden-content-write-implementation-evidence-20260613.md` plus `git diff --name-only` review | Diff is limited to the accepted write set; no fixture promotion, source, tests, README, design or control-doc edits unless separately authorized. |

## Review plan

- Source-body verification gate requires MiMo review plus DS review before controller judgment.
- Any later tracked golden content write implementation gate requires MiMo review plus DS review before controller judgment.
- Reviewers must explicitly check row identity, `report_year: 2025`, fee-row exclusion, source-body verification lineage, JSON build provenance, and no unrelated tracked output changes.
- Reviewers must also check the source-body verification artifact against the written Markdown/JSON at value level and confirm existing non-target golden content was preserved.
- Controller judgment must state whether rows become tracked strict golden truth, remain candidate rows, or are deferred/rejected.

## Stop conditions

- Stop before source-body verification if the 2025 annual-report body cannot be loaded through `FundDocumentRepository.load_annual_report()` or an equivalent repository-bounded path without new live access and no separately authorized live EID sub-slice exists.
- Stop for any individual row that cannot be matched under the field-level criteria above; that row must be deferred or rejected independently, while verified rows may proceed independently.
- Stop for `product_profile.investment_objective` only if the candidate value is not present as a normalized verbatim substring; do not stop solely because full free-text span boundaries are not mechanically recoverable.
- Stop if `benchmark.benchmark_name` formula differs in any material character, weight, index name or currency-adjustment wording.
- Stop if either rejected fee row appears in the proposed write scope without a separate accepted fee-row contract/source-owner clarification gate.
- Stop if a write implementation would hand-edit `golden-answer.json` instead of rebuilding it from reviewed Markdown.
- Stop if JSON rebuild deletes or mutates unrelated existing tracked golden rows.
- Stop and restore the prebuild `golden-answer.json` if value-level cross-check against the source-body verification artifact fails.
- Stop if fixture promotion, release/readiness, live/provider/LLM/analyze/checklist/PR/push/merge, source/test/README/design/control-doc edits, or cleanup actions are attempted inside this route without separate authorization.

## Residuals

| Residual | Owner | Destination |
|---|---|---|
| Seven accepted candidate rows still need source-body verification before tracked truth. | Golden content/source owner | `004393 / 2025 Controlled Source-body Verification Gate` |
| Source-body access may require new live EID authorization if no repository-bounded no-new-live access exists. | Controller / next gate planner | Verification gate prerequisite or separately authorized live EID sub-slice. |
| Two fee rows are rejected for this route. | Golden contract/source owner | Separate fee-row contract/source-owner clarification gate, if needed. |
| Deferred candidate families remain out of scope. | Golden content/source owner | Separate reviewed candidate/source-body gates. |
| Fixture promotion remains year-blind/unresolved. | Fixture promotion owner | Separate fixture promotion design/evidence gate. |
| Release/readiness remains `NOT_READY`. | Release owner | Future readiness rollup after content and promotion residuals close. |

## Recommended next entry

Recommended next entry:

```text
004393 / 2025 Controlled Source-body Verification Gate
```

Prerequisite: before opening that gate, confirm repository-bounded no-new-live access to the `004393 / 2025` annual-report body or include a separately authorized live EID sub-slice as the gate's first step. Stop if neither condition is authorized or available.

Do not open a tracked golden content write implementation gate until a controller judgment accepts source-body verification for the exact rows to be written.
