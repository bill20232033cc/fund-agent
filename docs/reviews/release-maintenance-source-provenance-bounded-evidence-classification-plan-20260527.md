# Source Provenance Bounded Evidence Classification Plan

> Date: 2026-05-27
> Role: AgentCodex planner
> Gate: `post-implementation source provenance bounded evidence classification gate`
> Current checkpoint: `a0de731 feat: expose source provenance in snapshots`
> Scope: planning handoff only. Do not implement code. Do not run extraction evidence in this planning step.

## Startup Packet Replay

| Item | Current state |
|---|---|
| Branch | `codex/local-reconciliation` |
| Current phase | `release maintenance` |
| Current gate | `source provenance public-output implementation accepted locally` |
| Next entry point | `post-implementation source provenance bounded evidence classification gate; must use init-agents / tmux multi-agent flow` |
| Latest checkpoint | `a0de731 feat: expose source provenance in snapshots` |
| Design truth | `docs/design.md` current design sections, especially §2 and §6.1 |
| Control truth | `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point |
| Evidence chain only | `docs/reviews/` and `docs/archive/implementation-control-history-20260525.md` |

Allowed next-gate scope from the control artifact:

- Run bounded public `fund-analysis extraction-snapshot`, `fund-analysis extraction-score`, and `fund-analysis quality-gate` only for `110020` / 2024 and `017641` / 2024.
- Classify each row using only public provenance fields plus quality outputs.
- Do not infer fallback eligibility from downstream extraction success.
- Keep `110020` and `017641` outside the clean denominator unless public provenance explicitly proves eligible fallback and quality outputs do not block.
- Keep durable baseline / golden promotion blocked.
- Keep large generated output in scratch or ignored report directories; tracked artifacts contain only summaries and paths.

## Gate Objective

Classify the two previously fallback-blocked representative rows using the new public source provenance output:

| Fund code | Year | Prior role | Gate question |
|---|---:|---|---|
| `110020` | 2024 | index slot, previously fallback-blocked / source-unknown | Does public provenance now prove an eligible upstream primary failure and non-blocking quality output? |
| `017641` | 2024 | QDII slot, previously fallback-blocked / source-unknown | Does public provenance now prove an eligible upstream primary failure and non-blocking quality output? |

This gate may produce an evidence summary and terminal classification only. It must not promote either row to a durable baseline, golden answer corpus, clean denominator, or scoring-ready fixture.

Current implementation note: `AnnualReportSourceMetadata` does not propagate `primary_failure_category` into the public production snapshot path. Therefore, if either bounded row resolves through fallback with `fallback_used=true`, this gate is expected to classify it as `provenance_unknown_public_metadata_absent`. The `provenance_fail_closed`, `quality_blocked_after_provenance`, and `provenance_eligible_for_next_review` rules below are defensive future-capable paths for public outputs that already contain a persisted primary failure category; they are not expected to trigger in the current implementation unless future metadata exists.

## Exact Run IDs And Output Paths

Use one isolated run root per fund. All generated paths below are ignored by `.gitignore`.

| Fund | Snapshot run id | Snapshot output dir | Score output dir | Quality gate output dir |
|---|---|---|---|---|
| `110020` | `source-provenance-bounded-110020-2024-20260527` | `reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/` | `reports/scoring-runs/source-provenance-bounded-110020-2024-20260527/` | `reports/quality-gate-runs/source-provenance-bounded-110020-2024-20260527/` |
| `017641` | `source-provenance-bounded-017641-2024-20260527` | `reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/` | `reports/scoring-runs/source-provenance-bounded-017641-2024-20260527/` | `reports/quality-gate-runs/source-provenance-bounded-017641-2024-20260527/` |

Tracked summary artifact for the evidence worker:

- `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-20260527.md`

Generated outputs to reference but not track:

- `snapshot.jsonl`, `summary.md`, `errors.jsonl` under each snapshot output dir.
- `score.json`, `score.md`, `golden_set.json` under each score output dir.
- `quality_gate.json`, `quality_gate.md` under each quality gate output dir.

## Public Provenance Fields

Classify only from public snapshot JSONL fields emitted by the current implementation:

- `fallback_used`
- `primary_failure_category`
- `fallback_eligibility`
- `source_provenance_status`
- `source_provenance_reason`
- Supporting context fields: `source_provenance_schema_version`, `source_strategy`, `resolved_source_name`

Also read public quality output:

- `quality_gate.json` status: `pass`, `warn`, or `block`.
- Rule codes and issue summaries only for deciding whether quality blocks after provenance classification.

Do not inspect `FundDocumentRepository`, source helper internals, PDF cache, parsed cache, downloader output, raw source exceptions, web/search results, or any non-public repository metadata.

## Classification Rules

For each fund, first evaluate repository run completion, then provenance, then quality:

1. `repository_run_failed`
   - Any of snapshot, score, or quality-gate command exits non-zero, or required output files are absent.
   - The summary must record the failing command, exit code, and public output path if present.

2. `primary_succeeded_no_fallback`
   - Snapshot succeeded and public provenance has `fallback_used=false`, `fallback_eligibility="not_applicable"`, and `source_provenance_status="not_applicable"`.
   - If quality status is `pass` or `warn`, this state may only be considered by a later corpus decision; it remains `promotion_disposition=not_promoted` in this gate.
   - If quality status is `block`, record the quality block in the evidence summary and keep the row outside promotion in this gate.

3. `provenance_unknown_public_metadata_absent`
   - Snapshot succeeded but provenance is absent from public snapshot rows; or
   - `fallback_used=true` and `primary_failure_category` is `null` / missing, or `fallback_eligibility="unknown_public_metadata_absent"`, or `source_provenance_status="incomplete"` for the missing-category reason.
   - This state is non-clean and cannot enter the denominator.
   - This is the expected terminal provenance state for current fallback-backed rows because current implementation does not propagate `primary_failure_category` from repository source metadata.

4. `provenance_fail_closed`
   - `fallback_used=true` and `primary_failure_category` is one of `schema_drift`, `identity_mismatch`, `integrity_error`; or
   - `fallback_eligibility="fail_closed"`.
   - This state is non-clean even if extraction, scoring, or quality-gate execution succeeds.
   - Defensive future-capable path only for public outputs that expose persisted primary failure category.

5. `quality_blocked_after_provenance`
   - Public provenance explicitly proves fallback eligibility, but `quality_gate.json` has `status="block"`.
   - This state is outside the clean denominator because quality outputs block after source provenance is resolved.
   - Defensive future-capable path only; current fallback-backed rows are expected to stop at `provenance_unknown_public_metadata_absent` while primary failure category is absent.

6. `provenance_eligible_for_next_review`
   - Required all together:
     - `fallback_used=true`.
     - `primary_failure_category in {"not_found", "unavailable"}`.
     - `fallback_eligibility="eligible"`.
     - `source_provenance_status="complete"`.
     - `quality_gate.json.status in {"pass", "warn"}`.
   - This state only means the row may be considered by a later reviewed corpus decision. It does not promote the row in this gate.
   - Defensive future-capable path only for public outputs that expose persisted eligible primary failure category.

7. `not_promoted`
   - Use as the final promotion disposition for every row in this gate.
   - Even if a row reaches `primary_succeeded_no_fallback` or `provenance_eligible_for_next_review`, the evidence artifact must still record `promotion_disposition=not_promoted`.

Strict negative rule:

- Successful extraction, a populated `snapshot.jsonl`, a populated `score.json`, or a non-blocking quality gate is not evidence of fallback eligibility. Fallback eligibility is proved only by public provenance fields showing `fallback_used=true`, an eligible `primary_failure_category`, and `fallback_eligibility="eligible"`.

## Denominator And Promotion Rules

- `110020` and `017641` remain outside the clean denominator unless public provenance explicitly proves eligible fallback and quality outputs do not block.
- If either row is `provenance_unknown_public_metadata_absent`, `provenance_fail_closed`, `repository_run_failed`, or `quality_blocked_after_provenance`, it remains outside the clean denominator.
- If either row is `primary_succeeded_no_fallback`, it remains `promotion_disposition=not_promoted` in this gate. With quality status `pass` or `warn`, it may only be considered by a later corpus decision; there is no direct promotion here.
- If either row is `provenance_eligible_for_next_review`, it is still not added to baseline / golden / fixture state in this gate. A later reviewed corpus gate must decide promotion.
- No direct baseline, golden answer, strict golden, curated fixture, or clean denominator promotion is allowed here.

## Reviewer Matrix

Use the `init-agents` tmux protocol before worker handoff: discover pane with `tmux-cli status` and `tmux list-panes -a`, clear only for new assigned tasks, avoid bare PR-number syntax, and require no commit / no push / no PR.

| Stage | Agent | Role | Required artifact |
|---|---|---|---|
| Plan review | AgentMiMo | Review plan against AGENTS, design §6.1, control Next Entry, source fail-closed semantics | `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-plan-review-mimo-20260527.md` |
| Plan review | AgentGLM | Independent review of command bounds, terminal states, denominator rules, forbidden scope | `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-plan-review-glm-20260527.md` |
| Evidence run | AgentCodex or explicitly assigned worker | Run only accepted bounded public CLI evidence and write summary artifact | `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-20260527.md` |
| Evidence review | AgentMiMo | Review classification logic and public-output-only evidence chain | `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-review-mimo-20260527.md` |
| Evidence review | AgentGLM | Independent review of terminal states and no-promotion discipline | `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-review-glm-20260527.md` |
| Controller judgment | AgentCodex controller | Accept/reject evidence classification and record next gate | `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-controller-judgment-20260527.md` |

## Validation Commands For Evidence Worker

Do not run these during planning. After plan review acceptance, run exactly the bounded commands below.

```bash
uv run fund-analysis extraction-snapshot --run-id source-provenance-bounded-110020-2024-20260527 --report-year 2024 --fund-code 110020 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/snapshot.jsonl --errors-path reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/source-provenance-bounded-110020-2024-20260527
uv run fund-analysis quality-gate --score-path reports/scoring-runs/source-provenance-bounded-110020-2024-20260527/score.json --output-dir reports/quality-gate-runs/source-provenance-bounded-110020-2024-20260527

uv run fund-analysis extraction-snapshot --run-id source-provenance-bounded-017641-2024-20260527 --report-year 2024 --fund-code 017641 --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/snapshot.jsonl --errors-path reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/errors.jsonl --source-csv docs/code_20260519.csv --output-dir reports/scoring-runs/source-provenance-bounded-017641-2024-20260527
uv run fund-analysis quality-gate --score-path reports/scoring-runs/source-provenance-bounded-017641-2024-20260527/score.json --output-dir reports/quality-gate-runs/source-provenance-bounded-017641-2024-20260527
```

Recommended public-output inspection commands after the six bounded runs:

```bash
python -m json.tool reports/quality-gate-runs/source-provenance-bounded-110020-2024-20260527/quality_gate.json
python -m json.tool reports/quality-gate-runs/source-provenance-bounded-017641-2024-20260527/quality_gate.json
rg -n '"(fund_code|fallback_used|primary_failure_category|fallback_eligibility|source_provenance_status|source_provenance_reason)"' reports/extraction-snapshots/source-provenance-bounded-110020-2024-20260527/snapshot.jsonl reports/extraction-snapshots/source-provenance-bounded-017641-2024-20260527/snapshot.jsonl
```

If an inspection helper script is needed for summary aggregation, it must read only the generated public JSON / JSONL outputs above and write only the tracked summary artifact. It must not import or call repository/source/cache/helper internals.

## Evidence Summary Required Shape

The evidence artifact must include:

- Startup Packet replay and exact checkpoint.
- Exact command table with exit codes.
- For each fund: output paths, provenance fields, quality gate status, issue count, terminal state, and `promotion_disposition=not_promoted`.
- A short denominator decision table.
- A generated-output hygiene note proving only ignored reports directories were written, plus the tracked summary artifact.
- Explicit statement that successful extraction was not used as fallback eligibility evidence.

## Forbidden Scope

This gate forbids:

- Source code changes.
- Test changes.
- `docs/design.md` changes.
- `docs/implementation-control.md` changes.
- Direct PDF, parsed-cache, document-cache, source-helper, downloader, source adapter, or source strategy access.
- `FundDocumentRepository` source strategy changes or fallback semantics changes.
- Renderer changes.
- FQ0-FQ6 or quality-gate policy changes.
- Default `fund-analysis analyze` / `fund-analysis checklist` behavior changes.
- Golden answer, baseline, strict golden, curated fixture, or clean denominator promotion.
- Host/Agent packages, `dayu.host`, `dayu.engine`, tool loop, runner, ToolRegistry, ToolTrace, session/run lifecycle work.
- Web/search replacement evidence or external source probing.
- Commit, push, PR creation, PR mutation, branch deletion, or merge operations.

## Stop Conditions

Stop and return to controller if:

- Any command requires code changes to complete.
- Public snapshot output lacks the provenance fields required for classification.
- Evidence requires direct repository/source/cache/PDF inspection.
- The row appears eligible only because extraction or quality gate succeeded, without public eligible provenance fields.
- Any proposed next step would promote baseline/golden fixtures or alter clean denominator in this gate.
