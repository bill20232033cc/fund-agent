# P4 Aggregate Deepreview — AgentDS

## Scope

- Mode: aggregate deepreview (P4 quality-loop work, P4-S1 through P4-S4)
- Branch: `main`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`, `docs/implementation-control-p4.md`
- Output file: `docs/reviews/p4-aggregate-deepreview-ds-20260519.md`
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
  - `fund_agent/ui/cli.py` (P4 commands)
  - `tests/fund/test_extraction_snapshot.py`
  - `tests/fund/test_extraction_score.py`
  - `tests/fund/test_golden_prefill.py`
  - `tests/fund/test_golden_answer.py`
  - `tests/fund/test_quality_gate.py`
  - `tests/services/test_extraction_snapshot_service.py`
  - `tests/services/test_extraction_score_service.py`
  - `tests/services/test_quality_gate_service.py`
  - `docs/implementation-control-p4.md`
  - `fund_agent/fund/data_extractor.py` (facade verification)
- Excluded scope:
  - Worktree edits in `fund_agent/fund/extractors/profile.py`, `fund_agent/fund/extractors/manager_ownership.py`, `fund_agent/fund/analysis/consistency_check.py`, `fund_agent/services/fund_analysis_service.py` (style_positioning, out of scope)
- Parallel review coverage: 无 — third reviewer scope bounded to P4 quality-loop modules; prior MiMo and Codex review artifacts consulted for overlap audit
- Verification: `20 passed` (P4 quality-loop tests), ruff passed, CLI help passed, diff check passed

## Findings

### 1-未修复-严重-score 与 quality gate 按字段聚合而非按基金，无法对单份报告做出可用性判断

- **入口/函数**: `score_snapshot_records()` → `_evaluate_score_payload()` → `_evaluate_field_score()`
- **文件(行号)**: `extraction_score.py:209-243`, `quality_gate.py:135-226`
- **输入场景**: 10 只基金生成 snapshot，其中 9 只 P0 字段完整，1 只 `fee_schedule` 缺失。snapshot 产生 `10 × 14 = 140` 条字段记录，`fee_schedule` 的 coverage 为 `90%`
- **实际分支**: `score_snapshot_records()` 按 `(field_group, field_name)` 聚合所有记录。`fee_schedule` 聚合结果：`records=10, covered=9, coverage_rate=0.9` → `status=pass`（达到 90% 阈值）。quality gate 消费聚合行，P0 `fee_schedule` status 为 pass → 不触发 block
- **预期行为**: 那只缺失 `fee_schedule` 的基金的 report quality gate 应为 block（P0 必须字段缺失）。报告可用性是 per-fund 判断，不应被池子聚合覆盖率掩盖
- **实际行为**: gate 输出 pass，缺失 `fee_schedule` 的基金的报告可正常输出，无任何质量警告
- **直接证据**: `extraction_score.py:228-243` 的计数器按 `(field_group, field_name)` 全局聚合，不保留 `fund_code`。`quality_gate.py:170-226` 的 `_evaluate_field_score()` 仅检查聚合后的 status。产物 `score.json` 中无 per-fund 维度（`extraction_score.py:604-632`）
- **影响**: P4 北极星"防止形式合格、内容不可用的报告误导用户"在当前骨架中对多基金场景不成立。单只基金 P0 缺失可被其他基金掩盖。这是粒度假定错误：snapshot 是 field-level（正确），但 score 应至少输出 per-fund summary，gate 才能按基金阻断
- **建议改法和验证点**:
  - `score.json` 增加 `fund_scores` 字段，包含每只基金的 `fund_code`、`p0_status`、`missing_p0_fields`、`missing_traceability_fields`
  - `quality_gate` 对任一基金 P0 fail 触发 fund-level block，issue 中保留 `fund_code`
  - 测试：10 只基金中 1 只 P0 缺失 → 字段聚合 rate 90% 但该基金 gate 必须 block
- **修复风险（低/中/高）**: 中（需扩展 score.json schema 和 gate 评估逻辑，但不改变 snapshot 输入格式）
- **严重程度（严重）**: P4 北极星目标在当前实现中不成立

### 2-未修复-高-quality gate 未接入 `analyze` 主链路，只能手动执行

- **入口/函数**: `FundAnalysisService.analyze()` / `cli.py:analyze()`
- **文件(行号)**: `fund_agent/services/fund_analysis_service.py`（全文件无 P4 引用），`fund_agent/ui/cli.py:128-132`
- **输入场景**: 用户执行 `fund-analysis analyze 004393`（该基金当前 `fee_schedule` P0 fail，已有 `quality_gate.json` 显示 `status=block`）
- **实际分支**: `analyze()` → `FundAnalysisService().analyze(request)` → `typer.echo(result.report_markdown)`。不经 snapshot/score/quality-gate，直接输出报告
- **预期行为**: P4 北极星要求"报告审计必须能识别低质量输入，避免误导用户"。至少应在报告输出时附加质量信号；理想情况 P0 fail 时阻断正常报告输出
- **实际行为**: 报告直接输出，不附加任何质量门信号。用户需手动执行三条独立 CLI 命令（`extraction-snapshot` → `extraction-score` → `quality-gate`）才能获知质量状态
- **直接证据**: `grep -rn "quality_gate\|extraction_snapshot\|extraction_score" fund_agent/services/fund_analysis_service.py` 无匹配。`cli.py:128` 直接 `typer.echo(result.report_markdown)` 不调用任何 P4 模块
- **影响**: quality gate 是 opt-in 工具而非 enforced 机制。控制文档 7.3 说"不改变报告生成主链路"——但 P4 北极星要求必须能"防止"低质量报告进入可用状态，两者当前矛盾
- **建议改法和验证点**:
  - 方案 A（最小）: `FundAnalysisResult` 附加 extraction snapshot/score 信号，CLI 在报告末尾输出质量状态摘要
  - 方案 B（完整）: Service 层在报告渲染前执行 per-fund extraction 并 gate，P0 block 时输出质量阻断提示而非正常最终判断
  - 验证: `fund-analysis analyze 004393` 输出应包含 `fee_schedule` P0 fail 的质量警告
- **修复风险（低/中/高）**: 中（需要决定集成深度：附加信息 vs 阻断输出；控制文档需同步更新）
- **严重程度（高）**: quality gate 当前不对用户产生实际保护

### 3-未修复-中-FQ1/FQ4/FQ5 规则未实现，gate 只能检测 coverage/traceability

- **入口/函数**: `_evaluate_score_payload()` / `_evaluate_field_score()`
- **文件(行号)**: `quality_gate.py:135-226`，`docs/implementation-control-p4.md:410-418`
- **输入场景**:
  - FQ1: 基金 App 类别为"国内股票类"但系统分类为 `bond_fund`（类型冲突）
  - FQ4: 报告 8 章中 5 章包含"数据不足"（比例超阈值）
  - FQ5: 主动权益基金的报告使用了指数基金的 `preferred_lens`
- **实际分支**: `_evaluate_field_score()` 只按 P0/P1 字段 status 触发 FQ2/FQ3。无代码路径检查 FQ1/FQ4/FQ5
- **预期行为**: FQ1/FQ4/FQ5 是控制文档 7.2 列出的候选质量规则，应在 P4-S4 骨架中至少实现最小版本或明确标记为 `not_implemented`
- **实际行为**: 仅有 FQ2（P0 字段缺失过多）、FQ3（证据锚点不足）、FQ0（correctness 未接入记录）三个规则。FQ1/FQ4/FQ5 在代码中无实现、无占位、无 TODO
- **直接证据**: `quality_gate.py:29-31` 仅定义 `SEVERITY_BLOCK/WARN/INFO`，无 FQ1/FQ4/FQ5 的 rule_code 常量或评估分支
- **影响**: gate 只能判断"字段有没有值、有没有锚点"，不能判断"类型是否冲突、数据不足比例、lens 是否错配"。content-valid 但 semantically wrong 的报告可通过 gate
- **建议改法和验证点**:
  - FQ1: 基于 snapshot 的 `app_category` vs `classified_fund_type` 冲突检测（需要类型映射表）
  - FQ4: 基于 report markdown "数据不足/未披露/未定位" 出现次数比例
  - FQ5: 输出 `preferred_lens` 并与 `classified_fund_type` 交叉验证
  - 或在控制文档中明确延后到 P5，并把它们的缺失登记为 residual risk
- **修复风险（低/中/高）**: 低-中（依赖控制文档裁决：实现 vs 延后）
- **严重程度（中）**: 不阻塞骨架验收，但限制 gate 实际效用

### 4-未修复-中-correctness 自动比对未实现，score 只证明"有值+有锚点"

- **入口/函数**: `extraction_score.py:_score_json_payload()` correctness 段
- **文件(行号)**: `extraction_score.py:628-632`, `golden_prefill.py`, `golden_answer.py`
- **输入场景**: extractor 输出 `benchmark = "沪深300指数收益率×80%+中债综合指数收益率×20%"`（有值、有锚点），但 golden answer 标注的真实值应为 `"中证800指数收益率×80%+中债综合指数收益率×20%"`
- **实际分支**: `score.json` correctness 固定为 `not_implemented`。quality gate 仅记录 FQ0/info。golden prefill → golden build 链路完成但不接入 score
- **预期行为**: 人工审核 golden answer JSON 可用后，应能逐字段比对 extractor 输出与 golden answer 期望值，将 correctness fail（尤其 P0 字段）接入 quality gate block
- **实际行为**: `score.json` correctness 状态为 `not_implemented`，quality gate 仅记录 info 不阻断。`golden_answer.py` 已有 strict JSON 构建与校验，但缺少将 JSON 与 extractor 输出做字段级比对的模块
- **直接证据**: `extraction_score.py:628-632` correctness 段。无 `golden_answer_compare.py` 或类似比对模块
- **影响**: 即使所有 P0 字段 coverage/traceability 100%，也无法发现"值抽错"的问题。P4-S3b 修复后 `004393` 多个字段 100% coverage/traceability，但这不等价于 correctness
- **建议改法和验证点**:
  - 新增 `fund_agent/fund/golden_compare.py` 或 `golden_answer.py` 扩展：逐字段比对 `golden-answer.json` records 与 extractor/snapshot 输出
  - 将 correctness fail（至少 P0 字段）接入 quality gate block
  - 测试：golden answer 期望值 `foo`，extractor 输出 `bar` → correctness fail → gate block
- **修复风险（低/中/高）**: 中（需要新增比对模块并决定匹配粒度）
- **严重程度（中）**: 当前 control doc 明确记录为 wait-for-human-review，不阻塞骨架验收

### 5-未修复-低-004393 known_failure 代码分支在 P4-S3a 后不可达

- **入口/函数**: `_record_note()` → `write_snapshot_summary()`
- **文件(行号)**: `extraction_snapshot.py:1046-1047`, `extraction_snapshot.py:621`, `extraction_snapshot.py:43`
- **输入场景**: P4-S3a 后 `004393` 真实年报已修复为 `active_fund`。生产路径中 `classified_fund_type == "index_fund"` 不再为真
- **实际分支**: `_record_note()` 条件 `fund_code == "004393" and classified_fund_type == "index_fund"` 永远为 `False`
- **预期行为**: 硬编码基金代码特判在 root cause 修复后应移除，或改为通用冲突检测
- **实际行为**: 代码和测试 (`test_004393_known_failure_classification_is_captured`) 仍保留该分支，使用 fake extractor 回放历史错误状态
- **直接证据**: `extraction_snapshot.py:1046-1047` 的 `if selected_fund.fund_code == "004393" and classified_fund_type == "index_fund"`。测试使用 `_build_bundle("004393", "index_fund")` 硬编码旧分类绕过真实 extractor
- **影响**: 维护成本：未来开发者可能误以为这是仍需要的保护逻辑。测试给 false confidence — 保护不可达路径而非真实回归
- **建议改法和验证点**:
  - 移除 `_record_note()` 中的硬编码 `004393` 特判
  - 改为通用冲突检测：当 `app_category` 与 `classified_fund_type` 明显矛盾时追加 note（如国内股票类 → index_fund）
  - 或将测试改为回归测试：使用 P4-S3a 后真实 `active_fund` 值，断言没有 known_failure note
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: 死代码，不影响生产正确性

### 6-未修复-低-_normalize_extraction_mode 静默吞掉未知模式

- **入口/函数**: `_normalize_extraction_mode()`
- **文件(行号)**: `extraction_snapshot.py:964-981`
- **输入场景**: 底层 extractor 新增 `extraction_mode` 值（如 `"cached"` 或 `"inferred"`）
- **实际分支**: 不在白名单 `{direct, estimated, missing, partial}` 中 → 走到 `return _EXTRACTION_MODE_MISSING`
- **预期行为**: 未知模式应至少记录原始值（如写入 `note`），便于排查覆盖率异常
- **实际行为**: 静默映射为 `"missing"`，原始模式信息丢失
- **直接证据**: `extraction_snapshot.py:979-981` 兜底 `return _EXTRACTION_MODE_MISSING`
- **影响**: extractor 扩展新模式时，snapshot 覆盖率可能被低估且难以发现原因。当前所有 extractor 仅输出 `direct/estimated/missing/derived`，无实际触发
- **建议改法和验证点**: 兜底分支保留原值或在 `note` 中记录 `unknown_extraction_mode:{original}`
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: 当前不触发

### 7-未修复-低-golden_prefill confidence 启发式缺乏校准依据

- **入口/函数**: `_confidence_for_value()`
- **文件(行号)**: `golden_prefill.py:380-409`
- **输入场景**: 两个值都来自 `page-` 含页码锚点、extraction_mode 为 `direct`：值 A 是 119 字符 → confidence `"high"`；值 B 是 121 字符 → confidence `"medium"`
- **实际分支**: `len(str(value)) > 120` → `return "medium"`；否则 `"high"`（因为 `page-` in source）
- **预期行为**: confidence 应基于抽取模式和证据锚点质量一致判断。120 字符阈值无文档依据
- **实际行为**: 121 字符的基金经理策略文本（常见于年报 §4）被降级为 medium，但 119 字符的相同来源收益数据保持 high。行为在 120 字符边界突变
- **直接证据**: `golden_prefill.py:405`: `if len(str(value)) > 120: return "medium"`。无注释说明 120 阈值来源
- **影响**: 预填 confidence 标签对长文本字段（如 `manager_strategy_text`）系统性偏低，可能误导人工审核优先级。但预填明确标注为 silver label，不影响 correctness 评分
- **建议改法和验证点**: 移除长度启发式，或改为按字段类型配置（如 `manager_strategy_text` 长文本不因长度降级）；最低限度加注释说明阈值选择依据
- **修复风险（低/中/高）**: 低
- **严重程度（低）**: silver label 质量，不影响 correctness

## Architecture Boundary Assessment

P4 模块严格遵守四层架构：

- **Capability 层**: `extraction_snapshot.py`, `extraction_score.py`, `golden_prefill.py`, `golden_answer.py`, `quality_gate.py` — 承载完整业务逻辑，使用 Protocol 注入测试替身，不依赖 UI/Service
- **Service 层**: `extraction_snapshot_service.py` 等 — 薄包装，显式请求对象收敛参数，参数校验，单行委托
- **UI 层**: `cli.py` — Typer CLI 入口，委托 Service，不承载业务逻辑

未发现反向 import、跨层穿透调用、或下层泄漏上层治理状态。

## Explicit Parameter Audit

全部 P4 Service 请求使用 frozen dataclass 显式传递所有参数。未发现：
- `extra_payload` 或 `**kwargs` 传递隐藏参数
- 隐式 cwd 依赖
- 字符串拼凑的未校验参数

CLI 通过 Typer Option/Argument 显式传入并通过 `_validate_request()` 校验。

## Document Repository Boundary Audit

P4 模块访问数据的两条路径：

1. snapshot / golden_prefill: 通过 `FundDataExtractor.extract(...)`（生产）或 `SnapshotExtractor`/`GoldenPrefillExtractor` Protocol（测试注入），不直接读取 `fund_agent/fund/pdf/*` 或 `cache/pdf/*`
2. extraction_score / golden_answer / quality_gate: 只读取各自声明的运行产物（`snapshot.jsonl`、`score.json`、golden answer Markdown/JSON），不访问年报或缓存

未发现 P4 模块直接读取 PDF 文件、缓存文件或绕过统一文档仓库契约。

## Evidence Traceability

- Snapshot: 每条记录携带 `section_id`、`page`、`table_id`、`row_id`、`anchor_present`
- Score: 按字段统计 `anchor_present` 比率 → `traceability_rate`
- Quality gate: P0 traceability fail → FQ3 block

证据链从 extractor 的 `EvidenceAnchor` → snapshot 字段级 → score 统计 → gate 阻断，完整可追溯。缺口是 correctness 尚未验证锚点内容是否真正支持字段值（待 golden answer 自动比对接入）。

## State Machine & Overcoupling Check

P4 质量闭环流程：`snapshot → score → golden-prefill → golden-build → quality-gate`。每个模块产出 immutable dataclass，不持有共享可变状态。模块间依赖单向且通过文件路径契约（snapshot.jsonl → score.json → quality_gate.json），不互相 import 实现细节。未发现 overcoupling。

## Open Questions

1. **score/gate 粒度假定**: 控制文档 7.3 说 quality gate 骨架"只消费 score.json"，但未明确 score 必须是 per-fund 还是 field-aggregate。如果 P4 目标是"防止单份报告内容不可用"，则 per-fund score 是必需的。请在 controller 裁决中明确粒度假定。

2. **quality gate 集成深度**: 控制文档 7.3 说"不改变报告生成主链路"，但 P4 北极星要求"防止形式合格、内容不可用的报告进入产品可用状态"。这两个约束当前矛盾：集成深度是多少？（方案 A: CLI 输出末尾附加质量信号 / 方案 B: P0 fail 阻断报告正常输出 / 方案 C: 保持独立命令，文档声明 manual gate）

3. **FQ1/FQ4/FQ5 归属**: 控制文档 7.2 列出 5 条候选规则，当前仅实现 FQ2/FQ3。剩余三条属于 P4 还是 P5？需要显式裁决写回控制文档。

4. **correctness 自动比对时间表**: golden answer JSON 构建与校验已完备，字段级比对模块属于 P4-S4 后续还是 P5？

5. **004393 known_failure note**: 是保留为历史记录（可解释 P4-S1 基线）还是立即移除？移除后 snapshot 输出变化不影响 score。

## Residual Risk

| ID | 风险 | 影响 | Owner |
|---|---|---|---|
| P4-DS-R1 | score/gate 缺少 fund-level 状态 | 严重 — 单基金 P0 缺失可被多基金聚合覆盖率掩盖 | 后续 per-fund score/gate slice |
| P4-DS-R2 | quality gate 未接入 `analyze` 主链路 | 高 — 用户可直接获得无质量信号报告 | 后续 quality gate integration slice |
| P4-DS-R3 | correctness 自动比对未实现 | 中 — 有值+有锚点但值错误的情况无法检测 | 后续 correctness compare slice |
| P4-DS-R4 | FQ1/FQ4/FQ5 规则未实现 | 中 — 内容语义冲突无法被 gate 检测 | 后续 quality gate rules slice |
| P4-DS-R5 | `016492` CSV 重复 | 低 — 数据源需人工核对；summary 已标红 | 用户核对 App 源数据 |
| P4-DS-R6 | `share_change` 多份额列选择策略 deferred | 低 — A/C 份额基金可能选错列 | 后续 extractor refinement |
| P4-DS-R7 | 004393 known_failure note 死代码 | 低 — 维护负担，无正确性影响 | 后续 cleanup |
| P4-DS-R8 | quality_gate / golden_answer 测试覆盖不足 | 低 — 核心逻辑正确但边界未锁定 | 后续 test hardening |

## Final Recommendation

**FAIL for "quality loop prevents form-valid but content-unusable reports."**
**PASS for individual module code quality, architecture conformance, and skeleton implementation.**

具体裁决：

- **Snapshot (P4-S1)**: PASS. 字段级快照正确记录 extraction_mode、value_present、anchor_present 和锚点定位。通过 `FundDataExtractor` 访问年报，遵守文档仓库边界。
- **Score (P4-S2)**: PASS (skeleton). Coverage/traceability 计算、P0/P1/P2 映射、golden set 选择符合控制文档。但粒度假定错误：只输出 field-aggregate score，缺少 per-fund score。这是设计决策问题，不是实现 bug。
- **Golden-prefill / Golden-build (P4-S4 pre-label)**: PASS. 预填正确声明为 silver label；golden-build strict 校验人工审核字段。不读取 PDF/cache。correctness 自动比对未实现是已记录残余风险。
- **Quality-gate (P4-S4 skeleton)**: PASS (skeleton), FAIL (effectiveness). 骨架按控制文档 7.3 节落地：只消费 score.json、P0 fail block、P1 fail warn。但 gate 不能实际防止低质量报告进入可用状态，原因有两个：score 是 field-aggregate 而非 per-fund（Finding 1），gate 未接入 analyze 主链路（Finding 2）。

P4-S1 至 P4-S4 代码实现符合控制文档 7.3-7.4 的骨架验收目标。但从 P4 北极星"防止形式合格、内容不可用的报告误导用户"出发，当前质量闭环存在两个关键 gap：per-fund gate 缺失和主链路未集成。建议 controller 对这两个 gap 做出显式裁决（修复纳入 P4 / deferred 到 P5 并登记 owner），并写回控制文档。
