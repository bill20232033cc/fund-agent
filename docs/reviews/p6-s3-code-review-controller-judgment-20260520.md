# P6-S3 Code Review Controller Judgment - 2026-05-20

## Verdict

P6-S3 implementation is accepted after fix and targeted re-review.

下一 gate：`P6-S3 acceptance / next slice planning`，后续候选为 `P6-S4 ITEM_RULE manifest plan/review`。

## Scope

Accepted implementation:

- Shared chapter block module:
  - `fund_agent/fund/template/chapter_blocks.py`
  - moved `RenderedChapterBlock`, `get_template_chapter_heading(...)`, `split_rendered_chapter_blocks(...)`, and splitter helpers out of renderer
- Deterministic contract audit:
  - `fund_agent/fund/audit/contract_rules.py`
  - `ProgrammaticAuditInput.chapter_blocks`
  - `C2` deterministic `CHAPTER_CONTRACT` conformance
  - per-chapter P3 minimum evidence line check
  - fallback splitting from `report_markdown`
- Renderer alignment:
  - renderer passes `chapter_blocks` into audit input
  - renderer adds only accepted required-item labels/placeholders
- Docs/tests:
  - `docs/design.md`
  - `fund_agent/fund/README.md`
  - `tests/README.md`
  - audit/template/P3 integration tests

## Review Inputs

- Implementation artifact: `docs/reviews/p6-s3-implementation-20260520.md`
- MiMo review: `docs/reviews/code-review-p6-s3-mimo-20260520.md`
- GLM review: `docs/reviews/code-review-p6-s3-glm-20260520.md`
- GLM targeted re-review: `docs/reviews/code-review-p6-s3-glm-rereview-20260520.md`
- Accepted plan: `docs/reviews/p6-s3-programmatic-contract-audit-plan-20260520.md`
- Plan rereview: `docs/reviews/p6-s3-plan-rereview-controller-20260520.md`

## Reviewer Findings

MiMo verdict: PASS.

MiMo residual risks were accepted:

- test-only private helper import from `tests.fund.template.test_renderer._render_input`
- forbidden marker rules intentionally do not cover every `must_not_cover` item because semantic constraints remain v2
- rule validation re-runs on each audit call; acceptable for MVP volume

GLM initial verdict: two findings.

| Finding | Severity | Controller decision | Resolution |
|---|---|---|---|
| C2 chapter block metadata path lacked direct test coverage | 中 | accepted | Added `test_run_programmatic_audit_detects_malformed_explicit_chapter_blocks` covering malformed explicit block heading and incomplete block sequence |
| Renderer chapter 0 labels used `next_minimum_verification` as a proxy for current variable / biggest risk | 低 | accepted | Changed both labels to explicit `数据不足` wording so unavailable values are not inferred |

GLM targeted re-review verdict: PASS. Both findings closed, no new findings.

## Controller Checks

- `audit_programmatic.py` does not import `renderer.py`.
- `contract_rules.py` required item rules match manifest required items with no missing or extra rule.
- Forbidden content rules are an explicit deterministic subset and match manifest `must_not_cover` entries when present.
- `ProgrammaticAuditInput.chapter_blocks` is explicit and typed; no `extra_payload` was introduced.
- C2 only checks deterministic markers and chapter block metadata; it does not claim semantic LLM audit.
- P3 only checks evidence line presence and appendix leakage; it does not claim evidence-to-claim support.
- Renderer labels stay within the accepted marker matrix and use explicit `数据不足` for unavailable current-variable / biggest-risk values.
- `docs/design.md` now separates deterministic C2 subset from semantic C2 v2.
- No Service/Engine/UI/CLI behavior expansion was introduced; P3 CLI integration only updates checked-rule expectations.
- No fund document filesystem, PDF, cache, or repository access was added.

## Verification

Controller-rerun verification:

```bash
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_contracts.py tests/fund/template/test_renderer.py -q
```

Result: `45 passed`

```bash
.venv/bin/python -m pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/integration/test_p3_cli_e2e_matrix.py -q
```

Result: `23 passed`

```bash
.venv/bin/python -m pytest tests/ -q
```

Result: `228 passed`

```bash
.venv/bin/python -m ruff check .
```

Result: `All checks passed!`

```bash
git diff --check
```

Result: passed with no output.

## Residual Risks

- C2 required item markers prove labels/placeholders exist, not answer quality. This remains LLM audit / Evidence Confirm v2.
- P3 per-chapter evidence line presence proves format only, not evidence support. E1/E2/E3 remain v2.
- Source template typo `危级/降级阈值` remains intentionally preserved and tracked as RR-19.
- Rule validation is not cached. Current volume is acceptable; revisit if batch audit performance becomes material.

## Decision

Accepted. P6-S3 can be committed.
