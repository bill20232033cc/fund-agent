# 017641 Manager Strategy Text Quality Triage Plan — Review (AgentGLM)

> Reviewer: AgentGLM
> Date: 2026-05-27
> Plan artifact: `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

---

## 1. Review Scope

本 review 独立审查 plan artifact，真源范围：

- `AGENTS.md`（规则真源）
- `docs/design.md` v2.2 当前设计章节（设计真源）
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point（控制真源）
- Plan artifact 引用的 accepted evidence chain
- Plan artifact 自身

## 2. Startup Packet 一致性核查

| Plan 声明 | Control doc 真源 | 判定 |
|---|---|---|
| Current phase: `release maintenance` | `implementation-control.md` line 8: `release maintenance` | 一致 |
| Current gate: `017641 manager_strategy_text extraction/quality triage gate` | Next entry point: `017641 manager_strategy_text extraction/quality triage gate` (line 29) | 一致 |
| Latest checkpoint: `110020 reviewed coverage candidate evidence accepted locally` | `implementation-control.md` line 8 和 line 30 确认 | 一致 |
| Worker role: planning worker only, not controller | Control doc line 393: "plan/review first and must not implement extractor changes" | 一致 |
| `promotion_disposition=not_promoted` | 全部 evidence chain controller judgment 均保持 `not_promoted` | 一致 |

Plan Startup Packet replay 与控制真源完全一致。无偏离。

## 3. 根因推断挑战

### 3.1 Plan 的根因推断逻辑

Plan 明确指出：quality gate `block`（FQ2/FQ3 `manager_strategy_text` P0, FQ2F P0 field failure）是 **症状**，不是根因。可能的真实根因包括：

1. Extractor gap：源披露存在但抽取失败
2. 披露/数据缺口：年报本身不包含所需内容
3. Policy/taxonomy issue：QDII 不应要求 `manager_strategy_text` P0
4. Replacement/exclusion：该行无法在当前范围内修复
5. Reject/exclude：evidence 本身有问题

Plan 据此推荐 public-only evidence triage gate 作为最小下一步，而非直接进入 extractor implementation。

### 3.2 根因推断评估

**判定：根因推断逻辑正确且充分。**

理由：

- `AGENTS.md` 硬约束要求"root cause 一定要逻辑/数据同源，禁止使用间接证据"。Quality gate block 是间接证据——它只说明字段缺失/不合格，不说明原因。
- Accepted evidence chain 的 provenance rerun controller judgment 明确记录 `017641` 为 `quality_blocked_after_provenance`，即源可及性已解决但质量仍阻断。这确认了质量问题是第二阶段阻断点，需要独立根因分类。
- Plan 的 Root-Cause Triage Principles（lines 70-83）为每种根因类型定义了同源证据要求，禁止间接推断。这与 `AGENTS.md` 第一性原理约束完全对齐。

### 3.3 质量阻断是否足以证明 extractor gap？

**不充分，且 Plan 正确识别了这一点。**

Quality gate FQ2/FQ3 P0 只证明 `manager_strategy_text` 字段在抽取评分中 `value_present=false` 或 `traceability` 不足。它不能区分：

- 年报 §4 管理人讨论章节存在但 extractor 未解析到（extractor gap）
- 年报 §4 不包含可识别的 manager strategy text（披露缺口）
- QDII 年报的 §4 内容结构与国内主动基金不同，当前 extractor 的锚点不适配（taxonomy/format issue）

Plan 正确地将 extractor gap 作为需要 public evidence 先行证明的候选路径之一，而非默认推断。

### 3.4 Public-only evidence triage 是否为最小正确下一步？

**是。**

理由：

1. 当前已有 public CLI 路径（`extraction-snapshot` / `extraction-score` / `quality-gate`）可以获取字段级状态。
2. 不需要新代码、不需要 PDF 直读、不需要 source helper 改动。
3. 如果 public output 能暴露足够的字段级信息（extraction_mode、value_present、anchor_present），可能区分 extractor gap 和 disclosure gap；如果不足以区分，stop condition 会阻止猜测。
4. 这比直接进入 extractor implementation 更安全——避免在根因不明时实现修复。

## 4. 终端路径区分能力

### 4.1 五类终端路径的进入/退出条件审查

| 候选路径 | 进入条件 | 退出条件 | 区分能力评估 |
|---|---|---|---|
| Public-only evidence triage gate | 当前 accepted state + quality block 但无根因 | 命令失败 / provenance 回退 / 信息不足 / 私有访问 / 新 P0 | 合理。作为根因分类入口而非终端路径。 |
| Extractor implementation plan gate | Public evidence 证明源材料存在但抽取失败 | 证据指向其他根因 / 需要非公共路径 | 合理。需要 same-source 证据证明 extractor gap。 |
| Disclosure / data-gap classification gate | Public evidence 证明无公开路径材料可填充字段 | 证据显示源材料存在 / 有替代路径 | 合理。 |
| Policy / taxonomy issue gate | Public evidence 证明 QDII 不应要求此字段 P0 | 证据指向缺失或 extractor 失败 | 合理。但见 F1。 |
| Replacement / exclusion path | Public evidence 证明该行不可修复 | 替代候选未批准 / 用于凑覆盖数 | 合理。 |

### 4.2 边界案例：extractor gap vs disclosure gap

如果 triage 发现 `manager_strategy_text` 的 `extraction_mode=missing`、`value_present=false`：

- 这可能意味着 extractor 没有找到 §4 中的相关内容（extractor gap），也可能意味着 §4 不包含该内容（disclosure gap）
- Public CLI output 中 `snapshot.jsonl` 的字段级记录包含 `extraction_mode`、`value`、`anchor`、`extraction_notes` 等信息
- 但它不直接暴露年报原始文本中是否包含 manager strategy 相关锚点

Plan 已预见此边界：stop condition line 165 明确规定 "Public outputs do not expose enough field-level information to classify root cause without private inspection" 时必须停止。这是正确的安全网。

## 5. Findings

### F1: Non-blocking — Policy/taxonomy 候选路径需要显式 QDII field applicability baseline

**观察**：Plan 的 Decision Candidate "Policy / taxonomy issue gate"（line 98）进入条件为 "public evidence shows `manager_strategy_text` should not be required for this QDII subtype"。然而 `design.md` §7.3 明确将 `manager_strategy_text` 列为 P0 字段，且未按基金类型区分适用性。QDII preferred_lens（§3.4）优先分析"汇率风险、境外市场暴露"，但没有排除 manager strategy 作为 P0 必要字段。

**风险**：如果 triage worker 在 public output 中发现 `manager_strategy_text` 缺失且无同源证据表明是 extractor bug，可能会倾向于归类为 policy issue，但实际上 design truth 当前要求所有类型都满足此 P0 字段。Taxonomy 变更需要先完成独立 design gate，不能在 triage 中隐式完成。

**Plan 已有缓解**：Plan 的 Forbidden scope（line 98）明确禁止 "broad taxonomy redesign"、"fund_type.py changes without separate accepted plan"。这是充分的。

**建议**：Evidence artifact template 可以增加一个显式检查项：确认 triage worker 在归入 policy/taxonomy issue 之前，必须先记录 `design.md` 当前 P0 字段适用范围，并证明当前设计与 QDII 年报实际披露之间存在矛盾。不需要 plan 修改，但可作为 evidence worker 的 review matrix 补充。

**严重性**：Non-blocking。Plan 的 forbidden scope 已足够保护。

### F2: Non-blocking — Triaging matrix step 4 的一致性风险

**观察**：Triage matrix step 4（line 136）是 "Public-output inspection only, summarized in the evidence artifact"。这一步没有具体命令，而是要求 evidence worker 手动检查 JSONL/JSON 输出并提取字段级事实。不同 evidence worker 可能以不同粒度检查相同输出。

**风险**：如果 evidence worker 只看 `summary.md` 而不看 `snapshot.jsonl` 原始记录，可能遗漏 `extraction_mode`、`extraction_notes`、`anchor` 等关键区分字段。

**Plan 已有缓解**：Required tracked evidence artifact（lines 143-151）列出了必须包含的字段，包括 field-level status from public `snapshot.jsonl` / `score.json` / `score.md` 和 exact FQ issue records。

**建议**：无需 plan 修改。Review matrix 中 AgentMiMo 的 scope 已包含 "field-level `manager_strategy_text` classification"，这足以覆盖。

**严重性**：Non-blocking。Plan 的 evidence artifact 要求字段列表足够。

### F3: Informational — Evidence chain 中 `fund_type_slot` 的来源

**观察**：Plan 的 Accepted Evidence Summary（line 47）记录 `fund_type_slot = qdii_fund`。此值应来自 public CLI output 中的 `classified_fund_type` 字段。017641 的基金名称（南方金砖）包含 QDII 关键词，`fund_type.py` 的识别规则第 3 条（"QDII"/"境外" → `qdii_fund`）应能正确分类。

**验证**：在 provenance rerun controller judgment 中确认 `017641` 作为 QDII 被接受。与 design.md §6.5 识别规则一致。

**严重性**：Informational。无需行动。

## 6. Evidence Commands 审查

| 检查项 | 结果 |
|---|---|
| 所有命令走公共 CLI | 通过。三个命令均为 `uv run fund-analysis` 公共入口。 |
| 通过 FundDocumentRepository backed path | 通过。`extraction-snapshot` 内部调用 `FundDataExtractor.extract()` → `FundDocumentRepository`。 |
| `--force-refresh` 避免旧缓存 | 通过。与 accepted provenance rerun plan 一致。 |
| 无直接 PDF/cache/source-helper 访问 | 通过。Plan 明确禁止。 |
| 输出在 ignored report paths | 通过。所有输出指定在 `reports/extraction-snapshots/` 下。 |
| 不运行命令（plan-only gate） | 通过。Line 129 明确 "should not be run as part of this plan artifact"。 |

## 7. Stop Conditions 审查

| Stop condition | 阻止的风险 | 评估 |
|---|---|---|
| 命令非零退出 | Provenance 或基础设施回归 | 充分 |
| Provenance tuple 与 accepted state 不一致 | Provenance 回退 | 充分。明确列出 4 个必须匹配的字段。 |
| Public output 信息不足 | 间接证据或猜测根因 | 充分。阻止 worker 在信息不足时强行分类。 |
| Reviewer 报告私有访问 / 策略变动 / gate 弱化 / promotion | Provenance 回退、scope drift、quality weakening | 充分。 |
| 新 P0/P1 出现在 accepted cluster 外 | Scope drift | 充分。 |

所有 stop conditions 能够有效阻止：
- Provenance 回退：tuple 一致性检查 ✓
- 间接证据：信息不足 stop + forbidden shortcuts ✓
- Scope drift：新 P0/P1 阻断 + forbidden scope ✓
- Promotion：全链路 `not_promoted` ✓
- Quality gate weakening：explicit non-entry ✓

## 8. Forbidden Scope 审查

| 禁止项 | 对应真源约束 | 评估 |
|---|---|---|
| Renderer / FQ0-FQ6 / Service / CLI 变更 | design.md §7.4 quality gate 不可弱化 | 通过 |
| Default analyze / checklist / source strategy 变更 | AGENTS.md 生产路径约束 | 通过 |
| FundDocumentRepository 变更 | AGENTS.md line 68-70 | 通过 |
| Host / Agent / Dayu 变更 | AGENTS.md 四层边界 + design.md Dayu 裁决 | 通过 |
| PDF / cache / source-helper 直读 | AGENTS.md line 68-70 | 通过 |
| Commit / push / PR / branch mutation | Control doc gate discipline | 通过 |
| Golden / baseline promotion | 全 evidence chain `not_promoted` 纪律 | 通过 |

## 9. GitHub Mutation 检查

Plan 不包含任何 `git commit`、`git push`、`gh pr create`、`git merge` 或任何其他 GitHub mutation 操作。Plan 是 pure document artifact。通过。

## 10. 综合判定

**PASS_WITH_FINDINGS**

Plan 在以下方面完全合规：

1. 根因推断逻辑正确：quality block ≠ extractor gap，需要 public evidence 先分类根因
2. Public-only evidence triage 是最小正确下一步
3. 五类终端路径有清晰的进入/退出条件和禁止范围
4. Evidence commands 全部走公共 CLI 和 repository-backed path
5. Stop conditions 能有效阻止 provenance 回退、间接证据、scope drift、promotion 和 quality weakening
6. 未触碰 renderer / FQ0-FQ6 / Service / CLI / source strategy / FundDocumentRepository / Host / Agent / Dayu
7. 无 GitHub mutation
8. Evidence chain 引用与 accepted controller judgments 完全一致
9. `promotion_disposition=not_promoted` 贯穿全 plan

三个 finding 均为 non-blocking：
- F1: Policy/taxonomy 候选路径需要 evidence worker 显式对照 design.md 当前 P0 适用范围
- F2: Step 4 manual inspection 的一致性已通过 required evidence artifact 字段列表缓解
- F3: `fund_type_slot = qdii_fund` 来源验证，informational

Plan 可以安全进入下一阶段：evidence worker 在 controller 批准后执行 public-only evidence triage。
