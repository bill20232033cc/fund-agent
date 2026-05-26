# release-maintenance bond-lens contract + baseline coverage recovery plan - 2026-05-27

> Worker: AgentCodex planning worker
> Scope: plan/review 前置 artifact only
> Output path: `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-20260527.md`

## 0. Scope Guard

本 artifact 只做 code-generation-ready plan，不授权实现、不提交、不 push、不创建 PR。

本次读取的当前真源：

- `AGENTS.md`
- `docs/design.md` 当前设计章节：fund type、CHAPTER_CONTRACT / preferred_lens、ReportEvidenceBundle / Fact-Evidence、quality gate、baseline / golden
- `docs/implementation-control.md` Startup Packet、Next Entry Point、Open Residuals、Active Gate Ledger
- 当前 accepted artifacts：small baseline corpus v1、baseline coverage/source/taxonomy/bond triage、share_change focused implementation

`docs/reviews/` 仅作为 accepted evidence chain；历史 archive 不覆盖 Startup Packet 或 `docs/design.md` 当前设计。

## 1. Startup Packet Replay

| Item | Current state / plan interpretation |
| --- | --- |
| Current phase | `release maintenance` |
| Current gate before this artifact | `share_change focused implementation accepted locally` |
| Next entry point | `bond-lens contract design + baseline coverage recovery plan/review` |
| Latest accepted checkpoint | Branch HEAD observed as `5f07019`; Startup Packet says use latest branch HEAD for exact hash |
| Design truth | `docs/design.md` v2.2 current design sections |
| Control truth | `docs/implementation-control.md` Startup Packet / current gate / next entry point / open residuals |
| Current architecture guardrail | Four-layer target `UI -> Service -> Host -> Agent`; current deterministic path remains Service -> `fund_agent/fund` Agent-layer fund capability |
| Durable baseline / golden status | blocked; no sample may be promoted in this gate |
| Required review route | MiMo + GLM plan review checklist in this artifact; controller decides acceptance |

Allowed in the next reviewed sub-gates:

- plan/review first;
- bond-lens evidence-contract design for `bond_fund`;
- evidence-only diagnostics through public CLI / repository-verified public paths;
- candidate recovery or replacement planning for index/QDII/pure FOF coverage;
- tracked summary artifacts under `docs/reviews/`;
- scratch/bulk outputs under `/tmp/...` or ignored `reports/...`;
- `git diff --check` and scoped validation commands.

Forbidden until a later accepted implementation plan explicitly narrows scope:

- renderer changes;
- FQ0-FQ6 semantic weakening or threshold changes;
- Service/CLI default behavior changes;
- Host/Agent package creation or `dayu.host` / `dayu.engine` runtime integration;
- `FundDocumentRepository` source strategy or fallback semantics changes;
- direct source helper/downloader/cache/PDF access from Service/UI/quality gate/renderer;
- extractor logic changes;
- golden corpus, durable baseline, fixture promotion;
- passing explicit parameters through `extra_payload`;
- GitHub mutation.

Verifier matrix for this plan gate:

| Verifier | Required result |
| --- | --- |
| `git diff --check` | must pass and be recorded below |
| Scope file check | only this plan artifact is created by this worker; pre-existing untracked files are unrelated |
| Review | MiMo + GLM should review against the checklist in section 10 |
| Controller decision | required before any implementation or evidence sub-gate proceeds |

## 2. Reconciliation: share_change Accepted, 006597 Still Blocked

`share_change` focused implementation is accepted because it safely improved deterministic share-class mapping:

- supports A-Z share-class labels beyond A/C;
- uses same-source §2 subordinate fund name / trading-code rows;
- preserves exact fund-code header priority;
- rejects default A-class, first non-empty column, total-share column, other-code column, and duplicate same-class ambiguity;
- fixed A-Z bare-suffix false-positive risk for ETF/LOF/NAV-like labels;
- passed focused tests, ruff, 006597 public snapshot/score/quality-gate rerun, and diff check.

The real `006597` / 2024 row still cannot enter golden corpus v1 because accepted post-run evidence still reports:

- `share_change`: `missing`; note remains `§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别`;
- P1 failed fields remain `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`;
- quality gate status remains `block`;
- missing-field rate remains 35.7%, above the FQ4 block threshold;
- correctness matched only the comparable covered golden rows and does not prove missing bond-lens facts are available or inapplicable.

Conclusion: the implementation was correct because it refused to guess. The baseline/golden decision is also correct because a repository-verified document with a blocked field contract cannot become durable baseline or golden material.

## 3. First-Principles Bond Contract Decision

### 3.1 Problem Statement

`docs/design.md` says `bond_fund` lens prioritizes duration, credit, leverage, liquidity, and drawdown; Chapters 4 and 6 are core, Chapters 2 and 5 are high priority. Current `holdings_snapshot` scoring semantics, however, are equity-shaped: `extraction_score.py` treats `holdings_snapshot` coverage as direct stock top-ten / all-stock-investment-details coverage.

For a bond fund, requiring stock top-ten / industry distribution as P1 evidence is a category error. But marking the field simply N/A would also be wrong, because bond investors still need holdings/risk evidence to assess credit, duration, liquidity, leverage, concentration, redemption pressure, and drawdown.

### 3.2 Contract Decision

Recommended decision: `holdings_snapshot` becomes fund-type-dependent for `bond_fund`.

Do not continue requiring equity-shaped `holdings_snapshot` for `bond_fund`. Do not make the whole risk evidence slot N/A. Replace the scoring meaning of this slot, for bond funds only, with an explicit `bond_holdings_risk_evidence` contract. The old field name may remain as a transitional snapshot field only if the implementation records an explicit applicability decision and does not count missing stock holdings against bond-fund quality.

### 3.3 Required Evidence Contract

For `bond_fund`, the required evidence should be expressed as a typed, fund-type-specific contract rather than a generic table scrape:

| Evidence group | Required evidence | Design source / chapter reason |
| --- | --- | --- |
| Duration / rate risk | portfolio duration, average remaining maturity, interest-rate sensitivity disclosure, or accepted explicit data gap | Bond lens; Chapter 6 core risk; Chapter 5 current stage |
| Credit risk | bond rating distribution, credit bond exposure, non-policy-financial bond exposure, default/impairment risk disclosure, or accepted explicit data gap | Bond lens; Chapter 6 core risk |
| Leverage / liquidity | leverage ratio, repo/financing exposure, liquidity risk note, concentration of large redemptions if disclosed, or accepted explicit data gap | Bond lens; Chapter 4 investor experience; Chapter 6 risk |
| Asset allocation / holdings mix | bond / cash / financial instruments mix, top bond holdings if disclosed, issuer or sector concentration if disclosed, or accepted explicit data gap | Product process evidence; not equity top-ten substitute |
| Drawdown / stress evidence | max drawdown, volatility, stress threshold status, or accepted derived risk calculation with source anchors | 有知有行 behavior / stable-money lens; Chapter 4/6 |
| Redemption / share pressure | share change / subscription-redemption trend if deterministically extractable, or explicit ambiguity/data-gap | Chapter 4 investor experience; baseline triage accepted `share_change` remains relevant to bond funds |

Minimum pass for future `bond_holdings_risk_evidence` should not require every group at once in the first implementation. A safe initial gate can require either:

- at least one direct annual-report anchor from duration/credit/leverage/asset-allocation risk evidence plus explicit data gaps for missing groups; or
- an explicit `bond_risk_evidence_status="insufficient"` that removes the equity-shaped `holdings_snapshot` false blocker but still emits a report-quality / quality-gate issue under a bond-specific taxonomy.

The second option is safer if source evidence is not yet available. It prevents false equity requirements without silently passing missing bond risk evidence.

### 3.4 allowed_na_reason

Allowed `N/A` semantics must be narrow:

| Field / slot | Allowed N/A reason | Not allowed |
| --- | --- | --- |
| equity-shaped `holdings_snapshot.top_holdings_status` for `bond_fund` | `not_applicable_to_bond_fund_equity_holdings`; must be paired with `bond_holdings_risk_evidence` requirement | `not_applicable` with no replacement evidence |
| stock/industry distribution subfields | `equity_holdings_not_required_for_bond_lens` | counting missing stock table as P1 fail |
| bond risk groups with no accepted source in current run | `bond_risk_evidence_not_yet_reviewed` or field-specific `data_gap` | pass/green status |
| investor_return | no bond N/A in this gate | treating missing direct investor return as bond inapplicable |
| nav_data annual-report anchor | no annual-report-anchor requirement for NAV cache in this gate | modifying annual-report extractor to fabricate anchors |

### 3.5 Failure Behavior

Recommended failure behavior:

- If fund type is unknown or conflicted: fail closed, keep generic required fields.
- If fund type is `bond_fund` and equity-shaped `holdings_snapshot` is missing: do not count equity top-ten missing as a bond P1 fail.
- If `bond_holdings_risk_evidence` is absent or unreviewed: emit a bond-specific issue, not a silent pass.
- If annual-report source identity, schema, or integrity is unsafe: preserve source fail-closed semantics; do not use Eastmoney fallback to hide `schema_drift`, `identity_mismatch`, or `integrity_error`.
- If only public CLI evidence is available and cannot prove source absence: classify as `needs_more_evidence`, not extractor fix.

### 3.6 Issue Taxonomy

Proposed issue taxonomy for later implementation/review:

| Issue code / category | Meaning | Severity recommendation |
| --- | --- | --- |
| `bond_lens_contract_gap` | Current contract requires equity-shaped evidence for a bond fund | material design issue; fix before golden |
| `bond_risk_evidence_missing` | Bond-specific risk evidence contract exists but no evidence/data-gap record is present | warn/block depending priority policy; do not pass |
| `bond_risk_anchor_missing` | Value exists but lacks accepted annual-report or external-source provenance | traceability issue |
| `bond_risk_data_gap_declared` | Accepted explicit missing/unavailable evidence with next validation question | warning/observation, excluded from false coverage |
| `equity_holdings_not_applicable_to_bond` | Stock holdings subfield not applicable because replacement bond contract is used | info/N/A denominator exclusion |
| `source_fail_closed_blocked` | Source failure category forbids fallback | block; unchanged semantics |
| `needs_more_evidence` | Public evidence cannot determine source absence vs extractor gap vs policy gap | planning/evidence residual; no implementation |
| `score_contract_gap` | Existing score/evidence model cannot represent valid non-annual-report or derived evidence | future contract work |

### 3.7 Design-Only vs Minimal Implementation Candidate

Design-only in this gate:

- naming and semantics of `bond_holdings_risk_evidence`;
- required evidence groups and allowed N/A reasons;
- issue taxonomy;
- decision that `holdings_snapshot` must be fund-type-dependent for `bond_fund`;
- rule that investor_return/nav_data are not solved by this bond-lens gate.

Possible later minimal implementation only after plan review/controller acceptance:

- add a fund-type applicability layer in `extraction_score.py` so `holdings_snapshot` equity subfields are excluded for `bond_fund`;
- add explicit score issue output for missing/unreviewed bond risk evidence instead of passing;
- add focused tests proving active/index/enhanced behavior remains unchanged and bond funds no longer fail because stock holdings are absent;
- optionally add a synthetic or reviewed snapshot fixture representing bond risk evidence status, without promoting durable golden/baseline.

Do not implement bond risk extraction from annual reports in the first minimal slice. That requires separate source/evidence proof.

## 4. Baseline Coverage Recovery Plan

### 4.1 Index / QDII Source Recovery

Rows:

- `110020` / 2024 / `index_fund`
- `017641` / 2024 / `qdii_fund`

Required plan:

1. Use only `FundDocumentRepository`-backed public/product paths or accepted source-reliability evidence paths.
2. Recover the original upstream failure category before durable baseline consideration.
3. Allow fallback only for `not_found` or `unavailable`.
4. Preserve fail-closed behavior for `schema_drift`, `identity_mismatch`, and `integrity_error`.
5. If failure category cannot be recovered, exclude the row or replace the candidate through a reviewed candidate-selection artifact.
6. Do not weaken fallback semantics or patch source helpers to make baseline coverage look better.

Candidate replacement criteria:

- same report year target unless controller accepts a year-specific reason;
- repository-verified annual report identity;
- no unknown fallback boundary;
- fund type resolves to the desired slot;
- snapshot/score/quality-gate commands can run through public CLI paths;
- not `probe_only`, not `unknown`, not fallback-blocked.

Stop conditions:

- recovered failure category is fail-closed;
- repository identity cannot be verified;
- candidate type does not match slot;
- only Eastmoney fallback can fetch the document without a safe upstream category;
- scratch output would need to become a durable fixture before review.

### 4.2 Pure FOF Coverage

Rows already recorded as gaps:

- `007721` is QDII-FOF/type-gap evidence, not pure FOF coverage.
- `017970` has QDII-FOF/type-gap plus fallback-blocked risk.

Plan:

1. Do not count QDII-FOF as pure `fof_fund` coverage unless a separate taxonomy/precedence gate accepts that behavior.
2. Select pure FOF candidates by stable disclosure: fund name/category contains `FOF` or `基金中基金`, and does not primarily classify as QDII under current accepted precedence unless taxonomy gate changes precedence.
3. Verify through `FundDocumentRepository` public path and current `classify_fund_type()` output.
4. Record candidates that become QDII-FOF as `taxonomy_pending`, not clean FOF.
5. If no pure FOF can be repository-verified, keep FOF as `data_gap` and do not lower the representative coverage target by pretending the slot is covered.

### 4.3 Durable Baseline / Golden Freeze

No durable baseline or golden corpus may be promoted from this gate.

Entry to future `golden answer corpus v1` remains blocked until:

- index and QDII are recovered or replaced with clean source boundaries;
- pure FOF is found or taxonomy gate explicitly resolves QDII-FOF handling;
- `006597` no longer quality-gate blocks, or a different clean bond candidate is reviewed and accepted;
- reviewed facts are frozen for the selected rows;
- a separate curated-fixture/golden gate accepts promotion.

## 5. 006597 Remaining Fields Handling

| Field | Current accepted status | Plan handling |
| --- | --- | --- |
| `share_change` | focused implementation accepted; real 006597 still ambiguous/missing | keep as residual data blocker; next action may be evidence-only diagnostics, not another extractor guess |
| `holdings_snapshot` | `bond_lens_contract_gap` | resolve by bond-specific contract and scoring applicability design first |
| `turnover_rate` | `needs_more_evidence` | do not infer applicability or source absence from public missing output; no implementation from absence |
| `holder_structure` | `needs_more_evidence` | same; require reviewed source/policy proof before implementation |
| `investor_return` | `score_contract_gap` | future fallback/projection evidence-contract work; not bond N/A and not immediate P1 blocker |
| `nav_data` | `score_contract_gap` for anchor/provenance | future external evidence provenance/source-contract work; do not modify annual-report extractor |

Root-cause rule: every future classification must be logic/data same-source. Public score/gate output may localize a failure, but it cannot by itself prove annual-report source absence.

## 6. Proposed Next Gate Split

### Gate A: Plan Review For This Artifact

Entry conditions:

- this artifact exists at the fixed path;
- `git diff --check` passes;
- no files except this artifact are changed by this worker.

Allowed files:

- `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-20260527.md`

Validation:

- `git diff --check`
- reviewer checklist in section 10

Stop conditions:

- MiMo/GLM find a material plan flaw;
- controller rejects or narrows the plan.

### Gate B: Bond-Lens Score Applicability Design

Goal:

- decide exact implementation shape for excluding equity-shaped `holdings_snapshot` semantics from `bond_fund` while preserving explicit bond risk evidence requirements.

Allowed files if later authorized:

- plan artifact under `docs/reviews/`;
- possibly `docs/design.md` only by controller after design acceptance;
- no source/test files in design-only gate.

Validation:

- `rg` references for `holdings_snapshot`, `bond_fund`, `FIELD_PRIORITY_BY_NAME`, `_record_is_covered`;
- `git diff --check`.

Stop conditions:

- plan would weaken FQ0-FQ6 globally;
- plan cannot preserve active/index/enhanced behavior;
- plan treats bond risk evidence as silent N/A.

### Gate C: Minimal Bond-Lens Score Implementation

Entry conditions:

- Gate B accepted by controller;
- explicit implementation plan accepted after MiMo/GLM review.

Allowed file range if later authorized:

- `fund_agent/fund/extraction_score.py`
- `tests/fund/test_extraction_score.py` or adjacent focused extraction-score tests
- `fund_agent/fund/README.md` only if public Fund package behavior documentation changes
- `tests/README.md` only if new test organization needs documentation
- tracked evidence artifact under `docs/reviews/`

Forbidden in Gate C:

- extractor logic;
- renderer;
- FQ0-FQ6 thresholds/severity semantics;
- Service/CLI;
- source strategy/helpers;
- golden/baseline fixtures.

Test/validation commands:

- `uv run pytest tests/fund/test_extraction_score.py -q`
- adjacent quality gate tests if applicability changes touch gate summaries
- `uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py`
- `git diff --check`
- optional public 006597 snapshot/score/quality-gate rerun as evidence only; expected result may remain `block` if bond risk evidence is still missing.

Stop conditions:

- any non-bond fund field priority/coverage behavior changes unexpectedly;
- 006597 becomes pass/warn only because evidence is suppressed without replacement bond issue;
- implementation needs annual-report parsing or source helper changes.

### Gate D: Source Recovery / Replacement Evidence For Index + QDII

Entry conditions:

- controller supplies approved candidate list or approves recovery commands;
- source fallback classification route is explicit.

Allowed files:

- tracked evidence artifact under `docs/reviews/`;
- scratch output only under `/tmp/...` or ignored `reports/...`.

Validation commands:

- public repository/product commands agreed by controller;
- extraction-snapshot / extraction-score / quality-gate for candidates that pass source boundary;
- `git diff --check`.

Stop conditions:

- upstream failure category is `schema_drift`, `identity_mismatch`, or `integrity_error`;
- fallback category remains unknown;
- candidate cannot be repository-verified.

### Gate E: Pure FOF Candidate Evidence Or Taxonomy Decision

Entry conditions:

- controller supplies approved candidate list or authorizes candidate selection evidence route;
- explicit decision whether this is pure FOF search or QDII-FOF taxonomy design.

Allowed files:

- plan/evidence artifact under `docs/reviews/`;
- possible `docs/design.md` update only by controller after accepted taxonomy design;
- no production code unless a later implementation gate is accepted.

Validation:

- `classify_fund_type()` evidence through public structured path;
- no QDII-FOF counted as pure FOF without accepted taxonomy;
- `git diff --check`.

Stop conditions:

- only QDII-FOF candidates are found;
- candidate uses unsafe fallback;
- taxonomy change would affect current fund-type precedence without design review.

### Gate F: 006597 Same-Source Diagnostic Evidence

Entry conditions:

- controller explicitly authorizes evidence-only diagnostics;
- route uses public CLI or accepted repository abstraction, not direct file/cache/helper reads.

Allowed files:

- tracked evidence artifact under `docs/reviews/`;
- scratch output only.

Stop conditions:

- diagnostics require direct PDF/cache/source-helper access outside repository abstraction;
- evidence still cannot tie §2 share class to a unique §10 column.

## 7. Non-Goals And Hard Prohibitions

This plan explicitly forbids:

- renderer changes;
- FQ0-FQ6 rule weakening, threshold changes, or severity downgrades;
- Service/CLI behavior or command surface changes;
- Host/Agent/dayu runtime/package work;
- `FundDocumentRepository` source strategy changes;
- source helper/downloader/cache/PDF direct access or fallback semantic changes;
- extractor logic changes;
- golden corpus or durable baseline promotion;
- fixture promotion;
- `extra_payload` parameter tunneling;
- GitHub mutation.

## 8. Code-Generation-Ready Implementation Notes For Future Gate C

If controller later authorizes minimal score implementation, the implementation worker should:

1. Start from `fund_agent/fund/extraction_score.py`.
2. Add explicit constants for bond-specific applicability rather than string literals scattered through code.
3. Keep `_record_is_covered()` equity semantics intact for non-bond funds.
4. Add a fund-type-aware path in `_scorable_records()` or an adjacent helper so `holdings_snapshot` equity subfields are excluded for `bond_fund`.
5. Emit/retain a bond-specific issue path so absence of bond risk evidence does not pass silently.
6. Add focused tests:
   - active fund missing `holdings_snapshot` still behaves as before;
   - index/enhanced behavior stays unchanged;
   - bond fund missing equity `holdings_snapshot` is not counted as stock-holdings coverage failure;
   - bond fund with no bond risk evidence records an explicit bond issue / non-scoring-ready status;
   - unknown/conflicted fund type remains conservative.
7. Do not touch extraction, renderer, Service/CLI, source strategy, or golden files.

## 9. Validation For This Artifact

Commands to run after creating this artifact:

| Command | Result |
| --- | --- |
| `git diff --check` | pass, exit 0 |

Observed workspace note before creating this artifact:

- Pre-existing untracked files were present and unrelated: `docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md`, `docs/reviews/repo-review-20260526-231040.md`, `docs/tmux-agent-memory-store.md`.
- This worker must not modify or delete those files.

## 10. Review Questions For MiMo / GLM

Please review this plan against these questions:

1. Does the plan correctly reconcile accepted `share_change` implementation with real `006597` still being quality-gate blocked?
2. Is `holdings_snapshot` as fund-type-dependent for `bond_fund` the right first-principles decision, rather than continuing equity requirements or marking the slot silent N/A?
3. Does the proposed `bond_holdings_risk_evidence` contract cover duration, credit, leverage/liquidity, allocation/holdings mix, drawdown/stress, and redemption/share pressure without over-implementing extraction?
4. Are `allowed_na_reason`, failure behavior, and issue taxonomy explicit enough to prevent silent quality-gate weakening?
5. Does Gate C preserve current FQ0-FQ6 semantics while allowing field applicability to become bond-aware?
6. Does the plan keep `turnover_rate` and `holder_structure` as `needs_more_evidence` and avoid implementing from absence?
7. Does the plan keep `investor_return` and `nav_data` in future score/evidence-contract work rather than misclassifying them as bond N/A?
8. Does the source recovery plan preserve fallback fail-closed semantics for `110020` and `017641`?
9. Does the FOF plan avoid counting QDII-FOF as pure FOF without a taxonomy gate?
10. Are file ranges, stop conditions, and validation commands narrow enough for a safe next implementation gate?
