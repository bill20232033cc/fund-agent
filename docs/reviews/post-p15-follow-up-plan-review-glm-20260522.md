# Post-P15 Follow-up Planning Review — GLM（2026-05-22）

## Review Identity

| Field | Value |
|---|---|
| Reviewer | AgentGLM |
| Review target | `docs/reviews/post-p15-follow-up-planning-20260522.md` |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |
| Context artifacts | `docs/reviews/p15-s1a-code-review-controller-judgment-20260522.md`, `docs/reviews/post-p14-follow-up-plan-review-controller-judgment-20260522.md` |
| Excluded inputs | `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md` — 未读取、未引用 |
| Review type | plan-review adversarial review |

## Verdict

`PASS_WITH_FINDINGS`

规划文件从第一性原理正确拒绝继续硬推 `001548` production `tracking_error` golden，正确选择 enhanced-index 候选证据获取作为最短可验证下一步，候选基金代码全部来自 selected CSV，`161725` fixture 没有被误当 production evidence，`FundDocumentRepository` / `FundDataExtractor` 边界、fail-closed、golden sequencing 均得到保持。发现 4 个非阻断 finding。

## First-principles Assessment

### 1. 拒绝继续硬推 001548 — 正确

P15-S1A 通过 `FundDocumentRepository` / `FundDataExtractor` 边界证明 `001548` 2024 年报 12 个 keyword hit 全部是 target/limit 或 manager narrative，没有 direct observed `tracking_error` disclosure。规划文件 First-principles Criteria 第 4 条明确"尊重 P15 负结果"，第 6 条明确"可 fail closed"。这与设计真源 `design.md` §6.2 抽取模式（`missing` = 无法获取）和控制真源 Active Residuals（production `tracking_error` golden correctness owner = future golden gate only if direct observed evidence is later accepted）完全一致。继续硬推没有第一性原理依据。

### 2. 选择 P16-S1 enhanced-index production golden — 正确

候选对比表逐一评估 5 个备选方案的产品价值、边界/证据风险，并给出 defer/select 决策：

| 备选方案 | 评估结论 | GLM 确认 |
|---|---|---|
| enhanced-index production golden | Select — 最贴近真实 production quality gap | 正确。P14 已把 `tracking_error` 纳入 `enhanced_index` 条件 P1 分母，当前只有 `161725` fixture |
| source-metadata retry | Defer — provenance hygiene，不创造新的 direct disclosure | 正确。P15-S1A 已分类全部候选文本，刷新 metadata 不改变分类 |
| extractor early-return | Defer — 需要新的 false-negative 证据，001548 不是 false negative | 正确。当前 `_has_ambiguous_tracking_error_text`（`performance.py:517-542`）对 001548 行为正确 |
| repo hygiene | Defer — 维护价值，非产品证据 | 正确。不抢占产品 evidence gate |
| calculated tracking error | Defer — 需要新 source contracts / 计算语义，跳阶过大 | 正确。与设计真源非目标和控制真源 Non-goal reminder 一致 |

enhanced-index production golden 是唯一同时满足"直接服务当前设计目标"、"保持证据同源"、"最小化新增架构"三个标准的方案。

### 3. 候选基金代码 — 全部验证通过

| 基金代码 | 名称 | selected CSV 验证 |
|---|---|---|
| `004194` | 招商中证1000指数增强A | `docs/code_20260519.csv` line 38，国内股票类 |
| `005313` | 万家中证1000指数增强A | `docs/code_20260519.csv` line 39，国内股票类 |
| `017644` | 博道中证1000指数增强A | `docs/code_20260519.csv` line 40，国内股票类 |
| `019918` | 招商中证2000指数增强A | `docs/code_20260519.csv` line 41，国内股票类 |
| `019923` | 华泰柏瑞中证2000指数增强A | `docs/code_20260519.csv` line 42，国内股票类 |

`161725`：不在 selected CSV 中，规划文件正确标注为"deterministic fixture coverage only, not selected-fund production golden evidence"。验证确认 `161725` 不在 `reports/golden-answers/golden-answer-prefill-reviewed.md`、`golden-answer-prefill.md` 或 `golden-answer.json` 中，仅存在于 test fixture 代码。

`001548`：在 selected CSV 中（line 17，天弘上证50ETF联接A，国内股票类，`index_fund`），已有 production `index_profile` golden rows，但 `tracking_error` golden 正确地被 P15-S1A blocked。

### 4. 边界 / fail-closed / golden sequencing — 保持良好

- `FundDocumentRepository` / `FundDataExtractor` 边界：Implementation Guardrails 第 1 条明确要求所有年报访问必须通过这两个入口。
- Fail-closed：Stop conditions 覆盖 7 类不可接受证据（target/limit、narrative、standard deviation only、benchmark-only for tracking error、ambiguous、unparseable、anchor-incomplete），且要求 stop 时输出 blocker 和 residual。
- Golden sequencing：File Ownership 表明确把 plan-review、evidence-acquisition、golden implementation 三阶段分离，golden rows 编辑必须在独立 gate 进行。

### 5. 范围控制 — 适当

规划文件没有把 plan-review 变成 implementation 或 golden 修改。禁止列表明确排除 direct edits to golden files、source/test/README/design/control edits、calculated tracking error 等。验证 success signals 第一条就是 `git diff --check HEAD`，确认 plan gate 不应有代码变更。

## Findings

### F1 — MEDIUM: review plan 缺少对候选评估顺序的约束

**位置**: `post-p15-follow-up-planning-20260522.md` "Review Plan" section (line 133-143)

**发现**: Review Plan 要求 reviewer reject 如果 plan"skips any of the five selected-fund enhanced-index candidates without a documented reason"，但没有要求 plan 定义候选的评估优先级顺序。Validation Success Signals 第 1 条说"exact candidate list and evaluation order are defined"，但 review plan 本身没有约束这个顺序应该基于什么原则（如：基金规模、成立年限、已有 golden coverage、指数类型等）。

**建议**: Controller judgment 应明确 P16-S1 plan 必须在候选列表外额外定义评估顺序原则，避免实现阶段按任意顺序遍历。

**Severity**: MEDIUM — 不阻断 gate 进入，但如果 P16-S1 plan 不定义顺序原则，evidence acquisition 可能优先选择证据最少的候选，浪费 gate 时间。

### F2 — LOW: "also listed in research notes" 引用不具体

**位置**: `post-p15-follow-up-planning-20260522.md` line 81-83

**发现**: `017644` 和 `019923` 的 Source fact 列标注"also listed in research notes"，但没有指明是哪个 research notes 文件。这降低了对来源事实的可审计性。

**建议**: 如果 research notes 是 selected CSV 之外的辅助来源，应标注具体文件路径或直接删除该补充说明，因为 selected CSV 已充分证明这两个候选的来源合法性。

**Severity**: LOW — 不影响候选选择正确性，仅影响可审计性。

### F3 — LOW: benchmark-only for `index_profile` 的接受边界需在 P16-S1 plan 中显式定义

**位置**: `post-p15-follow-up-planning-20260522.md` line 95

**发现**: Implementation Guardrails 第 5 条说"Treat benchmark-only evidence as acceptable only for `index_profile` fields that are already supported by current extractor semantics"。这个约束正确区分了 `index_profile` 和 `tracking_error` 的证据要求，但"already supported by current extractor semantics"是隐含引用——P16-S1 plan 需要显式定义当前 extractor 对 `index_profile` 哪些子字段支持 benchmark-only、哪些不支持，否则实现阶段可能对"benchmark-only"的理解产生分歧。

**建议**: Controller judgment 应要求 P16-S1 plan 在 evidence contract 中显式列出 `index_profile` 的 benchmark-only 可接受子字段清单。

**Severity**: LOW — 当前 extractor 对 `index_profile` 的 `benchmark_context` source_tier 已有明确实现（见 `001548` golden rows），分歧风险较低。

### F4 — INFO: extractor early-return false-negative 路由条件表述精确

**位置**: `post-p15-follow-up-planning-20260522.md` line 98-99

**发现**: Implementation Guardrails 第 7 条要求"If another enhanced-index candidate exposes a real direct disclosure that current extractor misses because of early-return behavior, route that as an evidence-backed extractor refinement inside a separate implementation slice before any golden edit"。这条正确地把可能的 false-negative 发现路由到 extractor refinement 而不是 golden bypass，与控制真源 Active Residuals 中"Tracking-error extractor early-return scope"的 owner 一致。这是一个正面 finding，记录为 INFO。

**Severity**: INFO — 确认边界设计合理。

## Residual Verification

规划文件的 Residuals 表（9 项）与控制真源 Active Residuals 完全对齐，没有遗漏或新增。特别确认：

- `001548` production `tracking_error` golden rows: owner = future golden gate，status = blocked by P15-S1A — 正确
- `001548` source metadata retry: owner = future evidence retry，status = deferred — 正确
- extractor early-return scope: owner = future extractor-improvement phase，status = deferred — 正确
- enhanced-index production golden expansion: owner = P16-S1 plan-review，status = selected next gate — 正确
- RR-13 duplicate `016492`: owner = User / App source，status = untouched — 正确

## Scope Compliance

- 未读取或引用 `docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md`
- 未 commit、push、创建 PR 或修改任何源文件
- Review 产出仅为本 review artifact

## Recommendation

Controller 可以接受此规划文件。F1 建议在 controller judgment 中作为 P16-S1 plan 的附加约束带入，F2 和 F3 可作为非阻断 wording/precision note。
