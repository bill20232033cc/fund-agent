# Post-P15 Follow-up Planning / Next Phase Selection（2026-05-22）

## Verdict

`PROCEED_TO_P16-S1_ENHANCED_INDEX_PRODUCTION_GOLDEN_CANDIDATE_EVIDENCE_PLAN_REVIEW`

P15-S1A 已经通过 `FundDocumentRepository` / `FundDataExtractor` 边界证明：`001548` 2024 年报没有可支持 production
`tracking_error` golden rows 的 direct observed disclosure evidence。下一阶段不应继续硬推 `001548` golden，也不应把
calculated tracking error 或 external index adapter 当成默认下一步。

最短可验证下一步是：

```text
P16-S1 enhanced-index production golden candidate evidence plan-review
```

该 gate 只做 selected-fund candidate evaluation / evidence acquisition plan-review：先评估 selected CSV 中的指数增强候选
`004194`、`005313`、`017644`、`019918`、`019923` 是否存在可复核 production evidence，再决定是否开启后续 evidence
acquisition implementation。不得直接修改 production golden rows。

## Current Baseline

| Item | Baseline |
|---|---|
| Current gate | `post-P15 follow-up planning / next phase selection` |
| P15 accepted result | `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` for `001548` 2024 `tracking_error` |
| Golden status | production `tracking_error` golden rows for `001548` remain blocked |
| Existing enhanced-index coverage | `161725` is deterministic fixture coverage only, not selected-fund production golden evidence |
| Selected-fund enhanced-index candidates | `004194` 招商中证1000指数增强A, `005313` 万家中证1000指数增强A, `017644` 博道中证1000指数增强A, `019918` 招商中证2000指数增强A, `019923` 华泰柏瑞中证2000指数增强A |
| Relevant design truth | deterministic MVP, evidence-auditable quality gates, fund type before generic analysis, annual-report access through `FundDocumentRepository` |
| Hard non-goals | no Dayu Host/Engine/tool loop, no LLM audit, no Evidence Confirm execution, no calculated tracking-error phase by default |

## First-principles Criteria

下一阶段选择必须满足这些判断标准：

1. 直接服务当前设计目标：让 index / enhanced-index 的 P1 关键字段在真实 production selected funds 上可审计，而不是只靠 fixture。
2. 保持证据和 root cause 同源：年报证据、抽取结果、golden correctness 必须来自同一 `FundDocumentRepository` / Fund Capability 边界。
3. 最小化新增架构：优先验证已有 P13/P14 direct-disclosure、index_profile、tracking_error、quality denominator 路径，而不是引入新数据源或计算模型。
4. 尊重 P15 负结果：`001548` 已证明无 direct observed tracking_error disclosure，不能反复消耗同一候选。
5. 不把维护债伪装成产品推进：repo hygiene 有价值，但不能替代增强指数 production evidence 缺口。
6. 可 fail closed：如果候选没有 direct evidence，输出 blocker 和 residual，不靠 target/limit、manager narrative、benchmark-only 或计算值补 golden。

## Candidate Comparison

| Candidate | Product value | Boundary / evidence risk | Decision |
|---|---|---|---|
| enhanced-index production golden expansion | High. P14 已把 `tracking_error` / `index_profile` 纳入 `index_fund` / `enhanced_index` P1 分母，但 enhanced-index 目前只有 `161725` fixture。selected CSV 中有 5 个真实指数增强候选，最贴近真实 production quality gap。 | Medium. 需要逐一确认候选年报身份、基金类型、direct disclosure、anchors；但可完全保持在 Fund Capability / repository 边界内。 | **Select.** 下一 gate 先做 candidate evidence plan-review，不直接改 golden rows。 |
| source-metadata retry / `force_refresh` evidence retry for `001548` | Low-medium. 可补齐 `001548` parsed-cache `source_metadata=None` provenance gap。 | Low. 但 P15-S1A 已分类全部候选文本为 target/limit 或 narrative；刷新 source metadata 不会把目标阈值变成 observed disclosure。 | Defer. 仅当 controller 明确需要 provenance hygiene 时再做，不作为产品下一阶段。 |
| extractor early-return refinement | Medium. 可缩小 `_has_ambiguous_tracking_error_text` 对其他基金的潜在 broad early return。 | Medium. 需要新的 evidence-backed false-negative 案例；当前 `001548` 不是 false negative。 | Defer until a candidate evaluation proves a direct-looking disclosure is being suppressed. |
| repo hygiene / artifact retention / C-1 type-ignore / magic-number cleanup | Maintenance value. 可降低长期维护成本。 | Low-medium, but not product evidence. 这些项需要从代码重新验证，且不能读取或依赖 excluded repo-audit artifact。 | Defer. 可作为单独 repo-hygiene phase，不抢占 product evidence gate。 |
| broader index methodology / constituents extraction or calculated tracking error | High long-term. 可补 Chapter 1 方法论/成份股和 direct disclosure 缺失时的 tracking-error能力。 | High. 需要新 source contracts、外部数据或计算语义、provenance、failure taxonomy；不应从 P15 直接跳过去。 | Defer to dedicated design/source/calculation phase after production evidence candidates are evaluated. |

## Selected Next Gate

Proceed to:

```text
P16-S1 enhanced-index production golden candidate evidence plan-review
```

Recommended plan artifact:

```text
docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md
```

The plan must answer one narrow question:

```text
Do any selected-fund enhanced-index candidates have reviewed annual-report evidence that can support future production
golden rows for index_profile and/or tracking_error through the current P13/P14 extraction/comparable path?
```

Minimum candidate set:

| Fund code | Name | Source fact |
|---|---|---|
| `004194` | 招商中证1000指数增强A | `docs/code_20260519.csv` selected-fund candidate |
| `005313` | 万家中证1000指数增强A | `docs/code_20260519.csv` selected-fund candidate |
| `017644` | 博道中证1000指数增强A | `docs/code_20260519.csv`; also listed in research notes |
| `019918` | 招商中证2000指数增强A | `docs/code_20260519.csv` selected-fund candidate |
| `019923` | 华泰柏瑞中证2000指数增强A | `docs/code_20260519.csv`; also listed in research notes |

Plan-review success does not mean golden rows are ready. It means the next implementation is safe to run a bounded
evidence-acquisition pass over these candidates and produce a reviewed evidence artifact.

## Implementation Guardrails

P16-S1 plan-review must require:

- Use `FundDocumentRepository.load_annual_report()` or `FundDataExtractor.extract()` for any future annual-report access.
- Evaluate candidate identity first: fund code, report year, document kind, fund type, and selected-fund source row.
- Classify evidence separately for `index_profile` and `tracking_error`.
- Treat benchmark-only evidence as acceptable only for `index_profile` fields that are already supported by current extractor semantics.
- Require direct observed disclosure for `tracking_error`: observed value, period label, annualization support, `source_type="direct_disclosure"`, `calculation_method="disclosed"`, and complete annual-report anchor.
- Stop if evidence is target/limit text, manager narrative, standard deviation only, benchmark-only for tracking error, ambiguous, unparseable, or anchor-incomplete.
- If another enhanced-index candidate exposes a real direct disclosure that current extractor misses because of early-return behavior, route that as an evidence-backed extractor refinement inside a separate implementation slice before any golden edit.
- Keep `001548` out of production `tracking_error` golden implementation unless a future explicit retry produces new reviewed direct evidence.

P16-S1 plan-review must prohibit:

- direct edits to `reports/golden-answers/golden-answer-prefill-reviewed.md`, `reports/golden-answers/golden-answer.json`, or `docs/golden-answer-template.md`;
- source, test, README, design, control, selected CSV, RR-13, or source CSV edits in the plan gate;
- calculated tracking error, external index adapters, methodology extraction, constituents extraction, QDII subtype redesign, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, or tool loop;
- reading or citing `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`, or excluded audit inputs.

## File Ownership

P16-S1 plan-review ownership:

| Area | Files | Scope |
|---|---|---|
| plan artifact | `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` | candidate evaluation plan, evidence contract, stop conditions, future validation |

Future evidence-acquisition implementation ownership, only after plan-review acceptance:

| Area | Files | Scope |
|---|---|---|
| evidence artifact | `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` | per-candidate repository provenance, extraction decisions, accepted/rejected evidence |
| optional helper/tests | Fund Capability evidence helper or extractor tests only if stable code is introduced or a false-negative is proven | no Service/UI/Engine/renderer/source bypass |

Future golden implementation ownership, only after reviewed evidence is accepted:

| Area | Files | Scope |
|---|---|---|
| reviewed golden | `reports/golden-answers/golden-answer-prefill-reviewed.md` | add only accepted evidence-backed rows |
| strict JSON | `reports/golden-answers/golden-answer.json` | rebuild through existing golden path |
| golden/template tests | targeted golden, extraction score, snapshot, quality gate tests if rows or comparable behavior change | no architecture expansion |

## Review Plan

P16-S1 plan-review should be reviewed by two independent reviewers. Reviewers should reject the plan if it:

- treats `161725` fixture as production selected-fund evidence;
- opens direct golden edits before evidence acquisition;
- relies on indirect tracking-error evidence;
- skips any of the five selected-fund enhanced-index candidates without a documented reason;
- proposes calculated tracking error or external index sources as part of this gate;
- bypasses `FundDocumentRepository` or moves source logic into Service/UI/Engine/renderer/quality gate;
- leaves no stop condition for no-evidence candidates.

Controller judgment should classify each finding as accepted / rejected / deferred / needs-more-evidence and preserve residual owners in the control record if the gate proceeds.

## Validation Success Signals

This planning artifact success signal:

```bash
git diff --check HEAD
```

P16-S1 plan-review success signals:

- exact candidate list and evaluation order are defined;
- direct evidence contract for `tracking_error` and benchmark-context contract for `index_profile` are explicit;
- future implementation commands are bounded to `FundDocumentRepository` / `FundDataExtractor`;
- stop conditions preserve fail-closed behavior for target/limit, narrative, benchmark-only tracking-error, standard-deviation-only, ambiguous, unparseable, and anchor-incomplete evidence;
- file ownership separates evidence acquisition from later golden implementation;
- no source/test/golden/README/design/control edits are made in the plan gate.

Future evidence-acquisition implementation success signals:

- each candidate has a repository identity/provenance record or a classified source blocker;
- each candidate has structured extraction results for fund type, `index_profile`, and `tracking_error`;
- all tracking-error mentions are inventoried and classified;
- accepted `tracking_error` evidence, if any, includes value text, normalized value, period, annualized status, source type, calculation method, and anchor;
- no production golden rows are edited unless a separate golden gate is opened after review acceptance.

Future golden implementation success signals, only if evidence is accepted:

- production golden rows are added only for reviewed selected-fund evidence;
- strict JSON validates through existing golden build path;
- extraction score / quality gate correctness reflects matches and mismatches for the new rows;
- targeted golden, extraction snapshot/score, quality integration, relevant extractor, ruff, full pytest, and `git diff --check HEAD` pass.

## Residuals

| Residual | Owner / destination | Status |
|---|---|---|
| `001548` production `tracking_error` golden rows | future golden gate only if new direct evidence is accepted | blocked by P15-S1A |
| `001548` source metadata retry with `force_refresh=True` | future evidence retry if selected | deferred; provenance hygiene, not product evidence priority |
| extractor early-return scope | future extractor-improvement phase if a false negative is proven | deferred |
| enhanced-index production golden expansion | P16-S1 plan-review | selected next gate |
| methodology / constituents extraction | future source-contract phase | deferred |
| calculated tracking error / external index adapter | future data-source/calculation phase | deferred |
| repo hygiene / artifact retention / C-1 type-ignore / magic-number cleanup | future repo-hygiene phase | deferred; must be re-verified from code, not excluded audit input |
| RR-13 duplicate `016492` | User / App source | untouched |
| E1-E3 / Evidence Confirm | future audit architecture phase | deferred |

## Handoff Prompt

Suggested next prompt:

```text
Gate: P16-S1 enhanced-index production golden candidate evidence plan-review.

Use docs/reviews/post-p15-follow-up-planning-20260522.md as the accepted next-phase selection input.

Create docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md.
Do not modify source code, tests, golden files, README, docs/design.md, docs/implementation-control.md, source CSV, RR-13 data, commit, push, PR, or external state.

The plan must evaluate selected-fund enhanced-index candidates 004194, 005313, 017644, 019918, and 019923. It must define
how a future evidence-acquisition implementation will use only FundDocumentRepository / FundDataExtractor boundaries to
record annual-report identity, fund type, index_profile evidence, tracking_error direct-disclosure evidence, rejected
candidates, source blockers, file ownership, validation commands, and stop conditions.

Do not directly add production golden rows in this gate. If evidence is later accepted, open a separate golden
implementation gate. Do not introduce calculated tracking error, external index adapters, methodology/constituents
extraction, QDII subtype redesign, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, or tool loop.
```
