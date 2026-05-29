# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.1
> **日期**: 2026-05-27
> **设计真源**: `docs/design.md` (v2.2)
> **规则真源**: `AGENTS.md`
> **历史快照**: `docs/archive/implementation-control-history-20260525.md`
> **release-maintenance 长账本**: `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`
> **当前状态**: release maintenance；strict golden correctness / fixture promotion gate 已 accepted local validation；tracked residual disposition manifest 与 tracked fixture promotion state manifest 均存在但都不是 promotion manifest，且未被 runtime/preflight 消费；006597/2024 的 bond risk evidence blocker 保持 closed；当前 golden v1 仍 blocked，下一最小入口为 004393 / 004194 / 006597 strict correctness follow-up gate；golden promotion 未进入

---

## Startup Packet

### Current Truth Guardrails

本节是每个总控 / 子 Agent 恢复任务时必须先读取并复述的当前执行口径。

- 当前真源只包括 `AGENTS.md`、`docs/design.md` 当前设计章节、本文档 Startup Packet 和当前 gate。
- `docs/reviews/` 与 `docs/archive/` 只作为证据链；旧六层、Application、Runtime/Engine 表述只作为历史证据，不得作为当前架构依据。
- 当前架构按 Dayu 四层 `UI -> Service -> Host -> Agent` 设计；当前确定性生产主链路仍是 UI -> Service -> `fund_agent/fund` Agent 层基金能力的过渡实现。
- 未开独立 Host/Agent gate 前，不得创建占位 `fund_agent/host` 或 `fund_agent/agent` 包；确需 Host 时必须使用 `dayu.host`，确需 Agent 执行内核 / tool loop / runner / ToolRegistry / ToolTrace 时必须使用 `dayu.engine`。
- 后续 plan/review 必须显式检查四层边界、Dayu Host/Agent 依赖纪律、显式参数 / 禁止 `extra_payload`、`dayu-agent` pyproject 工程基线和当前 gate 非目标。
- 当前 phase 采用 `AGENTS.md` 的 Gate 轻重分类规则；每个 gate 进入前必须记录 `fast_path` / `standard` / `heavy` 分类、分类依据、验证矩阵和升级条件。默认 `standard`，分类不确定时选择更重一级；不得用轻量流程改变 public contract、schema、quality gate 语义、final judgment、Host/Agent/dayu、外部来源策略或 release/PR 外部状态。

| Field | State |
|---|---|
| Branch | `codex/local-reconciliation` |
| Current phase | `release maintenance` |
| Current gate | `strict golden correctness / fixture promotion gate accepted local validation` |
| Current gate classification | `heavy` |
| Next entry point | `004393 / 004194 / 006597 strict correctness follow-up gate` |
| Next gate classification | `heavy` |
| Latest accepted gate checkpoint | `Strict golden correctness / fixture promotion decision accepted: 004393 is conditional_candidate_pending_partial_coverage_decision, 004194 is conditional_candidate_pending_p0_coverage_decision, 006597 is needs_future_gate pending score rerun with golden answer, and 017641/QDII/FOF/110020 remain deferred_from_minimum_v1. All entries keep promotion_allowed=false; fixture_state remains absent/deferred_from_v1; 006597 bond blocker remains closed as resolved context only. No score/quality/FQ0-FQ6/golden fixture/manifest/runtime changes; no PR, push, merge, release or promotion changes.` |
| Design truth | `docs/design.md` (v2.2) |
| Control truth | `docs/implementation-control.md` |
| Historical control snapshots | `docs/archive/implementation-control-history-20260525.md`; `docs/archive/implementation-control-release-maintenance-ledger-20260527.md` |
| External repo state | PR 18 merged at `2026-05-25T14:44:05Z`; PR 19 merged at `2026-05-25T15:43:35Z`; `origin/main` points to `44ea955` |

## Current Gate

### Current Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Prior NAV primer / contract judgment | `docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-controller-judgment-20260528.md` |
| NAV source identity plan | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-20260528.md` |
| NAV source identity evidence | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-20260528.md` |
| NAV source identity evidence reviews | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-review-ds-20260528.md`; `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-review-glm-20260528.md` |
| NAV source identity controller judgment | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-controller-judgment-20260528.md` |
| CSRC EID / stock-sdk source evaluation plan | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-20260528.md` |
| CSRC EID / stock-sdk source evaluation evidence | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-20260528.md` |
| CSRC EID / stock-sdk source evaluation reviews | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-review-ds-20260528.md`; `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-review-glm-20260528.md` |
| CSRC EID / stock-sdk source evaluation judgment | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-controller-judgment-20260528.md` |
| CSRC EID adapter normalization plan | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-plan-20260529.md` |
| CSRC EID adapter normalization implementation evidence | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-evidence-20260529.md` |
| CSRC EID adapter normalization implementation reviews | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-review-mimo-20260529.md`; `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-implementation-review-glm-20260529.md` |
| CSRC EID adapter normalization aggregate deepreviews | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-aggregate-deepreview-mimo-20260529.md`; `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-aggregate-deepreview-glm-20260529.md` |
| CSRC EID adapter normalization controller judgment | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-controller-judgment-20260529.md` |
| Drawdown NAV-derived metric plan | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md` |
| Drawdown NAV-derived metric plan reviews | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-glm-20260529.md`; `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-mimo-20260529.md`; `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-rereview-glm-20260529.md`; `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-rereview-mimo-20260529.md` |
| Drawdown NAV-derived metric implementation evidence | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-evidence-20260529.md` |
| Drawdown NAV-derived metric implementation reviews | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-review-glm-20260529.md`; `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-review-mimo-20260529.md`; `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-rereview-glm-20260529.md`; `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-rereview-mimo-20260529.md` |
| Drawdown NAV-derived metric aggregate deepreviews | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-aggregate-deepreview-glm-20260529.md`; `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-aggregate-deepreview-mimo-20260529.md` |
| Drawdown NAV-derived metric controller judgment | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md` |
| Golden readiness preflight plan | `docs/reviews/release-maintenance-golden-readiness-preflight-plan-20260529.md` |
| Golden readiness preflight plan reviews | `docs/reviews/release-maintenance-golden-readiness-preflight-plan-review-mimo-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-preflight-plan-review-glm-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-preflight-plan-rereview-mimo-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-preflight-plan-rereview-glm-20260529.md` |
| Golden readiness preflight implementation evidence | `docs/reviews/release-maintenance-golden-readiness-preflight-implementation-evidence-20260529.md` |
| Golden readiness preflight implementation reviews | `docs/reviews/release-maintenance-golden-readiness-preflight-implementation-review-mimo-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-preflight-implementation-review-ds-20260529.md` |
| Golden readiness preflight aggregate deepreviews | `docs/reviews/release-maintenance-golden-readiness-preflight-aggregate-deepreview-mimo-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-preflight-aggregate-deepreview-ds-20260529.md` |
| Golden readiness preflight controller judgment | `docs/reviews/release-maintenance-golden-readiness-preflight-controller-judgment-20260529.md` |
| Golden readiness preflight outputs | `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`; `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.md` |
| Golden readiness residual disposition plan / reviews | `docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-review-mimo-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-review-ds-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-rereview-mimo-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-residual-disposition-plan-rereview-ds-20260529.md` |
| Golden readiness residual disposition manifest / evidence | `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`; `docs/reviews/release-maintenance-golden-readiness-residual-disposition-implementation-evidence-20260529.md` |
| Golden readiness residual disposition evidence reviews | `docs/reviews/release-maintenance-golden-readiness-residual-disposition-evidence-review-mimo-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-residual-disposition-evidence-review-ds-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-residual-disposition-evidence-rereview-mimo-20260529.md` |
| Golden readiness residual disposition aggregate deepreviews | `docs/reviews/release-maintenance-golden-readiness-residual-disposition-aggregate-deepreview-mimo-20260529.md`; `docs/reviews/release-maintenance-golden-readiness-residual-disposition-aggregate-deepreview-ds-20260529.md` |
| Golden readiness residual disposition controller judgment | `docs/reviews/release-maintenance-golden-readiness-residual-disposition-controller-judgment-20260529.md` |
| Fixture promotion state manifest plan / reviews | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md`; `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-review-mimo-20260529.md`; `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-review-ds-20260529.md`; `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-rereview-mimo-20260529.md`; `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-rereview-ds-20260529.md` |
| Fixture promotion state manifest / evidence | `docs/reviews/fixture-promotion-state-manifest-20260529.json`; `docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-evidence-20260529.md` |
| Fixture promotion state manifest implementation reviews | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-review-mimo-20260529.md`; `docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-review-ds-20260529.md` |
| Fixture promotion state manifest aggregate deepreviews | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-aggregate-deepreview-mimo-20260529.md`; `docs/reviews/release-maintenance-fixture-promotion-state-manifest-aggregate-deepreview-ds-20260529.md` |
| Fixture promotion state manifest controller judgment | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md` |
| Typed implementation plan | `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md` |
| Typed implementation evidence | `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-evidence-20260528.md` |
| Aggregate deepreview: DS | `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-aggregate-deepreview-ds-20260528.md` |
| Aggregate deepreview: GLM | `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-aggregate-deepreview-glm-20260528.md` |
| Controller judgment | `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-controller-judgment-20260528.md` |

### Current Decision Summary

- NAV primer and typed adapter contract are implemented locally through Fund data layer typed models, adapter metadata, repository normalization, tests, docs, real smoke, and aggregate review.
- `FundNavRepository.load_nav_series("006597", minimum_records=30)` real smoke succeeded with 1809 records, `share_class="A"`, `nav_type="unit_nav"`, `adjusted_basis="raw_unit_nav"`, `dividend_adjustment_status="not_adjusted"`, `identity_status="requested_code_only"`, `strong_drawdown_evidence_eligible=false`, `source="nav_cache"`, `origin_source="akshare"`.
- NAV adjusted-basis source identity evidence accepted Eastmoney / 天天基金 `累计净值走势` / `Data_ACWorthTrend` as `accumulated_nav` source/basis identity candidate for A/C/E and F source-inception-forward windows. The E-class proof is anchored by `FundDocumentRepository` annual-report distribution evidence and provider exact date `2023-01-11`, where accumulated minus unit NAV changed by `0.0080`, matching every 10 shares `0.080`.
- Accepted limitations: A/C acceptance is inferential through same-provider/same-variable E-class behavior plus independent zero-distribution evidence; identity is cross-endpoint same-provider binding (`fund_open_fund_info_em` data plus `pingzhongdata/{code}.js` identity), not same-response metadata; F is `missing_date_range` for pre-2024-10-08 windows.
- CSRC EID / stock-sdk source evaluation accepted CSRC EID as future primary `accumulated_nav` source candidate. CSRC EID public search maps `国泰利享中短债债券`, `006597`, `006598`, and `014217` to internal ID `5755`; the verified detail page exposes A/C/E/F classification NAV tables with `估值日期`, `单位净值`, `累计净值`, share-class identity and pagination. E-class CSRC rows reproduce the `2023-01-11` distribution effect: accumulated minus unit NAV changes by `0.0080`, matching annual-report §3.3.
- stock-sdk remains evidence-only: it wraps Eastmoney `pingzhongdata/{code}.js`; `getFundDividendList` cross-checks the E-class 2023 dividend, but `getFundNavHistory` has a date-normalization `integrity_error`, so it is not accepted as runtime or typed secondary source as-is.
- `累计收益率走势` / `LJSYLZS` remains `adjustment_basis_unknown` and is not accepted as total-return evidence.
- Legacy `FundNavDataAdapter.load_nav_data()` behavior remains compatible; cache hit still reports `source="nav_cache"` while typed source path can expose origin source/cache updated metadata.
- Current production typed NAV path now defaults to CSRC EID accumulated NAV through `FundNavRepository()`. Real smoke accepted A/C/E/F typed series for 006597 family: `006597=A/5755:2030-1010` and `006598=C/5755:2030-1020` from 2018-12-18 to 2026-05-28 with 1807 records each, `014217=E/5755:2030-1040` from 2022-04-25 to 2026-05-28 with 994 records, and `022176=F/5755:2030-1050` from 2024-10-08 to 2026-05-28 with 398 records.
- CSRC EID accumulated series uses `nav_type="accumulated_nav"`, `adjusted_basis="accumulated_nav"`, `dividend_adjustment_status="not_applicable"`, `identity_status="verified"`, and `strong_drawdown_evidence_eligible=true`. In the prior adapter gate this was source-level eligibility only; the current drawdown metric gate has now consumed it through the typed repository to produce reviewed max drawdown evidence.
- Legacy `FundNavDataAdapter.load_nav_data()` behavior remains compatible. Raw-unit typed compatibility remains available only through constructor-injected raw adapters and stays `raw_unit_nav`, `requested_code_only`, and `strong_drawdown_evidence_eligible=false`.
- Drawdown NAV-derived metric implementation accepted max drawdown as the minimum quantitative metric for this gate. It uses `006597 / A`, period `2024-01-01` to `2024-12-31`, and the CSRC EID typed `accumulated_nav` series only through `FundNavRepository.load_nav_series()`.
- Latest real metric for `006597 / A` is max drawdown `-0.0010059518819683125157179982` (`-0.10%`), with peak `2024-09-26 / 1.1929`, trough `2024-10-09 / 1.1917`, and `243` period records.
- `bond_risk_evidence.v1.drawdown_stress` now accepts reviewed `quantitative_derived / derived_metric` evidence. Annual-report “控制回撤” qualitative text remains weak when no accepted NAV-derived metric exists.
- Latest 006597 rerun `bond-risk-drawdown-nav-006597-2024-20260529` has snapshot `bond_risk_contract_status="satisfied"`, all seven bond risk groups satisfied, `score_applicability_issues=[]`, and no quality-gate `bond_risk_evidence_missing` issue.
- Full validation passed for the CSRC EID adapter normalization gate: `uv run ruff check .`; `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` with `925 passed`, total coverage `92.37%`. Real CSRC EID smoke passed for A/C/E/F through `FundNavRepository()` with `force_refresh=True`.
- Full validation passed for the drawdown metric implementation gate: `uv run ruff check .`; `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` with `939 passed`, total coverage `92.42%`. Real CSRC EID NAV smoke, extraction snapshot, extraction score, and quality gate reruns passed for the gate scope.
- No score policy, quality gate semantics, golden fixture, PR, push, merge, release, or promotion change occurred in this gate.
- Golden readiness preflight now produces repeatable machine-readable and Markdown readiness reports. Current output is `overall_status=block`; `006597` bond risk is not a blocker, and remaining blockers are non-bond readiness residuals.
- Golden answer corpus v1 remains blocked until QDII / FOF / `110020` / strict golden correctness / fixture-promotion blockers are resolved or explicitly deferred.
- Golden readiness residual disposition now has tracked machine-readable manifest `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`. It is control-plane disposition evidence only, not a promotion manifest and not runtime/preflight-consumed.
- Fixture promotion state manifest now has tracked machine-readable manifest `docs/reviews/fixture-promotion-state-manifest-20260529.json`. It is control-plane state evidence only, not a promotion manifest and not runtime/preflight-consumed. All entries keep `promotion_allowed=false`.
- Accepted minimum-v1 path excludes QDII / FOF / `110020` for now: those entries keep `blocks_v1=true`, `blocks_minimum_v1=false`, and `promotion_allowed=false`. They remain full-v1 blockers and are not ready.
- `004393`, `004194`, and `006597` are fixture_state `absent` in the accepted manifest. They still require strict golden correctness / quality residual handling and a separate accepted promotion gate before any fixture promotion can occur. `006597` bond blocker remains closed as resolved context only.

## Next Entry Point

`strict golden correctness / fixture promotion gate`.

This next gate must start with Startup Packet replay and `$init-agents` / tmux multi-agent flow if multi-agent panes are used. It should consume `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md`, the strict correctness decision/evidence artifacts, `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`, `docs/reviews/fixture-promotion-state-manifest-20260529.json`, and the preflight JSON/Markdown outputs. It must not enter promotion unless a separate promotion gate is explicitly authorized.

Allowed scope:

- Decide strict golden correctness / fixture readiness requirements for controller-approved candidate inputs only: `004393`, `004194`, and `006597`.
- Treat both residual disposition and fixture promotion state manifests as control-plane state only; do not modify golden answer fixtures and do not set `promotion_allowed=true` without a separate accepted promotion gate.
- Revalidate `006597` latest preflight/snapshot/score/quality artifacts before any fixture candidacy; if `bond_risk_evidence_missing` regresses, reclassify as `fix_now` or `needs_evidence_gate`.
- Preserve QDII / FOF / `110020` as deferred from minimum v1 and still blocking full v1 unless a future controller judgment changes their disposition.
- Keep strict golden correctness unresolved until an accepted strict golden / fixture gate handles it.
- Consume only `FundNavRepository.load_nav_series()` for any NAV-derived follow-up.
- Pass explicit `fund_code`, `share_class`, `start_date`, `end_date`, `minimum_records`, and other required parameters; do not use `extra_payload`.
- Reject `raw_unit_nav` and `requested_code_only` as strong drawdown evidence.
- Keep A/C/E/F NAV series separated; do not mix share classes into one product-level NAV path.
- Preserve fail-closed taxonomy for `schema_drift`, `identity_mismatch`, `integrity_error`, `adjustment_basis_unknown`, `missing_date_range`, `insufficient_records`, `not_found`, and `unavailable`.
- Keep qualitative drawdown-control text weak unless a reviewed contract explicitly changes the rule.
- Preserve evidence-strength distinctions and do not treat weak or ambiguous groups as accepted.
- Preserve existing FQ0-FQ6 semantics, renderer output, Service/CLI behavior, source strategy, and `FundDocumentRepository` boundaries.
- Do not enter QDII probing, FOF taxonomy work, release readiness, Host/Agent/dayu work, baseline/golden promotion, or GitHub mutation.
- Produce two independent reviews and controller judgment before acceptance.

## Current Non-Goals

- Do not change current v0 renderer or current 8-chapter output.
- Do not change FQ0-FQ6 quality gate behavior.
- Do not claim LLM audit / Evidence Confirm / repair loop is implemented.
- Do not create Host/Agent packages or introduce `dayu.host` / `dayu.engine` before an explicit gate.
- Do not introduce calculated index series, external index adapters beyond accepted thermometer data-source protocols, methodology extraction, constituents extraction, QDII subtype redesign, unsupported coverage targets, or quality-gate weakening.
- Do not promote local scoring, writing, or data-source run outputs into tracked fixtures without a later reviewed gate.
- Do not enter `golden answer corpus v1` until coverage, source, quality, fund-type, and fixture-promotion blockers are resolved.
- Do not push, create PR, mark ready, merge, close PRs, edit unrelated PRs, delete branches, or perform additional GitHub mutations without explicit user authorization.

## Open Residuals

| Residual | Owner / next gate | Required handling |
|---|---|---|
| QDII coverage blocked after hard stop | future QDII diagnosis or taxonomy / asset-class fitness gate | Automatic QDII probing is stopped; preserve `096001`, `040046`, `019172`, `021539` as provenance-eligible, quality `block`, `not_promoted`. No new QDII evidence before a separate accepted gate. |
| Golden answer corpus v1 blocked | future fixture promotion / strict golden correctness gates | Current preflight output is `overall_status=block`. QDII / FOF / `110020` are deferred from minimum v1 but remain full-v1 blockers. Do not promote any sample until fixture state and strict correctness blockers are handled by accepted gates. |
| `110020` reviewed coverage candidate | future golden/baseline preflight | Accepted only as reviewed coverage candidate input; remains `not_promoted`; methodology / constituents evidence remains insufficient. |
| `017641` QDII data gap | disposition / taxonomy follow-up | Original QDII row is provenance-complete but quality `block` due to `manager_strategy_text`; accepted disposition is `replace`, not promotion. |
| FOF coverage / taxonomy | future fund-type taxonomy gate | Find pure `fof_fund` repository-verified candidate, or open taxonomy gate before counting QDII-FOF attempts as FOF coverage. |
| `006597` bond risk evidence blocker | closed by drawdown metric gate | `credit_risk`, `redemption_share_pressure`, and `drawdown_stress` are repaired and validated locally. Latest `006597` snapshot has all seven bond risk groups satisfied; score has `score_applicability_issues=[]`; quality gate has no `bond_risk_evidence_missing`. Keep this closed status unless a later regression appears. |
| `006597` remaining quality warnings | future readiness / residual reconciliation gate | Latest quality gate remains `warn` for unrelated `turnover_rate`, `holder_structure`, `share_change`, fund-level P1 failures, FQ0 golden not configured, and FQ4 missing field rate. Do not treat these as bond-risk evidence residuals without a separate gate. |
| Strict correctness / fixture promotion preconditions accepted but not promotion | 004393 / 004194 / 006597 strict correctness follow-up gate | `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` records current decisions: `004393` is conditional pending partial coverage decision; `004194` is conditional pending P0 strict correctness coverage decision; `006597` needs score rerun with `reports/golden-answers/golden-answer.json`. All entries keep `promotion_allowed=false`; fixture states remain unchanged; no golden fixture promotion is authorized. |
| Tracked residual disposition manifest not runtime-consumed | future manifest runtime consumption gate, only if needed | `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` is accepted control-plane evidence, but preflight still has static in-code disposition. Runtime/preflight consumption requires a separate implementation gate with full ruff, full pytest, and preflight rerun. |
| Snapshot multi-anchor projection | future snapshot evidence display hardening gate | Current snapshot field-level projection exposes one traceable anchor. Derived provenance is present in extractor evidence; if consumers need simultaneous annual-report and derived anchors in snapshot rows, open a narrow projection gate. |
| CSRC EID NAV provenance cleanup | future NAV provenance hardening gate | `source_query_params` currently mixes HTTP query params and request context such as `force_refresh`; accepted as low risk. Consider splitting HTTP params from request context if a consumer needs replayable provenance. |
| CSRC EID source generalization | future NAV source generalization gate | Current adapter is scoped to verified 006597 family constants and a hardcoded F direct-search gap. Extend only with reviewed identity evidence for additional fund families or share-class search gaps. |
| CSRC EID parser/source resilience | future schema-drift / caching strategy gate | Detail-page text parsing and public endpoint availability are accepted low residuals. Existing behavior fail-closes on schema/identity/integrity issues; caching strategy should wait for accepted metric consumer requirements. |
| Source metadata strict bool parsing | future source provenance hardening gate | Plan/review strict bool parser for `AnnualReportSourceMetadata.from_dict()`; current known issue: string `"false"` coerces truthy. |
| Stray untracked `--help` file | artifact disposition / user-authorized cleanup | Do not stage or promote; delete only with explicit authorization or accepted disposition. |
| Untracked review/evidence artifacts | artifact disposition gate if needed | Decide whether to accept, archive, or leave untracked; do not silently stage unrelated artifacts. |

## Recent Active Gate Ledger

| Gate | Status | Artifact | Validation / judgment | Next action |
|---|---|---|---|---|
| `source provenance post-implementation bounded evidence rerun` | accepted locally | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md` | `110020` and `017641` exposed complete eligible fallback provenance; no promotion | post-provenance coverage recovery decision |
| `docs-only truth reconciliation` | accepted locally | `docs/reviews/release-maintenance-docs-truth-reconciliation-20260527.md` | Repo review F1/F2 closed in `docs/design.md`; F3 deferred; ruff / pytest / diff check passed | coverage recovery decision |
| `post-provenance coverage recovery decision plan` | accepted locally | `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-controller-judgment-20260527.md` | Roadmap gates 1-4 skipped as accepted; golden corpus v1 blocked | `110020` candidate decision |
| `110020 reviewed coverage candidate evidence` | accepted locally | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md` | Public evidence accepted terminal `reviewed_coverage_candidate_input_accepted`; no promotion | `017641` triage |
| `017641 manager_strategy_text public evidence triage` | accepted locally | `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md` | Terminal `disclosure_data_gap_not_baseline_ready`; no promotion | baseline disposition |
| `baseline coverage disposition decision plan` | accepted locally | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-controller-judgment-20260527.md` | Accepted disposition matrix requirements; no code/evidence/product-flow changes | replacement / exclusion selection |
| `replacement/exclusion candidate selection` | accepted locally | `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` | Accepted `017641=replace`, `FOF=needs_taxonomy_gate`, `006597=needs_evidence_gate`; no promotion | QDII replacement plan |
| `QDII replacement evidence sequence` | accepted locally | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-controller-judgment-20260527.md` | `096001`, `040046`, `019172`, `021539` all provenance-eligible but quality `block`; `021539` triggers hard stop | QDII post-021539 disposition decision |
| `release-maintenance consolidation / QDII post-021539 disposition` | accepted locally | `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md` | Control-doc compression accepted; QDII automatic probing stopped; QDII coverage blocked; golden corpus v1 remains blocked; DS/MiMo reviews `PASS_WITH_FINDINGS`; no code/product changes | bond positive-risk evidence |
| `bond positive-risk evidence` | accepted locally | `docs/reviews/release-maintenance-bond-positive-risk-evidence-controller-judgment-20260527.md` | Truth preflight fixed Gate classification rules in `AGENTS.md`; 006597 evidence run found candidate annual-report evidence for all seven bond-risk groups, but current CLI/score cannot express positive records; DS/MiMo reviews `PASS_WITH_FINDINGS`; no code/product changes | bond risk evidence extractor / anchor hardening design |
| `bond risk evidence extractor / anchor hardening` | blocked with reason | `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice6-controller-judgment-20260528.md` | Slice 1-5 accepted locally and emit structured `bond_risk_evidence.v1`; Slice 6 real validation still has `bond_risk_evidence_missing.baseline_blocking=true` for `credit_risk`, `drawdown_stress`, `redemption_share_pressure`; DS/GLM agree only two groups are extractor misses and drawdown remains weak | drawdown evidence contract / NAV-derived risk metric design gate, or authorized extractor-hardening amendment |
| `section2 crosscheck unit suffix repair` | accepted locally | `docs/reviews/release-maintenance-section2-crosscheck-unit-suffix-repair-controller-judgment-20260528.md`; `docs/reviews/code-review-20260528-081225.md` | Added whitelist terminal `份` parsing for §2 ending-share cells; `006597` real snapshot now satisfies `redemption_share_pressure`; score missing groups now only `drawdown_stress`; full ruff / full pytest / real PDF smoke / snapshot / score / quality gate passed | drawdown evidence contract / NAV-derived risk metric design gate |
| `drawdown_stress NAV-derived evidence contract` | blocked with decision | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-controller-judgment-20260528.md`; plan reviews `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-mimo-20260528.md`, `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-ds-20260528.md` | NAV-derived drawdown accepted only as future candidate. Current NAV provider/cache cannot prove total-return / adjusted basis; `bond_risk_evidence.v1` derived anchors and snapshot/score per-group provenance are unresolved. No implementation, no blocker解除. | NAV source capability / adjusted basis evidence gate |
| `NAV source capability / adjusted basis evidence` | blocked pending source adapter | `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-controller-judgment-20260528.md`; DS/GLM review and re-review artifacts | Public `FundNavDataAdapter` smoke for `006597` succeeds but exposes only raw `净值日期` / `单位净值` / `日增长率`; direct SQLite inspection is diagnostic-only; current capability cannot prove adjusted / cumulative / total-return basis or dividend adjustment status. No production code, score, quality gate, schema, golden, PR, push, or promotion changes. | NAV repository/source adapter adjusted-basis contract gate |
| `NAV repository/source adapter adjusted-basis contract` | accepted blocked-with-contract-gap | `docs/reviews/release-maintenance-nav-source-adapter-adjusted-basis-contract-controller-judgment-20260528.md`; primer / plan / evidence artifacts and DS/GLM reviews | Accepted fund NAV / share-class / adjusted-basis primer and typed adapter contract. Independent reviews confirmed 006597 2025 E-class year-end NAV is `1.1967` via `FundDocumentRepository`, and current `FundNavDataAdapter` remains raw-unit-only without share_class / adjusted_basis / provenance / identity / failure taxonomy. No production code, score, quality gate, schema, golden, PR, push, or promotion changes. | NAV repository/source adapter typed contract implementation gate |
| `NAV repository/source adapter typed contract implementation` | accepted local validation | `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-controller-judgment-20260528.md`; implementation evidence and aggregate deepreviews | Implemented typed NAV models, adapter metadata, repository normalization, docs, tests, and real 006597 smoke. Full ruff and full pytest passed. Current 006597 NAV remains raw-unit-only/requested-code-only/not strong eligible; `drawdown_stress` blocker remains. No score, snapshot, quality gate, golden, PR, push, release, or promotion changes. | drawdown_stress NAV-derived metric implementation gate or NAV adjusted-basis source identity gate |
| `NAV adjusted-basis source identity` | accepted local evidence with partial acceptance | `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-controller-judgment-20260528.md`; plan/evidence and DS/GLM review artifacts | Accepted Eastmoney / 天天基金 `Data_ACWorthTrend` / `累计净值走势` as future `accumulated_nav` source/basis identity candidate for A/C/E and F source-inception-forward windows; `LJSYLZS` remains `adjustment_basis_unknown`; raw unit NAV remains not strong evidence; no code/test/runtime/score/snapshot/quality/golden changes. | NAV accumulated-nav source adapter normalization implementation gate |
| `CSRC EID and stock-sdk accumulated NAV source evaluation` | accepted local evidence | `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-controller-judgment-20260528.md`; plan/evidence and DS/GLM review artifacts | Accepted CSRC EID as future primary `accumulated_nav` source candidate: public search verifies internal ID `5755`, classification pages separate A/C/E/F, and E-class distribution cross-check matches annual report §3.3. stock-sdk remains evidence-only because it wraps Eastmoney and `getFundNavHistory` has date `integrity_error`. No code/test/dependency/runtime/score/snapshot/quality/golden changes. | CSRC EID accumulated NAV adapter normalization implementation gate |
| `CSRC EID accumulated NAV adapter normalization implementation` | accepted local validation | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-controller-judgment-20260529.md`; implementation evidence and MiMo/GLM aggregate deepreviews | Implemented CSRC EID accumulated NAV source adapter through `FundNavRepository()` typed boundary. A/C/E/F real smoke passed; full ruff and full pytest passed. `strong_drawdown_evidence_eligible=true` is source-level only; no drawdown metric, score, snapshot, quality gate, golden, PR, push, release or promotion changes. | drawdown_stress NAV-derived metric contract / implementation gate |
| `drawdown_stress NAV-derived metric implementation` | accepted local validation | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md`; implementation evidence and MiMo/GLM aggregate deepreviews | Implemented reviewed max drawdown evidence for `006597/A` 2024 through `FundNavRepository()` and CSRC EID accumulated NAV. Latest snapshot satisfies all seven bond risk groups, score has no `bond_risk_evidence_missing`, quality gate has no bond-risk blocker. Full ruff and full pytest passed. No golden, PR, push, release or promotion changes. | bond risk evidence local readiness reconciliation gate |
| `golden-readiness preflight` | accepted local validation | `docs/reviews/release-maintenance-golden-readiness-preflight-controller-judgment-20260529.md`; implementation evidence and MiMo/DS aggregate deepreviews | Implemented read-only golden readiness preflight JSON/Markdown. Current output is `overall_status=block`; 006597 bond blocker is resolved item only; QDII/FOF/110020/strict-golden/fixture blockers have owner/next_gate/evidence. Full ruff and full pytest passed. No golden, PR, push, release or promotion changes. | golden readiness residual disposition gate |
| `golden readiness residual disposition` | accepted local validation | `docs/reviews/release-maintenance-golden-readiness-residual-disposition-controller-judgment-20260529.md`; `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`; MiMo/DS aggregate deepreviews | Accepted tracked residual disposition matrix. All current blockers have decision / owner / next_gate; QDII/FOF/110020 are deferred from minimum v1 but not ready; 006597 bond blocker remains closed; manifest is not a promotion manifest and not runtime-consumed. No code/runtime/score/quality/FQ/golden fixture changes. | fixture promotion state manifest gate |
| `fixture promotion state manifest` | accepted local validation | `docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md`; `docs/reviews/fixture-promotion-state-manifest-20260529.json`; MiMo/DS aggregate deepreviews | Accepted tracked fixture promotion state manifest. It records 2 global blockers and 10 fund/slot entries with all `promotion_allowed=false`; 004393/004194/006597 are `absent`; QDII/FOF/110020 and 017641 are `deferred_from_v1`; 006597 bond blocker remains closed as resolved context only. No code/runtime/score/quality/FQ/golden fixture changes. | strict golden correctness / fixture promotion gate |
| `strict golden correctness / fixture promotion` | accepted local validation | `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md`; decision/evidence artifacts; DS/GLM aggregate deepreviews | Accepted docs-only decision matrix. `004393` is conditional pending partial coverage; `004194` is conditional pending P0 strict correctness coverage; `006597` requires score rerun with golden answer; 017641/QDII/FOF/110020 remain deferred. All `promotion_allowed=false`; fixture states unchanged; no code/runtime/score/quality/FQ/golden fixture/manifest changes. | 004393 / 004194 / 006597 strict correctness follow-up gate |

## Historical Evidence Index

Detailed control history is preserved in archive files:

- `docs/archive/implementation-control-history-20260525.md`
- `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`

Use archive files only for evidence reconstruction. They are not current gate truth and must not override this Startup Packet or `docs/design.md` current design sections.

Archived material includes:

- P0-P19 phase definitions, detailed gate logs, PR/commit records, validation counts, and residual histories.
- Superseded six-layer / Application / Runtime/Engine wording.
- Long-form release-maintenance PR 16 / PR 17 / 004393 quality gate / P19 thermometer records.
- Detailed release-maintenance accepted artifacts, Current Decisions, Open Residuals, and Active Gate Ledger through QDII replacement fallback 021539 evidence.

## Design / Control Alignment Rules

1. `AGENTS.md` is the highest-priority execution rule source.
2. `docs/design.md` remains the design truth for architecture, boundaries, current product behavior, Dayu non-dependency, `FundDocumentRepository` source boundaries, report-quality design, and thermometer design.
3. `docs/implementation-control.md` remains the control truth for current phase, current gate, accepted artifacts, residual owners, and next entry point.
4. Historical archive entries are evidence only. If archive content contradicts Startup Packet or `docs/design.md`, treat the archive content as superseded unless a new controller judgment says otherwise.
5. Future control-doc updates should prefer a new `docs/reviews/` artifact plus a short control-doc reference over appending long logs.

## Resume Checklist

When resuming:

1. Read `AGENTS.md`.
2. Read `docs/design.md` current relevant sections.
3. Read this Startup Packet.
4. Confirm `Current phase`, `Current gate`, and `Next entry point`.
5. Confirm the next action is controller work or specialist work.
6. Classify the next gate as `fast_path`, `standard`, or `heavy` per `AGENTS.md`.
7. If specialist work is required, delegate through the current gate handoff; do not write the specialist plan directly unless explicitly authorized.
8. Preserve deterministic MVP boundaries and do not introduce Host/Agent/runtime work outside an explicit gate.
