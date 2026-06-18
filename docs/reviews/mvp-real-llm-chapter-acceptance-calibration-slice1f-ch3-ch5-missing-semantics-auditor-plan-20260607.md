# MVP Real LLM Chapter Acceptance Calibration Slice 1F Plan

## 1. Goal

Fix the deterministic LLM-auditor prompt-contract root of Ch3/Ch5 remaining LLM blocking residuals by making bounded semantic audit respect approved missing markers and evidence gaps, without live LLM, provider/runtime changes, parser relaxation, template JSON changes, writer marker changes, or repair-budget changes.

## 2. Direct Evidence

Retained post-config live artifact:

- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-03.json`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-03-attempt-01-repair.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-03-attempt-01-auditor-feedback.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-05.json`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-05-attempt-01-repair.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-05-attempt-01-auditor-feedback.md`

Observed facts:

- Ch3 terminal failure is `failure_category=prompt_contract`, `failure_subcategory=code_bug_other`; Slice 1B already counted retained Ch3 as `marker_issues=12`, `llm_blocking_issues=6`, and marker sub-residuals are locally covered by Slice 1A.
- Ch3 attempt 1 repair marks manager basic info as `<!-- missing:field_missing -->`, but the LLM auditor still requires manager basic info anchors.
- Ch5 terminal failure is `failure_category=prompt_contract`, `failure_subcategory=code_bug_other`; Slice 1B already counted retained Ch5 as `marker_issues=8`, `llm_blocking_issues=1`, and marker sub-residuals are locally covered by Slice 1A.
- Ch5 attempt 1 repair marks cross-period comparison as `<!-- missing:cross_period_comparison_missing -->` and field gaps as `<!-- missing:field_missing -->`, but the LLM auditor still asks for cross-period / share-change anchors or extra data.
- Current auditor prompt already says message cannot require external sources, but it does not explicitly instruct the auditor to treat approved missing markers as acceptable evidence-gap handling.

## 3. Root Hypothesis

The bounded semantic auditor is over-enforcing evidence completeness. It treats absent facts/anchors as a semantic failure even when the writer has used approved missing markers and cautious gap wording. The parser and programmatic audit are doing the fail-closed checks; the LLM auditor needs a clearer boundary:

- do not require facts, anchors or external sources that are absent from allowed facts/anchors;
- if a required item uses an approved `<!-- missing:<reason> -->` marker and cautious gap wording, do not block merely because anchor-backed source data is unavailable;
- block only if the draft turns missing data into a positive assertion, omits the approved missing marker, cites an unknown anchor, or asks the user to accept unsupported conclusions.

This is auditor prompt-contract hardening, not writer/auditor parser relaxation.

## 4. Scope

Allowed production files:

- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/fund/README.md`

Allowed tests:

- `tests/fund/test_chapter_auditor.py`

Allowed evidence/control artifacts:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1f-ch3-ch5-missing-semantics-auditor-plan-20260607.md`
- `docs/reviews/plan-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1f-ch3-ch5-missing-semantics-auditor-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1f-ch3-ch5-missing-semantics-auditor-implementation-evidence-20260607.md`
- `docs/reviews/code-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1f-ch3-ch5-missing-semantics-auditor-implementation-controller-judgment-20260607.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 5. Non-Goals

- Do not run live LLM.
- Do not change provider/default/runtime/budget/config.
- Do not relax `_parse_llm_audit_response()`.
- Do not relax programmatic audit missing-marker, required-output marker or unknown-anchor checks.
- Do not change writer prompt, writer parser, required-output marker protocol or missing-marker parser.
- Do not store raw auditor response in diagnostics, reports or artifacts.
- Do not change extractor, projection schema, template JSON, quality gate, score-loop or golden/readiness state.
- Do not claim Ch3/Ch5 live acceptance or full report acceptance.

## 6. Implementation Decisions

1. Harden `ChapterAuditLLMRequest` prompt construction in `chapter_auditor.py`:
   - state that `<!-- missing:<reason> -->` is an approved evidence-gap marker when it uses an allowed missing reason and cautious wording;
   - state that the LLM auditor must not require unavailable facts, unavailable anchors, external sources or future data;
   - state that it may block missing sections only when the draft asserts a positive conclusion from missing evidence, omits required missing semantics, or contradicts allowed facts.

2. Keep parser and programmatic audit unchanged:
   - `_parse_llm_audit_response()` remains strict;
   - programmatic missing marker and required-output checks remain fail-closed.

3. Keep retained marker residuals routed to Slice 1A:
   - do not duplicate typed marker implementation.

## 7. Tests

Add or extend deterministic tests:

- `tests/fund/test_chapter_auditor.py`
  - Auditor prompt includes approved missing-marker / evidence-gap boundary instructions.
  - Auditor prompt explicitly forbids requiring unavailable facts, anchors or external sources.
  - Existing parser strictness tests continue to pass.

## 8. Validation Commands

```bash
uv run pytest tests/fund/test_chapter_auditor.py -q
```

Expected: pass.

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Expected: pass.

```bash
uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py
```

Expected: pass.

```bash
git diff --check -- fund_agent/fund/chapter_auditor.py fund_agent/fund/README.md tests/fund/test_chapter_auditor.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

Expected: pass.

## 9. Completion Criteria

Slice 1F can be accepted locally if:

- LLM auditor prompt explicitly respects approved missing markers and cautious gap wording.
- LLM auditor prompt forbids asking for unavailable facts/anchors/external sources.
- Parser and programmatic audit strictness are unchanged.
- Focused tests and regression tests pass.
- No live LLM, provider/runtime/config, template JSON, quality gate, score-loop, golden/readiness or Agent runtime changes occur.

## 10. Residuals After Acceptance

- Ch3/Ch5 live acceptance remains unproven until a separately authorized live evidence gate.
- Ch3/Ch5 retained required-output marker C2 live proof remains unproven, although Slice 1A covers typed marker protocol locally.
- Ch2 `delete_if_not_applicable` marker-obligation residual may require a separate slice if deterministic evidence shows it survives.
- Any surviving Ch6 pressure-test C2 remains separate.
