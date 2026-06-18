# MVP Real LLM Chapter Acceptance Calibration Slice 1C Plan

## 1. Goal

Fix the deterministic prompt-contract root of Ch6 `unknown_anchor` without live LLM, provider/runtime changes, projection migration, or parser relaxation.

## 2. Direct Evidence

Retained post-config live artifact:

- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-06.json`

Observed facts:

- Ch6 terminal failure is `failure_category=prompt_contract`, `failure_subcategory=unknown_anchor`, `terminal_stop_reason=unknown_anchor`.
- Attempt 1 writer parse reports two `writer:unknown_anchor` issues for `chapter-anchor:006597:2024:ch6:structured.bond_risk_evidence`.
- The writer issue message says `bond_risk_evidence 组级锚点未展开为 ChapterEvidenceAnchor，需后续 conversion helper 后才能引用`.
- Existing projection test `test_bond_risk_evidence_group_anchors_kept_in_value_and_not_expanded` asserts bond-risk group anchors stay inside the value and must not be expanded to `ChapterEvidenceAnchor`.
- Existing writer parser correctly blocks unknown anchors; this slice must not relax that guard.

## 3. Root Hypothesis

Ch6 writer prompt leaves room for the model to synthesize an anchor id from `source_field_id` / fact identity or internal `bond_risk_evidence` group evidence rather than using only `prompt.allowed_anchor_ids`.

The correct local fix is prompt-contract hardening:

- make `allowed anchors` the only citeable anchor source;
- explicitly forbid synthesizing anchor ids from `fact_id`, `source_field_id`, `source_field_name` or nested fact values;
- explicitly state that `bond_risk_evidence` group/internal anchors are not citeable until a future conversion helper creates `ChapterEvidenceAnchor`;
- preserve fail-closed parser behavior for any unknown anchor.

This is not a bond-risk evidence schema migration and not a group-anchor conversion implementation.

## 4. Scope

Allowed production files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/README.md`

Allowed tests:

- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py` only if needed for orchestration diagnostic regression.

Allowed evidence/control artifacts:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-plan-20260607.md`
- `docs/reviews/plan-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-implementation-evidence-20260607.md`
- `docs/reviews/code-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1c-ch6-unknown-anchor-implementation-controller-judgment-20260607.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 5. Non-Goals

- Do not run live LLM.
- Do not change provider/default/runtime/budget/config.
- Do not expand `bond_risk_evidence` group anchors into `ChapterEvidenceAnchor`.
- Do not change extractor, projection schema, template JSON, quality gate, score-loop or golden/readiness state.
- Do not relax unknown-anchor parser.
- Do not fix Ch2 `l1_numerical_closure`.
- Do not fix Ch4 `audit_parse`.
- Do not fix Ch3/Ch5 LLM blocking residuals.
- Do not claim Ch6 live acceptance or full report acceptance.

## 6. Implementation Decisions

1. Add a short writer protocol line in `chapter_writer.py`:
   - only `allowed anchors` may be used inside `<!-- anchor:<anchor_id> -->`;
   - never synthesize anchor ids from fact metadata or nested values;
   - if a fact is available but has no `evidence_anchor_ids`, discuss it without anchor marker or use allowed missing marker if the field is missing.

2. Add a Ch6/bond-risk-specific prompt note when current chapter facts include `source_field_name == "bond_risk_evidence"`:
   - internal/group bond-risk anchors are not citeable;
   - cite only anchors listed in `allowed anchors`;
   - if details are unavailable/compacted, write a bounded evidence gap or next verification question.

3. Do not change `_parse_anchor_markers()` or `_unknown_anchor_issue()`.

4. Do not change `project_chapter_facts()` behavior that keeps bond-risk group anchors inside value.

## 7. Tests

Add focused deterministic tests in `tests/fund/test_chapter_writer.py`:

- Prompt contract test for Ch6 bond fund:
  - built writer prompt includes "do not synthesize anchor ids" wording;
  - built writer prompt includes bond-risk internal/group anchor non-citeable wording;
  - prompt still includes `allowed anchors` section.

- Parser regression:
  - a draft that cites `chapter-anchor:<fund>:<year>:ch6:structured.bond_risk_evidence` remains blocked with `unknown_anchor`;
  - issue message still mentions group-level bond-risk anchor not expanded.

Existing tests that should continue passing:

- `test_bond_risk_evidence_group_anchors_kept_in_value_and_not_expanded`
- `test_writer_rejects_unknown_anchor_reference`
- `test_writer_reports_bond_risk_internal_anchor_message`
- typed marker tests from Slice 1A.

## 8. Validation Commands

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_facts.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Expected: pass.

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Expected: pass.

```bash
uv run ruff check fund_agent/fund/chapter_writer.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py
```

Expected: pass.

```bash
git diff --check -- fund_agent/fund/chapter_writer.py fund_agent/fund/README.md tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

Expected: pass.

## 9. Completion Criteria

Slice 1C can be accepted locally if:

- Prompt contract explicitly prevents synthesized anchors and bond-risk internal/group anchor citation.
- Unknown-anchor parser remains fail-closed.
- Projection still does not expand bond-risk group anchors.
- Focused tests and regression tests pass.
- No live LLM, provider/runtime/config, template JSON, quality gate, score-loop, golden/readiness or Agent runtime changes occur.

## 10. Residuals After Acceptance

- Ch6 live acceptance remains unproven until a separately authorized live evidence gate.
- Ch6 may still have content/audit residuals after unknown-anchor prompt hardening.
- Ch2 `l1_numerical_closure`, Ch4 `audit_parse`, and Ch3/Ch5 LLM blocking residuals remain separate routes.
- Future bond-risk group-anchor conversion remains a separate schema/contract gate if needed; this slice only prevents invalid citation of internal anchors.
