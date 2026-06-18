# MVP Provider Runtime Non-Timeout Residual Disposition / Diagnostic Plan

## 1. Scope And Classification

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate objective: decide how to dispose of the current same-run `provider_runtime_error_non_timeout` residual from the live rerun evidence.
- Role: planning worker only; not controller, not reviewer, not evidence executor, not provider operator, not implementation worker.
- Allowed write for this step: this plan artifact only.
- Classification: `heavy`.

Classification rationale under `AGENTS.md`: this gate does not change code, but it controls provider runtime residual routing after a live provider evidence gate. Its decision can affect future provider endpoint/network diagnostics, provider/default/runtime sequencing, Real LLM smoke re-baseline acceptance, and whether Chapter acceptance calibration remains blocked. Those are high-impact runtime/release-readiness adjacent decisions, so `heavy` is the conservative classification.

This plan itself authorizes no live provider command, endpoint reachability probe, curl, handwritten HTTP, PASS-only timing probe, retry, deterministic fallback, provider override, runtime/default change, source change, or external-state operation.

## 2. Authoritative Inputs Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md` as boundary truth only
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-controller-judgment-20260605.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-evidence-20260605.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-evidence-review-mimo-20260605.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-live-rerun-evidence-review-ds-20260605.md`
- `docs/reviews/mvp-future-live-provider-calibration-evidence-gate-plan-20260604.md`

Workspace preflight at planning time:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Dirty workspace includes unrelated tracked `pyproject.toml` and unrelated untracked files. They are not used as this gate's evidence and must not be staged or committed by this worker.

## 3. Current Same-Run Facts

Accepted controller judgment for the live rerun supersedes the evidence artifact's original label and classifies the residual as `provider_runtime_error_non_timeout`.

Direct same-run facts:

- presence-only readiness passed;
- exactly one unchanged-default command ran: `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`;
- command exited `1`;
- stdout was empty;
- no deterministic fallback was used;
- retained artifact exists at `reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/`;
- `orchestration_status=blocked`;
- `final_assembly_status=incomplete`;
- all six body chapters failed at writer operation with `llm_network_error` / `ConnectError` / provider runtime category `network`;
- no body chapter has an accepted draft or accepted conclusion.

Immediate implications:

- the residual is not the prior all-chapter `ReadTimeout` / `llm_timeout` shape;
- it is not `provider_runtime_residual_narrowed`, because there is no accepted/failed split;
- it is not Chapter acceptance calibration input, because there is no accepted draft/conclusion;
- it must remain fail-closed and must not be hidden by retry, fallback, provider default changes, or endpoint availability reclassification without same-source evidence.

## 4. Gate Question

This gate answers one routing question:

Should the current same-run `ConnectError` / `llm_network_error` residual be:

1. handled by a separate provider endpoint/network diagnostic gate;
2. deferred to provider runtime operator / environment owner without more repository work;
3. resolved by the existing accepted evidence with no further commands, meaning Real LLM smoke re-baseline remains blocked until a controller-authorized future attempt.

The gate does not answer whether the provider endpoint is reachable right now. It only defines what evidence and control decisions are required before anyone may attempt to answer that question.

## 5. Non-Goals And Forbidden Actions

Forbidden in this plan and any review/controller judgment of this plan:

- no live provider command;
- no endpoint reachability probe;
- no `curl`, handwritten HTTP, private provider client call, socket probe, DNS probe, or account metadata query;
- no PASS-only timing probe;
- no retry command;
- no deterministic fallback command;
- no provider endpoint, model, API key, timeout, attempts, backoff, max-output, budget, runtime default or provider default change;
- no source, tests, config, README, design doc, control doc, startup packet, template, quality gate, golden/readiness, runtime, Host/Agent, multi-year runtime, score-loop, PR/push/release change;
- no Chapter acceptance calibration;
- no inference from historical retained artifacts as root cause for this residual;
- no printing API key, Authorization header, bearer token, full env, provider base URL value, model value, raw prompt, writer draft, raw provider response, raw audit response or provider message body.

Allowed in this plan gate:

- read the authoritative artifacts listed above;
- write this plan artifact only;
- run local non-network repository/document checks if needed to verify artifact existence or syntax, as long as they do not touch provider/network/external state.

## 6. Decision Model

### 6.1 Existing Evidence Sufficient For Operator Deferral

Choose this route when controller agrees that the current accepted evidence already proves the repo behavior under unchanged defaults:

- fail-closed behavior is intact;
- incomplete stdout remains empty;
- no fallback occurred;
- all chapters failed before content calibration with same-run `ConnectError` / `llm_network_error`;
- no repository code/config/default change is implicated by same-source evidence.

Disposition: hand to provider runtime operator / environment owner. No further repository gate is required until the operator confirms environment/network/provider availability or requests a narrowly scoped diagnostic gate.

### 6.2 Separate Local-First Provider Endpoint/Network Diagnostic Gate

Choose this route only if controller needs a durable diagnostic artifact to separate local environment inheritance, local configuration shape, retained artifact classification, and external provider reachability responsibility.

This route must be local-first. The initial diagnostic gate may collect only non-live/local evidence from accepted artifacts, retained run artifacts, typed config schema/default definitions, and secret-safe environment presence metadata already collected in evidence. It must not probe endpoint reachability.

If local-first evidence is insufficient and an external diagnostic is still needed, that external step must be a separate controller-authorized gate after plan review. It must specify exact command(s), singularity limits, redaction rules, stop conditions, and residual owner before any network/provider call.

### 6.3 Existing Evidence Resolves Current Planning Question

Choose this route when the controller decides the accepted judgment already supplies the only valid classification: `provider_runtime_error_non_timeout`.

Disposition: record that Real LLM smoke re-baseline remains blocked, Chapter acceptance calibration remains blocked, and the next valid action is a later controller-authored provider/operator handoff or separately reviewed diagnostic gate. No command is needed now.

## 7. Evidence Allowed For A Future Diagnostic Gate

Future diagnostic evidence must prefer local, non-live, same-source evidence first.

### 7.1 Tier 0: Already Accepted Direct Evidence

Allowed:

- accepted live rerun controller judgment;
- accepted evidence artifact;
- MiMo and DS evidence reviews;
- retained artifact path and safe fields cited by those artifacts;
- presence-only readiness output already recorded in the evidence artifact.

Purpose:

- confirm current residual classification;
- confirm fail-closed/no-fallback/stdout-empty semantics;
- confirm no accepted chapter draft/conclusion exists;
- confirm no external command is needed to block Chapter acceptance calibration.

### 7.2 Tier 1: Local Retained Artifact Inspection

Allowed:

- read `manifest.json`, `summary.json`, and per-chapter JSON under the same retained artifact path;
- verify chapter matrix fields: `status`, `stop_reason`, `failure_category`, operation, terminal issue class, provider runtime category, attempts, elapsed scalar, timeout hint, accepted flags;
- run local redaction scans over the retained artifact and the new diagnostic artifact;
- compute a local summary table from retained JSON files.

Forbidden:

- reading raw prompt payloads, raw provider responses, raw audit responses, headers, endpoint URL values, API key values, or provider message bodies;
- treating missing raw provider body as evidence of endpoint behavior.

### 7.3 Tier 2: Local Code/Config Contract Inspection

Allowed:

- read typed config contract and serializer code to confirm safe field names, default names, and failure taxonomy;
- read tests only to understand current contract coverage, not to change behavior;
- run non-network static checks against documentation/artifact syntax if controller asks.

Forbidden:

- changing source/tests/config/defaults;
- deriving endpoint availability from config shape alone;
- treating env presence as proof of network reachability.

### 7.4 Tier 3: External Diagnostic Candidate, Not Authorized Here

External diagnostics are not authorized by this plan. If later needed, a separate controller-authorized gate must define one exact action set. Candidate actions must be evaluated and reviewed before execution, for example:

- a presence-only config recheck with no HTTP;
- one endpoint/provider reachability probe with safe method and strict redaction;
- one provider API minimal-call probe, if and only if controller accepts that spending provider quota and touching external state is necessary;
- one rerun of `006597 / 2024 --use-llm` only if the controller explicitly decides a full smoke rerun is the evidence target.

Any such external gate must preserve command singularity, no retry, no override unless explicitly under review, no default changes, no raw response capture, and immediate stop on secret leak or unexpected stdout/fallback behavior.

## 8. Blocker Taxonomy

| Blocker | Definition | Evidence source | Owner | Handling |
|---|---|---|---|---|
| `provider_runtime_error_non_timeout` | Same-run provider runtime failure other than timeout, including `llm_network_error` / `ConnectError` | accepted live rerun judgment and retained artifact | provider runtime operator / future calibration controller | Do not retry or reclassify; decide deferral vs separate diagnostic gate |
| `environment_inheritance_unproven` | Current execution shell cannot prove provider env presence without printing values | presence-only readiness only | provider config/operator shell owner | Fix shell inheritance outside repo; no code change implied |
| `local_artifact_incomplete` | Retained artifact path or safe fields needed for classification are missing/corrupt | local retained artifact inspection | diagnostic evidence worker / controller | Stop; do not substitute historical artifacts |
| `secret_safety_blocker` | Any artifact or command output includes API key, Authorization header, provider URL/model value, raw prompt or raw provider/audit response | redaction scan / review | controller | Stop immediately; open remediation gate |
| `forbidden_scope_drift` | Source/test/config/runtime/default/control/startup/golden/score/Agent/PR/release state changes appear | git status/diff and artifact scope | controller | Stop; classify as scope violation |
| `endpoint_reachability_unknown` | Local evidence cannot distinguish network path, provider account, endpoint DNS/TLS, or provider service availability | local-only evidence result | provider runtime operator / future calibration controller | Only external diagnostic gate can resolve; not this plan |
| `chapter_calibration_blocked` | No accepted draft/conclusion exists, so content calibration has no substrate | retained artifact chapter accepted flags | chapter/content calibration owner | Keep deferred |
| `provider_default_change_requested` | Any proposed fix changes endpoint/model/timeout/attempt/backoff/max-output/default budget | plan/review/controller text | controller | Requires separate reviewed implementation/config gate; not diagnostic evidence |

## 9. Acceptance Criteria

| ID | Criterion | Required evidence | Blocking failure |
|---|---|---|---|
| A1 | Gate classification is correct | Plan states `heavy` and rationale under `AGENTS.md` | Classified as `fast_path` or unreasoned `standard` |
| A2 | Gate question is explicit | Plan distinguishes separate diagnostic gate vs operator deferral vs existing-evidence resolution | Plan assumes a diagnostic command is already authorized |
| A3 | Same-run evidence is the only residual root-cause basis | Current facts cite accepted live rerun judgment and retained artifact | Historical timeout artifacts used as root cause for current `ConnectError` |
| A4 | Forbidden actions are complete | Plan forbids live commands, probes, retries, fallback, defaults/runtime/provider changes and scope changes | Any command or change is implicitly authorized |
| A5 | Local-first evidence hierarchy is defined | Tier 0-2 precede any external diagnostic candidate | External probe placed before local evidence review |
| A6 | External diagnostics are separated | Tier 3 says external diagnostics require a later controller-authorized gate | This plan authorizes curl/provider call/retry/PASS-only timing |
| A7 | Fail-closed semantics are preserved | Plan requires exit/stdout/no-fallback/retained-artifact safety to remain dispositive | Plan allows partial stdout, fallback, retry masking, or fail-open |
| A8 | Chapter acceptance calibration remains blocked | Plan ties block to zero accepted drafts/conclusions | Plan enters body chapter acceptance calibration |
| A9 | Provider/default/runtime changes remain blocked | Plan requires separate reviewed gate for any endpoint/model/timeout/attempt/backoff/max-output/default change | Plan recommends changing defaults as diagnostic |
| A10 | Reviewer handoff is actionable | MiMo and DS focus areas and verdict shapes are defined | Reviews cannot determine pass/fix/block |
| A11 | Controller judgment requirements are explicit | Controller must choose one disposition and residual owner before next work | Next entry point is ambiguous |
| A12 | Secret safety is preserved | Plan forbids secrets/raw payloads and requires redaction scanning for future evidence | Raw provider/request data can enter artifacts |

## 10. Reviewer Handoff Criteria

Required independent plan reviews before controller judgment:

- AgentMiMo review focus:
  - forbidden-scope containment;
  - no live/provider/network command authorization;
  - no retry/fallback/default change;
  - fail-closed stdout/exit/no-fallback semantics;
  - secret-safety and redaction constraints;
  - whether external diagnostics are properly separated into a later gate.

- AgentDS review focus:
  - first-principles evidence logic;
  - same-source root-cause discipline;
  - decision model completeness;
  - blocker taxonomy correctness;
  - acceptance criteria testability;
  - whether operator deferral vs separate diagnostic gate is a controller choice, not a planning-worker assumption.

Each review must return exactly one of:

- `PASS`: no blocking findings;
- `NEEDS_FIX`: plan can be corrected without new evidence;
- `BLOCKED`: the reviewer cannot validate the plan without missing truth input or controller clarification.

Blocking findings must be fixed in this artifact and re-reviewed before controller judgment.

## 11. Controller Judgment Requirements

Controller judgment after reviews must explicitly state:

- whether this plan is accepted;
- accepted residual classification remains `provider_runtime_error_non_timeout` or is changed only with same-run evidence;
- one chosen disposition:
  - `operator_deferred_no_repo_action`;
  - `open_local_first_provider_endpoint_network_diagnostic_gate`;
  - `existing_evidence_resolves_current_planning_question`;
- whether any future diagnostic gate is local-only or may later request a separate external diagnostic plan;
- that no live provider command, endpoint reachability probe, curl, handwritten HTTP, PASS-only timing probe, retry, fallback, provider/default/runtime/budget change, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/push/release work is authorized by this plan;
- that Chapter acceptance calibration remains unauthorized because no body chapter has an accepted draft/conclusion;
- residual owner and next entry point.

## 12. Residual Owners

| Residual / disposition | Owner | Next handling |
|---|---|---|
| `operator_deferred_no_repo_action` | provider runtime operator / environment owner | Investigate provider/network outside repo; return only with operator evidence or controller request |
| `open_local_first_provider_endpoint_network_diagnostic_gate` | future diagnostic planning/evidence worker under controller | Produce separate local-first plan/evidence artifact; no external command unless later authorized |
| `existing_evidence_resolves_current_planning_question` | controller | Keep Real LLM smoke re-baseline blocked; await provider/operator availability or future gate |
| `endpoint_reachability_unknown` | provider runtime operator / future calibration controller | Requires separate external diagnostic gate if controller wants direct reachability evidence |
| `chapter_calibration_blocked` | future chapter/content calibration owner | Remains deferred until a run produces accepted draft/conclusion substrate |
| `secret_safety_blocker` | controller | Stop and open remediation gate |
| `forbidden_scope_drift` | controller | Stop; quarantine or classify unrelated changes before proceeding |

## 13. Recommended Next Entry Point

After this plan artifact is reviewed:

1. Send this plan to MiMo and DS for independent plan review.
2. If both reviews pass, controller should issue a judgment choosing one disposition.
3. Recommended controller disposition: `open_local_first_provider_endpoint_network_diagnostic_gate` only if the controller needs a durable local diagnostic record before operator handoff; otherwise choose `operator_deferred_no_repo_action`.

Recommended next worker prompt if controller chooses the local-first diagnostic gate:

```text
你是 diagnostic evidence worker，只执行本 handoff，不要启动完整 gateflow。读取 AGENTS.md、startup/control、accepted non-timeout residual disposition plan/reviews/judgment、live rerun evidence/reviews/judgment，以及 retained artifact reports/llm-runs/006597-2024-20260604T164428Z-host_run_bd4ba477cecf42c/。只允许写一个 docs/reviews/ 下的 local diagnostic evidence artifact。禁止 live provider command、endpoint probe、curl、HTTP、PASS-only timing、retry、fallback、provider/default/runtime/budget/config/source/test/control/startup/design/README/golden/score/Agent/PR/release change。仅做本地 retained artifact summary、redaction scan、same-source classification check、operator-handoff recommendation。
```

## 14. Plan Verdict

This plan is ready for independent plan review. It intentionally stops before any diagnostic execution and does not authorize provider/network access. The minimum safe next step is MiMo and DS plan review, followed by controller judgment on disposition.
