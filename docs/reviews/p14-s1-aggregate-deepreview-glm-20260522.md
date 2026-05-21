# P14-S1 Aggregate Deepreview (AgentGLM)

## Scope

- Mode: current changes (aggregate deepreview)
- Branch: `docs/post-p13-follow-up-planning`
- Base: `origin/main` (merge-base `b7117876985c778b95bfeae5cd9cd9399bbf95e3`)
- Output file: `docs/reviews/p14-s1-aggregate-deepreview-glm-20260522.md`
- Included scope: commits `1908a4f`, `d36b902`, `c7d0ec8`, `85af949`, `6762cfd`, `71087c2` — post-P13 follow-up planning, P14-S1 plan/review, implementation, code review (含 GLM F-1/F-2 fix pass), control doc update
- Excluded scope: `docs/repo-audit-20260521.md`（未跟踪，未触碰）；RR-13 source data
- Parallel review coverage: 无 subagent；主 reviewer 逐一走读全部生产代码变更和关键测试链路

## Conclusion

**PASS_WITH_FINDINGS**

P14-S1 aggregate 整体 ready-to-open-draft-PR 前可接受。所有 planning artifacts、implementation、review artifacts 和 control doc 状态一致；核心约束（conditional P1 denominator、unknown/conflicting conservative、non-index exclusion、dataclass comparable/golden prefill、no ExtractionMode expansion）在代码中已正确实现并由 428 passed 测试覆盖；无跨层边界违规；无阻断问题。

Findings 为低严重度：planning-to-implementation golden field substitution 缺乏显式 rationale 记录。

## Findings

### F-1-未修复-[低]-001548 golden field substitution 未显式记录

- **入口/函数**: `reports/golden-answers/golden-answer.json`、`reports/golden-answers/golden-answer-prefill-reviewed.md`
- **文件(行号)**: plan `p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md` Exact Scope Decisions section 4 规定 4 行 golden rows：`benchmark_identity_status`、`benchmark_index_name`、`methodology_availability`、`constituents_availability`（均为 `medium` confidence）
- **输入场景**: aggregate reviewer 对比 plan 与 implementation 的 001548 golden rows
- **实际分支**: implementation 产出了 4 行 golden rows，但字段为 `benchmark_text`、`benchmark_identity_status`、`benchmark_index_name`、`source_tier`（均为 `high` confidence）
- **预期行为**: plan-review controller judgment 或 implementation artifact 显式记录字段替换的理由和 stop-condition 触发与否
- **实际行为**: implementation artifact 只列出最终字段，未记录 `methodology_availability` / `constituents_availability` 被替换为 `benchmark_text` / `source_tier` 的理由；controller judgment 接受了 confidence 从 medium 升级到 high，但未显式裁决字段替换
- **直接证据**: plan section 4 列出 `methodology_availability = benchmark_only` 和 `constituents_availability = benchmark_only`；实际 `golden-answer.json` 中 `001548` 的 `index_profile` 子字段不包含这两项；implementation artifact 列出的是 `benchmark_text` 和 `source_tier`
- **影响**: 仅文档追溯性影响。字段替换本身合理（implementation 可能发现实际 extractor 输出不含 plan 假设值，且 plan 有 stop condition），但缺乏显式 rationale 使后续 golden expansion 难以判断该 substitution 是否代表 methodology/constituents golden 被有意推迟还是被遗漏
- **建议改法和验证点**: 在 implementation artifact 或 controller judgment 中补一行 substitution rationale；无需改生产代码或 golden files
- **修复风险（低）**: 纯文档补充
- **严重程度（低）**: 不影响生产行为正确性

## Open Questions

无。

## Residual Risk

| Risk | Owner | Blocking for draft-PR |
|---|---|---|
| `tracking_error` production golden correctness 缺失 — 当前无 001548 直接披露跟踪误差的 verified golden row | Controller / future golden evidence slice | 否 |
| enhanced-index production golden 缺失 — `161725` 仅为 deterministic fixture，不在 selected-fund CSV / strict golden 中 | Future selected-fund/golden expansion phase | 否 |
| calculated tracking error 仍缺 | Future data-source/calculation phase | 否 |
| external index series adapter / methodology / constituents extraction 仍缺 | Future source-contract phases | 否 |
| QDII index subtype 仍 unmodeled | Future subtype-design phase | 否 |
| F-1 golden field substitution rationale 未记录 | Controller / docs cleanup | 否（低严重度） |
| `docs/repo-audit-20260521.md` | Controller / user | 否（excluded） |
| RR-13 duplicate `016492` | User / App source | 否（excluded） |

## Aggregate Verification Matrix

### Constraint Verification

| Constraint | Status | Evidence |
|---|---|---|
| Conditional P1 denominator | PASS | `extraction_score.py:100-104` 定义 `INDEX_QUALITY_FIELD_NAMES` 和 `INDEX_QUALITY_APPLICABLE_FUND_TYPES`；`_scorable_records()` / `_is_non_applicable_index_quality_record()` 在 aggregate/fund/fund_quality 三层一致过滤 |
| Unknown/conflicting conservative | PASS | `_is_non_applicable_index_quality_record()` 第 1419-1420 行：`fund_type is None` 时返回 `False`（保留评分）；`_build_fund_score_row()` 使用 `use_record_fund_type=False` 避免 row-level fallback；test `test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts` 覆盖 |
| Non-index exclusion | PASS | `_is_non_applicable_index_quality_record()` 第 1421 行：`fund_type not in INDEX_QUALITY_APPLICABLE_FUND_TYPES` 时返回 `True`（排除） |
| Dataclass comparable/golden prefill | PASS | `_value_utils.py:value_mapping()` 统一 dict/dataclass 规范化；`extraction_snapshot.py:_comparable_values_for_field()` 和 `golden_prefill.py:_sub_field_value()` 均消费该 helper |
| No ExtractionMode expansion | PASS | `extractors/models.py:ExtractionMode = Literal["direct", "derived", "estimated", "missing"]` 未变 |
| FundDocumentRepository boundary | PASS | score/snapshot/golden_prefill/_value_utils 均不 import documents 层或访问 PDF/cache |
| Dayu non-dependency | PASS | 无 dayu import |
| extra_payload ban | PASS | 无 extra_payload 使用 |
| Service/UI/Engine 不直接处理 Fund source internals | PASS | 变更全部在 `fund_agent/fund/` Capability 层 |
| No production tracking_error golden | PASS | `grep "tracking_error" golden-answer.json` 返回 0 条 |
| No calculated tracking error / external adapter | PASS | 代码变更仅涉及 snapshot/score/golden_prefill |
| No methodology/constituents extraction | PASS | comparable sub-fields 包含 `methodology_availability`/`constituents_availability` 作为 status 字段，但无 extraction 逻辑 |

### Artifact Consistency

| Artifact pair | Consistent | Notes |
|---|---|---|
| Control doc ↔ actual gate state | PASS | Startup Packet: `P14-S1 aggregate deepreview`，Active Gate Ledger: P14-S1 implementation accepted at `6762cfd` |
| Plan ↔ implementation | PASS_WITH_FINDINGS | F-1: 001548 golden field substitution；其余所有 scope decision 一致 |
| Implementation ↔ code review controller judgment | PASS | GLM F-1/F-2 fixes verified in re-review |
| Golden JSON ↔ reviewed markdown | PASS | 4 行 `001548 index_profile` 完全对应 |
| Golden JSON ↔ template | PASS | template 新增 4 行 `index_profile` 空行，与 reviewed markdown 字段一致 |
| Test suite | PASS | `428 passed`，`ruff` passed，`git diff --check HEAD` passed |

### Test Coverage Assessment

| Behavioral assertion | Covered | Evidence |
|---|---|---|
| index_fund disclosed path | PASS | `test_p1_sample_matrix.py` 的 `510300` case |
| enhanced_index applicable path | PASS | `test_p1_sample_matrix.py` 的 `161725` case：assert `classified_fund_type == "enhanced_index"` + `tracking_error.extraction_mode == "direct"` |
| Non-index excluded path | PASS | `test_index_quality_fields_are_p1_only_for_applicable_fund_types` |
| Unknown/conflicting conservative | PASS | `test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts` |
| Dataclass comparable values | PASS | `test_build_snapshot_records_serializes_index_quality_dataclass_comparable_values` |
| Golden correctness match/mismatch | PASS | `test_compare_snapshot_correctness_handles_index_quality_comparable_fields` |
| Golden prefill dataclass support | PASS | `test_run_golden_prefill_writes_prefilled_markdown` 使用 `IndexProfileValue` / `TrackingErrorValue` |
| Bool comparable serialization | PASS | `_comparable_scalar` 使用 `str(value)`；plan GLM F-1 要求 `True`/`False` 字符串 |
| Full suite no regression | PASS | 428 passed ≥ 424 baseline（P13 closeout） |

## Not-covered Areas

- `methodology_availability` 和 `constituents_availability` comparable values 的 production golden correctness 未覆盖（无对应 golden row）
- `tracking_error` comparable sub-fields 的 production golden correctness 未覆盖（无对应 golden row）
- 真实 `001548` 年报 PDF 中 `source_tier` 值是否确实为 `benchmark_context` 未由独立证据二次验证（当前依赖 extractor 输出和 reviewed markdown）
