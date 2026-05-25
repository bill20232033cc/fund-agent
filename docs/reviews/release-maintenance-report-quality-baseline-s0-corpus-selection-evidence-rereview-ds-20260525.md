# 发布维护 报告质量基线 S0 Corpus Selection Evidence Re-Review (DS)

> 日期: 2026-05-25
> 复审者: AgentDS（phaseflow 独立审核代理，re-review）
> 分支: `codex/v0-release-readiness-plan`
> Gate: `release-maintenance report-quality baseline / Fact-Evidence contract plan accepted locally`
> 复审工件: `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md`（Codex 补丁后）
> 原始审核: `docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-review-ds-20260525.md`
> 范围: 复核补丁，不完整重新审核

## 裁决

**PASS** — 原始审核全部 3 项发现已解决（2 项修复，1 项正确推迟）。Fallback 未知失败类别问题已得到实质性加强。未引入新问题。可进入 controller judgment。

---

## 原始发现处置

### F-1 (MEDIUM): async `load_annual_report` — 已解决

- **原始问题**: 工件将 `FundDocumentRepository().load_annual_report(code, year, force_refresh=False)` 显示为同步调用；实际仓库方法是异步的（`repository.py:290`），且探针在不可验证的被忽略路径中。
- **补丁位置**: 第 32 行
- **补丁内容**: `async repository access: the probe enters an async context through asyncio.run(...) and then awaits FundDocumentRepository().load_annual_report(code, year, force_refresh=False)`
- **评估**: 已解决。工件现在明确说明 `asyncio.run()` 包装器。第 116 行 `rg` 验证确认 `asyncio.run` 存在于工件中。未来读者能理解实际的异步仓库调用契约。
- **状态**: 已关闭。

### F-3 (LOW): `DocumentKey` 简写 — 已解决

- **原始问题**: `DocumentKey(fund_code=004393, year=2024, annual_report)` 使用了无引号字符串、前导零整数、缺失 `document_kind=` 字段名，与 dataclass repr 不一致。
- **补丁位置**: 第 41–47 行（所有 `DocumentKey` 出现）
- **补丁内容**: 现在使用规范形式 `DocumentKey(fund_code="004393", year=2024, document_kind="annual_report")` — 有引号的字符串、正确的字段名、显式的 `document_kind` 参数。
- **评估**: 已解决。所有 5 处出现（`004393`、`110020`、`004194`、`006597`、`017641`、`017970`）现在与 `fund_agent/fund/documents/models.py:315` 的 `DocumentKey` dataclass 字段匹配。`fof_fund` `007721` 的验证状态行（第 46 行）在 prose 描述而非 `DocumentKey` repr 中仍使用自然语言——在上下文中可接受，因为那一行的验证状态特意是 `verified_as_annual_report_but_type_gap`，而非直接的 `verified`。
- **状态**: 已关闭。

### F-2 (LOW): `repository verification status` 词汇 — 已推迟至 S1

- **原始问题**: `verified_as_annual_report_but_type_gap` 将文档身份与基金类型槽位成员资格混合在单个字段中；S1 应将其拆分为独立字段。
- **补丁**: 工件中无更改。
- **评估**: 正确推迟。这是一个 S1 score-schema 设计问题，而非 S0 证据工件问题。原始审核承认：“当前工件适当地披露了差距（`review state: candidate`、`source failure category: data_gap`），但词汇将来可能会被误用。”工件通过在 `repository verification status`（描述性）和 `review state`（`candidate`）以及 `source failure category`（`data_gap`）之间保持分离来正确处理此事。
- **状态**: S1 未完成。

### 额外加强: Fallback 未知失败类别 — 实质性改进

这并非一项原始发现，而是在我原始审核中标记的一个关注点（“东方财富 fallback 原始失败类别未保留”在开放问题表中，以及第 108 行原始残余风险条目）。Codex 实施的补丁远不止记录这一点：

**补丁 1 — 显式来源失败类别**:
- 第 42 行（`110020`）: `source failure category` 从 `n/a` 改为 `unknown_upstream_failure_category`
- 第 45 行（`017641`）: 同上，`n/a` → `unknown_upstream_failure_category`
- 第 47 行（`017970`）: 从 `data_gap` 改为 `data_gap; unknown_upstream_failure_category for fallback source`

**补丁 2 — 每个 fallback 条目明确注明**:
- 第 42 行、第 45 行、第 47 行均包含: `repository metadata only preserves fallback source/result, not original upstream failure category in this S0 probe`

**补丁 3 — 强化 S1 前提条件**:
- 第 108 行，`Required next handling` 从咨询性升级为强制性:
  - 旧: `S1/source gate should preserve original failure categories when selecting durable corpus.`
  - 新: `S1 entry gate precondition: before durable baseline selection, source boundary / source reliability evidence must recover the original upstream failure category, or the fallback candidate must be excluded from the durable baseline corpus.`

**评估**: 这体现了正确的 fail-closed 行为。`unknown_upstream_failure_category` 是一个合法的观察性类别——它承认 fallback 成功但我们不知道为什么主源失败。如果没有原始失败类别，在 AGENTS.md fallback taxonomy 下，我们无法确认 fallback 是否合法（`not_found`/`unavailable`）还是非法（`schema_drift`/`identity_mismatch`/`integrity_error`）。S1 前提条件正确地要求：要么恢复原始类别，要么从持久语料库中排除该条目。这与我原始审核推荐和 AGENTS.md 硬约束一致。

---

## 无新增发现

复审未发现补丁引入任何新问题。具体来说：

- `unknown_upstream_failure_category` 并非 AGENTS.md 中的标准失败类别——它是工件创建的一个观察性标记，用于表示“我们知道这被 fallback 使用了，但我们不知道上游原因”。这是一个准确的描述，且不违反失败分类体系（该体系为来源层决策定义了 5 种类别）。它是对未知信息的诚实承认，而非在分类体系中引入新类别。
- `source failure category` 对于 fallback 条目现在有值（`unknown_upstream_failure_category`），对于非 fallback 条目（`004393`、`004194`、`006597`）为 `n/a`，对于 FOF 类型差距条目（`007721`、`017970`）为 `data_gap`。语义一致。
- 第 108 行中的 `S1 entry gate precondition` 表述赋予 S1 一个明确的、可验证的职责，完全在 S1 的范围内。它不要求 S0 完成额外工作。
- 所有其他边界（FundDocumentRepository、无渲染器/质量门控/Host/Agent 更改、忽略运行路径）保持不变。

---

## 最终裁决与建议

**裁决: PASS。** 直接进入下一 gate 或 controller judgment。

S0 工件在补丁后已满足 `docs/implementation-control.md` Next Entry Point 和控制器判决中为该 gate 设定的所有要求。语料库表现在完整具备：每种基金类型的异步仓库调用路径可追溯、正确的 `DocumentKey` repr、用于 fallback 条目的显式 `unknown_upstream_failure_category` 标记，以及要求恢复或排除的强制性 S1 前提条件。

建议的下一个状态: controller judgment → 接受 S0 → 进入 `report-quality-baseline S1 score-schema fixture draft`。

## 验证

```text
rg -n 'DocumentKey|asyncio.run|unknown_upstream_failure_category|durable baseline selection' docs/reviews/release-maintenance-report-quality-baseline-s0-corpus-selection-evidence-20260525.md
```

所有补丁术语均在工件中存在并被考虑。

此工件无需 `pytest` 或 `ruff`——复核仅限文档，不做代码更改。
