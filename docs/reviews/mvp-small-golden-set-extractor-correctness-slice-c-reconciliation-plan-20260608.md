# MVP Small Golden Set / Extractor Correctness Slice C Reconciliation Plan

## 1. Gate Identity

Current gate: `small golden set extractor correctness implementation gate` Slice C planning/reconciliation.

Gate classification: `standard`.

This artifact is planning-only and code-generation-ready for the next worker. It does not modify code, fixtures, extractors, provider/runtime/config, production golden/readiness artifacts, quality gate semantics, score-loop state, release state or PR external state.

Accepted baseline:

- Implementation gate plan accepted at checkpoint `d05c1c9`.
- Slice A manifest accepted at checkpoint `a94c705`: `docs/reviews/mvp-small-golden-set-manifest-20260608.json`.
- Slice B fixture retention evidence accepted at checkpoint `ceb418b`: all five rows use `fixture_source_kind=synthetic` / `source_identity.status=unmatched_synthetic`.
- Slice B controller judgment explicitly accepts fixture-shape evidence only and preserves source identity, exact correctness and numeric correctness as unresolved.

## 2. Premise Review

Slice B being entirely synthetic is blocking for exact/numeric extractor correctness.

Reason:

- Extractor correctness needs same-source evidence: the expected field value and the extractor input must come from the same matched annual-report source identity.
- Synthetic fixtures can validate local fixture schema, parser mechanics, status propagation and offline test harness boundaries.
- Synthetic fixtures cannot prove annual-report source identity, source-document field values, share-class identity, benchmark text, manager, scale, fee, return, holdings or risk numeric correctness.
- Therefore Slice C must not claim `exact`, `normalized_text` or `numeric_percent` correctness from the current Slice B fixtures.

This is not blocking for the entire gate if Slice C is reconciled into one of two legal directions:

1. obtain matched source identity offline before exact/numeric assertions; or
2. narrow Slice C to parser/fixture mechanics only and explicitly preserve extractor correctness as residual.

## 3. Legal Directions

### Option 1: Source Identity Acquisition Mini-Slice

Objective: acquire matched source identity for one or more rows without live repository/PDF/network/fallback activity, then permit exact/numeric extractor correctness tests only for matched rows and fields.

Allowed evidence sources:

- pre-existing repository metadata already retained in the workspace before this slice;
- pre-existing public provenance already recorded in accepted review artifacts or local ignored evidence;
- retained real minimal excerpt anchors that are already local and safe to retain;
- a newly written source-identity evidence artifact that cites only offline, pre-existing materials.

Forbidden evidence sources:

- live `FundDocumentRepository` call;
- PDF download or PDF parsing against a production source;
- network, DNS, socket, curl, akshare, EID, endpoint or provider probe;
- fallback invocation or fallback-result reuse;
- inferred identity from synthetic fixture text;
- inferred identity from rendered reports, LLM output or old control summaries without source-document provenance.

Required artifacts if Option 1 is chosen:

- `docs/reviews/mvp-small-golden-set-extractor-correctness-source-identity-evidence-20260608.md`
- targeted source-identity test, for example `tests/fund/test_small_golden_set_source_identity.py`
- optional local fixture metadata updates under `tests/fixtures/fund/small_golden_set/<fund_code>_2024/expected_fields.json` only for rows proven matched
- optional retained real minimal excerpts under `tests/fixtures/fund/small_golden_set/<fund_code>_2024/annual_report_excerpt.txt` only after retention safety is recorded
- `tests/README.md` only if test commands or fixture semantics change

Controller amendment after plan review:

- Pre-existing repository metadata must not mean arbitrary unrelated workspace residue.
- Option 1 may use only metadata/provenance already accepted in a review artifact, already referenced by current control truth, or newly documented in the source-identity evidence artifact with file path, provenance origin, timestamp/source label if present, and reason it is safe to treat as pre-existing offline evidence.
- Untracked, unrelated or unproven workspace fragments cannot establish matched identity.

Required row-level identity fields:

- `identity_status=matched`
- `source_document_title`
- `source_document_id` or source-safe identifier
- `resolved_fund_code`
- `resolved_share_class` where class-specific fields are asserted
- `report_year=2024`
- `source_kind=annual_report`
- `identity_evidence_anchor`
- `fallback_used=false`
- `fallback_invocation=prohibited`
- `identity_evidence_origin=pre_existing_offline_metadata` or `retained_real_minimal_excerpt_anchor`

Required tests:

- source-identity test proves that matched rows contain all required identity fields and still preserve `promotion_allowed=false`.
- source-identity test fails closed when `fixture_source_kind=synthetic`, `source_identity.status=unmatched_synthetic`, missing document id/title, mismatched fund code/year/share class, or fallback metadata is present.
- extractor correctness test may assert `exact`, `normalized_text` or `numeric_percent` only for fields whose row has `identity_status=matched` and `fixture_source_kind=real_minimal_excerpt`.
- unmatched rows remain `availability_status`, `unavailable`, `not_applicable` or `deferred_policy`.
- ordinary pytest must read only local test fixtures and evidence artifacts.

No-live/no-fallback proof:

- implementation evidence must list the exact commands run.
- changed-file list must exclude repository/PDF/cache/source-helper/provider/runtime/config files unless the controller stops and reclassifies.
- tests must not import or monkeypatch live source clients to reach external systems.
- evidence must state that no command invoked live LLM, retry, endpoint/DNS/curl/socket probe, `FundDocumentRepository` live access, PDF download, source fallback, provider, akshare or EID.
- test review must inspect imports and fixtures for repository, PDF/cache, network, provider and fallback leakage.

Copyright/source retention:

- retain only minimal excerpts necessary to prove the asserted field, section/table/row and identity anchor.
- do not retain full annual reports or broad chapter text.
- each retained excerpt must include a source anchor, retention rationale, approximate size, and field groups it supports.
- if copyright/source retention is uncertain, do not commit real text; keep row as `unavailable` or use source identity metadata without exact/numeric extractor assertions.
- any excerpt used for exact/numeric correctness must be traceable to a matched identity and must avoid unrelated text.

Stop conditions for Option 1:

- any needed identity source requires live repository/PDF/network/fallback/provider access;
- any row cannot be matched to fund code, year, annual-report identity and share class where needed;
- any real excerpt retention is unsafe or too broad;
- any implementation needs extractor code changes before a same-source failing fixture test exists;
- any worker attempts `promotion_allowed=true`, golden/readiness promotion, quality gate semantic change, provider/runtime/config change, Agent runtime expansion, score-loop, release, merge or mark-ready.

### Option 2: Narrow Slice C to Parser/Fixture Mechanics Only

Objective: keep Slice C offline and useful by testing fixture parsing, metadata normalization, unsupported/unavailable status propagation and fail-closed boundaries, while explicitly not claiming extractor correctness.

Allowed files:

- `tests/fund/test_small_golden_set_parser_mechanics.py` or equivalent focused test under `tests/fund/`
- test-only helper under `tests/fund/` if needed
- `tests/README.md` only if documenting a new focused command
- implementation evidence/review/judgment artifacts under `docs/reviews/`

Forbidden files:

- `fund_agent/fund/extractors/`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/fund_type.py`
- `reports/golden-answers/`
- `reports/golden-readiness-preflight/`
- provider/default/runtime/budget/config files
- production quality gate or score-loop files

Required assertions:

- the five fixture directories remain exact: `004393`, `110020`, `004194`, `006597`, `017641`, all `2024`.
- every row preserves `promotion_allowed=false`, `fallback_invocation=prohibited`, `fixture_source_kind=synthetic`, `source_identity.status=unmatched_synthetic` and `exact_numeric_correctness_allowed=false`.
- no field uses `exact`, `normalized_text` or `numeric_percent`.
- expected field status is preserved from the Slice A manifest, including `017641 holdings=unavailable` and `risk=deferred_policy`.
- parser/test helper output degrades unsupported fields to explicit unavailable/not-applicable/deferred status, not silent success.
- tests must not call repository, PDF/cache/source helper, provider, network, fallback, live LLM or endpoint probes.

Stop conditions for Option 2:

- any assertion attempts to prove source truth, annual-report correctness or numeric correctness;
- any extractor change is needed;
- any worker needs live or fallback evidence;
- any production golden/readiness/quality gate/score/provider/runtime/config file would change.

## 4. Recommendation

Recommended direction: Option 1 as a bounded source identity acquisition mini-slice, with an immediate fallback to Option 2 when matched identity cannot be proven offline.

Reason:

- The current gate is named extractor correctness. Without at least one matched same-source row, the gate cannot exercise its central purpose.
- Option 1 is the shortest path that can legally unlock exact/numeric correctness while preserving the no-live and no-fallback boundary.
- Option 1 must be row-gated: matched rows may progress; unmatched rows stay residual. This avoids all-or-nothing blocking while preventing false correctness claims.
- Option 2 remains useful only as a harness/mechanics slice. It should be chosen deliberately if offline matched identity is unavailable or retention-safe real excerpts cannot be used.

Controller decision rule:

- Start with Option 1 discovery using only offline pre-existing metadata/provenance and retained minimal anchors.
- If no row obtains matched identity without violating boundaries, stop Option 1 and execute Option 2 only.
- Do not enter extractor fix in either option unless a later accepted plan has matched same-source fixture evidence proving root cause.

## 5. Allowed Files

Planning artifact already produced by this worker:

- `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-reconciliation-plan-20260608.md`

Option 1 implementation may touch only:

- `docs/reviews/mvp-small-golden-set-extractor-correctness-source-identity-evidence-20260608.md`
- `tests/fund/test_small_golden_set_source_identity.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py` only for matched rows/fields
- `tests/fund/` test-only helpers if needed
- `tests/fixtures/fund/small_golden_set/<fund_code>_2024/annual_report_excerpt.txt`
- `tests/fixtures/fund/small_golden_set/<fund_code>_2024/expected_fields.json`
- `tests/README.md` only if commands or fixture semantics change
- implementation evidence/review/judgment artifacts under `docs/reviews/`

Option 2 implementation may touch only:

- `tests/fund/test_small_golden_set_parser_mechanics.py` or equivalent focused test under `tests/fund/`
- `tests/fund/` test-only helpers if needed
- `tests/README.md` only if commands or fixture semantics change
- implementation evidence/review/judgment artifacts under `docs/reviews/`

Extractor code remains forbidden in this reconciliation slice. A future extractor-fix slice requires a separate accepted plan and matched same-source failing fixture evidence.

## 6. Forbidden Actions

- live LLM, retry, endpoint/DNS/curl/socket/PASS-only probe;
- network, PDF download, repository download, akshare, EID, provider call;
- live `FundDocumentRepository` source access or fallback invocation;
- provider/default/runtime/budget/config change;
- production golden/readiness/quality gate/score semantic change;
- `promotion_allowed=true`;
- extractor code change before a later accepted matched same-source root-cause plan;
- Agent runtime expansion, multi-year runtime, score-loop, release, merge or mark-ready;
- deriving source identity from synthetic fixtures, generated reports or LLM output;
- direct production PDF/cache/source-helper access outside accepted repository boundaries.

## 7. Matched Identity Failure Handling

If matched identity cannot be obtained offline:

- keep every affected row as `source_identity.status=unmatched_synthetic` or explicit `unavailable`;
- keep `exact_numeric_correctness_allowed=false`;
- keep field assertions as `availability_status`, `unavailable`, `not_applicable` or `deferred_policy`;
- record the residual as `synthetic_only_source_identity_unresolved`;
- do not alter extractor code;
- do not infer root cause;
- do not promote row, fixture or correctness status;
- proceed only with Option 2 parser/fixture mechanics if useful.

If only some rows are matched:

- exact/numeric assertions are allowed only for matched row-field pairs with retained real minimal excerpt anchors.
- unmatched rows remain residual and cannot contribute to extractor correctness acceptance.
- evidence must separate `matched`, `unavailable` and `unmatched_synthetic` rows.

## 8. Review Acceptance Matrix

| Review item | Acceptance criterion | Blocking if absent |
|---|---|---|
| Slice B premise | Plan states synthetic-only fixtures block exact/numeric extractor correctness claims. | Yes |
| Direction legality | Plan presents both Option 1 source identity acquisition and Option 2 parser/fixture mechanics. | Yes |
| Recommended route | Recommendation is row-gated Option 1 with fallback to Option 2 if offline identity cannot be proven. | Yes |
| No-live boundary | Allowed evidence excludes live repository/PDF/network/fallback/provider/endpoint/probe activity. | Yes |
| No-fallback boundary | Every row and test preserves `fallback_invocation=prohibited` and `fallback_used=false`. | Yes |
| Copyright retention | Real excerpts are minimal, anchor-specific, retention-reviewed and not full reports. | Yes for Option 1 |
| Source identity schema | Matched rows require document title/id or source-safe identifier, fund code, year, share class where relevant and evidence anchor. | Yes for Option 1 |
| Synthetic guard | Synthetic or unmatched rows cannot drive `exact`, `normalized_text` or `numeric_percent`. | Yes |
| Extractor boundary | Extractor changes remain prohibited until a separate accepted matched same-source root-cause plan. | Yes |
| Row unavailable handling | Unmatched rows remain `unavailable` / `unmatched_synthetic` / residual and do not enter extractor fix. | Yes |
| Promotion boundary | No production golden/readiness/quality gate/score semantics or `promotion_allowed=true`. | Yes |
| Allowed files | Implementation file scope is explicit and excludes unrelated dirty/untracked files. | Yes |
| Stop conditions | Plan stops on live/fallback need, unsafe retention, identity mismatch, extractor-change need, promotion/runtime/config/release scope. | Yes |

## 9. Validation Commands For Next Worker

Option 1 minimum validation:

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py -q
```

If matched rows unlock focused extractor tests:

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Option 2 minimum validation:

```bash
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_parser_mechanics.py -q
```

Diff hygiene:

```bash
git diff --check -- docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-reconciliation-plan-20260608.md
```

Implementation evidence must add the exact `git diff --check -- <changed gate files>` command that covers all files changed by that worker.

## 10. Residual Blocker

Residual blocker status after this planning artifact: open.

Blocker: all accepted Slice B fixtures are synthetic and no row currently has matched annual-report source identity. Exact/numeric extractor correctness remains blocked until Option 1 proves matched identity offline for at least one row-field pair. If Option 1 cannot do so, the only legal Slice C implementation is Option 2 parser/fixture mechanics with extractor correctness left as residual.
