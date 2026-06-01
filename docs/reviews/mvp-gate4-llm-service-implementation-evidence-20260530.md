# MVP Gate 4 Slice 4B Service analyze_with_llm implementation evidence

日期：2026-05-30

角色：implementation worker。本文只记录 Slice 4B 实现证据；未 commit、未 push、未 PR、未 merge、未 release、未 promotion。

## Gate / Scope

- Current gate: `MVP Gate 4 Slice 4B: Service analyze_with_llm implementation gate`
- Scope: 在 Service 层新增显式 LLM analyze use case，复用 `_run_analysis_core()`、Gate 3 `orchestrate_chapters()` 和 Slice 4A `assemble_final_chapters()`，返回 typed `FundLLMAnalysisResult`。
- Non-goals preserved: 未修改 CLI `--use-llm`、生产 LLM provider、Host/Agent/dayu、final judgment 语义、quality gate/FQ 语义、golden/score/snapshot/manifests、Fund primitives 或 renderer。

## Required Preflight

```text
$ git branch --show-current
codex/local-reconciliation
```

```text
$ git status --short
?? --help
?? docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/reviews/repo-review-20260527-215953.md
?? docs/reviews/repo-review-20260527-225303.md
?? docs/tmux-agent-memory-store.md
?? reviews/
```

预检结论：当前分支不是 protected trunk；初始状态只有已知无关 untracked，没有 tracked dirty，继续实现。

## Source Of Truth Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/design.md` Route C / Gate 4 相关段落
- `docs/reviews/mvp-gate4-final-assembler-cli-plan-20260530.md`
- `docs/reviews/mvp-gate4-final-assembler-cli-plan-decision-20260530.md`
- `docs/reviews/mvp-gate4-final-assembler-slice4a-controller-judgment-20260530.md`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/final_chapter_assembler.py`

## Changed Files

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/README.md`
- `docs/reviews/mvp-gate4-llm-service-implementation-evidence-20260530.md`

## Implementation Decisions

- Added `FundLLMAnalysisResult` typed dataclass with `structured_data`, `final_judgment_decision`, `llm_orchestration_result`, `final_assembly_result`, `quality_gate_result`, and `quality_gate_not_run_reason`.
- Added `FundLLMAnalysisResult.report_markdown` fail-closed property: returns `final_assembly_result.report_markdown` only when present; otherwise raises `ValueError` with orchestration status, final assembly status, and issue reasons.
- Added `FundAnalysisService.analyze_with_llm(request, *, llm_clients, chapter_policy=None, assembly_policy=None)`.
- `analyze_with_llm()` calls `_run_analysis_core(replace(request, command_source="analyze"))`; existing `QualityGateBlockedError` / `QualityGateNotRunBlockedError` propagate before any Gate 3 orchestration.
- Gate 3 input is built by `build_chapter_orchestration_input()` from `core_result.structured_data`; default `ChapterOrchestrationPolicy()` targets chapters `(1, 2, 3, 4, 5, 6)`.
- Gate 3 uses explicit injected `ChapterOrchestratorLLMClients`; production code does not construct real providers or fake clients.
- Gate 4 `assemble_final_chapters()` is always called after Gate 3 returns, including accepted / partial / blocked results; no deterministic renderer fallback is used in LLM path.
- `analyze()` and `checklist()` behavior was not changed.
- `tests/README.md` was updated because a new Service test file was added.

## Validation

```text
$ uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/services/test_fund_analysis_service_llm.py
All checks passed!
```

```text
$ uv run pytest tests/services/test_fund_analysis_service_llm.py -q
.......                                                                  [100%]
7 passed in 0.61s
```

```text
$ uv run pytest tests/services/test_final_chapter_assembler.py tests/services/test_chapter_orchestrator.py -q
............................................                             [100%]
44 passed in 0.53s
```

```text
$ uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1061 passed in 5.06s
Required test coverage of 50% reached. Total coverage: 91.73%
```

```text
$ git diff --check
<clean>
```

## Boundary Evidence

- Static import test in `tests/services/test_fund_analysis_service_llm.py` verifies `fund_analysis_service.py` does not import direct documents/repository/cache/pdf/source/downloader/parser/host/dayu/openai/httpx modules, while allowing the existing `fund_agent.fund.data_extractor` transition import.
- LLM path tests use fake extractor and fake writer/auditor only inside tests.
- Missing auditor client test verifies typed blocked orchestration plus incomplete final assembly, and `report_markdown` raises instead of returning deterministic markdown.
- Deterministic `analyze()` and `checklist()` tests verify those paths do not call writer/auditor fake clients.

## Final Workspace Status

```text
$ git status --short
 M fund_agent/services/__init__.py
 M fund_agent/services/fund_analysis_service.py
 M tests/README.md
?? --help
?? docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/reviews/repo-review-20260527-215953.md
?? docs/reviews/repo-review-20260527-225303.md
?? docs/tmux-agent-memory-store.md
?? reviews/
?? tests/services/test_fund_analysis_service_llm.py
```

注：本 evidence artifact 自身在写入后也属于本 slice 新增文件；上述 status 是写入 artifact 前的最终检查结果。无关 untracked 未 stage、未删除、未修改。

## Residuals

- Slice 4C CLI `--use-llm` remains unimplemented.
- Slice 4D production LLM provider construction remains a separate future gate.
- Chapter 0/7 LLM polish, LLM audit, Evidence Confirm / E2 source verification remain out of scope.
- Host/Agent/dayu integration remains deferred to Route C Gate 5.
- No commit was created by this implementation worker.

## Self-check

pass：当前动作仍属于 assigned implementation gate；只触碰 allowed files；没有 commit/push/PR；validation 已完成；residuals 已列明并交回 controller。
