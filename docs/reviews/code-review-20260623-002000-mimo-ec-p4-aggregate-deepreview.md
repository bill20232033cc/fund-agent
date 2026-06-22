# Aggregate Deepreview: EC-P4 Service/UI/Renderer/Quality-Gate Production Integration

## Scope

- Mode: current changes
- Branch: evidence-confirm-productionization
- Base: main
- Output file: docs/reviews/code-review-20260623-002000-mimo-ec-p4-aggregate-deepreview.md
- Gate: EC-P4 aggregate deepreview after accepted Slice 1-6 local commit 4c80d86
- Included scope: EC-P4 Slice 1-6 code, tests, docs and artifacts across fund_agent/fund/evidence_confirm_production.py, fund_agent/fund/quality_gate_integration.py, fund_agent/services/fund_analysis_service.py, fund_agent/ui/cli.py, fund_agent/fund/template/renderer.py, and focused tests under tests/fund and tests/services
- Excluded scope: source/test/runtime behavior outside accepted gates; live/PDF/provider/network commands; PR-40 mutation; release/readiness claims
- Parallel review coverage: 无

## Truth Chain Verification

- AGENTS.md: 已读取。四层架构 UI->Service->Host->Agent，模块边界、硬约束、Evidence Confirm 规则均在位。
- docs/design.md: 已读取 Lines 875-903。Evidence Confirm developer opt-in 与 ECQ 投影当前已实现段落、未来/候选边界、Service policy/gate 状态机均已同步。
- docs/implementation-control.md: 已读取。EC-P4 Slice 1-6 accepted，当前 gate 为 aggregate deepreview，下一入口为 aggregate deepreview gate，release/readiness remains NOT_READY。
- docs/current-startup-packet.md: 已读取。EC-P4 accepted plan chain、slice commits、controller judgments 均已索引。

## Findings

未发现实质性问题。

以下是 review 过程中检查的集成路径和验证结论：

### 1. Live source/PDF summary propagation (Slice 1)

- **入口**: `summary_from_repository_result()` @ evidence_confirm_production.py:77
- **验证**: repository fail 结果正确转为 `status="fail"` + `not_run_reason="repository_failure:<reason>"`。compact summary 不携带 excerpt、PDF/cache 路径、parser JSON 或 source adapter 对象。
- **证据**: test_summary_from_repository_fail_is_compact_and_no_excerpt 验证 `"excerpt" not in payload` 和 `"SHOULD_NOT_LEAK" not in repr(payload)`。

### 2. Semantic companion injected-result propagation (Slice 5)

- **入口**: `summary_from_repository_result(semantic_result=...)` @ evidence_confirm_production.py:81
- **验证**: injected no-live semantic result 正确传播为 `semantic_status`，`_validate_semantic_result_identity()` 在 fund_code/report_year 不一致时 ValueError fail-closed。
- **证据**: test_semantic_result_can_be_injected_into_production_summary_without_client 和 test_semantic_result_identity_mismatch_fails_closed_before_propagation 通过。

### 3. Service opt-in policy (Slice 2)

- **入口**: `_effective_evidence_confirm_policy()` @ fund_analysis_service.py:1658
- **验证**: `checklist` command_source 固定返回 `"off"`，`analyze` 使用 `resolved_contract.evidence_confirm_policy`。product mode 默认 `evidence_confirm_policy="off"` (line 1587)。
- **证据**: test_fund_analysis_service_checklist_returns_shared_core_without_rendering 验证 `evidence_runner.calls == []`。

### 4. CLI/UI summary and exit behavior (Slice 3)

- **入口**: `analyze()` @ cli.py:901-902, `checklist()` @ cli.py:980
- **验证**: analyze 调用 `_echo_quality_gate_summary` 和 `_echo_evidence_confirm_summary`。checklist 只调用 `_echo_quality_gate_summary`（EC policy 固定 off，summary 始终 None，echo 为 no-op）。`EvidenceConfirmBlockedError` 在 analyze 路径被 catch 并输出 stderr 结构化信息，exit code 2。
- **证据**: test_cli_evidence_confirm_blocked_exits_two 通过。

### 5. Renderer non-rendering (Slice 4)

- **入口**: `render_template_report()` @ renderer.py:141
- **验证**: renderer.py 不包含 evidence_confirm、ECQ、semantic 相关代码。报告 Markdown 不渲染 Evidence Confirm 内容，不写入正文或证据附录。
- **证据**: grep 确认 renderer.py 无 EC-P4 内容；design.md line 888 明确记录 "renderer 报告 Markdown 仍不渲染 Evidence Confirm"。

### 6. ECQ0-ECQ4 quality-gate projection (Slice 1/5)

- **入口**: `_evidence_confirm_quality_gate_issues()` @ quality_gate_integration.py:173
- **验证**: ECQ0/info (not_run/not_requested), ECQ1 (pathway fail), ECQ2 (deterministic fail), ECQ3/warn (deterministic warn), ECQ4 (semantic fail/warn) 投影正确。`_ecq_policy_severity()` 在 policy="off" 时 ValueError fail-closed。ECQ 只进入 quality_gate.json，不修改 score.json schema。
- **证据**: 14 个 ECQ 投影测试全部通过，包括 test_score_json_schema_remains_evidence_confirm_unaware。

### 7. Docs truth (Slice 6)

- **验证**: design.md Lines 875-903 正确记录 Evidence Confirm developer opt-in、ECQ 投影、未来/候选边界。implementation-control.md 正确记录 EC-P4 Slice 1-6 accepted 状态和 NOT_READY。
- **证据**: 代码实现与文档描述一致。

## Commands Run and Results

```
.venv/bin/pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py -v --tb=short
Result: 255 passed in 1.70s
```

## Open Questions

无。

## Residual Risk

- checklist Evidence Confirm CLI support 未实现（design.md line 886 明确记录为后续 gate）。
- default-on Evidence Confirm 未实现（design.md line 892 明确记录为未来/候选边界）。
- provider-backed semantic quality 未实现（design.md line 892 明确记录为未来/候选边界）。
- release/readiness remains NOT_READY（implementation-control.md 和 startup-packet.md 均已记录）。

## Verdict

PASS

---

AGGREGATE_DEEPREVIEW_COMPLETE_NOT_READY
