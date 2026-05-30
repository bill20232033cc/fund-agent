# Baseline Coverage / Source Recovery / Taxonomy + Bond Triage Plan

> Date: 2026-05-27
> Worker: AgentCodex planning worker
> Scope: plan artifact only. No source, tests, README, renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, `FundDocumentRepository` / source fallback semantics, extractor, fixture, golden corpus, package config, commit, push, PR, or GitHub mutation.

## Startup Packet Recap

- Phase: `release maintenance`.
- Current gate: `small baseline corpus v1 accepted locally`.
- Next entry point: `baseline coverage / source recovery / taxonomy + bond extraction triage plan/review`.
- Latest accepted checkpoint: `297f5cb`.
- Gate 4 evidence: `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-controller-judgment-20260527.md`.
- Truth sources: `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current gate / Next entry point, and current accepted artifacts. `docs/reviews/` is evidence chain only.

## Reconciliation

Gate 4 is accepted as an evidence run, but not as golden-corpus readiness:

- Clean evaluated coverage is only three candidates / three fund-type slots: `004393` active, `004194` enhanced index, `006597` bond.
- `006597` is quality-gate blocked by missing-field rate; correctness matched available comparable rows, so the blocker is not a golden mismatch.
- `110020` index and `017641` QDII remain fallback-blocked because upstream failure category is unknown.
- `007721` and `017970` remain FOF attempts / QDII-FOF type-gap evidence; pure `fof_fund` coverage is still a `data_gap`.
- `004393` / 2025 remains probe-only; same-fund 2024 golden rows must not be reused for 2025 correctness.
- Therefore the next gate must increase clean coverage and resolve the bond blocker before `golden answer corpus v1` can be considered.

## First-Principles Decomposition

The next decision should optimize for the smallest evidence that changes routing. There are three independent blockers, and merging them into one implementation would hide root cause.

### Problem A: Index / QDII Source Recovery Or Replacement

Question: can `110020` and `017641` safely count as repository-verified clean candidates?

They can only move toward clean coverage if the original upstream failure category is recovered as fallback-eligible:

- `not_found`: allowed fallback.
- `unavailable`: allowed fallback.

They must be excluded or replaced if the category is fail-closed:

- `schema_drift`
- `identity_mismatch`
- `integrity_error`
- still `unknown_upstream_failure_category` after bounded recovery.

Safe recovery path:

1. Use existing public CLI / Fund-layer repository paths only. Do not call concrete EID / Eastmoney adapters, PDF cache helpers, or download helpers directly.
2. If current public artifacts do not expose upstream failure category, do not infer it from successful Eastmoney fallback. Record `needs-more-evidence`.
3. Replacement is preferred over source implementation if a clean index/QDII candidate can be found through bounded `fund-analysis extraction-snapshot` probes without source fallback ambiguity.
4. Source fallback semantic changes are out of scope. If the only way to recover category is changing `FundDocumentRepository` or source orchestration, open a separate source-boundary plan/review gate.

### Problem B: FOF Coverage / Taxonomy

Question: is the current FOF gap a missing pure-FOF candidate problem or a taxonomy precedence problem?

There are two possible paths:

- Pure FOF search: find a candidate whose current classifier returns `fof_fund`, annual report identity is verified, and source category is clean.
- QDII-FOF taxonomy gate: decide whether QDII-FOF should count as `qdii_fund`, `fof_fund`, or a separate precedence rule for this project.

First-principles choice:

- Do not count QDII-FOF as pure FOF without an accepted taxonomy gate.
- Prefer pure FOF search first because it does not alter taxonomy semantics.
- Open taxonomy only if bounded pure FOF search fails or if the selected fund pool structurally contains only hybrid QDII-FOF examples.

### Problem C: `006597` Bond Quality-Gate Block

Question: are `006597` missing fields real extractor gaps, field-applicability policy gaps, or bond-lens evidence/report-quality gaps?

Gate 4 observed:

- `turnover_rate`: missing; for bond funds, stock turnover may be not applicable or not disclosed. It should not automatically be treated as equity-style manager consistency evidence.
- `holder_structure`: missing; may be a real extraction gap if §9 discloses holder structure.
- `holdings_snapshot`: missing; for bond funds, stock holdings snapshot is likely the wrong lens. Bond lens should ask for duration, credit exposure, leverage/liquidity, drawdown, or bond holding risk evidence.
- `share_change`: missing; may be extractor ambiguity if §10 has multiple share classes.
- `investor_return`: missing; this is generally Chapter 3 / investor-return evidence, not equity-only. Its absence should be classified as `extractor_gap`, `evidence_anchor_or_score_projection`, or score-contract gap unless a reviewed design explicitly says it is not applicable to `bond_fund`.
- Missing-field rate hits FQ4 block; correctness comparable rows still match.

Root-cause decision must be same-source:

- If the annual report has the field and the extractor failed, classify as `extractor_gap`.
- If the field is equity-specific or irrelevant for bond lens, classify as `field_applicability_policy`.
- Do not classify `investor_return` as `field_applicability_policy` for bond funds unless an accepted design / template artifact explicitly says investor-return evidence is not applicable to `bond_fund`.
- If the fact exists but lacks stable anchor / comparable subfield exposure, classify as `evidence_anchor_or_score_projection`.
- If the current quality score asks for the wrong bond-lens facts, classify as `bond_lens_contract_gap`.

Allowed evidence for this decision is intentionally narrow:

- public CLI outputs from `fund-analysis extraction-snapshot`, `extraction-score`, `quality-gate`, `analyze`, and `checklist`;
- existing extracted snapshot / score / quality artifacts from Gate 4;
- accepted review evidence under `docs/reviews/`;
- current tracked extractor tests / fixtures, if they already exist and can be read without generating new production data;
- domain rules from accepted `docs/design.md` current sections and `docs/fund-analysis-template-draft.md`.

Forbidden evidence:

- direct production PDF reads;
- direct cache inspection;
- concrete source helper / downloader / source adapter calls;
- ad hoc parsing of production annual-report files outside the public repository / extractor path.

If the allowed evidence cannot prove whether an annual-report fact exists, classify the field as `needs-more-evidence` rather than inferring presence or absence.

Do not weaken FQ0-FQ6. If fields are reclassified as N/A, this must happen upstream in score/fund-quality applicability with explicit fund-type reasons, not by lowering quality-gate thresholds.

## Recommended Minimal Next Slice

Choose ordered subgates, not a big-bang implementation.

### Subgate 1: Evidence-Only Triage And Coverage Probe

This should be authorized next.

Goals:

- Produce a tracked evidence artifact that classifies `006597` missing fields into `extractor_gap`, `field_applicability_policy`, `evidence_anchor_or_score_projection`, or `bond_lens_contract_gap`.
- Run bounded replacement probes for index/QDII/FOF candidates using public CLI commands only.
- Decide whether Subgate 2 should be a bond score-applicability implementation, extractor implementation, source recovery plan, or taxonomy plan.

Why first:

- It is the only step that can distinguish "fix extractor" from "change field applicability" without weakening FQ rules.
- It can improve coverage routing without changing source fallback semantics.
- It keeps current product behavior unchanged while producing same-source evidence.

Subgate 1 has two independently closeable tracks:

- Track 1A: `006597` bond triage. This can proceed and close even if controller-approved replacement candidates are unavailable.
- Track 1B: index/QDII/FOF replacement probing. If no controller-approved candidate list exists, close this track as `not_run_no_approved_candidates` and keep source/taxonomy blockers open without blocking Track 1A.

### Subgate 2A: Bond Score-Applicability Implementation

Only authorize if Subgate 1 proves `006597` block is caused by fields that should be N/A for `bond_fund`.

Expected scope:

- Make fund-type applicability explicit in scoring / fund-quality inputs so bond funds are not blocked by equity-only fields.
- Preserve FQ0-FQ6 thresholds and severity.
- Keep `quality_gate.py` unchanged unless focused tests prove no other way to preserve semantics.

### Subgate 2B: Bond Extractor / Anchor Implementation

Only authorize if Subgate 1 proves same-source annual-report facts exist and current extractor/projection missed them.

Expected scope:

- Fix the smallest extractor or snapshot projection path for the proven field only.
- Do not add broad bond analytics, renderer text, or golden rows.

### Subgate 2C: Source Recovery / Candidate Replacement Evidence

Authorize if Subgate 1 finds clean index/QDII replacements or proves current fallback-blocked rows need source-boundary work.

Expected scope:

- Evidence-only if replacement works.
- Separate source-boundary plan if fallback category cannot be recovered through current public surfaces.

### Subgate 2D: Pure FOF Search Or Taxonomy Plan

Authorize after Subgate 1 pure-FOF probe result:

- If a pure FOF candidate is found, run the same snapshot/score/quality evidence loop.
- If not, open a taxonomy plan for QDII-FOF precedence; do not implement taxonomy in the same gate.

## Slice Specifications

### Slice 1: Evidence-Only Triage

Allowed operations:

- `uv run fund-analysis extraction-snapshot` with explicit `--fund-code`, `--report-year`, and `--run-id`.
- `uv run fund-analysis extraction-score` and `uv run fund-analysis quality-gate` for produced snapshots.
- `uv run python scripts/selected_funds_smoke.py` dry-run or bounded `--run` for explicitly listed replacement candidates.
- Read existing scratch outputs from Gate 4 and new ignored scratch outputs.
- Read accepted review artifacts, current tracked extractor tests / fixtures, and accepted design/template sections.
- Write one tracked evidence artifact under `docs/reviews/`.

Forbidden operations:

- Do not directly read production PDFs.
- Do not inspect production cache contents directly.
- Do not call concrete source helpers, downloaders, source adapters, EID helpers, or Eastmoney helpers.
- Do not parse annual-report files outside the public CLI / Fund repository path.
- Do not infer that a missing fact exists or does not exist when the allowed evidence cannot prove it.

Bond triage checklist:

| Field | Initial question | Allowed classifications |
|---|---|---|
| `turnover_rate` | Is this relevant to bond-fund manager consistency, disclosed as a bond-relevant turnover fact, or equity-only? | `field_applicability_policy`, `extractor_gap`, `evidence_anchor_or_score_projection`, `needs-more-evidence` |
| `holder_structure` | Does accepted/public evidence indicate §9 holder structure exists and extractor missed it? | `extractor_gap`, `evidence_anchor_or_score_projection`, `needs-more-evidence` |
| `holdings_snapshot` | Is current stock-holdings expectation wrong for bond fund, and what bond-lens evidence should replace it? | `field_applicability_policy`, `bond_lens_contract_gap`, `extractor_gap`, `needs-more-evidence` |
| `share_change` | Is the missing value caused by multi-share-class ambiguity or absent disclosure? | `extractor_gap`, `evidence_anchor_or_score_projection`, `needs-more-evidence` |
| `investor_return` | Is Chapter 3 / investor-return evidence absent, unexposed, or outside current score contract? | `extractor_gap`, `evidence_anchor_or_score_projection`, `score_contract_gap`, `needs-more-evidence`; not `field_applicability_policy` without accepted design support |
| `nav_data` anchor | Is lack of annual-report anchor acceptable because NAV is non-annual-report source, or should score contract model it separately? | `score_contract_gap`, `evidence_anchor_or_score_projection`, `needs-more-evidence` |

Allowed tracked files:

- `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-20260527.md` or equivalent controller-assigned path.

Scratch policy:

- `/tmp/fund-agent-baseline-coverage-triage-20260527/`
- `reports/smoke/baseline-coverage-triage-20260527/`
- `reports/extraction-snapshots/baseline-coverage-triage-20260527-*/`
- `reports/data-source-runs/baseline-coverage-triage-20260527/`

No scratch output is a durable fixture or golden input.

Suggested commands:

```text
uv run fund-analysis extraction-snapshot --run-id baseline-coverage-triage-006597-2024 --fund-code 006597 --report-year 2024
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/baseline-coverage-triage-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/baseline-coverage-triage-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json
uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/baseline-coverage-triage-006597-2024/score.json
uv run python scripts/selected_funds_smoke.py --code <INDEX_REPLACEMENT> --code <QDII_REPLACEMENT> --code <FOF_REPLACEMENT> --report-year 2024 --output-dir reports/smoke/baseline-coverage-triage-20260527
```

Candidate replacement commands must be filled from accepted selected-fund CSV evidence or a controller-approved candidate list. If no candidate list is accepted, close Track 1B as `not_run_no_approved_candidates` and continue / close Track 1A bond triage; do not perform ad hoc browsing or direct source calls.

Validation:

```text
git diff --check
```

No pytest is required for evidence-only unless a script is changed, which this slice forbids.

Stop conditions:

- Any needed evidence requires direct PDF/cache/source-helper access.
- Source failure category cannot be observed through public paths.
- Candidate replacement would require changing fallback semantics.
- FOF probe finds only QDII-FOF hybrids and no pure `fof_fund`; route to taxonomy plan instead of counting coverage.
- Bond root cause cannot be classified from current public outputs; record `needs-more-evidence`.
- `investor_return` would be treated as not applicable for bond funds without an accepted design / template decision.

### Slice 2A: Bond Score-Applicability Implementation

Allowed production files, only if implementation is later authorized:

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/fund_type.py` only if an existing fund-type helper needs an explicit exported applicability predicate.
- `fund_agent/fund/README.md` only if public Fund package behavior changes and README sync is required by repository rules.

Preferred non-production tests:

- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/test_quality_gate_integration.py`

Default forbidden files:

- `fund_agent/fund/quality_gate.py` unless tests prove FQ semantics cannot be preserved within score/fund-quality inputs.
- renderer, Service/CLI, Host/Agent/dayu, document repository/source fallback, extractor, golden files, fixtures.

Implementation contract:

- Add explicit fund-type applicability reasons such as `not_applicable_for_bond_fund` for equity-only fields.
- Exclude true N/A fields from denominator before FQ4 missing-rate calculation.
- Do not hide real bond-lens facts. If a field is bond-relevant, keep it scorable and failing.
- Preserve `006597` correctness matched rows; do not add or edit golden answers.

Focused validation:

```text
uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py
git diff --check
```

Stop conditions:

- The implementation needs to lower FQ4 thresholds or change FQ0-FQ6 severity.
- The implementation would make genuinely missing bond-lens facts disappear from quality context.
- The implementation needs renderer or Service/CLI behavior changes.
- Same-source evidence does not prove the fields are N/A for bond funds.

### Slice 2B: Bond Extractor / Anchor Implementation

Allowed production files, only if later authorized by same-source evidence:

- Narrow extractor module that owns the proven field.
- `fund_agent/fund/extraction_snapshot.py` only if snapshot exposure is the actual gap.
- `fund_agent/fund/extraction_score.py` only if comparable / score projection is the actual gap.
- `fund_agent/fund/README.md` only for required Fund package docs sync.

Tests:

- Existing focused extractor tests for the owning module.
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py` if quality output changes.

Validation:

```text
uv run pytest <focused extractor tests> tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
uv run pytest tests/fund/test_quality_gate.py -q
uv run ruff check <changed production/test files>
git diff --check
```

Stop conditions:

- The field requires broad new bond analytics rather than a narrow extractor fix.
- Evidence anchor cannot be tied to annual-report section/table/row.
- Implementation would require direct PDF/cache/source helper access.

### Slice 2C: Source Recovery / Replacement

Allowed operations:

- Evidence-only public CLI probes for candidate replacements.
- If replacement succeeds, write tracked evidence artifact; do not implement source changes.

Possible implementation files only for a later separate source-boundary gate:

- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/documents/models.py`
- focused document tests under `tests/fund/documents/`

This plan does **not** authorize those source changes.

Validation for evidence-only:

```text
uv run fund-analysis extraction-snapshot --run-id baseline-coverage-triage-<code>-2024 --fund-code <code> --report-year 2024
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/baseline-coverage-triage-<code>-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/baseline-coverage-triage-<code>-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json
uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/baseline-coverage-triage-<code>-2024/score.json
git diff --check
```

Stop conditions:

- Replacement candidate uses fallback with unknown upstream category.
- Any fail-closed source category appears.
- Recovery requires modifying source fallback semantics.

### Slice 2D: FOF Taxonomy

Evidence-only first:

- Probe pure FOF candidates through public CLI / snapshot path.
- If no pure FOF is found, produce a taxonomy decision plan; do not implement.

Possible implementation files only after accepted taxonomy plan:

- `fund_agent/fund/fund_type.py`
- `tests/fund/test_fund_type.py` or current fund-type test owner if differently named.
- Fund README only if public behavior changes.

Stop conditions:

- The plan would count QDII-FOF as pure FOF without explicit taxonomy decision.
- Taxonomy change would require renderer, Service/CLI, quality gate, or golden corpus changes in the same gate.

## Non-Goals

- No renderer changes.
- No FQ0-FQ6 weakening, threshold lowering, or severity changes.
- No Service/CLI default behavior changes.
- No Host/Agent/dayu work.
- No `FundDocumentRepository`, source fallback, concrete source adapter, PDF cache, or download helper semantic changes.
- No direct PDF/cache/source helper access.
- No extractor changes unless a later accepted implementation slice proves same-source need.
- No fixtures, durable baseline, golden corpus, or curated golden rows.
- No explicit parameter hidden in `extra_payload` or free-form dicts.
- No GitHub mutation.

## Verifier Matrix

| Gate type | Command | Required? |
|---|---|---|
| Plan-only closeout | `git diff --check` | Yes. |
| Evidence-only bond triage | `uv run fund-analysis extraction-snapshot --run-id baseline-coverage-triage-006597-2024 --fund-code 006597 --report-year 2024` | If Subgate 1 is authorized. |
| Evidence-only score | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/baseline-coverage-triage-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/baseline-coverage-triage-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json` | If snapshot exists. |
| Evidence-only quality gate | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/baseline-coverage-triage-006597-2024/score.json` | If score exists. |
| Replacement candidate smoke | `uv run python scripts/selected_funds_smoke.py --code <candidate> --report-year 2024 --output-dir reports/smoke/baseline-coverage-triage-20260527` | Only with controller-approved candidate list. |
| Bond score implementation tests | `uv run pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q` | Only if Slice 2A implementation is authorized. |
| Extractor / anchor implementation tests | `uv run pytest <focused extractor tests> tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q` | Only if Slice 2B implementation is authorized. |
| Ruff | `uv run ruff check <changed files>` | Only if implementation is authorized. |

## Acceptance Criteria

Subgate 1 is accepted when:

- `006597` missing fields are classified by same-source evidence into root-cause categories.
- Index/QDII fallback-blocked rows are either still excluded with explicit reason or replaced by clean candidates.
- FOF remains `data_gap` unless a pure FOF candidate is found or a taxonomy plan is opened.
- All bulky output is in ignored scratch paths.
- `git diff --check` passes.

Authorize Slice 2A implementation only when:

- Same-source evidence proves one or more `006597` failing fields are not applicable for `bond_fund`.
- The implementation can preserve FQ0-FQ6 semantics by changing score/fund-quality applicability, not quality-gate severity.

Authorize Slice 2B implementation only when:

- Same-source evidence proves annual-report facts exist and current extraction / anchor / score projection misses them.

Authorize source-boundary implementation only when:

- Candidate replacement fails and the only remaining blocker is inability to observe safe upstream failure category through public surfaces.
- A separate source-boundary plan/review accepts exact file scope.

Golden corpus v1 may become eligible only when:

- At least five representative clean candidates across at least half target fund-type slots are repository-verified.
- No included candidate has `unknown_upstream_failure_category`, fail-closed source category, `taxonomy_pending`, or `probe_only`.
- No included clean candidate is quality-gate blocked.
- Same-year golden coverage is separated from missing coverage and no correctness mismatch remains.
- A curated-fixture / golden-corpus gate explicitly authorizes tracked paths and review criteria.

## Recommendation

Authorize **Subgate 1 evidence-only triage** next. Do not authorize implementation yet.

Rationale:

- The strongest concrete blocker is `006597` quality-gate block, but current evidence does not yet prove whether to fix extraction, change bond field applicability, or add bond-lens evidence policy.
- Coverage is also below target, but source recovery / FOF taxonomy can proceed as evidence-only probing without touching source semantics.
- A big-bang implementation would risk weakening FQ behavior or baking a taxonomy decision into code without accepted evidence.

## Validation

- `git diff --check`: passed.
