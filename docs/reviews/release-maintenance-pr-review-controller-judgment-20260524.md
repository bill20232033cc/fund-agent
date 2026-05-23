# Release Maintenance PR Review Controller Judgment - 2026-05-24

## Gate

- Current phase: `release maintenance`
- Current gate: `PR review`
- Pull Request: `https://github.com/bill20232033cc/fund-agent/pull/16`
- Head: `codex/checklist-host-engine-design` @ `23a3c320fd0fa9a317f0803fe567125ca9dc9125`
- Base: `main` @ `3769def95badb5d89ba32db4ff4fa00443dbcd44`
- Review artifacts:
  - `docs/reviews/release-maintenance-pr-review-mimo-20260524.md`
  - `docs/reviews/release-maintenance-pr-review-glm-20260524.md`
- Controller conclusion: `PR fix required for one accepted low finding`

## Review Summary

| Reviewer | Conclusion | Findings | Gate Recommendation |
|---|---|---:|---|
| MiMo | `PASS_WITH_FINDINGS` | 3 low | PASS / can merge after low-risk cleanup or defer |
| GLM | `PASS_WITH_FINDINGS` | 3 low | PASS / can merge |

Both reviewers confirmed the PR satisfies the current truth guardrails:

- no `fund_agent/host` or `fund_agent/agent` placeholder package;
- no `dayu.host` / `dayu.engine` code import or dependency before an explicit gate;
- current deterministic path remains UI -> Service -> `fund_agent/fund`;
- no explicit business parameters are hidden in `extra_payload`;
- local `review_report.md` is not part of the PR diff;
- PR merge state is `CLEAN` and CI `test` is successful.

## Controller Finding Decisions

### PR16-C1-accepted-low-current-source-old-runtime-engine-terms

- **Source**: MiMo F1.
- **Decision**: accepted.
- **Reason**: `fund_agent/fund/_value_utils.py` is current source, not archive. Its module docstring still says the helper does not depend on `Service、Engine、Runtime 或 UI 层`; `Engine` and `Runtime` are superseded architecture terms. Current truth uses `UI -> Service -> Host -> Agent`, so this should be corrected before final PR pass.
- **Required fix**: In `fund_agent/fund/_value_utils.py`, replace the old `Engine、Runtime` wording with current `Host` wording. Do not change runtime behavior.
- **Validation**: `rg -n "Engine|Runtime" fund_agent`, `uv run ruff check fund_agent/fund/_value_utils.py`, `git diff --check`, and PR range `git diff --check origin/main..HEAD` after the follow-up push.

### PR16-C2-rejected-historical-control-archive-capability-terms

- **Source**: MiMo F2.
- **Decision**: rejected for current PR fix.
- **Reason**: The cited `docs/implementation-control.md` lines are historical/archive context. Startup Packet explicitly says archive old six-layer/Application/Runtime/Engine/Capability wording is historical evidence only and not current architecture truth. Rewriting historical control archive rows now would expand scope and reduce evidence fidelity.
- **Residual**: none for this PR.

### PR16-C3-deferred-low-quality-gate-summary-protocol

- **Source**: MiMo F3.
- **Decision**: deferred.
- **Reason**: `_echo_quality_gate_summary` currently uses duck typing across `FundAnalysisResult` and `FundChecklistResult`; this is a maintainability cleanup, not a correctness or architecture blocker. It should be handled in a dedicated UI typing cleanup if selected later.
- **Owner / destination**: future release-maintenance UI typing cleanup.

### PR16-C4-deferred-low-renderer-status-sets

- **Source**: GLM F1.
- **Decision**: deferred.
- **Reason**: The hard-coded sets reflect current `Literal` value domains and are covered by renderer/final-judgment behavior tests. Constant extraction can improve maintainability later, but no current failure or boundary violation is shown.
- **Owner / destination**: future renderer maintainability cleanup.

### PR16-C5-deferred-low-report-year-default

- **Source**: GLM F2.
- **Decision**: deferred.
- **Reason**: CLI `report_year=2024` is an existing product default shared by `analyze` and `checklist`. Changing it to dynamic or required input is user-visible behavior and requires a separate product-contract plan/review, not a PR review fix.
- **Owner / destination**: future CLI product-contract review if selected.

### PR16-C6-deferred-low-cli-boundary-test-deduplication

- **Source**: GLM F3.
- **Decision**: deferred.
- **Reason**: Duplicate or overlapping boundary tests are maintenance cost, not a correctness failure. Test consolidation should be done only in a dedicated test-hygiene slice.
- **Owner / destination**: future test-hygiene cleanup.

### PR16-C7-rejected-checklist-quality-gate-policy-residual

- **Source**: GLM residual risk.
- **Decision**: rejected as not evidenced by current code path.
- **Reason**: CLI `checklist` builds a `FundAnalysisRequest` without developer overrides; Service resolution defaults `quality_gate_policy` to `block`, matching the current design/control contract that `checklist()` shares block-policy parity with `analyze`. Test helpers use `quality_gate_policy="off"` for unit setup, but that is not the product CLI default.

## Required Fix Scope

Dispatch a fix worker for `PR16-C1` only.

Allowed files:

- `fund_agent/fund/_value_utils.py`
- `docs/reviews/release-maintenance-pr-review-fix-20260524.md`

Non-goals:

- no behavior change;
- no test changes unless the fix worker finds a validation-only need;
- no design/control/README/CI/dependency/lockfile changes;
- no Host/Agent package creation or Dayu dependency changes;
- no PR comments, reviewer requests, merge, mark-ready, or branch deletion.

## Next Gate

Fix `PR16-C1`, dispatch targeted PR re-review to MiMo and GLM, then if both pass, create the accepted PR review commit and push the follow-up commit.
