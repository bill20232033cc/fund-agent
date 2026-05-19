# P4 计划审核报告

> **日期**: 2026-05-19
> **审核对象**: `post-mvp-p4-first-principles-plan.md`
> **审核基准**: `docs/design.md`、`docs/implementation-control.md`、仓库实际代码

---

## 一、核心理念评价

**结论：✅ 完全赞同**

P4 的核心理念"先建立质量闭环，再扩功能"是正确的。从第一性原理出发：

| 问题 | P4 的回答 | 评价 |
|------|----------|------|
| 当前系统能生成报告，但报告可靠吗？ | 不知道 → 先建立量化评估 | ✅ 正确 |
| 基金类型误判会导致什么？ | 后续全链路错误 → 先修复分类器 | ✅ 正确 |
| 形式合格但内容低质量的报告怎么办？ | 建立质量阻断机制 | ✅ 正确 |

**关键洞察**："把项目从'能生成报告'推进到'知道报告哪里可靠、哪里不可靠，并能持续变好'"——这是 MVP 后最重要的方向。

---

## 二、Step 1-6 逐项审核

| Step | 评价 | 意见/建议 |
|------|------|---------|
| **Step 1** 冻结精选基金池 | ✅ 合理 | `016492` 重复问题：建议选项 B（P4-S1 允许重复但标红），不阻塞进度 |
| **Step 2** 建立 extraction snapshot | ✅ 合理 | snapshot 字段设计完整，建议增加 `extraction_timestamp` 和 `extractor_version` 用于跨版本对比 |
| **Step 3** 定义字段级评分规则 | ✅ 合理 | P0/P1/P2 分层合理。建议 gate 阈值可配置化（放入 `config/settings.py`） |
| **Step 4** 建立 golden set | ✅ 合理 | 6 只覆盖主要类别合理。建议明确 6 只具体代码，避免后续反复确认 |
| **Step 5** 修复高影响 bug | ✅ 合理 | 优先级排序正确：基金类型误判 > 表格抽取 > 质量阻断 |
| **Step 6** 升级报告审计 | ✅ 合理 | FQ1-FQ5 规则设计合理。建议增加 FQ6：同一基金跨 run 的 snapshot diff 超过阈值 |

---

## 三、Open Questions 回答建议

| 问题 | 建议回答 | 理由 |
|------|---------|------|
| `016492` 重复如何处理？ | **选项 B**：P4-S1 允许重复，summary 中标红 | 不阻塞进度，后续人工确认后修正 |
| 第一批 golden set 选哪些？ | **建议 6 只**：004393（国内股票）、110011（指数）、000001（债券）、519772（海外股票）、000322（海外债券）、159915（黄金） | 覆盖主要类别，包含已知 failure case |
| 货币基金是否纳入？ | **不纳入 P4-S1** | 当前模板不适配，作为 edge case 后续处理 |
| 是否要求真实 network/PDF 全量运行？ | **不要求** | 先支持指定代码和分层抽样，稳定后扩大 |

---

## 四、与现有实施总控文档的关系

**问题**：P4 计划与 `implementation-control.md` 的关系未明确。

**建议**：
1. P4 应作为新的 Phase 追加到 `implementation-control.md`
2. 或创建独立的 `docs/implementation-control-p4.md`（推荐，避免主文档膨胀）

### P4 任务切片建议

| Slice | 任务 | 对应 P4 计划 | 验收条件 |
|-------|------|-------------|---------|
| P4-S1 | Selected Fund Extraction Snapshot + Quality Gate MVP | Step 1-2 | 能对 6 只 golden set 基金生成 snapshot，输出 summary.md |
| P4-S2 | 定义字段级评分规则 + 建立 golden set | Step 3-4 | P0 字段 coverage >= 90%，traceability >= 90% |
| P4-S3 | 修复基金类型误判 + 扩展表格抽取 | Step 5 | `004393` 不再被识别为 `index_fund` |
| P4-S4 | 升级报告审计（FQ1-FQ5）+ 质量阻断 CLI | Step 6 | 低质量输入可被质量 gate 识别并阻断 |

---

## 五、补充建议

### 5.1 建议增加的产出物

| 产出物 | 用途 | 优先级 |
|--------|------|--------|
| `scripts/extraction_snapshot.py` | 生成 snapshot 的 CLI 工具 | 🔴 高 |
| `scripts/quality_score.py` | 计算 coverage/traceability/correctness | 🔴 高 |
| `docs/golden-set-definition.md` | Golden set 字段定义和标注规则 | 🟡 中 |
| `tests/fund/golden/` | Golden answer JSON 文件 | 🟡 中 |

### 5.2 建议增加的验收条件

- P4-S1 验收：能对 6 只 golden set 基金生成 snapshot，输出 summary.md
- P4-S2 验收：P0 字段 coverage >= 90%，traceability >= 90%
- P4-S3 验收：`004393` 不再被识别为 `index_fund`
- P4-S4 验收：低质量输入可被质量 gate 识别并阻断

### 5.3 与 Dayu-Agent 对齐的补充

P4 计划第5节提到与 Dayu-Agent 对齐，建议补充：

- Dayu-Agent 的 `snapshot` 机制是离线处理产物，本项目应同样设计为**可离线运行**（不依赖网络/PDF）
- Dayu-Agent 的 `score` 是 CI gate 的一部分，本项目应同样集成到 pytest 或 pre-commit

---

## 六、总结评分

| 维度 | 评价 |
|------|------|
| 方向正确性 | ⭐⭐⭐⭐⭐ 先质量后功能，完全正确 |
| 步骤完整性 | ⭐⭐⭐⭐☆ Step 1-6 完整，建议补充任务切片 |
| 可执行性 | ⭐⭐⭐⭐☆ 需要明确产出物和验收条件 |
| 与现有文档关系 | ⭐⭐⭐☆☆ 需要明确与 implementation-control.md 的关系 |

**结论**：P4 计划方向正确、步骤合理。建议：
1. 明确 6 只 golden set 具体代码
2. 补充任务切片定义（P4-S1 ~ P4-S4）
3. 更新或创建实施总控文档
4. 将 P4 计划保存为正式文档（`docs/implementation-control-p4.md`）
