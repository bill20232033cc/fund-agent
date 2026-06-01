# Small Baseline Corpus v1 Evaluation Plan

> Date: 2026-05-27
> Worker: AgentCodex implementation/planning worker
> Scope: code-generation-ready evaluation plan artifact only. No source, tests, README, renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, extractor, `FundDocumentRepository` source fallback, fixtures, commit, push, PR, or large product-chain run.

## Startup Packet Recap

- Truth sources for this plan are limited to `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current gate / Next entry point, and current accepted artifacts listed in the control doc.
- `docs/reviews/` artifacts are evidence chain only. They do not override the Startup Packet, current gate, or `docs/design.md` current design sections.
- Current architecture remains `UI -> Service -> Host -> Agent`; current deterministic production path is UI -> Service -> `fund_agent/fund` Agent-layer fund capability.
- Current gate is `small baseline corpus v1 plan/review`.
- The accepted active-fund Chapter 3 renderer minimal integration is already accepted and must not be repeated in this gate.
- This plan keeps all candidates as evaluation candidates. It does not promote any sample to durable baseline, golden answer corpus, `scoring_ready`, or tracked fixture.

## Reconciliation

The control doc already accepts seven unique fund codes from existing evidence. This v1 plan expands them into eight candidate rows because `004393` appears twice: `004393` / 2024 as the accepted active-fund clean candidate, and `004393` / 2025 as a probe-only report-year availability row.

- Clean near-term evaluation candidates: `004393` active, `004194` enhanced index, `006597` bond.
- Fallback-blocked planning candidates: `110020` index and `017641` QDII, pending upstream failure-category recovery or replacement.
- FOF remains a data gap: `007721` and `017970` are QDII-FOF / type-gap evidence, not fulfilled pure `fof_fund` coverage.

The current clean denominator is only three clean candidates across three fund-type slots: active, enhanced index, and bond. This remains below the desired 5-10 representative target and below broad fund-type coverage because index and QDII are fallback-blocked while FOF is a visible `data_gap`. The prior small-baseline real evaluation proved offline validator consumption over three clean slots and localized failure categories, but it explicitly did not create `scoring_ready`, durable baseline, product-flow readiness, or future golden material.

## Candidate Selection Strategy

Use an 8-row candidate matrix for v1 evaluation planning, covering seven unique fund codes:

1. Include the three clean rows in the clean evaluation denominator only after each run records reviewed input refs, validator summaries, quality-gate status, and report-quality issue categories.
2. Keep fallback-blocked rows visible but outside the clean denominator until the upstream failure category is recovered as `not_found` or `unavailable`, or the row is replaced.
3. Keep FOF attempts visible as `data_gap` / `taxonomy_pending`; do not count QDII-FOF as pure FOF coverage.
4. Do not read PDFs or cache directly. Any future annual-report access in implementation must go through `FundDocumentRepository` or existing Fund-layer public extraction paths that use it internally.
5. Treat 2025 probing, including `004393` / 2025 smoke, as availability and regression probing only until repository identity, report year, and reviewed facts are accepted.
6. Separate golden-covered observations from golden-missing observations. `004393` / 2024 may have current golden coverage; `004194` / 2024 and `006597` / 2024 are expected to produce `year_not_covered` / `FQ0/info` rather than correctness signal unless a later reviewed golden artifact says otherwise.

## Candidate Matrix

| fund_code | report_year | fund_type_slot | evaluation status | annual report availability | extraction field gaps | quality gate status to capture | report-quality issue categories to classify | false-positive suspicion | required next action | suitable for future golden |
|---|---:|---|---|---|---|---|---|---|---|---|
| `004393` | 2024 | `active_fund` | `repository_verified`; not `scoring_ready` | Accepted S0 annual-report identity; clean source boundary in accepted evidence. | Chapter 3 turnover / style-change reviewed evidence gap; manager consistency claims need explicit degradation if unsupported. | Capture `analyze` and `checklist` status for product smoke; capture FQ issue ids and stderr summary. | `chapter contract`, `evidence traceability`, possible `report writing quality`. | Unsupported stability/style-consistency positive wording can be a false positive if evidence is missing. | Run narrow 2024 smoke and offline bundle validation; record whether accepted renderer wording prevents the false positive. | Potential later golden only after fact review freeze and no material unresolved Chapter 3 issue. |
| `004393` | 2025 | `active_fund` | `repository_verified` pending; probe-only | Unknown in accepted evidence; probe only through product/Fund repository path. | Same Chapter 3 fields plus year-specific report availability and annual data completeness. | Capture analyze/checklist exit, not-run/block/warn/pass, and report-year golden coverage reason. | `data/source extraction`, `chapter contract`, `year_not_covered` correctness scope. | 2024 golden or facts must not be reused for 2025 correctness. | Smoke only; if report unavailable or identity is unverified, record as `data_gap` and exclude from v1 denominator. `--dev-override` smoke must not be interpreted as consuming final-judgment semantics; record only exit, quality gate summary, availability, and report-year scope. | No for v1; can only become future candidate after report-year identity and reviewed facts are accepted. |
| `004194` | 2024 | `enhanced_index` | `repository_verified`; not `scoring_ready` | Accepted S0 identity with EID metadata. | Tracking-error readiness and enhanced-index benchmark / excess-return facts not yet frozen as reviewed scoring input. | Capture FQ status and whether correctness coverage is missing, covered, or year-not-covered. | `data/source extraction`, `evidence traceability`, `chapter contract`. | Benchmark context may be misread as tracking-error evidence. | Run offline evaluation only with reviewed facts; otherwise classify as extraction/fact-review gap. | Possible future golden after reviewed tracking-error / benchmark-context rows exist. |
| `006597` | 2024 | `bond_fund` | `repository_verified`; not `scoring_ready` | Accepted S0 annual-report identity. | Bond lens facts: duration, credit risk, leverage/liquidity, drawdown, and pressure-test evidence need reviewed inputs. | Capture FQ status and missing-field denominator effects. | `data/source extraction`, `evidence traceability`, `report writing quality`. | Generic equity-style conclusions may be false positives for bond fund if bond lens facts are unavailable. | Evaluate bond-specific gaps and next minimal validation question quality. | Possible future golden after bond-lens fact review; not v1 durable baseline. |
| `110020` | 2024 | `index_fund` | `repository_verified` but fallback-blocked; not `scoring_ready` | S0 repository evidence exists, but `fallback_used=True` and upstream failure category is unknown. | Index profile / tracking error may be useful only after source-boundary recovery. | Capture only if source recovery proves fallback was eligible; otherwise mark excluded. | `data/source extraction`, `source fallback recovery`. | Eastmoney fallback could mask `schema_drift`, `identity_mismatch`, or `integrity_error`. | Recover upstream failure category as `not_found` / `unavailable`, or replace candidate. | No until fallback category is accepted and facts are reviewed. |
| `017641` | 2024 | `qdii_fund` | `repository_verified` but fallback-blocked; not `scoring_ready` | S0 repository evidence exists, but `fallback_used=True` and upstream failure category is unknown. | QDII overseas exposure, FX risk, benchmark, and fee facts need reviewed inputs after source recovery. | Capture only after fallback eligibility is proven. | `data/source extraction`, `source fallback recovery`, `evidence traceability`. | Fallback can hide unsafe source-contract failures. | Recover upstream failure category or replace with a clean QDII candidate. | No until source recovery and reviewed facts are accepted. |
| `007721` | 2024 | `fof_fund` attempt | `data_gap`; `taxonomy_pending` | Annual report may be loadable in accepted evidence, but accepted state is QDII-FOF / type gap, not pure FOF. | Pure FOF sub-fund quality and double-fee facts are not fulfilled by current classification. | Do not include in clean denominator; record taxonomy/data-gap status only. | `fund-type taxonomy`, `data_gap`. | Counting QDII-FOF as pure FOF would be a coverage false positive. | Open pure FOF second-pass corpus search or QDII-FOF precedence taxonomy gate. | No unless taxonomy gate explicitly accepts slot membership and facts are reviewed. |
| `017970` | 2024 | `fof_fund` attempt | `data_gap`; `taxonomy_pending`; fallback-blocked | Loadable per S0, but QDII-FOF/type gap plus `fallback_used=True` with unknown upstream failure category. | Pure FOF facts unavailable; source recovery also unresolved. | Exclusion/data-gap row only. | `fund-type taxonomy`, `data/source extraction`, `source fallback recovery`. | Double false-positive risk: type coverage and fallback safety. | Replace, recover fallback category, or defer to taxonomy gate. | No for v1. |

## Run Procedure

Implementation worker for the next gate should execute the evaluation in four explicit phases:

1. **Manifest freeze**
   - Create a scratch manifest with all eight candidate rows / seven unique fund codes.
   - Mark clean denominator rows: `004393` / 2024, `004194` / 2024, `006597` / 2024.
   - Record that this is only three clean candidates and three fund-type slots, below the 5-10 representative target.
   - Mark `004393` / 2025 as probe-only unless repository identity and reviewed facts are accepted during a later gate.
   - Mark fallback-blocked and FOF data-gap rows as exclusions with exact reason.

2. **Product smoke / availability probes**
   - Run only the listed smoke commands.
   - Use `--dev-override --quality-gate-policy warn` for broad smoke where needed so product block policy does not prevent observation.
   - For `004393` / 2025, `--dev-override` exists only to keep the probe observable; it must not be used to evaluate final-judgment semantics, report quality, or golden readiness.
   - Keep stdout/stderr under ignored scratch paths; tracked artifact records only exit status, quality gate summary, and scratch path.

3. **Candidate probing and offline evaluation**
   - Use `fund-analysis extraction-snapshot` and `fund-analysis extraction-score` only as explicit commands with `--fund-code`, `--report-year`, and caller-chosen run ids.
   - Run `scripts/report_quality_eval.py` only over explicit JSONL / bundle JSON inputs already assembled in scratch.
   - Do not add product CLI commands, do not register scripts in `pyproject.toml`, and do not use unreviewed outputs as fixtures.

4. **Decision summary**
   - Write a tracked summary artifact under `docs/reviews/` with candidate statuses, evidence paths, issue categories, and next-owner recommendation.
   - Separate `golden_covered` from `golden_missing` / `year_not_covered` rows before classifying extraction gaps. Expected current behavior is that `004393` / 2024 may provide correctness signal, while `004194` / 2024 and `006597` / 2024 should be summarized as golden-missing `FQ0/info` unless later accepted golden rows exist.
   - Keep all heavy outputs in `/tmp/...` or ignored `reports/...` directories.

## Artifact Policy

Tracked artifacts allowed:

- This plan: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`.
- A future review summary artifact under `docs/reviews/`, containing only:
  - candidate matrix summary;
  - command list and exit/status summary;
  - quality gate status and issue category counts;
  - relative or absolute scratch evidence paths;
  - decision recommendation and residual risks.

Scratch artifacts only:

- `/tmp/fund-agent-small-baseline-corpus-v1-20260527/`
- `reports/scoring-runs/small-baseline-corpus-v1-20260527/`
- `reports/smoke/small-baseline-corpus-v1-20260527/`
- `reports/extraction-snapshots/small-baseline-corpus-v1-20260527-*/`
- `reports/quality-gate-runs/small-baseline-corpus-v1-20260527-*/`

Large Markdown reports, stderr logs, snapshot JSONL, score JSON, quality gate JSON/Markdown, bundle JSON, validator summaries, and failure matrices must stay in scratch paths. They are not durable evidence, not accepted baseline material, and not golden fixtures.

## Verifier Matrix

Prefer `uv run`. If `uv` is unavailable in the worker environment, use `.venv/bin/...` equivalents and record the substitution in the future summary artifact.

| Purpose | Command | Expected handling |
|---|---|---|
| 004393 / 2024 product analyze smoke | `uv run fund-analysis analyze 004393 --report-year 2024` | Must capture exit code, quality gate stderr summary, and report path if produced. This is a smoke, not baseline approval. |
| 004393 / 2024 checklist smoke | `uv run fund-analysis checklist 004393 --report-year 2024` | Must capture exit code and checklist summary. |
| 004393 / 2025 product analyze smoke | `uv run fund-analysis analyze 004393 --report-year 2025 --dev-override --quality-gate-policy warn` | Probe availability / report-year correctness scope only; if annual report or golden coverage is missing, record `data_gap` / `year_not_covered`. Do not interpret dev override as final-judgment semantics. |
| 004393 / 2025 checklist smoke | `uv run fund-analysis checklist 004393 --report-year 2025 --dev-override --quality-gate-policy warn` | Probe-only; record only exit, quality gate summary, availability, and report-year scope. Do not infer final-judgment semantics or durable readiness. |
| Selected candidate smoke dry-run | `uv run python scripts/selected_funds_smoke.py --code 004393 --code 004194 --code 006597 --report-year 2024 --output-dir reports/smoke/small-baseline-corpus-v1-20260527` | Dry-run by default; validates script argument parsing and command construction only. Unless a later implementation proves otherwise, it provides no annual-report availability confidence and has no network/cache expectation. |
| Selected candidate smoke run | `uv run python scripts/selected_funds_smoke.py --run --continue-on-fail --code 004393 --code 004194 --code 006597 --report-year 2024 --output-dir reports/smoke/small-baseline-corpus-v1-20260527` | Optional bounded smoke for clean rows; outputs remain ignored scratch. |
| Per-candidate snapshot, active | `uv run fund-analysis extraction-snapshot --run-id small-baseline-corpus-v1-004393-2024 --fund-code 004393 --report-year 2024` | Uses production Fund-layer extraction path; output scratch only. |
| Per-candidate snapshot, enhanced index | `uv run fund-analysis extraction-snapshot --run-id small-baseline-corpus-v1-004194-2024 --fund-code 004194 --report-year 2024` | Same. |
| Per-candidate snapshot, bond | `uv run fund-analysis extraction-snapshot --run-id small-baseline-corpus-v1-006597-2024 --fund-code 006597 --report-year 2024` | Same. |
| Score active snapshot | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json` | Captures FQ/correctness inputs; does not create golden. |
| Score enhanced snapshot | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json` | Same. |
| Score bond snapshot | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/small-baseline-corpus-v1-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/small-baseline-corpus-v1-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json` | Same. |
| Quality gate from score | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/score.json` | Repeat per candidate; record status and issue ids only. |
| Dev-only report-quality validator | `uv run python scripts/report_quality_eval.py --jsonl /tmp/fund-agent-small-baseline-corpus-v1-20260527/bundles.jsonl --output /tmp/fund-agent-small-baseline-corpus-v1-20260527/validator-summary.json --run-id small-baseline-corpus-v1-20260527` | Only consumes explicit JSONL/bundle inputs; not product CLI. |
| Focused script tests | `uv run pytest tests/scripts/test_report_quality_eval.py -q` | Verifies dev-only wrapper if touched in a later implementation gate. |
| Focused validator tests | `uv run pytest tests/fund/test_report_quality_validation.py -q` | Required if validator behavior is touched; otherwise record not touched. |
| Focused snapshot/score tests | `uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q` | Required if snapshot/score behavior is touched; otherwise optional smoke validation. |
| CLI/service regression tests | `uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service.py -q` | Required if CLI/Service behavior is touched; this v1 evaluation gate should not touch them. |
| Ruff | `uv run ruff check .` | Required for implementation gates; for this planning-only artifact, not executed unless reviewer asks. |
| Full pytest | `uv run pytest` | Not required for this design-only / analysis-only plan because it adds no executable code, tests, package metadata, or product behavior. Required before any later accepted implementation checkpoint that changes code. |
| Diff whitespace closeout | `git diff --check` | Required before closeout even for plan-only gates. |

## Risks And Stop Conditions

Stop and return `needs-more-evidence` if any condition occurs:

- A candidate cannot be evaluated without direct PDF/cache/source-helper access outside `FundDocumentRepository`.
- Fallback-blocked `110020` or `017641` is requested in the clean denominator before upstream failure category recovery.
- Any fallback recovery reveals `schema_drift`, `identity_mismatch`, or `integrity_error`; fail closed and do not mask with Eastmoney fallback.
- Pure FOF coverage is required before a pure FOF candidate or accepted taxonomy decision exists.
- 004393 / 2025 probing tries to reuse 2024 golden rows or facts for correctness.
- `004194` / 2024 or `006597` / 2024 golden-missing `FQ0/info` is misclassified as extraction failure rather than missing golden coverage.
- Validator schema failures cannot be separated from report-quality failures.
- Large run outputs are about to be committed or promoted to durable fixture paths.
- Evaluation requires changing renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, extractor behavior, or source fallback behavior.

Next gate decision rules:

| Observation | Next gate |
|---|---|
| Clean coverage reaches at least five representative candidates across at least half the target fund-type slots, with reviewed facts, clean validator summaries, explicit quality-gate status, separated golden-covered vs golden-missing rows, and no fail-closed source issue. | `golden answer corpus v1` planning gate, still without automatic fixture promotion. |
| Missing facts dominate, especially tracking error, bond risk lens, QDII exposure, or 2025 availability. | `data extraction priority fixes` gate. |
| Facts exist but anchors/backlinks/derived sources are weak or missing. | `evidence anchor hardening` gate. |
| Chapter contract / writing issues dominate with sufficient facts. | scoped chapter contract / report-writing gate. |
| Clean coverage is at or below three clean candidates, covers fewer than half the target fund-type slots, or FOF/index/QDII blockers dominate. | more baseline probing / source recovery / taxonomy gate. |

## Non-Goals

- Do not modify renderer, including active-fund Chapter 3 renderer minimal integration.
- Do not modify FQ0-FQ6 quality gate behavior.
- Do not modify Service/CLI default analyze/checklist behavior.
- Do not create or modify Host/Agent packages, `dayu.host`, `dayu.engine`, ToolRegistry, runner, ToolTrace, session/run lifecycle, or outbox behavior.
- Do not modify `FundDocumentRepository`, concrete annual-report sources, PDF cache helpers, download helpers, or fallback policy.
- Do not modify extractors or parsing rules in this gate.
- Do not place explicit parameters in `extra_payload` or free-form dicts.
- Do not create durable baseline, golden answer corpus, or curated fixtures.
- Do not run unbounded product chains.
- Do not mutate GitHub state: no push, PR, issue, review request, merge, or external comment.

## Validation For This Artifact

This artifact is documentation-only. I read the current control/design truth and accepted evidence chain, then created this plan. No source code, tests, README, product output, fixture, control doc, commit, push, or PR was modified. Closeout still requires `git diff --check`; the result must be reported by the worker before handing the plan back.
