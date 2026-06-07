# MVP Agent Engine Design Slice D No-Live Equivalence Validation Plan Review (DS)

## 1. Verdict

**PASS_WITH_NON_BLOCKING_OBSERVATIONS**

Plan artifact reviewed:
- `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md`

This review does NOT authorize implementation, source edits, tests, provider calls, runtime changes, PR, push, commit, or live `--use-llm`.

## 2. Findings

### NBO-1: Terminal Category Mapping Missing Three Current Stop Reason Values

- **File**: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md`
- **Section**: 5.2 Terminal Category Equivalence (lines 95–110)
- **Severity**: Non-blocking observation

The plan's 5.2 mapping table declares "required minimum mappings" with 10 mapping groups, but three current `ChapterRunStopReason` literal values are not explicitly covered:

1. `fund_type_unknown` (line 57 in `chapter_orchestrator.py`)
2. `writer_blocked` (line 59, originating from `prompt_only` where no LLM call was made)
3. `llm_unavailable` (line 64)
4. `llm_empty_response` (line 65)

These have observable current behavior:
- `writer_blocked` → the chapter was blocked before reaching a provider call (distinct from provider runtime or content contract block)
- `llm_unavailable` / `llm_empty_response` → provider-side issues that are not timeout/rate-limit/malformed/network/exception
- `fund_type_unknown` → fund identity resolution failure, closer to fact gap than scope exclusion

The plan explicitly defers full mapping to the implementation planning gate (line 95–96: "Future implementation planning must provide a mapping table"), so this is non-blocking. The implementation planning gate should ensure no current stop reason is silently dropped.

**Recommendation**: Add a note in Section 5.2 stating that `fund_type_unknown`, `writer_blocked`, `llm_unavailable`, and `llm_empty_response` must also have explicit future Agent terminal mappings, even if grouped under existing categories.

### NBO-2: `request_id` Allowlist Constraint Not Explicitly Referenced

- **File**: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md`
- **Section**: 5.5 ToolTrace Safe Scalar Equivalence (line 183, "allowlisted request id scalar")
- **Severity**: Non-blocking observation

The plan lists "allowlisted request id scalar" as an allowed diagnostic assertion. Slice B Codex NBO-1 (accepted followup in controller judgment Section 4) explicitly required that `request_id` must be "an optional scalar from an explicit response-header allowlist only" and that ToolTrace "must not serialize arbitrary response headers, full header maps, provider URLs, cookies, Authorization headers or provider config values."

The current wording "allowlisted request id scalar" implicitly captures this constraint, but does not reiterate the explicit response-header allowlist rule. The implementation planning gate that designs ToolTrace serialization could interpret "allowlisted" differently (e.g., any allowlist, not specifically response-header).

**Recommendation**: Expand line 183 to read "allowlisted request id scalar (from explicit response-header allowlist only)" or add a footnote referencing the Slice B Codex NBO-1 constraint.

### NBO-3: `ChapterFailureCategory` Mappings Not Included in 5.2 Mapping Table

- **File**: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md`
- **Section**: 5.2 Terminal Category Equivalence (lines 93–110)
- **Severity**: Non-blocking observation

Section 5.2's preamble says the implementation plan must provide "a mapping table from current `ChapterRunStopReason` / `ChapterFailureCategory` to future Agent terminal state" (emphasis added). The mapping table that follows only covers `ChapterRunStopReason` values, not `ChapterFailureCategory` values.

Current `ChapterFailureCategory` values (`provider_runtime`, `llm_timeout`, `prompt_contract`, `audit_parse`, `audit_rule_too_strict`, `fact_gap`, `code_bug`) are a parallel classification axis. Some are implicit in the stop reason groupings (e.g., `prompt_contract` maps to content/contract blocked), but `audit_rule_too_strict` and `code_bug` don't have explicit current→future mapping entries.

Future Agent terminal states may consolidate or split these two axes differently, and the implementation planning gate should address both.

**Recommendation**: Clarify whether the implementation planning gate must also map `ChapterFailureCategory` values, or limit the 5.2 scope to `ChapterRunStopReason` only and handle `ChapterFailureCategory` separately.

### NBO-4: Equivalence Matrix Omits Non-Live Stop Reason Scenarios

- **File**: `docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md`
- **Section**: 5.1 Chapter Outcome Matrix (lines 73–91)
- **Severity**: Non-blocking observation

The 5.1 equivalence matrix covers 8 scenarios (all accepted, writer blocked, provider timeout, provider network, audit blocked, needs_more_facts, repair budget exhausted, mixed). These are well chosen. However, two edge scenarios observable in current tests are not explicitly in the matrix:

1. `fund_type_unknown` / `dependency_missing` → these are not "failed chapters" per se but precondition failures (test at line 525: `test_missing_writer_or_auditor_blocks_without_deterministic_fallback`)
2. `llm_unavailable` → a writer-level precondition failure distinct from provider runtime exceptions

These are covered by the terminal mapping in 5.2 and by the minimum assertions in 5.1 ("generated/attempted chapter ids must remain row-complete"), so this is non-blocking.

## 3. Positive Findings

The following review focus areas all PASS:

1. **Equivalence criteria concreteness (Section 5)**: The matrix (5.1), terminal mapping (5.2), repair budget rules (5.3), final assembly assertions (5.4), and ToolTrace safety assertions (5.5) are collectively concrete enough for a later implementation planning gate to work from. Each section provides specific current→future expectation pairs with explicit minimum assertions.

2. **No-live constraints enforceability (Section 6)**: The plan defines a closed set of allowed test commands, explicitly enumerates allowed test doubles (fake clients, MockTransport, monkeypatch, in-memory data), and lists forbidden validation categories (real provider API, live command, readiness check, endpoint probe, retained artifact as sole source). Section 7 further requires the implementation plan to include its own explicit no-live and forbidden command lists, creating a double enforcement layer.

3. **Final assembly readiness not weakened (Section 5.4)**: All five minimum assertions preserve the current fail-closed semantics: accepted body chapters only, partial/blocked → no complete markdown, Ch0/Ch7 blocked if body readiness absent, blocked chapters excluded from source, Service authority preserved. This is consistent with the Slice A accepted design fact that "Agent `FinalAssemblyReadiness` feeds Service final assembly, does not replace Service authority."

4. **Repair budget and provider runtime budget remain separate (Section 5.3)**: Eight explicit preservation rules enforce separation. Notable specifics: "provider timeout retry attempts do not consume content repair budget" (line 121), "provider runtime failures do not trigger content repair" (line 122), "hidden Agent retry remains forbidden" (line 127). All consistent with Slice C's accepted `hidden_retry_allowed=false`.

5. **ToolTrace safety assertions are complete (Section 5.5)**: The forbidden list of 14 items is comprehensive and covers all parent artifact requirements (Slice A Codex NBO-1, Slice B safety assertions, Slice C Codex NBO-1). The allowed list of 19 items is appropriately scoped to safe scalars only.

6. **No implementation or live/provider scope authorized**: Section 1, Section 4 (12 categories of forbidden actions), Section 6 ("Slice D does not run these commands now"), and Section 10 (stop conditions) all explicitly prevent scope creep. The plan is a true design-only artifact.

## 4. Parent Follow-Up Assessment

| Parent finding | Slice D coverage | Status |
|---|---|---|
| Slice A NBO-2: equivalence test scope underspecified | Section 5 defines explicit equivalence criteria and Section 7 requires implementation plan to include in-scope tests | **Resolved**: criteria are now concrete enough for implementation planning |
| Slice B Codex NBO-1: `request_id` safe projection shape | Section 5.5 includes "allowlisted request id scalar" in allowed diagnostics | **Partially resolved**: see NBO-2 for explicit allowlist constraint |
| Slice C DS NBO-1: Terminal state name mapping | Section 5.2 provides a 10-group initial mapping; full table deferred to implementation | **Partially resolved**: mapping framework present; see NBO-1/NBO-3 for completeness gaps |
| Slice C DS NBO-3: Design-only validation is minimal | Section 5 provides equivalence criteria; Section 6 provides no-live validation commands; Section 7 requires implementation plan to include contract-level coverage | **Resolved**: criteria are now defined |
| Slice C Codex NBO-1: Host interruption scheduler-normalized | Section 5.1 implicitly preserves Host boundary separation; not directly addressed in Slice D scope | **Correctly deferred**: Host/Agent scheduling is an implementation concern |
| Chapter-attributed blocked reasons (deferred from Slice A) | Not addressed in Slice D | **Still deferred**: correctly remains in implementation planning scope |

## 5. Scope and Forbidden-Action Audit

### Forbidden actions NOT authorized by this plan:

| Category | Checked? | Result |
|---|---|---|
| Agent runtime implementation | Section 1, 4, 10 | PASS — explicitly forbidden |
| `fund_agent/agent` creation | Section 4, 10 | PASS — explicitly forbidden |
| ToolRegistry / ToolTrace / adapter implementation | Section 4 | PASS — explicitly forbidden |
| `ChapterOrchestrator` code migration | Section 4 | PASS — explicitly forbidden |
| Test addition/editing in this gate | Section 4 | PASS — explicitly forbidden |
| Provider / default / runtime / budget / config change | Section 4, 10 | PASS — explicitly forbidden |
| Live `--use-llm`, retry, endpoint/network probe | Section 4, 6, 10 | PASS — explicitly forbidden |
| Quality gate / golden / readiness / score-loop change | Section 4, 10 | PASS — explicitly forbidden |
| Multi-year runtime / public chapter ids change | Section 4 | PASS — explicitly forbidden |
| dayu-agent / LangGraph / MCP runtime | Section 4 | PASS — explicitly forbidden |
| PR / push / merge / external comment | Section 4, 10 | PASS — explicitly forbidden |
| Source edit / test edit / control-doc edit | Section 1, 4 | PASS — plan artifact only |

### Reviewer actions NOT performed:

- No live provider call, `--use-llm`, curl, DNS, socket, or endpoint probe
- No source, test, or control-doc edits
- No PR, push, commit, or external state change
- Review is read-only analysis plus write to allowed review artifact path only

## 6. Validation Commands and Results

```text
$ git branch --show-current
feat/mvp-llm-incomplete-run-artifacts

$ git status --short
M pyproject.toml
?? docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md
?? docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-ds-20260608.md
... (other untracked review artifacts unrelated to this gate)

$ git diff --check -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md
(exit 0, no whitespace errors)

$ git diff --check -- docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-d-no-live-equivalence-validation-plan-review-ds-20260608.md
(exit 0, no whitespace errors)
```

## 7. Residual Risks and Open Questions

1. **Terminal category enumeration completeness**: The implementation planning gate will need to exhaustively enumerate all 23 current `ChapterRunStopReason` values (not just the 10 groups listed in 5.2) and all 7 `ChapterFailureCategory` values, ensuring no current value is silently dropped or misclassified. Residual risk is low because the plan explicitly defers this to implementation planning.

2. **Future Agent state name instability**: The plan allows that "future state names may differ, but the fail-closed meaning must not weaken" (line 112). This is reasonable for a design-only gate, but the implementation planning gate should pin exact future state names before code changes, per Slice C DS NBO-1.

3. **`request_id` serialization precision**: The ToolTrace safety assertions are comprehensive but the `request_id` derivation rule (explicit response-header allowlist) is implicit in the wording "allowlisted." The implementation planning gate should make this explicit.

4. **MiMo absence**: AgentMiMo remained unavailable. AgentDS review is the first independent review. Per operator authorization, Codex review should provide the second independent review.

## 8. Artifact Readiness

This review finds zero blocking findings. The plan artifact is ready for controller judgment.
