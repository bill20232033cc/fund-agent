# MVP Real LLM Chapter Acceptance Calibration Plan Review — MiMo

> **Reviewer**: AgentMiMo
> **Date**: 2026-06-02
> **Plan artifact**: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-plan-20260602.md`
> **Review type**: adversarial plan review
> **Gate classification**: `heavy`

## Review Inputs

- `AGENTS.md` — rules, boundaries, same-source root-cause rule
- `docs/design.md` — current/future status labels
- `docs/implementation-control.md` — next entry, residual owners
- `docs/current-startup-packet.md` — current mainline truth
- `docs/fund-analysis-template-draft.md` — CHAPTER_CONTRACT chapter 2 section, L1 semantics
- Plan artifact under review

---

## Focus Area 1: Single Heavy Gate, No Implementation Before Plan Acceptance

**Finding**: PASS

The plan correctly maintains heavy gate discipline:

- Self-check explicitly states `work type: plan artifact only` and `forbidden: runtime/source/test/config/design/control/startup edits, real smoke execution, implementation, staging, commit, push, PR`.
- Slice 1 is purely evidence triage — no code changes allowed.
- Slice 2 is gated on Slice 1 proving `l1_numerical_closure` as the actionable blocker.
- Review and acceptance criteria require two independent plan reviews plus controller judgment before implementation.
- The plan references `docs/implementation-control.md` next entry which says "do not implement calibration before plan/review/accepted checkpoint".

No blocking findings.

---

## Focus Area 2: Slice 1 Requires Direct Retained Artifact + Fresh Real Smoke Evidence

**Finding**: PASS

Slice 1 has two mandatory evidence sources:

1. **Retained artifact inspection** — must locate the latest `reports/llm-runs/` directory for `fund_code=006597`, `report_year=2024`, `trigger=use_llm_incomplete`. Must read specific fields from `manifest.json`, `summary.json`, `chapters/chapter-02.json`, and draft/feedback files. Must classify failures by direct fields (`status`, `stop_reason`, `failure_category`, `failure_subcategory`, etc.).

2. **Fresh real LLM smoke rerun** — must run `006597 / 2024 --use-llm` with current provider configuration before any code change. Must record exit code, stdout empty status, orchestration_status, chapter matrix, first failed diagnostic, artifact path.

The plan explicitly states: "Implementation must start by locating the latest relevant local ignored run directory" and "Before any code change, rerun a real LLM smoke."

No blocking findings.

---

## Focus Area 3: Root-Cause Taxonomy Prevents Indirect Inference

**Finding**: PASS (with one non-blocking observation)

The taxonomy defines 6 classes with explicit direct evidence requirements:

| Class | Direct evidence gate |
|---|---|
| `prompt_contract_problem` | Draft violates existing contract despite adequate facts/anchors/repair feedback |
| `repair_guidance_gap` | Initial draft fails, auditor identifies issue, repair draft repeats same issue because repair context lacks correction |
| `diagnostic_clarity_gap` | Failure visible in draft/feedback but safe diagnostic classifies too broadly |
| `programmatic_audit_code_bug` | Audit code flags valid draft or misses invalid draft when checked against same draft/input/anchors/facts/contract |
| `fact_evidence_gap` | Writer cannot satisfy contract because projection lacks required values/anchors |
| `provider_runtime_blocker` | Provider runtime diagnostics show timeout/rate-limit/network/malformed before usable draft/audit |

The plan explicitly prohibits indirect inference: "Indirect evidence is not sufficient. Do not conclude 'L1 is too strict' merely from a failed chapter matrix. Do not conclude 'writer forgot anchors' unless the retained draft lines and auditor issue prove it."

**Non-blocking observation**: The taxonomy correctly separates the 6 classes. However, the plan does not define what happens when a chapter has **multiple contributing factors** (e.g., both `prompt_contract_problem` and `repair_guidance_gap` contribute to the same failure). The plan says "exactly one primary root-cause class, plus optional secondary observations" which is adequate, but the implementation agent should be aware that secondary observations may require their own residual owner assignment if they are independently actionable.

---

## Focus Area 4: Chapter 2 `l1_numerical_closure` Same-Source Evidence Requirement

**Finding**: PASS

The same-source rule for chapter 2 L1 calibration requires **all 8 conditions** to be true in the same retained run or rerun artifact:

1. `chapter_id=2`
2. `failure_category=prompt_contract`
3. `failure_subcategory=l1_numerical_closure`
4. prompt-contract diagnostic phase is `programmatic_audit` or auditor feedback contains a programmatic L1 issue
5. retained draft or repair draft contains an `R=A+B-C`, `A=R-B`, or `A-C` numerical assertion
6. the same local line or near context lacks the accepted anchor marker required by `_audit_numerical_closure()`
7. the relevant fact/anchor ids are available or the draft should have declared a data gap
8. the failure is not preceded by provider runtime timeout, missing draft, missing facts, invalid required markers, forbidden phrase, candidate facet assertion, or a higher-priority code path

This is strict and actionable. The conditions are checkable against specific retained artifact fields. The requirement that conditions 5-6 must be verified against the **same draft lines** (not just chapter-level metadata) enforces genuine same-source evidence.

No blocking findings.

---

## Focus Area 5: Plan Avoids Forbidden Scope Changes

**Finding**: PASS

The non-goals section explicitly prohibits:

- Relaxing auditor rules
- Increasing repair budget as default solution
- Deterministic fallback for incomplete results
- Partial or half-finished reports
- Provider timeout/retry/backoff budget changes
- Provider fallback, model fallback, multi-provider routing
- `chapter_generation_score` connection to score/golden/readiness/quality gate
- Quality gate, golden fixtures, golden answers, manifests, snapshot promotion, readiness, final judgment changes
- Template, design, control, startup doc changes
- `dayu-agent`, `dayu.host`, `dayu.engine` as production runtime dependencies
- Agent runner/tool-loop, async Host runner, durable session/resume/memory/outbox migration

The "Not acceptable" real smoke criterion further reinforces: "chapter 2 passes only because L1 is disabled/relaxed globally, repair budget increased, incomplete report emitted, deterministic fallback used, or unsafe diagnostics leak secrets."

No blocking findings.

---

## Focus Area 6: Slices Are Code-Generation-Ready

**Finding**: PASS (with minor non-blocking observations)

Each slice has:
- **Allowed/forbidden file matrix** — explicit and consistent across the plan
- **Validation requirements** — targeted pytest commands, `ruff check .`, real smoke rerun
- **Smoke criteria** — specific expected outcomes for each slice
- **Exit criteria** — controller can decide whether to continue or defer
- **Residual owners** — table assigns future gates for unresolved issues

**Non-blocking observation 1**: Slice 2 lists "Likely allowed source files" and "Likely allowed tests" — the word "likely" introduces ambiguity. The implementation agent must confirm allowed files against the actual root-cause finding before editing. This is acceptable for a calibration gate where the exact fix type depends on evidence, but the implementation evidence must explicitly justify each file touched.

**Non-blocking observation 2**: Slice 2 required tests include "Auditor test for a chapter 2 draft with numerical closure plus nearby allowed anchor marker passing L1, and a draft without nearby anchor marker failing L1." This is good but does not specify whether this tests the existing `_audit_numerical_closure()` behavior (regression) or a modified version. If the root cause is `programmatic_audit_code_bug`, the test must prove the bug fix; if the root cause is `prompt_contract_problem`, the test must prove the existing audit code correctly rejects the old draft and accepts the guided draft. The implementation agent should be explicit about which scenario applies.

---

## Focus Area 7: Chapters 3/6 Handled Without Broad Prompt Rewrite

**Finding**: PASS

Slice 3 explicitly constrains scope:

- "Slice 3 starts only after Slice 2 proves the chapter 2 path or Slice 1 proves chapters 3/6 share the same root cause."
- "It must not become a broad prompt rewrite for all body chapters."
- Allowed actions are limited to: same `l1_numerical_closure` pattern, different prompt-contract issue with narrow fix, or fact/evidence gap / provider runtime blocker (record residual owner only).
- "Broad all-chapter rewrite" is explicitly in the forbidden column.

No blocking findings.

---

## Focus Area 8: Secret Redaction and Safe Evidence Rules

**Finding**: PASS

The plan has a dedicated "Secret redaction and safe evidence" section that:

- Permits retained writer/repair drafts because the accepted artifact retention gate explicitly saves redacted drafts.
- Prohibits prompts, raw provider responses, raw auditor responses, API keys, Authorization/Bearer/cookies, request headers, full provider config, model names (if omitted by safe serializers), stack traces, and unredacted secret-looking substrings.
- Requires quoting only minimal lines needed to prove root cause, preferring paraphrase plus file path and field references.

The evidence protocol section also specifies: "command shape with secret-bearing environment omitted or redacted" for the fresh smoke rerun.

No blocking findings.

---

## Additional Adversarial Challenges

### Challenge A: What if the fresh smoke rerun shows provider runtime timeout as first blocker?

The plan handles this explicitly: "If first blocker is provider runtime timeout across chapters, do not implement prompt/auditor calibration in this gate; record provider runtime blocker and hand off to the future provider runtime budget calibration gate." Slice 1 exit criteria allow the controller to decide whether to continue or defer.

**Verdict**: Adequate.

### Challenge B: What if retained artifacts and fresh smoke show contradictory failure patterns?

The plan says: "The implementation evidence must not infer a root cause from old logs if the retained artifact fields contradict it." This handles the case where old evidence is stale. However, the plan does not explicitly state which evidence takes precedence when both exist and disagree — the retained artifact or the fresh smoke. Given that the fresh smoke uses the same code path, it should generally take precedence for current-state diagnosis, while retained artifacts provide historical pattern context.

**Verdict**: Non-blocking. The implementation agent should prioritize fresh smoke evidence when both exist, and note discrepancies in the evidence artifact.

### Challenge C: Is the `l1_numerical_closure` same-source rule too strict to be actionable?

The 8 conditions are individually checkable against retained artifact fields. Condition 8 ("not preceded by provider runtime timeout, missing draft, missing facts, invalid required markers, forbidden phrase, candidate facet assertion, or a higher-priority code path") is a negative condition that requires checking that none of the other failure classes apply first. This is achievable by reading the chapter JSON's `stop_reason` and `failure_category` fields, but it does require the implementation agent to perform a careful precedence check.

**Verdict**: Non-blocking. The strictness is appropriate for a heavy gate. The implementation agent should document the precedence check explicitly in the evidence artifact.

### Challenge D: Does the plan account for the case where chapter 2 `failure_category` is not `prompt_contract` at all?

The plan's expected smoke outcomes handle this: "If chapter 2 fails with `failure_category=prompt_contract` and `failure_subcategory=l1_numerical_closure`, continue to same-source L1 triage." The implicit corollary is that if chapter 2 fails with a different category (e.g., `provider_runtime_timeout` or `fact_evidence_gap`), the plan stops or records residual owners. This is correct.

**Verdict**: Adequate.

### Challenge E: Is `fund_agent/services/llm_run_artifacts.py` correctly scoped as "narrowly allowed"?

The plan allows `llm_run_artifacts.py` "only for diagnostic clarity and only if no schema-breaking change is needed." This is appropriate — diagnostic clarity improvements should not change the artifact schema that other tooling may depend on. The constraint is clear.

**Verdict**: Adequate.

---

## Verdict

**PASS** — No blocking findings.

The plan correctly maintains heavy gate discipline, requires direct retained artifact plus fresh real smoke evidence before any code change, enforces strict same-source root-cause classification, prohibits all forbidden scope changes, handles chapters 3/6 without broad rewrite, and provides adequate secret redaction rules.

### Non-blocking observations (do not require plan changes before acceptance):

1. **Secondary root-cause observations**: The plan allows "optional secondary observations" alongside the primary root-cause class. If secondary observations are independently actionable, they should be assigned their own residual owner. This is an implementation discipline point, not a plan gap.

2. **"Likely allowed" file lists**: Slice 2 uses "likely allowed" for source files and tests. The implementation agent must confirm each file against the actual root-cause finding before editing, and the implementation evidence must justify each file touched.

3. **Existing vs modified audit code test clarity**: The required auditor test for L1 pass/fail should explicitly state whether it tests existing `_audit_numerical_closure()` behavior (regression) or a modified version (bug fix), depending on the root-cause finding.

4. **Fresh smoke vs retained artifact precedence**: When both exist and disagree, the implementation agent should prioritize fresh smoke evidence for current-state diagnosis and note discrepancies explicitly.

---

## Reviewer Certification

I have reviewed this plan against all 8 specified focus areas plus 5 adversarial challenges. The plan is evidence-driven, maintains safety boundaries, and is code-generation-ready for the implementation agent. I recommend PASS.
