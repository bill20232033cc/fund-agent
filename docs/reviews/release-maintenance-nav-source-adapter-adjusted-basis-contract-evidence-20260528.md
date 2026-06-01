# NAV Repository / Source Adapter Adjusted-Basis Contract Evidence

日期：2026-05-28

角色：Gateflow worker

Gate：`NAV repository/source adapter adjusted-basis contract gate`

结论：`blocked-with-contract-gap`

## 1. Preflight

命令：

```text
git branch --show-current
git status --short
```

结果：

- branch：`codex/local-reconciliation`
- tracked dirty：无
- unrelated untracked：`--help`、旧 `docs/reviews/repo-review-*`、旧 comprehensive audit、`docs/tmux-agent-memory-store.md`

该状态与 controller handoff 一致。未 stage、未 commit、未 push。

## 2. 真源复述

已读取：

- `AGENTS.md`：中文回答；文档和基金 PDF 必须通过统一 repository；fallback failure taxonomy；四层边界；禁止 `extra_payload`；不得输出无证据数值判断；债券基金 preferred_lens 要关注信用风险、久期、最大回撤。
- `docs/design.md`：当前主链路是 UI -> Service -> `fund_agent/fund` 过渡实现；`FundNavDataAdapter.load_nav_data()` 在 P1 extraction 中加载 NAV，失败时降级 unavailable；`FundDocumentRepository.load_annual_report()` 是年报读取边界。
- `docs/implementation-control.md`：当前 release maintenance；当前 gate blocked_pending_source_adapter；下一入口为 NAV repository/source adapter adjusted-basis contract gate；credit_risk 和 redemption_share_pressure 已修复，006597 仍因 drawdown_stress weak qualitative 保持 baseline blocker。
- `release-maintenance-nav-source-capability-adjusted-basis-controller-judgment-20260528.md`：public `FundNavDataAdapter` smoke 成功但只返回 raw `净值日期` / `单位净值` / `日增长率`，不能证明 adjusted/cumulative/total-return basis。
- `release-maintenance-drawdown-stress-nav-derived-contract-controller-judgment-20260528.md`：NAV-derived quantitative evidence 只是未来 candidate；当前不能实现；qualitative `控制回撤` 必须保持 weak。

最新 006597 artifacts 复述：

- `snapshot.jsonl`：`bond_risk_evidence` 记录 `contract_status=partial`；satisfied groups 为 `duration_rate_risk`、`credit_risk`、`leverage_liquidity`、`asset_allocation_holdings_mix`、`redemption_share_pressure`、`convertible_bond_equity_exposure`；weak groups 为 `drawdown_stress`。
- `score.json`：`bond_risk_evidence_missing.baseline_blocking=true` 仍存在；missing evidence groups 只剩 `drawdown_stress`；`credit_risk` 与 `redemption_share_pressure` 不再是 missing。
- `quality_gate.json`：status 为 `warn`；FQ0 strict golden answer 未配置；FQ2/FQ2F/FQ4 仍有 warnings；不得通过本 gate 改变 FQ0-FQ6 或 promotion 状态。

## 3. 年报 repository smoke

命令只使用公开 repository：

```text
uv run python - <<'PY'
import asyncio
from fund_agent.fund.documents import FundDocumentRepository

async def main():
    repo = FundDocumentRepository()
    for year in (2024, 2025):
        report = await repo.load_annual_report("006597", year)
        print(year, report.metadata.source.to_dict())
        section = report.get_section_text("§3") or ""
        # 只打印 §3.1 / §3.2 / §3.3 片段，不读 PDF/cache internals。

asyncio.run(main())
PY
```

结果摘要：

### 2024

- source：`eid`
- source_url：`http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1253099`
- fund_code：`006597`
- fund_id：`5755`
- report_year：`2024`
- report_code：`FB010010`
- report_desp：`年度报告`
- report_name：`国泰利享中短债债券型证券投资基金2024年年度报告`
- upload_info_id：`1253099`
- upload_info_detail_id：`1290497`
- fallback_used：`False`

2024 §3 evidence：

- §3.1 按 A/C/E/F 分别披露主要会计数据和财务指标。
- A 类 2024 期末基金份额净值 `1.2003`，本期基金份额净值增长率 `2.57%`，累计净值增长率 `20.03%`。
- C 类 2024 期末基金份额净值 `1.1859`，本期基金份额净值增长率 `2.37%`，累计净值增长率 `18.59%`。
- E 类 2024 期末基金份额净值 `1.1819`，本期基金份额净值增长率 `2.19%`，累计净值增长率 `5.96%`。
- F 类 2024 期末基金份额净值 `1.2003`，本期基金份额净值增长率 `0.60%`，累计净值增长率 `0.60%`。
- §3.2 按 A/C/E/F 分别披露份额净值增长率、份额净值增长率标准差、业绩比较基准收益率及标准差。
- §3.2 注释：F 类自 `2024-10-08` 增加，`2024-10-15` 开始计算 F 类基金份额净值和基金份额累计净值。
- §3.3：A/C 过去三年未分配；E 类 2023 每 10 份分红 `0.080`，现金 `7,273,431.12`，再投资 `1,871,517.43`，合计 `9,144,948.55`；2024 / 2022 为 `-`；F 自新增以来未分配。

### 2025

- source：`eid`
- source_url：`http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1450363`
- fund_code：`006597`
- fund_id：`5755`
- report_year：`2025`
- report_code：`FB010010`
- report_desp：`年度报告`
- report_name：`国泰利享中短债债券型证券投资基金2025年年度报告`
- upload_info_id：`1450363`
- upload_info_detail_id：`1497253`
- fallback_used：`False`

2025 §3 evidence：

- §3.1 A 类 2025 期末基金份额净值 `1.2192`，本期基金份额净值增长率 `1.57%`，累计净值增长率 `21.92%`。
- §3.1 C 类 2025 期末基金份额净值 `1.2022`，本期基金份额净值增长率 `1.37%`，累计净值增长率 `20.22%`。
- §3.1 E 类 2025 期末基金份额净值 `1.1967`，本期基金份额净值增长率 `1.25%`，累计净值增长率 `7.29%`。
- §3.1 F 类 2025 期末基金份额净值 `1.2191`，本期基金份额净值增长率 `1.57%`，累计净值增长率 `2.17%`。
- §3.2 按 A/C/E/F 分别披露过去三个月、六个月、一年等区间的份额净值增长率和标准差；F 类有 `自新增F类份额起至今` 行。
- §3.2 注释：F 类自 `2024-10-08` 增加，`2024-10-15` 开始计算 F 类基金份额净值和基金份额累计净值。
- §3.3：A/C 过去三年未分配；E 类 2023 每 10 份基金份额分红 `0.080`，现金形式 `7,273,431.12`，再投资形式 `1,871,517.43`，年度利润分配合计 `9,144,948.55`；2024 / 2025 为 `-`；F 自新增份额以来未分配。

重要差异：

- 用户 handoff 中写 2025 §3.1 E 期末基金份额净值为 `1.1744`。本次通过 `FundDocumentRepository` 读取 2025 年报 §3.1 验证到 E 类期末基金份额净值为 `1.1967`。这需要 controller review：`1.1744` 可能来自非年末日期、其他公告或旧来源，但不能作为本 artifact 的 repository 年报事实。

## 4. Current FundNavDataAdapter Public Contract Smoke

命令：

```text
uv run python - <<'PY'
import asyncio, json
from fund_agent.fund.data.nav_data import FundNavDataAdapter

async def main():
    result = await FundNavDataAdapter().load_nav_data("006597")
    records = result.records
    print(json.dumps({
        "fund_code": result.fund_code,
        "source": result.source,
        "cached": result.cached,
        "unavailable": result.unavailable,
        "unavailable_reason": result.unavailable_reason,
        "record_count": len(records),
        "first": records[0] if records else None,
        "last": records[-1] if records else None,
        "keys": list(records[0].keys()) if records else [],
    }, ensure_ascii=False, indent=2))

asyncio.run(main())
PY
```

结果：

```json
{
  "fund_code": "006597",
  "source": "nav_cache",
  "cached": true,
  "unavailable": false,
  "unavailable_reason": null,
  "record_count": 1809,
  "first": {
    "净值日期": "2018-12-03",
    "单位净值": 1.0,
    "日增长率": 0.0
  },
  "last": {
    "净值日期": "2026-05-27",
    "单位净值": 1.2275,
    "日增长率": 0.01
  },
  "keys": [
    "净值日期",
    "单位净值",
    "日增长率"
  ]
}
```

Public contract gap：

- 无 `share_class`
- 无 `fund_code_mapping`
- 无 `nav_type`
- 无 `adjustment_basis`
- 无 `dividend_adjustment_status`
- 无 `retrieved_at`
- 无 `source_url` / `source_id`
- 无 `source_returned_fund_code`
- 无 `identity_status`
- 无 `failure_category`
- 无 public cache updated_at / origin source metadata

当前 adapter 只能证明 raw unit NAV rows reachable，不能证明 adjusted / cumulative / total-return basis。

## 5. Code Boundary Evidence

读取代码但未修改：

- `fund_agent/fund/data/nav_data.py`
  - `_fetch_nav_with_akshare()` 调用 `ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")`。
  - `NavDataResult` 只包含 `fund_code`、`records`、`source`、`cached`、`unavailable`、`unavailable_reason`。
  - cache hit 返回 `source="nav_cache"`，records 为 cached payload；origin source / updated_at 不通过 public result 暴露。
- `fund_agent/fund/documents/repository.py`
  - `FundDocumentRepository.load_annual_report()` 是年报公开读取入口。
  - 本次年报证据均通过该入口获取。
- `fund_agent/fund/documents/models.py`
  - 年报 source metadata 已有 `source_url`、`fund_code`、`report_year`、`report_name`、`upload_info_id` 等字段，可作为 NAV repository metadata 设计参考。

## 6. Regulatory / Industry Source Evidence

已核验但未全文复制：

- 中国证监会《公开募集证券投资基金信息披露管理办法》要求基金信息披露义务人披露基金信息，公开披露信息包括基金资产净值、基金份额净值；托管人需复核基金管理人编制的基金资产净值、基金份额净值等公开披露信息。
- 中国证监会《关于实施〈公开募集证券投资基金信息披露管理办法〉有关问题的规定》提到基金电子披露网站和 XBRL 模板支持。
- 中基协 2026 年公告发布 5 项公开募集证券投资基金信息披露 XBRL 模板，包含净值公告、年度报告和中期报告模板。
- 官方 / 行业 disclosure sources 足以支持本 gate 的 conservative contract：公开披露中存在单位净值、累计净值增长率、净值表现、利润分配等对象，但不足以证明当前 `FundNavDataAdapter` 已取得 total-return 或复权 path。

引用链接：

- `https://www.csrc.gov.cn/csrc/c101877/c1029542/content.shtml`
- `https://www.gov.cn/gongbao/content/2019/content_5462516.htm`
- `https://www.csrc.gov.cn/csrc/c101877/c1029541/content.shtml`
- `https://www.amac.org.cn/xwfb/xhyw/202603/t20260313_27409.html`

## 7. Contract Gap Judgment

当前 `FundNavDataAdapter` 不满足 adjusted-basis NAV source adapter contract。

理由：

1. 它只公开 raw `单位净值走势` rows，字段为 `净值日期`、`单位净值`、`日增长率`。
2. 它没有 share-class identity。006597 产品存在 A/C/E/F，且主代码优先对应 A 类；不能混成产品级单序列。
3. 它没有 adjustment basis。不能判断序列是 raw unit NAV、累计净值、分红调整净值还是 total-return。
4. 它没有 dividend adjustment status。E 类 2023 有分红，raw unit NAV 跨分红期间可能把除息误判为 drawdown。
5. 它没有 source-returned identity / source_url / retrieved_at / failure taxonomy，不满足 calculation-ready provenance。
6. 年报 §3.2 区间净值增长率不能替代 daily / periodic NAV path 计算 max drawdown。

因此：

- `drawdown_stress` 继续 weak qualitative。
- `bond_risk_evidence_missing.baseline_blocking=true` 继续有效。
- 不允许用当前 raw NAV 解除 blocker。

## 8. 下一最小 Implementation Gate

建议 gate 名称：

`NAV repository/source adapter typed contract implementation gate`

最小目标：

- 在 `fund_agent/fund/data/` 建立 typed NAV series result / record / metadata。
- 当前 Akshare `单位净值走势` 显式标记为 `nav_type=unit_nav`、`adjustment_basis=raw_unit_nav`，并默认不满足 drawdown strong evidence。
- public result 暴露 cache-hit origin source / cache updated_at metadata，不允许消费者读 sqlite internals。
- 建立 share-class mapping contract；006597 默认 A 类，C/E/F 必须显式分离。
- 引入 failure taxonomy：`not_found` / `unavailable` 可 retry/fallback；`schema_drift` / `identity_mismatch` / `integrity_error` / `adjustment_basis_unknown` fail-closed。

明确非目标：

- 不改 score / quality gate / golden。
- 不改 `bond_risk_evidence` satisfaction。
- 不计算 max drawdown。
- 不做 blocker 解除。

## 9. Validation Performed

已执行：

- preflight branch / status
- 读取真源文档和 latest artifacts
- `FundDocumentRepository` 读取 006597 2024/2025 年报 §3
- `FundNavDataAdapter.load_nav_data("006597")` public smoke
- 读取 adapter/repository code boundary

未执行：

- `ruff`
- full `pytest`

原因：本 gate 只新增 docs/reviews artifacts，不修改生产代码、测试、schema、score、quality gate 或 fixture。
