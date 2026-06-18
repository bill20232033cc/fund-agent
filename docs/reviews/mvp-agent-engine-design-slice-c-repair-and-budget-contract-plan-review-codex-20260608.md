# MVP Agent Engine Design Slice C Repair And Budget Contract Plan Review - Codex

## 1. Verdict

`PASS_WITH_NON_BLOCKING_OBSERVATIONS`

Reviewed target:

- `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md`

Assigned scope:

- Design-only adversarial plan review.
- No implementation, source edits, tests, control-doc edits, live provider calls, provider readiness, curl, DNS, socket, endpoint probes, PR, push or commit.

## 2. Findings Ordered By Severity

No blocking findings.

### NBO-1-未修复-低-Host interruption signal should stay scheduler-normalized before repair policy input

- **位置**: `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:160` decision mapping; `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:172`; `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:211`
- **问题类型**: 架构边界 / 契约缺失
- **当前写法**: Plan maps `Host cancel/deadline observed` to `host_interrupted`, and later defines `host_interrupted` as observed at scheduling boundary or after tool return.
- **反例/失败场景**: Later implementation agent could place Host cancel/deadline inspection directly inside `RepairPolicy.decide`, because the row appears inside the repair decision contract rather than only in Agent scheduler lifecycle handling.
- **为什么有问题**: Design truth says Agent observes Host cancel/deadline at task scheduling boundaries and after tool-call return, while mid-tool-call interruption relies on provider timeout. Host owns lifecycle; repair policy should not inspect Host state.
- **直接证据**: `docs/design.md:63` assigns Host cancel/deadline observation to Agent scheduling boundaries and after tool-call return; `AGENTS.md:109`-`AGENTS.md:118` separate Host lifecycle governance from Agent execution; Slice B follow-up requires `host_interrupted` to stay scheduling boundary, not adapter implementation (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-controller-judgment-20260608.md:61`-`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-controller-judgment-20260608.md:65`).
- **影响**: Low implementation drift risk: an implementation worker might wire Host lifecycle details into repair policy instead of passing an already-normalized scheduler interruption signal.
- **建议改法和验证点**: In controller judgment or implementation planning, require `RepairPolicy.decide` to consume only an already-normalized interruption event/status emitted by Agent scheduling, and explicitly forbid importing or inspecting Host context/state in repair policy or tool adapters.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## 3. Parent Slice B Follow-Up Assessment

Slice C consumes the Slice B follow-ups sufficiently for a design-only plan:

- Prompt char/token counts: Slice C requires in-memory prompt length heuristics only and forbids serialized prompts, external token-count services and retained prompt reads (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:237`-`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:239`).
- `host_interrupted`: Slice C keeps the terminal state at scheduling boundary or after tool return (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:211`), with NBO-1 recorded to prevent implementation drift.
- `request_id`: Slice C pins it to an optional scalar from an explicit response-header allowlist, and forbids arbitrary header maps, provider URL, cookies, Authorization header or provider config values (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:241`-`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:243`).
- Hidden retry: Slice C defines `hidden_retry` and sets `hidden_retry_allowed=false` (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:128`-`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:142`).

## 4. Scope And Forbidden-Action Audit

- Service provider runtime budget remains separate from Agent content repair budget: `ProviderRuntimeBudget` currently owns provider timeouts, output chars and prompt payload mode (`fund_agent/services/execution_contract.py:133`-`fund_agent/services/execution_contract.py:152`); Slice C keeps these Service-owned and makes Agent content repair budget separate (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:86`-`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:126`).
- Provider timeout retry remains provider-client behavior only: `_complete()` retries only `httpx.TimeoutException`; transport, rate limit, HTTP and malformed responses fail closed without retry (`fund_agent/services/llm_provider.py:259`-`fund_agent/services/llm_provider.py:295`; `fund_agent/services/llm_provider.py:296`-`fund_agent/services/llm_provider.py:418`). Slice C preserves that boundary (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:103`-`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:105`).
- Fund issue ids and repair hints remain Fund-owned semantics: `ChapterAuditRepairHint` and issue ids are defined in Fund (`fund_agent/fund/chapter_auditor.py:47`; `fund_agent/fund/chapter_auditor.py:310`-`fund_agent/fund/chapter_auditor.py:337`); Slice C says Agent must not redefine Fund issue meaning (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:146`-`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:159`).
- `needs_more_facts` does not source-probe: current `_decide_repair()` maps it to terminal `needs_more_facts` and explicitly says Service does not source probe (`fund_agent/services/chapter_orchestrator.py:2280`-`fund_agent/services/chapter_orchestrator.py:2287`); Slice C preserves no source probing (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:167`; `docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:207`).
- Provider runtime failures do not trigger content repair: Slice C maps provider runtime timeout/rate-limit/malformed/network/http errors to stop with provider runtime stop reason (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:172`) and separately says provider runtime failure does not trigger content repair (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:125`).
- Diagnostics remain allowlist-only: current runtime diagnostic serializer excludes model name, message, prompt, draft, raw response, raw audit, provider body, API key and header (`fund_agent/services/chapter_orchestrator.py:727`-`fund_agent/services/chapter_orchestrator.py:735`) and payload only emits scalar/allowlisted fields (`fund_agent/services/chapter_orchestrator.py:3258`-`fund_agent/services/chapter_orchestrator.py:3301`). Slice C mirrors that rule (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:222`-`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:243`).
- No forbidden scope was authorized in the target plan: the plan forbids Agent package creation, implementation, provider/default/runtime/budget/config changes, live/provider probes, dayu runtime, quality/golden/score/multi-year/public chapter id changes, PR and push (`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:67`-`docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md:82`).

## 5. Validation Commands And Results

```text
git branch --show-current
```

Result: `feat/mvp-llm-incomplete-run-artifacts`.

```text
git status --short
```

Result: worktree contains pre-existing modified/untracked files, including untracked target plan; no unrelated files were edited by this review.

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md
```

Result: pass, exit code 0.

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-review-codex-20260608.md
```

Result: pass, exit code 0.

No live `--use-llm`, provider readiness, curl, DNS, socket, endpoint probe, network check, implementation scaffold, test run, source edit, control-doc edit, PR, push or commit was run.

## 6. Residual Risks Or Open Questions

- Slice D or implementation planning still owns equivalence testing and chapter-attributed blocked reason details inherited from Slice A/B (`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-controller-judgment-20260608.md:80`-`docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-controller-judgment-20260608.md:82`).
- NBO-1 should be handled in controller judgment or implementation planning, not by editing this plan during review.
