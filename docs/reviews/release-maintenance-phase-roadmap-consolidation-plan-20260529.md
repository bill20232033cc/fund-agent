# Release Maintenance Phase Roadmap Consolidation Plan

日期：2026-05-29

角色：AgentCodex planning worker。当前 artifact 只提供下一 gate 的 handoff-ready plan；不得视为 controller judgment、promotion manifest、release readiness 或 implementation authorization。

## Worker Self-Check

- 当前工作单元：`release maintenance phase roadmap consolidation gate`。
- 当前分支：`codex/local-reconciliation`。
- Gate 分类：`heavy`，原因是 roadmap 会触达 minimum golden v1、fixture promotion、source/provenance hardening、Host/Agent/dayu future architecture、manifest lifecycle 与 control-plane next-entry semantics。
- 本 worker 不启动 `$gateflow` 或 `/gateflow`，不实现代码，不修改生产代码，不修改 `docs/implementation-control.md`，不提交、不 push、不 PR、不 merge、不 release、不 promotion。
- 本 worker 只允许新增本计划 artifact：`docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-20260529.md`。
- 既有 untracked artifacts 只读作为 workspace 状态证据；不 stage、不删除、不覆盖。

## Goal

为 controller /后续执行 worker 准备一个 handoff-ready 计划，用于下一 gate 产出两个 docs/control-plane-only 结果：

1. `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`：release maintenance phase roadmap consolidation artifact。
2. `docs/implementation-control.md` 的最小更新：只压缩/更新 Startup Packet、current roadmap pointer、accepted artifacts index、open residuals、next entry point；禁止追加长日志。

最终 roadmap 必须把 release maintenance 后续工作拆成五条路线，并避免把 deferred 或条件候选误报为 ready：

- minimum golden v1 readiness。
- deferred coverage。
- source/provenance hardening。
- future Host/Agent/dayu architecture。
- artifact/manifest lifecycle。

## Scope

- 消费并引用本计划列出的 truth sources。
- 汇总 solved blockers 与 remaining blockers，尤其明确 `006597` 的 `bond_risk_evidence_missing` 已 closed，但 `006597` 不是 promotion-ready。
- 给出 minimum v1 仍需处理的 004393 / 004194 / 006597 strict correctness、fixture promotion state 与 strict correctness 决策顺序。
- 明确 QDII candidates、FOF_SLOT、110020、017641 从 minimum v1 deferred，但仍 block full v1，除非后续 controller 明确改判。
- 区分三类后续工作：代码实现任务、人工 fact-freeze / coverage policy judgment、manifest/control-plane maintenance。
- 纳入 mandatory future architecture / fund reasoning residual：facet inference / ITEM_RULE routing design gate；本 gate 不实现 facet。

## Non-Goals And Hard Stops

- 不修改生产代码、测试、runtime、CLI、score、quality gate、snapshot、renderer、Service/UI、Host/Agent/dayu。
- 不修改 golden answer 或 golden fixture。
- 不修改 `docs/implementation-control.md` 于本 planning worker；后续 gate 只能做最小 control-doc pointer/update。
- 不执行 golden promotion，不设置 `promotion_allowed=true`。
- 不改变 score / quality gate / FQ0-FQ6 / final judgment 语义。
- 不重启 QDII probing。
- 不把任何 deferred item 报告为 ready。
- 不创建 Host/Agent/dayu package，不做 architecture implementation。
- 不 PR、不 push、不 merge、不 release。
- 不把显式参数藏入 `extra_payload`；保留 `UI -> Service -> Host -> Agent` 边界。

## Truth Sources To Cite

后续 roadmap artifact 必须直接引用这些来源，并在关键结论旁标注来源路径：

- `AGENTS.md`：规则真源、heavy gate 分类、control doc 压缩原则、四层边界、禁止 `extra_payload`、FundDocumentRepository 与 fallback taxonomy。
- `docs/design.md`：设计真源、当前确定性 `UI -> Service -> fund_agent/fund` 过渡链路、future Host 使用 `dayu.host`、future Agent engine 使用 `dayu.engine`、CHAPTER_CONTRACT / ITEM_RULE / preferred_lens 当前事实。
- `docs/implementation-control.md`：当前 Startup Packet、accepted artifacts、open residuals、next entry point。
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json` and `.md`：preflight `overall_status=block`、per-fund readiness、resolved `bond_risk_evidence_missing`、global blockers。
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`：control-plane residual decisions、`blocks_minimum_v1` / `blocks_v1`、`promotion_allowed=false`。
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`：fixture_state、promotion blockers、resolved context、all `promotion_allowed=false`。
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md`：004393 / 004194 / 006597 conditional decisions and next gate.
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md`：006597 bond risk closure evidence and residual warnings.
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-controller-judgment-20260528.md`：typed NAV boundary and raw-unit ineligibility.
- `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-controller-judgment-20260528.md`：Eastmoney accumulated NAV candidate and limitations.
- `docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-controller-judgment-20260528.md`：CSRC EID primary candidate, stock-sdk evidence-only.
- `docs/reviews/release-maintenance-csrc-eid-accumulated-nav-adapter-normalization-controller-judgment-20260529.md`：CSRC EID runtime typed source, source-level eligibility, residuals.
- `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md`：110020/017641 provenance terminal states.
- `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md`：QDII probing stopped, FOF taxonomy gap, coverage disposition.
- Relevant optional sources when writing route detail: `110020`, `017641`, replacement/exclusion, and QDII candidate controller judgments.

## Direct Evidence Summary

- Current architecture guardrail: `AGENTS.md` and `docs/design.md` define target `UI -> Service -> Host -> Agent`; current deterministic production path remains UI -> Service -> `fund_agent/fund`. Future Host must use `dayu.host`; future Agent execution kernel/tool loop must use `dayu.engine`.
- Control-plane guardrail: `docs/implementation-control.md` says release maintenance current next entry is `004393 / 004194 / 006597 strict correctness follow-up gate`; golden promotion has not entered.
- Golden readiness preflight says `overall_status=block`, ready count is zero, and preflight is read-only with no fixture promotion, golden promotion, release, or QDII probing.
- Solved blocker: preflight and drawdown controller judgment agree `006597` `bond_risk_evidence_missing` / `drawdown_stress` is resolved by reviewed NAV-derived max drawdown evidence. Latest 006597 snapshot satisfies all seven bond risk groups; score has no `bond_risk_evidence_missing`; quality gate has no bond-risk blocker.
- Not ready: fixture promotion manifest records 006597 `fixture_state="absent"`, blockers `strict_golden_not_configured` and `fixture_promotion_absent`, and `promotion_allowed=false`. Therefore do not say 006597 is promotion-ready.
- 004393: strict-golden controller judgment records `conditional_candidate_pending_partial_coverage_decision`; score comparable records are partial (`9/150`, P0 `9/11`, P1 `0/10`). It requires a partial coverage decision or expansion gate before fixture promotion prep.
- 004194: strict-golden controller judgment records `conditional_candidate_pending_p0_coverage_decision`; current covered scope is only five `index_profile.*` records and P0 strict correctness coverage is zero. It requires P0 coverage / index_profile-only fixture decision.
- QDII candidates `096001`, `040046`, `019172`, `021539`, plus `017641`, `FOF_SLOT`, and `110020` are deferred from minimum v1 in the residual and fixture manifests, but keep `blocks_v1=true`; they remain full-v1 blockers.
- Source/provenance hardening has accepted runtime source work for 006597-family CSRC EID accumulated NAV, but has residuals around source generalization, parser/schema drift, request-context provenance, endpoint availability, and multi-anchor projection.
- Existing residual / fixture manifests are control-plane evidence only, not promotion manifests and not runtime/preflight-consumed unless a future implementation gate explicitly changes that.

## Affected Files

This planning worker:

- Add only `docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-20260529.md`.

Future roadmap consolidation gate, after plan review/controller authorization:

- Add `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`.
- Minimally update `docs/implementation-control.md`.

No production source, tests, reports, golden answers, golden fixtures, manifests, or README files should change in the future roadmap consolidation gate unless the controller explicitly opens a separate gate.

## Proposed Artifact Paths

- Plan artifact: `docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-20260529.md`.
- Roadmap artifact: `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`.
- Plan reviews: `docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-review-mimo-20260529.md` and `docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-review-ds-20260529.md` or equivalent two independent reviewers.
- Implementation evidence: `docs/reviews/release-maintenance-phase-roadmap-consolidation-implementation-evidence-20260529.md`.
- Implementation reviews: two independent reviews under `docs/reviews/`.
- Controller judgment: `docs/reviews/release-maintenance-phase-roadmap-consolidation-controller-judgment-20260529.md`.

## Route Taxonomy

The roadmap artifact must use exactly these five top-level routes.

### Route 1: Minimum Golden V1 Readiness

Purpose: get the minimum explicitly authorized v1 set to a promotion-prep decision point without promoting.

Must include:

- 004393 partial coverage decision or expansion gate.
- 004194 P0 coverage / index_profile-only fixture decision gate.
- 006597 strict correctness rerun or follow-up gate after bond blocker closure.
- Fixture promotion-prep gate after strict correctness and coverage decisions.
- Minimum v1 promotion gate only after explicit authorization.

Must not include:

- QDII probing.
- FOF taxonomy unless prioritized by controller.
- 110020 / 017641 full-v1 recovery.
- Any promotion or `promotion_allowed=true` in this route artifact.

### Route 2: Deferred Coverage

Purpose: keep non-minimum-v1 blockers visible without letting them block the minimum v1 path.

Must include:

- QDII candidates `096001`, `040046`, `019172`, `021539`: deferred from minimum v1, still full-v1 blockers, QDII probing stopped.
- `017641`: replacement disposition preserved; source provenance complete but quality block / manager strategy data gap; deferred from minimum v1, still full-v1 blocker.
- `FOF_SLOT`: pure FOF taxonomy / repository-verified candidate gap; QDII-FOF cannot count as pure FOF.
- `110020`: reviewed coverage candidate only; methodology / constituents / reviewed fact-freeze insufficient; deferred from minimum v1, still full-v1 blocker.

Must distinguish policy decisions from implementation work:

- QDII / 017641 / FOF / 110020 require manual coverage policy or fact-freeze gates before any code work.
- None of these rows may be described as ready.

### Route 3: Source / Provenance Hardening

Purpose: collect source reliability and provenance residuals that are not minimum-v1 promotion blockers unless controller says so.

Must include:

- CSRC EID runtime typed source is accepted for 006597-family accumulated NAV through `FundNavRepository()`.
- `raw_unit_nav` remains ineligible for strong drawdown evidence.
- stock-sdk remains evidence-only due to date identity/integrity issue.
- Future hardening candidates: source_query_params split, CSRC EID source generalization, F direct-search gap generalization, parser/schema drift, duplicate date early detection, endpoint caching/SLA, strict bool parsing for source metadata, multi-anchor snapshot projection if consumers need it.

Must preserve:

- Fund data boundary and explicit params.
- `FundDocumentRepository` for annual-report access.
- Fail-closed taxonomy for schema/identity/integrity failures.

### Route 4: Future Host / Agent / Dayu Architecture

Purpose: record architecture residuals without implementing them.

Must include:

- Current production path remains deterministic UI -> Service -> `fund_agent/fund`; no Host/Agent package creation now.
- Future Host gate must use `dayu.host` for session/run/lifecycle/concurrency/timeout/cancel/resume/memory/reply outbox/events.
- Future Agent execution gate must use `dayu.engine` for runner/tool loop/ToolRegistry/ToolTrace/context budget/tool execution.
- No `extra_payload` parameter hiding; all scene/tool/fund/year/source/cache/quality parameters must be explicit.

Mandatory fund reasoning residual:

- Future `facet inference / ITEM_RULE routing design gate`.
- It must state the current boundary: `fund_type` is the coarse standard type used by preferred_lens and ITEM_RULE; facets are narrower evidence-based traits that should not be inferred by LLM guessing.
- Implicit unmodeled facets to consider:
  - Bond: short-duration, credit-rating, leverage-liquidity, redemption pressure, multi-share-class, NAV-derived drawdown availability, convertible-bond exposure.
  - Index/enhanced index: ETF-linked, tracking-error direct disclosure, `index_profile` benchmark-only.
  - QDII: QDII-FOF, overseas index, overseas bond, FX, geography.
  - FOF: pure FOF, QDII-FOF, holding look-through availability.
- Inference must be deterministic and evidence-based; it must consume structured annual-report/source facts and expose missing/ambiguous states, not LLM guesses.
- Routing implications: facets may affect `ITEM_RULE`, `must_answer`, `must_not_cover`, `preferred_lens`, evidence requirements, and deletion/render decisions.
- Ownership: Agent/Fund layer, because it understands fund type, CHAPTER_CONTRACT, ITEM_RULE, preferred_lens and evidence audit. Service may choose scenes/contracts, but fund facet inference belongs in `fund_agent/fund`.
- It can be designed before Host/Agent/dayu integration and later consumed by a dayu agent first-step facet flow.
- Do not implement facet inference in this roadmap gate.

### Route 5: Artifact / Manifest Lifecycle

Purpose: prevent control-plane artifacts from being confused with runtime truth or promotion manifests.

Must include:

- `golden-readiness-residual-disposition-manifest-20260529.json` is tracked control-plane evidence only, not a promotion manifest and not runtime/preflight-consumed.
- `fixture-promotion-state-manifest-20260529.json` is tracked control-plane state evidence only, not a promotion manifest and not runtime/preflight-consumed; all entries keep `promotion_allowed=false`.
- Future runtime/preflight manifest consumption requires separate implementation gate, full validation, and clear schema/lifecycle rules.
- Future control doc updates should compress pointers, not append long logs.
- Untracked artifacts and stray `--help` remain read-only unless a separate artifact disposition gate or explicit user authorization says otherwise.

## Residual Table Requirements

The roadmap artifact must include a residual table with at least these columns:

| route | item | current_state | owner | next_gate | blocks_minimum_v1 | blocks_full_v1 | evidence |
|---|---|---|---|---|---|---|---|

Minimum expected rows:

- `004393 / 2024`: conditional candidate pending partial coverage decision; `blocks_minimum_v1=true`; `blocks_full_v1=true`.
- `004194 / 2024`: conditional candidate pending P0 coverage / index_profile-only decision; `blocks_minimum_v1=true`; `blocks_full_v1=true`.
- `006597 / 2024`: bond blocker closed but strict correctness / fixture absent unresolved; `blocks_minimum_v1=true`; `blocks_full_v1=true`.
- Global fixture promotion: absent / not authorized; `blocks_minimum_v1=true`; `blocks_full_v1=true`.
- QDII candidates: deferred from minimum v1; `blocks_minimum_v1=false`; `blocks_full_v1=true`.
- `017641 / 2024`: replacement / quality block; `blocks_minimum_v1=false`; `blocks_full_v1=true`.
- `FOF_SLOT`: taxonomy/data gap; `blocks_minimum_v1=false`; `blocks_full_v1=true`.
- `110020 / 2024`: reviewed candidate only, evidence insufficient; `blocks_minimum_v1=false`; `blocks_full_v1=true`.
- Source/provenance hardening residuals: generally `blocks_minimum_v1=false` unless tied to a specific accepted next gate; `blocks_full_v1` should be explicit per item.
- Facet inference / ITEM_RULE routing design: future architecture/fund reasoning residual; not a minimum-v1 blocker unless controller elevates it; full-v1 impact should be marked as future design blocker/risk, not ready.
- Artifact/manifest lifecycle: manifest runtime consumption and artifact disposition; not promotion authorization.

## Suggested Next Gate Order

Recommended order after roadmap consolidation is accepted:

1. `004393 / 004194 / 006597 strict correctness follow-up gate`.
2. If separated by controller: `006597 strict correctness rerun with reports/golden-answers/golden-answer.json`.
3. `004393 partial coverage decision or expansion gate`.
4. `004194 P0 coverage / index_profile-only fixture decision gate`.
5. `fixture promotion-prep gate`.
6. `minimum v1 promotion gate` only after explicit authorization.

Gates not to do now:

- Golden promotion.
- QDII probing.
- FOF taxonomy unless explicitly prioritized.
- Host/Agent/dayu integration.
- Release readiness.
- Source generalization or manifest runtime consumption unless separately prioritized.

## Implementation Slice For Future Roadmap Gate

Slice A: roadmap artifact

- Write `docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md`.
- Include goal/scope/non-goals, truth-source index, evidence summary, five route taxonomy, residual table, next gate order, and stop conditions.
- Cite source paths inline; avoid unsupported claims from untracked artifacts.
- Avoid saying any sample is ready, promoted, or `promotion_allowed=true`.

Slice B: minimal control-doc update

- Update only the front control-plane surface of `docs/implementation-control.md`.
- Allowed edits:
  - Startup Packet current status / next entry point.
  - Current roadmap pointer to the new roadmap artifact.
  - Accepted artifacts index with the roadmap artifact and controller judgment after acceptance.
  - Open residuals summarized by the five-route taxonomy.
  - Next entry point set to `004393 / 004194 / 006597 strict correctness follow-up gate` unless controller chooses another accepted next gate.
- Forbidden edits:
  - Long logs.
  - Historical narrative appendices.
  - Promotion status changes.
  - Runtime/preflight manifest consumption claims.
  - Architecture implementation claims.

## Review Plan

Because this is a heavy docs/control-plane gate, require at least two independent reviewers before controller acceptance.

Reviewer focus:

- Verify five-route taxonomy matches truth sources and does not collapse deferred coverage into minimum v1.
- Verify `006597` wording: bond blocker closed, not promotion-ready.
- Verify `004393` and `004194` strict correctness details and next gates.
- Verify QDII/FOF/110020/017641 remain deferred from minimum v1 and still block full v1.
- Verify control-doc update strategy stays compressed and does not append ledger material.
- Verify facet inference / ITEM_RULE routing residual includes current fund_type vs facet boundary and Agent/Fund ownership.
- Verify no non-goal is violated: no promotion, no quality semantic change, no Host/Agent/dayu implementation, no QDII probing.

## Validation Matrix

Planning worker validation:

- `git diff --check -- docs/reviews/release-maintenance-phase-roadmap-consolidation-plan-20260529.md`.
- No JSON checks required because this plan artifact is Markdown only.
- No ruff / pytest required because no Python, tests, runtime, CLI, schema, golden fixture, or manifest is modified.

Future roadmap gate validation:

- Always run `git diff --check`.
- If JSON is touched, run `python -m json.tool <json-path>` for every touched JSON file.
- If only Markdown/control docs are touched, ruff / pytest are not required; explain why in implementation evidence.
- If any Python/test/runtime/schema/manifest-consumption code is touched despite this plan, stop and reclassify with a new implementation plan and full validation.

## Stop Conditions

Stop and return to controller if any of the following occurs:

- A requested edit would modify production code, score, quality gate, snapshot, renderer, CLI, Service, Host/Agent/dayu, golden answers, golden fixtures, or promotion manifests.
- A reviewer asks to set `promotion_allowed=true` or mark a deferred item ready.
- New evidence suggests 006597 bond blocker regressed; do not silently reopen or close without a separate evidence gate.
- Any roadmap claim requires QDII probing, FOF taxonomy, Host/Agent/dayu integration, release readiness, or source generalization now.
- `docs/implementation-control.md` update expands into a long ledger rather than compressed pointers.
- JSON manifests need schema changes or runtime/preflight consumption.
- Workspace contains tracked dirty changes not attributable to the current gate and they conflict with the planned files.

## Completion Report Format

Final worker/controller report should be concise and include:

- Artifact path(s) written.
- Validation commands and outcomes.
- Whether only allowed files changed.
- Summary of route taxonomy and next gate.
- Explicit statement: no promotion, no production code, no golden fixture, no quality semantic, no QDII probing, no Host/Agent/dayu implementation.
- `Self-check: pass` or `Self-check: blocked` with reason.
