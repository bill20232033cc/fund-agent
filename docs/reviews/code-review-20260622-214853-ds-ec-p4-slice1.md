# Code Review: EC-P4 Slice 1 — Fund Summary + Quality Gate ECQ Projection

## Gate

- Work unit: `Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration`
- Gate: `deepreview` (code review)
- Classification: `heavy`
- Slice: `Slice 1 - Fund Summary + Quality Gate ECQ Projection`
- Branch: `evidence-confirm-productionization`
- Reviewer: AgentDS
- Timestamp: `2026-06-22 21:48 Asia/Shanghai`
- Release/readiness: `NOT_READY`

## Verdict

**PASS_WITH_FINDINGS** — 3 findings (1 HIGH, 2 MEDIUM), 0 blockers.

Implementation is structurally correct, all 44 tests pass, boundary constraints are satisfied, and the core contracts (summary type, ECQ issue taxonomy, merge semantics, score.json isolation) match the accepted plan. No live/PDF/network/provider/LLM execution is required or performed.

## Reviewed Target

### Source files (new/modified)
- `fund_agent/fund/evidence_confirm_production.py` (new, 400 lines)
- `fund_agent/fund/quality_gate.py` (+43 lines: `issue_id` field, `merge_quality_gate_issues()`)
- `fund_agent/fund/quality_gate_integration.py` (+153 lines: ECQ projection, summary ingestion)

### Test files (new/modified)
- `tests/fund/test_evidence_confirm_production.py` (new, 1 test)
- `tests/fund/test_quality_gate_integration.py` (+9 tests)
- `tests/fund/test_quality_gate.py` (unchanged, 29 pre-existing tests pass)

### Context documents
- `docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md`
- `docs/reviews/evidence-confirm-productionization-ec-p4-plan-controller-judgment-20260622.md`
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice1-implementation-evidence-20260622.md`

## Summary

Slice 1 implements the Fund-layer Evidence Confirm production summary type (`EvidenceConfirmProductionSummary`) and quality-gate ECQ issue projection (`ECQ0`–`ECQ3`). The implementation correctly:

- Creates compact summaries without raw excerpts, PDF/cache paths, or parser JSON.
- Maps `EvidenceConfirmRepositoryRunResult` → `EvidenceConfirmProductionSummary` via `summary_from_repository_result()` with correct aggregate precedence (`fail > warn > pass > not_run/not_applicable`).
- Maps EC summaries to stable `ECQ*` issues with deterministic issue IDs (`evidence-confirm:{fund_code}:{report_year}:{rule_code}:{reason}`), no timestamp or run id.
- Merges ECQ issues into `QualityGateResult` via `merge_quality_gate_issues()` with status re-aggregation using existing `_aggregate_gate_status()` semantics.
- Preserves `score.json` unchanged; ECQ issues appear only in `quality_gate.json`/`quality_gate.md`.
- Maintains backward compatibility: `run_quality_gate_for_bundle()` without `evidence_confirm_summary` keeps existing FQ-only behavior.
- Respects the boundary: `quality_gate_integration.py` imports no repository, source adapter, parser, Docling, or provider modules (verified by AST test and manual inspection).

## Findings

### Finding DS-ECP4S1-01 — HIGH — `hard_gate.informational_issue_ids` 被静默丢弃

- **File/line:** `fund_agent/fund/evidence_confirm_production.py:326–343` (`_warning_issue_ids`)
- **Issue:** `EvidenceConfirmHardGate` 有三个 issue 列表：`blocking_issue_ids`、`reviewable_issue_ids`、`informational_issue_ids`。`_blocking_issue_ids` 收集了 `hard_gate.blocking_issue_ids`，`_warning_issue_ids` 收集了 `hard_gate.reviewable_issue_ids`，但 `hard_gate.informational_issue_ids` 没有被任何函数收集，在摘要中**完全丢失**。
- **Why it matters:** V2 hard gate 产生的 informational issue（如 `E3/informational` 维度的非阻塞提示）在进入生产摘要后不可见。下游 quality gate 和 Service 无法感知这些信息性信号。同时 `issue_count`（来自 `_issue_count`）仍然统计了这些 issue（通过 `len(result.evidence_confirm_result.issues)`），但 `blocking_issue_ids` 和 `warning_issue_ids` 中找不到对应 ID，造成 count 与 ID 列表不一致。
- **Required fix:** 决定 informational issue 的去向：要么在摘要中新增 `informational_issue_ids` 字段（需更新 schema version），要么将 V2 informational issue 合并到 `warning_issue_ids` 中（需更新 docstring 说明映射关系），要么在 plan 中显式声明 informational issues 不在生产摘要范围内。无论哪种选择，`issue_count` 与 ID 列表的统计口径必须一致。
- **Suggested owner:** Fund/Evidence Confirm owner

### Finding DS-ECP4S1-02 — MEDIUM — 测试覆盖缺口：pass/warn 摘要路径及校验边界

- **File/line:** `tests/fund/test_evidence_confirm_production.py:14–56`
- **Issue:** 模块只有 1 个测试 (`test_summary_from_repository_fail_is_compact_and_no_excerpt`)，仅覆盖 repository fail 路径。以下路径无测试：
  - `summary_from_repository_result` 的 pass 结果（pathway=pass, deterministic=pass）
  - `summary_from_repository_result` 的 warn 结果（deterministic=warn）
  - `not_run_evidence_confirm_summary` 的合法 reason 变体（`runner_exception:SomeError`、`invalid_request`）
  - `not_run_evidence_confirm_summary` 的非法 reason（应抛出 `ValueError`）
  - `not_run_evidence_confirm_summary` 的非法 policy（应抛出 `ValueError`）
  - `_aggregate_summary_status` 的 `not_applicable` 边界
- **Why it matters:** `not_run_evidence_confirm_summary` 是 Service/CLI（Slice 2/3）将直接调用的 public API。其参数校验逻辑（`_validate_policy`、`_validate_reason`）的错误路径未经测试，回归风险较高。`summary_from_repository_result` 的 pass/warn 路径同样未验证，无法证明摘要在这些场景下不泄漏 excerpt 或 PDF 路径。
- **Required fix:** 新增至少 3 个测试：pass summary 不泄漏 excerpt、warn summary 正确设置 `warning_issue_ids`、`not_run_evidence_confirm_summary` 拒绝非法 reason/policy。建议在 Slice 2 开始前补齐，避免 Service 集成时才发现校验缺口。
- **Suggested owner:** Fund/Evidence Confirm owner + test owner

### Finding DS-ECP4S1-03 — MEDIUM — `_ecq_policy_severity` 对 policy=`off` 返回 `warn`，缺乏防御性断言

- **File/line:** `fund_agent/fund/quality_gate_integration.py:264–279` (`_ecq_policy_severity`)
- **Issue:** `_ecq_policy_severity` 的实现是 `if policy == "block": return SEVERITY_BLOCK; return SEVERITY_WARN`。如果 policy 为 `"off"`，返回 `SEVERITY_WARN`。虽然当前调用链中 policy=`off` 的摘要 `status` 必定为 `not_run`（由 `not_run_evidence_confirm_summary` 构造），不会进入 ECQ1/ECQ2 分支，但缺乏显式断言意味着未来调用方如果错误传入 policy=`off` 的 fail/warn 摘要，会被**静默降级**为 warn 而非 fail-closed。
- **Why it matters:** 防御性编程。在经济性 gate（heavy classification）中，policy=`off` 的非 not_run 摘要是明确的调用方逻辑错误，应 fail-closed 而非静默继续。
- **Required fix:** 在 `_ecq_policy_severity` 开头增加 `if summary.policy == "off": raise ValueError(...)` 或 assert。或在 `_evidence_confirm_quality_gate_issues` 的 ECQ1/ECQ2 分支调用前增加 policy 一致性断言。
- **Suggested owner:** Quality gate owner

## Residual Risks / Uncovered Areas

| Risk | Coverage | Owner |
|---|---|---|
| `_evidence_confirm_quality_gate_issues` 的 `summary is None` 分支在当前 `run_quality_gate_for_bundle` 路径不可达（只有 `is not None` 时才调用），属 Slice 2 前置代码 | Slice 2 集成测试应覆盖 | Service owner |
| `not_run_evidence_confirm_summary` 不校验 policy 与 reason 的一致性（如 `policy="block"` + `reason="policy_off"`） | 调用方（Service）负责构造一致参数 | Fund owner |
| `merge_quality_gate_issues` 在已由 `run_quality_gate` 写过文件后再次写入，造成同一请求中 `quality_gate.json`/`.md` 被写两次 | 正确性无影响，性能影响可忽略 | — |
| `evidence_confirm_production.py` → `evidence_confirm_sources.py` 的导入会传递引入 `documents.models`（`ParsedAnnualReport` 等类型），虽不违反 boundary 字面条文，但类型图比必要更重 | 后续可按需提取独立类型模块 | Fund owner |
| 测试 `test_evidence_confirm_production.py` 直接导入 `evidence_confirm_sources` 构造 `EvidenceConfirmRepositoryRunResult`，未通过 `evidence_confirm_production` 的 public API | 可接受；测试需要构造底层类型 | — |
| `_warning_issue_ids` 将 runner 层 `informational` severity 映射为 summary `warning_issue_ids`，同时混入 `pathway:{reason}` 合成 ID，使 ECQ3 reason 中的 count 含义不纯粹（包含 pathway warning 而非仅 V2 warning） | 不影响正确性，但 reason 字符串 `deterministic_warn_N` 的 N 可能误导 | Quality gate owner |

## Required Follow-Up

1. **DS-ECP4S1-01 (HIGH):** 在 Slice 2 开始前决定 `hard_gate.informational_issue_ids` 的去向，统一 `issue_count` 与 ID 列表的统计口径。
2. **DS-ECP4S1-02 (MEDIUM):** 补齐 `test_evidence_confirm_production.py` 的 pass/warn/validation 测试（≥3 个）。
3. **DS-ECP4S1-03 (MEDIUM):** 为 `_ecq_policy_severity` 增加 policy=`off` 防御性断言。
4. Slice 2 实现时必须覆盖 `_evidence_confirm_quality_gate_issues(summary=None)` 的调用路径。

## Validation

- `uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q` → 44 passed
- `uv run ruff check` → All checks passed
- `git diff --check` → no whitespace errors
- AST boundary check: `quality_gate_integration.py` imports no repository/source_adapter/parser/docling/provider
- `rg evidence_confirm\|EvidenceConfirm\|ECQ fund_agent/fund/extraction_score.py` → no matches
- Manual verification: no timestamp/run_id in ECQ issue IDs, no excerpt/PDF path in summary, `score.json` unchanged

## Reviewed By

AgentDS, 2026-06-22 21:48 Asia/Shanghai
