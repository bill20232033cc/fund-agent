# P14-S1 PR Review — AgentMiMo（2026-05-22）

## Scope

- Mode: PR
- PR: #9
- Title: P14-S1 index quality denominators
- Author: bill20232033cc
- Head: `docs/post-p13-follow-up-planning`
- Base: `main`
- URL: https://github.com/bill20232033cc/fund-agent/pull/9
- Output file: `docs/reviews/p14-pr-review-mimo-20260522.md`
- Included scope: PR 9 完整 diff（36 files），含 planning artifacts、review artifacts、production code、tests、golden answers、docs
- Excluded scope: `docs/repo-audit-20260521.md`（untracked，未纳入 PR）
- CI status: `test` passed (14s)
- Parallel review coverage: 无

## Conclusion

**PASS**

PR 9 严格限于 post-P13 planning 与 P14-S1 quality-denominator scope。所有核心约束在代码中已正确实现，全量测试 428 passed，ruff 通过，无阻断问题。PR body、control doc、review artifacts、CI 状态一致，满足 draft-PR-pass 条件。

## Findings

未发现实质性问题。

## Verification Matrix

### 1. PR scope 是否严格限于 post-P13 planning 与 P14-S1 quality-denominator

**PASS。** PR diff 包含 36 个文件：

- Production code（5 files）：`extraction_score.py`、`extraction_snapshot.py`、`golden_prefill.py`、`_value_utils.py`、`golden-answer.json`
- Docs（3 files）：`golden-answer-template.md`、`implementation-control.md`、`golden-answer-prefill-reviewed.md`
- READMEs（2 files）：`fund_agent/fund/README.md`、`tests/README.md`
- Tests（5 files）：`test_extraction_snapshot.py`、`test_extraction_score.py`、`test_golden_prefill.py`、`test_quality_gate.py`、`test_p1_sample_matrix.py`
- Review artifacts（21 files）：post-P13 planning + P14-S1 plan/review/implementation/code-review/aggregate 全链路

无 `docs/design.md`、root `README.md`、`extractors/models.py`、Service/UI/Engine 层文件、source CSV、RR-13 数据变更。符合 plan 约束的 allowed files 列表。

### 2. index_profile / tracking_error conditional P1 denominator 逻辑

**PASS。** 经独立代码走读确认：

- `extraction_score.py:49-50`：`FIELD_PRIORITY_BY_NAME` 新增 `index_profile: P1` 和 `tracking_error: P1`
- `extraction_score.py:100-104`：`INDEX_QUALITY_FIELD_NAMES = ("index_profile", "tracking_error")`，`INDEX_QUALITY_APPLICABLE_FUND_TYPES = ("index_fund", "enhanced_index")`
- `extraction_score.py:1392-1421`：`_is_non_applicable_index_quality_record()` 实现：
  - `index_fund` / `enhanced_index`：返回 `False`（不排除，进入分母）
  - `active_fund` / `bond_fund` / `qdii_fund` / `fof_fund`：返回 `True`（排除）
  - `fund_type is None`（unknown/conflicting）：返回 `False`（保守保留，可评分）
- `extraction_score.py:1116-1130`：`_build_fund_score_row` 先通过 `_unique_optional_text` 解析 fund-level type，再传入 `_scorable_records(..., use_record_fund_type=False)`
- `extraction_score.py:1242-1247`：`_build_fund_quality_row` 使用相同模式

两条路径（fund_score / fund_quality）在冲突场景下行为一致：均保守保留 index quality 字段。回归测试 `test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts` 覆盖。

### 3. dataclass comparable / golden prefill 一致性

**PASS。**

- `extraction_snapshot.py:59-80`：`COMPARABLE_SUB_FIELDS_BY_FIELD` 包含 `index_profile`（7 子字段）和 `tracking_error`（10 子字段），均为稳定标量
- `_value_utils.py`（33 行）：`value_mapping()` 统一处理 `None` → `None`、`Mapping` → return、`is_dataclass` → `asdict()`；仅 import stdlib，无跨层依赖
- `extraction_snapshot.py` 和 `golden_prefill.py` 均从 `_value_utils` import `value_mapping`，无本地重复定义
- `golden_prefill.py:324`：`_sub_field_value` 通过 `value_mapping(extracted_field.value)` 处理 dataclass

### 4. Golden answer JSON / reviewed markdown / template 一致性

**PASS。**

- `golden-answer.json`：`001548` 新增 4 条 `index_profile` 记录（`benchmark_text`、`benchmark_identity_status`、`benchmark_index_name`、`source_tier`），全部 `high` confidence；`record_count` 121→125，`fund_count` 6 不变
- `golden-answer-prefill-reviewed.md`：对应 4 行与 JSON 完全一致，source 均指向 `年报2024 §2 page-6 page-6-table-0 benchmark`
- `golden-answer-template.md`：新增 4 行 `index_profile` 空行模板
- 未新增 production `tracking_error` golden——`grep "tracking_error" golden-answer.json` 返回 0 条，符合 plan stop condition

### 5. 架构边界合规

**PASS。**

| 约束 | 状态 | 证据 |
|---|---|---|
| FundDocumentRepository 边界 | PASS | 无直接 PDF/cache/source 访问 |
| Dayu 非依赖 | PASS | 无 dayu import |
| extra_payload 禁令 | PASS | 无 extra_payload 使用 |
| Service/UI/Engine 不直接处理 Fund source internals | PASS | 所有变更在 `fund_agent/fund/` Capability 层 |
| ExtractionMode 不扩展 | PASS | `extractors/models.py:10` 仍为 `Literal["direct", "derived", "estimated", "missing"]` |
| 分层边界 | PASS | `_value_utils.py` 仅被 Capability 内部模块 import，无反向依赖 |

### 6. PR body / control doc / review artifacts / CI 一致性

**PASS。**

- PR body 列出的 validation commands 和结果与 implementation artifact、aggregate controller judgment 一致
- `docs/implementation-control.md`：Active Gate Ledger 新增 4 行 accepted 记录（post-P13 planning → P14-S1 plan-review → implementation/code review → aggregate deepreview），Phase History Index 新增 P14-S1，Archive 新增 P14 段落
- Review artifacts gate 链完整：plan → plan review → re-review → plan controller judgment → implementation → code review → re-review → code controller judgment → aggregate → aggregate controller judgment
- CI `test` passed (14s)
- 本地验证：`pytest -q` 428 passed，`ruff check` passed，`git diff --check HEAD` passed

### 7. docs/repo-audit-20260521.md 未纳入 PR

**PASS。** `git diff main...HEAD --name-only | grep repo-audit` 返回空；`git status` 显示 `?? docs/repo-audit-20260521.md`（untracked）。PR diff 的 36 个文件中不包含此文件。

## Open Questions

无。

## Residual Risk

| Residual | Owner | Blocking? |
|---|---|---|
| `tracking_error` production golden correctness 缺失（`001548` 无 reviewed direct disclosure 证据） | Future golden evidence slice | 否 |
| Enhanced-index production golden 覆盖缺失（`161725` 仅 deterministic fixture） | Future selected-fund/golden expansion | 否 |
| Methodology / constituents extraction 和 golden correctness 仍缺 | Future source-contract phase | 否 |
| Calculated tracking error 和 external index series adapter 仍缺 | Future data-source/calculation phase | 否 |
| QDII tracking-error subtype 适用性仍未建模 | Future subtype-design phase | 否 |
| E1-E3 / Evidence Confirm 仍缺失 | Future audit architecture phase | 否 |
| RR-13 duplicate `016492` | User / App source | 否 |
| `docs/repo-audit-20260521.md` publication decision | Controller / user | 否 |

以上 residual risks 均为已知 deferred items，有明确 owner，不阻断 draft-PR-pass。

## Draft-PR-Pass Assessment

PR 9 满足 draft-PR-pass 条件：

1. PR diff 严格限于 post-P13 planning 与 P14-S1 quality-denominator scope。
2. `index_profile` / `tracking_error` conditional P1 denominator 实现正确：index/enhanced 适用、non-index 排除、unknown/conflicting conservative。
3. dataclass comparable / golden prefill 路径共享 `_value_utils.value_mapping`，golden answer JSON/reviewed markdown/template 一致。
4. 未新增 production `tracking_error` golden，符合 plan stop condition。
5. 无 FundDocumentRepository、Dayu 非依赖、extra_payload、分层边界违规。
6. PR body、control doc、review artifacts、CI 状态完全一致。
7. `docs/repo-audit-20260521.md` 未纳入 PR。
8. 全量测试 428 passed ≥ 424 baseline，ruff passed，`git diff --check HEAD` passed。
