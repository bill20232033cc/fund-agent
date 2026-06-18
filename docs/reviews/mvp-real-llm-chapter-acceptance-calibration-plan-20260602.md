# MVP Real LLM Chapter Acceptance Calibration Plan

## Self-check

- Phase: `MVP real LLM observability and chapter acceptance phase`.
- Gate: `MVP real LLM chapter acceptance calibration gate`.
- Role: planning specialist, `AgentCodex`.
- Gate classification: `heavy`, because this can affect real LLM chapter acceptance, writer/repair guidance, auditor diagnostics, and fail-closed report generation behavior.
- Work type: plan artifact only.
- Allowed edit for this planning task: this file under `docs/reviews/`.
- Forbidden in this planning task: runtime/source/test/config/design/control/startup edits, real smoke execution, implementation, staging, commit, push, PR, provider budget changes, score-loop entry, quality gate/golden/readiness/final judgment changes.

## Source Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-real-llm-observability-progress-ux-truth-sync-controller-judgment-20260602.md`
- `docs/reviews/mvp-llm-run-progress-timeout-ux-implementation-controller-judgment-20260602.md`
- `docs/reviews/mvp-incomplete-llm-run-artifact-retention-slice1-controller-judgment-20260602.md`
- `docs/fund-analysis-template-draft.md` CHAPTER_CONTRACT and chapter 2 section

## Accepted Current Facts

Artifact retention is accepted at checkpoint `4f7903f`: typed incomplete `fund-analysis analyze --use-llm` results remain fail-closed with stdout empty, non-zero exit, and no deterministic fallback, while writing local ignored artifacts under `reports/llm-runs/`. Retained artifacts include `manifest.json`, `summary.json`, per-chapter JSON, writer draft markdown, repair draft markdown, normalized auditor feedback markdown, prompt-contract diagnostics, runtime scalar diagnostics, chapter matrix, and first failed diagnostic. Serialization is allowlist-first and applies redaction; it must not save prompts, raw provider responses, raw audit responses, provider headers, API keys, Authorization/Bearer/cookies, full config, stack traces, or partial final report markdown.

Progress/timeout UX is accepted at checkpoint `d656816`: `fund-analysis analyze --use-llm` can emit safe stderr-only progress using `--llm-progress/--no-llm-progress` and Host generic `event_sink`. This changes visibility only. It does not change stdout, fail-closed semantics, quality gate behavior, provider runtime timeout/retry/backoff, artifact schema, chapter acceptance policy, auditor strictness, repair budget, score/golden/readiness, or PR state.

The next gate is chapter acceptance calibration planning. Earlier real smoke for `006597 / 2024 --use-llm` failed closed with stdout empty, exit `1`, partial orchestration and incomplete final assembly. Historical matrix evidence included chapters `1 accepted`, `2 failed`, `3 failed`, `4 accepted`, `5 accepted`, `6 failed`, with chapter 2 `l1_numerical_closure` as the first priority. Later compact-mode same-source diagnostics also recorded provider runtime writer timeouts for chapters 1-6; provider runtime budget calibration remains a separate future gate. This plan therefore requires current retained artifacts plus a fresh real smoke rerun before implementation root-cause classification.

## Gate Scope

This gate calibrates real LLM body-chapter acceptance using evidence from retained artifacts and a fresh real smoke rerun. The priority is template chapter 2, specifically `l1_numerical_closure`. Chapters 3 and 6 are included only for evidence triage and regression once the chapter 2 path is proven, unless retained artifacts prove the same root cause.

The implementation objective, after this plan is reviewed and accepted, is to make the smallest evidence-supported change that improves real LLM chapter acceptance while keeping fail-closed behavior intact. Valid change types are limited to writer prompt contract/guidance, repair guidance, safe diagnostic clarity, or a narrowly proven programmatic audit code bug.

## Non-goals

- Do not relax auditor rules.
- Do not increase repair budget as the default solution.
- Do not let incomplete results fall back to deterministic reports.
- Do not output partial or half-finished reports.
- Do not change provider timeout/retry/backoff budget or provider config defaults.
- Do not add provider fallback, model fallback, multi-provider routing, or multi-model writer/auditor split.
- Do not connect `chapter_generation_score` to existing score/golden/readiness/quality gate.
- Do not modify quality gate, golden fixtures, golden answers, manifests, snapshot promotion, readiness, final judgment, or release/PR external state.
- Do not modify `docs/fund-analysis-template-draft.md`, `docs/design.md`, `docs/implementation-control.md`, or `docs/current-startup-packet.md` during implementation unless a later controller truth-sync gate explicitly authorizes it.
- Do not introduce `dayu-agent`, `dayu.host`, or `dayu.engine` as production runtime dependencies.
- Do not migrate Agent runner/tool-loop, async Host runner, durable session/resume/memory/outbox, or Host business semantics.

## Evidence Protocol

### Retained artifact inspection

Implementation must start by locating the latest relevant local ignored run directory under `reports/llm-runs/` for `fund_code=006597`, `report_year=2024`, and `trigger=use_llm_incomplete`. The evidence artifact for implementation must record the run directory path, timestamp, full `host_run_id` from `manifest.json`, schema versions, `retention_policy`, and whether `redaction_applied` is true.

For each inspected run, read only these retained files and fields:

- `manifest.json`: schema version, trigger, fund identity, run id, chapter count, chapter files, artifact file list, redaction summary.
- `summary.json`: `orchestration_status`, `final_assembly_status`, `first_failed`, and `chapter_matrix`.
- `chapters/chapter-02.json`: status, stop reason, failure category/subcategory, accepted draft presence, attempts, writer/audit stop reasons, programmatic issues, LLM issues, prompt-contract diagnostics, runtime diagnostics, repair decisions, used fact ids, used anchor ids, declared missing reasons, deleted item rules.
- `chapter-02-attempt-*-writer.md` and `chapter-02-attempt-*-repair.md`: chapter 2 markdown drafts only, after confirming they are saved retained artifacts and not raw provider payloads.
- `chapter-02-attempt-*-auditor-feedback.md`: normalized auditor feedback only.
- Chapter 3 and chapter 6 JSON/draft/feedback files only after chapter 2 has been triaged, or earlier if chapter matrix shows chapter 2 is blocked by provider runtime and chapter 3/6 are the first non-runtime audit failures.

Artifact inspection must classify each failed chapter by direct fields from the same run: `status`, `stop_reason`, `failure_category`, `failure_subcategory`, `audit_repair_hint`, `programmatic_issues`, `llm_issues`, prompt-contract diagnostic counters, and runtime diagnostic scalars. The implementation evidence must not infer a root cause from old logs if the retained artifact fields contradict it.

### Fresh real LLM smoke rerun

Before any code change, rerun a real LLM smoke for `006597 / 2024 --use-llm` with the currently accepted CLI path and configured provider credentials. The exact command must be recorded by the implementation agent, with secrets redacted. Use `--llm-progress` only if stderr progress evidence is useful; progress lines remain stderr-only and are not acceptance evidence by themselves.

The smoke evidence must record:

- command shape with secret-bearing environment omitted or redacted;
- wall-clock start/end time and date;
- exit code;
- whether stdout is empty;
- whether stderr contains only safe diagnostics/progress;
- whether deterministic fallback occurred, expected `false`;
- `orchestration_status`;
- `final_assembly_status`;
- generated, skipped, accepted and failed chapter ids;
- chapter matrix with chapter id, status, stop reason, failure category and failure subcategory;
- first failed diagnostic;
- artifact directory path and manifest path;
- whether final report markdown is present, expected `false` unless all body chapters accepted and final assembly completes;
- if provider runtime timeout is the first blocker, the runtime operation, attempts/max attempts, timeout root-cause hint, approx prompt tokens, prompt chars and max output chars from safe diagnostics.

Expected smoke outcomes are evidence-driven:

- If exit `1`, stdout empty, no deterministic fallback and artifact path is present, the run remains valid calibration evidence.
- If the first blocker is provider runtime timeout across chapters, do not implement prompt/auditor calibration in this gate; record provider runtime blocker and hand off to the future provider runtime budget calibration gate.
- If chapter 2 fails with `failure_category=prompt_contract` and `failure_subcategory=l1_numerical_closure`, continue to same-source L1 triage.
- If chapter 2 accepts but chapter 3 or 6 fails, treat chapter 2 calibration as already unblocked for this run and triage chapter 3/6 only within the candidate scope below.

### Secret redaction and safe evidence

Evidence artifacts may include retained writer/repair drafts because the accepted artifact retention gate explicitly saves redacted drafts for local diagnosis. They must not include prompts, raw provider responses, raw auditor responses, API keys, Authorization/Bearer/cookies, request headers, full provider config, model names if omitted by safe serializers, stack traces, or unredacted secret-looking substrings.

When quoting retained draft or feedback text in review artifacts, quote only the minimal lines needed to prove the root cause. Prefer paraphrase plus file path and field references. Do not paste entire drafts.

## Root-cause Taxonomy

Every failed chapter must be assigned exactly one primary root-cause class, plus optional secondary observations. A class can be assigned only from same-source evidence in the retained artifacts and rerun smoke.

| Class | Direct evidence required | Valid next action |
|---|---|---|
| `prompt_contract_problem` | Writer/repair draft violates an existing contract despite adequate facts, anchors and repair feedback; examples include missing required output markers, wrong anchor/missing marker syntax, numerical closure sentence without nearby anchor marker, or must_not_cover violation. | Change writer prompt/guidance or chapter-specific instruction only. |
| `repair_guidance_gap` | Initial writer draft fails with a specific issue, auditor feedback/repair decision identifies it, but repair draft repeats the same issue because `ChapterRepairContext` or repair prompt lacks actionable correction. | Change repair context rendering or repair guidance only. |
| `diagnostic_clarity_gap` | Actual failure is visible in draft/feedback, but safe diagnostic fields classify it too broadly or hide the actionable subcategory; root behavior is otherwise correct. | Change safe diagnostic mapping/serialization only. |
| `programmatic_audit_code_bug` | Audit code flags a valid draft or misses an invalid draft when checked against the same draft, same `ChapterAuditInput`, same allowed anchors, same structured facts, and CHAPTER_CONTRACT. | Fix the narrow audit code bug and add direct unit coverage. |
| `fact_evidence_gap` | Writer cannot satisfy the chapter contract because `ChapterFactProjection` lacks required values or anchors, and draft/feedback correctly show unavailable facts or `needs_more_facts`. | Do not patch writer wording as the primary fix; hand off to fact projection/evidence extraction gate unless a clearer safe diagnostic is needed. |
| `provider_runtime_blocker` | Provider runtime diagnostics show timeout/rate-limit/network/malformed response before a usable draft/audit is available, especially with small prompt costs under current bounded budget. | Stop calibration implementation for this gate; hand off to provider runtime budget/reliability gate. |

### Chapter 2 `l1_numerical_closure` same-source rule

Chapter 2 L1 calibration may proceed only if all of the following are true in the same retained run or rerun artifact:

- `chapter_id=2`;
- `failure_category=prompt_contract`;
- `failure_subcategory=l1_numerical_closure`;
- prompt-contract diagnostic phase is `programmatic_audit` or auditor feedback contains a programmatic L1 issue;
- retained draft or repair draft contains an `R=A+B-C`, `A=R-B`, or `A-C` numerical assertion;
- the same local line or near context lacks the accepted anchor marker required by `_audit_numerical_closure()`;
- the relevant fact/anchor ids for R, B, A or cost are available or the draft should have declared a data gap instead of asserting the number;
- the failure is not preceded by provider runtime timeout, missing draft, missing facts, invalid required markers, forbidden phrase, candidate facet assertion, or a higher-priority code path.

Indirect evidence is not sufficient. Do not conclude "L1 is too strict" merely from a failed chapter matrix. Do not conclude "writer forgot anchors" unless the retained draft lines and auditor issue prove it.

## Candidate Implementation Slices

### Slice 1: evidence triage and same-source diagnostic

Goal: produce an implementation evidence artifact that reconstructs current failure from retained artifacts and a fresh real smoke rerun, without changing runtime behavior.

Actions:

- Inspect current `reports/llm-runs/` retained artifacts for `006597 / 2024`.
- Rerun real LLM smoke once under current provider configuration, subject to controller/user availability of credentials/network/cost.
- Record safe evidence under `docs/reviews/` in a new implementation evidence artifact.
- Classify chapter 2, 3 and 6 failures using the taxonomy above.
- Decide whether Slice 2 is authorized. If first blocker is provider runtime, stop here and recommend provider runtime budget calibration gate.

Allowed files:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-evidence-20260602.md`
- Local ignored `reports/llm-runs/` generated by the real smoke

Forbidden files:

- All source, tests, config, design/control/startup docs, templates, schema, score/golden/readiness files

Validation:

- No unit test required because no code changes.
- Evidence must include `git status --short` scope check.
- Evidence must prove no source/test/config/design/control/startup edits occurred.

Exit criteria:

- Root-cause taxonomy table completed for chapter 2, and triage entries for chapters 3 and 6.
- Controller can decide whether implementation should continue to Slice 2 or defer to provider runtime/evidence projection gate.

### Slice 2: chapter 2 calibration implementation

Slice 2 is allowed only if Slice 1 proves chapter 2 `l1_numerical_closure` is the current actionable blocker and not a provider runtime blocker or fact/evidence gap.

Allowed change types, in priority order:

1. Writer prompt/guidance: make chapter 2 numerical closure instructions explicitly require nearby anchor markers for every R/B/A/Cost equation and require data-gap wording when inputs are unavailable.
2. Repair guidance: make `l1_numerical_closure` repair context tell the writer to patch the specific equation lines by adding allowed anchor markers or removing unsupported numbers.
3. Diagnostic clarity: if drafts/feedback are actionable but safe diagnostics are too broad, improve subcategory or phase counters while preserving redaction and allowlists.
4. Programmatic audit code bug fix: only if same-source evidence proves `_audit_numerical_closure()` rejects valid anchored output or accepts invalid output.

Likely allowed source files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/services/llm_run_artifacts.py`, only for diagnostic clarity and only if no schema-breaking change is needed
- `fund_agent/ui/cli.py`, only if safe CLI diagnostic display is proven ambiguous and no artifact schema change is required

Likely allowed tests:

- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_llm_run_artifacts.py`, only for diagnostic serialization/artifact evidence fields
- `tests/ui/test_cli.py`, only for safe first-failed/chapter-matrix diagnostic display

Forbidden files unless a controller explicitly opens a new gate:

- `fund_agent/config/llm.py`
- `fund_agent/services/llm_provider.py` provider budget/retry/backoff semantics
- `fund_agent/services/execution_contract.py`
- provider config/readiness/golden/score/snapshot/quality gate/final judgment modules
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/fund-analysis-template-draft.md`
- any `fund_agent/host` or future `fund_agent/agent` migration files
- any `dayu-agent`, `dayu.host`, or `dayu.engine` production runtime dependency

Required tests:

- Unit test proving chapter 2 writer guidance includes the L1 anchor-near-equation requirement and does not include prompts/raw provider payloads in diagnostics.
- Unit test proving repair context for `l1_numerical_closure` gives actionable correction and preserves typed explicit parameters.
- Auditor test for a chapter 2 draft with numerical closure plus nearby allowed anchor marker passing L1, and a draft without nearby anchor marker failing L1.
- Orchestrator diagnostic test proving `failure_category=prompt_contract`, `failure_subcategory=l1_numerical_closure`, and `l1_numerical_closure_count` remain safe and precise.
- Artifact/CLI regression only if those files change.

Validation:

- Targeted pytest for changed files.
- `uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q`, adjusted if changed files require more tests.
- `uv run pytest tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q` if artifact or CLI diagnostics change.
- `uv run ruff check .`.
- Fresh real LLM smoke rerun after the code change, recorded in implementation evidence, with expected result below.

Expected real smoke criteria:

- Always acceptable: fail-closed behavior remains intact, stdout empty on incomplete, no deterministic fallback, artifact retained.
- Success signal: chapter 2 no longer fails with `prompt_contract/l1_numerical_closure`.
- Strong success signal: chapter 2 is accepted, or if it fails, the new first failed diagnostic is a different, more precise, evidence-supported category.
- Not acceptable: chapter 2 passes only because L1 is disabled/relaxed globally, repair budget increased, incomplete report emitted, deterministic fallback used, or unsafe diagnostics leak secrets.

### Slice 3: chapters 3 and 6 regression and narrow calibration

Slice 3 starts only after Slice 2 proves the chapter 2 path or Slice 1 proves chapters 3/6 share the same root cause. It must not become a broad prompt rewrite for all body chapters.

Allowed actions:

- If chapters 3/6 share `l1_numerical_closure`, apply the same narrow guidance/diagnostic pattern and add chapter-specific tests only where needed.
- If chapter 3 or 6 shows a different prompt-contract issue, write a separate mini-triage section and implement only a same-source narrow fix.
- If chapter 3 or 6 shows fact/evidence gap or provider runtime blocker, do not patch prompt wording; record residual owner.

Likely allowed files and tests are the same as Slice 2, but changes must be limited to the proven root cause.

Validation:

- Targeted tests for the changed root cause.
- CLI/Service fail-closed regressions if orchestration/diagnostics changed.
- Real LLM smoke rerun with chapter matrix comparison against the pre-change smoke.

Exit criteria:

- Chapter 2 remains not blocked by `l1_numerical_closure`.
- Chapters 3/6 either improve for the same proven cause or are explicitly assigned to residual owners.
- No quality gate/golden/readiness/score/provider budget semantics changed.

## Allowed and Forbidden File Matrix

| Slice | Allowed | Forbidden |
|---|---|---|
| Slice 1 | `docs/reviews/*evidence*.md`; ignored `reports/llm-runs/` from manual smoke | Source, tests, config, design/control/startup, templates, git operations |
| Slice 2 | `fund_agent/fund/chapter_writer.py`; `fund_agent/fund/chapter_auditor.py`; `fund_agent/services/chapter_orchestrator.py`; narrowly `fund_agent/services/llm_run_artifacts.py`; narrowly `fund_agent/ui/cli.py`; matching tests | Provider budget/config, provider retry/backoff, artifact schema unless controller approves, score/golden/readiness/quality gate/final judgment, design/control/startup/template docs, Host/Agent/dayu runtime |
| Slice 3 | Same as Slice 2 but only for proven chapter 3/6 root cause | Broad all-chapter rewrite, provider runtime changes, score/golden/readiness, template mutation, Host/Agent migration |

## Test and Validation Matrix

| Area | Required validation | Notes |
|---|---|---|
| Writer guidance | Targeted unit tests in `tests/fund/test_chapter_writer.py` | Verify chapter 2 L1 anchor-near-equation guidance and repair prompt requirements. |
| Auditor L1 | Targeted unit tests in `tests/fund/test_chapter_auditor.py` | Verify L1 pass/fail with same draft and same allowed anchors; do not weaken L1. |
| Orchestrator diagnostics | `tests/services/test_chapter_orchestrator.py` | Verify failure category/subcategory and counters stay precise and safe. |
| Artifact diagnostics | `tests/services/test_llm_run_artifacts.py` if changed | Verify retained fields remain allowlisted/redacted and existing schema expectations still pass. |
| CLI diagnostics | `tests/ui/test_cli.py` if changed | Verify stderr only, stdout empty on fail-closed, no secret/prompt/draft leak in CLI diagnostics. |
| Service fail-closed | `tests/services/test_fund_analysis_service_llm.py` if orchestration/final assembly behavior changes | Incomplete LLM result must not fallback deterministic. |
| Lint | `uv run ruff check .` | Required before review. |
| Manual real smoke | `006597 / 2024 --use-llm` before and after implementation | Record exit code, stdout empty, no fallback, statuses, matrix, first failed diagnostic, artifact path. |

## Review and Acceptance Criteria

Plan acceptance requires two independent plan reviews before implementation. Preferred reviewers are any two of `AgentMiMo`, `AgentDS`, and `AgentGLM`. Controller judgment must explicitly adjudicate each review finding as accepted, rejected, deferred, or needs-more-evidence.

Implementation acceptance requires:

- Slice 1 evidence artifact with retained artifact inspection and fresh smoke evidence, or a controller-recorded reason why fresh smoke could not run.
- If Slice 2/3 proceeds, implementation evidence mapping each change to same-source root cause.
- Required unit/CLI/Service tests passing.
- `uv run ruff check .` passing.
- Fresh real LLM smoke rerun after implementation, unless provider credentials/network are unavailable and controller accepts that residual.
- Code review by at least two independent reviewers, or explicit controller risk acceptance if one reviewer is unavailable.
- Re-review after fixes if any blocking finding is accepted.
- Controller implementation judgment and local accepted checkpoint before any truth sync.

Acceptance criteria for the gate:

- No implementation starts before reviewed and accepted plan.
- Root cause for chapter 2 is proven from retained artifacts and rerun smoke, not inferred indirectly.
- If implemented, chapter 2 `l1_numerical_closure` is no longer the first blocker without weakening L1 or fail-closed behavior.
- Chapters 3 and 6 are either triaged with same-source evidence or assigned residual owners.
- Incomplete `--use-llm` still exits non-zero with stdout empty, no deterministic fallback, no partial report, and retained artifacts.
- Safe diagnostics still exclude prompts, raw provider/auditor responses, secrets, headers, full config, stack traces and model names where current safe serializers omit them.
- Provider budget/config, score/golden/readiness/quality gate/final judgment, Host/Agent/dayu runtime, and template/control/design/startup docs remain unchanged unless a later controller gate explicitly authorizes them.

## Residual Owners

| Residual | Owner / next gate |
|---|---|
| Provider runtime timeout or small-prompt endpoint blocker | Future `MVP provider runtime budget calibration gate` |
| Progress/timeout UX polish beyond accepted stderr progress | Already accepted; future provider observability gate only if new evidence warrants it |
| Artifact lifecycle, cleanup, upload, or timeline schema | Future observability/control policy gate |
| Artifact schema change for richer evidence | Future artifact schema gate with controller approval |
| `chapter_generation_score` / score-loop implementation | Future score-loop implementation gate after provider/runtime and acceptance blockers are handled |
| Chapters not fixed in this gate | Future chapter-specific calibration gate with retained same-source evidence |
| Fact/evidence projection gaps | Future fact projection/evidence extraction gate |
| Programmatic audit C2 issues not related to chapter 2 L1 | Future `MVP programmatic audit C2 calibration gate` |

## Handoff Summary for Implementation Agent

Start with Slice 1. Do not change code until retained artifacts and a fresh smoke rerun prove the current first actionable blocker. If provider runtime timeout is first, stop and write evidence. If chapter 2 `prompt_contract/l1_numerical_closure` is proven from same-source draft and auditor feedback, implement the smallest chapter 2 guidance/repair/diagnostic/code fix that addresses that evidence. Keep fail-closed behavior, auditor strictness, repair budget, provider budget, score/golden/readiness and Host/Agent boundaries unchanged.
