# Design Alignment Review（2026-05-22）

## Verdict

`PARTIAL_ACCEPT_WITH_CORRECTIONS`

`docs/design-control-alignment-guide.md` 是有价值的设计对齐输入，但不能作为真源直接覆盖 `docs/design.md` / `docs/implementation-control.md`。从第一性原理看，当前要解决的问题不是“冻结所有开发并重命名历史 phase”，而是把真实代码事实、设计非目标、控制文档 gate 三者重新对齐，避免后续 phase 在未检查设计边界的情况下扩张。

本次接受最小一致性修复：

- 澄清温度计非目标：禁止的是自建温度计计算和自动投资判断映射，不是只读查询有知有行公开数据。
- 在 `docs/design.md` 中补充当前 CLI 命令清单，明确 `checklist` 仍是占位命令。
- 后续 plan review 必须显式做 design-boundary check。

本次拒绝：

- 不回滚 `ThermometerService` / `fund-analysis thermometer`。当前代码、README、Fund README、tests 和 control history 都证明它是只读查询能力，不是自建温度计计算。
- 不把 P13-P16 追溯改名或合并为 P18。历史 gate artifact、PR、commit、review 证据必须保持稳定；可以在未来建立能力域摘要，但不能重写 phase 身份。
- 不设置 `tracking_error coverage >= 90%` 作为当前 exit criteria。P15/P16 已证明生产直接披露证据稀缺；无证据时追求覆盖率会激励错误接受。

## Inputs

| Input | Role |
|---|---|
| `docs/design-control-alignment-guide.md` | Scoped user-provided alignment plan input |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |
| Current code facts under `fund_agent/services/`, `fund_agent/ui/cli.py`, `fund_agent/fund/data/thermometer.py` | Implementation evidence |
| README / tests references | User-facing and validation evidence |

Excluded local drafts remain excluded unless separately scoped: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`.

## Finding Decisions

| Guide claim | Decision | First-principles rationale |
|---|---|---|
| P1: `ThermometerService` violates design non-goal | **Corrected, not accepted as violation** | `docs/design.md` already records `ThermometerService`, `data/thermometer.py`, and CLI structure. The real ambiguity is wording: “不做温度计自建” should mean no self-calculated thermometer and no automatic valuation mapping. Read-only public data query is already an accepted code fact. |
| P2: P13-P16 are too granular and should become P18 | **Rejected for history rewrite; defer as optional capability summary** | Phase identity is evidence bookkeeping. Rewriting merged P13-P16 into P18 would break artifact traceability. Future control docs may add a capability-domain summary without changing historical gate names. |
| P3: Exit criteria are not verifiable | **Partially accepted** | Some historical criteria are artifact/process oriented, but current quality gates already expose coverage/traceability/correctness. Future plan reviews should require verifiable success signals and reject coverage targets that conflict with evidence availability. |
| P4: Plan review lacks design check | **Accepted** | This is a real process improvement. Controller and reviewers should explicitly check design non-goals, layer boundaries, source-access constraints, and whether design updates are required. |
| P5: design.md not updated | **Partially accepted** | Current `docs/design.md` is not as stale as the guide claims; thermometer and P13/P14/P15 facts are present. Still, thermometer non-goal wording and CLI command inventory need clearer current-state wording. |

## Accepted Design Updates

Update `docs/design.md` to v2.1 with a narrow scope:

1. Change non-goal wording from “不做温度计自建” to “不做温度计自建计算”.
2. State that thermometer data is read-only public-page query plus cache, not automatic `valuation_state` mapping.
3. Add current CLI command list under §9 before the project structure.

These changes do not alter runtime behavior and do not authorize new product scope.

## Rejected P18 Rewrite

The guide’s P18 proposal bundles P13-P16 under a new “指数基金核心指标数据质量” phase and proposes `tracking_error` coverage / traceability targets. This is not accepted for the current gate.

Reasons:

- P13-P16 are already merged / accepted with durable artifacts, PRs, reviews and residual owners.
- P15/P16 directly established that production `tracking_error` golden rows remain blocked without direct observed disclosure evidence.
- A `tracking_error coverage >= 90%` target would be unsafe unless the eligible universe is restricted to funds with direct observed disclosure; otherwise it creates pressure to accept target / narrative / benchmark-only evidence.
- P17-S1 already selects the safer next step: harden fail-closed extractor semantics.

## Process Rule For Next Gates

For P17-S1 and later plan reviews, reviewers must include a design-boundary section that checks:

- Whether the plan violates `docs/design.md` §1.3 non-goals.
- Whether annual-report access remains through `FundDocumentRepository` / `FundDataExtractor`.
- Whether Service/UI/Engine boundaries are preserved.
- Whether the plan introduces external Dayu runtime, LLM writing, Evidence Confirm, calculated tracking error, external index adapters, or hidden explicit parameters in `extra_payload`.
- Whether success signals are verifiable without incentivizing unsupported evidence acceptance.

## Control Handling

This review does not supersede the current control gate. `docs/implementation-control.md` currently points to `P17-S1 tracking_error extractor ambiguity boundary plan-review`; that remains correct. The design alignment work is a controller reconciliation slice before P17-S1 implementation, not a replacement for P17-S1.
