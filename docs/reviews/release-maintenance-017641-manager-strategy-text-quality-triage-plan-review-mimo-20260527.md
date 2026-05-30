# 017641 Manager Strategy Text Quality Triage Plan — MiMo Review

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Plan artifact: `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-20260527.md`
> Gate: `017641 manager_strategy_text extraction/quality triage gate`
> Review type: plan review
> Verdict: **PASS**

---

## Review Scope

Review against:
- `AGENTS.md` (规则真源)
- `docs/design.md` v2.2 当前设计章节
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point
- accepted evidence chain for 017641
- plan artifact 自身引用的 accepted evidence chain

---

## Review Checklist

### 1. Startup Packet / Next Entry Point 对齐

**Result: PASS**

Plan 的 Startup Packet replay 与 control doc 当前状态一致：
- `Current phase: release maintenance` — 正确
- `Current gate: 017641 manager_strategy_text extraction/quality triage gate` — 正确，与 control doc next entry point 对齐
- `Next entry point` 引用 `$init-agents` / tmux multi-agent flow — 与 control doc "must use init-agents / tmux multi-agent flow" 语义一致
- 推荐下一步为 `017641 manager_strategy_text public-only evidence triage gate` — 这是当前 gate 内的合理细分，不违反 next entry point 定位

### 2. 017641 Accepted State 使用正确性

**Result: PASS**

Plan 的 Accepted Evidence Summary 与 accepted evidence chain 完全对齐：

| Field | Plan claim | Evidence source (provenance rerun controller judgment) | Match |
|---|---|---|---|
| `fund_code` | `017641` | accepted | ✓ |
| `report_year` | 2024 | accepted | ✓ |
| `source_strategy` | `primary_then_fallback` | accepted | ✓ |
| `resolved_source_name` | `eastmoney` | accepted | ✓ |
| `fallback_used` | `true` | accepted | ✓ |
| `primary_failure_category` | `unavailable` | accepted | ✓ |
| `fallback_eligibility` | `eligible` | accepted | ✓ |
| `source_provenance_status` | `complete` | accepted | ✓ |
| `quality_gate_status` | `block` | accepted | ✓ |
| Blocking issues | FQ2/FQ3 manager_strategy_text P0, FQ2F P0 | accepted | ✓ |
| Terminal state | `quality_blocked_after_provenance` | accepted | ✓ |
| `promotion_disposition` | `not_promoted` | accepted | ✓ |

Evidence chain 引用的 5 个 artifact 路径均存在于 control doc accepted artifacts 表中。

### 3. Public-Only Evidence Triage 先行推荐的合理性

**Result: PASS**

Plan 推荐先做 public-only evidence triage 而不是直接 extractor implementation，理由充分：

- AGENTS.md 硬约束："找问题的 root cause 一定要逻辑/数据同源，禁止使用间接证据"
- 当前 accepted state 只证明 `017641` 是 quality-blocked（FQ2/FQ3/FQ2F P0），但未证明 root cause 是 extractor gap、disclosure data gap、policy taxonomy issue 还是 replacement need
- 直接跳到 extractor implementation 会从 quality symptoms 推断 root cause，属于间接证据
- Public-only triage 使用现有 public CLI production route through `FundDocumentRepository`，保持 source/fallback 语义不变
- 符合 control doc 中 post-provenance controller judgment 的定位："017641 needs a separate quality/data extraction decision gate for `manager_strategy_text`"

### 4. 禁止直接 PDF/cache/source-helper 访问

**Result: PASS**

Plan 在多处明确禁止：
- "Do not directly inspect PDF files, cache files, source helper internals, source dumps, or downloaded artifacts"
- "Production annual report access must remain through public CLI paths backed by `FundDocumentRepository`"
- "No direct PDF/cache/source-helper inspection"（Forbidden evidence shortcuts）
- Decision Candidates 表中每个 candidate 的 Forbidden scope 均包含此约束
- Stop conditions 包含 "output requires private PDF/cache/source-helper inspection to decide"

### 5. 未弱化 FQ0-FQ6 / 未改 renderer/Service/CLI/source strategy/Host/Agent/dayu / 无 promotion / 无 GitHub mutation

**Result: PASS**

Plan 的 Forbidden scope 完整覆盖：
- "Do not weaken, bypass, or reclassify FQ0-FQ6 quality gate behavior"
- "Do not modify renderer, FQ0-FQ6, Service, CLI, default `analyze` / `checklist`, source strategy, `FundDocumentRepository`, Host, Agent, Dayu runtime, golden fixtures, or baseline fixtures"
- "Do not promote `017641` to durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus"
- "Do not commit, push, open PRs, or mutate branches"
- Non-Entry Statements 再次重述所有禁止项

与 AGENTS.md 模块边界、设计原则、control doc 当前 gate 约束完全一致。

### 6. Public-Only Evidence Triage Matrix 可执行性与可审查性

**Result: PASS**

Matrix 定义了 4 个步骤，每步包含：
- 具体 CLI 命令（`extraction-snapshot --force-refresh`, `extraction-score`, `quality-gate`）
- 必需输出（`snapshot.jsonl`, `summary.md`, `score.json`, `quality_gate.json` 等）
- 明确目的

Step 4 为 public-output inspection，产出 tracked Markdown artifact。

Required tracked evidence artifact 清单明确，包含：
- Startup Packet replay 和 command log
- Source provenance tuple 和 row-consistency check
- Field-level `manager_strategy_text` status
- FQ2/FQ3/FQ2F issue records
- Classification into exactly one terminal state
- `promotion_disposition=not_promoted`

Review matrix 定义 3 个 review role（AgentMiMo / AgentGLM / Controller），scope 明确。

5 个 terminal classifications 覆盖所有合理出口：
1. `extractor_gap_requires_implementation_plan`
2. `disclosure_data_gap_not_baseline_ready`
3. `policy_taxonomy_issue_requires_design_plan`
4. `replacement_or_exclusion_required`
5. `reject_exclude_due_to_evidence_violation`

Stop conditions 有 5 条，覆盖命令失败、provenance 回退、证据不足需要私有检查、审查者报告违规、新增未预期 P0/P1。

足以区分 extractor gap / disclosure data gap / policy taxonomy issue / replacement exclusion / reject exclude。

---

## Findings

**无 material finding。**

以下为 observation（不构成 blocking 或建议修改）：

1. **O1: `$init-agents` vs `init-agents` 术语** — Plan 使用 `$init-agents` shell variable 形式，control doc 使用 `init-agents` 作为 tmux multi-agent flow 标识。语义一致，不构成歧义。

2. **O2: Decision Candidates 表中 `fund_type.py` 出现** — Policy/taxonomy candidate 的 forbidden scope 提到 "no `fund_type.py` changes without separate accepted plan"。当前代码中基金类型定义在 `fund_agent/fund/` 内，`fund_type.py` 是合理的具体文件引用，不构成越界。

3. **O3: 命令中的 `--source-csv docs/code_20260519.csv`** — 该 CSV 路径在之前 accepted evidence artifacts 的命令中已使用过，此处保持一致。非新增硬编码。

---

## Conclusion

Plan artifact 与当前 Startup Packet next entry point 完全对齐；017641 accepted state 被正确使用；public-only evidence triage 先行推荐符合 logic/data same-source root-cause 标准；PDF/cache/source-helper 禁止访问约束完整；未弱化 FQ0-FQ6、未改 renderer/Service/CLI/source strategy/Host/Agent/dayu、无 promotion、无 GitHub mutation；triage matrix 足够可执行和可 review，能区分所有 5 种 terminal classification。

**Verdict: PASS**
