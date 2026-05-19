# P4 Aggregate Deepreview - Codex

## 审查范围

- Gate：`P4 aggregate deepreview`
- 设计真源：`docs/design.md`
- 控制真源：`docs/implementation-control.md`、`docs/implementation-control-p4.md`
- 审查对象：P4-S1 至 P4-S4 的 snapshot、score、golden-prefill、golden-build、quality-gate 质量闭环
- 排除范围：用户指定的 `style_positioning` 相关当前工作树改动
- 验证：`.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_golden_prefill.py tests/fund/test_golden_answer.py tests/fund/test_quality_gate.py tests/services/test_extraction_snapshot_service.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py -q`，结果 `20 passed`

## Findings

### 高 - quality gate 以字段聚合分数为输入，不能阻断单只基金内容不可用报告

位置：
- `fund_agent/fund/extraction_score.py:209-243`
- `fund_agent/fund/extraction_score.py:622-636`
- `fund_agent/fund/quality_gate.py:135-226`

`score_snapshot_records()` 只按 `(field_group, field_name)` 聚合所有 snapshot 记录，输出 `field_scores` 时没有 `fund_code`、`fund_name`、`app_category` 或单基金状态。`quality_gate` 随后只遍历这些字段级聚合行，按 P0/P1 字段状态生成 block/warn。

这意味着多基金 run 中，如果某只基金的 P0 字段缺失，但同一字段在池子里的覆盖率仍达到 90%，gate 会通过该字段。该实现可以衡量“池子整体字段抽取质量”，但不能保证“某一份待交付报告”可用。

这直接削弱 P4 北极星：防止“形式合格、内容不可用”的报告进入可用状态。报告可用性是 fund-level 判断，当前 gate 是 field-level aggregate 判断，两者粒度不一致。

建议：
- `score.json` 增加 per-fund score，例如 `fund_scores[fund_code].p0_status`、`missing_p0_fields`、`missing_traceability_fields`。
- `quality_gate` 对任一基金 P0 fail 触发 fund-level block，并在 issue 中带 `fund_code`。
- 增加测试：10 只基金中 1 只 P0 缺失时，字段聚合率 90% 但该基金 gate 必须 block。

### 高 - quality gate 未接入 `analyze` 主链路，当前只能手动执行，不能自动防止低质量报告输出

位置：
- `fund_agent/ui/cli.py:128-136`
- `fund_agent/ui/cli.py:338-363`
- `docs/implementation-control-p4.md:422-431`

当前 `fund-analysis analyze` 直接调用 `FundAnalysisService().analyze()` 并输出 Markdown 报告；P4 的 `quality-gate` 是独立 CLI 命令，只消费用户显式传入的 `score.json`。控制文档第 7.3 节明确允许“不改变报告生成主链路”，因此这不违反 P4-S4 骨架验收；但从 aggregate deepreview 的目标看，它尚不能“实际阻断”用户通过 `analyze` 获得内容不可用报告。

真实产物对 `004393` 单基金 score 能正确 block：`reports/extraction-snapshots/p4-s3b-quality-gate-smoke/quality_gate.json` 显示 `status=block`，原因是 `fee_schedule` P0 fail。但这个 block 不会影响 `fund-analysis analyze 004393` 的输出路径。

建议：
- 短期：在 `analyze` 输出中附加质量状态，至少对已有 score/gate 结果给出显式不可用提示。
- 完整方案：Service 层在报告生成后或生成前执行 per-fund score/gate，P0 block 时不输出正常最终判断。
- 增加端到端测试：`004393` 当前 `fee_schedule` P0 fail 时，`analyze` 不得无提示输出正常可用报告。

### 中 - FQ1/FQ4/FQ5 仍未实现，内容冲突和 lens 错配不能被质量门识别

位置：
- `docs/implementation-control-p4.md:410-418`
- `fund_agent/fund/quality_gate.py:170-226`

控制文档列出 FQ1（基金类型与 App 类别或 golden answer 冲突）、FQ4（报告中“数据不足”比例过高）、FQ5（`preferred_lens` 与基金类型不匹配）。当前 `quality_gate` 只实现了 FQ2/FQ3 和 FQ0 信息项。

这使 gate 只能判断 coverage/traceability，不能判断“形式上有值但内容语义不可用”的情况。例如基金类型与 App 类别冲突、主动基金错误套用指数基金 lens、报告大量“数据不足”但 P0 字段勉强达标，当前都不会被阻断。

建议：
- FQ1：基于 snapshot 的 `app_category`、`classified_fund_type` 和后续 golden answer 做类型冲突检测。
- FQ4：从报告或模板渲染结构统计“数据不足/未披露/未定位”比例。
- FQ5：输出并检查报告实际使用的 preferred_lens，与 `classified_fund_type` 同源比对。

### 中 - correctness golden answer 已能构建，但尚未接入自动比对，score 仍只能证明“抽到且有锚点”

位置：
- `fund_agent/fund/extraction_score.py:628-632`
- `fund_agent/fund/golden_prefill.py:1-6`
- `fund_agent/fund/golden_answer.py:1-5`
- `docs/reviews/p4-s4-control-doc-reconciliation-20260519.md:33`

`golden-prefill` 正确声明自动预填只是 silver label，`golden-build` 也能把人工审核 Markdown 转成 strict JSON。但 `score.json` 中 correctness 仍是 `not_implemented`，quality gate 仅记录 FQ0/info。

这条链路目前为后续 correctness 准备了输入，但还不能发现“字段有值、有锚点，但值抽错”的问题。P4-S3b 修复后 `004393` 多个字段 coverage/traceability 达到 100%，但这不等价于 correctness 通过。

建议：
- 实现 `golden-answer.json` 与 snapshot/extractor 输出的字段级比对。
- 将 correctness fail 至少对 P0 字段接入 block。
- golden answer JSON 中建议保留字段来源定位与审核时间/审核人或审核批次，便于追溯人工标注版本。

### 低 - `004393` known_failure note 已成为历史特判，后续维护价值下降

位置：
- `fund_agent/fund/extraction_snapshot.py:43`
- `fund_agent/fund/extraction_snapshot.py:621`
- `fund_agent/fund/extraction_snapshot.py:1046-1047`

P4-S3a 已将 `004393` 修复为 `active_fund`，但 snapshot 仍保留 `004393 + index_fund` 的 hard-coded known_failure note。它对 P4-S1 历史基线有解释价值，但当前生产路径已经不应触发。

建议后续改为通用类型冲突 note：当 `app_category` 与 `classified_fund_type` 明显冲突时记录，而不是绑定单个基金代码。

## 明确判断

### Snapshot

通过。`extraction_snapshot.py` 位于 Capability 层，通过 `FundDataExtractor.extract(...)` 或测试 Protocol 获取结构化数据；未发现上层直接读取 PDF/cache。snapshot 记录了字段值、提取模式、锚点存在性和章节/页码/表格/行定位。`016492` 重复在 summary 标红但不阻断，符合控制文档。

### Score

部分通过。coverage/traceability 计算、P0/P1/P2 映射、golden set 选择符合 P4-S2 当前约束。但 score 粒度是字段聚合，不是 fund-level gate 输入；这对“单份报告可用性”是不充分的。

### Golden-prefill / Golden-build

通过当前骨架验收。预填只作为 silver label；`golden-build` 校验 `expected_value`、`confidence`、`source` 和 skipped fields，且不读取 PDF/cache。未完成 correctness 自动比对是已记录的残余风险。

### Quality-gate

骨架通过，目标不完全达成。对单基金 `004393` 的当前 score 能正确 block P0 fail；但多基金聚合会掩盖单基金缺失，且 gate 未接入 `analyze` 主链路。因此当前实现不能完整防止“形式合格、内容不可用”的报告进入可用状态。

### 证据可追溯性

通过当前 coverage/traceability 层。snapshot 保留 `section_id/page/table_id/row_id`，score 统计 `anchor_present`，quality gate 对 P0 traceability fail 阻断。缺口是 correctness 尚未验证“锚点是否支持字段值”。

### 文档仓库边界

通过。审查范围内未发现直接读取 `fund_agent/fund/pdf/*`、`cache/pdf/*` 或本地 PDF 的 P4 逻辑。涉及真实年报抽取的路径通过 `FundDataExtractor` 进入统一文档仓库契约；score/golden-build/quality-gate 只读各自声明的运行产物。

### `extra_payload`

通过。P4 Service 请求均为显式 dataclass 参数，未发现把显式参数隐藏到 `extra_payload`。

## Open Questions

1. P4 aggregate 的通过标准是“骨架按控制文档落地”，还是“质量闭环已经能阻断 `analyze` 输出”？如果是后者，当前必须 FAIL。
2. per-fund gate 是 P4 必须补齐，还是进入 P5？从“防止单份报告误导用户”的第一性原理看，应在 P4 收口。
3. FQ1/FQ4/FQ5 是 P4-S4 后续规则扩展，还是只作为候选规则保留到下一 phase？
4. correctness 自动比对的 owner 是否就是“后续 correctness slice”，是否需要写回 `docs/implementation-control-p4.md` 的风险表？

## Residual Risks

| ID | 风险 | 影响 | 当前 owner |
|---|---|---|---|
| P4-DR-C1 | score/gate 缺少 fund-level 状态 | 单只基金 P0 缺失可能被多基金聚合覆盖率掩盖 | 建议新增 P4 follow-up：per-fund score/gate |
| P4-DR-C2 | quality gate 未接入 `analyze` | 用户仍可直接获得无质量阻断的报告 | 后续 quality gate integration slice |
| P4-DR-C3 | correctness 自动比对未实现 | 有锚点但抽错值的问题无法发现 | 后续 correctness slice |
| P4-DR-C4 | FQ1/FQ4/FQ5 未实现 | 类型冲突、数据不足比例、preferred_lens 错配无法阻断 | 后续 quality gate rules slice |
| P4-DR-C5 | `016492` CSV 重复 | 数据源仍需人工核对 | 用户核对 App 源数据 |
| P4-DR-C6 | `share_change` 多份额列选择策略 deferred | A/C 份额可能选错列 | 后续 extractor refinement |
| P4-DR-C7 | 当前 worktree 存在 style_positioning 非本 scope 改动 | 不影响本次 P4 只读审查，但合入前需独立裁决 | 后续独立字段契约 slice |

## Final Recommendation

**FAIL for aggregate quality-loop readiness.**

P4-S1 至 P4-S4 的代码骨架质量整体可接受：边界清晰、参数显式、无直接 PDF/cache 读取、证据锚点链路可见，单基金 `004393` 的 score/gate smoke 也能阻断 P0 fail。

但按本次 deepreview 的核心问题“质量闭环是否实际防止形式合格但内容不可用报告”判断，当前答案是否定的：gate 只看字段聚合 score，缺少 fund-level 阻断；并且未接入 `analyze` 主链路。建议在进入下一 gate 前至少补齐 per-fund score/gate，并明确主链路集成策略或在控制文档中把它登记为阻断级 residual risk 和 owner。
