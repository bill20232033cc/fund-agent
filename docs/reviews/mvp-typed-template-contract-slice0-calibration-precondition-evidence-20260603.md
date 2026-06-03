# MVP typed template contract Slice 0 calibration/precondition evidence

## Worker Self-Check

- Role: evidence/planning worker only; not controller and not implementation worker.
- Gate: `MVP typed template contract Slice 0 calibration/precondition gate`.
- Classification: `heavy`.
- Scope: docs/evidence artifact only.
- Output path: `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md`.
- Sources read: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-typed-template-contract-implementation-planning-controller-judgment-20260603.md`, and scoped code/evidence files allowed by this gate.
- Actions intentionally not taken: no source code edit, no tests edit, no template truth edit, no provider/runtime/default/golden/readiness/score-loop edit, no live provider run, no commit, no push, no PR.
- Public chapter ids must remain `0-7`.

## 1. Output Form Decision

Slice 0 output form is **reference markdown only**.

This artifact is the accepted calibration source for later implementation slices. It does not create a reusable fixture/test-data module because the current gate explicitly forbids source and test implementation. Creating a fixture module under `tests/` or `fund_agent/` would be test/data implementation, not docs-only evidence.

Future Slice 4 owns programmatic encoding of this taxonomy into tests and fixtures. A future implementation may create a fixture module only after controller authorization, and it must preserve this artifact as the reviewed reference. Suggested future fixture shape, not created in Slice 0:

- `tests/fund/fixtures/ch3_polarity_cases.py`
- each case has `case_id`, `chapter_id=3`, `text`, `expected_context`, `expected_polarity`, `availability_state`, `expected_blocked`, and `notes`.
- case ids must be stable and trace back to this artifact section names, for example `ch3_required_label_allowed_001` and `ch3_quasi_positive_unreviewed_block_001`.

## 2. Chinese Assertion Polarity / Quasi-Positive Taxonomy

Scope: Ch3 `基金经理画像与言行一致性`, especially active-fund style claims around `言行一致`, `风格稳定`, and `风格一致`.

Terminology:

- `positive_assertion`: states or strongly implies reviewed consistency/stability is true.
- `quasi_positive_assertion`: softens a positive claim but still leaves the reader with a positive consistency/stability conclusion.
- `negative_or_risk_assertion`: states inconsistency, drift, or uncertainty as a risk.
- `neutral_label`: section label or required output marker with no judgment.
- `gap_statement`: explicit evidence insufficiency statement that blocks inference rather than making one.

Future Slice 4 must treat these as deterministic text categories, not LLM judgment.

| Category | Representative Chinese forms | Missing/unreviewed Ch3 style evidence behavior |
|---|---|---|
| `neutral_label` | `言行一致性判断：`, `风格稳定性判断：`, `一致性汇总边界：` | Allowed only in `required_label` context. |
| `gap_statement` | `证据不足`, `缺少已复核`, `不能据此判断`, `不输出一致性结论`, `需要复核后再判断` | Allowed only when the sentence denies inference and does not append a positive conclusion. |
| `positive_assertion` | `言行一致`, `风格稳定`, `风格一致`, `风格保持稳定`, `投资框架稳定`, `说的和做的一样` | Blocks when required evidence is missing, unavailable, or unreviewed. May pass only when typed evidence predicate is satisfied and all other audit rules pass. |
| `quasi_positive_assertion` | `基本一致`, `大体一致`, `较为一致`, `倾向一致`, `未见明显不一致`, `没有明显漂移`, `变化不大`, `基本稳定`, `相对稳定`, `延续原有风格` | Blocks under missing/unreviewed evidence. These are positive-enough for a reader and must not be treated as safe hedges. |
| `negative_or_risk_assertion` | `言行不一致`, `风格漂移`, `存在不一致风险`, `无法证明一致`, `尚不能确认稳定` | Does not satisfy a positive required output. It may be allowed if evidence supports the risk or if it is explicitly framed as a gap/risk, but Slice 4 must not use it to satisfy reviewed positive consistency. |
| `unsupported_causal_assertion` | `因为换手率低所以言行一致`, `持仓集中所以风格稳定` without reviewed supporting evidence | Blocks when the underlying evidence predicate is not satisfied; causal wording increases severity but does not change allowed contexts. |

Hard rule: under missing, unavailable, or unreviewed turnover/style-change evidence, `未见明显不一致` is **not** safe. It is a quasi-positive assertion because it converts absence of reviewed contradiction into a positive reader takeaway.

## 3. Deterministic Allowed Contexts Matching Spec

Allowed contexts are narrow exemptions around otherwise forbidden words. They must be matched by deterministic line/block structure and local lexical rules only; no LLM judgment.

### `required_label`

Allowed when all conditions hold:

- The matched phrase appears only before the first Chinese/ASCII colon in a single Markdown list item or heading-like line.
- The prefix is one of the reviewed required labels for Ch3: `言行一致性判断`, `风格稳定性判断`, `一致性汇总边界`, or future typed `RequiredOutputItem.required_label`.
- Text after the colon contains an explicit gap statement or non-assertive content, not a positive or quasi-positive claim.
- The line is not an evidence quote body and not a paragraph continuing a previous assertion.

Not allowed:

- `言行一致性判断：言行一致。`
- `风格稳定性判断：基本稳定。`
- required label followed by a positive conclusion in the same line.

### `evidence_gap_statement`

Allowed when all conditions hold:

- The same sentence contains a gap marker such as `证据不足`, `缺少已复核`, `缺少可复核`, `不可用`, `未复核`, `无法判断`, `不能据此判断`, or `不输出一致性结论`.
- The sentence denies inference with a negative predicate such as `不能`, `无法`, `不足以`, `不得`, or `不输出`.
- No positive or quasi-positive assertion appears after the denial in a way that reverses the gap, for example `但总体一致`.

Allowed example shape:

- `证据不足，当前缺少已复核的换手率或跨期风格变化证据，不能据此判断风格稳定、风格一致或言行一致。`

Blocked example shape:

- `证据不足，但未见明显不一致。`

### `quote`

Allowed only for bounded source quotes or quoted labels, with all conditions:

- The matched phrase is inside Chinese quotes or markdown quote formatting.
- The quote is immediately introduced as source wording, label text, or contract wording, not the author's conclusion.
- The same line or adjacent previous line contains a source/quote introducer such as `原文`, `披露`, `表述`, `合同`, `模板要求`, `引用`, or `标注`.
- A quote may not be used to launder the report's own positive conclusion. If the sentence after the quote says `因此言行一致` or equivalent, the assertion blocks.

### `anchor_caption`

Allowed only in evidence anchor metadata/caption zones:

- Markdown evidence line begins with `> 📎 证据：`.
- Or an internal anchor/comment/caption line uses the known anchor marker/caption format.
- The phrase is part of source description, field name, or caption, not body conclusion.
- Anchor captions do not satisfy positive consistency/stability requirements by themselves.

### Explicitly Not Allowed As Context

- Generic hedges such as `可能`, `倾向`, `目前看`, `未见明显` are not allowed contexts.
- The presence of `证据不足` anywhere in a paragraph does not whitelist all later positive wording.
- Required output labels do not authorize the same line to conclude `言行一致` or `风格稳定`.
- Retained provider/auditor text must not be inspected semantically by an LLM to decide context.

## 4. Ch3 C2 Current Code-Path / Root-Cause Evidence

Same-source code evidence shows two different current paths that must not be conflated.

### Current runtime path that emits `programmatic:C2:言行一致`

The emitting path is in `fund_agent/fund/chapter_auditor.py`, not in `fund_agent/fund/audit/contract_rules.py`.

- `audit_chapter_programmatic()` aggregates `_audit_must_not_cover(input_data)` into programmatic issues. Evidence: `fund_agent/fund/chapter_auditor.py:342-353`.
- `_audit_must_not_cover()` iterates `input_data.writer_input.chapter.contract.must_not_cover`, extracts phrases from each clause, and emits C2 when a phrase is found anywhere in draft markdown. Evidence: `fund_agent/fund/chapter_auditor.py:557-584`.
- `_must_not_cover_phrases()` removes the leading negative `不...` prefix, splits by punctuation and conjunctions, then keeps fragments length >= 4. Evidence: `fund_agent/fund/chapter_auditor.py:741-761`.
- `_clean_must_not_cover_fragment()` strips generic words but does not preserve assertion polarity or allowed contexts. Evidence: `fund_agent/fund/chapter_auditor.py:798-814`.
- Ch3 current manifest contains the must-not-cover clause `不在换手率或风格变化证据缺失、不可用、未复核时，推断主动基金风格稳定、风格一致或言行一致。` Evidence: `fund_agent/fund/template/contracts.py:373-378`.
- The same Ch3 manifest also requires labels `言行一致性判断` and `风格稳定性判断`. Evidence: `fund_agent/fund/template/contracts.py:379-386`.

Root-cause mapping from code: the current `_audit_must_not_cover()` path is a global substring match over extracted phrase fragments. It has no concept of `required_label`, `evidence_gap_statement`, `quote`, `anchor_caption`, evidence availability, or assertion polarity. Therefore `言行一致` can be emitted as `programmatic:C2` even when the text is a required label or a gap statement, if the phrase is present in markdown.

Safe retained artifact evidence, without raw prompt/provider/draft bodies:

- `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/chapters/chapter-03.json` contains safe diagnostic fields showing `issue_id=programmatic:C2:言行一致:db9a79f992`, `chapter_id=3`, `failure_category=prompt_contract`, `failure_subcategory=code_bug_other`, and `stop_reason=repair_budget_exhausted`.
- Similar safe issue/status fields appear in retained Ch3 artifacts for `20260602T220325Z` and `20260602T224137Z`.
- This retained evidence proves the emitted issue identity/status, but the root cause must be taken from same-source code above, not from raw provider or draft text.

### `_FORBIDDEN_CONTENT_RULES` is not the Ch3 `言行一致` path

`fund_agent/fund/audit/contract_rules.py` declares `_FORBIDDEN_CONTENT_RULES` as explicit deterministic marker mappings for a small set of must-not-cover items. Ch3 entries there cover `性格`, `人品`, and `动机`, not `言行一致`. Evidence: `fund_agent/fund/audit/contract_rules.py:185-195`.

This path should remain separate from Ch3 style-claim polarity enforcement.

### `_MUST_NOT_COVER_COVERAGE_RULES` currently declares Ch3 style clause non-programmatic

`fund_agent/fund/audit/contract_rules.py` also declares `_MUST_NOT_COVER_COVERAGE_RULES`. The Ch3 clause about missing turnover/style evidence is explicitly routed as `narrative_guidance`, with rationale that stable low-false-positive markers are lacking and current coverage is narrative/semantic/manual. Evidence: `fund_agent/fund/audit/contract_rules.py:197-281`.

The same module validates that a must-not-cover item cannot be both programmatic forbidden content and non-programmatic coverage in that coverage manifest. Evidence: `fund_agent/fund/audit/contract_rules.py:674-717`.

Important distinction: the coverage manifest's non-programmatic declaration does not stop `chapter_auditor.py` from separately extracting phrases from `chapter.contract.must_not_cover` and matching them globally. Future Slice 4 must resolve this duplication/conflict explicitly.

## 5. RequiredOutputItem Block Criteria

Future typed `RequiredOutputItem.when_evidence_missing` must distinguish three outcomes.

### Render Gap

Use `render_evidence_gap` when:

- The item is still required for reader orientation.
- Missing evidence can be safely disclosed without producing an unsupported conclusion.
- The output can include a required label plus explicit gap statement and next minimum verification question.

Ch3 examples:

- `言行一致性判断` under unreviewed style evidence should render a gap, not disappear.
- `风格稳定性判断` under unreviewed style evidence should render a gap, not a positive or quasi-positive conclusion.

### Block

Use `block` when:

- The required item cannot be truthfully rendered as a label, gap, or verification question.
- The item would force a positive causal/numerical/final judgment without required evidence.
- Missing evidence would make downstream final assembly unsafe.
- The missing state is `unreviewed` but the item is contractually required to assert reviewed evidence.
- A writer attempts to satisfy a required output with positive/quasi-positive wording under missing/unreviewed evidence.

Block means fail closed before accepting the chapter; it must not trigger deterministic fallback, partial stdout report, or auditor relaxation.

### Delete If Not Applicable

Use `delete_if_not_applicable` only when:

- The item is conditionally required by fund type/facet/typed predicate.
- The predicate is deterministically false or `not_applicable`.
- A typed reason is present and traceable.

It must not be used for active-fund Ch3 `言行一致性判断` or `风格稳定性判断`, because those labels remain required; missing evidence should render gap or block depending on whether safe degrade text is possible.

## 6. Existing Active-Fund Ch3 Renderer Degradation Preservation

Current design truth states that active-fund Ch3 renderer already has evidence-aware degradation behavior. Code evidence confirms:

- `_render_chapter_3()` sets `active_missing_evidence = _is_active_fund(input_data.structured_data)` and sends it into Ch3 consistency/style lines. Evidence: `fund_agent/fund/template/renderer.py:1086-1120`.
- For active funds, `_chapter_3_consistency_summary_line()` renders an explicit `证据不足` / `不能据此判断` line instead of a positive consistency conclusion. Evidence: `fund_agent/fund/template/renderer.py:1140-1159`.
- `_chapter_3_style_stability_line()` does the same for style stability. Evidence: `fund_agent/fund/template/renderer.py:1162-1177`.
- `_chapter_3_consistency_rollup_line()` says no consistency conclusion is output when evidence is missing. Evidence: `fund_agent/fund/template/renderer.py:1180-1199`.
- `_chapter_3_dimension_line()` preserves declared/actual fields but says it does not output a consistency conclusion. Evidence: `fund_agent/fund/template/renderer.py:1202-1230`.
- `_chapter_3_next_minimum_validation_line()` renders the minimum follow-up verification question. Evidence: `fund_agent/fund/template/renderer.py:1233-1249`.

Future typed missing/degrade semantics must formalize and extend this existing degradation path. They must not create a divergent parallel rule where renderer says `证据不足` but typed writer/auditor uses different wording or different availability semantics.

Current limitation to preserve as fact, not as final design: `_is_active_fund()` only checks `classified_fund_type == "active_fund"` and the current renderer treats active funds as missing reviewed style evidence by default. A future typed evidence gate may replace that coarse default with `EvidenceAvailability`, but it must preserve the visible degradation outcome when reviewed evidence is absent.

## 7. Future Slice 1 Adapter Mapping Rule

Slice 1 adapter from current natural-language `contracts.py` strings to typed ids must be explicit and reviewed.

Rules:

- No fuzzy matching.
- No substring matching.
- No embedding/LLM matching.
- No auto-normalization beyond exact whitespace-safe normalization reviewed in code.
- Every current `must_answer`, `must_not_cover`, and `required_output_items` string mapped into a typed contract must have a stable reviewed id.
- Any unmapped current string fails closed at load/validation time.
- Public chapter ids remain exactly `0-7`.
- Ch2 internal units may be typed subcontracts only under `chapter_id=2`; they must not appear as public chapter ids or chapter-matrix rows.

Suggested id style for later review, not implemented here:

- `ch3.must_answer.consistency_judgment`
- `ch3.must_answer.style_stability_judgment`
- `ch3.must_not_cover.no_style_consistency_claim_without_reviewed_evidence`
- `ch3.required_output.consistency_judgment`
- `ch3.required_output.style_stability_judgment`

## 8. Future Slice 4 Preconditions And Unresolved Decisions

Slice 4 must decide how typed `MustNotCoverClause` interacts with current enforcement paths before code changes.

Required decision:

- The Ch3 evidence-conditional style clause should **migrate out of the global phrase-extraction path** for that clause and into typed `MustNotCoverClause` enforcement with evidence predicate plus allowed contexts.
- `_FORBIDDEN_CONTENT_RULES` should continue to handle explicit always-forbidden marker rules such as personality/motivation/trading-advice categories.
- `_MUST_NOT_COVER_COVERAGE_RULES` must be updated or superseded consistently so the same clause is not simultaneously declared narrative-only and enforced by typed programmatic logic.
- `chapter_auditor.py` must not run both old phrase extraction and new typed clause enforcement for the same clause. Duplicate enforcement would preserve false positives and produce unstable issue identities.

Unresolved items for controller/Slice 4:

- Whether typed Ch3 clause fully replaces `_audit_must_not_cover()` only for mapped typed clauses, while legacy phrase extraction remains for unmapped clauses, or whether all must-not-cover enforcement migrates to typed explicit mappings.
- Exact stable issue id format if moving from `programmatic:C2:<phrase>:<hash>` to `programmatic:C2:<clause_id>`. Serializer and retained artifact impact analysis is mandatory before issue-id changes.
- Exact fixture module path and whether fixtures live under tests only or under a Fund-layer dev fixture package.
- Whether quote/anchor-caption context should be implemented as a general allowed-context engine or only for Ch3 clauses in the first Slice 4 acceptance target.

## 9. Verifier Matrix And DS/MiMo Review Checklist

| Area | Evidence to verify | Expected result |
|---|---|---|
| Output form | This artifact section 1 | Slice 0 is reference markdown only; future Slice 4 owns encoding. |
| Polarity taxonomy | Section 2 | Positive and quasi-positive claims block under missing/unreviewed evidence; labels and gaps are not treated as claims. |
| Allowed contexts | Section 3 | `required_label`, `evidence_gap_statement`, `quote`, `anchor_caption` are deterministic and narrow. |
| Current C2 path | Section 4 | `programmatic:C2:言行一致` maps to `chapter_auditor.py` phrase extraction, not `_FORBIDDEN_CONTENT_RULES`. |
| Coverage conflict | Section 4 and 8 | Ch3 style clause is currently narrative guidance in `contract_rules.py` but still reachable by `chapter_auditor.py`; Slice 4 must avoid duplicate enforcement. |
| Required output behavior | Section 5 | Gap vs block vs delete-if-not-applicable is explicit. |
| Renderer preservation | Section 6 | Existing active-fund Ch3 degradation is preserved/formalized, not bypassed. |
| Adapter mapping | Section 7 | Explicit reviewed mapping only; unmapped current strings fail closed. |
| Safety | Section 10 | No provider/runtime/PASS-only/Agent runtime/score-loop/golden/readiness changes. |

Review checklist:

- [ ] Does the taxonomy classify `未见明显不一致` as quasi-positive and blocking under missing/unreviewed evidence?
- [ ] Are required labels allowed only before the colon and only when the post-colon text is non-assertive?
- [ ] Does the artifact avoid using LLM judgment for allowed-context matching?
- [ ] Does the root-cause section cite same-source code rather than inferring from retained drafts?
- [ ] Does the artifact distinguish `_FORBIDDEN_CONTENT_RULES`, `_MUST_NOT_COVER_COVERAGE_RULES`, and `chapter_auditor.py` runtime phrase extraction?
- [ ] Does RequiredOutputItem behavior prevent silent deletion of active-fund Ch3 required labels?
- [ ] Does the future Slice 4 note require duplicate-enforcement avoidance and serializer impact analysis before issue-id changes?

## 10. Non-Goals And Safety Constraints

Non-goals:

- No implementation.
- No tests or fixture module creation.
- No edits to `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, source code, tests, provider config, runtime defaults, score-loop, golden/readiness, retained artifacts, or template truth.
- No public chapter id changes; preserve `0-7`.
- No Ch2 public split.
- No Agent runtime/tool-loop/score-loop/multi-year runtime work.
- No provider/runtime/PASS-only live probe.
- No commit, push, or PR.

Safety constraints:

- Programmatic audit remains fail-closed.
- No auditor relaxation and no fail-open behavior.
- `audit_focus` remains semantic-only and cannot disable programmatic blockers.
- Incomplete `--use-llm` remains fail-closed with empty stdout and no deterministic fallback.
- Annual report production access remains through `FundDocumentRepository`; this artifact does not access or quote raw PDF/parsed annual-report text.
- This artifact does not paste raw prompts, raw provider responses, raw audit responses, writer drafts, API keys, Authorization headers, request ids, base URLs, model values, or raw PDF text.

## Validation

Required validation after creating this artifact:

```bash
git diff --check -- docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md
```

