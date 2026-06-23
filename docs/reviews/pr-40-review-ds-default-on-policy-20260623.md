# Code Review

## Scope

- **Mode**: PR Review
- **PR**: [#40](https://github.com/bill20232033cc/fund-agent/pull/40) — Add Evidence Confirm productionization and service integration
- **Repository**: bill20232033cc/fund-agent
- **Author**: bill20232033cc
- **Head**: `3c4fe064775a50c5e7b5fec58d5fce8ec03c39f7` (branch `evidence-confirm-productionization`)
- **Base**: `evidence-confirm-anchor-audit-score`
- **CI Status**: `test` workflow **SUCCESS** (completed 2026-06-22T21:12:01Z)
- **Merge State**: `CLEAN`
- **State**: `OPEN`, `DRAFT`
- **Review Date**: 2026-06-23

### Included Scope

Source files reviewed:

| File | Status | Review Depth |
|------|--------|-------------|
| `fund_agent/services/fund_analysis_service.py` | Modified | Full — every changed function and dataclass |
| `fund_agent/ui/cli.py` | Modified | Full — EC parameter wiring, stderr output, block handling |
| `fund_agent/fund/evidence_confirm_runner.py` | New | Full — facade contract |
| `fund_agent/fund/evidence_confirm_production.py` | New | Full — all public and private helpers |
| `fund_agent/fund/evidence_confirm_semantic.py` | New | Full — semantic entailment chain |
| `fund_agent/fund/evidence_confirm_sources.py` | New | Key paths — runner, reference builder, repository boundary |
| `fund_agent/fund/quality_gate.py` | Modified | `merge_quality_gate_issues`, `QualityGateIssue.issue_id` |
| `fund_agent/fund/quality_gate_integration.py` | Modified | Full — ECQ0-ECQ4 projection |
| `tests/services/test_fund_analysis_service.py` | Modified | Full — EC policy matrix, fake runner/QG |
| `tests/ui/test_cli.py` | Modified | Full — EC stderr, product/dev paths |
| `tests/fund/test_evidence_confirm_production.py` | New | Full — summary construction, reason validation |
| `tests/fund/test_quality_gate_integration.py` | Modified | Full — ECQ0-ECQ4 integration matrix |
| `tests/fund/test_evidence_confirm_semantic.py` | New | Key paths — semantic status/severity mapping |
| `README.md` | Modified | Docs sync — EC CLI flag, default behavior |
| `docs/design.md` | Modified | Docs sync — EC default-on, ECQ projection, future boundaries |
| `docs/current-startup-packet.md` | Modified | Control sync — gate state |
| `docs/implementation-control.md` | Modified | Control sync — PR gate state |
| `fund_agent/README.md` | Modified | Docs sync |
| `fund_agent/fund/README.md` | Modified | Docs sync |
| `tests/README.md` | Modified | Docs sync |
| `scripts/evidence_confirm_ec_p2_live_sample.py` | New | Live sample script (not production code) |

### Excluded Scope

- `docs/reviews/` review artifacts (130+ files) — evidence chain only, not production code.
- Local commit `0e2d321` — controller bookkeeping after push/update, not part of PR-40 diff.

### Validation Commands Used

```bash
gh pr view 40 --json number,title,state,isDraft,headRefOid,baseRefName,mergeStateStatus,statusCheckRollup,url,body
gh pr diff 40
gh pr checks 40 --json name,state,bucket,completedAt,startedAt,link
git show --stat 3c4fe064775a50c5e7b5fec58d5fce8ec03c39f7
```

Source diffs extracted via `gh pr diff 40 | sed -n '<line_range>p'` for each target file.

---

## Findings

### PR Body Truthfulness Assessment

逐项核实 PR body 声明与代码diff一致：

| PR Body Claim | Code Evidence | Verdict |
|---|---|---|
| product `analyze` defaults to `warn` | `_resolve_analyze_contract()` product path: `evidence_confirm_policy="warn"` | ✅ 一致 |
| `analyze-annual-period` inherits `warn` via `analyze()` delegation | `analyze_multi_year_annual()` → `self.analyze()` unchanged | ✅ 一致 |
| `checklist` remains EC `off` | `_effective_evidence_confirm_policy()` returns `"off"` for `command_source="checklist"` | ✅ 一致 |
| `--evidence-confirm-policy` only with `--dev-override` | CLI detection in `_has_developer_override_options()`, rejection in `_build_developer_overrides()` | ✅ 一致 |
| plain `--dev-override` keeps EC `off` | `evidence_confirm_policy=overrides.evidence_confirm_policy or "off"` where default is `None` | ✅ 一致 |
| NOT_READY residuals listed (no provider semantic, no checklist EC CLI, no report-body rendering, no multi-sample live proof, no mark-ready/merge) | All confirmed in code and docs | ✅ 一致 |
| No overclaim of release/readiness | All references to readiness are `NOT_READY` | ✅ 一致 |
| renderer non-rendering guard | Report Markdown does not include EC content; only safe summary on stderr | ✅ 一致 |

**PR body is truthful and does not overclaim.**

### Architecture Boundary Verification

**UI → Service → Fund (Agent) 边界检查：**

1. Service 不直接导入 `FundDocumentRepository`、`pdf_cache`、`cache_helper`、`source_adapter`、`Docling`、`pdfplumber` — 通过 `evidence_confirm_runner.py` facade (`fund_agent/fund/evidence_confirm_runner.py`) 间接调用。
2. Service 的 `_run_evidence_confirm_if_enabled()` 只消费 `StructuredFundDataBundle` 并投影 `project_chapter_facts()`，不读取 PDF/XML/source。
3. EC runner facade (`evidence_confirm_runner.py`) 仅做 typed re-export，Service 不穿透到 `evidence_confirm_sources.py` 内部实现。
4. quality gate ECQ 投影 (`_evidence_confirm_quality_gate_issues`) 只消费 compact `EvidenceConfirmProductionSummary`，不读取 repository/PDF/cache/source。
5. CLI 只输出安全 stderr 行（`evidence_confirm_status`、`evidence_confirm_policy`、`evidence_confirm_checked_facts`、`evidence_confirm_failed_facts`、`evidence_confirm_auditability_score`），不输出原文/路径/parser/provider payload。

**边界检查结论：未发现架构穿透。**

### Default-On Policy State Machine

`_run_analysis_core()` 中的 EC → QG → block 排序审查：

```
入口 → extract → _run_evidence_confirm_if_enabled → _run_quality_gate_if_enabled(evidence_confirm_summary=...) → block checks
```

block 检查顺序（`fund_agent/services/fund_analysis_service.py:1193-1203`）：

1. `quality_gate_policy == "block"` + `quality_gate_result is None` → `_raise_evidence_confirm_block_if_required` → `QualityGateNotRunBlockedError`
2. `quality_gate_policy == "block"` + `quality_gate_result.status == GATE_STATUS_BLOCK` → `QualityGateBlockedError`（含 ECQ2 合并）
3. `_raise_evidence_confirm_block_if_required`（QG warn/off 或 QG pass 后）

每个状态的排他性覆盖：

| QG Policy | QG Result | EC Policy | EC Status | Raised Exception |
|-----------|-----------|-----------|-----------|-----------------|
| block | not run | block | fail | `EvidenceConfirmBlockedError` |
| block | not run | warn | pass/fail | `QualityGateNotRunBlockedError` |
| block | block | block | fail | `QualityGateBlockedError` (含 ECQ2/block) |
| block | block | warn | fail | `QualityGateBlockedError` (含 ECQ2/warn) |
| warn | pass/warn | block | fail | `EvidenceConfirmBlockedError` |
| warn | pass/warn | warn | fail | 不阻断（warn 摘要） |
| off | pass/block | block | fail | `EvidenceConfirmBlockedError` |
| off | pass/block | warn | fail | 不阻断 |

排他性覆盖完整，无重叠分支。

### Test Coverage Matrix

| Scenario | Test | Status |
|----------|------|--------|
| Product analyze default warn calls EC | `test_fund_analysis_service_product_analyze_default_warn_calls_evidence_confirm` | ✅ |
| Product analyze warn + EC fail non-blocking | `test_fund_analysis_service_product_analyze_default_warn_fail_is_non_blocking` | ✅ |
| Product analyze runner exception → safe summary | `test_fund_analysis_service_product_analyze_runner_exception_is_safe_summary` | ✅ |
| Product checklist default keeps EC off | `test_fund_analysis_service_product_checklist_default_keeps_evidence_confirm_off` | ✅ |
| Developer default and explicit off don't inherit warn | `test_fund_analysis_service_developer_default_and_explicit_off_do_not_inherit_warn` | ✅ |
| Developer block + EC fail → EvidenceConfirmBlockedError | `test_fund_analysis_service_evidence_confirm_block_raises_when_gate_off` | ✅ |
| QG warn + EC block + fail → EvidenceConfirmBlockedError | `test_fund_analysis_service_quality_warn_evidence_confirm_block_fail_raises_ec_error` | ✅ |
| QG block + EC fail → QualityGateBlockedError (含 ECQ2) | `test_fund_analysis_service_quality_block_evidence_confirm_fail_raises_quality_error` | ✅ |
| Product mode rejects EC override | `test_fund_analysis_service_product_mode_rejects_evidence_confirm_override` | ✅ |
| Boundary static imports clean | `test_fund_analysis_service_evidence_confirm_boundary_static_imports` | ✅ |
| EC stderr output (product warn) | `test_cli_analyze_default_product_emits_evidence_confirm_warn_to_stderr` | ✅ |
| EC stderr only exposes safe fields | `test_cli_analyze_evidence_confirm_does_not_leak_source_or_provider` | ✅ |
| EC block exit code 2 | `test_cli_analyze_evidence_confirm_block_exit_code` | ✅ |
| ECQ0/info not_requested | `test_quality_gate_integration_explicit_summary_none_produces_no_ecq_issues` | ✅ |
| ECQ1 repository failure | Covered via pathway_status="fail" → ECQ1 | ✅ |
| ECQ2/block deterministic fail | `test_quality_gate_integration_maps_evidence_confirm_fail_to_ecq2_block` | ✅ |
| ECQ2/warn deterministic fail | `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` | ✅ |
| ECQ2 block changes gate status | `test_quality_gate_integration_ecq2_block_changes_gate_status_to_block` | ✅ |
| ECQ3/warn deterministic warn | `test_quality_gate_integration_maps_evidence_confirm_warn_to_ecq3_warn` | ✅ |
| ECQ4/block semantic fail | `test_quality_gate_integration_maps_semantic_fail_to_ecq4_block` | ✅ |
| ECQ4/warn semantic fail | `test_quality_gate_integration_maps_semantic_fail_warn_policy_to_ecq4_warn` | ✅ |
| Deterministic fail not overridden by semantic pass | `test_quality_gate_integration_deterministic_fail_blocks_even_when_semantic_passes` | ✅ |
| Summary compact (no excerpt leak) | `test_summary_from_repository_fail_is_compact_and_no_excerpt` | ✅ |
| Summary pass counts facts | `test_summary_from_repository_pass_is_compact_and_counts_checked_facts` | ✅ |
| Summary warn keeps reviewable ids | `test_summary_from_repository_warn_keeps_reviewable_and_informational_ids` | ✅ |
| Stable reason validation | `test_not_run_evidence_confirm_summary_accepts_stable_reason_variants` | ✅ |
| Invalid reason rejected | `test_not_run_evidence_confirm_summary_rejects_invalid_reason` | ✅ |

**Test coverage: 29 targeted scenarios verified. No uncovered critical path identified.**

### 未发现实质性问题

---

## Open Questions

1. **`project_chapter_facts` 对空/最小 bundle 的行为**：当 `StructuredFundDataBundle` 不含任何 annual-report anchor 时，`project_chapter_facts` 返回空投影 → 0 fact 被检查 → `status="pass"`。这是正确的技术行为（没有东西检查 = 没有失败），但消费方应将 `checked_fact_count=0` 与 `status="pass"` 结合判断。当前 CLI stderr 行输出 `evidence_confirm_checked_facts: 0` 足以让调用方区分。

2. **`analyze-annual-period` EC summary 单独展示**：PR body 和 `docs/design.md` 已声明 CLI 当前不额外展示 annual-period 专用 EC summary 行，该显示问题保留为后续 UI/CLI residual。EC 确实在 target year `analyze()` 调用中运行并产生摘要，只是 CLI 不单独展示。

---

## Residual Risk

| Risk | Status | Owner |
|------|--------|-------|
| 无 provider-backed semantic quality proof | 声明为 NOT_READY，semantic companion 当前只接受 injected no-live result | 后续 gate |
| 无 checklist Evidence Confirm CLI support | 声明为 NOT_READY | 后续 gate |
| 无 report-body Evidence Confirm rendering | 声明为 NOT_READY，renderer guard 已确认 | 后续 gate |
| 无 multi-sample live source/PDF readiness proof | 声明为 NOT_READY | 后续 gate |
| `analyze-annual-period` CLI 不展示 EC summary 行 | 已知 residual，不影响运行语义 | 后续 UI/CLI gate |
| 单样本 live evidence（`004393/2025`）不证明多基金通用性 | 已声明为 NOT_READY | 后续 gate |

---

## Verdict

**PR_REVIEW_PASS**
