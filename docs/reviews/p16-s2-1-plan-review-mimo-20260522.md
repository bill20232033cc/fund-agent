# P16-S2.1 Plan Review AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

Plan `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md` is architecturally correct and safe to accept. Two findings are non-blocking and do not require plan revision; they are implementation-phase clarifications.

## Inputs

| Artifact | Role |
|---|---|
| `docs/reviews/p16-s2-1-benchmark-text-newline-normalization-decision-plan-20260522.md` | Plan under review |
| `docs/reviews/p16-s2-index-profile-benchmark-context-golden-implementation-20260522.md` | P16-S2 blocker artifact |
| `docs/reviews/p16-s2-code-review-controller-judgment-20260522.md` | Controller judgment accepting blocker |
| `AGENTS.md` | Agent execution rules |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |

Excluded inputs: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Review Focus Findings

### F1: First-principles Choice — PASS

**Question**: Is narrow benchmark_text normalization the correct first-principles choice over preserving raw newline expected values?

**Evidence**: I verified the four code paths that consume `benchmark_text`:

1. **Golden Markdown** (`golden_answer.py:parse_golden_answer_markdown`): uses `splitlines()` — each line is parsed as a separate table row. An embedded `\n` in `expected_value` would split the row and break parsing entirely. This is a hard constraint, not a preference.

2. **Golden prefill** (`golden_answer.py:_escape_markdown_cell`): does `value.replace("\\\\|", "|").strip()` — no newline handling. A raw newline would survive into Markdown and hit the `splitlines()` wall.

3. **Comparable extraction** (`extraction_snapshot.py:_comparable_scalar`): does `str(value).strip()` only — no internal whitespace normalization. Embedded newlines would survive into comparable values, causing correctness comparison fragility.

4. **Extractor** (`profile.py:_benchmark_text`): does `str(value).strip()` only — preserves embedded newlines from table cell parsing.

The plan's reasoning is correct: golden Markdown is structurally single-line, and the existing infrastructure cannot safely represent multiline `expected_value`. Normalizing at the source (extractor) rather than at each consumption point is the right architectural choice. The alternative (preserving raw newlines) would require redesigning golden Markdown/JSON schema first, which is out of scope and unjustified for a PDF layout artifact.

**Verdict**: First-principles reasoning is sound.

### F2: Correct Ownership In Profile Extractor Only — PASS

**Question**: Is the normalization correctly scoped to the profile extractor benchmark path only?

**Evidence**: The plan states:

> Add a private helper in `profile.py`... used only by the benchmark field path.

And:

> do not normalize all fields globally; do not normalize methodology, constituents, manager narrative, tracking error, or arbitrary raw section text.

Code fact verification confirms: `_build_benchmark()` constructs `benchmark_text` from `matched_field.value` with no normalization. The plan correctly identifies this as the single normalization insertion point. The normalization applies to both `benchmark.value["benchmark_text"]` and the anchor note derived from the same matched row, keeping them同源.

The rejection criteria include "normalizes all profile fields or all parsed table cells instead of the benchmark path only," which guards against scope creep.

**Verdict**: Ownership is correctly scoped.

### F3: Risk Of Over-normalization — PASS_WITH_FINDINGS (F-1)

**Question**: Is there a risk of over-normalization?

**Evidence**: The normalization rule states:

> remove newline runs when they are PDF visual wraps inside CJK text or adjacent to benchmark arithmetic punctuation, percent signs, parentheses, or full-width equivalents; replace newline runs with one ASCII space only when removing them would merge two ASCII word tokens

I verified this rule against both affected cases:

| Input | Newline context | Correct action |
|---|---|---|
| `017644`: `...存款利\n率(税后)×5%` | between CJK `利` and CJK `率` | remove (CJK-CJK boundary) |
| `019918`: `...（税后）\n*5%` | between full-width `）` and ASCII `*` | remove (punctuation boundary) |

And all three unaffected cases have no embedded newlines, so normalization is a no-op.

The rule is safe for these cases. However, the "replace with space when merging ASCII word tokens" clause is hypothetical — neither affected case involves ASCII word token boundaries. A simple "always remove newlines adjacent to CJK or punctuation" rule would suffice and be easier to implement correctly.

**Finding F-1** (info): The "replace with ASCII space" clause adds implementation complexity for a case not present in current evidence. Implementation should consider whether a simpler "always remove embedded newlines" rule is sufficient, since `benchmark_text` values are CJK-heavy formula expressions where embedded newlines are always PDF artifacts. This does not block plan acceptance.

**Severity**: info. **Disposition**: Implementation clarification, not plan revision.

### F4: Tests For Affected/Unaffected Funds — PASS

**Question**: Does the plan require adequate tests for both affected and unaffected funds?

**Evidence**: The plan requires:

- `017644`-shape: `...存款利\n率(税后)×5%` → normalized to canonical
- `019918`-shape: `...（税后）\n*5%` → normalized to canonical
- `004194` no-op: exact match preserved
- `005313` no-op: exact match preserved
- `019923` no-op: exact match preserved
- Composite semantics preserved for all five

Code fact verification: existing tests in `tests/fund/extractors/test_profile.py` use clean single-line benchmark values and have NO coverage for embedded newlines. The plan correctly identifies this gap and requires dedicated deterministic tests.

**Verdict**: Test coverage is adequate.

### F5: Preservation Of Anchors And Composite Semantics — PASS_WITH_FINDINGS (F-2)

**Question**: Are anchors and composite semantics preserved?

**Evidence**: The plan requires:

- `benchmark_identity_status` remains `composite`
- `benchmark_index_name` remains `None`
- `benchmark_component_text` behavior unchanged except consuming normalized text
- anchor `section_id`, `page_number`, `table_id`, `row_locator` remain from original row

The implementation instruction states: "Normalize embedded newlines only in the benchmark_text path before benchmark/index_profile values and anchor notes are built."

**Finding F-2** (info): The plan should clarify that the anchor `note` field (which contains the benchmark text in human-readable form) is also normalized, not just `benchmark_text`. The plan says "anchor notes are built" after normalization, which implies this, but an explicit statement would prevent implementation ambiguity. This does not block plan acceptance.

**Severity**: info. **Disposition**: Implementation clarification, not plan revision.

### F6: Future Golden Resume Path — PASS

**Question**: Is the future golden implementation resume path clear?

**Evidence**: The plan's "Realignment" section specifies:

1. Canonical expected values are the no-newline strings from P16-S2 plan
2. Historical artifacts are not rewritten
3. P16-S2.1 implementation artifact must verify all five match
4. Resume P16-S2 with same 25 scalar rows
5. Rebuild strict JSON through golden-build
6. Verify pre-existing records unchanged

This is a clear, linear path from normalization to golden implementation.

**Verdict**: Resume path is clear and correct.

### F7: Stop Conditions — PASS

**Question**: Are stop conditions adequate?

**Evidence**: The plan has two stop-condition categories:

1. **Before source edits**: code fact divergence, non-reproducible newline, parser/repository/schema changes needed
2. **Before golden edits**: normalized output still differs, identity/anchor changes, composite semantics changed, golden-build churn, no_comparable_fields, null/tuple golden assertions required

These cover the key risks. The "normalized extractor output still differs" condition is particularly important — it ensures the normalization actually resolves the blocker before proceeding to golden edits.

**Verdict**: Stop conditions are adequate.

### F8: Boundary Violations — PASS

**Question**: Does the plan violate any module boundaries or evidence rules?

**Evidence**: The plan:

- Restricts normalization to `fund_agent/fund/extractors/profile.py` (Capability layer)
- Prohibits direct PDF/cache/source helper access
- Prohibits Service/UI/Engine/renderer/quality gate boundary changes
- Prohibits edits to design/control/CSV/RR-13
- Requires `FundDocumentRepository` / `FundDataExtractor` for production verification
- Does not introduce Dayu runtime, external adapters, or LLM audit

This aligns with AGENTS.md module boundaries and evidence rules.

**Verdict**: No boundary violations.

## Findings Summary

| # | Focus | Severity | Verdict | Disposition |
|---|---|---|---|---|
| F1 | First-principles choice | — | PASS | Accepted |
| F2 | Ownership scope | — | PASS | Accepted |
| F3 | Over-normalization risk | info | PASS_WITH_FINDINGS | Implementation: consider simpler "always remove" rule |
| F4 | Test coverage | — | PASS | Accepted |
| F5 | Anchor/composite preservation | info | PASS_WITH_FINDINGS | Implementation: clarify anchor note normalization |
| F6 | Golden resume path | — | PASS | Accepted |
| F7 | Stop conditions | — | PASS | Accepted |
| F8 | Boundary violations | — | PASS | Accepted |

Both findings are info-severity and do not require plan revision. They are implementation-phase clarifications that the implementer should address.

## Recommendation

Accept the plan without revision. The two info findings should be recorded as implementation-phase guidance in the controller judgment.

## Validation

Commands run during this review:

```bash
git diff --check HEAD
```

Result: exit code `0`, no output.

No files were modified during this review.
