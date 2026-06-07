# MVP Real LLM Chapter Acceptance Calibration Slice 1D Plan

## 1. Goal

Fix the deterministic prompt-contract root of Ch2 `l1_numerical_closure` without live LLM, provider/runtime changes, auditor relaxation, template JSON changes, or repair-budget changes.

## 2. Direct Evidence

Retained post-config live artifact:

- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-02.json`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-02-attempt-00-writer.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-02-attempt-01-repair.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-02-attempt-00-auditor-feedback.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-02-attempt-01-auditor-feedback.md`

Observed facts:

- Ch2 terminal failure is `failure_category=prompt_contract`, `failure_subcategory=l1_numerical_closure`.
- Attempt 0 has seven required-output marker C2 issues, one L1 issue and three blocking LLM C1 issues.
- Attempt 1 has seven required-output marker C2 issues, one `delete_if_not_applicable` C2 issue, two L1 issues and one reviewable LLM C1 issue.
- Slice 1A already fixed the typed required-output marker protocol locally, so this slice must not reimplement marker checking.
- Attempt 0 writer placed a concrete `A = R - B = 2.57% - 3.42% = -0.85%` statement without a nearby anchor in item 03.
- Attempt 1 repair moved anchors into item 03 and item 07, but still repeated concrete R/A/B/C percentages in `### 结论要点` without nearby anchors and repeated source percentages plus `R=A+B-C` wording in `### 证据与出处` without anchor markers.
- Current `_audit_numerical_closure()` intentionally blocks R/A/B/C closure lines that contain concrete percentages and lack a nearby `<!-- anchor:... -->`; this guard should stay fail-closed.

## 3. Root Hypothesis

Ch2 writer guidance says formula or percentage closure assertions need nearby anchors, but it is too easy for a real model to treat that as applying only to the detailed required-output section. The model then repeats numeric closure claims in summary or evidence-source prose without nearby marker context.

The correct local fix is prompt-contract hardening and repair-context specificity:

- Ch2 numeric closure statements are permitted only when each line/bullet containing R/A/B/C/A-C percentages also contains allowed anchor markers in the same bullet or adjacent line.
- `### 结论要点` should summarize the direction of the conclusion without repeating unanchored formula percentages, unless it carries the same allowed anchors.
- `### 证据与出处` should list source labels or anchor-backed statements; it must not repeat R/A/B/C formula percentages without markers.
- Repair context for `programmatic:L1` should explicitly name the summary/evidence-section repetition failure pattern.

This is not an auditor-rule relaxation and not a Ch2 schema/template split.

## 4. Scope

Allowed production files:

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/README.md`

Allowed tests:

- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py` only for deterministic regression coverage proving the auditor remains fail-closed.

Allowed evidence/control artifacts:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-plan-20260607.md`
- `docs/reviews/plan-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-implementation-evidence-20260607.md`
- `docs/reviews/code-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-implementation-controller-judgment-20260607.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 5. Non-Goals

- Do not run live LLM.
- Do not change provider/default/runtime/budget/config.
- Do not change `_audit_numerical_closure()` to accept unanchored closure percentages.
- Do not increase repair budget or change repair retry policy.
- Do not change extractor, projection schema, template JSON, quality gate, score-loop or golden/readiness state.
- Do not fix Ch4 `audit_parse`.
- Do not fix Ch3/Ch5 LLM blocking residuals.
- Do not fix the remaining Ch2 `delete_if_not_applicable` marker-obligation residual unless a failing deterministic test proves it is inseparable from the L1 prompt fix.
- Do not claim Ch2 live acceptance or full report acceptance.

## 6. Implementation Decisions

1. Add a Ch2-specific writer protocol paragraph in `chapter_writer.py`:
   - if a line or bullet contains `R=`, `A=R-B`, `A-C`, `R=A+B-C` or a concrete R/A/B/C closure percentage, it must include allowed anchor markers in the same bullet or adjacent line;
   - in `### 结论要点`, prefer non-numeric directional wording unless the same bullet carries the required allowed anchors;
   - in `### 证据与出处`, cite source labels and anchors; do not re-state formula percentages without marker context.

2. Strengthen `programmatic:L1` repair corrections generated for typed repair context in Service `chapter_orchestrator.py`:
   - explicitly tell the writer to repair unanchored numeric closure not only in detailed items, but also in conclusion and evidence-source sections;
   - preserve existing `previous_issue_ids`, `previous_messages` and typed repair context shape.

3. Keep `_audit_numerical_closure()` unchanged:
   - L1 remains fail-closed for concrete R/A/B/C closure percentages without nearby anchor marker;
   - existing tests proving L1 block/allow behavior remain valid.

4. Do not change required-output marker parsing/checking:
   - Slice 1A already covers typed item-id markers for the current typed path;
   - Ch2 retained marker C2 rows should remain residual evidence unless deterministic post-Slice 1A tests prove otherwise.

## 7. Tests

Add focused deterministic tests:

- `tests/fund/test_chapter_writer.py`
  - Ch2 writer prompt contains summary/evidence-section numeric closure anchor guidance.

- `tests/services/test_chapter_orchestrator.py`
  - `programmatic:L1` repair context contains a correction that names conclusion/evidence-source numeric closure repetition and requires allowed anchor markers.
  - A fake Ch2 repair output that moves the same concrete closure sentence next to allowed anchors can be accepted by programmatic audit.

- `tests/fund/test_chapter_auditor.py`
  - A Ch2-style `### 证据与出处` line that repeats concrete percentages plus `R=A+B-C` without anchor remains blocked by L1.
  - The same line with nearby allowed anchor marker is not blocked by L1.

## 8. Validation Commands

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Expected: pass.

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Expected: pass.

```bash
uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

Expected: pass.

```bash
git diff --check -- fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py fund_agent/fund/README.md tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

Expected: pass.

## 9. Completion Criteria

Slice 1D can be accepted locally if:

- Ch2 writer prompt explicitly prevents unanchored numeric closure repetition in summary and evidence-source sections.
- `programmatic:L1` repair context points to the same concrete failure pattern.
- L1 auditor remains fail-closed and unchanged for unanchored numeric closure percentages.
- Focused tests and regression tests pass.
- No live LLM, provider/runtime/config, template JSON, quality gate, score-loop, golden/readiness or Agent runtime changes occur.

## 10. Residuals After Acceptance

- Ch2 live acceptance remains unproven until a separately authorized live evidence gate.
- Ch2 required-output marker C2 rows are expected to be covered by Slice 1A in typed path but remain unproven against live output.
- Ch2 `delete_if_not_applicable` marker-obligation residual may require a separate slice if retained or deterministic evidence shows it survives.
- Ch4 `audit_parse`, Ch3/Ch5 LLM blocking residuals and any surviving Ch6 pressure-test C2 remain separate routes.
