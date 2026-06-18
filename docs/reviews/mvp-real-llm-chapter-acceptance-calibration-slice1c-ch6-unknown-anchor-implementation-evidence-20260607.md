# MVP Real LLM Chapter Acceptance Calibration Slice 1C Implementation Evidence

## 1. Scope

- Gate: `Real LLM chapter acceptance calibration gate`
- Slice: `1C - Ch6 unknown_anchor prompt-contract hardening`
- Plan: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-plan-20260607.md`
- Plan review: `docs/reviews/plan-review-20260607-093454.md`
- Controller judgment: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-controller-judgment-20260607.md`

This slice did not run live LLM and did not change provider/default/runtime/budget/config, template JSON, extractor/projection schema, quality gate, score-loop, golden/readiness, Agent runtime, Host runtime, PR, push or release state.

## 2. Root Cause Addressed

Retained artifact Ch6 terminal failure:

- `failure_category=prompt_contract`
- `failure_subcategory=unknown_anchor`
- `writer:unknown_anchor:chapter-anchor:006597:2024:ch6:structured.bond_risk_evidence`

The writer parser correctly fail-closed because that anchor is not in `prompt.allowed_anchor_ids`. The local root addressed here is prompt ambiguity: the writer prompt did not explicitly tell the model that anchors must never be synthesized from `fact_id`, `source_field_id`, `source_field_name` or nested fact values, and did not explicitly call out `bond_risk_evidence` internal/group anchors as non-citeable.

## 3. Files Changed

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`
- `fund_agent/fund/README.md`
- this evidence artifact

## 4. Implementation Summary

`chapter_writer.py`:

- Added a general anchor contract line:
  - do not synthesize anchor ids from fact metadata or fact values;
  - if a fact is available but has no `evidence_anchor_ids`, discuss it without anchor marker or use approved missing/verification wording when missing.
- Added `_bond_risk_anchor_contract_prompt(chapter)`:
  - emits a Ch6/bond-risk-specific instruction when current facts include `bond_risk_evidence`;
  - states that internal/group bond-risk anchors are not `ChapterEvidenceAnchor`;
  - restricts citation to the `allowed anchors` list.
- Kept `_parse_anchor_markers()` and `_unknown_anchor_issue()` fail-closed behavior unchanged.
- Did not expand group anchors into `ChapterEvidenceAnchor`.

Tests:

- Added prompt contract test for Ch6 bond fund prompt wording.
- Added parser regression for synthesized `chapter-anchor:<fund>:<year>:ch6:structured.bond_risk_evidence`.
- Existing projection and writer unknown-anchor tests remain in coverage.

README:

- Updated Fund writer behavior to document synthesized-anchor prohibition and bond-risk internal/group anchor non-citeability.

## 5. Validation

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_facts.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Result: `177 passed in 1.18s`

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Result: `47 passed in 0.93s`

```bash
uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py
```

Result: `All checks passed!`

## 6. Residuals

- Ch6 live acceptance is not proven. This slice only hardens deterministic prompt contract and parser regression coverage.
- Ch6 attempt 0 also had required-output marker C2 and `must_not_cover` pressure-test C2 in the retained artifact; marker C2 is locally covered by Slice 1A, but pressure-test wording may still need a later Ch6 content/audit slice if it survives unknown-anchor hardening.
- Ch2 `l1_numerical_closure`, Ch4 `audit_parse`, and Ch3/Ch5 LLM blocking residuals remain separate routes.
- Future bond-risk group-anchor conversion remains a separate schema/contract gate if group anchors should become citeable.

## 7. Verdict

`SLICE_1C_IMPLEMENTED_LOCALLY`

Ch6 synthesized/internal bond-risk anchor prompt ambiguity is locally hardened without relaxing fail-closed parser behavior.
