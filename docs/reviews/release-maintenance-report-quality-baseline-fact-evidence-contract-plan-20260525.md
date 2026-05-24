# Release Maintenance Report-Quality Baseline / Fact-Evidence Contract Plan

> Date: 2026-05-25
> Branch: `codex/v0-release-readiness-plan`
> Gate: `release-maintenance report-quality baseline / Fact-Evidence contract candidate selection / plan-review`
> Plan status: candidate for plan review

## Step Self-Check

- Current role: specialist planning Agent; produce an executable design plan artifact only.
- Truth sources: `AGENTS.md`; `docs/design.md` current design, especially §5.4 to §5.4.3; `docs/implementation-control.md` Startup Packet / Current gate / Next entry point; accepted artifacts `docs/reviews/release-maintenance-chapter-audit-report-pipeline-design-implementation-20260524.md`, `docs/reviews/release-maintenance-methodology-coverage-matrix-plan-20260525.md`, and `docs/reviews/release-maintenance-methodology-coverage-matrix-implementation-20260525.md`.
- Historical evidence boundary: older `docs/reviews/` material may explain why a constraint exists, but old six-layer, Application, Runtime / Engine wording is superseded and must not drive this plan.
- Scope boundary: design plan only; no source, tests, renderer, quality gate, Host/Agent package, Dayu runtime, report output, golden answer, commit, push, or PR.
- Validation boundary: document-level `rg` checks and `git diff --check` only. `pytest` / `ruff` are not required because this plan changes no executable code or tests.

## Objective

Create the next report-quality gate as an observable baseline, not as a prose rewrite.

The next executable gate should first choose a small representative baseline corpus, define a report-quality scoring schema, and define a Fact / Evidence input contract. Only after scoring failures are categorized should the project choose between data-source / extraction iteration and template / writing iteration.

This follows `docs/design.md` §5.4: report quality must become measurable and reproducible before renderer or writing changes.

## Current Architecture Boundary

The current production path remains deterministic `fund-analysis analyze` with v0 8-chapter Markdown output. The target architecture is still:

```text
UI -> Service -> Host -> Agent
```

Boundary consequences for this plan:

- UI may display future scoring outputs, but must not perform fund analysis, extraction, scoring, or audit decisions.
- Service may orchestrate a future scoring use case, select quality policy, and assemble explicit input contracts.
- Host is not created in this gate. If future session / run lifecycle, cancel, resume, outbox, or chapter-task concurrency is required, that must be a separate Host gate using `dayu.host`.
- Agent-layer `fund_agent/fund` owns fund type, preferred_lens, CHAPTER_CONTRACT, ITEM_RULE, evidence anchors, extraction facts, and audit semantics.
- Agent execution runtime is not created in this gate. If future tool loop, runner, ToolRegistry, ToolTrace, or context budget is required, that must be a separate Agent gate using `dayu.engine`.
- Explicit business parameters such as fund code, report year, report type, scoring dimensions, corpus id, source policy, fund type, lens, chapter id, and audit policy must be typed fields. They must not be hidden in `extra_payload` or `extra_payloads`.

## Slice 1: Small Baseline Corpus Candidate Selection

### Selection Goal

Choose a small corpus that is broad enough to expose report-quality failure modes, but small enough for manual review. The initial target is 6 to 8 fund-year cases, with expansion only after the scoring schema proves useful.

### Required Coverage

The corpus must cover fund type lens before general analysis:

| Required slot | Minimum target | Why it matters |
|---|---:|---|
| `active_fund` | 1 to 2 | Tests People / Process, manager consistency, structural vs stage alpha, holdings and cost evidence. |
| `index_fund` | 1 | Tests index rules, tracking evidence, low-cost Beta, benchmark identity, and thermometer discipline. |
| `enhanced_index` | 1 | Tests separation between structural enhancement and stage excess return, plus tracking constraints. |
| `bond_fund` | 1 | Tests duration / credit / leverage / liquidity, downside experience, and risk-control writing. |
| `qdii_fund` | 1 | Tests overseas exposure, currency / market risk, fee and benchmark interpretation. |
| `fof_fund` | 0 to 1 in first pass, required by second pass | Tests allocator process, underlying fund evidence, four-money suitability, and double-fee discussion. |

If QDII or FOF annual reports cannot be repository-verified in the first pass, the plan must record a `data_gap` and keep the corpus at 5 to 6 cases rather than accepting unverified substitutes.

### Annual Report Identity Verification

Every corpus candidate must pass annual-report identity checks before it can be scored:

| Check | Required evidence | Failure category |
|---|---|---|
| Fund code / fund id identity | Repository metadata or report §2 identity matches requested fund. | `identity_mismatch` if conflicting. |
| Share class identity | Report name and share-class text are explicit when class-specific fields are scored. | `identity_mismatch` or `data_gap` if ambiguous. |
| Report year | Annual report year equals requested year. | `identity_mismatch`. |
| Report type | Source identifies annual report, not interim / quarterly / prospectus. | `identity_mismatch`. |
| Source response contract | Source fields and attachment shape match repository expectation. | `schema_drift`. |
| PDF integrity | Repository accepts content type, file header, and parsed report integrity. | `integrity_error`. |
| Temporary source availability | Network, timeout, or upstream outage is explicit. | `unavailable`. |
| Missing annual report | Source responds normally but target fund-year annual report is absent. | `not_found`. |

Fallback is allowed only for `not_found` and `unavailable`. `schema_drift`, `identity_mismatch`, and `integrity_error` must fail closed and remain visible in the candidate record.

### FundDocumentRepository Boundary

All production annual-report access in future implementation must go through `FundDocumentRepository` or public Fund extraction APIs that themselves use `FundDocumentRepository`.

Forbidden in the corpus gate:

- Directly reading annual-report PDF files from cache.
- Calling a concrete EID / Eastmoney / download helper from Service, UI, renderer, quality gate, or a scoring script.
- Treating local parsed cache existence as proof of annual-report identity.
- Manually pasting annual-report facts into long-lived fixtures without recording evidence anchors and reviewer state.

### Manual Review State

Corpus entries must carry explicit review status:

| State | Meaning | Allowed next action |
|---|---|---|
| `candidate` | Selected by fund type / year only; annual report not yet verified. | Repository verification only. |
| `repository_verified` | Annual-report identity and source failure semantics checked through repository boundary. | Fact prefill and evidence extraction. |
| `fact_prefill_generated` | Structured facts and anchors generated, not human-reviewed. | Manual review. |
| `fact_prefill_reviewed` | Human accepted or corrected each scored field with evidence location. | Scoring-ready. |
| `scoring_ready` | Facts, anchors, gaps, and quality context are frozen for the first scoring run. | Report-quality scoring. |
| `accepted_baseline` | Scoring input is curated as durable baseline after review. | May become long-lived fixture in a separate implementation gate. |

Unreviewed output is never a golden answer and must not be used to claim correctness.

### Ignored Local Run Artifacts

The following outputs must stay in ignored run directories unless a later curated-fixture gate explicitly promotes a reviewed subset:

- `reports/scoring-runs/`: scoring JSON, markdown summaries, failure matrices, score deltas, reviewer scratch summaries.
- `reports/data-source-runs/`: source feasibility probes, repository refresh attempts, extraction debugging snapshots.
- `reports/writing-runs/`: draft report variants, chapter-writing experiments, prompt / template comparisons.
- `reports/smoke/`: local analyze / checklist smoke outputs.
- `reports/quality-gate-runs/` and `reports/extraction-snapshots/`: existing ignored quality and extraction diagnostics.
- Temp directories used during repository or scoring probes.

Durable artifacts should be limited to this plan, later review artifacts under `docs/reviews/`, and separately approved curated fixtures.

## Slice 2: Report-Quality Scoring Schema Candidate

The scoring schema should be observational at first. It must not replace current FQ0-FQ6 quality gate and must not change v0 renderer behavior.

### Score Record Shape

Each score issue should be locatable:

```text
score_run_id
corpus_id
fund_code
report_year
fund_type
preferred_lens
chapter_id
dimension
rule_id
severity
score
field_path
evidence_anchor_id
source_boundary
failure_category
observed_text_or_value_ref
expected_fact_or_rule_ref
recommended_next_gate
review_status
```

`observed_text_or_value_ref` and `expected_fact_or_rule_ref` should point to structured excerpts or reviewed fact ids, not duplicate large source text.

### Dimensions

| Dimension | What is scored | Locating key | Typical failure category | Next-gate bias |
|---|---|---|---|---|
| `fact_coverage` | Whether required facts exist for CHAPTER_CONTRACT / ITEM_RULE and fund-type lens. | `chapter_id`, `must_answer`, `field_path`, `data_gap.id` | `missing_fact`, `unsupported_lens`, `not_disclosed` | Data-source / extraction if fact should exist; writing if gap is not stated. |
| `extraction_correctness` | Whether extracted facts match reviewed annual-report evidence. | `field_path`, `evidence_anchor_id`, reviewed value | `wrong_value`, `wrong_unit`, `wrong_date`, `wrong_share_class`, `wrong_table` | Data-source / extraction. |
| `evidence_traceability` | Whether every key number and judgment has an EvidenceAnchor or derived calculation source. | `chapter_id`, `claim_id`, `evidence_anchor_id` | `missing_anchor`, `weak_anchor`, `derived_source_missing` | Evidence Store / anchor generation. |
| `chapter_contract_completeness` | Whether chapter answers must_answer and avoids must_not_cover. | `chapter_id`, `contract_item_id` | `must_answer_missing`, `must_not_cover_violation`, `item_rule_missing` | Template / chapter plan / rule audit. |
| `final_judgment_consistency` | Whether final judgment consumes accepted prior conclusions and quality context only. | `final_judgment.field`, `source_chapter_ids` | `unsupported_conclusion`, `quality_context_ignored`, `strong_conclusion_with_core_gap` | Final judgment contract / assembly audit. |
| `investment_advice_boundary` | Whether wording avoids buy/sell advice, return prediction, position sizing, and unsupported causality. | `chapter_id`, `paragraph_id`, `wording_rule_id` | `buy_sell_advice`, `return_forecast`, `position_advice`, `unsupported_causality` | Wording audit / LLM audit in a later gate. |
| `readability_actionability` | Whether reader gets a concise rationale and next minimal validation question. | `chapter_id`, `summary_id`, `next_question_id` | `field_dump`, `unclear_action`, `missing_next_question` | Template / writing iteration. |

### Scoring Scale

Use a simple per-dimension score before weighted totals:

| Score | Meaning |
|---:|---|
| 0 | Blocking: key claim is unsupported, wrong, unsafe, or violates a hard boundary. |
| 1 | Material issue: report can be read, but decision quality is impaired. |
| 2 | Minor issue: mostly correct, with localization or wording gaps. |
| 3 | Pass: meets current contract for the available evidence. |
| `N/A` | Dimension is not applicable for this fund type / chapter, with reason. |

Weighted total is optional in the first implementation. The mandatory output is issue localization and next-gate recommendation.

### Methodology Matrix Constraints

The scoring schema must cite `docs/design.md` §5.4.3 for every dimension:

- Morningstar dimensions are coverage lenses only: People, Process, Parent, Price, Performance. The report must not output Morningstar medals, stars, or ratings.
- 有知有行 dimensions are behavior-safety lenses: R=A+B-C, fund type first, knowledge / emotion / willingness, four-money suitability, thermometer / valuation-state discipline, and next minimal validation question.
- Fund type priority changes the scoring denominator. For example, People is core for `active_fund`, low priority for `index_fund`; tracking evidence is core for `index_fund` / `enhanced_index`, not a generic denominator for every fund.
- CHAPTER_CONTRACT / preferred_lens / ITEM_RULE define chapter obligations, not generic prose preferences.
- Evidence source hierarchy must be preserved: fund disclosures are strongest for fund facts; official index / regulatory sources support index and system facts; manager interviews support stated philosophy only; third-party ratings and tools support comparison only.
- Missing facts degrade explicitly to `未披露`, `数据不足`, or `下一步最小验证问题`; they must not be converted into inferred alpha, risk, intent, or advice.
- Future 8-chapter to 0-10 mapping remains a boundary. Scoring may record candidate mapping fields, but must score current v0 8 chapters until a separate gate changes the renderer.

## Slice 3: Fact / Evidence Contract Candidate

The future evidence bundle is the only allowed input for report-quality scoring and later chapter writing. It should be built from repository-derived facts, derived calculations, evidence anchors, explicit gaps, and quality context.

### Top-Level Shape

```text
ReportEvidenceBundle
  bundle_id
  corpus_id
  fund_code
  report_year
  fund_type
  preferred_lens
  source_documents
  facts
  derived_calculations
  evidence_anchors
  data_gaps
  quality_context
  review_status
```

All business fields above must be explicit typed fields in the future implementation. They must not be carried through `extra_payload` / `extra_payloads`.

### `facts`

Purpose: structured observed facts used by scoring and writing.

Required field semantics:

| Field | Meaning |
|---|---|
| `fact_id` | Stable id within bundle, such as `profile.fund_name` or `fees.management_fee`. |
| `category` | Domain group: identity, fund_type, benchmark, holdings, performance, fee, manager, risk, holders, valuation, thermometer, etc. |
| `value` | Normalized value. |
| `raw_value_ref` | Pointer to reviewed source excerpt or structured parsed cell, not a direct PDF path. |
| `unit` | Percent, CNY, date, text, count, ratio, or explicit `not_applicable`. |
| `period` | Reporting period or effective date. |
| `source_anchor_ids` | EvidenceAnchor ids supporting the fact. |
| `extraction_mode` | Direct observed disclosure, derived from parsed table, external official source, unavailable, missing, or reviewed manual correction. |
| `review_status` | Generated, reviewed, rejected, or deferred. |
| `failure_category` | Empty on success; otherwise one of the explicit source / data-gap categories. |

Source boundary: facts must come from current extractors or later `FundDocumentRepository`-derived structured sources. Scoring cannot directly read PDF, cache, or source adapters.

### `derived_calculations`

Purpose: auditable calculations such as R=A+B-C, cost estimates, thermometer state, pressure tests, and final judgment support.

Required field semantics:

| Field | Meaning |
|---|---|
| `calculation_id` | Stable id, such as `return_attribution.alpha_beta_cost`. |
| `formula_name` | Named formula or rule set. |
| `input_fact_ids` | Facts consumed by the calculation. |
| `input_anchor_ids` | Anchors inherited from inputs. |
| `output_value` | Computed result or structured result. |
| `assumptions` | Explicit assumptions; empty if none. |
| `calculation_status` | computed, blocked_by_missing_fact, blocked_by_conflict, not_applicable. |
| `degradation` | Required report wording when calculation cannot run. |

Missing inputs must block calculation rather than fabricating values. For example, missing R/B/C inputs means no pseudo-alpha; the report writes a data gap and next minimal validation question.

### `evidence_anchors`

Purpose: source traceability for facts, calculations, and report claims.

Required field semantics:

| Field | Meaning |
|---|---|
| `anchor_id` | Stable bundle-local id. |
| `source_kind` | annual_report, prospectus, fund_contract, official_index, regulatory, external_api, derived, reviewed_note. |
| `document_year` | Year for annual reports or disclosure year. |
| `section_id` | Section such as `§7.4.10.2`. |
| `page_number` | Page when available. |
| `table_id` | Table id when available. |
| `row_locator` | Row / column locator when available. |
| `source_strength` | fund_disclosure, official_reference, manager_statement, third_party_reference, derived. |
| `note` | Short reviewer note explaining what the anchor proves. |

Evidence anchors may point to derived calculations only when the calculation lists its input fact ids and source anchors.

### `data_gaps`

Purpose: make missing, conflicted, or unsafe facts explicit.

Required field semantics:

| Field | Meaning |
|---|---|
| `gap_id` | Stable id. |
| `related_fact_id` | Fact that could not be produced or trusted. |
| `chapter_ids` | Chapters affected. |
| `failure_category` | `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, `not_disclosed`, `ambiguous`, `not_applicable`, `unsupported_source`, `manual_review_required`. |
| `fallback_allowed` | Boolean derived from failure category. |
| `fallback_used` | Boolean and source metadata when fallback occurred. |
| `degradation_text` | Required report wording: `未披露`, `数据不足`, or next minimal validation question. |
| `blocks_scoring_dimensions` | Dimensions that must be N/A or blocking because of the gap. |

Source failure categories from AGENTS / design remain strict: fallback only for `not_found` and `unavailable`; fail closed for `schema_drift`, `identity_mismatch`, and `integrity_error`.

### `quality_context`

Purpose: context for confidence, warning, and blocking semantics. It must not replace facts.

Required field semantics:

| Field | Meaning |
|---|---|
| `fq_gate_status` | Current FQ0-FQ6 quality gate status when available: pass, warn, block, not_run. |
| `fq_issues` | Current quality gate issue summaries by rule id. |
| `programmatic_audit_status` | Current programmatic audit result and checked rules. |
| `report_quality_scores` | Observational scores from this new baseline gate. |
| `known_residuals` | Accepted residuals that affect interpretation. |
| `judgment_constraint` | Whether final judgment may be strong, cautious, or must be blocked / downgraded. |

Quality context can change confidence and warnings. It cannot manufacture missing facts or override an unsupported final judgment.

## Slice 4: Data / Extraction vs Template / Writing Decision Standard

The next gate must be chosen from scoring failure categories, not from subjective report taste.

| Dominant failure pattern | Root-cause interpretation | Next gate |
|---|---|---|
| Low `fact_coverage` because expected facts are absent from extractors but present in reviewed report evidence. | Data model or extractor gap. | Data-source / extraction implementation gate. |
| Low `extraction_correctness` with wrong value, unit, date, table, or share class. | Extractor or normalization bug. | Data-source / extraction implementation gate. |
| Low `evidence_traceability` with correct fact but missing / weak anchor. | Evidence Store / anchor generation gap. | Evidence contract / anchor implementation gate. |
| Facts are available and anchored, but `chapter_contract_completeness` fails. | Template contract, chapter plan, or rule audit gap. | Template / CHAPTER_CONTRACT / rule-audit gate. |
| Final judgment ignores gaps, quality context, or accepted chapter conclusions. | Assembly / final judgment contract gap. | Final judgment contract / assembly audit gate. |
| Wording violates advice boundary despite correct facts. | Writing safety / audit gap. | Wording audit, then later LLM audit only after separate gate. |
| Report is factual but unreadable or lacks next validation question. | Writing / summary ergonomics gap. | Template / writing iteration gate. |
| Most failures are `not_found` / `unavailable`. | Source availability or retry policy question. | Source reliability gate, preserving fallback taxonomy. |
| Any `schema_drift`, `identity_mismatch`, or `integrity_error`. | Source contract safety issue. | Fail-closed source contract gate before scoring expansion. |

Tie-breaker: data-source / extraction correctness precedes template writing. A polished template built on wrong or missing facts worsens decision safety.

## Slice 5: Future 8-Chapter to 0-10 Mapping Boundary

This plan may add candidate metadata that maps current v0 chapter ids to future 0-10 chapter ids, but scoring must use current 8-chapter output as the target until a separate renderer / chapter-pipeline gate is accepted.

Accepted boundary:

- Current v0 8 chapters remain unchanged.
- Future Chapter 0 summary is generated last from accepted conclusions only.
- Future Chapter 10 final judgment is generated after Chapters 1-9 and consumes accepted conclusions plus quality context only.
- Exact split from current Chapter 1 / 2 / 3 into future 0-10 remains a later design gate.
- No current renderer changes are allowed in this gate.

## Non-Goals

- Do not change renderer output or current v0 8-chapter structure.
- Do not change current FQ0-FQ6 quality gate behavior.
- Do not implement LLM audit, Evidence Confirm, repair loop, patch / regenerate, or chapter writer.
- Do not create `fund_agent/host` or `fund_agent/agent`.
- Do not introduce `dayu.host`, `dayu.engine`, external `dayu-agent` runtime, queue, model dependency, prompt registry, or tool loop.
- Do not add calculated index series, new external index adapters beyond accepted thermometer data-source protocols, methodology extraction, constituents extraction, QDII subtype redesign, unsupported coverage targets, or quality-gate weakening.
- Do not promote local scoring / writing / data-source runs into tracked fixtures without a later reviewed gate.

## Plan Review Checklist

Reviewers should explicitly check:

- Four-layer boundary: plan preserves `UI -> Service -> Host -> Agent`.
- Current deterministic path: no hidden Host / Agent / tool-loop / LLM writing is introduced.
- Future Host: any future Host work is gated and uses `dayu.host`.
- Future Agent execution: any future runner / tool loop / ToolRegistry / ToolTrace / context budget is gated and uses `dayu.engine`.
- Fund boundary: annual-report access remains through `FundDocumentRepository`; Service, UI, Host, renderer, and quality gate do not call concrete sources, PDF cache, or download helpers.
- Source failure taxonomy: fallback only for `not_found` / `unavailable`; fail closed for `schema_drift` / `identity_mismatch` / `integrity_error`.
- Explicit parameters: no business parameter is placed in `extra_payload` or `extra_payloads`.
- Methodology matrix: scoring dimensions cite §5.4.3 fund type lens, CHAPTER_CONTRACT, evidence hierarchy, and missing-fact degradation.
- 8-to-0-10 boundary: no current renderer rewrite or claim that 0-10 is implemented.
- Engineering baseline: any future package or dependency change checks `pyproject.toml` baseline, Python `>=3.11`, setuptools, explicit dependency bounds, optional `test` / `dev` dependency separation, pytest / ruff / black tool entry points, and package-data declaration for non-Python assets.
- Artifact policy: local runs stay under ignored `reports/*-runs/`, `reports/smoke/`, or temp dirs unless separately curated.

## Executable Next Gate Proposal

Recommended next gate after plan review:

1. `report-quality-baseline S0 corpus-selection evidence`
   - Produce a candidate table with fund type slot, fund code, report year, repository verification status, review state, source failure category, and ignored run path.
   - No renderer or quality gate changes.
2. `report-quality-baseline S1 score-schema fixture draft`
   - Produce JSON schema / dataclass plan and one reviewed dry-run scoring artifact under ignored `reports/scoring-runs/`.
   - No long-lived fixture promotion.
3. `fact-evidence-contract S2 bundle candidate`
   - Define the typed contract in code only after S0/S1 plan review passes.
   - Any code gate must include tests and README updates according to touched package boundaries.

Stop after S0 if corpus identity verification fails for multiple fund types; choose source reliability / repository boundary work before scoring schema implementation.

## Open Questions

1. Should the first baseline require FOF in S0, or accept FOF as S1 expansion if repository-verified FOF evidence is not immediately available?
2. Should report-quality scores remain purely issue-based in the first implementation, or should a non-blocking weighted total be added for trend tracking?
3. What is the minimum human-review artifact format for `fact_prefill_reviewed`: Markdown table under `docs/reviews/`, curated JSON fixture, or both after a later fixture gate?

## Residual Risks

- Small corpus may overfit if the first implementation treats it as product-wide proof rather than baseline observability.
- Manual review can become the bottleneck unless states and reviewer responsibilities are explicit.
- Scoring may expose source gaps that are more urgent than writing quality; the plan intentionally prioritizes fact correctness over prose polish.
- Future LLM audit / repair design may need Host / Agent runtime, but that remains blocked until a separate gate with `dayu.host` / `dayu.engine` design.

## Suggested Plan Reviewers

- AgentMiMo: review product-methodology coverage, baseline corpus sufficiency, and whether scoring dimensions map cleanly to user decision safety.
- AgentGLM: review architecture boundaries, failure taxonomy, explicit parameter discipline, artifact policy, and pyproject / Dayu Host-Agent constraints.

## Validation Plan

```text
rg -n "report-quality baseline|Fact / Evidence|ReportEvidenceBundle|FundDocumentRepository|extra_payload|dayu.host|dayu.engine|CHAPTER_CONTRACT|0-10|reports/scoring-runs" docs/reviews/release-maintenance-report-quality-baseline-fact-evidence-contract-plan-20260525.md
git diff --check
```

No `pytest` or `ruff` is required for this artifact because it changes documentation only and adds no executable Python, tests, package metadata, renderer behavior, or quality gate behavior.
