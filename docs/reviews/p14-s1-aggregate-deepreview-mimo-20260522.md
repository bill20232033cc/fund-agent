# P14-S1 Aggregate Deepreview — AgentMiMo（2026-05-22）

## Verdict

`PASS`

## Scope

- Mode: current changes
- Branch: `docs/post-p13-follow-up-planning`
- Base: `origin/main` (merge-base `b7117876985c778b95bfeae5cd9cd9399bbf95e3`)
- Output file: `docs/reviews/p14-s1-aggregate-deepreview-mimo-20260522.md`
- Included scope: commits `1908a4f`, `d36b902`, `c7d0ec8`, `85af949`, `6762cfd`, `71087c2` — full diff of P14-S1 planning, plan review, implementation, code review, control doc updates, and all review artifacts
- Excluded scope: `docs/repo-audit-20260521.md` (pre-existing untracked file, untouched)
- Parallel review coverage: 无

## Review Method

Aggregate deepreview 按以下顺序执行：

1. 读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md` 确认设计真源和控制约束。
2. 读取全部 planning / plan-review / implementation / code-review / controller-judgment artifacts，确认 gate 链完整性。
3. 读取完整 diff（`origin/main...HEAD`），逐文件走读生产代码变更。
4. 验证当前 `ExtractionMode` 未被扩展、golden answer JSON 结构一致性、全量测试 `428 passed`、ruff 通过、`git diff --check HEAD` 通过。
5. 对照 plan 约束和 code review 裁决，检查是否有未关闭的 finding 或未覆盖的行为断言。

## Findings

未发现实质性问题。

## Open Questions

无。

## Aggregate Consistency Verification

### 1. Gate 链完整性

| Gate | Artifact | Status | Controller |
|---|---|---|---|
| post-P13 follow-up planning | `post-p13-follow-up-planning-20260522.md` | accepted | `post-p13-follow-up-plan-review-controller-judgment-20260522.md` |
| P14-S1 plan-review | `p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md` | accepted | `p14-s1-plan-review-controller-judgment-20260522.md` |
| P14-S1 implementation/code review | `p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md` | accepted | `p14-s1-code-review-controller-judgment-20260522.md` |

所有 plan review findings（MiMo F-1 至 F-6，GLM F1 至 F2）已在 re-review 中关闭。所有 code review findings（GLM F-1 fund type conflict，GLM F-2 duplicate value_mapping，MiMo 001 重复 helper，MiMo 002/GLM O-1 golden confidence promotion）已在 fix pass 中关闭。

### 2. Plan → Implementation 一致性

| Plan Decision | Implementation Evidence | Consistent? |
|---|---|---|
| `ExtractionMode` 不扩展 | `fund_agent/fund/extractors/models.py:10` 仍为 `Literal["direct", "derived", "estimated", "missing"]` | ✅ |
| `index_profile` / `tracking_error` 加入 `FIELD_PRIORITY_BY_NAME` 为 P1 | `fund_agent/fund/extraction_score.py` 新增两条 P1 条目 | ✅ |
| 条件化：只对 `index_fund` / `enhanced_index` 适用 | `_scorable_records()` + `_is_non_applicable_index_quality_record()` 实现 `INDEX_QUALITY_APPLICABLE_FUND_TYPES` 过滤 | ✅ |
| 非指数基金排除 | `active_fund` / `bond_fund` / `qdii_fund` / `fof_fund` 的 `index_profile` / `tracking_error` 记录被过滤出分母 | ✅ |
| 未知/冲突基金类型保守计分 | `_is_non_applicable_index_quality_record` 在 `fund_type is None` 时返回 `False`（不排除）；conflict 测试 `test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts` 覆盖 | ✅ |
| `COMPARABLE_SUB_FIELDS_BY_FIELD` 增加精确子字段 | diff 确认 7 个 `index_profile` 子字段和 10 个 `tracking_error` 子字段与 plan 一致 | ✅ |
| `_comparable_values_for_field` 支持 dataclass | 通过 `_value_utils.value_mapping()` 规范化 dict/dataclass 后读取子字段 | ✅ |
| Golden 只增加 `001548` `index_profile` 行 | `golden-answer.json` 新增 4 条 `001548` `index_profile` 记录，0 条 `tracking_error` 记录；`record_count` 121→125 | ✅ |
| plan 列出 6 行 golden，实现只加 4 行 | plan 的 stop condition 允许实现时只添加有 reviewed evidence 支持的行；`methodology_availability` 和 `constituents_availability` 未添加为证据不足的审慎决策，code review controller 接受 | ✅ |
| `510300` 只用于 sample matrix | `test_p1_sample_matrix.py` 继续使用 `510300`，未写入生产 golden | ✅ |
| `161725` enhanced-index fixture | `test_p1_sample_matrix.py` 新增 `161725` 样本，含 §1/§2 分类/index_profile 和 §3 直接披露 tracking_error | ✅ |
| `_value_utils.py` 保持 Fund Capability 内部 | 文件位于 `fund_agent/fund/_value_utils.py`，只被 `extraction_snapshot.py` 和 `golden_prefill.py` 导入 | ✅ |

### 3. 硬约束遵从

| 约束 | Evidence | Status |
|---|---|---|
| 生产年报访问经 `FundDocumentRepository` | P14-S1 不引入新的文档来源访问路径 | ✅ |
| Dayu 非依赖 | 未引入外部 Dayu 引用 | ✅ |
| `extra_payload` 禁令 | 未使用 `extra_payload` 传递参数 | ✅ |
| Service/UI/Engine 不直接处理 Fund source internals | `_value_utils.py` 在 `fund_agent/fund/` 内部，snapshot/score/golden 均在 Capability 层 | ✅ |
| `ExtractionMode` 不扩展 | 已确认 enum 不变 | ✅ |
| 非指数基金不被误计为质量失败 | `test_index_quality_fields_are_p1_only_for_applicable_fund_types` 覆盖 active/bond/QDII/FOF 排除路径 | ✅ |
| 未知/冲突类型保守计分 | `test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts` 覆盖 | ✅ |

### 4. Golden Answer / Reviewed Markdown / Docs 一致性

- `golden-answer-prefill-reviewed.md` 新增 4 行 `001548` `index_profile`：`benchmark_text`、`benchmark_identity_status`、`benchmark_index_name`、`source_tier`，全部 `high` confidence。
- `golden-answer.json` 包含完全对应的 4 条记录，`record_count` 121→125，`fund_count` 6 不变。
- `golden-answer-template.md` 新增对应的 4 行模板。
- top-level `records` 数组和 per-fund `records` 数组一致（125 条，内容相同）。
- 未新增 production `tracking_error` golden 行——符合 plan 约束和 stop condition。
- `fund_agent/fund/README.md` 和 `tests/README.md` 已同步更新当前行为。

### 5. 控制文档状态

- `docs/implementation-control.md` Startup Packet 已更新：branch、gate、next entry point、current phase 均指向 P14-S1 aggregate deepreview。
- Active Gate Ledger 新增 `post-P13 follow-up planning`、`P14-S1 plan-review`、`P14-S1 implementation/code review` 三行 accepted 记录。
- Phase History Index 新增 `P14-S1` 行。
- Archive 新增 `Archive: P14` 段落。
- P13 Archive 段落已更新包含 `post-P13-follow-up-plan-review-controller-judgment` 引用。

### 6. 测试验证

| 验证命令 | 结果 |
|---|---|
| `pytest -q` | `428 passed`（P13 baseline `424`，+4 新测试，符合预期） |
| `ruff check fund_agent tests` | All checks passed |
| `git diff --check HEAD` | 无输出 |

测试增量说明：新增 4 个测试覆盖 index quality 条件化评分、冲突类型保守计分、dataclass comparable 序列化和 index quality correctness 比对。

## Residual Risk

| Risk | Owner | Blocking? |
|---|---|---|
| `tracking_error` 生产 golden 正确性未覆盖（`001548` 无 reviewed direct disclosure 证据） | Future golden evidence slice | 否 |
| Enhanced-index 生产 golden 覆盖缺失（当前仅 deterministic fixture 覆盖） | Future selected-fund/golden expansion | 否 |
| Methodology / constituents 抽取仍缺失 | Future source-contract phase | 否 |
| 计算型 tracking error 仍缺失 | Future data-source/calculation phase | 否 |
| 外部指数 series adapter 仍缺失 | Future source-contract phase | 否 |
| QDII tracking-error 适用性仍未建模 | Future subtype-design phase | 否 |
| E1-E3 / Evidence Confirm 仍缺失 | Future audit architecture phase | 否 |
| `docs/repo-audit-20260521.md` 保持排除 | Controller / user | 否 |
| RR-13 duplicate `016492` 保持 human-owned | User / App source | 否 |

以上 residual risks 均为已知 deferred items，有明确 owner，不阻断 ready-to-open-draft-PR。

## Ready-to-open-draft-PR Assessment

P14-S1 aggregate 满足 ready-to-open-draft-PR 条件：

1. Planning artifacts、implementation、review artifacts、control doc 状态完全一致。
2. 代码满足所有 plan 约束：conditional P1 denominator、unknown/conflicting conservative、non-index exclusion、dataclass comparable/golden prefill、no ExtractionMode expansion。
3. 无跨层边界违规：`_value_utils.py` 在 Fund Capability 内部，snapshot/score/golden 均在 Capability 层消费。
4. Golden answer JSON 与 reviewed markdown 一致，未新增 production tracking_error golden。
5. 全量测试 `428 passed`，ruff 通过，`git diff --check HEAD` 通过。
6. 所有 residual risks 有明确 owner，无阻断项。
