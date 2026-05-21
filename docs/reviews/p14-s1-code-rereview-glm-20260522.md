# Code Re-Review (Targeted)

## Scope

- Mode: targeted re-review
- Branch: `docs/post-p13-follow-up-planning`
- Base: `main`
- Output file: `docs/reviews/p14-s1-code-rereview-glm-20260522.md`
- Reviewed findings: GLM F-1 / F-2 (`docs/reviews/p14-s1-code-review-glm-20260522.md`)、MiMo F-001 (`docs/reviews/p14-s1-code-review-mimo-20260522.md`)
- Included scope: `fund_agent/fund/extraction_score.py`（F-1 fix）、`fund_agent/fund/_value_utils.py`（新增，F-2 fix）、`fund_agent/fund/extraction_snapshot.py`（F-2 fix import）、`fund_agent/fund/golden_prefill.py`（F-2 fix import）、`tests/fund/test_extraction_score.py`（F-1 新增测试）、`fund_agent/fund/README.md`（F-2 文档同步）
- Excluded scope: 未修改的 golden answer 文件、`docs/repo-audit-20260521.md`

## Conclusion

**PASS**

GLM F-1 和 F-2 / MiMo F-001 均已正确关闭，未引入回归。

## Finding Disposition

### F-1 (GLM) — `_build_fund_score_row` 冲突类型不一致 — 已关闭

**修复验证**：

`_build_fund_score_row`（`extraction_score.py:1116-1130`）现在：
1. 先通过 `_unique_optional_text(records, "classified_fund_type")` 解析基金级类型
2. 将解析值传入 `_scorable_records(records, classified_fund_type=resolved, use_record_fund_type=False)`
3. 将解析值同时传入 `_score_records_for_single_fund(scorable_records, thresholds=..., classified_fund_type=resolved, use_record_fund_type=False)`

数据流与 `_build_fund_quality_row`（`:1240-1250`）完全一致：先解析、后过滤、同参数。

`_score_records_for_single_fund` 签名新增 `classified_fund_type: str | None = None` 和 `use_record_fund_type: bool = True` 参数（`:1158-1159`），内部 `_scorable_records` 调用使用传入参数（`:1177-1181`）。

**新增测试直接验证冲突路径**：

`test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts` 构造两条记录（basic_identity 携带 `"active_fund"`、index_profile 携带 `"bond_fund"`），触发 `_unique_optional_text` 冲突（返回 `None`），断言：
- `fund_score.records == 2`（index_profile 保守保留）
- `fund_score.p1_failed_fields == ("index_profile",)`
- `fund_quality.total_field_count == 2`（一致）
- `fund_quality.missing_p1_fields == ("index_profile",)`（一致）

两条路径在冲突场景下行为完全一致，F-1 关闭。

### F-2 (GLM) / F-001 (MiMo) — `_value_mapping` 重复定义 — 已关闭

**修复验证**：

新增 `fund_agent/fund/_value_utils.py`，定义公共 `value_mapping(value: object) -> Mapping[str, object] | None`。模块特性：
- 仅 import stdlib（`dataclasses.asdict`、`dataclasses.is_dataclass`、`typing.Mapping`）
- 无 Service / Engine / Runtime / UI 依赖
- 模块名单下划线前缀 `_value_utils`，明确 Capability 内部工具，不污染 public API

`extraction_snapshot.py:22` 和 `golden_prefill.py:16` 均改为 `from fund_agent.fund._value_utils import value_mapping`，旧的两个本地 `_value_mapping` 定义已删除。消费点（`extraction_snapshot.py:1050`、`golden_prefill.py:324`）调用名从 `_value_mapping` 改为 `value_mapping`。

`fund_agent/fund/README.md:350` 新增文档行描述 `_value_utils.py` 用途。

F-2 / F-001 关闭。

### MiMo F-002 — confidence medium→high — 不需修复（信息项）

MiMo 和 GLM review 均确认 confidence 提升有 reviewed evidence 支撑（具体页码引用 `年报2024 §2 page-6 page-6-table-0 benchmark`），plan 明确允许 "unless implementer verifies exact PDF pages and can safely promote to high"。正确关闭。

## Regression Check

| 检查项 | 结果 |
|---|---|
| `tests/fund/` 相关 53 测试 | 53 passed |
| 全量测试套件 | 428 passed（427 + 1 新测试，无回归） |
| ruff lint | All checks passed |
| `git diff --check HEAD` | 无输出（通过） |
| ExtractionMode 未扩展 | `extractors/models.py:10` 保持 `Literal["direct", "derived", "estimated", "missing"]` |
| 无新增 tracking_error 生产 golden | `golden-answer.json` 中 tracking_error records = 0 |
| 未触碰 `docs/repo-audit-20260521.md` | git status 确认仍为 `??`（untracked） |
| 无跨层依赖 | `_value_utils.py` 仅 stdlib import；`extraction_score.py`、`extraction_snapshot.py`、`golden_prefill.py` 无反向 import |
| README 同步 | `fund_agent/fund/README.md` 已记录 `_value_utils.py` |

## Open Questions

- 无。

## Residual Risk

- 无新增 residual risk。原有 residual（tracking_error 生产 golden 缺失、enhanced_index 生产 golden 缺失、methodology/constituents 可比子字段无生产 golden）仍存在，但均为 P14-S1 计划中明确 defer 的项。
