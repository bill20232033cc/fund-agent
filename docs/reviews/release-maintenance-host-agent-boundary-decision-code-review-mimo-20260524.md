# Release Maintenance Host/Agent Boundary Decision Code Review - 2026-05-24

## Gate

- Current phase: `release maintenance`.
- Current gate: `release-maintenance Host/Agent boundary decision code review`.
- Worker role: review worker only; not controller.
- External actions: none.
- Files modified by reviewer: none.

## Reviewed Artifacts

| Artifact | Path |
|---|---|
| Decision artifact | `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` |
| Implementation artifact | `docs/reviews/release-maintenance-host-agent-boundary-decision-implementation-20260524.md` |
| Approved plan | `docs/reviews/release-maintenance-next-candidate-plan-20260524.md` |

## Truth Sources Consulted

| Source | Key facts verified |
|---|---|
| `AGENTS.md` | Four-layer boundary `UI -> Service -> Host -> Agent`; Host must use `dayu.host`; Agent execution kernel must use `dayu.engine`; explicit params forbidden in `extra_payload`; current deterministic transition path is Service calling `fund_agent/fund` public capabilities. |
| `docs/design.md` (v2.2) | Section 1.3: no Host/tool-loop/LLM splicing in current deterministic mainline. Section 2.1: current CLI is UI -> Service -> `fund_agent/fund`. Section 2.2: no `HostRun`/`AgentInput`/scene preparation mainline; no empty Host/Agent packages without concrete need. Section 9.1: local engineering baseline. Section 12: plan review boundary checks. |
| `docs/implementation-control.md` Startup Packet | Current gate: `release maintenance next candidate plan accepted locally`; next entry: `release-maintenance Host/Agent boundary decision implementation`. Guardrails: no placeholder `fund_agent/host` or `fund_agent/agent` before independent gate; historical six-layer/Runtime/Engine is evidence-only. |
| Current repository facts | `fund_agent/host` and `fund_agent/agent` directories do not exist. `pyproject.toml` has no `dayu.host` or `dayu.engine` dependency. Only two untracked `docs/reviews/` files present; no tracked files modified. |

## Review Checklist

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Current truth uses Dayu four-layer `UI -> Service -> Host -> Agent` | PASS | Decision artifact line 26, 62; direct evidence table correctly cites `AGENTS.md` and `docs/design.md` sections 1.3, 2.1, 2.2. |
| 2 | Current deterministic default remains UI -> Service -> `fund_agent/fund` | PASS | Decision artifact lines 44-57; `Current-State Decision` section explicitly preserves this path. |
| 3 | Host, if landed, must use `dayu.host` | PASS | Decision artifact lines 26, 83, 86, 149-185; Host gate entry criteria and Host implementation gate skeleton both require `dayu.host`. |
| 4 | Agent execution/tool-loop, if landed, must use `dayu.engine` | PASS | Decision artifact lines 27, 106, 110, 186-226; Agent gate entry criteria and Agent execution gate skeleton both require `dayu.engine`. |
| 5 | No `fund_agent/host` or `fund_agent/agent` placeholder package created | PASS | Decision artifact lines 16, 35, 120; implementation artifact lines 31-32; `git status --short` confirms only `docs/reviews/` files. |
| 6 | Dependency gate remains blocked until production implementation imports require it | PASS | Decision artifact lines 114-143; states gate may open only when controller-approved implementation imports `dayu.host` or `dayu.engine` in production code. |
| 7 | No source/test/config/README/design/control/pyproject/lockfile changes | PASS | `git diff --name-only` shows no tracked file changes; `git status --short` shows only two untracked `docs/reviews/` files. |
| 8 | No explicit parameter hidden in `extra_payload` / `extra_payloads` | PASS | Decision artifact lines 20, 29, 86, 110, 163, 184, 203, 224; future gate skeletons include `extra_payload` as stop condition. |
| 9 | Future package/dependency changes check local baseline `docs/design.md` section 9.1 plus current `pyproject.toml` | PASS | Decision artifact lines 37, 129-131, 239; dependency gate skeleton requires local baseline comparison. |
| 10 | External `dayu-agent` pyproject comparison records URL, commit/revision, fetched content/provenance, and delta from local baseline | PASS | Decision artifact lines 38, 130, 240, 258; dependency gate skeleton requires provenance tracking. |
| 11 | Production annual-report access remains through `FundDocumentRepository` / `FundDataExtractor` | PASS | Decision artifact line 109, 211, 223; Agent execution gate stop conditions block direct PDF/source/cache access. |
| 12 | License/repo hygiene unchanged and not weakened | PASS | Decision artifact has no metadata, test relaxation, or hygiene weakening language. |
| 13 | Historical six-layer/Application/Runtime/Engine wording not used as current architecture basis | PASS | Decision artifact line 40 explicitly marks such artifacts as "historical evidence only" and "not current architecture truth." |

## Plan Conformance

| Plan requirement | Status | Evidence |
|---|---|---|
| Required section skeleton (12 sections) | Done | Decision artifact includes all 12 required top-level sections; no extra top-level sections. |
| Direct evidence table with citations | Done | Lines 24-38 cite `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `pyproject.toml`, directory fact, local baseline, and external baseline rule. |
| Current-state decision matrix | Done | Lines 42-65 record deterministic path as default with reasoning. |
| Host gate entry criteria with triggers and constraints | Done | Lines 67-87 define 5 allowed triggers, `dayu.host` requirement, and boundary constraints. |
| Agent execution gate entry criteria with triggers and constraints | Done | Lines 89-111 define 6 allowed triggers, `dayu.engine` requirement, and boundary constraints. |
| Dependency gate status blocked until needed | Done | Lines 113-143 record current status, open conditions, future checks, and validation commands. |
| Future gate skeletons (Host, Agent, Dependency) | Done | Lines 145-260 include all three gate skeletons with allowed files, contracts, tests, README triggers, and stop conditions. |
| Validation plan with exact commands | Done | Lines 262-283 include all 5 required `rg` commands plus `git diff --check` and `git status --short`. |
| Review checklist | Done | Lines 285-299 cover all 13 review items from the approved plan. |
| Stop conditions with stop report format | Done | Lines 301-319 define 8 stop conditions and the required stop report fields. |
| Decision absorption path | Done | Lines 321-328 describe controller tracking or separate docs/control update. |
| Completion report format | Done | Lines 330-343 define the implementer completion report fields. |
| Handoff status | Done | Line 347: "ready for plan review." |

## Validation Run (Reviewer Independent Verification)

| Command | Expected | Result |
|---|---|---|
| `rg -n "UI -> Service -> Host -> Agent\|dayu.host\|dayu.engine\|extra_payload\|pyproject\|fund_agent/host\|fund_agent/agent" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Required terms present | PASS; all required terms found across 20+ matching lines. |
| `rg -n "dependency gate remains blocked\|blocked until implementation imports\|no fund_agent/host\|no fund_agent/agent\|extra_payload\|local baseline\|docs/design.md.*9\.1\|external dayu-agent\|URL\|commit\|provenance" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Guardrail terms present | PASS; all required terms found across 15+ matching lines. |
| `rg -n "Host implementation gate\|Agent execution/tool-loop gate\|Dependency gate\|Stop Conditions" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Future gate sections present | PASS; Host implementation gate (line 147), Agent execution/tool-loop gate (line 186), Dependency gate (line 227), Stop Conditions (line 301). |
| `rg -n "rg -n .*dayu.*pyproject\.toml\|uv lock --check\|tool\.setuptools\.packages\.find\|tool\.setuptools\.package-data\|package discovery\|package-data\|URL\|commit\|provenance" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Validation commands present | PASS; dependency validation commands found at lines 138-140, 248-250, 272. |
| `git diff --check` | No whitespace errors | PASS; exit code 0. |
| `git status --short` | Only two allowed `docs/reviews/` files | PASS; shows exactly two untracked files: the decision artifact and the implementation artifact. |

## Findings

Finding count: 0.

No blocking findings. No non-blocking findings.

## Semantic Assessment

The decision artifact correctly:

1. Preserves the current deterministic `UI -> Service -> `fund_agent/fund`` production path as the default.
2. Defines concrete, evidence-backed entry criteria for each future gate (Host, Agent execution, dependency) rather than opening them prematurely.
3. Keeps the dependency gate blocked until production imports actually require `dayu.host` or `dayu.engine`, avoiding unused-dependency pollution against the local engineering baseline.
4. Maintains the `extra_payload` / `extra_payloads` prohibition consistently across all gate skeletons and stop conditions.
5. Requires local baseline (`docs/design.md` section 9.1 + current `pyproject.toml`) and external provenance tracking for any future dependency comparison.
6. Preserves the `FundDocumentRepository` / `FundDataExtractor` annual-report access boundary in Agent execution gate stop conditions.
7. Distinguishes historical six-layer/Runtime/Engine evidence from current four-layer architecture truth.
8. Implements all 12 required plan sections with no scope creep or missing content.

The implementation artifact's validation table is truthful: all claimed pass results are independently verified. Skipped validations (test suite, `uv lock --check`) are correctly justified as inapplicable to a document-only work unit.

## Conclusion

**PASS**

Zero blocking findings. Zero non-blocking findings. Implementation follows the approved plan exactly. Only allowed files changed. Decision artifact is architecturally sound, internally consistent, and faithful to all truth sources.

## Completion Report

- Artifact paths:
  - Decision artifact: `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`
  - Implementation artifact: `docs/reviews/release-maintenance-host-agent-boundary-decision-implementation-20260524.md`
  - This review artifact: `docs/reviews/release-maintenance-host-agent-boundary-decision-code-review-mimo-20260524.md`
- Decision: PASS.
- Future gates opened / blocked: Host implementation gate, Agent execution/tool-loop gate, and Dependency gate all remain blocked with documented entry criteria.
- Changed files: none (review-only).
- Validation run: all 6 commands pass as documented above.
- Docs decision: no docs/control updates required by this review.
- Residual risks: `rg` checks are existence-only; semantic correctness is confirmed by this manual review.
- Decision absorption path: controller records accepted decision in control tracking; any truth change requires separate docs/control update.
- Blocking questions: none.
- Recommended next gate: `release-maintenance Host/Agent boundary decision code review controller judgment`.
