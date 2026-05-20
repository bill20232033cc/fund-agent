# P6-S1 Plan Re-review - Controller - 2026-05-20

## Reviewed Target

- Patched plan: `docs/reviews/p6-s1-template-contract-manifest-plan-20260520.md`
- Prior review: `docs/reviews/p6-s1-plan-review-controller-20260520.md`

## Prior Findings

| Finding | Status | Evidence |
|---|---|---|
| P6-S1-PR1: 章节标题校验会诱导依赖 renderer 私有常量 | closed | Plan now says P6-S1 production code must not import renderer private constants such as `_CHAPTER_TITLES`; manifest carries its own chapter titles as the P6 machine-contract title source; tests validate against `docs/design.md` / template expectations rather than renderer internals. |

## Re-review Notes

The patch closes the coupling risk:

- `contracts.py` owns P6 machine-contract chapter titles.
- Renderer title alignment is explicitly deferred to P6-S2.
- P6-S1 tests are no longer required to couple production code to renderer private constants.
- The plan remains inside Capability and still excludes ITEM_RULE, contract audit, FQ5 upgrade, LLM audit, and thermometer valuation mapping.

## Residual Risks

- The manifest is curated manually from `docs/fund-analysis-template-draft.md`; drift remains possible until later contract audit / renderer alignment tests broaden coverage. This is acceptable for P6-S1 and tracked by P6-S2/P6-S3.

## Conclusion

PASS. P6-S1 plan is code-generation-ready.

Next gate: `P6-S1 implementation`.
