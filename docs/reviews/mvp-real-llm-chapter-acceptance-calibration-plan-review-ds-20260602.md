# MVP Real LLM Chapter Acceptance Calibration Plan Review — AgentDS

## Review Identity

- **Reviewer**: AgentDS
- **Role**: Independent plan review specialist (not controller, not implementer)
- **Date**: 2026-06-02
- **Plan under review**: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-plan-20260602.md`
- **Gate classification**: `heavy`
- **Review type**: Pre-implementation plan review per `/planreview` handoff

## Reference Documents Reviewed

| Document | Version/State |
|---|---|
| `AGENTS.md` | Current, as authoritative execution rules |
| `docs/design.md` v2.3 | Current/future status labels verified |
| `docs/implementation-control.md` v2.4 | Next entry point and residual owners verified |
| `docs/current-startup-packet.md` | Current mainline and boundary guardrails verified |
| `docs/fund-analysis-template-draft.md` | Chapter 2 contract and CHAPTER_CONTRACT semantics verified |

## Focus Area Findings

### Focus 1: Single Heavy Gate — Plan Only, No Implementation Before Review

**Verdict: PASS**

The plan self-declares as `heavy` gate classification (line 8), work type `plan artifact only` (line 10), and explicitly forbids implementation, runtime/source edits, smoke execution, staging, commit, push, or PR in the planning task (line 11). The acceptance criteria state "No implementation starts before reviewed and accepted plan" (line 301). The Handoff Summary reinforces: "Start with Slice 1. Do not change code until retained artifacts and a fresh smoke rerun prove the current first actionable blocker" (line 313). The gate scope clearly separates planning from implementation: "The implementation objective, after this plan is reviewed and accepted, is to make the smallest evidence-supported change…" (line 36).

No ambiguity exists between planning and implementation phases. The plan correctly positions itself as a plan-only artifact requiring two independent reviews before any code change.

### Focus 2: Slice 1 — Retained Artifact + Fresh Real Smoke Before Any Calibration Code Change

**Verdict: PASS**

Slice 1 (lines 133–163) is unambiguous: its goal is evidence triage "without changing runtime behavior." Actions explicitly require both:
1. Inspecting current `reports/llm-runs/` retained artifacts for `006597 / 2024`
2. Rerunning real LLM smoke once under current provider configuration

The decision gate is explicit: "Decide whether Slice 2 is authorized. If first blocker is provider runtime, stop here and recommend provider runtime budget calibration gate" (line 143). Forbidden files include all source, tests, config, design/control/startup docs, templates, schema, and score/golden/readiness files. Validation requires `git status --short` scope check proving no source/test/config edits occurred.

The evidence protocol (lines 54–68) further constrains artifact inspection to direct same-run fields only: "The implementation evidence must not infer a root cause from old logs if the retained artifact fields contradict it" (line 67–68). This correctly prevents the implementation agent from shortcutting to code changes based on stale evidence.

### Focus 3: Root-Cause Taxonomy — No Indirect Inference

**Verdict: PASS**

The taxonomy (lines 107–114) defines 6 classes, each with a "Direct evidence required" column that specifies what same-source artifact fields must prove the classification. Critically:

- `prompt_contract_problem` requires draft/repair draft evidence, not just matrix status
- `programmatic_audit_code_bug` requires proving audit code flags valid output or misses invalid output — not just "chapter matrix says L1 failed"
- `provider_runtime_blocker` explicitly stops calibration and hands off to a different gate

The preamble (line 105) anchors all classification to "same-source evidence in the retained artifacts and rerun smoke." The explicit prohibition on indirect inference appears at line 129: "Indirect evidence is not sufficient. Do not conclude 'L1 is too strict' merely from a failed chapter matrix."

This taxonomy correctly separates prompt_contract, repair guidance, diagnostic clarity, programmatic audit code bug, fact/evidence gap, and provider runtime blocker as distinct root causes requiring distinct evidence and distinct remediation paths. It prevents the common failure mode of conflating "chapter 2 L1 failed" with "L1 auditor is too strict" without examining the actual draft content.

### Focus 4: Chapter 2 l1_numerical_closure — Same-Source Evidence

**Verdict: PASS**

The L1 same-source rule (lines 116–128) is specific and actionable. It requires all 7 conditions to be true in the same retained run or rerun artifact:
- chapter_id, failure_category, failure_subcategory match
- diagnostic phase or auditor feedback content confirmed
- draft contains actual numerical equation text
- equation lacks nearby anchor marker
- fact/anchor IDs available or gap should have been declared
- no higher-priority code path triggered first

This rule is strict enough: it prevents calibration from proceeding on a "L1 failed" matrix entry alone. It is actionable: each condition maps to a concrete field or line that can be verified by reading retained artifacts. It correctly preserves the precedence of provider runtime timeout, missing facts, forbidden phrases, and candidate facet assertions over L1 (line 127).

The rule aligns with the CHAPTER_CONTRACT chapter 2 semantics: L1 checks R=A+B-C numerical closure, so the same-source rule requires seeing the actual R, A, B, C equation text and the missing anchor marker in the same draft.

### Focus 5: Boundary Protection — Auditor Rules, Repair Budget, Provider Budget, Fallback, Quality Gate, Score-Loop, Schema, Host/Agent/Dayu

**Verdict: PASS**

Non-goals (lines 39–50) explicitly forbid all of:
- Relaxing auditor rules
- Increasing repair budget as default solution
- Deterministic fallback for incomplete results
- Partial/half-finished report output
- Provider timeout/retry/backoff budget changes
- Provider/model fallback or multi-provider routing
- Score-loop connection to existing score/golden/readiness/quality gate
- Quality gate, golden fixtures/answers, manifests, snapshot promotion, readiness, final judgment changes
- Template, design, control, startup doc modifications
- `dayu-agent`, `dayu.host`, `dayu.engine` as production runtime dependencies
- Agent runner/tool-loop, async Host runner, durable session/resume/memory/outbox migration

Forbidden files (lines 193–203) enumerate: provider config, provider retry/backoff, execution contract, score/golden/readiness/quality gate/final judgment, design/control/startup/template docs, Host/Agent/dayu files. Acceptance criteria (lines 298–305) reiterate these constraints as gate-level requirements.

The plan's expected real smoke criteria (lines 222–237) include a critical guardrail: "Not acceptable: chapter 2 passes only because L1 is disabled/relaxed globally, repair budget increased, incomplete report emitted, deterministic fallback used, or unsafe diagnostics leak secrets." This prevents the most likely implementation shortcut.

### Focus 6: Slices — Code-Generation-Ready

**Verdict: PASS**

Each slice is self-contained with:

| Slice | Allowed Files | Forbidden Files | Validation | Smoke Criteria | Stop Conditions | Residual Owners |
|---|---|---|---|---|---|---|
| 1 | `docs/reviews/*evidence*.md`, ignored `reports/llm-runs/` | All source, tests, config, design/control/startup, templates | `git status --short` scope check | Exit criteria: taxonomy table + controller decision | Provider runtime → stop | Yes (line 163) |
| 2 | 5 source files + matching tests | Provider config, retry, schema, score/golden/readiness, template, Host/Agent | Targeted pytest, ruff, fresh smoke rerun | Success/failure/not-acceptable criteria (7 conditions) | L1 must be proven blocker | Via residual table |
| 3 | Same as Slice 2, narrow only | Broad all-chapter rewrite, provider runtime, Host/Agent migration | Targeted tests, CLI regressions, smoke comparison | Chapter 2 not L1-blocked, 3/6 triaged or residual | Must not become broad rewrite | Via residual table |

The test and validation matrix (lines 262–272) maps each area to required validation with notes. The allowed/forbidden file matrix (lines 253–259) provides a quick reference. The slice dependencies are explicit: Slice 2 requires Slice 1 authorization; Slice 3 requires Slice 2 proof or same-root-cause proof.

### Focus 7: Chapters 3/6 — No Broad Prompt Rewrite

**Verdict: PASS**

Slice 3 (lines 229–251) gates itself behind Slice 2 success or Slice 1 same-root-cause proof. It explicitly constrains actions:
- Same `l1_numerical_closure` → apply narrow same pattern (line 242)
- Different prompt-contract issue → separate mini-triage, same-source narrow fix only (line 243)
- Fact/evidence gap or provider runtime → no prompt wording patch, record residual (line 244)

The explicit prohibition: "It must not become a broad prompt rewrite for all body chapters" (line 231). The allowed files are "same as Slice 2, but changes must be limited to the proven root cause."

This correctly prevents scope creep from "fix chapter 2 L1" into "rewrite all chapter prompts."

### Focus 8: Secret Redaction and Safe Evidence

**Verdict: PASS**

The evidence protocol (lines 97–102) explicitly defines:
- What must NOT appear in evidence: prompts, raw provider responses, raw auditor responses, API keys, Authorization/Bearer/cookies, request headers, full provider config, model names (if safe serializers omit them), stack traces, unredacted secret-looking substrings
- What quoting rules apply: "quote only the minimal lines needed to prove the root cause. Prefer paraphrase plus file path and field references. Do not paste entire drafts."

The retained artifact inspection rules (lines 58–66) specify exact files and fields to read, which implicitly excludes non-allowlisted files. The acceptance criteria (line 304) confirm safe diagnostics must "still exclude prompts, raw provider/auditor responses, secrets, headers, full config, stack traces and model names."

These rules are sufficient. The key risk — retained writer/repair drafts containing secret-like text — is mitigated by the combination of: (a) the artifact retention gate applies redaction before saving, (b) the evidence protocol forbids quoting entire drafts, and (c) the plan explicitly lists what must be excluded.

## Cross-Reference Consistency Checks

### AGENTS.md Alignment

- **Same-source root cause rule** (AGENTS.md line 71): Plan's taxonomy (line 105) and chapter 2 rule (line 129) directly implement this constraint. Consistent.
- **CHAPTER_CONTRACT design goal** (AGENTS.md line 73): Plan's approach of "smallest evidence-supported change" to writer guidance aligns with "lowest cognitive burden for correct next action." Consistent.
- **Gate classification** (AGENTS.md lines 52–57): Plan correctly classifies as `heavy` — chapter acceptance calibration can affect prompt/repair guidance, auditor diagnostics, and fail-closed behavior. Consistent.
- **Module boundaries** (AGENTS.md lines 89–139): Plan's allowed files respect the UI→Service→Host→Agent boundary. Writer/auditor changes stay in `fund_agent/fund` (Agent layer). Orchestrator changes stay in Service. No Host/Agent/dayu runtime changes. Consistent.
- **No extra_payload** (AGENTS.md line 83): Not directly tested by this plan but the plan doesn't introduce any new parameter passing. Consistent.
- **Explicit parameters** (AGENTS.md line 83): Plan's repair guidance changes require "typed explicit parameters" (line 218). Consistent.

### docs/design.md Current/Future Status Labels

- Design doc §5.4.1 (Route C gate sequence) marks chapter acceptance calibration as future work. The plan correctly treats it as a future gate being planned, not as current code fact.
- Design doc §2.2 describes current `--use-llm` path. The plan's non-goals preserve this current implementation.
- Design doc §5.1 (audit mechanism) labels L1 as `✅ 实现`. The plan's repair guidance and diagnostic clarity changes would modify how L1 failures are communicated, not the L1 rule itself. The plan explicitly forbids relaxing `_audit_numerical_closure()`.
- Design doc §5.4.1 marks provider runtime budget calibration, score-loop, async Host, durable session, and Agent engine as future. The plan's non-goals and residual owners correctly defer all of these.

### docs/implementation-control.md Next Entry and Residual Owners

- Control doc line 67: "Next entry point: `MVP real LLM chapter acceptance calibration gate` plan gate; do not implement calibration before plan/review/accepted checkpoint." Plan aligns — it's the planning artifact for that next entry point.
- Control doc line 257: "Chapter 2/3/6 acceptance calibration: Deferred until per-chapter artifacts and progress UX support evidence-based diagnosis; must not relax auditor or increase repair budget by default." Plan accepts these constraints.
- Control doc line 258: "Provider runtime budget calibration: Deferred." Plan's residual owners table correctly preserves this as a future gate.
- Control doc line 254: "Score-loop implementation: Future score-loop implementation gate after Gate B timeout is handled." Plan excludes score-loop changes.
- Control doc line 253: "Programmatic audit C2: Future `MVP programmatic audit C2 calibration gate`." Plan's residual owners table includes this (line 309).

### docs/current-startup-packet.md

- Line 22: Same next entry point. Plan is the artifact for that entry.
- Line 127: "Chapter 2/3/6 acceptance calibration remains deferred until artifact evidence and progress UX are in place; it must not relax auditor rules or increase repair budget by default." Plan's non-goals mirror this.

### docs/fund-analysis-template-draft.md Chapter 2 / CHAPTER_CONTRACT

- Chapter 2 contract (lines 334–368): `must_answer` includes R calculation, B identification, A = R - B, structural vs phase-based judgment, cost decomposition, and R=A+B-C synthesis. `evidence_requirements` require each value to cite source and each calculation to cite formula and inputs.
- Plan's L1 same-source rule (line 124): requires "R=A+B-C, A=R-B, or A-C numerical assertion" in the retained draft. This maps directly to the chapter 2 `must_answer` requirements.
- Plan's writer guidance change target (line 171): "make chapter 2 numerical closure instructions explicitly require nearby anchor markers for every R/B/A/Cost equation." This aligns with chapter 2's `evidence_requirements`: calculations must cite formula and sources, and anchor markers are the mechanism.

## Observations (Non-Blocking)

### O1: L1 Rule and Provider Timeout Cross-Reference

The chapter 2 L1 same-source rule (lines 116–128) does not explicitly cross-reference the provider runtime timeout decision tree (lines 92–94). Condition "the failure is not preceded by provider runtime timeout" (line 127) covers it, but an implementation agent reading only the L1 rule might not realize they should first check the smoke evidence's top-level blocker before applying L1 criteria.

**Severity**: Non-blocking. The evidence protocol (lines 90–95) and Slice 1 exit criteria (line 143) establish the priority at the gate level. The L1 rule's last condition covers it. No plan change required, but the implementation evidence artifact should explicitly record the provider-runtime-first check.

### O2: Slice 2 Priority Order — Sequential vs Cumulative

Slice 2's allowed change types are listed "in priority order" (line 169) with 4 numbered items, but the plan doesn't specify whether the implementation agent must try them sequentially (writer guidance only, test, if success stop; else add repair guidance) or can apply all supported changes at once. The handoff summary says "implement the smallest…fix that addresses that evidence" (line 313), which implies minimalism, but a sequential constraint would be clearer.

**Severity**: Non-blocking. The "smallest fix" language and the requirement that each change be "evidence-supported" together constrain over-implementation. The implementation review can enforce minimalism.

### O3: Cold Start — No Existing Retained Artifacts

The plan says implementation must "start by locating the latest relevant local ignored run directory under `reports/llm-runs/`" (line 56). If no real smoke has been run since the artifact retention checkpoint (`4f7903f`), there may be no retained artifacts to inspect. The plan doesn't explicitly address this "cold start" scenario. In practice, the fresh smoke rerun (Slice 1, line 140) would produce the first set of retained artifacts, which could then be inspected.

**Severity**: Non-blocking. The fresh smoke rerun requirement ensures artifacts will exist. The implementation agent can run smoke first if retained artifacts are absent, then inspect the resulting artifacts. The implementation evidence should record whether pre-existing artifacts were available.

### O4: Provider Credential Availability

Slice 1 requires a "fresh real LLM smoke rerun" but notes "subject to controller/user availability of credentials/network/cost" (line 140). The acceptance criteria (line 289) allow "a controller-recorded reason why fresh smoke could not run." This is a reasonable real-world accommodation, but it creates a scenario where Slice 2 could proceed based on retained artifacts alone, without fresh smoke confirmation. The plan does not explicitly address whether retained-artifact-only evidence is sufficient for proceeding to Slice 2, or whether absent fresh smoke the gate should defer to provider runtime budget calibration.

**Severity**: Non-blocking. The controller judgment step in Slice 1 exit criteria (line 163) provides a decision point. The controller can require fresh smoke before authorizing Slice 2, or accept retained-artifact-only evidence with explicit risk acceptance.

## Verdict

**PASS — No blocking plan findings.**

The plan correctly:
1. Positions itself as a single heavy gate planning artifact with explicit prohibition on implementation before review and acceptance
2. Requires Slice 1 to complete retained artifact inspection and fresh real smoke before any calibration code change
3. Defines a root-cause taxonomy that prevents indirect inference and correctly separates 6 distinct failure classes
4. Establishes a strict, actionable same-source evidence rule for chapter 2 `l1_numerical_closure`
5. Explicitly forbids relaxing auditor rules, increasing repair budget, changing provider timeout budget, deterministic fallback, quality gate/golden/readiness/score-loop, artifact schema, and Host/Agent/dayu runtime changes
6. Provides code-generation-ready slices with allowed/forbidden files, validation, smoke criteria, stop conditions, and residual owners
7. Handles chapters 3/6 with narrow, evidence-constrained scope and explicit prohibition on broad prompt rewrite
8. Defines sufficient secret redaction and safe evidence rules for retained drafts and auditor feedback

Four non-blocking observations are recorded above. None prevent the plan from proceeding to review. The plan is internally consistent, aligned with all reference documents, and ready for controller judgment after the second independent review.

## Review Signature

- **Reviewer**: AgentDS
- **Date**: 2026-06-02
- **Verdict**: PASS
- **Blocking findings**: 0
- **Non-blocking observations**: 4 (O1–O4)
