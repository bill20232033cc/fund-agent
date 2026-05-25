# Release Maintenance Report-Quality Baseline S0 Corpus Selection Evidence

> Date: 2026-05-25  
> Worker: AgentCodex specialist evidence worker  
> Gate: `release-maintenance report-quality baseline / Fact-Evidence contract plan accepted locally`  
> Scope: S0 corpus-selection evidence only; no code/test/renderer/FQ0-FQ6/Host/Agent/PR/commit work.

## Step Self-Check

- Truth sources read: `AGENTS.md`; `docs/design.md` current architecture boundary, `FundDocumentRepository` boundary, report-quality §5.4, Fact/Evidence §5.4.2, methodology matrix §5.4.3, fund type detection §6.5; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals / Active Gate Ledger.
- Accepted evidence chain read: report-quality baseline Fact/Evidence plan, MiMo review, DS review, and controller judgment artifacts dated 2026-05-25.
- Boundary: production annual-report access was only through `FundDocumentRepository.load_annual_report(...)`; no direct PDF cache, download helper, EID helper, Eastmoney helper, renderer, quality gate, Host, Agent, `dayu.host`, or `dayu.engine` was touched.
- Local run outputs are ignored under `reports/data-source-runs/s0-corpus-selection-20260525/`; they are evidence scratch only and are not promoted to tracked fixtures.

## Evidence Inputs

| Evidence | Path / command | What it proves |
|---|---|---|
| Selected public corpus source | `docs/code_20260519.csv` | Existing public selected-fund entry points include active, index, enhanced index, bond, QDII, and QDII-FOF candidates. |
| Curated golden review artifact | `reports/golden-answers/golden-answer-prefill-reviewed.md` | Existing manually reviewed rows already cover `004393`, `006597`, `004194`, and `007721`; `007721` is reviewed as `qdii_fund`, not `fof_fund`. |
| Repository probe JSONL | `reports/data-source-runs/s0-corpus-selection-20260525/repository-probe.jsonl` | All candidate annual reports below were loaded through `FundDocumentRepository`; document key, year, sections, table count, source metadata, and current `classify_fund_type()` result were recorded. |
| Repository probe summary | `reports/data-source-runs/s0-corpus-selection-20260525/repository-probe-summary.md` | Human-readable ignored summary of the same probe. |

Probe command:

```text
.venv/bin/python reports/data-source-runs/s0-corpus-selection-20260525/probe_repository_candidates.py
```

The probe script lives in the ignored run path and calls only:

- async repository access: the probe enters an async context through `asyncio.run(...)` and then awaits `FundDocumentRepository().load_annual_report(code, year, force_refresh=False)`.
- `classify_fund_type(report)`

## S0 Reviewed Candidate Table

`repository verification status` means the repository returned a parsed annual report whose `DocumentKey` matched the requested fund code and report year. It does not mean facts have been manually reviewed for scoring.

| fund type slot | fund code | report year | repository verification status | review state | source failure category | ignored run path |
|---|---|---:|---|---|---|---|
| `active_fund` | `004393` | 2024 | `verified`: `DocumentKey(fund_code="004393", year=2024, document_kind="annual_report")`; current classifier `active_fund`; existing reviewed golden rows present | `repository_verified` | n/a | `reports/data-source-runs/s0-corpus-selection-20260525/` |
| `index_fund` | `110020` | 2024 | `verified`: `DocumentKey(fund_code="110020", year=2024, document_kind="annual_report")`; current classifier `index_fund`; selected CSV row present; source metadata says `eastmoney`, `fallback_used=True`; repository metadata only preserves fallback source/result, not original upstream failure category in this S0 probe | `repository_verified` | `unknown_upstream_failure_category` | `reports/data-source-runs/s0-corpus-selection-20260525/` |
| `enhanced_index` | `004194` | 2024 | `verified`: `DocumentKey(fund_code="004194", year=2024, document_kind="annual_report")`; current classifier `enhanced_index`; EID metadata report name is annual report; existing reviewed golden section present | `repository_verified` | n/a | `reports/data-source-runs/s0-corpus-selection-20260525/` |
| `bond_fund` | `006597` | 2024 | `verified`: `DocumentKey(fund_code="006597", year=2024, document_kind="annual_report")`; current classifier `bond_fund`; existing reviewed golden section present | `repository_verified` | n/a | `reports/data-source-runs/s0-corpus-selection-20260525/` |
| `qdii_fund` | `017641` | 2024 | `verified`: `DocumentKey(fund_code="017641", year=2024, document_kind="annual_report")`; current classifier `qdii_fund`; selected CSV row present; source metadata says `eastmoney`, `fallback_used=True`; repository metadata only preserves fallback source/result, not original upstream failure category in this S0 probe | `repository_verified` | `unknown_upstream_failure_category` | `reports/data-source-runs/s0-corpus-selection-20260525/` |
| `fof_fund` | `007721` | 2024 | `verified_as_annual_report_but_type_gap`: repository loaded the annual report, existing reviewed golden rows identify fund name as `天弘标普500发起式证券投资基金（QDII-FOF）`, but current public classifier returns `qdii_fund` and reviewed golden `classified_fund_type` is also `qdii_fund` | `candidate` | `data_gap` | `reports/data-source-runs/s0-corpus-selection-20260525/` |
| `fof_fund` | `017970` | 2024 | `verified_as_annual_report_but_type_gap`: `DocumentKey(fund_code="017970", year=2024, document_kind="annual_report")`; repository loaded the annual report for another selected QDII-FOF candidate, but current public classifier returns `qdii_fund`; no reviewed golden section observed; source metadata says `eastmoney`, `fallback_used=True`; repository metadata only preserves fallback source/result, not original upstream failure category in this S0 probe | `candidate` | `data_gap`; `unknown_upstream_failure_category` for fallback source | `reports/data-source-runs/s0-corpus-selection-20260525/` |

## FOF Attempt Result

S0 attempted FOF with two selected-fund candidates:

- `007721` from `docs/code_20260519.csv` row `天弘标普500发起(QDII-FOF)A`.
- `017970` from `docs/code_20260519.csv` row `摩根海外稳健配置混合(QDII-FOF)人民币A`.

Both annual reports are repository-loadable for 2024. However, current public fund type detection checks QDII before FOF, so both candidates classify as `qdii_fund`. Existing reviewed golden evidence for `007721` also records `classified_fund_type | fund_type | qdii_fund`, despite the annual-report fund name containing `QDII-FOF`.

Therefore S0 records FOF as `data_gap`, not a blocking failure. The second pass must either:

- provide a repository-verified pure `fof_fund` whose current public classifier returns `fof_fund`; or
- explicitly open a fund type taxonomy / QDII-FOF precedence gate before treating QDII-FOF as satisfying the `fof_fund` baseline slot.

## Review State Transition Contract

| From state | To state | Transition trigger | Actor | Minimum evidence |
|---|---|---|---|---|
| `candidate` | `repository_verified` | Annual report identity probe succeeds through `FundDocumentRepository` or a public Fund API that itself uses it. | Evidence worker or future source-verification script; controller reviews artifact. | Fund code, report year, document kind, source metadata when available, parsed section/table presence, current fund type classification, and explicit source failure category if not verified. |
| `repository_verified` | `fact_prefill_generated` | Structured extraction / prefill command is run from the verified annual report boundary. | Future S1/S2 implementation worker or approved prefill script. | Ignored run path, command, input corpus id, generated facts, generated anchors or gap records, extraction modes, and no direct PDF/cache/helper access. |
| `fact_prefill_generated` | `fact_prefill_reviewed` | Human reviewer accepts, corrects, or defers each scored field and evidence location. | Human reviewer / controller-designated reviewer. | Markdown evidence table under `docs/reviews/` with field id, value, evidence anchor/source location, confidence, reviewer decision, correction if any, and unresolved data gaps. |
| `fact_prefill_reviewed` | `scoring_ready` | Controller confirms reviewed facts, anchors, data gaps, quality context, and corpus identity are frozen for the first scoring run. | Controller. | Reviewed evidence artifact path, corpus table, no unresolved identity mismatch for included slots, explicit `N/A` / data-gap handling for excluded dimensions, and ignored scoring run destination. |
| `scoring_ready` | `accepted_baseline` | Observational scoring run completes and review accepts the input as durable baseline material. | S1 reviewer(s) plus controller judgment. | Score issues with localization, denominator / `N/A` semantics, source boundary, failure categories, next-gate recommendation, validation commands, and explicit statement that machine fixtures are not promoted without a later curated-fixture gate. |

State meanings:

- `candidate`: selected by fund type slot and year only; repository identity may be missing or incomplete.
- `repository_verified`: annual-report identity is checked through repository boundary; not yet fact-reviewed.
- `fact_prefill_generated`: extractor/prefill output exists; not human-reviewed.
- `fact_prefill_reviewed`: human-reviewed facts and anchors exist in a Markdown evidence artifact.
- `scoring_ready`: reviewed facts/gaps/context are frozen for first scoring.
- `accepted_baseline`: reviewed scoring input is accepted for durable baseline consideration, still not automatically a tracked fixture.

## Stop Condition

S0 may proceed to review only because multiple corpus identity verifications did not fail: active, index, enhanced index, bond, and QDII have repository-verified annual reports. FOF remains a `data_gap`, as allowed by the controller judgment.

If a future S0 rerun sees identity verification fail for multiple fund type slots, stop after S0. The next gate should be source reliability / repository boundary work, not scoring schema implementation. In particular:

- `schema_drift`, `identity_mismatch`, and `integrity_error` must fail closed and be fixed before scoring expansion.
- repeated `not_found` or `unavailable` should go to source reliability / retry / fallback observability work.
- unverified substitutes must not be accepted to make corpus coverage look complete.

## Non-Goals Reconfirmed

- No renderer changes and no v0 8-chapter output changes.
- No FQ0-FQ6 quality gate behavior changes.
- No claim that LLM audit, Evidence Confirm, repair loop, patch/regenerate, or chapter writer is implemented.
- No `fund_agent/host` or `fund_agent/agent` package creation.
- No `dayu.host` or `dayu.engine` introduction.
- No direct PDF cache, download helper, EID helper, Eastmoney helper, Service/UI/renderer/quality-gate source access.
- No local run output promoted to tracked fixtures; `reports/data-source-runs/s0-corpus-selection-20260525/` remains ignored scratch evidence.

## Open Gaps / Residual Risks

| Gap | Risk | Required next handling |
|---|---|---|
| FOF slot is only QDII-FOF evidence today | Current `FundType` is single-label and QDII precedence masks FOF, so accepting it as `fof_fund` would weaken fund-type-first scoring. | Record `data_gap`; second pass must find pure FOF or open taxonomy/precedence design. |
| Some repository-verified records lack source metadata because parsed/cache metadata is absent | Verification can prove `DocumentKey`, but source-level annual-report identity details are thinner for cached records. | S1 should prefer candidates with source metadata for durable baseline, or refresh through repository if controller accepts a source-verification run. |
| Eastmoney fallback used for `110020`, `017641`, and `017970` | Fallback is allowed only if upstream failure category was `not_found` / `unavailable`; current metadata records fallback used but not the original failure class in this artifact. | S1 entry gate precondition: before durable baseline selection, source boundary / source reliability evidence must recover the original upstream failure category, or the fallback candidate must be excluded from the durable baseline corpus. |
| Existing reviewed golden coverage is uneven | `004393`, `006597`, `004194`, `007721` have observed reviewed rows; `110020`, `017641`, `017970` need fact prefill/review before scoring. | Do not enter scoring for those entries until `fact_prefill_reviewed`. |

## Validation

Commands run:

```text
rg -n "fund type slot|repository verification status|review state|source failure category|ignored run path|fof_fund|data_gap|candidate|repository_verified|fact_prefill_generated|fact_prefill_reviewed|scoring_ready|accepted_baseline|stop after S0|renderer|FQ0-FQ6|LLM audit|Evidence Confirm|dayu.host|dayu.engine|asyncio.run|unknown_upstream_failure_category|durable baseline selection" docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md
git diff --check
git check-ignore -v reports/data-source-runs/s0-corpus-selection-20260525/ reports/data-source-runs/s0-corpus-selection-20260525/repository-probe.jsonl reports/data-source-runs/s0-corpus-selection-20260525/repository-probe-summary.md reports/data-source-runs/s0-corpus-selection-20260525/probe_repository_candidates.py
```

Actual result:

- `rg` passed and confirmed the required table fields, review states, FOF `data_gap`, stop condition, non-goal boundary terms, async probe wording, fallback unknown-category marker, and durable baseline selection precondition are present.
- `git diff --check` passed with no whitespace errors.
- `git check-ignore -v` passed and confirmed `.gitignore:24:reports/data-source-runs/` covers the ignored run directory and probe files.
