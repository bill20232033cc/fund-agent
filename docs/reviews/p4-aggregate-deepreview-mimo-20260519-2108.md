# P4 Aggregate Deepreview

## Scope

- Mode: aggregate deepreview (P4-S1 through P4-S4 quality-loop work)
- Branch: `main`
- Base: `main`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`, `docs/implementation-control-p4.md`
- Output file: `docs/reviews/p4-aggregate-deepreview-mimo-20260519-2108.md`
- Included scope:
  - `fund_agent/fund/extraction_snapshot.py`
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/golden_prefill.py`
  - `fund_agent/fund/golden_answer.py`
  - `fund_agent/fund/quality_gate.py`
  - `fund_agent/services/extraction_snapshot_service.py`
  - `fund_agent/services/extraction_score_service.py`
  - `fund_agent/services/golden_prefill_service.py`
  - `fund_agent/services/golden_answer_service.py`
  - `fund_agent/services/quality_gate_service.py`
  - `fund_agent/services/__init__.py`
  - `fund_agent/ui/cli.py` (P4 commands only)
  - `tests/fund/test_extraction_snapshot.py`
  - `tests/fund/test_extraction_score.py`
  - `tests/fund/test_golden_prefill.py`
  - `tests/fund/test_golden_answer.py`
  - `tests/fund/test_quality_gate.py`
  - `tests/services/test_extraction_snapshot_service.py`
  - `tests/services/test_extraction_score_service.py`
  - `tests/services/test_quality_gate_service.py`
  - `docs/implementation-control-p4.md`
  - `docs/reviews/p4-*.md`
  - `reports/extraction-snapshots/` (summary inspection)
- Excluded scope:
  - `fund_agent/fund/extractors/profile.py`, `fund_agent/fund/extractors/manager_ownership.py`, `fund_agent/fund/analysis/consistency_check.py`, `fund_agent/services/fund_analysis_service.py` style_positioning changes (out-of-scope per assignment)
- Parallel review coverage: 无 (single reviewer, scope bounded to P4 quality-loop modules)
- Verification: `20 passed` (P4 quality-loop tests), ruff passed

---

## Findings

### 1-未修复-高-quality gate 未接入报告生成主链路，无法自动阻断低质量报告

- **入口/函数**: `fund_agent/services/fund_analysis_service.py:FundAnalysisService.analyze()`
- **文件(行号)**: `fund_agent/services/fund_analysis_service.py`（整个文件无 quality gate 引用）
- **输入场景**: 用户执行 `fund-analysis analyze 004393` 生成报告
- **实际分支**: `FundAnalysisService.analyze()` 直接编排 `FundDataExtractor.extract()` → P2 分析 → 模板渲染 → 程序审计，不经过 snapshot/score/quality-gate 流程
- **预期行为**: P4 北极星明确要求"报告审计必须能识别低质量输入，避免'形式合格、内容不可用'的报告误导用户"。quality gate 应在报告生成链路中作为阻断点，或至少在报告输出时附加质量信号
- **实际行为**: quality gate 只是独立 CLI 命令 `fund-analysis quality-gate`，需要用户手动执行 snapshot → score → quality-gate 三步链路。`FundAnalysisService.analyze()` 不引用任何 P4 模块。报告可直接输出给用户，不受质量 gate 约束
- **直接证据**: `grep -n "quality_gate\|extraction_snapshot\|extraction_score\|golden_prefill\|golden_answer" fund_agent/services/fund_analysis_service.py` 返回空。`cli.py:128` 的 `analyze` 命令直接调用 `FundAnalysisService().analyze(request)` 后输出 `result.report_markdown`，无质量 gate 检查
- **影响**: P4 核心目标"防止形式合格、内容不可用的报告进入产品可用状态"在当前骨架中未实现。quality gate 是 opt-in 而非 enforced，依赖用户主动执行三步 CLI 链路
- **建议改法和验证点**:
  - 方案 A（轻量）: 在 `FundAnalysisService.analyze()` 返回的 `FundAnalysisResult` 中附加 extraction snapshot 质量信号，CLI 输出时在报告末尾附加质量 gate 状态
  - 方案 B（完整）: 将 snapshot → score → quality-gate 链路集成到 Service 层，P0 fail 时在报告头部附加阻断警告
  - 验证: 用 `004393`（当前 P0 `fee_schedule` 为 fail）执行 `analyze`，确认输出包含质量警告或阻断信号
- **修复风险（低/中/高）**: 中（需要决定集成深度和用户体验）
- **严重程度（高）**: 直接影响 P4 北极星是否达成

### 2-未修复-中-004393 known_failure 测试覆盖已死代码路径

- **入口/函数**: `tests/fund/test_extraction_snapshot.py:test_004393_known_failure_classification_is_captured()`
- **文件(行号)**: `tests/fund/test_extraction_snapshot.py:226-259`，`fund_agent/fund/extraction_snapshot.py:1046`
- **输入场景**: 测试使用 `_FakeExtractor` 构造 `classified_fund_type="index_fund"` 的 bundle
- **实际分支**: `_record_note()` 检查 `fund_code == "004393" and classified_fund_type == "index_fund"` → 追加 known_failure note
- **预期行为**: 测试应覆盖生产代码中真实可达的路径
- **实际行为**: P4-S3a 已将 `004393` 修复为 `active_fund`。生产代码中 `_record_note()` 的 `004393 + index_fund` 分支已不可达。测试仍通过是因为 fake bundle 硬编码 `index_fund`，测试的是已修复状态的回放，不是真实回归路径
- **直接证据**: `extraction_snapshot.py:1046` 条件 `selected_fund.fund_code == "004393" and classified_fund_type == "index_fund"` 在 P4-S3a 后的生产路径中永远为 `False`。测试 `test_004393_known_failure_classification_is_captured` 使用 `_build_bundle("004393", "index_fund")` 绕过了真实 extractor
- **影响**: 测试给 false confidence — 看起来在保护 004393 的 known failure 记录，实际保护的是已不存在的代码路径。如果 `004393` 回归到 `index_fund`，应由 snapshot/score 流程检测，而非硬编码 note
- **建议改法和验证点**:
  - 移除 `_record_note()` 中的硬编码 `004393` 特判，改为通用机制：当 `app_category`（如"国内股票类"）与 `classified_fund_type`（如"index_fund"）明显冲突时追加 note
  - 测试改为验证通用冲突检测，而非特定基金代码
  - 或者：保留 known_failure note 作为历史记录，但更新测试为回归测试（使用 P4-S3a 修复后的真实 `active_fund` 值）
- **修复风险（低/中/高）**: 低
- **严重程度（中）**: 测试有效性问题，不影响生产正确性

### 3-未修复-中-quality gate 测试覆盖薄弱

- **入口/函数**: `tests/fund/test_quality_gate.py`
- **文件(行号)**: `tests/fund/test_quality_gate.py`（仅 2 个测试，118 行）
- **输入场景**: quality gate 消费 `score.json`
- **实际分支**: 测试仅覆盖 P0 fail → block 和 P1 fail → warn 两个路径
- **预期行为**: quality gate 作为报告质量阻断点，应覆盖：全通过场景、P2 fail 静默通过、`field_scores` 缺失、字段行缺少必需键、混合 P0+P1 fail、`correctness` 字段缺失等边界
- **实际行为**: 缺少以下场景测试：
  - 全字段 pass → gate 为 pass
  - P2 fail → gate 仍为 pass（确认 P2 不触发阻断或警告）
  - `score.json` 缺少 `field_scores` 键 → 应抛出 ValueError
  - 字段行缺少 `field_name` / `priority` / `status` → 应抛出 ValueError
  - `correctness` 字段不存在时不应追加 FQ0 issue
  - 混合 P0 fail + P1 fail → gate 为 block（P0 优先）
- **直接证据**: `test_quality_gate.py` 仅包含 `test_run_quality_gate_blocks_failed_p0_fields` 和 `test_run_quality_gate_warns_failed_p1_without_blocking`
- **影响**: quality gate 的防御性边界未被测试锁定，后续修改可能引入静默失效
- **建议改法和验证点**: 补充上述 6 个场景测试
- **修复风险（低/中/高）**: 低（纯测试补充）
- **严重程度（中）**: 测试覆盖不足，不直接影响生产

### 4-未修复-低-golden_answer 测试覆盖不足

- **入口/函数**: `tests/fund/test_golden_answer.py`
- **文件(行号)**: `tests/fund/test_golden_answer.py`（仅 3 个测试，132 行）
- **输入场景**: `parse_golden_answer_markdown()` 和 `build_golden_answer_json()`
- **实际分支**: 测试覆盖 happy path（正常解析）、校验失败（空 expected_value / 非法 confidence / 缺失 source）、JSON 输出
- **预期行为**: 应覆盖：空 markdown（无基金标题）、同一基金内重复字段、畸形表格行（列数不对）、多基金场景、转义竖线在 JSON 中还原
- **实际行为**: 缺少以下场景：
  - 空 markdown → 应抛出 "未找到任何基金标题"
  - 同一基金重复 `(field, sub_field)` → 应抛出重复错误
  - 3 列或 7 列表格行 → 应抛出 "Markdown 表格必须为 5 列"
  - 多只基金混合有效/跳过/错误行
  - `build_golden_answer_json` 对多基金的 `fund_count` 和 `record_count` 正确性
- **直接证据**: `test_golden_answer.py` 仅 3 个测试函数
- **影响**: golden answer 校验逻辑的边界条件未锁定
- **建议改法和验证点**: 补充上述场景测试
- **修复风险（低/中/高）**: 低（纯测试补充）
- **严重程度（低）**: 校验逻辑本身正确，测试覆盖不足

### 5-未修复-低-_normalize_extraction_mode 静默吞掉未知模式

- **入口/函数**: `fund_agent/fund/extraction_snapshot.py:_normalize_extraction_mode()`
- **文件(行号)**: `extraction_snapshot.py:964-981`
- **输入场景**: 底层 extractor 输出新的 `extraction_mode` 值（如 `"inferred"` 或 `"cached"`）
- **实际分支**: `if extraction_mode in {"direct", "estimated", "missing", "partial"}:` 不匹配 → 走到 `return _EXTRACTION_MODE_MISSING`
- **预期行为**: 未知模式应被记录为异常或原样保留，便于后续分析
- **实际行为**: 任何不在白名单中的 `extraction_mode` 被静默映射为 `"missing"`，不记录原始值
- **直接证据**: `extraction_snapshot.py:979-981`: `return _EXTRACTION_MODE_MISSING` 是兜底分支
- **影响**: 如果 extractor 新增模式（如 `"cached"`），snapshot 会将其记录为 `"missing"`，可能导致 score 覆盖率被低估，且难以发现
- **建议改法和验证点**: 兜底分支记录 `note=f"unknown_extraction_mode:{extraction_mode}"`，或保留原值
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: 当前所有 extractor 只使用 `direct/estimated/missing/derived`，无实际影响

---

## Open Questions

- **quality gate 集成深度**: P4 控制文档 7.3 节说"不改变报告生成主链路"，但 P4 北极星要求"能识别低质量输入，避免误导用户"。当前骨架满足前者但未实现后者。用户期望的集成深度是什么？是报告末尾附加质量信号，还是 P0 fail 时阻断输出？
- **correctness 自动比对时间表**: `golden_answer.py` 已实现 strict JSON 构建与校验，但 correctness 自动比对（将 extractor 输出与 golden answer 逐字段对比）尚未实现。这是 P4 还是 P5 的范围？
- **FQ1/FQ4/FQ5 规则实现时机**: 控制文档 7.2 节列出的 FQ1（基金类型与 App 类别冲突）、FQ4（"数据不足"比例超阈值）、FQ5（preferred_lens 不匹配）是否在 P4 内实现，还是推迟到后续 phase？

---

## Residual Risk

| ID | 风险 | 影响 | 缓解 | Owner |
|---|---|---|---|---|
| P4-DR1 | quality gate 未接入报告生成主链路 | 高 — 低质量报告可直接输出给用户 | 当前作为独立 CLI 命令可用；集成方案待用户裁决 | 后续 quality gate integration slice |
| P4-DR2 | correctness 自动比对未实现 | 中 — golden answer 已有 JSON 但无法自动验证 extractor 输出 | `golden_answer.py` 已完成 JSON 构建校验；比对逻辑待接入 | 后续 correctness slice |
| P4-DR3 | FQ1/FQ4/FQ5 规则未实现 | 中 — quality gate 仅覆盖 coverage/traceability，不覆盖内容冲突 | FQ2/FQ3 已实现为骨架；FQ1/FQ4/FQ5 作为后续规则扩展 | 后续 quality gate rules slice |
| P4-DR4 | 004393 known_failure note 已成为死代码 | 低 — 不影响生产正确性，但维护成本增加 | 测试仍通过（使用 fake bundle）；通用冲突检测机制待建立 | 后续 extractor refinement |
| P4-DR5 | quality gate / golden_answer 测试覆盖薄弱 | 低 — 核心逻辑正确但边界条件未锁定 | 补充测试即可，无架构改动 | 后续 test hardening |
| P4-DR6 | `share_change` 多份额列选择策略 deferred | 低 — 当前按第一列选择，A/C 份额基金可能选错列 | 已在 P4-S3b 裁决中记录为 deferred；owner 明确 | 后续 extractor refinement |

---

## P4 质量闭环整体判断

### 架构边界

P4 模块严格遵守四层架构边界：
- **Capability 层** (`fund_agent/fund/extraction_snapshot.py`, `extraction_score.py`, `golden_prefill.py`, `golden_answer.py`, `quality_gate.py`): 承载所有业务逻辑，使用 Protocol 注入测试替身
- **Service 层** (`fund_agent/services/*_service.py`): 薄包装，显式请求对象，参数校验，委托 Capability
- **UI 层** (`fund_agent/ui/cli.py`): Typer 入口，委托 Service
- 无反向 import，无跨层穿透调用

### 显式参数 vs extra_payload

所有 P4 Service 请求使用 frozen dataclass 显式传递参数。无 `extra_payload` 使用。CLI 通过 Typer 参数显式传入。符合控制文档 4.3 约束。

### 文档仓库访问

所有 P4 模块通过 `FundDataExtractor` 或 `SnapshotExtractor` / `GoldenPrefillExtractor` Protocol 访问数据。无直接 PDF/cache 读取。符合控制文档 4.3 约束。

### 证据可追溯性

snapshot 记录包含 `section_id`、`page`、`table_id`、`row_id`。score 模块统计 `anchor_present`。quality gate 基于 traceability rate 阻断。证据链完整。

### 残余风险 owner 状态

| 控制文档风险 ID | 状态 | 说明 |
|---|---|---|
| P4-R1 (016492 重复) | 已处理 | summary 标红，用户核对 App 源数据 |
| P4-R2 (schema 复杂化) | 未发生 | schema 保持最小 14 字段 |
| P4-R3 (跳过基线) | 已缓解 | P4-S1/S2 先于 P4-S3 执行 |
| P4-R4 (标注成本) | 已缓解 | 第一版只标 P0 字段 |
| P4-R5 (网络波动) | 已缓解 | 离线优先，真实 smoke 单独记录 |
| P4-R6 (dayu-agent 依赖) | 不阻塞 | P4 模块不直接依赖 dayu-agent |

---

## Final Recommendation

**PASS with conditions.**

P4-S1 through P4-S4 的代码实现质量良好：架构边界清晰、显式参数传递、证据可追溯、无 PDF/cache 直读。snapshot → score → golden-prefill → golden-build → quality-gate 流程本身是正确且可复核的。

但存在一个高严重程度的架构 gap：quality gate 未接入报告生成主链路，P4 北极星"防止形式合格、内容不可用的报告误导用户"在当前骨架中仅作为 opt-in CLI 命令存在，不构成自动阻断。

**Pass 条件**:
1. 用户裁决 quality gate 集成深度（Finding 1）
2. 补充 quality gate 和 golden_answer 测试覆盖（Finding 3、4）可在后续 test hardening slice 完成
3. 004393 known_failure 死代码可在后续 extractor refinement 清理（Finding 2）

**不阻塞当前 aggregate deepreview 通过**: 控制文档 7.3 节明确说"不改变报告生成主链路"，当前实现满足该约束。集成深度是后续 slice 的设计决策，不是本 slice 的 defect。
