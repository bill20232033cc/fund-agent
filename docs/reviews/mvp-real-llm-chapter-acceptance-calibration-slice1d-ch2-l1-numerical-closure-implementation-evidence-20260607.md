# MVP Real LLM Chapter Acceptance Calibration Slice 1D Implementation Evidence

## 1. Scope

Accepted plan:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-plan-20260607.md`

Accepted plan reviews:

- `docs/reviews/plan-review-20260607-094336.md`
- `docs/reviews/plan-review-20260607-094515.md`

Controller judgment:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-controller-judgment-20260607.md`

## 2. Implementation Summary

Changed:

- `fund_agent/fund/chapter_writer.py`
  - Ch2 writer prompt now explicitly says numeric R/A/B/C/A-C closure assertions require nearby allowed anchor markers.
  - Ch2 writer prompt now explicitly says `### 结论要点` must not repeat unanchored concrete closure percentages.
  - Ch2 writer prompt now explicitly says `### 证据与出处` should use source labels or anchor-backed fact sentences, not unanchored formula percentages.
  - The Ch2 numeric-closure prompt paragraph is now gated to chapter 2 and omitted from non-Ch2 prompts.

- `fund_agent/services/chapter_orchestrator.py`
  - `programmatic:L1` repair correction now tells the writer to check `### 结论要点` and `### 证据与出处` for unanchored R/A/B/C/A-C percentage repetition.
  - Existing repair context shape, issue ids, sanitized messages and retry policy are unchanged.

- `tests/fund/test_chapter_writer.py`
  - Expanded Ch2 prompt test to assert summary/evidence-section L1 guidance.
  - Added non-Ch2 prompt regression proving the Ch2 numeric-closure paragraph does not leak into other chapters.

- `tests/services/test_chapter_orchestrator.py`
  - Expanded L1 repair-context tests to assert summary/evidence-section correction guidance.

- `tests/fund/test_chapter_auditor.py`
  - Added Ch2-style source-section L1 fail-closed regression for unanchored percentages plus `R=A+B-C`.
  - Added anchored counterpart proving nearby anchor marker still satisfies the existing L1 rule.

- `fund_agent/fund/README.md`
  - Documented current Ch2 numeric-closure writer prompt behavior.

## 3. Boundary Confirmation

- No live LLM command was run.
- No provider/default/runtime/budget/config behavior changed.
- No `_audit_numerical_closure()` relaxation occurred.
- No repair budget or retry policy changed.
- No extractor/projection schema changed.
- No template JSON changed.
- No quality gate, score-loop, golden/readiness, Host runtime, Agent runtime, PR, push or release state changed.

## 4. Validation

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Result:

```text
167 passed in 1.10s
```

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Result:

```text
47 passed in 0.47s
```

```bash
uv run ruff check fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

Result:

```text
All checks passed!
```

```bash
git diff --check -- fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py fund_agent/fund/README.md tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

Result: passed.

```bash
rg -n '[[:blank:]]$' fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py fund_agent/fund/README.md tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-plan-20260607.md docs/reviews/plan-review-20260607-094336.md docs/reviews/plan-review-20260607-094515.md docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1d-ch2-l1-numerical-closure-controller-judgment-20260607.md
```

Result: no matches.

## 5. Residuals

- Ch2 live acceptance remains unproven.
- Ch2 retained required-output marker C2 live proof remains unproven, although Slice 1A covers typed marker protocol locally.
- Ch2 `delete_if_not_applicable` marker-obligation residual remains open.
- Ch4 `audit_parse` remains open.
- Ch3/Ch5 LLM blocking residuals remain open.
- Any surviving Ch6 pressure-test `must_not_cover` C2 residual remains open.
