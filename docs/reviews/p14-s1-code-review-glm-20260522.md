# Code Review

## Scope

- Mode: current changes
- Branch: `docs/post-p13-follow-up-planning`
- Base: `main`
- Output file: `docs/reviews/p14-s1-code-review-glm-20260522.md`
- Included scope: 当前 workspace unstaged diff 中 P14-S1 相关文件：`fund_agent/fund/extraction_score.py`、`fund_agent/fund/extraction_snapshot.py`、`fund_agent/fund/golden_prefill.py`、`tests/fund/test_extraction_score.py`、`tests/fund/test_extraction_snapshot.py`、`tests/fund/test_golden_prefill.py`、`tests/fund/test_quality_gate.py`、`tests/fund/integration/test_p1_sample_matrix.py`、`reports/golden-answers/golden-answer.json`、`reports/golden-answers/golden-answer-prefill-reviewed.md`、`docs/golden-answer-template.md`、`fund_agent/fund/README.md`、`tests/README.md`
- Excluded scope: `docs/repo-audit-20260521.md`；P14-S1 plan / plan-review / controller-judgment / implementation-report artifacts（已单独 review）
- Parallel review coverage: 无 subagent；主 reviewer 全量走读 diff 和关键数据流

## Conclusion

**PASS_WITH_FINDINGS**

P14-S1 实现正确覆盖了计划的核心目标：`index_profile` / `tracking_error` 作为条件 P1 进入 FQ2 coverage、traceability、fund score、fund quality denominator；非指数基金排除；unknown/missing 保守可评分。ExtractionMode 未扩展。`not_applicable` 语义通过 quality-layer applicability 过滤表达，未伪装成 extraction mode。comparable subfields 稳定标量，bool 序列化为 `True`/`False`。golden_prefill 支持 dataclass 值。enhanced_index fixture 覆盖 index_profile 和 tracking_error。

发现 2 个低严重度 findings、1 个观察项。无阻断问题。

## Findings

### F-1-未修复-[低]-`_build_fund_score_row` 单记录类型回退与 `_build_fund_quality_row` 解析类型不一致

- **入口/函数**: `score_fund_records()` → `_build_fund_score_row()` vs `derive_fund_quality_records()` → `_build_fund_quality_row()`
- **文件(行号)**: `fund_agent/fund/extraction_score.py:1116`（`_build_fund_score_row` 调用 `_scorable_records(records)` 使用默认参数） vs `:1222-1226`（`_build_fund_quality_row` 传入 `classified_fund_type=resolved, use_record_fund_type=False`）
- **输入场景**: 同一基金的 snapshot 记录集合中存在多个不同的 `classified_fund_type` 值（冲突情况），且包含 `index_profile` / `tracking_error` 记录
- **实际分支**: `_build_fund_score_row` 路径中 `_scorable_records(records)` 使用默认参数 `classified_fund_type=None, use_record_fund_type=True`，对 index_profile 记录回退到该记录自身的 `classified_fund_type`（如 `"bond_fund"`）进行适用性判断
- **预期行为**: 两个路径在相同冲突输入下应产生一致的适用性判断
- **实际行为**: `_build_fund_score_row` 根据单条记录的 `classified_fund_type` 排除非适用指数质量记录；`_build_fund_quality_row` 使用 `_unique_optional_text` 解析得到的 `None`（冲突）且 `use_record_fund_type=False`，因此保守保留所有指数质量记录。结果是同一基金在 `fund_score` 中 index_profile 可能被排除（不计入 P1 failed），但在 `fund_quality.missing_p1_fields` 中被包含
- **直接证据**:
  - `_build_fund_score_row:1116` 调用 `_scorable_records(records)` 无额外参数 → `_is_non_applicable_index_quality_record:1396-1397` 在 `use_record_fund_type=True` 时读取单条记录的 `classified_fund_type`
  - `_build_fund_quality_row:1222-1226` 传入 `classified_fund_type=classified_fund_type`（由 `:1221` 的 `_unique_optional_text` 解析，冲突时为 `None`）且 `use_record_fund_type=False` → `:1398` 命中 `if fund_type is None: return False`（保守保留）
  - 现有测试 `test_derive_fund_quality_records_marks_conflicting_fund_type_without_first_resolving_lens` 仅覆盖 `fund_quality` 路径，未覆盖 `fund_score` 路径的冲突场景
- **影响**: 正常运行中所有记录来自同一 bundle、`classified_fund_type` 一致，不触发此不一致。仅在人工构造的冲突 snapshot 记录上，`fund_score` 与 `fund_quality` 对同一基金的指数质量字段适用性判断可能不同。`fund_quality` 是 quality gate 的权威判断来源，保守方向正确；`fund_score` 在冲突场景下的非保守行为不影响 gate 判定
- **建议改法和验证点**: 两种修复方向：(a) `_build_fund_score_row` 也先通过 `_unique_optional_text` 解析 `classified_fund_type`，传入 `_scorable_records` 时使用解析值和 `use_record_fund_type=False`；(b) 在 `score_fund_records` 层面先解析 fund-level `classified_fund_type` 再传入。增加冲突场景下 `score_fund_records` 的测试断言
- **修复风险（低）**: 改动只影响 `_build_fund_score_row` 的 `_scorable_records` 调用参数，不影响其他路径
- **严重程度（低）**: 不一致仅在人工构造的冲突场景中触发；正常运行不受影响；fund_quality 路径保守正确

### F-2-未修复-[低]-`_value_mapping` 在 extraction_snapshot.py 和 golden_prefill.py 中重复定义

- **入口/函数**: `extraction_snapshot._value_mapping()` 和 `golden_prefill._value_mapping()`
- **文件(行号)**: `fund_agent/fund/extraction_snapshot.py:1064-1083`、`fund_agent/fund/golden_prefill.py:330-352`
- **输入场景**: 任意需要将 `ExtractedField.value` 从 `dict | dataclass` 规范化为 `Mapping[str, object]` 的调用
- **实际分支**: 两个文件各自定义了完全相同的 `_value_mapping` 函数
- **预期行为**: 按 `AGENTS.md` 规则 "重复逻辑必须抽取为公共函数/类"，应抽取到共享模块
- **实际行为**: 两个模块各持有一份相同实现的私有函数
- **直接证据**:
  - `extraction_snapshot.py:1064-1083`: 检查 `None` → `isinstance(value, Mapping)` → `is_dataclass(value) and not isinstance(value, type)` → `asdict(value)`
  - `golden_prefill.py:330-352`: 完全相同的逻辑和类型签名
- **影响**: 未来如果 `_value_mapping` 的规范化逻辑需要变更（例如支持新的值类型），需要同步修改两个文件，否则行为发散
- **建议改法和验证点**: 抽取到 `fund_agent/fund/` 下的共享工具模块（例如 `fund_agent/fund/_value_utils.py` 或现有内部工具模块），两个文件改为 import。改动后运行完整测试套件验证无回归
- **修复风险（低）**: 纯重构，不改变任何行为
- **严重程度（低）**: 当前行为正确；维护性风险

## Observations

### O-1: 生产 golden answer 子字段与计划指定有偏差

计划（`p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md`）列出的 `001548` index_profile 生产 golden 行为：

| sub_field | planned expected_value | planned confidence |
|---|---|---|
| `benchmark_identity_status` | `identified` | `medium` |
| `benchmark_index_name` | `上证50指数` | `medium` |
| `methodology_availability` | `benchmark_only` | `medium` |
| `constituents_availability` | `benchmark_only` | `medium` |

实际实现的 golden 行为：

| sub_field | actual expected_value | actual confidence |
|---|---|---|
| `benchmark_text` | `上证50指数收益率×95%＋银行活期存款利率（税后） ×5%` | `high` |
| `benchmark_identity_status` | `identified` | `high` |
| `benchmark_index_name` | `上证50指数` | `high` |
| `source_tier` | `benchmark_context` | `high` |

4 行中有 2 行的 sub_field 不同（`benchmark_text`/`source_tier` 替代了 `methodology_availability`/`constituents_availability`），confidence 全部从 `medium` 提升为 `high`。

计划包含 stop condition："如果实施发现 `001548` 当前 extractor 输出与提议值不匹配，在编辑生产 golden 文件前停止并向 controller 报告 blocker"。实施报告未报告 blocker，而是选择了替代的证据支撑子字段。

证据链确认：
- `golden-answer-prefill-reviewed.md` 中的 4 行均有具体页码 source（`年报2024 §2 page-6 page-6-table-0 benchmark`）
- `golden-answer.json` 的 `record_count` 从 121 增加到 125，增量 4 与新增行数一致
- JSON schema `fund-agent.golden-answer.v1` 保持有效
- 无 `tracking_error` 生产 golden 行，符合计划的保守策略

判断：偏差可接受。替代子字段有明确的证据锚点支撑，confidence 提升有页码引用依据。计划 stop condition 的核心意图（不编造 expected values）被遵守。

## Open Questions

- 无。

## Residual Risk

### 测试覆盖

- **正常路径覆盖充分**: `index_fund` 适用、`enhanced_index` 适用、`active_fund` 排除、空字符串保守，4 条路径在 `fund_score` 和 `fund_quality` 中均有断言
- **dataclass comparable 序列化覆盖充分**: `index_profile` 7 个子字段、`tracking_error` 10 个子字段在 snapshot 测试中逐一断言；bool 序列化为 `"True"`/`"False"` 有验证
- **golden correctness 覆盖**: match 和 mismatch 路径均测试（`test_compare_snapshot_correctness_handles_index_quality_comparable_fields`）；bool mismatch 场景已验证
- **golden prefill dataclass 支持**: index_profile 和 tracking_error 的 dataclass 预填在 fake extractor 测试中覆盖
- **enhanced_index fixture**: `161725` 在 P1 sample matrix 中覆盖分类、index_profile 和 tracking_error 的端到端路径
- **冲突 classified_fund_type 的 fund_score 路径未测试**: 现有冲突测试仅覆盖 `fund_quality` 路径。若 F-1 被修复，应同步增加 `score_fund_records` 的冲突场景断言

### 功能残差

- **`tracking_error` 生产 golden 缺失**: P14-S1 计划明确限制为仅添加证据支撑的 `index_profile` 行；`tracking_error` correctness 通过单元测试和 sample matrix 覆盖，但无生产 golden 行。未来需要专门验证 `001548` 是否有直接披露的跟踪误差
- **`methodology_availability` / `constituents_availability` 无生产 golden**: 实施中选择了替代子字段，这两个可比子字段仅通过 snapshot/comparable 测试覆盖
- **`_value_mapping` 重复定义**: 维护性风险，见 F-2

### 架构合规

- **FundDocumentRepository 边界**: 变更文件中无直接 PDF/cache/source 访问，`extraction_score.py`、`extraction_snapshot.py`、`golden_prefill.py` 均只消费 `StructuredFundDataBundle` 或 snapshot 记录 ✓
- **Dayu 非依赖**: 变更文件中无 Dayu 引用 ✓
- **extra_payload 禁令**: 变更文件中无 extra_payload 使用 ✓
- **Capability/Service/Engine/UI 分层**: 所有变更文件均在 `fund_agent/fund/`（Capability 层）内，无跨层反向 import ✓
- **ExtractionMode 未扩展**: `extractors/models.py:10` 保持 `Literal["direct", "derived", "estimated", "missing"]`；`not_applicable` 仅作为 `preferred_lens_status` 字符串常量存在，未伪装为 extraction mode ✓

### 文档同步

- `fund_agent/fund/README.md`: 已更新 snapshot 描述和条件 P1 分母语义 ✓
- `tests/README.md`: 已更新测试描述，包含 P14-S1 覆盖范围 ✓
- `docs/golden-answer-template.md`: 已添加 index_profile 行 ✓
- 未修改 `docs/design.md`（无架构变更）✓
- 未修改 `docs/implementation-control.md`（controller 未单独分配）✓
- 未修改根 `README.md`（无用户入口变更）✓

### 测试基线

- P13 closeout 基线：424 passed
- P14-S1 报告：427 passed（+3）
- 增量解释：`test_extraction_snapshot.py` +1（dataclass comparable 测试）、`test_extraction_score.py` +2（指数质量条件 P1 测试、correctness comparable 测试） ✓
