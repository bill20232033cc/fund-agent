PLAN_REREVIEW_PASS

## Rereview Scope

Targeted re-review gate. Reviewed target: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-plan-20260620.md`（fixed plan artifact）。对比基线：`docs/reviews/plan-review-core-risk-source-truth-ds-20260620.md` 中的 F1–F7 finding。Scope: 仅确认 F1–F7 闭合并检查 fix 是否在相同 planning scope 内引入新 blocker。

## Assumptions Tested

1. 修复后的 plan 仍遵守 AGENTS.md 的模块边界、Gate 分类和禁止事项。
2. 修复后的 plan 与当前代码事实（`fund_disclosure_processor.py`, `data_extractor.py`）一致。
3. 所有 F1–F7 修正互相不矛盾，不引入新的跨族耦合、scope 漂移或契约缺失。

## F1–F7 Closure Verification

### F1 [CRITICAL] Slice 2 错误复用 product_essence selector → CLOSED

**原 finding**: Plan 要求 `core_risk.v1` 调用 `_select_product_essence_values()`，造成跨族耦合和计算浪费。

**修复后 plan**:
- 第 140 行：`Do not call _select_product_essence_values() from any core_risk.v1 code path.` — 显式禁止。
- 第 141–146 行：要求抽取三个族中立的共享 helper（`_collect_risk_characteristic_table_candidates`、`_collect_risk_characteristic_paragraph_candidates`、`_select_risk_characteristic_value`），product_essence 和 core_risk 共同调用。
- 第 147 行：`The neutral selector helpers must collect only output path risk_characteristic_text.risk_characteristic_text`。
- 第 149–152 行：`_select_core_risk_values()` call chain 只调用中立 helper，返回 `_RiskCharacteristicValueCandidate` 类型。

**裁决**: 已闭合。禁止措辞明确，共享 helper 签名和作用域已指定，product_essence 和 core_risk 通过族中立接口解耦。

---

### F2 [HIGH] Gate 名称与实现范围严重不匹配 → CLOSED

**原 finding**: Gate 标签 `core_risk.v1 Source-truth Direct Extraction` 暗示完整族提取，实际只做 1/5 role。

**修复后 plan**:
- 第 5 行：Gate 标签改为 `FundDisclosureDocument core_risk.v1 risk_characteristic_text Source-truth Direct Extraction Planning Gate`。
- 第 7–8 行：Mandatory scope statement 显式声明仅实现 risk_characteristic_text，四个 role 保持 deferred，完整 source truth 需后续独立 gate。

**裁决**: 已闭合。Gate 名称和 scope statement 精确传达实现范围。

---

### F3 [HIGH] Deferred candidate roles 无公开缺口语义 → CLOSED

**原 finding**: proof-positive 路径 `candidate_evidence=()` 导致四个 deferred role 完全不可见，消费者无法区分完整覆盖与部分覆盖。

**修复后 plan**:
- 第 77–82 行：新增 `Deferred role public gap semantics` 章节。要求 accepted direct 结果必须包含每个 deferred role 一个 `FundExtractionGap`，`gap_code="deferred_role"`、`required=False`。
- 第 78–81 行：显式列出四个 deferred role。
- 第 156 行：`_core_risk_source_truth_gaps()` 必须增加四个 `required=False` `deferred_role` gaps。
- 测试矩阵第 207–208 行：新增 test case `proof-positive accepted deferred gaps`。

**裁决**: 已闭合。Deferred role 缺口语义完整，消费者可通过 gaps 区分"只有 1/5 role"与"完整族"。

---

### F4 [MEDIUM] Facade fallback 死代码激活未显式承认 → CLOSED

**原 finding**: plan 未承认 `data_extractor.py:742-754` 的 fallback 路径是死代码首次激活。

**修复后 plan**:
- 第 177–179 行：Slice 4 增加声明：`This slice is the first activation verification for the existing data_extractor.py:742-754 core_risk.v1 -> risk_characteristic_text fallback path; before this work, the path is effectively dead code because core_risk.v1 cannot emit an accepted direct value.`

**裁决**: 已闭合。首次激活被显式承认，Slice 4 的 facade 测试定位为死代码激活验证。

---

### F5 [MEDIUM] `_select_core_risk_values()` 未充分指定 → CLOSED

**原 finding**: plan 列出函数名但不说明内部实现策略，存在三种歧义解读。

**修复后 plan**:
- 第 148–152 行：显式指定 call chain：只调用中立 risk-characteristic collection/selection helper，返回 `_RiskCharacteristicValueCandidate`，仅映射 `risk_characteristic_text.risk_characteristic_text` → `core_risk.v1` ambiguity。
- 第 141–146 行：三个中立 helper 已命名。

**裁决**: 已闭合。Call chain 充分指定，implementation agent 可直接按规格实现。

---

### F6 [LOW] 缺少 risk_characteristic_text 歧义路径测试 → CLOSED

**原 finding**: Test Matrix 缺少 core_risk 上下文中 risk_characteristic_text 歧义时的专项测试。

**修复后 plan**:
- 第 166 行：Slice 3 增加 `Ambiguous direct text` 测试描述。
- 测试矩阵第 209 行：增加 `proof-positive ambiguous risk-characteristic text → missing, empty value/anchors, ambiguous_table_or_locator, candidate_evidence == ()`。

**裁决**: 已闭合。Ambiguous path 的行为差异（单 output path 家族歧义 → overall missing）有显式测试覆盖。

---

### F7 [LOW] Forbidden files 遗漏 `docs/fund-analysis-template-draft.md` → CLOSED

**原 finding**: 模板真源文件未列入 forbidden 清单。

**修复后 plan**:
- 第 267 行：`docs/fund-analysis-template-draft.md` 列入 forbidden files。

**裁决**: 已闭合。

---

## New Blocker Check

对修复后 plan 做 adversarial scan，未发现新的 material blocker：

- **架构边界**：plan 不修改 contracts.py、不扩展 EvidenceSourceKind、不引入新 public schema、不穿透 Service/UI/Host/Agent 层。中立 helper 抽取在 `fund_disclosure_processor.py` 内部完成，不改变模块边界。
- **过度耦合**：中立 shared helper 的引入（第 141–154 行）是 F1 的修复结果，product_essence 和 core_risk 共享 selector/value-builder 但保持各自的 family ownership。两个 family 对共享 helper 的依赖是单向的（都依赖中立 helper），不引入双向耦合。
- **状态一致性**：binary `accepted | missing` status（第 58–62 行）的刻意简化已注明后续多 subvalue gate 需重写，当前 scope 内无风险。
- **contracts.py 不变**：`deferred_role` gap_code 已存在于 `contracts.py:43-62`（见 plan 第 36 行），不需要新增 gap code。
- **测试覆盖**：processor tests 覆盖 positive/missing/ambiguous/proof-missing/proof-invalid/candidate-boundary/candidate-suppression/forbidden-keys/non-interference（9 类 case）；facade tests 覆盖 fallback-only/product-wins/all-six-marker/candidate-only/first-activation（5 类 case）。
- **forbidden files**：第 262–270 行的 forbidden 清单完整，包含 contracts.py、data_extractor.py production code、template draft、documents、services/ui/host/agent、renderer、quality gate、LLM provider。

## Residual Suggestions Representation

原始 review 的三条 residual suggestions 在修复后 plan 的 Residual Risks 中均有对应：

| 原始 suggestion | Plan 对应位置 |
|---|---|
| 共享 helper 重构对 product_essence 的回退风险 | 第 279 行：`reviewers must verify product_essence risk_characteristic_text output is byte/shape-compatible with current tests before accepting core-risk behavior` |
| `_CORE_RISK_REQUIRED_TOP_LEVEL` 常量设计与二元 status | 第 275–276 行：`The status model is intentionally binary for this single-subvalue gate. Owner: later multi-subvalue core_risk.v1 gate must redesign _core_risk_status()` |
| Candidate boundary 路径下 deferred role 候选证据行为 | 第 279 行（candidate boundary 说明）+ 测试矩阵第 213–214 行（`including deferred role candidate evidence when matching source text exists`） |

## Conclusion

PLAN_REREVIEW_PASS — F1–F7 全部闭合，fix 未引入新 blocker。Plan 可进入 implementation gate。
