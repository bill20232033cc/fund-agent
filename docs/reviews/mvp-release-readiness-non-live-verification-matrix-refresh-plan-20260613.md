# Release-readiness Non-live Verification Matrix Refresh Plan

Date: 2026-06-13

Role: planning worker

Gate: `Release-readiness Non-live Verification Matrix Refresh Planning Gate`

Classification: `standard`

## Goal

Refresh the previously accepted deterministic non-live verification matrix so
the next evidence gate can account for the latest accepted facts:

- `004393 / 2025` has exactly seven accepted tracked golden rows.
- The year-aware fixture promotion parser/schema is accepted.
- The exact `004393 / 2025` fixture promotion manifest is accepted.
- Downstream preflight consumes the exact manifest and does not cross-apply it
  to `004393 / 2024`.
- Residual rollup is accepted at `4590e3b`.
- Release/readiness remains `NOT_READY`.

The output of this planning gate is only a code-generation-ready plan for a
later evidence artifact under `docs/reviews/`.

## Non-goals

This plan does not authorize:

- implementation, source, test, runtime, golden-answer, fixture, manifest,
  README or design edits;
- live/provider/LLM/network/PDF/FDR/FundDocumentRepository acquisition;
- `fund-analysis analyze`, `fund-analysis analyze-annual-period`,
  `fund-analysis checklist`, golden generation/build, readiness, release, PR,
  push, merge or cleanup commands;
- fixture/golden/readiness promotion beyond already accepted facts;
- treating untracked residue, local PDFs, reports or historical artifacts as
  proof;
- changing release/readiness from `NOT_READY`.

## Inputs And Accepted Facts

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth and gate classification rules. |
| `docs/current-startup-packet.md` | Current startup truth: active gate is this planning gate; `NOT_READY` preserved. |
| `docs/implementation-control.md` | Control truth for accepted checkpoints and next entry. |
| `docs/design.md` relevant golden/readiness/source policy sections | Design truth for year-aware golden identity, source policy and readiness non-goals. |
| `docs/reviews/mvp-release-readiness-residual-rollup-after-fixture-manifest-evidence-controller-judgment-20260613.md` | Latest accepted rollup at `4590e3b`. |
| `docs/reviews/mvp-release-readiness-non-live-verification-plan-controller-judgment-20260612.md` | Prior accepted matrix planning boundary. |
| `docs/reviews/mvp-release-readiness-non-live-verification-repaired-evidence-controller-judgment-20260612.md` | Prior repaired matrix evidence acceptance. |

Accepted fact summary:

| Fact | Matrix impact |
|---|---|
| Seven rows are accepted tracked golden content only for `004393 / 2025`. | Add explicit row-scope and identity assertions. |
| Fee rows, `turnover_rate`, skipped/deferred rows remain excluded. | Add negative row assertions and residual preservation. |
| Golden identity is `fund_code + report_year + field_name + sub_field`. | Matrix must reject cross-year reuse as proof. |
| Year-aware fixture promotion parser requires exact `(fund_code, report_year)`. | Add parser/schema guard row. |
| Accepted manifest is exact `004393 / 2025` with no legacy fund-code-only state. | Add manifest JSON identity guard. |
| Downstream preflight consumes exact manifest for 2025 and not 2024. | Add downstream exact-year and wrong-year guard. |
| Rollup closes only exact manifest residual, not readiness. | Add `NOT_READY` / residual statement guard. |

## Proposed Refreshed Matrix Rows

The next evidence gate should preserve prior V0-V10 and add V11-V15. It should
execute rows in order and stop on any prohibited live/provider/readiness
behavior.

| ID | Command | Evidence type | Expected assertion |
|---|---|---|---|
| V0 | `test -f tests/fund/test_annual_evidence.py && test -f tests/fund/test_annual_period_report.py && test -f tests/services/test_fund_analysis_service.py && test -f tests/ui/test_cli.py && test -f tests/services/test_execution_contract.py && test -f tests/services/test_fund_analysis_service_llm.py && test -f tests/services/test_llm_run_artifacts.py && test -d tests/host && test -d tests/agent && test -f tests/fund/test_golden_answer.py && test -f tests/fund/test_golden_readiness_preflight.py && test -f reports/golden-answers/golden-answer.json && test -f docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json` | path guard | Required deterministic test/data/artifact paths exist; no readiness claim from existence alone. |
| V1 | `git status --branch --short` | metadata | Branch/ahead/dirty state captured; branch divergence is metadata only. |
| V2 | `git status --short` | metadata | Current tracked/untracked state captured; accepted residue routes preserved. |
| V3 | `git diff --name-only` | metadata | No unauthorized tracked source/tests/runtime/golden/manifest/fixture/README/design drift before evidence artifact write. |
| V4 | `git diff --check` | whitespace/static | Exit 0. |
| V5 | `uv run ruff check fund_agent tests` | deterministic lint | Exit 0. |
| V6 | `uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q` | focused deterministic fund tests | Exit 0. |
| V7 | `uv run pytest tests/fund/test_annual_evidence.py tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py::test_multi_year_annual_analysis_maps_service_request_to_fund_scope tests/ui/test_cli.py::test_analyze_annual_period_cli_calls_multi_year_service -q` | deterministic annual-period product tests | Exit 0. |
| V8 | `uv run pytest tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/services/test_llm_run_artifacts.py tests/host tests/agent -q` | Service/Host/Agent boundary tests | Exit 0. |
| V9 | `uv run pytest -q` | broad deterministic test pass | Exit 0. |
| V10 | `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | project coverage floor | Exit 0; coverage floor remains sanity check only, not readiness proof. |
| V11 | `uv run pytest tests/fund/test_golden_answer.py::test_parse_golden_answer_markdown_accepts_explicit_report_year_metadata tests/fund/test_golden_answer.py::test_load_golden_answer_json_allows_same_fund_code_different_report_year tests/fund/test_extraction_score.py::test_compare_snapshot_correctness_marks_current_year_not_covered -q` | year-aware golden identity tests | Same fund across years remains distinct; missing same-year golden is `year_not_covered`, not cross-year comparison. |
| V12 | `uv run python -m json.tool docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json` | manifest syntax | Accepted manifest parses as JSON; no mutation. |
| V13 | `uv run python -c "import json; from pathlib import Path; payload=json.loads(Path('reports/golden-answers/golden-answer.json').read_text(encoding='utf-8')); expected={('basic_identity','fund_name'),('basic_identity','fund_code'),('basic_identity','management_company'),('basic_identity','custodian'),('basic_identity','inception_date'),('product_profile','investment_objective'),('benchmark','benchmark_name')}; funds=[f for f in payload['funds'] if f.get('fund_code')=='004393' and f.get('report_year')==2025]; assert len(funds)==1; records=funds[0]['records']; flat=[r for r in payload['records'] if r.get('fund_code')=='004393' and r.get('report_year')==2025]; assert payload.get('record_count')==len(payload.get('records', [])); assert len(records)==7; assert len(flat)==7; assert all(r.get('fund_code')=='004393' and r.get('report_year')==2025 for r in records); assert all(r.get('fund_code')=='004393' and r.get('report_year')==2025 for r in flat); assert {(r.get('field_name'), r.get('sub_field')) for r in records}==expected; assert {(r.get('field_name'), r.get('sub_field')) for r in flat}==expected; assert not funds[0].get('skipped_fields'); assert not any(r.get('field_name') in {'fee_schedule','turnover_rate'} for r in records + flat); print('004393_2025_row_scope_ok')"` | static golden row-scope assertion | Exactly seven accepted nested and top-level rows for `004393 / 2025`; every row preserves record-level `fund_code=004393` and `report_year=2025`; no fee rows, `turnover_rate` or skipped fields accepted. |
| V14 | `uv run python -c "from pathlib import Path; from fund_agent.fund.golden_readiness_preflight import _load_fixture_promotion_states; states=_load_fixture_promotion_states(Path('docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json')); assert states is not None; assert states.fund_year_states == {('004393', 2025): 'promoted_fixture'}; assert states.legacy_fund_states == {}; print('fixture_promotion_manifest_year_aware_ok')"` | parser/manifest identity assertion | Manifest has exact `004393 / 2025` fund-year state and no legacy fund-code-only promotion state. |
| V15 | `uv run pytest tests/fund/test_golden_readiness_preflight.py::test_preflight_accepts_year_aware_fixture_promotion_matching_year tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_fixture_promotion_wrong_year tests/fund/test_golden_readiness_preflight.py::test_preflight_blocks_legacy_fund_code_only_fixture_promotion tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_duplicate_year_aware_fixture_promotion_entry tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_year_aware_fixture_promotion_unknown_field tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_year_aware_fixture_promotion_wrong_identity -q` | downstream preflight exactness tests | Exact-year promotion passes; wrong-year, legacy, duplicate, unknown-field and wrong-identity cases fail closed. |

## Failure Classification

| Condition | Classification |
|---|---|
| Any command attempts live/network/provider/PDF/FDR/FundDocumentRepository acquisition or readiness/release/PR behavior. | `blocking_question`; stop immediately. |
| V0 missing path for accepted matrix inputs. | `blocker` unless controller identifies superseding accepted path before execution. |
| V1/V2 show unrelated accepted residue only. | `accepted_residual`; not proof and not blocker. |
| V3 shows unauthorized tracked source/tests/runtime/golden/manifest/fixture/README/design drift. | `blocker`. |
| V4-V15 non-zero exit. | `blocker` unless evidence records exact failing path, proves it is unrelated to this gate, and assigns owner/next gate. |
| V10 exceeds 10 minutes after V6-V9 pass. | `material_residual`; partial coverage output is not pass. |
| V13 row count differs from seven, includes skipped fields, fee rows or `turnover_rate`. | `blocker`; do not reinterpret as readiness progress. |
| V14 finds legacy fund-code-only state or non-exact identity. | `blocker`. |
| V15 wrong-year/legacy guard does not fail closed. | `blocker`. |

## Allowed Evidence Commands For Next Gate

Allowed commands are exactly the proposed V0-V15 commands plus this static audit
command:

```bash
rg -n --count-matches -e '(httpx|requests|socket|network|Eid|EID|FDR|FundDocumentRepository|load_annual_report|download|provider|LLM|--use-llm|akshare|fund-analysis analyze|fund-analysis checklist|readiness|release|gh pr|git push)' tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py tests/fund/test_extraction_score.py tests/fund/test_annual_evidence.py tests/fund/test_annual_period_report.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/services/test_llm_run_artifacts.py tests/host tests/agent
```

The evidence artifact must record command, exit status, short output and
live/prohibited-behavior assessment for every command.

## Forbidden Commands And Paths

Forbidden commands/actions:

- live EID, network, DNS, socket, HTTP probes;
- PDF download, PDF body parsing, FDR or FundDocumentRepository acquisition;
- provider, LLM, `--use-llm`, endpoint or runtime-budget probes;
- `fund-analysis analyze`, `fund-analysis analyze-annual-period`,
  `fund-analysis checklist`;
- `fund-analysis golden-build`, golden-prefill, fixture projection, baseline
  promotion, readiness promotion;
- readiness, release, GitHub PR, push, merge, mark-ready, approval, review
  request or external comment;
- cleanup, delete, move, archive, ignore-rule, import, promote;
- worker-initiated `git add`, `git commit`, `git stash`, `git merge`.

Forbidden edits:

- `fund_agent/`
- `tests/`
- `reports/golden-answers/`
- `docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json`
- fixtures under `tests/fixtures/`
- README files
- `docs/design.md`
- `docs/current-startup-packet.md` and `docs/implementation-control.md` before
  controller acceptance/control sync
- cache, PDFs, generated reports, lockfiles, `.gitignore`

Allowed next evidence writes:

- one evidence artifact under `docs/reviews/`;
- DS review artifact under `docs/reviews/`;
- MiMo review artifact under `docs/reviews/`;
- controller judgment under `docs/reviews/`;
- post-acceptance control-doc sync only after controller acceptance and local
  accepted checkpoint.

## Required Evidence Artifact Sections

The next evidence artifact must include:

- scope statement confirming no live/provider/LLM/analyze/checklist/readiness/
  release/PR command ran;
- accepted input list and checkpoint lineage through `4590e3b`;
- command log for V0-V15 and static audit;
- file-state table before and after evidence write;
- row-scope table for the seven `004393 / 2025` accepted rows;
- negative assertion table for fee rows, `turnover_rate`, skipped/deferred rows,
  other funds and other years;
- manifest identity table for exact `004393 / 2025`;
- downstream exact-year and wrong-year preflight result table;
- failure classification table;
- residual owner table;
- explicit `NOT_READY` statement;
- exact next entry recommendation.

## Planning-gate Static Checks

The controller performed only static planning checks before this plan write:

```text
rg -n "<V11/V15 test node names>" tests/fund
test -f docs/reviews/mvp-fixture-promotion-state-manifest-20260613.json
test -f reports/golden-answers/golden-answer.json
test -f tests/fund/test_golden_answer.py
test -f tests/fund/test_golden_readiness_preflight.py
test -f tests/fund/test_extraction_score.py
git status --branch --short
git diff --check
```

These checks verify referenced paths/test nodes exist. They do not execute the
refresh matrix and do not prove readiness.

## Review Requirements

Required independent reviews before controller acceptance:

- AgentDS review;
- AgentMiMo review.

Review focus:

- whether V11-V15 directly cover the new accepted facts without overclaiming;
- whether the matrix remains deterministic and non-live;
- whether golden/manifest reads are static and non-mutating;
- whether wrong-year and legacy fail-closed assertions are explicit;
- whether fee rows, `turnover_rate`, skipped/deferred rows, other funds and
  other years remain residual;
- whether untracked residue is not used as proof;
- whether `NOT_READY` is preserved.

Controller may accept without one reviewer only by recording reviewer
unavailability and explicit review-channel risk.

## Stop Conditions

Stop the next evidence gate immediately if:

- any command attempts prohibited live/provider/network/PDF/FDR/LLM/analyze/
  checklist/readiness/release/PR behavior;
- V0 shows required accepted paths are missing;
- unauthorized tracked source/tests/runtime/golden/manifest/fixture/README/design
  drift is present;
- V13, V14 or V15 contradict exact `004393 / 2025` identity, seven-row scope, or
  2024 non-cross-application;
- dependency resolution requires network repair or installation not separately
  authorized;
- a result would require changing source/tests/runtime/golden/manifest/fixture
  content to proceed;
- any worker action would stage, commit, push, merge, clean or mutate external
  state.

## Exact Next Entry Recommendation

If this plan receives DS + MiMo review and controller acceptance, the exact next
mainline entry should be:

`Release-readiness Non-live Verification Matrix Refresh Evidence Gate`

Purpose:

- execute the refreshed deterministic non-live matrix V0-V15;
- record direct evidence for accepted `004393 / 2025` seven-row scope,
  year-aware parser/manifest identity and downstream exact-year preflight
  behavior;
- preserve `NOT_READY`;
- route any blocker to a named blocker-fix planning gate instead of modifying
  source/tests/runtime/golden/manifest/fixture content.

Deferred entries remain:

- release/readiness execution or release claim;
- PR/push/merge/mark-ready;
- live/provider/LLM/analyze/checklist commands;
- fee-row clarification;
- `turnover_rate` policy changes;
- other fund/year sample expansion;
- cleanup/archive/ignore disposition.
