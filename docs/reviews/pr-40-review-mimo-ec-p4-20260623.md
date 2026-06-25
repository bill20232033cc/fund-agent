# PR-40 Review: Evidence Confirm Productionization

## Scope

- Mode: PR review
- PR: #40 — Add Evidence Confirm productionization and service integration
- URL: https://github.com/bill20232033cc/fund-agent/pull/40
- Author: bill20232033cc
- Head: evidence-confirm-productionization @ 12f36c3628626611f3385c7cbc943856292ea046
- Base: evidence-confirm-anchor-audit-score
- CI: test=PASS (59s)
- Mergeable: MERGEABLE
- State: OPEN / draft
- Output file: docs/reviews/pr-40-review-mimo-ec-p4-20260623.md

## Verdict: PASS

## PR Body Review

PR body 正确声明：

- EC-P1A/P2/P3/P4 scope 和实现边界
- developer opt-in `--evidence-confirm-policy off|warn|block`
- product default 和 checklist 保持 `off` / no-run
- renderer non-rendering guard
- ECQ0-ECQ4 projection
- no-live injected semantic companion
- `evidence_confirm_runner` facade

Non-goals / NOT_READY 声明完整：

- No provider-backed semantic quality proof
- No checklist Evidence Confirm CLI support
- No default-on Evidence Confirm
- No release/readiness promotion
- PR remains draft

PR body 未过声称 release/readiness/default-on/checklist/provider-backed semantic quality。

## Key Integration Verification

### 1. Repository-bounded live source/PDF pathway

Service 通过 `evidence_confirm_runner` facade 导入 typed runner 契约，不直接导入 `evidence_confirm_sources`：

```
fund_agent/services/fund_analysis_service.py:65:
from fund_agent.fund.evidence_confirm_runner import (
    EvidenceConfirmRepositoryRunRequest,
    EvidenceConfirmRepositoryRunResult,
    run_repository_bounded_evidence_confirm,
)
```

`grep -c "evidence_confirm_sources" fund_agent/services/fund_analysis_service.py` = 0。

### 2. Semantic entailment remains no-live injected

`summary_from_repository_result()` 接受 `semantic_result: EvidenceSemanticResult | None`，不构造 provider client。`_validate_semantic_result_identity()` 在身份不一致时 ValueError fail-closed。

### 3. Service opt-in policy

`_effective_evidence_confirm_policy()` line 1679: `command_source == "checklist"` 返回 `"off"`。Product mode 默认 `evidence_confirm_policy="off"` (line 1587)。

### 4. Renderer non-rendering

`grep -c "evidence_confirm" fund_agent/fund/template/renderer.py` = 0。Renderer 不导入、不引用、不渲染 Evidence Confirm 内容。

### 5. ECQ0-ECQ4 projection

`_evidence_confirm_quality_gate_issues()` 正确投影 ECQ0-ECQ4。ECQ 只进入 quality_gate.json，不修改 score.json。

### 6. CLI summary and exit behavior

- `analyze` 命令输出 `_echo_quality_gate_summary` 和 `_echo_evidence_confirm_summary`
- `EvidenceConfirmBlockedError` → exit code 2
- `checklist` 不暴露 `--evidence-confirm-policy`

## Commands Run

```
.venv/bin/pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate_integration.py tests/fund/test_evidence_confirm_semantic.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py::test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries -q --tb=short
Result: 170 passed in 1.22s
```

CI: test=PASS (59s)

## Residual Risks

- EC runner 生产集成未经多基金 live 验证；当前仅 `004393/2025` 单样本 bounded live evidence。
- 多年路径 (`analyze_multi_year_annual`) 不传递 EC policy，通过 `analyze()` 间接获得 product mode `off` 默认值。
- release/readiness remains NOT_READY；default-on EC、checklist EC CLI、provider-backed semantic quality 未授权。

---

PR_REVIEW_COMPLETE_NOT_READY
