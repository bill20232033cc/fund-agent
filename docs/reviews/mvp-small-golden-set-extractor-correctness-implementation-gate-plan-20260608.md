# MVP Small Golden Set / Extractor Correctness Implementation Gate Plan

## 1. Gate Identity

Current gate: `small golden set extractor correctness implementation gate`.

Gate classification: `standard`.

Reason: this gate may add offline review artifacts, focused local fixtures, focused extractor correctness tests and narrowly scoped extractor fixes proven by those tests. It must not change golden/readiness/quality gate promotion semantics, provider/default/runtime/budget/config, live LLM behavior, Agent runtime scope, multi-year runtime or score-loop semantics. If implementation attempts to promote small-set rows into production golden/readiness, change FQ0-FQ6 semantics or change correctness oracle identity, the gate must stop and be reclassified as `heavy`.

Accepted planning baseline:

- Draft PR #22 review/fix/re-review gate is accepted at checkpoint `2b1c804`.
- Small golden set fixture/evidence planning gate is accepted at checkpoint `4ebaf0b`.
- Accepted planning artifact: `docs/reviews/mvp-small-golden-set-extractor-correctness-planning-gate-plan-20260608.md`.
- Accepted five rows: `004393`, `110020`, `004194`, `006597`, `017641`, all with `report_year=2024` and `promotion_allowed=false`.
- Slice E first no-live Agent body-chapter mechanics remains current code fact.
- Full production Agent tool-loop/retry/budget/ToolRegistry/live runtime expansion, durable Host features, live acceptance, multi-year runtime, score-loop, golden/readiness promotion and provider/default/runtime change remain future scope.

## 2. Gate Objective

Implement the accepted small-set extractor correctness loop in the smallest offline form that can expose extractor correctness failures:

1. create a review-owned five-row manifest with source identity and field expectation status;
2. create minimal offline extractor fixtures only after source/retention safety is recorded;
3. add focused pytest coverage that consumes local fixtures/fakes only;
4. fix extractor bugs only when a same-source fixture test proves the root cause;
5. close with implementation evidence, two independent reviews and controller judgment.

## 3. Non-Goals

- No live LLM, retry, endpoint/DNS/curl/socket/PASS-only probe or fallback invocation.
- No provider/default/runtime/budget/config change.
- No Chapter calibration, Agent runtime expansion, multi-year runtime, score-loop, release, merge, mark-ready or PR external-state action.
- No production `reports/golden-answers/` change.
- No golden/readiness preflight promotion, fixture promotion manifest update or `promotion_allowed=true`.
- No FQ0-FQ6 threshold, score schema, correctness oracle identity or final judgment semantic change.
- No direct production PDF/cache/source-helper access outside the existing `FundDocumentRepository` boundary.
- No ordinary pytest requiring network, PDF download, provider, akshare, EID or existing local cache state.
- No handling unrelated dirty or untracked files.

## 4. Implementation Slices

### Slice A: Small-set manifest and schema guard

Allowed files:

- `docs/reviews/mvp-small-golden-set-manifest-20260608.json`
- `tests/fund/test_small_golden_set_manifest.py`
- optional test-only helper under `tests/fund/` if needed

Required manifest shape:

```json
{
  "schema_version": "fund-agent.small_golden_set_manifest.v1",
  "promotion_allowed_default": false,
  "ordinary_pytest_network_allowed": false,
  "fallback_invocation_allowed": false,
  "rows": [
    {
      "fund_code": "004393",
      "report_year": 2024,
      "slot": "active_equity_or_mixed",
      "expected_fund_type": "active_fund",
      "promotion_allowed": false,
      "source_document_identity": {
        "source_kind": "annual_report",
        "identity_status": "pending_offline_fixture",
        "fallback_used": false,
        "fallback_invocation": "prohibited"
      },
      "field_expectations": {
        "identity": "expected",
        "source_document": "expected",
        "benchmark": "expected",
        "manager": "expected",
        "scale": "expected",
        "fee": "expected",
        "return": "expected",
        "holdings": "expected",
        "risk": "expected"
      }
    }
  ]
}
```

Manifest acceptance:

- exactly five rows;
- exact fund-code set equals `004393`, `110020`, `004194`, `006597`, `017641`;
- every row has `report_year=2024`;
- every row and global default preserve `promotion_allowed=false`;
- every row records all expected field groups from the accepted planning matrix;
- fallback invocation is explicitly prohibited;
- source identity may be `pending_offline_fixture` in Slice A, but numeric correctness assertions may not pass until Slice B/C records matched identity or row-level unavailable status.

Stop condition:

- `uv run pytest tests/fund/test_small_golden_set_manifest.py -q` passes;
- `git diff --check -- docs/reviews/mvp-small-golden-set-manifest-20260608.json tests/fund/test_small_golden_set_manifest.py` passes;
- no production golden/readiness/config files changed.

### Slice B: Offline extractor fixture design and retention evidence

Allowed files:

- `tests/fixtures/fund/small_golden_set/<fund_code>_2024/annual_report_excerpt.txt`
- `tests/fixtures/fund/small_golden_set/<fund_code>_2024/expected_fields.json`
- `docs/reviews/mvp-small-golden-set-extractor-correctness-fixture-retention-evidence-20260608.md`
- focused tests under `tests/fund/` or `tests/fund/extractors/`
- `tests/README.md`

Fixture rules:

- excerpts must be minimal parsed text/table fragments, not full annual reports;
- each excerpt must identify the source section/table/row or explicit unavailable reason;
- expected fields must store `status`, `expected_value` where safe, `source_anchor` or `unavailable_reason`, `assertion_kind`, and `fixture_source_kind`;
- `assertion_kind` must be one of `exact`, `normalized_text`, `numeric_percent`, `availability_status`, `not_applicable`, `deferred_policy`;
- `fixture_source_kind` must be one of `real_minimal_excerpt`, `synthetic`, `unavailable`;
- copyright/source retention must be recorded before committing real excerpts;
- if real excerpts cannot be retained safely, use synthetic parser fixtures and record that they are not source truth and cannot satisfy source identity acceptance alone.
- only `fixture_source_kind=real_minimal_excerpt` with matched source document identity may drive `exact`, `normalized_text` or `numeric_percent` correctness assertions.

Stop condition:

- all fixture files are local and deterministic;
- no ordinary pytest reads `FundDocumentRepository`, PDF cache, source helper, network or provider;
- fixture-retention evidence records whether each row uses real minimal excerpt, synthetic excerpt or unavailable status.
- `tests/README.md` records the new fixture directory, offline constraint and focused pytest command if fixture/test directories are added.

### Slice C: Extractor correctness tests

Allowed files:

- `tests/fund/test_small_golden_set_extractor_correctness.py`, or targeted files under `tests/fund/extractors/`
- test-only fixture helpers under `tests/fund/`
- Fund extraction-chain modules only if a failing fixture test proves a same-source root cause:
  - `fund_agent/fund/extractors/`
  - `fund_agent/fund/data_extractor.py`
  - `fund_agent/fund/fund_type.py`
- `tests/README.md` only if new test/fixture directories are added

Required assertions:

- manifest is loaded and every test row preserves `promotion_allowed=false`;
- source identity is either `matched` from retained real excerpt anchors or pre-existing offline `FundDocumentRepository` metadata/public provenance, or explicitly row-level `unavailable`;
- `identity_status=matched` must include `source_document_title`, `source_document_id` or source-safe identifier, `resolved_fund_code`, `resolved_share_class` and `identity_evidence_anchor`;
- `pending_offline_fixture` and synthetic fixture metadata do not satisfy source identity and must not allow exact/numeric correctness assertions;
- fund type classification matches the row expectation, including `enhanced_index`, `bond_fund` and `qdii_fund` status handling;
- benchmark text/return, manager, scale, fee, return, holdings and risk field statuses are asserted for every row;
- A/C/E/F share-class identity is tested for rows where class-specific fields are asserted;
- missing or unsupported fields degrade to explicit unavailable/not-applicable/deferred status, not silent success;
- no test uses live repository/source/PDF/provider/network access.

Extractor-fix rule:

- only fix extractor code after a test proves the same-source failure;
- root cause must be in the same parsed excerpt/fixture as the failing assertion;
- do not infer a fix from indirect evidence, generated reports, old control logs or live-provider output;
- changed Fund extraction-chain modules must receive both a happy-path test and a fail-closed test for the new behavior.

Stop condition:

- focused pytest command passes;
- if `fund_agent/fund/extractors/` changes, related existing extractor tests pass;
- if `fund_agent/fund/data_extractor.py` changes, `uv run pytest tests/fund/test_data_extractor.py -q` passes;
- if `fund_agent/fund/fund_type.py` changes, related fund-type/profile/classification tests pass;
- no golden/readiness/quality gate semantic diff exists.

### Slice D: Evidence, review and controller closeout

Allowed files:

- `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-evidence-20260608.md`
- two independent code-review artifacts under `docs/reviews/`
- re-review artifact if any blocking finding is fixed
- `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-controller-judgment-20260608.md`
- `docs/implementation-control.md` and `docs/current-startup-packet.md` only after implementation is accepted

Required evidence:

- branch and `git status --short`;
- changed file list;
- validation command results;
- explicit no-live/no-fallback/no-provider/config-change statement;
- promotion boundary diff check;
- finding decisions with accepted/rejected/deferred status and owner;
- next entry point after this gate.

## 5. Validation Matrix

| Validation item | Command or direct evidence | Blocking if absent |
|---|---|---|
| Manifest schema and exact five rows | `uv run pytest tests/fund/test_small_golden_set_manifest.py -q` | Yes |
| Offline extractor correctness | `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` or accepted equivalent focused command | Yes |
| Existing extractor regression | related existing extractor tests for changed modules, for example `uv run pytest tests/fund/extractors -q` when extractor code changes | Yes if extractor code changes |
| No formatting errors | `git diff --check -- <changed gate files>` | Yes |
| No promotion boundary change | `git status --short -- reports/golden-answers reports/golden-readiness-preflight docs/reviews` plus explicit check that no new/modified production golden/readiness path is in the gate-owned changes; inspect gate-owned manifest/fixture/evidence files for `promotion_allowed=true` or fixture-promotion intent and treat any match as blocking | Yes |
| No provider/runtime/config change | changed-file list excludes provider/default/runtime/budget/config files unless controller stops and reclassifies | Yes |
| No live/network dependency | tests use local fixture/fake path; no command invokes live LLM, endpoint probe, repository download, fallback or provider | Yes |
| Source identity/fallback boundary | each row records `matched` or row-level `unavailable` identity and `fallback_invocation=prohibited`; matched identity must come from retained real excerpt anchors or pre-existing offline repository metadata/public provenance, not synthetic fixture metadata | Yes |

## 6. Review Instructions

Two independent implementation-plan reviews must check:

- whether the slice order is code-generation-ready and bounded;
- whether source identity can be pending in Slice A without allowing false correctness claims;
- whether fixture retention/copyright handling is explicit enough before real excerpts are committed;
- whether the plan prevents fallback invocation and live/network/provider leakage;
- whether extractor fixes are constrained to same-source root cause evidence;
- whether promotion semantics remain unchanged.

Any finding that allows full golden promotion, fallback invocation, live evidence, provider/runtime/config change, Agent runtime expansion or quality gate semantic change is blocking.

## 7. Residual Risks

| Risk | Disposition | Owner |
|---|---|---|
| Real source excerpts may be unsafe to retain in repo | Slice B must record retention evidence; if unsafe, use synthetic fixtures plus separate evidence note and do not claim source identity acceptance | Implementation worker, reviewed by controller |
| One of the five proposed funds may lack offline source identity evidence | Row becomes explicit unavailable or replacement requires controller judgment before fixture creation | Controller |
| QDII extraction may expose unsupported fields | Treat as diagnostic unavailable/deferred policy, not promotion blocker for domestic extractor correctness | Future QDII evidence policy gate |
| Small set can miss broader product failures | Accepted; this gate compresses feedback loop only and cannot support release/golden/readiness claims | Future expansion/promotion gate |

## 8. Controller Stop Conditions

The controller must stop before implementation if plan review finds unresolved blocking issues.

The controller must stop during implementation if any worker needs:

- live LLM or provider/network probe;
- fallback invocation;
- provider/default/runtime/budget/config change;
- production golden/readiness/quality gate semantic change;
- Agent runtime expansion, multi-year runtime or score-loop entry.

The controller may accept this gate only after implementation evidence, two independent reviews, blocker fixes or explicit residual owners, control/startup sync and a local accepted checkpoint.
