# MVP Real LLM Chapter Acceptance Calibration Slice 1E Plan

## 1. Goal

Fix the deterministic prompt-contract root of Ch4 `audit_parse` without live LLM, provider/runtime changes, parser relaxation, template JSON changes, or repair-budget changes.

## 2. Direct Evidence

Retained post-config live artifact:

- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-04.json`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-04-attempt-00-auditor-feedback.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-04-attempt-01-auditor-feedback.md`
- `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/chapters/chapter-04-attempt-01-repair.md`

Observed facts:

- Ch4 terminal failure is `failure_category=audit_parse`.
- Attempt 0 has four required-output marker C2 issues and no LLM issue.
- Attempt 1 has the same four required-output marker C2 issues plus one `llm:parse_failure`.
- Attempt 1 runtime diagnostics show `operation=auditor`, `finish_reason=stop`, `response_chars=208`, and `chapter_failure_category=audit_parse`.
- The retained auditor feedback intentionally redacts raw response content and records only parse-failure classification; raw provider output must not be stored in new evidence.
- Slice 1A already fixed the typed required-output marker protocol locally, so this slice must not reimplement Ch4 marker checking.
- Current parser already rejects empty/free-text/extra-separator/explanatory-prefix responses and must remain fail-closed.

## 3. Root Hypothesis

The Ch4 auditor returned a provider-complete response that did not match the strict line protocol. The parser did the right thing by blocking. The local gap is that the auditor prompt and parse-failure repair instruction can be made more explicit for real providers:

- if no semantic issue remains, output exactly one line: `PASS|chapter|no issues`;
- otherwise output only lines whose first field is exactly `BLOCKING`, `REVIEWABLE` or `INFO`;
- every non-pass line must have exactly three pipe-separated fields;
- do not output labels such as `审计结果：`, Markdown bullets, JSON, code fences, headings, summaries, natural-language prefaces or the placeholder word `SEVERITY`;
- do not include `|` inside the message field.

This is prompt/repair hardening, not parser relaxation.

## 4. Scope

Allowed production files:

- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/README.md`

Allowed tests:

- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`

Allowed evidence/control artifacts:

- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1e-ch4-audit-parse-plan-20260607.md`
- `docs/reviews/plan-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1e-ch4-audit-parse-controller-judgment-20260607.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1e-ch4-audit-parse-implementation-evidence-20260607.md`
- `docs/reviews/code-review-*.md`
- `docs/reviews/mvp-real-llm-chapter-acceptance-calibration-slice1e-ch4-audit-parse-implementation-controller-judgment-20260607.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## 5. Non-Goals

- Do not run live LLM.
- Do not change provider/default/runtime/budget/config.
- Do not relax `_parse_llm_audit_response()`.
- Do not store raw auditor response in diagnostics, reports or artifacts.
- Do not increase repair budget or change repair retry policy.
- Do not change extractor, projection schema, template JSON, quality gate, score-loop or golden/readiness state.
- Do not fix Ch3/Ch5 LLM blocking residuals.
- Do not fix Ch4 retained required-output marker C2 rows except by relying on Slice 1A's typed marker protocol fix.
- Do not claim Ch4 live acceptance or full report acceptance.

## 6. Implementation Decisions

1. Harden `ChapterAuditLLMRequest` prompt construction in `chapter_auditor.py`:
   - state that pass output must be exactly one non-empty line and no other text;
   - state that issue output may contain multiple lines, but each line must be exactly `BLOCKING|...`, `REVIEWABLE|...` or `INFO|...`;
   - explicitly forbid explanatory prefixes, headings, bullets, Markdown, JSON, code fences, summaries and the placeholder word `SEVERITY`;
   - explicitly forbid extra `|` inside location/message.

2. Harden `llm:parse_failure` repair correction in Service `chapter_orchestrator.py`:
   - tell the next repair/audit loop that auditor output must be exact raw line protocol;
   - keep the correction sanitized and do not include raw auditor response.

3. Keep `_parse_llm_audit_response()` unchanged:
   - free text, explanatory prefix, extra pipe separator and empty response remain blocked.

4. Keep runtime diagnostics safe:
   - no raw auditor response, prompt, draft, API key or Authorization header in artifacts.

## 7. Tests

Add or extend deterministic tests:

- `tests/fund/test_chapter_auditor.py`
  - Prompt test asserts exact one-line PASS instruction.
  - Prompt test asserts allowed severities are literal and `SEVERITY` placeholder is not offered as an output token.
  - Existing parse-failure tests still prove explanatory prefix and extra separator are blocked.

- `tests/services/test_chapter_orchestrator.py`
  - Parse-failure repair correction mentions exact raw line protocol and no explanatory prefix/Markdown/JSON.
  - Audit-parse diagnostic remains `audit_parse` and sanitized.

## 8. Validation Commands

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py -q
```

Expected: pass.

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
```

Expected: pass.

```bash
uv run ruff check fund_agent/fund/chapter_auditor.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py
```

Expected: pass.

```bash
git diff --check -- fund_agent/fund/chapter_auditor.py fund_agent/services/chapter_orchestrator.py fund_agent/fund/README.md tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/
```

Expected: pass.

## 9. Completion Criteria

Slice 1E can be accepted locally if:

- Auditor prompt gives stricter, unambiguous line protocol instructions.
- `llm:parse_failure` repair correction is more explicit and remains sanitized.
- Parser strictness is unchanged and tested.
- Focused tests and regression tests pass.
- No live LLM, provider/runtime/config, template JSON, quality gate, score-loop, golden/readiness or Agent runtime changes occur.

## 10. Residuals After Acceptance

- Ch4 live acceptance remains unproven until a separately authorized live evidence gate.
- Ch4 retained required-output marker C2 live proof remains unproven, although Slice 1A covers typed marker protocol locally.
- Ch3/Ch5 LLM blocking residuals remain separate routes.
- Ch2 `delete_if_not_applicable` marker-obligation residual may require a separate slice if deterministic evidence shows it survives.
- Any surviving Ch6 pressure-test C2 remains separate.
