# NAV Source Capability / Adjusted Basis Plan Review — DS

Date: 2026-05-28

Reviewer: DS (review worker, not controller)

Gate: `NAV source capability / adjusted basis evidence gate`

Gate classification: `standard`

Reviewed targets:
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-plan-20260528.md`
- `docs/reviews/release-maintenance-nav-source-capability-adjusted-basis-evidence-20260528.md`

Conclusion: PASS_WITH_FINDINGS

## Worker Self-Check — Start

- Status: pass.
- Current role is review worker only. I did not start `$gateflow` / `/gateflow`, did not restart from plan, and did not enter implementation.
- Source of truth read: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, prior drawdown contract controller judgment, prior DS plan review, latest `006597 / 2024` snapshot / score / quality-gate artifacts, and current NAV boundary code (`nav_data.py`, `data_extractor.py`, `extraction_snapshot.py`).
- Scope boundary: write durable review artifact only. No production code, tests, score, quality gate, schema, golden fixture, release / PR state, Host / Agent / dayu, QDII / FOF / `110020`, or blocker removal.
- Completion signal: one review artifact with conclusion and findings in gateflow format.

## Source Replay

The current gate starts from these accepted truths:

- `AGENTS.md` is the highest-priority rule source. Project boundary is `UI -> Service -> Host -> Agent`. Current deterministic production path is UI → Service → `fund_agent/fund` Agent-layer Fund package.
- `docs/design.md` §6.2: `FundDataExtractor` composes `FundDocumentRepository`, section extractors, and `FundNavDataAdapter`. `NavDataResult` exposes `source`, `cached`, `unavailable`, but not basis/provenance.
- `docs/implementation-control.md`: next entry point is this NAV source capability gate. Prior drawdown NAV-derived contract gate blocked because current adapter proves only `单位净值走势` / `日增长率`, not total-return / cumulative / adjusted basis.
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-controller-judgment-20260528.md`: NAV-derived evidence accepted only as future candidate. Six requirements must be met before `drawdown_stress` can become accepted.
- `docs/reviews/release-maintenance-drawdown-stress-nav-derived-contract-plan-review-ds-20260528.md`: DS-P1 through DS-P4 all accepted; current provider cannot prove adjusted basis; gate converted to blocked-with-decision.
- Latest `006597 / 2024` artifacts: `bond_risk_evidence` partial with `drawdown_stress` weak; `nav_data` value present but not traceable; quality gate `warn` with FQ2F `bond_risk_evidence_missing`.

## Review Method

- Static review of both target artifacts against all required truth sources.
- Direct code verification of every code claim in plan and evidence against `nav_data.py`, `data_extractor.py`, `extraction_snapshot.py`.
- Cross-reference of artifact evidence claims against the actual snapshot / score / quality-gate JSON.
- Boundary check against `AGENTS.md` module boundaries, `docs/design.md` architecture, and `docs/implementation-control.md` scope constraints.
- Adversarial pass: what could a future implementer misinterpret from these artifacts?

## Assumptions Tested

1. Plan/evidence accurately answers source capability, adjusted basis, provenance, identity, fail-closed.
2. Read-only cache inspection is correctly positioned as auxiliary diagnostic, not production-acceptable boundary.
3. `blocked_pending_source_adapter` recommendation has direct evidence from the public `FundNavDataAdapter` boundary.
4. No scope violations: no unblocking, no score/quality/schema/golden changes, no upgrading 控制回撤, no bypassing FundDocumentRepository or UI/Service/Host/Agent boundaries.
5. Independent NAV repository/source adapter gate recommendation is appropriate and correctly sequenced.

## Direct Evidence Summary

All code claims in the plan and evidence were verified against current code:

- `nav_data.py:72`: `indicator="单位净值走势"` — confirmed. Only unit NAV trend is fetched.
- `nav_data.py:99-117`: `NavDataResult` dataclass — confirmed. Fields are `fund_code`, `records`, `source`, `cached`, `unavailable`, `unavailable_reason`. No `nav_type`, `adjustment_basis`, `origin_source_name`, `retrieved_at`.
- `nav_data.py:299-306`: `_load_cached_sync()` — confirmed. SELECTs only `payload_json`, drops `source` and `updated_at`.
- `nav_data.py:251`: cache hit returns `source="nav_cache"` — confirmed. Origin source name is lost.
- `data_extractor.py:247-273`: `_load_nav_data_or_unavailable()` — confirmed. NAV provider exceptions degrade to `unavailable=True`; annual-report failures remain outside catch.
- `extraction_snapshot.py:957-1009`: `_build_nav_record()` — confirmed. Always passes `anchor=None`, emits note text only, no provenance/basis/date-range fields.
- Snapshot line 17: `nav_data` has `value_present=true`, `anchor_present=false`, note `source=nav_cache; cached=True; records=1802` — confirmed.
- Score: `nav_data` coverage 1.0, traceability 0.0, status `fail` — confirmed.
- Score: `bond_risk_evidence_missing` with `baseline_blocking=true`, `missing_evidence_groups=["drawdown_stress"]` — confirmed.
- Quality gate: status `warn`, FQ2F for `bond_risk_evidence_missing` — confirmed.

Smoke evidence was collected through the correct unified boundary (`FundNavDataAdapter().load_nav_data("006597")`). Cache inspection was read-only SQLite metadata query, clearly labeled as such.

## Findings

### DS-F1-[info]-cache inspection 标注措辞可更精确

- **位置**: evidence artifact Worker Self-Check line 17, plan lines 104–109
- **问题类型**: 措辞清晰度 / 非阻断
- **当前写法**: evidence self-check 写 "No direct production PDF/cache access was used; the only cache inspection was NAV SQLite read-only metadata and payload shape inspection"。同一文档随后详述了 SQLite cache 读取。
- **为什么需要注意**: "No direct production cache access" 与 "the only cache inspection was NAV SQLite" 之间存在轻微张力。实际意图是正确的：NAV SQLite 读取是只读诊断，不是生产路径变更。但措辞可能让未来 controller 或 reviewer 误以为 evidence collector 在回避承认 cache 读取。
- **实际风险评估**: 低。所有 cache 读取都明确标注为 read-only，命令完整记录在 evidence artifact 中，capability 结论（blocked）完全基于公开 `FundNavDataAdapter` 边界结果，不依赖 cache inspection。cache inspection 只补充了公开边界丢失的 metadata（stored_source, updated_at），这些 metadata 不影响 capability 结论。
- **建议 disposition**: accept as info。不需要修改 artifact，但 controller 在 judgment 中应确认 cache inspection 的辅助诊断角色。
- **严重程度**: info

### DS-F2-[info]-plan line 110 "This proves" 指代可更明确

- **位置**: plan line 110–111
- **问题类型**: 措辞清晰度 / 非阻断
- **当前写法**: "This proves raw NAV availability for 006597 through the current unified Fund boundary."
- **为什么需要注意**: "This" 的指代范围略模糊——它可能被读作指向前面两段证据（公开边界 smoke + cache inspection），也可能仅指公开边界 smoke。实际上公开边界 smoke（lines 96–101）已经独立证明了 raw NAV availability，不需要 cache inspection 来补充这个结论。
- **实际风险评估**: 低。无论哪种读法，结论都是正确的：raw NAV 可用，adjusted basis 不可证明。不影响 capability decision。
- **建议 disposition**: accept as info。未来写类似 evidence 时建议用 "The public boundary smoke proves..." 替代 "This proves..."。
- **严重程度**: info

### DS-F3-[info]-`_load_cached_sync` metadata 丢失已正确识别为 capability gap

- **位置**: plan lines 89–90, evidence lines 123–125
- **问题类型**: 确认性观察 / 非阻断
- **当前写法**: plan 和 evidence 都正确指出 cache hit 时 `_load_cached_sync()` 只返回 `payload_json`，丢失 `source` 和 `updated_at`。
- **为什么记录**: 这是一个真实的代码 gap：SQLite schema 存储了 `source` 和 `updated_at`，但公开适配器接口不暴露它们。这是未来 NAV source adapter gate 应该修复的问题。plan 正确地将此作为 capability 证据而非本 gate 的修复目标。
- **实际风险评估**: 低。当前不影响 capability 结论，但未来 NAV adapter gate 必须解决。
- **建议 disposition**: accept as info。Controller 应在 next gate 的 scope 中包含此 gap 的修复要求。
- **严重程度**: info

## Review Criteria Assessment

### 1. Source Capability — PASS

Plan 准确描述了当前 NAV 适配器的能力边界：通过 `ak.fund_open_fund_info_em(indicator="单位净值走势")` 获取 `净值日期`、`单位净值`、`日增长率` 三个字段。Evidence 通过公开边界 smoke 和代码审查独立验证了这一点。Future contract decision 清晰定义了 accepted basis（total_return_nav / cumulative_nav / adjusted_nav）和 rejected basis。

### 2. Adjusted Basis — PASS

Plan 正确判定当前 `adjustment_basis=unknown`。`NavDataResult` 没有 `nav_type`、`adjustment_basis`、`series_type` 字段。公开边界 smoke 返回的字段不包含 cumulative NAV、adjusted NAV 或 dividend adjustment 信息。Rejected basis 列表（unit_nav_only, daily_growth_rate_unknown_basis, cache_legacy_unknown_basis）覆盖了当前所有可能的误用路径。

### 3. Provenance — PASS

Plan 正确识别了 provenance gap：cache hit 时 `origin_source_name` 和 `retrieved_at` 丢失；snapshot 的 `_build_nav_record()` 不暴露 NAV provenance、basis、date range、source kind 或 calculation method。Required provenance fields 列表（lines 135–148）是全面的。

### 4. Identity — PASS

Plan 正确指出 identity 只能在 request/cache key 级别验证，没有 source-returned identity field。Failure classification 表中 `identity_mismatch` 的定义正确，handling 为 fail-closed。

### 5. Fail-Closed — PASS

Plan 的 failure classification（lines 152–163）对所有非正常情况都推荐 fail-closed。`adjustment_basis_unknown` → fail closed for max drawdown / volatility evidence。`insufficient_history` → fail closed for annual risk contract。Evidence 的 failure classification for current state（lines 263–283）将当前 006597 正确归类为 `adjustment_basis_unknown`，handling 为 `ineligible_fail_closed`。

### 6. Cache Inspection Boundary — PASS (with DS-F1 note)

Cache inspection 在所有位置都标注为 read-only 和 supplementary。Capability 结论基于公开 `FundNavDataAdapter` 结果。DS-F1 记录措辞可优化但不影响实质。

### 7. blocked_pending_source_adapter Evidence Support — PASS

推荐有充分的直接证据支撑：
- 代码级证据：`indicator="单位净值走势"` 固定为单位净值
- 公开边界 smoke：返回字段只有 `净值日期`、`单位净值`、`日增长率`
- `NavDataResult` 结构：无 basis/provenance 字段
- 现有 artifact：snapshot `nav_data` anchor_present=false，score traceability 0.0

### 8. Scope Boundary — PASS

Plan 的 non-goals 明确排除：改变 `bond_risk_evidence` satisfaction、score/quality gate/schema/golden 变更、升级 控制回撤、绕过 FundDocumentRepository、进入 QDII/FOF/110020、Host/Agent/dayu、release/PR 操作。

Evidence 的实际内容与 non-goals 一致。没有发现 scope 越界。

检验清单：
- 未改变 `bond_risk_evidence` satisfaction ✓
- 未改变 score 语义 ✓
- 未改变 quality gate 语义 ✓
- 未改变 snapshot schema ✓
- 未改变 golden fixtures ✓
- 未升级 qualitative 控制回撤 text ✓
- 未绕过 `FundDocumentRepository` ✓
- 未进入 UI/Service/Host/Agent 边界变更 ✓
- 未解除 blocker ✓（explicitly `blocked_pending_source_adapter`）

### 9. Independent NAV Gate Recommendation — PASS

Plan 的 Future Gate Slicing（lines 167–213）正确分解为三个顺序 gate：
- Gate 1: NAV Source Repository / Adapter Capability（先决条件）
- Gate 2: Derived Drawdown Evidence Contract Schema（依赖 Gate 1）
- Gate 3: Risk Metric Calculator And 006597 Validation（依赖 Gate 2）

每个 gate 有明确的 objective、allowed changes、non-goals、stop condition。Gate 1 的 stop condition（"If no existing or reviewed provider can expose cumulative / adjusted / total-return basis for 006597, stop as blocked"）是正确且必要的。

这完全符合 `docs/implementation-control.md` 的 next entry point 要求和 prior DS plan review 的 DS-P4 建议（将 source capability 与 schema migration / calculator / score 解耦）。

## Relationship to Prior DS Review

本次 review target（plan + evidence）实际上是 prior DS plan review（`release-maintenance-drawdown-stress-nav-derived-contract-plan-review-ds-20260528.md`）DS-P4 建议的直接产物。Prior DS-P4 说 "将计划拆成先决 gate：NAV source capability / adjusted basis decision"。当前 plan/evidence 正是按这个建议执行的窄 gate。

Prior DS review 的四条 finding（DS-P1 到 DS-P4）在当前 gate 中均得到正确处理：
- DS-P1（NAV source 不能证明 total-return）→ 当前 plan 确认为 blocked，不做实现
- DS-P2（derived anchor 与 v1 冲突）→ 推迟到未来 Gate 2
- DS-P3（snapshot/score 不能 machine-check per-group provenance）→ 推迟到未来 Gate 2/3
- DS-P4（slices 过粗）→ 当前 plan 的三 gate 拆分解决了这个问题

## Residual Risks

- 当前 plan/evidence 使用了 read-only SQLite cache inspection 作为辅助证据。虽然不影响 capability 结论的正确性，但若未来 worker 模仿此模式用于 production path 判断，必须确保 capability 决策始终以公开边界结果为准。
- `_load_cached_sync()` 丢失 metadata 是真实 gap，当前只作为 capability 证据记录。未来 NAV adapter gate 若仅添加 `NavDataResult` 字段而不修复 cache hit 路径，metadata 仍会在 cache hit 时丢失。
- 若 akshare 实际上支持 `累计净值走势` 或其他 indicator（如 `fund_open_fund_info_em` 的 `indicator="累计净值走势"`），当前 plan 未探索此可能性。但这属于未来 Gate 1 的 provider investigation 范围，不是本 capability assessment gate 的缺陷。

## Controller Decision Placeholder

| Finding | Suggested disposition | Controller decision |
|---|---|---|
| DS-F1 (cache inspection wording) | accept as info | TBD |
| DS-F2 (plan "This proves" referent) | accept as info | TBD |
| DS-F3 (`_load_cached_sync` metadata gap) | accept as info | TBD |

## Final Conclusion

PASS_WITH_FINDINGS.

Plan 和 evidence 准确回答了 source capability、adjusted basis、provenance、identity 和 fail-closed 五个核心问题。Cache inspection 被正确标注为辅助诊断，capability 结论基于公开 `FundNavDataAdapter` 边界。`blocked_pending_source_adapter` 推荐有充分的代码和 smoke 证据支撑。没有发现 scope 越界。三个 info 级 finding 涉及措辞清晰度和已正确识别的代码 gap，均不改变 capability 结论或 blocker 状态。

推荐 controller 接受 `blocked_pending_source_adapter` 结论，将 next entry point 设为独立的 `NAV repository/source adapter adjusted-basis contract gate`（即 plan 中定义的 Gate 1），并在该 gate 的 scope 中包含 `_load_cached_sync` metadata 暴露的修复。

## Worker Self-Check — Completion

- Status: pass.
- I produced the requested durable review artifact only.
- I did not modify production code, tests, score, quality gate, schema, golden fixture, design/control truth, release / PR state, or unrelated untracked files.
- I did not commit, push, create PR, merge, or close out the gate.
- Review conclusion is PASS_WITH_FINDINGS; all findings are info-level; core capability conclusion is confirmed.
