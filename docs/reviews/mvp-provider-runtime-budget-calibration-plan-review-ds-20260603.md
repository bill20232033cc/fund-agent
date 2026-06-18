# MVP provider runtime budget calibration plan review (DS)

## Reviewer Self-Check

- Role: independent plan reviewer only. No implementation, no code edit, no commit/push/PR.
- Gate: `MVP provider runtime budget calibration gate`, classification `heavy`.
- Plan under review: `docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md`
- Output: `docs/reviews/mvp-provider-runtime-budget-calibration-plan-review-ds-20260603.md`

## Evidence Sources Read

| Source | Status |
|---|---|
| `AGENTS.md` | read |
| `docs/design.md` | read (provider runtime, ownership boundary, future design sections) |
| `docs/implementation-control.md` | read |
| `docs/current-startup-packet.md` | read |
| `docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md` | read (plan under review) |
| `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1-controller-judgment-after-provider-restore-20260602.md` | read |
| `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json` | read and cross-validated |

## Validation Performed

- `python3` cross-validation of plan chapter matrix claims against `summary.json` runtime_diagnostics — all claims verified.
- `git diff --check` on plan artifact — PASS, exit 0.

## Review Findings

### Blocking Findings

None.

### Overall Verdict: PASS

---

## Detailed Review

### 1. Same-Source Evidence Distinction (2026-05-31 vs 2026-06-02)

**Verdict: PASS**

The plan correctly distinguishes two evidence periods:

- 2026-05-31 evidence (from `docs/reviews/mvp-provider-runtime-timeout-follow-up-implementation-evidence-20260531.md`, treated as historical): all body chapters experienced **writer** timeouts after compact mode. Ch2/Ch4/Ch6 writer prompt tokens were 1590/1274/2110.
- 2026-06-02 retained run (`reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431`): Ch2/Ch4/Ch6 writer drafts were **produced**, and terminal failures occurred at the **auditor** operation. Auditor prompt tokens are 743/584/731 — all under 800 tokens.

Cross-validation against `summary.json` confirms:
- Ch2: 2 auditor timeout rows, `approx_prompt_tokens=743`, `repair_attempt_index=0`, `timeout_seconds=60.0`, `timeout_max_attempts=2`
- Ch4: 2 auditor timeout rows, `approx_prompt_tokens=584`, `repair_attempt_index=0`, `timeout_seconds=60.0`, `timeout_max_attempts=2`
- Ch6: 2 auditor timeout rows, `approx_prompt_tokens=731`, `repair_attempt_index=1` (after repair), `timeout_seconds=60.0`, `timeout_max_attempts=2`

The plan's chapter matrix table (lines 74-81) matches all verified fields. The correction at line 45 — "the latest retained run disproves 'Ch2/Ch4/Ch6 writer timeout' for that run, but not for all future provider reruns" — is accurate and properly scoped.

The plan transparently discloses that a 2026-06-02 timeout follow-up evidence artifact is missing and uses 2026-05-31 as substitute, correctly labeling the older artifact as "historical implementation evidence only." The 2026-06-02 retained run provides sufficient same-source primary evidence; the substitute gap affects only implementation history, not diagnostic reasoning.

### 2. Root-Cause Claims

**Verdict: PASS**

The plan presents six hypotheses (H1-H6) with clear evidentiary status, support criteria, and disproof criteria:

- H1 (provider endpoint small-prompt timeout): **supported** — repeated `provider_runtime_category=timeout` at small prompt sizes
- H2 (current timeout budget too low): **unresolved** — requires bounded-higher-budget experiment
- H3 (writer timeout remains primary): **not supported** — writer drafts exist in 2026-06-02 run
- H4 (auditor prompt format induces endpoint hang): **unresolved** — requires PASS-only probe experiment
- H5 (audit rules too strict): **not supported** — timeout occurs before audit result
- H6 (prompt contract/fact gap/code bug): **not supported** — no such issues in terminal timeout rows

No unsupported root-cause claim is presented. The plan frames the primary question as a diagnostic separation problem (provider endpoint vs budget vs auditor prompt format), not as a premature assertion. H4 is an internally consistent hypothesis: if a PASS-only auditor probe returns fast but the full auditor prompt times out, the cause is prompt complexity rather than endpoint unavailability. The plan correctly gates this behind controlled evidence, not immediate implementation.

Cause classes (lines 36-43) are well-separated: provider runtime timeout, prompt contract failure, audit parse/rule block, fact gap, code bug, and large prompt cost. Large prompt cost is explicitly rejected for the current retained evidence, which is correct given sub-800-token auditor prompts.

### 3. Fail-Closed and Constraint Preservation

**Verdict: PASS**

Hard constraints (lines 48-55) explicitly preserve:

- No deterministic fallback for incomplete LLM result
- No partial accepted report from partial chapter matrix
- No auditor relaxation, no programmatic blocker weakening, no fail-open parsing
- No provider budget change without controller-authorized implementation gate
- No mutation of score, golden, quality gate, readiness, retained reports, or PR state
- No secrets or raw payloads in artifacts

These are reinforced throughout:
- Option A recommends budget evaluation only after controlled evidence, not immediate implementation
- Option C explicitly states PASS-only probe output "must never be accepted as chapter audit"
- Option D split-audit is blocked behind H4 evidence and requires Agent-aware design
- Option E rejects per-chapter budget as first change
- Option G PoC explicitly states no result "may produce an accepted report unless the normal production path accepts every required chapter"
- Stop condition at line 277 blocks any fix that "requires auditor relaxation, deterministic fallback, score/golden/quality/readiness mutation, or template truth replacement"

All design options and future slices preserve the fail-closed envelope.

### 4. Future Evidence Commands, Stop Conditions, and Implementation Slices

**Verdict: PASS**

Future evidence commands (lines 222-266) are explicitly labeled "do not run in this planning gate" and "handoff commands for a later authorized evidence gate." They include:
- Read-only retained artifact checks using `jq` and `json.tool`
- Future live provider commands with explicit env-override matrix
- Secret-safety scan using `rg` with specific forbidden patterns

Stop conditions (lines 268-277) are specific and actionable:
- Missing provider env → stop
- Secret-bearing text → stop
- Insufficient runtime field exposure → stop
- Blocker shift from timeout to content/audit → route to appropriate calibration gate
- Bounded higher timeout still times out → classify as endpoint residual, do not escalate budgets
- Any relaxation/fallback proposal → stop

Implementation slices (lines 279-360) are all conditional with explicit entry conditions:
- Slice 1 (Evidence-Only Runtime Matrix): gated on serializer insufficiency
- Slice 2 (Operation-Specific Budget Policy): gated on evidence showing higher auditor timeout resolves the issue
- Slice 3 (Diagnostic PASS-Only Probe): gated on ambiguous evidence after budget experiments
- Slice 4 (Split-Audit Design Gate): gated on PASS-only success with full-audit timeout, and requires Agent-aware design

Each slice lists files to be confirmed by controller, implementation decisions, and validation requirements. No slice requires the implementation worker to redesign ownership. Default budget change is explicitly separated into "a separate heavy implementation gate" (Slice 2, line 323).

### 5. Ownership Boundary Compliance

**Verdict: PASS**

The plan's ownership boundary section (lines 362-376) correctly reflects both current implementation facts and accepted future design:

Current (matching `docs/design.md` lines 59, 501-506, 520-522):
- Service owns `FundLLMExecutionRequest`, runtime plan, and openai-compatible writer/auditor clients
- CLI passes only generic Host operation/deadline/session fields
- Host is lifecycle-only, business-agnostic
- Fund owns domain writer/auditor semantics and programmatic-first audit

Future (matching accepted Agent/tool-loop design, `docs/design.md` line 63):
- Agent owns runner, tool loop, retry/repair attempt ledger, budget spending, stop/retry decision, ToolTrace
- Provider clients remain Service-constructed explicit per-run typed fields — not ToolRegistry tools, not `extra_payload`
- Runtime budget evidence maps to ToolTrace attempt rows
- Split-audit and per-attempt budget belong to Agent ownership, not ad hoc Service expansion

The warning at line 376 — "not expanded ad hoc inside Service beyond the first-MVP diagnostic need" — correctly prevents premature ownership drift.

### 6. Residual Risks

**Verdict: PASS**

Residual risks table (lines 390-398) correctly identifies:
- Provider endpoint may remain unreliable under higher budgets
- Ch6 has non-terminal C2/C1 evidence before terminal timeout — routes to separate audit/contract calibration only after timeout resolved
- Ch3 `programmatic:C2`/`code_bug_other` — routes to Ch3-only calibration gate, not runtime budget gate
- Split-audit complexity — routes to future Agent/tool-loop gate
- Budget default change cost/latency impact — separate heavy implementation gate
- Service ownership transition — routes to future Agent implementation gate

All residual owners are correctly assigned to appropriate future gates per the control doc ledger.

---

## Non-Blocking Observations

**N1 — Option G env-var names not in current code.** `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS` and `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS` are proposed as future operation-specific overrides. These don't exist in the current config layer (current env vars are `FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS` and `FUND_AGENT_LLM_TIMEOUT_BACKOFF_SECONDS`). The plan correctly labels Option G as requiring controller authorization and Slice 2 as conditional on evidence. No action needed in this planning gate — the implementation slice will add them if evidence supports it.

**N2 — Slice 1 file paths need controller confirmation.** The plan lists `fund_agent/services/chapter_orchestrator.py`, `fund_agent/services/llm_provider.py`, `fund_agent/services/llm_run_artifacts.py`. If the implementation worker discovers different touchpoints, the plan already states "to be confirmed by controller." This is adequate for a conditional future slice.

**N3 — Ch6 mixed evidence handling.** Ch6 attempt 0 has real C2/C1 audit evidence (programmatic C2 at `压力测试`, LLM C1 about compressed bond-risk evidence) before the terminal auditor timeout in attempt 1. The plan correctly surfaces this in the residual risks table ("Ch6 has non-terminal C2/C1 evidence before terminal timeout") and does not prematurely route it to audit calibration while timeout is the terminal blocker. This is consistent with the controller judgment (`docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1-controller-judgment-after-provider-restore-20260602.md` lines 54-71).

**N4 — H4 hypothesis framing.** The plan introduces H4 (auditor prompt format induces endpoint hang) and proposes Option C (PASS-only audit probe) to test it. This is a well-formed diagnostic hypothesis with a safe probe design, but the probe requires constructing a minimal auditor request that uses "retained accepted writer draft metadata" — the current artifact does not include throttled/scalar auditor-probe capability. If Slice 1 (serializer improvement) is needed to expose the right fields, that would be the natural sequencing. The plan already conditions Slice 3 on Slice 1/2 evidence remaining ambiguous.

---

## Review Handoff Criteria Check

Per the plan's own review criteria (lines 400-408):

| Criterion | Status |
|---|---|
| Distinguishes 2026-05-31 writer timeout from 2026-06-02 auditor timeout | PASS |
| Root-cause claims use same-source retained fields or label historical evidence | PASS |
| Fail-closed, no-fallback, no-auditor-relaxation, no-secret constraints preserved | PASS |
| Future live commands are diagnostics-only, cannot change provider defaults | PASS |
| Implementation slices are conditional, small, no ownership redesign required | PASS |

---

## Conclusion

No blocking findings. The plan correctly distinguishes the two evidence periods, bases root-cause hypotheses on same-source retained artifact fields, preserves all fail-closed constraints, gates implementation behind conditional evidence, and respects current and future Service/Host/Agent/Fund ownership boundaries. Recommend acceptance for controller judgment.
