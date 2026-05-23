# P16 Aggregate Deep Review（AgentGLM, 2026-05-22）

## Verdict

**PASS**

P16 从 post-P15 follow-up planning 到 P16-S2 resumed golden accepted 的完整 evidence-to-golden 链条闭合、scope 严格受控、测试覆盖充分、文档/控制状态准确。无 blocking 或 high severity finding。以下按 6 个 review focus 逐项给出证据。

---

## Review Scope

| Item | Value |
|---|---|
| Aggregate range | `f80affc^..604e2d9` (10 commits) |
| Production code changes | `fund_agent/fund/extractors/profile.py` (P16-S2.1 normalization) |
| Test changes | `tests/fund/extractors/test_profile.py`, `tests/fund/test_golden_answer.py`, `tests/fund/test_extraction_snapshot.py`, `tests/fund/test_extraction_score.py`, `tests/fund/test_quality_gate.py` |
| Golden data changes | `reports/golden-answers/golden-answer-prefill-reviewed.md`, `reports/golden-answers/golden-answer.json` |
| Docs/control changes | `docs/implementation-control.md` + 31 review artifacts |
| Excluded inputs | `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md` — 未读取、未引用 |

---

## Focus 1: Design/Control Compliance

### FundDocumentRepository Boundary

| Check | Evidence | Result |
|---|---|---|
| P16-S1 年报访问 | 只使用 `FundDocumentRepository.load_annual_report()` 和 `FundDataExtractor.extract()`（`docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` line 27-28） | PASS |
| P16-S2.1 production boundary | 五个候选通过 `FundDataExtractor` 验证，`force_refresh=False`，无直接 PDF/cache/source helper 访问（同文件 line 79-103） | PASS |
| No Service/UI/Engine 直连 | P16 diff 中无 `fund_agent/services/`、`fund_agent/ui/`、`fund_agent/engine/` 文件变更 | PASS |

### Dayu Non-dependency

P16 全部 10 个 commit 和 41 个 changed files 中无任何 `dayu`、`Dayu`、`Host`、`Engine tool loop` 导入或运行时依赖。Dayu 保持方法论/历史参考角色。PASS。

### No extra_payload

`git diff f80affc^..604e2d9` 中无 `extra_payload` 模式。PASS。

### Capability Ownership

`index_profile` 抽取、normalization、benchmark 构造全部在 `fund_agent/fund/extractors/profile.py`（Fund Capability 层）。Golden answer 路径由 `fund_agent/fund/golden_answer.py` + `fund_agent/fund/golden_prefill.py` 管理，均属于 Capability。PASS。

### Deterministic MVP Boundaries

无 LLM 写作、无 Host/Engine/tool loop、无 prompt scene registry、无 Evidence Confirm 执行。PASS。

---

## Focus 2: Evidence-to-Golden Chain Completeness

### P16-S1 Evidence Acquisition

| Candidate | `classified_fund_type` | Source | `fallback_used` | `index_profile` | `tracking_error` |
|---|---|---|---|---|---|
| `004194` | `enhanced_index` | EID | `False` | accepted (benchmark_context) | blocked |
| `005313` | `enhanced_index` | EID | `False` | accepted (benchmark_context) | blocked |
| `017644` | `enhanced_index` | EID | `False` | accepted (benchmark_context) | blocked |
| `019918` | `enhanced_index` | EID | `False` | accepted (benchmark_context) | blocked |
| `019923` | `enhanced_index` | EID | `False` | accepted (benchmark_context) | blocked |

Verdict: `PARTIAL_ACCEPTED_INDEX_PROFILE_ONLY`。`tracking_error` 全部 `blocked_no_direct_tracking_error`：target/limit text、manager narrative、benchmark-only text、ambiguous note 均未升级为 direct observed disclosure。PASS。

### P16-S2 Golden Plan → Blocker → Normalization → Resume

| Gate | Status | Key Evidence |
|---|---|---|
| P16-S2 plan | accepted | 25 planned scalar rows（5 funds × 5 sub-fields） |
| P16-S2 implementation | BLOCKED | `017644`/`019918` extractor output 含 embedded newline（`BLOCKED_BEFORE_GOLDEN_EDIT_EXTRACTOR_TEXT_DIFF`） |
| P16-S2.1 plan | accepted | Narrow benchmark-path-only normalization |
| P16-S2.1 implementation | accepted | `974615e`；profile tests 22 passed；full suite 433 passed |
| P16-S2 resumed | accepted | `121ad1f`；25 rows；full suite 439 passed |

链路完整：evidence → plan → blocker → normalization → resumed golden，无跳跃或断点。PASS。

### P16-S2.1 Normalization Correctness

Normalization 实现（`profile.py` line 343-396）：
- 只在 `_build_benchmark()` 路径调用（line 577）
- 创建新 `_MatchedField` 而非 mutate frozen 对象（line 389-396）
- 换行规则：`\r\n`/`\r`/`\n` + 周围横向空白 → 两侧 ASCII 词元间插入空格，其余删除
- `benchmark_text` 和 anchor `note` 同步规范化
- 五个候选 production boundary 验证通过（`017644` 和 `019918` newline 被清理，其余三个保持不变）

PASS。

### P16-S2 Resumed Golden Rows Match Production Extractor Semantics

Verified via `FundDataExtractor.extract(code, 2024)` preflight check（resume artifact line 67）：所有五个 benchmark_text 与 accepted 值精确匹配，无 embedded newline。Golden JSON 重建后 `fund_count=11`，`record_count=150`。PASS。

---

## Focus 3: Golden Correctness / Quality Denominator Soundness

### Strict JSON

Golden JSON 验证结果：

| Metric | Value |
|---|---|
| `fund_count` | 11 |
| `record_count` | 150 |
| Enhanced-index `index_profile` rows | 25（5 funds × 5 sub-fields） |
| Enhanced-index `tracking_error` rows | 0 |
| `benchmark_index_name` rows for enhanced-index | 0 |
| `benchmark_component_text` rows for enhanced-index | 0 |

PASS。

### Comparable Scalar Handling

`test_extraction_snapshot.py` 测试覆盖：composite `IndexProfileValue` 序列化只包含 scalar comparable values，省略 `null`（`benchmark_index_name`）和 tuple（`benchmark_component_text`）。PASS。

### Composite No-synthesis

`test_golden_answer.py` 验证：enhanced-index golden rows 中无 `benchmark_index_name` 行。`_benchmark_index_name()` 函数在 `identity_status != "identified"` 时返回 `None`（`profile.py` line 781），所有五个候选均为 `composite`，不会合成虚假 index name。PASS。

### Quality FQ1

`test_quality_gate.py` 测试覆盖：composite scalar correctness mismatch 触发 FQ1 阻断。PASS。

### Existing 001548 Preservation

Golden JSON 中 `001548` 保留 4 条 `index_profile` rows（与 P14 添加时一致）。`test_golden_answer.py` 显式验证 `001548` rows 不变。PASS。

---

## Focus 4: Scope / Risk

| Prohibited Item | Evidence | Result |
|---|---|---|
| `tracking_error` golden rows | Golden JSON 中五个候选 `te=0` | PASS |
| `benchmark_index_name` rows | Golden JSON 中 `bin=0` | PASS |
| `benchmark_component_text` rows | Golden JSON 中 `bct=0` | PASS |
| Methodology/constituents detail | `methodology_availability=benchmark_only`，`constituents_availability=benchmark_only`，无提取行为 | PASS |
| Calculated index series | 无新计算逻辑 | PASS |
| External adapters | 无新外部依赖或 adapter | PASS |
| LLM audit | 无 LLM 调用 | PASS |
| Evidence Confirm execution | 无 Evidence Confirm 实现 | PASS |
| Direct PDF/cache/source access | 全部通过 `FundDocumentRepository` / `FundDataExtractor` | PASS |
| RR-13 / CSV edits | 无 | PASS |
| `docs/design.md` edits | 无 | PASS |
| README edits | 不需要（公开契约未变） | PASS |
| Branch / PR / external state | 无 | PASS |

无 scope 越界。PASS。

---

## Focus 5: Documentation / Control Readiness

### Startup Packet Accuracy

| Field | Expected | Actual (`docs/implementation-control.md` line 17-19) | Match |
|---|---|---|---|
| Branch | `docs/post-p14-follow-up-planning` | `docs/post-p14-follow-up-planning` | YES |
| Current gate | `P16 aggregate deepreview` | `P16 aggregate deepreview` | YES |
| Next entry point | `P16 aggregate review` | `P16 aggregate review` | YES |

### Active Gate Ledger

P16 全部 7 个 gate entry 均存在且准确（line 127-134）：
1. post-P15 follow-up planning — accepted
2. P16-S1 plan/review — accepted
3. P16-S1 evidence acquisition — accepted/partial
4. P16-S2 plan/review — accepted
5. P16-S2 implementation — accepted/blocked
6. P16-S2.1 plan/review + implementation — accepted
7. P16-S2 resumed implementation — accepted

每个 entry 包含 artifact、commit、validation、residual owner、next action。PASS。

### Open Residuals

| Residual | Owner | Tracking |
|---|---|---|
| Enhanced-index `tracking_error` golden | future evidence gate | Line 182 |
| Full dataclass tuple/null golden semantics | future golden/comparable schema phase | Line 181 |
| Index methodology/constituents extraction | future source-contract phase | Lines 177-178 |
| RR-13 duplicate `016492` | user / App source | Line 175 |
| Source metadata gap for `001548` | future evidence retry | Line 179 |
| Repo-hygiene D-1/D-8/C-5/C-9 | future repo-hygiene phase | Line 186 |

Residuals 与 P16-S1/P16-S2/P16-S2.1 artifacts 一致。PASS。

### README Update Decision

P16 未改变公开 CLI 命令、包架构、Engine/Fund 契约、config 默认值、测试组织或文档模板结构。README 不更新合理。PASS。

---

## Focus 6: Testing Adequacy

| Suite | Result | Scope |
|---|---|---|
| Full `pytest` | **439 passed** in 0.93s | 全部测试 |
| Targeted golden/score/quality | **61 passed** in 0.40s | `test_golden_answer.py`, `test_extraction_snapshot.py`, `test_extraction_score.py`, `test_quality_gate.py` |
| Profile extractor | **22 passed** in 0.36s | `tests/fund/extractors/test_profile.py` |
| `ruff check fund_agent tests` | All checks passed | Lint |
| `git diff --check HEAD` | No whitespace errors | Formatting |

P16 新增测试覆盖：

| Test File | Coverage |
|---|---|
| `test_profile.py` | 5 个 benchmark newline 形态（affected 2 + unaffected 3）+ anchor note 规范化 + composite 语义 + benchmark-only/source-tier 语义 |
| `test_golden_answer.py` | strict JSON 25 planned rows + 禁止非计划字段 + `001548` preservation |
| `test_extraction_snapshot.py` | composite `IndexProfileValue` scalar 序列化 |
| `test_extraction_score.py` | composite scalar correctness match/mismatch |
| `test_quality_gate.py` | composite scalar mismatch 触发 FQ1 |

测试覆盖充分。未跑 integration/smoke 是合理的，因为 P16 未改变 CLI 入口或 Service 层。PASS。

---

## Findings

### F1 (INFO) — `missing_reasons` 硬编码

**Location**: `fund_agent/fund/extractors/profile.py` line 684

```python
missing_reasons=("methodology_not_directly_disclosed", "constituents_not_directly_disclosed"),
```

所有 `benchmark_context` 来源的 index_profile 均硬编码这两个 missing_reason。当前语义正确（methodology/constituents 确实未在年报直接披露），但未来如出现年报直接披露 methodology 的基金，此硬编码需要按基金差异化。不阻塞当前 gate。

### F2 (INFO) — Golden-build skipped count

P16-S2 resumed implementation 记录 `golden-build` output `skipped: 29`。这是预期行为（非指数基金 `index_profile` 行被跳过），但未来 phase 如改变 golden Markdown 结构，应验证此数字稳定。不阻塞当前 gate。

### F3 (INFO) — `_normalize_benchmark_text` 潜在过度规范化

**Location**: `fund_agent/fund/extractors/profile.py` line 343-363

规范化函数处理 benchmark 路径中所有 `\r\n`/`\r`/`\n` 片段。对于当前五个 production candidate 均验证正确。理论上，如果未来出现多行 benchmark 文本（如含合法换行的复杂 benchmark），此函数会将其展平为单行。当前风险可控：benchmark 来源是 §2 表格单元格，PDF 表格单元格内换行几乎总是视觉换行。不阻塞当前 gate。

---

## Residual Risks

| Risk | Severity | Owner | Mitigation |
|---|---|---|---|
| Enhanced-index `tracking_error` production golden 持续 blocked | Medium | future evidence gate | P15-S1A + P16-S1 均确认无 direct observed disclosure；需等待年报格式变化或新数据源 |
| `benchmark_index_name=null` 在 composite 场景下的 golden 覆盖缺口 | Low | future golden/comparable schema phase | 当前 scalar 覆盖已足够检测 regression；null active golden 需要新 comparable 语义 |
| `_normalize_benchmark_text` 对未来多行 benchmark 的潜在影响 | Low | future extractor phase | 当前五个 candidate 验证通过；新 fund type 出现时应在 extractor phase 显式处理 |

---

## Suggested Next Gate

P16 aggregate deepreview accepted 后，建议进入 **P16 draft PR gate**：
- 将 `docs/post-p14-follow-up-planning` 分支推送到 GitHub
- 创建 draft PR
- 走 PR review / CI / merge 流程

需用户授权后执行。

---

## Validation Commands Summary

| Command | Result |
|---|---|
| `.venv/bin/python -m pytest -q` | 439 passed |
| `.venv/bin/python -m pytest tests/fund/test_golden_answer.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q` | 61 passed |
| `.venv/bin/python -m pytest tests/fund/extractors/test_profile.py -q` | 22 passed |
| `.venv/bin/python -m ruff check fund_agent tests` | All checks passed |
| `git diff --check HEAD` | No whitespace errors |
| Golden JSON: `fund_count=11`, `record_count=150`, 5 candidates × 5 rows = 25 new, 0 tracking_error, 0 benchmark_index_name, 0 benchmark_component_text, 001548 preserved | Verified |

---

## Reviewer Limitation

本 review 基于 P16 commit range `f80affc^..604e2d9` 的 diff、artifact 文本、production golden JSON 验证和 test suite 执行。未逐条重新执行 P16-S1 的 `FundDataExtractor.extract()` 调用来独立确认五个候选的 raw extractor output（该验证已在 P16-S1 和 P16-S2.1 production boundary check 中完成，review 信任这些已 accepted 的验证结果）。未做 PDF 原文交叉核验（属于 Evidence Confirm v2 scope）。
