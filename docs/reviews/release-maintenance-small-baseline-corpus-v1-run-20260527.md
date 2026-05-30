# Small Baseline Corpus v1 Evaluation Run

> Date: 2026-05-27
> Worker: AgentCodex evaluation runner
> Scope: bounded evaluation run only. No source, tests, README, renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, `FundDocumentRepository`, source fallback, extractor, fixture, golden corpus, package config, commit, push, PR, or GitHub mutation was changed.

## Inputs

- Accepted plan: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`
- Controller judgment: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-controller-judgment-20260527.md`
- Primary scratch root: `/tmp/fund-agent-small-baseline-corpus-v1-20260527/`
- Ignored run roots:
  - `reports/smoke/small-baseline-corpus-v1-20260527/`
  - `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/`
  - `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/`
  - `reports/extraction-snapshots/small-baseline-corpus-v1-006597-2024/`

## Command Summary

| Command | Status | Notes / evidence |
|---|---|---|
| `uv run fund-analysis analyze 004393 --report-year 2024` | pass | stdout/stderr under `/tmp/.../product-smoke/004393-2024-analyze.*`; stderr reports `quality_gate_status: warn`, `quality_gate_issues: 3`. |
| `uv run fund-analysis checklist 004393 --report-year 2024` | pass | `/tmp/.../product-smoke/004393-2024-checklist.*`; stderr reports `quality_gate_status: warn`, `quality_gate_issues: 3`. |
| `uv run fund-analysis analyze 004393 --report-year 2025 --dev-override --quality-gate-policy warn` | pass | `/tmp/.../product-smoke/004393-2025-analyze-dev-warn.*`; recorded only availability/year-scope, not final-judgment semantics. |
| `uv run fund-analysis checklist 004393 --report-year 2025` | pass | CLI has no `--dev-override` / `--quality-gate-policy` for `checklist`; used supported command and recorded deviation. |
| `uv run python scripts/selected_funds_smoke.py --code 004393 --code 004194 --code 006597 --report-year 2024 --output-dir reports/smoke/small-baseline-corpus-v1-20260527` | pass | Dry-run only; validates argument parsing and command construction, not availability. |
| `uv run python scripts/selected_funds_smoke.py --run --continue-on-fail --code 004393 --code 004194 --code 006597 --report-year 2024 --output-dir reports/smoke/small-baseline-corpus-v1-20260527` | pass | 3/3 process pass; quality statuses: `004393=warn`, `004194=warn`, `006597=block`. |
| `uv run fund-analysis extraction-snapshot --run-id small-baseline-corpus-v1-004393-2024 --fund-code 004393 --report-year 2024` | pass | 16 snapshot rows, 0 errors. |
| `uv run fund-analysis extraction-snapshot --run-id small-baseline-corpus-v1-004194-2024 --fund-code 004194 --report-year 2024` | pass | 16 snapshot rows, 0 errors. |
| `uv run fund-analysis extraction-snapshot --run-id small-baseline-corpus-v1-006597-2024 --fund-code 006597 --report-year 2024` | pass | 16 snapshot rows, 0 errors. |
| `uv run fund-analysis extraction-score ...004393... --golden-answer-path reports/golden-answers/golden-answer.json` | pass | correctness `available`, `partially_covered`, 9/9 comparable matches. |
| `uv run fund-analysis extraction-score ...004194... --golden-answer-path reports/golden-answers/golden-answer.json` | pass | correctness `available`, `covered`, 5/5 comparable matches. |
| `uv run fund-analysis extraction-score ...006597... --golden-answer-path reports/golden-answers/golden-answer.json` | pass | correctness `available`, `partially_covered`, 9/9 comparable matches. |
| `uv run fund-analysis quality-gate --score-path ...004393.../score.json` | pass | `warn`, 3 issues. |
| `uv run fund-analysis quality-gate --score-path ...004194.../score.json` | pass | `warn`, 3 issues. |
| `uv run fund-analysis quality-gate --score-path ...006597.../score.json` | pass | `block`, 7 issues. |

## Candidate Matrix

| fund_code | report_year | fund_type_slot | status flags | annual report availability | commands / not-run reason | observed extraction gaps | quality gate / issue taxonomy | report-quality categories | false-positive suspicion | required next action | suitable for future golden | scratch evidence |
|---|---:|---|---|---|---|---|---|---|---|---|---|---|
| `004393` | 2024 | `active_fund` | `repository_verified`; not `scoring_ready` | Product analyze/checklist and snapshot succeeded through public CLI/Fund path; 16 snapshot rows, 0 errors. | analyze, checklist, selected smoke, snapshot, score, quality-gate all ran. | `turnover_rate` missing; `investor_return` missing; non-index `tracking_error` / `index_profile` N/A by type; `nav_data` has no annual-report anchor. | Snapshot quality gate `warn`; P1 `turnover_rate`; correctness `available`, `partially_covered`, 9/9 comparable matches; info says some strict golden fields are outside snapshot comparable contract. | `chapter contract`, `data/source extraction`, `evidence traceability`. | Active Chapter 3 style/stability claim remains risky if rendered without explicit turnover/style-change evidence. Current accepted renderer wording must keep this degraded. | Keep as clean candidate, but not durable baseline. Next action: reviewed fact freeze for Chapter 3 turnover/style-change gap and comparable contract expansion decision. | No for immediate golden corpus; possible later after fact review freeze and Chapter 3 issue disposition. | `/tmp/.../004393-2024-*`; `reports/smoke/.../004393_*.md`; `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/`. |
| `004393` | 2025 | `active_fund` | `probe_only`; repository identity not accepted for baseline | Product analyze/checklist succeeded and output cites `年报2025§2`, so availability is observed only as probe evidence. | analyze ran with `--dev-override --quality-gate-policy warn`; checklist ran without unsupported dev override flags. | Product gate reports `turnover_rate` P1 gap. No snapshot/score run was requested for 2025 in this gate. | analyze/checklist quality gate `warn`, 3 issues; info says 004393 has strict golden records but current report year is not covered and other-year golden is not used. | `year_not_covered`, `data/source extraction`, `chapter contract`. | Do not consume final-judgment semantics from `--dev-override`; 2024 golden/facts must not be reused for 2025 correctness. | Keep probe-only. Next action: separate 2025 repository identity + fact-review gate if 2025 is desired. | No; report-year coverage missing and probe-only. | `/tmp/.../004393-2025-*`; `reports/quality-gate-runs/analyze-004393-2025-20260526T180308084465Z/`; `reports/quality-gate-runs/checklist-004393-2025-20260526T180314403191Z/`. |
| `004194` | 2024 | `enhanced_index` | `repository_verified`; not `scoring_ready` | Product selected smoke and snapshot succeeded; 16 snapshot rows, 0 errors. | selected smoke, snapshot, score, quality-gate all ran. | `tracking_error` missing; `turnover_rate` missing; `investor_return` missing; index profile is benchmark-context only and must not be treated as methodology / constituent evidence. | Snapshot quality gate `warn`; P1 `tracking_error`, `turnover_rate`; correctness `available`, `covered`, 5/5 comparable matches. | `data/source extraction`, `evidence traceability`, `chapter contract`. | Benchmark text can be misread as tracking-error or index methodology evidence. | Keep as clean candidate but below baseline readiness. Next action: tracking-error / enhanced-index fact review and anchor hardening. | No immediate; possible later because current comparable golden rows matched, but tracking-error gap remains material. | `/tmp/.../004194-2024-*`; `reports/smoke/.../004194_*.md`; `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/`. |
| `006597` | 2024 | `bond_fund` | `repository_verified`; not `scoring_ready` | Product selected smoke and snapshot succeeded; 16 snapshot rows, 0 errors. | selected smoke, snapshot, score, quality-gate all ran. | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` missing; `investor_return` missing; non-index `tracking_error` / `index_profile` N/A by type; `nav_data` has no annual-report anchor. | Snapshot quality gate `block`; 7 issues; missing-field rate 35.7%; correctness `available`, `partially_covered`, 9/9 comparable matches; info says some strict golden fields are outside snapshot comparable contract. | `data/source extraction`, `evidence traceability`, bond-lens fact coverage. | Generic equity-style report confidence would be a false positive because bond-lens facts are materially incomplete. | Do not enter baseline/golden. Next action: bond extraction priority fixes or bond-specific gap policy before more writing work. | No; quality gate blocks and bond-lens fact coverage is insufficient. | `/tmp/.../006597-2024-*`; `reports/smoke/.../006597_*.md`; `reports/extraction-snapshots/small-baseline-corpus-v1-006597-2024/`. |
| `110020` | 2024 | `index_fund` | `fallback_blocked`; visible excluded row | Not re-run by this evaluation. Accepted evidence says repository identity exists but `fallback_used=True` with unknown upstream failure category. | Not run by design; clean denominator exclusion. | Not observed in this run. | Not observed in this run. | `source fallback recovery`, `data/source extraction`. | Eastmoney fallback may mask fail-closed categories. | Recover upstream failure category as `not_found` / `unavailable`, or replace with clean index candidate. | No. | No new scratch output. |
| `017641` | 2024 | `qdii_fund` | `fallback_blocked`; visible excluded row | Not re-run by this evaluation. Accepted evidence says repository identity exists but `fallback_used=True` with unknown upstream failure category. | Not run by design; clean denominator exclusion. | Not observed in this run. | Not observed in this run. | `source fallback recovery`, `data/source extraction`, QDII fact coverage. | Fallback can hide unsafe source-contract failure. | Recover upstream failure category or replace with clean QDII candidate. | No. | No new scratch output. |
| `007721` | 2024 | `fof_fund` attempt | `data_gap`; `taxonomy_pending` | Not re-run. Accepted evidence treats it as QDII-FOF / type gap, not pure FOF. | Not run by design; data-gap row only. | Not observed in this run. | Not observed in this run. | `fund-type taxonomy`, `data_gap`. | Counting QDII-FOF as pure FOF would be coverage false positive. | Pure FOF second-pass corpus search or QDII-FOF precedence taxonomy gate. | No. | No new scratch output. |
| `017970` | 2024 | `fof_fund` attempt | `data_gap`; `taxonomy_pending`; `fallback_blocked` | Not re-run. Accepted evidence has both type gap and unknown fallback category. | Not run by design; data-gap/fallback-blocked row only. | Not observed in this run. | Not observed in this run. | `fund-type taxonomy`, `source fallback recovery`, `data/source extraction`. | Double false-positive risk: type coverage plus fallback safety. | Replace, recover fallback category, or defer to taxonomy gate. | No. | No new scratch output. |

## Clean Denominator

- Clean evaluated candidates: 3
- Clean evaluated fund-type slots: 3 (`active_fund`, `enhanced_index`, `bond_fund`)
- Excluded visible rows: 4 unique fund codes / 4 rows for index, QDII, and FOF attempts; plus `004393` / 2025 probe-only row.
- This remains below the 5-10 representative target and below broad fund-type coverage. It must not route to `golden answer corpus v1`.

## Interpretation Notes

- `004194` / 2024 did produce correctness signal in this run (`covered`, 5/5 matches), so it should not be reported as `year_not_covered` for this exact run.
- `006597` / 2024 produced correctness signal (`partially_covered`, 9/9 matches), but quality gate blocked on field missing rate. This is a data/source extraction and bond-lens coverage problem, not a golden mismatch.
- `004393` / 2025 correctly stayed year-scoped: quality gate info says existing 004393 golden rows do not cover 2025 and other-year golden is not used.
- `selected_funds_smoke.py` dry-run remains command construction only; the bounded `--run` result is the actual availability smoke.
- No fallback-blocked or FOF data-gap row was treated as clean denominator.

## Next Gate Recommendation

Route to **more baseline probing / source recovery / taxonomy**, with a focused data-extraction priority subpath for the clean rows:

- recover or replace `110020` and `017641` before counting index/QDII coverage;
- find a pure FOF candidate or open a QDII-FOF precedence taxonomy gate;
- fix or explicitly policy-classify `006597` bond missing fields before any golden corpus gate;
- decide whether `004194` tracking-error and active `004393` turnover/style gaps are extraction fixes, evidence-anchor hardening, or accepted data-gap wording.

Do not enter `golden answer corpus v1` yet because clean coverage is only 3 candidates / 3 slots and one clean slot (`006597`) is quality-gate blocked.

## Validation

- `git diff --check`: passed.
