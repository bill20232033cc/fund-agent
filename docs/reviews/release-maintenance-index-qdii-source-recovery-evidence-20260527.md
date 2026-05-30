# Index/QDII Source Recovery Evidence

> Date: 2026-05-27
> Worker: AgentCodex evidence worker
> Gate: `index/QDII source recovery evidence gate`
> Latest accepted checkpoint: `bb1b67f`
> Scope: bounded public CLI evidence only. No code changes, no commit, no push, no PR.

## Startup Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `index/QDII source recovery evidence gate` |
| Truth sources | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point; accepted plan and controller judgment artifacts |
| Accepted plan | `docs/reviews/release-maintenance-index-qdii-source-recovery-replacement-plan-20260527.md` |
| Controller judgment | `docs/reviews/release-maintenance-index-qdii-source-recovery-replacement-plan-controller-judgment-20260527.md` |
| Candidates | exactly `110020` / 2024 and `017641` / 2024 |
| Replacement candidates | none approved in this handoff |

## Commands Run

| Step | Candidate | Command | Exit status | Public output paths |
|---|---|---|---:|---|
| snapshot | `110020` / 2024 | `uv run fund-analysis extraction-snapshot --run-id index-qdii-source-110020-2024 --fund-code 110020 --report-year 2024` | 0 | `reports/extraction-snapshots/index-qdii-source-110020-2024/snapshot.jsonl`; `reports/extraction-snapshots/index-qdii-source-110020-2024/summary.md`; `reports/extraction-snapshots/index-qdii-source-110020-2024/errors.jsonl` |
| score | `110020` / 2024 | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/index-qdii-source-110020-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/index-qdii-source-110020-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json` | 0 | `reports/extraction-snapshots/index-qdii-source-110020-2024/score.json`; `reports/extraction-snapshots/index-qdii-source-110020-2024/score.md`; `reports/extraction-snapshots/index-qdii-source-110020-2024/golden_set.json` |
| quality gate | `110020` / 2024 | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/index-qdii-source-110020-2024/score.json` | 0 | `reports/extraction-snapshots/index-qdii-source-110020-2024/quality_gate.json`; `reports/extraction-snapshots/index-qdii-source-110020-2024/quality_gate.md` |
| snapshot | `017641` / 2024 | `uv run fund-analysis extraction-snapshot --run-id index-qdii-source-017641-2024 --fund-code 017641 --report-year 2024` | 0 | `reports/extraction-snapshots/index-qdii-source-017641-2024/snapshot.jsonl`; `reports/extraction-snapshots/index-qdii-source-017641-2024/summary.md`; `reports/extraction-snapshots/index-qdii-source-017641-2024/errors.jsonl` |
| score | `017641` / 2024 | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/index-qdii-source-017641-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/index-qdii-source-017641-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json` | 0 | `reports/extraction-snapshots/index-qdii-source-017641-2024/score.json`; `reports/extraction-snapshots/index-qdii-source-017641-2024/score.md`; `reports/extraction-snapshots/index-qdii-source-017641-2024/golden_set.json` |
| quality gate | `017641` / 2024 | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/index-qdii-source-017641-2024/score.json` | 0 | `reports/extraction-snapshots/index-qdii-source-017641-2024/quality_gate.json`; `reports/extraction-snapshots/index-qdii-source-017641-2024/quality_gate.md` |

Additional read-only public-output inspection commands:

- `sed -n` over generated `summary.md`, `errors.jsonl`, `score.md`, and `quality_gate.md`.
- `rg -n "fallback|source|upstream|not_found|unavailable|schema_drift|identity_mismatch|integrity_error|Eastmoney|category|error" reports/extraction-snapshots/index-qdii-source-110020-2024`.
- `rg -n "fallback|source|upstream|not_found|unavailable|schema_drift|identity_mismatch|integrity_error|Eastmoney|category|error" reports/extraction-snapshots/index-qdii-source-017641-2024`.
- `jq 'keys'` over generated `score.json` and `quality_gate.json`.
- `awk 'END {print NR}'` over generated `errors.jsonl`.

## Per-Candidate Terminal State

| Candidate | Snapshot result | Score / gate result | Original upstream category recovered? | Terminal state | Reason |
|---|---|---|---|---|---|
| `110020` / 2024 | `summary.md` reports `succeeded_funds: 1`, `failed_funds: 0`, `classified_fund_type: index_fund`; `errors.jsonl` has 0 lines | score `p0_status: pass`; quality gate `status: warn`, 3 issues | No | `unrecoverable_safe_path` | Public outputs expose successful repository-backed extraction plus field-level quality issues, but do not expose the original upstream failure category. No direct PDF/cache/source-helper/downloader access is allowed, and fallback eligibility cannot be inferred from later extraction success. |
| `017641` / 2024 | `summary.md` reports `succeeded_funds: 1`, `failed_funds: 0`, `classified_fund_type: qdii_fund`; `errors.jsonl` has 0 lines | score `p0_status: fail`; quality gate `status: block`, 8 issues | No | `unrecoverable_safe_path` | Public outputs expose successful repository-backed extraction plus field-level quality issues, but do not expose the original upstream failure category. The P0/P1 extraction failures are downstream field evidence, not direct upstream category evidence. |

No row is classified as `recovered_eligible`, `recovered_fail_closed`, `repository_run_failed`, `replacement_verified`, or `not_run_no_approved_candidates`.

Subgate B replacement probing closes as `not_run_no_approved_candidates` for both `110020` / 2024 and `017641` / 2024 because this handoff approved no replacement candidates. This Subgate B terminal state does not make either original row clean; both original rows remain outside the clean denominator because Subgate A ended as `unrecoverable_safe_path`.

## Direct Evidence Notes

`110020` / 2024:

- `reports/extraction-snapshots/index-qdii-source-110020-2024/summary.md` directly shows one selected fund, one succeeded fund, zero failed funds, and `classified_fund_type` = `index_fund`.
- `reports/extraction-snapshots/index-qdii-source-110020-2024/errors.jsonl` is empty.
- `reports/extraction-snapshots/index-qdii-source-110020-2024/quality_gate.md` directly shows `status: warn`; issues are `turnover_rate` coverage/traceability and missing correctness oracle coverage for this fund.
- `jq 'keys' reports/extraction-snapshots/index-qdii-source-110020-2024/score.json` shows no top-level source-recovery or upstream-failure-category field. `quality_gate.json` top-level keys are only `issue_count`, `issues`, `rule_results`, `score_path`, and `status`.

`017641` / 2024:

- `reports/extraction-snapshots/index-qdii-source-017641-2024/summary.md` directly shows one selected fund, one succeeded fund, zero failed funds, and `classified_fund_type` = `qdii_fund`.
- `reports/extraction-snapshots/index-qdii-source-017641-2024/errors.jsonl` is empty.
- `reports/extraction-snapshots/index-qdii-source-017641-2024/quality_gate.md` directly shows `status: block`; issues are `manager_strategy_text`, `turnover_rate`, `holdings_snapshot`, missing correctness oracle coverage, and field missing-rate warning.
- `jq 'keys' reports/extraction-snapshots/index-qdii-source-017641-2024/score.json` shows no top-level source-recovery or upstream-failure-category field. `quality_gate.json` top-level keys are only `issue_count`, `issues`, `rule_results`, `score_path`, and `status`.

The `rg` scans found generic field/source strings in public extraction and score artifacts, but no direct `fallback_used`, original upstream failure category, or eligible/fail-closed source taxonomy evidence for either candidate.

## Scratch / Ignored Output Paths

Generated public CLI outputs are under ignored report paths:

- `reports/extraction-snapshots/index-qdii-source-110020-2024/`
- `reports/extraction-snapshots/index-qdii-source-017641-2024/`

These paths contain generated snapshot, errors, summary, score, golden-set, and quality-gate outputs. They are evidence scratch only and are not promoted to tracked baseline, golden, or fixture material.

## Source Boundary Compliance

- Used only public `fund-analysis` CLI commands for extraction snapshot, scoring, and quality gate.
- Did not inspect PDFs, PDF cache contents, source helpers, source-specific downloaders, or repository internals.
- Did not use ad hoc web/search replacement discovery.
- Did not modify source strategy, `FundDocumentRepository`, extractors, renderer, FQ0-FQ6 rules, Service/CLI behavior, Host/Agent/Dayu code, `fund_type.py`, golden fixtures, or baseline fixtures.

## Baseline / Golden Promotion

- No golden answer was changed.
- No baseline fixture was created or promoted.
- `golden_set.json` files generated by `extraction-score` remain scratch outputs under ignored report directories.
- Both original rows remain outside the clean denominator because original upstream fallback eligibility was not recovered from public output artifacts.

## Residual Risks And Next Recommended Gate

- Public CLI output currently does not expose the original upstream source failure category for fallback-backed candidates. That makes source-safety recovery impossible without either a future approved public-output contract change or a controller-approved replacement candidate.
- Because no replacement candidates were approved in this handoff, the safe closeout is to keep `110020` and `017641` excluded from durable baseline/golden selection for this gate.
- Recommended next gate: controller judgment on this evidence artifact, then decide whether to authorize a separate design/implementation gate to expose source recovery metadata through public repository outputs, or to provide explicitly approved replacement candidates for index/QDII coverage.

## Validation

- Required closeout validation commands:
  - `git diff --check`
  - `git status --short`

Expected status shape: this tracked summary artifact plus pre-existing unrelated untracked files; generated `reports/extraction-snapshots/...` outputs should remain ignored and unstaged.
