# Golden Readiness Preflight Plan Rereview — MiMo

日期：2026-05-29
Review target: 修订后的 `docs/reviews/release-maintenance-golden-readiness-preflight-plan-20260529.md`
Gate: `golden-readiness preflight gate`
Role: plan review worker only，不改代码、不 commit/push/PR。
Rereview context: MiMo F1 被 controller reject（`fund_agent/fund/` 实际存在）；需验证 MiMo F2/F3/F4、GLM F1/F2 required fixes 是否 closed。

## Verdict

**accepted**

所有 required fixes 均已 closed。Plan 可进入 implementation。

## 逐项 Closed Verification

### MiMo F1 — Rejected (controller disposition)

Controller reject 理由：`fund_agent/fund/` 在当前仓库实际存在，`extraction_score.py`、`quality_gate.py`、`golden_answer.py` 均位于该包内。

Plan Fix Notes 第 1 行明确记录 reject 理由，实现路径维持 `fund_agent/fund/golden_readiness_preflight.py`。**Closed.**

### GLM F1 — Closed: golden-answer schema v1 fund-level only

| 检查项 | Plan 位置 | 状态 |
|--------|-----------|------|
| 输入 contract 描述修正为 v1 无 report_year | L74: "当前 v1 JSON 不含 report_year，不能做 year-level coverage 判定"；L140: "只读 `funds[].fund_code` 与 `funds[].records[]`" | ✓ |
| `strict_golden_year_not_covered` 标为 reserved | L271: "reserved pending golden-answer schema v2；本 gate 不实现、不触发" | ✓ |
| `strict_golden_partial_coverage` 标为 reserved | L272: "reserved pending golden-answer schema v2 或 future correctness coverage contract；本 gate 不实现、不触发" | ✓ |
| Fail-closed 规则仅提及 fund-level | L295: "strict golden answer v1 fund-level coverage 不足必须 block；不得沿用 FQ0 info 语义把 promotion readiness 放行。Year-level / partial coverage 本 gate 不触发。" | ✓ |
| Stop Conditions 覆盖 year/partial 场景 | L508: "需要实现 year-level 或 partial-field strict golden readiness；当前 v1 golden-answer schema 不支持，必须另开 schema v2 / correctness coverage gate。" | ✓ |
| Blocking Questions 补充说明 | L521: "当前 strict golden answer v1 不含 `report_year`，所以本 gate 只能回答 fund 是否存在于 strict golden answer" | ✓ |
| Test plan 覆盖 reserved code 不触发 | L429: `test_preflight_reserves_strict_golden_year_and_partial_coverage_codes` | ✓ |

**Closed.** 所有 6 处 required fix 均已修正。

### GLM F2 / MiMo F4 — Closed: --preflight-input schema + --fund-artifact shortcut

| 检查项 | Plan 位置 | 状态 |
|--------|-----------|------|
| `--preflight-input` 为 production recommended path | L59: "Production recommended path"；L381-385 CLI 示例 | ✓ |
| 完整 JSON schema 给出 | L79-125: 包含 `schema_version`、`run_id`、`source_csv`、`selected_pool_path`、`golden_answer_path`、`fixture_promotion_state_path`、`coverage_disposition_path`、`output_dir`、`fund_artifacts[]`，每项含完整字段 | ✓ |
| Schema validation 禁止未知字段 | L133: "发现未知字段时抛 `ValueError`，防止形成隐式 `extra_payload`" | ✓ |
| `--fund-artifact` 仅覆盖 5 字段 | L389-401: "格式必须为 `fund_code::report_year::snapshot_path::score_path::quality_gate_path`"，"split 后字段数必须精确等于 5"，"只填这五项；其余均来自 static disposition manifest/defaults" | ✓ |
| 分隔符明确为 `::` | L396: "分隔符固定为 `::`" | ✓ |
| 二者互斥 | L59/L387/L362: "若同时提供 `--preflight-input` 和单项参数，Service 校验冲突并退出 2" | ✓ |
| Test 覆盖冲突退出 2 | L439: "`--preflight-input` 与显式参数冲突退出 2" | ✓ |
| Test 覆盖 `--fund-artifact` 字段数校验 | L440: "`--fund-artifact` 使用 `::` 分隔且字段数必须为 5；错误字段数退出 2" | ✓ |

**Closed.** 所有 required fix 要素均已修正。

### MiMo F2 — Closed: fixture promotion manifest 不存在

| 检查项 | Plan 位置 | 状态 |
|--------|-----------|------|
| 删除不存在的默认路径 | L75: "`fixture_promotion_state_path: Path | None`。Optional JSON manifest；没有默认文件路径。" | ✓ |
| 缺省输出 `fixture_promotion_absent` blocker | L75: "若缺失，所有候选默认 `promotion_state='not_promoted'` 并输出 `fixture_promotion_absent` blocker" | ✓ |
| CLI 示例不再引用不存在的文件 | L371-377: CLI 示例未包含 `--fixture-promotion-state-path` | ✓ |
| Test 覆盖 absence 场景 | L430: `test_preflight_blocks_fixture_promotion_absence` | ✓ |

**Closed.**

### MiMo F3 — Closed: static manifest metadata + lifecycle

| 检查项 | Plan 位置 | 状态 |
|--------|-----------|------|
| `schema_version` 字段 | L159-163 output schema: `static_disposition_manifest.schema_version`；L336: `schema_version="fund-agent.coverage-disposition.static-current.v1"` | ✓ |
| `accepted_as_of` 字段 | L161: `accepted_as_of: "2026-05-29"`；L336: `accepted_as_of="2026-05-29"` | ✓ |
| `source_artifacts` 字段 | L162: `source_artifacts: []`；L336: `source_artifacts` | ✓ |
| Lifecycle exit criteria | L346-352: 4 条明确条件（disposition 变更、fund 池变更、fixture promotion 变更、3+ 条目维护），满足任一必须开独立 manifest gate | ✓ |
| 输出 JSON 必须包含 manifest 原样 | L354: "Preflight JSON 输出必须把当前使用的 static manifest 原样写入 `static_disposition_manifest`" | ✓ |
| Test 覆盖 metadata 输出 | L431: `test_preflight_outputs_static_disposition_manifest_metadata` | ✓ |

**Closed.**

## 额外验证：110020 raw disposition 追踪

| 检查项 | Plan 位置 | 状态 |
|--------|-----------|------|
| `raw_disposition` 字段存在于 FundArtifactInput | L68: `raw_disposition: str \| None` | ✓ |
| 110020 static manifest 条目保留原始值 | L339: `raw_disposition="reviewed_coverage_candidate_input_accepted"` | ✓ |
| 110020 preflight-input JSON 示例保留双字段 | L116-117: `raw_disposition` + `preflight_disposition` | ✓ |
| 110020 output row 示例保留双字段 | L192-193: `raw_disposition` + `preflight_disposition` | ✓ |
| 110020 test 验证原始值保留 | L427: `test_preflight_preserves_110020_raw_disposition_and_blocks_not_promoted` | ✓ |

**Confirmed.** Controller judgment 原始语义可追踪，不被 preflight 映射覆盖。

## Resolved Item Code 泛化

MiMo F5（原 review 中的 F5）：`bond_006597_resolved` 改为通用 `blocker_resolved`，用 `original_blocker_code` + `fund_code` 区分。

- L198-201 output 示例：`code="blocker_resolved"`, `original_blocker_code="bond_risk_evidence_missing"`, `fund_code="006597"` ✓
- L262 blocker code 定义：通用 `blocker_resolved`，必须携带 `original_blocker_code`、`fund_code`、`evidence_artifacts` ✓
- L420 test：验证通用 code 而非 per-fund code ✓

**Closed.**

## GLM F3/F4/F5 — Suggestion 级处理确认

| Suggestion | 状态 |
|------------|------|
| F3: coverage_disposition enum gap → 通过 `raw_disposition` + `preflight_disposition` 双字段解决 | ✓ |
| F4: static manifest 版本标识 → `schema_version` + `accepted_as_of` + `source_artifacts` + lifecycle exit criteria | ✓ |
| F5: `tests/ui/test_cli.py` 改为新建 | L435: "新增 `tests/ui/test_cli.py`"（非"更新"） ✓ |

## Remaining Findings

无 block 级或 warn 级 remaining findings。

以下为 info 级观察，不影响 verdict：

1. **`preflight_input` schema 中 `coverage_disposition_path` 字段可能冗余**：当使用 `--preflight-input` 时，`fund_artifacts[]` 每项已含 `raw_disposition`/`preflight_disposition`，顶层 `coverage_disposition_path` 的用途是读取外部 manifest。但 plan 说 "本 gate 若尚无 manifest，应先在代码内提供静态默认 manifest"，所以 `coverage_disposition_path` 在本 gate 下大概率为 `null`。不影响实现，但实现 worker 可考虑在 `--preflight-input` 模式下该字段的语义是否与 inline disposition 冲突。

2. **`source_artifacts` 在 output JSON 中是空数组**：plan 示例中 `static_disposition_manifest.source_artifacts: []`，但实际应填充 controller judgment artifact 路径。实现 worker 需确保代码内 manifest 的 `source_artifacts` 非空。

3. **`selected_pool_path` 在 `--preflight-input` schema 中存在但未在 CLI shortcut 模式暴露**：如果使用 `--fund-artifact` shortcut，selected pool 只能从 `source_csv` + static manifest 构造。这是 plan 设计意图（shortcut 只填 5 字段），但实现 worker 应确保 shortcut 模式下 selected pool 构造逻辑正确。

以上均为实现细节级提醒，不阻塞 implementation。

## 结论

**Verdict: accepted.** 所有 MiMo 和 GLM required fixes 均已 closed，修订后 plan 可进入 implementation。
