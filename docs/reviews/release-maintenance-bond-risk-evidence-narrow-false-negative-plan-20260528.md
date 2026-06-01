# Bond Risk Evidence Narrow False-Negative Plan

> Date: 2026-05-28
> Role: planning worker, not controller
> Gate: `bond risk evidence narrow false-negative gate`
> Work unit: `bond risk evidence narrow false-negative`
> Status: amended after accepted plan-review findings
> Blocking questions: none

## Worker Self-Check

### Before Start

- Role confirmed: planning worker only; no gateflow start, no implementation, no test run, no staging, no commit, no push, no PR.
- Truth sources read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, accepted bond-risk extractor/anchor plan, plan reviews/fix/controller judgment, Slice 6 validation/root-cause/investigation/controller judgment, and aggregate deepreview/controller judgment artifacts under `docs/reviews/`.
- Current outputs inspected: `reports/extraction-snapshots/bond-risk-evidence-006597-2024-20260528/snapshot.jsonl`, `reports/scoring-runs/bond-risk-evidence-006597-2024-20260528/score.json`, `reports/quality-gate-runs/bond-risk-evidence-006597-2024-20260528/quality_gate.json`.
- Current branch/status inspected: branch `codex/local-reconciliation`; pre-existing untracked files are unrelated review artifacts, `--help`, and `docs/tmux-agent-memory-store.md`.

### Before File Edit

- Allowed write path confirmed: this planning artifact only.
- No source code, tests, generated reports, control doc, README, score, snapshot, quality gate, Service/UI/Host/Agent/dayu, baseline, golden, PR, or GitHub state will be changed by this worker.

### Before Completion

- This plan is limited to a narrow extractor false-negative amendment for `credit_risk` and `redemption_share_pressure`, while preserving `drawdown_stress` as weak qualitative evidence unless a future quantitative metric contract exists.
- This plan explicitly incorporates the user correction: annual-report rating distribution is held bond/security rating distribution, not fund own rating; `006597` redemption pressure must aggregate A/C/E/F share classes, not just A.

## Goal And Motivation

Goal: fix two safe false negatives in the annual-report-only `bond_risk_evidence.v1` extractor for `006597` / 2024:

1. `credit_risk` should accept held bond/security rating distribution tables as `portfolio_credit_exposure / holding_rating_distribution`.
2. `redemption_share_pressure` should aggregate all share classes A/C/E/F from §10, with class breakdown, anchors, and arithmetic cross-checks.

Motivation: Slice 6 real validation proved the current implementation emits a positive `bond_risk_evidence.v1` row but leaves `credit_risk`, `drawdown_stress`, and `redemption_share_pressure` unsatisfied. Independent reviews agree `credit_risk` and `redemption_share_pressure` are extractor false negatives, while `drawdown_stress` is a true weak-evidence boundary under the current contract.

Expected best outcome for this gate: `006597` / 2024 score `missing_evidence_groups` drops to only `["drawdown_stress"]`. `bond_risk_evidence_missing.baseline_blocking=true` should remain because `drawdown_stress` is still unsatisfied.

## Hard Constraints

- `credit_risk` must not represent or imply fund own rating.
- Annual-report rating distribution tables are usable only as held bond/security rating distribution, under `portfolio_credit_exposure / holding_rating_distribution`.
- Do not add `fund_rating`, `ratings`, `fund_own_rating`, or wording that claims the fund itself has a rating.
- If future fund own rating support is desired, it requires a separate reviewed contract containing at minimum: rating object, agency, rating date, and source anchor.
- `redemption_share_pressure` for `006597` must aggregate all disclosed share classes A/C/E/F, not just A.
- The A/C/E/F computation must include beginning shares, subscription shares, redemption shares, ending shares, net change, net change ratio, class breakdown, and row/class anchors.
- Redemption aggregation must fail closed if class mapping, numeric parsing, row matching, class count, or arithmetic reconciliation does not align.
- `drawdown_stress` remains weak qualitative evidence unless max drawdown, volatility, or an accepted stress metric exists. No NAV-derived drawdown calculation in this gate.
- No FQ0-FQ6 weakening, no score-policy bypass, no missing evidence pass, no quality gate semantic change.
- No direct PDF/cache/source helper access; production annual-report access remains through `FundDocumentRepository`, and this extractor consumes only `ParsedAnnualReport`.
- No QDII/FOF/110020/golden readiness/release/Host-Agent-dayu/PR/push/merge.

## Direct Evidence

### Current Output Evidence

`snapshot.jsonl` currently has one `bond_risk_evidence` row:

- `bond_risk_contract_status=partial`
- satisfied groups: `duration_rate_risk`, `leverage_liquidity`, `asset_allocation_holdings_mix`, `convertible_bond_equity_exposure`
- weak groups: `credit_risk`, `drawdown_stress`
- ambiguous groups: `redemption_share_pressure`

`score.json` currently emits:

- `issue_code=bond_risk_evidence_missing`
- `baseline_blocking=true`
- `required_evidence_groups` equals all seven bond-risk groups
- `missing_evidence_groups=["credit_risk","drawdown_stress","redemption_share_pressure"]`

`quality_gate.json` currently remains `warn` and includes FQ2F `reason=bond_risk_evidence_missing`. Other warnings for `turnover_rate`, `holder_structure`, and `share_change` are unrelated to this gate.

### Root-Cause Evidence

Accepted Slice 6 investigations found:

- `credit_risk`: rating distribution tables exist, but current row matching requires credit/rating terms inside data rows; real data rows contain rating categories such as `A-1`, `AAA`, `AAA以下`, `未评级`, `合计`.
- `redemption_share_pressure`: the actual §10 share-change table exists, but current table selection can hit a net-asset statement table first, and §2 share-class mapping fails for table-style A/C/E/F layouts.
- `drawdown_stress`: annual report has qualitative `控制回撤` intent only; no max drawdown, volatility, or stress metric was found.

## Scope

Allowed files:

- `fund_agent/fund/extractors/bond_risk_evidence.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- new implementation/review/controller artifacts under `docs/reviews/`

Allowed only if implementation proves mandatory and plan review accepts the reason:

- no expected changes to `fund_agent/fund/extractors/models.py`
- no expected changes to `fund_agent/fund/extraction_snapshot.py`
- no expected changes to `fund_agent/fund/extraction_score.py`
- no expected changes to `fund_agent/fund/quality_gate.py`
- no expected changes to Service/UI/Host/Agent/dayu modules

Docs decision:

- No README or `docs/design.md` update is expected because no schema, public CLI, quality gate semantic, template chapter structure, or architecture boundary changes are planned.
- If implementation changes public fields, snapshot schema, score semantics, or user-facing commands despite this plan, stop and return to controller; do not broaden docs ad hoc.

Extraction mode decision:

- `extraction_mode` has no `partial` enum value. When `bond_risk_contract_status=partial`, keep `extraction_mode=ExtractionMode.estimated`; the structured `bond_risk_contract_status` field remains authoritative for partial contract status. Do not change extractor model schema in this gate.

## Contract Decisions

### Distinguish Fund Own Rating vs Portfolio Credit Exposure

Implementation must treat rating distribution as portfolio exposure evidence:

- group: `credit_risk`
- status: `accepted`
- strength: `quantitative_direct`
- measurement_kind: `actual_exposure`
- metric_name: `持仓评级分布` or `holding_rating_distribution`
- evidence_role: `holding_rating_distribution`
- summary wording: `年报表格披露持有债券/证券的信用评级分布`

Forbidden wording and data names:

- Do not use `fund_rating`, `ratings`, `fund_own_rating`, `基金评级`, `本基金评级`, or `评级为 AAA 的基金`.
- Do not infer rating agency, rating date, or fund-level credit assessment from holding distribution.

Fail-closed rule:

- If only qualitative credit strategy text exists, keep the current weak path.
- If a rating table is detected but lacks row/table anchors or recognizable rating categories, do not accept it.

### How Rating Distribution Enters Credit Risk

Add a dedicated helper in `bond_risk_evidence.py`, for example `_credit_rating_distribution_anchor_drafts(tables, group_id)`.

Detection rules:

- Candidate table must have table-level text containing held-position rating-distribution semantics, preferably header text containing `信用` and `评级`, or equivalent `短期信用评级` / `长期信用评级`.
- Candidate table must describe held bond/security/portfolio ratings. Acceptable semantics include §8 portfolio context, or header/table text containing `持有` / `持仓` / `证券` combined with `信用评级`.
- Explicitly reject fund-own-rating semantics. If header/table text contains `本基金评级`, `基金评级信息`, `基金自身评级`, or `本基金` + `评级` without held-position qualifiers (`持有` / `持仓` / `证券`), do not accept the table.
- Candidate rows must contain rating category tokens, not necessarily the words `信用` or `评级`.
- Recognized row labels include at minimum: `A-1`, `AAA`, `AA+`, `AA`, `AA-`, `A+`, `A`, `A-`, `BBB`, `AAA以下`, `未评级`, `合计`.
- Require numeric shape: at least one data row must have a recognized rating category label and a parseable current-period numeric amount. Tables with no numeric current-period amount, no row/table anchor, or fewer than two data rows must not be accepted.
- Prefer tables where the first semantic column contains rating category labels and the current-period column contains numeric amounts. Percentage-only or text-description-only tables are not sufficient for `accepted`.
- Prefer rows with non-empty current-period values; dash-only rows may be included only as supporting rows, not the sole positive evidence unless accompanied by a non-empty numeric `合计`.

Anchor rules:

- Use row-level anchors, not only a broad text anchor.
- `section_id` remains `_SECTION_PORTFOLIO` unless the parsed table carries a more precise section mechanism in current code.
- `page_number`, `table_id`, and `row_locator` must be populated.
- Generate one or more anchors with evidence role `holding_rating_distribution`.
- When multiple valid held-rating tables exist, retain anchors for all matching tables. Do not accept only the first table and discard the other anchors.
- `metric_value` should summarize current-period values from the first representative matching table as holding distribution, for example `长期信用评级: AAA=..., AAA以下=..., 未评级=..., 合计=...`; keep it concise with `_trim_note`.
- Include `合计` in `metric_value` when present. Prior-period values are supplementary and may be included in anchor notes, but they are not required in `metric_value`.

Acceptance rule:

- When at least one valid held bond/security rating distribution table with numeric current-period values and row-level anchor is found, `credit_risk` becomes `accepted / quantitative_direct / actual_exposure`.
- Qualitative credit strategy text may remain as fallback only when no valid rating distribution anchor exists; do not combine it to force acceptance.

### A/C/E/F Aggregate Redemption Pressure

Change `redemption_share_pressure` from single-class selection to explicit all-class aggregation when multiple share classes exist.

Required class mapping:

- Parse §2 subordinate fund mapping from parsed tables first, not only raw text lines.
- Table-based mapping must recognize a row containing `下属分级基金的基金简称` and a nearby row containing `下属分级基金的交易代码`.
- For `006597` / 2024, expected mapping is:
  - A -> `006597`
  - C -> `006598`
  - E -> `014217`
  - F -> `022176`
- The implementation must preserve this as class breakdown context. Do not select only the A column for `bond_risk_evidence`; A-only belongs to a separate per-fund-code `share_change` extractor problem and is not sufficient here.

Required §10 share-change table selection:

- Scan all parsed tables; do not return the first table matching `期初` / `期末` / `申购` / `赎回`.
- Score candidates and select the best §10 share-change table: prefer section/header/table text containing `§10` / `基金份额` / `份额总额` / `总申购份额` / `总赎回份额` / `期初` / `期末`.
- Explicitly reject or heavily downgrade financial-statement tables with `实收基金`, `未分配利润`, `净资产合计`, even if they contain `申购` / `赎回`.
- If multiple non-rejected candidates survive with no unique best candidate, fail closed as `ambiguous` instead of guessing.
- Require value columns to align with all mapped classes A/C/E/F by §2 mapping or recognizable §10 header labels.
- Exclude row-label columns and total/合计 columns from class-column matching. If the mapping has four classes but the §10 table cannot align exactly four class value columns, fail closed as `ambiguous` with `na_reason="share_class_column_count_mismatch"`.

Required rows and calculations:

- beginning: row matching `期初` and `基金份额总额`
- subscription: row matching `申购`
- redemption: row matching `赎回`
- split/change: row matching `拆分变动` if present; treat dash as zero
- ending: row matching `期末` and `基金份额总额`
- class net change: `subscription - redemption + split`
- class arithmetic check: `beginning + subscription - redemption + split == ending`, with tolerance `Decimal("0.01")`
- aggregate beginning/subscription/redemption/split/ending: sum A/C/E/F class values
- aggregate net change: `aggregate_subscription - aggregate_redemption + aggregate_split`
- aggregate net change ratio: `aggregate_net_change / aggregate_beginning`; if aggregate beginning is zero or missing, fail closed unless a controller-approved rule says otherwise
- aggregate arithmetic check: sum of class ending equals aggregate ending and `aggregate_beginning + aggregate_net_change == aggregate_ending`
- per-class net change ratio: if a class beginning is zero, set the class ratio to `None` and include note `class_beginning_zero`. This is not a failure for F 类期初 `-`; only aggregate beginning zero fails closed.

Share value parsing contract:

- Strip commas and all surrounding/internal whitespace before `Decimal()` conversion.
- Treat `-`, `－`, `—`, and `--` as `Decimal(0)`.
- Do not set a custom Decimal context precision for this gate.
- If `Decimal()` conversion raises `InvalidOperation`, fail closed as `ambiguous` with `na_reason="non_parseable_share_value"`.
- Use absolute tolerance `abs(computed - stated) <= Decimal("0.01")` for class and aggregate reconciliation.

Metric value:

- `metric_name="A/C/E/F 份额变动汇总"`
- `metric_value` must include aggregate beginning, subscription, redemption, ending, net change, net change ratio, and compact class breakdown. Example shape:
  `all_classes: beginning=..., subscription=..., redemption=..., ending=..., net_change=..., net_change_ratio=...; A(...); C(...); E(...); F(...)`

Anchor rules:

- Emit anchors for the four required rows at minimum: beginning, subscription, redemption, ending.
- Include row-level anchors from the actual §10 share-change table.
- Include a §2 mapping anchor if current helper design can express it without model changes; if not, include the mapping source in `metric_value`/summary and keep §10 row anchors as source anchors.
- If any required row lacks an anchor, return `ambiguous` with `na_reason="incomplete_share_change_rows"` or a more precise fail-closed reason.

Acceptance rule:

- Only all-class aggregation with complete mapping, complete rows, parseable numbers, anchors, and arithmetic reconciliation can set `redemption_share_pressure` to `accepted / quantitative_direct / actual_exposure`.
- Single-class A-only selection must not satisfy this group for `006597`.

### Drawdown Boundary

No implementation changes should upgrade `drawdown_stress`.

Current accepted behavior remains:

- qualitative `控制回撤` text -> `weak`
- strength -> `qualitative_control_intent`
- measurement_kind -> `control_intent`
- `drawdown_stress` not in `satisfied_group_ids`

Accepted quantitative boundary:

- Only disclosed max drawdown, volatility, direct stress metric, or a future reviewed NAV-derived metric contract can satisfy `drawdown_stress`.
- This gate must not calculate drawdown from NAV, add NAV-derived anchors, or change `BOND_RISK_EVIDENCE_GROUPS`.

## Implementation Slices

### Slice 1: Credit Rating Distribution Helper

Allowed file: `fund_agent/fund/extractors/bond_risk_evidence.py`

Implementation decisions:

- Add module-level constants for rating row labels and credit-rating table keywords; avoid magic strings scattered across logic.
- Add `_credit_rating_distribution_anchor_drafts(...)` or equivalent module-private helper.
- Update `_extract_credit_risk()` to call the dedicated helper before qualitative fallback.
- Keep fallback text behavior unchanged when no table evidence is accepted.
- The helper must reject fund-own-rating headers and require held-position/portfolio credit-rating semantics plus numeric current-period amount shape before returning accepted anchors.
- The helper must preserve anchors for all matching held-rating tables; `metric_value` may summarize the first representative table only.

Stop conditions:

- If implementing this requires model/schema changes or score/snapshot changes, stop and return to controller.
- If the helper cannot distinguish holding rating distribution from fund own rating wording, stop and revise plan.
- If the helper matches a table where `AAA` or other rating tokens appear in fund-own-rating context, stop and revise plan.

### Slice 2: All-Class Share Mapping And §10 Table Selection

Allowed file: `fund_agent/fund/extractors/bond_risk_evidence.py`

Implementation decisions:

- Add a small internal dataclass if useful, for example `_ShareClassMapping(class_labels, fund_codes, source_note, source_anchor_draft?)`.
- Prefer parsed §2 table mapping over raw text proximity.
- Keep existing text-line mapping only as fallback.
- Replace or wrap `_select_share_change_column()` for bond-risk redemption pressure so the group uses all mapped class columns, not a single column.
- Improve `_find_share_change_table()` to scan all tables, score candidates, prefer real §10 share-change tables, reject or downgrade net-asset statement tables, and fail closed if no unique surviving best candidate exists.
- Align §10 columns using §2 class mapping order or explicit §10 header labels; exclude total columns and fail closed with `share_class_column_count_mismatch` when class-column count does not match.

Stop conditions:

- If all-class mapping is unavailable, return `ambiguous`; do not fall back to A-only for `006597`.
- If table selection hits a financial-statement table, tests must catch it before acceptance.

### Slice 3: Redemption Aggregation And Fail-Closed Reconciliation

Allowed file: `fund_agent/fund/extractors/bond_risk_evidence.py`

Implementation decisions:

- Use `Decimal` for share values; parse comma-separated values after removing commas and whitespace, and parse `-` / `－` / `—` / `--` as zero.
- Compute class and aggregate beginning/subscription/redemption/split/ending/net_change/net_change_ratio.
- Add row-level anchors for required §10 rows.
- Set `metric_value` to a deterministic compact summary.
- Fail closed to `ambiguous` for any missing class, missing row, non-parseable number, duplicate class mapping, column count mismatch, or arithmetic mismatch.
- For individual class beginning zero, set per-class net_change_ratio to `None` and add note `class_beginning_zero`; do not drop the class and do not fail unless aggregate beginning is zero.
- Use `Decimal("0.01")` as the reconciliation tolerance. On `InvalidOperation`, fail closed with `na_reason="non_parseable_share_value"`.

Stop conditions:

- Do not silently ignore F share because it has beginning `-`; parse dash as zero and include it in class breakdown.
- Do not accept a table that cannot align A/C/E/F columns.

### Slice 4: Tests And Real-Path Assertions

Allowed file: `tests/fund/extractors/test_bond_risk_evidence.py`

Implementation decisions:

- Add targeted synthetic unit tests first, then optionally a slow/real-path test only if existing test conventions allow it. The required real-path validation can also be performed as CLI validation artifact by controller.
- Keep tests deterministic; do not require network inside unit tests.

Stop conditions:

- If real `006597` path cannot be unit-tested without network/cache dependence, document it as validation command output rather than a normal pytest fixture.

## Required Tests

### Credit Risk

- `test_holding_rating_distribution_table_is_credit_risk_portfolio_exposure_not_fund_rating`
  - Build a table whose header contains `长期信用评级` and rows contain `AAA`, `AAA以下`, `未评级`, `合计`.
  - Assert `credit_risk.status == "accepted"`.
  - Assert `strength == "quantitative_direct"`.
  - Assert `measurement_kind == "actual_exposure"`.
  - Assert `metric_name` / `summary` uses holding/portfolio exposure wording.
  - Assert no value, summary, note, or metric uses forbidden fund-own-rating wording.
  - Assert row-level anchor has page, table id, and row locator.
  - Assert current-period numeric amounts are required for accepted status.

- `test_fund_own_rating_table_is_rejected_for_credit_risk`
  - Build a table whose header contains `本基金评级` / `基金评级信息` and row labels such as `AAA`.
  - Assert it does not satisfy `credit_risk` as portfolio credit exposure.

- `test_multiple_holding_rating_distribution_tables_preserve_all_anchors`
  - Build short-term and long-term held-rating tables.
  - Assert accepted `credit_risk` retains anchors for all valid tables while `metric_value` summarizes a representative current-period table.

- `test_credit_risk_qualitative_text_without_rating_distribution_remains_weak`
  - Only credit strategy text exists.
  - Assert current weak behavior remains and `credit_risk` is not satisfied.

- `test_credit_risk_anchor_missing_not_accepted`
  - Use helper-level or value-level validation to prove accepted credit risk without resolvable anchor fails or is downgraded.

### Redemption Share Pressure

- `test_share_class_evidence_from_section_two_table`
  - Build a synthetic §2 table with `下属分级基金的基金简称` and `下属分级基金的交易代码` rows.
  - Assert parsed table mapping returns A/C/E/F -> `006597`/`006598`/`014217`/`022176` in order and records mapping source evidence.

- `test_redemption_share_pressure_aggregates_all_a_c_e_f_classes`
  - Synthetic §2 mapping A/C/E/F to codes and §10 table with the `006597` real shape.
  - Assert all four classes are included, including F with beginning dash parsed as zero.
  - Assert aggregate beginning, subscription, redemption, ending, net change, and net change ratio are present in `metric_value`.
  - Assert class breakdown includes A, C, E, and F.
  - Assert F per-class net change ratio is `None` or represented with `class_beginning_zero`, not omitted.
  - Assert at least four §10 row anchors exist.

- `test_redemption_share_pressure_not_a_only`
  - Use values where A-only aggregate differs from all-class aggregate.
  - Assert `metric_value` contains the all-class totals, not A-only values.

- `test_redemption_share_pressure_rejects_net_asset_statement_table`
  - Put a financial-statement table before the true §10 share-change table.
  - Assert the extractor chooses the §10 share-change table.

- `test_redemption_share_pressure_fails_closed_when_class_columns_do_not_align`
  - §2 mapping has A/C/E/F but §10 table has fewer, extra non-total, or mismatched class columns.
  - Assert `status="ambiguous"`, `na_reason="share_class_column_count_mismatch"`, and the group is not satisfied.

- `test_redemption_share_pressure_fails_closed_on_arithmetic_mismatch`
  - Deliberately make `beginning + subscription - redemption + split != ending`.
  - Assert `status="ambiguous"`.

- `test_redemption_share_pressure_fails_closed_on_non_parseable_share_value`
  - Use a current-period share value that remains non-parseable after comma/whitespace cleanup.
  - Assert `status="ambiguous"` and `na_reason="non_parseable_share_value"`.

- `test_redemption_share_pressure_parses_full_width_dash_as_zero`
  - Use full-width dash `－` for a class split or beginning value.
  - Assert it is parsed as zero and reconciliation still uses all classes.

- `test_redemption_share_pressure_anchor_missing_not_accepted`
  - Missing one required row anchor keeps the group ambiguous.

### Drawdown

- `test_drawdown_control_text_alone_remains_weak_after_false_negative_fix`
  - Assert qualitative `控制回撤` remains weak and unsatisfied.
  - Assert no NAV-derived drawdown value is introduced.

### Real 006597 Public Path

Controller validation after implementation must rerun:

- repository smoke for `FundDocumentRepository` loading `006597` / 2024
- `fund-analysis extraction-snapshot`
- `fund-analysis extraction-score`
- `fund-analysis quality-gate`

Expected assertions:

- Snapshot `bond_risk_satisfied_groups` includes `credit_risk` and `redemption_share_pressure`.
- Snapshot `bond_risk_weak_groups` contains `drawdown_stress`.
- Snapshot `bond_risk_ambiguous_groups` no longer contains `redemption_share_pressure`.
- Score `missing_evidence_groups` drops to only `["drawdown_stress"]`.
- Score still has `bond_risk_evidence_missing.baseline_blocking=true`.
- Quality gate still includes FQ2F `reason=bond_risk_evidence_missing` until drawdown is quantitatively satisfied.

## Validation Commands

Required commands before implementation acceptance:

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
uv run python -c "from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence; print('import OK')"
uv run python -c 'import asyncio; from fund_agent.fund.documents import FundDocumentRepository; repo = FundDocumentRepository(); report = asyncio.run(repo.load_annual_report("006597", 2024, force_refresh=True)); print(report.key.fund_code, report.key.year, len(report.sections), len(report.tables))'
uv run fund-analysis extraction-snapshot --run-id bond-risk-narrow-006597-2024-20260528 --fund-code 006597 --report-year 2024 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/bond-risk-narrow-006597-2024-20260528
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/bond-risk-narrow-006597-2024-20260528/snapshot.jsonl --errors-path reports/extraction-snapshots/bond-risk-narrow-006597-2024-20260528/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/bond-risk-narrow-006597-2024-20260528
uv run fund-analysis quality-gate --score-path reports/scoring-runs/bond-risk-narrow-006597-2024-20260528/score.json --output-dir reports/quality-gate-runs/bond-risk-narrow-006597-2024-20260528
```

Notes:

- The real smoke must use `FundDocumentRepository`; no direct PDF/cache/source helper.
- The `FundDocumentRepository.load_annual_report` smoke must call the async method through `asyncio.run(...)`.
- The targeted import smoke must run before the full extraction pipeline to catch import-time helper errors quickly.
- Use the new `bond-risk-narrow-006597-2024-20260528` run-id/output directories so validation output does not overwrite the previous gate's `bond-risk-evidence-006597-2024-20260528` artifacts.
- Generated `reports/...` files remain validation outputs, not tracked fixtures, unless a later artifact disposition gate says otherwise.

## Review Gates

Plan review:

- At least two independent reviews before controller acceptance, unless controller records reviewer unavailability.
- Review must explicitly check fund-own-rating confusion, all-class redemption aggregation, drawdown boundary, and no FQ0-FQ6 weakening.

Implementation review:

- Review Slice 1 for false-positive risk in rating table detection and forbidden rating wording.
- Review Slice 2/3 for A/C/E/F aggregation, Decimal parsing, class/table alignment, row anchors, and arithmetic fail-closed behavior.
- Review tests for negative cases: missing anchor, A-only not accepted, class mismatch, arithmetic mismatch, qualitative drawdown weak.

Aggregate review:

- If implementation is accepted, run aggregate deepreview before any readiness claim.
- Do not proceed to ready-to-open-draft-PR unless controller separately decides the work unit is no longer blocked for its accepted goal. This narrow gate is expected to remain blocked by drawdown if the original goal is full blocker解除.

## Residuals

| Residual | Owner / next gate | Handling |
|---|---|---|
| `drawdown_stress` remains weak for `006597` | future NAV-derived drawdown/stress metric design gate | Do not resolve here. Define source, calculation, anchors, and score semantics separately. |
| `bond_risk_evidence_missing.baseline_blocking=true` remains if only drawdown is unsatisfied | controller | Expected and correct under current contract. Do not suppress. |
| Existing unrelated P1 gaps (`turnover_rate`, `holder_structure`, `share_change`) | future extractor gates | Out of scope. Do not fix opportunistically. |
| Generated report artifacts | controller artifact disposition | Keep as local validation evidence unless separately accepted. |

## Completion Report Format

Implementation worker should report:

- Files changed.
- For `credit_risk`: exact helper added, accepted evidence wording, forbidden fund-rating wording check, anchor shape.
- For `redemption_share_pressure`: class mapping source, selected §10 table, A/C/E/F class totals, aggregate totals, net change ratio, arithmetic reconciliation result, anchor count.
- For `drawdown_stress`: explicit confirmation it remains weak and unsatisfied.
- Validation command results.
- Real `006597` rerun summary: snapshot groups, score missing groups, quality gate FQ2F status.
- Residuals and any deviations from this plan.

## Explicit Non-Goals And Hard Stops

- No FQ0-FQ6 weakening.
- No direct PDF/cache/source helper.
- No missing evidence pass.
- No fund rating confusion.
- No A-only redemption aggregate.
- No NAV-derived drawdown.
- No QDII, FOF, `110020`, golden readiness, release readiness, Host/Agent/dayu, PR, push, merge, or external GitHub mutation.
