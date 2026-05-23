# P19-S4 Plan Review Controller Judgment - 2026-05-23

## Inputs

- Plan: `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md`
- MiMo review: `docs/reviews/p19-s4-plan-review-mimo-20260523.md`
- GLM review: `docs/reviews/p19-s4-plan-review-glm-20260523.md`
- Design truth: `docs/design.md` v2.2 §11.4 / §11.5
- Control truth: `docs/implementation-control.md` P19-S4

## Judgment

Verdict: ACCEPT PLAN AS SOURCE-GATE BLOCKER, NOT AS FINAL P19-S4 CLOSEOUT

The plan correctly prevents implementation against the current `akshare.stock_index_pe_lg` / `stock_index_pb_lg` interface family. It proves that the five P19-S4 target indexes are not present in the local akshare 1.18.60 Legulegu symbol map and that common target symbols return `KeyError`. It also correctly rejects semantically adjacent substitutes such as 创业板50、上证红利、深证红利 and 中证1000.

However, both reviewers found that the evidence is not sufficient to close P19-S4 as fully blocked/deferred. `docs/design.md` allows "akshare + 中证指数官方或 akshare 指数估值接口", not only the current Legulegu PE/PB pair. Therefore P19-S4 must move to a dedicated source feasibility gate before any code implementation or final deferral.

## Accepted Findings

### F1 - Current plan only closes the Legulegu PE/PB route

Accepted.

First-principles reason: the necessary fact for P19-S4 is exact target-index PE/PB history. The current plan proves one source family cannot provide it, but it does not prove all design-allowed sources cannot provide it.

Required next action:

- Create a P19-S4 source feasibility artifact.
- Probe design-allowed candidates, including at minimum:
  - `akshare.stock_zh_index_value_csindex`
  - other akshare index valuation interfaces discoverable in the installed package
  - 中证指数官方 accessible files/pages/APIs if reachable without introducing a new external runtime dependency
- For each target index `399006`, `000688`, `000922`, `000932`, `000933`, record exact identity, PE/PB availability, field semantics, date coverage, common-date count, failure mode, and license/use constraints where observable.

### F2 - Conditional implementation plan is only code-generation-ready for same-schema Legulegu sources

Accepted.

First-principles reason: if source feasibility is resolved through an official or non-Legulegu source, the implementation may need a new Capability data adapter and source-shaped fixtures. A mapping-only plan would risk forcing different semantics into the current `滚动市盈率中位数` / `市净率中位数` contract.

Required next action:

- The source feasibility artifact must produce a source contract before implementation:
  - exact API/URL/source name
  - identity proof for target index
  - PE field meaning
  - PB field meaning
  - date and numeric schema
  - missing/failure semantics
  - fixture sample shape
  - whether the existing `AkshareIndexThermometerSource` can be extended or a new Capability data adapter is required

## Controller Decisions

- Do not implement P19-S4 code from the current plan.
- Do not substitute non-target indexes.
- Do not broaden P19-S3 `ValuationStateResolution` automatic mapping.
- Do not use the public Youzhiyouxing page as production truth.
- Do not mark P19-S4 final blocked/deferred until the broader source feasibility gate has completed.

## Next Gate

P19-S4 source feasibility gate.

Expected artifact:

- `docs/reviews/p19-s4-source-feasibility-20260523.md`

Possible outcomes:

- `ACCEPT_SUBSET_IMPLEMENTATION`: one or more exact P19-S4 targets have PE/PB history with sufficient source contract; implementation scope must shrink to verified targets unless controller explicitly updates exit criteria.
- `BLOCKED_DEFERRED`: no target has usable exact PE/PB history from design-allowed sources; update control as P19-S4 deferred and keep P19-S5 all-A separate.
- `NEEDS_PLAN_PATCH`: source exists but requires new adapter semantics; create a patched implementation plan and re-review before coding.

