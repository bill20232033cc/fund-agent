# P14-S1 Plan Review — AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Plan 整体可执行，scope、non-goals、slicing、validation matrix、stop condition 和 residual risk owner 均清晰且与 AGENTS.md / design.md / implementation-control.md 一致。发现 6 个 non-blocking findings，其中 2 个建议在实现前修正 plan artifact，4 个为实现时注意项。

## Review Inputs

- Plan artifact: `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md`
- Reference truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`
- Prior planning: `docs/reviews/post-p13-follow-up-planning-20260522.md`, `docs/reviews/post-p13-follow-up-plan-review-controller-judgment-20260522.md`, `docs/reviews/p13-main-branch-closeout-20260522.md`
- Code evidence: `fund_agent/fund/extraction_snapshot.py`, `fund_agent/fund/extraction_score.py`, `fund_agent/fund/quality_gate.py`, `fund_agent/fund/extractors/models.py`, `fund_agent/fund/golden_prefill.py`

## Findings

### F-1: `_build_fund_quality_row` 缺少访问 `classified_fund_type` 的显式路径（建议修正 plan）

**Severity**: medium

Plan Section 1 (FQ2 / ExtractionScore) 要求在 `_build_fund_quality_row()` 的 missing field count / total field count 路径中按 `classified_fund_type` 排除非适用 index quality 字段。但当前 `_build_fund_quality_row(extraction_score.py:1194-1254)` 通过 `_unique_optional_text(records, "classified_fund_type")` 从 snapshot 记录中读取基金类型——这依赖 snapshot 中存在 `field_name=classified_fund_type` 的独立记录。

问题是：`index_profile` / `tracking_error` 的 snapshot 记录本身不携带 `classified_fund_type` 字段值。当 `_build_fund_quality_row` 遍历 `records` 时，它需要先知道当前基金的 `classified_fund_type`，才能决定哪些 index quality 记录应被排除。

当前代码确实有 `_unique_optional_text(records, "classified_fund_type")` 在 `extraction_score.py:1213` 行读取该值，所以技术上可行。但 plan 应明确说明实现时的过滤顺序：先从 records 中解析 `classified_fund_type`，再用它过滤 index quality records 参与 missing/total 计数。目前 plan 只列出了函数名但未描述数据流。

**Required change**: 在 Slice B Exact changes 中补充一句说明：`_build_fund_quality_row` 应先通过现有 `_unique_optional_text(records, "classified_fund_type")` 获取基金类型，再将结果传入 `_scorable_records()` 过滤器；`_missing_fields_by_priority()` 同理需要接收 `classified_fund_type` 参数。

### F-2: `_build_extracted_field_record` 类型签名与 dataclass 值不匹配（建议修正 plan）

**Severity**: medium

`_build_extracted_field_record(extraction_snapshot.py:780-831)` 的参数类型为 `extracted_field: ExtractedField[dict[str, object]]`。当 `index_profile` 的值是 `IndexProfileValue` dataclass（而非 `dict`）时，`getattr(bundle, field_name)` 返回的 `ExtractedField[IndexProfileValue]` 在类型检查上与 `ExtractedField[dict[str, object]]` 不兼容。

当前代码通过 `getattr(bundle, field_name)` 在运行时传递（duck typing），所以不会 crash，但 `_comparable_values_for_field()` 内部调用 `value.get(sub_field)` 只对 `dict` 有效，对 dataclass 会抛 `AttributeError`。

Plan Slice A 提到了 "Add helper to normalize dataclass or dict structured values to a mapping" 和 "Update `_comparable_values_for_field()` to support dataclass values via `dataclasses.asdict()` or a small helper"，这是正确的。但 plan 的 Affected Files 列表中没有 `extractors/models.py`，且未明确说明是否需要更新 `_build_extracted_field_record` 的类型签名。

**Required change**: 在 Slice A 的 Non-goals 或 Stop condition 中补充：如果 `_build_extracted_field_record` 类型签名需要从 `ExtractedField[dict[str, object]]` 放宽为 `ExtractedField[object]` 或使用 `Union`，这是可接受的最小类型调整，不属于 extractor model 范围扩展。或者明确 `_comparable_values_for_field` 内部的 dataclass→dict 转换足以绕过类型问题。

### F-3: `partial` extraction mode 未在 plan 中讨论

**Severity**: low

Plan Section 2 声明 `ExtractionMode` 保持 `direct / derived / estimated / missing` 不变。但 `extraction_snapshot.py:1076` 的 `_normalize_extraction_mode()` 还处理 `partial` 模式。Plan 未说明 `index_profile` / `tracking_error` 是否可能产出 `partial` 模式（例如部分子字段抽取成功），以及如果产出，quality denominator 应如何处理。

**Required change**: 无需修正 plan。实现时注意：如果 P13 extractor 对这两个字段可能输出 `partial`，它在 snapshot 层会被保留为 `partial`，score 层应视为非 missing（`value_present` 由 snapshot 构造逻辑决定）。这是当前行为的自然延伸，不需要额外设计。

### F-4: Golden build 工作流命令未显式说明

**Severity**: low

Plan Slice C 要求 "Rebuild `reports/golden-answers/golden-answer.json` using existing golden-build workflow"，但未给出具体命令。实现者可能不确定是 `fund-analysis golden-build`、直接 Python 调用还是其他方式。

**Required change**: 无需修正 plan（实现者可通过 grep `golden-build` 或阅读 `golden_prefill.py` / CLI 入口确认）。但建议在 Slice C Validation 中补充一条提示：golden-build 命令可通过 `fund-analysis golden-build --help` 确认。

### F-5: `quality_gate.py` 在 allowed / not-allowed 列表中的矛盾表述

**Severity**: low

Plan Affected Files 的 Allowed tests 包含 `tests/fund/test_quality_gate.py`，而 Slice B 的 Allowed files 说 "quality_gate.py only if tests prove no way to preserve FQ2 semantics within extraction_score.py; preferred path does not edit quality gate"。这两个表述实际上不矛盾（tests 可以修改，production 代码优先不改），但阅读时容易混淆。

**Required change**: 无需修正。实现者应遵循 Slice B 的约束：优先不改 `quality_gate.py`，只在测试证明必须改时才动。

### F-6: `_comparable_values_for_field` 当前只接受 `dict` 值

**Severity**: low（与 F-2 关联）

`extraction_snapshot.py:1010-1039` 中 `_comparable_values_for_field(field_name, value)` 的 `value` 参数类型为 `dict[str, object] | None`。当 `index_profile` / `tracking_error` 的值是 dataclass 时，`value.get(sub_field)` 不可用。

Plan Slice A 已经识别了这个问题并提出了解决方案（`dataclasses.asdict()` 或 helper）。这是一个实现细节，不需要 plan 层面的额外决策，但实现者需要在 Slice A 中优先解决此问题，否则 Slice C 的 golden prefill 也会失败。

**Required change**: 无需修正 plan。Slice A 的 stop condition 已覆盖此场景："If dataclass comparable extraction requires changing extractor model types, stop and report"。

## Boundary Compliance Check

| 边界约束 | 状态 | 证据 |
|---|---|---|
| FundDocumentRepository 是年报唯一入口 | PASS | Plan 不引入新的文档访问路径 |
| 不依赖 Dayu runtime / Host / Engine / tool loop | PASS | Non-goals 明确排除 |
| 不引入 LLM / Evidence Confirm | PASS | Non-goals 明确排除 |
| 不计算 tracking error / 不引入外部指数数据 | PASS | Non-goals 和 scope 均明确 |
| 不做 QDII subtype redesign | PASS | Non-goals 明确排除 |
| 不修改 RR-13 / repo-audit | PASS | Non-goals 明确排除 |
| 不改变 CLI 用户入口 | PASS | Non-goals 明确排除 |
| 不扩大 ExtractionMode enum | PASS | Section 2 明确保持不变 |
| 基金类型判断优先于通用分析 | PASS | Applicability matrix 按 classified_fund_type 决策 |
| 证据必须可溯源 | PASS | Golden rows 必须有 source 列 |
| FQ2 P1 fail 仍为 warn | PASS | Plan 明确不改 quality_gate.py severity |

## Positive Observations

1. **State transition table 完整**：Section 1 的 5 种输入组合覆盖了 applicable / non-applicable / unknown 三种路径，包括 unknown fund type 必须 remain scorable 的保守策略。
2. **Comparable sub-fields 选择合理**：只包含 stable scalar fields，排除 Decimal/tuple/list，与 `_comparable_scalar()` 行为一致。
3. **Golden stop condition 明确**：如果 `001548` 实际值与 proposed values 不符，必须停止编辑 production golden files 并报告 controller。
4. **Fixture 策略务实**：`510300` 用于 sample matrix，`001548` 用于 production golden，`161725` 用于 enhanced_index deterministic test，各司其职。
5. **Validation matrix 全面**：覆盖 snapshot、score、quality gate、golden、integration、ruff、full suite 和 diff check。
6. **Residual risk owner 清晰**：每个 deferred item 都有明确的 destination phase。

## Verdict Summary

Plan 可进入 implementation。建议在实现前修正 F-1（`_build_fund_quality_row` 数据流说明）和 F-2（类型签名兼容性说明），以减少实现者的歧义。其余 findings 为实现时注意项，不阻塞。

## Recommended Next Gate

```text
P14-S1 implementation
```
