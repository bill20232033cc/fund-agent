# Release Acceptance Packaging / PR Readiness — 2026-05-25

## Scope

This gate packages the accepted deterministic MVP release evidence for local acceptance and PR readiness. It does not implement new product behavior and does not enter report-quality validator integration, Host/Agent, or Dayu runtime work.

Authoritative inputs:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point
- `docs/reviews/release-readiness-reconciliation-20260525.md`

## Branch State

Current branch:

- `codex/v0-release-readiness-plan`

Remote:

- `origin https://github.com/bill20232033cc/fund-agent.git`

Upstream:

- no upstream configured for `codex/v0-release-readiness-plan`

Base:

- `origin/main`
- merge-base: `99df84c266430a89e321fe75989708adc5b3858a`

HEAD before this packaging artifact:

- `96b5406 docs: sync release readiness control pointer`

Current PR state from read-only `gh pr list --state all --limit 50`:

- no open PRs
- PR 17: `MERGED`, `codex/004393-quality-gate` -> `main`, merged at `2026-05-24T09:26:04Z`
- PR 16: `MERGED`
- PR 15: `CLOSED`, not open; the older control-doc statement that PR 15 remained open is superseded by current GitHub state

No push, PR creation, PR close, or GitHub mutation was performed in this gate.

## Branch Diff for PR

`origin/main..HEAD` currently contains 33 local commits.

High-level diff:

- 86 tracked files changed
- 20,186 insertions
- 2,187 deletions

Runtime-relevant source/test additions:

- `fund_agent/fund/report_evidence.py`
- `fund_agent/fund/report_quality_validation.py`
- `tests/fund/test_report_evidence.py`
- `tests/fund/test_report_quality_validation.py`

Runtime boundary check:

`git diff --name-only origin/main..HEAD -- fund_agent/fund/template/renderer.py fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py fund_agent/services fund_agent/ui fund_agent/host fund_agent/agent pyproject.toml uv.lock` returned no files.

Conclusion:

- current renderer unchanged
- FQ0-FQ6 quality gate implementation unchanged
- Service unchanged
- CLI unchanged
- no Host package introduced
- no Agent runtime package introduced
- no `pyproject.toml` / `uv.lock` dependency change
- no `dayu.host` / `dayu.engine` runtime dependency introduced

## Release Command Evidence

Command:

```text
uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block
```

Result:

- exit code: 0
- `quality_gate_status: warn`
- `quality_gate_issues: 3`
- `quality_gate_info: strict golden answer not covered for fund_code 004393 reason=field_not_comparable`
- 8-chapter report rendered with evidence appendix

Command:

```text
uv run fund-analysis checklist 004393 --report-year 2024 --thermometer-cache-dir /tmp/fund-agent-release-acceptance/thermometer
```

Result:

- exit code: 0
- `quality_gate_status: warn`
- `overall_signal: yellow`
- `overall_status: watch`
- `valuation_state: unavailable`
- `final_judgment: needs_attention`
- `next_minimum_verification: 先补充或复核黄灯问题 manager_alignment 的关键证据。`

Command:

```text
uv run fund-analysis thermometer --cache-dir /tmp/fund-agent-release-acceptance/thermometer --json
```

Result:

- exit code: 0
- `index_code: wind_all_a`
- `temperature: 65.80`
- `valuation_state_candidate: fair`
- `data_date: 2026-05-22`
- `source: akshare_legulegu_all_a_pe_pb`

## Validation Evidence

Command:

```text
uv run pytest
```

Result:

- `697 passed in 1.49s`

Command:

```text
uv run ruff check .
```

Result:

- `All checks passed!`

Command:

```text
git diff --check
```

Result:

- passed with no output

Tracked scratch check:

```text
git ls-files reports docs/reviews | rg '\.(jsonl|json)$|scoring-runs|quality-gate-runs|scratch|tmp'
```

Result:

- only `reports/golden-answers/golden-answer.json`

Ignored runtime outputs:

- `cache/`
- `reports/quality-gate-runs/`

These are ignored runtime outputs and are not tracked PR payload.

## Untracked Local Documents

Current untracked local files:

- `docs/dayu-agent-timeline-analysis.md`
- `docs/dayu-agent模板技术机制深度解析.md`
- `docs/reviews/release-maintenance-report-quality-validator-integration-decision-plan-20260525.md`
- `docs/基金分析模板方法论对比.md`
- `review_report_20260525.md`
- `review_report_20260526.md`

Packaging decision:

- Keep these files untracked for this release PR.
- They are not required to prove deterministic MVP release readiness.
- The untracked `release-maintenance-report-quality-validator-integration-decision-plan-20260525.md` belongs to the deferred validator integration decision and must not be mixed into release acceptance.

## PR Readiness Judgment

Local branch readiness:

- Ready to push as a release-readiness PR branch, subject to user authorization.

Recommended PR title:

```text
Release readiness: deterministic MVP and report-quality evidence contract
```

Recommended PR body:

```markdown
## Summary

- Adds typed ReportEvidenceBundle projection and JSONL content validator under Fund capabilities.
- Preserves current deterministic product path: UI -> Service -> fund_agent/fund.
- Records release-readiness reconciliation and PR readiness evidence.

## Runtime Boundaries

- No renderer changes.
- No FQ0-FQ6 quality gate behavior changes.
- No Service or CLI default behavior changes.
- No Host/Agent package introduction.
- No dayu.host / dayu.engine runtime dependency introduction.

## Validation

- `uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block`
  - exits 0; `quality_gate_status: warn`
- `uv run fund-analysis checklist 004393 --report-year 2024 --thermometer-cache-dir /tmp/fund-agent-release-acceptance/thermometer`
  - exits 0; `overall_signal: yellow`
- `uv run fund-analysis thermometer --cache-dir /tmp/fund-agent-release-acceptance/thermometer --json`
  - exits 0; `index_code: wind_all_a`
- `uv run pytest`
  - `697 passed`
- `uv run ruff check .`
  - passed
- `git diff --check`
  - passed

## Notes

- `reports/quality-gate-runs/` and `cache/` are ignored runtime outputs.
- Report-quality validator integration, durable baselines, Host/Agent/dayu runtime, FOF taxonomy, and nav_data mapping remain future explicit gates.
```

## Next Gate

Next gate requires user authorization:

- push `codex/v0-release-readiness-plan`
- open a draft PR against `main`

Until that authorization is given, do not push, create PRs, close PRs, or mutate GitHub state.
