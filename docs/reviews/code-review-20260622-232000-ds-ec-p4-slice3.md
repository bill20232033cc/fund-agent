# Code Review

## Scope

- Mode: current changes (uncommitted diff)
- Branch: evidence-confirm-productionization
- Base: prior accepted slice commit `1dd08fa gateflow: accept ec-p4 service integration slice 2`
- Output file: docs/reviews/code-review-20260622-232000-ds-ec-p4-slice3.md
- Included scope:
  - `fund_agent/ui/cli.py` — uncommitted diff
  - `tests/ui/test_cli.py` — uncommitted diff
  - Implementation evidence artifact `docs/reviews/evidence-confirm-productionization-ec-p4-slice3-implementation-evidence-20260622.md`
- Excluded scope:
  - Service layer internals (`fund_agent/services/fund_analysis_service.py`) — outside allowed command list; `FundAnalysisDeveloperOverrides.evidence_confirm_policy`, `EvidenceConfirmBlockedError`, `EvidenceConfirmProductionSummary` type shapes verified via prior reads only
  - `FundAnalysisRequest` constructor — unchanged in this diff, verified passes `evidence_confirm_policy` through `developer_overrides` path
  - Live/PDF/provider/network behavior — out of Slice 3 scope per contract
  - `docs/reviews/evidence-confirm-productionization-ec-p4-service-quality-integration-plan-20260622.md` — accepted plan, not re-reviewed
- Parallel review coverage: 无

## Contract Compliance Summary

| Contract clause | Status | Evidence |
|---|---|---|
| analyze only adds `--evidence-confirm-policy off\|warn\|block` | PASS | `cli.py:747-753`, default `"off"` |
| policy passes through `FundAnalysisDeveloperOverrides.evidence_confirm_policy` into `FundAnalysisService.analyze()` | PASS | `cli.py:2300`; test at `test_cli.py:2913-2916` |
| checklist has no `--evidence-confirm-policy` | PASS | `test_cli.py:3496`, `test_cli.py:3517` |
| CLI prints safe compact EC summary after quality-gate summary and before report body | PASS | `cli.py:901-903` order verified |
| `EvidenceConfirmBlockedError` caught after `QualityGateBlockedError`, exits code 2, no report body | PASS | `cli.py:889-891`; test at `test_cli.py:3118-3120` |
| CLI does not call Fund Evidence Confirm runner, repository, PDF/source/parser/provider internals, Docling, pdfplumber, or EID render artifacts | PASS | `test_cli.py:2730-2762` static guard verifies no forbidden imports |
| default analyze output remains unchanged and has no `evidence_confirm_` lines | PASS | `test_cli.py:2851-2875` |

## Findings

未发现实质性问题。

### Assessment Notes

以下项目经过逐项 adversarial 检查，未形成 material finding：

1. **分支顺序** (`cli.py:883-893`)：`QualityGateNotRunBlockedError` → `QualityGateBlockedError` → `EvidenceConfirmBlockedError` → `typer.Exit` → `Exception` 的顺序正确。`EvidenceConfirmBlockedError` 继承自 `ValueError`，与 quality gate 异常无继承关系，不存在 shadow catch。

2. **参数生效链**：`--evidence-confirm-policy` (CLI Option, default `"off"`) → `_build_developer_overrides` → `_evidence_confirm_policy(evidence_confirm_policy)` 校验 → `FundAnalysisDeveloperOverrides(evidence_confirm_policy=...)` → `FundAnalysisService.analyze(request)`。在 `dev_override=False` 时不构造 overrides，Service 收到 `developer_overrides=None`。生效链完整，无中间覆盖或静默丢弃。

3. **默认输出不变性**：`_echo_evidence_confirm_summary` (`cli.py:2641-2668`) 在 `summary is None` 时立即返回，无输出。默认 product mode 下 `FundAnalysisResult.evidence_confirm_summary` 由 Service 层设为 `None`（或不存在该属性），因此 `getattr(result, "evidence_confirm_summary", None)` 返回 `None`，静默跳过。测试 `test_analyze_cli_default_output_has_no_evidence_confirm_lines` 确认默认输出不含 `evidence_confirm_` 字符。

4. **阻断输出安全性**：`_echo_evidence_confirm_summary` 仅输出 `status`、`policy`、`checked_fact_count`、`failed_fact_count`、`auditability_score` 五个字段。不输出原文片段、文件路径、source/parser 内部标识。`test_analyze_cli_evidence_confirm_warn_passes_policy_and_prints_summary` 显式断言 `"excerpt" not in result.output.lower()` 和 `"pdf" not in result.output.lower()`。

5. **`_has_developer_override_options` 默认哨兵一致性** (`cli.py:2207`)：`evidence_confirm_policy != "off"` 与 CLI Option 默认值 `"off"` 一致，只有用户显式传入 `warn`/`block` 时才计入开发覆盖，与 `quality_gate_policy != "block"` 的哨兵模式对称。

6. **空/非法输入**：`_evidence_confirm_policy` 仅接受 `{"off", "warn", "block"}`，空字符串 `""`、大小写变体、任意其他值均触发 `typer.BadParameter`，被 `analyze` 函数 `cli.py:822-824` 捕获并以 code 2 退出。`test_analyze_cli_rejects_evidence_confirm_policy_without_dev_override` 覆盖了 product mode 下传入 `warn` 的拒绝路径。

7. **checklist 隔离**：`test_checklist_cli_rejects_use_llm_option` (`test_cli.py:3496`) 验证 checklist 参数集中不含 `--evidence-confirm-policy`；`test_checklist_cli_help_does_not_expose_evidence_confirm_policy` (`test_cli.py:3499-3517`) 验证 help 输出不暴露该选项。

8. **Fake 测试覆盖的契约面**：新增 5 个测试覆盖了：默认无 EC 行、warn 策略透传+摘要、block 阻断退出码+无报告正文、product mode 拒绝 warn、checklist 无 EC flag、CLI 无禁止 import。两个 fake Service（`_FakeEvidenceConfirmWarnService`、`_FakeEvidenceConfirmBlockedAnalysisService`）和一个 fake summary（`_FakeEvidenceConfirmSummary`）精确定义了测试输入形状，无真实 Service/PDF/网络依赖。

## Open Questions

- `FundAnalysisDeveloperOverrides.evidence_confirm_policy` 的类型是 `EvidenceConfirmProductionPolicy | None`（来自 `fund_analysis_service.py:243`），但 `_evidence_confirm_policy` 返回 plain `str`。在 strict type checker 下可能产生类型不匹配。此问题与 `_quality_gate_policy` → `QualityGatePolicy` 的模式完全一致，属于既有代码库模式而非本次引入的新问题。未形成 finding。

## Residual Risk

| Risk | Severity | Owner | Destination |
|---|---|---|---|
| 测试仅使用 fake Service，未验证真实 `FundAnalysisService.analyze()` 的 `evidence_confirm_policy` 消费路径 | 低 | EC-P4 后续 Slice（Service 层集成测试） | 已在 Slice 3 contract 中明确排除；属于 Slice 1/2/4/5 验证范围 |
| `EvidenceConfirmBlockedError` 的 `not_run_reason` 在阻断时未输出 | 低 | 后续 checklist EC slice | `_echo_evidence_confirm_summary` 只输出五个 compact 字段，`not_run_reason` 仅存储在 summary 对象中未打印。与 quality gate `not_run` 场景的显式输出不一致，但 compact 契约是有意设计 |
| Checklist Evidence Confirm CLI 支持未实现 | 低 | 后续 checklist EC slice | Slice 3 contract 明确 checklist 无 `--evidence-confirm-policy`；后续工作单元负责 |

## Validation Commands and Results

```
$ uv run pytest tests/ui/test_cli.py -q
........................................................................ [ 87%]
..........                                                               [100%]
82 passed in 1.29s
```

```
$ uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
All checks passed!
```

```
$ git diff --check -- fund_agent/ui/cli.py tests/ui/test_cli.py
<no output — no whitespace errors>
```

## Verdict

**PASS**

Release/readiness: NOT_READY — Slice 3 CLI/UI gate 通过；release 需要完成后续 Service 集成 slice、端到端测试和 docs sync。
