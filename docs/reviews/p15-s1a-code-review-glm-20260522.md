# P15-S1A Tracking Error Evidence Acquisition — GLM Code Review（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Artifact 结论 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` 与证据库存一致，分类正确，scope 严格控制在 artifact-only implementation。所有 12 个 candidate 均被正确拒绝，golden decision `do_not_edit_golden` 符合 source contract 和 stop conditions。存在 2 个 LOW 和 2 个 INFO 级 finding，无阻断项。

## Inputs

- Implementation artifact: `docs/reviews/p15-s1a-tracking-error-evidence-acquisition-implementation-20260522.md`
- Plan: `docs/reviews/p15-s1a-tracking-error-source-contract-evidence-acquisition-plan-20260522.md`
- Plan controller judgment: `docs/reviews/p15-s1a-plan-review-controller-judgment-20260522.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Key source files reviewed: `fund_agent/fund/extractors/performance.py`, `fund_agent/fund/extractors/models.py`, `fund_agent/fund/data_extractor.py`, `fund_agent/fund/documents/repository.py`, `fund_agent/fund/documents/models.py`

## Source Contract Compliance

| Requirement | Status | Evidence |
|---|---|---|
| Access through `FundDocumentRepository` / `FundDataExtractor` | ✅ pass | Artifact 记录 `FundDocumentRepository.load_annual_report("001548", 2024)` 和 `FundDataExtractor.extract("001548", 2024)` |
| Identity check (fund_code, year, document_kind) | ✅ pass | `DocumentKey(fund_code="001548", year=2024, document_kind="annual_report")` |
| `source_type="direct_disclosure"` required for acceptance | ✅ pass | 无 accepted evidence；structured decision 返回 `extraction_mode="missing"` |
| Complete anchor required for acceptance | ✅ pass | 无 accepted evidence；所有 candidate 的 anchor 均标注为 target/limit 或 narrative |
| Golden sequencing enforced | ✅ pass | Golden decision 为 `do_not_edit_golden` |
| Stop conditions met | ✅ pass | 只发现 target/limit 和 narrative；无直接披露值 |

## AGENTS.md Compliance

| Rule | Status | Evidence |
|---|---|---|
| `FundDocumentRepository` / `FundDataExtractor` 边界 | ✅ pass | 未直接访问 PDF cache、下载 helper 或 source adapter |
| 证据可溯源 | ✅ pass | 每个 candidate 有年报章节 + 行号 + 原文短摘 |
| 第一性原理 | ✅ pass | 未从 benchmark、标准差或 NAV/index series 推导 tracking error |
| 显式参数 | ✅ pass | `fund_code="001548"`、`report_year=2024`、`force_refresh=False` 显式记录 |
| 禁止间接证据 | ✅ pass | target/limit 和 narrative 均被拒绝 |

## Candidate Classification Review

12 个 candidate 全部审查：

| # | Location | Excerpt | Artifact classification | Reviewer assessment |
|---|---|---|---|---|
| 1 | §2 line 33 | "偏离度和跟踪误差的最小化。" | investment-objective target/limit | ✅ correct：上下文为投资目标段落 |
| 2 | §2 line 56 | "紧密跟踪标的指数，追求跟踪偏离度和跟踪误差的最" | investment-objective target/limit | ✅ correct：目标陈述 |
| 3 | §2 line 57 | "投资目标 小化，本基金力争将日均跟踪偏离度控制在0.2%以" | investment-objective target/limit | ✅ correct：`0.2%` 是日偏离度控制目标 |
| 4 | §2 line 58 | "内，年化跟踪误差控制在2%以内。" | investment-objective target/limit | ✅ correct：`2%` 是年化跟踪误差控制上限 |
| 5 | §4 line 87 | "相关和跟踪误差最小化。" | manager narrative | ✅ correct：策略叙述 |
| 6 | §4 line 88 | "出于基金充分投资、减少交易成本、降低跟踪误差的需要" | manager narrative | ✅ correct：风险管理叙述 |
| 7 | §4 line 92 | "控制联接基金跟踪误差的前提是控制ETF基金的跟踪误差" | manager narrative | ✅ correct：控制前提讨论 |
| 8 | §4 line 93 | "误差的来源主要是申购赎回、打新、成分股调整" | manager narrative | ✅ correct：误差来源描述 |
| 9 | §4 line 95 | "基金采取被动复制与组合优化相结合的方式跟踪指数" | manager narrative | ✅ correct：管理方法讨论 |
| 10 | §4 line 97 | "造成跟踪误差的扩大，争取保障联接基金的跟踪效果。" | manager narrative | ✅ correct：管理讨论 |
| 11 | §5 line 1407 | "追求跟踪偏离度和跟踪误差最小化" | investment-objective target/limit | ✅ correct：目标/风控框架 |
| 12 | page 6 table 1 header | "日均跟踪偏离度控制在0.2%以内，年化跟踪误差控制在2%以内" | investment-objective target/limit | ✅ correct：表格标题中的目标限制 |

分类汇总验证：

| Class | Artifact count | Reviewer count | Match |
|---|---:|---:|---|
| investment-objective target/limit | 6 | 6 | ✅ |
| manager narrative | 6 | 6 | ✅ |
| direct observed disclosure | 0 | 0 | ✅ |
| benchmark-only | 0 | 0 | ✅ |
| standard-deviation-only | 0 | 0 | ✅ |

## Misclassification Risk Assessment

| Risk vector | Status | Evidence |
|---|---|---|
| investment-objective target/limit 被误当 observed value | ✅ 无风险 | `0.2%` 和 `2%` 均被正确识别为目标/限制 |
| manager narrative 被误当数值披露 | ✅ 无风险 | 6 条 narrative 均无具体数值 |
| benchmark-only 被误当 tracking_error | ✅ 无风险 | benchmark 上下文仅用于 `index_profile` |
| standard deviation 被误当 tracking error | ✅ 无风险 | 无标准差列命中 |
| ambiguous hit 被误当 direct disclosure | ✅ 无风险 | `_has_ambiguous_tracking_error_text` 正确触发 early-return（`performance.py:357-358`），extractor 返回 `missing` |

## Provenance Assessment

| Field | Artifact claim | Code cross-reference | Assessment |
|---|---|---|---|
| `source_metadata=None` | parsed-cache hit 无 source metadata | `repository.py:323-334`：正常 cache hit 会从 `cached_report.metadata.source` 恢复；`None` 仅在 cache 由旧版代码写入时出现 | ⚠️ F1：可能来自旧版 cache，但 artifact 未建议补救 |
| `parsed_cache_hit=True` | 命中 parsed report JSON 缓存 | `models.py:135`：`AnnualReportCacheProvenance` 记录此字段 | ✅ consistent |
| `pdf_cache_hit=False` | 未命中 PDF 文件缓存 | 同上 | ✅ consistent |
| `cache_schema_version=1` | 当前 schema 版本 | `cache.py` 的 `PARSED_REPORT_SCHEMA_VERSION` | ✅ consistent |

## Structured Extraction Decision Cross-Check

| Artifact claim | Code verification |
|---|---|
| `extraction_mode="missing"` | `performance.py:750-756`：`_missing_tracking_error()` 构造 `extraction_mode="missing"` ✅ |
| `note="tracking_error_ambiguous"` | `performance.py:357-358`：`_has_ambiguous_tracking_error_text()` 返回 `True` 时使用此 note ✅ |
| `value=None`, `anchors=()` | `performance.py:751-752`：`_missing_tracking_error()` 固定返回 `value=None, anchors=()` ✅ |
| fund type `index_fund` | `data_extractor.py:224-249`：`index_fund` 不会 override tracking_error 为不适用 ✅ |

Early-return 路径 `performance.py:357-358` 在 `_has_ambiguous_tracking_error_text` 返回 `True` 时跳过了后续 table/text 搜索。对 `001548` 而言这是正确的——inventory 证明 §3 无 tracking error 表格——但此 early-return 可能在其他基金上跳过有效 §3 表格披露（见 F4）。

## Validation Assessment

| Command | Artifact claim | Scope proportionality |
|---|---|---|
| Repository + extractor inline commands | Passed | ✅ artifact-only scope 不需要新测试文件 |
| `test_performance.py` | 14 passed | ✅ 已覆盖 direct disclosure、target-only、ambiguous、standard deviation、table/text consistency |

Validation 与 artifact-only implementation scope 相称。Plan 要求的 full keyword inventory 通过 inline Python 完成，未引入永久 helper 模块。

## Scope Boundary Check

| Area | Artifact claim | Reviewer verification |
|---|---|---|
| No source code changed | ✅ stated | Scope Self-Check section 确认；无 file ownership 变更 |
| No tests changed | ✅ stated | 同上 |
| No golden/CSV edits | ✅ stated | Golden decision `do_not_edit_golden` |
| No Dayu/LLM/runtime | ✅ stated | 同上 |
| No excluded files referenced | ✅ stated | 明确排除 `design0522.md`、`implementation-control0522.md`、`repo-audit-20260521.md` |

## Findings

### F1 — LOW: provenance gap 未建议补救路径

**Location**: Implementation artifact → Repository Provenance section

**问题**: Artifact 记录 `source_metadata=None`，表示 parsed cache 未保留原始来源元数据。Artifact 正确承认此限制并拒绝推断 source URL/fallback status，但未建议后续补救操作（如 `force_refresh=True` 以重新获取 source metadata）。

**Code 交叉验证**: `repository.py:323-334` 显示正常 cache hit 应从 `cached_report.metadata.source` 恢复 metadata。`None` 仅在旧版代码写入的 cache 中出现。Plan step 2 要求记录 "source URL/报告名称等可用 provenance"，但 `force_refresh=False` 的默认设置使得 provenance 可能永远不完整。

**影响**: 不影响本次 evidence classification（所有 candidate 无论来源如何均为 target/limit 或 narrative）。但若未来需要重新审查此基金或验证来源身份，缺少 source metadata 是一个 residual risk。

**建议**: Artifact 应在 residual 部分显式建议：若后续需要 retry `001548` evidence acquisition，应使用 `force_refresh=True` 确保 source metadata 完整。

---

### F2 — LOW: `跟踪偏离度` 与 `跟踪误差` 上下文判断未显式记录

**Location**: Implementation artifact → Candidate Classification, candidates 2-3

**问题**: Plan controller judgment GLM F3 明确要求 "Artifact must record context judgment for any `跟踪偏离度` hit and must not treat daily deviation as observed tracking error without direct support"。Artifact 的 candidate 2-3 提及 "跟踪偏离度"（日偏离度），分类为 investment-objective target/limit，分类本身正确。但 artifact 未显式记录 `跟踪偏离度`（tracking deviation）与 `跟踪误差`（tracking error）是不同指标这一上下文判断。

**Code 交叉验证**: `performance.py:517-542` 中 `_has_ambiguous_tracking_error_text` 扫描 `§3` 和 `§2`，使用 `_TRACKING_ERROR_KEYWORDS` 同时覆盖两种术语，未在代码层面区分日偏离度和年化跟踪误差。

**影响**: 不影响结论——所有 `跟踪偏离度` 命中均为目标控制文本而非观测值。但显式记录此判断可加强 rejection 的说服力，并满足 plan controller 的明确要求。

**建议**: 在 candidate 2-3 的 Reason 列补充说明 "跟踪偏离度（tracking deviation）与跟踪误差（tracking error）为不同指标；此处为日偏离度目标，非年化跟踪误差观测值"。

---

### F3 — INFO: 分类逻辑无独立测试模块

**Location**: Implementation artifact → Validation section

**说明**: Plan 要求 "tests prove target/limit, benchmark-only, narrative-only, standard deviation, ambiguous and unparseable cases cannot become accepted direct disclosure"。Artifact 通过 inline Python 命令和现有 `test_performance.py`（14 passed）覆盖分类逻辑，但未新建独立测试模块。这符合 plan "one-off helper/test" 范围，且现有测试已覆盖 direct disclosure、target-only、ambiguous、standard deviation 和 table/text consistency 行为。

**建议**: 无需行动。若后续 gate 需要 `001548` 的持久化 evidence helper，可在那时引入独立测试。

---

### F4 — INFO: `_has_ambiguous_tracking_error_text` early-return 对 `001548` 正确但语义较重

**Location**: `fund_agent/fund/extractors/performance.py:357-358`

**说明**: Extractor 在 `_has_ambiguous_tracking_error_text` 返回 `True` 时立即返回 `missing`，跳过后续 table/text 搜索。对 `001548` 而言这是正确的——inventory 证明 §3 无 tracking error 表格，early-return 不影响结果。但此 early-return 的语义是"只要 §2 或 §3 存在实际值信号与目标控制语言混杂，就拒绝整个 tracking_error 抽取"，可能在其他基金上跳过有效的 §3 表格直接披露。

**影响**: 不影响 `001548` 结论。记录为 future extractor 改进候选：若未来发现某基金 §2 有混杂文本但 §3 表格有独立明确披露，应评估是否收紧 early-return scope。

**建议**: 作为 future residual 记录，不在本 gate 修复。

## Scope Compliance Summary

- ✅ 无 source code 变更
- ✅ 无 test 变更
- ✅ 无 README 变更
- ✅ 无 golden answer 或 selected-fund data 变更
- ✅ 无 production `tracking_error` golden rows 添加
- ✅ 无 Dayu Host/Engine/tool loop、external runtime、LLM audit、Evidence Confirm
- ✅ 无 external index adapter、calculated tracking-error path
- ✅ 无 RR-13 或 source CSV 操作
- ✅ 无 excluded local drafts 或 excluded repo-audit artifact 引用
- ✅ 无 commit/push/PR/external comment

## Residual Assessment

Artifact 的 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` 结论正确。以下 residual 与 control truth 一致：

| Residual | Owner | Status |
|---|---|---|
| `001548` production `tracking_error` golden rows | future golden implementation gate | blocked |
| Provenance gap on stale cache | F1 remediation | future retry 应使用 `force_refresh=True` |
| Early-return 语义范围 | future extractor improvement candidate | not blocking |
| Enhanced-index production golden expansion | future selected-fund/golden expansion | deferred |
