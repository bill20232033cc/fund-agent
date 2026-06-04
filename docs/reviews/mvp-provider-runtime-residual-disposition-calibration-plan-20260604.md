# MVP Provider Runtime Residual Disposition / Calibration Plan

## 1. Scope & Classification

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Preceding gate: `Real LLM smoke re-baseline gate` — blocked at evidence stage by `B3 provider_runtime_residual_all_chapters_llm_timeout`
- This gate: `Provider runtime residual disposition / calibration gate`
- Gate classification: `heavy` — real provider smoke evidence affects subsequent calibration sequencing; must preserve fail-closed/no-fallback/stdout safety semantics
- Role: planning worker (not controller); produces handoff-ready disposition plan only
- Allowed write: this artifact only
- Preceding accepted artifacts:
  - Configured evidence: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-20260604.md`
  - Controller judgment: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-controller-judgment-20260604.md`
  - Retained artifact: `reports/llm-runs/006597-2024-20260604T091239Z-host_run_b52b779e7e9a43c/`

## 2. Goal / Motivation

**Goal**: Produce a first-principles disposition of the `provider_runtime_residual_all_chapters_llm_timeout` blocker using existing retained diagnostic evidence, without any live provider interaction. The disposition must determine whether the residual is endpoint-level, runtime-policy-level, or evidence-insufficient, and must produce a calibration readiness assessment that either authorizes or defers a future live-evidence gate.

**Motivation**: The Real LLM smoke re-baseline gate cannot be accepted because all six body chapters fail with provider `ReadTimeout`. Before any provider default/runtime/budget change or Chapter acceptance calibration can be considered, the root cause must be classified from first principles using the existing same-run retained evidence. Jumping to live provider probes or timeout changes without this classification would be premature and risks masking the true residual.

## 3. Non-Goals

- No live provider smoke, probe, reachability check, or HTTP request of any kind
- No code, test, config, README, design doc, control doc, or startup packet changes
- No provider default, runtime default, timeout, attempt, backoff, model, endpoint, or budget changes
- No Chapter acceptance calibration (no chapter has accepted draft/conclusion)
- No Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/push/release
- No deterministic fallback introduction or fail-closed relaxation
- No env override setting or env-based timeout reconfiguration
- No historical artifact substitution for current same-run evidence
- No Chapter 3 `programmatic:C2` / `code_bug_other` calibration (separate residual, separate gate)

## 4. First-Principles Residual Classification

### 4.1 Direct Evidence Summary (Same-Run Retained Artifact)

All facts below are from the single retained artifact `host_run_b52b779e7e9a43c` (2026-06-04T091239Z), not from historical runs.

| Chapter | Terminal Operation | Provider Attempts | Approx Prompt Tokens | Timeout (s) | Error | Root Cause Hint | Diagnostic Consistency |
|---|---|---|---|---|---|---|---|
| 1 | auditor | 2/2 | 1074 | 60.0 | ReadTimeout | small_prompt_provider_timeout | consistent |
| 2 | writer | 2/2 | 1843 | 60.0 | ReadTimeout | small_prompt_provider_timeout | consistent |
| 3 | writer | 2/2 | 2879 | 60.0 | ReadTimeout | small_prompt_provider_timeout | consistent |
| 4 | writer | 2/2 | (writer) | 60.0 | ReadTimeout | small_prompt_provider_timeout | consistent |
| 5 | writer | 2/2 | (writer) | 60.0 | ReadTimeout | small_prompt_provider_timeout | consistent |
| 6 | auditor | 2/2 | (auditor) | 60.0 | ReadTimeout | small_prompt_provider_timeout | consistent |

Cross-chapter invariants:

- Every provider call (12 total across 6 chapters x 2 attempts) returned `ReadTimeout`
- Every chapter has `terminal_runtime_diagnostic_present: true`
- Every chapter has `diagnostic_consistency_status: consistent`
- `Host timeout classification: none` — Host did not enforce timeout; provider-level timeout only
- CLI elapsed max: ~923s, well under derived Host deadline of ~2160s
- `error_type: ReadTimeout` on every failing provider call — TCP connection established but no HTTP response received within timeout window
- `status_code: None`, `response_chars: None`, `finish_reason: None` on every failing call — zero bytes received from provider
- Prompt token range: 1074–2879 (all "small prompt")
- Writer drafts exist for Ch1 and Ch6 only (chapters where writer completed before auditor timed out)
- Ch2–Ch5: writer never produced a draft (writer itself timed out)

### 4.2 Differential Diagnosis

The question: is this an endpoint residual, a runtime policy residual, or evidence-insufficient?

#### Hypothesis A: Endpoint Availability/Performance Residual

**Evidence for**:
- Every provider call (12/12) fails with `ReadTimeout` — zero successful responses
- Prompt sizes are small (1074–2879 tokens) — rules out large-prompt processing delay
- Both writer and auditor operations fail — rules out operation-specific bug
- `status_code: None`, `response_chars: None` — provider sends zero bytes, not a partial response or error code
- Elapsed times cluster tightly around 60s (the timeout ceiling) — provider never responds within the window
- Host timeout is `none` — rules out Host-enforced termination
- Diagnostic consistency is `consistent` across all chapters — rules out serializer/lineage bug

**Evidence against**: none from the retained data. The pattern is uniform and unambiguous.

**Verdict**: This is the **primary** classification. The provider endpoint is not responding to HTTP chat-completions requests within 60s.

#### Hypothesis B: Runtime Policy Residual (timeout too short)

**Evidence for**:
- 60s timeout with 2 attempts gives ~120s per operation before giving up
- If the endpoint is genuinely slow (rather than unavailable), a longer timeout could help

**Evidence against**:
- `ReadTimeout` means no bytes received at all — the server isn't "slow," it's not responding
- 1074 prompt tokens at 60s is ~18 tokens/s — far below any reasonable LLM provider throughput
- If the endpoint were merely slow, we would expect at least some calls to succeed (especially the smallest prompts), but 12/12 fail
- Historical evidence from 2026-06-02 shows the same endpoint succeeded for some chapters under the same 60s timeout, which suggests intermittent availability rather than a structural timeout-is-too-short problem

**Verdict**: **Secondary at most**. Increasing timeout would not help if the endpoint is not responding at all. The 60s default is not the root cause.

#### Hypothesis C: Evidence Insufficient

**Evidence against**:
- 12 provider calls across 6 chapters, all with complete per-attempt runtime diagnostics
- `terminal_runtime_diagnostic_present: true` on every chapter
- `diagnostic_consistency_status: consistent` on every chapter
- Chapter-level, attempt-level, and CLI-level diagnostics are all present and mutually consistent
- Redaction scans passed with no secret leakage
- Retained artifact includes manifest, summary, per-chapter JSON, and writer draft markdown files

**Verdict**: **Rejected**. The evidence is comprehensive and internally consistent. There is no diagnostic gap that prevents classification.

#### Hypothesis D: Code/Serializer/Diagnostic Bug

**Evidence against**:
- Diagnostic serialization repair gate (commit `218a4f6`) is accepted locally
- Terminal provider exception diagnostics are retained at chapter level when no safe attempt record exists
- First-failed runtime summaries prefer terminal-matching diagnostics
- Missing terminal runtime diagnostics are explicit and do not invent fields
- All 6 chapters show `diagnostic_consistency_status: consistent`
- The 12 provider attempts show consistent `ReadTimeout` / `error_type` / `status_code: None` / `response_chars: None` patterns

**Verdict**: **Rejected**. Diagnostic serialization is working correctly.

### 4.3 Final Classification

```
Primary:   endpoint_availability_residual
Secondary: not_applicable (timeout policy is not causal)
Tertiary:  not_applicable (evidence is sufficient; diagnostics are consistent)
```

**Rationale**: The provider endpoint consistently fails to deliver any HTTP response within 60s for 12/12 calls across writer and auditor operations at small prompt sizes. The failure is at the transport layer (`ReadTimeout`), not the application layer. No code defect, serializer bug, prompt-size issue, or Host timeout policy explains the uniform failure pattern. The retained diagnostic evidence is complete, consistent, and sufficient for this classification.

**Corollary**: This residual cannot be resolved by code changes, prompt changes, timeout tuning, or diagnostic improvements within the current codebase. Resolution depends on provider endpoint availability, which is outside the scope of this project's code. The project's responsibility is to (a) fail closed correctly (confirmed), (b) produce complete safe diagnostics (confirmed), and (c) not silently mask the failure with fallbacks (confirmed).

## 5. Affected Files / Modules

This plan gate touches NO source files. The disposition operates on the retained artifact only.

For reference, the modules implicated in the broader residual (not modified by this plan):

| Module | Role in Residual | Changed by This Plan? |
|---|---|---|
| `fund_agent/services/llm_provider.py` | Provider HTTP client; issues the calls that timeout | No |
| `fund_agent/services/llm_run_artifacts.py` | Retained artifact serialization | No |
| `fund_agent/config/llm.py` | Provider timeout/attempt/backoff defaults | No |
| `fund_agent/services/execution_contract.py` | Host timeout derivation from provider timeouts | No |
| `fund_agent/services/fund_analysis_service.py` | Orchestrates write-audit-repair; classifies failures | No |
| `fund_agent/fund/chapter_writer.py` | Writer prompt assembly and provider call | No |
| `fund_agent/fund/chapter_auditor.py` | Auditor prompt assembly and provider call | No |
| `fund_agent/cli/analyze.py` | CLI `--use-llm` entry point; safe stderr summary | No |

## 6. Contract / Schema / Runtime / Default Impact

**No changes to any of the following:**

- Public chapter ids (`0-7`): unchanged
- Provider defaults (`FUND_AGENT_LLM_TIMEOUT_SECONDS=60`, `TIMEOUT_MAX_ATTEMPTS=2`, `TIMEOUT_BACKOFF_SECONDS=1.0`): unchanged
- Runtime policy (fail-closed, no deterministic fallback, stdout empty on incomplete): unchanged
- Diagnostic serialization schema: unchanged
- Retained artifact schema (`manifest.json`, `summary.json`, per-chapter JSON): unchanged
- Host timeout derivation formula: unchanged
- Writer/auditor contracts (anchor markers, required_output, audit_focus): unchanged
- Quality gate (FQ0-FQ6): unchanged
- ExecutionContract / FundLLMExecutionRequest schema: unchanged
- CLI exit code semantics (exit 1 on incomplete, stdout empty): unchanged
- Secret-safe diagnostic policy (no prompt/draft/raw response/API key/Authorization header in serialized output): unchanged

## 7. Decision: Artifact/Diagnostic Disposition Without Live Provider

### 7.1 Disposition Strategy

This gate performs a **static artifact/diagnostic disposition** on the existing retained artifact `host_run_b52b779e7e9a43c`. No live provider interaction. The disposition answers three questions:

1. **Is the diagnostic evidence complete and internally consistent?** → Determines whether the retained artifact is sufficient for endpoint calibration decisions.
2. **Does the failure pattern support endpoint-level classification over alternatives?** → Formalizes the differential diagnosis from Section 4.
3. **Is the system ready for a future live provider calibration gate, or is more diagnostic instrumentation needed first?** → Produces a calibration readiness verdict.

### 7.2 Why Not Live Provider Now

- Running another live provider command without first understanding the failure pattern risks repeating the same `ReadTimeout` without learning anything new
- The configured evidence already consumed the one authorized replacement attempt
- A new live evidence attempt requires a separate reviewed controller gate with explicit authorization
- The current retained artifact already contains 12 provider call diagnostics — this is sufficient for classification
- If the endpoint is genuinely unavailable, additional live runs would produce identical `ReadTimeout` results and waste the operator's time

### 7.3 Disposition Slices

#### Slice D1: Diagnostic Completeness Verification

Examine every chapter JSON in the retained artifact and verify:

- `terminal_runtime_diagnostic_present` is `true` for all 6 chapters
- `diagnostic_consistency_status` is `consistent` for all 6 chapters
- `chapter_runtime_diagnostics[]` array contains 2 entries per chapter (matching `provider_max_attempts=2`)
- Each runtime diagnostic entry has non-null `error_type`, `operation`, `provider_runtime_category`, `timeout_seconds`, `approx_prompt_tokens`, `elapsed_ms`
- `terminal_issue_class`, `terminal_failure_category`, `terminal_stop_reason` are non-null and consistent with the runtime diagnostics array
- `chapter_prompt_contract_diagnostics` is present (may be empty — writer never produced output for Ch2–Ch5)
- Writer draft `.md` files exist for Ch1 and Ch6 (chapters where writer succeeded) and do NOT exist for Ch2–Ch5 (chapters where writer timed out)
- No chapter JSON contains `prompt`, `raw_response`, `raw_audit_response`, `message`, `model_name`, API key, base URL, or Authorization header values

**Pass criteria**: All checks pass for all 6 chapters.

#### Slice D2: Cross-Chapter Failure Pattern Analysis

Aggregate the 12 provider call diagnostics and verify:

- All 12 calls have `error_type: ReadTimeout`
- All 12 calls have `provider_runtime_category: timeout`
- All 12 calls have `status_code: None` and `response_chars: None`
- All 12 calls have `timeout_root_cause_hint: small_prompt_provider_timeout`
- Elapsed times cluster in [60003, 60224] ms (the 60s timeout ceiling ± jitter)
- Prompt token range is [1074, ~3000] — all "small prompt"
- Both `writer` and `auditor` operations fail — no operation type succeeds
- `timeout_budget_kind` correctly distinguishes `writer_initial` from `auditor`
- `repair_timeout_fallback_used: true` on all calls (consistent with the repair-timeout-fallback path being triggered by primary timeout exhaustion)

**Pass criteria**: All invariants hold across all 12 calls.

#### Slice D3: Fail-Closed Safety Verification

Verify that the system's fail-closed behavior is intact:

- CLI exit code is `1` (not `0`)
- stdout is empty (no partial report printed)
- `orchestration_status: blocked` (not `partial` or `complete`)
- `final_assembly_status: incomplete` (not `complete`)
- No deterministic fallback was triggered
- No accepted report file was produced
- Safe stderr summary was emitted with chapter matrix but no secrets
- Retained artifact was written to local ignored `reports/llm-runs/`

**Pass criteria**: All fail-closed invariants hold.

#### Slice D4: Calibration Readiness Assessment

Based on Slices D1-D3, produce a calibration readiness verdict:

- **If D1-D3 all PASS**: The retained diagnostic evidence is complete, consistent, and sufficient. The system is ready for a future live provider calibration gate. The residual is classified as `endpoint_availability_residual`. No additional diagnostic instrumentation is needed before the next live evidence gate.
- **If any slice FAILS**: The failure must be classified (diagnostic gap, serializer bug, inconsistency) and a remediation slice must be defined before calibration readiness can be declared.

### 7.4 What Calibration Readiness Means (and Does NOT Mean)

Readiness means:
- The retained diagnostic schema captures all fields needed to classify provider failures
- The fail-closed safety boundary is intact and verified
- A future controller can authorize exactly one live provider evidence run with confidence that the result will be classifiable
- No code, config, or default changes are needed before the next evidence gate

Readiness does NOT mean:
- The endpoint is working (it is not; that's the residual)
- A live run will succeed (it probably won't, unless endpoint availability changes)
- Provider defaults should change (they should not; 60s is reasonable)
- Chapter acceptance calibration can begin (no chapter has accepted draft/conclusion)

## 8. Validation Matrix

| Slice | Verification | Method | Pass Criteria |
|---|---|---|---|
| D1 | Diagnostic completeness | Static inspection of 6 chapter JSON files + 2 writer draft `.md` files | All fields present, no secrets, terminal diagnostics match runtime array |
| D2 | Cross-chapter pattern | Aggregate analysis of 12 provider call diagnostics | Uniform `ReadTimeout` / `timeout` / `small_prompt_provider_timeout` / null response |
| D3 | Fail-closed safety | Manifest + evidence cross-check | exit 1, stdout empty, no fallback, no accepted report, safe stderr |
| D4 | Calibration readiness | Synthesis of D1-D3 | All PASS → ready for future live calibration gate; any FAIL → remediation needed |

## 9. Review Gates

This plan artifact requires:

1. **Independent review** by at least two reviewers (AgentMiMo, AgentDS per current convention) — verify:
   - First-principles residual classification is sound and evidence-based
   - Disposition slices are correctly scoped (no live provider, no code change)
   - Non-goals and forbidden scope are comprehensive
   - Calibration readiness criteria are neither too lax nor too strict
   - Future live evidence is correctly deferred to a separate gate
2. **Controller judgment** — accept or revise the disposition plan; if accepted, authorize execution of Slices D1-D4
3. **Execution evidence** (separate artifact after plan acceptance) — record D1-D4 results with direct retained-artifact evidence
4. **Execution evidence reviews** (2 reviewers)
5. **Controller judgment on disposition outcome** — accept the calibration readiness verdict and decide next gate

## 10. Stop Conditions

Stop immediately if any of the following occur:

- Any D1-D3 check fails → classify the failure, update the residual, do NOT proceed to D4
- Secret-like value discovered in retained artifact → stop, redact, escalate to controller
- Diagnostic inconsistency found between chapter JSON and manifest/summary → stop, classify as serializer/lineage bug
- Any temptation to run a live provider command → stop; that belongs in a separate gate
- Any temptation to change provider defaults, timeouts, or runtime policy → stop; that requires a separate heavy implementation gate with its own plan/review/controller judgment

## 11. Residual Owner

After this disposition gate completes:

- **If calibration readiness is ACCEPTED**: The next gate owner is the **future live provider calibration evidence gate owner**. That gate must: (a) run presence-only readiness preflight, (b) run exactly one live provider command if readiness passes, (c) record the result as same-run direct evidence, (d) not change any defaults. The endpoint availability residual itself is owned by the provider endpoint operator and is outside this project's code scope.
- **If calibration readiness is REJECTED** (diagnostic gap found): The next gate owner is the **diagnostic instrumentation gate owner** who must add the missing diagnostic fields before calibration readiness can be re-assessed.
- **Chapter 3 `programmatic:C2` / `code_bug_other` residual**: Remains a separate residual with a separate owner. Not addressed by this gate. Ch3 writer timeout in the current retained artifact means the C2 rule was never reached; the prior Ch3 C2 evidence is from a different historical run and must not be mixed with current same-run evidence.

## 12. Completion Report Format

The disposition execution evidence artifact must include:

1. **Slice D1 results**: Per-chapter table with each completeness check and PASS/FAIL
2. **Slice D2 results**: Aggregate table of 12 provider calls with invariant verification
3. **Slice D3 results**: Fail-closed invariant table with CLI/manifest/retained-artifact cross-references
4. **Slice D4 verdict**: Calibration readiness (READY / NOT_READY) with rationale
5. **Redaction scan**: `rg` scan of the evidence artifact for secret-like patterns
6. **Forbidden-scope checklist**: Confirm no code/test/config/runtime/default/provider change occurred

## 13. Gate Nature: Disposition Plan, Not Live Evidence

**This gate is a docs/reviews disposition plan gate.** It produces:

- A first-principles residual classification (endpoint availability residual)
- A static diagnostic examination of the existing retained artifact
- A calibration readiness verdict

**This gate is NOT a live evidence gate.** It does not:

- Run any provider command
- Make any HTTP request
- Change any code, config, or default
- Produce new runtime artifacts

**Future live evidence belongs in a separate, subsequent heavy gate** with its own plan, reviews, controller judgment, and explicit authorization for exactly one live provider command. This plan gate may conclude that such a future gate is warranted (calibration readiness), but it does not execute it.

The distinction is explicit: **disposition now, live evidence later (if authorized).**
