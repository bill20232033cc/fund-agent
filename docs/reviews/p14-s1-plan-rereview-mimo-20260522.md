# P14-S1 Targeted Re-Review — AgentMiMo（2026-05-22）

## Verdict

`PASS`

F-1 和 F-2 均已在修订后的 plan 中关闭。低优先级实现注意项（F-3 至 F-6）保持 non-blocking。

## Inputs

- Revised plan: `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md`
- Source review: `docs/reviews/p14-s1-plan-review-mimo-20260522.md`

## Findings Disposition

### F-1: `_build_fund_quality_row` 数据流 — CLOSED

Plan Slice B 新增（lines 363-367）：

> - `_build_fund_quality_row()` data flow must remain code-fact aligned:
>   - first obtain `classified_fund_type` via the existing `_unique_optional_text(records, "classified_fund_type")`;
>   - then pass that resolved value into the index-quality scorable-record filtering used for `missing_field_count` and `total_field_count`;
>   - compute missing/total counts from the filtered records, not the original records, so non-applicable `index_profile` / `tracking_error` rows do not inflate missing rate.
> - `_missing_fields_by_priority()` must receive `classified_fund_type`, receive pre-filtered records, or otherwise use equivalent context so it excludes non-applicable index-quality fields consistently with `_build_fund_quality_row()` and `_score_records_for_single_fund()`.

数据流描述完整：先获取类型，再过滤，再计算缺失率。与当前 `_unique_optional_text` 代码路径一致。

### F-2: 类型签名兼容性 — CLOSED

Plan Slice A 新增（lines 308-309）：

> - If `_build_extracted_field_record()` or an equivalent snapshot helper currently types extracted fields as `ExtractedField[dict[str, object]]`, loosening that signature to `ExtractedField[object]`, `ExtractedField[dict[str, object] | IndexProfileValue | TrackingErrorValue]`, or an equivalent protocol/union is allowed as a minimal snapshot typing adjustment. This is not a model-scope expansion and must not change `ExtractedField` or `ExtractionMode`.

明确允许 snapshot 层类型放宽，同时划定了不可触碰的边界（`ExtractedField` 和 `ExtractionMode` 本身不变）。

### F-3 至 F-6: 低优先级实现注意项

保持 non-blocking，无需 plan 层修正。实现者在执行时自然会覆盖这些细节。

## Additional Revision Notes

Plan 还吸收了 GLM review 的两个 findings：

- GLM F-1：Slice A expected assertions 明确了 bool comparable serialization 为 `str(True) == "True"` / `str(False) == "False"`。
- GLM F-2：Slice D 要求 `161725` enhanced-index fixture builder 必须包含 `§1`/`§2`/`§3` 足够分类和字段抽取的内容。

两个补充均合理，增强了 plan 的可执行性。

## Recommended Next Gate

```text
P14-S1 implementation
```
