# Plan Re-Review: report-quality scoring JSONL content validation plan

> **Reviewer**: AgentGLM
> **Date**: 2026-05-25
> **Reviewed artifact**: `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-20260525.md` (patched)
> **Prior review**: `docs/reviews/release-maintenance-report-quality-scoring-jsonl-content-validation-plan-review-glm-20260525.md`
> **Review posture**: Verify patch against prior findings; assess new areas called out by re-review brief; no fishing expedition

---

## 1. Prior Findings Disposition

### F1 (中) — §4.C 与 §4.H scoring_ready 前置条件重复定义

**CLOSED**

Patch evidence:
- §4.C L194: "所有 `review_status=="scoring_ready"` 的前置条件只在 §4.H 实现一次；§4.C 不重复列出 C2-C8。任何 scoring_ready 前置条件违反都统一输出 `RQV_SCORING_READY_PRECONDITION/blocking`，避免同一语义被重复计入 summary。"
- §4.H L259: "本节是 `scoring_ready` 前置条件的唯一 canonical implementation location；implementation 不应在 §4.C 另行实现重复规则。所有 `scoring_ready` 前置条件违反统一输出 `RQV_SCORING_READY_PRECONDITION/blocking`。"
- §4.C original rules 2-8 removed, replaced by single canonical delegation statement.

Verdict: Plan now provides unambiguous canonical location + error code. Implementation agent has no room for duplicate issue emission on scoring_ready violations.

### F2 (中) — §4.H 缺少 fact review_status 检查

**CLOSED**

Patch evidence:
- §4.H L273: "11. 所有 facts 的 `review_status=="reviewed"`；存在 `not_reviewed` 或 `partially_reviewed` fact 时，bundle-level `scoring_ready` 声明与内容矛盾，blocking。"
- 负例矩阵 L380: `review_status=scoring_ready`, any fact `review_status=not_reviewed` or `partially_reviewed` → `RQV_SCORING_READY_PRECONDITION/blocking`
- 测试 7 L355: test name 明确包含 `unreviewed_facts`

Verdict: scoring_ready precondition 现在覆盖 fact review_status，与代码事实 `report_evidence.py::_is_scoring_ready` L2123 (`context.fact_review_status == "reviewed"`) 对齐。

### F3 (低) — N/A + chapter_summary 语义规则交叉覆盖

**CLOSED**

Patch evidence:
- §4.E L238: "若同一 record 同时违反 N/A 与 chapter_summary 唯一性，implementation 应只输出一条 canonical issue，优先使用 `RQV_CHAPTER_SUMMARY_SEMANTICS`，避免 summary counts 重复。"
- §4.F L246: "`chapter_summary` status 唯一性由本节作为 canonical location；同一 `dimension/status` 语义错误不得同时输出 `RQV_CHAPTER_SUMMARY_SEMANTICS` 和 `RQV_NA_SEMANTICS`。"
- 负例矩阵 L389: `dimension=chapter_summary`, `status=N/A` → "one canonical `RQV_CHAPTER_SUMMARY_SEMANTICS/blocking`, no duplicate `RQV_NA_SEMANTICS`"

Verdict: Canonical location 声明 + 优先级规则 + 负例矩阵三重保障。Implementation agent 可以无歧义地只输出一条 issue。

---

## 2. Re-Review Focus Areas

### fallback_allowed / fallback_used / source_failure_category 一致性

**PASS**

Patch 新增/强化了 §4.C rules 3-4 (L195-196) 和 §4.G rules 5-6 (L254-255)，形成完整 fallback 一致性规则链：

| Rule | Location | What | Error code |
|------|----------|------|------------|
| fallback_allowed 必须与 source_failure_category 一致 | §4.C L195, §4.G L254 | 仅 not_found/unavailable → True | RQV_FALLBACK_CONFLICT/blocking |
| fallback_used=True 必须 fallback_allowed=True | §4.C L196, §4.G L256 | 层级约束 | RQV_FALLBACK_CONFLICT/blocking |
| fallback_used=True + fail-closed failure | §4.C L197 | schema_drift/identity_mismatch/integrity_error | RQV_FAIL_CLOSED_SOURCE/blocking |
| fallback_used=True + failure_category=none | §4.C L198 | 矛盾 | RQV_FALLBACK_CONFLICT/blocking |
| not_found/unavailable 允许 fallback 但须记录完整 | §4.G L253 | fallback_used=True + 原始 category 缺失 | material |

负例矩阵 L383-384 覆盖了 `fallback_allowed=True + failure_category=none` 和 `fallback_used=True + fallback_allowed=False` 两个关键组合。

与代码事实对齐：`report_evidence.py::_build_source_document` L1056 (`fallback_allowed=context.source_failure_category in _FALLBACK_ALLOWED_SOURCE_FAILURES`) 和 `_validate_projection_context` L964-966 一致。

**Note**: §4.C L195-196 与 §4.G L254-256 存在语义重复（同一条规则出现在两处），但 error code 统一为 `RQV_FALLBACK_CONFLICT`，重复检查不会产生不同 code 的 issue。这与 F1 的模式类似但后果更轻。作为 residual 记录，不升级为 finding。

### N/A severity 明确性

**PASS**

旧版: "minor 或 material，推荐 minor" — 不确定。
新版: §4.C L204 "material" + §4.E L236 "RQV_NA_SEMANTICS/material" — canonical severity 为 `material`。

负例矩阵 L387 覆盖 `status=N/A with severity=minor` → `RQV_NA_SEMANTICS/material`。

Implementation agent 不再有歧义。

### 嵌套 enum 负例测试

**PASS**

旧版: test 4 仅写 "test_invalid_enum_value_is_blocking"，未指定嵌套路径。
新版: §6 test 4 L352 "必须覆盖嵌套 enum，例如 `source_documents[0].source_boundary="invalid_value"` 输出 `RQV_ENUM_INVALID/blocking`。"

负例矩阵 L385: `source_documents[0].source_boundary=invalid_value` → `RQV_ENUM_INVALID/blocking`。

Implementation agent 有了具体的嵌套路径示例。

### 双向 / id reference 完整性（含 anchor.document_id）

**PASS**

旧版 §4.D 有 10 条规则，新版有 11 条：

- **新增** L227: "evidence anchor `document_id` 非空时必须存在于 `document_ids`；缺失为 material，若 bundle 声明 `scoring_ready` 则 blocking。"
- 新增测试 18 L367: `test_anchor_document_id_must_exist_in_source_documents`
- 负例矩阵 L392: `evidence anchor document_id=doc:missing` → `RQV_REF_MISSING/material or blocking if scoring_ready`

与代码事实对齐：`ReportEvidenceAnchor` L329 (`document_id: str | None = None`)，`project_report_evidence.py::_normalize_anchor_projection` L1344 只在 `source_kind == "annual_report"` 时设置 document_id。Validator 检查非空 anchor 的 document_id 存在性是合理的。

### preferred_lens.chapters 必填字段

**PASS**

新增 §4.A 条件必填 6 (L179): "preferred_lens.chapters[] 每条记录必须包含 chapter_id、lens_key、used_default、primary_focus；缺失为 material，若 bundle 声明 scoring_ready 则 blocking。"

新增测试 17 L366: `test_preferred_lens_chapter_required_fields_are_validated`
负例矩阵 L395: `preferred_lens.chapters[0] missing primary_focus` → `RQV_FIELD_MISSING/material or blocking if scoring_ready`

与代码事实对齐：`ReportPreferredLensChapter` L506-525 四个必填字段 (`chapter_id`, `lens_key`, `used_default`, `primary_focus`) 均无默认值。

### scoring_ready canonical 规则位置 + 重复 issue 避免

**PASS**

已通过 F1 closure 验证。§4.H L259 明确声明 canonical location，§4.C L194 明确不重复。所有 scoring_ready 前置条件统一 error code `RQV_SCORING_READY_PRECONDITION`。

---

## 3. New Findings

### F4-未修复-低-§4.C 与 §4.G fallback 一致性规则语义重复

- **位置**: §4.C L195-196, §4.G L254-256
- **问题类型**: 规则冗余（与已修复 F1 同模式）
- **当前写法**: §4.C rule 3 (fallback_allowed vs source_failure_category) 与 §4.G rule 5 语义相同；§4.C rule 4 (fallback_used → fallback_allowed) 与 §4.G rule 6 语义相同
- **反例/失败场景**: Implementation agent 在两处各实现一次检查，同一 `fallback_allowed=True + failure_category=none` violation 输出两条相同 error code 的 issue，导致 summary `error_code_counts` 中 `RQV_FALLBACK_CONFLICT` 被计数两次
- **为什么有问题**: F1 已通过 canonical location 声明解决，但 fallback 规则缺乏同等机制
- **直接证据**:
  - §4.C L195: "source_documents[].fallback_allowed 必须与 source_documents[].source_failure_category 一致"
  - §4.G L254: "ReportSourceDocument.fallback_allowed 必须与 failure category 一致" — 语义等价
  - §4.H L259 提供了 scoring_ready 的 canonical location 声明，但 fallback 规则无同等声明
- **影响**: 低 — error code 统一为 `RQV_FALLBACK_CONFLICT`，重复计数不影响 fail-closed 判断，但增加 summary 噪音
- **建议改法和验证点**: 在 §4.C 或 §4.G 增加 canonical location 声明（例如 "§4.G 是 fallback 一致性规则的 canonical location；§4.C 不重复实现"），或合并到一处
- **修复风险**: 低
- **严重程度**: 低

---

## 4. Residual Risks

| # | Risk | Change from prior review |
|---|------|-------------------------|
| R1 | Literal domain 后续扩展时 validator helper 需同步更新 | 不变 |
| R2 | nav_data 后续 source-contract 可能引入新 fact category | 不变 |
| R3 | Host/Agent/dayu 接入可能改变序列化格式 | 不变 |
| R4 | `_is_blocking_gap` 定义未在 plan 中显式内联 | 不变 — implementation agent 仍需从 `report_evidence.py` L2131-2144 读取 |
| R5 | `ClassifiedFundType = FundType \| Literal["unknown"]` Union 展平需特殊处理 | 不变 |

---

## 5. Conclusion

**PASS**

所有 3 个 prior findings（F1 中、F2 中、F3 低）均已在 patch 中完整关闭：

- F1: scoring_ready canonical location + 统一 error code + §4.C 不重复声明 ✓
- F2: 新增 §4.H 条件 11 fact review_status + 负例矩阵 + 测试名称 ✓
- F3: §4.E/§4.F canonical location + 优先级规则 + 负例矩阵去重验证 ✓

新发现 F4（低）是 F1 同模式的 fallback 规则冗余，severity 为低且 error code 统一，不阻断 implementation。

Plan 现在 code-generation-ready。

---

## 6. Reviewer Self-Check

- [x] All prior findings dispositioned (3/3 closed)
- [x] Re-review focus areas from brief covered (6/6)
- [x] New finding is evidence-based and adversarial
- [x] Conclusion reflects actual finding severity
- [x] Output path matches required format
