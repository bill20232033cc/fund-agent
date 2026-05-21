# P14-S1 Code Review Controller Judgment（2026-05-22）

## Verdict

`ACCEPTED`

Controller 接受 P14-S1 `index_profile` / `tracking_error` quality-denominator implementation。实现符合
`docs/design.md` 中 quality gate 保护主链路、防止低质量输入静默消费的设计目标，也保持 Fund Capability
对字段抽取、correctness、质量分母和 golden answer 的归属边界。

## Inputs

- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Accepted plan: `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-plan-20260522.md`
- Plan controller judgment: `docs/reviews/p14-s1-plan-review-controller-judgment-20260522.md`
- Implementation artifact: `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md`
- MiMo code review: `docs/reviews/p14-s1-code-review-mimo-20260522.md`
- GLM code review: `docs/reviews/p14-s1-code-review-glm-20260522.md`
- MiMo targeted re-review: `docs/reviews/p14-s1-code-rereview-mimo-20260522.md`
- GLM targeted re-review: `docs/reviews/p14-s1-code-rereview-glm-20260522.md`

## Review Results

| Reviewer | Initial verdict | Re-review verdict | Controller decision |
|---|---|---|---|
| AgentMiMo | `PASS` | `PASS` | accepted |
| AgentGLM | `PASS_WITH_FINDINGS` | `PASS` | accepted after fix |

No blocking findings remain.

## Accepted Behavior

- `ExtractionMode` remains `Literal["direct", "derived", "estimated", "missing"]`; non-applicability is not encoded as a new extraction mode.
- `index_profile` and `tracking_error` are conditional P1 quality fields only for `index_fund` and `enhanced_index`.
- Non-index fund types are excluded from these two fields' FQ2 coverage, traceability, single-fund score, and fund-quality missing-field denominators.
- Missing, unknown, or conflicting fund type remains conservative: index-quality fields stay scorable instead of being silently excluded.
- Snapshot comparable values now include stable scalar sub-fields for `index_profile` and `tracking_error`; bool values serialize as `True` / `False`.
- Golden prefill supports dataclass-valued `ExtractedField` objects through a Fund Capability internal value-mapping helper.
- Production golden answer adds only reviewed-evidence-backed `001548` `index_profile` rows; no production `tracking_error` golden rows were added.
- `161725` deterministic enhanced-index fixture covers classification, `index_profile`, and `tracking_error`.
- The implementation does not introduce calculated tracking error, external index series adapters, methodology or constituents extraction, QDII subtype redesign, E1-E3, Evidence Confirm, Dayu runtime, Host, Engine, tool loop, RR-13 source edits, or `docs/repo-audit-20260521.md` changes.

## Finding Decisions

| Finding | Source | Decision | Rationale |
|---|---|---|---|
| `_build_fund_score_row` used row-level type fallback and could disagree with fund-quality filtering under conflicting `classified_fund_type` | GLM F-1 | accepted and fixed | Based on the quality-denominator design goal, fund score and fund quality must derive applicability from the same fund-level fact. The fix now resolves fund-level type first and keeps conflict cases conservative in both paths. |
| Duplicate `_value_mapping` helpers in snapshot and golden prefill | GLM F-2 / MiMo 001 | accepted and fixed | AGENTS.md requires repeated logic to be extracted. The shared helper is inside `fund_agent/fund`, preserving Capability ownership without cross-layer dependency. |
| `001548` production golden confidence promoted from medium to high | MiMo 002 / GLM O-1 | accepted as evidence-backed implementation decision | The plan allowed promotion after exact reviewed evidence verification. The resulting rows use page-level benchmark evidence and do not add unverified `tracking_error` production golden rows. |

## Validation

Implementation agent reported after fix pass:

```text
.venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_extraction_snapshot.py tests/fund/test_golden_prefill.py -q
33 passed

.venv/bin/python -m ruff check fund_agent tests
All checks passed!

.venv/bin/python -m pytest -q
428 passed

git diff --check HEAD
<no output>
```

Re-review evidence additionally records targeted `tests/fund/` coverage at `53 passed`.

## Residual Tracking

- `tracking_error` production golden correctness remains future scope until a reviewed direct tracking-error value is verified.
- Enhanced-index production golden coverage remains future scope; current `161725` coverage is deterministic fixture coverage.
- Methodology and constituents extraction remain future source-contract scope.
- `docs/repo-audit-20260521.md` remains excluded and untracked.

These residuals are accepted because P14-S1's design goal is quality-denominator coverage for P13 structured fields, not new source extraction or calculated time-series capability.

## Next Step

Controller should run local acceptance validation, update `docs/implementation-control.md`, create the accepted P14-S1 implementation commit, then proceed to P14-S1 aggregate readiness / aggregate deepreview according to phaseflow.
