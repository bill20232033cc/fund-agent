# MVP Real LLM Chapter Acceptance Calibration Slice 1B Plan

## 1. Goal

Determine whether Ch3 and Ch5 share the same typed required-output marker root cause fixed in Slice 1A, using deterministic no-live evidence only.

This slice is an evidence / routing slice, not an implementation slice.

## 2. Motivation

The post-config live smoke artifact records Ch3 and Ch5 as `prompt_contract/code_bug_other`.

Slice 1A fixed the typed path mismatch where writer/parser expected stable typed required-output item id markers while programmatic auditor still checked legacy text markers. Before opening new implementation work, the controller needs direct same-source evidence for whether Ch3 and Ch5 are already covered by that generic auditor fix or need separate calibration.

## 3. Scope

Allowed files:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1b-ch3-ch5-marker-sharing-plan-20260607.md`
- `docs/reviews/plan-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1b-ch3-ch5-marker-sharing-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1b-ch3-ch5-marker-sharing-evidence-20260607.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Read-only evidence inputs:

- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/summary.json`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-03.json`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-05.json`
- current code/tests from Slice 1A

## 4. Non-Goals

- Do not run live LLM.
- Do not change provider/default/runtime/budget/config.
- Do not modify production code or tests.
- Do not change `docs/fund-analysis-template-draft.md`.
- Do not fix Ch2 `l1_numerical_closure`.
- Do not fix Ch4 `audit_parse`.
- Do not fix Ch6 `unknown_anchor`.
- Do not touch score-loop, golden/readiness, Agent runtime, Host runtime, PR, push or release state.
- Do not claim a complete accepted report or Ch1/Ch3/Ch5 live acceptance.

## 5. Direct Evidence To Collect

E1 retained-artifact classification:

- Parse Ch3 and Ch5 chapter JSON from the retained post-config live artifact.
- Confirm each terminal failure is `failure_category=prompt_contract` and `failure_subcategory=code_bug_other`.
- Confirm each has programmatic C2 issues whose messages start with `缺少 required output item marker：`.
- Record issue counts, final attempt issue ids, LLM blocking issue counts and parse-failure signals.
- Distinguish marker-protocol evidence from full chapter-residual closure. A chapter can have marker C2 covered by Slice 1A while still retaining separate LLM semantic or parse residuals.

E2 typed-marker deterministic coverage:

- Run existing deterministic no-live tests that exercise typed item id marker acceptance:
  - `uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q`
- Confirm the current Slice 1A tests cover generic typed marker behavior, not only hard-coded Ch1 behavior:
  - typed missing marker still fail-closes;
  - legacy path still requires legacy marker;
  - Service typed path accepts typed item id markers.

E3 no-code-change boundary:

- Confirm no production/test source changes are required for this slice.
- Confirm any updates are docs/evidence/control only.

## 6. Completion Criteria

This slice can be accepted locally if all are true:

- Ch3 retained artifact `code_bug_other` is proven to be required-output marker C2, not a different programmatic C2 class.
- Ch5 retained artifact `code_bug_other` is proven to be required-output marker C2, not a different programmatic C2 class.
- Ch3 and Ch5 non-marker blocking evidence is explicitly enumerated rather than ignored.
- Existing Slice 1A deterministic tests pass and exercise the generic typed marker contract.
- No live LLM, provider/runtime/config, production code or tests were changed.

If Ch3 or Ch5 has additional non-marker blocking evidence, close only the marker-protocol sub-residual for that chapter and route the remaining blocker to a separate future slice. Do not claim full chapter residual closure for that chapter.

## 7. Expected Controller Decision

If completion criteria pass:

- Accept `SLICE_1B_EVIDENCE_ACCEPTED_NO_CODE_CHANGE`.
- Mark Ch3 and Ch5 marker-protocol sub-residual as locally covered by Slice 1A.
- Preserve any non-marker Ch3/Ch5 residuals found in the retained artifact as separate future routes.
- Keep live acceptance unproven until a separately authorized live evidence gate.
- Set next slice selection to one of:
  - Ch6 `unknown_anchor`;
  - Ch2 `l1_numerical_closure`;
  - Ch4 `audit_parse`.

If completion criteria fail:

- Record the exact unmatched issue evidence.
- Open a separate reviewed plan for the failing chapter root cause.

## 8. Validation Commands

```bash
python - <<'PY'
import json
from pathlib import Path

root = Path("reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters")
for chapter_id in (3, 5):
    data = json.loads((root / f"chapter-{chapter_id:02d}.json").read_text())
    programmatic_issues = []
    llm_issues = []
    for attempt in data.get("attempts", []):
        programmatic_issues.extend(attempt.get("programmatic_issues", []))
        llm_issues.extend(attempt.get("llm_issues", []))
    marker_issues = [
        issue for issue in programmatic_issues
        if issue.get("rule_code") == "C2"
        and issue.get("message", "").startswith("缺少 required output item marker：")
    ]
    blocking_llm_issues = [
        issue for issue in llm_issues
        if issue.get("severity") == "blocking"
    ]
    print(
        chapter_id,
        data.get("failure_category"),
        data.get("failure_subcategory"),
        "marker_issues=",
        len(marker_issues),
        "llm_blocking_issues=",
        len(blocking_llm_issues),
    )
PY
```

Expected: Ch3 and Ch5 both show `prompt_contract code_bug_other` with positive marker issue counts. Any `llm_blocking_issues` count greater than zero must be recorded as a separate residual and must not be closed by this slice.

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Expected: pass.

```bash
git diff --check -- docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1b-ch3-ch5-marker-sharing-plan-20260607.md docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1b-ch3-ch5-marker-sharing-evidence-20260607.md docs/current-startup-packet.md docs/implementation-control.md
```

Expected: pass after evidence/control updates.

## 9. Stop Conditions

- Any evidence command requires live provider access.
- Ch3 or Ch5 terminal artifact contains non-marker blocking evidence that prevents shared-root routing.
- Deterministic tests fail.
- Evidence requires changing production code or tests.
- Workspace scope becomes unsafe because unrelated dirty files must be modified.
