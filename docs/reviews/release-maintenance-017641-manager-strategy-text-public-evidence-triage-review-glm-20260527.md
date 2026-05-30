# 017641 Manager Strategy Text Public Evidence Triage — Review (AgentGLM)

> Reviewer: AgentGLM
> Date: 2026-05-27
> Evidence artifact: `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

---

## 1. Review Scope

本 review 独立审查 evidence artifact，真源范围：

- `AGENTS.md`（规则真源）
- `docs/design.md` v2.2 当前设计章节（设计真源）
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point（控制真源）
- Accepted plan/judgment: `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-controller-judgment-20260527.md`
- Public evidence artifact 及其引用的 ignored report outputs

## 2. Startup Packet 一致性核查

| Evidence artifact 声明 | Control doc / accepted plan 真源 | 判定 |
|---|---|---|
| Current phase: `release maintenance` | `implementation-control.md` line 8 | 一致 |
| Current gate: `017641 manager_strategy_text quality triage plan accepted locally` | `implementation-control.md` line 28 | 一致 |
| Next entry point: `017641 manager_strategy_text public-only evidence triage gate` | `implementation-control.md` line 29 | 一致 |
| Latest accepted checkpoint: `9e6a3b1` | Branch HEAD at gate entry | 一致 |
| Worker scope: public CLI evidence only | Controller judgment accepted constraints | 一致 |
| `promotion_disposition=not_promoted` | Controller judgment line 57 | 一致 |

Startup Packet replay 与控制真源完全一致。无偏离。

## 3. Source Provenance Tuple 独立验证

从 public `snapshot.jsonl` 实际记录独立提取并比对：

| Field | Artifact 声明 | Public snapshot.jsonl 实际值 | Match |
|---|---|---|---|
| `fund_code` | `017641` | `017641` | yes |
| `report_year` | `2024` | `2024` | yes |
| `classified_fund_type` | `qdii_fund` | `qdii_fund` | yes |
| `source_strategy` | `primary_then_fallback` | `primary_then_fallback` | yes |
| `resolved_source_name` | `eastmoney` | `eastmoney` | yes |
| `fallback_used` | `true` | `true` | yes |
| `primary_failure_category` | `unavailable` | `unavailable` | yes |
| `fallback_eligibility` | `eligible` | `eligible` | yes |
| `source_provenance_status` | `complete` | `complete` | yes |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` | `fallback_used_primary_failure_category_eligible` | yes |

全部匹配。Provenance tuple 与 accepted complete eligible fallback tuple 一致，无 stop condition 触发。

## 4. Field-Level Status 独立验证

从 public `snapshot.jsonl` 提取 `manager_strategy_text` 记录：

| Artifact 声明 | Public output 实际值 | 验证结果 |
|---|---|---|
| `extraction_mode=missing` | `missing` | 一致 |
| `value_present=false` | `false` | 一致 |
| `anchor_present=false` | `false` | 一致 |
| `section_id=null` | `null` | 一致 |
| `comparable_values={}` | `{}` | 一致 |
| `note=§4 未披露可规则化抽取的投资策略/后市展望` | 完全匹配 | 一致 |
| `priority` in score: `P0` | score.md: `P0` | 一致 |
| `records=1` | score.md: `1` | 一致 |
| `coverage_rate=0.0` | score.md: `0.0%` | 一致 |
| `traceability_rate=0.0` | score.md: `0.0%` | 一致 |

全部字段级状态验证通过。

## 5. FQ2/FQ3/FQ2F Issue Records 独立验证

从 public `quality_gate.json` 独立提取并比对：

| Artifact 声明 | quality_gate.json 实际 | 验证结果 |
|---|---|---|
| FQ2 block, `manager_strategy_text` P0, coverage 0.0, traceability 0.0 | 完全匹配 | 一致 |
| FQ3 block, `manager_strategy_text` P0, coverage 0.0, traceability 0.0 | 完全匹配 | 一致 |
| FQ2F block, `017641` P0, failed: `manager_strategy_text` | 完全匹配 | 一致 |
| FQ2 warn, `turnover_rate` P1 | 完全匹配 | 一致 |
| FQ2 warn, `holdings_snapshot` P1 | 完全匹配 | 一致 |
| FQ2F warn, `017641` P1, failed: `turnover_rate`, `holdings_snapshot` | 完全匹配 | 一致 |
| FQ0 info, `017641` | 完全匹配 | 一致 |
| FQ4 warn, `017641`, missing-field rate 28.6% | `observed_rate: 0.2857...`, threshold 0.2 | 一致 |

共 8 个 issues，全部验证通过。无 artifact 未记录的额外 P0/P1 issue。

## 6. Errors File 独立验证

`errors.jsonl` 为 0 bytes。Artifact 声明一致。抽取命令成功完成，无 failed-fund records。

## 7. Policy / Taxonomy Check 独立验证

`docs/design.md` §7.3 明确列出 P0 字段：

> P0: basic_identity, classified_fund_type, benchmark, nav_benchmark_performance, fee_schedule, **manager_strategy_text**

Public score output 确认 `manager_strategy_text` 优先级为 P0，`field_applicability_decisions` 为空列表，`score_applicability_issues` 为空列表。

Artifact 声明"current design and current public score policy both treat `manager_strategy_text` as applicable P0 for this `qdii_fund` row"——验证通过。无暗改 policy 行为。

## 8. Adversarial Root-Cause Classification Challenge

### 8.1 核心问题

Artifact 将根因分类为 `disclosure_data_gap_not_baseline_ready`。关键 adversarial 质疑：**public evidence 是否足以排除 `extractor_gap_requires_implementation_plan`？**

### 8.2 Artifact 的推理链

1. Quality gate block 是症状，不是根因（已由 accepted plan 确立）
2. Public snapshot 显示 `extraction_mode=missing`，extractor note 说 `§4 未披露可规则化抽取的投资策略/后市展望`
3. Public provenance complete → 源可及
4. Public outputs 不能证明源材料存在但被 extractor 漏掉
5. Current design 仍要求 P0 → 不能归为 policy issue
6. 因此分类为 `disclosure_data_gap_not_baseline_ready`

### 8.3 循证分析

**支持 `disclosure_data_gap` 的证据：**

- (a) `extraction_mode=missing`：extractor 自身评估字段缺失
- (b) Extractor note："§4 未披露可规则化抽取的投资策略/后市展望"
- (c) Provenance complete，errors 为空：源可及且抽取流程无异常
- (d) `classification_basis` 中可见基金自我描述为被动指数化投资："本基金进行被动指数化投资，紧密跟踪标的指数"，"本基金采用完全复制策略"——被动指数基金的 §4 通常包含跟踪方法论，不包含主动管理策略/后市展望
- (e) `fund_name` 为"摩根标普500指数(QDII)"——标普 500 被动指数基金，§4 内容结构与主动基金不同

**潜在质疑：extractor note 的循环性**

Extractor note 是导致 quality block 的同一系统的输出。能否信任它作为"披露确实缺失"的证据？

在纯 public-only discipline 下，extractor note 是最直接的可用证据。但严格来说，它是 extractor 对源材料的解读，不是源材料本身。单独依赖它存在循环论证风险：extractor 说字段缺失 → quality gate 阻断 → 用 extractor 的说法作为披露缺失的证据。

**缓解因素：**

Public snapshot 中的 `classification_basis` 提供了独立于 extractor note 的上下文证据。该字段显示基金自我描述为被动指数化投资（tracking S&P 500），使得 §4 不包含主动管理策略内容在结构上是预期的、一致的。这不是 extractor 的解读——这是从源材料 §1/§2 直接提取的分类信息。

### 8.4 分类判定

Artifact 的推理链逻辑上成立，但存在一个弱点：它没有显式引用 `classification_basis` 作为独立支撑证据，而是主要依赖 extractor note 和"public outputs 不能证明 extractor gap"的排除法。

**判定：分类结论正确，但论证可以更强。** 见 Finding F1。

### 8.5 替代分类评估

| 替代分类 | 是否成立 | 理由 |
|---|---|---|
| `extractor_gap_requires_implementation_plan` | 不成立 | Public evidence 不支持：无同源证据证明源材料存在且被漏掉；基金为被动指数型，§4 无主动策略内容是结构预期的 |
| `reject_exclude_due_to_evidence_violation` | 不成立 | 无 evidence violation：所有 public outputs 一致，provenance tuple 完整，errors 为空 |
| `replacement_or_exclusion_required` | 不成立 | 单字段缺失不等于行不可修复；其他 13 个字段中 9 个 pass |
| `policy_taxonomy_issue_requires_design_plan` | 不成立 | Design truth 当前明确将 `manager_strategy_text` 列为所有类型 P0；taxonomy 变更需独立 design gate |

## 9. Public-Only Discipline 检查

| 检查项 | 结果 |
|---|---|
| 所有数据来自 public CLI outputs | 通过。三个命令均为 `uv run fund-analysis` 公共入口 |
| 无直接 PDF/cache/source-helper 访问 | 通过 |
| 无 source strategy mutation | 通过。Provenance tuple 与 accepted state 一致 |
| 无 quality gate weakening | 通过。Block status 保留 |
| 无 promotion | 通过。`not_promoted` 贯穿 |
| 无 renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu 变更 | 通过 |
| 无 GitHub mutation | 通过。Artifact 纯文档 |
| 输出在 ignored report paths | 通过。`reports/extraction-snapshots/` 下 |

## 10. Stop Condition 检查

| Stop condition | 是否触发 |
|---|---|
| 命令非零退出 | 未触发。三个命令均 exit 0 |
| Provenance tuple 不一致 | 未触发。全部匹配 |
| Public output 信息不足 | 未触发。字段级、issue 级、fund 级信息完整 |
| 私有访问 | 未触发 |
| 新 P0/P1 outside accepted scope | 未触发。P1 `turnover_rate`/`holdings_snapshot` 已在 accepted plan 中命名 |

## 11. Findings

### F1: Non-blocking — Root-cause 论证缺少 `classification_basis` 独立支撑

**观察**：Artifact 的 Terminal Classification Rationale 主要依赖两根支柱：(1) extractor note "§4 未披露" 作为披露缺失的直接证据，(2) "public outputs do not prove extractor gap" 的排除法。然而 extractor note 存在内在循环性——它是导致 quality block 的同一系统的输出。Public snapshot 中实际存在一条独立支撑证据：`classification_basis` 字段显示基金自我描述为被动指数化投资（"本基金进行被动指数化投资，紧密跟踪标的指数"、"本基金采用完全复制策略"）。对于被动标普 500 指数基金，§4 不包含主动管理策略/后市展望是结构预期的。

**风险**：如果未来出现一个主动 QDII 基金的类似 gate，仅依赖 extractor note 而不引用 `classification_basis` 的论证模式可能不够充分——主动基金的 §4 理应包含策略内容，extractor 说"未披露"的可信度需要更强的独立支撑。

**建议**：Controller 可接受当前分类结论，但在后续同类 gate 的 evidence worker 指导中建议显式引用 `classification_basis` / `fund_name` / `classified_fund_type` 作为 extractor note 的独立交叉验证。

**严重性**：Non-blocking。当前被动指数 QDII 的场景下，`classification_basis` 虽未被显式引用但客观存在于 public output 中，分类结论正确。

### F2: Informational — P2 `nav_data` 字段状态未被记录

**观察**：Public `score.md` 显示 `nav_data` (P2) coverage_rate 100.0%、traceability_rate 0.0%、status `fail`。Artifact 的 Field-Level Status 和 Stop/Blocker Status 均未提及此 P2 字段。Controller judgment 的 stop condition 只要求检查 "new unexplained P0/P1 issue outside the accepted cluster"，P2 不在检查范围内。

**建议**：无需行动。Artifact scope 为 accepted cluster（P0 `manager_strategy_text` + 已知 P1 issues），P2 不在 gate 关注范围内。仅作为完整性记录。

**严重性**：Informational。

## 12. Command Log 验证

Artifact 记录三个命令均 exit 0，输出 `snapshot.jsonl`/`summary.md`/`errors.jsonl`、`score.json`/`score.md`/`golden_set.json`、`quality_gate.json`/`quality_gate.md`。实际 report 目录包含 9 个文件（含 `summary.md`），与 artifact 描述一致。`errors.jsonl` 为 0 bytes 已验证。

## 13. 综合判定

**PASS_WITH_FINDINGS**

Artifact 在以下方面完全合规：

1. Source provenance tuple 10/10 字段与 public output 完全匹配
2. Field-level status 全部从 public `snapshot.jsonl`/`score.json`/`score.md` 独立验证通过
3. FQ2/FQ3/FQ2F issue records 全部从 public `quality_gate.json` 独立验证通过（8/8 issues）
4. Errors file 状态验证通过
5. Policy/taxonomy check 正确对照 `design.md` 当前 P0 applicability，无暗改
6. Terminal classification `disclosure_data_gap_not_baseline_ready` 结论正确：public evidence 支持披露缺失分类，排除法正确排除了 extractor gap、evidence violation、replacement、policy issue
7. `promotion_disposition=not_promoted` 贯穿全 artifact
8. 无 public-only discipline 违反
9. 无 source strategy mutation、quality gate weakening、promotion
10. 无 renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu/GitHub mutation
11. Stop conditions 全部未触发
12. No new unexplained P0/P1 outside accepted scope

两个 finding：
- **F1 (non-blocking)**：Root-cause 论证应显式引用 `classification_basis`（被动指数基金）作为 extractor note 的独立交叉验证，以应对未来主动基金同类 gate 的论证需求
- **F2 (informational)**：P2 `nav_data` fail 未被记录，但不在 gate scope 内

Controller 可安全接受此 evidence artifact 的分类结论。F1 建议作为后续 evidence worker 指导的改进输入，不阻断当前 gate 推进。
