# Dayu-Agent 公司分析报告 Audit 能力深度分析

## 一、Audit 机制概述

Dayu-Agent 的 audit（审核/审计）能力是整个报告写作流水线的核心质量保障机制。它对 LLM 依据定性分析模板生成的各章节 Markdown 文档进行多层次的自动化审核，确保报告内容的**准确性、完整性和可追溯性**。

核心理念：**让 AI 读财报的方式从"大海捞针"变成"按图索骥"，让数据有置信度，让投资结论、投资报告可审计、可追踪**。

---

## 二、核心架构设计

### 2.1 模块职责划分

```
dayu/services/internal/write_pipeline/
├── chapter_audit_coordinator.py   # 审计协调器（主编排）
├── audit_rules.py                 # 审计规则定义与决策逻辑
├── audit_formatting.py            # 格式化处理与内容提取
├── audit_evidence_rewriter.py     # 证据锚点重写
├── repair_executor.py             # 修复执行器
└── models.py                      # 数据模型定义
```

### 2.2 三层审计架构

```
┌─────────────────────────────────────────────────────────────┐
│                    程序审计                                  │
│     结构检查 → 内容检查 → 证据检查（无需 LLM）               │
└─────────────────────────────────────────────────────────────┘
                              ↓ 通过
┌─────────────────────────────────────────────────────────────┐
│                    LLM 审计                                  │
│     证据充分性 → 内容合规性 → 风格一致性（调用 LLM）         │
└─────────────────────────────────────────────────────────────┘
                              ↓ 发现疑似违规
┌─────────────────────────────────────────────────────────────┐
│                    证据复核                                  │
│     验证证据是否真实存在 → 判断是否为幻觉                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 三、审计规则体系

### 3.1 规则分类与编号

| 类别 | 规则码 | 含义 | 阻断级别 |
|------|--------|------|----------|
| **结构类(P)** | P1 | 章节结构与骨架不匹配 | 阻断 |
| | P2 | 内容过短（<10字符） | 阻断 |
| | P3 | 缺少"证据与出处"小节 | 阻断 |
| **证据类(E)** | E1 | 证据锚点不精确 | 可复核 |
| | E2 | 证据与正文断言不匹配 | 可复核 |
| | E3 | 证据完全缺失 | 需整章重建 |
| **内容类(C)** | C1 | 内容违规（如幻觉） | 阻断 |
| | C2 | 内容不完整 | 低优先级 |
| **风格类(S)** | S1-S7 | 格式/风格问题 | 视严重度 |

### 3.2 规则判定逻辑

```python
# audit_rules.py 核心逻辑
def _recompute_audit_result(*, violations: list[Violation]) -> tuple[bool, AuditCategory]:
    rules = [item.rule for item in violations]
    
    # 证据类阻断规则
    if any(rule in BLOCKING_EVIDENCE_AUDIT_RULE_CODES for rule in rules):
        return False, AuditCategory.EVIDENCE_INSUFFICIENT
    
    # 内容类阻断规则
    if any(rule in BLOCKING_CONTENT_AUDIT_RULE_CODES for rule in rules):
        return False, AuditCategory.CONTENT_VIOLATION
    
    # 风格类规则（需累积才阻断）
    if any(severity == "high" for _rule, severity in effective_style_pairs):
        return False, AuditCategory.STYLE_VIOLATION
    if sum(1 for severity in severities if severity == "medium") >= 2:
        return False, AuditCategory.STYLE_VIOLATION
    
    return True, AuditCategory.OK
```

---

## 四、审计流程详解

### 4.1 程序审计（Programmatic Audit）

**特点**：纯规则驱动，无需调用 LLM，快速失败

```python
def _run_programmatic_audits(content, skeleton, allowed_conditional_headings):
    # 1. 结构匹配检查（P1）
    if not _matches_skeleton_structure(content, skeleton, allowed_conditional_headings):
        return AuditDecision(passed=False, category=CONTENT_VIOLATION, 
                            violations=[Violation(rule=P1, ...)])
    
    # 2. 内容长度检查（P2）
    if len(content.strip()) < 10:
        return AuditDecision(passed=False, ...)
    
    # 3. 证据小节存在检查（P3）
    if not _has_evidence_section(content):
        return AuditDecision(passed=False, category=EVIDENCE_INSUFFICIENT, ...)
    
    return None  # 通过
```

**骨架结构匹配算法**：
- 提取正文中的 Markdown 标题序列
- 与模板骨架标题按顺序匹配
- 允许条件型标题（通过 ITEM_RULE 定义）
- 使用 Unicode 归一化消除中英文标点差异

### 4.2 LLM 审计

**触发条件**：程序审计通过后

**审计 Prompt 构建**：
```python
# 审计场景输入包含：
- chapter_markdown: 当前章节正文
- skeleton: 章节骨架
- chapter_contract: 章节契约（必须回答的问题、禁止覆盖的内容）
- item_rules: 条件型条目规则
- audit_scope_rules: 审计规则范围摘要
```

**LLM 返回结构**：
```json
{
  "pass": false,
  "class": "evidence_insufficient",
  "violations": [
    {
      "rule": "E1",
      "severity": "high",
      "excerpt": "2024年营收增长15%",
      "reason": "证据锚点未精确到具体报表行",
      "rewrite_hint": "补充 income_statement.revenue.2024 锚点"
    }
  ],
  "repair_contract": {
    "repair_strategy": "patch",
    "retry_scope": "targeted_evidence_patch"
  }
}
```

### 4.3 证据复核

**目的**：验证疑似证据违规是否为真实问题还是误判

**触发条件**：审计发现 E1 或 E2 类违规

```python
def _collect_confirmable_evidence_violations(violations):
    # 收集可进入 confirm 环节的违规
    for violation in violations:
        if violation.rule in {E1, E2}:  # CONFIRMABLE_EVIDENCE_AUDIT_RULE_CODES
            collected.append(violation)
    return collected
```

**Confirm 结果状态**：

| 状态 | 含义 | 后续动作 |
|------|------|----------|
| `confirmed_missing` | 证据确实缺失 | 删除对应断言 |
| `supported` | 证据有效存在 | 移除违规 |
| `supported_but_anchor_too_coarse` | 证据存在但锚点粗糙 | 触发锚点重写 |
| `supported_elsewhere_in_same_filing` | 证据在同文件其他位置 | 触发锚点重写 |

---

## 五、修复闭环机制

### 5.1 修复策略推导

```python
def _derive_repair_strategy(violations):
    rule_set = {item.rule for item in violations}
    
    # 结构性违规或 E3 → 整章重建
    if rule_set & (STRUCTURAL_REPAIR_AUDIT_RULE_CODES | REGENERATE_EVIDENCE_AUDIT_RULE_CODES):
        return RepairStrategy.REGENERATE
    
    # 其他 → 局部修补
    return RepairStrategy.PATCH
```

### 5.2 修复合同

```python
@dataclass
class RepairContract:
    contract_version: str                    # 合同版本
    missing_evidence_slots: list             # 缺失证据槽位
    offending_claim_spans: list              # 违规断言片段
    remediation_actions: list                # 修复动作列表
    preferred_tool_action: str               # 建议工具动作
    repair_strategy: str                     # patch / regenerate / none
    retry_scope: str                         # 重试作用域
    notes: list[str]                         # 备注
```

### 5.3 Repair Patch 应用

```python
def _apply_repair_plan(chapter_markdown, repair_plan, repair_contract):
    for patch in repair_plan["patches"]:
        # 1. 定位目标片段
        target_excerpt = patch["target_excerpt"]
        target_kind = patch["target_kind"]  # substring/line/bullet/paragraph
        
        # 2. 确定作用域（可限定在特定 section）
        if patch["target_section_heading"]:
            scope_start, scope_end = _find_markdown_section_span(...)
        
        # 3. 匹配并替换
        if match_count == 1:
            markdown = markdown[:start] + replacement + markdown[end:]
```

**Patch 粒度类型**：
- `substring`: 精确子串替换
- `line`: 整行替换
- `bullet`: 列表项替换
- `paragraph`: 段落替换

---

## 六、证据锚点重写机制

### 6.1 设计背景

当 confirm 发现证据存在但锚点不精确时（如 `supported_but_anchor_too_coarse`），系统可自动修正证据锚点，无需重新生成整章。

### 6.2 锚点修复类型

```python
@dataclass
class EvidenceAnchorFix:
    kind: str        # same_filing_section / same_filing_statement / same_filing_evidence_line
    action: str      # append / refine_existing
    keep_existing_evidence: bool
    evidence_line: str       # 完整 evidence line
    section_path: str        # 标题路径
    statement_type: str      # 报表类型
    period: str              # 期间
    rows: list[str]          # 报表行标签
```

### 6.3 重写流程

```python
def maybe_rewrite_evidence_anchors(task, current_content, confirmation_result, ...):
    # 1. 检查是否有 anchor rewrite 候选
    if not _has_anchor_rewrite_candidates(confirmation_result):
        return current_content  # 无需重写
    
    # 2. 执行机械重写
    rewritten_lines = _rewrite_evidence_lines_and_collect_resolved_anchor_issues(...)
    
    # 3. 后验校验
    if not _validate_anchor_rewrite_postconditions(...):
        return current_content  # 校验失败，回退原文
    
    # 4. 移除已解决的违规
    audit_decision = _drop_resolved_supported_anchor_violations(...)
    
    return rewritten_content
```

---

## 七、完整审计流程图

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        Chapter Audit Pipeline                            │
└──────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  1. 程序审计                                                             │
│     ├─ P1: 骨架结构匹配                                                   │
│     ├─ P2: 内容长度检查                                                   │
│     └─ P3: 证据小节存在                                                   │
└──────────────────────────────────────────────────────────────────────────┘
                          │                    │
                     通过 │                    │ 失败
                          ▼                    ▼
┌─────────────────────────────┐    ┌─────────────────────────────┐
│  2. LLM 审计                │    │  直接进入修复流程            │
│     ├─ 证据充分性 (E1-E3)   │    │  (repair_strategy:          │
│     ├─ 内容合规性 (C1-C2)   │    │   regenerate)               │
│     └─ 风格一致性 (S1-S7)   │    └─────────────────────────────┘
└─────────────────────────────┘
                          │
                          ▼ (有可复核违规)
┌──────────────────────────────────────────────────────────────────────────┐
│  3. 收集可复核违规                                                       │
│     CONFIRMABLE = {E1, E2}                                               │
└──────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  4. 证据复核                                                             │
│     ├─ confirmed_missing → 标记删除                                      │
│     ├─ supported → 移除违规                                              │
│     └─ supported_* + anchor_fix → 进入锚点重写                           │
└──────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  5. 锚点重写 (Anchor Rewrite)                                            │
│     ├─ 机械修正证据锚点                                                   │
│     ├─ 后验校验                                                           │
│     └─ 移除已解决违规                                                     │
└──────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│  6. 合并结果 & 推导修复合同                                               │
│     ├─ repair_strategy: patch / regenerate                               │
│     └─ retry_scope: targeted_patch / chapter_regenerate                  │
└──────────────────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────┴───────────┐
              │                       │
         passed │                       │ failed
              ▼                       ▼
    ┌─────────────────┐     ┌─────────────────────────┐
    │  章节通过       │     │  7. 执行修复             │
    │  进入下一章     │     │     ├─ patch: 局部修补   │
    └─────────────────┘     │     └─ regenerate: 整章重建│
                            └─────────────────────────┘
                                        │
                                        ▼
                            ┌─────────────────────────┐
                            │  8. 重新审计 (循环)      │
                            │     直到通过或达到最大重试│
                            └─────────────────────────┘
```

---

## 八、关键设计亮点

### 8.1 分层审计策略

- **程序审计**：快速失败，节省 LLM 调用成本
- **LLM 审计**：深入语义层面，识别证据不足、内容违规、风格问题
- **证据复核**：二次确认，降低误判率

### 8.2 结构化修复合同

将违规转化为可执行的修复动作：
- `remediation_actions`: 明确的修复指令
- `repair_strategy`: 智能选择修复粒度
- `retry_scope`: 精准定位修复范围

### 8.3 证据可追溯性

每条断言必须关联到：
- 具体财报文件
- 明确的报表类型
- 精确的期间和行标签

### 8.4 渐进式修复

```
初始写作 → 审计 → 局部修补 → 审计 → 锚点修正 → 审计 → 通过
                ↓
           (严重违规)
                ↓
           整章重建 → 审计 → 通过
```

---

## 九、与定性分析模板的协同

模板中的 HTML 注释提供了审计依据：

```markdown
<!--
CHAPTER_CONTRACT
must_answer:
  - 用一句话定义这到底是什么生意
  - 说明公司面向用户提供什么核心产品
must_not_cover:
  - 不展开竞争格局、市场份额
END_CHAPTER_CONTRACT
-->

<!--
ITEM_RULE
mode: conditional
item: 平台/互联网公司的双边参与方结构
when: 只要有稳定披露且有判断价值就写
facets_any: [平台互联网, 电商/交易平台]
END_ITEM_RULE
-->
```

审计时：
- `must_answer` → 检查是否遗漏必答项
- `must_not_cover` → 检查是否越界输出
- `ITEM_RULE` → 构建允许的条件型标题集合

---

## 十、总结

Dayu-Agent 的 audit 能力是一个**多层次、可闭环、可追溯**的智能审核系统：

1. **程序审计**提供快速失败机制，在结构层面拦截明显问题
2. **LLM 审计**深入语义层面，识别证据不足、内容违规、风格问题
3. **证据复核**二次确认疑似违规，区分真实问题与误判
4. **修复闭环**根据违规严重程度智能选择局部修补或整章重建
5. **锚点重写**支持轻量级证据修正，避免不必要的全文重生成

这套机制确保了 AI 生成的分析报告具备**买方研究级别的质量标准**：结论有据、证据可查、逻辑自洽。

---

## 参考代码路径

```
dayu-agent/
├── dayu/services/internal/write_pipeline/
│   ├── chapter_audit_coordinator.py    # 审计协调器
│   ├── audit_rules.py                  # 审计规则
│   ├── audit_formatting.py             # 格式处理
│   ├── audit_evidence_rewriter.py      # 证据重写
│   ├── repair_executor.py              # 修复执行
│   ├── models.py                       # 数据模型
│   └── enums.py                        # 枚举定义
└── dayu/assets/定性分析模板.md          # 报告模板
```

---

*本文档基于 Dayu-Agent 开源代码分析生成*
