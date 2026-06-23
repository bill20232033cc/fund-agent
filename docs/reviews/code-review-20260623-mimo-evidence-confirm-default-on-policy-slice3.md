# Code Review

## Scope

- Mode: current changes
- Branch: `evidence-confirm-productionization`
- Base: `main`
- Output file: `docs/reviews/code-review-20260623-mimo-evidence-confirm-default-on-policy-slice3.md`
- Included scope:
  - `tests/fund/test_quality_gate_integration.py` — committed diff (`main...HEAD`) + unstaged working-tree diff
  - `docs/reviews/evidence-confirm-productionization-default-on-policy-slice3-implementation-evidence-20260623.md` — implementation evidence artifact
- Excluded scope: production code, score schema, control doc, startup packet, design doc, README, live/PDF/network/provider/LLM paths
- Parallel review coverage: 无

## Findings

未发现实质性问题。

## Evidence Summary

### Warn Policy ECQ Mapping

验证 `policy="warn"` 在所有 ECQ issue 类型下均正确映射为 `severity="warn"` 而非 `block`：

- **ECQ1/warn** (unstaged): `test_quality_gate_integration_maps_pathway_fail_warn_policy_to_ecq1_warn` — `pathway_status="fail"` + `policy="warn"` → ECQ1 severity=warn, gate status=warn
- **ECQ2/warn** (committed): `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` — `deterministic_status="fail"` + `policy="warn"` → ECQ2 severity=warn, gate status=warn
- **ECQ4/warn** (committed): `test_quality_gate_integration_maps_semantic_fail_warn_policy_to_ecq4_warn` — `semantic_status="fail"` + `policy="warn"` → ECQ4 severity=warn, gate status=warn

生产代码路径确认：`_ecq_policy_severity()` (quality_gate_integration.py:291-308) 对 `policy="block"` 返回 `SEVERITY_BLOCK`，对 `policy="off"` 抛 `ValueError`，其余（含 `"warn"`）返回 `SEVERITY_WARN`。测试覆盖了 happy path 和 off-policy 拒绝路径。

### score.json Unaware

`test_score_json_schema_remains_evidence_confirm_unaware` 验证 ECQ issue 只写入 `quality_gate.json`，`score_payload` 不含 `"evidence_confirm"` key。边界成立。

### Static Boundary

`test_quality_gate_integration_boundary_no_repository_or_source_imports` 使用 AST 解析 `quality_gate_integration.py` 的全部 import，断言不含 forbidden tokens `("repository", "source", "parser", "docling", "provider")`。

unstaged 将 `"source_adapter"` 收紧为 `"source"`，覆盖更广的 source-module substring。生产代码仅 import `evidence_confirm_production`（不含 `"source"` 子串），因此边界守卫通过且收紧后仍无误报。

### No Production/Live/Source Changes

- `git status --short` 仅显示 `M tests/fund/test_quality_gate_integration.py`
- `git diff main...HEAD --name-only` 中 `fund_agent/` 下的变更均属于本 branch 更早 slice，不属于 EC-DO-3 scope
- EC-DO-3 slice 只新增测试函数和调整 fixture/boundary guard，无生产代码、score schema、control doc、startup packet 或 design doc 修改

### Tests

```
uv run pytest -q tests/fund/test_quality_gate_integration.py
20 passed in 0.89s
```

```
uv run ruff check tests/fund/test_quality_gate_integration.py
All checks passed!
```

## Open Questions

无。

## Residual Risk

- 无未覆盖的高风险区域。`policy="off"` + `semantic_status="fail"` 路径的 `ValueError` 行为与 `deterministic_status="fail"` 路径共享同一 `_ecq_policy_severity()` 入口，无需独立回归测试。
- ECQ3 (deterministic warn) 的 `policy="off"` 路径理论上不可达（`not_run_evidence_confirm_summary` 已在上游拒绝 off+warn 组合），当前测试覆盖充分。

## Verdict

**CODE_REVIEW_PASS**
