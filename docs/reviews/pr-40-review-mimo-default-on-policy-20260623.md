# Code Review — PR-40 Evidence Confirm Default-on Policy

## Scope

- Mode: PR Review
- PR: #40 `https://github.com/bill20232033cc/fund-agent/pull/40`
- Title: Add Evidence Confirm productionization and service integration
- Base branch: `evidence-confirm-anchor-audit-score`
- Head: `3c4fe064775a50c5e7b5fec58d5fce8ec03c39f7`
- PR state: OPEN, draft
- CI status: `test` = SUCCESS
- Output file: `docs/reviews/pr-40-review-mimo-default-on-policy-20260623.md`
- Included scope:
  - `fund_agent/services/fund_analysis_service.py` — Service-layer default-on policy, contract resolution, EC runner integration
  - `fund_agent/ui/cli.py` — CLI surface, developer override, stderr summary
  - `fund_agent/fund/evidence_confirm_runner.py` — Fund-layer facade
  - `fund_agent/fund/evidence_confirm_production.py` — Production summary dataclass and conversion
  - `fund_agent/fund/quality_gate_integration.py` — ECQ0-ECQ4 issue projection
  - `fund_agent/fund/evidence_confirm_semantic.py` — Semantic companion contract
  - `fund_agent/fund/evidence_confirm_sources.py` — Repository-bounded runner
  - `tests/services/test_fund_analysis_service.py` — Default-on policy tests
  - `tests/ui/test_cli.py` — CLI summary and override tests
  - `tests/fund/test_quality_gate_integration.py` — ECQ projection tests
  - `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `README.md` — Documentation sync
- Excluded scope:
  - Local commit `0e2d321` (controller bookkeeping after push/update, not part of PR-40)
  - Review artifacts under `docs/reviews/` (metadata, not reviewed as code)
- Parallel review coverage: 无

## Findings

未发现实质性问题。

### Verification Summary

**1. Default-on Policy Correctness**

- `_resolve_analyze_contract` (fund_analysis_service.py:1587-1614): product path (no developer overrides) correctly sets `evidence_confirm_policy="warn"`.
- Developer override path (line 1614): `overrides.evidence_confirm_policy or "off"` — explicit override used when provided, otherwise `"off"`. This correctly isolates developer sandbox from product defaults.
- `_effective_evidence_confirm_policy` (line 1658-1682): `checklist` command source returns `"off"` unconditionally; `analyze` returns the resolved contract policy. This correctly prevents checklist from inheriting warn.
- `_resolve_analyze_contract` for developer mode (line 1614): `overrides.evidence_confirm_policy or "off"` — when developer passes `--dev-override` without `--evidence-confirm-policy`, the value is `None` → `"off"`. Correct: developer sandbox defaults to off, not warn.

**2. Architecture Boundary Compliance**

| Boundary | Check | Result |
|---|---|---|
| UI → Service | CLI only imports `EvidenceConfirmBlockedError` from Service | 符合 |
| Service → Fund (facade) | Service imports from `evidence_confirm_runner.py` (facade), not directly from `evidence_confirm_sources.py` | 符合 |
| Service → Fund (production) | Service imports `summary_from_repository_result` from `evidence_confirm_production.py` | 符合 |
| No source/PDF internals | Service does not import `FundDocumentRepository`, `load_annual_report`, PDF helpers, or source adapters | 符合 |
| Renderer guard | PR body states "renderer non-rendering guard, so report Markdown does not include Evidence Confirm content" | 符合 |
| ECQ projection boundary | `_evidence_confirm_quality_gate_issues` only consumes compact `EvidenceConfirmProductionSummary`, not repository/PDF/cache/provider | 符合 |

**3. PR Body Truthfulness**

| Claim | Verified |
|---|---|
| product `analyze` defaults to `warn` | ✅ `_resolve_analyze_contract` line 1587 |
| `analyze-annual-period` inherits `warn` via `analyze()` delegation | ✅ `analyze_multi_year_annual` calls `analyze()` which uses `_resolve_analyze_contract` |
| `checklist` remains `off` | ✅ `_effective_evidence_confirm_policy` returns `"off"` for `checklist` |
| `--evidence-confirm-policy` behind `--dev-override` | ✅ CLI only exposes option, Service gates on developer mode |
| plain `--dev-override` keeps EC `off` | ✅ `overrides.evidence_confirm_policy or "off"` when None → "off" |
| No provider-backed semantic quality proof | ✅ PR body Non-goals section |
| No checklist Evidence Confirm CLI support | ✅ PR body Non-goals section |
| No report-body Evidence Confirm rendering | ✅ PR body Non-goals section |
| No release/readiness promotion | ✅ PR body Non-goals section |
| PR remains draft, no mark-ready/merge | ✅ PR state is draft/open |

**4. Test Coverage for Default-on Behavior**

| Test | Coverage |
|---|---|
| `test_fund_analysis_service_product_analyze_default_warn_calls_evidence_confirm` | Product analyze → warn → runner called |
| `test_fund_analysis_service_product_analyze_default_warn_fail_is_non_blocking` | Warn policy → EC fail → no `EvidenceConfirmBlockedError` |
| `test_fund_analysis_service_product_analyze_default_warn_runner_exception_becomes_safe_summary` | Runner exception → safe summary (no path/secret leak) |
| `test_fund_analysis_service_product_checklist_default_keeps_evidence_confirm_off` | Checklist → EC not called |
| `test_fund_analysis_service_developer_default_and_explicit_off_do_not_inherit_warn` | Developer mode → off |
| `test_multi_year_annual_analysis_product_default_inherits_evidence_confirm_warn` | Annual-period → warn inherited |
| `test_analyze_cli_default_product_prints_evidence_confirm_warn_summary` | CLI stderr summary output |
| `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off` | Plain --dev-override → off |
| `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` | ECQ2 with warn policy → severity warn |
| `test_quality_gate_integration_maps_evidence_confirm_fail_to_ecq2_block` | ECQ2 with block policy → severity block |

**5. Runner Exception Safety**

`_run_evidence_confirm_if_enabled` (fund_analysis_service.py:1301-1351) catches all exceptions (`except Exception`) and converts to `_runner_exception_evidence_confirm_summary` which produces a safe summary with reason `runner_exception:<class_name>`. The exception type name is used, not the message, preventing leakage of file paths, provider secrets, or parser payloads. Verified by test `test_fund_analysis_service_product_analyze_default_warn_runner_exception_becomes_safe_summary` which passes a RuntimeError containing `/tmp/raw.pdf parser_payload provider_secret excerpt` and asserts no leakage.

**6. Block Behavior**

`_raise_evidence_confirm_block_if_required` (fund_analysis_service.py:1752-1766) only raises `EvidenceConfirmBlockedError` when `policy == "block"` AND `status == "fail"`. Under the product default `warn`, EC failures are non-blocking. Verified by test `test_fund_analysis_service_product_analyze_default_warn_fail_is_non_blocking`.

## Open Questions

无。

## Residual Risk

| Risk | Status | Note |
|---|---|---|
| `checklist` EC CLI support | Not in scope | PR body explicitly lists as non-goal; separate gate required |
| Annual-period CLI EC summary display | Not in scope | PR body notes "CLI 尚未单独展示 annual-period 的 Evidence Confirm summary 行" |
| Provider-backed semantic quality | Not in scope | PR body explicitly lists as non-goal |
| Multi-sample live source/PDF proof | Not in scope | PR body explicitly lists as non-goal |
| Report-body EC rendering | Not in scope | PR body explicitly lists as non-goal |

## Validation / Read-only Commands Used

| Command | Purpose |
|---|---|
| `gh pr view 40 --json number,title,state,isDraft,headRefOid,baseRefName,mergeStateStatus,statusCheckRollup,url,body` | PR metadata |
| `gh pr diff 40` | Full PR diff |
| `gh pr checks 40` | CI status |
| `git show --stat 3c4fe064775a50c5e7b5fec58d5fce8ec03c39f7` | Commit stats |
| `git diff evidence-confirm-anchor-audit-score...3c4fe064775a50c5e7b5fec58d5fce8ec03c39f7 -- <files>` | Per-file diffs |
| `rg/grep` on diff output | Import boundary verification |

## Reviewer Self-Check

- [x] review mode、base/PR、included/excluded scope 和 source evidence 已写清
- [x] 无 findings 需要绑定 code location（未发现实质性问题）
- [x] adversarial pass 完成：architecture boundary、PR body truthfulness、default-on correctness、test coverage、runner exception safety
- [x] open questions、residual risk 和未覆盖区域已记录
- [x] output path 位于 `docs/reviews/`
- [x] 未修改任何代码、PR body、git index、branch、remote 或 GitHub state

## Verdict

PR_REVIEW_PASS
