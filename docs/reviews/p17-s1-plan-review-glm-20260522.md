# P17-S1 Plan Review — GLM（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

本计划代码生成就绪。设计边界完整、范围自洽、代码事实准确。发现 5 项非阻塞发现，无一项阻断计划接受。实施 Agent 可在实施中就地消解所有发现，无需修订计划后重新送审。

---

## Design-Boundary Checklist

对照 `docs/design.md` §11，逐项评估：

| 检查项 | 结果 | 说明 |
|--------|------|------|
| §1.3 非目标 | **PASS** | 未引入全市场比较、实时行为检测、自建温度计、组合管理、买卖建议或外部 Dayu 运行时 |
| UI / Service / Capability / Runtime / Engine 边界 | **PASS** | 实施仅限 `performance.py` + 聚焦测试；未触碰 UI、Service、Runtime、Engine、renderer、quality gate、来源编排 |
| 生产年报访问仍通过 `FundDocumentRepository` / `FundDataExtractor` | **PASS** | 抽取器仅消费 `ParsedAnnualReport` 输入；未直接调用 PDF cache、source adapter 或 download helper |
| 未引入外部 Dayu runtime、LLM 写作、Evidence Confirm、计算型 tracking error、外部指数适配器、`extra_payload` 隐式参数 | **PASS** | Non-goals 和 Stop Conditions 明确禁止以上全部 |
| Success signals 可验证且不激励缺少直接证据时错误接受 | **PASS** | 测试矩阵断言 direct-disclosure 语义与 blocker note；blocker 优先级将不安全匹配排在通用缺失之上 |

计划自身的 Design-Boundary Checklist 与上述逐项评估一致，无遗漏或矛盾。

---

## Extractor 正确性审查

### 代码事实核验

| 计划声称 | 代码实际 | 验证结果 |
|----------|----------|----------|
| `performance.py:344-398` 是顶层跟踪误差抽取器 | `_extract_tracking_error` 起始行 344 | ✅ |
| `performance.py:357-358` 广义早期返回 | `if _has_ambiguous_tracking_error_text(report): return _missing_tracking_error("tracking_error_ambiguous")` 行 357-358 | ✅ |
| `performance.py:357-364` 两处复用 `"tracking_error_ambiguous"` | 行 358（广义预检）与行 364（table/text 不一致经 `_select_consistent_tracking_error_match` 返回 `None`）均使用同一 note | ✅ |
| `performance.py:494-496` 第二处早期返回 | `if _has_actual_tracking_error_signal(normalized_line): return None` 在行 495-496 | ✅ |
| `performance.py:427-469` 多匹配静默返回 `None` | `if len(matches) > 1: return None` 在行 465-466 | ✅ |
| `performance.py:472-514` 文本多匹配静默返回 `None` | `if len(matches) > 1: return None` 在行 510-511 | ✅ |
| `performance.py:587-601` 所有目标/控制关键词归为一类 | `_tracking_error_context_is_target_or_ambiguous` 对全部 9 个负向关键词返回同一布尔值 | ✅ |
| `performance.py:545-564` 排除含 `标准差` 的表头 | `_find_tracking_error_header_index` 行 560 跳过含 `标准差` 的 header | ✅ |
| `data_extractor.py:224-249` 非指数类型获得 missing note | `_tracking_error_for_fund_type` 行 243-248 对非适用类型返回 `extraction_mode="missing"` | ✅ |
| `models.py:37-51` missing-path 通过 `value=None` + `extraction_mode="missing"` + `note` 表达 | `ExtractedField` 泛型允许 `value=None`；`_missing_tracking_error` 构造器使用此模式 | ✅ |
| `models.py:133-170` `source_type`/`calculation_method` 仅在成功路径出现 | `TrackingErrorValue` 要求 `value: Decimal` 非 `None`；missing 路径构造 `ExtractedField(value=None)` 不实例化 `TrackingErrorValue` | ✅ |

所有代码事实均与实际代码一致。

### Note 分裂审查

当前代码仅使用 3 种 note：
- `"tracking_error_ambiguous"`（广义预检 + table/text 不一致）
- `"tracking_error_unparseable"`（不可解析百分比）
- `"年报未直接披露跟踪误差"`（无匹配）

计划提出分裂为 10 种确定性 note。分裂逻辑正确：
- `tracking_error_mixed_actual_and_target`：当前被 `"tracking_error_ambiguous"` 吞没
- `tracking_error_table_text_inconsistent`：当前被 `"tracking_error_ambiguous"` 吞没
- `tracking_error_multi_match`：当前被静默 `None` → `"年报未直接披露跟踪误差"` 吞没
- `tracking_error_target_or_limit` / `tracking_error_manager_narrative` / `tracking_error_benchmark_only` / `tracking_error_standard_deviation_only`：新增语义粒度

### 双早期返回位置审查

**位置一（行 357-358）**：`_has_ambiguous_tracking_error_text(report)` 在任何 table/text 抽取之前扫描全文本。若 §3/§2 任一行同时含 TE 关键词 + 目标语义 + 实际信号，即触发全量返回。此路径的问题：
- 阻止了对后续可能的有效直接披露的扫描
- 将混合行与纯目标行归为同一 `"tracking_error_ambiguous"` note

计划 Slice 2 正确识别并提出替换为收集/分类，允许继续扫描。**修复方向正确。**

**位置二（行 494-496）**：`_extract_tracking_error_from_text` 内部 `return None`。当单行同时匹配目标上下文和实际信号时直接终止文本扫描。此路径的问题：
- 阻止了对后续行的扫描
- `None` 被调用方映射为 `"年报未直接披露跟踪误差"` 或在 table/text 组合路径中被 `tracking_error_ambiguous` 覆盖

计划 Slice 2 正确识别并提出替换为显式 blocker outcome 后继续扫描。**修复方向正确。**

### 多匹配处理审查

当前行为：`_extract_tracking_error_from_tables`（行 465-466）和 `_extract_tracking_error_from_text`（行 510-511）在 `len(matches) > 1` 时静默返回 `None`。`None` 最终被映射为通用缺失 note，丢失了"存在多个候选"这一诊断信息。

计划 Slice 3 提出 `tracking_error_multi_match` 显式 blocker。保守默认 fail-closed 正确。允许未来去重的 escape hatch 以 residual owner 形式记录。**处理恰当。**

### Blocker 优先级审查

计划提出 10 级优先级，从最不安全/最具体到最通用：

| 优先级 | Note | 风险 | 判定 |
|--------|------|------|------|
| 1 | `tracking_error_table_text_inconsistent` | 披露冲突，误选任一即错误 | 正确最高 |
| 2 | `tracking_error_multi_match` | 无法确定选择，误选风险高 | 正确第二 |
| 3 | `tracking_error_incomplete_anchor` | 无法构造证据锚点 | 正确 |
| 4 | `tracking_error_unparseable` | 有候选但值不可解析 | 正确 |
| 5 | `tracking_error_mixed_actual_and_target` | 混杂语义，可能非实际值 | 正确 |
| 6 | `tracking_error_target_or_limit` | 明确非实际值 | 正确 |
| 7 | `tracking_error_manager_narrative` | 叙事而非数据 | 正确 |
| 8 | `tracking_error_benchmark_only` | 基准相关而非 TE | 正确 |
| 9 | `tracking_error_standard_deviation_only` | 标准差而非 TE | 正确 |
| 10 | `年报未直接披露跟踪误差` | 无匹配 | 正确兜底 |

优先级排序逻辑一致：冲突 > 结构问题 > 语义歧义 > 通用缺失。**无问题。**

### Missing-path 一致性审查

计划要求缺失路径全部通过 `ExtractedField.note` + `extraction_mode="missing"` 表达，不要求 `source_type`/`calculation_method` 在缺失路径出现。对照 `models.py`：
- `ExtractedField[TrackingErrorValue]` 允许 `value=None`
- `_missing_tracking_error(note)` 构造 `value=None, anchors=(), extraction_mode="missing", note=note`
- `TrackingErrorValue` 要求 `value: Decimal` 非 `None`，不会在缺失路径被实例化

**一致，无问题。**

---

## 测试审查

### 测试矩阵充分性

计划提出约 13 项测试，覆盖：

| 类别 | 测试数 | 充分性 |
|------|--------|--------|
| Blocker note 精确断言 | 8-9 | 覆盖所有 10 种 note（incomplete_anchor 可标记为 residual） |
| 早期返回修复验证 | 2 | 覆盖两个早期返回位置（混合行后有效披露、目标行后有效披露） |
| 现有成功契约保持 | 3 | 覆盖文本直接披露、表格直接披露、table/text 一致双披露 |
| Edge case | 1-2 | 多匹配、unparseable |

测试方法合理：优先使用 inline `ParsedAnnualReport`/`ParsedTable` builder，仅在可读性显著提升时引入 fixture 文件。**充分。**

### 验证命令审查

计划提出 5 层验证：
1. 目标 extractor 测试
2. 全部 extractor 测试
3. 相邻 snapshot/score/quality 测试
4. ruff lint
5. `git diff --check HEAD`

若触碰共享模型则追加全量测试。**验证策略合理，覆盖渐进风险。**

---

## Findings

### F1（低）| 双扫描路径合并策略未明确

**Issue**：计划 Slice 2 提出"替换顶层 `_has_ambiguous_tracking_error_text` 为收集/分类"，但 `_extract_tracking_error_from_text` 仍独立扫描 §3/§2 同一文本。移除顶层早期返回后，两条扫描路径可能对同一行产生重复分类逻辑。

**Risk**：实施 Agent 可能保留两条独立扫描路径，增加维护负担和分类不一致风险。

**Required plan change**：无。建议实施 Agent 考虑移除 `_has_ambiguous_tracking_error_text`，将分类逻辑完全内化到 `_extract_tracking_error_from_text` 的丰富返回类型中。这不是计划修订要求，是实施优化建议。

### F2（低）| target-only `continue` 路径的分类方案隐含在行为表中

**Issue**：当前 `_extract_tracking_error_from_text` 行 494-497 中，`_tracking_error_context_is_target_or_ambiguous` 为 True 但 `_has_actual_tracking_error_signal` 为 False 的行被 `continue` 跳过。计划行为表列出此类产生 `tracking_error_target_or_limit`，但 Slice 2 实施形状仅明确处理了混合行的 `return None` 替换，未显式说明 `continue` 路径如何转为显式 blocker note。

**Risk**：实施 Agent 可能遗漏对 `continue` 路径的分类，导致目标/限制行仍被静默跳过而非获得精确 note。

**Required plan change**：无。行为表意图清晰（"target / limit / control → `tracking_error_target_or_limit`"），实施 Agent 应在文本扫描循环中将 `continue` 路径改为记录 blocker 候选。若实施 Agent 有疑虑，可在实施 artifact 中记录决策。

### F3（低）| 部分 note 常量在当前 §3/§2 扫描架构下可能不会自然触发

**Issue**：计划列出 10 种 note 常量，其中 `tracking_error_benchmark_only` 和 `tracking_error_manager_narrative` 在当前扫描架构下的触发条件不明确：
- `tracking_error_benchmark_only`：需要同时含"跟踪误差"关键词 + 百分比 + 纯基准上下文，但不含目标/控制关键词。此组合在 §3/§2 中较少见。
- `tracking_error_manager_narrative`：经理叙事通常出现在 §4，当前抽取器仅扫描 §3 和 §2。

**Risk**：定义了不会触发的 note 常量不会造成功能问题，但增加了实施和测试的复杂度。

**Required plan change**：无。这些 note 作为防御性分类存在，即使当前不触发也无害。测试矩阵中相关测试可使用构造 fixture 验证分类逻辑。若实施 Agent 发现某 note 确实无法构造合理 fixture，应按 residual 记录而非虚构场景。

### F4（信息）| `_has_actual_tracking_error_signal` 未纳入重构范围

**Issue**：`_has_actual_tracking_error_signal`（行 604-618）检查"实际"、"报告期"、"本报告期"、"过去一年"、"年化"等关键词。其中"年化"范围较宽，可能匹配到非 TE 相关的年化文本。计划未提出对此函数的调整。

**Risk**：低。当前函数在 P13 实施中已通过测试验证，其行为已被接受。P17-S1 的范围是 note 分裂和早期返回修复，不是关键词策略重构。

**Required plan change**：无。若未来出现误分类案例，应作为独立 extractor 策略改进处理。

### F5（信息）| 成功契约保持验证依赖现有测试的 note 断言可能需要更新

**Issue**：计划要求现有成功路径测试继续通过（`test_extract_performance_outputs_direct_tracking_error_when_disclosed` 等 3 项）。但 Slice 1 引入 `_TrackingErrorExtractionOutcome` 内部类型会改变 `_extract_tracking_error` 的内部结构。如果实施 Agent 重构了返回路径，现有测试的 `note is None` 断言（成功路径 note 为 None）仍应成立，但中间 helper 的签名变更可能影响测试构造方式。

**Risk**：极低。现有测试通过 `extract_performance` 公共入口调用，不直接依赖内部 helper 签名。

**Required plan change**：无。实施 Agent 应确认所有现有测试在实施后不经修改即通过。

---

## 实施范围确认

| 约束 | 验证 |
|------|------|
| 无 production golden rows | ✅ Non-goals、Stop Conditions、Residual Risks 三处明确禁止 |
| 无外部数据 | ✅ 仅消费 `ParsedAnnualReport` 内联 builder 和 fixture |
| 无计算型跟踪误差 | ✅ Non-goals 明确排除；Slice 4 保持 `source_type="direct_disclosure"` |
| 无 Service/UI/Engine/renderer/source 触碰 | ✅ No-go 文件列表覆盖全部越界路径 |
| 无 `extra_payload` | ✅ Non-goals 明确排除；Slice 1 step 5 指出不添加 |
| 无设计/总控真源修改 | ✅ Non-goals 和 README/Docs Update Rule 明确排除 |
| 无 excluded local draft 引用 | ✅ Inputs Read 显式排除；未在正文中引用 |

---

## 结论

计划 `PASS_WITH_FINDINGS`。5 项发现均为低/信息级别，不阻断计划接受。实施 Agent 可按计划既定切片顺序（blocker outcome type → 双早期返回替换 → 多匹配 note → 测试）推进实施，并在实施中就地消解 F1-F5 的建议。

核心判定依据：
- 设计边界检查全部通过
- 代码事实 12/12 验证通过
- 双早期返回位置正确识别、修复方向正确
- Blocker 优先级逻辑一致
- 测试矩阵充分
- 实施范围严格自洽
