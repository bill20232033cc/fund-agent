# NAV Adjusted-Basis Source Identity Gate — Handoff Plan

日期：2026-05-28

角色：planning worker，非 controller。

Work unit：`NAV adjusted-basis source identity gate`

计划结论：`handoff-ready plan`

## Step Self-Check

- Current gate / role：本 artifact 仅为 planning worker handoff；不启动新 gateflow，不 implement、commit、push、PR、release 或 golden promotion。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、前序 NAV controller judgments / deepreviews、当前 snapshot / score / quality gate、`fund_agent/fund/data/nav_*.py` 和 `tests/fund/data/test_nav_repository_contract.py`。
- Scope boundary：本 gate 只验证并裁决 NAV source identity 与 adjusted basis 是否可接受；不实现 max drawdown、volatility、score、snapshot、quality gate、golden fixture、bond extractor、Host/Agent/dayu、QDII/FOF/110020 或 release/PR 外部动作。
- Stop conditions：若不能证明 adjusted / dividend-adjusted / total-return basis 与 source/share-class identity，输出 `blocked-with-source-gap`，不得解除 `drawdown_stress` blocker。
- Evidence and validation：优先产出 source smoke / evidence artifact、source semantics proof、A/C/E/F identity matrix；只有 plan/review 后才允许最小 adapter/source-spike tests。
- Next action：controller 可派发 DS 与 GLM plan review；review 通过后进入 evidence slice，不进入 drawdown metric implementation。

## Gate Classification

Classification：`heavy`

Rationale：

- 本 gate 影响 future `drawdown_stress` strong quantitative evidence 的来源身份、调整基础、failure taxonomy 和外部来源策略。
- 任何错误接受都可能把 raw unit NAV、错误份额类别或未复权序列升级为强证据，进而错误解除 baseline blocker。
- 按 `AGENTS.md`，外部来源策略、质量门控语义、baseline/golden 资格和高影响 public contract 相关 gate 均选择 `heavy`；分类不确定时选择更重一级。

## Goal

验证并决定：是否存在一个可接受的 NAV source identity 与 adjusted basis，可以作为未来 `drawdown_stress` strong evidence 的输入前置。

本 gate 的唯一成功输出是 source identity / adjusted basis 的可接受性裁决和后续最小实现入口。即使找到候选 adjusted / total-return 序列，也不得在本 gate 实现 max drawdown、volatility 或解除 blocker。

## Non-Goals

- 不解除 `drawdown_stress` blocker。
- 不把 raw unit NAV 或年报“控制回撤”文字视为 quantitative strong evidence。
- 不混合 006597 A、006598 C、014217 E、022176 F 到同一条 product-level NAV series。
- 不修改 score、snapshot、quality gate、golden fixture、bond extractor、Host/Agent/dayu、QDII/FOF/110020、release/PR/push/merge。
- 不改变 UI -> Service -> Host -> Agent 边界；NAV source adapter / repository 仍属于 Agent 层 Fund data 包。
- 不用 `extra_payload`；后续所有参数必须显式声明。
- 不直接把 Akshare/public JS smoke 接入生产；smoke 仅能作为 evidence artifact 输入。

## Direct Source Facts Already Known

### Current Product / Control Facts

- `docs/implementation-control.md` 当前 next entry point 包含 `NAV adjusted-basis source identity gate`。
- 当前 typed NAV path 已 accepted-local-validation，但 006597 real smoke 仍是：
  - `records=1809`
  - `share_class="A"`
  - `nav_type="unit_nav"`
  - `adjusted_basis="raw_unit_nav"`
  - `dividend_adjustment_status="not_adjusted"`
  - `identity_status="requested_code_only"`
  - `strong_drawdown_evidence_eligible=false`
  - `source="nav_cache"`
  - `origin_source="akshare"`
- `docs/design.md` 当前设计明确：后续路径型 drawdown metric 只能消费 `FundNavRepository.load_nav_series()`；不得直接读取 Akshare、SQLite cache、snapshot JSONL 或旧 raw payload。
- `reports/extraction-snapshots/.../snapshot.jsonl` 当前 `bond_risk_evidence.v1` 为 `contract_status=partial`，`weak_groups=["drawdown_stress"]`，其余已满足组包括 `credit_risk` 与 `redemption_share_pressure`。
- `reports/scoring-runs/.../score.json` 当前 `bond_risk_evidence_missing.baseline_blocking=true`，`still_missing_evidence_groups` 只剩 `drawdown_stress`。
- `reports/quality-gate-runs/.../quality_gate.json` 当前 status 为 `warn`，仍包含 006597 债券风险证据相关 warning；不得在本 gate 修改。

### Current Code Facts

- `FundNavRepository.load_nav_series()` 签名使用显式参数：`fund_code`、`share_class`、`start_date`、`end_date`、`minimum_records`、`force_refresh`；无 `extra_payload`、无 `**kwargs`。
- `FundNavSeries` / `FundNavRecord` / `NavSourceMetadata` / `ShareClassMapping` 已能表达：
  - `nav_type`
  - `adjusted_basis`
  - `dividend_adjustment_status`
  - `identity_status`
  - source/cache provenance
  - `strong_drawdown_evidence_eligible`
  - fail-closed `NavFailureCategory`
- 当前 repository normalization 固定把 Akshare `单位净值走势` 标为 `unit_nav` / `raw_unit_nav` / `not_adjusted` / `requested_code_only`，并强制 not strong eligible。
- 当前 models 已有 `NavType` 值：`unit_nav`、`accumulated_nav`、`adjusted_nav`、`total_return_index`、`unknown`。
- 当前 models 已有 `AdjustmentBasis` 值：`raw_unit_nav`、`accumulated_nav`、`dividend_adjusted_nav`、`total_return`、`unknown`。
- 因此下一步大概率不需要新增 typed model 字段；可能只需要新增 source adapter normalization、source identity proof 和 tests。若 evidence 发现需要同时携带多个 NAV 序列或 provider method metadata，再由 review 决定是否开独立 schema slice。

### Public Source Smoke Facts From Planning Probe

这些 probe 是 source evidence 输入，不是生产边界实现：

- 本地项目环境 `uv run python` 可 import `akshare==1.18.60`。
- `ak.fund_open_fund_info_em(symbol, indicator=...)` 源码支持指标：
  - `单位净值走势` -> `Data_netWorthTrend`，列为 `净值日期`、`单位净值`、`日增长率`。
  - `累计净值走势` -> `Data_ACWorthTrend`，列为 `净值日期`、`累计净值`。
  - `累计收益率走势` -> Eastmoney API `LJSYLZS`，列为 `日期`、`累计收益率`。
- 真实 smoke for 006597 / 006598 / 014217 / 022176：
  - 三类 indicator 均可返回非空序列。
  - DataFrame 列本身不包含基金代码或基金名称 identity 字段。
  - 006597 A：`单位净值走势` / `累计净值走势` 各 1809 rows；`累计收益率走势` 202 rows。
  - 006598 C：`单位净值走势` / `累计净值走势` 各 1809 rows；`累计收益率走势` 202 rows。
  - 014217 E：`单位净值走势` / `累计净值走势` 各 994 rows；`累计收益率走势` 250 rows。
  - 022176 F：三类 indicator 各 398 rows；成立期从 2024-10-08 附近开始。
- 公开 Eastmoney JS `https://fund.eastmoney.com/pingzhongdata/{code}.js` smoke 返回：
  - 006597 -> `fS_code="006597"`，`fS_name="国泰利享中短债债券A"`，存在 `Data_netWorthTrend` / `Data_ACWorthTrend` / `Data_grandTotal`。
  - 006598 -> `fS_code="006598"`，`fS_name="国泰利享中短债债券C"`，存在同类变量。
  - 014217 -> `fS_code="014217"`，`fS_name="国泰利享中短债债券E"`，存在同类变量。
  - 022176 -> `fS_code="022176"`，`fS_name="国泰利享中短债债券F"`，存在同类变量。
- Planning probe 不能证明 `累计净值走势` 或 `累计收益率走势` 的分红处理语义；只能说明候选序列存在。

## Candidate Sources And Capability Questions

### Candidate 1: Current Akshare `fund_open_fund_info_em`

Candidate status：`candidate-requires-proof`

Known capabilities：

- `单位净值走势` 已是当前生产 path，必须继续标为 `raw_unit_nav` / not strong eligible。
- `累计净值走势` 可返回 `累计净值` 序列，但字段名不足以证明 adjusted basis。
- `累计收益率走势` 可返回 `累计收益率` 序列，可能是 total-return-like candidate，但需要 provider/source semantics proof。

Required inspection without bypassing future production boundaries：

- Evidence slice 可调用 Akshare public APIs 或读取 installed Akshare source，产出 `docs/reviews/...evidence...md`。
- Production path 不得让 metric consumer 直接调用 Akshare；若 accepted，后续 implementation 只能把新 source logic 封装进 Fund data source adapter，再通过 `FundNavRepository.load_nav_series()` 输出 typed `FundNavSeries`。
- Evidence script 必须保留 command、akshare version、requested code、indicator、columns、row counts、date range、sample rows、error taxonomy；不得写入 cache fixture 或 golden。

Open proof needs：

- Akshare docstring / source code只能证明字段映射来自 Eastmoney 变量/API，不能单独证明 adjusted basis。
- 必须获得 provider 文档、Eastmoney page semantics、official source metadata 或分红事件 cross-check，至少满足 proof standard 中的一类强证明。

### Candidate 2: Eastmoney public JS `pingzhongdata/{code}.js`

Candidate status：`candidate-requires-proof`

Known capabilities：

- JS 中可见 `fS_code` / `fS_name`，可作为 source-returned identity candidate。
- JS 中可见 `Data_netWorthTrend` / `Data_ACWorthTrend` / `Data_grandTotal` 变量存在。
- 该来源与 Akshare 当前函数同源；可作为 future adapter normalization 的 source identity / source_id / source_url evidence candidate。

Required inspection：

- E1 identity smoke 只能用 public HTTP GET 读取 006597 / 006598 / 014217 / 022176 JS header、`fS_code`、`fS_name` 和变量名存在性，记录 HTTP status、Content-Type、source URL、identity 值和变量存在性。
- E1 不解析 `Data_ACWorthTrend`、`Data_grandTotal` 或其他数值变量内容；这些数值序列的语义证明和 cross-check 只属于 E2。
- E2 如需解析 JS 数值变量内容，必须使用 structured JS parser or existing Akshare/PyMiniRacer-style execution；regex 只能作为 evidence-only diagnostic 读取 `fS_code` / `fS_name` / 变量存在性，不得进入 production adapter implementation。

Open proof needs：

- `fS_code` / `fS_name` 可证明 requested code 与返回 identity 是否一致，但不能证明 adjusted basis。
- `Data_ACWorthTrend` / `Data_grandTotal` 的金融语义仍需文档或 cross-check 证明。

### Candidate 3: Official Fund Disclosure / Annual Reports

Candidate status：`supporting-cross-check-only`

Known capabilities：

- 前序 controller judgment 已接受：006597 2025 年报 §3.1 E-class year-end NAV 为 `1.1967`。
- 前序 controller judgment 已接受：006597 2025 年报 §3.3 证明 E class 2023 distribution：每 10 份 `0.080`，现金 `7,273,431.12`，再投资 `1,871,517.43`，合计 `9,144,948.55`。

Allowed use：

- 只能通过 `FundDocumentRepository` 读取年报，不得直接操作 PDF 文件系统。
- 可用于 dividend event cross-check 和 share-class identity cross-check。

Limit：

- 年报 §3.1 / §3.2 / §3.3 是披露锚点，不提供 daily NAV path；不能替代 max drawdown path source。
- 年报“控制回撤”类文字只能是 weak qualitative evidence。

### Candidate 4: Other Provider Or Official Metadata

Candidate status：`future-source-gap-option`

If Akshare/Eastmoney cannot provide acceptable proof：

- Controller should open next minimal source discovery gate for a provider that can return daily adjusted NAV / total-return index with explicit official semantics and source-returned identity.
- Do not weaken proof standard to accept raw unit NAV, ambiguous accumulated NAV, or unverifiable total-return-like fields.

## Proof Standard For Adjustment Basis

Adjustment basis must be proven, not guessed from column names.

Acceptable proof standard requires at least one primary proof plus one independent consistency check:

Primary proof options：

1. Provider documentation explicitly defines the field as accumulated NAV including historical distributions, dividend-adjusted NAV, or cumulative total-return series.
2. Source field semantics from official/source-owned metadata or page text explicitly states treatment of cash dividends and reinvestment.
3. Official fund disclosure provides share-class distribution events and NAV definitions, and provider series can be shown to incorporate those events in the expected direction around ex-dividend dates.

Independent consistency checks：

1. Around known dividend events, raw unit NAV and candidate adjusted/accumulated/total-return series must diverge by the distribution amount or return effect expected for that share class.
2. End-of-period candidate returns must reconcile within documented tolerance to annual-report §3.2 NAV growth or provider-reported cumulative return, with explanation of date window and share class.
3. Candidate source identity must match requested code/name/share class for the same series.

Mandatory block conditions：

- Field name only says `累计净值` or `累计收益率` but no semantics proof.
- Provider returns data without source-returned code/name/share class and no independent identity source at the same URL or response.
- Candidate series equals raw unit NAV across a period with known distribution for that share class, unless documentation proves no distribution applies to the requested class/date window.
- Cross-check cannot identify either an exact ex-dividend date or a defensible distribution window for the share class.
- Source terms or API shape changed unexpectedly (`schema_drift`) or returns contradict requested code/share class (`identity_mismatch`).

Accepted classifications if proven：

- `accumulated_nav`: acceptable only if semantics prove cumulative NAV and review accepts drawdown suitability as future metric input.
- `dividend_adjusted_nav`: preferred if source explicitly reinvests/distribution-adjusts NAV path.
- `total_return`: preferred if source provides total-return index or cumulative return path with source semantics and enough periodicity.
- `raw_unit_nav`: not acceptable for strong drawdown evidence unless a later separate gate proves the exact target period is distribution-free and identity/basis are verified. This gate should not rely on that exception.

## A/C/E/F Source Identity Plan

Required share-class matrix：

| Share class | Fund code | Expected name evidence | Required identity result |
|---|---:|---|---|
| A | `006597` | `国泰利享中短债债券A` | `verified` only if source returns code `006597` and name/share class A, or same-response metadata proves it |
| C | `006598` | `国泰利享中短债债券C` | `verified` only if source returns code `006598` and name/share class C, or same-response metadata proves it |
| E | `014217` | `国泰利享中短债债券E` | `verified` only if source returns code `014217` and name/share class E, or same-response metadata proves it |
| F | `022176` | `国泰利享中短债债券F` | `verified` only if source returns code `022176` and name/share class F, or same-response metadata proves it |

Rules：

- Each fund code is its own series and share class. Never merge A/C/E/F by product name.
- `share_class=None` may default to A only when `fund_code=006597` and mapping evidence says requested code maps to A; default must remain `requested_code_only` unless source identity is verified.
- Source-returned `fS_code` / `fS_name` or equivalent must be captured in `NavSourceMetadata.returned_fund_code` and `returned_fund_name`.
- `ShareClassMapping.resolved_fund_code` and `resolved_share_class` must come from source identity or explicit reviewed mapping, not name suffix guessing alone.
- If source returns fund name without suffix or with a conflicting suffix, fail `identity_mismatch`.
- If source returns rows but no identity metadata, classify `requested_code_only`; series may be returned but cannot be strong eligible.

## Why E-Class Raw Unit NAV Is Not Strong Evidence

E-class raw unit NAV across historical distribution periods cannot be strong evidence because raw unit NAV mechanically drops on cash distributions while investor total return may be preserved through cash / reinvestment. A path drawdown computed on raw unit NAV would confuse distribution mechanics with market or credit stress.

For 014217 E:

- Prior accepted evidence says E class had a 2023 distribution: every 10 shares `0.080`.
- Planning smoke shows 014217 `单位净值走势` has records around 2023-06 to 2023-09 and `累计净值走势` differs from `单位净值走势` during that window.
- This suggests candidate accumulated/adjusted behavior exists, but does not prove its treatment. Future evidence must identify the exact distribution/ex-date and show candidate adjusted/accumulated/total-return series handles it according to documented semantics.

If an adjusted series is accepted for E:

- It must be the 014217 E series, not 006597 A / 006598 C / 022176 F.
- Proof must include provider semantics plus dividend-event cross-check around the 2023 E-class distribution.
- Raw unit NAV remains weak and blocked even if an adjusted E series is accepted.

## Existing Typed Contract Fit

Current implementation can carry the needed decision without model-field changes for the likely path:

- `NavSourceMetadata.source_name`, `origin_source`, `source_id`, `source_url`, `retrieved_at`, `cache_updated_at`, `requested_fund_code`, `returned_fund_code`, `returned_fund_name`, `failure_category` can carry source identity/provenance.
- `ShareClassMapping` can carry requested/resolved code, share class, identity status and mapping evidence.
- `FundNavSeries.nav_type`, `adjusted_basis`, `dividend_adjustment_status`, `identity_status`, `completeness_status`, `strong_drawdown_evidence_eligible` can express accepted basis and eligibility.

Likely no new fields needed if source returns exactly one accepted series per call.

Possible future new field / schema slice only if review accepts one of these cases：

- A single source response returns multiple series and implementation must preserve original provider variable name / method name separately from `source_id`.
- Candidate `累计收益率走势` is accepted as a return series rather than NAV value series, requiring record-level value semantics beyond `nav_value`.
- Need to carry distribution-event proof metadata in runtime model rather than evidence artifact.

If any such case appears, stop current implementation and open a separate typed contract amendment plan.

## Failure Taxonomy

The gate must use these categories consistently:

| Category | Meaning | Fallback / handling |
|---|---|---|
| `not_found` | Source normally responds but target fund/code/indicator/date range not found | Eligible fallback; do not mask later fail-closed errors |
| `unavailable` | Network, timeout, transient provider, dependency unavailable | Eligible fallback; preserve original cause |
| `schema_drift` | Source response shape, variables, columns, or metadata differ from accepted contract | Fail-closed; no silent fallback masking |
| `identity_mismatch` | Returned code/name/share class contradict requested identity | Fail-closed |
| `integrity_error` | Content type, parse, duplicate date, impossible NAV/return values, record count mismatch | Fail-closed |
| `adjustment_basis_unknown` | Series exists but adjusted / accumulated / total-return semantics cannot be proven | Fail-closed; this is the expected result if proof is absent |
| `insufficient_history` | Candidate series does not cover required lookback/window or has too few records for future path metric | Fail-closed for strong evidence; may be diagnostic |

Note：`insufficient_history` is an evidence-level diagnostic label only. Current model terms are `insufficient_records` and `missing_date_range`; every E1/E2 evidence artifact that uses `insufficient_history` must also record the current model mapping, either `model_category="insufficient_records"` for too few rows or `model_category="missing_date_range"` for uncovered date windows. If future implementation needs exact runtime `NavFailureCategory="insufficient_history"`, it must first open a minimal model taxonomy amendment; do not silently overload unrelated categories.

## Proposed Evidence Slices

### Slice E1 — Source Capability And Identity Smoke

Purpose：produce a reproducible evidence artifact showing what each candidate source returns for A/C/E/F.

Allowed files：

- Add `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-20260528.md`
- Optional temporary/local one-off commands only; do not commit scripts unless controller explicitly accepts a scripts artifact path.

Actions：

1. Record branch/status and confirm dirty scope before smoke.
2. Run `uv run python` evidence script that calls only public APIs:
   - `ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")`
   - `ak.fund_open_fund_info_em(symbol=code, indicator="累计净值走势")`
   - `ak.fund_open_fund_info_em(symbol=code, indicator="累计收益率走势", period="成立来")`
   - public HTTP GET `https://fund.eastmoney.com/pingzhongdata/{code}.js` for `fS_code` / `fS_name` / variable presence.
3. Matrix codes：`006597`, `006598`, `014217`, `022176`.
4. For JS identity smoke, parse only `fS_code` / `fS_name` values and `Data_netWorthTrend` / `Data_ACWorthTrend` / `Data_grandTotal` variable presence. Do not parse or record numeric content from those JS variables in E1.
5. Record for each call:
   - source function / URL
   - akshare version
   - requested code
   - returned code/name if present
   - indicator / variable name
   - columns
   - row count
   - first / last date
   - sample rows around 2023 E-class distribution window where applicable
   - error and proposed failure category.

Expected result：

- Current Akshare DataFrames likely have no identity columns.
- Eastmoney JS likely has `fS_code` / `fS_name` for each share class.
- Capability exists for candidate cumulative/return series, but adjusted-basis proof remains unresolved until E2.

Stop condition：

- If public APIs are unavailable, classify `unavailable` and produce evidence artifact with commands and failure causes. Do not install new dependencies outside existing project lock.

### Slice E2 — Adjustment Basis Proof

Purpose：decide whether candidate `累计净值走势` or `累计收益率走势` can be accepted as `accumulated_nav`, `dividend_adjusted_nav`, or `total_return`.

Allowed files：

- Update only `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-20260528.md`
- Optionally add a separate proof appendix under `docs/reviews/` if too long.

Actions：

1. Find source-owned semantics for:
   - Eastmoney `Data_ACWorthTrend` / “累计净值走势”
   - Eastmoney `LJSYLZS` / “累计收益率走势”
   - Any provider page text that states dividend/reinvestment handling.
2. Use `FundDocumentRepository` only for official annual report distribution evidence; do not read PDF directly.
3. For E class 014217, identify the exact 2023 distribution event date/range from official disclosure if available through repository text/tables.
4. If official annual report evidence does not disclose an exact E-class ex-dividend date, use a window-based divergence check only when all conditions hold:
   - provider/source semantics primary proof has already passed;
   - the window is traceable to official disclosure or `FundDocumentRepository` evidence, such as the disclosed year/period and share-class distribution amount;
   - raw unit NAV vs candidate accumulated/adjusted/total-return divergence direction and approximate magnitude are consistent with the distribution amount;
   - the evidence artifact records the uncertainty, chosen window, source anchors, expected effect and observed effect.
5. If neither an exact date nor a defensible official window exists, fail closed as `adjustment_basis_unknown` / insufficient evidence; do not accept the candidate by column name, visual similarity or unanchored period selection.
6. Cross-check around the exact date or accepted window:
   - raw unit NAV movement
   - cumulative NAV movement
   - cumulative return movement
   - expected distribution amount effect.
7. Compare year-end or interval values to annual report §3.1 / §3.2 where date windows align.

Accept criteria：

- At least one primary proof and one independent consistency check passes.
- Identity proof for the same code/share class also passes.
- Candidate has sufficient daily/periodic history for future drawdown window; otherwise classify evidence-level `insufficient_history` and map it to current model `insufficient_records` or `missing_date_range`.

Reject criteria：

- Only column names or variable names are available.
- Series semantics are ambiguous or conflict with distribution behavior.
- Source identity cannot be verified for the same response/source.

Output options：

- `accepted-source-basis-candidate`: name exact source, indicator/variable, nav_type, adjusted_basis, dividend_adjustment_status, identity method, limitations, and allowed future adapter slice.
- `partial-acceptance-with-blocked-classes`: at least one share class passes source/basis/identity proof while other classes remain blocked; must cross-reference `share classes covered` and `insufficient classes/windows` in the completion report, and blocker remains unchanged for blocked classes.
- `blocked-with-source-gap`: no acceptable source/basis found; provide next minimal gate.

### Slice E3 — Minimal Adapter / Source-Spike Tests Only If Review Accepts

Purpose：if E1/E2 prove an acceptable source, define the smallest implementation-ready slice for a future gate. This slice should usually be a plan, not production implementation.

Allowed files if controller explicitly allows source-spike tests：

- `tests/fund/data/test_nav_repository_contract.py`
- Possibly `tests/fund/data/test_nav_data.py`
- `docs/reviews/...source-identity-evidence...md`

Not allowed in this gate unless controller changes scope after review：

- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data/nav_repository.py`
- `fund_agent/fund/data/nav_models.py`
- Any extractor / score / quality / golden / snapshot file.

Potential tests to specify for future implementation：

- fake adapter returns verified `fS_code` / `fS_name` and accumulated/total-return rows -> repository emits `identity_status="verified"` and accepted basis only when proof flag/normalizer says so.
- fake adapter with mismatched `fS_code` -> `identity_mismatch`.
- fake adapter with candidate series but missing semantics proof -> `adjustment_basis_unknown`.
- fake adapter with 022176 insufficient lookback -> current model `insufficient_records` or `missing_date_range`; if implementation requires exact `insufficient_history`, stop for model taxonomy amendment first.

## Real Smoke Matrix To Run

Minimum matrix：

| Code | Class | Unit NAV | Accumulated NAV | Cumulative return | JS identity | Distribution cross-check |
|---|---|---|---|---|---|---|
| `006597` | A | required | required | required | `fS_code` / `fS_name` required | optional unless A distribution event found |
| `006598` | C | required | required | required | `fS_code` / `fS_name` required | optional unless C distribution event found |
| `014217` | E | required | required | required | `fS_code` / `fS_name` required | required for 2023 E-class distribution |
| `022176` | F | required | required | required | `fS_code` / `fS_name` required | classify `insufficient_history` if window predates inception |

Feasibility from planning probe：all four codes currently return data for unit NAV / accumulated NAV / cumulative return, and JS identity exists. This is not acceptance; it only means E1 is feasible.

## Allowed Files By Outcome

Evidence-only gate：

- Add/update `docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-evidence-20260528.md`
- Add DS/GLM review artifacts under `docs/reviews/`
- Add controller judgment under `docs/reviews/`
- Optional control-doc update by controller after acceptance, if needed

Future implementation gate only after accepted evidence：

- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/data/nav_repository.py`
- `fund_agent/fund/data/nav_models.py` only if schema amendment is accepted
- `tests/fund/data/test_nav_data.py`
- `tests/fund/data/test_nav_repository_contract.py`
- `fund_agent/fund/README.md`, `tests/README.md`, `docs/design.md` if code behavior changes

Always disallowed in this work unit：

- `reports/extraction-snapshots/**`
- `reports/scoring-runs/**`
- `reports/quality-gate-runs/**`
- golden fixtures
- bond extractor / score / quality gate implementation
- Host/Agent/dayu packages
- release/PR/push/merge state

## Stop Conditions

Stop immediately and return to controller if:

- No primary proof exists for adjustment basis.
- Identity proof is unavailable, incomplete, or mismatched for any target code intended for use.
- A/C/E/F series cannot be kept separate.
- E-class distribution cross-check contradicts candidate adjusted/total-return semantics.
- Evidence requires changing typed model schema before source acceptance.
- Source smoke is unavailable for transient reasons and cannot distinguish `unavailable` from `not_found`.
- Any reviewer asks to implement max drawdown or volatility in this gate.

Terminal outputs：

- `accepted-source-basis-candidate`: only source/basis/identity candidate accepted for a later implementation gate; blocker still remains.
- `partial-acceptance-with-blocked-classes`: only named share classes are accepted as source/basis/identity candidates for a later implementation gate; blocked classes/windows stay fail-closed and must be listed.
- `blocked-with-source-gap`: no acceptable source; next minimal gate is source discovery / provider documentation acquisition.

## Validation Matrix

Evidence-only changes：

- Required:
  - `git branch --show-current`
  - `git status --short`
  - exact source smoke commands recorded in evidence artifact
  - Markdown artifact review for forbidden scope claims
- Not required:
  - `uv run ruff check .`
  - full `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- Rationale：docs/reviews-only evidence does not modify Python, tests, schema, score, quality gate, runtime behavior or production source path.

If tests are added/changed：

- Required:
  - `uv run ruff check tests/fund/data/test_nav_repository_contract.py tests/fund/data/test_nav_data.py`
  - focused pytest for touched tests
- Full ruff / full pytest required if:
  - any production Python changes occur
  - typed model/schema changes occur
  - source adapter or repository behavior changes
  - README/design docs are updated to current implementation facts

If production code changes in a later gate：

- Required:
  - `uv run ruff check .`
  - `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
  - focused real smoke for 006597 / 006598 / 014217 / 022176 through `FundNavRepository.load_nav_series()`
  - explicit assertion that raw unit NAV remains not strong eligible
  - explicit assertion that `drawdown_stress` score/quality blocker is unchanged unless a separate future drawdown metric gate is accepted.

## Review Requirements

Minimum independent reviews before controller acceptance：

- DS plan review
- GLM plan review

Review focus checklist：

- Proof standard is strong enough and does not infer basis from column names.
- A/C/E/F identity rules prevent share-class mixing.
- E-class distribution risk is correctly treated as blocker for raw unit NAV.
- Existing typed contract fields are sufficient or schema amendment is explicitly deferred.
- Failure taxonomy is complete and does not allow fail-closed errors to be hidden by fallback.
- Evidence-only validation matrix is justified.
- No max drawdown / volatility implementation sneaks into this gate.
- No score/snapshot/quality/golden/Host/Agent/dayu/release scope leakage.

If either reviewer finds a blocking issue, planning fix + re-review is required before any evidence slice.

## Completion Report Format

Controller / worker final report should include:

```text
Gate: NAV adjusted-basis source identity gate
Classification: heavy
Role: <planning/evidence/review/controller>, not implementation
Artifacts:
- Plan: docs/reviews/release-maintenance-nav-adjusted-basis-source-identity-plan-20260528.md
- Evidence: <path or not produced>
- Reviews: <DS path>, <GLM path>
- Judgment: <path if controller>

Decision:
- accepted-source-basis-candidate | partial-acceptance-with-blocked-classes | blocked-with-source-gap | review-fix-needed

Accepted source/basis, if any:
- source:
- exact endpoint/function:
- source identity proof:
- nav_type:
- adjusted_basis:
- dividend_adjustment_status:
- share classes covered:
- insufficient classes/windows:
- evidence-level insufficient_history mapping, if any:

Blocker status:
- drawdown_stress blocker remains unchanged
- raw_unit_nav remains not strong evidence
- score/snapshot/quality/golden unchanged

Validation:
- commands run:
- commands intentionally not run and reason:

Next minimal gate:
- <source adapter normalization implementation plan | source discovery/provider documentation gate | drawdown metric contract gate only after source accepted>
```

## Recommended Next Minimal Gate If Source Gap Remains

If E1/E2 cannot prove source semantics and identity, output `blocked-with-source-gap`.

Next minimal gate：

- `NAV adjusted/total-return provider discovery gate`
- Objective：find a provider or official source that returns daily adjusted NAV / total-return path with source-returned fund code/name/share class and documented dividend handling.
- Non-goal：still no drawdown metric implementation or blocker解除.
