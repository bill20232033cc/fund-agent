# Adversarial Plan Re-Review: Release Maintenance Next Candidate Plan (2026-05-24)

> **Reviewer**: GLM
> **Revised plan**: `docs/reviews/release-maintenance-next-candidate-plan-20260524.md`
> **Fix artifact**: `docs/reviews/release-maintenance-next-candidate-plan-fix-20260524.md`
> **Controller judgment**: `docs/reviews/release-maintenance-next-candidate-plan-review-controller-judgment-20260524.md`
> **Source review (GLM lane)**: `docs/reviews/release-maintenance-next-candidate-plan-review-glm-20260524.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` v2.2, `docs/implementation-control.md` Startup Packet
> **Date**: 2026-05-24

---

## Conclusion: PASS

All 9 accepted findings are fully fixed. No new blocker introduced.

---

## Per-Finding Verification

### C1-accepted-MiMo-F1 / dayu-agent pyproject baseline definition is too vague

**Status: 已修复**

**Controller required fix**: Clarify local baseline as `docs/design.md` §9.1 plus current `pyproject.toml`; external `dayu-agent` pyproject requires URL/commit/provenance; add concrete validation commands.

**Verification in revised plan**:

| Requirement | Location | Evidence |
|---|---|---|
| Local baseline defined as `docs/design.md` §9.1 + current `pyproject.toml` | Line 35 | "docs/design.md §9.1 + 当前 pyproject.toml 是本地 Dayu-Agent 工程吸收基线" with full enumeration of Python >=3.11, setuptools, PEP 621, dependencies, pytest/ruff/black, package discovery exclusions, and current lack of `[tool.setuptools.package-data]` |
| External `dayu-agent` provenance required | Line 36 | "未来 dependency gate 如需对照外部 dayu-agent，必须记录精确 URL、commit/revision、获取时间、摘要内容或完整片段，以及该外部内容与本地 docs/design.md §9.1 / pyproject.toml 的差异" |
| Dependency gate trigger references local baseline | Line 156-157 | "checked against the local baseline: docs/design.md §9.1 plus current pyproject.toml"; "any external dayu-agent pyproject.toml comparison records URL, commit/revision, fetched content/provenance, and delta from the local baseline" |
| Concrete validation commands added | Lines 180-183 | Dependency gate command set: `rg -n "dayu" pyproject.toml`, `uv lock --check`, `rg -n "tool\\.setuptools\\.(packages\\.find|package-data)|include-package-data" pyproject.toml`, import smoke checks |

Fix artifact validation confirms: `rg -n "dayu" pyproject.toml` returned no match (exit code 1), `uv lock --check` passed, setuptools config found. All consistent with plan's baseline statement.

---

### C2-accepted-MiMo-F2 / decision artifact skeleton missing

**Status: 已修复**

**Controller required fix**: Add a minimal required section outline for the boundary decision artifact.

**Verification in revised plan**:

| Requirement | Location | Evidence |
|---|---|---|
| Required section skeleton added | Lines 61-75 | 13-section skeleton listed: Gate/Scope, Direct Evidence, Current-State Decision, Host Gate Entry Criteria, Agent Execution Gate Entry Criteria, Dependency Gate Status, Future Gate Skeletons, Validation Plan, Review Checklist, Stop Conditions, Decision Absorption Path, Completion Report Format, Handoff Status |

Skeleton is concrete, does not expand scope, and provides sufficient structure for the implementer without mandating content.

---

### C3-accepted-MiMo-F3 / validation should distinguish existence checks from semantic review

**Status: 已修复**

**Controller required fix**: State that `rg` commands are existence checks and semantic correctness is covered by plan/review gates.

**Verification in revised plan**:

| Requirement | Location | Evidence |
|---|---|---|
| Explicit validation scope note | Lines 116-118 | "Validation note: All rg commands in this plan are programmatic existence checks only. They prove required terms or guardrails are present in the artifact; they do not prove the decision is semantically correct. Semantic correctness, boundary fit, and evidence quality are covered by the plan review / re-review gates." |

The note is placed before all slices, applies uniformly, and correctly delegates semantic correctness to review gates.

---

### C4-accepted-MiMo-F4 / accepted decision absorption path missing

**Status: 已修复**

**Controller required fix**: Add Decision absorption path to completion/reporting: controller records accepted decision in control tracking or opens a separate docs/control update only if the decision changes current truth.

**Verification in revised plan**:

| Requirement | Location | Evidence |
|---|---|---|
| Decision absorption path in Slice 4 | Line 201 | "Add Decision absorption path describing how an accepted decision is recorded: controller records it in control tracking, or opens a separate docs/control update only if the accepted decision changes current truth." |
| Decision absorption path in completion report | Line 281 | "Decision absorption path:" listed as required completion report field |

Correctly scoped: does not authorize direct control_doc changes, defers to controller for tracking.

---

### C5-accepted-MiMo-F5 / stop-condition report format missing

**Status: 已修复**

**Controller required fix**: Add minimal stop report format: triggered condition, context/evidence, suggested scope adjustment, and whether user decision is required.

**Verification in revised plan**:

| Requirement | Location | Evidence |
|---|---|---|
| Stop report format added | Lines 251-256 | Four fields: Triggered condition, Context/evidence, Suggested scope adjustment, User decision required: yes/no |

Minimal and appropriate. Does not over-specify while giving controller sufficient context for scope裁决.

---

### C6-accepted-GLM-F1 / code-generation-ready wording misstates document-only deliverable

**Status: 已修复**

**Controller required fix**: Replace or qualify `code-generation-ready` with `plan-review-ready decision plan`.

**Verification in revised plan**:

| Requirement | Location | Evidence |
|---|---|---|
| Wording replaced in Goal | Line 5 | "给出 plan-review-ready 决策计划" — replaces "code-generation-ready 实施计划" |
| Document-only nature explicitly stated | Line 5 | "本 work unit 是 document-only boundary decision，不授权代码生成、Host/Agent 实现、依赖修改或包结构变更。" |
| No residual "code-generation-ready" | Full plan scan | String "code-generation-ready" does not appear anywhere in the revised plan |

---

### C7-accepted-GLM-F2 / Slice 2 validation lacks executable command

**Status: 已修复**

**Controller required fix**: Add rg validation command for dependency-gate-blocked, no placeholder packages, and no extra_payload.

**Verification in revised plan**:

| Requirement | Location | Evidence |
|---|---|---|
| rg command added to Slice 2 | Line 164 | `rg -n "dependency gate remains blocked\|blocked until implementation imports\|no fund_agent/host\|no fund_agent/agent\|extra_payload\|local baseline\|docs/design.md.*9\\.1\|external dayu-agent\|URL\|commit\|provenance" docs/reviews/release-maintenance-host-agent-boundary-20260524.md` |

Command covers all required assertions (dependency gate blocked, no placeholder, no extra_payload) and additionally covers baseline provenance terms (local baseline, design.md §9.1, external dayu-agent, URL, commit). More comprehensive than minimum required. Consistent with Slice 1 and Slice 3 rg command style.

---

### C8-accepted-GLM-F3 / completion validation field lacks pass criteria

**Status: 已修复**

**Controller required fix**: Specify that Validation run records each command, expected assertion, and exit code or observed pass signal.

**Verification in revised plan**:

| Requirement | Location | Evidence |
|---|---|---|
| Pass criteria specified | Line 280 | "Validation run: list each command, expected assertion, exit code or observed pass signal, and any skipped validation with reason." |

Concrete enough: each validation entry must include command, assertion, and result signal. Also handles the edge case of skipped validations with documented reason.

---

### C9-accepted-GLM-F4 / design.md §12 checklist incomplete

**Status: 已修复**

**Controller required fix**: Add review checklist items for production annual-report access through FundDocumentRepository/FundDataExtractor, and License/repo hygiene.

**Verification in revised plan**:

| Requirement | Location | Evidence |
|---|---|---|
| Annual-report access checklist item | Line 236 | "Confirms production annual-report access remains through FundDocumentRepository / FundDataExtractor only." |
| License/repo hygiene checklist item | Line 237 | "Confirms License/repo hygiene is preserved and not weakened by test or metadata relaxation." |

Review checklist expanded from 8 to 11 items. Both new items align with design.md §12 requirements. The annual-report item uses the exact interface names from design.md §6.1. The License item includes the "not weakened by test or metadata relaxation" guard consistent with design.md §9.1 `License` requirement.

---

## New Issue Scan

No new blocker introduced by the fix. Specific checks:

| Check | Result |
|---|---|
| Scope still document-only | PASS — no code, dependency, package, or config changes authorized |
| No placeholder fund_agent/host or fund_agent/agent created | PASS — §Non-Goals, §Affected Files, §Stop Conditions all maintain prohibition |
| Host still dayu.host, Agent still dayu.engine | PASS — all references unchanged |
| No extra_payload for explicit parameters | PASS — prohibition maintained in Non-Goals, Slice 2, Review Gates, Stop Conditions |
| No historical architecture as current truth | PASS — Non-Goals and Stop Conditions unchanged |
| No design/control/doc truth modification | PASS — still explicitly forbidden |
| Baseline provenance requirement does not imply current external fetch | PASS — Line 36 clearly states "不属于本地既有事实" and only requires provenance when a future gate actually compares |
| Artifact skeleton does not expand scope | PASS — skeleton is structural, not substantive |
| Validation note does not weaken existing checks | PASS — correctly scopes rg to existence, delegates semantics to review gates |

---

## Final Status Mapping

| Finding | Final Status |
|---|---|
| C1 dayu-agent pyproject baseline | 已修复 |
| C2 decision artifact skeleton | 已修复 |
| C3 rg validation limits | 已修复 |
| C4 decision absorption path | 已修复 |
| C5 stop-condition report format | 已修复 |
| C6 code-generation-ready wording | 已修复 |
| C7 Slice 2 executable rg command | 已修复 |
| C8 validation pass criteria | 已修复 |
| C9 review checklist completeness | 已修复 |

---

## Blocking Questions

None.
