# DS Plan Review: Fixture Promotion Content / Promotion-state Manifest Plan

Date: 2026-06-13

Review timestamp: 20260613-142506

Reviewer role: DS-role plan review worker, not controller

Reviewed artifact:
`docs/reviews/mvp-fixture-promotion-content-manifest-plan-20260613.md`

Verdict: `PASS_WITH_AMENDMENTS`

## Scope

This review is limited to plan review. No source, test, runtime, golden,
fixture, control or design files were modified.

Allowed reads used:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`
- the reviewed plan artifact
- relevant controller judgments
- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py`

Allowed validation used:

- `git status --short`
- `git diff --check`
- `git diff --check --no-index -- /dev/null docs/reviews/mvp-fixture-promotion-content-manifest-plan-20260613.md`
- targeted `rg` / `sed` / `nl` reads

No live/provider/LLM/analyze/checklist/readiness/release/PR command was run.

## Assumptions Tested

| Assumption | Result | Evidence |
|---|---|---|
| Source authority is bounded to accepted tracked golden content write, strict coverage evidence, parser implementation/downstream evidence and controller judgments. | PASS | Plan lines 28-35 and 60-68; tracked golden content judgment lines 19-27 and 33-55; downstream judgment lines 57-62 and 82-90. |
| Proposed write set is narrow and stays under `docs/reviews/`. | PASS | Plan lines 70-91; current startup packet lines 23-27; implementation-control lines 42-47. |
| Schema contract matches the implemented parser. | PASS | Plan lines 97-142; parser lines 1236-1254 and 1299-1354. |
| Validation matrix is executable and stays inside non-live/local boundaries. | PASS_WITH_AMENDMENTS | Plan lines 156-176; amendment needed because path-limited status does not prove forbidden paths are unchanged. |
| Release/readiness remains `NOT_READY` and overclaim is blocked. | PASS | Plan lines 11, 52-54, 178-184, 205-207, 227-229 and 253-263; startup packet lines 24-26. |

## Findings

| severity | evidence | recommended disposition |
|---|---|---|
| Medium | Plan lines 156-176 validate JSON parsing, parser loading, targeted tests, whitespace checks and path-limited status for only two target files. Plan lines 85-91 and 218-219 forbid edits to `reports/golden-answers/`, source, tests, fixtures, runtime outputs, README, control and design docs, but the validation matrix has no forbidden-path guard that would detect an accidental tracked edit in those paths. | Amend the next implementation-gate validation matrix before implementation acceptance. Add a read-only guard such as `git diff --name-only -- fund_agent tests reports/golden-answers docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md fund_agent/README.md tests/README.md` with expected empty output, and optionally a path-scoped `git status --short -- fund_agent tests reports/golden-answers docs/design.md docs/implementation-control.md docs/current-startup-packet.md README.md fund_agent/README.md tests/README.md` if the controller wants to detect new forbidden files too. Keep the existing target-file status check for the two allowed implementation artifacts. |
| Low | Plan line 159 uses `python3 -m json.tool`; the rest of project-aware validation uses `uv run python ...` / `uv run pytest ...` at lines 160-161. Historical repo artifacts have accepted `python -m json.tool`, and JSON syntax validation does not require project dependencies. | `python3 -m json.tool` is acceptable for syntax-only JSON validation. Prefer `uv run python -m json.tool ...` for interpreter consistency with the repo's current `uv` validation style, but do not block on this alone. |

## Schema Contract Check

The proposed manifest shape matches the implemented year-aware parser:

- Top-level unknown fields are rejected by `_reject_unknown_keys()` with the
  exact key set `schema_version`, `accepted_as_of`, `source_artifacts`,
  `entries`.
- Entry-level unknown fields are rejected with the exact key set `fund_code`,
  `report_year`, `promotion_state`, `promotion_identity`, `evidence_artifacts`.
- `promotion_identity` must equal `fund_year`.
- Identity is stored as `(fund_code, report_year)` and duplicate identities
  raise `ValueError`.
- Legacy fund-code-only inputs are routed into `legacy_fund_states`, not
  `fund_year_states`; downstream mapping treats them as diagnostic-only.

The plan correctly avoids adding row hashes, notes, raw body text,
readiness status or arbitrary `extra_payload` fields, which would violate the
current parser contract.

## Authority And Scope Check

The plan uses the correct authority chain:

- exactly seven accepted `004393 / 2025` tracked golden rows;
- strict golden coverage accepted as year-aware for the current tracked JSON
  surface;
- implemented year-aware parser/schema;
- downstream evidence for exact-year consumption, wrong-year non-cross-apply
  behavior and legacy diagnostic-only routing;
- controller judgments for those gates.

It does not rely on arbitrary workspace residue, old fund-code-only manifests,
local PDF/body files, live access, provider/LLM output or readiness/release
state.

The proposed next write set is narrow enough: one manifest JSON, one
implementation evidence artifact, review artifacts and one controller judgment,
all under `docs/reviews/`. It explicitly forbids edits to golden-answer
content, fixture content, source/tests/runtime, README, control and design docs.

## Validation Notes

Observed during this review:

- `git diff --check` returned clean.
- `git diff --check --no-index -- /dev/null docs/reviews/mvp-fixture-promotion-content-manifest-plan-20260613.md` emitted no whitespace diagnostics; exit code was non-zero only because the untracked file differs from `/dev/null`, which matches the plan's expected interpretation.

The implementation-gate validation should keep the parser self-check and
targeted parser tests. It should add the forbidden-path guard above before
controller acceptance.

## Open Questions

None blocking.

## Residual Risks

The implemented manifest schema is fund-year-level, not row-hash-level. This is
acceptable for the current plan only because the source authority is tied to the
accepted tracked golden content snapshot and the plan keeps future fee rows,
`turnover_rate`, skipped rows, deferred rows, other funds and other years out of
scope. Any future golden content expansion for `004393 / 2025` should trigger a
separate reviewed gate before reusing the same promotion claim.

## Conclusion

`PASS_WITH_AMENDMENTS`.

The plan is safe to hand to the next narrow implementation gate after adding a
forbidden-path validation guard. The `python3 -m json.tool` line is acceptable
as syntax-only validation; `uv run python -m json.tool` is preferred but not a
blocker.
