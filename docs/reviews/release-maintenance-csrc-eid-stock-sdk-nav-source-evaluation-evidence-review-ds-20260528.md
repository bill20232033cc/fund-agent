# CSRC EID and stock-sdk NAV Source Evaluation Evidence — Evidence Review (DS)

日期：2026-05-28

角色：AgentDS evidence review worker，非 controller，非 implementation worker。

Work unit：`CSRC EID and stock-sdk accumulated NAV source evaluation gate`

Reviewed artifact：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-evidence-20260528.md`

Accepted plan：`docs/reviews/release-maintenance-csrc-eid-stock-sdk-nav-source-evaluation-plan-20260528.md`

## Verdict

**Accepted** — 5 non-blocking findings. Evidence supports both recommended decisions. CSRC EID accepted-primary-candidate 和 stock-sdk evidence-only 判断均有直接证据支撑。

## Preflight

已读取全部必读真源：
- `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`
- NAV adjusted-basis source identity controller judgment + evidence（前 gate）
- `fund_agent/fund/data/nav_models.py`、`nav_repository.py`、`nav_data.py`
- Accepted plan 及 DS/GLM plan re-reviews

Scope check：本 review 只产出本 artifact；不修改 evidence、plan、code、tests、score、snapshot、quality gate、golden、Host/Agent/dayu。

## Plan Compliance Check

逐条对照 plan 的 E1-E4 步骤：

### E1 — CSRC EID Smoke

| Plan Step | Evidence Status | Notes |
|---|---|---|
| E1-0 公开搜索定位 | ✅ 执行 | POST validate_fund.do，name + A/C/E 代码均映射到 5755，F 搜索缺失已记录 |
| E1-1 HTTP/XHR endpoint 发现 | ✅ 执行 | 用标准库 urllib GET/POST，记录 method/URL/params/response |
| E1-2 内部分 ID 与份额身份映射 | ✅ 执行 | 5755 详情页列出全部四个份额类别及 classification code |
| E1-2 产品级 vs 份额级粒度检查 | ✅ 执行 | 确认 classification 参数区分份额级 rows |
| E1-3 NAV 表字段解析 | ✅ 执行 | 估值日期、单位净值、累计净值、基金资产净值、备注 |
| E1-4 分页 / full-history 验证 | ✅ 执行 | 记录 total pages、total rows、per-class 首尾日期 |
| E1-5 字段语义验证 | ✅ 执行 | 通过 E 类分红 cross-check 证明 additive accumulated_nav |
| E1-6 失败分类 | ✅ 执行 | 6 类全覆盖，含 A/C blank rows 和 F search gap |

### E2 — stock-sdk Smoke

| Plan Step | Evidence Status | Notes |
|---|---|---|
| E2-1 package/license/docs 定位 | ✅ 执行 | npm view 全量 metadata，ISC license，Node >=18，zero-dependency |
| E2-2 getFundNavHistory smoke | ✅ 执行 | 四个代码均返回，含单位/累计净值字段 |
| E2-3 API surface 分类 | ✅ 执行 | d.ts 字段映射；API 存在且返回 accum，但 date 字段存在 bug |
| E2-4 underlying provider 反查 | ✅ 执行 | d.ts + bundled source 确认 Eastmoney pingzhongdata endpoint |
| E2-5 getFundDividendList smoke | ✅ 执行 | E 类 014217 2023 分红匹配年报 §3.3，六类失败分类覆盖 |
| E2-6 错误与异常模型 | ✅ 执行 | 记录了 integrity_error（date shift）、missing_date_range（F pre-inception） |
| E2-7 dependency model 评估 | ✅ 执行 | 四级分类，最终推荐 evidence-only |

### E3 — Cross-Source Reconciliation

| Plan Step | Evidence Status | Notes |
|---|---|---|
| Execution dependency | ✅ 执行 | 来源可用性表明确 blocked/rejected 跳过 |
| §2 / §3.3 via FundDocumentRepository | ✅ 执行 | §2 份额映射、§3.3 E 分红已提取 |
| Identity reconciliation | ✅ 执行 | 四个代码 per-source identity 已记录 |
| E-class distribution cross-check | ✅ 执行 | CSRC + stock-sdk + 年报三源一致 |
| Numeric reconciliation | ✅ 执行 | CSRC vs prior Eastmoney/Akshare 行数和值对齐 |
| Basis decision rules | ✅ 执行 | accumulated_nav only，dividend/TR 未证明 |

### E4 — Decision / Judgment

| Plan Requirement | Evidence Status | Notes |
|---|---|---|
| CSRC EID decision | ✅ | accepted-primary-candidate |
| stock-sdk decision | ✅ | evidence-only |
| Per-code matrix | ✅ | 四个代码 × 两个 source，metadata 字段完整 |
| Provider lineage | ✅ | 两个 source 的 URL/provider/retrieved_at |
| Residuals | ✅ | adapter caveats、date bug disposition、no drawdown decision |

## Per-Review-Focus Assessment

### 1. CSRC EID accepted-primary-candidate 的 evidence basis

**Pass.** 证据链完整：

- 公开搜索（E1-0）：POST `/fund/disclose/validate_fund.do` 验证名称 `国泰利享中短债债券` → fundId `5755`，A/C/E 代码各自搜也返回 `5755`
- 身份映射（E1-2）：详情页 `cFundCode=5755` 同时列出四个份额类别的分类链接，classification codes `2030-1010`/`1020`/`1040`/`1050` 区分 A/C/E/F
- 份额级粒度（E1-2）：每个 classification 页独立返回对应份额的 rows，包含返回的 share-class code 和 name
- 机器可读（E1-1/3）：标准 HTTP GET HTML，字段为 `估值日期`、`单位净值`、`累计净值`
- 分页（E1-4）：stable `limit=20&start=<offset>` 分页，A/C 1809 rows，E 994 rows，F 398 rows
- 分红交叉验证（E1 distribution）：2023-01-11 accumulated_nav − unit_nav 从 0.0000 变为 0.0080，与年报 §3.3 每 10 份 0.080 一致

**Primary candidate 资格成立**：CSRC EID 是官方来源、可机器读取、份额级分离、有可复现分页、累计净值语义经分红事件证明。

### 2. CSRC caveats 的 fail-closed 分类

**Pass.** 两条 caveat 均有明确分类：

- **F direct search gap**（line 124）：分类为 "search-index limitation, not a detail-page identity mismatch"。正确——详情页有 F classification link，只是公开搜索不支持通过 F 代码或名称直接定位。
- **A/C earliest blank accumulated rows**（line 177–182）：明确指出 2018-12-07 和 2018-12-14 两行累计净值为空，2018-12-18 起正常。未来 adapter 须对请求覆盖这些行的窗口 fail-closed 为 `missing_date_range` 或 `schema_drift`/`integrity_error`。

### 3. stock-sdk evidence-only 判断依据

**Pass.** 两个独立理由充分：

- **Provider lineage**（lines 246–255）：stock-sdk 包装 Eastmoney `pingzhongdata/{code}.js`，与已接受的 Akshare/Eastmoney 路径同源。不提供独立 provenance，不能升为 primary 或 secondary。
- **Date integrity_error**（lines 270–281）：通过源码确认 `new Date(timestamp).toISOString().slice(0,10)` 导致 UTC 日期转换偏移。三源交叉验证确认 CSRC 2023-01-12 的 `1.1254/1.1334` 在 stock-sdk 显示为 `date="2023-01-11"`。date 是 typed NAV record 的 identity key，偏移使 API 输出不能直接用于 typed contract。

### 4. stock-sdk date offset 根因分析

**Pass with minor observation.** 证据给出两个层面的分析：

- **Empirical**（line 273–274）：三源日期对比确认单向一天偏移
- **Source-level**（line 275）：定位到 bundled source 的 `new Date(timestamp).toISOString().slice(0,10)` 调用

见下方 F1 关于 source location precision 的 minor 建议。

### 5. Source metadata completeness

**Pass.** E4 matrix（lines 363–393）每条记录包含 plan required 的全部字段：source_name、source_url/provider、retrieved_at、fund_code、share_class、date_range、record_count、unit_nav、accumulated_nav、adjustment_basis、identity_status、failure_category。

CSRC 的 failure_category 正确区分了：null（正常窗口）、earliest blank rows caveat、F pre-inception missing_date_range。stock-sdk 的统一 `integrity_error` 分类一致。

### 6. Blocked bases preservation

**Pass.** 证据明确：

- Line 356: CSRC EID 只接受 `accumulated_nav`
- Line 358: `dividend_adjusted_nav` 和 `total_return` 未被证明
- Line 359: raw unit NAV 仍 blocked
- Completion report（line 443）: 四个 blocked bases 全部列出

### 7. FundDocumentRepository compliance

**Pass.** Line 195: `FundDocumentRepository.load_annual_report("006597", 2025)` 获取年报证据。Line 97: "No annual-report PDF/cache direct reads were used."

年报 metadata 记录 source 为 `eid`，report name 和 instance ID 与年报身份一致。

### 8. Non-goal and hard constraint preservation

**Pass.** Non-Goals Preserved section（lines 406–411）明确：
- 未修改 production code/tests
- 未修改 dependency files
- stock-sdk 使用 `/tmp` 解包，未动 `pyproject.toml`/`package.json`/lockfile
- drawdown blocker 未解除
- 未做 metric/score/snapshot/quality/golden/PR/push/release 变更

ruff/pytest 未运行——这符合 evidence-only gate 规则（验证矩阵已标注不要求），理由明确。

## Findings

### F1 — stock-sdk Date Computation Source Location Not Pinned (Non-Blocking)

**Location**: Evidence line 275

**Finding**: 证据声称 "The bundled source computes `date` via `new Date(timestamp).toISOString().slice(0,10)`"，但未提供该代码在 unpacked package 中的确切文件路径和行号。Commands run section（line 81）显示 `rg -n "getFundNavHistory|getFundDividendList|Data_ACWorthTrend|fund.eastmoney"` 执行过，但这不会匹配到 `toISOString` 或 `new Date`。不清楚 evidence worker 是实际查看了 source 中的 date computation，还是从行为推断。

**Severity**: Low。三源交叉验证（CSRC vs stock-sdk vs prior Akshare）已足以证明 date 偏移事实。无论根因是 UTC conversion 还是其他逻辑，`integrity_error` 的分类不受影响。

### F2 — A/C Earliest Blank Rows: Verification Scope Unclear (Non-Blocking)

**Location**: Evidence lines 172–173, 177–182

**Finding**: 证据称 A/C 的 "earliest two rows have blank accumulated NAV"（2018-12-07 和 2018-12-14），但未说明这个结论是通过完整分页扫描（全部 91 页）还是仅检查首页得出。若仅检查首页（前 20 行），可能存在后续页面也有 blank rows 的情况。

**Severity**: Low。即使有更多 blank rows，已有的 "earliest blank rows → fail-closed window handling" caveat 仍然正确——它只说 earliest rows 有问题且需要 adapter 处理。blank rows 的具体数量不影响分类逻辑。

### F3 — §3.1 Year-End NAV Reconciliation Not Executed (Non-Blocking)

**Location**: Plan E3 step 1 requires §3.1/§3.2/§3.3 extraction; Evidence lines 195–203

**Finding**: 证据通过 `FundDocumentRepository` 提取了 §2（份额映射）和 §3.3（E 类分红），也提到了 §3.1 E 类 2025 年末 NAV `1.1967`（line 203）。但未做系统性的同日期 CSRC source NAV 值与 §3.1 年报年末 NAV 的数值比对（如 2025-12-31 CSRC A/C/E/F 各份额单位净值 vs 年报 §3.1 披露值）。

**Severity**: Low。以下因素降低影响：
- E 类 2023 分红 cross-check 是更强的语义证明（event-level，not just snapshot）
- 前 gate（NAV adjusted-basis source identity）已对 Eastmoney/Akshare 做过年末 NAV 比对
- 年报 §3.1 year-end NAV 与 source NAV 的对齐在 adapter implementation gate 中会被更严格地执行

### F4 — stock-sdk +1 Record Count Discrepancy Not Explained (Non-Blocking)

**Location**: Evidence line 265–268, CSRC 1809 vs stock-sdk 1810 for A/C

**Finding**: stock-sdk 返回 1810 条 A/C 记录，而 CSRC 和 prior Akshare 都返回 1809 条。stock-sdk 最早日期为 `2018-12-02`（CSRC 为 `2018-12-07`），这表明 stock-sdk 多了一条边界日期的记录。证据未讨论这个 +1 差异的原因或影响。

**Severity**: Low。差异为 1 条边界记录，date shift 的 integrity_error 已经使 stock-sdk 无法进入 runtime，行数差异不影响 evidence-only 判定。

### F5 — getFundNavHistory 2023-01-11 Row Identity 描述可更精确 (Non-Blocking)

**Location**: Evidence lines 270–276

**Finding**: Evidence 正确观察到 date shift，但表述顺序可能引起混淆。Line 274 说 "stock-sdk does not align those values to `date="2023-01-11"`" 指的是 CSRC 2023-01-11 的值（1.1252/1.1332）没有出现在 stock-sdk 的任何日期下。实际上 CSRC 2023-01-12 的值（1.1254/1.1334）出现在了 stock-sdk 的 `date="2023-01-11"`。两句话各自正确，但读者需要结合前文 context 才能清晰区分"CSRC 的 1-11 values"和"stock-sdk 的 1-11 date 下的 values"。

**Severity**: Trivial。阅读上下文后意思清晰，不影响结论。

## Cross-Reference with Prior Gate Evidence

| Prior Gate (Eastmoney/Akshare) | Current Gate (CSRC EID) | Consistency |
|---|---|---|
| A 006597: 1809 rows, 2018-12-03 to 2026-05-27 | A 006597: 1809 rows, 2018-12-07 to 2026-05-28 | ✅ count match, date boundary 差几天（不同 source endpoint） |
| E 014217: 994 rows, 2022-04-25 start | E 014217: 994 rows, 2022-04-25 start | ✅ exact match |
| E distribution: 2023-01-11 diff 0.0080 | E distribution: 2023-01-11 diff 0.0080 | ✅ exact match |
| F 022176: 398 rows, 2024-10-08 start | F 022176: 398 rows, source-inception-forward | ✅ count match |
| Adjustment basis: accumulated_nav | Adjustment basis: accumulated_nav | ✅ 一致 |
| LJSYLZS: adjustment_basis_unknown | N/A (CSRC 无此 endpoint) | ✅ 无冲突 |

## Residual Risks

1. **CSRC EID endpoint stability**：当前使用的 `validate_fund.do`/`fund_detail_search.do`/`list_net_classification.do` 是 HTML endpoint，非结构化 API，CSRC 可能在未来改变 HTML schema 或分页参数。Adapter implementation 需处理 `schema_drift`。

2. **CSRC A/C earliest blank rows 边界不精确**：evidence 确认 blank 存在但未穷举。Adapter 实现时需全量扫描后确定精确的 blank→populated 切换日期。

3. **stock-sdk date bug fixability 未知**：当前 bug 在 bundled source 中，stock-sdk 是否能接受 patch 或 upstream fix 未调查。即使 fix 后，stock-sdk 仍只是 Eastmoney wrapper，不改变 provenance。

4. **F class CSRC 适配路径**：F 的公开搜索缺失意味着 adapter 需先通过 A/C/E 搜索定位到 detail page，再从 detail page 提取 F classification link。这是间接路径，需在 adapter 中显式处理并保留 fail-closed。

5. **CSRC 分页依赖**：当前使用 `limit=20`，adapter 需实现完整分页遍历并处理边界（最后一页可能不足 20 行）。

## Explicit Statement

Controller **可以** accept 当前 evidence 并 proceed to controller judgment。两条 recommended decisions（CSRC EID accepted-primary-candidate、stock-sdk evidence-only）均有充分 evidence basis。F1–F5 为非阻断 minor findings，不影响决策质量，可作为 controller judgment 的 residual notes 记录。

Recommended next gate：CSRC EID adapter normalization implementation plan（先于或与 accumulated-nav source adapter normalization implementation gate 合并），在该 gate 中按当前 evidence 记录的 caveats 实现 fail-closed 适配逻辑。
