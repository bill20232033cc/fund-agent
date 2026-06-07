# MVP Agent Engine Design Slice B Tool Adapter Contract Plan Controller Judgment

## 1. Verdict

`PLAN_ACCEPTED_DESIGN_ONLY_WITH_FOLLOWUP_REQUIREMENTS`

Accepted plan:

- `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md`

Accepted reviews:

- `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-review-ds-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-review-codex-20260608.md`

Reviewer route:

- AgentMiMo remained unavailable for this gate.
- AgentDS provided the first independent review.
- AgentCodex was used as the operator-authorized Codex reviewer capacity in MiMo's absence.

DS returned `PASS`. Codex returned `PASS_WITH_NON_BLOCKING_OBSERVATIONS`.

## 2. Boundary Judgment

This judgment accepts Slice B as design-only planning input.

This judgment does not authorize:

- Agent runtime implementation;
- `fund_agent/agent` package creation;
- ToolRegistry, ToolTrace, adapter or schema implementation;
- migration of current Service `ChapterOrchestrator`;
- provider/default/runtime/budget/config change;
- provider writer/auditor clients as registry tools;
- live `--use-llm`, retry, endpoint probe, curl, DNS, socket probe or provider readiness check;
- LangGraph or MCP runtime;
- `dayu-agent`, `dayu.host` or `dayu.engine` production dependency;
- copying or rewriting upstream Dayu code;
- quality gate, golden/readiness, score-loop, multi-year runtime or public chapter ids `0-7` change;
- PR, push, merge, mark-ready, reviewer request or external comment.

## 3. Accepted Slice B Design Facts

- Future first Agent ToolRegistry may wrap only current Fund primitives: `project_chapter_facts()`, `write_chapter()`, `audit_chapter_programmatic()` and `audit_chapter_llm()`.
- `derive_evidence_availability()` is accepted as run-level same-source precomputation, not a ToolRegistry tool. It must be invoked once after `ChapterFactProjection` exists and reused across tasks and repair attempts.
- Provider writer/auditor clients remain Service-constructed per-run fields. They are passed into relevant Fund tool adapters but are not registry tools.
- ToolTrace and serialized Agent diagnostics must use allowlist projection only. They must not store current runtime diagnostic dataclasses wholesale.
- Serialized trace surfaces must exclude prompt text, draft markdown, fact values, unsafe anchor prose, raw provider response, raw audit response, raw provider request/body, API key, Authorization header, bearer token, model value and base URL value.
- Adapter error taxonomy keeps provider runtime failures separate from content/contract repair. Provider runtime categories must not become hidden Agent content repair attempts.
- Programmatic audit runs before semantic audit. Semantic audit pass must not overwrite programmatic blockers.

## 4. Review Finding Disposition

### DS NBO-1: Prompt char/token counts need implementation-time derivation rule

Disposition: `accepted_followup_requirement`

The later implementation planning gate must specify that prompt char counts and approximate prompt token counts are derived from in-memory prompt length heuristics only. They must not require retained prompt content, external token-count service calls, network access or serialized prompt text.

### DS NBO-2: `host_interrupted` belongs to Host/Agent scheduling, not adapter implementation

Disposition: `accepted_followup_requirement`

The later implementation planning gate must keep cancel/deadline detection in Host/Agent scheduling boundaries. Tool adapters may surface an already-observed `host_interrupted` terminal category, but must not implement Host lifecycle logic or inspect Host business state.

### Codex NBO-1: `request_id` safe projection shape must be pinned

Disposition: `accepted_followup_requirement`

The later implementation planning gate or Slice D trace validation plan must define `request_id` as an optional scalar from an explicit response-header allowlist only. ToolTrace and Agent serialized diagnostics must not serialize arbitrary response headers, full header maps, provider URLs, cookies, Authorization headers or provider config values.

## 5. Parent Follow-Up Status

| Parent requirement | Slice B status | Judgment |
|---|---|---|
| Runtime diagnostics safe projection | resolved | accepted: allowlist projection only; no wholesale runtime diagnostic dataclass storage |
| `diagnostic_consistency_status` explicit literal | resolved | accepted: current literal set or named explicit future equivalent |
| Run-level `EvidenceAvailability` non-tool boundary | resolved | accepted: not registry tool; derive once and reuse |
| Hidden retry semantics | partially resolved | taxonomy forbids hidden Agent retry; Slice C still owns field-level semantics |
| Chapter-attributed blocked reasons | deferred | still owned by implementation planning or later state-model gate |
| Equivalence testing | deferred | still owned by Slice D or implementation planning before code changes |

## 6. Validation Accepted

Controller validation:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md
```

Result: pass.

DS reviewer validation:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-review-ds-20260608.md
```

Result: pass.

Codex reviewer validation:

```text
git branch --show-current
git status --short
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-b-tool-adapter-contract-plan-review-codex-20260608.md
```

Result: pass.

No reviewer ran live provider, endpoint, network, PR, push, commit, source edit, test edit or control-doc edit actions.

## 7. Next Entry Point

Next authorized local entry is design-only:

- `MVP Agent Engine Design Slice C Repair And Budget Contract Plan`

Slice C must consume the follow-up requirements in Section 4 and the still-open
hidden retry semantics requirement from Slice A. It remains design-only unless a
later implementation plan receives review and controller judgment.

Still not authorized:

- Agent runtime implementation;
- live evidence;
- provider/runtime/default changes;
- score-loop, multi-year runtime, golden/readiness or quality gate changes;
- external PR/push/release actions.
