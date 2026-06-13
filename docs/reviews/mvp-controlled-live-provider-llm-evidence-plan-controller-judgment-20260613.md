# Controller Judgment: Controlled Live Provider/LLM Evidence Plan

Date: 2026-06-13

Gate: `Controlled Live Provider/LLM Evidence Planning and Authorization Gate`

Controller verdict: `ACCEPT_WITH_FIXED_FINDINGS_NOT_READY`

## Scope

This judgment accepts a planning/authorization-only artifact for a later
controlled live provider/LLM evidence execution gate.

This gate did not run live provider/LLM, network, PDF, FDR, source, analyze,
checklist, readiness, release, PR, push, merge, cleanup or external-state
commands. It did not modify source, tests, runtime behavior, manifest, fixture,
golden-answer content, README or design truth.

Release/readiness remains `NOT_READY`.

## Inputs Reviewed

| Input | Role |
|---|---|
| `AGENTS.md` | Rule truth for heavy gate, source policy and live/external authorization. |
| `docs/design.md` | Design truth for explicit opt-in provider-backed `--use-llm` Route C. |
| `docs/current-startup-packet.md` | Current gate and `NOT_READY` posture. |
| `docs/implementation-control.md` | Control truth and next entry. |
| `fund_agent/ui/cli.py` | Current CLI option contract. |
| `fund_agent/config/llm.py` | Current provider env/config contract. |
| `docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-20260613.md` | Plan artifact under judgment. |
| `docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-review-ds-20260613.md` | DS review and targeted re-review. |
| `docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-review-mimo-20260613.md` | MiMo review and targeted re-review. |

## Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| DS | Initial `FINDINGS`; targeted re-review `PASS` | ACCEPT_FIXED_FINDINGS |
| MiMo | Initial `FINDINGS`; targeted re-review `PASS` | ACCEPT_FIXED_FINDINGS |

## Finding Disposition

| Finding | Disposition | Controller rationale |
|---|---|---|
| Redaction checks could misclassify safe scalar/policy metadata as sensitive leakage. | ACCEPTED_AND_FIXED | Plan now separates value-bearing secret/raw-body retention from safe scalar/policy metadata and allows known safe metadata fields. |
| `FUND_AGENT_LLM_MAX_OUTPUT_CHARS` was not fixed by the exact command. | ACCEPTED_AND_FIXED | Plan now forces `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000` in exact/allowed commands and stop conditions. |
| Source-policy terms were mixed with sensitive terms. | ACCEPTED_AND_FIXED | Plan now classifies actual source/fallback use as `UNEXPECTED_SOURCE_ACCESS` while allowing negative assertions and guardrail text. |

## Accepted Plan Facts

| Fact | Disposition | Basis |
|---|---|---|
| The plan is execution-ready but does not execute live commands. | ACCEPT | Scope and next-entry sections. |
| Future execution requires separate explicit live authorization. | ACCEPT | Authorization boundary and acceptance criteria. |
| Future execution is limited to one exact sample: `004393 / 2025`. | ACCEPT | Proposed live sample and stop conditions. |
| Future execution is limited to one exact Route C command using `--use-llm`. | ACCEPT | Command boundary. |
| The command uses `--dev-override --quality-gate-policy warn`, matching current CLI constraints. | ACCEPT | CLI contract and review results. |
| Provider timeout/backoff/output caps are fixed in the command prefix. | ACCEPT | Command boundary and env table. |
| EID single-source/no fallback remains current source policy. | ACCEPT | Non-goals, stop conditions and source-policy residual handling. |
| Redaction rules forbid raw prompt/provider/PDF/cache/source/final-report body retention while allowing safe scalar/policy metadata. | ACCEPT | Redaction section after review fixes. |
| 401/403 provider-response classification remains non-blocking residual unless proven directly. | ACCEPT_RESIDUAL | Plan residual table and L3/L4/Post-L4 accepted judgments. |
| Release/readiness remains `NOT_READY`. | ACCEPT_CONTROL_FACT | Plan and control docs. |

## Rejected Claims

| Claim | Disposition | Reason |
|---|---|---|
| This plan authorizes live execution now. | REJECT | Execution requires a later explicit live execution authorization. |
| One live run can prove provider readiness. | REJECT | Future evidence is one bounded sample only. |
| One live run can prove LLM content quality or chapter acceptance globally. | REJECT | Content acceptance remains separate. |
| This plan changes deterministic default behavior. | REJECT | Route C is explicit opt-in only. |
| This plan changes source policy or authorizes fallback/source expansion. | REJECT | EID single-source/no fallback is preserved. |
| This plan authorizes PR/release/readiness state changes. | REJECT | External state and readiness remain separate. |

## Residuals

| Residual | Classification | Owner | Next handling |
|---|---|---|---|
| Controlled live provider/LLM execution remains unrun. | next live authorization boundary | User/controller + provider runtime owner | `Controlled Live Provider/LLM Evidence Execution Gate` only after explicit live authorization. |
| 401/403 provider-response classification remains unproven. | optional no-live residual | Provider/runtime owner | Defer unless controller/user requires no-live mock classification before execution. |
| LLM content quality/chapter acceptance remains unaccepted. | content-quality residual | Provider/runtime + chapter owners | Separate content-quality review gate after live evidence if needed. |
| Source/PDF/cache body leak absence remains bounded to safe metadata/redaction. | evidence-scope residual | Controller/evidence owner | Do not read raw bodies in execution evidence. |
| Release/readiness remains unproven. | readiness blocker | Release owner/controller | Separate readiness/release gate only. |
| PR/push/merge/mark-ready remains external state. | external-state residual | User/controller | Separate explicit authorization only. |

## Controller Decision

Accept the controlled live provider/LLM evidence plan with fixed findings.

The accepted plan defines one future live Route C execution boundary, but does
not authorize execution in this gate. It preserves EID single-source/no fallback
and `NOT_READY`.

## Next Entry

Recommended next entry:

`Controlled Live Provider/LLM Evidence Execution Gate`

This next entry requires separate explicit authorization before any
live/provider/LLM/network command is run.

Deferred entries:

- no-live 401/403 provider-response mock classification;
- LLM content acceptance;
- release/readiness execution or claim;
- PR/push/merge/mark-ready;
- cleanup/archive/ignore disposition;
- golden-answer promotion or fixture/manifest expansion;
- source expansion or fallback design.
