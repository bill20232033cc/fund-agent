# MVP internalized Agent engine and typed audit contract design gate

## Worker self-check at start

- Current gate / role: Gateflow-governed design worker for `MVP internalized Agent engine and typed audit contract design gate`; not controller.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/fund-analysis-template-draft.md`, retained 006597 run artifacts, and the Slice 1 controller judgment after provider restore.
- Scope boundary: docs/reviews design artifact only. No code, runtime config, provider budget, prompt, score-loop, fail-closed semantic, `docs/design.md`, control/startup, commit, push or PR changes.
- Stop conditions: if this artifact needs to assert current implementation facts beyond accepted truth docs, stop; this document instead records a proposed design for review.
- Evidence and validation: output is this design artifact plus JSON parsing / text self-check / diff whitespace validation.

## Status

This artifact is proposed design for review. It is not current implementation fact and must not be copied into `docs/design.md`, `docs/implementation-control.md`, README files, startup packet, or code as accepted truth until a later controller gate accepts it.

## Goal

Define the next architecture boundary for an MVP internalized Agent engine and typed audit contract so chapter write-audit-repair execution stops leaking engine responsibilities into Service while preserving the current fail-closed `--use-llm` behavior.

The design answers six gate questions:

- Service should keep use case, `ExecutionContract`, quality policy and report strategy only.
- Agent should own runner, tool-loop, bounded retry/repair loop, execution budget accounting and `ToolTrace`.
- Fund should own fund-domain facts, CHAPTER_CONTRACT / preferred_lens / ITEM_RULE interpretation, and programmatic-first audit rules.
- LLM auditor should become a bounded semantic audit tool, not an unbounded authority over contract semantics.
- Ch2/Ch6 timeout and Ch3 `must_not_cover` show different architecture problems.
- Dayu Engine capabilities should be internalized in this repo without production dependency on `dayu-agent` or `dayu.engine`.

## Evidence

- `docs/design.md` defines the target boundary as `UI -> Service -> Host -> Agent`; current `--use-llm` is `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`; Agent runner/tool-loop is not implemented.
- `docs/design.md` records that current Host only governs run lifecycle, deadline/cancel, terminal state, phase events and safe diagnostics. Durable Host features and Agent runner/tool-loop remain future gates.
- `docs/design.md` states Dayu is architecture reference and capability source, not production runtime dependency; direct `dayu-agent`, `dayu.host` and `dayu.engine` production dependency is forbidden.
- `docs/design.md` records current programmatic audit as `P1/P2/P3/C2/L1/R1/R2`; `E1/E2/E3/C1/L2` are later LLM audit / Evidence Confirm / semantic review targets and must not be described as already passed.
- `docs/fund-analysis-template-draft.md` makes Ch2 answer R/B/A/C, structural vs phase alpha, and cost coverage with every number traceable to source and formula.
- `docs/fund-analysis-template-draft.md` makes Ch3 answer manager identity, stated strategy, actual behavior, consistency, style stability and manager holding; it forbids inferring active-fund style stability, style consistency or word-action consistency when turnover or style-change evidence is missing, unavailable or unreviewed.
- `docs/fund-analysis-template-draft.md` makes Ch6 answer decisive risk, veto vs tracking, pressure-test conclusion and next minimum validation question; it forbids final hold/replace conclusions, market prediction, probability prediction and unordered risk laundry lists.
- Retained run `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json` is `orchestration_status=partial`, `final_assembly_status=incomplete`, `stdout` remained empty per controller judgment, and first failed chapter is Ch2 with `stop_reason=llm_timeout`.
- Ch2 artifact shows writer drafted successfully, then auditor timed out twice at about 60 seconds with `provider_runtime_category=timeout`, `timeout_budget_kind=auditor`, `timeout_root_cause_hint=small_prompt_provider_timeout`, and approx prompt tokens 743.
- Ch3 artifact shows `status=failed`, `stop_reason=repair_budget_exhausted`, `failure_category=prompt_contract`, `failure_subcategory=code_bug_other`; both attempts hit programmatic C2 around `言行一致`.
- Ch6 artifact shows attempt 0 had C2 / LLM semantic issues, then repair attempt auditor timed out twice at about 60 seconds with `timeout_root_cause_hint=small_prompt_provider_timeout` and approx prompt tokens 731.
- Controller judgment after provider restore classifies Ch2 and Ch6 as deferred to provider runtime budget calibration, while Ch3 is eligible for a narrow Ch3-only planning gate; it explicitly forbids provider budget changes, auditor relaxation and Ch2/Ch6 changes in that gate.

## First-principles diagnosis

The root problem is not one failure class. It is a boundary mismatch between business orchestration, execution mechanics, deterministic audit contracts and semantic audit.

Service currently has legitimate ownership of the business use case: what user requested, what report mode is allowed, what quality policy applies, which report strategy is selected, and what `ExecutionContract` is passed into the run. Those are product semantics.

Service should not become the owner of execution mechanics. Chapter attempt state, write-audit-repair iteration, retry classification, tool invocation records, per-attempt budget accounting and replayable traces are engine semantics. If these stay in Service, every future fix for timeout, repair, semantic audit, typed patch, context budget or tool replay will keep crossing product and execution boundaries.

Fund should not become a generic Agent runtime either. Fund owns domain truth: fund type, document-derived facts, preferred lens, CHAPTER_CONTRACT, ITEM_RULE, audit rules, evidence anchors, missing-fact semantics and final judgment constraints. It can expose typed tools and typed audit results, but should not own generic run lifecycle or cross-tool scheduling.

The LLM auditor is useful only where deterministic rules cannot decide semantic support or wording safety. It should not decide whether a required chapter item exists, whether a forbidden contract clause was crossed, whether R=A+B-C numerically closes, whether a pressure-test threshold matches fund type, or whether final judgment contradicts quality policy. Those must be programmatic-first because they are contract, schema or arithmetic questions.

## Proposed architecture boundary

This is the proposed boundary for the review gate, not current implementation fact.

| Layer | Proposed ownership | Explicit non-ownership |
|---|---|---|
| UI | User opt-in, CLI flags, display, stdout/stderr behavior | No Agent internals, no audit semantics, no provider/runtime policy |
| Service | Use case, scene/report strategy, `ExecutionContract`, typed request, quality policy, report assembly policy, fail-closed product semantics | No runner/tool-loop, no per-tool retry engine, no `ToolTrace`, no context budget accounting, no Fund audit implementation |
| Host | Run lifecycle, global deadline, cancellation, terminal state, safe run diagnostics, phase/event delivery | No fund knowledge, no prompt semantics, no tool loop, no provider clients |
| Agent | Runner, chapter task loop, tool-loop, typed retry/repair state machine, tool execution contract, context/budget accounting, `ToolTrace`, accepted chapter state | No UI rendering, no Service use-case choice, no Host lifecycle governance |
| Fund | Fund facts/tools, CHAPTER_CONTRACT / preferred_lens / ITEM_RULE, programmatic audit, evidence anchor rules, bounded semantic audit tool adapter | No generic runner, no Host lifecycle, no Service report policy |

Service should keep only:

- the use case (`analyze --use-llm` as explicit opt-in);
- the business `ExecutionContract`;
- quality/fail-closed/report assembly policy;
- selection of chapter/report strategy;
- safe final result mapping for UI.

Agent should own:

- chapter runner and task graph;
- write-audit-repair loop as a typed state machine;
- retry and repair budgets inside Service-declared ceilings;
- context budget and prompt/tool input budgeting;
- typed `ToolTrace` for writer, programmatic audit, semantic LLM audit, repair and final assembly steps;
- accepted chapter state and replayable failure summaries.

Provider timeout numbers and endpoint calibration remain outside this design gate. This design may define where budget accounting belongs, but must not change budget values or provider runtime policy.

### MVP boundary handoff

For the first Agent-engine MVP, provider construction remains Service-owned unless a later provider-factory migration gate explicitly changes it. This keeps the current accepted `FundLLMExecutionRequest` boundary intact while moving execution mechanics out of Service.

| Concern | MVP owner | Proposed handoff |
|---|---|---|
| Business request, report mode and quality policy | Service | Service builds `FundLLMExecutionContract` and declares fail-closed/report policy. |
| Provider config parsing and HTTP client construction | Service | Service constructs or injects writer/auditor Protocol clients; Agent receives typed tool clients, not env/config. |
| Runtime ceilings | Service | Service declares ceilings such as target chapters, max repair attempts, timeout/max-attempt values and max output chars; Agent may spend and trace within those ceilings but cannot silently raise them. |
| Chapter task execution | Agent | Agent receives chapter projection, tool clients and ceilings, then runs writer -> programmatic audit -> bounded semantic audit -> repair loop. |
| Fund domain tools | Fund | Fund exposes typed writer, programmatic audit and semantic audit tool adapters over existing Fund primitives. |
| Safe diagnostics | Agent + Service | Agent records `ToolTrace`; Service serializes final incomplete-run artifact using allowlist policy and existing fail-closed UI semantics. |

Minimal Agent runner input shape:

- `run_id`, `fund_code`, `report_year`.
- `ChapterFactProjection` or already validated equivalent.
- Service-declared `ChapterExecutionCeilings`: target chapter ids, max repair attempts, writer/auditor/repair timeout ceilings, provider max attempts, max output chars, safe diagnostic policy id.
- Injected typed tools: writer, programmatic auditor, bounded semantic auditor and optional repair planner.

Minimal Agent runner output shape:

- `accepted_chapters`: accepted draft/conclusion references and source attempt ids.
- `chapter_results`: status, stop reason, issue ids, repair decisions and runtime failure summaries.
- `audit_results`: typed programmatic and semantic audit results.
- `tool_trace`: redacted per-tool trace entries.
- `final_assembly_readiness`: complete / incomplete with missing accepted chapter ids.

## Typed audit contract design

The next design should split audit into typed contracts instead of treating all audit failures as generic prompt-contract or LLM feedback strings.

Proposed core types:

- `AuditSubject`: chapter id, fund code, report year, fund type, accepted fact ids, evidence anchor ids, draft version and attempt index.
- `AuditRuleId`: stable rule identifier, for example `P1`, `P2`, `P3`, `C2`, `L1`, `R1`, `R2`, `ITEM_RULE`, `E1_ANCHOR_FORMAT`, `SEMANTIC_C1`.
- `AuditLayer`: `programmatic`, `semantic_llm`, `evidence_confirm`.
- `AuditIssue`: rule id, layer, severity, location, message, related fact ids, related anchor ids, source contract clause, repair hint and determinism flag.
- `AuditDecision`: accepted / rejected / repairable / blocked, with reason and next action.
- `RepairPlan`: `patch`, `regenerate`, `stop`, or `defer_to_gate`, always tied to specific issue ids.
- `ToolTrace`: one trace entry per writer/auditor/repair/fact tool call with redacted inputs metadata, safe output metadata, duration, retry index, budget counters, result status and failure category.

### MVP typed schema and current-type mapping

The first implementation plan should not invent a fully new audit universe. It should wrap the current accepted types and make their relationships explicit.

MVP schema boundary:

- `schema_version`: `agent_audit_contract.v1`.
- `AuditLayer`: `programmatic`, `semantic_llm`, `evidence_confirm_deferred`.
- `AuditStatus`: `pass`, `fail`, `blocked`.
- `AuditDecisionAction`: `accept`, `repair`, `stop`, `needs_more_facts`, `defer_to_gate`.
- `AuditIssueSeverity`: `blocking`, `reviewable`, `informational`.
- `RuntimeFailureKind`: `timeout`, `rate_limit`, `malformed_response`, `network`, `http_error`, `unavailable`.

Current-type mapping:

| Current type | MVP audit contract mapping |
|---|---|
| `ChapterAuditIssue` | `AuditIssue` with existing `issue_id`, `rule_code`, `severity`, `location`, `fact_ids`, `anchor_ids`, `item_rule_ids`, `repair_hint`. |
| `ChapterProgrammaticAuditResult` | `AuditPass(programmatic)` or `AuditFailure(programmatic)` with deterministic issue ids. |
| `ChapterLLMAuditResult` | `AuditPass(semantic_llm)`, `AuditFailure(semantic_llm)` or `RuntimeFailure(semantic_llm)`; raw response must not enter trace/artifact serialization. |
| `ChapterAuditResult.accepted` | `AuditDecision(action=accept)` only when both programmatic and semantic audit pass. |
| `ChapterRepairAction` | `AuditDecisionAction` mapping: `regenerate -> repair`, `needs_more_facts -> needs_more_facts`, `stop -> stop`, `none -> accept/stop by status`. |
| `ChapterRunStopReason` | Agent chapter result stop reason; runtime reasons remain runtime failures, not audit content issues. |
| `ChapterFailureCategory` / `ChapterFailureSubcategory` | Safe summary classifications derived from typed issue/runtime records, not independent truth. |

MVP programmatic-first scope is intentionally narrower than the full list below:

- required output markers and fixed chapter structure;
- allowed anchor/missing marker semantics;
- must-not-cover issue identity and clause source;
- missing-fact downgrade issue identity for Ch3-style unsafe positive inference;
- L1 numerical-closure issue identity where already implemented;
- timeout/runtime failure typed separately from content failure.

Evidence Confirm, final-judgment consistency expansion, full Ch6 threshold semantics and broader domain rule expansion remain later gates unless an implementation plan explicitly scopes and reviews them.

Typed invariants:

- Programmatic audit runs before LLM semantic audit.
- Semantic LLM audit cannot mark a programmatic blocker as accepted.
- Evidence Confirm can upgrade semantic uncertainty into confirmed evidence mismatch, but cannot invent missing source data.
- Every issue must declare whether it is deterministic. Deterministic blockers should be fixable without provider calls.
- Repair budget exhaustion must cite issue ids and attempt ids, not only chapter-level text.
- A timeout is a tool runtime failure, not proof that a chapter contract is wrong.
- A contract violation is a content/state failure, not proof that provider timeout budget should change.

## Programmatic-first audit list

These audit categories should be programmatic-first in Fund before any bounded LLM semantic audit is allowed to influence acceptance.

- Chapter structure: P1 / P2 / P3, including required sections where applicable and chapter presence.
- CHAPTER_CONTRACT forbidden and required clauses: C2 and required output item checks, including `must_answer`, `must_not_cover` and required marker coverage.
- ITEM_RULE compliance: rendered segment presence, identity/context conditions and item-specific evidence requirements.
- Evidence anchor syntax and declared-anchor consistency: anchor format, allowed anchor ids, missing markers, unknown anchor ids and cited source field presence. This is programmatic-first even if deeper E2 source/claim matching remains Evidence Confirm.
- Numeric closure: Ch2 R/B/A, excess return, cost decomposition, fee arithmetic and any derived ratio used in the draft. L1 remains deterministic.
- Fund-type lens selection: identify index / active / bond / enhanced index / QDII / FOF before applying preferred lens and thresholds.
- Missing-fact downgrade: if required reviewed facts are missing, unavailable, not applicable or unreviewed, output must express insufficiency rather than positive conclusions.
- Ch3 active-fund consistency guard: no positive or quasi-positive style stability, style consistency or word-action consistency without reviewed turnover or style-change evidence.
- Ch6 pressure-test and risk contract: fund-type thresholds, veto vs tracking distinction, single decisive risk, no final hold/replace conclusion, no market/probability prediction.
- Final judgment consistency: R1/R2, final judgment only from accepted chapter conclusions and quality context, no direct buy/sell advice.

LLM semantic audit may review evidence-support reasoning, wording safety, reader comprehensibility and possible hallucination, but only after the deterministic contract is already represented as typed issues.

## Bounded LLM semantic audit design

The LLM auditor should be downgraded to a bounded semantic audit tool.

Bounded means:

- It receives only `AuditSubject`, structured facts, evidence anchor summaries, declared data gaps, draft text and explicit semantic questions.
- It does not receive API keys, provider config, raw provider responses, hidden prompts, filesystem paths with secrets, PDF/cache/source helper access, or unbounded document text.
- It emits only typed `AuditIssue` rows with rule code, severity, location, short message, referenced fact/anchor ids and repair hint.
- It cannot relax programmatic rules, delete deterministic blockers or change final fail-closed behavior.
- It has explicit timeout, max attempts, max output and redaction policy recorded in `ToolTrace`.
- Its failure mode is typed: unavailable/timeout/malformed output/semantic blocker. Timeout is not silently converted into content failure.

This makes the auditor useful for `C1` semantic hallucination, evidence-support concerns and unsafe investment wording, while keeping CHAPTER_CONTRACT, ITEM_RULE, arithmetic and chapter acceptance state deterministic.

## Ch2 / Ch6 timeout vs Ch3 must_not_cover

Ch2 and Ch6 show runtime observability and engine-boundary problems, not immediate audit-contract changes.

- Ch2 writer succeeded and auditor timed out twice on small auditor prompts. The artifact points to `small_prompt_provider_timeout`, not large prompt cost, prompt contract failure or missing config.
- Ch6 has mixed evidence: the first audit found C2 / semantic issues, but the terminal blocker after repair was again auditor provider timeout. That means Ch6 cannot be used as clean evidence for prompt or audit relaxation in this gate.
- Both chapters need provider runtime budget calibration or provider endpoint strategy in a separate gate. This design should not tune timeout values.

Ch3 shows a deterministic contract expression and repair-loop boundary problem.

- The terminal failure is `repair_budget_exhausted`, with repeated programmatic C2 around `言行一致`.
- The draft attempts continued to approach a forbidden inference boundary after missing or unreviewed actual behavior evidence.
- This is not solved by increasing provider timeout. It requires typed representation of the contract clause, missing-evidence state, forbidden inference, repair target and deterministic acceptance criteria.
- It also exposes that a literal forbidden phrase can collide with a required output item named `言行一致性判断`. The next Ch3-only planning gate must decide whether the safest fix is writer/repair wording, contract expression, or a separately reviewed auditor granularity change. This artifact does not authorize auditor relaxation.

## Dayu Engine capabilities to internalize

The following Dayu Engine-style capabilities should be internalized in this repo when the Agent gate is accepted:

- Runner: deterministic state machine for one Agent run and chapter tasks.
- Tool loop: typed calls to writer, programmatic audit, semantic audit, repair, fact/facet tools and assembly helpers.
- ToolRegistry: explicit typed registry of allowed tools, inputs, outputs and failure categories.
- ToolTrace: replayable, redacted, per-tool execution records with attempt index, duration, budget counters and issue links.
- Context budget: token/character/fact/anchor budget accounting before provider calls.
- Retry/repair contract: bounded retry, typed repair decisions and stop reasons.
- Accepted artifact state: accepted chapter conclusions, failed attempts, issue mapping and final assembly readiness.
- Failure taxonomy: timeout/rate limit/malformed response/network/programmatic blocker/semantic blocker/repair exhausted/dependency missing.
- Safe diagnostics: allowlist-first serialization that excludes secrets, raw provider responses and prompt payloads.

These capabilities must be implemented inside `fund_agent/agent` or the accepted local Agent boundary. They must not add production dependency on `dayu-agent`, `dayu.engine` or copied upstream Dayu runtime code. Any copying or substantial adaptation of upstream Dayu code requires a separate license/compliance gate before implementation.

## Non-goals

- No code changes.
- No prompt fix.
- No provider runtime budget change.
- No score-loop.
- No fail-closed semantic change.
- No deterministic fallback.
- No auditor relaxation.
- No Ch2 or Ch6 calibration.
- No update to `docs/design.md`, `docs/implementation-control.md`, startup packet, README files or runtime/config/provider code.
- No secret-bearing artifact.

## Risks / open questions

- Typed audit contracts may become too broad if they try to model every future Evidence Confirm need now. Keep MVP to chapter acceptance and issue mapping first.
- The boundary between Agent generic audit orchestration and Fund domain audit implementation needs exact file ownership in the implementation plan.
- Ch3 may require a contract-expression change rather than writer-only guidance. That must be decided in a narrow Ch3-only planning/review gate, not assumed here.
- Provider timeout may continue to block semantic audit even after Agent trace is introduced. Runtime budget calibration remains a separate owner.
- `ToolTrace` can accidentally capture prompts or model output if serializer policy is not allowlist-first. The implementation gate must include a secret scan / redaction test.
- Current retained artifacts have safe summaries but not enough accepted design authority to rewrite truth docs. Controller acceptance is required before any truth-source sync.

## Acceptance criteria

This design artifact is acceptable for review if:

- It is stored only under `docs/reviews/`.
- It states that it is proposed design, not current implementation fact.
- It answers Service, Agent, Fund audit, bounded LLM auditor, Ch2/Ch6 vs Ch3, and Dayu Engine internalization questions.
- It preserves all listed non-goals.
- It does not include API keys, Authorization headers, cookies, raw provider responses, hidden prompts, complete provider config or secret-bearing environment data.
- It provides enough boundary decisions for a later planning agent to write a code-generation-ready Agent engine plan without inventing ownership.

## Next gate

Recommended next controller action: run plan review for this design artifact. If accepted, create a separate implementation planning gate for `internalized Agent engine and typed audit contract MVP`, still with no provider runtime budget change.

Suggested implementation-planning slices, only after review acceptance:

- Slice A: define typed Agent execution and audit contract schema without changing runtime behavior or provider construction ownership.
- Slice B: wrap existing writer/programmatic-auditor/semantic-auditor calls in Agent-owned runner and `ToolTrace` using fake clients first.
- Slice C: migrate write-audit-repair state machine ownership from Service facade to Agent while Service keeps use case / policy / report strategy and provider construction remains Service-owned.

Ch3-only deterministic contract / wording calibration remains a separate controller gate. It may use this design as motivation, but it must not be bundled into Agent-engine implementation planning.

## Worker self-check at end

- Scope: pass. This artifact only proposes design under `docs/reviews/`.
- Non-goals: pass. No code, prompt, provider budget, score, fail-closed behavior, truth-doc or runtime/config changes are proposed as completed work.
- Evidence: pass. Claims are grounded in the required read set and retained 006597 artifacts.
- Secret handling: pass. The artifact includes only safe summary fields and file paths, not raw prompts, raw provider responses or secrets.
- Completion status: pass, pending external review by controller/review agents.
