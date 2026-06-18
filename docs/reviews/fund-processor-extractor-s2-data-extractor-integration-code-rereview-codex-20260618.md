# Fund Processor/Extractor S2 DataExtractor Integration — Code Re-review (AgentCodex)

> Date: 2026-06-18
> Role: AgentCodex independent code re-reviewer
> Gate: S2 code re-review gate after code fix
> Verdict: FAIL_NOT_READY

## Scope

- Mode: current changes, targeted S2 code re-review after code fix
- Branch or PR: `post-merge/pr22-origin-main`
- Base: current workspace diff and accepted S2 review/fix artifacts; no PR metadata inspected
- Output file: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-rereview-codex-20260618.md`
- Included scope:
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md`
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md`
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-review-codex-20260618.md`
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-review-mimo-20260618.md`
  - `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-fix-evidence-20260618.md`
  - `fund_agent/fund/data_extractor.py`
  - `tests/fund/test_data_extractor.py`
  - `fund_agent/fund/README.md`
  - `fund_agent/fund/processors/contracts.py`
  - `fund_agent/fund/processors/registry.py`
  - `fund_agent/fund/processors/active_annual.py`
  - `fund_agent/fund/data/nav_data.py`
- Excluded scope:
  - No live/source/PDF/FDR/Docling conversion/provider/LLM/analyze/checklist/golden/readiness/release commands.
  - Unrelated untracked residue was not reviewed or classified.
  - `docs/design.md`, `docs/implementation-control.md`, and `fund_agent/README.md` were checked only for stale S1/S2 statements; they were outside this fix write set and are recorded as residual context, not as the blocking code finding below.
- Parallel review coverage: 无 subagent；main reviewer covered accepted blocking fixes, active identity path, active bundle projection, Fund README sync, focused tests, static checks, forbidden write-set scan, and adversarial failure pass.

## Findings

### 1-未修复-高-repository/report mismatch still mixes request NAV data with report evidence

- **入口/函数**: `FundDataExtractor.extract()` -> `_load_nav_data_or_unavailable()` -> `_extract_active_fund_via_processor()` -> `_active_processor_result_to_bundle()`
- **文件(行号)**: `fund_agent/fund/data_extractor.py:303-312`, `fund_agent/fund/data_extractor.py:357-364`, `fund_agent/fund/data_extractor.py:615-633`, `fund_agent/fund/data/nav_data.py:100-118`, `tests/fund/test_data_extractor.py:879-900`
- **输入场景**: `repository.load_annual_report("999999", 2024)` 因 cache/source/repository bug 返回 `ParsedAnnualReport.key.fund_code="110011"` 的 active fund 年报；当前 fix test `test_active_fund_bundle_uses_report_identity_not_request_identity` 正是这个场景。
- **实际分支**: `extract()` 先用外层请求 `fund_code` 调用 NAV provider，再用 repository 返回的 `report.key.fund_code` 构造 active processor dispatch key；processor result identity 校验只校验 result 对 dispatch/report 一致；bundle 顶层身份使用 result/report identity，但 `nav_data` 原样保留请求 fund_code 的 NAV result。
- **预期行为**: blocking identity drift 应完整关闭：同一个 `StructuredFundDataBundle` 不应同时包含 A 基金的 NAV data 和 B 基金的年报/processor evidence。repository/report identity mismatch 应 fail-closed，或至少在加载 NAV 前统一使用已加载 report identity，并有测试证明 bundle 内部身份一致。
- **实际行为**: 当前实现不验证请求 identity 与 repository 返回 report identity；在测试中的 mismatch 场景下，`bundle.fund_code == "110011"`，但 `bundle.nav_data.fund_code == "999999"`。测试只断言顶层 identity 和 processor marker 字段，没有断言 NAV identity，也没有 fail-closed。
- **直接证据**: `extract()` 在加载 report 后仍把外层 `fund_code` 传入 `_load_nav_data_or_unavailable()`（`data_extractor.py:303-312`）；active dispatch 使用 `report.key.fund_code`（`data_extractor.py:357-364`）；bundle 写入 `fund_code=result.fund_code` 且 `nav_data=nav_data`（`data_extractor.py:615-633`）；`NavDataResult` 自带 `fund_code` 字段（`nav_data.py:100-118`）；新增 repository mismatch test 用请求 `"999999"` 调用并只断言 bundle 顶层为 `"110011"`（`test_data_extractor.py:879-900`）。
- **影响**: 错误状态 / 静默失效。上游看到的 bundle 顶层和年报字段属于 `110011`，但 NAV 数据属于请求 `999999`；后续 R=A+B-C、净值展示、章节事实投影或人工复核可能把跨基金 NAV data 当成同源事实。该问题与本 gate 要关闭的 identity drift 属于同一数据路径，不能用 processor result identity 校验单独覆盖。
- **建议改法和验证点**: 在 `extract()` 加载 report 后显式校验 `report.key.fund_code/report.key.year` 与请求 `fund_code/report_year` 一致；不一致时 fail-closed（建议 typed identity mismatch error），并确保 NAV provider 不被调用。若 controller 选择允许 repository 返回 canonical report identity，则 NAV provider 必须使用 `report.key.fund_code/report.key.year` 派生的同源 identity，并新增测试断言 `bundle.nav_data.fund_code == bundle.fund_code`。推荐优先 fail-closed，因为 source identity mismatch 已是仓库边界的高风险类别。
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

## Accepted Finding Verification

- Blocking identity drift: 未完全关闭。Processor result identity 已校验到 dispatch/report，bundle 顶层 identity 不再使用请求参数；但 repository/report mismatch 场景仍混入请求 fund_code 的 NAV data，且新增测试未覆盖该内部身份一致性。
- Blocking Fund README stale: 已关闭。`fund_agent/fund/README.md:77` 与 `fund_agent/fund/README.md:111` 已反映 S2 active fund processor facade 行为和 non-active direct residual。
- Nonblocking core_risk fallback condition: 已加强。`risk_characteristic_text.extraction_mode == "missing"` 与 `value is None` 均被检查。
- ExtractedField[Any] type erasure: 仍为 nonblocking residual；本轮未发现运行时 bug。
- New blocking bug / boundary violation / forbidden write-set expansion: 未发现 forbidden write-set expansion；tracked modified files 为 `fund_agent/fund/README.md`、`fund_agent/fund/data_extractor.py`、`tests/fund/test_data_extractor.py`。未发现 Service/UI/Host/renderer/quality gate 直接消费 candidate/parser internals。发现上方 identity/NAV 同源性 blocking defect。

## Open Questions

- 无。

## Residual Risk

- Tests pass, but current identity mismatch test proves only top-level report identity replacement, not bundle-wide identity consistency or fail-closed behavior.
- `fund_agent/README.md:35`、`docs/design.md:5` / `docs/design.md:672`、`docs/implementation-control.md:9` / `docs/implementation-control.md:40` still contain S1-era "尚未接入 FundDataExtractor.extract()" statements. These files were outside the current fix write set; controller should decide whether they are handled in the next control/doc sync gate.
- Non-active processors remain unimplemented and direct legacy path remains active for index/enhanced/bond/QDII/FOF/unclassified funds.
- `index_profile` still comes from bootstrap `extract_profile()` for active funds, as accepted S2 residual.
- Active path still duplicates in-memory `extract_profile()` for classification and processor extraction, as accepted S2 residual.
- `_field_from_family()` still returns `ExtractedField[Any]`; retained as nonblocking residual.

## Commands Inspected/Run

```text
git branch --show-current
git status --short
sed -n '1,520p' /Users/maomao/.codex/skills/deepreview/SKILL.md
rg -n "Fund Processor/Extractor|S2 DataExtractor|docling-architecture|Processor/Extractor|2026-06-18" /Users/maomao/.codex/memories/MEMORY.md
sed -n '108,136p' /Users/maomao/.codex/memories/MEMORY.md
sed -n '1,240p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md
sed -n '1,260p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-implementation-evidence-20260618.md
sed -n '1,260p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-review-codex-20260618.md
sed -n '1,260p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-review-mimo-20260618.md
sed -n '1,260p' docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-fix-evidence-20260618.md
git diff -- fund_agent/fund/data_extractor.py
git diff -- tests/fund/test_data_extractor.py
git diff -- fund_agent/fund/README.md
nl -ba fund_agent/fund/data_extractor.py | sed -n '1,760p'
nl -ba tests/fund/test_data_extractor.py | sed -n '1,980p'
nl -ba fund_agent/fund/README.md | sed -n '1,180p'
nl -ba fund_agent/fund/processors/contracts.py | sed -n '1,260p'
nl -ba fund_agent/fund/processors/registry.py | sed -n '1,220p'
nl -ba fund_agent/fund/processors/active_annual.py | sed -n '1,340p'
nl -ba fund_agent/fund/data/nav_data.py | sed -n '1,120p'
rg -n "FundDataExtractor\\.extract\\(\\).*not connected|尚未接入|processor 尚未接入|FundProcessorRegistry|ActiveFundAnnualProcessor|默认生产 facade" README.md fund_agent/README.md fund_agent/fund/README.md docs/design.md docs/implementation-control.md
rg -n "extra_payload|FundDisclosureDocument|docling|Docling|candidate|pdfplumber|EID|service|host|renderer|quality" fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
uv run pytest tests/fund/processors/test_registry.py tests/fund/processors/test_active_annual_processor.py tests/fund/test_data_extractor.py
uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
git diff --check -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md docs/reviews/fund-processor-extractor-s2-data-extractor-integration-code-fix-evidence-20260618.md
git diff --name-only -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/documents/candidates fund_agent/service fund_agent/host fund_agent/agent fund_agent/render fund_agent/quality
git diff --cached --name-only
git diff --stat -- fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/README.md
date +%Y%m%d-%H%M%S
```

Observed verification:

```text
uv run pytest ... -> 30 passed in 0.56s
uv run ruff check ... -> All checks passed!
git diff --check ... -> no output
git diff --cached --name-only -> no output
target write-set name-only scan -> fund_agent/fund/README.md, fund_agent/fund/data_extractor.py, tests/fund/test_data_extractor.py
```
