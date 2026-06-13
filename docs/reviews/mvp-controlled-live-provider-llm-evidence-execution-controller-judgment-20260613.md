# Controller Judgment - Controlled Live Provider/LLM Evidence Execution

Date: 2026-06-13

Gate: `Controlled Live Provider/LLM Evidence Execution Gate`

Controller verdict: `ACCEPT_FAIL_CLOSED_WITH_PLAN_BLOCKER_RESIDUALS_NOT_READY`

Release/readiness: `NOT_READY`

## Inputs

Truth/control inputs:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- accepted live plan checkpoint `b6853e3`
- `docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-20260613.md`
- `docs/reviews/mvp-controlled-live-provider-llm-evidence-plan-controller-judgment-20260613.md`

Execution/review inputs:

- `docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-20260613.md`
- `docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-review-mimo-20260613.md`
- `docs/reviews/mvp-controlled-live-provider-llm-evidence-execution-review-ds-20260613.md`

## Scope Judgment

This gate is accepted only as bounded live execution evidence. It does not
authorize source/test/runtime behavior changes, manifest edits, golden-answer
content changes, fixture promotion, README/design truth changes, source policy
changes, cleanup, PR/push/merge/mark-ready or release/readiness status changes.

The runtime artifact under `reports/llm-runs/` remains local evidence residue.
It is not source truth, content truth, release evidence or readiness proof.

## Accepted Facts

| Fact | Disposition | Basis |
|---|---|---|
| The exact accepted Route C `--use-llm` command for `004393 / 2025` was run once after explicit user authorization. | ACCEPT | Execution evidence command and stats. |
| The command failed closed with `exit_code=1`, empty stdout and incomplete final assembly. | ACCEPT | Execution stats and safe stderr summary. |
| The run produced incomplete diagnostic metadata at the recorded `reports/llm-runs/.../manifest.json` path. | ACCEPT | Manifest/summary safe metadata. |
| Chapters 1, 2, 4, 5 and 6 reached accepted status in metadata. | ACCEPT_WITH_SCOPE_LIMIT | Safe chapter matrix only; not content-quality acceptance. |
| Chapter 3 failed before provider attempt metadata with `llm_exception` / `code_bug` / `ValueError`. | ACCEPT | Summary first-failed diagnostic metadata. |
| First-failed provider attempt count was `0`. | ACCEPT | Summary first-failed diagnostic metadata. |
| The exact command set `FUND_AGENT_LLM_MAX_OUTPUT_CHARS=12000`. | ACCEPT_COMMAND_FACT | Executed command boundary. |
| Runtime metadata proves `max_output_chars=12000`. | REJECT | Safe runtime metadata recorded `max_output_chars=null`. |
| The `max_output_chars` runtime metadata stop condition is plan-compliant. | ACCEPT_AS_BLOCKER_RESIDUAL_ONLY | Command fact is bounded; runtime proof is absent due pre-provider Chapter 3 failure. |
| Safe manifest/summary metadata did not show annual-report source fallback or Eastmoney/CNINFO/fund-company source expansion. | ACCEPT_WITH_SCOPE_LIMIT | Metadata-only search; not broad source-policy proof. |

## Rejected Claims

| Claim | Disposition | Reason |
|---|---|---|
| Provider readiness is proven. | REJECT | The run failed incomplete; first failure had provider attempt count `0`. |
| LLM content quality is accepted. | REJECT | No report body or chapter content body was reviewed. |
| 401/403 provider-response classification is closed. | REJECT | No 401/403 provider response was observed. |
| Release/readiness is accepted. | REJECT | Current control truth remains `NOT_READY`. |
| Source acquisition policy changed or fallback was authorized. | REJECT | EID single-source/no fallback remains current operational policy. |
| Another live execution should be run immediately. | REJECT | Chapter 3 code-bug and output-cap metadata residuals require no-live root-cause disposition first. |

## Review Disposition

| Reviewer | Initial status | Targeted re-review | Controller disposition |
|---|---|---|---|
| MiMo | High finding on `max_output_chars` runtime metadata proof; low next-entry wording finding. | PASS | Findings closed; residual preserved rather than overclaimed. |
| DS | High finding on `max_output_chars` runtime metadata proof. | PASS | Finding closed; residual preserved rather than overclaimed. |

## Accepted / Rejected / Residual Table

| Item | Controller disposition | Owner | Next handling |
|---|---|---|---|
| Exact single live command execution. | ACCEPT | Controller/evidence owner | Accepted checkpoint. |
| Fail-closed incomplete run. | ACCEPT | Controller/evidence owner | Accepted checkpoint. |
| Chapter 3 `code_bug` / `ValueError`. | ACCEPT_RESIDUAL | Provider/LLM Route C owner | No-live Chapter 3 root-cause planning/evidence. |
| Runtime `max_output_chars=12000` metadata proof. | ACCEPT_AS_BLOCKER_RESIDUAL_ONLY | Provider/LLM Route C owner + controller | Determine whether null metadata is expected for pre-provider code bug or indicates diagnostic propagation defect. |
| Live provider/LLM full report completion. | DEFER | Runtime/provider owner | Only after Chapter 3 residual is dispositioned. |
| LLM content quality acceptance. | DEFER | Runtime/provider + chapter owners | Separate content-quality gate after complete accepted run exists. |
| 401/403 provider-response classification. | DEFER | Provider/runtime owner | Optional no-live mock classification gate. |
| Release/readiness. | REJECT_FOR_THIS_GATE | Release owner/controller | Separate readiness/release gate; remains `NOT_READY`. |
| PR/push/merge/mark-ready. | DEFER_EXTERNAL_STATE | User/controller | Separate explicit authorization only. |

## Controller Self-check

- Current role: controller; this judgment accepts bounded evidence and records
  residuals only.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`,
  `docs/implementation-control.md`, accepted plan checkpoint `b6853e3`, evidence
  artifact and two review artifacts.
- Scope boundary: docs/reviews artifact closeout and subsequent control-doc sync
  only; no source/test/runtime behavior change and no repeat live execution.
- Stop conditions: no blocking reviewer findings remain; residuals are classified
  with owners and next gate.
- Evidence: one authorized live command ran once; two targeted re-reviews passed.
- Next action: create local accepted checkpoint, then synchronize startup/control
  docs to the no-live Chapter 3 root-cause planning next entry.

## Next Entry

Recommended next entry:

`Provider/LLM Chapter 3 Code-bug Root-cause Planning Gate`

Purpose: determine, without live execution, why Chapter 3 failed before provider
attempt metadata was available and whether a narrow code/test fix is needed.

Rules for the next entry:

- no live/provider/LLM/network/PDF/FDR/source/analyze/checklist/readiness/release/PR commands;
- preserve EID single-source/no fallback;
- preserve `NOT_READY`;
- do not repeat live execution until Chapter 3 and output-cap metadata residuals
  have reviewed disposition.
