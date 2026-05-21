# P13-S1 Plan Review Controller Judgment（2026-05-22）

## Verdict

`ACCEPTED`

Controller 接受 `docs/reviews/p13-s1-tracking-error-index-data-plan-20260522.md` 作为 P13 tracking-error / index-data direct-disclosure implementation 的 code-generation-ready source-contract plan。

## Basis

- 设计真源仍要求确定性 MVP 主链路、Fund Capability ownership、`FundDocumentRepository` 年报入口、Dayu 非生产依赖。
- `next-phase selection` 已选择 P13-S1 tracking-error / index-data source contract plan-review。
- P13-S1 plan 明确把第一段实现收窄为年报直接披露路径；calculated index series、methodology、constituents 保持后续可选 scope。
- P13-S1 plan 修订后补齐了 `ExtractionMode` 语义、renderer 输入管道、risk-check resolved object 迁移、quality gate/FQ2 策略、非指数/QDII 行为、composite benchmark 行为和 ambiguity fixture。

## Review Disposition

| Review artifact | Verdict | Controller disposition |
|---|---|---|
| `docs/reviews/p13-s1-plan-review-mimo-20260522.md` | `pass-with-risks` | accepted; 5 个 finding 要求折入计划后复审 |
| `docs/reviews/p13-s1-plan-review-glm-20260522.md` | `PASS` with findings | accepted; 4 个 finding 和 3 个 open questions 要求折入计划 |
| `docs/reviews/p13-s1-plan-rereview-mimo-20260522.md` | `PASS` | accepted; MiMo 01-05、GLM F1-F4 全部 closed |
| `docs/reviews/p13-s1-plan-rereview-glm-20260522.md` | `PASS` | accepted; 9 个 finding 全部 closed，无新增 blocker |

## Accepted Implementation Scope

Next implementation gate may implement only the direct-disclosure slices from the accepted plan:

- explicit typed `index_profile` and `tracking_error` structured fields in Fund Capability;
- direct annual-report tracking-error extraction from `FundDocumentRepository`-provided parsed reports;
- pure index / enhanced index / non-index / QDII-not-applicable / ambiguity / composite / missing fixtures;
- risk-check migration to `ResolvedTrackingErrorForRisk` with no equal raw-scalar product authority;
- renderer replacement of tracking-error placeholder only through `input_data.structured_data.tracking_error`;
- deterministic audit guards against benchmark-anchor misuse;
- quality gate snapshot observability policy that does not change FQ2/comparable/golden denominator in the first implementation.

## Explicit Non-Goals

- Do not implement calculated tracking error from external index series.
- Do not implement index methodology or constituents extraction beyond benchmark-context tiering.
- Do not touch RR-13 data or `docs/repo-audit-20260521.md`.
- Do not introduce Dayu runtime, LLM writing, Evidence Confirm, E1/E2/E3 execution, or Service/UI direct source access.

## Next Gate

Proceed to:

```text
P13 tracking-error direct-disclosure implementation
```

Required implementation artifact:

```text
docs/reviews/p13-tracking-error-direct-disclosure-implementation-20260522.md
```
