# P13 PR 7 Review — AgentMiMo（2026-05-22）

## PR Metadata

- **PR**: [PR 7](https://github.com/bill20232033cc/fund-agent/pull/7)
- **Branch**: `feat/p13-tracking-error-direct-disclosure` → `main`
- **Commits**: `2172691` (feat), `ffa8eff` (docs: accept aggregate review), `7b7be45` (docs: record aggregate commit)
- **Scope**: P13 tracking-error / index-profile direct-disclosure
- **Reference truth**: AGENTS.md, design.md, implementation-control.md, P13 plan/code/aggregate controller judgments

## Verdict

**PASS** — 无 blocking finding。

---

## Review Summary

PR 7 实现了 accepted P13-S1 plan 的全部 direct-disclosure slice，未引入 scope creep。实现与 prior code review / aggregate deepreview 的 controller judgment 一致。代码质量、模块边界、测试覆盖和文档同步均达标。

---

## Findings

### F1 [RESOLVED] renderer `assert` 已替换为显式 missing-data 分支

Code review 阶段发现 renderer 使用 `assert` 做运行时验证，已在 re-review 前修复为显式条件分支（`_has_renderable_tracking_error` + `_render_tracking_error_insufficient`）。当前代码无 `assert` 用于运行时路径。

### F2 [RESOLVED] composite benchmark 分隔符覆盖补齐

Code review 阶段发现 `_COMPOSITE_BENCHMARK_SEPARATORS` 仅覆盖 `+` / `＋`，已补齐为 `("＋", "+", "×", "*", "和", "及")`，`re.split` 同步使用全部分隔符。当前覆盖完整。

### F3 [RESOLVED] table+text 同值歧义逻辑修正

Code review 阶段发现表格和正文同时命中同一跟踪误差值时被误判为 ambiguous，已在 `_select_consistent_tracking_error_match` 中实现：解析值一致时优先返回 table match，不一致时 fail-closed。当前逻辑正确。

---

## Scope Compliance

| Accepted scope item | Status |
|---|---|
| explicit typed `IndexProfileValue` and `TrackingErrorValue` in models | ✅ |
| direct annual-report tracking-error extraction from `FundDocumentRepository`-provided parsed reports | ✅ |
| pure index / enhanced index / non-index / QDII-not-applicable / ambiguity / composite / missing fixtures | ✅ |
| risk-check migration to `ResolvedTrackingErrorForRisk` with no equal raw-scalar product authority | ✅ |
| renderer consumes `input_data.structured_data.tracking_error` | ✅ |
| deterministic audit guards against benchmark-anchor misuse | ✅ |
| snapshot observability does not enter FQ2/comparable/golden denominator | ✅ |

## Explicit Non-Goal Compliance

| Non-goal | Status |
|---|---|
| no calculated tracking error from external index series | ✅ 未引入 |
| no index methodology/constituents extraction beyond benchmark-context tiering | ✅ `_build_index_profile` 仅构造 `benchmark_only` availability |
| no RR-13 or `docs/repo-audit-20260521.md` changes | ✅ 未触及 |
| no Dayu runtime, LLM, Evidence Confirm, E1/E2/E3 | ✅ 未引入 |
| no Service/UI direct source access | ✅ Service 通过 `resolve_tracking_error_for_risk()` 消费 Capability 结构化数据 |

---

## Module Boundary Check

| Boundary rule | Status |
|---|---|
| Capability 层 owns tracking-error extraction / risk-check / audit / renderer | ✅ |
| Service 层只调用 `resolve_tracking_error_for_risk()` 消费 Capability 暴露的接口 | ✅ |
| `FundDocumentRepository` 是唯一文档入口 | ✅ extractors 通过 `ParsedAnnualReport` 消费 |
| 显式参数不放 `extra_payload` | ✅ `ResolvedTrackingErrorForRisk` 为 frozen dataclass，全部显式字段 |
| 基金类型判断优先 | ✅ `_tracking_error_for_fund_type` / `resolve_tracking_error_for_risk` 均先判断 fund_type |
| 无 `assert` 用于运行时验证 | ✅ 已修复 |

---

## Evidence Preservation Check

- 跟踪误差：`EvidenceAnchor` 含 `source_kind="annual_report"`、`section_id`、`page_number`、`table_id`、`row_locator`
- 审计 guard：`_audit_tracking_error_source_guard` 检查 `direct_disclosure` 必须有 `annual_report` 锚点
- 指数画像：`_audit_index_profile_source_guard` 阻止 benchmark-only 证据冒充编制方法/成分股

---

## Test Coverage Assessment

| Area | Coverage |
|---|---|
| tracking-error extractor: direct disclosure, target-only, ambiguous, std-dev guard | ✅ `test_performance.py` + fixtures |
| index-profile extractor: pure index, enhanced index, non-index, composite, ambiguous | ✅ `test_profile.py` + fixture |
| risk-check: resolved authority, developer override fallback, QDII not-applicable, missing | ✅ `test_risk_check.py` |
| renderer: structured_data tracking-error replacement, benchmark-only insufficient boundary | ✅ `test_renderer.py` |
| audit: tracking-error source guard, index-profile source guard | ✅ `test_audit_programmatic.py` |
| snapshot: `index_profile` / `tracking_error` observability not in comparable denominator | ✅ `test_extraction_snapshot.py` |
| service: full orchestration path with `resolve_tracking_error_for_risk` | ✅ `test_fund_analysis_service.py` |
| golden prefill: P13 fields integration | ✅ `test_golden_prefill.py` |

---

## Docs Sync Check

| Document | Updated | Content correct |
|---|---|---|
| `fund_agent/fund/README.md` | ✅ 12→14 items, tracking_error/index_profile description, risk-check mechanism update | ✅ |
| `tests/README.md` | ✅ test descriptions updated for P13 coverage | ✅ |
| `docs/implementation-control.md` | ✅ P13 aggregate acceptance recorded | ✅ |

---

## Controller Validation (recorded evidence)

- `pytest`: 424 passed in 1.38s ✅
- `ruff check fund_agent tests`: passed ✅
- `git diff --check HEAD`: passed ✅
- GitHub PR 7 CI test: passed ✅

---

## Accepted Residuals

| Residual | Owner / destination |
|---|---|
| Calculated tracking error from fund/index time series | Future P13 follow-up or separate data-source phase |
| External index series adapter | Future source-contract phase |
| Index methodology / constituents extraction beyond benchmark-context | Future index document/source-contract phase |
| QDII tracking-error applicability | Future subtype-design scope |
| `index_profile` / `tracking_error` snapshot promotion into comparable/golden/FQ2 denominator | Future quality-gate / golden-answer phase |
| `docs/repo-audit-20260521.md` | Untracked; excluded from PR scope |

---

## Residual Risk Assessment

无新增 residual risk。所有 residual 均为 prior aggregate deepreview 已接受的 future scope，PR 7 未引入新的技术债务或边界违规。

---

## Conclusion

PR 7 实现了 accepted P13-S1 plan 的完整 direct-disclosure 范围，prior code review 的 3 个 finding 全部 resolved，aggregate deepreview 已 PASS。生产代码模块边界清晰，Fund Capability 拥有全部基金领域逻辑，Service 只消费 Capability 暴露的结构化接口。测试覆盖充分，文档同步完整。

**Verdict: PASS。PR 7 可进入 draft PR gate。**
