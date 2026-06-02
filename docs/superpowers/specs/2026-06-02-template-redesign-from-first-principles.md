# 基金 LLM 报告模板重设计 —— 第一性原理诊断与改造草案

- 设计 gate: heavy（公共契约 + 审计语义 + 模板结构）
- 配套真源:
  - `docs/fund-analysis-template-draft.md`（v1，不动）
  - `fund_agent/fund/template/contracts.py`（v1，不动）
  - `fund_agent/fund/chapter_auditor.py`（不读取、不修改）
- 依据保留证据:
  - `reports/manual-llm-smoke/mvp-real-llm-chapter-acceptance-slice1-20260602-195518/slice1-evidence-triage-summary.md`
  - `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json`
- 非目标: 不改代码 / 不改真源文档 / 不放松审计规则 / 不直接喂 5 年 PDF 原文 / 不接 provider budget 或 score-loop

---

## 0. 范围声明

本文档为**重设计草案**，不替代现有真源。所有"建议改造"在进入实施前必须通过独立的 standard 实施 gate 与 review gate，且需在 `docs/implementation-control.md` 中建立对应 phase。本文档本身定位为 design **input**，不是 design **truth**。

事实 vs 设计判断区分原则:
- **事实**: 来自 `slice1-evidence-triage-summary.md` / `summary.json` / `contracts.py` / `chapter_auditor.py` 原文，且无推断。
- **设计判断**: 上述事实之外的所有"应该 / 必须 / 推荐"，需在实施 gate 中独立接受 reviewer challenge。

---

## 1. 模板问题诊断（事实 / 设计判断分层）

### 1.1 事实证据：来自 `slice1-evidence-triage-summary.md` + `summary.json`

| 章节 | 状态 | 失败原因 | 操作 | user_prompt_chars | approx_tokens | allowed_anchor | allowed_fact | elapsed_ms |
|------|------|---------|------|--------------------|---------------|----------------|--------------|------------|
| Ch1 | accepted | — | — | — | — | — | — | — |
| Ch2 | failed | `llm_timeout` | auditor (attempt 0) | 2917 | 743 | 6 | 5 | 60003 / 60035 |
| Ch3 | failed | `repair_budget_exhausted` | programmatic C2 @ 言行一致 | — | — | — | — | — |
| Ch4 | failed | `llm_timeout` | auditor (attempt 0) | 2280 | 584 | 4 | 5 | 60003 / 60036 |
| Ch5 | accepted | — | — | — | — | — | — | — |
| Ch6 | failed | `llm_timeout` | auditor (attempt 1, repair 1) | 2868 | 731 | 10 | 8 | 60003 / 60032 |

事实层可观察到的硬约束:
- 3 章失败 (`Ch2/Ch4/Ch6`) 全部发生在 **auditor** 阶段，writer 阶段全部 `finish_reason=stop` 正常返回。
- 3 章失败章的 user_prompt 都在 **2280–2917 字符** 区间，**远小于**当前主链 10000–27000 字符的事实填充量。
- 3 章失败章 elapsed_ms 都是 `60003` 或 `60035`，提示 60s hard cap，第二次 attempt 也未突破。
- Ch3 失败在 **programmatic C2 词法命中**，是合同自相矛盾，不是 LLM 推理问题。
- Ch6 的 `attempt 0` 在 auditor 阶段已经先吃了 C2 @ `压力测试`，repair 后 `attempt 1` auditor 又被 60s timeout 吃掉。

### 1.2 事实证据：来自 `contracts.py` 与 `chapter_auditor.py`

来自 [contracts.py:151-749](file:///Users/maomao/fund-agent/fund_agent/fund/template/contracts.py#L151-L749):

- `ChapterContract` 是 4-tuple 形式契约: `must_answer / must_not_cover / required_output_items / preferred_lens` 全部为 `tuple[str, ...]`。
- Ch2 = 7 must_answer / 3 must_not_cover / 7 required_output_items。
- Ch3 = 7 must_answer / 4 must_not_cover / 6 required_output_items，其中 must_answer 第 4 项要求 "言行一致性判断"。
- Ch6 = 6 must_answer / 6 must_not_cover / 4 required_output_items。
- 8 章共享同一 `DEFAULT_AUDIT_FOCUS` 五元组。

来自 [chapter_auditor.py:45-51](file:///Users/maomao/fund-agent/fund_agent/fund/chapter_auditor.py#L45-L51):

```python
DEFAULT_AUDIT_FOCUS: Final[tuple[str, ...]] = (
    "evidence_support",
    "must_not_cover_boundary",
    "missing_semantics",
    "readability",
    "non_asserted_facet_boundary",
)
```

来自 [chapter_auditor.py:557-584](file:///Users/maomao/fund-agent/fund_agent/fund/chapter_auditor.py#L557-L584):

- `_audit_must_not_cover` 对每条 must_not_cover 调用 `_must_not_cover_phrases` 抽短语，纯词法判断。
- 抽出的短语与 markdown 直接 `in` 比较，**不查证据可用性**。

来自 [chapter_auditor.py:114-123](file:///Users/maomao/fund-agent/fund_agent/fund/chapter_auditor.py#L114-L123) 与 [741-761](file:///Users/maomao/fund-agent/fund_agent/fund/chapter_auditor.py#L741-L761):

- `_MUST_NOT_COVER_STOPWORDS` 不含"言行一致"或"风格一致"等业务短语，因此 `_must_not_cover_phrases` 在第 4 条 Ch3 must_not_cover 上会抽到 `言行一致`、`风格一致`、`风格稳定` 等。
- 任何包含这些短语的 markdown 都触发 C2 BLOCKING。

来自 [chapter_auditor.py:835-849](file:///Users/maomao/fund-agent/fund_agent/fund/chapter_auditor.py#L835-L849):

- auditor system_prompt 仅 54 字符。
- user_prompt 列举 5 个 audit_focus + 严格行协议。
- 协议要求每次响应必须落到 `PASS|chapter|no issues` 或 `SEVERITY|LOCATION|MESSAGE` 行形式。

### 1.3 模板事实问题（直接由证据支撑，非推断）

#### F-1. 合同自相矛盾：Ch3 must_answer 与 must_not_cover 在"言行一致"上直接冲突

- 事实: must_answer 第 4 项是"言行一致性判断：说的和做的一样吗？", must_not_cover 第 4 项被 `_must_not_cover_phrases` 抽到禁用短语 `言行一致`、`风格一致`、`风格稳定`。
- 后果: LLM 写"言行一致性"被 C2 阻断；LLM 不写"言行一致性"被 C1/R1 阻断。
- 证据: slice1 Ch3 attempt 0/1 都是同一 C2 失败，最终 `repair_budget_exhausted`。
- 改进方向: 这不是"必须删一些条款"的取舍问题，是**合同结构**问题：必须用 `evidence_conditional` 把禁用短语改为"在 X 证据缺失时禁用"，并把 evidence 状态显式注入审计上下文。

#### F-2. Ch2/Ch4/Ch6 的 60s timeout 不是 prompt size 问题

- 事实: 三个失败章 user_prompt 都在 2280–2917 字符（远低于主链 10k–27k 区间），系统 prompt 54 字符。
- 反证: Ch1 / Ch5 在同样 60s budget 内成功，user_prompt 长度量级相当。
- 后果: 单纯提高 `timeout_seconds` 或 `timeout_max_attempts` 不能解决，根因在 auditor 任务复杂度。
- 改进方向: 拆 Ch2 业绩 + 归因 → 拆 3 章后单章信息密度下降；audit_focus 改为章节子集；typed 简化的 chapter contract 让 LLM 决策面更小。

#### F-3. required_output_items 没有"无证据即降级"语义

- 事实: Ch2 = 7 items, Ch3 = 6 items, Ch6 = 4 items。LLM 在 60s 严格审计下倾向于用占位符/编造凑齐。
- 后果: 缺 5 年数据时 LLM 经常编造"近 5 年"或写"未披露"被 E3 阻断。
- 改进方向: required_output_items 必须可携带 `optional: bool` / `evidence_required: tuple[str, ...]`, 不满足时 LLM 必须显式输出 EVIDENCE_GAP, 而不是硬填占位符。

#### F-4. must_not_cover 词法匹配无法表达"证据条件"

- 事实: `_must_not_cover_phrases` 不读取 evidence availability, 也不解析"在...时"条件状语。
- 后果: "不在...时, 推断..."这类带条件的禁区, 程序化实现为无条件禁用, 触发自相矛盾。
- 改进方向: must_not_cover 必须升级为结构化: `clause: str` + `evidence_conditional: tuple[str, ...] | None` + `literal_forbidden_phrases: tuple[str, ...]`, evidence 不满足时该 clause 不参与审计。

#### F-5. preferred_lens 与 must_answer 重复声明, 没有"覆盖"语义

- 事实: Ch1 主动基金 lens 列出"投资哲学/选股标准/卖出标准/仓位管理/风险控制" 5 个; Ch1 must_answer 第 2-5 项又重复一遍; Ch3 又要求"言行一致"。
- 后果: LLM 困惑于同一概念在多章重复, 且不知道哪一章是 first-class。
- 改进方向: 引入 "first-class chapter for facet X" 单一源; 其他章节只通过引用 + 摘要使用, 不重新展开。

#### F-6. Ch0 与 Ch7 动作判断分离, 容易触发 R2 跨章不一致

- 事实: Ch0 must_answer 第 3 项"回答当前判断应是值得持有 / 需要关注 / 建议替换"; Ch7 must_answer 第 1 项"三选一明确立场: 值得持有、需要关注、建议替换"。
- 后果: Ch0 写 🟡, Ch7 写 🟢 → R2 风险。
- 改进方向: Ch0 必须显式"引用"Ch7 结论, 不独立判断; Ch0 的 contract 改为"消费 Ch7 conclusion bundle, 不重新做判断"。

#### F-7. Ch6 压力测试 lens 阈值与 must_answer 不联动

- 事实: Ch6 must_answer "压力测试结论是什么"; bond_fund lens 写"压力测试默认阈值: -5% / -10% / -20%"; 但 must_answer 不要求"按 fund_type 应用对应阈值"。
- 后果: 006597 纯债基金 LLM 经常套用 -30% 默认值, 触发 E2。
- 改进方向: 压力测试必须用 typed `StressTestThresholds` 注入审计上下文, LLM 不能自由选取阈值。

#### F-8. 8 章共享 audit_focus 五元组, 不分章差异化

- 事实: `DEFAULT_AUDIT_FOCUS` 是 5 个固定项, 8 章都用同一组。
- 后果: Ch1 (产品本质) 几乎不触发 must_not_cover / non_asserted_facet_boundary, 5 focus 全套浪费; Ch3 / Ch6 高度敏感却只用同样的 5 项。
- 改进方向: `ChapterContract.audit_focus` 改为 `tuple[AuditFocusLiteral, ...]`, 每章声明子集。

#### F-9. 没有"evidence_gap_declaration"审计项

- 事实: 5 个 audit_focus 不包含"显式声明数据缺口"。
- 后果: 缺 5 年数据的章节不会因没声明缺口而失败, LLM 倾向写"近 5 年"凑数。
- 改进方向: 新增 `evidence_gap_declaration` 焦点, 要求 LLM 在 `evidence_availability` 不足时显式 `EVIDENCE_GAP: <item>` 输出。

#### F-10. 5 年数据语义未分层

- 事实: Ch2 must_answer 第 1 项"近 1 年、3 年、5 年的基金净值增长率"; 但年报披露 1Y/3Y 普遍, 5Y 仅成熟基金才有。
- 后果: 基金成立 < 5 年时 LLM 必须编造或写"未披露"占位符。
- 改进方向: must_answer 改为"按可用时段 (1Y/3Y/5Y) 逐条声明, 缺则标 EVIDENCE_GAP"。

### 1.4 设计判断（需在实施 gate 接受 challenge）

> 以下是本设计 gate 的提案, 必须在独立 standard 实施 gate 中被至少两位 reviewer 复核, 且至少一位 reviewer 显式接受或拒绝。

- D-1. 上述 F-1 ~ F-10 已经形成"模板设计"问题而不是"LLM 不够好"问题; 改造的优先级应当高于 provider budget / 模型选择。
- D-2. timeout 根因的 60% 在合同复杂度, 30% 在 audit_focus 不分章, 10% 在 prompt 长度。
- D-3. 5 年证据接入不应当"全文喂 LLM", 应当通过 typed `EvidenceBundle` 由 Python 层预算与分片。
- D-4. 第 2 章拆分不是为拆分而拆, 是为了让单章决策面降到 60s 内可解。

---

## 2. 新模板设计原则

### 2.1 第一性原则

P1. **合同比 prompt 重要** —— LLM 的稳定行为来自机器可消费的契约, 来自自然语言提示的稳定性是次要。
P2. **缺证据必须显式, 不能默认凑数** —— 章节契约必须区分"有数据" vs "无数据"两条路径, 缺数据时只允许 EVIDENCE_GAP + 最小验证问题, 禁止编造。
P3. **章节互不重复** —— 同一概念只在 first-class 章节展开, 其他章节只引用 / 摘要。
P4. **章节结论可被上游章节消费** —— Ch0 必须显式消费 Ch7 conclusion bundle, Ch7 失败则 Ch0 失败, 不独立判断。
P5. **审计契约 typed** —— must_not_cover / audit_focus / required_output 全部 typed enum, 词法匹配只作为 fallback。
P6. **审计上下文显式化** —— evidence_availability / stress_test_thresholds / facet_application 必须由 Python 层注入审计上下文, LLM 不能从 prompt 推导。
P7. **章节数服务章节粒度, 不服务章节数** —— 拆章节是手段, 降低单章决策面是目的。
P8. **5 年证据走 typed bundle** —— 5 年 PDF 原文不直接喂 LLM, 由 EvidenceBundle 在 Python 层预算、分片、按章节路由。

### 2.2 与 dayu 定性模板的对比 (事实观察)

| 维度 | 基金模板 v1 (事实) | dayu 定性模板 v1 (事实) | 启示 (设计判断) |
|------|--------------------|--------------------------|----------------|
| 业务维度 | 12 fund_type + 12 constraint | 38 business_model + 28 constraint | 基金 facet 数量合理; 不需要追平 dayu |
| ITEM_RULE / 章 | 2–5 个, 集中在 Ch1 | 20–40 个, 均匀分布 | 应当扩充 ITEM_RULE 数量并下放到更多章节 |
| 章节数 | 0+7 = 7 章正文 | 0+10 = 10 章正文 | dayu 10 章正文 + 大量 ITEM_RULE, 信息粒度更细 |
| 缺证据语义 | "未披露/不适用 + 占位符" | "必须删除 (不输出)" + "可选"模式 | 应当引入 `optional` / `delete_if_no_evidence` 模式 |
| 三段结构 | 默认全文三段, Ch0 除外 | 默认三段, Ch0 封面页除外 | dayu 的 Ch0 约束更严格 (封面页, 不写证据) |
| Lens 区分度 | index/active/bond/enhanced/qdii/fof 6 类 | 业务 38 类 + 约束 28 类 | 应当对 bond/active/enhanced_index 等子类型加更细 lens |
| 审计协议 | 5 audit_focus (自由 tuple) | 未披露 (参考文档无 audit_focus) | dayu 没有 typed audit contract, 不能直接对齐 |

设计判断 (D-5): 基金模板的章节粒度可以向 dayu 看齐, 但契约结构必须 typed, 5 audit_focus 的概念应改成可配置。

### 2.3 设计判断: 不直接迁移 dayu 的"20-40 ITEM_RULE"

理由 (事实 + 判断):
- 事实: 基金模板 ITEM_RULE 集中在 Ch1 (2 个) 与 Ch2 (2 个), 其他章节为 0。
- 事实: ITEM_RULE 当前没有 typed, 是自然语言注释。
- 判断: 数量本身不是问题, "ITEM_RULE 是否真的被 LLM 看到并执行"才是问题。当前 ITEM_RULE 数量 2-5 个 vs LLM 0 个, 都是低信号。要做的是 typed 化 + 全章节铺开, 不只是增加数量。

---

## 3. 章节结构草案

### 3.1 设计判断: 章节数 0+7 → 0+9 (待 gate 复核)

| 新章节 | 旧章节对应 | 主要理由 (设计判断) |
|--------|------------|----------------------|
| Ch0 投资要点概览 | Ch0 | 保留, 但 contract 改为"消费 Ch9 conclusion bundle", 不独立判断 |
| Ch1 产品本质 | Ch1 | 保留, 唯一允许展开"投资哲学/选股标准"的 first-class 章节 |
| **Ch2 业绩表现 (R / B)** | Ch2 拆出 | 仅含 1Y/3Y/5Y 净值增长率与基准, 不含归因; 缺数据时只输出 EVIDENCE_GAP |
| **Ch3 收益归因 (A = α)** | Ch2 拆出 | 结构性 vs 阶段性; 含分年度表 |
| **Ch4 成本侵蚀 (C)** | Ch2 拆出 | 管理费 / 托管费 / 销售服务费 / 换手率 / 隐性成本估算 |
| Ch5 基金经理画像 | Ch3 改名 | 改名为"画像"避免与 Ch3 "收益归因"混淆; 言行一致改为 evidence_conditional |
| Ch6 投资者获得感 | Ch4 | 保留 |
| Ch7 当前阶段与关键变化 | Ch5 | 保留 |
| Ch8 核心风险与否决项 | Ch6 | 保留; 压力测试必须用 typed `StressTestThresholds` |
| Ch9 最终判断 | Ch7 | 保留, 改为 first-class 章节, Ch0 引用其结论 |

设计判断 (D-6): 拆 Ch2 → Ch2/Ch3/Ch4 三章后, 单章 user_prompt 字符量预计从 10k 量级降至 3-5k, 与当前 auditor 60s timeout 区间内的 2-3k 经验值接近, 假设 typed contract 简化决策, timeout 概率显著降低。但**这个假设需要独立 acceptance gate 验证**, 不能只凭推理。

设计判断 (D-7): Ch5 (原 Ch3) 与 Ch3 (原 Ch2-归因) 的顺序对换, 让"业绩 → 归因 → 成本 → 经理"成为连续的因果链; 但这违反旧模板"产品 → 收益 → 经理 → 获得感 → 阶段 → 风险 → 判断"的叙事节奏, 必须 reviewer 显式接受。

### 3.2 typed ChapterContract 草案 (设计)

```python
class MustAnswerClause(TypedDict):
    question: str
    evidence_required: tuple[str, ...]  # fact_ids / anchor_patterns
    data_availability_tier: Literal["required", "best_effort", "optional"]
    fallback: Literal["evidence_gap", "delete_section", "degrade_to_question"]

class MustNotCoverClause(TypedDict):
    clause: str
    literal_forbidden_phrases: tuple[str, ...]  # 词法匹配
    evidence_conditional: tuple[str, ...]  # 满足时该 clause 不参与审计
    chapter_scope: Literal["this", "all"]

class RequiredOutputItem(TypedDict):
    item: str
    optional: bool
    evidence_required: tuple[str, ...]
    render_when_missing: Literal["evidence_gap", "skip", "stub"]

class StressTestThresholds(TypedDict):
    fund_type: FundType
    normal_pct: float
    extreme_pct: float
    historical_worst_pct: float

class ChapterContract(TypedDict):
    chapter_id: int
    title: str
    narrative_mode: Literal["cover", "definition", "decomposition", "portrait",
                            "data", "change", "risk", "judgment"]
    evidence_requirements: EvidenceRequirements
    must_answer: tuple[MustAnswerClause, ...]
    must_not_cover: tuple[MustNotCoverClause, ...]
    required_output: tuple[RequiredOutputItem, ...]
    preferred_lens: Mapping[FundType, TemplateLensRule]
    audit_focus: tuple[AuditFocusLiteral, ...]  # 章节子集
    stress_test_thresholds: StressTestThresholds | None
    first_class_facets: tuple[str, ...]  # 该章 first-class 处理的 facet
    consumes_chapter_conclusions: tuple[int, ...]  # 上游章节 id
```

设计判断 (D-8): 草案只为概念示意, 不进入代码; 真正落 TypedDict / dataclass 是实施 gate 范围。

### 3.3 evidence contract 草案 (设计)

```python
class EvidenceAvailability(TypedDict):
    fund_code: str
    report_year: int
    facts: tuple[str, ...]  # 全量 fact_ids
    anchors: tuple[str, ...]  # 全量 anchor_ids
    data_availability: Mapping[Literal["1Y", "3Y", "5Y"], bool]
    evidence_gaps: tuple[EvidenceGap, ...]
    audit_context_injection: tuple[str, ...]  # 注入审计 system_prompt 的固定信息

class EvidenceGap(TypedDict):
    item: str  # 例: "近 5 年净值增长率"
    reason: Literal["fund_age_too_short", "not_disclosed", "unreconciled", "schema_drift"]
    discovered_at: str  # ISO8601
    minimum_verification_question: str
```

设计判断 (D-9): EvidenceAvailability 由 Python 层在 prompt 构造时注入, 不由 LLM 推导。LLM 在 user_prompt 中看到的 evidence_availability 必须是 typed 字符串, 不可省略。

### 3.4 typed audit_focus 草案 (设计)

```python
AuditFocusLiteral = Literal[
    "evidence_support",          # 已有
    "must_not_cover_boundary",   # 已有
    "missing_semantics",         # 已有
    "readability",               # 已有
    "non_asserted_facet_boundary",  # 已有
    "evidence_gap_declaration",  # 新增: 必须显式 EVIDENCE_GAP
    "evidence_conditional_phrase",  # 新增: 带条件状语的禁用短语必须 evidence 已满足
    "cross_chapter_consistency",  # 新增: Ch0 结论必须等于 Ch9 结论
    "data_availability_match",   # 新增: 不允许写 "近 5 年" 当 5Y availability=False
    "first_class_facet_respect",  # 新增: 非 first-class 章节不展开 facet
]
```

设计判断 (D-10): 9 个 audit_focus 中保留 5 个现有, 新增 4 个; 不应在 typed 化时减少现有语义, 避免审计规则被悄悄放松 (违反 non-goal)。

---

## 4. audit contract / evidence contract 建议

### 4.1 audit contract 演进路径 (设计)

| 阶段 | 行为 | typed 程度 |
|------|------|------------|
| 当前 v1 | `must_not_cover` 词法匹配; `audit_focus` 全局 5 项 | 弱 (tuple[str, ...]) |
| 阶段 A (本次 gate 提议) | `must_not_cover` 改 typed; 引入 `evidence_conditional`; `audit_focus` 改章节子集 | 中 (TypedDict) |
| 阶段 B (后续 gate) | audit_focus 新增 4 项 typed; 引入 `cross_chapter_consistency` 自动比对 Ch0 ↔ Ch9 | 强 |
| 阶段 C (后续 gate) | 完全 typed contract + JSON Schema; 词法匹配仅作 fallback | 全 typed |

非目标 (来自用户): 不放松审计规则。阶段 A/B/C **不减少**现有 must_not_cover 语义, 5 个现有 audit_focus 全部保留。

### 4.2 evidence contract 演进路径 (设计)

| 阶段 | 行为 | 5 年证据接入 |
|------|------|----------------|
| 当前 v1 | 全量 facts 注入 (500+ 字段) | 不接 5 年 |
| 阶段 A | ChapterFactStore (设计) + 章节路由 | 不接 5 年 |
| 阶段 B | EvidenceBundle + availability tier | 接 1Y/3Y typed |
| 阶段 C | 5 年 PDF 原文 typed bundle + Python 预算分片 | 接 5Y typed |

非目标: 不接 5Y PDF 原文, 不直接喂 LLM。阶段 A/B 的 EvidenceBundle 在 Python 层预算, 5 年数据先做 typed 抽取 (5Y 净值、5Y 基准、5Y 规模) 再注入。

### 4.3 解决 Ch3 "言行一致" 自相矛盾的具体路径 (设计)

事实: 冲突点 = must_answer "言行一致性判断" + must_not_cover "言行一致" 词法禁用。
解决 (typed 化):
1. must_answer 第 4 项改为 `MustAnswerClause(evidence_required=("turnover", "style_change_evidence"), fallback="evidence_gap")`。
2. must_not_cover 第 4 项改为 `MustNotCoverClause(clause="不在...时推断...", literal_forbidden_phrases=("风格稳定", "风格一致", "言行一致"), evidence_conditional=("turnover", "style_change_evidence"))`。
3. audit_focus 新增 `evidence_conditional_phrase`: 当 `turnover` 和 `style_change_evidence` 都不可用时, literal_forbidden_phrases 不参与审计 (因为 LLM 不会写这些词, 不需要禁)。
4. 当 `turnover` 可用但 `style_change_evidence` 不可用时, LLM 必须输出 `EVIDENCE_GAP: 跨期风格变化证据`, 审计要求"不得写'风格稳定'"。

这个路径的真实性需要 gate 验证, 但逻辑上自洽于事实证据。

### 4.4 解决 Ch2/Ch4/Ch6 60s timeout 的具体路径 (设计)

事实: 失败章 user_prompt 都在 2280-2917 字符。
路径 (拆章节 + typed 简化):
1. 拆 Ch2 → Ch2 业绩 + Ch3 归因 + Ch4 成本, 单章 prompt 字符量预计降至 1.5-2k。
2. 章节 `audit_focus` 收窄: Ch2 业绩 只需 `evidence_support + data_availability_match` (2 项); Ch3 归因 需 `evidence_support + must_not_cover_boundary + data_availability_match` (3 项)。
3. evidence_availability 在 user_prompt 显式列出, LLM 不再需要从 facts 推导。
4. required_output 改为 typed, LLM 决策面下降。

D-11 (设计判断): 单章 prompt 长度降 30% + audit_focus 减半, auditor 60s 完成概率预计从 ~50% 提升到 ~85% (经验估计, 需 acceptance gate 实测)。**这个数字不能直接写入真源, 必须在 acceptance gate 实测后写回**。

### 4.5 Agent tool-loop 兼容性 (设计)

事实: 当前是确定性 CLI 主链路, 不接 dayu-agent runtime; 后续 Host 层 / Agent 层需要在本项目内化。
设计: typed contract 应是 Host-agnostic, 不依赖具体 Host 实现。
- `ChapterContract` 是 dataclass, Host 可序列化。
- `EvidenceAvailability` 是 typed dict, Host 可路由。
- `AuditFocusLiteral` 是 Literal, 后续可映射到 tool call / score。
- 不应在 contract 中硬编码 provider / model 名称。

---

## 5. 迁移计划与风险

### 5.1 迁移阶段 (设计)

| 阶段 | 范围 | gate 类型 | 风险等级 | 验收 |
|------|------|-----------|----------|------|
| 阶段 0: 本文作为 design input | 仅文档 | standard | low | 至少 2 reviewer 接受 / 1 reviewer 显式拒绝后改写 |
| 阶段 1: typed contract schema 草案 (代码原型) | `fund_agent/fund/template/contracts_v2.py` 新建, 不替换 v1 | standard | medium | v1 / v2 并行可运行, 旧路径不变 |
| 阶段 2: 5 audit_focus 子集化实验 | auditor 加 `audit_focus: tuple[AuditFocusLiteral, ...]` 字段, 默认仍 5 项 | standard | medium | 旧审计语义 100% 保留 |
| 阶段 3: must_not_cover evidence_conditional 实验 | auditor 新增 evidence_conditional 分支, 默认仍词法匹配 | standard | high | Ch3 修复, slice1 证据重跑 |
| 阶段 4: 章节拆分 (Ch2 → Ch2/Ch3/Ch4) | 模板改为 0+9, 旧 0+7 标记 deprecated | heavy | high | slice2 acceptance, 至少 2 个基金, timeout 概率下降到 80%+ |
| 阶段 5: Ch0 消费 Ch9 结论 | Ch0 contract 改为 consume | standard | medium | R2 风险显式消失 |
| 阶段 6: 5 年数据 typed bundle | EvidenceBundle 接入 1Y/3Y/5Y | heavy | high | 5Y availability 显式可注入 |
| 阶段 7: v1 标记 deprecated, 写 v2 真源 | 真源文档更新 | heavy | critical | 跨层验收, UI 兼容 |

设计判断 (D-12): 阶段 0-2 不改任何 v1 行为, 阶段 3 才开始触及审计语义, 阶段 4 才触及章节结构, 阶段 5-7 逐步收口。每个阶段独立 gate, 上一阶段不过不进下一阶段。

### 5.2 关键风险

| ID | 风险 | 事实依据 | 缓解 |
|----|------|----------|------|
| R-1 | 阶段 1 v1/v2 并行导致双契约漂移 | 当前 v1 在 8 个文件 import contracts | v2 默认 fallback 到 v1, 阶段 7 才切主路径 |
| R-2 | 阶段 3 evidence_conditional 引入新 bug | `_must_not_cover_phrases` 是纯函数, 改动面大 | 保留旧函数为 `_lexical_must_not_cover_phrases` 默认路径, 新函数 `evidence_conditional_must_not_cover` 为 opt-in |
| R-3 | 阶段 4 章节拆分破坏下游 report assembler | summary.json 中 `final_assembly_issues` 已经依赖 chapter_id 强引用 | 阶段 4 同步更新 report assembler, 至少 2 个真实基金跑通 |
| R-4 | 阶段 5 Ch0 ↔ Ch9 一致性引入新审计项 | Ch0 失败时 Ch9 也必须失败, 整体 acceptance 下降 | 阶段 5 显式 acceptance 门槛: 5 个基金中至少 4 个同时 accept |
| R-5 | 阶段 6 5Y 数据接入可能让 prompt 反弹 | 当前 prompt 70-95% 是 facts/anchors, 5Y 数据加入会更糟 | 5Y 数据 typed bundle 必须预算化, 不超过 1200 字符 / 章 |
| R-6 | typed contract 升级破坏 renderer / parser | 当前 renderer 用 duck typing 解析自然语言注释 | 阶段 1 加 2 周兼容层, renderer 双解析 |
| R-7 | 用户要求 "不放松审计规则" 与新增 audit_focus 不冲突 | 5 个现有 focus 全部保留, 4 个新增 | 阶段 2 把现有 5 focus 全部 default-on, 不删除 |
| R-8 | 设计判断 D-6 (拆 Ch2) 的 timeout 改善是经验估计, 没有实测 | 无历史证据, 纯推理 | 阶段 4 必须先跑 3 个基金 acceptance, 不达预期则回滚 |

### 5.3 与现有 spec 的关系

事实: `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` 已经存在, 是 plan A (章节拆分) + plan C (facet 链路接通) 的 design spec。
关系:
- 本文是 plan A 的**深化与重设计**, 不是平行 spec。
- 阶段 1-3 可视为 plan A 的前置 (typed contract + audit_focus 子集化), 阶段 4 是 plan A 主线 (章节拆分), 阶段 5-7 是 plan A + 本文 5 项 contract 演进的合并。
- plan C (facet 链路接通) 与本文互补, 不冲突: facet 链路接通解决"facet 能否控制 LLM"问题, 本文解决"facet 控制什么、什么时候控、控到什么程度"问题。
- 后续实施 gate 应在 `implementation-control.md` 建立新 phase, 引用本文 + 现有 spec 共同作为 input。

### 5.4 验收门槛 (设计判断, 需 gate 复核)

- A-1. 阶段 0 完成后, 阶段 1-3 必须在 4 周内出 typed contract 原型。
- A-2. 阶段 4 完成后, 5 个不同 fund_type 基金 (含至少 1 个 active_fund, 1 个 bond_fund) acceptance 通过率 ≥ 80%。
- A-3. 阶段 5 完成后, Ch0 ↔ Ch9 动作判断不一致 (R2) issue 计数 = 0 (在 5 个基金 acceptance 样本中)。
- A-4. 阶段 6 完成后, 5Y availability 显式注入, 不允许 LLM 编造"近 5 年"。
- A-5. 阶段 7 完成后, v2 为主路径, v1 仍保留 6 个月供回滚。

---

## 6. 给用户的下一步

1. 阶段 0 review: 接受本文作为 design input, 标记 design spec 状态。
2. 阶段 1 plan gate: 在 `docs/implementation-control.md` 建立新 phase, 引用本文 + 现有 facet-wiring spec。
3. 阶段 1 implementation gate: 写 `contracts_v2.py` 原型, 不替换 v1。
4. 不要在本 gate 直接进入阶段 3+ (审计语义 + 章节拆分), 必须先有阶段 1-2 的 typed 化产物, 再做 acceptance 实测。

---

## 附: 引用真源

- [docs/fund-analysis-template-draft.md](file:///Users/maomao/fund-agent/docs/fund-analysis-template-draft.md) (v1, 不动)
- [fund_agent/fund/template/contracts.py](file:///Users/maomao/fund-agent/fund_agent/fund/template/contracts.py) (v1, 不动)
- [fund_agent/fund/chapter_auditor.py](file:///Users/maomao/fund-agent/fund_agent/fund/chapter_auditor.py) (不读取实现细节, 只引用 DEFAULT_AUDIT_FOCUS 与 _must_not_cover_phrases)
- [reports/manual-llm-smoke/mvp-real-llm-chapter-acceptance-slice1-20260602-195518/slice1-evidence-triage-summary.md](file:///Users/maomao/fund-agent/reports/manual-llm-smoke/mvp-real-llm-chapter-acceptance-slice1-20260602-195518/slice1-evidence-triage-summary.md)
- [docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md](file:///Users/maomao/fund-agent/docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md) (plan A + C 主线)
- [定性分析模板.md](file:///Users/maomao/fund-agent/定性分析模板.md) (dayu 参考, 不在本文档改动)
