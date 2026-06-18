# Fund Processor/Extractor S2 DataExtractor Integration — Aggregate Deepreview (AgentDS)

> Date: 2026-06-18
> Role: AgentDS independent aggregate deepreview reviewer
> Work unit: Fund Processor/Extractor S2 DataExtractor Integration
> Gate: Fund Processor/Extractor S2 Aggregate Deepreview Gate
> Classification: standard aggregate review
> Review target: commit `02b9ca9`, accepted S2 artifacts, key source files as specified in gate scope
> Base: `post-merge/pr22-origin-main`

## Verdict

**PASS_NOT_READY**

The S2 implementation slice correctly integrates `ActiveFundAnnualProcessor` into `FundDataExtractor.extract()` default production facade through `FundProcessorRegistry`. All seven mandatory verification questions pass with direct code evidence. Two known S1 wording residuals exist in `docs/design.md` and `fund_agent/README.md` — already accepted by prior controller judgment for next truth-sync/bookkeeping gate. No blocking issues found. Release/readiness remains `NOT_READY`.

## Scope

- Mode: aggregate deepreview (single accepted commit slice)
- Branch: `post-merge/pr22-origin-main`
- Commit reviewed: `02b9ca9` (range `02b9ca9^..02b9ca9`)
- Included scope:
  - `fund_agent/fund/data_extractor.py` — production implementation
  - `tests/fund/test_data_extractor.py` — focused tests
  - `fund_agent/fund/README.md` — S2 behavior documentation
  - `fund_agent/fund/processors/contracts.py` — contract definitions (S1, consumed by S2)
  - `fund_agent/fund/processors/registry.py` — processor registry (S1, consumed by S2)
  - `fund_agent/fund/processors/active_annual.py` — active fund processor (S1, consumed by S2)
  - All accepted S2 plan/review/fix artifacts under `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-*20260618.md`
  - `docs/design.md` (relevant Processor/Extractor sections, line 5)
  - `fund_agent/README.md` (relevant boundary sections, line 35)
- Excluded scope:
  - `docs/implementation-control.md` / `docs/current-startup-packet.md` (control docs, not reviewed as code)
  - Untracked residue under `docs/`, `.mimocode/` (not in scope per gate instructions)
  - Candidate harness (`fund_agent/fund/documents/candidates/`)
  - Service/Host/Agent/UI/renderer/quality gate source files (not in S2 write set)
  - PDF/cache/source helper internals
- Parallel review coverage: none (single reviewer)

## Mandatory Verification Questions

### Q1: active_fund annual ParsedAnnualReport 默认 facade 是否真实通过 FundProcessorRegistry / ActiveFundAnnualProcessor 投影 StructuredFundDataBundle

**PASS.** Direct code evidence:

1. **Entry point** — `data_extractor.py:319-330`: `classified_fund_type == "active_fund"` dispatches to `_extract_active_fund_via_processor()`.

2. **Registry resolution** — `data_extractor.py:362-370`: constructs `FundProcessorDispatchKey(fund_type="active_fund", report_type="annual_report", intermediate_kind="parsed_annual_report.v1", source_kind="annual_report", ...)`, calls `self._processor_registry.resolve(dispatch_key)`.

3. **Processor invocation** — `data_extractor.py:372-377`: constructs `FundProcessorInput`, calls `processor.extract(processor_input)`.

4. **Bundle projection** — `data_extractor.py:400-407`: calls `_active_processor_result_to_bundle()` which maps six field families to `StructuredFundDataBundle` fields via `_field_family_by_id()` and `_field_from_family()`.

5. **Marker proof** — test `test_active_fund_uses_processor_path_with_marker_values` (`test_data_extractor.py:811-845`): injects `_MarkerActiveFundProcessor` that returns known marker values; verifies all 14 bundle fields carry marker values (e.g., `"product_profile_from_processor"`, `"fee_from_processor"`) rather than direct extractor results.

6. **Default registry** — `registry.py:129-147`: `FundProcessorRegistry.create_default()` registers `ActiveFundAnnualProcessor`; `data_extractor.py:278` defaults to this when no custom registry is injected.

### Q2: repository report identity mismatch 是否在 NAV load 和 processor dispatch 前 fail-closed

**PASS.** Direct code evidence:

1. **Identity gate** — `data_extractor.py:303-312`: immediately after `load_annual_report()` and before `_load_nav_data_or_unavailable()`, checks `report.key.fund_code != fund_code or report.key.year != report_year`, raises `RuntimeError("Report identity mismatch: …")`.

2. **NAV isolation** — test `test_data_extractor_rejects_report_identity_mismatch_before_nav` (`test_data_extractor.py:879-900`): repository returns report with `fund_code="110011"` but request is `"999999"`; verifies `RuntimeError` raised with `"Report identity mismatch"` and `nav_provider.calls == []`.

3. **Repository failure propagation** — existing test `test_data_extractor_does_not_mask_repository_failure` (`test_data_extractor.py:248-270`): repository raises `RuntimeError` before any NAV provider call; `nav_provider.calls == []`.

### Q3: processor result identity mismatch、unsupported/blocked 是否 fail-closed，且不 fallback 到 direct extractor

**PASS.** Three-layer fail-closed defense:

1. **Registry resolution failure** — `registry.py:102-127`: `resolve()` raises `UnsupportedFundProcessorError` when no registered processor supports the dispatch key. `data_extractor.py:370`: no try/except around this call — exception propagates up. Test: `test_active_fund_unsupported_registry_fails_closed` (`test_data_extractor.py:847-860`).

2. **Processor contract status** — `data_extractor.py:378-382`: if `result.contract_status in ("unsupported", "blocked")`, raises `RuntimeError` with processor_id and gaps. No fallback to direct path.

3. **Processor result identity validation** — `data_extractor.py:511-554`: `_validate_processor_result_identity()` checks five fields (`fund_code`, `report_year`, `fund_type`, `report_type`, `input_intermediate_kind`) against dispatch key; any mismatch raises `RuntimeError`. Test: `test_active_fund_processor_mismatched_identity_fails_closed` (`test_data_extractor.py:863-876`), `_MismatchedIdentityProcessor` returns `fund_code="999999"`.

4. **Unexpected processor exception** — per accepted S2 plan, `processor.extract()` unexpected exceptions propagate naturally (no try/except wrapping); never silently swallowed, never fallback to direct active-fund path.

### Q4: non-active/unclassified direct legacy residual 是否保持，不被 active processor 误覆盖

**PASS.** Direct code evidence:

1. **Dispatch gate** — `data_extractor.py:319-331`: only `classified_fund_type == "active_fund"` enters processor path; the `else` branch calls `_extract_bundle_direct_legacy_path()`.

2. **Classified fund type scope** — `data_extractor.py:731-756`: `_classified_fund_type()` only returns known FundType values; `index_fund`, `enhanced_index`, `bond_fund`, `qdii_fund`, `fof_fund`, and `None` (unclassified) all fall through to the direct legacy path.

3. **Direct legacy path** — `data_extractor.py:410-468`: `_extract_bundle_direct_legacy_path()` preserves exact pre-S2 behavior: `extract_performance()` → `extract_manager_ownership()` → `extract_holdings_share_change()` → drawdown → bond_risk_evidence → `StructuredFundDataBundle`.

4. **Verification** — test `test_index_fund_direct_path_smoke_test` (`test_data_extractor.py:903-917`): index fund report with `classified_fund_type="index_fund"` returns bundle via direct path, `bundle.tracking_error.extraction_mode == "missing"`.

### Q5: AGENTS 边界违规检查

**PASS — no violations found.**

| Rule | Check | Result |
|------|-------|--------|
| 不得直接消费 Docling/raw full JSON/EID HTML/pdfplumber source truth | `grep -rn 'docling\|pdfplumber\|eid_xbrl_html\|candidates' fund_agent/fund/data_extractor.py` | No matches |
| 不得绕过 FundDocumentRepository | `data_extractor.py:303` loads via `self._repository.load_annual_report()` | PASS |
| 不得 Service/UI/Host/renderer/quality gate 直接 parser 调用 | `grep -rn 'import.*extract_profile\|extract_performance\|extract_manager' fund_agent/services/` | No direct narrow extractor imports in Service |
| 不得 extra_payload 参数 | `grep -rn extra_payload fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py fund_agent/fund/processors/` | No matches (exit 1) |
| 不得 readiness/release/parser replacement/source truth claim | `grep -rn 'readiness\|release\|source.truth\|parser.replacement' fund_agent/fund/data_extractor.py` — no matches. Active processor docstring explicitly disclaims these. | PASS |
| Constructor 不得访问 I/O | `data_extractor.py:253-278`: constructor only stores injected dependencies; no I/O | PASS |
| candidate_boundary 不得写成 production proof | `data_extractor.py:376`: passes `candidate_boundary=None` in processor input; bundle projection never accesses candidate status | PASS |
| 不得跨层 import (data_extractor → Service/Host/UI) | `grep -rn 'import.*Service\|import.*Host\|import.*renderer\|import.*quality' fund_agent/fund/data_extractor.py` | No matches |

### Q6: tests 是否覆盖关键 failure path 和 regression surface

**PASS.** 30 tests, all passing, covering:

**Failure paths (8 tests):**
- `test_data_extractor_degrades_nav_failure_without_blocking_annual_report` — NAV external failure → `nav_unavailable`, bundle still produced
- `test_data_extractor_does_not_mask_repository_failure` — repository exception propagates, NAV never called
- `test_data_extractor_rejects_report_identity_mismatch_before_nav` — report identity mismatch before NAV call
- `test_active_fund_unsupported_registry_fails_closed` — `UnsupportedFundProcessorError` propagates
- `test_active_fund_processor_mismatched_identity_fails_closed` — processor identity mismatch fail-closed
- `test_data_extractor_raw_unit_nav_error_keeps_drawdown_weak` — bond drawdown NAV error → weak evidence
- `test_data_extractor_projects_fallback_metadata_as_unknown_when_category_absent` — missing failure category → unknown
- Repository failure propagation preserved from S1 (existing tests)

**Regression surface (5 tests):**
- `test_active_fund_uses_processor_path_with_marker_values` — 14 marker field assertions prove processor path
- `test_index_fund_direct_path_smoke_test` — non-active fund behavior preserved
- `test_data_extractor_non_bond_bond_risk_evidence_does_not_scan_groups` — non-bond early exit preserved
- `test_data_extractor_bond_fund_uses_a_share_nav_metric_without_mixing_classes` — bond drawdown typed NAV preserved
- 3 source provenance tests — provenance projection preserved

**Edge cases (3 tests):**
- `test_structured_bundle_default_source_provenance_is_not_none` — default provenance safety
- `test_data_extractor_returns_bundle_with_bond_risk_evidence` — portfolio_managers + risk_characteristic_text projection
- Active fund bond_risk_evidence returns `not_applicable_non_bond_fund` (embedded in existing tests)

**Processor contract tests (9 tests):** covering registry resolution, dispatch key validation, field family output, mapping coverage, gap attribution, provenance projection, candidate-free claims, source boundary isolation, and fail-closed semantics.

### Q7: 控制文档和 artifact 是否足以进入 accepted deepreview commit

**PASS — with documented residuals.**

Accepted S2 artifacts form a complete evidence chain:
1. Plan → DS/MiMo reviews → plan fix → DS/MiMo re-reviews → controller judgment (`ACCEPT_PLAN_READY_FOR_IMPLEMENTATION_GATE_NOT_READY`)
2. Implementation evidence → MiMo/Codex code reviews → code fix → Codex re-review → code fix2 → Codex re-review2 → controller judgment (`ACCEPT_IMPLEMENTATION_READY_FOR_AGGREGATE_DEEPREVIEW_NOT_READY`)
3. Committed slice `02b9ca9` contains all 13 changed files as documented

**Known S1 wording residuals** (already accepted by controller judgment for next truth-sync/bookkeeping gate):
- `docs/design.md:5` — still states S1 processor "尚未接入 `FundDataExtractor.extract()` 默认生产 facade"
- `fund_agent/README.md:35` — same S1-era wording residual

These residuals are non-blocking: the `fund_agent/fund/README.md` (package-level documentation) and the code itself already reflect S2 reality. The controller judgment explicitly routed these to "next truth-sync/bookkeeping gate."

## Findings

未发现实质性问题。

所有 7 项强制验证问题均 PASS，Mandatory 检查未发现阻塞性缺陷。30 项聚焦测试全部通过，ruff 静态分析通过，`git diff --check` 无空白错误。S2 实现严格遵守 accepted plan 和 AGENTS 边界约束。

### Nonblocking Observation: S1 wording residuals in design.md and top-level README

- **入口/文件**: `docs/design.md:5`, `fund_agent/README.md:35`
- **输入场景**: 阅读设计文档或顶层开发手册时
- **实际分支**: 文档仍写 S1 processor "尚未接入 `FundDataExtractor.extract()` 默认生产 facade"
- **预期行为**: 应反映 S2 已接入的事实
- **实际行为**: 描述落后于代码实际状态一个 slice
- **直接证据**: `docs/design.md:5` — "尚未接入 `FundDataExtractor.extract()` 默认生产 facade"; `fund_agent/README.md:35` — 同上
- **影响**: 误导首次阅读文档的开发者，使其认为 processor path 尚未集成到生产 facade。不影响运行时正确性。
- **建议改法和验证点**: 在下次 truth-sync/bookkeeping gate 中更新两处文档，移除 "尚未接入" 表述。当前 code review controller judgment 已将此残差路由至 next truth-sync/bookkeeping gate。
- **修复风险**: 低 — 纯文档更新，不改变代码行为
- **严重程度**: 低 — 已知残差，已由 controller judgment disposition，不阻塞当前 gate

## Open Questions

无。

## Residual Risk

| Residual | Severity | Owner | Mitigation |
|---|---|---|---|
| `docs/design.md` / `fund_agent/README.md` S1 wording residual | 低 | Controller / truth-sync owner | Next truth-sync/bookkeeping gate |
| Non-active fund processors 未实现 (index, enhanced_index, bond, QDII, FOF) | 中 | Future Fund Processor owner | Separate processor implementation gates per fund type |
| `index_profile` 仍来自 bootstrap `extract_profile()` | 低 | S3 planning owner | Future field-family coverage / precomputed extraction context gate |
| Active path 存在临时 in-memory `extract_profile()` 重复 | 极低 | S3 gate owner | 仅 memory 重复，无 I/O 重复；S3 消除 |
| `current_stage.v1` 和 `core_risk.v1` 的非 fallback 字段不进入 bundle projection | 低 | Future extraction contract owner | 已显式 marked informational/redundant |
| `_field_from_family()` 使用 `ExtractedField[Any]` 类型擦除 | 极低 | Future typing hardening owner | 运行时正确性由 processor output schema 保证 |
| Field-level anchors 保持 family-level | 低 | Future extraction contract owner | 后续可按需细化 field-level anchor 分配 |
| Candidate intermediates 仍未授权进入生产 facade | — | Fund documents / processor owner | 仍为 NOT_READY；candidate boundary 明确 |
| 5 种非 active 基金类型仅 index_fund 有 smoke test | 低 | Future test owner | 代码路径完全不变（封装为命名 helper），风险极低 |

Release/readiness remains **NOT_READY**.

## Coverage / Commands Run

```
uv run pytest tests/fund/processors/test_registry.py \
  tests/fund/processors/test_active_annual_processor.py \
  tests/fund/test_data_extractor.py -v
# 30 passed in 0.69s

uv run ruff check fund_agent/fund/data_extractor.py tests/fund/test_data_extractor.py
# All checks passed!

git diff --check 02b9ca9^..02b9ca9
# (no output — no whitespace errors)

git show 02b9ca9 --stat
# 13 files changed, 1662 insertions(+), 48 deletions(-)
```

Full adversarial boundary pass executed:
- Docling/pdfplumber/EID HTML/candidate import check: **clean**
- extra_payload check: **clean**
- Cross-layer import check (data_extractor → Service/Host/UI): **clean**
- Direct narrow extractor import check in Service: **clean** (uses `_FundDataExtractor` Protocol only)
- Readiness/release/source truth/parser replacement claim check: **clean**
- Identity mismatch before NAV: **verified** (direct code evidence + test)
- Processor identity validation: **verified** (5-field check + test)
- Unsupported/blocked fail-closed: **verified** (3-layer defense + tests)
