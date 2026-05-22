# P16-S2 Code Review AgentMiMo（2026-05-22）

## Verdict

`PASS`

Implementation artifact `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md` correctly applied stop condition and produced a valid blocker. No golden, source, test, or documentation files were modified.

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md` | Implementation artifact under review |
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-plan-20260522.md` | Accepted plan |
| `docs/reviews/p16-s2-plan-review-controller-judgment-20260522.md` | Controller judgment |
| `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` | Accepted P16-S1 evidence |
| `docs/reviews/p16-s1-code-review-controller-judgment-20260522.md` | Accepted P16-S1 evidence judgment |
| `AGENTS.md` | Agent execution rules |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |

Excluded inputs: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Review Focus Findings

### F1: Stop Condition Validity — PASS

**Question**: Is the blocker `BLOCKED_BEFORE_GOLDEN_EDIT_EXTRACTOR_TEXT_DIFF` valid under accepted stop conditions?

**Evidence**: The plan's stop condition (section "Stop Conditions") states:

> Future implementation must stop before golden edits if any of these occur: current extractor output differs from P16-S1 accepted values for any candidate

The implementation artifact ran `FundDocumentRepository.load_annual_report()` + `extract_profile()` for all five candidates and compared `benchmark_text` to P16-S1 accepted values. Two funds showed TEXT_DIFF:

| fund_code | current extractor `benchmark_text` | embedded `\n` location |
|---|---|---|
| `017644` | `中证1000指数收益率×95%+同期银行活期存款利\n率(税后)×5%` | between `利` and `率` |
| `019918` | `中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）\n*5%` | between `）` and `*` |

I independently verified both values by running `extract_profile()` through the production repository path. The `repr()` output confirms embedded `\n` characters are present in the extractor's `benchmark_text` field for both funds.

**Verdict**: Stop condition correctly triggered. The text diffs are real, not artifact measurement error.

### F2: Evidence Boundary — PASS

**Question**: Did the evidence check stay through `FundDocumentRepository` / `extract_profile` boundary?

**Evidence**: The stop-condition script uses only:

- `FundDocumentRepository()` — production document repository
- `repo.load_annual_report(code, 2024, force_refresh=False)` — annual report loading
- `extract_profile(report).index_profile` — production extractor

No external adapters, PDF cache direct access, source CSV reads, or calculated values were used. The boundary matches AGENTS.md hard constraints and P16-S1 accepted evidence acquisition path.

**Verdict**: Evidence boundary correctly preserved.

### F3: Text Diffs Are Real And Material — PASS

**Question**: Are the text diffs real and material?

**Evidence**: The embedded line breaks are genuine newline characters (`\n`) in the extractor output string, confirmed by `repr()` and `chr(10) in bt` checks. Three funds (`004194`, `005313`, `019923`) have no embedded newlines and match P16-S1 expected values exactly.

The diffs are material because:

1. Production golden `benchmark_text` rows would contain embedded newlines that do not match the reviewed P16-S1 accepted text.
2. Correctness comparison (`_comparable_scalar()`) does string equality; embedded newlines would cause mismatch even if the semantic content is equivalent.
3. The plan explicitly requires "exact P16-S1 benchmark text punctuation/anchors."

**Verdict**: Text diffs are real and material. The blocker is not a false positive.

### F4: No Golden/Source/Test Changes — PASS

**Question**: Were no golden, source, or test files modified?

**Evidence**: The artifact explicitly states:

- `reports/golden-answers/golden-answer-prefill-reviewed.md` — not edited
- `reports/golden-answers/golden-answer.json` — not rebuilt
- No source code edits
- No test edits

I verified independently:

```bash
git diff -- reports/golden-answers/ tests/ fund_agent/
```

Result: exit code 0, no output. No tracked files were modified.

`git diff --check HEAD` passes with exit code 0.

The only new file is the implementation artifact itself (`docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md`), which is an untracked review artifact as expected.

**Verdict**: No golden, source, test, or documentation files were modified. Implementation correctly stopped before any production file edits.

### F5: Validation Adequacy — PASS

**Question**: Is the validation adequate?

**Evidence**: The artifact includes:

1. Conflict-marker check: `rg -n "^(<<<<<<<|=======|>>>>>>>)"` — exit 1, no matches
2. Trailing whitespace check: `rg -n "[ \t]+$"` — exit 1, no matches
3. `git diff --check HEAD` — exit 0, no output
4. `git status --short` — confirms only pre-existing untracked excluded files plus this artifact
5. `git diff -- reports/golden-answers/ tests/ fund_agent/` — exit 0, confirms no golden/source/test modifications

Per controller judgment requirement for "explicit whitespace/conflict-marker checks for all new or newly tracked artifacts," the artifact runs conflict-marker and trailing-whitespace checks on itself.

**Verdict**: Validation is adequate and meets controller judgment requirements.

### F6: Composite Benchmark Scalar Fields — PASS (positive confirmation)

**Question**: Are the other structured fields still consistent with P16-S1 evidence?

**Evidence**: All five funds still preserve:

- `benchmark_identity_status=composite`
- `benchmark_index_name=None`
- `benchmark_index_code=None`
- `methodology_availability=benchmark_only`
- `constituents_availability=benchmark_only`
- `source_tier=benchmark_context`

I verified these independently through the same production repository path. The TEXT_DIFF in `benchmark_text` does not affect other structured fields.

**Verdict**: Non-text structured fields remain consistent. The blocker is scoped correctly to `benchmark_text` only.

### F7: Residual Handling — PASS

**Question**: Are residuals correctly identified and assigned?

**Evidence**: The artifact identifies four residuals:

| Residual | Assessment |
|---|---|
| Decide whether extractor should preserve or normalize embedded line breaks | Correctly assigned to "next reviewed extractor/golden plan" — cannot silently normalize in golden gate |
| Production golden rows for five funds | Correctly deferred until text discrepancy resolved |
| Tuple/null golden semantics | Correctly deferred (out of P16-S2 scope per plan) |
| `tracking_error` production golden | Correctly deferred (P16-S1 blocked all five) |

**Verdict**: Residuals are correctly identified and appropriately owned.

## Findings Summary

| # | Focus | Severity | Verdict |
|---|---|---|---|
| F1 | Stop condition validity | — | PASS |
| F2 | Evidence boundary | — | PASS |
| F3 | Text diffs real and material | — | PASS |
| F4 | No golden/source/test changes | — | PASS |
| F5 | Validation adequacy | — | PASS |
| F6 | Composite benchmark scalar fields | — | PASS |
| F7 | Residual handling | — | PASS |

No findings require artifact revision or controller action.

## Next Gate Recommendation

The blocker is valid. The next gate must resolve the embedded-newline discrepancy before golden implementation can proceed. Two options:

1. **Extractor normalization**: If the embedded newlines are PDF table-cell line breaks that should be stripped, the extractor should normalize `benchmark_text` before goldening. This requires a reviewed extractor-improvement plan.
2. **Golden-text acceptance**: If the embedded newlines are considered part of the raw text and should be preserved, the P16-S1 expected values need revision to match the actual extractor output. This requires a reviewed evidence re-acceptance.

Neither option can be decided in this code review. A controller judgment or new plan-review gate is required to select the path forward.

## Validation

Commands run during this review:

```bash
.venv/bin/python -c "
import asyncio
from fund_agent.fund.documents import FundDocumentRepository
from fund_agent.fund.extractors import extract_profile

async def main():
    repo = FundDocumentRepository()
    for code in ['017644', '019918']:
        report = await repo.load_annual_report(code, 2024, force_refresh=False)
        profile = extract_profile(report).index_profile
        value = profile.value
        bt = value.benchmark_text
        print(f'{code}: repr={repr(bt)}')
        print(f'{code}: has_newline={chr(10) in bt}')

asyncio.run(main())
"
```

Result: confirmed embedded `\n` in both `017644` and `019918`.

```bash
.venv/bin/python -c "
import asyncio
from fund_agent.fund.documents import FundDocumentRepository
from fund_agent.fund.extractors import extract_profile

EXPECTED = {
    '004194': '中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%',
    '005313': '中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%',
    '017644': '中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%',
    '019918': '中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%',
    '019923': '中证2000指数收益率×95%＋人民币活期存款税后利率×5%',
}

async def main():
    repo = FundDocumentRepository()
    for code, expected in EXPECTED.items():
        report = await repo.load_annual_report(code, 2024, force_refresh=False)
        profile = extract_profile(report).index_profile
        value = profile.value
        bt = value.benchmark_text
        match = bt == expected
        has_nl = chr(10) in bt
        print(f'{code}: match={match} has_newline={has_nl} identity={value.benchmark_identity_status} idx_name={value.benchmark_index_name} source_tier={value.source_tier}')

asyncio.run(main())
"
```

Result: `004194` match=True, `005313` match=True, `017644` match=False, `019918` match=False, `019923` match=True. All five `benchmark_identity_status=composite`, `benchmark_index_name=None`, `source_tier=benchmark_context`.

```bash
git diff -- reports/golden-answers/ tests/ fund_agent/
```

Result: exit 0, no output. No golden/source/test modifications.

```bash
git diff --check HEAD
```

Result: exit 0, no output.

```bash
git status --short
```

Result: only pre-existing untracked excluded files plus the implementation artifact.
