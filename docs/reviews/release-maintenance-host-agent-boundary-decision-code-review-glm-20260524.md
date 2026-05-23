# Release Maintenance Host/Agent Boundary Decision — Code Review (GLM) - 2026-05-24

## Reviewer

- Reviewer: AgentGLM
- Model: GLM-5.1
- Role: code review worker; not controller.
- Review lens: correctness and architecture-boundary review for document-only implementation.

## Reviewed Artifacts

| Artifact | Role |
|---|---|
| `docs/reviews/release-maintenance-next-candidate-plan-20260524.md` | Approved plan (commit `ccde2f7`) |
| `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Implemented decision artifact |
| `docs/reviews/release-maintenance-host-agent-boundary-decision-implementation-20260524.md` | Implementation handoff artifact |

## Truth Sources Consulted

| Source | Sections / Scope Used |
|---|---|
| `AGENTS.md` | §硬约束, §模块边界, §边界执行规则 |
| `docs/design.md` | §1.3, §2.1, §2.2, §9.1, §12 |
| `docs/implementation-control.md` | Startup Packet, next release-maintenance candidates, gate history |
| Current `pyproject.toml` | Dependency check (no `dayu` text) |
| Current repository directory structure | `fund_agent/host` and `fund_agent/agent` do not exist |

## Validation Run

| Check | Command or Method | Expected | Observed |
|---|---|---|---|
| Top-level section skeleton | `rg -n "^## " decision.md` | 13 sections matching plan skeleton | 13 sections present: Gate/Scope, Direct Evidence, Current-State Decision, Host Gate Entry Criteria, Agent Execution Gate Entry Criteria, Dependency Gate Status, Future Gate Skeletons, Validation Plan, Review Checklist, Stop Conditions, Decision Absorption Path, Completion Report Format, Handoff Status |
| Boundary and guardrail terms | `rg` for `dayu.host`, `dayu.engine`, `extra_payload`, `pyproject`, `fund_agent/host`, `fund_agent/agent`, `UI -> Service -> Host -> Agent` | All required terms present | All present with correct context |
| Dependency gate blocked | `rg` for `dependency gate remains blocked` / `blocked until implementation imports` | Present | Present |
| No placeholder packages | `rg` for `no fund_agent/host` / `no fund_agent/agent` | Present | Present |
| No explicit params in extra_payload | `rg` for `extra_payload` | Present as prohibition, not as usage | Correct |
| Local/external baseline | `rg` for `local baseline`, `docs/design.md.*9\.1`, `external dayu-agent`, `URL`, `commit`, `provenance` | All present | All present |
| Future gate skeletons | `rg` for `Host implementation gate`, `Agent execution/tool-loop gate`, `Dependency gate`, `Stop Conditions` | All present | All present with sub-sections |
| Future dependency validation commands | `rg` for `dayu.*pyproject`, `uv lock --check`, `tool\.setuptools\.packages\.find`, `tool\.setuptools\.package-data` | Present in dependency gate skeleton | Present |
| Only allowed files changed | `git status --short` | Two new `docs/reviews/` files only | Exactly the decision artifact and implementation artifact, both untracked |
| No source/test/config changes | Cross-check git status | No changes outside `docs/reviews/` | Confirmed |
| FundDocumentRepository boundary preserved | Decision artifact §Agent Execution Gate Entry Criteria stop conditions | Stop condition for bypassing repository | Present: "Agent plan bypasses `FundDocumentRepository` / `FundDataExtractor` for production annual-report access" |
| License/repo hygiene preserved | Decision artifact §Stop Conditions | Stop condition for hygiene weakening | Present |
| No six-layer/Application/Runtime wording as current truth | Decision artifact §Direct Evidence | Historical-only disclaimer | Present: "They are not current architecture truth." |

## Review Checklist Verification

| # | Checklist item (from approved plan §Review Gates) | Verdict | Evidence |
|---|---|---|---|
| 1 | Current truth uses Dayu four-layer `UI -> Service -> Host -> Agent` | Pass | Decision artifact §Direct Evidence cites AGENTS.md; §Current-State Decision records target boundary |
| 2 | Current deterministic default remains UI -> Service -> `fund_agent/fund` | Pass | Decision artifact §Current-State Decision: "keep the current deterministic UI -> Service -> `fund_agent/fund` transition as the default production path" |
| 3 | Host, if landed, must use `dayu.host` | Pass | Decision artifact §Host Gate Entry Criteria: "Implementation must use `dayu.host`" |
| 4 | Agent execution/tool-loop, if landed, must use `dayu.engine` | Pass | Decision artifact §Agent Execution Gate Entry Criteria: "Implementation must use `dayu.engine`" |
| 5 | No `fund_agent/host` or `fund_agent/agent` placeholder package is created | Pass | `git status --short` confirms no package directories; decision artifact Non-goals explicitly states this |
| 6 | Dependency gate remains blocked until production implementation imports require it | Pass | Decision artifact §Dependency Gate Status: "Host/Agent dependency gate remains blocked until implementation imports require it" |
| 7 | No source/test/config/README/design/control/pyproject/lockfile changes | Pass | `git status --short` shows only two new `docs/reviews/` files |
| 8 | No explicit parameter is hidden in `extra_payload` or `extra_payloads` | Pass | Decision artifact Non-goals and both gate constraint sections explicitly prohibit this |
| 9 | Future package/dependency changes check local `docs/design.md` section 9.1 plus current `pyproject.toml` | Pass | Decision artifact §Dependency Gate Status and §Direct Evidence local baseline entry both reference this |
| 10 | Any external `dayu-agent` pyproject comparison records URL, commit/revision, fetched content/provenance, and delta | Pass | Decision artifact §Direct Evidence external baseline rule and §Future Gate Skeletons dependency gate both require this |
| 11 | Production annual-report access remains through `FundDocumentRepository` / `FundDataExtractor` | Pass | Decision artifact §Agent Execution Gate Entry Criteria stop conditions and constraints both enforce this |
| 12 | License/repo hygiene is preserved and not weakened | Pass | Decision artifact §Stop Conditions includes hygiene weakening as a stop trigger; no pyproject.toml changes |
| 13 | No historical six-layer/Application/Runtime/Engine wording is used as current architecture basis | Pass | Decision artifact §Direct Evidence explicitly disclaims historical wording as current truth |

## Findings

### C1 — Non-blocking: implementation artifact section count inaccuracy

- **Severity**: low (cosmetic)
- **Location**: `docs/reviews/release-maintenance-host-agent-boundary-decision-implementation-20260524.md` §Validation, row 1
- **Description**: The implementation artifact states the `rg -n "^## "` validation "lists the 12 required sections". The approved plan skeleton defines 13 top-level sections (Gate/Scope, Direct Evidence, Current-State Decision, Host Gate Entry Criteria, Agent Execution Gate Entry Criteria, Dependency Gate Status, Future Gate Skeletons, Validation Plan, Review Checklist, Stop Conditions, Decision Absorption Path, Completion Report Format, Handoff Status). The actual decision artifact contains all 13.
- **Impact**: None on decision correctness. The decision artifact is accurate; only the implementation artifact's count description is off by one.
- **Recommendation**: If the implementation artifact is revised, correct the count from 12 to 13. No blocker.

## Scope Creep Assessment

- No source, test, config, README, design, control, pyproject, or lockfile changes detected.
- No `fund_agent/host` or `fund_agent/agent` package created.
- No dependency declaration added.
- The decision artifact is purely documentary; it records decisions and entry criteria for future gates without implementing any of them.
- No misleading future-work-as-done language detected. The decision artifact explicitly states: "The target boundary is a future implementation direction, not authorization to create placeholder packages in this gate."

## Stop Condition Assessment

No stop conditions triggered. All stop conditions from the approved plan and the decision artifact itself remain unsatisfied (correctly):

- No Host or Agent implementation attempted in this gate.
- No dependency added without concrete implementation import.
- No six-layer/Application/Runtime/Engine revival.
- No scope expansion beyond a decision artifact.
- No forbidden file modifications.
- No `extra_payload` proposals.

## Conclusion

**PASS**

The decision artifact faithfully implements the approved plan. It preserves the deterministic UI -> Service -> `fund_agent/fund` default, records correct Host (`dayu.host`) and Agent (`dayu.engine`) gate entry criteria, keeps the dependency gate blocked until production imports require it, and does not create placeholder packages or change any source/test/config/dependency files. One non-blocking cosmetic finding on section count in the implementation artifact.

---

- **Artifact**: `docs/reviews/release-maintenance-host-agent-boundary-decision-code-review-glm-20260524.md`
- **Conclusion**: PASS
- **Finding count**: 1 (non-blocking)
- **Blocking questions**: none
