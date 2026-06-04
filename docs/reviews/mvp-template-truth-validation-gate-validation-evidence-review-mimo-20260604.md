# MVP Template Truth Validation Gate — Validation Evidence Review (MiMo)

## 1. Review Context

- Review target: `docs/reviews/mvp-template-truth-validation-gate-validation-evidence-20260604.md`
- Plan: `docs/reviews/mvp-template-truth-validation-gate-plan-20260604.md`
- Controller judgment: `docs/reviews/mvp-template-truth-validation-gate-plan-controller-judgment-20260604.md`
- Gate: `MVP typed-template-to-agent report generation stabilization phase / Gate 1 Template truth validation gate`
- Review role: AgentMiMo，validation evidence independent review
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Rule truth: `AGENTS.md`

Review scope：独立 review validation evidence artifact，不实现、不修改被审 evidence、不 commit、不 push、不创建 PR、不运行 live provider / promotion / golden readiness / snapshot refresh / release readiness。

## 2. Findings

**PASS / no blocking findings.**

以下为逐 lens 审查结论：

### 2.1 A1-A8 Current Direct Evidence（无旧日志依赖）

- V1-V7 共 7 条 validation command，每条记录完整命令、exit code、stdout 摘要、stderr 摘要。
- 所有命令均为当前执行结果，不依赖旧日志、旧 aggregate review 或间接结论。
- Criterion mapping 在每条命令和 Acceptance Criteria Matrix 中均有明确绑定。
- **结论：PASS。**

### 2.2 Canonical JSON Truth Source / Untyped-Typed Same-Source Projection / Chapter IDs 0-7 / Ch2 Internal Subcontract Boundary

- V1（`--validate-template-doc`）直接验证 canonical JSON 可被当前 untyped parser 读取、投影并 fail-closed 校验，报告 `template_contract_manifest=valid`、`chapters=8`。
- V2（`test_contracts.py` + `test_typed_contracts.py`，46 passed）覆盖 untyped/typed projection、public chapter ids `0-7`、stale `source_manifest` fail-closed、Ch2 internal subcontract 边界。
- 代码验证确认：`_EXPECTED_CHAPTER_IDS = tuple(range(8))`、`EXPECTED_PUBLIC_CHAPTER_IDS = tuple(range(8))`、Ch2 `public_chapter_id must be None`、`audit_focus` 闭集校验 `AUDIT_FOCUS_IS_SEMANTIC_ONLY = True`。
- **结论：PASS。**

### 2.3 Same-Source Consumers 覆盖

| Consumer | Evidence | 命令映射 |
|---|---|---|
| `EvidenceAvailability` | V4（9 passed） | `test_evidence_availability.py` |
| `chapter_writer` | V5（81 passed） | `test_chapter_writer.py` |
| `chapter_auditor` | V5（81 passed） | `test_chapter_auditor.py` |
| `ChapterOrchestrator` | V6（124 passed） | `test_chapter_orchestrator.py` |
| `chapter_contract_constraints` | V3（4 passed） | `test_chapter_contract_constraints.py` |

- 代码验证确认 `EvidenceAvailability` 模块 docstring 声明不读取 repository/PDF/cache/source helper/Service/Host/provider/dayu；writer 要求显式 `EvidenceAvailability` 且缺 mapping/behavior fail-closed；auditor 用 `EvidenceAvailability` 执行 typed Ch3 `must_not_cover` 且未知 requirement fail-closed；orchestrator typed path 由 `typed_template_path="typed_template_contract"` 选择并派生 `EvidenceAvailability`、传 typed required-output items 和 `audit_focus`。
- **结论：PASS。**

### 2.4 No Deterministic Fallback / Incomplete Stdout Empty / Quality Gate Fail-Closed

- V6（`test_fund_analysis_service_llm.py`）覆盖：deterministic analyze/checklist 不调用 LLM orchestrator；missing/partial/incomplete LLM result 不回退 deterministic；quality fail-closed policy。
- V7（`test_cli.py`，74 passed）覆盖：CLI `--use-llm` incomplete stdout 为空、exit 1；quality gate block/not-run 保持 exit 2 且 stderr structured。
- 代码验证确认：`test_missing_writer_or_auditor_blocks_without_deterministic_fallback` 断言 `status == "blocked"` 且 `report_markdown is None`；`test_use_llm_incomplete_typed_readiness_empty_stdout_exit_one` 断言 `exit_code == 1` 且 `stdout == ""`；`test_analyze_cli_structured_quality_gate_block` 断言 `exit_code == 2`。
- **结论：PASS。**

### 2.5 Pre/Post Integrity（只新增允许 evidence artifact）

- Pre-validation：`git branch` = `feat/mvp-llm-incomplete-run-artifacts`；`git diff --name-only` 为空；`git status --short` 显示 pre-existing untracked files。
- Post-validation：`git branch` 不变；`git diff --name-only` 为空（无 staged 或 modified 文件）；`git status --short` 仅新增允许 artifact `docs/reviews/mvp-template-truth-validation-gate-validation-evidence-20260604.md`。
- 无 source / test / config / runtime behavior / design doc / control doc / startup packet / plan / review / controller judgment 文件被修改。
- **结论：PASS。**

### 2.6 A8 Forbidden-Scope Checklist 完整性

Evidence Section 6 包含 21 项 forbidden-scope checklist，逐项确认 PASS：

- 无 live provider、real LLM smoke、provider runtime/live probe
- 无 promotion、golden readiness、snapshot refresh、strict correctness rerun、release readiness
- 无 push、PR creation/状态变更
- 无 external state action
- 无 Agent runtime implementation、Host/Agent durable runtime / tool-loop / ToolRegistry / ToolTrace / multi-year runtime / score-loop / `chapter_generation_score`
- 无 `dayu-agent` / `dayu.host` / `dayu.engine` 直接依赖
- 无生产 PDF/cache/source helper 直接读取
- 无 `extra_payload` 显式业务参数
- 无 auditor / quality gate / fail-closed 语义放松
- 无 deterministic fallback for incomplete LLM result
- 无 half-finished report stdout
- public chapter ids 保持 `0-7`

Checklist 完整，未遗漏 controller judgment 要求的 forbidden-scope 项。
- **结论：PASS。**

### 2.7 V1 RuntimeWarning 裁决

V1 stderr 包含：

```text
<frozen runpy>:128: RuntimeWarning: 'fund_agent.fund.template.contracts' found in sys.modules after import of package 'fund_agent.fund.template', but prior to execution of 'fund_agent.fund.template.contracts'; this may result in unpredictable behaviour
```

**裁决：harmless warning，non-blocking residual。**

理由：
- 这是 Python `runpy` 在 `-m` 执行模块时的 import 顺序提示，因 `fund_agent.fund.template` 包的 `__init__.py` 可能间接触发了 `contracts` 模块的 import。
- V1 命令 exit code = 0，输出 `template_contract_manifest=valid`，功能验证正常通过。
- V2（46 tests passed）进一步确认 `contracts.py` 和 `typed_contracts.py` 的完整功能正确性，不依赖 `-m` 执行路径。
- 该 warning 不影响一次性 validation 命令的正确性；按 plan Section 10 residual 分类，属于 future developer tooling / import hygiene cleanup 范畴，不是当前 gate blocker。
- **结论：non-blocking residual，不阻断 gate。**

### 2.8 A6 Explicit Mapping（controller judgment 要求）

Controller judgment DS-1 要求 evidence 显式映射 `test_execution_contract.py` 到 A6 具体覆盖项。Evidence Section 5 A6 row 声明：

> `test_execution_contract.py` is direct evidence for request/runtime policy consistency, `typed_template_path` consistency, and mismatch fail-closed behavior.

该映射已记录在 Acceptance Criteria Matrix A6 row 和 V6 criterion mapping 中，满足 controller judgment 的 evidence-recording precision 要求。
- **结论：PASS。**

## 3. Verdict

**Verdict: PASS**

- Blocking findings: **0**
- Non-blocking residuals: **1**（V1 RuntimeWarning，harmless import order warning，future import hygiene cleanup）
- 所有 A1-A8 acceptance criterion 均有 current direct evidence，不依赖旧日志或旧 aggregate review
- 命令结果足以验证 canonical JSON truth source、untyped/typed same-source projection、chapter ids 0-7、Ch2 internal subcontract boundary
- same-source consumers 全部覆盖：EvidenceAvailability、chapter_writer、chapter_auditor、ChapterOrchestrator、chapter_contract_constraints
- no deterministic fallback、incomplete stdout empty、quality gate/fail-closed 语义均由 service/CLI tests 覆盖
- pre/post integrity 证明只新增允许 evidence artifact，未修改 source/test/config/runtime behavior
- A8 forbidden-scope checklist 完整，未误运行任何 forbidden scope 命令
- V1 RuntimeWarning 是 harmless warning，non-blocking residual
