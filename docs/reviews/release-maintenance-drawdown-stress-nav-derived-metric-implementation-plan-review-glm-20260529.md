# Drawdown Stress NAV-Derived Metric Implementation Plan — Adversarial Review (GLM)

日期：2026-05-29
角色：plan review worker only。不做实现、修复、commit、push、PR、merge、release、golden promotion。
Gate：`drawdown_stress NAV-derived metric contract / implementation gate`
Gate classification：`heavy`

---

## 0. 审查范围与方法

### 0.1 规则真源

- `AGENTS.md` 是本仓库所有 Agent 执行规则的唯一权威入口。
- 当前目标架构固定为 `UI -> Service -> Host -> Agent`；当前确定性 CLI 主链路仍是 UI -> Service -> `fund_agent/fund` Agent 层基金能力过渡实现。
- `docs/design.md` 是设计真源；`docs/implementation-control.md` 是实施总控。

### 0.2 审查对象

- Plan artifact：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md`
- Required truth sources：全部读取，包括 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、typed NAV controller judgment / DS / GLM aggregate deepreviews、CSRC EID controller judgment / evidence / MiMo / GLM aggregate deepreviews。
- Relevant code paths：逐文件阅读 `bond_risk_evidence.py`（全文 2550+ 行）、`extractors/models.py`（Literal 域、validator 链、dataclass 定义）、`nav_models.py`（FundNavSeries/strong_drawdown_eligibility）、`nav_repository.py`（load_nav_series 签名与 CSRC accumulated path）、`data_extractor.py`（extract() 主链路与 bond_risk_evidence 调用）、`extraction_snapshot.py`（bond_risk 投影逻辑）、`extraction_score.py`（bond_risk_evidence_missing issue 派生逻辑）。
- Latest run artifacts：006597/2024 snapshot.jsonl、score.json、quality_gate.json。

### 0.3 审查方法

独立逐项对照 10 个审查焦点，对 plan 做对抗性审查。对每个焦点验证：(1) plan 声称是否与代码事实一致；(2) 与真源文档是否对齐；(3) 是否存在遗漏或隐含风险。

---

## 1. Max Drawdown Alone 是否足够作为 drawdown_stress 最小可接受指标

**结论：defensible，accepted。**

Plan 选择 max drawdown alone 的理由：

1. `drawdown_stress` 当前阻断源是缺少"最大回撤、波动率、压力测试阈值状态，或带来源锚点的回撤/压力计算"之一——这些是替代条件而非全部必要条件。最大回撤直接度量净值路径从峰值到谷值的最大损失，最贴合债券基金第 6 章"核心风险"中回撤压力问题。
2. `docs/design.md` §3.4 preferred_lens 表明确将"最大回撤"列为债券基金 (`bond_fund`) 的核心关注点，而非波动率。
3. 波动率衡量收益离散度，不等同于最坏路径损失；作为后续增强指标有价值，但不是解除 blocker 的最小必要条件。
4. 只接受一个最小指标可以减少 contract/snapshot 扩面，降低 heavy gate 风险。

代码验证：
- `_extract_drawdown_stress()` 当前只搜索"回撤"文本，不搜索"波动率"。说明当前 extractor 语义本身就以回撤为核心。
- `extraction_score.py` 的 `BOND_RISK_EVIDENCE_GROUPS` 中 `drawdown_stress` 组名为"drawdown"而非"volatility"，语义对齐。

Plan 正确将 volatility 标记为 non-goal / residual。后续如需 volatility，必须独立 gate 定义日收益率、年化因子、交易日样本、节假日缺口和单位。

---

## 2. 006597/A 作为主证据且不混合 A/C/E/F 是否正确

**结论：correct，accepted。**

代码事实验证：
- 006597 是请求基金代码，A 类是其主份额。
- 006598/C、014217/E、022176/F 有不同的费用路径和成立日期（E 2022-04-25，F 2024-10-08），混合会破坏 source identity。
- `implementation-control.md` Next Entry Point 明确要求："Keep A/C/E/F NAV series separated; do not mix share classes into one product-level NAV path."
- CSRC EID source 按 classification 分份额输出，fund_id=5755 下 A/C/E/F 有不同 source_id（2030-1010/1020/1040/1050）。

Plan 正确规定 C/E/F 仅允许 smoke/diagnostics，不进入 `drawdown_stress` group 的 metric_value。

---

## 3. 2024-01-01..2024-12-31 作为 006597/2024 证据周期是否正确

**结论：correct，accepted。**

验证：
- `bond_risk_evidence.v1` 由 `report_year=2024` 驱动，snapshot/score 也是 `fund_code + report_year` 粒度。同年 period 能与 annual-report 风险披露同源对齐。
- Trailing window 会引入 report cutoff 之后的信息，对 2024 年报证据不公平，也可能让 006597/2024 因 2025/2026 数据变化而不稳定。
- CSRC EID source 返回交易日记录；非交易日缺失不补齐、不插值——这与 accumulated NAV 路径的实际行为一致（真实 smoke 显示 006597/A 2018-12-18 到 2026-05-28 共 1807 records，约为交易日密度）。
- Plan 正确要求 metric helper 二次过滤 `period_start <= record.date <= period_end`，因为 repository 返回完整 series 而非窗口裁剪 series。

**Non-blocking observation N1**：Plan 中提到 `minimum_period_records=30`（§ 4. Formula 步骤 3）与函数参数名 `minimum_records`（§ Implementation Design）不同。虽然语义清晰（前者指过滤后的 period 级阈值，后者是函数参数名），但建议 implementation worker 在代码中保持一致的命名以避免歧义。

---

## 4. Formula / Fail-Closed 设计是否完整覆盖各种异常场景

**结论：comprehensive，accepted with one non-blocking finding。**

逐项验证：

| 场景 | Plan 处理 | 与现有代码对齐 | 判定 |
|---|---|---|---|
| 重复 date | fail-closed `integrity_error`，不 silent dedupe | `nav_models.py:397-403` `_validate_record_shape` 已做 duplicate → `integrity_error` | ✅ |
| 非交易日缺失 | 不补齐、不插值，只消费落入 period 的 records | CSRC EID source 本身只返回交易日记录 | ✅ |
| insufficient records | `< minimum_period_records` → fail-closed | `nav_models.py:503-508` 已有 `insufficient_records` | ✅ |
| source unavailable | group remains weak/missing | 与 `implementation-control.md` fail-closed taxonomy 一致 | ✅ |
| raw_unit_nav | reject with `na_reason` | `nav_models.py:550-562` validator 已强制 `strong_drawdown_evidence_eligible=False` | ✅ |
| ineligible source | reject with `na_reason` | 与 `_apply_strong_drawdown_eligibility` 一致 | ✅ |
| NAV <= 0 | fail-closed `integrity_error` | `nav_repository.py:395-401` 已有 nonpositive NAV → `integrity_error` | ✅ |
| identity_status != "verified" | reject | `nav_models.py:544-546` 已有 | ✅ |
| adjusted_basis != "accumulated_nav" | reject | `nav_models.py:556-558` 已有 | ✅ |
| strong_drawdown_evidence_eligible not True | reject | 与 validator 行为一致 | ✅ |
| schema_drift / identity_mismatch / integrity_error from source | fail-closed, group not accepted | 与 CSRC EID adapter fail-closed 行为一致 | ✅ |
| metric calculation error | reject, `na_reason="drawdown_metric_calculation_error"` | 新增 category，合理 | ✅ |
| unsorted records | sort before calculation | repository 已排序；二次排序是防御性正确 | ✅ |

Formula 正确性验证：
- `drawdown = nav_value / peak_value - 1`：数学正确，非正数，0 表示无回撤
- Running peak 追踪：标准算法
- 输出为 Decimal ratio（如 `-0.0123`）而非百分比：与 `metric_unit="ratio"` 一致
- Tie handling（多个 trough 相同最大回撤时保留最早 trough）：合理
- 全期单调不跌时 `max_drawdown_ratio=Decimal("0")`，peak/trough 均为第一条记录：正确

**Non-blocking finding N2**：Plan § Fail-Closed Behavior 的 `schema_drift` 行说 "fail-closed; group must not be accepted; preserve category in reviewer_note / na_reason"。但 `na_reason` 当前可接受的值集没有枚举 `drawdown_nav_schema_drift` 之类的前缀。建议 implementation worker 使用一致的 `na_reason` 前缀模式（如 `drawdown_` 前缀），但不阻塞 plan acceptance。

---

## 5. Additive Enum Extension 与 Schema Version（最重要）

**结论：accepted as additive semantic extension under heavy gate。Plan 正确识别风险且不弱化 FQ0-FQ6。**

### 5.1 现状

代码中 `extractors/models.py` 当前定义：

```python
BondRiskEvidenceStrength = Literal[
    "quantitative_direct", "quantitative_absence",
    "qualitative_direct", "qualitative_control_intent",
    "ambiguous", "missing"
]  # 6 values

BondRiskEvidenceMeasurementKind = Literal[
    "actual_metric", "actual_exposure", "explicit_absence",
    "risk_disclosure", "strategy_text", "control_intent", "not_found"
]  # 7 values

_BOND_RISK_ACCEPTED_STRENGTHS = frozenset((
    "quantitative_direct", "qualitative_direct"
))  # 2 values
```

### 5.2 Plan 提议

- `BondRiskEvidenceStrength` 增加 `"quantitative_derived"`（第 7 个值）
- `BondRiskEvidenceMeasurementKind` 增加 `"derived_metric"`（第 8 个值）
- `_BOND_RISK_ACCEPTED_STRENGTHS` 扩展为包含 `"quantitative_derived"`（第 3 个值）
- `_validate_bond_risk_status_strength()` 允许 `status="accepted"` + `strength="quantitative_derived"` + `measurement_kind="derived_metric"`
- 不 bump `BondRiskEvidenceSchemaVersion`（仍为 `"bond_risk_evidence.v1"`）

### 5.3 为什么这是可接受的 additive extension

**不构成 structural schema change 的理由**：

1. Dataclass 字段形状不变：`BondRiskEvidenceGroupRecord`、`BondRiskEvidenceValue`、`EvidenceAnchor` 的所有字段类型和数量均不变。
2. 现有 Literal 值全部保留：没有任何旧值被删除、改名或改变语义。
3. Wire format 不变：序列化为 JSON 的结构完全相同，只是多了一种合法的字符串值。
4. 所有现有数据保持 valid：使用旧 Literal 值的记录不受影响。

**是 semantic extension**：

`_BOND_RISK_ACCEPTED_STRENGTHS` 从 2 个值扩展到 3 个值，改变了 `status="accepted"` 允许的 strength 组合。这是一种语义扩展——扩大了 "accepted" 的定义范围。

### 5.4 为什么不弱化 FQ0-FQ6

逐项验证：

| 规则 | 是否受影响 | 理由 |
|---|---|---|
| FQ0 | 不受影响 | score.json 数据结构不变 |
| FQ1 | 不受影响 | correctness 比对不涉及 bond_risk_evidence strength |
| FQ2 | 不受影响 | coverage/traceability 阈值不变 |
| FQ2F | 自然消失 | `_bond_risk_unsatisfied_groups()` 只检查 `contract_status` 和四个 group ID 集合，不检查 `strength` 或 `measurement_kind`。当 `drawdown_stress` 进入 `satisfied_group_ids` 后，unsatisfied groups 自然为空 |
| FQ3 | 不受影响 | traceability 阈值不变 |
| FQ4 | 不受影响 | 缺失率计算不变 |
| FQ5 | 不受影响 | preferred_lens 不涉及 bond risk strength |
| FQ6 | 不受影响 | 抽取流程失败处理不变 |

关键代码路径验证：
- `_bond_risk_unsatisfied_groups()`（`extraction_score.py:1855`）：只看 `contract_status`、`satisfied_groups`、`missing_groups`、`weak_groups`、`ambiguous_groups` 这五个结构化字段。不解析 `strength` 或 `measurement_kind`。
- `_bond_risk_evidence_missing_issue()`（`extraction_score.py:1753`）：创建 issue 时只设置 `severity="warn"`、`baseline_blocking=True`、`rule_code_hint="FQ2F"`，不涉及 strength。
- `_build_bond_risk_evidence_record()`（`extraction_snapshot.py:1012`）：投影到 SnapshotRecord 时只提取 `contract_status` 和四个 group ID 集合，不提取 strength 或 measurement_kind。

因此，`quantitative_derived` / `derived_metric` 的引入只会通过正常的 `satisfied_group_ids` 路径自然消除 blocker，不会绕过或弱化任何 FQ 规则。

### 5.5 为什么不 bump schema version

`bond_risk_evidence.v1` 的 version 标识的是 dataclass 字段结构版本，不是 validation rule 版本。当前字段形状不变，只有 Literal 枚举值扩展。这与 AGENTS.md 的 gate 分类规则一致：additive enum extension 在 heavy gate 下可以实现。

如果后续 reviewer 认为应该 bump 到 v2，那是 controller decision，不阻塞本 plan acceptance。

---

## 6. Derived Anchor 与 section_id="derived:nav" / source_kind="derived" 的兼容性

**结论：compatible，accepted。**

代码验证：
- `EvidenceAnchor.source_kind` 类型为 `Literal["annual_report", "external_api", "derived"]`——`"derived"` 已存在于 Literal 域中。
- `EvidenceAnchor.section_id` 类型为 `str`，无格式限制。`"derived:nav"` 是合法字符串值。
- `BondRiskEvidenceAnchorRef.section_id` 同样为 `str`，无格式限制。
- Snapshot 投影逻辑 `_build_bond_risk_evidence_record()` 不解析 `section_id` 的格式或内容，只提取结构化 group 字段。
- Score 逻辑 `_bond_risk_unsatisfied_groups()` 完全不触及 anchor 字段。

Plan 提议的 anchor convention（`source_kind="derived"`、`section_id="derived:nav"`、`row_locator="metric:max_drawdown:..."`）与现有类型定义完全兼容。

Plan 提议的 `_build_group_anchors()` 修改——根据 `section_id.startswith("derived:")` 设置 `source_kind="derived"` vs `"annual_report"`——是一个 extractor 内部行为变更，但不是 snapshot schema 变更。正确。

**Non-blocking finding N3**：Plan § Anchor Builder 提议修改 `_build_group_anchors()` 使其对 `section_id.startswith("derived:")` 设置不同的 `source_kind`。Implementation worker 应确保该分支逻辑有独立测试覆盖，且不影响现有 annual-report anchor 的 `source_kind` 赋值。不阻塞。

---

## 7. 数据边界是否正确

**结论：correct，accepted。**

验证：
- Plan 明确规定 metric consumer 只能通过 `FundNavRepository.load_nav_series()` 读取 series。
- 禁止在 extractor 里直接调用 `CsrcEidNavSource`、httpx endpoint、stock-sdk、Eastmoney、Akshare、SQLite cache 或 `FundNavDataAdapter.load_nav_data()`。
- Extractor 只接收预计算的 `NavMaxDrawdownMetric` 或错误——这是一个 DTO，不携带任何 IO 能力。
- Repository 调用在 `data_extractor.py`，不在 `bond_risk_evidence.py`——保持 extractor 为纯计算模块。
- 参数全部显式声明（`fund_code`、`share_class`、`start_date`、`end_date`、`minimum_records`、`force_refresh`），无 `extra_payload`。

Plan 的推荐架构（async wrapper in data_extractor, sync extractor with DTO input）是合理的，保持了 extractor 的确定性和可测试性。

---

## 8. 测试与验证是否充分

**结论：sufficient，accepted with one non-blocking enhancement。**

Plan 规定 9 类测试，逐项验证充分性：

| # | 测试类别 | 覆盖范围 | 充分性 |
|---|---------|---------|--------|
| 1 | Max drawdown 计算 | 正确路径 + monotonic + peak/trough 精确 | ✅ |
| 2 | Bad series fail-closed | insufficient records / duplicate dates / non-positive NAV / ineligible source | ✅ |
| 3 | Raw-unit rejection | constructor-injected raw adapter never yields accepted group | ✅ |
| 4 | 006597/A accepted path | fake typed repository → FundDataExtractor → satisfied_group_ids contains drawdown_stress | ✅ |
| 5 | No A/C/E/F mixing | fake repository 只收到 006597/A 调用，无 006598/014217/022176 | ✅ |
| 6 | Provenance completeness | anchor note 包含全部审计关键字段 | ✅ |
| 7 | Weak qualitative not promoted | control text alone remains weak; NAV unavailable → score still lists drawdown_stress | ✅ |
| 8 | Snapshot/score/quality true path | satisfied contract → no bond_risk_evidence_missing → no FQ2F | ✅ |
| 9 | Contract extension | validator accepts new combination, rejects incompatible ones | ✅ |

**Non-blocking finding N4**：Test 7 规定 "when NAV metric is unavailable/error, weak annual-report text still remains weak and score still lists drawdown_stress"。这是一个退路测试（regression test），但它只覆盖"NAV 不可用"的场景。建议增加一个显式的 regression test：当 drawdown_stress 是唯一 unsatisfied group 时，score 仍产生 `bond_risk_evidence_missing` issue（其他六组 satisfied）。这能证明新实现不会意外影响其他组的 satisfaction 判定。不阻塞——Plan 测试集已足够全面，此为增强建议。

---

## 9. Allowed File List 是否过宽或缺失

**结论：acceptable with tightening recommendation。**

Production files:

| 文件 | 评估 |
|---|---|
| `fund_agent/fund/data/nav_metrics.py`（新增） | ✅ 合理 |
| `fund_agent/fund/data/__init__.py` | ✅ 导出 metric types |
| `fund_agent/fund/data_extractor.py` | ✅ wiring |
| `fund_agent/fund/extractors/models.py` | ✅ Literal 扩展 |
| `fund_agent/fund/extractors/bond_risk_evidence.py` | ✅ extractor extension |
| `fund_agent/fund/extraction_snapshot.py` | ⚠️ "only if needed for derived anchor projection tests" |
| `fund_agent/fund/extraction_score.py` | ⚠️ "only if tests reveal issue wording needs no change" |
| `fund_agent/fund/README.md` | ✅ |
| `tests/README.md` | ✅ |

**Non-blocking finding N5**：`extraction_snapshot.py` 和 `extraction_score.py` 的条件允许语言（"only if needed"/"only if tests reveal"）偏宽。建议 implementation worker 在实施前明确判断是否需要修改这两个文件，如果需要，应在 evidence artifact 中说明具体修改内容和理由。不阻塞——Plan 的 disallowed list 已明确排除 score threshold/policy logic 和 FQ semantic changes。

Disallowed list 正确排除了：quality_gate.py、quality_gate_integration.py、golden fixtures、Service/UI/Host/Agent/dayu、CSRC source adapter。

---

## 10. 阻断发现与非阻断发现汇总

### Blocking Findings

**无。**

Plan 在所有审查焦点上均与真源文档和代码事实对齐，未发现阻断性问题。

### Non-Blocking Findings

| # | 严重度 | 内容 | 建议 |
|---|--------|------|------|
| N1 | LOW | Plan § 4. Formula 步骤 3 使用 `minimum_period_records` 而 Implementation Design 使用 `minimum_records` | Implementation worker 保持命名一致 |
| N2 | LOW | Fail-closed 表中 `na_reason` 的前缀模式未统一枚举 | Implementation worker 使用 `drawdown_` 前缀统一 na_reason |
| N3 | LOW | `_build_group_anchors()` 新增 `section_id.startswith("derived:")` 分支 | 确保独立测试覆盖，不影响现有 annual-report anchor |
| N4 | LOW | 缺少显式 regression test（仅 drawdown_stress unsatisfied 时 score 仍产生 blocker） | 建议补充，不阻塞 |
| N5 | LOW | `extraction_snapshot.py` / `extraction_score.py` 条件允许语言偏宽 | Implementation worker 在 evidence 中说明具体修改理由 |

### Residual Risks（Plan 已正确识别）

| Residual | 评估 |
|----------|------|
| CSRC EID endpoint 无 SLA | Plan 正确处理为 fail-closed |
| `source_query_params` 语义混合 | 不在本 gate scope 内 |
| CSRC source 限定 006597 家族 | 已接受 residual |
| Accumulated NAV 不是 total-return index | Plan 正确不重新标记 |
| Volatility 为 non-goal | 正确，后续独立 gate |

---

## 11. Slice 结构评估

Plan 5-slice 分解合理：

| Slice | 目标 | 依赖 | 评估 |
|-------|------|------|------|
| Slice 1 | Metric 纯计算 | 无外部依赖 | ✅ 可独立测试 |
| Slice 2 | Contract extension + anchor projection | 依赖 Slice 1 类型定义 | ✅ 正确依赖 |
| Slice 3 | DataExtractor wiring | 依赖 Slice 1 + 2 | ✅ 正确依赖 |
| Slice 4 | Snapshot/score/quality natural path tests | 依赖 Slice 1 + 2 + 3 | ✅ 集成验证 |
| Slice 5 | Docs + real evidence | 依赖全部前置 | ✅ 最终验证 |

每个 slice 都有明确的 stop condition，且 stop condition 不会激励在缺少直接证据时错误接受数据。

---

## 12. Verdict

**accepted**

理由：

1. Max drawdown alone 作为最小可接受指标：defensible，与 preferred_lens 和当前 extractor 语义对齐。
2. 006597/A 不混合 A/C/E/F：与 implementation-control 和 CSRC EID 分份额验证一致。
3. 2024 annual period：与 report_year 粒度和 annual-report 风险披露同源对齐。
4. Formula / fail-closed 设计：全面覆盖 8 类失败场景，与现有 taxonomy 一致，数学正确。
5. Additive enum extension：不改变 dataclass 字段形状，不弱化 FQ0-FQ6（下游 consumer 只看结构化 group 字段），在 heavy gate 下可接受。Schema version 不 bump 是合理的。
6. Derived anchor：`source_kind="derived"` 已存在于 Literal 域，`section_id="derived:nav"` 为合法字符串值，与 snapshot/score 投影逻辑兼容。
7. 数据边界：只有 `FundNavRepository.load_nav_series()`，extractor 不直接 IO，参数全部显式。
8. 测试与验证：9 类测试覆盖计算正确性、fail-closed、退路、provenance、snapshot/score/quality 自然路径。
9. 文件列表：无过宽风险，条件允许项有合理的限定语。
10. 零 blocking finding，5 条 non-blocking finding 全部为 LOW 级别。

Plan 达到 code-generation-ready 状态，可交由 implementation worker 执行。

---

## 13. 文件路径

| 文件 | 路径 |
|---|---|
| 本 review | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-review-glm-20260529.md` |
| Plan artifact | `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-plan-20260529.md` |
