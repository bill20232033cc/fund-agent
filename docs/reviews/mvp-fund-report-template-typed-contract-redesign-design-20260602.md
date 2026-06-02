# MVP fund report template typed contract redesign design

## Worker Self-Check

- Role: scoped design worker only, not controller.
- Gate: `MVP fund report template typed contract redesign gate`.
- Classification: heavy.
- Scope: design evidence and proposed future design only.
- Actions taken: read required sources and write this single `docs/reviews/` artifact.
- Actions intentionally not taken: no Gateflow/Phaseflow controller start, no implementation, no code/test/prompt/provider/auditor/runtime/golden/quality-gate changes, no commit, no push, no PR, no edit to `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, retained reports, or runtime code.
- Truth status: this artifact is a design recommendation for controller review. It is not current implementation fact and does not by itself update accepted future design.

## Current Code And Template Facts

Current template facts from `docs/design.md` and `docs/fund-analysis-template-draft.md`:

- Current template is an 8 chapter structure, chapter ids `0-7`.
- Current `ChapterContract` fields are `chapter_id`, `title`, `narrative_mode`, `must_answer`, `must_not_cover`, `required_output_items`, and `preferred_lens`; `must_answer`, `must_not_cover`, and `required_output_items` are natural-language list contracts, not typed clause objects.
- Current Chapter 0 requires an independent-looking action output: `值得持有 / 需要关注 / 建议替换`.
- Current Chapter 7 is the final judgment chapter and also requires the same three-way action output.
- Current Chapter 2 combines R/B/A/C: 1Y/3Y/5Y return, benchmark, alpha, structural vs stage alpha, and cost decomposition.
- Current Chapter 3 requires `言行一致性判断`, but its `must_not_cover` also says not to infer active-fund style stability, style consistency, or conduct consistency when turnover/style-change evidence is missing, unavailable, or unreviewed.
- Current Chapter 6 contains fund-type pressure-test thresholds in `preferred_lens`, but the `must_answer` item only says to answer the pressure-test conclusion.
- Current design truth already says future Chapter 0 should summarize accepted conclusions and not introduce new facts or judgments; current Route C final assembly code fact deterministically generates Chapter 7 before Chapter 0. The template draft still needs a clearer typed contract expression for this dependency.
- Current design truth explicitly says future 0-10 chapter mapping remains a gate topic; it must not be written as current renderer/runtime fact.

Current execution boundary facts:

- Current default production path remains deterministic `fund-analysis analyze/checklist`.
- Current Route C `--use-llm` path is opt-in and fail-closed. Gate 3 `ChapterOrchestrator` remains Service-owned until a separate Agent-engine implementation gate.
- Accepted design-only future Agent architecture says Fund audit should be programmatic-first and the LLM auditor bounded to semantic concerns; it does not authorize runtime or auditor changes.

## Retained LLM Evidence

Same-run retained evidence comes from `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431`.

Run-level evidence:

- `summary.json` records `orchestration_status=partial` and `final_assembly_status=incomplete`.
- Its `chapter_matrix` records Chapter 1 and Chapter 5 accepted; Chapters 2, 3, 4, and 6 failed.
- Chapter 2 failed with `llm_timeout` in auditor retries, `user_prompt_chars=2917`, `approx_prompt_tokens=743`, `timeout_seconds=60.0`.
- Chapter 4 failed with `llm_timeout` in auditor retries, `user_prompt_chars=2280`, `approx_prompt_tokens=584`.
- Chapter 6 is mixed: attempt 0 had a programmatic C2 issue at `压力测试` and an LLM C1 issue; terminal attempt 1 failed with auditor `llm_timeout`, `user_prompt_chars=2868`, `approx_prompt_tokens=731`.
- The controller judgment after provider restore classifies Ch2 as provider runtime blocker, Ch6 as mixed but currently provider runtime blocker, and Ch3 as eligible same-source `must_not_cover` calibration evidence.

Chapter 3 direct evidence:

- Attempt 0 writer includes required output `言行一致性判断` and says missing actual behavior evidence prevents judging consistency.
- Attempt 0 auditor feedback blocks on programmatic C2 at `言行一致` and also has an LLM C1 missing-anchor issue for `实际投资行为（§8）`.
- Attempt 1 repair again writes positive or quasi-positive directionality around strategy consistency while also admitting strict verification is unavailable.
- Attempt 1 auditor feedback has no LLM issues but repeats the same programmatic C2 blocker at `言行一致`; repair budget is exhausted.
- `chapter-03.json` records `failure_category=prompt_contract`, `failure_subcategory=code_bug_other`, and repeated `programmatic:C2:言行一致:db9a79f992`.

Evidence limits:

- Chapter 2/4/6 timeout evidence is direct runtime evidence, not direct proof that chapter splitting or prompt simplification will fix acceptance.
- External draft D-2 timeout percentage/root-cause allocation is unsupported by retained evidence. Ch2/Ch4/Ch6 have `small_prompt_provider_timeout` diagnostics and remain provider runtime gate evidence.
- Chapter 3 evidence is direct contract-shape evidence: the current natural-language `must_answer` and `must_not_cover` are too coarse for a literal programmatic checker.
- No retained evidence proves a 0+9 or 0+10 chapter structure is superior. Structural redesign may still be valid, but it needs a separate gate and validation sample.

## External Redesign Proposal

The external draft proposes:

- typed `ChapterContract`;
- typed `EvidenceAvailability`;
- evidence-conditional `must_not_cover`;
- typed required output items with missing/degrade behavior;
- Chapter 0 consuming the final judgment chapter rather than independently judging;
- splitting old Chapter 2 into separate performance, attribution, and cost chapters, yielding a 0+9 structure;
- per-chapter `audit_focus`;
- pressure-test thresholds as typed context;
- later EvidenceBundle/5Y evidence routing;
- migration stages and acceptance-rate targets.

Controller should treat the external draft as candidate input, not accepted design truth. Several concepts are well-supported by current evidence, but exact chapter count, migration schedule, timeout-improvement percentages, and 5Y data ingestion strategy are not yet directly supported by same-source evidence.

## Recommendation Summary

Accepted for proposed future design:

- typed `ChapterContract` as the contract surface for Fund template semantics.
- typed `EvidenceAvailability` as the derived supplemental source of evidence-present/evidence-missing decisions.
- evidence-conditional `must_not_cover` that distinguishes required labels, degraded insufficiency statements, bounded quote/anchor mentions, and forbidden positive assertions. This is strongest supported by same-source Ch3 evidence; broader cross-chapter applicability needs more calibration evidence.
- required output missing/degrade semantics.
- Chapter 0 referencing/consuming Chapter 7 final judgment bundle, not independently deriving the action.
- per-chapter typed `audit_focus`, with strict protection that it must not silently disable current programmatic blockers.

Rejected for accepted future design at this gate:

- Writing 0+9 or 0+10 chapter structure as accepted future design solely from the retained 006597 run.
- Any numerical claim that chapter splitting will reduce timeout probability by a specified percentage.
- Any direct 5-year PDF/raw text injection into LLM prompts.
- Any exact migration timeline, rollback duration, sample pass-rate threshold, or v1/v2 coexistence period without a separate plan/review gate.
- External draft D-2 style timeout root-cause allocation or percentages. The retained `small_prompt_provider_timeout` evidence does not support allocating Ch2/Ch4/Ch6 timeout root cause to contract complexity, prompt size, or audit focus percentages.

Deferred:

- Chapter 2 structural split vs no split.
- exact enum names and schema implementation form (`TypedDict`, dataclass, JSON Schema, or Pydantic-like validation).
- pressure-test threshold implementation shape beyond the requirement that thresholds become typed evidence/audit context.
- `first_class_facets` type, enum domain, resolution mechanism, and any programmatic facet-respect wiring.
- `source_strength_by_requirement` semantics unless a later gate defines strength levels and audit use.
- programmatic audit extensions for `data_availability_match`, `evidence_gap_declaration`, `cross_chapter_consistency`, and facet-respect checks. In this gate, matching `audit_focus` values are LLM semantic emphasis and repair hint categories only.

## Decision 1: typed ChapterContract

Recommendation:

Accept typed `ChapterContract` as proposed future design.

Rationale:

The current contract is natural-language heavy and relies on a fallible reasoner plus a literal programmatic checker to infer condition, polarity, evidence state, and chapter ownership. That violates the first-principles goal of CHAPTER_CONTRACT: reduce cognitive burden so a shortcut-prone reasoner reliably takes the next correct action. Typed clauses should make the machine contract explicit before prompt wording is tuned.

Direct evidence:

- Current template lists `must_answer`, `must_not_cover`, and `required_output_items` as free text.
- Ch3 requires `言行一致性判断` and also blocks `言行一致` phrase coverage under evidence-missing conditions.
- Retained Ch3 attempt 0 and attempt 1 both fail on the same programmatic C2 identity despite writer attempts to express evidence insufficiency.
- The accepted Agent-engine design already accepts typed audit contract as future architecture, with programmatic-first audit and runtime/content failure separation.

Future contract shape:

```text
ChapterContract
- chapter_id
- title
- narrative_mode
- must_answer: list[MustAnswerClause]
- must_not_cover: list[MustNotCoverClause]
- required_output: list[RequiredOutputItem]
- preferred_lens: map[FundType, TemplateLensRule]
- evidence_requirements: EvidenceRequirementSet
- audit_focus: list[AuditFocusLiteral]
- consumes_chapter_conclusions: list[chapter_id]
```

Accepted `chapter_id` range remains `0-7`, matching the current 8 chapter template. Any chapter renumbering, 0+9 structure, 0+10 structure, or public chapter count change requires a separate structural gate.

The typed schema must include stable ids for clauses and output items. Free-text labels may remain for writer readability, but audit identity should use ids, evidence requirements, assertion polarity, and missing behavior.

`MustAnswerClause` must not introduce an overlapping fallback system at this gate. Missing-evidence behavior is governed by `RequiredOutputItem.when_evidence_missing`; if a later gate wants clause-level missing behavior, it must define explicit precedence against required-output behavior before implementation. Until then, conflicting fallback semantics are rejected rather than left to implementer choice.

Non-goals:

- Do not implement `contracts_v2.py` in this gate.
- Do not replace the current 8 chapter template in this gate.
- Do not use typed contract as a reason to loosen existing C2/L1/R rules.
- Do not hide explicit parameters in `extra_payload`.

Validation/review implications:

- Future implementation gate must prove every current v1 clause maps to a typed id or is explicitly rejected by controller.
- Tests must include self-contradictory clause detection, especially required label vs forbidden assertion.
- Review must check Service/Host/Agent/Fund ownership: template contract semantics belong in Fund; Service may select scene/request contract; Host must not understand fund business clauses.

## Decision 2: EvidenceAvailability

Recommendation:

Accept `EvidenceAvailability` as proposed future design, with narrow semantics: it represents what the Fund/Agent evidence projection has actually made available for a chapter, not what the LLM infers from prose.

Rationale:

The Ch3 failure is not caused by lack of prose explaining that evidence is missing. The writer already wrote missing-evidence language, but the checker could not distinguish insufficiency from forbidden coverage. Evidence state must be an explicit machine input so writer, programmatic audit, and semantic audit are operating on the same source.

Direct evidence:

- Ch3 writer declared `<!-- missing:field_missing -->` for actual investment behavior and still hit C2 at `言行一致`.
- Ch3 `chapter-03.json` records `writer_declared_missing_reasons=["field_missing"]` and used facts for holdings/turnover, but the final contract check still reduced the issue to a forbidden phrase.
- Current design already requires LLM writing/audit to consume structured facts, derived calculations, EvidenceAnchor, and explicit data gaps, not raw PDFs or source helpers.

Future contract shape:

```text
EvidenceAvailability
- fund_code
- report_year
- chapter_id
- available_fact_ids
- available_anchor_ids
- unavailable_requirements
- data_gaps
- reviewed_evidence_flags
- not_applicable_flags
- data_tier_availability: map[Literal["1Y","3Y","5Y"], available | missing | not_applicable | unreviewed]
- available_report_years
- source_strength_by_requirement: deferred unless separately defined
```

`EvidenceAvailability` is a derived supplemental availability view over same-source chapter facts and anchors. It does not replace the current `ChapterFactProjection` unless a later gate explicitly accepts that replacement. The safe MVP relationship is: `ChapterFactProjection` remains the structured fact projection; `EvidenceAvailability` derives machine-readable availability, data gaps, reviewed/unreviewed states, not-applicable states, and year-tier/data-tier availability from that projection and its anchors.

`source_strength_by_requirement` is not accepted as an implementable field in this gate. A later gate may add it only after defining strength levels, how they differ from availability/data-tier flags, and whether they affect blocking audit decisions or only diagnostics.

For Ch3, example flags should distinguish:

- `manager_strategy_text.available`
- `actual_behavior.holdings_snapshot.missing_or_unreviewed`
- `actual_behavior.turnover_rate.missing_or_unreviewed`
- `style_change_evidence.cross_period.missing_or_unreviewed`
- `manager_alignment.available`

For Ch2-style time horizons, availability must distinguish partial data safely:

- `data_tier_availability["1Y"]`
- `data_tier_availability["3Y"]`
- `data_tier_availability["5Y"]`
- report-year coverage and not-applicable reasons for immature funds

Non-goals:

- Do not make LLM infer availability from natural-language fact snippets.
- Do not direct LLMs to read PDFs, cache files, source helpers, or retained reports.
- Do not use `EvidenceAvailability` to bypass `FundDocumentRepository`.
- Do not add 5Y raw evidence ingestion in this gate.

Validation/review implications:

- Future tests must cover available, missing, not-applicable, and unreviewed states separately.
- Programmatic audit should fail closed when a clause requires an availability flag that is absent or malformed.
- Review must check that availability is same-source with chapter facts and anchors.

## Decision 3: evidence-conditional must_not_cover

Recommendation:

Accept evidence-conditional `must_not_cover` as the most important future contract change for the retained Ch3 failure mode. Broader applicability across other chapters is plausible but not proven by this gate and requires additional evidence.

Rationale:

The root issue is not that `must_not_cover` should be softer. It is that the current clause cannot express when a phrase is a required label, when it is an allowed insufficiency statement, and when it is a forbidden positive assertion. The future design must preserve the prohibition while making its condition and assertion polarity machine-checkable.

Direct evidence:

- Template Ch3 must answer `言行一致性判断`.
- Template Ch3 must not infer style stability/style consistency/conduct consistency when turnover or style-change evidence is missing, unavailable, or unreviewed.
- Attempt 0 says it cannot judge consistency due to missing actual behavior evidence, but literal phrase `言行一致` is blocked.
- Attempt 1 says strategy direction is consistent while strict verification is unavailable, and is blocked again.
- Controller judgment classifies Ch3 as contract-shape/programmatic audit calibration evidence, not auditor looseness.

Future contract shape:

```text
MustNotCoverClause
- clause_id
- scope
- applies_when: EvidencePredicate
- forbidden_assertions:
  - phrase_or_concept
  - polarity: positive | negative | quasi_positive | unsupported_causal | any
  - allowed_contexts: required_label | evidence_gap_statement | quote | anchor_caption
- repair_guidance
```

Composition rule:

- `applies_when` gates clause applicability. If the evidence predicate is false, that specific clause does not participate in audit.
- If `applies_when` is true, programmatic C2 participation is independent of `audit_focus`; omitting an audit category from `audit_focus` must not disable a programmatic blocker.
- `audit_focus` only affects bounded LLM semantic audit emphasis and repair hint grouping in this gate.
- Evidence-disabled clauses are not checked. Evidence-enabled clauses are checked programmatically where a programmatic checker exists, regardless of `audit_focus`.

For Ch3:

```text
applies_when:
  any_missing_or_unreviewed(
    actual_behavior.turnover_rate,
    actual_behavior.holdings_snapshot,
    style_change_evidence.cross_period
  )
forbidden_assertions:
  - concept: 言行一致
    polarity: positive_or_quasi_positive
  - concept: 风格稳定
    polarity: positive_or_quasi_positive
allowed_contexts:
  - required_output_label
  - explicit evidence-gap statement that says no judgment can be made
```

`allowed_contexts` semantics:

- Programmatic C2 is expected to use `allowed_contexts` when implementing evidence-conditional `must_not_cover`; otherwise the retained Ch3 C2 failure mode is not fixed.
- `required_label` is limited to the required output item's label or marker and cannot contain a positive conclusion.
- `evidence_gap_statement` is limited to statements that explicitly say evidence is missing, unavailable, unreviewed, not applicable, or insufficient for a conclusion.
- `anchor_caption` is limited to identifying evidence source/position and cannot add analysis beyond the anchor description.
- `quote` is limited to a bounded direct quotation or source label needed for evidence traceability. A quote may mention a forbidden phrase, but it cannot be used to add, imply, or launder a positive conclusion in the writer's own voice.

Partial availability behavior:

- When some evidence requirements are available and others are missing/unreviewed, the writer may make a bounded conclusion only over the available evidence and must explicitly name the missing evidence boundary.
- For Ch3, turnover-only evidence may support a narrow statement about observed turnover, but cannot support positive or quasi-positive `言行一致` or `风格稳定` conclusions while holdings/cross-period style-change evidence is missing or unreviewed.
- Programmatic audit should treat the full forbidden positive conclusion as still blocked when any predicate component required for that conclusion is missing or unreviewed.
- Missing evidence cannot be converted into a positive conclusion through softer wording such as "倾向一致", "基本一致", "未见明显不一致", or similar quasi-positive phrasing unless a separate polarity calibration gate proves the detector can handle those patterns.

Non-goals:

- Do not simply add stopwords for `言行一致`.
- Do not globally disable phrase matching.
- Do not allow positive `言行一致` conclusions without reviewed actual-behavior evidence.
- Do not merge this with provider runtime budget or Ch2/Ch6 timeout work.
- Do not accept brittle global Chinese phrase matching as the implementation solution for polarity/quasi-positive detection. Before any implementation gate creates polarity-bearing `MustNotCoverClause` behavior, a separate feasibility/calibration step must demonstrate acceptable detection behavior for Chinese positive, negative, quasi-positive, and unsupported-causal assertions.

Validation/review implications:

- Need fixtures for: required label only, explicit insufficiency statement, quasi-positive consistency claim, and positive consistency claim with reviewed evidence.
- Programmatic audit should produce stable issue ids tied to `clause_id`, not just phrase hash.
- Review must verify no regression in forbidden investment advice, future return prediction, motivation guessing, or unsupported causal inference.

## Decision 4: required_output missing/degrade semantics

Recommendation:

Accept typed missing/degrade semantics for `required_output`.

Rationale:

A required output item has two different obligations: the chapter must address the item, and the chapter must not invent facts when required evidence is missing. The current natural-language contract makes these obligations compete. The future design should tell the writer exactly whether to render an evidence gap, delete an inapplicable item, or degrade to the next verification question.

Direct evidence:

- Ch3 required output includes `实际投资行为（§8）`, `言行一致性判断`, and `风格稳定性判断`.
- Ch3 writer produced missing markers and still failed C2 because required-output labels and forbidden phrases were not separable.
- Ch2 required outputs demand 1Y/3Y/5Y data and cost decomposition; Chapter 2 writer already declared `field_not_applicable` and deleted some item rules before auditor timeout. This is evidence that output presence/deletion/gap semantics already exist in practice but are not first-class enough in the template contract.
- Current design says missing facts must result in `未披露 / 数据不足 / 下一步最小验证问题`, not pseudo alpha or unsupported conclusions.

Future contract shape:

```text
RequiredOutputItem
- item_id
- label
- required_in_chapter: true | false
- evidence_required
- when_evidence_missing:
  - render_evidence_gap
  - render_minimum_verification_question
  - delete_if_not_applicable
  - block
- marker_policy
- allowed_missing_reasons
```

Semantics:

- `required_in_chapter=true` means the item must be addressed.
- Missing evidence may satisfy the item only through an approved evidence-gap/degrade output.
- `delete_if_not_applicable` requires a typed deletion reason; it is not a silent omission.
- `block` is reserved for core facts whose absence makes the chapter unsafe. A missing item should block only when any substantive conclusion in that chapter would become unreliable, when downstream Ch7 final judgment would be unsafe, or when the contract authoring gate explicitly marks the item as non-degradable and reviewers accept that item-level reason.
- `RequiredOutputItem.when_evidence_missing` is the only accepted missing-evidence behavior in this gate. Clause-level fallback is deferred; if both mechanisms are later introduced, `block` must take precedence unless the controller accepts a stricter item-level exception.

Non-goals:

- Do not let `required_output` become optional by default.
- Do not allow placeholder values such as fake 5Y data or generic `未披露` without a typed reason.
- Do not modify current renderer or auditor in this design artifact.

Validation/review implications:

- Tests must assert marker presence and allowed missing reason identity.
- Review must inspect whether degrade text still answers the chapter goal without fabricating a conclusion.
- Future acceptance should include at least one missing-evidence fixture per high-risk chapter: Ch2, Ch3, Ch6, Ch7.

## Decision 5: Ch0 Referencing Ch7

Recommendation:

Accept as proposed future design: Chapter 0 must consume a Chapter 7 final judgment bundle and must not independently derive the action.

Rationale:

Chapter 0 is a front-page compression layer. It should not be a second final-judgment engine. A fallible LLM asked to generate both Ch0 and Ch7 independently can create cross-chapter inconsistency. The lower-cognitive-burden design is one source of final action truth, then a constrained summary.

Direct evidence:

- Current template Ch0 requires current action.
- Current template Ch7 also requires final action.
- Current design already says Ch0 summarizes accepted conclusions and does not introduce new facts or judgments.
- Current Route C final assembly already generates Ch7 before Ch0 deterministically.
- `summary.json` final assembly blocks incomplete reports when required chapters are not accepted, showing the final report path already treats accepted chapter availability as a precondition.

Future contract shape:

```text
ChapterContract(chapter_id=0)
- consumes_chapter_conclusions: [7]
- must_answer includes action only as "render final_judgment.action"
- must_not_cover includes "do not independently recalculate or reinterpret final action"
- required_output item "current_action" source = chapter_7.final_judgment.action
- final assembly constraint: fail closed if any required body chapter, currently chapters 1-6, is not accepted
```

The Ch7 bundle should include:

- action: `值得持有 | 需要关注 | 建议替换`
- primary_reason
- largest_risk
- minimum_verification_question
- upgrade_or_downgrade_threshold
- evidence/readiness status

Ch0 must not mask unsafe Ch7. Final assembly must fail closed when required body chapters are incomplete, rejected, or unaccepted, even if a Ch7-looking bundle exists. If a later structural gate accepts a Ch2 split, the Ch7 dependency chain and Ch0 final-assembly preconditions must be revisited in the same structural gate.

Non-goals:

- Do not create a new action taxonomy.
- Do not permit Ch0 to output a stronger conclusion than Ch7.
- Do not implement Ch0 LLM polish in this gate.
- Do not write any new chapter count as current fact.

Validation/review implications:

- Need cross-chapter consistency tests where Ch0 action must equal Ch7 action.
- Need failure tests where Ch7 unavailable means Ch0 cannot be assembled as a complete report.
- Review should check that Ch0 does not import new facts, new anchors, or new reasoning.

## Decision 6: Ch2 Split vs No Split

Recommendation:

Defer structural Chapter 2 split. Do not accept 0+9 structure or Ch2 split as future design yet. Accept only the narrower future-design requirement that old Chapter 2 should be representable as internal typed organizational units for performance, attribution, and cost within the single current Chapter 2.

Rationale:

The external draft's split is plausible from first principles: Ch2 currently combines multiple cognitive tasks. But the retained Ch2 evidence is an auditor provider timeout classified by controller as a provider runtime blocker, not direct proof that chapter structure caused the failure. A heavy structural chapter change affects public report contract, renderer, final assembly, cross-chapter references, docs, tests, snapshots, and retained evidence interpretation. Same-source evidence does not yet justify accepting the split.

Direct evidence:

- Ch2 current contract combines return, benchmark, alpha calculation, structural/stage alpha, cost decomposition, and cost reasonableness.
- Ch2 retained run failed in auditor timeout with small prompt diagnostics, not with prompt-contract or missing-output diagnostics.
- Controller judgment says Ch2 should not be touched in the next Ch3-only calibration gate and should defer to provider runtime budget calibration.
- `docs/design.md` already marks future chapter mapping as a gate topic, not current renderer fact.

Future contract shape:

```text
Chapter 2 internal typed organizational units, not split chapters:
- performance_subcontract: R and benchmark availability
- attribution_subcontract: alpha calculation and structural/stage judgment
- cost_subcontract: explicit costs, inferred/derived costs, cost coverage
```

These units must remain inside a single `ChapterContract(chapter_id=2)`. They must not have independent chapter ids, must not appear as separate chapter-matrix rows, must not change renderer/public chapter count, and must not imply acceptance of 0+9/0+10 numbering. Typed contract precision and structural chapter split are independent design dimensions: this gate accepts the former and defers the latter.

If a later controller accepts a split, the split decision should separately define:

- new chapter ids and titles;
- old-to-new mapping;
- Ch0/Ch7 conclusion dependency changes;
- renderer/final assembly impacts;
- evidence availability routing;
- backward compatibility/non-compatibility decision;
- validation sample and review matrix.
- updated Ch7 `consumes_chapter_conclusions` dependency chain, including how performance, attribution, and cost conclusions feed final judgment.

Non-goals:

- Do not write `0+9` or `0+10` as accepted future design from this gate.
- Do not use Ch2 timeout as proof of template structural defect.
- Do not alter current report chapter ids or retained reports.
- Do not set acceptance-rate targets here.

Validation/review implications:

- Before structural split, require a separate planreview or design review with at least two independent reviewers.
- Need same-source evidence beyond one provider-timeout run, ideally multiple funds and at least one direct prompt-contract failure tied to overloaded Ch2 semantics.
- A safer first validation is typed subcontracts while preserving current chapter id.

## Decision 7: per-chapter audit_focus

Recommendation:

Accept per-chapter typed `audit_focus` as proposed future design, but constrain it so it cannot silently relax current programmatic audit rules.

Rationale:

The current global focus list asks every chapter to carry the same semantic audit burden. That is high cognitive load and weakly aligned with chapter-specific risk. However, `audit_focus` cannot become a switch that disables core programmatic invariants. It should initially guide LLM semantic audit emphasis, diagnostics, and repair hints; programmatic blockers remain always-on unless a later gate explicitly changes severity/rule selection.

Direct evidence:

- Current auditor focus is global: `evidence_support`, `must_not_cover_boundary`, `missing_semantics`, `readability`, `non_asserted_facet_boundary`.
- Ch3 failure is programmatic `must_not_cover` identity; Ch2/4/6 terminal failures are auditor timeouts.
- External draft correctly identifies that one global focus list does not express chapter differences, but it overreaches if it claims focus subsetting alone will fix provider runtime timeouts.
- Accepted Agent design says LLM auditor should be bounded semantic audit, while programmatic-first audit handles mechanically checkable rules.

Future contract shape:

```text
AuditFocusLiteral
- evidence_support
- must_not_cover_boundary
- missing_semantics
- readability
- non_asserted_facet_boundary
- evidence_gap_declaration
- evidence_conditional_assertion
- cross_chapter_consistency
- data_availability_match
- first_class_facet_respect
```

Initial safe semantics:

- `audit_focus` controls only bounded LLM auditor semantic emphasis and repair hint grouping in this gate.
- Programmatic C2, required markers, anchor validation, missing/degrade policy, forbidden investment advice, and implemented L1/R rules stay always-on.
- Programmatic checks for `data_availability_match`, `evidence_gap_declaration`, `cross_chapter_consistency`, and `first_class_facet_respect` are separate programmatic audit extension gates. Adding their names to `audit_focus` does not implement those checks and does not let LLM-only focus substitute for programmatic blockers.
- Evidence-conditional clause predicates decide whether a clause is applicable; `audit_focus` never controls programmatic participation.
- Any future change that lets `audit_focus` disable a blocking programmatic rule must be a separate heavy gate.

Non-goals:

- Do not reduce the five current audit concepts without explicit review.
- Do not use per-chapter focus to hide Ch3 C2 or Ch6 pressure-test issues.
- Do not claim timeout improvement until measured.

Validation/review implications:

- Need tests proving all current blocking programmatic issues still fire when a chapter has a smaller focus list.
- Need auditor-prompt tests proving chapter-specific focus is included without leaking raw prompts or provider responses into artifacts.
- Review must inspect severity mapping and fail-closed behavior.

## What Must Not Enter Accepted Future Design Yet

The following should not be proposed as accepted future design from this gate:

- `0+9` or `0+10` chapter structure as an accepted target.
- Exact chapter renumbering for Ch2/Ch3/Ch4/Ch5.
- Exact timeout-improvement percentages or acceptance-rate targets.
- External draft D-2 style percentage/root-cause allocation for timeout failures. Ch2/Ch4/Ch6 timeout evidence remains provider runtime gate evidence because retained diagnostics show `small_prompt_provider_timeout`.
- Exact migration stages, dates, coexistence durations, or file names.
- Direct 5Y PDF/raw text injection into LLM context.
- Provider budget changes, timeout changes, score-loop wiring, deterministic fallback, stdout partial-report behavior, prompt/provider budget changes, or auditor relaxation.
- Any change to quality gate, golden promotion, final judgment semantics, release readiness, PR state, or retained report format.
- Any current-fact wording that says the typed template redesign is implemented.
- Any production dependency on `dayu-agent`, `dayu.host`, or `dayu.engine`.

## Non-Goals

- No code.
- No tests.
- No prompt change.
- No provider/runtime budget change.
- No auditor implementation change.
- No score-loop.
- No deterministic fallback.
- No stdout behavior change.
- No retained report edits.
- No design/control/template truth-source edits.
- No commit, push, or PR.

## Residual Risks And Open Questions For Controller

- Whether the next gate should be a narrow Ch3 contract-shape plan or a broader typed contract schema plan. Same-source evidence most strongly supports Ch3 first.
- Whether typed programmatic rule profiles should be designed in a separate follow-up phase after this gate's MVP `audit_focus` LLM-semantic-only boundary.
- Whether the current accepted future 0-10 mapping in `docs/design.md` should be reconciled before any Ch2 split discussion, to avoid competing structural futures.
- How to represent assertion polarity robustly in Chinese text without falling back to brittle phrase matching; this is a mandatory precondition before implementation, not an accepted implementation detail.
- Whether the derived `EvidenceAvailability` MVP can be built only from current `ChapterFactProjection`, or whether a new evidence bundle is needed in a later gate.
- Whether future Ch2 split or other structural changes require revising the Ch7 dependency chain beyond the current fail-closed Ch0/Ch7 constraint.
- Whether pressure-test thresholds should be part of `EvidenceAvailability`, `preferred_lens`, or a separate typed risk context.

## Handoff Criteria

Accepted decisions for the next design/plan gate:

- Typed `ChapterContract` may be referenced as accepted future contract direction while preserving current chapter ids `0-7`.
- `EvidenceAvailability` may be referenced as a derived supplemental availability view over `ChapterFactProjection`, not as a replacement.
- Evidence-conditional Ch3-style `must_not_cover` may be referenced as accepted future direction, with `allowed_contexts`, partial availability, and polarity-calibration preconditions.
- `RequiredOutputItem.when_evidence_missing` is the accepted missing/degrade mechanism; overlapping `MustAnswerClause` fallback is deferred.
- Ch0 consuming Ch7 is accepted only with fail-closed final assembly when required body chapters are not accepted.
- Per-chapter `audit_focus` is accepted only for LLM semantic emphasis and repair hint grouping; it does not control programmatic blockers.

Deferred or rejected items:

- Ch2 structural split, 0+9/0+10 numbering, public chapter count changes, and independent subchapter ids are deferred to a separate structural gate.
- `first_class_facets` implementation and facet-respect programmatic wiring are deferred to a separate facet wiring/programmatic audit gate.
- `source_strength_by_requirement` is deferred unless a later gate defines the levels and audit semantics.
- Timeout root-cause percentages, acceptance-rate targets, migration timelines, provider budget changes, raw 5Y PDF/text injection, quality gate changes, golden promotion, final-judgment taxonomy changes, and runtime implementation changes are rejected for this gate.

Mandatory preconditions before implementation:

- Run a Chinese assertion polarity/quasi-positive feasibility or calibration step before implementing polarity-bearing `MustNotCoverClause` behavior; brittle global phrase matching is not an accepted solution.
- Define item-level `block` criteria for any required output item that can fail closed.
- Define programmatic matching boundaries for `allowed_contexts`, especially `quote` and `anchor_caption`.
- Confirm the next implementation gate scope: likely either Ch3-only contract-shape calibration or a broader typed contract schema plan with Ch3 as the first calibration target.

Next likely gate options:

- Ch3-only evidence-conditional `must_not_cover` calibration plan.
- Typed `ChapterContract` schema plan that preserves chapter ids `0-7` and uses Ch3 as the first fixture.
- Provider runtime budget/timeout gate for Ch2/Ch4/Ch6.
- Separate facet wiring/programmatic audit extension gate.

## Validation And Secret Safety

Validation to run for this artifact:

```bash
git diff --check -- docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md
```

Secret-safety statement: this artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw prompt body, or secret-bearing runtime payload. It references only safe local artifact paths, safe diagnostic labels, and short public/template excerpts needed for design review.
