# Golden Readiness Preflight Plan — Rereview (GLM)

日期：2026-05-29
Review 角色：plan review worker only。不改代码、不 commit/push/PR。
Review 对象：`docs/reviews/release-maintenance-golden-readiness-preflight-plan-20260529.md`（修订后版本）
前次 review：`docs/reviews/release-maintenance-golden-readiness-preflight-plan-review-glm-20260529.md`
Gate：`golden-readiness preflight gate`

---

## Verdict: **accepted**

修订版完整闭合了前次 review 的 2 项 required fixes 和 4 项 suggestions。Blocker taxonomy、fail-closed 规则、非目标边界、模块设计、测试计划均无回归。Plan 可进入 implementation。

---

## F1 (was Required Fix) — golden-answer.json 无 report_year → Closed ✓

逐项验证：

| 前次 Required Fix 子项 | 修订版闭合位置 | 判定 |
|---|---|---|
| 显式声明 v1 无 report_year，strict golden 只做 fund-level | Plan Fix Notes L14；输入 Contract L74 "当前 v1 JSON 不含 report_year，不能做 year-level coverage 判定"；输入读取规则 L140 "当前 v1 不读取也不推断 report_year；year-level coverage 是 reserved" | ✓ Closed |
| year/partial blocker codes 标注为 reserved | Blocker 聚合规则 L271-272："reserved pending golden-answer schema v2；本 gate 不实现、不触发" | ✓ Closed |
| 修正输入 contract 描述 | 输入读取规则 L140："strict golden answer JSON v1 只读 `funds[].fund_code` 与 `funds[].records[]`" | ✓ Closed |
| Stop Conditions 新增非目标 | L508："需要实现 year-level 或 partial-field strict golden readiness；当前 v1 golden-answer schema 不支持，必须另开 schema v2 / correctness coverage gate" | ✓ Closed |
| Blocking Questions 新增 | L521："当前 strict golden answer v1 不含 report_year，所以本 gate 只能回答'fund 是否存在于 strict golden answer'" | ✓ Closed |
| ready/blocked 枚举描述更新 | L229："strict golden fund-level coverage `covered`"；L230："strict golden JSON 缺失或 fund-level 未覆盖"；L295："Year-level / partial coverage 本 gate 不触发" | ✓ Closed |
| 新增专用测试 | L429："test_preflight_reserves_strict_golden_year_and_partial_coverage_codes：确认 v1 不触发" | ✓ Closed |

**结论**：全部 7 处修改到位，无残留。

---

## F2 (was Required Fix) — CLI 输入路径 → Closed ✓

逐项验证：

| 前次 Required Fix 子项 | 修订版闭合位置 | 判定 |
|---|---|---|
| `--preflight-input` 为 production recommended，补完整 JSON schema | L59："Production recommended path"；L79-126 完整 JSON schema 示例，含 `schema_version`、每只 fund 的全部 12 个字段；L383-385 CLI 示例 | ✓ Closed |
| `--fund-artifact` shortcut 仅覆盖 5 字段，`::` 分隔 | L389-401：明确 `fund_code::report_year::snapshot_path::score_path::quality_gate_path` 五项，split 后必须精确 5 字段，路径含 `::` 必须用 JSON 路径 | ✓ Closed |
| 二者互斥 | L59："如果提供该参数，CLI 不再接受 `--fund-artifact` 等逐项输入"；L362："冲突抛 ValueError，CLI 转 exit 2"；L387："若同时提供 Service 校验冲突并退出 2" | ✓ Closed |
| Schema validation 拒绝未知字段 | L133："发现未知字段时抛 ValueError，防止形成隐式 extra_payload" | ✓ Closed |
| 新增测试 | L432："test_preflight_input_schema_rejects_unknown_fields"；L440："--fund-artifact 使用 :: 分隔且字段数必须为 5；错误字段数退出 2" | ✓ Closed |

**加分项**：分隔符从单 `:` 改为 `::`（L377），避免 Windows 路径 `C:\` 误解析，是更安全的选择。

**结论**：全部闭合，CLI 输入路径设计无歧义。

---

## F3 (was Suggestion) — coverage_disposition enum gap → Closed ✓

| 前次建议 | 修订版闭合位置 | 判定 |
|---|---|---|
| 加入 `reviewed_coverage_candidate` 枚举或保留原始值 traceability | L69：`preflight_disposition` enum 新增 `reviewed_coverage_candidate`；L68：新增 `raw_disposition: str \| None` 捕获 controller judgment 原始值；L132："raw_disposition 是 controller judgment 原始 terminal/disposition 字符串；preflight_disposition 是 preflight enum 映射。二者都写入输出 JSON" | ✓ Closed |
| Static manifest 110020 条目双字段 | L339：`raw_disposition="reviewed_coverage_candidate_input_accepted"`、`preflight_disposition="reviewed_coverage_candidate"` | ✓ Closed |
| Per-fund row 输出双字段 | L192-193：示例 row 包含 `raw_disposition` 和 `preflight_disposition` | ✓ Closed |
| 新增测试 | L427："test_preflight_preserves_110020_raw_disposition_and_blocks_not_promoted" | ✓ Closed |

**结论**：raw + mapped 双字段方案比原建议更优——`raw_disposition` 是自由字符串，不限制 controller judgment 表达；`preflight_disposition` 是受控枚举，保证 preflight 逻辑确定性。二者同时写入输出 JSON，traceability 完整。

---

## F4 (was Suggestion) — static manifest 版本/lifecycle → Closed ✓

| 前次建议 | 修订版闭合位置 | 判定 |
|---|---|---|
| 版本标识 | L336：manifest 必须含 `schema_version`、`accepted_as_of`、`source_artifacts` | ✓ Closed |
| 输出 JSON 包含 manifest | L159-163：顶层 `static_disposition_manifest` 含三个元数据字段 + entries | ✓ Closed |
| 升级/过期条件 | L346-352：4 条明确 exit criteria（disposition 变更/新 fund/promotion 变更/超过 3 条目跨 gate 复用） | ✓ Closed |
| 新增测试 | L431："test_preflight_outputs_static_disposition_manifest_metadata" | ✓ Closed |

**结论**：lifecycle exit criteria 明确且可操作。特别是"3 条目以上或跨 gate 复用"触发升级这条，防止 static manifest 无限膨胀。

---

## F5 (was Suggestion) — tests/ui/test_cli.py 新建 → Closed ✓

L435："新增 `tests/ui/test_cli.py`"（原文是"更新"，已改为"新增"）。✓

实现 worker 需注意 Typer `CliRunner` harness 配置，但这是 implementation detail，不阻塞 plan。

---

## F6 (was Confirmation) — 006597 处理 → 仍然正确 ✓

修订版进一步改进了 resolved item 模式：从 `bond_006597_resolved` 改为 generic `blocker_resolved` + `original_blocker_code="bond_risk_evidence_missing"` + `fund_code="006597"`（L198-202, L262）。这避免了为每只基金扩散 resolved code，是更可扩展的设计。

---

## 新增内容审查

修订版新增了以下内容，需确认无回归：

### 1. Plan Fix Notes / Controller Disposition 段落（L11-20）

清晰记录每项 fix 的闭合状态和决策依据。无问题。

### 2. MiMo findings 闭合（L13, L16-17）

Plan 同时处理了 MiMo review 的 findings（F1 module path rejection、F2 fixture promotion manifest default removal、F3 static manifest metadata）。与 GLM findings 方向一致，无冲突。

### 3. `--fund-artifact` 路径含 `::` 的限制（L401）

"shortcut 不支持路径中包含 `::`；如有该需求必须使用 `--preflight-input` JSON"——合理 fallback。当前项目路径不含 `::`，短期不构成问题。

### 4. 110020 示例中 score/quality 路径在 extraction-snapshots/ 下（L112-113）

示例 JSON 中 110020 的 `score_path` 和 `quality_gate_path` 指向 `reports/extraction-snapshots/110020-.../score.json`，而非标准 `reports/scoring-runs/` / `reports/quality-gate-runs/`。这可能是示例 copy-paste 不精确，但 preflight 只读 JSON 字段不依赖路径目录结构，实际路径由 input JSON 显式传入，所以不影响实现。属于 cosmetic issue，不阻塞。

---

## 无回归确认

| 维度 | 判定 |
|---|---|
| Gate classification `heavy` | ✓ 未变 |
| 006597 bond blocker resolved | ✓ 未变，且 resolved item 更通用 |
| 006597 quality warn 不当 ready | ✓ 未变 |
| Fail-closed 规则 | ✓ 未变，新增 year/partial golden 不触发说明 |
| Stop Conditions | ✓ 未变，新增 year-level golden 非目标 |
| 非目标边界（promotion/FQ0-FQ6/Host/Agent/dayu/PR） | ✓ 未变 |
| 模块位置 `fund_agent/fund/` | ✓ 未变 |
| 无 extra_payload 风险 | ✓ 未变，且新增 unknown field rejection |

---

## Remaining Observations（non-blocking）

1. **110020 示例路径 cosmetic issue**：input JSON 示例中 110020 的 `score_path` / `quality_gate_path` 指向 `extraction-snapshots/` 子目录而非 `scoring-runs/` / `quality-gate-runs/`。实现 worker 应使用实际 artifact 路径，示例仅供参考。

2. **`selected_pool_path` 消费逻辑未细化**：输入 contract 声明该参数（L58），但 preflight 聚合规则和代码设计中未描述其具体消费方式。由于该参数为 optional 且不影响 blocker 聚合核心逻辑（fund_artifacts 是主输入），可由实现 worker 在实现时补全，不阻塞 plan。

以上两项均为 implementation detail 层面，不影响 plan correctness。
