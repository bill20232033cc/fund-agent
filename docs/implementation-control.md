# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.1
> **日期**: 2026-05-27
> **设计真源**: `docs/design.md` (v2.2)
> **规则真源**: `AGENTS.md`
> **历史快照**: `docs/archive/implementation-control-history-20260525.md`
> **release-maintenance 长账本**: `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`
> **当前状态**: release maintenance；CSRC EID and stock-sdk accumulated NAV source evaluation gate 已 accepted local evidence；006597/2024 的 `credit_risk` 与 `redemption_share_pressure` false negative 已解除；typed NAV runtime path 仍只实现 raw-unit-only series，但 source evidence 已接受 CSRC EID 作为 future primary `accumulated_nav` adapter candidate，stock-sdk 仅 evidence-only；bond blocker 仍因 `drawdown_stress` 缺 adapter normalization 与 reviewed metric implementation 保留；下一入口为 CSRC EID accumulated NAV adapter normalization implementation gate

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
| Current gate | `CSRC EID and stock-sdk accumulated NAV source evaluation gate accepted local evidence` |
| Current gate classification | `heavy` |
| Next entry point | `CSRC EID accumulated NAV adapter normalization implementation gate` |
| Next gate classification | `heavy` |
| Latest accepted gate checkpoint | `CSRC EID source evaluation accepted: eid.csrc.gov.cn internal ID 5755 maps to 国泰利享中短债债券 A/C/E through public search and exposes A/C/E/F share-class classification NAV tables; CSRC EID is accepted as future primary accumulated_nav source candidate; stock-sdk is evidence-only due Eastmoney lineage and date integrity_error; raw_unit_nav remains not strong evidence; drawdown_stress blocker remains.` |
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
- Current production typed NAV path is still raw-unit-only and requested-code-only; accepted CSRC EID / Eastmoney `accumulated_nav` source identities exist only as evidence for the next adapter normalization gate and are not yet implemented in runtime.
- `drawdown_stress` remains weak qualitative. Latest 006597 score remains `bond_risk_evidence_missing.baseline_blocking=true`, with `missing_evidence_groups` only `drawdown_stress`.
- Full validation passed: `uv run ruff check .`; `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` with `893 passed`, total coverage `92.40%`.
- No score, snapshot, quality gate, golden fixture, PR, push, merge, release, or promotion change occurred in this gate.
- Golden answer corpus v1 remains blocked until coverage, source, quality, fund-type, and fixture-promotion blockers are resolved or explicitly deferred.

## Next Entry Point

`CSRC EID accumulated NAV adapter normalization implementation gate`.

This next gate must start with Startup Packet replay and `$init-agents` / tmux multi-agent flow if multi-agent panes are used. `credit_risk` and `redemption_share_pressure` false negatives are locally repaired and validated for `006597` / 2024. Real validation still keeps `bond_risk_evidence_missing.baseline_blocking=true` because `drawdown_stress` remains weak qualitative evidence under the current score contract. The typed NAV implementation gate proved the current repository boundary is reachable for 006597, but the runtime series remains `raw_unit_nav`, `not_adjusted`, `requested_code_only`, and `strong_drawdown_evidence_eligible=False`. CSRC EID is now accepted as future primary `accumulated_nav` source candidate, so the next implementation gate should normalize CSRC EID through the Fund data boundary before any drawdown metric gate.

Allowed scope:

- Consume only `FundNavRepository.load_nav_series()` for NAV-derived drawdown work.
- Pass explicit `fund_code`, `share_class`, `start_date`, `end_date`, `minimum_records`, and other required parameters; do not use `extra_payload`.
- Reject `raw_unit_nav` and `requested_code_only` as strong drawdown evidence.
- Normalize CSRC EID `accumulated_nav` source identity into the typed NAV boundary before any quantitative `drawdown_stress` work.
- Bind CSRC EID public search / internal ID `5755` / A-C-E-F classification links and fail closed on search, identity, pagination, blank accumulated NAV, schema drift, duplicate date, bad decimal, or missing-date-window issues.
- Require an additional reviewed metric contract before using `accumulated_nav`, adjusted, dividend-adjusted, or total-return basis to produce quantitative `drawdown_stress`.
- Keep A/C/E/F NAV series separated; do not mix share classes into one product-level NAV path.
- Preserve fail-closed taxonomy for `schema_drift`, `identity_mismatch`, `integrity_error`, `adjustment_basis_unknown`, `missing_date_range`, `insufficient_records`, `not_found`, and `unavailable`.
- Do not change `bond_risk_evidence` satisfaction, score acceptance, snapshot schema, quality gate semantics, or baseline status in the adapter normalization implementation gate.
- Keep qualitative drawdown-control text weak unless a reviewed contract explicitly changes the rule.
- Preserve evidence-strength distinctions and do not treat weak or ambiguous groups as accepted.
- Preserve existing FQ0-FQ6 semantics, renderer output, Service/CLI behavior, source strategy, and `FundDocumentRepository` boundaries.
- Do not enter QDII probing, FOF taxonomy work, golden corpus preflight, release readiness, Host/Agent/dayu work, baseline/golden promotion, or GitHub mutation.
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
| Golden answer corpus v1 blocked | future golden preflight after coverage disposition | Do not promote any sample until coverage, source, quality, fund-type, and fixture-promotion blockers are resolved. |
| `110020` reviewed coverage candidate | future golden/baseline preflight | Accepted only as reviewed coverage candidate input; remains `not_promoted`; methodology / constituents evidence remains insufficient. |
| `017641` QDII data gap | disposition / taxonomy follow-up | Original QDII row is provenance-complete but quality `block` due to `manager_strategy_text`; accepted disposition is `replace`, not promotion. |
| FOF coverage / taxonomy | future fund-type taxonomy gate | Find pure `fof_fund` repository-verified candidate, or open taxonomy gate before counting QDII-FOF attempts as FOF coverage. |
| `006597` bond risk evidence blocker | future `CSRC EID accumulated NAV adapter normalization implementation gate`, then separate drawdown metric contract / implementation gate | `credit_risk` and `redemption_share_pressure` false negatives are repaired and validated locally. Runtime typed NAV path remains `raw_unit_nav`, `not_adjusted`, `requested_code_only`, and `strong_drawdown_evidence_eligible=false`. Source evidence accepted CSRC EID as future primary `accumulated_nav` candidate for A/C/E/F share-class NAV tables, with A/C blank-row, F search-index, HTML schema and pagination caveats recorded; stock-sdk is evidence-only due date `integrity_error`. Latest `006597` score still has `bond_risk_evidence_missing.baseline_blocking=true`, with `missing_evidence_groups` only `drawdown_stress`. Do not claim blocker解除 without adapter normalization and a reviewed drawdown metric implementation. |
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
