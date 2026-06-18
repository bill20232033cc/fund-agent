# 004393 / 2025 Fixture Promotion / Strict Golden Coverage Evidence

Date: 2026-06-13

Gate: `004393 / 2025 Fixture Promotion / Strict Golden Coverage Evidence Gate`

Role: evidence worker only

Status: `EVIDENCE_READY_FOR_REVIEW`

Accepted plan:

- `docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-planning-20260613.md`

Controller judgment:

- `docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-plan-controller-judgment-20260613.md`

## 1. Scope

Allowed write:

- `docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-20260613.md`

This evidence gate does not edit source, tests, runtime behavior, README,
design/control docs, golden-answer files, fixture files, promotion-state files,
or release/readiness state.

This evidence gate does not run live EID, network, PDF, FDR, provider, LLM,
analyze, checklist, readiness, release or PR commands.

Release/readiness remains `NOT_READY`.

## 2. Boundary Snapshot

Command:

```bash
git status --branch --short
```

Observed output:

```text
## feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 14]
?? docs/audit/
?? docs/learning-roadmap.md
?? docs/next-development-phaseflow.md
?? docs/reviews/audit-disposition-phaseflow-reconciliation-controller-judgment-20260610.md
?? docs/reviews/mvp-dayu-host-runtime-governance-adapter-implementation-preflight-20260601.md
?? docs/reviews/mvp-post-eid-artifact-disposition-controller-judgment-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-inventory-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-review-ds-20260609.md
?? docs/reviews/mvp-post-eid-artifact-disposition-startup-judgment-20260609.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-controller-judgment-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-live-evidence-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-ds-20260606.md
?? docs/reviews/mvp-post-operator-provider-availability-evidence-gate-plan-review-mimo-20260606.md
?? docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-evidence-20260608.md
?? docs/reviews/mvp-real-llm-chapter-acceptance-live-evidence-gate-mimo-review-20260608.md
?? docs/reviews/mvp-small-golden-set-matched-source-retained-excerpt-fixture-planning-prep-gate-plan-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-ds-20260609.md
?? docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-mimo-20260609.md
?? docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md
?? docs/reviews/plan-review-20260609-071706.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/reviews/repo-review-20260527-215953.md
?? docs/reviews/repo-review-20260527-225303.md
?? docs/reviews/repo-review-20260609-130307.md
?? docs/reviews/repo-review-20260609-165959.md
?? docs/reviews/repo-review-20260611-231358.md
?? docs/reviews/workspace-ownership-reconciliation-20260531.md
?? docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md
?? docs/tmux-agent-memory-store.md
?? reports/live-evidence/
?? reports/manual-llm-smoke/
?? reviews/
?? scripts/claude_mimo_simple.py
?? "\345\237\272\351\207\221\345\271\264\346\212\245/"
?? "\345\256\232\346\200\247\345\210\206\346\236\220\346\250\241\346\235\277.md"
```

Disposition:

- branch is the expected work branch;
- existing untracked residue is workspace state only and is not used as proof;
- this gate adds only the evidence artifact listed in §1.

## 3. Validation Commands

### V0 - Diff Whitespace Check Before Evidence Write

Command:

```bash
git diff --check
```

Observed output:

```text
<no output>
```

Disposition: `PASS`

### V1 - Strict Golden Content Identity

Command:

```bash
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_answer import load_golden_answer_json; funds=load_golden_answer_json(Path('reports/golden-answers/golden-answer.json')); target=[f for f in funds if f.fund_code=='004393' and f.report_year==2025]; assert len(target)==1; assert len(target[0].records)==7; assert target[0].skipped_fields==(); keys={(r.field_name,r.sub_field) for r in target[0].records}; assert keys=={('basic_identity','fund_name'),('basic_identity','fund_code'),('basic_identity','management_company'),('basic_identity','custodian'),('basic_identity','inception_date'),('product_profile','investment_objective'),('benchmark','benchmark_name')}; assert all(r.report_year==2025 for r in target[0].records); print('strict_golden_004393_2025_content_ok')"
```

Observed output:

```text
strict_golden_004393_2025_content_ok
```

Disposition: `PASS`

Evidence conclusion:

- tracked strict golden JSON contains exactly one `004393 / 2025` entry;
- that entry contains exactly seven active rows;
- skipped rows are empty;
- the seven rows are exactly:
  `basic_identity.fund_name`,
  `basic_identity.fund_code`,
  `basic_identity.management_company`,
  `basic_identity.custodian`,
  `basic_identity.inception_date`,
  `product_profile.investment_objective`,
  `benchmark.benchmark_name`;
- fee rows, `turnover_rate`, skipped rows and deferred rows are not accepted by
  this evidence as tracked `004393 / 2025` golden content.

### V2 - Strict Golden Coverage Is Year-aware

Command:

```bash
uv run python -c "from pathlib import Path; from fund_agent.fund.golden_readiness_preflight import _load_strict_golden_coverage; cov=_load_strict_golden_coverage(Path('reports/golden-answers/golden-answer.json')); assert cov is not None; assert '004393' in cov.fund_codes; assert ('004393',2025) in cov.fund_years; assert ('004393',2024) in cov.fund_years; assert ('004393',2026) not in cov.fund_years; print('strict_golden_coverage_year_aware_ok fund_years=%s' % sorted(x for x in cov.fund_years if x[0]=='004393'))"
```

Observed output:

```text
strict_golden_coverage_year_aware_ok fund_years=[('004393', 2024), ('004393', 2025)]
```

Disposition: `PASS`

Evidence conclusion:

- strict golden coverage loader records `004393 / 2024` and `004393 / 2025`
  as distinct `(fund_code, report_year)` entries;
- `004393 / 2026` is absent;
- this is coverage-loader evidence only, not release/readiness proof.

### V3 - Fixture Promotion Parser Is Fund-code-only

Command:

```bash
uv run python -c "import json, tempfile; from pathlib import Path; from fund_agent.fund.golden_readiness_preflight import _load_fixture_promotion_states; d=Path(tempfile.mkdtemp()); p=d/'fixture-promotion-collision.json'; p.write_text(json.dumps({'entries':[{'fund_code':'004393','report_year':2024,'promotion_state':'not_promoted'},{'fund_code':'004393','report_year':2025,'promotion_state':'promoted_fixture'}]}, ensure_ascii=False), encoding='utf-8'); states=_load_fixture_promotion_states(p); assert states=={'004393':'promoted_fixture'}; assert len(states)==1; print('fixture_promotion_fund_code_only_confirmed states=%s' % states)"
```

Observed output:

```text
fixture_promotion_fund_code_only_confirmed states={'004393': 'promoted_fixture'}
```

Disposition: `PASS`

Evidence conclusion:

- fixture promotion loader collapses multiple yearly rows for the same fund code
  into one `004393` key;
- `report_year` is not part of the promotion-state identity;
- the observed value is last-write-wins for this collision order;
- under the current parser, a `promoted_fixture` state for `004393` is unsafe
  as proof that `004393 / 2025` specifically is promoted.

### V4 - Targeted Golden Tests

Command:

```bash
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py -q
```

Observed output:

```text
34 passed in 0.62s
```

Disposition: `PASS`

Evidence conclusion:

- existing golden-answer and golden-readiness preflight tests pass under the
  current local state;
- this does not run release/readiness/analyze/checklist commands and does not
  promote fixtures.

## 4. Finding Table

| Finding | Disposition | Evidence |
|---|---|---|
| `004393 / 2025` strict golden content exists with seven accepted rows and no skipped rows. | `ACCEPT` | V1 |
| Strict golden coverage is year-aware for `004393 / 2024` and `004393 / 2025`. | `ACCEPT` | V2 |
| Strict golden coverage does not include non-existent `004393 / 2026`. | `ACCEPT` | V2 |
| Fixture promotion identity is fund-code-only, not year-aware. | `ACCEPT_AS_RESIDUAL` | V3 |
| Fund-code-only fixture promotion cannot prove `004393 / 2025`-specific promotion. | `ACCEPT_AS_BLOCKING_FOR_PROMOTION_CLAIM_ONLY` | V3 |
| Current evidence supports a strict golden coverage closeout without code changes. | `ACCEPT_FOR_REVIEW` | V1, V2, V4 |
| Current evidence does not support release/readiness. | `ACCEPT_NOT_READY` | Gate boundary, V1-V4 |

## 5. Residuals And Routing

| Residual | Current impact | Recommended destination |
|---|---|---|
| Fixture promotion parser is fund-code-only. | Blocks any claim that promotion state is year-specific for `004393 / 2025`; does not invalidate strict golden row coverage. | Narrow `Fixture Promotion State Year-aware Schema / Parser Planning Gate` only if controller requires year-specific promotion state before downstream readiness. |
| Historical untracked residue is still present. | Not used as proof in this gate. | Existing artifact disposition / release-readiness residual routing. |
| Release/readiness remains `NOT_READY`. | No release/PR claim is accepted. | Future readiness rollup after accepted coverage/promotion disposition. |

## 6. Controller Recommendation

Recommended controller disposition:

```text
ACCEPT_WITH_RESIDUALS_NOT_READY
```

Recommended accepted facts:

- `004393 / 2025` strict golden content is present with exactly seven accepted
  rows and no skipped rows;
- strict golden coverage is year-aware for the current tracked JSON surface;
- no strict golden coverage implementation gate is needed on the evidence
  currently collected;
- fixture promotion remains fund-code-only and cannot be used as
  `004393 / 2025`-specific promotion proof;
- release/readiness remains `NOT_READY`.

Recommended next entry:

```text
Fixture Promotion State Year-aware Schema / Parser Planning Gate
```

This next entry should be opened only as a planning gate. It should not promote
fixtures, edit golden-answer content, run live/provider/LLM/readiness/release
commands, or claim release readiness.

## 7. Boundary Confirmation

This evidence gate did not perform or authorize:

- source, test or runtime behavior changes;
- golden-answer, fixture or promotion-state content edits;
- fixture promotion;
- live EID, network, PDF, FDR, provider, LLM, analyze, checklist, readiness,
  release or PR commands;
- cleanup, deletion, archive, push, merge or external-state actions.
