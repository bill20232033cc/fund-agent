# P19-S5 All-A PE/PB Source Feasibility Artifact — 2026-05-23

## Verdict

**ACCEPT_IMPLEMENTATION_PLAN**

全 A PE+PB 历史数据源契约已验证通过，满足 `docs/design.md` v2.2 §11 的全部设计兼容性要求。下一 gate 是 all-A market thermometer implementation plan/review，不得直接进入编码。

---

## 1. 运行环境

| 项目 | 值 |
|------|-----|
| Python | 3.11.15 (Clang 21.0.0) |
| akshare | 1.18.60 |
| 虚拟环境 | `.venv` |
| 平台 | macOS ARM64 (Darwin 25.5.0) |
| 网络 | 公网直连；Legulegu 偶发 SSL EOF 瞬断（重试 ≤3 次恢复） |

关键命令：

```text
.venv/bin/python -c "import akshare as ak; print(ak.__version__)"
.venv/bin/python -c "ak.stock_a_all_pb()"
.venv/bin/python -c "ak.stock_a_ttm_lyr()"
```

---

## 2. Probe Matrix

### 2.1 主探针（Mandatory Probes）

#### akshare.stock_a_ttm_lyr

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_a_ttm_lyr` |
| function_or_endpoint | `akshare.stock_feature.stock_ttm_lyr.stock_a_ttm_lyr()` |
| source_module | `.venv/lib/python3.11/site-packages/akshare/stock_feature/stock_ttm_lyr.py` |
| page_url | `https://www.legulegu.com/stockdata/a-ttm-lyr` |
| api_url | `https://legulegu.com/api/stock-data/market-ttm-lyr?marketId=5` |
| identity_scope | **all-A** — docstring: "全部 A 股-等权重市盈率、中位数市盈率"；Legulegu 页面 meta: "全部A股等权(全A等权)市盈率中位数、平均数走势图" |
| universe_definition | 全部 A 股（Legulegu 定义），具体纳入/排除规则未在页面中逐条列出；marketId=5 为 Legulegu 内部全 A 市场标识 |
| identity_reconciliation | 与 `stock_a_all_pb` 同属 Legulegu "全部A股" 产品族；PE 页面标题含 "全部A股等权(全A等权)市盈率"，PB 页面标题含 "全部A股-等权重市净率、中位数市净率"；marketId 不同（5 vs ALL）是 API 技术差异，非 universe 差异 |
| license_or_access | **public** — Legulegu 公开网页；token 从公开页面 JS 中提取；无登录/付费/API Key 要求；akshare MIT 许可证 |
| pe_fields | `middlePETTM` (中位数滚动市盈率), `averagePETTM` (等权平均滚动市盈率), `middlePELYR` (中位数静态市盈率), `averagePELYR` (等权平均静态市盈率) |
| pb_fields | **none** — 此接口仅返回 PE 数据 |
| weighting_method | equal-weight — 全部 A 股每家等权重，取中位数/平均数 |
| statistic_type | median + average — `middlePExxx` 为中位数，`averagePExxx` 为等权平均数 |
| pe_basis | **TTM + LYR** — `middlePETTM`/`averagePETTM` 为滚动市盈率（TTM），`middlePELYR`/`averagePELYR` 为静态市盈率（LYR/上年度） |
| pb_basis | none — 不适用 |
| rows | **5186** (API 原始返回)；5182 唯一日期 |
| date_start | **2005-01-05** |
| date_end | **2026-05-22** |
| latest_date | 2026-05-22 (新鲜度 1 天) |
| common_dates | 与 `stock_a_all_pb` 公共日期 **4828** 天 (2005-01-05 ~ 2026-05-22) |
| missing_rule | PE 值列 (middlePETTM/averagePETTM/middlePELYR/averagePELYR): **0 NaN, 0 non-positive**；close 列：60 行 = 0（仅早期日期），不影响 PE 值；quantile 列：前 5185 行为 NaN（历史分位数需足够历史数据），仅最新行有值 |
| failure_class | **none** — 探针通过 |
| decision | **accepted** — 作为 all-A PE 历史数据源 |

#### akshare.stock_a_all_pb

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_a_all_pb` |
| function_or_endpoint | `akshare.stock_feature.stock_all_pb.stock_a_all_pb()` |
| source_module | `.venv/lib/python3.11/site-packages/akshare/stock_feature/stock_all_pb.py` |
| page_url | `https://www.legulegu.com/stockdata/all-pb` |
| api_url | `https://legulegu.com/api/stock-data/market-index-pb?marketId=ALL` |
| identity_scope | **all-A** — docstring: "全部A股-等权重市净率、中位数市净率" |
| universe_definition | 全部 A 股（Legulegu 定义）；marketId=ALL；源码中删除了 `weightingAveragePB` 列（市值加权 PB），仅保留等权中位数和等权平均数 |
| identity_reconciliation | 与 `stock_a_ttm_lyr` 同属 Legulegu "全部A股" 产品族；两者公共日期 4828 天，覆盖相同时间窗口 |
| license_or_access | **public** — 同上 |
| pe_fields | **none** — 此接口仅返回 PB 数据 |
| pb_fields | `middlePB` (中位数市净率), `equalWeightAveragePB` (等权平均市净率) |
| weighting_method | equal-weight — 全部 A 股每家等权重，取中位数/平均数 |
| statistic_type | median + equalWeightAverage — `middlePB` 为中位数，`equalWeightAveragePB` 为等权平均数 |
| pe_basis | none — 不适用 |
| pb_basis | **median + equalWeightAverage** — `middlePB` 为中位数市净率 |
| rows | **5184** (5184 唯一日期) |
| date_start | **2005-01-04** |
| date_end | **2026-05-22** |
| latest_date | 2026-05-22 (新鲜度 1 天) |
| common_dates | 与 `stock_a_ttm_lyr` 公共日期 **4828** 天 (2005-01-05 ~ 2026-05-22) |
| missing_rule | PB 值列 (middlePB/equalWeightAveragePB): **0 NaN, 0 non-positive**；close 列：0 NaN；quantile 列前 5183 行为 NaN，仅最新行有值 |
| failure_class | **none** — 探针通过 |
| decision | **accepted** — 作为 all-A PB 历史数据源 |

#### akshare.stock_a_lg_indicator

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_a_lg_indicator` |
| function_or_endpoint | 无 — 在 akshare 1.18.60 中不存在 |
| identity_scope | N/A |
| universe_definition | N/A |
| identity_reconciliation | N/A |
| license_or_access | N/A |
| pe_fields | N/A |
| pb_fields | N/A |
| weighting_method | N/A |
| statistic_type | N/A |
| pe_basis | N/A |
| pb_basis | N/A |
| rows | N/A |
| date_start | N/A |
| date_end | N/A |
| common_dates | N/A |
| missing_rule | N/A |
| failure_class | **missing_interface** — `dir(akshare)` 中无 `lg_indicator` 相关函数；`rg` 搜索 akshare 源码无匹配 |
| decision | **rejected** — 不可用 |

---

### 2.2 板块/市场 PE/PB 探针（Negative Controls）

#### akshare.stock_market_pe_lg

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_market_pe_lg` |
| function_or_endpoint | `akshare.stock_market_pe_lg(symbol=...)` |
| identity_scope | **board-level** — 上证/深证/创业板/科创板；无 "全A" symbol |
| pe_fields | `平均市盈率` — 仅单一平均 PE 字段 |
| pb_fields | **none** — 无 PB |
| decision | **rejected** — board-level, PE-only, 单字段（无中位数），不满足 all-A PE+PB 需求 |
| failure_class | **not_all_a** + **no_pb** |

注：上证返回 330 行 (1999-2026)；深证 SSL 错误；创业板/科创版连接中断；`全A` symbol 返回 KeyError。

#### akshare.stock_market_pb_lg

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_market_pb_lg` |
| function_or_endpoint | `akshare.stock_market_pb_lg(symbol=...)` |
| identity_scope | **board-level** — 上证/深证/创业板/科创板；无 "全A" symbol |
| pe_fields | **none** |
| pb_fields | `市净率`, `等权市净率`, `市净率中位数` |
| decision | **rejected** — board-level, PB-only，不满足 all-A PE+PB 需求 |
| failure_class | **not_all_a** + **no_pe** |

注：四板均返回 5191 行 (2005-2026)，数据完整；但 universe 非 all-A，不可冒充。

#### akshare.stock_index_pe_lg / stock_index_pb_lg

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_index_pe_lg` / `akshare.stock_index_pb_lg` |
| identity_scope | **index-level** — 沪深300/中证500 等指数成分股；无 "万得全A" symbol |
| decision | **rejected** — index-level，不满足 all-A 需求 |
| failure_class | **not_all_a** |

注：沪深300 PE+PB 均可用 (5130 行, 2005-2026)；中证500 PE 可用，PB SSL 瞬断。此接口已用于 P19-S1/S2 指数温度计，不可冒充全 A 温度计。

---

### 2.3 Direct Legulegu API 探针

| Endpoint | 结果 | failure_class |
|----------|------|--------------|
| `GET /api/stock-data/market-ttm-lyr?marketId=5` | 200, body=0 (无 token 时返回空) | **auth** (需 akshare token/cookie 流程) |
| `GET /api/stock-data/market-index-pe?marketId=ALL` | **404** | **404** |
| `GET /api/stock-data/market-index-ttm-pe?marketId=ALL` | **404** | **404** |
| `GET /api/stock-data/market-index-lyr-pe?marketId=ALL` | **404** | **404** |
| `GET /api/stock-data/market-pe?marketId=ALL` | 200, body=0 (空响应) | **not_all_a** (非 all-A 端点) |

使用 akshare token + cookie 复现完整请求后，`market-ttm-lyr?marketId=5` 返回 200 + 619KB JSON (5186 行)，即 `stock_a_ttm_lyr()` 底层 API。其他端点均不可作为 all-A 路径使用。

---

### 2.4 Eastmoney / CSIndex / 交易所探针

#### akshare.stock_zh_a_spot_em

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_zh_a_spot_em` |
| function_or_endpoint | `akshare.stock_zh_a_spot_em()` |
| identity_scope | stock-level, current-only |
| failure_class | **network_unavailable** — 本地返回 `ConnectionError: ('Connection aborted.', RemoteDisconnected)`；此前 P19 data-source review 也报告 `ProxyError`。即使可用，也是逐股当前快照，无法构成历史序列。 |
| decision | **rejected** |

#### akshare.stock_zh_index_value_csindex

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_zh_index_value_csindex` |
| function_or_endpoint | `akshare.stock_zh_index_value_csindex(symbol='000300')` |
| identity_scope | index-level |
| pe_fields | `市盈率1`, `市盈率2` — 仅 2 个 PE 字段，语义不明（未标注 TTM/LYR/静态/滚动） |
| pb_fields | **none** — 无 PB 字段 |
| rows | 20 (仅近期) |
| failure_class | **not_all_a** + **no_pb** + **current_only** (仅 20 行) |
| decision | **rejected** |

#### akshare.stock_zh_index_hist_csindex

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_zh_index_hist_csindex` |
| identity_scope | index-level, price-only |
| failure_class | **not_all_a** — price-only，无 PE/PB |
| decision | **rejected** |

#### akshare.stock_a_gxl_lg

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_a_gxl_lg` |
| identity_scope | all-A, dividend-yield-only |
| failure_class | **no_pe** + **no_pb** — 仅 `股息率` 一个字段 |
| decision | **rejected** |

#### akshare.stock_a_congestion_lg

| 字段 | 值 |
|------|-----|
| candidate_id | `akshare.stock_a_congestion_lg` |
| failure_class | **network_unavailable** — SSL EOF 瞬断；非 PE/PB 端点 |
| decision | **rejected** |

---

### 2.5 Akshare 包搜索发现的候选函数全量分类

通过 `dir(akshare)` 和源码搜索 (`rg "市盈率|市净率|估值|market.*pe|all.*pb" .venv/.../akshare`) 发现的相关函数：

| 函数 | 分类 | 决策 |
|------|------|------|
| `stock_a_all_pb` | all-A PB history | **accepted** |
| `stock_a_ttm_lyr` | all-A PE history | **accepted** |
| `stock_a_lg_indicator` | missing_interface | rejected |
| `stock_market_pe_lg` | board-level PE | rejected (not_all_a + no_pb) |
| `stock_market_pb_lg` | board-level PB | rejected (not_all_a + no_pe) |
| `stock_index_pe_lg` | index-level PE | rejected (not_all_a) |
| `stock_index_pb_lg` | index-level PB | rejected (not_all_a) |
| `stock_zh_a_spot_em` | stock-level current spot | rejected (network_unavailable + current_only) |
| `stock_zh_index_value_csindex` | index-level PE-only recent | rejected (not_all_a + no_pb + current_only) |
| `stock_zh_index_hist_csindex` | index price-only | rejected (no pe/pb) |
| `stock_a_gxl_lg` | all-A dividend yield | rejected (no pe/pb) |
| `stock_a_congestion_lg` | congestion indicator | rejected (network_unavailable) |
| `stock_a_below_net_asset_statistics` | 破净统计 | rejected (not PE/PB history) |
| `stock_a_high_low_statistics` | 高低统计 | rejected (not PE/PB history) |
| `macro_china_stock_market_cap` | 市值统计 | rejected (not PE/PB) |

---

## 3. stock_a_ttm_lyr 独立复验

### 3.1 字段名与样例

```
columns: ['date', 'middlePETTM', 'averagePETTM', 'middlePELYR', 'averagePELYR',
          'close', 'quantileInAllHistoryMiddlePeTtm', 'quantileInRecent10YearsMiddlePeTtm',
          'quantileInAllHistoryAveragePeTtm', 'quantileInRecent10YearsAveragePeTtm',
          'quantileInAllHistoryMiddlePeLyr', 'quantileInRecent10YearsMiddlePeLyr',
          'quantileInAllHistoryAveragePeLyr', 'quantileInRecent10YearsAveragePeLyr']
```

首行: `date=2005-01-05, middlePETTM=28.79, averagePETTM=43.85, middlePELYR=31.43, averagePELYR=50.09, close=0.0`

末行: `date=2026-05-22, middlePETTM=44.28, averagePETTM=66.78, middlePELYR=45.06, averagePELYR=68.60, close=4845.1`

### 3.2 行数与日期范围

- 原始行数: 5186
- 唯一日期: 5182
- 日期范围: 2005-01-05 ~ 2026-05-22
- PE 值列 NaN: 0
- PE 值列 ≤0: 0
- middlePETTM 统计: min=17.44, max=90.66, mean=39.46

### 3.3 与 stock_a_all_pb 的 common_dates

- PB 唯一日期: 5184
- PE 唯一日期: 5182
- **公共日期: 4828** (2005-01-05 ~ 2026-05-22)
- PB-only 日期: 356 (含 2005-01-04 等 PB 比 PE 多 1 天的日期)
- PE-only 日期: 354

### 3.4 middle/average PE 字段语义与设计兼容性

| 设计要求 (§11.2) | 对应字段 | 兼容性 |
|------------------|---------|--------|
| PE 等权中位数 | `middlePETTM` (中位数滚动市盈率) | ✅ TTM 中位数，同 P19-S1 `PE_COLUMN="滚动市盈率中位数"` |
| PB 等权中位数 | `middlePB` (中位数市净率) | ✅ 中位数，同 P19-S1 `PB_COLUMN="市净率中位数"` |
| 统计口径：等权 | 中位数天然等权（每家对排序贡献相同） | ✅ |
| PE basis: TTM | `middlePETTM` 为滚动市盈率 | ✅ 与 P19-S1 TTM 一致 |
| percentile_rank 可行 | 4828 公共日期 > MIN_HISTORY_POINTS | ✅ 覆盖两轮牛熊 |

若未来需要 LYR (静态市盈率) 也可用 `middlePELYR`，但需单独设计决策。当前推荐使用 `middlePETTM` 与已有指数温度计 PE 口径一致。

---

## 4. Failure Class 汇总

| Failure Class | 命中候选 | 说明 |
|---------------|---------|------|
| `missing_interface` | `stock_a_lg_indicator` | akshare 1.18.60 中不存在 |
| `404` | `legulegu.market-index-pe.ALL`, `legulegu.market-index-ttm-pe.ALL`, `legulegu.market-index-lyr-pe.ALL` | Legulegu API 直接访问 404 |
| `auth` | `legulegu.market-ttm-lyr` (直接) | 无 token 返回空；通过 akshare 流程可正常访问 |
| `not_all_a` | `stock_market_pe_lg`, `stock_market_pb_lg`, `stock_index_pe_lg`, `stock_index_pb_lg`, `stock_zh_index_value_csindex`, `stock_zh_index_hist_csindex` | 板块/指数级，非全 A |
| `no_pb` | `stock_market_pe_lg`, `stock_zh_index_value_csindex` | PE 可用但 PB 缺失 |
| `no_pe` | `stock_market_pb_lg`, `stock_a_gxl_lg` | PB 可用但 PE 缺失 |
| `current_only` | `stock_zh_a_spot_em` (理论), `stock_zh_index_value_csindex` (20 行) | 无法构成历史序列 |
| `network_unavailable` | `stock_zh_a_spot_em`, `stock_a_congestion_lg`, 部分 `stock_market_pe_lg` symbol | 本地网络/代理导致不可达；偶发 SSL EOF |

---

## 5. 源契约综合评估

### 5.1 Acceptance Rule 逐条对照

| 验收条件 (from plan) | 状态 | 证据 |
|---------------------|------|------|
| exact all-A identity | ✅ | 两个函数 docstring 均为 "全部A股"；Legulegu 页面 meta 确认 "全部A股等权(全A等权)" |
| PE history 存在 | ✅ | `stock_a_ttm_lyr()`: 5182 天, 2005-2026 |
| PB history 存在 | ✅ | `stock_a_all_pb()`: 5184 天, 2005-2026 |
| 同一来源族或可合并 | ✅ | 同属 Legulegu via akshare；public 日期 4828 天可合并 |
| PE/PB 字段语义清晰 | ✅ | `middlePETTM`=中位数滚动市盈率, `middlePB`=中位数市净率 |
| 统计口径 = equal-weight median | ✅ | 中位数天然等权；Legulegu 页面标题含 "等权" |
| PE basis 匹配设计 | ✅ | TTM (middlePETTM)，与 P19-S1 `PE_COLUMN="滚动市盈率中位数"` 一致 |
| PB basis 匹配设计 | ✅ | median (middlePB)，与 P19-S1 `PB_COLUMN="市净率中位数"` 一致 |
| 公共日期充足 | ✅ | 4828 > MIN_HISTORY_POINTS，覆盖两轮牛熊 |
| 最新日期新鲜 | ✅ | 2026-05-22 (昨日) |
| public 访问 | ✅ | Legulegu 公开网页 token，无付费/登录 |
| missing/null/non-positive 规则 | ✅ | 0 NaN, 0 non-positive；quantile 列 NaN 为预期行为 |
| source-shaped fixtures 可脱离网络 | ✅ | 可从 DataFrame 导出 JSON fixtures |

### 5.2 设计兼容性确认

`docs/design.md` v2.2 §11.2 核心算法与 all-A source contract 对照：

```text
设计: PE 等权中位数 = median(样本内有效 PE)  → middlePETTM ✅
设计: PB 等权中位数 = median(样本内有效 PB)  → middlePB ✅
设计: PE 分位数 = percentile_rank(当日, 历史序列) → 4828 公共日期 ✅
设计: PB 分位数 = percentile_rank(当日, 历史序列) → 4828 公共日期 ✅
设计: 综合温度 = (PE分位数 + PB分位数) / 2 → 可计算 ✅
设计: 考察周期 = 两轮完整牛熊 → 2005-2026, 21 年 ✅
设计: PE basis = TTM → middlePETTM ✅
设计: 加权方式 = 等权 → 中位数天然等权 ✅
```

### 5.3 风险评估

| 风险 | 等级 | 缓解 |
|------|------|------|
| Legulegu SSL 瞬断（观测到 2 次/10 次调用） | 低 | `ThermometerSourceError` + 重试机制；cache 命中时无网络依赖 |
| Legulegu API token 机制未来变更 | 低 | akshare 版本锁定 (`>=1.18.60`)；CI 中可加 probe-only 冒烟测试 |
| marketId=5 vs marketId=ALL 不一致 | 低 | 两者均声称全部A股，页面 title 互证；公共日期高度重合 (93%) |
| close=0 (60 行早期 PE) | 无影响 | PE/PB 值列不受影响；仅 close 列有 0 值 |
| Legulegu 未公开精确纳入规则 | 中 | 设计目标为 "方向一致，数值合理偏差" (§11.1)，不追求精确复现 |

---

## 6. 排除项目

以下明确排除，不作为 all-A 温度计数据源：

- PB-only 输出 (如仅用 `stock_a_all_pb`)
- PE-only 输出 (如仅用 `stock_a_ttm_lyr`)
- 板块级替代 (如上证/深证/创业板/科创板)
- 指数级替代 (如沪深300/中证500 冒充全A)
- 逐股重建 PE/PB (未授权，存储/成本/许可证未评估)
- 有知有行页面抓取作为生产真源 (§11.9)
- Eastmoney 实时行情 (`stock_zh_a_spot_em`，不可用且 current-only)
- CSIndex 官方估值表 (PE-only, 仅近期, 无 PB)
- 中证/国证交易所下载文件 (price-only)

---

## 7. 网络/访问错误原文摘要

Legulegu 偶发 SSL EOF 瞬断，模式如下：

```text
SSLEOFError: [SSL: UNEXPECTED_EOF_WHILE_READING] EOF occurred in violation of protocol (_ssl.c:1016)
```

观测频率：约 2/10 次调用，重试 1-3 次后均恢复。发生在 `stock_a_all_pb()`、`stock_a_ttm_lyr()`、`stock_market_pb_lg()` 等所有 Legulegu 端点。非永久性阻断，属于 transient network 类别。

Eastmoney spot (`stock_zh_a_spot_em`) 本地持续失败：

```text
ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
```

此前 P19 data-source review 报告 `ProxyError`，属本地网络环境限制。

---

## 8. 下一 Gate

当前 gate **P19-S5 source feasibility execution 完成**。下一 gate 为 **P19-S5 all-A market thermometer implementation plan/review**。

禁止：
- 直接编码实现
- 修改生产代码、tests、`docs/design.md`、`docs/implementation-control.md`
- commit、push、开 PR
- 改变 `fund-analysis analyze` 行为
- 自动映射 `valuation_state`

---

## 9. 验证

```text
$ git diff --check
passed
```

未修改除本 artifact 外的任何文件。
