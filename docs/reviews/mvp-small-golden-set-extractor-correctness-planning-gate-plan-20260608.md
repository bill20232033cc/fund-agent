# MVP Small Golden Set / Extractor Correctness Planning Gate Plan

## 1. Gate Identity

Current gate: `small golden set fixture/evidence planning gate`.

Gate classification: `standard`.

Reason: this gate creates a code-generation-ready plan only. It does not create fixtures, alter extractor code, change schema, modify golden/readiness/quality gate promotion semantics, run live LLM, or change provider/runtime defaults. If a later revision promotes any file into a golden/readiness baseline or changes quality gate semantics, that later gate must be reclassified as `heavy`.

Current accepted baseline:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Latest checkpoint: `2b1c804 gateflow: accept draft pr review fixes`.
- Control truth remains `draft-PR-pass` after Draft PR 22 review/fix/re-review closeout.
- Slice E first no-live Agent body-chapter mechanics is current code fact.
- Full production Agent runtime, multi-year runtime, score-loop, live acceptance, golden/readiness promotion and provider/default/runtime changes remain future scope.

This plan uses `docs/next-development-phaseflow.md` and `docs/learning-roadmap.md` only as auxiliary route documents. They are not design truth or control truth.

## 2. Gate Question

Can the repo define a five-fund small golden set that is source-stable, auditable and narrow enough to drive the next extractor correctness gate without changing full golden/readiness/quality gate promotion semantics?

## 3. Non-Goals

- Do not run live LLM, retry, endpoint/DNS/curl/socket/PASS-only probe or fallback.
- Do not change provider/default/runtime/budget/config.
- Do not enter Chapter calibration, Agent runtime expansion, multi-year runtime, score-loop, release, merge or mark-ready.
- Do not create or promote full golden fixtures.
- Do not modify `reports/golden-answers/`, `reports/golden-readiness-preflight/`, quality gate thresholds, score semantics, snapshot schema, final judgment semantics or readiness manifests.
- Do not treat this five-fund set as proof of full product correctness.
- Do not handle unrelated dirty or untracked files.

## 4. Selection Principles

The small set must be small enough to audit manually and broad enough to expose extractor failure modes before LLM writing work resumes.

Selection rules:

1. Exactly five rows.
2. One row per primary extractor stress type:
   - active equity or mixed fund;
   - broad domestic index fund;
   - enhanced index fund;
   - bond fund;
   - QDII or FOF cross-market slot.
3. Prefer codes already present in project control history or selected-fund CSV so the next gate can reuse known evidence chains.
4. Use `report_year=2024` for all rows unless a plan review proves a specific fund lacks a valid 2024 annual report.
5. Each selected row must require source document identity before correctness assertions are accepted.
6. A/C/E/F share classes must not be mixed; expected fields must state the share-class identity requirement.
7. QDII and FOF remain diagnostic coverage, not promotion candidates, unless a later heavy gate accepts taxonomy and source policy.

## 5. Proposed Five-Fund Set

| Slot | Fund code | Report year | Expected fund type | Reason for inclusion | Promotion status |
|---|---:|---:|---|---|---|
| Active equity/mixed | `004393` | 2024 | `active_fund` | Existing release-maintenance evidence covers active-fund extractor and quality-gate residuals; stresses manager, holdings, fee and turnover applicability. | `promotion_allowed=false` |
| Broad domestic index | `110020` | 2024 | `index_fund` | Stresses benchmark identity, index profile, tracking-error applicability and source provenance; existing control docs keep it deferred from promotion. | `promotion_allowed=false` |
| Enhanced index | `004194` | 2024 | `enhanced_index` | Stresses enhanced-index benchmark composition, alpha attribution and tracking-error fields. | `promotion_allowed=false` |
| Bond | `006597` | 2024 | `bond_fund` | Existing NAV-derived drawdown and bond-risk evidence path makes it the narrow bond extractor correctness candidate. | `promotion_allowed=false` |
| QDII | `017641` | 2024 | `qdii_fund` | Existing QDII residual makes it useful for cross-market classification, benchmark/source-provenance and unavailable handling without promoting QDII readiness. | `promotion_allowed=false` |

If implementation evidence later proves one proposed fund lacks a repository-verified 2024 annual report, the replacement must keep the same slot and be accepted by controller judgment before fixture creation. A QDII-FOF fund must not satisfy the pure FOF slot unless a separate FOF taxonomy gate accepts it.

## 6. Source Document Requirements

For each row, the next gate must record a `source_document_identity` object before correctness comparison:

```json
{
  "fund_code": "004393",
  "report_year": 2024,
  "source_kind": "annual_report",
  "source_document_title": "<exact annual report title>",
  "source_document_date": "<publication or report-period date if available>",
  "source_document_id": "<repository/source identifier if available>",
  "resolved_fund_code": "<fund code observed in document>",
  "resolved_share_class": "A",
  "identity_status": "matched",
  "identity_evidence_anchor": "<section/table/row anchor or unavailable reason>"
}
```

Acceptance rules:

- `identity_status` must be `matched` before expected numeric fields become correctness assertions.
- `identity_mismatch`, `schema_drift` and `integrity_error` fail closed for that row.
- `not_found` and `unavailable` may only produce explicit row-level `unavailable` status; they must not be silently replaced by another source.
- This planning gate and the immediate extractor correctness gate must not invoke fallback. If an offline pre-existing provenance record already contains `fallback_used` or `fallback_eligibility`, it may be recorded only as historical metadata. Otherwise `fallback_used=false` and fallback invocation remains prohibited. If source identity would require fallback execution, the row must become `unavailable` or go through a controller replacement decision.

## 7. Expected Field Matrix

Each row in the future small-set fixture must use the same field list. A field can be `expected`, `unavailable`, `not_applicable` or `deferred_policy`, but cannot be omitted silently.

| Field group | Required fields | Source requirement | Applies to |
|---|---|---|---|
| Identity | fund code, fund name, report year, share class, expected fund type, classification basis | annual report identity section or repository metadata plus parsed section evidence | all five rows |
| Source document | title, source name, source id or URL-safe identifier, `fallback_used=false` or historical offline fallback metadata, primary failure category if row unavailable, fallback invocation prohibited | offline `FundDocumentRepository` metadata/public provenance only | all five rows |
| Benchmark | benchmark full text, benchmark index name if directly recoverable, benchmark return for report year | annual report performance section or benchmark disclosure table | all five rows, with QDII unavailable allowed only with reason |
| Manager | current manager name, tenure/start date, manager change in report period if disclosed | annual report manager section | all five rows |
| Scale | net asset value/end-period scale, share count if disclosed, holder structure availability | annual report financial/profile tables | all five rows |
| Fee | management fee, custody fee, sales/service fee if applicable | annual report fee disclosure or fund profile section | all five rows |
| Return | fund one-year return, benchmark one-year return, excess return formula inputs, NAV basis note | annual report §3 and NAV adapter where applicable | all five rows |
| Holdings | top holdings availability, concentration, industry allocation availability, bond allocation availability | annual report investment portfolio section | active/index/enhanced/bond; QDII may be unavailable with source reason |
| Risk | drawdown, tracking error, turnover, bond risk evidence, QDII currency/market risk availability | typed extractor output backed by annual report/NAV source | type-specific |
| Evidence anchors | source section/table/row for each expected field | parsed annual report anchors or explicit unavailable reason | all fields |

## 8. Per-Fund Expected Field Focus

### `004393` active fund

Expected focus:

- `classified_fund_type=active_fund`.
- benchmark text and benchmark return.
- management fee and custody fee.
- manager name and manager tenure.
- holdings snapshot and top-holdings availability.
- turnover availability status, including explicit unavailable/deferred policy if no directly disclosed turnover row exists.
- share-class identity proof before A-class fields are accepted.

Primary failure modes to test later:

- active fund incorrectly forced into index valuation logic;
- missing turnover treated as positive style-stability evidence;
- share-class column selection without direct class evidence.

### `110020` broad index fund

Expected focus:

- `classified_fund_type=index_fund`.
- benchmark full text and index identity.
- tracking error availability.
- fund return and benchmark return.
- index constituents/methodology availability status.
- fee fields.
- source provenance/fallback eligibility.

Primary failure modes to test later:

- benchmark identity drift;
- source fallback masking `schema_drift` or `identity_mismatch`;
- tracking error expected when source does not directly disclose it.

### `004194` enhanced index fund

Expected focus:

- `classified_fund_type=enhanced_index`.
- composite benchmark text.
- fund return, benchmark return and excess return fields.
- tracking error availability.
- holdings and industry allocation availability.
- fee fields.

Primary failure modes to test later:

- enhanced index classified as plain active or plain index;
- benchmark formula normalized into an unsupported simplified index;
- alpha attribution computed from missing benchmark data.

### `006597` bond fund

Expected focus:

- `classified_fund_type=bond_fund`.
- bond portfolio allocation and credit/duration/rate-risk evidence availability.
- NAV-derived drawdown stress evidence where repository path is available.
- fund return and benchmark return.
- fee fields.
- manager and scale fields.

Primary failure modes to test later:

- bond fund scanned through equity-specific holdings rules;
- A/C share classes mixed in NAV or annual report fields;
- NAV-derived drawdown treated as annual-report direct disclosure.

### `017641` QDII fund

Expected focus:

- `classified_fund_type=qdii_fund`.
- source document identity and public provenance.
- benchmark and fund return availability.
- overseas market/currency risk availability.
- fee and scale fields.
- explicit unavailable handling for fields not supported by current QDII extraction.

Primary failure modes to test later:

- QDII forced into domestic index valuation logic;
- QDII residual treated as promotion-ready;
- source fallback accepted without eligible failure classification.

## 9. Offline Fixture Strategy

The next extractor correctness gate should create offline, reviewable inputs in two layers.

Layer 1: small-set manifest.

Candidate path:

- `docs/reviews/mvp-small-golden-set-manifest-20260608.json`

Purpose:

- records five rows, source document identity requirements, field expectation status and owner notes;
- remains a review artifact, not a promoted golden answer.

Layer 2: extractor fixtures.

Candidate paths:

- `tests/fixtures/fund/small_golden_set/<fund_code>_<year>/annual_report_excerpt.txt`
- `tests/fixtures/fund/small_golden_set/<fund_code>_<year>/expected_fields.json`

Rules:

- fixture excerpts must be minimal sections/tables needed for extractor correctness tests;
- no ordinary pytest may require live network, PDF download or provider access;
- expected fields must store source anchor references or explicit unavailable reasons;
- source excerpts must be safe to retain in repo review context; if copyright/sourcing constraints prevent retention, the plan must switch to synthetic parser fixtures plus a separate evidence note and not call them golden truth;
- generated reports, snapshots and score outputs stay under `reports/` and remain local unless a later gate accepts promotion.

## 10. Boundary Against Full Golden Promotion

This gate and its immediate extractor correctness follow-up may create small-set review artifacts and test fixtures. They must not:

- modify strict golden answer JSON;
- add rows to production `reports/golden-answers/golden-answer.json`;
- mark `fixture_state` as promoted;
- set `promotion_allowed=true`;
- change FQ0-FQ6 quality gate thresholds;
- change correctness oracle identity semantics;
- alter `golden-readiness-preflight` disposition logic;
- claim release readiness.

Any future promotion from small set to production golden/readiness must enter a separate heavy gate with:

- row-level human review evidence;
- source document identity proof;
- source/license/copyright disposition;
- quality gate and score semantics review;
- two independent reviews and controller judgment.

## 11. Code-Generation-Ready Implementation Slices For The Next Gate

The next gate should be `small golden set extractor correctness implementation gate`, not Agent runtime expansion.

### Slice A: Manifest schema and fixture ownership

Allowed files:

- new `docs/reviews/mvp-small-golden-set-manifest-YYYYMMDD.json`;
- optional new schema helper under tests only if implementation plan accepts it;
- tests for manifest validation.

Stop condition:

- manifest has exactly five rows;
- all rows have field statuses and source requirements;
- no production golden/readiness files changed.

### Slice B: Offline extractor fixtures

Allowed files:

- `tests/fixtures/fund/small_golden_set/...`;
- focused tests under `tests/fund/`.

Stop condition:

- tests consume local fixture excerpts only;
- no `FundDocumentRepository` live access in ordinary pytest;
- no PDF/cache/network/provider dependency.

### Slice C: Extractor correctness assertions

Allowed files:

- focused extractor tests;
- extractor modules only where tests prove a same-source root cause.

Stop condition:

- each changed extractor has tests for happy path and at least one fail-closed path;
- A/C/share-class and report-year identity are explicitly tested;
- missing fields degrade explicitly.

### Slice D: Evidence and controller closeout

Allowed files:

- `docs/reviews/*implementation-evidence*.md`;
- `docs/reviews/*code-review*.md`;
- controller judgment;
- control/startup docs only if the gate is accepted and next entry changes.

Stop condition:

- validation commands pass;
- two independent reviews are complete or unavailability is recorded;
- controller judgment records accepted/residual findings and next gate.

## 12. Extractor Correctness Acceptance Matrix

| Acceptance item | Direct evidence required | Blocking if absent |
|---|---|---|
| Five-row manifest | JSON or Markdown table with exactly five selected funds and report year | Yes |
| Source identity | source document identity per row, explicit row unavailable, and no fallback invocation evidence | Yes |
| Fund type correctness | expected type vs extractor type for each row | Yes |
| Benchmark correctness | benchmark text and return source status per row | Yes for applicable rows |
| Manager correctness | manager name/tenure source status per row | Yes for applicable rows |
| Scale correctness | end-period scale source status per row | Yes for applicable rows |
| Fee correctness | management/custody/sales or service fee source status per row | Yes for applicable rows |
| Return correctness | fund return, benchmark return and NAV basis source status | Yes for applicable rows |
| Holdings correctness | holdings/industry/bond allocation availability status | Yes for applicable rows |
| Risk correctness | turnover/tracking error/bond risk/QDII risk status by fund type | Yes for applicable rows |
| Offline reproducibility | focused pytest command using only local fixtures/fakes | Yes |
| Promotion boundary | `promotion_allowed=false` and no golden/readiness/quality semantic diff | Yes |
| Residual classification | unsupported QDII/FOF/multi-year fields explicitly deferred | Yes |

## 13. Validation For This Planning Gate

Required before accepting this plan:

```bash
git diff --check -- docs/reviews/mvp-small-golden-set-extractor-correctness-planning-gate-plan-20260608.md
```

Required review:

- two independent plan reviews from `AgentDS`, `AgentMiMo` or `AgentGLM`;
- reviewers must check selection logic, field matrix, offline fixture strategy, non-promotion boundary and next-gate acceptance matrix;
- reviewers must treat any live/provider/runtime/golden-promotion leakage as blocking.

Controller judgment may accept the plan only if:

- current control truth was confirmed at `draft-PR-pass`;
- plan review findings are accepted/rejected/deferred with one-line rationale;
- no implementation files, provider config, live commands, golden/readiness promotion files or unrelated untracked files were touched.

## 14. Residual Risks

| Risk | Disposition | Owner |
|---|---|---|
| Proposed QDII row may remain unsupported by current source/extractor path | Accept as diagnostic coverage only; unsupported fields must become explicit unavailable/deferred statuses, not promotion claims | Future QDII evidence policy gate |
| Copyright/source retention may block real annual-report excerpts as fixtures | Next gate must either use minimal permitted excerpts or synthetic parser fixtures plus separate evidence notes | Next extractor correctness implementation gate controller |
| Existing control docs still queue live acceptance evidence | This steering request supersedes the queue for the next development entry; if plan is accepted, control/startup docs should be synced to record small golden set / extractor correctness as next entry | Controller after plan acceptance |
| Five funds cannot prove broad product quality | Accepted; purpose is to compress feedback loop, not prove readiness | Future small-set expansion / promotion gate |
