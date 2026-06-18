# 004393 / 2025 Fixture Promotion State / Strict Golden Coverage Evidence Planning

Date: 2026-06-13

Gate: `004393 / 2025 Fixture Promotion State / Strict Golden Coverage Evidence Planning Gate`

Role: planning worker only

Verdict: `PLAN_READY_FOR_CONTROLLER_REVIEW`

## 1. Scope

This artifact is the code-generation-ready plan for the next bounded evidence step after accepted checkpoint `1ce301b`.

Allowed write in this gate:

- `docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-planning-20260613.md`

Not authorized in this gate:

- source, test, runtime, README, design, control doc, pyproject, root README or `.gitignore` edits;
- golden answer, fixture, promotion state, fixture promotion, readiness, release, PR or external-state edits;
- live/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release commands;
- staging, committing, pushing, deleting, moving, archiving or cleanup;
- treating untracked workspace residue as proof.

## 2. Accepted Facts After `1ce301b`

| Fact | Status |
|---|---|
| Seven `004393 / 2025` rows are now tracked golden content through the reviewed Markdown and generated JSON path. | `ACCEPTED` |
| The accepted rows are `basic_identity.fund_name`, `basic_identity.fund_code`, `basic_identity.management_company`, `basic_identity.custodian`, `basic_identity.inception_date`, `product_profile.investment_objective`, and `benchmark.benchmark_name`. | `ACCEPTED` |
| `fee_schedule.management_fee`, `fee_schedule.custody_fee`, `turnover_rate`, skipped rows and deferred rows are excluded from the `004393 / 2025` tracked golden write. | `ACCEPTED` |
| `reports/golden-answers/golden-answer.json` and `reports/golden-answers/golden-answer-prefill-reviewed.md` are the tracked golden content surfaces to inspect. | `ACCEPTED` |
| Source-body verification used parsed cache and EID single-source/no-fallback metadata; it is not fresh-fetch proof. | `ACCEPTED_RESIDUAL` |
| Fixture promotion is unresolved. | `ACCEPTED_RESIDUAL` |
| Strict golden coverage/readiness evidence after the write is unresolved. | `ACCEPTED_RESIDUAL` |
| Release/readiness remains `NOT_READY`. | `ACCEPTED_RESIDUAL_NOT_READY` |

## 3. Problem Statement

The current risk is identity mismatch between two related surfaces:

1. strict golden correctness is supposed to be year-aware, using `fund_code + report_year + field_name + sub_field`;
2. current fixture promotion state may still be fund-code-only, so a promoted state for `004393` may not prove that only `004393 / 2025` is promoted and may be confused with `004393 / 2024`.

The next gate must collect exact local evidence for both surfaces before any implementation or promotion decision.

Required direct evidence:

- whether current tracked strict golden JSON and reviewed Markdown both contain distinct `004393 / 2024` and `004393 / 2025` entries;
- whether `004393 / 2025` has exactly the seven accepted rows and zero skipped rows;
- whether strict golden coverage loader/default semantics include `(004393, 2025)`;
- whether readiness preflight strict golden coverage derives `covered` by `fund_code + report_year`, not by fund code alone;
- whether fixture promotion state parsing is fund-code-only, and whether any tracked historical fixture-promotion manifest is runtime-consumable for year-specific promotion;
- whether coverage evidence can stop at strict golden rows and defer fixture promotion, or whether controller requires a narrow schema/parser plan for year-specific fixture promotion state.

## 4. Hypotheses To Distinguish

| Hypothesis | Evidence needed | Decision impact |
|---|---|---|
| H1: strict golden JSON now covers `004393 / 2025` under loader/default semantics. | `load_golden_answer_json()` and `_load_strict_golden_coverage()` show `(004393, 2025)` present with seven records. | If true, strict golden coverage evidence can pass for the tracked rows. |
| H2: readiness preflight strict golden coverage can identify `004393 / 2025` by `fund_code + report_year`. | Targeted code/test evidence shows `_derive_strict_golden_coverage()` checks `(artifact.fund_code, artifact.report_year)` and tests cover matching-year and year-miss cases. | If true, no strict-coverage implementation gate is needed before evidence. |
| H3: fixture promotion state parser is still fund-code-only and cannot prove year-specific promotion. | `_load_fixture_promotion_states()` returns `dict[fund_code, PromotionState]`; `_derive_fixture_promotion_state()` calls `fixture_states.get(artifact.fund_code)` without report year. | If true, do not treat any `004393` promoted state as `004393 / 2025`-specific. |
| H4: current state may be sufficient to defer fixture promotion if coverage evidence only needs strict golden rows. | Evidence gate records strict coverage pass plus fixture promotion unresolved/year-blind residual. | If controller accepts, next entry can be readiness residual routing, not implementation. |
| H5: current state may require a narrow schema/parser plan if fixture promotion must become year-specific. | Controller determines that fixture promotion state is required for the same acceptance unit as strict golden coverage. | Open a narrow implementation planning gate; do not implement directly from this plan. |

## 5. Next Evidence Gate

Recommended next entry:

```text
004393 / 2025 Fixture Promotion State / Strict Golden Coverage Evidence Gate
```

Classification: `standard`, non-live, local-only, evidence-only.

Allowed future evidence gate write set:

- `docs/reviews/mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-20260613.md`

No separate review/controller/control write is included in the worker write set unless the controller explicitly runs that later process. If the evidence gate finds that implementation is needed, it must stop after the evidence artifact and recommend a separate implementation planning gate.

## 6. Read-only Evidence Matrix

All commands below are local-only. They do not run live/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release commands and must not write artifacts other than the single evidence artifact.

### E0 - Boundary Snapshot

Command:

```bash
git branch --show-current
git status --short
git diff --name-only
```

Expected assertions:

- branch is `feat/mvp-llm-incomplete-run-artifacts`;
- only the evidence artifact is written by the next evidence worker;
- untracked residue is listed only as workspace state, not proof.

### E1 - Golden JSON / Markdown Identity

Command:

```bash
uv run python -c 'from pathlib import Path; from fund_agent.fund.golden_answer import load_golden_answer_json, parse_golden_answer_markdown; jp=Path("reports/golden-answers/golden-answer.json"); mp=Path("reports/golden-answers/golden-answer-prefill-reviewed.md"); jf=load_golden_answer_json(jp); mf=parse_golden_answer_markdown(mp.read_text(encoding="utf-8")); excluded={("fee_schedule","management_fee"),("fee_schedule","custody_fee"),("turnover_rate","turnover_rate")}; expected={("basic_identity","fund_name"),("basic_identity","fund_code"),("basic_identity","management_company"),("basic_identity","custodian"),("basic_identity","inception_date"),("product_profile","investment_objective"),("benchmark","benchmark_name")}; exec("for label,funds in ((\"json\",jf),(\"md\",mf)):\n    by_key={(f.fund_code,f.report_year): f for f in funds}\n    assert (\"004393\",2024) in by_key, label\n    assert (\"004393\",2025) in by_key, label\n    f=by_key[(\"004393\",2025)]\n    keys={(r.field_name,r.sub_field) for r in f.records}\n    assert keys==expected, (label, keys)\n    assert len(f.records)==7, (label, len(f.records))\n    assert len(f.skipped_fields)==0, (label, f.skipped_fields)\n    assert not (keys & excluded), (label, keys & excluded)\n    print(label, \"004393/2024_records\", len(by_key[(\"004393\",2024)].records), \"004393/2025_records\", len(f.records), \"004393/2025_skipped\", len(f.skipped_fields))")'
```

Expected assertions:

- JSON and Markdown both contain `004393 / 2024` and `004393 / 2025`;
- `004393 / 2025` has exactly seven records and zero skipped fields;
- excluded fee rows, `turnover_rate`, skipped rows and deferred rows are absent;
- `004393 / 2024` remains distinct and is not reused as 2025 truth.

### E2 - Strict Golden Loader Coverage

Command:

```bash
uv run python -c 'from pathlib import Path; from fund_agent.fund.golden_readiness_preflight import _load_strict_golden_coverage; cov=_load_strict_golden_coverage(Path("reports/golden-answers/golden-answer.json")); assert cov is not None; assert ("004393",2025) in cov.fund_years; assert ("004393",2024) in cov.fund_years; print("strict_coverage", "004393/2024", ("004393",2024) in cov.fund_years, "004393/2025", ("004393",2025) in cov.fund_years, "funds", len(cov.fund_codes), "fund_years", len(cov.fund_years))'
```

Expected assertions:

- strict coverage includes both `(004393, 2024)` and `(004393, 2025)`;
- evidence cites this only as loader/default coverage, not readiness or fixture promotion proof.

### E3 - Preflight Year-aware Strict Coverage Code And Tests

Commands:

```bash
rg -n "_derive_strict_golden_coverage|fund_years|strict_golden_year_not_covered|artifact.report_year" fund_agent/fund/golden_readiness_preflight.py
rg -n "test_preflight_blocks_strict_golden_absence_and_fund_miss|test_preflight_accepts_strict_golden_matching_year" tests/fund/test_golden_readiness_preflight.py
uv run pytest tests/fund/test_golden_readiness_preflight.py::test_preflight_blocks_strict_golden_absence_and_fund_miss tests/fund/test_golden_readiness_preflight.py::test_preflight_accepts_strict_golden_matching_year_and_reserves_partial_code -q
```

Expected assertions:

- `_derive_strict_golden_coverage()` checks `(artifact.fund_code, artifact.report_year)` against `golden_coverage.fund_years`;
- year-miss emits `strict_golden_year_not_covered`;
- matching-year coverage emits `covered`;
- targeted tests pass without running runtime readiness/release/analyze/checklist commands.

### E4 - Fixture Promotion Parser Identity

Commands:

```bash
rg -n "def _load_fixture_promotion_states|def _derive_fixture_promotion_state|states\\[fund_code\\]|fixture_states.get\\(artifact.fund_code\\)|report_year" fund_agent/fund/golden_readiness_preflight.py
uv run python -c 'from pathlib import Path; source=Path("fund_agent/fund/golden_readiness_preflight.py").read_text(encoding="utf-8"); load=source[source.index("def _load_fixture_promotion_states"):source.index("def _build_readiness_row")]; derive=source[source.index("def _derive_fixture_promotion_state"):source.index("def _derive_coverage_disposition_blockers")]; assert "report_year" not in load; assert "fixture_states.get(artifact.fund_code)" in derive; assert "artifact.report_year" not in derive; print("fixture_parser_identity=fund_code_only")'
```

Expected assertions:

- parser maps promotion state by `fund_code` only;
- `_derive_fixture_promotion_state()` does not use `report_year`;
- any future `promoted_fixture` for `004393` under current parser cannot be claimed as `004393 / 2025`-specific.

### E5 - Historical Manifest Runtime-consumability

Command:

```bash
uv run python -c 'from pathlib import Path; from fund_agent.fund.golden_readiness_preflight import _load_fixture_promotion_states; path=Path("docs/reviews/fixture-promotion-state-manifest-20260529.json"); exec("try:\n    states=_load_fixture_promotion_states(path)\nexcept Exception as exc:\n    print(\"historical_fixture_manifest_runtime_consumable=false\", type(exc).__name__, str(exc))\nelse:\n    print(\"historical_fixture_manifest_runtime_consumable=true\", \"004393_state\", states.get(\"004393\"), \"key_shape=fund_code_only\")")'
```

Expected assertions:

- either the historical manifest is not runtime-consumable by the current loader, or it loads into a fund-code-only map;
- in both cases it is not year-specific promotion proof for `004393 / 2025`;
- this historical manifest remains control-plane evidence only unless a later gate explicitly accepts a runtime-consumable manifest.

## 7. Evidence Gate Stop Conditions

The evidence worker must stop and record `BLOCKED_FOR_CONTROLLER` if any of the following occurs:

- `004393 / 2025` is absent from either tracked JSON or reviewed Markdown;
- JSON and Markdown disagree on `004393 / 2025` row count, skipped count or field/sub_field identities;
- any excluded row appears in `004393 / 2025`;
- strict coverage does not include `(004393, 2025)`;
- targeted preflight tests fail;
- fixture promotion parser unexpectedly appears year-aware, making this plan stale;
- validating fixture promotion would require running readiness/release/analyze/checklist or writing promotion artifacts;
- any command would require live/network/PDF/FDR/provider/LLM access.

## 8. Conditional Implementation Gate

Open this only if the evidence gate proves strict golden coverage is year-aware and present, but controller still requires fixture promotion to express year-specific state before downstream acceptance.

Recommended gate name:

```text
Fixture Promotion State Year-aware Schema / Parser Implementation Planning Gate
```

Narrowest allowed future implementation planning write:

- one plan artifact under `docs/reviews/`.

Narrowest possible later implementation write set, if that separate plan is accepted:

- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py`
- optionally one new fixture/promotion-state manifest sample under `tests/fixtures/` only if existing in-memory tests cannot express the contract
- optionally `tests/README.md` only if test-running or fixture conventions change

Explicit non-goals for that later implementation:

- no golden answer row edits;
- no fixture promotion;
- no production fixture write;
- no readiness/release claim;
- no live/network/PDF/FDR/provider/LLM/analyze/checklist command;
- no `docs/design.md`, control doc, README, pyproject, root README or `.gitignore` edits unless a separate controller sync gate authorizes them.

Expected implementation shape if needed:

- introduce a year-aware fixture promotion identity keyed by `(fund_code, report_year)`;
- preserve legacy fund-code-only manifests only as non-year-specific legacy input, not as year-specific proof;
- fail closed if a manifest mixes ambiguous fund-code-only promotion with a year-specific claim for the same fund;
- add regression tests for same fund `004393` with 2024 and 2025 states diverging.

## 9. Reviewer Checklist

Reviewer must verify:

- the plan does not authorize fixture promotion or golden edits;
- strict golden identity remains `fund_code + report_year + field_name + sub_field`;
- E1 proves JSON and Markdown agree on the seven `004393 / 2025` rows;
- E2/E3 prove strict coverage is year-aware at loader and preflight levels;
- E4/E5 do not overclaim fixture promotion readiness;
- untracked residue is not used as proof;
- release/readiness remains `NOT_READY`;
- future implementation write set is limited to parser/schema tests and only opens after controller decision.

## 10. Controller Acceptance Criteria

Controller may accept the next evidence gate if:

- the evidence artifact contains exact command output for E0-E5;
- all expected assertions pass or failures are classified with stop-condition routing;
- `004393 / 2025` strict golden coverage is classified separately from fixture promotion;
- fixture promotion is either explicitly deferred as not required for strict row coverage, or routed to a separate narrow schema/parser planning gate;
- no command violates no-live/no-readiness/no-release/no-promotion boundaries;
- no readiness/release/PR claim is made.

Recommended next entry:

```text
004393 / 2025 Fixture Promotion State / Strict Golden Coverage Evidence Gate
```

This is preferred over an immediate implementation planning gate because current code inspection already suggests strict golden coverage is year-aware while fixture promotion is year-blind; the remaining decision depends on evidence and controller scope, not on code changes first.
