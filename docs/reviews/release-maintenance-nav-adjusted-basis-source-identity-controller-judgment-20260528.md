# NAV Adjusted-Basis Source Identity Gate — Controller Judgment

日期：2026-05-28

角色：Gateflow controller，非 implementation worker。

Work unit：`NAV adjusted-basis source identity gate`

## Verdict

**Accepted local evidence with partial acceptance.**

Terminal decision：`partial-acceptance-with-blocked-classes`

本 gate 接受 Eastmoney / 天天基金 `累计净值走势` / `Data_ACWorthTrend` 作为未来 source adapter normalization gate 的 `accumulated_nav` source/basis identity candidate，但不解除 `drawdown_stress` blocker，不实现 max drawdown / volatility，不修改 score、snapshot、quality gate、golden fixture 或生产 Python 路径。

## Preflight And Scope

Gate 开始前已先运行：

```text
git branch --show-current
git status --short
```

结果：

- Branch：`codex/local-reconciliation`
- Tracked dirty：无
- Dirty scope：仅既有无关 untracked 文件；本 gate 新增 plan / review / evidence / judgment artifacts。

本 gate 使用 `$init-agents` tmux multi-agent flow：

- Codex：planning worker、planning fix worker、evidence worker。
- DS / GLM：plan review、plan re-review、evidence review。
- MiMo：未使用。

## Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Accepted plan | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-20260528.md` |
| Plan review: DS | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-review-ds-20260528.md` |
| Plan review: GLM | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-review-glm-20260528.md` |
| Plan re-review: DS | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-rereview-ds-20260528.md` |
| Plan re-review: GLM | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-rereview-glm-20260528.md` |
| Source evidence | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-20260528.md` |
| Evidence review: DS | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-review-ds-20260528.md` |
| Evidence review: GLM | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-review-glm-20260528.md` |

Accepted plan commit：

```text
8073178 gateflow: accept plan for NAV adjusted-basis source identity
```

## Controller Decision

### Accepted Candidate

Accepted source/basis candidate：

- Source：Eastmoney / 天天基金, currently reachable through Akshare `fund_open_fund_info_em` and same-provider JS identity metadata.
- Data function candidate：`ak.fund_open_fund_info_em(symbol=<code>, indicator="累计净值走势")`
- Provider variable lineage：`Data_ACWorthTrend`
- Identity URL candidate：`https://fund.eastmoney.com/pingzhongdata/{code}.js`
- Accepted `nav_type`：`accumulated_nav`
- Accepted `adjusted_basis`：`accumulated_nav`
- Accepted `dividend_adjustment_status`：implementation gate must decide exact runtime value; evidence proves additive accumulated NAV behavior for cash distributions, not dividend-reinvested total return.

Accepted share-class coverage：

- `006597` A：accepted source/basis identity candidate.
- `006598` C：accepted source/basis identity candidate.
- `014217` E：accepted source/basis identity candidate with exact 2023 distribution cross-check.
- `022176` F：accepted only for source-inception-forward windows; pre-2024-10-08 windows remain `missing_date_range`.

### Blocked Candidates

Still blocked / not accepted:

- `单位净值走势` / `Data_netWorthTrend` remains `raw_unit_nav`, `not_adjusted`, and not strong drawdown evidence.
- `累计收益率走势` / `LJSYLZS` remains `adjustment_basis_unknown` for all four classes. No source-owned semantics proved it is a total-return or dividend-reinvested path.
- `accumulated_nav` acceptance does not decide max drawdown / volatility metric suitability. That remains a separate future gate.

## Evidence Basis

E1 smoke verified A/C/E/F source capability:

- `006597` A, `006598` C, `014217` E, `022176` F all returned non-empty `单位净值走势`, `累计净值走势`, and `累计收益率走势` sequences.
- Same-provider JS identity returned matching `fS_code` and `fS_name` with A/C/E/F suffixes.
- E1 did not parse JS numeric variable contents; it recorded only `fS_code`, `fS_name`, and variable presence.

E2 proof foundation:

- `FundDocumentRepository.load_annual_report("006597", 2025)` confirmed official annual-report evidence for share-class code mapping and E-class 2023 distribution.
- Provider page evidence supplied E-class exact distribution date: `2023-01-11`, every share `0.0080`.
- Akshare provider series showed `014217` E `累计净值` minus `单位净值` changed from `0.0000` to `0.0080` exactly on `2023-01-11`, matching the official annual-report distribution amount of every 10 shares `0.080`.

This proves `Data_ACWorthTrend` additive accumulated NAV behavior for the E class. A/C acceptance is inferential: same provider, same variable, same product family, independent zero-distribution evidence from annual report and provider pages, and no observed divergence. Reviewers accepted this as source/basis candidate evidence with limitation recorded.

## Review Disposition

Plan review:

- DS initially accepted with two plan fixes: E-class ex-date fallback strategy and partial-acceptance output.
- GLM accepted with taxonomy and E1 JS parsing clarifications.
- Codex planning fix updated the plan.
- DS and GLM re-review both accepted.

Evidence review:

- DS accepted with non-blocking limitations:
  - A/C accumulated NAV proof is inferential via E-class behavior plus zero-distribution confirmation.
  - Identity proof is cross-endpoint same-provider binding, not same-response metadata.
- GLM accepted with non-blocking limitations:
  - A/C acceptance relies on transfer from E-class variable semantics.
  - A/C row-level equality should be programmatically checked in a future implementation gate.
  - Exact `dividend_adjustment_status` runtime enum choice belongs to implementation review.

Controller accepts these as residual implementation constraints, not blockers for this evidence gate.

## Residuals

`drawdown_stress` blocker remains:

- Current `006597 / 2024` score still has `bond_risk_evidence_missing.baseline_blocking=true`.
- `missing_evidence_groups` remains only `drawdown_stress`.
- This gate does not produce `bond_risk_evidence.v1.drawdown_stress` quantitative evidence.

Future implementation constraints:

- Future source adapter normalization must bind data endpoint and identity endpoint inside the Fund data boundary and record both provenance URLs / source IDs.
- Future adapter must fail closed on `schema_drift`, `identity_mismatch`, `integrity_error`, `adjustment_basis_unknown`, `missing_date_range`, `insufficient_records`, `not_found`, and `unavailable`.
- Future adapter must keep A/C/E/F separate and must not mix product-level NAV.
- Future implementation must decide `DividendAdjustmentStatus` value for accumulated NAV with no actual distribution in-window.
- Future metric contract must separately decide whether additive `accumulated_nav` is acceptable for max drawdown / volatility, since it is not total-return reinvestment.

## Validation

Run / reviewed:

- `git branch --show-current`
- `git status --short`
- E1/E2 source smoke through `uv run python`
- `FundDocumentRepository.load_annual_report("006597", 2025)` for annual-report evidence
- DS / GLM plan review and re-review
- DS / GLM evidence review

Not run:

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- extraction snapshot / score / quality gate reruns

Reason：this gate changed only `docs/reviews/` evidence/control artifacts and did not modify Python, tests, schema, runtime behavior, score, snapshot, quality gate, or golden fixtures.

## Next Entry Point

Next minimal gate：

```text
NAV accumulated-nav source adapter normalization implementation gate
```

Objective：

- Add a Fund data source adapter / repository path that fetches `累计净值走势` and same-provider identity metadata through the typed NAV boundary.
- Normalize `accumulated_nav` source/basis identity into `FundNavSeries`, `NavSourceMetadata`, and `ShareClassMapping`.
- Keep current `raw_unit_nav` path explicitly not strong evidence.
- Do not implement drawdown metric or unblock `drawdown_stress` in that gate unless a later reviewed metric contract authorizes it.

Non-goal：

- No drawdown metric, score policy, snapshot, quality gate, golden fixture, release, PR, push, merge, or promotion work.
