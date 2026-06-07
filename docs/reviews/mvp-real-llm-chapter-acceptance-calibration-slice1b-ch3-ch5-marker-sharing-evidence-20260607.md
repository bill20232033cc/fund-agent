# MVP Real LLM Chapter Acceptance Calibration Slice 1B Evidence

## 1. Scope

- Gate: `Real LLM chapter acceptance calibration gate`
- Slice: `1B - Ch3/Ch5 marker-sharing no-live evidence`
- Classification: `heavy`
- Plan: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1b-ch3-ch5-marker-sharing-plan-20260607.md`
- Plan reviews: `docs/reviews/plan-review-20260607-080548.md`; `docs/reviews/plan-review-20260607-080624.md`
- Controller judgment: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1b-ch3-ch5-marker-sharing-controller-judgment-20260607.md`

This slice did not run live LLM, did not change production code, did not change tests, and did not change provider/default/runtime/budget/config.

## 2. Retained Artifact Input

- Artifact root: `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/`
- Chapter files:
  - `chapters/chapter-03.json`
  - `chapters/chapter-05.json`

The artifact is the same post-config live smoke evidence baseline accepted for current chapter-calibration routing.

## 3. Evidence Command

```bash
python - <<'PY'
import json
from pathlib import Path

root = Path('reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters')
for chapter_id in (3, 5):
    data = json.loads((root / f'chapter-{chapter_id:02d}.json').read_text())
    programmatic_issues = []
    llm_issues = []
    for attempt in data.get('attempts', []):
        programmatic_issues.extend(attempt.get('programmatic_issues', []))
        llm_issues.extend(attempt.get('llm_issues', []))
    marker_issues = [
        issue for issue in programmatic_issues
        if issue.get('rule_code') == 'C2'
        and issue.get('message', '').startswith('缺少 required output item marker：')
    ]
    blocking_llm_issues = [
        issue for issue in llm_issues
        if issue.get('severity') == 'blocking'
    ]
    print(
        chapter_id,
        data.get('failure_category'),
        data.get('failure_subcategory'),
        'marker_issues=',
        len(marker_issues),
        'llm_blocking_issues=',
        len(blocking_llm_issues),
    )
PY
```

Result:

```text
3 prompt_contract code_bug_other marker_issues= 12 llm_blocking_issues= 6
5 prompt_contract code_bug_other marker_issues= 8 llm_blocking_issues= 1
```

## 4. Interpretation

Ch3:

- The retained `code_bug_other` includes required-output marker C2.
- This marker-protocol sub-residual shares the same root fixed by Slice 1A.
- Ch3 also has 6 LLM blocking issues in the retained artifact.
- Therefore Ch3 full chapter residual is not closed by Slice 1B.

Ch5:

- The retained `code_bug_other` includes required-output marker C2.
- This marker-protocol sub-residual shares the same root fixed by Slice 1A.
- Ch5 also has 1 LLM blocking issue in the retained artifact.
- Therefore Ch5 full chapter residual is not closed by Slice 1B.

## 5. Deterministic Validation

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Result:

```text
121 passed in 1.01s
```

## 6. Boundary Check

- No live LLM command was run.
- No production code was changed.
- No test source was changed.
- No provider/default/runtime/budget/config behavior was changed.
- No template JSON was changed.
- Ch2 `l1_numerical_closure`, Ch4 `audit_parse`, and Ch6 `unknown_anchor` were not touched.
- Score-loop, golden/readiness, Agent runtime, Host runtime, PR, push and release state were not touched.

## 7. Verdict

`SLICE_1B_EVIDENCE_ACCEPTED_NO_CODE_CHANGE`

Ch3 and Ch5 required-output marker sub-residuals are locally covered by the generic Slice 1A auditor fix.

Ch3 and Ch5 remain not live-accepted because retained artifact evidence still contains LLM blocking residuals. Those residuals require a separate reviewed slice if the controller chooses to route them before Ch6/Ch2/Ch4.
