# Code Review

## Scope

- Mode: current changes (slice EC-DO-2 only)
- Branch: evidence-confirm-productionization
- Base: main (HEAD commit context)
- Output file: docs/reviews/code-review-20260623-ds-evidence-confirm-default-on-policy-slice2.md
- Included scope:
  - `fund_agent/ui/cli.py` - `--evidence-confirm-policy` help text change, no functional logic change
  - `tests/ui/test_cli.py` - test additions and updates for EC-DO-2 CLI surface
- Excluded scope:
  - Service layer, quality gate, docs/control, README (covered by other slices)
  - `docs/reviews/evidence-confirm-productionization-default-on-policy-slice2-implementation-evidence-20260623.md` (implementation evidence, not production code)
- Accepted plan: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`
- Parallel review coverage: 无

## Findings

### 1-未修复-低-test命名与计划要求不完全对齐

- **入口/函数**: `test_analyze_cli_calls_service_and_prints_report`
- **文件(行号)**: `tests/ui/test_cli.py:1802`
- **输入场景**: 计划 Slice EC-DO-2 的 Required tests 列表中明确要求 `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off` 作为独立测试，验证 plain `--dev-override` 不继承 product `warn`
- **实际分支**: 该行为被嵌入在 `test_analyze_cli_calls_service_and_prints_report` (line 1802) 中，通过 `assert _FakeService.last_request.developer_overrides.evidence_confirm_policy == "off"` 覆盖，但不存在独立命名的测试函数
- **预期行为**: 计划要求一个命名明确的独立测试 `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off`
- **实际行为**: 断言存在于现有测试中，但函数名不匹配计划规范，且测试的 primary purpose 是验证完整 developer override 透传而非专门验证 evidence_confirm_policy=off 的继承隔离
- **直接证据**: `tests/ui/test_cli.py:1710` 函数名是 `test_analyze_cli_calls_service_and_prints_report`，不是计划要求的名称；`tests/ui/test_cli.py:1802` 行确实断言了 `evidence_confirm_policy == "off"`
- **影响**: 降低 plan-to-test traceability；未来维护者按计划名称搜索测试时找不到对应函数，可能误判为测试缺失
- **建议改法和验证点**: 创建独立测试函数 `test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off`，专门验证 `--dev-override` 不带 `--evidence-confirm-policy` 时 developer_overrides.evidence_confirm_policy == "off" 且 mode == "developer_override"。或在 implementation evidence 中记录命名偏差及原因
- **修复风险（低）**: 纯测试拆分，不影响生产行为
- **严重程度（低）**: 行为覆盖存在，仅 traceability 受影响

## Open Questions

- `MultiYearAnnualAnalysisResult.current_year_result` 是否携带 `evidence_confirm_summary`？如果 Slice EC-DO-1 使得 `analyze-annual-period` Service 路径返回 Evidence Confirm 摘要，当前 CLI `analyze_annual_period` 命令不会调用 `_echo_evidence_confirm_summary()`，摘要将被静默丢弃。计划 Slice EC-DO-2 未要求 CLI 层展示 `analyze-annual-period` 的 Evidence Confirm 摘要，这属于计划范围内还是遗漏需确认。

## Residual Risk

- **质量 gate ECQ warn-policy 回归测试**未在本 slice 覆盖，由 EC-DO-3 承担
- **文档/control truth sync**未在本 slice 完成，由 EC-DO-4 承担
- **checklist Evidence Confirm CLI 支持**仍缺失，由独立 work unit 承担
- **`analyze-annual-period` CLI Evidence Confirm 摘要输出**未在本 slice 实现或测试，若 Service 层返回摘要但 CLI 不展示，存在 UX 不一致风险
- 本 slice 的测试全部为 deterministic no-live 测试，未执行任何 live/PDF/network/provider/LLM 命令

## Verdict

CODE_REVIEW_PASS_WITH_FINDINGS
