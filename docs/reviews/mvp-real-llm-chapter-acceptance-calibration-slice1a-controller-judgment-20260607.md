# MVP Real LLM Chapter Acceptance Calibration Slice 1A Controller Judgment

## 1. Decision

`SLICE_1A_ACCEPTED_LOCALLY`

The implementation for `Ch1 Typed Required-Output Marker Protocol Alignment` is accepted as a local deterministic fix.

This does not accept `Real LLM smoke re-baseline gate`, does not accept a final LLM report, and does not authorize another live LLM command.

## 2. Evidence Chain

- Plan: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-gate-plan-20260607.md`
- Initial plan review: `docs/reviews/plan-review-20260607-072727.md`
- Re-review: `docs/reviews/plan-review-20260607-072818.md`
- Plan controller judgment: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-gate-plan-controller-judgment-20260607.md`
- Implementation evidence: `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-implementation-evidence-20260607.md`
- Code review: `docs/reviews/code-review-20260607-073445.md`

## 3. Accepted Local Facts

- Production `--use-llm` typed path supplies `typed_required_output_items` to `ChapterWriterInput`.
- Writer prompt/parser requires stable typed item id markers when typed required-output items are present.
- Programmatic auditor now checks the same stable typed item id markers when `writer_input.typed_required_output_items` is present.
- Legacy path still checks legacy `chapter.contract.required_output_items` marker text.
- Bare required-output text still cannot substitute for exact marker syntax.
- Missing typed marker still fail-closes with C2.
- The accepted implementation did not implement `delete_if_not_applicable` marker-obligation filtering.

## 4. Validation Accepted

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Accepted result: `121 passed in 1.02s`

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Accepted result: `47 passed in 0.46s`

```bash
uv run ruff check fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

Accepted result: `All checks passed!`

```bash
git diff --check -- fund_agent/fund/chapter_auditor.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py fund_agent/fund/README.md docs/reviews/mvp-real-llm-chapter-acceptance-calibration-gate-plan-20260607.md docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1a-implementation-evidence-20260607.md
```

Accepted result: passed.

## 5. Boundary Judgment

- No live LLM rerun was executed in Slice 1A.
- No provider/default/runtime/budget/config behavior changed.
- No template JSON changed.
- No Ch2 L1, Ch4 audit parse, Ch6 unknown anchor, score-loop, golden/readiness, Agent runtime, Host runtime, PR, push or release state changed.
- `fund_agent/fund/README.md` was updated because Fund code behavior changed.

## 6. Residual Routing

- Ch1 marker-protocol mismatch is accepted as fixed locally, but Ch1 live acceptance is not proven. Remaining Ch1 live risks include duplicate anchor ids, LLM semantic audit, conclusion extraction and final assembly behavior.
- Ch2 `prompt_contract/l1_numerical_closure` remains a separate numerical-closure calibration gate.
- Ch4 `audit_parse` remains a separate auditor line-protocol gate.
- Ch6 `prompt_contract/unknown_anchor` remains a separate anchor projection / group-anchor conversion gate.
- Ch3 and Ch5 `code_bug_other` should be revisited with same-source deterministic evidence to determine whether this Slice 1A fix also removes their marker-protocol blocker.
- `delete_if_not_applicable` marker-obligation sharing remains deferred until a future contract gate has direct evidence requiring it.

## 7. Next Controller Entry

The active gate remains `Real LLM chapter acceptance calibration gate`.

Recommended next entry is a new reviewed slice selection using the retained post-config live artifact and the accepted Slice 1A local facts. The controller should decide whether to:

1. run a deterministic no-live evidence check for Ch3/Ch5 marker-protocol sharing, or
2. open the separately routed Ch6 `unknown_anchor`, Ch2 `l1_numerical_closure`, or Ch4 `audit_parse` slice.

Do not run another live LLM command, retry, endpoint probe, fallback, provider/default/runtime/budget change, score-loop, golden/readiness, Agent runtime, PR, push or release before a new plan/review/controller judgment authorizes it.
