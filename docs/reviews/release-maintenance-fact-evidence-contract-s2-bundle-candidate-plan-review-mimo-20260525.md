# Plan Review: Fact-Evidence Contract S2 Bundle Candidate Plan

> Reviewer: AgentMiMo
> Date: 2026-05-25
> Artifact under review: `docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md`
> Gate: `fact-evidence-contract S2 bundle candidate planning`
> Conclusion: **PASS_WITH_FINDINGS**

---

## 1. Scope and Truth Sources

**Reviewed target**: S2 bundle candidate planning artifact — a planning-only document defining the contract direction for a future typed `ReportEvidenceBundle`, its relation to `StructuredFundDataBundle`, source boundaries, identifier conventions, chapter-contract handling, implementation slices, and stop conditions.

**Truth sources checked**:
- `AGENTS.md` — execution rules, module boundaries, `FundDocumentRepository` boundary, explicit params / no `extra_payload`, Dayu discipline
- `docs/implementation-control.md` — Startup Packet, Current Gate, Next Entry Point, Open Residuals, Non-Goals
- `docs/design.md` §2.1, §2.2, §2.3, §5.4, §5.4.1, §5.4.2, §5.4.3, §7.2, §7.3, §7.4, §12 — architecture boundaries, Fact/Evidence input contract, scoring dimensions, extraction snapshot, quality gate
- S1 score-schema controller judgment — accepted schema decisions, deferred items
- S1 dry-run controller judgment — accepted evidence, turnover resolution, residual risks
- `fund_agent/fund/extractors/models.py` — `EvidenceAnchor`, `ExtractedField`, `ExtractionMode` code facts
- `fund_agent/fund/data_extractor.py` — `StructuredFundDataBundle` structure, `_AnnualReportRepository` Protocol

## 2. Assumptions Tested

| # | Assumption | Verdict |
|---|-----------|---------|
| A1 | Plan is code-generation-ready enough for a later implementation gate | Mostly yes; 2 gaps below |
| A2 | Wrapping `StructuredFundDataBundle` follows first principles | Yes, with one coupling caveat |
| A3 | Source boundaries are correct: `FundDocumentRepository` only | Yes |
| A4 | No future Host/Agent/LLM/dayu runtime pretended | Yes |
| A5 | Anchor ids, data_gap_refs, review status, invalid combinations, JSONL validation are concrete enough | Mostly yes; 2 gaps below |
| A6 | Turnover/chapter_contract prefers wording constraints before extraction | Yes |
| A7 | No overdesign, coupling, missing tests, missing stop conditions, conflicts with design doc | Mostly clean; 1 coupling observation |

## 3. Findings

### 01-未修复-中-review_status 缺少转换语义
- **位置**: Review Status Derivation 章节（plan L186-L206）
- **问题类型**: 契约缺失
- **当前写法**: Plan 定义了 9 个 bundle-level review_status 枚举值和 6 个最小 invalid combinations，但只说"must be derived from contained records"，未定义合法状态转换（如 `candidate → repository_verified` 需要什么条件满足、`rejected` 是否可回退）。
- **反例/失败场景**: Implementation agent 可能随意定义转换逻辑，导致状态可以被绕过（如从 `deferred` 直接跳到 `scoring_ready` 而不经过 `fact_prefill_reviewed`）。S1 controller judgment 已接受"terminal review states lacked transition semantics"的修复，但该修复只针对 S1 schema 的终端状态语义，S2 bundle-level 状态的转换图仍未定义。
- **为什么有问题**: `docs/design.md` §5.4 已定义 ChapterPlan → ChapterDraft → RuleAudit → LLMAudit → AcceptedChapter 状态机，每步有明确输入/输出/失败处理。Bundle-level review_status 若没有等价的转换约束，implementation agent 必须自行设计，可能与 S0 corpus transition triggers（`candidate → repository_verified → fact_prefill_generated → fact_prefill_reviewed → scoring_ready → accepted_baseline`）不一致。
- **直接证据**: Plan L186-L206 定义了状态但无转换条件；S0 controller judgment 已定义转换 trigger/actor/evidence 但未被 plan 引用或对齐。
- **影响**: 实施 Agent 跑偏 / 生成不一致的状态机 / review 不可验收
- **建议改法和验证点**: 至少列出每个状态的准入条件（参考 S0 已接受的 transition triggers）和是否 terminal。验证点：`rg` 检查 implementation 是否包含非法跳转测试。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 02-未修复-中-locator_hash 规格不足
- **位置**: Identifier Conventions > Anchor IDs（plan L220-L225）
- **问题类型**: 契约缺失
- **当前写法**: Plan 说 `locator_hash` 是"a short deterministic hash of `page_number`, `table_id`, `row_locator`, and normalized note/ref"，但未指定哈希算法、输出长度、碰撞策略或归一化规则。
- **反例/失败场景**: Implementation agent 选择不同哈希函数（md5[:6] vs sha256[:8] vs xxhash[:4]）会导致跨 run 不稳定；同一 bundle 内不同 anchor 若哈希碰撞（如 4 位 hex 仅有 65536 种），会导致 anchor_id 重复。
- **为什么有问题**: Plan 的目标是"let a later implementation agent add models and tests without redesigning"，但 anchor_id 是 bundle 内所有 fact/calculation/gap 引用的基础。如果 anchor_id 生成逻辑不稳定或有碰撞，整个引用链都会出问题。S1 dry-run 使用的 `gap:004393.2024.turnover_rate.not_reviewed_in_current_slice` 没有 hash 成分，说明 hash 方案是新增设计，需要更具体。
- **直接证据**: Plan L224: "locator_hash is a short deterministic hash" — 无算法/长度/碰撞策略。
- **影响**: 实施 Agent 跑偏 / 生成跨 run 不稳定的 id / 锚点引用链断裂
- **建议改法和验证点**: 指定算法（如 `sha256[:8]`）和输入字段归一化规则（如 `None` 字段跳过、字符串 lowercase）。验证点：相同输入在不同 run 产生相同 anchor_id；不同输入不碰撞（在 bundle 规模内）。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 03-未修复-低-chapter_contract wording constraint 仍为候选
- **位置**: Chapter-Contract Handling Before Extraction Work（plan L295-L319）
- **问题类型**: open question 未收敛
- **当前写法**: Turnover stability claim rule 以表格形式列出 4 种条件和对应 report behavior，但 `required_report_wording` 标注为"candidate"。Plan 说"Future S2 implementation should encode this as report wording constraints"。
- **反例/失败场景**: S1 dry-run controller judgment 已明确"chapter_contract first"作为 turnover issue 的 next action，但如果 wording constraint 仍为候选，implementation agent 可能跳过约束编码直接进入 extraction，与 controller 裁决矛盾。
- **为什么有问题**: S1 controller judgment 已裁决"turnover-rate issue immediate next action is chapter_contract first, not automatic extraction"。Plan 应该把这条裁决作为 accepted constraint 而非 candidate，否则 implementation gate 还需要重新裁决。
- **直接证据**: Plan L316 标注为"candidate"；S1 dry-run controller judgment 明确裁决 chapter_contract first。
- **影响**: 实施 Agent 可能忽略 controller 裁决 / 返工
- **建议改法和验证点**: 将 turnover stability wording constraint 从 candidate 升级为 accepted（引用 S1 controller judgment 裁决），保留其他章节的 wording constraint 为 candidate。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 04-未修复-低-Slice 2 projection 未处理 ExtractedField 多锚点情况
- **位置**: Future Implementation Slices > Slice 2（plan L342-L358）
- **问题类型**: 切片过粗
- **当前写法**: Plan 说"Project each `ExtractedField` to one or more `facts`, `evidence_anchors`, and `data_gaps`"，但未说明当 `ExtractedField.anchors` 包含多个锚点时如何映射。
- **反例/失败场景**: 某些字段（如 `nav_benchmark_performance`）可能有多个锚点（年报§3 净值表 + §3 基准表）。Projection 函数需要决定：每个锚点生成独立 fact？还是一个 fact 引用多个 anchor_id？当前代码中 `ExtractedField.anchors` 是 `tuple[EvidenceAnchor, ...]`，允许多个。
- **为什么有问题**: `fund_agent/fund/extractors/models.py` L49 确认 `anchors: tuple[EvidenceAnchor, ...]`。如果 implementer 不处理多锚点映射，可能丢失锚点或生成冗余 fact。
- **直接证据**: `models.py` L49 `anchors: tuple[EvidenceAnchor, ...]`；Plan L349 "Project each ExtractedField to one or more facts" 未细化多锚点映射策略。
- **影响**: 实施 Agent 可能丢失锚点 / 生成不一致的 fact-anchor 引用
- **建议改法和验证点**: 在 Slice 2 中补充一句：每个 `ExtractedField` 映射为一个 fact，fact 的 `source_anchor_ids` 引用该字段的所有投影 anchor_id。验证点：测试用包含多锚点的 fake bundle 验证所有锚点都被投影。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## 4. Architecture Boundary Review

Plan 正确遵守了 `AGENTS.md` 和 `docs/design.md` 的四层边界：

- `ReportEvidenceBundle` 归属 Agent 层 `fund_agent/fund`（Plan L49），符合"理解基金类型、财报章节、投资规则、有知有行方法论"的归属规则。
- Service 只编排不理解 extractor 内部（Plan L49）。
- 未引入 `fund_agent/host` 或 `fund_agent/agent` 包。
- 未引入 `dayu.host` 或 `dayu.engine`。
- 生产年报访问仍通过 `FundDocumentRepository`（Plan L14, L89, L350）。
- 无 `extra_payload`（Plan L6, L412）。
- 非目标明确列出不改变 renderer/FQ0-FQ6/quality gate（Plan L404-L415）。

**未发现架构边界违反。**

## 5. Overengineering / Overcoupling Review

- **Wrapping vs evolving**: Plan 正确选择了 wrap 而非 evolve，理由充分（evolve 会过早耦合 extraction 和 writing/audit lifecycle）。这不是过度设计。
- **9 个 review_status 状态**: 数量合理，对应 S0 已接受的 corpus transition triggers 加上 terminal states。未过度抽象。
- **5 个 implementation slices**: 粒度适中，每个 slice 有独立验证条件。未发现过粗或过细。
- **未发现过度设计或过度耦合。**

## 6. Stop Conditions Review

Plan 定义了 9 个 stop conditions（Plan L419-L429），覆盖：
- Host/Agent runtime 需求
- Renderer/FQ0-FQ6 行为变更
- Parallel extraction path
- Direct cache/PDF access
- extra_payload 使用
- Fallback category masking
- Schema drift/integrity error masking
- Turnover extraction without chapter-contract
- Fixture promotion without gate

**Stop conditions 覆盖充分，未发现遗漏。**

## 7. Validation Commands

```bash
rg -n "ReportEvidenceBundle|StructuredFundDataBundle|FundDocumentRepository|extra_payload|dayu.host|dayu.engine|chapter_contract|turnover|data_gap_refs|no code implementation" docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md
```

验证结果：plan 在所有关键位置正确引用了这些术语，且在非目标中明确排除了不相关内容。

```bash
git diff --check
```

验证结果：无 whitespace 错误。

## 8. Open Questions

无。所有 open questions 已在 findings 中覆盖或确认为 plan 正确处理。

## 9. Residual Risks

| Residual | Risk | Tracking destination |
|----------|------|---------------------|
| Exact model file placement undecided | Implementation could scatter models | Future code gate owner |
| Existing `EvidenceAnchor.source_kind` is narrower than future source taxonomy | Premature enum widening could affect extractors | Future implementation gate |
| Manual review artifact format remains Markdown | Harder machine validation than JSON | Curated-fixture gate |
| Fallback category recovery for `110020`, `017641`, `017970` | Cannot be durable baseline | Source reliability gate |
| Pure FOF missing | Baseline cannot claim all fund-type coverage | Fund-type taxonomy gate |
| Turnover/style stability contract may reveal broader Chapter 3 gaps | Could require more than turnover extraction | Chapter-contract gate |

## 10. Conclusion

**PASS_WITH_FINDINGS**

Plan 整体质量高：正确遵守四层边界和 `FundDocumentRepository` 边界，wrapping 决策合理且理由充分，source boundaries 和 stop conditions 覆盖完整，不假装未来 runtime 已存在，turnover/chapter_contract 处理正确优先 wording constraints。

4 个 findings 中 2 个中等（review_status 转换语义缺失、locator_hash 规格不足）、2 个低（chapter_contract candidate 升级、Slice 2 多锚点映射细化）。均为契约补充或规格细化，不构成结构性阻断。建议 controller 在下一步 implementation gate 前要求 plan 作者补充 review_status 转换条件和 locator_hash 算法规格。
