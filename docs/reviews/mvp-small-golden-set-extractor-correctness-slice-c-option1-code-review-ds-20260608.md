# Code Review

## Scope

- Mode: current changes (workspace review of untracked mini-slice files)
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: N/A (reviewing untracked new files against accepted plan/reconciliation artifacts)
- Output file: `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option1-code-review-ds-20260608.md`
- Included scope:
  - `docs/reviews/mvp-small-golden-set-extractor-correctness-source-identity-evidence-20260608.md` (untracked)
  - `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option1-implementation-evidence-20260608.md` (untracked)
  - `tests/fund/test_small_golden_set_source_identity.py` (untracked)
- Excluded scope:
  - `tests/fixtures/fund/small_golden_set/*/expected_fields.json` (unchanged, verified no diff from HEAD)
  - `fund_agent/` (unchanged, verified no diff from HEAD)
  - `docs/reviews/mvp-small-golden-set-manifest-20260608.json` (unchanged, already accepted at Slice A checkpoint `a94c705`)
- Parallel review coverage: 无

## Findings

### 1-未修复-低-source_identity.reason 字段只校验存在性，未校验非空

- **入口/函数**: `_assert_unmatched_synthetic_shape()` → `test_matched_rows_require_complete_source_document_identity()` → `test_unmatched_synthetic_rows_remain_non_correctness_fixtures()`
- **文件(行号)**: `tests/fund/test_small_golden_set_source_identity.py:129`
- **输入场景**: 任一 unmatched synthetic 行的 `source_identity.reason` 被设为空字符串 `""` 或 JSON `null`
- **实际分支**: `assert "reason" in source_identity` 仅检查 key 存在性，空字符串和 `None` 均可通过
- **预期行为**: reason 字段应当包含非空诊断信息，便于后续 worker 或 reviewer 理解该行为何未能匹配
- **实际行为**: 空字符串或 `None` reason 不会触发断言失败，诊断信息可能静默丢失
- **直接证据**: `test_small_golden_set_source_identity.py:129` — `assert "reason" in source_identity` 无值校验；对比同文件 `:101-102` matched 路径的 `for field_name in MATCHED_REQUIRED_IDENTITY_FIELDS: assert source_identity[field_name] not in ("", None)` 有明确非空校验
- **影响**: 仅诊断信息丢失，不影响 fail-closed 行为边界；future worker 可能面对空 reason 无法快速判断行状态
- **建议改法和验证点**: 在 `_assert_unmatched_synthetic_shape` 中将 `assert "reason" in source_identity` 改为 `assert isinstance(source_identity.get("reason"), str) and source_identity["reason"].strip() != ""`；重新运行 `uv run pytest tests/fund/test_small_golden_set_source_identity.py -q` 确认通过
- **修复风险（低）**: 仅收紧断言，不改变 fixture 或生产行为；当前五行 fixture reason 均为非空字符串，修复后应继续通过
- **严重程度（低）**:

## Open Questions

1. **Matched 路径断言未被执行验证**：`_assert_matched_identity_shape()`（`test_small_golden_set_source_identity.py:74-103`）及其在 `test_matched_rows_require_complete_source_document_identity`（`:166-171`）中的调用分支当前无任何行触发。所有五行均为 unmatched，因此 matched 路径的全部 12 行断言从未被实际执行。静态审查确认断言逻辑与 Slice C reconciliation plan §3 要求的 matched identity 字段集合一致，但无法通过执行结果证明断言本身无逻辑错误（如 typo、key 名错误、比较方向反转）。Option 1 的 "found no matched identity" 结果使此路径天然不可达；当 future worker 首次添加 matched 行时，该路径将首次被执行。建议 future worker 在添加 matched 行前先以临时 fixture 验证 matched 路径断言正确性。

2. **Evidence artifact 与 fixture metadata 无自动交叉校验**：source identity evidence artifact 中的 row decisions 表（行级 `decision=unmatched`）与 `tests/fixtures/fund/small_golden_set/*/expected_fields.json` 中的 `source_identity.status=unmatched_synthetic` 字段之间无自动化测试确保一致性。当前两者一致（均为 unmatched），但若 future worker 单独更新 fixtures 而忘记更新 evidence artifact，不一致将不会被检测。当前 Slice C reconciliation plan 未要求此类交叉校验。

## Residual Risk

- **Matched 路径首次执行风险**：`_assert_matched_identity_shape()` 断言未被任何测试覆盖执行，存在断言逻辑错误在首次 matched 行出现时才暴露的残余风险。缓解：静态审查确认断言集合与 reconciliation plan §3 要求字段一致；future worker 应在添加 matched 行前以临时 fixture 验证。
- **Reason 字段值质量无保障**：如 Finding 1 所述，当前不校验 reason 值非空。当前五行 fixture reason 均为有效非空字符串，不影响当前状态。
- **无 extractor correctness 测试覆盖**：按设计，Slice C Option 1 不产生 `test_small_golden_set_extractor_correctness.py`（因无 matched 行可驱动 exact/numeric 断言）。extractor correctness 的测试覆盖仍为空白，需等待 matched source identity 建立后的后续 slice。此残余已由 Slice C reconciliation plan §3 显式记录为 Option 2 fallback 或后续 matched-row slice 的职责。

## Reviewer Self-Check

- [x] review mode、base/PR、included/excluded scope 和 source evidence 已写清
- [x] 每个 finding 绑定具体 code location，root cause 使用直接证据
- [x] findings 为 material、可执行，无 style/nit/speculation
- [x] adversarial pass 已完成（见下方）
- [x] open questions 和 residual risk 已记录
- [x] output path 位于 `docs/reviews/`，文件名符合指定格式

### Adversarial Failure Pass Summary

沿以下维度逐项检查，未发现可触发 blocking 的 failure：

| 维度 | 检查结果 |
|---|---|
| 错误 matched identity 声明 | fail-closed：`MATCHED_REQUIRED_IDENTITY_FIELDS.isdisjoint(source_identity)` on unmatched rows |
| fallback 语义漂移 | fail-closed：`fallback_invocation == "prohibited"` + `fallback_used is False` 双断言 |
| promotion 语义漂移 | fail-closed：`promotion_allowed is False` + `"promotion_allowed" not in source_identity` + `"quality_gate_promotion" not in source_identity` |
| exact/numeric correctness 泄漏 | fail-closed：top-level `exact_numeric_correctness_allowed is False` + field_group `assertion_kind not in EXACT_OR_NUMERIC_ASSERTIONS` 双重校验 |
| 行集合漂移 | fail-closed：`test_source_identity_guard_keeps_exact_five_rows` 严格五行 |
| 生产代码/提取器变更 | 已验证：`git diff --name-only HEAD -- fund_agent/` 无输出 |
| fixture 文件变更 | 已验证：`git diff --name-only HEAD -- tests/fixtures/` 无输出 |
| live import 泄漏 | 已验证：测试文件仅 import `json`, `pathlib.Path`, `typing.Any` |
| 证据来源为 untracked workspace residue | 已验证：每个 row decision 均引用具体 accepted review artifact 路径 |

**Verdict: PASS_WITH_NON_BLOCKING_FINDINGS**

Mini-slice 正确应用了 accepted provenance rule，五行均从具体 accepted/pre-existing offline evidence 判定为 unmatched，test 在所有关键边界 fail-closed，无生产代码、提取器、fixture、provider/runtime/config 变更，无 live/network/fallback 活动。Finding 1（reason 字段非空校验缺失）为低严重度诊断改进，不阻塞 gate 推进。
