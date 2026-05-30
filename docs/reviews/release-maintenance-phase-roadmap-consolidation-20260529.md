# Release Maintenance Phase Roadmap Consolidation

日期：2026-05-29

角色：AgentCodex implementation worker。本文是 docs/control-plane-only roadmap artifact；不是 controller judgment，不是 promotion manifest，不授权 release、golden promotion、fixture promotion、runtime manifest consumption 或 Host/Agent/dayu implementation。

## Scope And Guardrails

本 gate 消费已接受计划 `docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-20260529.md`，计划接受提交为 `807f5f2`。两份 plan review 均为 PASS：`docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-review-mimo-20260529.md` 和 `docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-review-ds-20260529.md`。

硬边界：

- 只写 roadmap/control-plane 文档；不修改生产代码、测试、runtime、score、quality gate、snapshot、renderer、Service/UI、Host/Agent/dayu、golden answers、golden fixtures、JSON manifests 或 reports。
- 不设置 `promotion_allowed=true`，不执行 PR、push、merge、release 或 promotion。
- `AGENTS.md` 与 `docs/design.md` 仍是执行与设计真源：目标架构为 `UI -> Service -> Host -> Agent`，当前确定性路径仍是 UI -> Service -> `fund_agent/fund`；未来 Host 必须使用 `dayu.host`，未来 Agent engine/tool loop 必须使用 `dayu.engine`。
- 年报访问边界仍是 `FundDocumentRepository`；fallback 仍按 `not_found`、`unavailable` 可 fallback，`schema_drift`、`identity_mismatch`、`integrity_error` fail-closed。
- 任何业务参数、基金代码、年份、来源、缓存、质量策略、scene/tool 参数都必须显式声明，禁止塞入 `extra_payload`。

## Evidence Freeze

Accepted truth sources used for this roadmap:

| Area | Evidence |
|---|---|
| Execution/design guardrails | `AGENTS.md`; `docs/design.md`; `docs/implementation-control.md` |
| Preflight state | `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`; `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.md` |
| Control-plane manifests | `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`; `docs/reviews/fixture-promotion-state-manifest-20260529.json` |
| Strict correctness fixture decision | `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md` |
| 006597 bond blocker closure | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md` |
| NAV/source provenance | `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-controller-judgment-20260528.md`; `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-controller-judgment-20260528.md`; `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-controller-judgment-20260528.md`; `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-controller-judgment-20260529.md` |
| Deferred coverage | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md` |

Workspace note: the workspace already contains untracked strict correctness follow-up evidence artifacts showing that a `006597` rerun triggered the same-fund unavailable field review stop condition. Those artifacts are unaccepted/untracked workspace evidence, not controller truth, and must not be staged or promoted unless a controller later accepts them.

## Solved Blockers

| Blocker | Current state | Evidence |
|---|---|---|
| `006597` `bond_risk_evidence_missing` / `drawdown_stress` | Closed as resolved context. Latest accepted drawdown metric gate produced reviewed NAV-derived max drawdown evidence and latest 006597 snapshot/score/quality no longer has bond-risk blocker. | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md`; preflight resolved item |
| CSRC EID accumulated NAV source for 006597 family | Accepted runtime typed source through `FundNavRepository()` for A/C/E/F 006597 family, with share classes separated and `accumulated_nav / verified` semantics. | `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-controller-judgment-20260529.md` |
| Control-plane residual and fixture state manifests | Tracked as control-plane evidence only. They preserve `promotion_allowed=false` and are not runtime/preflight-consumed. | `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`; `docs/reviews/fixture-promotion-state-manifest-20260529.json` |

## Remaining Minimum V1 Blockers

Minimum golden v1 remains blocked. The current actionable minimum-v1 blockers are:

- `004393 / 2024`: partial strict correctness coverage decision or expansion is required before fixture promotion-prep. Accepted state is conditional candidate pending partial coverage decision.
- `004194 / 2024`: P0 coverage or explicit `index_profile`-only fixture decision is required. Accepted state is conditional candidate pending P0 strict correctness coverage decision.
- `006597 / 2024`: bond blocker is closed, but strict correctness and fixture candidacy are unresolved. If the untracked follow-up evidence is accepted by a controller, next gate is a same-fund unavailable field review. If not accepted, rerun strict correctness with `reports/golden-answers/golden-answer.json`, then apply the same stop condition if unavailable same-fund fields appear.
- Global fixture promotion-prep: all current entries keep `promotion_allowed=false`; no fixture promotion or minimum v1 promotion is authorized.

Minimum v1 promotion can start only after an explicit promotion gate authorization. This roadmap does not authorize it.

## Five Routes

### Route 1: Minimum Golden V1 Readiness

Purpose: move only the minimum explicitly authorized set toward a later promotion-prep decision without promoting anything.

Recommended route order:

1. `004393 partial coverage decision / expansion gate`: decide whether P0 `9/11` and P1 `0/10` partial coverage may enter future fixture promotion-prep, or require more extraction/strict golden coverage.
2. `004194 P0 coverage or index_profile-only fixture decision gate`: decide whether an `index_profile.*`-only fixture is acceptable or whether P0 strict correctness coverage must be expanded first.
3. `006597 strict correctness route`: if controller accepts the untracked follow-up evidence, run a same-fund unavailable field review gate; if not, rerun strict correctness with `reports/golden-answers/golden-answer.json` before the manual field review decision.
4. `fixture promotion-prep gate`: only after the three fund-level decisions above are accepted.
5. `minimum v1 promotion gate`: only after explicit authorization; not part of this gate.

### Route 2: Deferred Coverage

Purpose: keep non-minimum-v1 blockers visible without allowing them to block the minimum path indefinitely.

- QDII candidates `096001`, `040046`, `019172`, `021539`: deferred from minimum v1; automatic QDII probing remains stopped; still block full v1.
- `017641 / 2024`: replacement disposition preserved; source provenance complete but quality block / manager strategy data gap remains; deferred from minimum v1; still blocks full v1.
- `FOF_SLOT`: no repository-verified pure FOF candidate; QDII-FOF does not count as pure FOF; deferred from minimum v1; still blocks full v1.
- `110020 / 2024`: accepted only as reviewed coverage candidate input; methodology / constituents / reviewed fact-freeze evidence remains insufficient; deferred from minimum v1; still blocks full v1.

These rows require manual coverage policy or fact-freeze gates before implementation work. None is ready.

### Route 3: Source / Provenance Hardening

Purpose: collect source reliability and provenance residuals without making them minimum-v1 blockers unless a controller elevates them.

Accepted current source boundary:

- CSRC EID runtime typed source is accepted for 006597-family accumulated NAV through `FundNavRepository()`.
- `raw_unit_nav` remains ineligible for strong drawdown evidence.
- stock-sdk remains evidence-only because of date identity/integrity issues.
- CSRC/Eastmoney/stock-sdk details do not bypass Fund data boundaries, explicit parameters, or fail-closed taxonomy.

Future hardening candidates:

- Split `source_query_params` into HTTP query params and request context.
- Generalize CSRC EID source beyond verified 006597 family and hardcoded F direct-search gap only after reviewed identity evidence.
- Harden parser/schema drift and duplicate-date early detection.
- Define endpoint caching/SLA strategy after accepted metric consumer requirements.
- Add strict bool parsing for source metadata.
- Add multi-anchor snapshot projection if consumers need simultaneous annual-report and derived anchors.

Every Route 3 residual is recorded in the residual table with explicit `blocks_minimum_v1` and `blocks_full_v1`.

### Route 4: Future Host / Agent / Dayu Architecture

Purpose: preserve architecture residuals without implementing them.

- Current production path remains deterministic UI -> Service -> `fund_agent/fund`. Do not create Host/Agent packages in this gate.
- Future Host gate must use `dayu.host` for session/run lifecycle, concurrency, timeout, cancel, resume, memory, reply outbox and events.
- Future Agent execution gate must use `dayu.engine` for runner, tool loop, ToolRegistry, ToolTrace, context budget and tool execution.
- No `extra_payload` parameter hiding. All scene/tool/fund/year/source/cache/quality parameters must be explicit.

Future fund reasoning design residual: `facet inference / ITEM_RULE routing design gate`.

- Current boundary: `fund_type` is the coarse standard type used by preferred_lens and ITEM_RULE; facets are narrower evidence-based traits and must not be inferred by LLM guessing.
- Candidate facets include bond traits such as short-duration, credit-rating, leverage/liquidity, redemption pressure, multi-share-class, NAV-derived drawdown availability and convertible-bond exposure; index traits such as ETF-linked, tracking-error direct disclosure and `index_profile` benchmark-only; QDII traits such as QDII-FOF, overseas index, overseas bond, FX and geography; FOF traits such as pure FOF, QDII-FOF and holding look-through availability.
- Inference must be deterministic and evidence-based, consuming structured annual-report/source facts and exposing missing/ambiguous states.
- Routing may affect `ITEM_RULE`, `must_answer`, `must_not_cover`, `preferred_lens`, evidence requirements and deletion/render decisions.
- Ownership belongs to Agent/Fund, because `fund_agent/fund` owns fund type, CHAPTER_CONTRACT, ITEM_RULE, preferred_lens and evidence audit. Service may choose scenes/contracts, but fund facet inference belongs in Fund.
- This can be designed before Host/Agent/dayu integration and later consumed by a dayu agent first-step facet flow.
- No facet inference implementation is authorized in this gate.

### Route 5: Artifact / Manifest Lifecycle

Purpose: prevent control-plane artifacts from being confused with runtime truth or promotion manifests.

- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` is tracked control-plane evidence only, not a promotion manifest and not runtime/preflight-consumed.
- `docs/reviews/fixture-promotion-state-manifest-20260529.json` is tracked control-plane state evidence only, not a promotion manifest and not runtime/preflight-consumed; all entries keep `promotion_allowed=false`.
- Future runtime/preflight manifest consumption requires a separate implementation gate, schema/lifecycle rules, full validation and preflight rerun.
- Future control-doc updates should compress pointers and route summaries, not append long ledgers.
- Untracked artifacts and stray `--help` remain read-only unless a separate artifact disposition gate or explicit user authorization says otherwise.

## Work Type Split

| Work type | Items |
|---|---|
| Code implementation work | Future manifest runtime/preflight consumption; source/provenance hardening; possible extractor/strict golden coverage expansion; Host/Agent/dayu integration; facet inference after design acceptance. None is authorized here. |
| Manual fact-freeze / policy decision | `004393` partial coverage decision; `004194` P0 vs index_profile-only decision; `006597` same-fund unavailable field review or rerun acceptance; QDII/FOF/017641/110020 coverage policy and fact-freeze gates. |
| Manifest/control-plane work | Maintain roadmap pointer, residual summaries, accepted artifact index, artifact disposition, and future promotion-prep state. This gate only performs docs/control-plane updates. |

## Residual Table

| route | item | current_state | owner | next_gate | blocks_minimum_v1 | blocks_full_v1 | evidence |
|---|---|---|---|---|---|---|---|
| Route 1 | `004393 / 2024` | Conditional candidate pending partial coverage decision; fixture absent; promotion not allowed. | future baseline / strict golden owner | partial coverage decision or expansion gate | true | true | strict correctness fixture judgment; fixture manifest |
| Route 1 | `004194 / 2024` | Conditional candidate pending P0 coverage / `index_profile`-only decision; fixture absent; promotion not allowed. | future baseline / strict golden owner | P0 coverage or `index_profile`-only fixture decision gate | true | true | strict correctness fixture judgment; fixture manifest |
| Route 1 | `006597 / 2024` | Bond blocker closed; strict correctness / fixture absent unresolved. Untracked follow-up evidence says rerun hit same-fund unavailable stop condition but remains unaccepted. | future baseline / strict golden owner | same-fund unavailable field review if accepted, otherwise rerun strict correctness then review | true | true | drawdown judgment; strict fixture judgment; untracked follow-up evidence as workspace state only |
| Route 1 | Global fixture promotion | No promotion-prep accepted; all `promotion_allowed=false`. | future fixture promotion gate | fixture promotion-prep after fund decisions | true | true | fixture manifest |
| Route 2 | QDII candidates `096001`, `040046`, `019172`, `021539` | Deferred from minimum v1; quality block; automatic probing stopped. | future QDII diagnosis / policy gate | QDII diagnosis or explicit deferred-from-v1 disposition | false | true | post-021539 judgment; residual and fixture manifests |
| Route 2 | `017641 / 2024` | Replacement disposition preserved; disclosure/manager strategy data gap; quality block. | future QDII diagnosis / replacement owner | QDII diagnosis or explicit deferred-from-v1 gate | false | true | 017641 triage; replacement judgment; manifests |
| Route 2 | `FOF_SLOT` | Pure FOF taxonomy/data gap; QDII-FOF cannot count as pure FOF. | future FOF taxonomy owner | pure FOF repository-verified candidate gate | false | true | replacement judgment; post-021539 judgment; manifests |
| Route 2 | `110020 / 2024` | Reviewed candidate only; methodology / constituents / reviewed fact-freeze insufficient. | future index evidence sufficiency owner | index reviewed fact-freeze / methodology / constituents evidence gate | false | true | 110020 judgment; source provenance rerun judgment; manifests |
| Route 3 | `source_query_params` split | Low-risk provenance cleanup; current tuple mixes HTTP params and request context. | future NAV provenance hardening owner | source provenance cleanup gate | false | false | CSRC EID adapter normalization judgment |
| Route 3 | CSRC EID source generalization | Current adapter scoped to verified 006597 family and F direct-search gap. | future NAV source generalization owner | reviewed identity evidence and source generalization gate | false | true | CSRC EID adapter normalization judgment |
| Route 3 | Parser/schema drift and duplicate-date detection | Current behavior fail-closes; earlier duplicate detection can be hardened. | future schema / model invariant hardening owner | parser/schema drift hardening gate | false | true | CSRC EID adapter normalization judgment; AGENTS fallback taxonomy |
| Route 3 | Endpoint caching/SLA | CSRC EID availability is external; cache strategy not yet accepted. | future source resilience owner | NAV caching / source resilience gate | false | true | CSRC EID adapter normalization judgment; drawdown judgment residuals |
| Route 3 | Strict bool parsing for source metadata | Known source metadata parsing cleanup; not tied to current minimum v1 promotion. | future source provenance hardening owner | strict bool parsing gate | false | false | implementation-control residual |
| Route 3 | Multi-anchor snapshot projection | Current snapshot exposes one traceable anchor; multi-anchor projection may be needed for display fidelity. | future snapshot evidence display owner | multi-anchor projection gate | false | false | drawdown judgment residuals |
| Route 4 | Host layer | Future architecture only; current path has no Host package. | future architecture owner | Host design/implementation gate using `dayu.host` | false | true | AGENTS; design.md |
| Route 4 | Agent engine/tool loop | Future architecture only; current Fund package remains Agent-layer domain capability. | future architecture owner | Agent design/implementation gate using `dayu.engine` | false | true | AGENTS; design.md |
| Route 4 | Facet inference / ITEM_RULE routing | Future fund reasoning design residual; no implementation. | Agent/Fund design owner | facet inference / ITEM_RULE routing design gate | false | true | AGENTS; design.md CHAPTER_CONTRACT / ITEM_RULE / preferred_lens |
| Route 5 | Residual disposition manifest lifecycle | Tracked control-plane evidence only; not promotion/runtime/preflight-consumed. | future manifest lifecycle owner | manifest runtime consumption gate only if authorized | false | true | residual disposition manifest |
| Route 5 | Fixture promotion state manifest lifecycle | Tracked control-plane state only; all `promotion_allowed=false`; not runtime/preflight-consumed. | future fixture / manifest owner | fixture promotion-prep then promotion gate only if authorized | true | true | fixture promotion state manifest |
| Route 5 | Untracked artifacts / stray `--help` | Leave untracked; do not stage/delete without accepted disposition. | artifact disposition owner | artifact disposition or explicit cleanup authorization | false | false | git status workspace state |

## Gates Not To Do Now

- Golden promotion or minimum v1 promotion.
- Fixture promotion or setting `promotion_allowed=true`.
- QDII probing restart.
- FOF taxonomy or pure FOF search unless separately prioritized.
- `110020` / `017641` recut or fact-freeze without a separate decision gate.
- Source generalization, manifest runtime consumption, score/quality semantic changes, renderer changes, Service/UI changes, Host/Agent/dayu integration.
- Release readiness, PR, push, merge or external-state mutation.

## Control-Doc Compression Strategy

`docs/implementation-control.md` should remain a recovery surface, not a ledger. Keep only:

- Startup Packet status, current gate and next entry.
- A pointer to this roadmap artifact.
- Accepted plan/review artifact references for this roadmap gate.
- Route-based residual summaries and owners.
- The next actionable entry by fund: `004393`, `004194`, `006597`, then fixture promotion-prep.

Long gate history, detailed evidence and review narratives should stay in `docs/reviews/` or `docs/archive/`.

## Recommended Next Entry

Recommended next entry after controller review/acceptance of this roadmap:

1. `004393 partial coverage decision / expansion gate`.
2. `004194 P0 coverage or index_profile-only fixture decision gate`.
3. `006597 same-fund unavailable field review gate` if controller accepts the existing untracked follow-up evidence; otherwise `006597 strict correctness rerun with reports/golden-answers/golden-answer.json`, followed by the same manual unavailable-field review if triggered.
4. `fixture promotion-prep gate`.
5. `minimum v1 promotion gate` only after explicit authorization.

Self-check: pass for roadmap artifact scope.
