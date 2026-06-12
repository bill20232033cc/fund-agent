# AgentDS Plan Review: Release-readiness Non-live Verification Planning Gate

Date: 2026-06-12

Role: AgentDS

Gate: `Release-readiness non-live verification planning gate`

Review target: `docs/reviews/mvp-release-readiness-non-live-verification-plan-20260612.md`

Review type: adversarial plan review (planning gate only; no evidence execution)

## 1. Verdict

**PASS_WITH_FINDINGS**

The plan is structurally sound, preserves NOT_READY, defines narrow read/write boundaries, enumerates forbidden commands comprehensively, proposes deterministic non-live commands with live-access safeguards, and provides actionable failure classification. Three minor findings and one material residual are identified below; none block plan acceptance.

## 2. Review Checklist

| # | Question | Result | Evidence |
|---|---|---|---|
| 1 | Does the plan preserve NOT_READY until direct evidence exists? | PASS | Section 1: default remains NOT_READY until later accepted evidence gate proves otherwise with direct local evidence and controller judgment. Section 7 fact table: "Release/readiness remains unproven." Section 8 requires explicit readiness statement defaulting to NOT_READY. Section 13: final state leaves release/readiness NOT_READY. |
| 2 | Is read/write scope narrow enough for the later evidence gate? | PASS | Read set (Section 4) limits to core truth docs, plan/review/judgment artifacts, metadata git output, and deterministic command outputs; explicitly excludes PDF/report/audit bodies, cache, provider payloads, network responses, and historical review artifacts. Write set (Section 5) limits to one evidence artifact, DS/MiMo reviews, one controller judgment, and post-acceptance control sync; explicitly excludes source, tests, runtime, README, .gitignore, cache, reports, PDFs, fixtures, golden, provider config, lockfile, PR metadata, archive/delete/import/promote. |
| 3 | Are forbidden commands/actions complete enough? | PASS | Section 6 forbids: live EID, network/DNS/socket/HTTP probes, PDF download/parsing/FDR/FundDocumentRepository acquisition, provider/LLM/endpoint probes, fund-analysis analyze/analyze-annual-period/checklist, golden/fixture/baseline/readiness promotion, release/readiness commands, GitHub PR/push/merge/mark-ready/reviewer/approval/comment actions, and cleanup/delete/move/archive/ignore/import/promote. Cross-checked against implementation-control.md non-goal reminders and the static gap controller judgment rejected claims. `.gitignore` edits are covered by write-set exclusion (Section 5) rather than command list; this is acceptable since the write set already bounds file-level changes. |
| 4 | Are proposed verification commands deterministic and non-live under current repo conventions? | PASS_WITH_FINDING | V1-V4 are pure git metadata, deterministic. V5 is ruff lint, deterministic. V6-V10 are pytest runs; the plan explicitly states they must use "repository-independent fixtures only" and requires the evidence gate to stop if live access is detected. The safeguard is post-hoc (detect-and-stop) rather than pre-verified (no proof that every targeted test file avoids live acquisition). See Finding F4. |
| 5 | Are success criteria and failure classifications actionable? | PASS_WITH_FINDING | Each command has explicit success criteria and failure classification (blocker / material residual / non-blocking residual / blocking_question). The evidence table template (Section 8) requires command log, failure classification, residual owner table, readiness statement, and next entry. However, two gaps exist: (a) V9 classification depends on "current product/readiness-critical scope" vs "unrelated legacy failure" without operational criteria for making that distinction (Finding F1); (b) "blocking_question" is used in context but not formally defined in a taxonomy table (Finding F3). |
| 6 | Does the plan avoid fallback/source-acquisition drift and avoid using untracked artifacts as proof? | PASS | Section 2 fact table affirms EID single-source with fallback disabled; Eastmoney/fund-company/CDN/CNINFO are not current fallback design. Section 9 explicitly forbids reintroducing fallback sources, changing EID policy, changing FundDocumentRepository, changing provider defaults, promoting untracked artifacts as proof, using local PDFs as proof, treating historical live evidence as broad acceptance, and treating deterministic test pass as PR/release acceptance. |

## 3. Findings

| # | Severity | Finding | Evidence | Required Change |
|---|---|---|---|---|
| F1 | Material Residual | V9 (`uv run pytest -q`) failure classification depends on distinguishing "current product/readiness-critical scope" from "unrelated legacy failure." The plan provides no operational criteria for making this distinction at evidence-gate time. | Section 7, V9 row: "blocker if fails in current product/readiness-critical scope; material residual if unrelated legacy failure has owner and does not affect this gate." | Add to Section 8 evidence table requirements: the evidence gate must document the criteria used to classify each V9 failure and record the specific test paths and rationales. Alternatively, pre-define a list of "readiness-critical" test paths in the plan. |
| F2 | Minor | V10 coverage floor at 50% (`--cov-fail-under=50`) is documented as a gate, but the plan does not state that passing at 50% does not constitute coverage sufficiency for readiness. This risks a future evidence gate treating the 50% pass as a positive coverage signal. | Section 7, V10 row; contrast with AGENTS.md single-file ≥80% target. | Add an explicit note: "Passing V10 at 50% is a floor sanity check only; it does not demonstrate coverage sufficiency. The readiness statement must not claim coverage adequacy based solely on V10 passing." |
| F3 | Minor | "blocking_question" is used as a failure classification (for live-access detection and dependency-resolution failure) but is not formally defined in a taxonomy table alongside blocker/material residual/non-blocking residual. | Section 7 paragraphs after V10; Section 8 failure classification requirement. | Add a one-line taxonomy entry: "blocking_question: the evidence gate cannot proceed without external resolution (e.g., dependency installation, user authorization); does not itself prove or disprove readiness." |
| F4 | Minor | The plan relies on post-hoc detection to verify that `uv run pytest` commands are non-live ("If a command attempts network/provider/live acquisition, the evidence gate must stop"). It does not require the evidence gate to pre-audit targeted test files for mock/fixture usage before execution. | Section 7 safeguard paragraph after V10. | Add to Section 8 evidence table requirements: the evidence gate must report whether any targeted test file imports or calls live provider/network/FDR APIs, based on static inspection of test file imports. |

## 4. Residuals and Risks

| # | Residual / Risk | Severity | Owner | Mitigation |
|---|---|---|---|---|
| R1 | V9 broad-test failure classification requires scope judgment at evidence-gate time without pre-defined criteria. | Medium | Evidence-gate executor / controller | Addressed by F1 required change; if not addressed before evidence gate, controller judgment must provide the classification criteria. |
| R2 | Process residuals (AgentCodex pane, sub-agent thread limit) accepted by controller in Section 3 do not block plan review but could affect evidence-gate worker reliability. | Low | Controller / worker-channel owner | Explicit handoff boundaries already required by static gap controller judgment; verify clean session before evidence gate execution. |
| R3 | The plan delegates verification that test files are non-live to runtime detection. A test that performs live acquisition only on a code path not exercised by the evidence gate's specific test invocation would not be detected. | Low | Evidence-gate executor | Static import audit (F4) partially mitigates; full mitigation requires pre-verified test isolation guarantees beyond this plan's scope. |
| R4 | Coverage floor at 50% could normalize low coverage as "passed" in subsequent gates if the distinction between floor and sufficiency is not maintained. | Low | Controller / future gate authors | Addressed by F2 required change; controller judgment should reaffirm the distinction at acceptance. |

## 5. Adversarial Pass

- **What if a V6-V8 test file has a live import that isn't exercised?** The post-hoc detection would miss it. The plan's safeguard only triggers on actual live access, not on capability. F4 partially addresses this.
- **What if `uv run` resolves test dependencies from a cache that was populated by a prior live run?** The plan treats `uv run` dependency resolution failure as blocking_question. If resolution succeeds from cache, the evidence gate may not detect that dependencies were originally obtained via network. This is inherent to local Python tooling and not unique to this plan; the safeguard against live acquisition during test execution is the primary defense.
- **What if `git diff --name-only` shows changes to source files that were made before plan acceptance but not yet committed?** V3 classifies this as blocker if "source/tests/runtime/config/README/control docs changed before plan acceptance without authorization." This correctly catches pre-existing drift.
- **What if a test in V9 fails due to environment differences (Python version, OS, missing system dependency) rather than code defects?** The plan classifies this as blocker if in readiness-critical scope. The evidence gate should distinguish environment failures from code failures, but the plan doesn't require this. This is implicitly covered by the V9 classification judgment (F1).

No adversarial scenario was found that would cause the plan to produce a false readiness claim, provided the safeguards are followed and the NOT_READY default is honored.

## 6. Scope Compliance

This review:
- Read only the required read set plus `AGENTS.md`
- Did not modify source, tests, runtime, docs/design.md, docs/current-startup-packet.md, or docs/implementation-control.md
- Did not run live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands
- Did not stage, commit, push, PR, merge, cleanup, delete, move, archive, ignore, import, or promote files
- Wrote only this review artifact under the allowed write set

## 7. Recommendation

Accept the plan with the four findings recorded. F1 (V9 classification criteria) is the most impactful and should be addressed in the plan or deferred to controller judgment before the evidence gate executes. F2-F4 are minor and can be addressed editorially or accepted as documented residuals.

The plan correctly preserves NOT_READY, defines appropriately narrow boundaries, and provides a workable deterministic verification matrix. No finding blocks plan acceptance.
