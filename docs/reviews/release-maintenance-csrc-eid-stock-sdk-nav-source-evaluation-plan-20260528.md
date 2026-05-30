# CSRC EID and stock-sdk NAV Source Evaluation Gate — Plan

日期：2026-05-28

角色：AgentCodex planning worker，非 controller，非 implementation worker。

Work unit：`CSRC EID and stock-sdk accumulated NAV source evaluation gate`

Gate classification：`heavy source/evidence gate`

## Step Self-Check

- Current gate / role：当前只为 controller 产出 handoff-ready plan artifact；不启动完整 gateflow，不进入 evidence、implementation、fix、review、commit、PR、push、merge、release 或 golden promotion。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、最新 NAV source identity controller judgment / evidence，以及 `fund_agent/fund/data/nav_models.py`、`fund_agent/fund/data/nav_repository.py`、`fund_agent/fund/data/nav_data.py`。
- Scope boundary：只允许新增本 plan artifact；不改 production code/tests、score、snapshot、quality gate、golden fixture、drawdown metric、Host/Agent/dayu、年报来源实现或 README。
- Stop conditions：若任一候选来源不能证明 source identity、field semantics、license/runtime fit 或 failure taxonomy，结论必须为 `blocked` / `rejected` / `secondary-only`，不得解除 `drawdown_stress` blocker。
- Evidence and validation：本计划完成信号是 controller 可直接派发 evidence worker 执行 E1-E4；本 gate 为 evidence-only，除非后续改代码/测试，否则不要求 full ruff/pytest。
- Next action：controller 派发 DS / GLM plan review；plan review 通过后再派 evidence worker，不由本 worker继续执行来源 smoke。

## Truth Source Recap

- 当前架构真源为 `UI -> Service -> Host -> Agent`；NAV source / repository 归属 Agent 层 `fund_agent/fund/data`，不得绕过 Fund data boundary。
- 年报 / PDF / cache 访问必须经过 `FundDocumentRepository`；跨核年报 §3.1 / §3.2 / §3.3 时不得直接读 PDF 或 cache 文件。
- 当前 typed NAV contract 已能表达 `unit_nav`、`accumulated_nav`、`adjusted_nav`、`total_return_index`、`raw_unit_nav`、`accumulated_nav`、`dividend_adjusted_nav`、`total_return`、identity / completeness / failure taxonomy。
- 当前 `FundNavRepository.load_nav_series()` 生产路径仍只把 Akshare `单位净值走势` 归一化为 `nav_type="unit_nav"`、`adjusted_basis="raw_unit_nav"`、`dividend_adjustment_status="not_adjusted"`、`identity_status="requested_code_only"`，且 `strong_drawdown_evidence_eligible=False`。
- 最新 accepted evidence 只接受 Eastmoney / 天天基金 `Data_ACWorthTrend` / `累计净值走势` 作为未来 `accumulated_nav` source/basis identity candidate；`LJSYLZS` 仍为 `adjustment_basis_unknown`；raw unit NAV 仍非强证据。
- 本 gate 只能评估 CSRC EID 与 stock-sdk 是否可成为 typed contract adjusted-basis source candidates，不能直接进入 adapter normalization 或 drawdown metric gate。

## Gate Classification

本 gate 分类为 `heavy`，原因：

- 涉及外部 NAV source strategy、source provenance、field semantics、failure taxonomy 和未来 adapter candidate 优先级。
- 可能影响后续 typed NAV source adapter normalization 的 primary / secondary source 顺序。
- 若误把 raw unit NAV、未知累计收益率或未证明语义的 SDK 输出当成 adjusted basis，会污染后续第 6 章 `drawdown_stress` 强证据。

升级条件：

- 若 evidence worker 发现任一来源需要新增 runtime dependency、schema change、public contract change、license exception、Node subprocess、MCP server 或 production cache schema，必须停止并交回 controller 开新 implementation / architecture gate。

## Scope / Non-Goals

### In Scope

- 评估 CSRC EID 页面是否可机器读取历史 NAV 表，字段至少包括 `date`、`unit_nav`、`accumulated_nav`。
- 评估 `chengzuopeng/stock-sdk` 的 `getFundNavHistory` 是否能返回 006597 full-history unit + accumulated NAV，并扩展验证 A/C/E/F：`006597`、`006598`、`014217`、`022176`。
- 评估 stock-sdk 的 underlying provider、字段语义、错误分类、license、dependency model，以及未来候选归属：runtime dependency、subprocess adapter、MCP/evidence-only adapter、secondary/cross-check only 或 reject。
- 评估 `getFundDividendList` 是否能 cross-check E 类 `014217` 历史分红，防止 raw unit NAV ex-dividend drawdown false positives。
- 设计 CSRC EID、stock-sdk、已接受 Eastmoney/Akshare accumulated NAV evidence 与年报 §3.1 / §3.2 / §3.3 的交叉核验矩阵。

### Non-Goals

- 不实现代码、测试、adapter、repository、metric、cache schema、CLI、Service、renderer 或 quality gate。
- 不写 source evidence artifact。
- 不直接解除 `drawdown_stress` blocker。
- 不实现 max drawdown / volatility。
- 不改 score、snapshot、quality gate、golden fixture、release、PR、push、merge 或 promotion。
- 不绕过 `FundDocumentRepository` 读取年报 / PDF / cache。
- 不新增 runtime Node / Python dependency；stock-sdk 只能作为被评估对象，不能在本 plan gate 中纳入生产依赖。
- 不改变 UI -> Service -> Host -> Agent 边界；NAV source / repository 保持在 Fund data layer。
- 不使用 `extra_payload` 传递显式参数。

## Source Evaluation Slices

### E1 — CSRC EID Smoke

Objective：判断 CSRC EID fund disclosure page 是否能作为官方、机器可读、可复现的 historical NAV source candidate。

User-supplied candidate URL：

```text
http://eid.csrc.gov.cn/fund/disclose/fund_detail_search.do?cFundCode=5755&rnd=0.368289794103286
```

该 URL 只能作为用户提供的待验证候选，不是已接受身份。Evidence worker 不得从 `cFundCode=5755` 反向假设目标基金身份。

Required evaluation steps：

0. 先使用 CSRC EID 公开搜索入口按基金名称 `国泰利享中短债债券` 或 6 位份额代码 `006597` / `006598` / `014217` / `022176` 定位官方披露详情页，并记录 EID 返回的内部 ID、详情页 URL、搜索参数和返回身份字段。只有当前置搜索可复现地把名称 / 份额代码映射到 EID 内部 ID 后，才能把该内部 ID 用于后续候选 URL / XHR 解析。若搜索无法映射名称或任一份额代码到内部 ID，分类为 `identity_status="unknown"` 并将 CSRC EID 判为 `blocked`；不得 reverse-assume `5755`。
1. 用 evidence-only 脚本或浏览器开发者网络日志定位页面是否存在可复现 HTTP GET/POST/XHR 数据端点；记录 method、URL、query/form params、headers 中的必要字段、response content-type、编码、分页参数和是否需要 cookie/session/captcha。
2. 证明前置搜索得到的 EID 内部 ID 与目标基金 / 份额代码的身份关系。若 EID 使用内部基金 ID 而非 6 位份额代码，必须找到官方页面字段、链接、表格或年报披露信息把该内部 ID 映射到 `006597` / `006598` / `014217` / `022176`，否则 `identity_status="unknown"` 或 `identity_mismatch`。同时必须确认 CSRC EID 披露粒度是产品级还是份额级；若只返回产品级数据且无法拆分 A/C/E/F 份额类别，分类为 `identity_mismatch` 或 `blocked`，不得把产品级 NAV 当作份额级 series。
3. 查找历史 NAV 表是否包含可机器解析的日期、单位净值、累计净值。接受字段要求：`date` 可解析为交易日，`unit_nav` 和 `accumulated_nav` 可解析为 Decimal，行级记录可按日期去重排序。
4. 验证表格是否为 full-history 或至少能显式分页获取完整历史；记录 `date_range`、`record_count`、分页总数、首尾日期。
5. 验证 CSRC EID 字段语义：若列名直接为 `单位净值` / `累计净值`，可作为 `nav_type="accumulated_nav"`、`adjustment_basis="accumulated_nav"` 的候选，但仍需与 E 类分红事件和年报交叉验证；若只有单位净值或收益率，不能作为 adjusted-basis candidate。
6. 分类失败：
   - 页面 / 接口正常但无目标基金或无 NAV 表：`not_found`。
   - 网络、超时、临时 5xx、DNS、TLS、短时不可访问：`unavailable`。
   - DOM/XHR schema 与预期字段不符、字段缺失、编码无法稳定解析：`schema_drift`。
   - `cFundCode`、基金简称、份额代码、日期范围或报告类型与目标矛盾：`identity_mismatch`。
   - response 截断、分页丢行、数值无法 Decimal 化、重复日期冲突：`integrity_error`。
   - 有 NAV 但不能证明累计净值语义：`adjustment_basis_unknown`。

Acceptance criteria：

- 若 CSRC EID 是官方来源且可机器读取 full-history 或明确覆盖所需窗口的 `date + unit_nav + accumulated_nav`，且身份可 verified，controller 可判定其为 primary source candidate。
- 若 CSRC EID 官方但只可人工页面查看、需要不可复现 session/captcha、无累计净值、字段语义不明或无法证明份额身份，判定为 `blocked` 或 `rejected`，不得进入 runtime adapter。

### E2 — stock-sdk Smoke / License / Provider

Objective：判断 `chengzuopeng/stock-sdk` 是否能提供可证明 provenance 的 full-history unit + accumulated NAV，以及是否适合本项目运行时边界。

Required evaluation steps：

1. 定位官方 repository、package metadata、license、README/API docs、release cadence、language/runtime、installation model、transitive dependency、network provider 说明；不得在本 gate 添加依赖到项目配置。
2. 以 evidence-only 方式验证 `getFundNavHistory`：
   - primary code：`006597`。
   - extended codes：`006598`、`014217`、`022176`。
   - 显式参数：`fund_code`、`share_class`、`start_date`、`end_date`、`minimum_records`、`force_refresh` / cache policy（若 SDK 支持）；不得使用自由 `extra_payload`。
   - 输出必须记录原始字段名、样例行、首尾日期、record_count、单位净值字段、累计净值字段、日期字段、source URL/provider 字段。
3. 验证 stock-sdk API surface：
   - 若 `getFundNavHistory` 不存在、函数名不同或 docs/source 中找不到等价 NAV history API，记录实际 API surface，分类为 `not_found`。
   - 若 `getFundNavHistory` 存在但参数签名、分页模型、返回字段或字段语义与 `date + unit_nav + accumulated_nav` contract 不兼容，分类为 `schema_drift` 并记录实际 contract。
4. 反查 SDK underlying provider：
   - 若 SDK 明确调用 Eastmoney / 天天基金 `Data_ACWorthTrend`，它只能作为 Eastmoney 的替代 client/cross-check，不能单独提高 provenance 等级。
   - 若 SDK 调用 CSRC EID、基金公司、交易所或其他官方接口，必须记录 provider URL、provider-owned identity 字段和字段语义文档。
   - 若 SDK 隐藏 provider、混合多个 provider 或只返回二次加工数据，除非能通过源码和网络日志证明 lineage，否则 `source_name="stock-sdk"` 不能作为 primary source。
5. 以 evidence-only 方式验证 `getFundDividendList` 作为 E 类分红冗余 cross-check，而非独立 primary source：
   - 必须调用 / 定位等价 API：`fund_code="014217"`；若 SDK 支持 `start_date` / `end_date`，显式覆盖包含 `2023-01-11` 的窗口。
   - 输出必须记录原始字段名、样例行、分红日期 / 除息日 / 除权日字段、每份分红金额、权益登记日 / record date（若有）、provider/source URL 字段、returned fund code/name/share class 字段。
   - Cross-check 方法：用 `getFundDividendList` 的 E 类 `014217` 分红日期和每份分红金额，对照 `getFundNavHistory` 在 `2023-01-11` 前后 `accumulated_nav - unit_nav` 的变化；期望与 `FundDocumentRepository.load_annual_report("006597", 2025)` 年报 §3.3 每 10 份 `0.080`（每份 `0.0080`）一致。
   - 失败分类：无分红记录为 `not_found`；provider/network/runtime 不可用为 `unavailable`；字段不可解析、缺少日期或金额字段为 `schema_drift`；分红日期 / fund identity / share class 与年报或 NAV history 身份矛盾为 `identity_mismatch`；日期可匹配但金额与年报或 NAV 差值矛盾、重复记录或数值完整性异常为 `integrity_error`；能返回分红但不能说明 NAV history 的累计净值调整语义时为 `adjustment_basis_unknown`。
6. 验证错误与异常模型：
   - 无基金 / 空数组：`not_found`。
   - provider/network/runtime unavailable：`unavailable`。
   - 字段改名、缺少累计净值、日期格式漂移：`schema_drift`。
   - 返回 code/name/share class 与请求不符：`identity_mismatch`。
   - 日期重复、数值非法、分页缺口、累计净值小数异常：`integrity_error`。
   - 返回 unit NAV 或收益率但无累计净值语义：`adjustment_basis_unknown`。
   - F 类 022176 请求 pre-2024-10-08 窗口：`missing_date_range`。
7. 评估 dependency model：
   - `runtime dependency` 只有在 license 明确兼容、维护状态可接受、provider lineage 透明、API 稳定、无重型 Node runtime/side effects、失败可分类、且强于现有 Akshare/Eastmoney client 时才可进入后续 architecture/implementation gate。
   - `subprocess adapter` 只有在 SDK 非 Python 但可 pin 版本、可纯命令行 JSON 输出、可隔离超时/退出码、无全局状态污染时作为未来候选。
   - `MCP/evidence-only adapter` 适用于 license/runtime 不适合生产依赖、但可作为人工 source evidence / cross-check 的场景。
   - `reject` 适用于 license 不明/不兼容、provider 不透明、字段语义无法证明、维护风险高、需不可控 runtime 或输出无法 fail-closed 的场景。

Acceptance criteria：

- `getFundNavHistory` 对 `006597` 必须返回 full-history 或覆盖显式窗口的 `date + unit_nav + accumulated_nav`，且能证明 provider identity / field semantics，才可作为 candidate。
- A/C/E/F 扩展验证必须保持 share class separated；不得把产品级数据混为份额级数据。
- 若 stock-sdk 的累计净值来源实际等同 Eastmoney `Data_ACWorthTrend`，默认为 secondary/cross-check candidate；除非 license/runtime/provider proof 显著优于现有路径，否则不升为 primary。

### E3 — Cross-Source Reconciliation

Objective：用官方年报、已接受 Eastmoney/Akshare accumulated NAV evidence、CSRC EID 和 stock-sdk 互相校验 source identity 与 accumulated NAV semantics。

Execution dependency：

- E3 reconciliation 矩阵只对 E1/E2 中至少返回一条 NAV row 且 `identity_status` 非 `unknown` / `identity_mismatch` 的 source 执行。
- 对 blocked / rejected / no-row / unknown-identity source，不执行数值 reconciliation；在 E4 disposition matrix 中对应行标记为 `not_applicable` 并保留原始 failure category。

Required cross-checks：

1. Annual report via `FundDocumentRepository`：
   - `load_annual_report("006597", 2025)`，只通过 repository 读取。
   - §2 / §3.1 / §3.2 / §3.3 提取份额代码映射、年末 NAV、基金净值表现、过去三年利润分配。
   - 必须记录年报章节/表格锚点，不得直接读 PDF/cache。
2. Identity reconciliation：
   - 对每个 source 和每个代码记录 requested code、returned code、returned name、share class suffix、provider URL。
   - `006597=A`、`006598=C`、`014217=E`、`022176=F` 必须逐一 verified；任何缺失只能降级，不得推断为 verified。
3. Field semantics reconciliation：
   - E 类 `014217` 必须用 2023 分红交叉验证：年报 §3.3 每 10 份 `0.080`，provider / source 分红日期，source `accumulated_nav - unit_nav` 在除权日后增加 `0.0080`。
   - A/C/F 无分红窗口只能证明 accumulated NAV 与 unit NAV 可相等，不能单独证明分红调整语义；需依赖同 source E 类事件或官方字段定义。
4. Numeric reconciliation：
   - 比较同日期 `unit_nav`、`accumulated_nav`；允许 Decimal 精度差异必须显式定义容忍度。
   - 与年报 §3.1 年末份额净值比对时，必须确认日期、份额类别、单位/累计字段，避免把年末 NAV 与累计 NAV 混用。
5. Existing accepted evidence reconciliation：
   - Eastmoney/Akshare `Data_ACWorthTrend` 已接受为 `accumulated_nav` candidate；CSRC EID 若官方且可机读，应优先级高于 Eastmoney/Akshare。
   - stock-sdk 若 underlying provider 为 Eastmoney，只能作为 client redundancy / cross-check，不改变 source provenance。

Decision rules：

- 只有 raw unit NAV 可得：保持 blocked；不得以 raw unit NAV 补 drawdown evidence。
- 能证明 `accumulated_nav`：只分类为 `adjustment_basis="accumulated_nav"`，不得写成 `dividend_adjusted_nav` 或 `total_return`。
- 若 source 字段名暗示复权、分红调整、后复权或 total return，但没有可验证的 provider-owned 文档 / 公式 / 事件级 cross-check 说明其语义，分类为 `adjustment_basis_unknown`；不得从字段名推断为 `dividend_adjusted_nav` 或 `total_return`。
- 能证明 dividend-reinvested total return：必须另开 source semantics gate；本 gate 不接受字段名推断。

### E4 — Decision / Judgment

Objective：为 controller 输出可裁决的 source disposition matrix。

Required outputs：

- CSRC EID decision：`accepted-primary-candidate` / `rejected` / `blocked`。
- stock-sdk decision：`accepted-runtime-candidate` / `secondary-only` / `evidence-only` / `rejected` / `blocked`。
- Per-code matrix：`006597`、`006598`、`014217`、`022176` 的 identity、date_range、record_count、unit_nav、accumulated_nav、adjustment_basis、failure_category；对 E1/E2 已 blocked / rejected / unknown-identity 或未返回 NAV row 的 source，填写 `not_applicable` 并引用对应 failure category。
- Provider lineage：每个 source 的 `source_name`、`source_url/provider`、retrieved_at、endpoint、字段语义证据。
- Residuals：license/runtime/source semantics/date coverage/failure taxonomy 中未解决项。

Controller judgment guardrails：

- CSRC EID 若官方且可机器读取 `date + unit_nav + accumulated_nav`，优先作为 future primary source candidate。
- stock-sdk 默认 secondary/cross-check；只有 source proof、license 与 runtime fit 都强于现有路径，才可进入 runtime dependency implementation gate。
- 任何 candidate 都不能在本 gate 中解除 `drawdown_stress` blocker；后续仍需 adapter normalization gate 和 metric contract gate。

## Required Source Metadata

每个成功或候选 series 必须显式记录：

| Field | Required meaning |
|---|---|
| `source_name` | `csrc_eid` / `stock_sdk` / underlying provider name |
| `source_url/provider` | 具体页面、API、SDK provider lineage |
| `retrieved_at` | UTC ISO timestamp |
| `fund_code` | requested 6 位基金份额代码 |
| `share_class` | A / C / E / F |
| `date_range` | first date / last date |
| `record_count` | source records count |
| `unit_nav` | typed Decimal field mapping and sample |
| `accumulated_nav` | typed Decimal field mapping and sample |
| `adjustment_basis` | only `accumulated_nav` if proven; otherwise `unknown` / blocked |
| `identity_status` | `verified` / `requested_code_only` / `identity_mismatch` / `unknown` |
| `failure_category` | `not_found` / `unavailable` / `schema_drift` / `identity_mismatch` / `integrity_error` / `adjustment_basis_unknown` / `missing_date_range` / `insufficient_records` |

## Stop Conditions

Evidence worker must stop and report to controller if:

- CSRC EID requires captcha, unreproducible session, manual-only UI, or public search cannot map fund name / target 6 位 share-class codes to an official EID internal ID.
- CSRC EID / stock-sdk returns only raw unit NAV or cumulative return without accumulated NAV semantics proof.
- stock-sdk license is missing, incompatible, ambiguous, or depends on an unacceptable runtime model.
- stock-sdk underlying provider cannot be identified from docs/source/network evidence.
- Any source returns product-level data that cannot be separated by A/C/E/F share class.
- Any data source contradicts annual report §3.1 / §3.2 / §3.3 and root cause cannot be proven from same-source logic/data.
- Any planned action would require adding dependency, modifying production code/tests, changing typed schema, changing score/snapshot/quality gate/golden fixture, or accessing annual reports outside `FundDocumentRepository`.
- Validation finds unclassified failure mode outside current `NavFailureCategory`; controller must decide whether to open taxonomy gate.

## Validation Matrix

| Validation | Required in this evidence gate | Expected result |
|---|---:|---|
| `git branch --show-current` | Yes | Branch recorded; no protected-branch action needed because no commit/push |
| `git status --short` | Yes | Dirty scope recorded; only planned artifact/evidence artifacts touched |
| Read truth sources | Yes | AGENTS/design/control/latest NAV judgments/current NAV code recap in artifact |
| CSRC EID HTTP/XHR smoke | Yes, evidence-only | Endpoint, params, identity, columns, dates, failures classified |
| stock-sdk docs/source/license inspection | Yes, evidence-only | Provider lineage, license, dependency model, API semantics classified |
| stock-sdk `getFundNavHistory` smoke | Yes, evidence-only if environment permits without project dependency mutation | 006597 primary and A/C/E/F matrix; if not runnable, record blocker |
| stock-sdk `getFundDividendList` smoke | Yes, evidence-only if environment permits without project dependency mutation | 014217 distribution cross-check or classified blocker |
| `FundDocumentRepository.load_annual_report("006597", 2025)` | Yes | §3.1 / §3.2 / §3.3 anchors used for reconciliation |
| Full `ruff` | No unless code/tests changed | Not required for docs/evidence-only gate |
| Full `pytest` | No unless code/tests changed | Not required for docs/evidence-only gate |
| Snapshot / score / quality gate | No | Must not be run as blocker-unblocking signal in this gate |

## Review Requirements

- Plan review：DS and GLM must independently review this plan before evidence execution.
- Evidence review：After evidence artifact is written, DS and GLM must independently review source identity, field semantics, failure classification, license/runtime fit and non-goal preservation.
- Controller judgment：Only controller may accept/reject/defer findings and set terminal source disposition.

Plan review focus:

- Does the plan prevent raw unit NAV / unknown basis from becoming strong evidence?
- Are CSRC EID and stock-sdk evaluated with direct provenance rather than indirect field-name inference?
- Is stock-sdk runtime/license/dependency risk separated from source semantics?
- Are A/C/E/F share classes kept separated?
- Is annual-report reconciliation constrained to `FundDocumentRepository`?
- Are stop conditions clear enough to prevent implementation drift?

## Completion Report Format

Evidence worker final report to controller must include:

```text
Self-check: pass | blocked - <reason>
Artifact path: <evidence artifact path>
CSRC EID decision: accepted-primary-candidate | rejected | blocked
stock-sdk decision: accepted-runtime-candidate | secondary-only | evidence-only | rejected | blocked
Accepted adjustment_basis: accumulated_nav | none
Rejected/blocked bases: raw_unit_nav, adjustment_basis_unknown, dividend_adjusted_nav, total_return, as applicable
Per-code coverage:
- 006597 A: <identity/date_range/record_count/failure>
- 006598 C: <identity/date_range/record_count/failure>
- 014217 E: <identity/date_range/record_count/distribution cross-check/failure>
- 022176 F: <identity/date_range/record_count/missing_date_range if applicable>
Provider/license/runtime disposition:
- CSRC EID: <official/machine-readable/provider URL/failure>
- stock-sdk: <underlying provider/license/dependency model/recommended role>
Annual report reconciliation: <§3.1/§3.2/§3.3 anchors via FundDocumentRepository>
Validation: <commands or evidence-only checks run>
Residual risks / controller decisions needed: <list>
Non-goals preserved: no code/tests, no drawdown blocker解除, no metric, no score/snapshot/quality/golden, no dependency, no PR/push/release
```

## Handoff Status

This plan is handoff-ready for controller review dispatch, subject to DS / GLM plan review.
