# Plan Review: report-quality scoring JSONL content validation plan

> **Reviewer**: AgentGLM
> **Date**: 2026-05-25
> **Reviewed artifact**: `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` §5.4 / §5.4.1 / §5.4.2 / §7.1-§7.6, `docs/implementation-control.md` Startup Packet / Next Entry Point, `fund_agent/fund/report_evidence.py`, `fund_agent/fund/extraction_score.py`, `fund_agent/fund/quality_gate.py`
> **Review posture**: Constructively adversarial; default suspect; evidence-based findings only

---

## 1. Assumptions Tested

| # | Assumption | Verification method | Result |
|---|-----------|-------------------|--------|
| A1 | Plan does not modify FQ0-FQ6 behavior | Cross-check §1 non-goals + §2 file scope against `quality_gate.py` (1348 lines, 6 rule codes FQ0-FQ6) | PASS — plan never touches `quality_gate.py`; §1 L26-27 explicitly non-goal |
| A2 | Plan reuses typed domain, no parallel schema | Cross-check §3 L84, §4.B L182-187 against `report_evidence.py` dataclass definitions (27 Literal types, 15 frozen slotted dataclasses) | PASS — plan mandates reuse; explicit prohibition at L84 |
| A3 | Plan prohibits PDF/cache/source/repo/dayu/nav_data/fixtures | Cross-check §1 non-goals L24-39, §7 boundary checks L406-417 against AGENTS.md hard constraints | PASS — all prohibited items explicitly listed |
| A4 | Plan focuses on input verifiability, not CLI/Service | Cross-check §2 L69-71 rationale against design.md §5.4 principle 1 ("scoring before iterating") | PASS — §2 L69-71 gives correct first-principles rationale |
| A5 | scoring_ready preconditions match existing projection code | Cross-check §4.H L257-272 against `report_evidence.py::_is_scoring_ready` (L2090-2128) | PASS with finding F1 — preconditions match but are restated; see F1 |
| A6 | Rule set is internally consistent | Cross-check §4.A-§4.I for contradictions | PASS with finding F3 — minor redundancy; no contradictions found |
| A7 | Invalid combinations cover all fail-closed cases in AGENTS.md | Cross-check §4.C L189-208 against AGENTS.md fallback strategy table (L226-237) and `report_evidence.py::_validate_projection_context` (L943-974) | PASS — all fail-closed source failures covered |

---

## 2. Findings

### F1-未修复-中-§4.C 与 §4.H scoring_ready 前置条件重复定义

- **位置**: §4.C 规则 2-8 (L192-199), §4.H 条件 1-7 (L259-268)
- **问题类型**: 契约缺失 / 规则重复
- **当前写法**: §4.C 以 "invalid combination" 视角列出 `review_status=="scoring_ready"` 且各条件不满足时为 blocking；§4.H 以 "scoring_ready preconditions" 视角列出相同 7 条前置条件
- **反例/失败场景**: Implementation agent 对同一 violation（如 `review_status=scoring_ready` + `corpus_id=ad_hoc`）同时触发 `RQV_SCORING_READY_PRECONDITION`（来自 §4.H）和 `RQV_FAIL_CLOSED_SOURCE`（来自 §4.C），导致 `summary.error_code_counts` 重复计数
- **为什么有问题**: 同一语义规则出现两次且绑定不同 error code 表面暗示，implementation agent 无法确定应归属哪个 error code
- **直接证据**:
  - §4.C L193: `review_status=="scoring_ready"` 且 `corpus_id=="ad_hoc"`：blocking
  - §4.H L261: 非 `ad_hoc` corpus
  - §5 error code 表 L299: `RQV_SCORING_READY_PRECONDITION` vs `RQV_FAIL_CLOSED_SOURCE` 没有明确排他关系
  - 代码事实: `report_evidence.py::_is_scoring_ready` L2118 检查 `context.corpus_id != "ad_hoc"`，只在一处实现
- **影响**: Implementation agent 生成重复 issue 导致 summary 不可靠；或因不确定归属而延迟实现
- **建议改法和验证点**: 在 §4.C 规则 2-8 前增加注释："以下 scoring_ready invalid combinations 由 §4.H scoring_ready preconditions 统一覆盖，implementation 只需实现一次，error code 统一使用 `RQV_SCORING_READY_PRECONDITION`。" 或将 §4.C 规则 2-8 合并到 §4.H
- **修复风险**: 低 — 纯文档调整，不影响规则语义
- **严重程度**: 中

### F2-未修复-中-§4.H scoring_ready 前置条件缺少 fact review_status 检查

- **位置**: §4.H L257-272
- **问题类型**: 规则集合不完整
- **当前写法**: §4.H 列出 10 条 scoring_ready 前置条件，未包含"所有 facts 的 `review_status` 应为 `reviewed`"
- **反例/失败场景**: 手工构造 JSONL bundle，声明 `review_status="scoring_ready"`，但 individual facts 的 `review_status="not_reviewed"`；validator 不报告任何 issue
- **为什么有问题**: 现有代码 `report_evidence.py::_is_scoring_ready` L2123 要求 `context.fact_review_status == "reviewed"`，所有投影出的事实都会携带该状态。Validator 作为序列化内容的最后一道防线，应能检测此不一致
- **直接证据**:
  - `report_evidence.py::_is_scoring_ready` L2123: `context.fact_review_status == "reviewed"`
  - `ReportFact` dataclass L404: `review_status: FactReviewStatus`
  - `FactReviewStatus = Literal["not_reviewed", "partially_reviewed", "reviewed"]` L168
- **影响**: 非投影生成的 JSONL（手工构造、跨系统导入、未来序列化格式变更）可能漏过此检查；residual risk 中等但实际概率低
- **建议改法和验证点**: 在 §4.H 增加：`11. 所有 facts 的 review_status=="reviewed"；存在 not_reviewed 或 partially_reviewed 事实时，scoring_ready 声明与内容矛盾，blocking。` 在测试计划负例矩阵补充对应 case
- **修复风险**: 低 — 增加一条规则和对应测试，不改变现有规则
- **严重程度**: 中

### F3-未修复-低-N/A + chapter_summary 语义规则交叉覆盖

- **位置**: §4.C 规则 14-15 (L205-206), §4.E 规则 4 (L240), §4.F 规则 1 (L245)
- **问题类型**: 规则冗余
- **当前写法**: 同一非法组合 (`dimension==chapter_summary, status!=skipped`) 被 §4.C 规则 14（`status=="skipped"` 且 `dimension!="chapter_summary"` → blocking）、§4.C 规则 15（`dimension=="chapter_summary"` 且 `status!="skipped"` → blocking）、§4.E 规则 4（N/A 不应出现在 chapter_summary）、§4.F 规则 1（chapter_summary 必须用 skipped）四条规则覆盖
- **反例/失败场景**: Implementation agent 对同一 `dimension=chapter_summary, status=N/A` violation 输出 `RQV_CHAPTER_SUMMARY_SEMANTICS`（来自 §4.F）和 `RQV_NA_SEMANTICS`（来自 §4.E）两条 issue
- **为什么有问题**: 冗余 issue 输出增加 summary 噪音；不矛盾但不精确
- **直接证据**:
  - `report_evidence.py::_validate_score_issue_links` L1991-1994 已实现等效检查（单次输出）
  - Plan §4.C L205-206 与 §4.F L245 语义等价
- **影响**: 低 — summary 多计数不影响 fail-closed 判断，但增加调用方过滤负担
- **建议改法和验证点**: 在 §4.F 增加："chapter_summary 的 status 唯一性由本节规则覆盖，§4.C 规则 14-15 不再重复检查。" 或明确指定合并到单一 error code
- **修复风险**: 低
- **严重程度**: 低

---

## 3. Open Questions

无阻断 implementation 的 open question。

唯一需 controller 裁决的已由 plan §9 "Blocking Open Questions" 正确识别：implementation gate 是否允许按 AGENTS.md 同步 `fund_agent/fund/README.md` 的模块导读。该问题不阻断 plan 的 code-generation-readiness。

---

## 4. Residual Risks

| # | Risk | Severity | Owner / next gate | Mitigation in plan |
|---|------|----------|-------------------|-------------------|
| R1 | `report_evidence.py` Literal domain 后续扩展（新增 enum 值）时，validator 的 `get_args()` helper 需同步更新；Union 类型如 `ClassifiedFundType = FundType \| Literal["unknown"]` 需特殊展平逻辑 | 低 | implementation + future domain extension | Plan §4.B L186-187 建议用 `get_args()` + helper；实现时需处理 Union 展平 |
| R2 | `nav_data` 后续 source-contract slice 可能引入新 fact category / anchor kind，影响 validator enum allowlist | 低 | future `nav_data` source-contract slice | Plan §8 L421-423 已声明 residual owner |
| R3 | 未来 Host/Agent/dayu 接入可能改变 bundle 序列化格式（如嵌套结构、id 命名空间），影响 validator 的 Mapping 导航逻辑 | 低 | future Host/Agent gate | Plan §8 L429-432 已声明 residual owner |
| R4 | `_is_blocking_gap` 定义（`gap_kind != "not_applicable" and failure_category != "not_applicable"`）未在 plan 中显式内联；implementation agent 需从 `report_evidence.py` L2131-2144 读取 | 低 | implementation | Plan §9 step 4 要求导入 typed domain；实际 risk 低但不够自包含 |
| R5 | §4.G 规则 5 `fallback_allowed` 一致性检查依赖 `ReportSourceDocument` 字段，但 JSONL 输入可能省略此字段；validator 需处理缺失时的默认行为 | 低 | implementation | Plan §4.A conditional required 已覆盖显式缺失 |

---

## 5. Architecture Boundary Review

| Boundary | Plan compliance | Evidence |
|----------|----------------|----------|
| 不改 FQ0-FQ6 | PASS | §1 L26-27 non-goal; §2 L65 不建议修改; `quality_gate.py` 不在文件范围 |
| 不改 renderer / Service / CLI | PASS | §1 L28 non-goal; §2 L66 不建议修改 |
| 不引入 Host/Agent/dayu | PASS | §1 L30 non-goal; §7 L412 boundary check #4 |
| 不创建 parallel schema | PASS | §3 L84 显式禁止; API design 复用 typed domain |
| 不读 PDF/cache/source | PASS | §1 L36 non-goal; §7 L408-410 boundary checks #1-3 |
| 不投影 nav_data | PASS | §1 L32 non-goal; §7 L415 boundary check #8 |
| 不创建 durable fixture | PASS | §1 L34 non-goal; §7 L416 boundary check #9 |
| 不用 extra_payload/kwargs | PASS | §1 L38 non-goal; §3 L144 API 设计显式参数; §7 L413 boundary check #5 |

---

## 6. Best-Practice Review

- **Testability**: PASS — 全部使用本地 fake dict / dataclass，无外部依赖；15 个核心测试 + 负例矩阵覆盖关键路径
- **Observability**: PASS — `ReportQualityValidationResult` 包含 structured issues + summary + error_code_counts + record_pointer
- **Failure handling**: PASS — fail-closed by design；`blocking` issue → `failed_closed=True`；JSONL parse error → `RQV_JSONL_INVALID`
- **Overengineering**: 未发现 — validator 是纯函数，无 builder/wrapper/protocol/migration 等过度抽象
- **Overcoupling**: 未发现 — 只依赖 `report_evidence.py` typed domain + 标准库；不与 extraction/score/gate 耦合

---

## 7. Conclusion

**PASS_WITH_FINDINGS**

Plan 符合第一性原理（先验证评分输入、不接 CLI/Service）、正确复用 typed domain、保持 FQ0-FQ6 不变、正确禁止所有规定禁止项。规则集合可实现、无互相矛盾。

2 个中等 finding（scoring_ready 前置条件重复定义 F1、缺少 fact review_status 检查 F2）和 1 个低 finding（N/A + chapter_summary 冗余 F3）均可在 implementation 前或 implementation 过程中低风险修复，不阻断 code-generation-ready 判断。

Plan 可以交给 implementation agent，建议 implementation agent 进入时优先处理 F1 和 F2。

---

## 8. Reviewer Self-Check

- [x] Reviewed target, scope, truth sources, assumptions tested — written in §1
- [x] Findings are evidence-based, adversarial, actionable — each finding cites plan line numbers and code facts
- [x] Open questions and residual risks separated from findings — §3 and §4
- [x] Conclusion is `PASS_WITH_FINDINGS` — §7
- [x] Output path matches required format — `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-review-glm-20260525.md`
