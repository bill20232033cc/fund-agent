# MVP Small Golden Set Row-field Extractor Gap Decision Gate — DS Review

- **Reviewer**: AgentDS
- **Role**: Independent decision review（独立复核，不进入实现，不处理 PR #22，不进入其它 gate）
- **Date**: 2026-06-09
- **Target**: `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md`
- **Classification**: `standard`（与 target gate 分类一致）

## Review Scope

审核该决策 gate 对 `manager` / `holdings` / `risk` 三个 blocked gap 的下一步路由判断是否正确、是否越界授权、下一 gate 是否为 code-generation-ready。本 review 不改实现、不读 PDF、不跑测试、不 stage/commit/push/PR。

## Evidence Sources Reviewed

| Source | Path | Relevance |
|--------|------|-----------|
| AGENTS.md | `/AGENTS.md` | 最高优先级执行规则 |
| Startup Packet | `docs/current-startup-packet.md` | 当前 gate 状态、prohibited actions |
| Control Doc | `docs/implementation-control.md` | 当前 gate closeout、next entry、residuals |
| Design Doc | `docs/design.md` | 架构边界、extractor 归属 |
| Retained Oracle | `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` | risk/holdings/manager expected values |
| Correctness Test | `tests/fund/test_small_golden_set_extractor_correctness.py` | 当前 test construction、xfail markers |
| profile.py | `fund_agent/fund/extractors/profile.py` | `style_positioning` 提取路径、`fund_manager` 字段 |
| holdings_share_change.py | `fund_agent/fund/extractors/holdings_share_change.py` | `top_holdings` 提取路径、表关键词 |
| manager_ownership.py | `fund_agent/fund/extractors/manager_ownership.py` | 管理人持有/换手率/持有人结构 |

---

## Findings

### F1. [MEDIUM — not blocking] `risk` → `style_positioning` 映射路径未经验证，依赖下一 gate 的 test construction 调整

**位置**: Decision gate L33 `risk` 行，“Convert to passing row-field assertion in the next test-only gate”；L44 允许“Remove `risk` from strict xfail only if adding passing `extract_profile(...).product_profile.value["style_positioning"]` assertions”。

**证据**:

当前 `test_small_golden_set_extractor_correctness.py` 的 `_build_report_from_oracle_row()` 将 risk 文本构造为 `("基金类型", _risk_category_text(row))` 表格行（L246），通过该路径进入 `basic_identity.fund_category`，而非 `product_profile.style_positioning`。

`profile.py` 中 `style_positioning` 提取路径有两条（L45–53, L71, L837–839）：
1. Text extraction：匹配 §2 raw_text 中 `风险收益特征：` / `风格定位：` / `产品定位：` 正则
2. Table extraction：匹配表格中 label 为 `("风格定位", "风险收益特征", "产品定位")` 的键值行（L71）

当前 test construction 的 §2 raw_text 只包含 `"基金类型：{risk_text}"` 和 `"业绩比较基准：{benchmark}"`（L305–306），不包含 `"风险收益特征："` 前缀。`_profile_table` 表格中 key 为 `"基金类型"` 而非 `"风险收益特征"`（L246）。因此当前 test construction 下 `style_positioning` **不会命中** retained risk 文本。

**判定**:

这不是 blocker，因为：
1. 下一 gate 可以在不修改 extractor 的前提下调整 test construction（例如将 `"基金类型"` 表格行改为 `"风险收益特征"`，或在 §2 raw_text 中增加对应行）。
2. Decision gate L81 stop condition 正确覆盖了此场景：`"If review finds that risk is not reliably exposed through product_profile.style_positioning, do not open risk test extension; move risk to row-shape contract decision."`

但 decision gate 正文**未明确提及**此 test construction 调整需求，可能被误解为当前 extractor 路径已天然覆盖 risk。建议在 decision gate 或下一 gate plan 中显式记录：

> `risk` → `style_positioning` 需要在 test construction 中调整表格列标签或 §2 raw_text，使 risk 文本通过 extractor 的 `style_positioning` label 路径进入，而非通过 `fund_category`。

**Residual risk**: 若下一 gate 直接打开 `style_positioning` assertion 而不调整 test construction，`style_positioning` 将为 `None`（`explicit_style` 为 None 且 `_derive_style_positioning(objective)` 因为无 investment_objective 而返回 None），导致测试 FAIL。stop condition 可拦截此情况，但可能浪费一轮 gate cycle。

---

### F2. [LOW] `holdings` equity split 的 extractor 股票导向假设可接受，但 017641 QDII 的 table shape 未被充分探索

**位置**: Decision gate L34 `holdings` 行；L45–48 列出 004393/004194/017641 进入 `holdings_snapshot.top_holdings` 测试。

**证据**:

`holdings_share_change.py` L18–19 的表格关键词：
```python
_TOP_HOLDINGS_TABLE_KEYWORDS = ("前十大", "重仓")
_ALL_STOCK_DETAILS_KEYWORDS = ("股票代码", "股票名称", "数量", "公允价值", "占基金资产净值比例")
```

上述关键词全部为股票导向，methods 命名（`_ALL_STOCK_DETAILS_KEYWORDS`、`_find_holdings_source` docstring 写"股票持仓明细来源"）也表明当前 extractor 设计范围是股票持仓。

三个获批进入测试的行的 retained expected shapes：
- `004393` `top_stock_table_row`: 标准 A 股股票行（code=00939 建设银行）
- `004194` `top_index_stock_table_row`: 指数增强股票行（code=600428 中远海特）
- `017641` `top_equity_table_row`: QDII 美股行（code=AAPL APPLE INC）

004393 和 004194 的表格结构符合股票导向关键词。017641 是 QDII 基金，其 §8.4 权益投资明细表可能使用不同的表头中文措辞（如"证券代码"而非"股票代码"），decision gate 未对此做显式评估。

**判定**: 不阻塞。decision gate 中 017641 的 `top_equity_table_row` 命名（`top_equity`而非 `top_stock`）暗示了 awareness of shape difference。且 decision gate 已将 017641 纳入允许列表，下一 gate 的具体 test construction 会自然验证。但建议下一 gate plan 对 017641 的表头兼容性做显式检查。

---

### F3. [LOW] `manager` deferral 正确但 decision gate 未引用关键代码证据说明 `fund_manager` 与 retained `manager` 的形状差距

**位置**: Decision gate L35 `manager` 行。

**证据**:

Retained oracle 中 `manager` expected 是结构化列表：
```json
[{"name": "张明", "role": "基金经理", "start_date": "2022-08-08"}]
```

而 `profile.py` L35–38 的 `fund_manager` 提取路径：
```python
"fund_manager": (
    ("§1", (r"基金经理\s*[：:]\s*(.+)",)),
    ("§2", (r"基金经理\s*[：:]\s*(.+)",)),
),
```
产出的是**单一字符串**（如 `"张明"`），不是结构化列表。`profile.py` L801 将其放入 `basic_identity.value["fund_manager"]` 作为原始字符串。

`manager_ownership.py` 处理的是管理人报告文本、换手率、基金经理持有比例、持有人结构——不涉及基金经理身份/任期（L34–59）。

**判定**: 结论正确——当前无 extractor surface 可产出 retained `manager` 结构化列表。decision gate 将 manager 路由到 "portfolio-manager identity/tenure output contract" 是合理的。但 decision gate 正文 L35 只写了 `profile.basic_identity.value["fund_manager"]` is "a simple profile string"，未引用代码行号或说明 structured list vs flat string 的具体差距。建议补充代码引用以增强 traceability。

---

### F4. [PASS] 无越界授权

Decision gate L40–57 明确划分了下一 gate 的 Allowed / Forbidden。

对照 startup packet §7 "Prohibited Actions" 和 control doc L72–74 的当前 gate constraints：

| 越界检查项 | Decision gate 处理 | 结论 |
|---|---|---|
| Extractor modification | L54 明确禁止 | PASS |
| PDF read / FDR live acquisition | L55 明确禁止 | PASS |
| Network / fallback / live provider | L55 明确禁止 | PASS |
| Provider/default/runtime/budget/config 变更 | L56 明确禁止 | PASS |
| Fixture projection / golden promotion | L57 明确禁止 | PASS |
| Release / merge / mark-ready | L57 明确禁止 | PASS |
| Chapter calibration / Agent runtime expansion | 未提及（但不在 scope 中，decision gate 本身不涉及） | PASS |
| 对 `docs/reviews/` 外的文件写入 | 仅本 artifact；未改实现文件 | PASS |

**判定**: PASS — 无越界。decision gate 的 allowed/forbidden 边界与 startup packet 的 current gate constraints 一致。

---

### F5. [PASS] 下一 gate 为 code-generation-ready

Decision gate L39–57 为下一 gate 定义了清晰的操作语义：

- **Allowed fields**: `risk`（转 passing，通过 `style_positioning`）、`holdings`（仅 004393/004194/017641 的 `top_holdings`）
- **Forbidden fields**: `manager`、`holdings` 的 006597/110020
- **Stop conditions**（L80–83）:
  1. risk 不可靠 → 移到 row-shape contract decision
  2. holdings 不可靠 → 全部移到 row-shape contract decision
  3. 任何路径需要 PDF/FDR/network → 停止并另开 gate
- **Oracle**: 唯一 correctness oracle 为 retained excerpt JSON

下一 gate implementer 可以直接对照这些约束编写测试，无需额外决策。

**判定**: PASS。

---

## Verification Matrix Cross-Check

Decision gate L69–76 的 Verification Matrix：

| 声明 | 本 review 确认 | 备注 |
|---|---|---|
| Branch/status reviewed | 未独立验证（review scope 内不要求；control doc 确认当前 gate closeout） | 依赖 control doc truth |
| Rule/control/design truth reviewed | 已确认 decision gate 引用 AGENTS.md / startup packet / control doc / design doc | 文件存在且内容一致 |
| Retained expected shapes reviewed | 已通过 oracle JSON 验证所有 5 行 × 8 字段 | 见 F1–F3 |
| Extractor surfaces reviewed | 已通过 `profile.py` / `holdings_share_change.py` / `manager_ownership.py` 验证 | decision gate 未提供行号引用（F1/F3 已标记） |
| No implementation performed | 确认 git status 无 source/test/config 变更 | 仅 untracked review artifacts |

---

## Summary

| 严重度 | 数量 | 关键项 |
|---|---|---|
| BLOCKING | 0 | — |
| MEDIUM | 1 | F1: `risk` → `style_positioning` test construction gap 未显式记录 |
| LOW | 2 | F2: 017641 QDII table shape 未充分评估；F3: `manager` deferral 缺代码行号引用 |
| PASS | 2 | F4: 无越界授权；F5: 下一 gate code-generation-ready |

## Verdict

**PASS — no blocking findings.**

Decision gate 的三个字段路由决策（risk → test extension via `style_positioning`，holdings → split by row shape，manager → defer）均被代码证据支持。越界授权检查通过。下一 gate 允许/禁止/停止条件完整明确。

## Re-review（2026-06-09 targeted）

Decision gate 已更新，对照原始 5 findings 逐项复核：

| Finding | 严重度 | 状态 | 变更证据 |
|---------|--------|------|----------|
| F1: risk → style_positioning test construction gap | MEDIUM | **FIXED** | L33 risk 行改为 "Defer to row-shape contract decision before tests"；L51 禁止 risk 进入下一 gate；L65 新增 risk deferred residual |
| F2: 017641 QDII table shape | LOW | **FIXED** | L48 允许下一 gate 决定 raw extractor header keys vs test-local comparison adapter；L83 新增 stop condition：canonical keys vs raw extractor keys 不可比则停 |
| F3: manager deferral 缺代码行号引用 | LOW | **NOT FIXED** | L35 仍无行号引用；但结论正确，属文档增强建议，非正确性缺陷 |
| F4: 越界授权 | PASS | **Still PASS** | 范围进一步缩窄（risk 移除），无新增越界 |
| F5: code-generation-ready | PASS | **Still PASS** | 下一 gate 更窄（仅 equity-like holdings），stop conditions 更完善 |

无新增 blocking findings。

## Re-review Residual Risk

1. **Canonical oracle keys vs raw extractor header keys 的 stop condition 触发阈值**: L48 将 header key mapping 决策委托给下一 gate，L83 设置 stop condition。若下一 gate 在 test construction 中发现 raw extractor header keys 与 canonical oracle keys (`code`, `name`, `fair_value_cny`, `net_asset_ratio`) 差距过大，会触发 stop 并回到 row-shape decision。这是正确的渐进式设计，但 stop condition 不定义"can reliably represent"的判断标准（多少行匹配算可靠？单个 017641 失败是否阻断全部三条？）。下一 gate plan 应明确此阈值。
2. **Risk deferred residual 的 scope creep risk**: L65 新增 `Retained risk-characteristic text` 作为独立 deferred residual，其 `Required next decision` 覆盖面较广（product profile / bond/QDII risk evidence / risk disclosure summary / new output contract）。未来 risk row-shape contract gate 可能需要 cross-cutting 的 design 工作，建议提前评估与其他 contract gate 的排序依赖。
