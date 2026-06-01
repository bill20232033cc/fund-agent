# MVP Provider Runtime Budget and Prompt-Cost Calibration Plan

> **日期**: 2026-05-31
> **分类**: `heavy` — 改变 provider runtime budget 策略、prompt 构造和 writer prompt cost；直接影响 Gate B real provider smoke acceptance
> **规则真源**: `AGENTS.md`
> **设计真源**: `docs/design.md`
> **控制真源**: `docs/implementation-control.md`

---

## 1. 问题陈述

### 1.1 当前症状

Real provider `006597 / 2024 --use-llm` smoke 的唯一主 blocker 为 `provider_runtime_timeout`：

| 章节 | 失败操作 | 失败分类 | approx prompt tokens |
|------|---------|---------|---------------------|
| 1 | writer | `llm_timeout` | — |
| 2 | writer | `llm_timeout` | ~26086 |
| 3 | auditor | `llm_timeout` | — |
| 5 | auditor | `llm_timeout` | — |
| 6 | writer | `llm_timeout` | ~29078 |

6 个章节中仅 chapter 4 accepted；final assembly incomplete；stdout 空；无 deterministic fallback。

### 1.2 Root Cause（同源证据链）

**Root Cause 1 — Writer prompt 过重**：

`chapter_writer.py:build_chapter_prompt()` 把以下内容全部 JSON 序列化进 `user_prompt`：

- `_prompt_fact_payload()`（行 1318-1343）：序列化每个 fact 的 `fact_id`、`source_field_id`、`source_field_name`、`status`、**完整 `value`**（含所有数值、嵌套 dict/list）、`evidence_anchor_ids`、`missing_reason`、`required_by`
- `_prompt_anchor_payload()`（行 1346-1371）：序列化每个 anchor 的 `anchor_id`、`source_kind`、`document_year`、`section_id`、`table_id`、`row_locator`、`note`
- `_json_text(contract.must_answer)`：全部 must answer 文本
- `_json_text(contract.must_not_cover)`：全部 must not cover 文本
- `_json_text(_prompt_required_output_payload(contract.required_output_items))`：每个 item 带 exact marker

Chapter 2（R=A+B-C 收益归因）和 Chapter 6（核心风险与否决项）的 facts 最多——包含净值数据、业绩归因、风险检查、压力测试等大量数值字段，完整序列化后 prompt 分别约 26086/29078 tokens（`ceil(chars/4)` heuristic）。

**Root Cause 2 — Runtime timeout budget 不足**：

- 默认 `FUND_AGENT_LLM_TIMEOUT_SECONDS = 60.0`（`config/llm.py:19`）
- 默认 `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS = 2`（行 20）
- 60s × 2 attempts = 最多 120s wall time
- 29k prompt tokens 的推理 + 12k output chars 的生成在 MiMo 兼容 provider 上需要远超 60s per attempt

**Root Cause 3 — 未向 provider 发送 `max_tokens`**：

`llm_provider.py:_chat_payload()`（行 423-444）只发送 `model` + `messages`，不发送 `max_tokens`。Provider 无法做输出预算规划，可能生成过多或过少后停止。

### 1.3 因果链

```
prompt fact/anchor 全量序列化 → 26k-29k prompt tokens
  → 60s default timeout 不足 → writer/auditor llm_timeout
    → 6 章仅 4 accepted → final assembly incomplete → exit 1
```

---

## 2. 设计约束

### 2.1 不改变

- Gate 1 `ChapterFactProjection` / `ChapterFactInput` schema
- Gate 2 `chapter_writer` / `chapter_auditor` 的 public Protocol 和 contract
- Gate 3 `ChapterOrchestrator` 编排逻辑
- Gate 4 Slice 4A/4B/4C/4D 的 public contract
- 确定性 `fund-analysis analyze/checklist` 默认路径
- Provider construction `openai_compatible` over `httpx` 的协议选择
- fail-closed 语义（missing config → exit 1；incomplete LLM → exit 1；无 deterministic fallback）
- Writer anchor marker / missing marker / required output marker 的 parser 和 contract
- Auditor line protocol `SEVERITY|LOCATION|MESSAGE` 的 strict parse
- 安全诊断 serializer（不输出 prompt/draft/raw response/API key/Authorization）
- 现有 test suite 的 test 行为（只允许扩展和调整 fixture）

### 2.2 允许改变

- Writer prompt 构造：`build_chapter_prompt()` 中 `_prompt_fact_payload()` 和 `_prompt_anchor_payload()` 的序列化策略
- Provider runtime config 默认值：`timeout_seconds`、`timeout_max_attempts` 的默认值和上限
- Provider HTTP payload：`_chat_payload()` 增加 `max_tokens` 字段
- Config validation：`LLMProviderConfig` 新增 `writer_max_tokens` 和 `auditor_max_tokens` typed config

### 2.3 不引入

- Provider fallback / multi-model writer-auditor split / retry beyond timeout
- Host/Agent/dayu runtime
- Quality gate / golden / score / snapshot / readiness / promotion 变更
- CHAPTER_CONTRACT / preferred_lens / ITEM_RULE 语义变更
- 模板结构变更

---

## 3. 实施方案

### Slice 1 — Writer prompt fact/anchor compaction

**目标文件**: `fund_agent/fund/chapter_writer.py`

**变更**:

1. 新增 `_compact_fact_payload()` 替换 `_prompt_fact_payload()`：
   - 只序列化写作必需字段：`fact_id`、`status`、**`value` 的数值摘要**（而非完整嵌套结构）、`missing_reason`
   - `value` 摘要策略：
     - `str`：原样保留（如基金名称、类型）
     - `int` / `float` / `Decimal`：保留数值 + 单位提示
     - `dict`：只保留顶层 key-value，嵌套结构展平为 `"key1:val1; key2:val2"` 格式
     - `list` / `tuple`：只保留前 5 项 + "...(N items total)"
     - `bool`：`"是"/"否"`
     - `None` / missing：`"未披露"`
   - 移除 `source_field_id`、`source_field_name`、`evidence_anchor_ids`、`required_by`（这些是内部元数据，LLM 不需要）

2. 新增 `_compact_anchor_payload()` 替换 `_prompt_anchor_payload()`：
   - 只序列化 `anchor_id` + `note`（或 `section_id` + `table_id` 的简短组合）
   - 移除 `source_kind`、`document_year`、`row_locator` 等内部字段

3. 更新 `build_chapter_prompt()` 调用新函数

**预期效果**: Chapter 2/6 prompt tokens 从 ~26k-29k 降至 ~8k-12k（约 60-70% 压缩）

**测试**:
- 更新 `tests/fund/test_chapter_writer.py` 中涉及 prompt payload 的 snapshot assertion
- 新增 compact_payload 单元测试验证各种 value 类型的摘要行为
- 确保所有 marker/contract 验证逻辑不变（prompt 内容变了但 writer contract 不变）

### Slice 2 — Provider max_tokens hint

**目标文件**: `fund_agent/services/llm_provider.py`

**变更**:

1. `_chat_payload()` 增加 `max_tokens: int | None = None` 参数：
   - 非 `None` 时在 payload 中加入 `"max_tokens": max_tokens`
   - `None` 时不发送（保持向后兼容）

2. `OpenAICompatibleChapterLLMClient._complete()` 从 `cost_context.max_output_chars` 推算 `max_tokens`：
   - 使用 `ceil(max_output_chars / 2)` 作为 `max_tokens` 估算（中文约 2 char/token）
   - Writer 传 `max_tokens`；auditor 不传（auditor 输出为结构化行协议，长度可控）

3. `_writer_cost_context()` 和 `_auditor_cost_context()` 无需变更（已有 `max_output_chars`）

**预期效果**: Provider 能做输出预算规划，避免生成过长被截断或生成过短

**测试**:
- 更新 `tests/services/test_llm_provider.py` 中 `_chat_payload` 测试验证 `max_tokens` 字段
- `MockTransport` 验证 request body 包含 `max_tokens`（writer）/ 不包含（auditor）

### Slice 3 — Runtime timeout budget calibration

**目标文件**: `fund_agent/config/llm.py`

**变更**:

1. 修改默认值：
   - `_DEFAULT_TIMEOUT_SECONDS`: `60.0` → `120.0`
   - `_MAX_TIMEOUT_SECONDS`: `300.0` → `600.0`（10 分钟上限）
   - 保持 `timeout_max_attempts` 默认 `2` 不变

2. 理由：
   - Slice 1 压缩 prompt 后，120s × 2 attempts = 最多 240s wall time 足以覆盖 ~12k prompt tokens + 生成
   - 若 Slice 1 未充分压缩（fallback scenario），600s 上限允许用户手动调高到 10 分钟
   - 保持 `timeout_backoff_seconds` 默认 `1.0` 不变

**预期效果**: 大幅降低 `llm_timeout` 概率，同时保持有界 retry

**测试**:
- 更新 `tests/config/test_llm_config.py` 中默认值断言和边界测试
- 验证 env override 仍然工作

### Slice 4 — Integration verification

**无新代码变更**。使用 Slice 1-3 完成后的代码执行以下验证：

1. `ruff check fund_agent/ tests/`
2. `uv run pytest tests/fund/test_chapter_writer.py tests/services/test_llm_provider.py tests/config/test_llm_config.py tests/services/test_chapter_orchestrator.py -v`
3. `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`（全量回归）
4. 确定性 smoke：`fund-analysis analyze 006597 --report-year 2024` 确认不回归
5. Missing config fail-closed：`fund-analysis analyze 006597 --report-year 2024 --use-llm`（无 env）确认 exit 1 + 空 stdout
6. **Real provider smoke**: `fund-analysis analyze 006597 --report-year 2024 --use-llm`（完整 env）观察 runtime diagnostic

---

## 4. 验证矩阵

| 验证项 | 方法 | 通过标准 |
|--------|------|---------|
| Ruff lint | `ruff check` | 零 finding |
| Writer prompt compaction 单测 | pytest | compact_payload 正确摘要各种 value 类型 |
| Writer prompt marker/contract 不变 | 现有 test_chapter_writer | 全部 PASS |
| Provider max_tokens 单测 | pytest MockTransport | writer body 含 max_tokens；auditor body 不含 |
| Config 默认值 | pytest | timeout=120, max=600 |
| Config env override | pytest | env 仍可覆盖 |
| Orchestrator regression | pytest | 全部 PASS |
| 全量回归 | pytest --cov | ≥50% global, 无 regression |
| 确定性 smoke 不回归 | CLI | exit 0, 8 章 0-7 |
| Missing config fail-closed | CLI | exit 1, 空 stdout |
| Real provider smoke 改善 | CLI + diagnostic | timeout 概率显著降低；至少 4/6 章 accepted 或 timeout 不再是唯一主 blocker |

---

## 5. 风险与残余

| 风险 | 缓解 |
|------|------|
| Prompt 压缩后 LLM 写作质量下降 | `_compact_fact_payload` 保留关键数值和文本；移除的只是内部元数据（`source_field_id`、`evidence_anchor_ids`、`required_by`），不影响写作语义 |
| `max_tokens` 估算不准 | 使用保守的 `ceil(max_output_chars / 2)`；中国模型通常中文 token ratio 更高，这会给出偏大的 max_tokens，让模型有足够空间 |
| 默认 timeout 120s 仍不够 | `_MAX_TIMEOUT_SECONDS` 上限提升到 600s，用户可通过 env 调高；Slice 1 prompt 压缩是主要改善手段 |
| Real provider smoke 仍不完全通过 | 本 gate 只解决 `provider_runtime_timeout` blocker；programmatic audit C2 是下一个已知 blocker，需后续 gate |
| PR #21 状态 | 保持 draft/open；本 gate 不改变外部状态 |

---

## 6. 边界检查

- [x] 不违反 §1.3 非目标
- [x] 保持 `UI -> Service -> Host -> Agent` 四层边界
- [x] 生产年报访问仍只通过 `FundDocumentRepository`
- [x] 不在确定性主链路误拼接 Host/tool loop/LLM 写作
- [x] Dayu runtime 不引入
- [x] 工程基线不变（Python ≥3.11, setuptools, pyproject.toml）
- [x] CI `--cov-fail-under=50` 仍守住
- [x] 不改变 quality gate / golden / score / readiness / promotion
- [x] 不改变 final judgment 语义
- [x] 不改变 Host/Agent/dayu 引用
- [x] Success signal 可验证：real provider smoke diagnostic 中的 `approx_prompt_tokens` 下降 + `provider_runtime_timeout` 不再是主 blocker
