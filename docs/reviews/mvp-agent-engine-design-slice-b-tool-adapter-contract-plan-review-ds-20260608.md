# MVP Agent Engine Design Slice B Tool Adapter Contract Plan Review DS

## 1. Verdict

`PASS`

No blocking findings. The plan correctly defines future ToolRegistry adapter contracts that wrap existing Fund primitives, preserves EvidenceAvailability as run-level non-tool precomputation, keeps provider clients Service-constructed, defines a comprehensive ToolTrace allowlist that excludes all sensitive fields, separates provider runtime errors from content repair, and mandates programmatic-first audit ordering. No implementation, live provider, runtime/config change, or external scope is authorized.

## 2. Required Source-of-Truth Files Read

| File | Status |
|---|---|
| `AGENTS.md` | read |
| `docs/current-startup-packet.md` | read |
| `docs/implementation-control.md` (current gate section) | read (lines 1–100, current gate at line 68–71) |
| `docs/design.md` (Agent engine, four-layer boundary sections) | read (lines 1–150, 515–564) |
| `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md` | read |
| `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md` | read |
| `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-controller-judgment-20260608.md` | read |
| `fund_agent/fund/chapter_facts.py` | read (lines 1–80, public dataclasses and project function) |
| `fund_agent/fund/evidence_availability.py` | read (lines 1–80, availability dataclasses and derive function) |
| `fund_agent/fund/chapter_writer.py` | read (lines 1–80, writer input/result/draft and write_chapter) |
| `fund_agent/fund/chapter_auditor.py` | read (lines 1–80, audit input/result and audit functions) |
| `fund_agent/services/chapter_orchestrator.py` | read (diagnostic and safe serializer sections: lines 1–200, 690–770, 3250–3350) |

## 3. Findings

### 3.1 Tool Boundary Wraps Existing Fund Primitives Only

**Finding**: PASS

Plan Section 5 maps four tools to existing Fund primitives:

- `fund.project_chapter_facts` → `project_chapter_facts()` / `ChapterFactProvider.project()` — confirmed at `fund_agent/fund/chapter_facts.py:1` (public `project_chapter_facts` and `ChapterFactProvider`)
- `fund.write_chapter` → `write_chapter()` — confirmed at `fund_agent/fund/chapter_writer.py:1`
- `fund.audit_programmatic` → `audit_chapter_programmatic()` — confirmed at `fund_agent/fund/chapter_auditor.py:1`
- `fund.audit_semantic` → `audit_chapter_llm()` — confirmed at `fund_agent/fund/chapter_auditor.py:1`

None of these tool definitions introduce new Fund logic or rewrite existing primitives. Each tool contract (Sections 6.1–6.5) describes a typed wrapper with input/output schema identities, safe identity projection, and error taxonomy — all derivable from the current primitive signatures.

The plan correctly excludes from ToolRegistry: `derive_evidence_availability()` (run-level precomputation, Section 5 line 105), provider writer/auditor clients (Service-constructed, Sections 5 and 6.3/6.5), Service final assembly, and Host lifecycle.

### 3.2 EvidenceAvailability Remains Run-Level Non-Tool Precomputation

**Finding**: PASS

Plan Section 5 explicitly lists `derive_evidence_availability()` as "not registry tools" (line 105). Section 6.2 defines the contract:

- invoked exactly once after `ChapterFactProjection` exists (lines 158–159);
- result stored on `AgentReportRun.evidence_availability` (line 160);
- all `fund.write_chapter` calls receive the same value or immutable copy (line 161);
- repair attempts reuse the same value (line 162);
- no recomputation from retained artifacts, filesystem state or external state (line 163).

This directly satisfies Slice A controller judgment DS NBO-4 disposition (`accepted_design_refinement`, Section 4 of the Slice A judgment) and is consistent with `design.md:63` ("`EvidenceAvailability` 是基于 same-source `ChapterFactProjection` 的预计算派生输入，不是 registry tool").

The safe identity (lines 165–175) and forbidden identity (lines 177–181) contract is complete and consistent with the current `evidence_availability.py` dataclass fields.

### 3.3 Provider Clients Remain Service-Constructed Per-Run Fields

**Finding**: PASS

Plan Section 5 (lines 106–108): "provider writer/auditor clients: Service-constructed typed per-run fields, passed into relevant Fund tool adapters but not registered as tools."

Section 6.3 (line 190): `fund.write_chapter` receives "Service-constructed writer `ChapterLLMClient | None` from per-run fields."
Section 6.5 (line 301): `fund.audit_semantic` receives "Service-constructed auditor `ChapterAuditLLMClient | None` from per-run fields."

This is consistent with `design.md:63` ("Provider writer/auditor clients 由 Service 构造并作为 explicit per-run typed fields 注入 `AgentReportRun`，Agent 再作为 typed tool input 传给 Fund tools；它们不是 ToolRegistry tool") and the parent plan Section 4 boundary rule (line 106 of parent plan: "Provider writer/auditor clients are not tools").

### 3.4 ToolTrace Allowlist Excludes All Sensitive Fields

**Finding**: PASS

Plan Section 7 defines comprehensive allowed and forbidden field lists.

Forbidden fields (lines 383–396) explicitly cover:
- `prompt text` ✓
- `draft markdown` ✓
- `fact values` ✓
- `anchor note text if it includes source prose` ✓
- `raw provider response` ✓
- `raw audit response` ✓
- `raw provider request/body` ✓
- `API key` ✓
- `Authorization header` ✓
- `bearer token` ✓
- `model value` ✓
- `base URL value` ✓
- `provider error message beyond existing redacted safe message policy` ✓

This matches the current `serialize_chapter_runtime_diagnostics()` (orchestrator.py:727) and `_runtime_diagnostic_payload()` (orchestrator.py:3258) which explicitly exclude `model_name`, `message`, prompt, draft, and raw response.

The runtime diagnostics rule (lines 399–407) correctly states Agent serialized state must not store `ChapterLLMRuntimeDiagnostic` wholesale and must use an allowlisted projection. This satisfies Codex NBO-1 from the Slice A controller judgment.

The `diagnostic_consistency_status` requirement (lines 404–407) pins values to the current `DiagnosticConsistencyStatus` literal set from `chapter_orchestrator.py:99-104`: `consistent`, `missing_terminal_runtime_diagnostic`, `terminal_category_conflict`, `non_runtime_terminal_without_scalar`. This satisfies DS NBO-7 from the Slice A controller judgment.

**Non-blocking observation (NBO-DS-1)**: Allowed fields include `prompt char counts` (line 376) and `approx prompt token counts` (line 377). These are scalar counts, not content. Since prompt TEXT is explicitly forbidden, this is secure by construction. The implementation plan should clarify that char/token counts are derived from length heuristics on the in-memory prompt, not from an external counting service or retained prompt content.

### 3.5 Error Taxonomy Separates Provider Runtime From Content Repair

**Finding**: PASS

Plan Section 8 defines a 14-category taxonomy with explicit retry/repair boundaries:

Provider runtime categories (lines 422–426): `provider_runtime_timeout`, `provider_runtime_rate_limited`, `provider_runtime_malformed_response`, `provider_runtime_network`, `provider_runtime_http_error` — all marked as "fail closed" or "Service/provider runtime category; not Agent content repair." `provider_runtime_rate_limited` explicitly forbids hidden Agent retry (line 423).

Content/contract categories: `writer_blocked`, `audit_programmatic_failed`, `audit_programmatic_blocked`, `semantic_audit_unavailable`, `semantic_audit_parse_blocked` — each has explicit repair semantics ("may feed repair only if issue semantics permit", "programmatic-first blocker", "fail closed unless policy disables semantic audit", etc.).

Input/infrastructure categories: `tool_input_invalid`, `tool_contract_error`, `tool_internal_error` — all "fail closed; code bug."

Final paragraph (lines 430–432): "Agent repair policy must not convert provider runtime categories into hidden content repair attempts." This satisfies the Slice A NBO-5 concern about hidden retry.

### 3.6 Programmatic Audit Before Semantic Audit, No Semantic Override

**Finding**: PASS

Plan Section 6.4 (lines 290–292): "Programmatic audit runs before semantic audit in future Agent scheduling. Programmatic blockers must not be overwritten by semantic audit pass."

Section 8 corroborates: `audit_programmatic_failed` → "deterministic audit found blocking issues" → "programmatic-first blocker" (line 418). `audit_programmatic_blocked` → "deterministic audit could not complete safely" → "fail closed" (line 419).

This matches `design.md:63` ("LLM auditor 只能作为 bounded semantic audit tool，不得覆盖 programmatic blockers") and the parent plan fail-closed invariant (Section 5: "programmatic audit before semantic audit").

**Non-blocking observation (NBO-DS-2)**: The plan uses `fund.audit_semantic` as the tool name while the underlying Fund primitive is `audit_chapter_llm()`. This rename (semantic vs llm) is a valid design choice within the plan's stated scope ("tool names" are among items the plan can decide per Section 2 line 26). The mapping is explicit in the tool table (Section 5). No ambiguity.

### 3.7 Scope and Forbidden-Action Audit

**Finding**: PASS

The plan explicitly forbids (Section 4, lines 77–89):
- creating `fund_agent/agent` ✓
- implementing ToolRegistry, ToolTrace, adapters or schemas ✓
- moving ChapterOrchestrator code ✓
- changing Fund primitive behavior ✓
- changing FundLLMExecutionContract or provider construction ✓
- putting provider clients into registry as tools ✓
- changing timeout, retry, provider, default model, base URL or budget ✓
- live `--use-llm`, retry, curl, DNS, socket, endpoint probes ✓
- `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph, MCP ✓
- quality gate, golden/readiness, score-loop, multi-year, public chapter ids ✓
- PR, push, merge, mark-ready, reviewer request ✓

The plan is consistently described as "design-only" throughout. No section authorizes implementation.

Validation scope (Section 9) is limited to local `git diff --check` only — consistent with a design-only artifact that makes no source/test changes.

### 3.8 Consistency With Parent Artifacts

| Parent requirement | Slice B compliance | Status |
|---|---|---|
| Agent Engine Design Refresh plan: tool boundary wraps existing Fund primitives | Section 5 tool table | PASS |
| Agent Engine Design Refresh plan: provider clients are not tools | Sections 5, 6.3, 6.5 | PASS |
| Slice A NBO-4: EvidenceAvailability is run-level, not tool | Sections 5, 6.2 | PASS |
| Slice A NBO-7: diagnostic_consistency_status must use current literal set | Section 7, lines 404–407 | PASS |
| Slice A Codex NBO-1: Agent serialized diagnostics must have allowlist | Section 7, lines 399–403 | PASS |
| Slice A NBO-5: hidden retry semantics (deferred to Slice C) | Section 8, lines 430–432 (addressed at taxonomy level; field definition deferred) | PASS (within Slice B scope) |
| design.md:63: programmatic-first audit, LLM auditor bounded | Sections 5, 6.4, 6.5, 8 | PASS |
| design.md:63: provider clients Service-constructed, not registry tools | Sections 5, 6.3, 6.5 | PASS |

## 4. Parent Slice A Follow-Up Assessment

| Slice A finding | Slice B status |
|---|---|
| DS NBO-4: EvidenceAvailability invocation point | Resolved — Section 6.2 explicitly defines run-level precomputation contract |
| DS NBO-5: hidden_retry_allowed semantics | Partially addressed — Section 8 forbids hidden Agent retry at taxonomy level; field-level definition remains deferred to Slice C per controller judgment |
| DS NBO-6: blocked_reasons chapter attribution | Not addressed — deferred to implementation planning gate per controller judgment; not in Slice B tool contract scope |
| DS NBO-7: diagnostic_consistency_status wording | Resolved — Section 7 pins to current DiagnosticConsistencyStatus literal set |
| Codex NBO-1: runtime diagnostics safe projection | Resolved — Section 7 mandates allowlisted projection, forbids wholesale storage of ChapterLLMRuntimeDiagnostic |

## 5. Validation Commands and Results

```text
$ git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md
(exit 0, no output — PASS)

$ git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-review-ds-20260608.md
(exit 0, no output — PASS)
```

Reviewer actions: read-only review. No source edits, tests, live `--use-llm`, provider readiness, curl, DNS, socket, endpoint probes, network checks, PR, push, or commit.

## 6. Residual Risks and Open Questions

1. **NBO-DS-1 (non-blocking)**: ToolTrace allowed `prompt char counts` and `approx prompt token counts` are secure as scalars, but the implementation plan should explicitly state the derivation method (length heuristics on in-memory prompt only, not retained or serialized).

2. **NBO-DS-2 (non-blocking)**: `host_interrupted` (Section 8, line 427) belongs in Host governance, not tool adapter error taxonomy. Including it for completeness is acceptable, but the implementation plan must ensure tool adapters do not implement Host lifecycle logic (cancel detection, deadline tracking). The plan's description "Host cancel/deadline observed at scheduling boundary or after tool return" correctly assigns observation to Agent scheduling, not tool adapters.

3. **Open question**: Whether `fund.audit_programmatic` results should feed directly into `fund.audit_semantic` input (e.g., programmatic issue ids constraining semantic audit focus) or whether the Agent repair policy mediates this handoff. The plan correctly does not decide this — it belongs in Slice C (Repair And Budget Contract).

4. **Open question**: The plan does not specify whether `fund.write_chapter` and `fund.audit_semantic` share the same provider client instance or receive independent instances. Since provider construction is Service-owned and clients are passed as per-run fields, this is a Service/policy decision, not a tool contract concern. No issue for Slice B.

## 7. Review Closeout

- Artifact reviewed: `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md`
- Verdict: PASS
- Blocking findings: 0
- Non-blocking observations: 2 (NBO-DS-1, NBO-DS-2)
- Artifact ready for controller judgment: YES
