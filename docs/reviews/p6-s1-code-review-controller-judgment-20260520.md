# P6-S1 Code Review Controller Judgment - 2026-05-20

## Scope

- Work unit: `P6-S1 template contract manifest implementation`
- Design truth: `docs/design.md`
- Control doc: `docs/implementation-control.md`
- Plan: `docs/reviews/p6-s1-template-contract-manifest-plan-20260520.md`
- Implementation owner: AgentCodex
- Reviewers:
  - AgentGLM: `docs/reviews/code-review-20260520-125906.md`
  - AgentMiMo: `docs/reviews/code-review-20260520-130008.md`

Reviewed files:

- `fund_agent/fund/template/contracts.py`
- `fund_agent/fund/template/__init__.py`
- `tests/fund/template/test_contracts.py`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Controller Verdict

Accepted after targeted test fix.

P6-S1 now provides a Capability-layer typed `CHAPTER_CONTRACT` manifest for template chapters `0..7`, exports public accessors, and validates the manifest fail-closed. The implementation stays within P6-S1 scope: it does not parse Markdown comments at runtime, does not depend on renderer private `_CHAPTER_TITLES`, does not change renderer output, and does not implement `ITEM_RULE`, contract audit, or FQ5 upgrade.

## Finding Decisions

| Finding | Source | Controller decision | Rationale |
|---|---|---|---|
| lens key / `fund_type` mismatch branch lacked explicit test coverage | AgentGLM + AgentMiMo | ✅ accepted and fixed | The production validator already failed closed, but the plan explicitly required mismatch coverage. A targeted test was added in `tests/fund/template/test_contracts.py`. |
| Chapter 7 `required_output_items` contains `危级/降级阈值` | AgentMiMo | 🟡 deferred | The typo is present in the source template at `docs/fund-analysis-template-draft.md`; P6-S1's current objective is faithful machine transcription. Changing only the manifest would make code diverge from the template source. Track as template-source cleanup for a later design/template edit. |
| `evidence_requirements` in template chapter 2 is not modeled | AgentGLM residual risk | 🟡 deferred | P6-S1 public contract only includes `narrative_mode`, `must_answer`, `must_not_cover`, `required_output_items`, and `preferred_lens`. Evidence requirement modeling belongs to a later contract/audit slice. |
| invalid `chapter_id` / unsupported runtime `fund_type` defensive branches lack independent tests | AgentGLM residual risk | 🟢 accepted residual | Current P6-S1 tests cover the required fail-closed manifest drift scenarios. These branches are defensive API checks and can be expanded when P6-S2/P6-S3 add downstream consumers. |

## Verification

Commands run after review fix:

```bash
.venv/bin/python -m pytest tests/fund/template/test_contracts.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

Results:

- `tests/fund/template/test_contracts.py`: `7 passed`
- full suite: `213 passed`
- ruff: passed
- diff check: passed

## Residual Risk

- Template source typo `危级/降级阈值` remains in both source template and manifest by design. Owner: future template-source cleanup / P6 follow-up, not P6-S1 implementation.
- `evidence_requirements` is not yet represented in `ChapterContract`. Owner: later P6 contract audit / evidence requirement slice if needed.

## Next Gate

`P6-S1 acceptance / control-doc update`.
