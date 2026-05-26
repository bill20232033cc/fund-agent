# Fund-layer CHAPTER_CONTRACT Sidecar + Dev-only Report-writing Audit Implementation Evidence

> Date: 2026-05-26
> Role: AgentCodex implementation worker
> Gate: Fund-layer executable CHAPTER_CONTRACT sidecar + dev-only report-writing audit implementation gate
> Verdict: IMPLEMENTATION_READY

## Scope

Allowed write scope used:

- `fund_agent/fund/template/chapter_contract_constraints.py`
- `fund_agent/fund/report_writing_audit.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/test_report_writing_audit.py`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-evidence-20260526.md`

No README, `docs/design.md`, `docs/implementation-control.md`, renderer, Service, CLI, FQ0-FQ6, quality gate, extraction score, document/PDF/source helper, Host/Agent/dayu, pyproject, or script file was modified.

Pre-existing untracked plan/review artifacts remain unmodified:

- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-20260526.md`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-controller-judgment-20260526.md`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-review-glm-20260526.md`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-plan-review-mimo-20260526.md`

## Implementation Summary

- Added a frozen/slotted CHAPTER_CONTRACT sidecar over the existing `ChapterContract` manifest. Default constraints copy `must_answer` and `must_not_cover` from the current manifest, preserving it as the single truth.
- Added explicit `RequirementSeverity`, `RequirementStatus`, and `FailureCategory` domains. `config_only` sidecar severity maps to informational audit issue severity.
- Added active-fund Chapter 3 material requirement for turnover/style-change evidence. Missing evidence prevents style stability / consistency / 言行一致 positive claims unless a compatible data gap and required insufficiency wording are present.
- Added Chapter 2 enhanced-index and Chapter 6 bond deferred config-only requirements.
- Added dev-only `report_writing_audit` over `ReportEvidenceBundle`, caller-supplied parsed records, and `ChapterDraftSurrogate`.
- Claim detection uses explicit `claim_tags` first, then deterministic Chinese phrase matching with a small negative-context guard.
- `bundle.fund_type_slot is None` resolves to `default`; explicit chapter draft fund type can still select active-fund constraints.

## Validation Commands

### Focused Tests

Command:

```bash
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Outcome:

```text
collected 13 items
tests/fund/template/test_chapter_contract_constraints.py ....            [ 30%]
tests/fund/test_report_writing_audit.py .........                        [100%]
13 passed in 0.62s
```

### Adjacent Tests

Command:

```bash
uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
```

Outcome:

```text
collected 147 items
tests/fund/template/test_chapter_contract_constraints.py ....            [  2%]
tests/fund/template/test_contracts.py ..........                         [  9%]
tests/fund/template/test_item_rules.py ...............                   [ 19%]
tests/fund/template/test_lens_application.py ...........                 [ 27%]
tests/fund/template/test_renderer.py ................................... [ 51%]
.....................                                                    [ 65%]
tests/fund/test_report_evidence.py .......................               [ 80%]
tests/fund/test_report_quality_validation.py ........................... [ 99%]
.                                                                        [100%]
147 passed in 0.49s
```

### Ruff

Command:

```bash
uv run ruff check fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Outcome:

```text
All checks passed!
```

### Whitespace

Command:

```bash
git diff --check
```

Outcome: no output, exit 0.

### Boundary Diff

Command:

```bash
git diff --name-only
git diff -- fund_agent/fund/template/renderer.py fund_agent/services fund_agent/ui fund_agent/fund/quality_gate.py fund_agent/fund/quality_gate_integration.py fund_agent/fund/extraction_score.py fund_agent/fund/documents fund_agent/fund/pdf fund_agent/host fund_agent/agent pyproject.toml README.md fund_agent/README.md fund_agent/fund/README.md docs/design.md docs/implementation-control.md
```

Outcome: both commands produced no output. Note: new files are untracked, so `git diff --name-only` is empty; `git status --short` shows only allowed new implementation files plus the pre-existing plan/review artifacts listed above.

### Boundary Rg

Command:

```bash
rg -n "dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source adapter|quality_gate|quality_gate_policy|FQ0|FQ6|renderer|FundAnalysisService" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Outcome: no output, exit 1, meaning no matches.

Additional targeted boundary rg:

```bash
rg -n "FundDocumentRepository|AnnualReportDocumentCache|quality_gate_policy|dayu\\.host|dayu\\.engine|FundAnalysisService" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Outcome: no output, exit 1, meaning no matches.

## Coverage Note

Attempted extra measurement:

```bash
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py --cov=fund_agent.fund.template.chapter_contract_constraints --cov=fund_agent.fund.report_writing_audit --cov-report=term-missing
```

Outcome: failed during test collection with existing dependency import error:

```text
ImportError: cannot load module more than once per process
ImportError: Unable to import required dependency numpy.
```

This was an extra coverage probe, not one of the required acceptance commands. Focused tests, adjacent tests, ruff, whitespace, and boundary checks all passed. Per-file coverage could not be measured locally in this pass; focused tests cover the new material branches required by the plan.

## Boundary Statement

The implementation did not call document repositories, PDF/cache/source helpers, downloaders, production extractors, renderer, Service/CLI product flow, FQ0-FQ6 quality gate, Host/Agent packages, or dayu runtime. No GitHub mutation, `git add`, commit, push, or PR operation was performed.

## Code Review Fix Pass

> Date: 2026-05-26
> Role: implementation/fix worker
> Verdict: IMPLEMENTATION_FIX_READY

### Accepted Review Fixes

- Compatible active-fund Chapter 3 `data_gap` now requires explicit insufficient-evidence wording and next minimum validation question even when the draft avoids a positive stability claim.
- Positive stability / style-consistency / 言行一致 claims with only a compatible `data_gap` now emit an additional `unsupported_stability_claim` issue.
- Reviewed facts satisfy the Chapter 3 requirement only when `source_anchor_ids` is non-empty and every declared anchor id resolves in `bundle.evidence_anchors`.
- `audit_report_writing_records()` now returns blocking `invalid_audit_input` with `failed_closed=True` for malformed `report_year` instead of raising.
- Conflicting explicit Chapter 3 `fund_type_slot` values now emit blocking `input_conflict` and `failed_closed=True`.
- Records-mode `data_gap` compatibility no longer defaults missing `reason_code`, `field_path`, or `required_report_wording`; incomplete records fail closed.

### Fix Validation Commands

Focused tests:

```bash
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Outcome:

```text
collected 18 items
tests/fund/template/test_chapter_contract_constraints.py ....            [ 22%]
tests/fund/test_report_writing_audit.py ..............                   [100%]
18 passed in 0.37s
```

Adjacent tests:

```bash
uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
```

Outcome:

```text
collected 147 items
tests/fund/template/test_chapter_contract_constraints.py ....            [  2%]
tests/fund/template/test_contracts.py ..........                         [  9%]
tests/fund/template/test_item_rules.py ...............                   [ 19%]
tests/fund/template/test_lens_application.py ...........                 [ 27%]
tests/fund/template/test_renderer.py ................................... [ 51%]
.....................                                                    [ 65%]
tests/fund/test_report_evidence.py .......................               [ 80%]
tests/fund/test_report_quality_validation.py ........................... [ 99%]
.                                                                        [100%]
147 passed in 0.60s
```

Ruff:

```bash
uv run ruff check fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Outcome:

```text
All checks passed!
```

Untracked whitespace checks:

```bash
git diff --no-index --check /dev/null fund_agent/fund/template/chapter_contract_constraints.py
git diff --no-index --check /dev/null fund_agent/fund/report_writing_audit.py
git diff --no-index --check /dev/null tests/fund/template/test_chapter_contract_constraints.py
git diff --no-index --check /dev/null tests/fund/test_report_writing_audit.py
```

Outcome: no whitespace warnings printed. Exit code `1` is expected for `--no-index` because each new file differs from `/dev/null`.

Boundary rg:

```bash
rg -n "quality_gate_policy|quality_gate|dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source helper|source adapter|pdf|cache|extractor|renderer|FundAnalysisService|extra_payload|FQ0|FQ6" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Outcome: no output, exit 1, meaning no matches.

### Residual Risk

- Duplicate `issue_id` occurrence-level uniqueness remains deferred per controller裁决; current ids are deterministic class ids and the fix did not expand scope to draft ordinals.
- Coverage measurement remains subject to the earlier local numpy import/coverage collection issue; focused and adjacent acceptance tests passed.

## Code Review Fix Pass 2

> Date: 2026-05-26
> Role: implementation/fix worker
> Verdict: IMPLEMENTATION_FIX2_READY

### Accepted Re-review Fix

- `_find_satisfying_fact()` now requires `source_anchor_ids` to be non-empty and every declared anchor id to resolve in `bundle.evidence_anchors` before a fact can satisfy `required_evidence`.
- Added a focused regression test where one fact declares both `anchor:turnover` and dangling `anchor:missing`; the requirement remains unsatisfied and emits `required_evidence_missing`.
- The existing valid minimal case with only `anchor:turnover` continues to pass.

### Fix2 Validation Commands

Focused tests:

```bash
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Outcome:

```text
collected 19 items
tests/fund/template/test_chapter_contract_constraints.py ....            [ 21%]
tests/fund/test_report_writing_audit.py ...............                  [100%]
19 passed in 0.38s
```

Adjacent tests:

```bash
uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
```

Outcome:

```text
collected 147 items
147 passed in 0.48s
```

Ruff:

```bash
uv run ruff check fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Outcome:

```text
All checks passed!
```

Boundary rg:

```bash
rg -n "FundDocumentRepository|PDF|pdf|cache|source helper|downloader|extractor|renderer|quality_gate|quality gate|FQ[0-6]|FundAnalysisService|fund-analysis analyze|fund-analysis checklist|dayu\\.host|dayu\\.engine|extra_payload|Host|Agent" fund_agent/fund/report_writing_audit.py fund_agent/fund/template/chapter_contract_constraints.py tests/fund/test_report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py
```

Outcome: only module docstring boundary wording matched `Agent`; no forbidden imports, calls, renderer, quality gate, repository, source/PDF/cache/extractor, Service/CLI, Host/dayu runtime, or `extra_payload` usage matched.
