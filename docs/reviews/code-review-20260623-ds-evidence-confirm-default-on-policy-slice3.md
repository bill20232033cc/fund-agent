# Code Review

## Scope

- Mode: current changes (EC-DO-3 gated review)
- Branch: `evidence-confirm-productionization`
- Base: `main`
- Output file: `docs/reviews/code-review-20260623-ds-evidence-confirm-default-on-policy-slice3.md`
- Included scope:
  - `tests/fund/test_quality_gate_integration.py` (committed diff + unstaged diff)
  - `docs/reviews/evidence-confirm-productionization-default-on-policy-slice3-implementation-evidence-20260623.md` (implementation evidence artifact)
- Excluded scope: all production code, score schema, design/control/startup docs, README, live/PDF/network/provider/LLM paths
- Parallel review coverage: 无

## Review Checklist

按用户指定的四项检查逐条验证：

### 1. warn policy ECQ mapping

**生产代码路径**（`fund_agent/fund/quality_gate_integration.py:291-308`）：

`_ecq_policy_severity()` 在 `policy="warn"` 时经过以下分支：
- `policy == "block"` → False
- `policy == "off"` → False（off policy 的 fail/warn 摘要已被上游 `_validate_policy` 拦截）
- fallthrough → 返回 `SEVERITY_WARN`

该函数为以下 ECQ 类型提供 severity：
- **ECQ1**（pathway fail, line 224）：`severity=_ecq_policy_severity(summary)` → warn policy 时返回 `warn` ✓
- **ECQ2**（deterministic fail, line 237）：`severity=_ecq_policy_severity(summary)` → warn policy 时返回 `warn` ✓
- **ECQ4**（semantic fail, line 283）：`severity=_ecq_policy_severity(summary)` → warn policy 时返回 `warn` ✓
- **ECQ3**（deterministic warn, line 252）：`severity=SEVERITY_WARN` — 硬编码为 WARN，不依赖 policy。符合产品语义：warning 级别证据不应因 policy 升级为 block ✓

**测试覆盖**：

| 测试 | ECQ 类型 | Policy | 断言 severity | 断言 gate status |
|---|---|---|---|---|
| `test_quality_gate_integration_maps_evidence_confirm_fail_to_ecq2_block` | ECQ2 | block | block | block |
| `test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn` | ECQ2 | warn | warn | warn |
| `test_quality_gate_integration_maps_semantic_fail_to_ecq4_block` | ECQ4 | block | block | block |
| `test_quality_gate_integration_maps_semantic_fail_warn_policy_to_ecq4_warn` | ECQ4 | warn | warn | warn |
| `test_quality_gate_integration_maps_pathway_fail_to_ecq1_block` | ECQ1 | block | block | block |
| `test_quality_gate_integration_maps_pathway_fail_warn_policy_to_ecq1_warn` | ECQ1 | warn | warn | warn |
| `test_quality_gate_integration_maps_evidence_confirm_warn_to_ecq3_warn` | ECQ3 | block(default) | warn | warn |
| `test_quality_gate_integration_rejects_off_policy_fail_summary` | — | off | ValueError raised | — |
| `test_quality_gate_integration_maps_not_run_to_ecq0_info` | ECQ0 | off | info | pass |

warn policy 下所有 ECQ fail 路径均正确映射为 `warn`，off policy 的 fail/warn 摘要被正确拒绝。

### 2. score.json unaware

**生产代码路径**（`fund_agent/fund/quality_gate_integration.py:117-134`）：

```
write_extraction_score_records() → score.json 写入完成
    ↓
run_quality_gate() → quality_gate.json 写入完成（仅 FQ issue）
    ↓
if evidence_confirm_summary is not None:       ← ECQ 介入点
    _evidence_confirm_quality_gate_issues()     ← 只构造 issue 对象
    merge_quality_gate_issues()                 ← 只重写 gate_json + gate_md
```

`merge_quality_gate_issues()`（`quality_gate.py:212-250`）仅操作 `gate_json_path` 和 `gate_markdown_path`，不接触 `score_path`。ECQ 分支在 score.json 写入完成后才执行。

**测试覆盖**：`test_score_json_schema_remains_evidence_confirm_unaware` 断言：
- `score_payload` 中不含 `"evidence_confirm"` key ✓
- `score_payload` 中所有 key 均不含 `"evidence_confirm"` 子串 ✓
- `gate_payload` 中存在 `ECQ3` issue ✓

### 3. static boundary

**生产代码**（`fund_agent/fund/quality_gate_integration.py`）实际 imports：

```python
from fund_agent.config.paths import DEFAULT_QUALITY_GATE_OUTPUT_ROOT
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extraction_score import ExtractionScoreResult, write_extraction_score_records
from fund_agent.fund.extraction_snapshot import SelectedFundRecord, build_snapshot_records, load_selected_funds, validate_selected_fund_pool
from fund_agent.fund.evidence_confirm_production import EvidenceConfirmProductionSummary
from fund_agent.fund.quality_gate import SEVERITY_BLOCK, SEVERITY_INFO, SEVERITY_WARN, QualityGateIssue, QualityGateResult, merge_quality_gate_issues, run_quality_gate
```

逐条检查 forbidden tokens（`repository`, `source`, `parser`, `docling`, `provider`）：

| Import module | repository | source | parser | docling | provider |
|---|---|---|---|---|---|
| `fund_agent.config.paths` | ✗ | ✗ | ✗ | ✗ | ✗ |
| `fund_agent.fund.data_extractor` | ✗ | ✗ | ✗ | ✗ | ✗ |
| `fund_agent.fund.extraction_score` | ✗ | ✗ | ✗ | ✗ | ✗ |
| `fund_agent.fund.extraction_snapshot` | ✗ | ✗ | ✗ | ✗ | ✗ |
| `fund_agent.fund.evidence_confirm_production` | ✗ | ✗ | ✗ | ✗ | ✗ |
| `fund_agent.fund.quality_gate` | ✗ | ✗ | ✗ | ✗ | ✗ |

无一命中。`evidence_confirm_production` 虽内部 import `evidence_confirm_sources`，但：
- adapter 只消费已物化的 `EvidenceConfirmProductionSummary` dataclass，不直接接触 `EvidenceConfirmRepositoryRunResult`
- 边界测试仅检查 `quality_gate_integration.py` 自身 import，不递归检查传递依赖
- 不依赖 `evidence_confirm_sources` 的类型、对象或行为

**测试覆盖**：`test_quality_gate_integration_boundary_no_repository_or_source_imports` 用 AST 解析静态校验所有 import。当前 diff 将 forbidden 从 `"source_adapter"` 拓宽为 `"source"`，覆盖更广的 source 相关边界模块。

### 4. no production/live/source changes

**Git diff 确认**：

```
git diff main...HEAD -- <only test file changed>
```

仅 `tests/fund/test_quality_gate_integration.py` 有修改（22 个测试函数），涉及：
- 新增 ECQ 映射回归测试（ECQ0~ECQ4，block/warn/off policy）
- 新增 score.json 无感知回归测试
- 新增静态边界回归测试
- 新增 pathway fail warn policy 测试（unstaged）
- 边界 forbidden token 拓宽（unstaged）
- `_summary` 测试辅助工厂函数
- `_golden_answer_json` 增加 `report_year` 字段
- `import ast`, `import pytest`, `from fund_agent.fund.evidence_confirm_production import ...` 新增导入

无生产代码、score schema、control doc、startup packet、design doc、README、live/PDF/network/provider/LLM 路径变更。

## Findings

未发现实质性问题。

## Open Questions

1. `_summary` 测试辅助函数对所有场景设置 `checked_fact_count=1` 和 `auditability_score=40`，包括 `pathway_status="fail"` + `deterministic_status="not_run"`（ECQ1 测试用例）。这在语义上不精确（pathway fail 时 V2 未运行，fact count 应为 0），但所有相关测试的断言不依赖这两个字段，不影响测试正确性。
2. AST 边界检查仅覆盖 `ast.Import` / `ast.ImportFrom` 静态导入，不覆盖 `importlib.import_module()` 动态导入。当前 `quality_gate_integration.py` 仅使用显式静态导入，暂无风险。

## Residual Risk

- **未覆盖的 ECQ 组合**：`policy="block"` + `deterministic_status="warn"` + `semantic_status="fail"` 同时出现的组合未单独测试。当前代码中 ECQ3（warn）和 ECQ4（semantic fail）独立生成后由 `merge_quality_gate_issues` 合并，聚合逻辑已有独立测试覆盖（`_aggregate_gate_status` 在 `quality_gate.py:1382-1400`），风险较低。
- **gate_markdown 内容**：多数测试只断言 JSON payload，仅 `test_quality_gate_integration_maps_evidence_confirm_fail_to_ecq2_block` 断言 markdown 中包含 `"ECQ2"` 字符串。其他 ECQ 类型的 markdown 输出格式未逐条验证。不影响功能正确性。
- **`_summary` 辅助函数参数校验**：`status` 参数与实际 `deterministic_status`/`pathway_status` 的一致性由调用方保证，无运行时校验。若测试写错参数组合（如 `status="pass"` + `deterministic_status="fail"`），会构造出内部不一致的摘要。已在现有测试中逐条核对，所有参数组合与生产语义一致。
- **后续 slice 依赖**：docs/design/control/startup/README 同步、checklist CLI 支持、provider-backed semantic quality、multi-sample live/source evidence、PR mark-ready、merge and release transition 均在 EC-DO-3 scope 之外（分配给 EC-DO-4 及后续 work unit）。

## Verdict

**CODE_REVIEW_PASS**

四项指定检查全部通过：warn policy ECQ mapping 正确，score.json 未被 ECQ 污染，静态边界未被突破，无生产代码变更。20 个测试全部通过，ruff 无警告，git diff --check 无空白问题。
