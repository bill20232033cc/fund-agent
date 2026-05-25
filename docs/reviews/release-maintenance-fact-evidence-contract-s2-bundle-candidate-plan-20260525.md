# Release Maintenance Fact-Evidence Contract S2 Bundle Candidate Plan

> Date: 2026-05-25
> Worker: AgentCodex planning specialist
> Gate: `fact-evidence-contract S2 bundle candidate planning`
> Scope: planning artifact only; no code implementation, no source code, no tests, no renderer, no FQ0-FQ6 behavior change, no config, no README, no design/control doc update, no Host/Agent package, no `dayu.host`, no `dayu.engine`, no fixture promotion, no commit, no push, no PR.

## Step Self-Check

- Role: planning specialist only, not controller.
- Truth sources read: `AGENTS.md`; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals; `docs/design.md` §2.1, §5.4, §5.4.1, §5.4.2, §5.4.3, §7.2, §7.3, §7.4, §11.5, §12; S1 score-schema controller judgment; S1 dry-run evidence; S1 dry-run controller judgment.
- Current production path remains deterministic `UI -> Service -> fund_agent/fund`; current Service may call Agent-layer Fund public capabilities directly as the accepted transition path.
- This plan does not implement code and does not claim future Host/Agent/LLM writing exists today.
- Annual-report access remains behind `FundDocumentRepository` / public Fund APIs that themselves use it. Future implementation must not read PDFs, cache paths, concrete sources, or download helpers directly.

## Objective

Turn accepted S0/S1 evidence into a code-generation-ready contract plan for a future typed `ReportEvidenceBundle` without starting implementation. The plan must let a later implementation agent add models and tests without redesigning:

- consume existing `StructuredFundDataBundle` outputs first;
- preserve source boundaries for facts, calculations, anchors, gaps, quality context, review status, and score issue linkage;
- normalize anchor and gap identifiers based on S1 dry-run evidence without freezing ad hoc names;
- force explicit chapter-contract wording for unsupported claims, especially the turnover stability claim, before opening data extraction work;
- define validation slices and stop conditions for a later code gate.

## Primary Design Decision: Wrap `StructuredFundDataBundle`

`ReportEvidenceBundle` should **wrap and project from `StructuredFundDataBundle`**, not replace it and not coexist as a parallel extraction path.

| Option | Decision | Reason |
|---|---|---|
| Wrap `StructuredFundDataBundle` | Accepted candidate | It consumes the current P1 truth source, preserves existing extractor and quality-gate investment, and avoids a second path that could disagree with `FundDataExtractor`. |
| Evolve `StructuredFundDataBundle` into `ReportEvidenceBundle` | Deferred | `StructuredFundDataBundle` is a P1 extraction bundle consumed by renderer, analysis, snapshots, and quality gate. Expanding it into report-quality review state would couple extraction with writing/audit lifecycle too early. |
| Coexist as independent bundle with its own extraction | Rejected for S2 | Parallel extraction would violate first principles: two fact sources create conflicts, extra review burden, and higher risk of bypassing `FundDocumentRepository`. |

Future implementation should create a projection adapter, conceptually:

```text
StructuredFundDataBundle
  + explicit quality gate / audit / scoring inputs
  + explicit manual review records
  -> ReportEvidenceBundle
```

This is not a code implementation. It is the contract direction for a later code gate.

### Ownership Boundary

`ReportEvidenceBundle` belongs to Agent-layer `fund_agent/fund` domain capability because it understands fund type, evidence anchors, `chapter_contract`, preferred lens, ITEM_RULE, and report-quality audit semantics. Service may orchestrate future use cases and pass explicit typed parameters, but it must not understand extractor internals or source fallback internals.

## Contract Candidate

### Top-Level Fields

| Field | Required | Candidate type / domain | Source boundary | Notes |
|---|---:|---|---|---|
| `bundle_id` | yes | `reb:{fund_code}:{report_year}:{schema_version}:{run_id}` | derived | Stable within one run; not a durable fixture id until a curated-fixture gate accepts it. |
| `schema_version` | yes | explicit string, e.g. `report_evidence_bundle.v0` | derived | Enables invalidation without reusing stale review states. |
| `corpus_id` | yes | `corpus:{corpus_name}:{version}` or `ad_hoc` | manual/review | Required for baseline scoring; explicit field, not `extra_payload`. |
| `fund_code` | yes | 6-digit fund code | `StructuredFundDataBundle` | Must match wrapped bundle. |
| `report_year` | yes | integer | `StructuredFundDataBundle` | Must match wrapped bundle. |
| `classified_fund_type` | yes | see `classified_fund_type values` below | `StructuredFundDataBundle.basic_identity` | Fund type must be known before applying preferred lens. |
| `fund_type_slot` | optional for ad hoc; required for baseline | accepted S1 slot domain | manual/review | Separates actual classification from baseline coverage slot. |
| `preferred_lens` | yes | see `preferred_lens` format below | fund methodology config | Derived after fund type classification; not a free string. |
| `source_documents` | yes | list of source document records | `FundDocumentRepository` metadata | Describes document identity and source failure/fallback state, not raw file paths. |
| `facts` | yes | list of `ReportFact` | projected from `StructuredFundDataBundle` and reviewed rows | No direct PDF/cache/source adapter access. |
| `derived_calculations` | yes | list of `DerivedCalculation` | P2 analysis / thermometer / quality result inputs | Must list input fact ids and inherited anchors. |
| `evidence_anchors` | yes | list of `ReportEvidenceAnchor` | `EvidenceAnchor` projection plus reviewed refs | Bundle-local ids normalize existing anchor objects and review artifact refs. |
| `data_gaps` | yes | list of `ReportDataGap` | extraction missing states, source failures, manual review gaps | Missing facts become first-class records, not renderer omissions. |
| `quality_context` | yes | `ReportQualityContext` | FQ0-FQ6, programmatic audit, S1 scoring | Can constrain confidence, cannot replace facts. |
| `score_issue_links` | yes | list of issue ids / score refs | S1 score schema | Links facts/gaps/anchors to report-quality observations. |
| `review_status` | yes | derived enum | contained records | Must be computed, not hand-entered inconsistently. |

`corpus_id` format: use `corpus:{corpus_name}:{version}`, where `corpus_name` is a stable snake_case name from the accepted review artifact and `version` is a date or reviewed revision id, for example `corpus:rqb_s0:20260525`. In S2, `ad_hoc` is allowed only for non-baseline local inspection because no durable baseline or curated fixture has been accepted. A baseline `corpus_id` must link to the S0/S1 review artifact by explicit review reference, not by guessing from ignored run paths.

`classified_fund_type values`: the directly implementable domain is `index_fund`, `active_fund`, `bond_fund`, `enhanced_index`, `qdii_fund`, `fof_fund`, and `unknown`. Projection reads `StructuredFundDataBundle.basic_identity.value["classified_fund_type"]`. If `basic_identity.value` is missing, not a mapping, lacks the key, or carries a value outside that domain, projection must set `classified_fund_type="unknown"`, create a `data_gap` with `gap_kind=missing_fact` or `type_slot_gap` as appropriate, and prevent `scoring_ready`. It must not infer fund type from fund name or benchmark text in the bundle projection layer.

`preferred_lens` format: store a serializable projection, not a live `TemplateLensRule` object. Minimum shape is `preferred_lens={"fund_type": classified_fund_type, "chapters": [{"chapter_id": "chapter_0", "lens_key": "active_fund", "used_default": false}, ...]}` for current chapter ids `chapter_0` to `chapter_7`. The implementation source should be the existing preferred_lens resolver / lens application plan; if `classified_fund_type="unknown"`, `preferred_lens` must be empty or blocked and the bundle cannot become `scoring_ready`.

### Source Documents

`source_documents` records must describe only the document boundary needed by scoring/writing:

| Field | Domain | Rule |
|---|---|---|
| `document_id` | `doc:{fund_code}:{report_year}:annual_report` | Bundle-local id. |
| `document_type` | `annual_report`, future `prospectus`, `fund_contract`, `periodic_report` | S2 implementation should support annual report first. |
| `identity_status` | `verified_annual_report`, `unverified`, `mismatch`, `source_failed`, `verified_as_annual_report_but_type_gap` | Reuse S1 split between document identity and fund-type slot membership. |
| `source_boundary` | `repository_derived`, `manual_review`, `external_official`, `unknown`, `probe_only` | Durable baseline excludes `unknown` and `probe_only`; `external_official` is future/metadata only in S2. |
| `source_failure_category` | `none`, `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, `unknown_upstream_failure_category` | Fallback is eligible only for `not_found` / `unavailable`. |
| `fallback_allowed` | boolean | Derived from failure category. |
| `fallback_used` | boolean | Must preserve metadata if fallback occurred. |
| `review_artifact_refs` | list | Markdown review artifacts are allowed; ignored run outputs are scratch only. |

No field may store PDF cache paths or concrete source helper names as the operational access route. Diagnostic metadata may identify source type, but future code must still call `FundDocumentRepository`.

`external_official` boundary clarification: in this S2 plan, `external_official` is metadata for already accepted official references only, not permission to call direct external APIs. Any future official-index, exchange, regulator, or third-party structured source must first pass a separate Repository-style official-source interface gate. Until then, `external_official` records cannot be created by ad hoc network calls and cannot by themselves make a bundle `scoring_ready`.

### Facts

`facts` are normalized projections of `ExtractedField` values from `StructuredFundDataBundle` plus reviewed manual corrections. Candidate fields:

| Field | Required | Domain / shape | Rule |
|---|---:|---|---|
| `fact_id` | yes | `fact:{category}.{field_path}` | Stable within bundle and reusable in calculations. |
| `category` | yes | `identity`, `fund_type`, `benchmark`, `performance`, `fee`, `manager`, `holdings`, `holders`, `risk`, `valuation`, `thermometer`, `nav`, `other` | Configurable domain; no hardcoded fund-type rule in renderer. |
| `field_path` | yes | existing snapshot-style path, e.g. `manager_alignment.manager_holding` | Align with §7.2 snapshot fields where possible. |
| `value` | yes | normalized scalar/object/list or explicit null for missing | Missing value must pair with data gap or `not_applicable`. |
| `unit` | yes | `percent`, `ratio`, `cny`, `date`, `text`, `count`, `object`, `not_applicable`, `unknown` | Prevent unit ambiguity in report wording. |
| `period` | optional | reporting period / date | Required when value is time-sensitive. |
| `source_anchor_ids` | yes | list of anchor ids | Empty only when fact has data gap explaining why. |
| `source_document_ids` | yes | list of document ids | Annual-report facts must point to `FundDocumentRepository`-verified document records. |
| `source_boundary` | yes | same boundary enum | Must not be `unknown` for durable scoring-ready facts. |
| `extraction_mode` | yes | current `direct`, `derived`, `estimated`, `missing` plus `manual_reviewed`, `not_applicable` candidate | Future code may map from current `ExtractionMode`; `estimated` must be explicit and cannot silently support strong claims. |
| `review_status` | yes | record lifecycle enum | Derived from manual review / source readiness. |
| `failure_category` | optional | source/data gap enum | Required when value is missing, unsafe, conflicted, or estimated. |
| `score_issue_ids` | yes | list | Links to S1/S2 scoring issues affecting this fact. |

Initial projection should cover current `StructuredFundDataBundle` `ExtractedField` fields: `basic_identity`, `product_profile`, `benchmark`, `index_profile`, `fee_schedule`, `turnover_rate`, `nav_benchmark_performance`, `investor_return`, `tracking_error`, `share_change`, `manager_alignment`, `manager_strategy_text`, `holdings_snapshot`, and `holder_structure`.

`nav_data` projection is explicitly excluded from the initial facts projection. `StructuredFundDataBundle.nav_data` is a `NavDataResult`, not an `ExtractedField`, and it lacks `extraction_mode` and `EvidenceAnchor` tuples. A later `nav_data` slice may define a safe mapping for NAV time series, source metadata, periods, units, and external-source anchoring. Until that slice exists, `nav_data` may be mentioned in `quality_context` or residual notes, but not projected as report facts.

Multi-anchor mapping rule: each `ExtractedField` should normally map to one `ReportFact` whose `source_anchor_ids` contains every projected `anchor_id` from `ExtractedField.anchors`. The projection must not drop secondary anchors. Splitting one field into multiple facts is allowed only when the field value itself contains independent subfields with distinct `field_path` values; even then, every original anchor must either be attached to the relevant subfact or preserved in a parent/source anchor reference.

### Derived Calculations

`derived_calculations` make P2 and report-level calculations auditable:

| Field | Required | Domain / shape | Rule |
|---|---:|---|---|
| `calculation_id` | yes | `calc:{formula_name}.{scope}` | Stable and referenced by claims. |
| `formula_name` | yes | `r_abc`, `cost_estimate`, `thermometer_state`, `pressure_test`, `final_judgment_support`, `other` | Named formula; not arbitrary prose. |
| `input_fact_ids` | yes | list | Missing inputs must block or degrade calculation. |
| `input_anchor_ids` | yes | list | Inherits evidence from inputs. |
| `output_value` | optional | normalized value/object | Empty only if status blocks. |
| `calculation_status` | yes | `computed`, `blocked_by_missing_fact`, `blocked_by_conflict`, `not_applicable`, `manual_review_required` | Invalid to claim computed without inputs. |
| `assumptions` | yes | list | Empty list if none. |
| `degradation_text` | optional | report wording constraint | Required when calculation is blocked but chapter still mentions the topic. |
| `data_gap_refs` | yes | list | Missing inputs are explicit. |
| `score_issue_ids` | yes | list | Link calculation failures to score issues. |

Rule: missing R/B/C inputs block pseudo-alpha; missing turnover/style-change evidence blocks stability inference unless chapter wording explicitly states the gap.

### Evidence Anchors

Existing `EvidenceAnchor` has no id. `ReportEvidenceBundle` must add bundle-local ids while preserving the source fields.

| Field | Required | Domain / shape | Rule |
|---|---:|---|---|
| `anchor_id` | yes | see naming convention below | Stable within bundle. |
| `source_kind` | yes | current `annual_report`, `external_api`, `derived`; future candidates `official_index`, `regulatory`, `reviewed_note` only after model gate | Do not widen code enum in this planning gate. |
| `source_strength` | yes | `fund_disclosure`, `official_reference`, `manager_statement`, `third_party_reference`, `derived`, `manual_review` | Determines claim strength, not a score. |
| `document_id` | optional | `doc:*` | Required for annual-report anchors. |
| `document_year` | optional | integer | Mirrors current `EvidenceAnchor`. |
| `section_id` | optional |年报章节 / external section | Mirrors current `EvidenceAnchor`. |
| `page_number` | optional | integer | Preserve when available. |
| `table_id` | optional | string | Preserve when available. |
| `row_locator` | optional | string | Preserve when available. |
| `review_artifact_ref` | optional | path plus line/ref | For manual reviewed rows such as S1 dry-run evidence. |
| `note` | optional | short note | No long pasted source excerpts. |

### Data Gaps

`data_gaps` are first-class records. They include missing fields, unsupported claims, unsafe fallback, type-slot gaps, and manual-review gaps.

| Field | Required | Domain / shape | Rule |
|---|---:|---|---|
| `gap_id` | yes | see naming convention below | Referenced by facts, calculations, and score issues. |
| `gap_kind` | yes | `missing_fact`, `not_disclosed`, `not_reviewed`, `source_failure`, `identity_conflict`, `type_slot_gap`, `unsupported_claim`, `not_applicable`, `manual_review_required` | Distinguishes document failure from fact-level gap. |
| `related_fact_id` | optional | `fact:*` | Required for missing fact gaps. |
| `related_claim_id` | optional | `claim:*` | Required for unsupported claim gaps. |
| `chapter_ids` | yes | `chapter_0` to `chapter_7`, `report_level` | Current v0 chapters only until separate renderer gate. |
| `failure_category` | yes | `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, `not_disclosed`, `ambiguous`, `not_applicable`, `unsupported_source`, `manual_review_required`, `not_reviewed_in_current_slice` | Preserve source taxonomy and S1 dry-run categories. |
| `fallback_allowed` | yes | boolean | True only for `not_found` / `unavailable`; false for fail-closed categories. |
| `fallback_used` | yes | boolean | Must not hide original source category. |
| `required_report_wording` | yes | short wording constraint | Examples: `未披露`, `数据不足`, `当前 slice 未复核换手率，不能据此判断风格稳定`. |
| `blocks_claim_ids` | yes | list | Unsupported claims cannot render strongly. |
| `blocks_scoring_dimensions` | yes | list | E.g. `fact_coverage`, `chapter_contract_completeness`. |
| `score_issue_ids` | yes | list | Links to S1/S2 score records. |

### Quality Context

`quality_context` constrains confidence and final judgment but cannot create facts.

| Field | Required | Domain / shape | Rule |
|---|---:|---|---|
| `fq_gate_status` | yes | `pass`, `warn`, `block`, `not_run` | Cite current FQ0-FQ6 final status semantics in later implementation. |
| `fq_issue_refs` | yes | rule ids / summaries | No behavior change to FQ0-FQ6 in S2. |
| `programmatic_audit_status` | yes | `pass`, `warn`, `block`, `not_run` candidate | Mirrors current audit result when available. |
| `report_quality_score_refs` | yes | S1/S2 score run ids / issue ids | Observational only. |
| `known_residual_refs` | yes | review artifacts / residual ids | Keeps FOF/fallback/turnover residuals visible. |
| `judgment_constraint` | yes | `strong_allowed`, `cautious_only`, `must_downgrade_or_block`, `not_evaluated` | Derived from facts/gaps/quality status. |

### Review Status Derivation

Bundle-level `review_status` must be derived from contained records. A future implementation should not allow callers to set it inconsistently.

| Bundle status | Derivation candidate |
|---|---|
| `candidate` | Source document identity or fund type is not verified. |
| `repository_verified` | Annual report identity is verified, but facts are not reviewed. |
| `fact_prefill_generated` | Facts/anchors are generated from `StructuredFundDataBundle`, but manual review has not accepted scored fields. |
| `fact_prefill_reviewed` | All facts needed by selected scoring dimensions are reviewed or have explicit `data_gaps`. |
| `scoring_ready` | Document identity, type slot, facts, anchors, gaps, and quality context pass value-domain and invalid-combination checks. |
| `accepted_baseline` | Only after a later curated-fixture gate accepts it; S2 must not promote it. |
| `rejected` | Any identity mismatch, integrity error, schema drift, invalid anchor, or reviewed contradiction invalidates the bundle for baseline use. |
| `deferred` | Required evidence is incomplete but recoverable, such as fallback category or manual review pending. |
| `expired` | Schema version, corpus revision, report year, or reviewed evidence is superseded. |

Legal progression aligned with S0 transitions:

```text
candidate
  -> repository_verified
  -> fact_prefill_generated
  -> fact_prefill_reviewed
  -> scoring_ready
  -> accepted_baseline
```

Transition semantics:

| Transition | Required trigger / evidence | Actor |
|---|---|---|
| `candidate -> repository_verified` | `FundDocumentRepository` verifies fund code, report year, report type, and document identity, or records an explicit source failure. | repository verification gate |
| `repository_verified -> fact_prefill_generated` | Projection from `StructuredFundDataBundle` creates facts, anchors, and explicit gaps without manual acceptance. | fact prefill generation |
| `fact_prefill_generated -> fact_prefill_reviewed` | Human review accepts/corrects selected facts or records explicit data gaps in a tracked review artifact. | manual review |
| `fact_prefill_reviewed -> scoring_ready` | Value-domain checks, id reference checks, invalid-combination checks, type-slot membership, and quality context all pass. | scoring validation |
| `scoring_ready -> accepted_baseline` | A later curated-fixture / durable-baseline gate accepts the bundle; S2 cannot perform this transition. | controller-reviewed future gate |

Terminal states:

- `rejected`: terminal for the current bundle revision. Use when identity mismatch, schema drift, integrity error, invalid anchor, illegal enum, reviewed contradiction, or fail-closed fallback condition invalidates the bundle. A later attempt must create a new bundle revision.
- `expired`: terminal for the current bundle revision. Use when schema version, corpus revision, report year, or reviewed evidence has been superseded.
- `deferred`: non-terminal but not scoring-ready. Use when evidence is incomplete and recoverable, such as manual review pending, fallback category recovery pending, or pure FOF corpus search pending.

`review_status priority`: when multiple conditions match, derive the most restrictive status in this order:

```text
rejected > expired > deferred > scoring_ready > fact_prefill_reviewed > fact_prefill_generated > repository_verified > candidate
```

Conflict examples:

- A verified annual report with an illegal `classified_fund_type` is `rejected` or `deferred` depending on whether the value is contradicted by review evidence or merely missing; it is not `repository_verified` for scoring.
- A bundle with reviewed facts but `unknown_upstream_failure_category` is `deferred`, not `fact_prefill_reviewed` or `scoring_ready`.
- A bundle whose schema version is superseded is `expired` even if its facts were previously reviewed.

Minimum invalid combinations:

- `review_status=scoring_ready` with any `source_boundary=unknown` or `probe_only`.
- `review_status=scoring_ready` with fallback category still `unknown_upstream_failure_category`.
- `review_status=scoring_ready` with `document_identity_status` other than `verified_annual_report`.
- `review_status=scoring_ready` with `type_slot_membership_status` not `matches_slot`, except excluded taxonomy/data-gap records.
- `review_status=accepted_baseline` in S2 planning or before a curated-fixture gate.
- `status=pass` while related blocking `data_gaps` exist for the same claim.
- `review_status=scoring_ready` with `classified_fund_type="unknown"`.
- `review_status=scoring_ready` with unresolved `data_gap_refs` or score issue links.

## Identifier Conventions

S1 dry-run used `gap:004393.2024.turnover_rate.not_reviewed_in_current_slice`. That shape is useful but too field-only and too ad hoc for all bundle objects. S2 should adopt explicit namespace prefixes and deterministic components.

### Anchor IDs

Candidate format:

```text
anchor:{fund_code}:{report_year}:{source_kind}:{section_or_source}:{locator_hash}
```

Rules:

- Use colon-separated components for object ids; avoid file path separators.
- `source_kind` must come from the bundle anchor domain.
- `section_or_source` should be sanitized from `section_id` for annual reports or official source id for external data.
- `locator_hash` is `sha256` first 8 lowercase hex characters over normalized locator fields. It prevents long brittle ids while preserving stability.
- Manual review anchors may use `anchor:{fund_code}:{report_year}:reviewed_note:{artifact_slug}:{row_hash}`.
- Do not use human line numbers as the only durable id; line numbers may remain in `review_artifact_ref`.

`locator_hash` normalization:

1. Build an ordered JSON-compatible object with keys `page_number`, `table_id`, `row_locator`, `note`, and `review_artifact_ref`.
2. Convert `None` to an empty string.
3. Convert all values to strings except integer `page_number`; strip leading/trailing whitespace; collapse internal ASCII whitespace to one space; apply Unicode NFC normalization.
4. Serialize with sorted keys, UTF-8, and no extra spaces.
5. Compute `sha256(serialized_bytes).hexdigest()[:8]`.

Collision handling within a bundle: if two distinct normalized locator objects produce the same 8-hex hash for the same `anchor:{fund_code}:{report_year}:{source_kind}:{section_or_source}` prefix, append `-2`, `-3`, etc. in deterministic sort order and record a validation warning. Tests must cover stable same-input hashing and deterministic collision suffixing.

Examples:

- `anchor:004393:2024:annual_report:sec9:7f3a12`
- `anchor:004393:2024:reviewed_note:s1_dry_run:91b2aa`

### Fact IDs

Candidate format:

```text
fact:{category}.{field_path}
```

Examples:

- `fact:manager.turnover_rate`
- `fact:manager.manager_alignment.manager_holding`
- `fact:performance.nav_benchmark_performance`

Fact ids are bundle-local because they represent normalized fields for one fund-year.

### Calculation IDs

Candidate format:

```text
calc:{formula_name}.{scope}
```

Examples:

- `calc:r_abc.chapter_2`
- `calc:pressure_test.chapter_6`

### Data Gap IDs and `data_gap_refs`

Candidate format:

```text
gap:{fund_code}:{report_year}:{gap_kind}:{field_or_claim_path}:{reason_code}
```

Rules:

- `data_gap_refs` must contain only `gap:*` ids from the same bundle or explicitly imported reviewed artifact.
- `gap_kind` must distinguish `missing_fact`, `not_reviewed`, `unsupported_claim`, `source_failure`, and `type_slot_gap`.
- `reason_code` must use a controlled snake_case domain.
- S1 dry-run id maps to `gap:004393:2024:not_reviewed:manager.turnover_rate:not_reviewed_in_current_slice`.

Examples:

- `gap:004393:2024:not_reviewed:manager.turnover_rate:not_reviewed_in_current_slice`
- `gap:017970:2024:type_slot_gap:fund_type.fof_slot:classified_as_qdii_fund`
- `gap:110020:2024:source_failure:annual_report:unknown_upstream_failure_category`

### Score Issue IDs

Candidate format:

```text
issue:{score_run_id}:{fund_code}:{report_year}:{chapter_id}:{dimension}:{field_or_claim_hash}
```

S1 dry-run `s1-dry-run-004393-ch3-turnover-gap` should become a score issue alias or legacy ref, not the canonical long-term convention.

## Chapter-Contract Handling Before Extraction Work

The turnover issue is not automatically a data-extraction mandate. First principles:

1. A report claim must be supported by direct facts, derived calculations with inputs, or explicit gap wording.
2. If current facts cannot support a stability claim, the safest first move is to constrain wording.
3. Data extraction work is justified only if the accepted `chapter_contract` says the chapter must answer the claim with turnover/style-change evidence and current data lacks it.

### Turnover Stability Claim Rule

For active funds, Chapter 3 may discuss manager consistency / "说 vs 做", but must obey:

| Condition | Required report behavior |
|---|---|
| `turnover_rate` reviewed and anchored | May use turnover as one piece of style/process consistency evidence, with limitations. |
| `turnover_rate` missing or not reviewed | Must state data gap if discussing process stability; must not infer stable style from manager statements alone. |
| holdings/style-change evidence also missing | Must downgrade to "数据不足 / 下一步最小验证问题", not a stability conclusion. |
| manager holding is anchored but turnover missing | May discuss interest alignment, but must not conflate holding alignment with process stability. |

Required `chapter_contract` wording constraint, accepted for this S2 plan based on the S1 dry-run controller judgment:

```text
If Chapter 3 makes a stability / style consistency claim, it must cite reviewed turnover or style-change evidence.
If such evidence is absent, the chapter must say the current evidence is insufficient and list turnover/style-change review as the next minimum validation question.
```

Turnover stability accepted constraint: future S2 implementation should encode this as report wording constraints attached to `data_gaps`, not as a renderer behavior change in this planning gate. The accepted constraint is narrow: it governs active-fund Chapter 3 stability/style-consistency claims and does not require automatic turnover extraction.

## Future Implementation Slices

These slices are for a later code gate only. They are not authorized by this planning artifact.

### Slice 1: Typed Model Skeleton and Value Domains

Files likely touched in future gate: Agent-layer `fund_agent/fund` model module and tests. Exact file path should be chosen by implementation after reading current package layout.

Tasks:

- Add typed dataclasses or equivalent models for source documents, facts, calculations, anchors, data gaps, quality context, score issue links, and bundle.
- Use explicit enum/Literal domains for source boundary, failure category, review status, score status, quality status, gap kind, source strength, and judgment constraint.
- Do not add `extra_payload` or free dict catchalls for explicit business parameters.
- Include Chinese docstrings with parameter/return/exception notes if functions are added, per `AGENTS.md`.

Validation:

- Unit tests for enum/domain acceptance and rejection.
- Negative tests: reject illegal `classified_fund_type` values other than `index_fund`, `active_fund`, `bond_fund`, `enhanced_index`, `qdii_fund`, `fof_fund`, and `unknown`.
- Negative tests: reject `preferred_lens` for `classified_fund_type="unknown"` when bundle status is proposed as `scoring_ready`.
- Negative tests: reject source boundaries that try to treat `external_official` as direct API permission in S2.
- `rg` proving no `extra_payload` is introduced in new model code.
- `git diff --check`.

### Slice 2: Projection From `StructuredFundDataBundle`

Tasks:

- Build a projection function that accepts `StructuredFundDataBundle` and explicit context objects.
- Project each `ExtractedField` to one or more `facts`, `evidence_anchors`, and `data_gaps`.
- Apply the multi-anchor rule: one `ExtractedField` fact references all projected anchor ids unless explicitly split into subfacts without dropping anchors.
- Preserve `EvidenceAnchor` fields and generate deterministic `anchor_id`.
- Preserve `extraction_mode=missing` as a gap, not a silent null.
- Exclude `nav_data` from initial facts projection; keep a later `nav_data` mapping slice separate.
- Keep `FundDocumentRepository` as the only production annual-report access path by consuming already extracted bundle/document metadata, not files.

Validation:

- Tests with fake bundles for each current field group.
- Tests that missing `turnover_rate` produces a `data_gap_refs`-addressable gap.
- Negative tests: `extraction_mode=missing` with non-null `value` must fail validation or be normalized to a rejected/deferred state before scoring.
- Negative tests: `extraction_mode=direct` with non-null `value` and empty anchors must produce a data gap or fail traceability validation unless explicitly `manual_reviewed`.
- Negative tests: `nav_data` does not appear in initial `facts`; any attempted `nav_data` fact fails until the later mapping slice is accepted.
- Tests with a multi-anchor `ExtractedField` prove no anchor is dropped from `source_anchor_ids`.
- Tests that annual-report anchors generate stable ids.
- Tests that projection never calls concrete source/download/cache helpers.

### Slice 3: Review Status Derivation and Invalid Combinations

Tasks:

- Implement derived bundle review status.
- Reject or block invalid state combinations listed above.
- Enforce `accepted_baseline` cannot appear unless explicitly enabled by a later curated-fixture gate.

Validation:

- Parameterized tests for each invalid combination.
- Tests for terminal states `rejected`, `deferred`, `expired`.
- Tests that `unknown` / `probe_only` cannot become `scoring_ready`.
- Negative tests: priority conflict derives `rejected` before `deferred` and `deferred` before `scoring_ready`.
- Negative tests: `classified_fund_type="unknown"` cannot become `scoring_ready`.
- Negative tests: `accepted_baseline` is rejected unless a future curated-fixture gate flag/context explicitly enables it.

### Slice 4: Score Issue Linkage and Content-Level JSONL Checks

Tasks:

- Link score records to facts, anchors, calculations, and gaps by ids.
- Add content-level JSONL validation for ignored scoring runs if future dry-runs continue to use JSONL scratch.
- Validate required fields, enum domains, issue object shape, `N/A` reason presence, `skipped` / `chapter_summary` constraints, and `data_gap_refs` existence.

Validation:

- JSONL fixture-like test inputs remain test-local unless curated fixture gate accepts tracked fixtures.
- Tests fail when `data_gap_refs` points to a non-existent gap.
- Tests fail when `status=N/A` lacks `na_reason` / reviewer note.
- Tests fail when `dimension=chapter_summary` is used outside `status=skipped`.
- Negative tests: score issue links fail when they reference missing facts, anchors, calculations, or gaps.
- Negative tests: `status=pass` fails when the same claim has blocking `data_gap_refs`.

### Slice 5: Chapter-Contract Wording Constraints

Tasks:

- Represent gap-driven wording constraints separately from extraction facts.
- Add the active-fund Chapter 3 turnover stability accepted constraint.
- Ensure constraints can block unsupported claims without changing current renderer or FQ0-FQ6 behavior in the implementation slice unless that future gate explicitly authorizes it.

Validation:

- Tests that missing turnover/style-change evidence blocks a stability claim.
- Tests that manager holding evidence alone does not satisfy process stability.
- Tests that a gap can require next-minimum-validation wording.
- Negative tests: a Chapter 3 process-stability claim with manager statement anchors but no turnover/style-change evidence must fail wording-constraint validation.

## Boundaries and Non-Goals

- No code implementation in this S2 planning gate.
- No source, tests, renderer, FQ0-FQ6, config, README, design doc, or control doc edits in this gate.
- No `fund_agent/host` or `fund_agent/agent` package creation.
- No `dayu.host` or `dayu.engine` introduction. If future session/run/cancel/resume/outbox or tool loop/runner/ToolRegistry/ToolTrace/context budget is required, stop and open a separate Host/Agent gate.
- No LLM writing, LLM audit, Evidence Confirm, repair loop, patch/regenerate, or report assembly pipeline claim.
- No current v0 8-chapter renderer behavior change.
- No quality-gate weakening and no FQ0-FQ6 behavior change.
- No direct PDF/cache/source/download helper access outside `FundDocumentRepository`.
- No explicit business parameter in `extra_payload` / `extra_payloads`.
- No promotion of ignored `reports/scoring-runs/` outputs or curated fixtures.
- No durable baseline selection.
- No QDII-FOF taxonomy change or FOF coverage claim.

## Stop Conditions for Future Code Gate

Stop implementation and return to planning/controller if:

1. Implementation needs to create Host/Agent runtime packages or import `dayu.host` / `dayu.engine`.
2. Implementation needs renderer output changes or FQ0-FQ6 behavior changes to prove the bundle model.
3. Projection cannot consume `StructuredFundDataBundle` and would require a parallel extraction path.
4. Annual-report facts require direct cache/PDF/source helper access instead of `FundDocumentRepository`.
5. A required parameter is proposed as `extra_payload`.
6. Fallback category remains `unknown_upstream_failure_category` but a record is proposed as `scoring_ready`.
7. `schema_drift`, `identity_mismatch`, or `integrity_error` would be masked by fallback.
8. The turnover stability issue is treated as automatic extraction work without first encoding chapter-contract wording constraints.
9. Tests would need tracked scoring-run outputs or curated fixtures before a fixture gate accepts them.

## Residual Risks

| Residual | Risk | Owner / next handling |
|---|---|---|
| Exact model file placement undecided | Implementation could scatter models across renderer/service/fund | Future code gate should keep models in Agent-layer Fund package and update package README only if code changes. |
| Existing `EvidenceAnchor.source_kind` is narrower than future source taxonomy | Premature enum widening could affect many extractors/tests | Future implementation should wrap current anchors first; widen only with tests and explicit contract need. |
| Manual review artifact format remains Markdown | Harder machine validation than JSON fixtures | Keep Markdown as reviewed truth until curated-fixture gate accepts JSON fixture promotion. |
| Fallback category recovery still open for `110020`, `017641`, `017970` | These cannot be durable baseline | Source reliability gate must recover category or keep excluded. |
| Pure FOF remains missing | Baseline cannot claim all fund-type coverage | Fund-type taxonomy or second-pass corpus gate. |
| Turnover/style stability contract may reveal broader Chapter 3 gaps | Could require more than turnover extraction | Chapter-contract gate should define claim-level wording constraints before data extraction scope. |

## Next Recommended Gate

Recommended next gate: **typed `ReportEvidenceBundle` model/projection implementation plan review**, not direct implementation.

That next gate should accept or amend this contract, choose exact file ownership, decide tests, and only then authorize code. If the controller wants a narrower first implementation, start with typed models + projection tests from `StructuredFundDataBundle`, leaving JSONL content validation and chapter-contract wording constraints as follow-up slices with explicit owners.

## Validation Plan for This Artifact

Required checks before returning:

```text
rg -n "ReportEvidenceBundle|StructuredFundDataBundle|FundDocumentRepository|extra_payload|dayu.host|dayu.engine|chapter_contract|turnover|data_gap_refs|no code implementation" docs/reviews/release-maintenance-fact-evidence-contract-s2-bundle-candidate-plan-20260525.md
git diff --check
```

No `pytest`, `ruff`, or renderer/quality-gate command is required because this artifact intentionally contains no code implementation.
