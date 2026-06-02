# MVP real LLM chapter acceptance calibration gate - Slice 1 controller judgment after provider restore

## Controller Self-Check

- Current gate / role: `MVP real LLM chapter acceptance calibration gate`, controller judgment only.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/fund-analysis-template-draft.md`, retained Slice 1 artifact `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431`, and triage summary `reports/manual-llm-smoke/mvp-real-llm-chapter-acceptance-slice1-20260602-195518/slice1-evidence-triage-summary.md`.
- Scope boundary: classify Slice 1 evidence and decide whether a narrow Slice 2 planning gate is authorized. No implementation, no provider runtime budget change, no auditor relaxation, no score-loop, no deterministic fallback, no stdout behavior change, no secret-bearing artifact.
- Stop conditions: implementation remains blocked until a Ch3-only plan and independent review are accepted.
- Evidence and validation: same-source retained chapter files exist for Ch3 writer draft, repair draft and two auditor feedback files; Ch2/Ch6 have provider timeout evidence and are deferred.

## Branch And Worktree Baseline

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Worktree note: repository already contains unrelated untracked review/report artifacts. This judgment only adds this `docs/reviews/` artifact.

## Slice 1 Evidence Accepted For Classification

Provider config was restored and the fresh smoke was executed:

- Command: `fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress`
- Env presence: `FUND_AGENT_LLM_PROVIDER`, `FUND_AGENT_LLM_MODEL`, `FUND_AGENT_LLM_BASE_URL`, `FUND_AGENT_LLM_API_KEY` were all recorded as `set`; values were not printed.
- Exit code: `1`
- Stdout: `0` bytes, preserving fail-closed no-partial-report behavior.
- Stderr/progress: `8914` bytes.
- Retained artifact: `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431`
- Run summary: `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json`
- Slice 1 triage summary: `reports/manual-llm-smoke/mvp-real-llm-chapter-acceptance-slice1-20260602-195518/slice1-evidence-triage-summary.md`

The retained artifact is sufficient same-run evidence for chapter-level classification. The old control-doc statement that Slice 1 stopped before orchestration due to missing provider config is stale for this resumed gate and must not override this fresh smoke evidence.

## Controller Classification

### Chapter 2

Decision: provider runtime blocker; defer to the provider runtime budget calibration gate.

Evidence:

- `chapter-02.json` status is `failed`.
- `stop_reason=llm_timeout`.
- Failure occurred in auditor, not writer.
- Provider attempts were `2/2`.
- Each auditor attempt timed out at about `60s`.
- Runtime diagnostics classify the attempts as `provider_runtime_category=timeout`.
- `timeout_root_cause_hint=small_prompt_provider_timeout`.
- `approx_prompt_tokens=743`, `system_prompt_chars=54`, `user_prompt_chars=2917`.

Judgment:

- This is not current chapter-acceptance calibration scope.
- Do not touch Ch2 in the next planning gate.
- Do not change provider runtime budget in this gate.

### Chapter 6

Decision: mixed failure, but currently provider runtime blocker after repair; defer to the provider runtime budget calibration gate unless a later, separately scoped evidence review proves the direct prompt-contract evidence is stronger.

Evidence:

- Attempt 0 writer draft and auditor feedback exist.
- Attempt 0 auditor raised one programmatic C2 issue at `压力测试` and one LLM C1 issue about unavailable compressed bond-risk evidence.
- Repair draft exists at `chapter-06-attempt-01-repair.md`.
- Attempt 1 auditor then timed out twice at about `60s`.
- Runtime diagnostics classify attempt 1 auditor retries as `provider_runtime_category=timeout`.
- `timeout_root_cause_hint=small_prompt_provider_timeout`.

Judgment:

- The direct prompt-contract evidence from attempt 0 is real, but the current terminal blocker after repair is auditor provider timeout.
- Do not touch Ch6 in the next planning gate.
- Do not use Ch6 to justify provider runtime changes in this chapter acceptance gate.

### Chapter 3

Decision: eligible same-source calibration evidence; authorize a narrow Ch3-only planning gate.

Evidence:

- Writer draft exists: `chapters/chapter-03-attempt-00-writer.md`.
- Auditor feedback exists: `chapters/chapter-03-attempt-00-auditor-feedback.md`.
- Repair draft exists: `chapters/chapter-03-attempt-01-repair.md`.
- Second auditor feedback exists: `chapters/chapter-03-attempt-01-auditor-feedback.md`.
- `chapter-03.json` status is `failed`, `stop_reason=repair_budget_exhausted`, `failure_category=prompt_contract`, `failure_subcategory=code_bug_other`.
- Attempt 0 auditor found:
  - Programmatic C2: CHAPTER_CONTRACT `must_not_cover` violation at `言行一致`.
  - LLM C1: declared missing evidence anchor not provided for `实际投资行为（§8）`.
- Attempt 1 auditor found:
  - Programmatic C2: same CHAPTER_CONTRACT `must_not_cover` violation at `言行一致`.
  - No LLM issues.
  - Repair budget exhausted.

Controller analysis:

- The Chapter 3 template explicitly requires `言行一致性判断`, but also prohibits inferring active-fund `风格稳定 / 风格一致 / 言行一致` when turnover or style-change evidence is missing, unavailable or unreviewed.
- The retained Ch3 drafts keep using `言行一致` framing after missing actual investment behavior evidence. Attempt 1 says the strategy direction is consistent while also admitting strict verification is unavailable. That is enough same-source evidence for a writer/repair guidance calibration plan.
- There is also evidence that the current programmatic auditor phrase extraction is coarse: `fund_agent/fund/chapter_auditor.py` extracts literal phrases from the must-not-cover clause, so the phrase `言行一致` can be flagged even when the chapter is trying to satisfy the required output item. This is a possible contract-expression or audit-granularity issue. It does not authorize auditor relaxation in this gate; it must be treated as a planning finding to analyze and either avoid through safer writer/repair wording or route into a separately accepted auditor/contract gate.

## Authorized Next Gate

Authorize only this narrow Slice 2 plan:

`Ch3-only must_not_cover calibration plan`

The plan must be code-generation-ready but must not implement changes. It must analyze the retained Ch3 writer draft, repair draft and auditor feedback to identify why the writer keeps producing forbidden `言行一致` coverage and propose the minimal correction.

Allowed planning scope:

- Analyze only Ch3 retained writer draft, repair draft and auditor feedback from `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431`.
- Identify the root cause of repeated `言行一致` forbidden coverage using same-source evidence.
- Propose minimal writer guidance, repair guidance, or contract clarification.
- Preserve fail-closed behavior.
- Preserve auditor strictness unless the plan records an explicit blocking open question for a separate auditor/contract gate.
- Define targeted tests and smoke validation for Ch3-only behavior.
- Define docs/control update decision separately from implementation.

Explicit non-goals:

- No Ch2 changes.
- No Ch6 changes.
- No broad chapter 2/3/6 calibration.
- No provider timeout tuning or runtime budget changes.
- No auditor relaxation.
- No score-loop.
- No deterministic fallback.
- No stdout half-report.
- No secret-bearing artifact, prompt payload, raw provider response, API key, Authorization header, cookies or passwords.
- No implementation before plan and review are accepted.

## Required Plan Contents

The Ch3-only plan must include:

- Goal and success signal.
- Same-source evidence table with exact retained artifact paths.
- Root-cause hypothesis split:
  - writer prompt/guidance ambiguity,
  - repair guidance insufficiency,
  - contract wording ambiguity,
  - auditor phrase granularity as a possible but not-yet-authorized implementation target.
- Minimal proposed implementation options, with one recommended option.
- Exact allowed files/modules for the future implementation slice.
- Test plan with expected assertions, including a fixture or fake-client Ch3 case where missing §8 evidence must produce safe insufficiency wording instead of positive or quasi-positive `言行一致` coverage.
- Validation commands.
- Residual risks and stop conditions.
- Review handoff criteria.

## Controller Decision

Slice 1 classification is accepted.

Ch2 and Ch6 are deferred to provider runtime budget calibration. Ch3 is authorized for a narrow planning gate only. Implementation remains blocked until the Ch3-only plan and independent review are accepted.
