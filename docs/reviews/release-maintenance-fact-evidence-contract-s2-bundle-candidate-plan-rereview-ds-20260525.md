# Fact-Evidence Contract S2 Bundle Candidate Plan — Re-Review (AgentDS)

> Date: 2026-05-25
> Reviewer: AgentDS (planreview specialist)
> Gate: `fact-evidence-contract S2 bundle candidate planning`
> Original review: `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-review-ds-20260525.md`
> Patched plan: `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md`
> Conclusion: **PASS**

## Step Self-Check

- Role: independent re-reviewer. No file edits, no commits, no controller judgment.
- This is a targeted re-review: only original findings F-1 through F-8 and any newly introduced issues.
- Truth sources unchanged from original review.

## Finding Resolution

### F-1 (中) classified_fund_type 值域未明确枚举 → **已解决**

Plan 现在第 76 行有专门的 `classified_fund_type values` 段落：
- 完整值域已枚举：`index_fund`, `active_fund`, `bond_fund`, `enhanced_index`, `qdii_fund`, `fof_fund`, `unknown`
- 从 `StructuredFundDataBundle.basic_identity.value["classified_fund_type"]` 的投影路径已明确
- 缺失/非法值的归一化策略：设为 `unknown`，创建 `data_gap`（`missing_fact` 或 `type_slot_gap`），阻止 `scoring_ready`
- 明确禁止从基金名称或基准文本推断基金类型
- Slice 1 新增负向测试（行 402）：拒绝不在域内的 `classified_fund_type` 值
- Slice 3 新增负向测试（行 445）：`classified_fund_type="unknown"` 不能成为 `scoring_ready`

### F-2 (中) review_status 派生算法缺少优先级与冲突裁决 → **已解决**

Plan 现在第 237–247 行有完整的优先级与冲突裁决：
- 显式优先级链：`rejected > expired > deferred > scoring_ready > fact_prefill_reviewed > fact_prefill_generated > repository_verified > candidate`
- 合法递进路径与 S0 对齐（行 210–218）
- 转移语义表含必需的触发器/证据和参与者（行 222–229）
- 终态语义：`rejected`（不可恢复）、`expired`（已取代）、`deferred`（可恢复但未就绪）
- 3 个具体冲突示例（行 243–247）
- 新增 2 条非法组合（行 257–258）：`classified_fund_type="unknown"`、未解决的 `data_gap_refs`
- Slice 3 新增负向测试（行 444–446）

### F-3 (中) nav_data 到 facts 的投影规则结构断层 → **已解决**

Plan 现在第 119–121 行明确将 `nav_data` 排除出初始投影：
- 初始投影字段列表不再包含 `nav_data`（行 119）
- 专门段落解释原因：`NavDataResult` 不是 `ExtractedField`，缺少 `extraction_mode` 和 `EvidenceAnchor` 元组
- 推迟到后续 `nav_data` slice，届时定义安全映射规则
- Slice 2 新增负向测试（行 426）：`nav_data` 不出现在初始 `facts` 中

### F-4 (低) anchor_id 的 locator_hash 稳定性未定义 → **已解决**

Plan 现在第 277–289 行有完整的 hash 稳定性规范：
- 算法：sha256 前 8 位小写十六进制（行 277）
- 5 步归一化流程（行 281–287）：有序 JSON 对象、None→空字符串、strip/NFC/ASCII 空白折叠、排序键 UTF-8 无多余空格、sha256 hexdigest[:8]
- 冲突处理（行 289）：同前缀同 hash 时追加 `-2`、`-3`，按确定性排序，记录验证警告
- 测试要求：同输入稳定 hash + 确定性冲突后缀

### F-5 (低) source_boundary=external_official 边界 → **已解决**

Plan 现在第 89 行和第 97 行有明确约束：
- `external_official` 在 S2 仅为未来/元数据用途（行 89：`future/metadata only in S2`）
- 专门澄清段落（行 97）：仅是已接受官方参考的元数据，不是直接调用外部 API 的许可
- 任何未来官方来源必须先通过独立的 Repository 风格接口 gate
- `external_official` 记录不能通过临时网络调用创建，也不能单独使 bundle 成为 `scoring_ready`
- Slice 1 新增负向测试（行 404）：拒绝将 `external_official` 当作 S2 中直接 API 权限的来源边界

### F-6 (低) preferred_lens 格式与派生逻辑 → **已解决**

Plan 现在第 78 行有专门的 `preferred_lens` format 段落：
- 存储可序列化投影，而非活对象 `TemplateLensRule`
- 最小形状已指定：`{"fund_type": classified_fund_type, "chapters": [{"chapter_id": "chapter_0", "lens_key": "active_fund", "used_default": false}, ...]}`
- 章节 ID 范围为 `chapter_0` 到 `chapter_7`
- 实现来源：现有 preferred_lens 解析器 / lens 应用计划
- `classified_fund_type="unknown"` 时 `preferred_lens` 必须为空或 blocked，bundle 不能成为 `scoring_ready`
- Slice 1 新增负向测试（行 403）

### F-7 (低) Slice 验证描述不足以防止假通过 → **已解决**

每个 Slice 现在包含具体的负向测试场景：
- **Slice 1**（行 402–404）：3 个负向测试——非法 `classified_fund_type`、unknown 类型的 `preferred_lens`、`external_official` 直接 API 滥用
- **Slice 2**（行 424–426）：3 个负向测试——missing 但 value 非 null、direct 但 anchors 为空、`nav_data` 排除
- **Slice 3**（行 444–446）：3 个负向测试——优先级冲突（`rejected` vs `deferred`）、`unknown` 类型 scoring_ready、`accepted_baseline` 越权
- **Slice 4**（行 462–463）：2 个负向测试——断裂的 score issue 链接、pass 与 blocking `data_gap_refs` 冲突
- **Slice 5**（行 478）：1 个负向测试——有经理声明锚点但无 turnover 证据的流程稳定性声明

共新增 12 个具体负向测试场景，覆盖了原始审查标记的关键边界。

### F-8 (低) corpus_id 格式与 S0 证据链接 → **已解决**

Plan 现在第 59 行和第 74 行有完整规范：
- 格式：`corpus:{corpus_name}:{version}`（对齐其他 id 的命名空间前缀约定）
- 示例：`corpus:rqb_s0:20260525`
- `corpus_name`：来自已接受审查 artifact 的稳定 snake_case 名称
- `version`：日期或已审查的修订 id
- `ad_hoc` 仅允许用于非 baseline 本地检查
- baseline `corpus_id` 必须通过显式审查引用链接到 S0/S1 审查 artifact

## 新增内容检查

| 新增内容 | 评估 |
|---------|------|
| 多锚点映射规则（行 123） | 合理。一个 `ExtractedField` 正常映射为一个 `ReportFact`，所有锚点均保留；仅当字段值包含独立子字段时才拆分。拆分时不得丢弃锚点。 |
| 转移语义表（行 222–229） | 合理。5 个转移各含必需的触发器/证据和参与者，与 S0 已接受转移对齐。 |
| 终态定义（行 231–235） | 合理。`rejected`（不可恢复）、`expired`（已取代）、`deferred`（可恢复）的语义清晰。 |
| 合法递进路径（行 210–218） | 合理。与原始 `candidate → repository_verified → ... → accepted_baseline` 序列对齐。 |
| 新增非法组合（行 257–258） | 合理但 `type_slot_membership_status` 的完整值域未在本文档中定义——参见下方开放问题。 |
| Turnover 约束标记为已接受（行 375–382） | 合理。显式注明基于 S1 dry-run controller judgment 的出处。 |

## 未改变的内容

以下原始审查中的项目不在补丁范围或有意保持开放：

1. **`type_slot_membership_status` 完整值域**：非法组合（行 254）引用了 `matches_slot`，但未定义完整的 status 枚举。这是 S1 schema 的遗留——S1 controller judgment 接受了文档身份/类型 slot 拆分，但将可执行的值域验证推迟到 S2/后续实施。不是补丁引入的新问题。

2. **Bundle 不可变性合约**：原始审查开放问题 #1——`ReportEvidenceBundle` 是否应为 `frozen=True`（如 `StructuredFundDataBundle`）？计划仍未明确说明。实施 gate 应决定。

3. **章节引用向前兼容性**：原始审查开放问题 #3——当未来 0–10 章节映射实施时，当前 `chapter_0` 到 `chapter_7` 引用如何迁移？计划将 `chapter_ids` 范围限定为 `chapter_0` 到 `chapter_7`，并注明"Current v0 chapters only until separate renderer gate"（行 172），这已足够。

## 验证命令

```text
# 确认补丁保留了原始自检关键词
rg -n "ReportEvidenceBundle|StructuredFundDataBundle|FundDocumentRepository|extra_payload|dayu\.host|dayu\.engine|chapter_contract|turnover|data_gap_refs|no code implementation" docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md | wc -l

# 确认新增规范存在
rg -n "classified_fund_type values|preferred_lens format|locator_hash normalization|review_status priority|external_official boundary clarification|nav_data projection is explicitly excluded|corpus_id format" docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md

# 确认负向测试存在
rg -n "Negative tests" docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md

# 无空白字符问题
git diff --check
```

结果：全部通过。

- 关键词出现次数：原始计划中 40+ 次（与补丁前一致）
- 7 个新增规范章节全部通过 `rg` 确认存在
- 5 处 `Negative tests` 出现（每个 Slice 1 处）
- `git diff --check` 无错误

## 审查者自检

- [x] 所有 8 个原始 findings 均已逐项检查，结论明确
- [x] 新增内容已检查，未引入结构性阻断项
- [x] 未改变的开放项目已注明并评估严重程度
- [x] 结论为 `PASS`

## 结论

**PASS**

全部 8 个原始 findings 均已解决：

- 3 个中等 findings（F-1 类型域、F-2 状态优先级、F-3 nav_data 断层）——已通过显式值域枚举、优先级链含冲突示例、以及 `nav_data` 显式排除得到解决
- 5 个低等 findings（F-4 hash 稳定性、F-5 external_official 边界、F-6 preferred_lens 格式、F-7 测试具体性、F-8 corpus_id 格式）——已通过完整算法规范、边界澄清、显式形状定义以及 12 个新增负向测试场景得到解决

补丁未引入新的阻断项。`type_slot_membership_status` 完整值域和 bundle 不可变性合约为可推迟到实施 gate 的开放项目，并非计划级阻断项。

计划的 5 个实施 Slice 现在对实施 Agent 来说已具备足够的规范性和可测试性，可以进入 typed model/projection implementation plan review，无需重新设计。
