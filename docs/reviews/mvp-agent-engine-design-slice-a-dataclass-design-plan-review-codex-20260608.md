# MVP Agent Engine Design Slice A Dataclass Design Plan Review Codex

## 1. Verdict

`PASS_WITH_NON_BLOCKING_OBSERVATIONS`

Reviewed target:

- `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md`

Scope:

- Same-repo design-only adversarial plan review.
- No implementation, source edit, test edit, control-doc edit, provider/live/runtime action, PR, push or commit.

Review timestamp from local system clock:

- `20260608-011800`

## 2. Findings Ordered By Severity

No blocking findings.

### NBO-1-未修复-中-runtime diagnostics 安全投影需在后续实现计划中显式化

- **位置**: `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:184`, `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:204`, `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:316`
- **问题类型**: 契约缺失 / ToolTrace 安全边界 / 不可直接实施
- **当前写法**: Slice A 正确要求 `ToolTrace` 不包含 prompt、draft、raw provider response、raw audit response、API key、Authorization header、bearer token、model value 或 base URL value；但 `ChapterTask` mapping 写入了 current prompt/runtime diagnostics，`ChapterAttempt.runtime_diagnostics` 只描述为 safe scalar runtime diagnostics。
- **反例/失败场景**: 后续 implementation agent 若把 current `ChapterLLMRuntimeDiagnostic` 原样搬进 Agent nested state，再从 nested state 生成 trace 或 retained diagnostics，会携带当前字段 `model_name`。当前代码里该字段是 provider 返回模型名，不满足 parent gate 的 safe diagnostics 禁止项。
- **为什么有问题**: Plan 自身在 `AgentReportRun` 边界禁止 model value，但 nested `ChapterAttempt.runtime_diagnostics` 没有给出 allowlist 投影规则；这会让“ToolTrace 安全”依赖实现者自行理解，而不是由 plan contract 约束。
- **直接证据**:
  - Plan 要求 `AgentReportRun` 不携带 model/base URL value：`docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:120`
  - Plan 将 runtime diagnostics 映射进 future Agent state：`docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:184`
  - Plan 的 `ChapterAttempt.runtime_diagnostics` 未列 allowlist：`docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:204`
  - Plan 的 `ToolTrace` 禁止项本身是正确的：`docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:316`
  - 当前 runtime diagnostic 包含 `model_name` 字段：`fund_agent/services/chapter_orchestrator.py:218`, `fund_agent/services/chapter_orchestrator.py:251`
- **影响**: 后续实现计划可能生成一个 trace-safe 但 Agent nested state 不安全的模型；review 需要额外追问哪些 diagnostics 可序列化。
- **建议改法和验证点**: 后续 Slice B/D 或 implementation plan 应把 Agent runtime diagnostics 定义为 allowlist projection，例如仅保留 category、status_code、request_id、elapsed_ms、finish_reason、response_chars、prompt char/token counts 等已允许标量，并明确排除 `model_name`、base URL、API key/header、prompt、draft、raw provider/audit response。验证点应断言 Agent serialized state 和 ToolTrace 均不含这些禁用字段。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中
- **阻断性**: 非阻断。当前 artifact 未授权实现，且 `ToolTrace` section 已明确排除用户要求的禁用项。

## 3. Parent NBO Follow-Up Assessment

### NBO-1 EvidenceAvailability Invocation Point

Assessment: resolved for Slice A.

- Parent requirement: Slice A/B must specify whether Agent invokes `derive_evidence_availability()` once at a bounded lifecycle point, keep it same-source, avoid retained artifacts/filesystem/external state, and prevent repair-attempt drift.
- Slice A states Agent derives `EvidenceAvailability` exactly once after `ChapterFactProjection` is available and before first `ChapterTask` enters `prepared`, stores it on `AgentReportRun`, passes the same value to every `ChapterTask`, and forbids recomputation/read of retained artifacts/filesystem/external state across repair attempts.
- Current code consistency: current Service derives typed inputs once before chapter loop and passes the same `_TypedTemplateInputs` through `_run_single_chapter`; initial and repair writer inputs read `typed_inputs.evidence_availability` from that same object.

Evidence:

- Parent NBO-1: `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md:52`
- Slice A resolution: `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:134`
- Current one-run typed input handoff: `fund_agent/services/chapter_orchestrator.py:679`
- Current initial writer availability use: `fund_agent/services/chapter_orchestrator.py:1081`
- Current repair writer availability reuse: `fund_agent/services/chapter_orchestrator.py:1275`

### NBO-2 Equivalence Test Scope

Assessment: intentionally deferred.

- Parent judgment allows Slice D or later implementation planning gate to define equivalence criteria before code changes.
- Slice A includes a current-to-future mapping matrix and does not claim to settle full equivalence testing.

Evidence:

- Parent NBO-2 defer point: `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md:58`
- Slice A mapping matrix: `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:348`

### NBO-3 FinalAssemblyReadiness Handoff Boundary

Assessment: resolved for Slice A.

- Parent requirement: future design slices must state whether Agent `FinalAssemblyReadiness` feeds or replaces current Service final assembly readiness; Service final product fail-closed mapping and stdout semantics remain unchanged until later implementation gate.
- Slice A states Agent readiness is a body-readiness handoff, not a replacement; it feeds Service final assembly; Service retains final product fail-closed mapping, chapter 0/7 assembly, stdout/stderr behavior and quality policy.
- Current code consistency: Service `assemble_final_chapters()` still builds readiness, decides incomplete/accepted status and controls whether `report_markdown` exists.

Evidence:

- Parent NBO-3: `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md:64`
- Slice A handoff statement: `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:319`
- Current Service final assembly authority: `fund_agent/services/final_chapter_assembler.py:263`
- Current Service readiness construction: `fund_agent/services/final_chapter_assembler.py:476`

## 4. Scope And Forbidden-Action Audit

Scope preserved.

- Service/Host/Agent/Fund ownership is explicit and matches parent gate: Service retains use case, ExecutionContract, provider construction, runtime ceilings, quality policy and final product fail-closed mapping; Host remains lifecycle-only; Fund remains domain/tool owner; future Agent owns execution mechanics only after a separate implementation gate.
- `EvidenceAvailability` is same-source, run-level, derived once and reused across attempts.
- `FinalAssemblyReadiness` feeds current Service final assembly and does not replace current Service final fail-closed authority.
- Current-to-future mapping is sufficient for Slice A design review, with the non-blocking diagnostics projection caveat above and NBO-2 equivalence testing deferred as parent judgment allows.
- `ToolTrace` safety explicitly excludes prompt, draft, raw provider response, raw audit response, API key, Authorization header, bearer token, model value and base URL value.
- The plan does not authorize source/test/control-doc edits, live `--use-llm`, provider readiness, curl, DNS, socket or endpoint probes, provider/default/runtime/budget/config changes, quality gate/golden/readiness changes, score-loop, multi-year runtime, public chapter id changes, PR, push or commit.

Evidence:

- Current control next entry and forbidden scope: `docs/current-startup-packet.md:19`, `docs/current-startup-packet.md:22`, `docs/implementation-control.md:68`, `docs/implementation-control.md:71`
- Four-layer boundary: `AGENTS.md:91`, `AGENTS.md:103`, `AGENTS.md:109`, `AGENTS.md:115`, `docs/design.md:45`
- Accepted future Agent boundary: `docs/design.md:63`
- Plan non-goals: `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:74`
- ToolTrace safety: `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md:312`

## 5. Validation Commands And Results

Commands run:

```text
git branch --show-current
```

Result: pass; output `feat/mvp-llm-incomplete-run-artifacts`.

```text
git status --short
```

Result: pass; workspace is dirty before this review. Notable in-scope untracked target plan exists; unrelated modified/untracked files were not touched.

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md
```

Result: pass; no whitespace errors.

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-review-codex-20260608.md
```

Result: pass; no whitespace errors.

No live provider, network, curl, DNS, socket, endpoint, PR, push, commit, source edit, test edit or control-doc edit command was run.

## 6. Residual Risks Or Open Questions

- Later Slice B/D or implementation planning must turn diagnostics safety into an explicit allowlist projection, not a reuse of current runtime diagnostic dataclasses.
- Later Slice D or implementation planning still owns full no-live equivalence criteria, including accepted/partial/fail-closed chapter outcome matrix, terminal failure categories, repair budget semantics and no weaker final assembly readiness.
- If future multi-year evidence changes `ChapterFactProjection` shape, Slice A correctly says the EvidenceAvailability invocation point cannot change without a separate implementation gate.
