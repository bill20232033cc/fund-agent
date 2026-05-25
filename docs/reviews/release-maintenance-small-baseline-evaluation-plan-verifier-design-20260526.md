# Gate B Small Baseline Evaluation Plan / Verifier Design

> Date: 2026-05-26  
> Worker: AgentCodex planning specialist  
> Scope: planning artifact only. No source, tests, README, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixtures, run outputs, commit, push, PR, annual-report fetch, annual-report parse, `FundDocumentRepository`, PDF/cache/source helper, downloader, or source-adapter work.

## Truth Sources

- `AGENTS.md`
- `docs/design.md` current design sections, especially report quality, Fact / Evidence input contract, and `UI -> Service -> Host -> Agent` boundary.
- `docs/implementation-control.md` Startup Packet / Current Truth Guardrails / Current Gate / Next Entry Point.
- Gate A artifact: `docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md`.
- Accepted report-quality / Fact-Evidence artifacts:
  - `docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md`
  - `docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-controller-judgment-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-controller-judgment-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md`
  - `docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-controller-judgment-20260526.md`

## Boundary Decision

Gate B is a verifier design gate, not an evaluation run. It must design a repeatable offline evaluation loop for Gate A candidates, but must not execute the loop.

The loop must stay outside product defaults:

- Do not call `fund-analysis analyze`.
- Do not call `fund-analysis checklist`.
- Do not modify or route through renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, fixtures, or tracked reports.
- Do not fetch or parse annual reports in this gate.
- Do not call `FundDocumentRepository`, concrete PDF cache helpers, source helpers, downloaders, or source adapters in this gate.

Future annual-report access, if needed, is a later gate condition and must go through `FundDocumentRepository` or public Fund extraction APIs that themselves use `FundDocumentRepository`.

## Gate A Reality

Gate B must preserve the accepted Gate A candidate state:

| Candidate | Fund type slot | Gate B treatment |
|---|---|---|
| `004393` / 2024 | `active_fund` | Clean near-term evaluation candidate. Use for active-fund chapter 3 turnover / manager-consistency verifier cases. |
| `004194` / 2024 | `enhanced_index` | Clean near-term evaluation candidate. Use for enhanced-index benchmark / excess-return / tracking-constraint verifier cases only after reviewed fact input is available. |
| `006597` / 2024 | `bond_fund` | Clean near-term evaluation candidate. Use for bond risk / duration-credit-liquidity verifier cases only after reviewed fact input is available. |
| `110020` / 2024 | `index_fund` | Fallback-blocked. Do not include in clean evaluation denominator until upstream failure category is recovered as `not_found` or `unavailable`, or the candidate is replaced. |
| `017641` / 2024 | `qdii_fund` | Fallback-blocked. Same rule as `110020`. |
| `007721` / 2024 | FOF attempt | `data_gap`; QDII-FOF/type-gap evidence only, not pure FOF coverage. |
| `017970` / 2024 | FOF attempt | `data_gap` plus fallback-blocked; not pure FOF coverage. |

No candidate is `scoring_ready`, `accepted_baseline`, or durable fixture material at Gate B.

## Repeatable Evaluation Flow

The future evaluator should run as an offline, explicit-input pipeline. Each run must be reconstructable from a manifest, scratch output directory, and tracked review artifact.

1. **Freeze an evaluation manifest**
   - Input: Gate A candidate ids, report year, fund-type slot, chapter ids, expected dimensions, accepted review artifact refs, and explicit exclusion reasons.
   - Clean first pass: include only `004393`, `004194`, and `006597`.
   - Excluded rows must still be represented in a `candidate_exclusions` section so fallback and FOF data gaps remain visible.

2. **Assemble reviewed input only**
   - Allowed input: accepted review artifacts, reviewed fact-prefill rows, and later accepted manually reviewed facts.
   - Not allowed input: direct PDF files, parsed cache, source adapters, production extractors, default analyze/checklist output, renderer Markdown, or unreviewed probe output.

3. **Build `ReportEvidenceBundle` records**
   - Existing function that produces the typed bundle when a pre-existing structured bundle is supplied:
     - `fund_agent.fund.report_evidence.project_report_evidence_bundle(bundle, context)`
   - Required explicit context:
     - `ReportEvidenceProjectionContext(run_id=..., corpus_id=..., source_boundary=..., source_failure_category=..., fund_type_slot=..., document_identity_status=..., fallback_used=..., review_artifact_refs=..., fact_review_status=..., data_gap_overrides=..., score_issue_links=...)`
   - Gate B does not provide or generate a `StructuredFundDataBundle`. If Gate C needs one, it must use a later accepted input source and must not create a parallel extraction path.

4. **Serialize JSONL**
   - JSONL line shape:
     - one or more `record_type="bundle"` records containing serialized `ReportEvidenceBundle` mappings;
     - optional linked `record_type="score_issue"` records copied from bundle-local `score_issue_links` to exercise score-issue consumer validation.
   - Serialization should use dataclass mapping semantics compatible with the current validator; the accepted validator already normalizes typed dataclass bundles and mappings.

5. **Run validator APIs**
   - Existing functions:
     - `fund_agent.fund.report_quality_validation.validate_report_quality_bundle(bundle, source_path=..., run_id=...)`
     - `fund_agent.fund.report_quality_validation.validate_report_quality_jsonl(jsonl_path, run_id=...)`
   - These functions produce `ReportQualityValidationResult`, including:
     - `summary.total_records`
     - `summary.scoring_ready_record_count`
     - `summary.blocking_count`
     - `summary.material_count`
     - `summary.minor_count`
     - `summary.failed_closed`
     - `summary.error_code_counts`
     - issue rows with stable `error_code`, severity, pointer, field, expected, actual, and message.

6. **Classify evaluation failures**
   - The verifier must combine validator issues, score issues, data gaps, source categories, and manual review notes into a failure-category matrix.
   - The output must distinguish validator failures from report-quality failures. A clean validator result means the input contract is consumable; it does not prove report quality.

7. **Write scratch outputs only**
   - Scratch output paths must be `/tmp/...` or ignored run directories. See the scratch path section below.
   - A tracked review artifact may summarize the run; scratch JSON/JSONL/result files must not become durable evidence by themselves.

## Command / Script Design

Gate B does not create the script. A later Gate C verifier implementation may introduce a small non-product harness only after review accepts this design.

Recommended future command shape:

```text
.venv/bin/python <future-verifier-script> \
  --manifest /tmp/fund-agent-small-baseline-eval-20260526/manifest.json \
  --out-dir /tmp/fund-agent-small-baseline-eval-20260526 \
  --run-id small-baseline-eval-20260526
```

If the project chooses an ignored repo-local run dir instead of `/tmp`, use:

```text
.venv/bin/python <future-verifier-script> \
  --manifest reports/scoring-runs/small-baseline-eval-20260526/manifest.json \
  --out-dir reports/scoring-runs/small-baseline-eval-20260526 \
  --run-id small-baseline-eval-20260526
```

The future script must only orchestrate accepted Fund-layer pure functions and explicit reviewed inputs. It must not become a product CLI command, must not call `fund-analysis analyze` / `checklist`, and must not reach through Service/CLI/renderer/FQ0-FQ6/Host/Agent/dayu.

Minimum future output files:

| Output | Producer | Durable? | Purpose |
|---|---|---|---|
| `manifest.json` | future verifier harness | No | Exact candidate list, exclusions, source review refs, run id, schema version, and allowed input refs. |
| `bundles.jsonl` | future verifier harness using `ReportEvidenceBundle` records | No | JSONL input for validator API. |
| `validator-result.json` | `validate_report_quality_bundle()` / `validate_report_quality_jsonl()` result serialized by harness | No | Validator summary and issue table. |
| `failure-categories.json` | future verifier harness classification step | No | Category matrix mapping each issue to next owner. |
| `summary.md` | future verifier harness or reviewer | No | Local human summary; tracked controller artifact must cite only accepted excerpts. |

## Scratch Paths

Preferred scratch path:

```text
/tmp/fund-agent-small-baseline-eval-20260526/
```

Allowed ignored fallback path:

```text
reports/scoring-runs/small-baseline-eval-20260526/
```

`reports/scoring-runs/` is git-ignored in the current repository. Scratch files in either path are not durable fixtures, not accepted baseline material, not product reports, and not durable evidence. A later tracked `docs/reviews/` artifact may summarize the run, but must state that scratch files are reproducible inputs/outputs only.

## Failure Category Mapping

The verifier must map every observation to exactly one primary next-owner category, with optional secondary tags.

| Primary category | Signals | Next development task |
|---|---|---|
| `data/source extraction` | Missing required fact that should exist in annual report; wrong unit/date/table/share class; extraction-mode conflict; source category recovery needed; fallback category unresolved. | Improve source reliability, repository-derived extraction, table parsing, normalization, or source failure capture. |
| `evidence traceability` | `RQV_REF_MISSING`, `RQV_TRACEABILITY_GAP`, weak/missing anchor, derived source missing, fact/gap backlink incomplete. | Improve Evidence Store / anchor generation / fact-gap-issue linking. |
| `chapter contract` | must_answer missing, must_not_cover violation, unsupported active-fund stability/style-consistency claim, `N/A` vs `skipped` semantics mismatch, final claim blocked by explicit data gap. | Update CHAPTER_CONTRACT / ITEM_RULE / chapter rule audit before changing extraction. |
| `validator schema` | `RQV_FIELD_MISSING`, `RQV_ENUM_INVALID`, `RQV_RECORD_TYPE_INVALID`, `RQV_JSONL_INVALID`, schema-version mismatch, duplicate ids, invalid source fallback consistency. | Harden `ReportEvidenceBundle` / JSONL validator schema and tests. |
| `report writing quality` | Field dump, unclear action, missing next minimal validation question, investment-advice boundary issue, unsupported causality, strong conclusion with core gap. | Improve writing rules, wording audit, later LLM audit, or report assembly contract. |
| `fund-type taxonomy` | pure FOF missing, QDII-FOF precedence ambiguity, `type_slot_membership_status=type_gap` or `taxonomy_pending`, classified type conflicts with intended slot. | Open fund-type taxonomy / QDII-FOF precedence gate or replace candidate. |

Source failure categories must retain fail-closed semantics:

| Source failure category | Verifier treatment |
|---|---|
| `none` | Eligible only if no fallback was used and identity/type-slot/review state are clean. |
| `not_found` | Fallback-eligible; may be considered after source-recovery evidence proves this exact category. |
| `unavailable` | Fallback-eligible; may be considered after source-recovery evidence proves this exact category. |
| `schema_drift` | Fail closed; map to `data/source extraction` or `validator schema` depending on same-source evidence. |
| `identity_mismatch` | Fail closed; map to `data/source extraction` or corpus replacement. |
| `integrity_error` | Fail closed; map to `data/source extraction` / source integrity. |
| `unknown_upstream_failure_category` | Stop before durable baseline; map to `data/source extraction` source-recovery task. |
| `data_gap` | Not a document-level fallback category; map by field to `data/source extraction`, `chapter contract`, or `report writing quality`. |

## Candidate-Specific Verifier Cases

| Candidate | Minimum Gate B verifier case | Expected category pressure |
|---|---|---|
| `004393` active | Chapter 3 manager holding traceability pass plus turnover/style-consistency gap issue. | `chapter contract` first; `data/source extraction` only if accepted wording requires turnover/style-change evidence. |
| `004194` enhanced index | Benchmark / enhanced-return / tracking-constraint reviewed fact bundle once facts are reviewed. | likely `evidence traceability`, `chapter contract`, or `data/source extraction`; do not infer tracking-error readiness from benchmark context alone. |
| `006597` bond | Bond risk lens facts: duration, credit, leverage, liquidity, drawdown, and next validation question once reviewed facts exist. | likely `data/source extraction`, `evidence traceability`, or `report writing quality`. |
| `110020` index | Exclusion row only until fallback category recovery. | `data/source extraction`. |
| `017641` QDII | Exclusion row only until fallback category recovery. | `data/source extraction`. |
| `007721` / `017970` FOF attempts | Data-gap rows only. | `fund-type taxonomy`; `017970` also `data/source extraction` because fallback category is unknown. |

## Entry Conditions For Durable Baseline Fixture Gate

Do not enter durable baseline fixture gate until all conditions below are true:

1. At least one clean candidate has `fact_prefill_reviewed` inputs for the selected chapters and dimensions.
2. Every included record has `document_identity_status=verified_annual_report`.
3. Every included record has `type_slot_membership_status=matches_slot`; taxonomy/data-gap rows are excluded from baseline denominators.
4. Every included source document has `source_failure_category=none`, or a reviewed source-recovery artifact proves fallback was eligible (`not_found` / `unavailable`) and keeps `fallback_used=True`.
5. No included record uses `unknown_upstream_failure_category`, `schema_drift`, `identity_mismatch`, `integrity_error`, `source_boundary=unknown`, or `source_boundary=probe_only`.
6. `validate_report_quality_bundle()` and `validate_report_quality_jsonl()` return `failed_closed=false` and zero blocking validator issues for the selected input.
7. Material report-quality issues are either accepted as baseline-known issues with owner/category, or fixed by a prior accepted gate.
8. Scratch output paths are ignored or under `/tmp`, and a tracked review artifact states they are non-durable.
9. Controller explicitly opens a curated-fixture gate that authorizes exact tracked fixture paths and review criteria.

## Stop Conditions

Stop and output `needs-more-evidence` instead of entering fixture work if:

- the evaluation cannot be designed without product default `analyze` / `checklist`;
- the only available clean evidence requires fetching/parsing annual reports in the same gate;
- `004393`, `004194`, and `006597` lack enough reviewed fact input for the selected verifier cases;
- fallback category for `110020` / `017641` is still unknown and the controller wants them in the clean denominator;
- pure FOF coverage is required before a fund-type taxonomy or second-pass corpus gate resolves the current `data_gap`;
- validator schema issues and content-quality issues cannot be separated in the run summary.

## Recommended Next Gate C Planning Inputs

Gate C should plan a small verifier evidence run, not durable fixtures:

- manifest shape for the three clean candidates and four exclusion/data-gap rows;
- exact reviewed input refs for `004393` chapter 3, and availability check for reviewed facts on `004194` / `006597`;
- future harness ownership and whether it lives as a temporary review-run script or a Fund-layer developer utility;
- JSONL serialization shape for bundle lines and score-issue lines;
- expected validator summary assertions and failure-category matrix assertions;
- review artifact template for summarizing scratch output without promoting it.

## Controller Control-Doc Update Suggestions

If this artifact is accepted, update only a short control-doc reference:

1. Add this artifact under accepted artifacts as Gate B baseline evaluation / verifier design.
2. Set the next entry point to Gate C small baseline verifier evidence-run planning.
3. Preserve clean candidates as `004393`, `004194`, `006597`.
4. Preserve `110020` and `017641` as fallback-blocked until source recovery or replacement.
5. Preserve FOF as `data_gap`; `007721` and `017970` remain QDII-FOF/type-gap evidence, not pure FOF coverage.
6. Reconfirm no durable baseline fixture gate is open yet.

## Validation

Read-only / document-only checks used for this planning artifact:

```text
git status --short
git branch --show-current
rg --files docs | sort
rg -n "Report Quality|report quality|Fact-Evidence|ReportEvidenceBundle|validator|quasi-real|四层|UI -> Service -> Host -> Agent|quality" docs/design.md docs/implementation-control.md
sed -n '1,260p' docs/implementation-control.md
sed -n '1,260p' docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md
sed -n '430,540p' docs/design.md
sed -n '1,300p' docs/reviews/release-maintenance-report-evidence-bundle-typed-model-projection-implementation-controller-judgment-20260525.md
sed -n '1,320p' docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-implementation-controller-judgment-20260525.md
sed -n '1,320p' docs/reviews/release-maintenance-report-quality-validator-quasi-real-bundle-evidence-20260525.md
sed -n '1,280p' docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-20260525.md
sed -n '1,280p' docs/reviews/release-maintenance-report-quality-baseline-s1-score-schema-fixture-draft-20260525.md
sed -n '1,260p' docs/reviews/release-maintenance-report-quality-baseline-s1-dry-run-evidence-20260525.md
rg -n "def validate_report_quality|class ReportQuality|error_code|failure_category|Next owner|RQV_|summary|record_type" fund_agent/fund/report_quality_validation.py fund_agent/fund/report_evidence.py tests/fund/test_report_quality_validation.py tests/fund/test_report_evidence.py
test -e docs/reviews/release-maintenance-small-baseline-evaluation-plan-verifier-design-20260526.md
git check-ignore -v reports/scoring-runs/ reports/data-source-runs/ reports/writing-runs/
```

Result:

- Target artifact did not exist before this gate.
- Current branch is `codex/local-reconciliation`.
- Existing unrelated untracked artifact remains: `docs/reviews/release-maintenance-deepreview-controller-judgment-20260526.md`.
- `reports/scoring-runs/`, `reports/data-source-runs/`, and `reports/writing-runs/` are ignored.
- No report, extractor, repository, source adapter, default analyze/checklist, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, fixture, or run-output command was executed.
