# Golden Readiness Preflight Plan — Adversarial Review (GLM)

日期：2026-05-29
Review 角色：plan review worker only。不改代码、不 commit/push/PR。
Review 对象：`docs/reviews/release-maintenance-golden-readiness-preflight-plan-20260529.md`
Gate：`golden-readiness preflight gate`

---

## Verdict: **accepted-with-required-fixes**

Plan 总体方向正确，blocker taxonomy 完备，fail-closed 规则严谨，006597 处理无误，非目标边界清晰。但存在 2 项 required fix 和 4 项建议改进，涉及 golden-answer schema 与实际数据结构不一致、CLI 输入可行性缺口等。修完 required fixes 后可进入 implementation。

---

## Findings

### F1 (Required Fix — severity: high) golden-answer.json 无 report_year 字段，plan 输入 contract 与实际 schema 不一致

**问题**：Plan 输入 contract 声明 "strict golden answer JSON 只读 `funds[].fund_code/report_year/records/skipped_fields`"，并定义 `strict_golden_fund_not_covered`、`strict_golden_year_not_covered`、`strict_golden_partial_coverage` 三个 blocker code。但实际 `reports/golden-answers/golden-answer.json` 的 schema 是 `fund-agent.golden-answer.v1`，每条 record 只有 `fund_code`、`field_name`、`sub_field`、`expected_value`、`confidence`、`source`——**没有 `report_year` 字段**。

11 只基金（004393, 000216, 007721, 007360, 006597, 001548, 004194, 005313, 017644, 019918, 019923）的 records 均无 year 维度。这意味着 `_derive_strict_golden_coverage()` 无法按 fund_code + report_year 做 year-level 覆盖检查，`strict_golden_year_not_covered` blocker 在当前 golden-answer schema 下永远触发（对所有 fund-year pair），`strict_golden_partial_coverage` 也无法按 year 判定。

**风险**：若按 plan 原样实现，所有 11 只基金都会因 "year not covered" 被 block，包括本不应该是 golden coverage 问题的 slot（如 006597）。这会制造虚假 blocker 噪声，削弱 preflight 输出的可信度。

**Required Fix**：
1. Plan 必须显式声明当前 golden-answer.json 的实际 schema（v1, 无 report_year），并修改 strict golden coverage 检查逻辑为两阶段：
   - 阶段一（本 gate）：只检查 fund_code 是否在 golden-answer `funds[]` 中。若在，按 `covered` 记录；若不在，输出 `strict_golden_fund_not_covered` blocker。不尝试 year-level 检查。
   - 阶段二（未来 gate，需 golden-answer schema 升级到 v2 加入 report_year 后）：启用 year-level 和 partial coverage 检查，届时再激活 `strict_golden_year_not_covered` 和 `strict_golden_partial_coverage` blocker code。
2. 在 blocker code 定义中，将 `strict_golden_year_not_covered` 和 `strict_golden_partial_coverage` 标注为 "reserved, pending golden-answer schema v2"，本 gate 不实现。
3. 删除或修正输入 contract 中 "只读 `funds[].fund_code/report_year/records/skipped_fields`" 的描述，改为 "只读 `funds[].fund_code/records[]`，当前 schema v1 无 report_year 维度"。

**注意**：修改 golden-answer.json schema 加入 report_year 属于 golden fixture 变更，是本 gate 的非目标。因此只能接受当前 schema 限制并调整 coverage 逻辑。

---

### F2 (Required Fix — severity: high) FundArtifactInput 字段数与 CLI `--fund-artifact` colon-separated 格式不匹配

**问题**：Plan 定义的 `FundArtifactInput` 有 11 个字段：`fund_code`、`report_year`、`snapshot_path`、`score_path`、`quality_gate_path`、`score_golden_set_path`、`promotion_state`、`coverage_disposition`、`coverage_owner`、`next_gate`、`evidence_artifacts`。但 CLI 示例只展示 4 字段 colon-separated 格式：

```
--fund-artifact 006597:2024:snapshot:score:quality
```

剩余 7 个字段（`score_golden_set_path`、`promotion_state`、`coverage_disposition`、`coverage_owner`、`next_gate`、`evidence_artifacts`）没有 CLI 传参路径。Plan 提到 `--preflight-input path.json` 作为替代，但未给出该 JSON 文件的 schema 定义，也未明确 `--fund-artifact` 与 `--preflight-input` 的使用场景划分。

**风险**：实现 worker 会遇到 CLI 设计歧义——无法确定哪些参数走 colon-separated、哪些走 JSON file、二者混用时的合并/冲突规则。

**Required Fix**：
1. 明确规定 **production 推荐路径是 `--preflight-input path.json`**，并给出完整的 JSON schema（必须与 `FundArtifactInput` 字段一一对应，不允许 extra fields）。
2. 若保留 `--fund-artifact` 简写，明确其只填充 `fund_code`、`report_year`、`snapshot_path`、`score_path`、`quality_gate_path` 五个字段，其余字段从 static disposition manifest 或默认值填充，并在输出中标记 `input_source="cli_shortcut"` 以便审计。
3. 明确 `--fund-artifact` 与 `--preflight-input` 互斥，而非"同时提供时 Service 校验冲突"——因为混用只会增加歧义。

---

### F3 (Suggestion — severity: medium) coverage_disposition enum 与 accepted controller judgment dispositions 有 gap

**观察**：Plan 定义 `coverage_disposition` 枚举为 `Literal["include_for_later_review","replace","needs_taxonomy_gate","needs_evidence_gate","blocked","deferred","unknown"]`。但实际 controller judgment 使用了更细粒度的 disposition，例如：
- `reviewed_coverage_candidate_input_accepted`（110020，来自 `release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md`）
- `data_gap`（FOF，来自 consolidation disposition judgment）
- `provenance eligible + quality block + not_promoted`（QDII slot 的组合状态）

`reviewed_coverage_candidate_input_accepted` 不在枚举中，plan 通过 static manifest 将其映射为 `include_for_later_review` + `not_promoted`，但这掩盖了 110020 的独特状态——它不是普通的 "for later review"，而是已通过 reviewed coverage evidence gate 但仍不满足 promotion 条件。

**建议**：
- 在枚举中加入 `reviewed_coverage_candidate` 作为独立值，或
- 在 static manifest 中为 110020 显式注释 `reviewed_coverage_candidate_input_accepted` 作为原始 disposition，`include_for_later_review` 作为 preflight 映射，保留原始值的 traceability。

这不是 blocker——static manifest 的逐条 artifact 链接已经提供 traceability——但明确映射关系能避免未来 preflight consumer 误解读。

---

### F4 (Suggestion — severity: medium) static default disposition manifest 应带版本标识和过期条件

**观察**：Plan 允许代码内定义 static manifest，并在 Blocking Questions 中承认"中期应另开 gate 把 accepted disposition 转成机器可读 manifest"。这个方向正确，但当前 static manifest 缺少：
1. **版本标识**：manifest 内容应带 `manifest_version` 和 `generated_from`（列出对应的 controller judgment artifacts），输出到 preflight JSON 的顶层。
2. **过期/升级条件**：明确声明 "本 static manifest 在以下条件下必须升级为外部 manifest：新 controller judgment 改变任一 slot 的 disposition / 新 fund 加入候选池 / promotion state 变更"。

**建议**：在代码注释和输出 JSON 中加入上述标识，并在 `blocking_questions` 中保留 "static manifest requires upgrade to external machine-readable manifest" 作为持续性提醒。

---

### F5 (Suggestion — severity: low) `tests/ui/test_cli.py` 不存在，需明确创建而非"更新"

**观察**：Plan 写 "更新 `tests/ui/test_cli.py`"，但该文件当前不存在。新增 CLI 测试文件涉及 CLI framework（Typer）的 test harness 配置（`CliRunner`、app fixture 等），应有更明确的测试基础设施说明。

**建议**：将 "更新" 改为 "新建"，并在测试计划中说明 Typer `CliRunner` 的使用方式（或引用现有 CLI 测试 pattern，如果其他测试文件已有 Typer 测试样板）。

---

### F6 (Suggestion — severity: low) 006597 处理完全正确，值得确认

**观察**：Plan 对 006597 的处理经逐一验证：
- quality_gate.json `status="warn"`，6 个 issues 均为 FQ2 turnover_rate/holder_structure 等 unrelated warnings，**无 `bond_risk_evidence_missing`**。✓
- score.json `score_applicability_issues=[]`。✓
- Plan 将 006597 列入 `resolved_items`（`bond_006597_resolved`），不列入 blockers。✓
- Plan 不把 quality `warn` 当 ready 证据。✓
- Plan 正确指出 strict golden/fixture promotion 仍 block 006597 的 promotion readiness。✓

006597 golden-answer.json 有 20 条 records（fund_code=006597 在 golden-answer 中），但无 year 维度（见 F1），按修正后逻辑应为 `covered`（fund-level）。

**结论**：006597 部分无问题，维持 plan 原判断。

---

## 逐项 Challenge 回答

### 1. 输入/输出 contract 是否 machine-readable，是否有 free-form/extra_payload 风险

**结论**：基本合格，有 1 处 schema 不一致（F1）和 1 处 CLI 可行性缺口（F2）。输出 JSON schema 足够 machine-readable，顶层 `schema_version` 和 per-fund row 结构清晰。**无 extra_payload 风险**——plan 明确禁止 extra_payload，所有字段显式声明。`--preflight-input` JSON 需补完整 schema（F2 required fix）。

### 2. blocker taxonomy 是否能可靠归因

**结论**：大部分可靠。QDII hard stop、FOF taxonomy_pending、110020 not_promoted、source provenance、strict golden coverage、fixture promotion absence 均有明确 controller judgment artifacts 可归因。

**例外**：strict golden year-level coverage 在当前 golden-answer schema 下不可归因（F1），必须降级为 fund-level only。

006597 bond blocker 正确归因为 resolved，不误列。

quality warn 正确不作为 ready 证据。

### 3. 是否会误把 006597 bond blocker 继续列为 blocker

**不会。** Plan 显式定义 `bond_006597_resolved` 放入 `resolved_items`，且 blocker 聚合规则中明确 "do not list `bond_risk_evidence_missing` as blocker"。实测 quality gate 和 score 均确认无 bond_risk_evidence_missing。✓

### 4. 是否误把 quality warn 当 ready

**不会。** Plan fail-closed 规则第 7 条 "quality gate `warn` 只能进入 warning；不得作为 ready 证据"，且 `ready` 枚举要求 "quality gate `pass`"。✓

### 5. static default disposition manifest 是否可接受

**短期可接受**，但需加版本标识和升级条件（F4）。中期必须转为外部 machine-readable manifest。Plan 的 Blocking Questions 已正确识别此 gap。

### 6. implementation slices、tests、validation、docs/control 更新是否充分

**基本充分**，但需注意：
- `tests/ui/test_cli.py` 需新建而非更新（F5）。
- 测试用例覆盖了所有关键 blocker codes，包括 006597 resolved 验证。
- 验证命令包含 ruff + pytest + smoke，合格。
- docs/control 更新时机正确（"实现接受后才更新"）。

### 7. 是否触碰 promotion、FQ0-FQ6、FundDocumentRepository、Host/Agent/dayu、release readiness、PR/push/merge 非目标

**不触碰。** Plan 明确声明 "不解除所有 blocker，不做 golden promotion，不修改 golden fixture，不改变 FQ0-FQ6"，代码只读 artifacts，不调用 PDF/cache/source helper，不引入 Host/Agent/dayu 依赖。Stop Conditions 也覆盖了所有非目标边界。✓

---

## Required Changes 汇总

| # | Fix | 影响 | Plan 位置 |
|---|-----|------|-----------|
| F1 | strict golden coverage 降级为 fund-level only；标注 year/partial blocker codes 为 reserved pending schema v2；修正输入 contract 描述 | `_derive_strict_golden_coverage()`、blocker code 列表、输入 contract 段落 | "输入 Contract" 和 "Blocker 聚合规则" |
| F2 | 明确 `--preflight-input path.json` 为 production 推荐路径并补完整 JSON schema；`--fund-artifact` 简写仅覆盖 5 字段；二者互斥 | CLI 入口、Service 层 request 校验 | "CLI 入口" 和 "Service 层" |

---

## Accepted Without Fix

以下设计决策经审查接受，无需修改：

1. **Gate classification `heavy`**：golden readiness preflight 涉及 baseline/golden promotion blocker 聚合，符合 AGENTS.md heavy 分类规则。
2. **006597 bond blocker resolved 判定**：与最新 artifacts 一致。
3. **Fail-closed 规则全集**：12 条规则覆盖所有已知 fail-closed 场景，无遗漏。
4. **Stop Conditions**：覆盖所有非目标边界，无越界风险。
5. **模块位置 `fund_agent/fund/golden_readiness_preflight.py`**：符合 Agent 层基金领域能力包定位。
6. **不创建 Host/Agent/dayu 依赖**：与当前过渡架构一致。
7. **output JSON `schema_version: fund-agent.golden-readiness-preflight.v1`**：支持未来 schema 演进。
8. **`deferred_with_owner` readiness enum**：准确描述 QDII/FOF/110020 等已有 owner 但未解除的状态。
9. **Markdown 输出必须包含 "已解除" 列表**：确保 006597 解除不丢失。
