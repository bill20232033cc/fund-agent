# P16-S1 Enhanced-index Production Golden Candidate Evidence Plan（2026-05-22）

## Verdict

`PLAN_READY_FOR_REVIEW`

本 gate 只产出计划，不获取新年报证据、不修改实现、不修改测试、不修改 golden、不修改 README、不修改
`docs/design.md` / `docs/implementation-control.md`、不修改 `docs/code_20260519.csv`、不触碰 RR-13、commit、branch、PR 或外部状态。

下一步仍然不是 golden implementation。P16-S1 只回答：

```text
未来 evidence-acquisition implementation 是否可以在 selected-fund enhanced-index 候选中，按当前 P13/P14
index_profile / tracking_error 抽取与 comparable 路径，找到可复核的 production golden 候选证据？
```

## Current Truth Inputs

本计划只使用以下输入：

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/post-p15-follow-up-planning-20260522.md`
- `docs/reviews/post-p15-follow-up-plan-review-controller-judgment-20260522.md`
- `docs/reviews/post-p15-follow-up-plan-review-mimo-20260522.md`
- `docs/reviews/post-p15-follow-up-plan-review-glm-20260522.md`
- `docs/reviews/p15-s1a-code-review-controller-judgment-20260522.md`
- `docs/code_20260519.csv`

明确排除且不得读取、引用或作为事实来源：

- `docs/design0522.md`
- `docs/implementation-control0522.md`
- `docs/repo-audit-20260521.md`
- 其它 excluded audit inputs

## Baseline Facts

| Fact | Current state |
|---|---|
| Current gate | `P16-S1 enhanced-index production golden candidate evidence plan-review` |
| P15 accepted result | `001548` 2024 `tracking_error` = `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` |
| `001548` status | production `tracking_error` remains blocked; no golden rows may be added from target/limit text or manager narrative |
| `161725` status | deterministic fixture coverage only; not selected-fund production golden evidence |
| P14 field status | `index_profile` and `tracking_error` are conditional P1 fields for `index_fund` / `enhanced_index` |
| Annual-report boundary | future access only through `FundDocumentRepository.load_annual_report()` and/or `FundDataExtractor.extract()` |
| Golden sequencing | plan-review -> evidence acquisition artifact -> reviewed acceptance -> separate golden implementation gate |

## Scope And Non-goals

### In Scope

- Define selected-fund enhanced-index candidate order and stop budget.
- Define the per-candidate identity record required before evidence classification.
- Define separate evidence contracts for `index_profile` and `tracking_error`.
- Define per-candidate source blocker handling using the accepted source failure taxonomy.
- Define file ownership, future implementation handoff, validation success signals, reviewer rejection criteria, and residuals.

### Out Of Scope

- No source code, test, golden, README, design/control, selected CSV, RR-13, commit, branch, PR, issue, or external-state edits.
- No implementation evidence acquisition in this gate.
- No production golden edits in this gate.
- No calculated tracking error.
- No external index adapters.
- No index methodology extraction.
- No constituents extraction.
- No QDII subtype redesign.
- No E1-E3 or Evidence Confirm execution.
- No LLM writing.
- No Dayu runtime, Host, Engine, or tool loop.

## Candidate Identity Set

Future evidence acquisition must record candidate identity first, before reading field evidence or classifying field sufficiency.
The fixed report scope is `report_year=2024`, `report_kind=annual_report`. Do not expand to other years or report kinds inside
P16-S1 without a new plan-review.

| Eval order | Fund code | Fund name | Expected fund type | Report year | Report kind | Selected-fund source row |
|---:|---|---|---|---:|---|---|
| 1 | `004194` | 招商中证1000指数增强A | `enhanced_index` | 2024 | `annual_report` | `docs/code_20260519.csv:38` |
| 2 | `005313` | 万家中证1000指数增强A | `enhanced_index` | 2024 | `annual_report` | `docs/code_20260519.csv:39` |
| 3 | `017644` | 博道中证1000指数增强A | `enhanced_index` | 2024 | `annual_report` | `docs/code_20260519.csv:40` |
| 4 | `019918` | 招商中证2000指数增强A | `enhanced_index` | 2024 | `annual_report` | `docs/code_20260519.csv:41` |
| 5 | `019923` | 华泰柏瑞中证2000指数增强A | `enhanced_index` | 2024 | `annual_report` | `docs/code_20260519.csv:42` |

## Candidate Ordering Rationale

第一性原理排序规则：

1. 只使用 selected CSV 已审计行，不引入规模、成立日、外部研究 notes 或其它未列入本 gate 的事实。
2. 保持 CSV 中 enhanced-index 候选的稳定行序，避免 implementation agent 用不可审计的偏好重排候选。
3. 先覆盖同一指数族的连续候选，再覆盖下一指数族：`004194`、`005313`、`017644` 都是中证1000指数增强；`019918`、`019923` 都是中证2000指数增强。这样能在不新增外部事实的前提下减少证据形态变量。
4. 同一管理人出现两次时不提前跳跃处理；`004194` 与 `019918` 分属不同指数族，仍按 CSV 稳定行序执行，避免把管理人相似性误当证据充分性。

## Stop Budget

| Budget item | Rule |
|---|---|
| Candidate budget | Exactly 5 candidates: `004194`, `005313`, `017644`, `019918`, `019923`; do not add candidates. |
| Report budget | Exactly one report identity per candidate: 2024 annual report. |
| Access budget | Only `FundDocumentRepository.load_annual_report()` and/or `FundDataExtractor.extract()`. |
| Source fallback budget | Only repository-owned fallback triggered by `not_found` or `unavailable`; no manual PDF/cache/source helper access. |
| Evidence budget | Classify `index_profile` and `tracking_error` separately for every candidate that passes source identity checks. |
| Stop success | Stop after all 5 candidates have either accepted field evidence or classified blockers; do not continue searching extra funds/years. |
| Stop blocked | If all 5 candidates lack acceptable evidence, produce `BLOCKED_NO_ACCEPTED_SELECTED_ENHANCED_INDEX_EVIDENCE`; do not open golden implementation. |
| Stop fail-closed | Any candidate with `schema_drift`, `identity_mismatch`, `integrity_error`, incomplete anchor, or contract/integrity breach is blocked for this gate and may not be rescued by fallback or golden edits. |

## Required Per-candidate Record

Future evidence acquisition must produce one record per candidate before field-level conclusions:

| Field | Required content |
|---|---|
| `fund_code` | Candidate code from selected CSV |
| `selected_source_row` | Exact CSV row path and line number |
| `requested_report_year` | `2024` |
| `requested_report_kind` | `annual_report` |
| `document_key` | Repository identity, including fund code, year, and kind |
| `document_identity_status` | `matched` or a fail-closed blocker |
| `classified_fund_type` | Must be `enhanced_index` for golden-candidate eligibility |
| `fund_type_source` | Structured extraction / annual-report identity source, not CSV name alone |
| `source_metadata` | Repository source provenance, including fallback status when available |
| `source_blocker` | One of the taxonomy categories if annual-report access or identity fails |

CSV name and category are candidate-selection facts only. They are not enough to accept fund type, report identity, or golden evidence.

## Annual-report Access Contract

Future implementation may use only:

- `FundDocumentRepository.load_annual_report(fund_code, 2024, document_kind="annual_report")`
- `FundDataExtractor.extract(fund_code, 2024)`

Forbidden access paths:

- Direct filesystem reads of production PDFs, parsed caches, or downloaded files.
- Direct calls to concrete source adapters, PDF cache helpers, downloader helpers, or Eastmoney/EID internals outside the repository.
- Service/UI/Engine/renderer/quality gate source orchestration.
- Manual web search or external index data to fill missing annual-report evidence.

## Source Blocker Handling

Per-candidate source handling must use the accepted five-category taxonomy.

| Failure category | Meaning | Fallback allowed? | P16-S1 handling |
|---|---|---:|---|
| `not_found` | Source responds normally but has no target fund/year annual report | Yes | Allow repository-owned fallback; if exhausted, record blocker. |
| `unavailable` | Network, timeout, service, or local dependency temporarily unavailable | Yes | Allow repository-owned fallback; preserve unavailable provenance if exhausted. |
| `schema_drift` | Source response shape, field, or attachment contract drifted | No | Fail closed; no fallback, no golden evidence. |
| `identity_mismatch` | Candidate conflicts with fund code, fund identity, year, or report kind | No | Fail closed; no fallback, no golden evidence. |
| `integrity_error` | PDF content type, file header, parsed content, or write integrity failed | No | Fail closed; no fallback, no golden evidence. |

Fallback success must preserve `metadata.fallback_used=True` when the repository exposes that metadata. Fallback blocked must preserve source, category, message, and original cause where available. Eligible failures exhausted must keep final exception semantics; do not collapse `unavailable` into `not_found`.

## Evidence Contract: `index_profile`

`index_profile` and `tracking_error` must be evaluated independently. Accepting `index_profile` evidence never implies accepting
`tracking_error` evidence.

The current truth inputs establish that `index_profile` is extracted from annual-report §1/§2 profile/benchmark context and that
P16-S1 must enumerate the benchmark-context subfields acceptable under current extractor semantics. Therefore P16-S1 accepts only
these benchmark-context subfields:

| Acceptable subfield | Acceptable evidence under current semantics | Required anchor/provenance | Not accepted |
|---|---|---|---|
| `index_profile.index_name` | A named target or benchmark index directly disclosed in annual-report §1/§2 benchmark/profile context, such as the index named by the product benchmark context. | Complete annual-report anchor; `source_kind=annual_report`; report year; section id; row/table/page locator when available; provenance must indicate benchmark/profile context, not external lookup. | Product name alone, CSV name alone, external index website, inferred index family, methodology text without a named index. |
| `index_profile.benchmark_context` | The annual-report benchmark/profile text that current extractor semantics use as benchmark context for the index profile. | Complete annual-report anchor to the benchmark/profile disclosure; repository source metadata; extraction mode must be direct or current extractor equivalent for benchmark context. | Manager narrative, marketing text, unanchored summary, future calculated benchmark mapping. |
| `index_profile.source_tier` / provenance marker | `benchmark_context` as provenance for why the index profile came from benchmark/profile disclosure. This is metadata, not a standalone golden value. | Must be tied to the same complete annual-report anchor as the accepted value field. | A provenance marker without anchored value text. |

Explicitly out of current `index_profile` benchmark-context scope:

- index methodology;
- constituent list;
- constituent weights;
- index provider details unless they are part of the accepted anchored current extractor value;
- rebalance frequency;
- index code;
- external adapter output;
- calculated or inferred index classification.

If a candidate has only broader index methodology or constituent information, record it as future methodology/constituents residual,
not as accepted P16-S1 `index_profile` golden evidence.

## Evidence Contract: `tracking_error`

`tracking_error` requires direct observed disclosure. The future implementation must reject anything less than a direct observed
annual-report value.

An accepted `tracking_error` row must include all of:

| Required field | Requirement |
|---|---|
| `observed_value` | A disclosed observed tracking-error value, not a target, cap, limit, threshold, or promise. |
| `period_label` | The period the disclosed value covers, e.g. a reporting period or annualized period label from the annual report. |
| `annualization_support` | Explicit annualized wording or enough disclosed wording to prove the value is annualized under the current direct-disclosure contract. |
| `source_type` | Must equal `direct_disclosure`. |
| `calculation_method` | Must equal `disclosed`. |
| `value_parse_status` | Must be parseable into the current structured value representation. |
| `anchor` | Complete annual-report anchor: report year, section id, and table/row/page/note locator where available. |
| `provenance` | Repository source metadata and document identity. |

Fail closed for:

- target/limit/control text, including daily tracking-deviation targets or annualized control limits;
- manager narrative;
- benchmark-only `tracking_error`;
- standard-deviation-only disclosure;
- ambiguous or unparseable values;
- incomplete anchors;
- `schema_drift`;
- `identity_mismatch`;
- `integrity_error`;
- any value sourced from calculation, external index series, external adapter, or post-hoc inference.

If current extraction returns `missing` or an ambiguity note, the evidence artifact may still inventory raw mentions through the same
repository-loaded annual report, but it may not convert raw mentions into accepted evidence unless every direct-disclosure requirement
above is satisfied.

## Evidence Classification Matrix

Each candidate-field conclusion must be one of:

| Classification | Meaning | Golden implication |
|---|---|---|
| `accepted_index_profile_candidate` | `index_profile` benchmark-context evidence satisfies the contract | Eligible for later golden gate only |
| `accepted_tracking_error_candidate` | `tracking_error` direct observed disclosure satisfies the contract | Eligible for later golden gate only |
| `blocked_no_direct_tracking_error` | Mentions exist but are target/limit/narrative/standard-deviation/benchmark-only/ambiguous/unparseable | No golden rows |
| `blocked_no_index_profile_contract_evidence` | No accepted benchmark-context index_profile field | No golden rows |
| `blocked_source_not_found` | Source not found after allowed fallback | No golden rows |
| `blocked_source_unavailable` | Source unavailable after allowed fallback | No golden rows |
| `blocked_schema_drift` | Source contract drift | Fail closed |
| `blocked_identity_mismatch` | Report identity mismatch | Fail closed |
| `blocked_integrity_error` | Integrity failure | Fail closed |
| `defer_extractor_false_negative` | Anchored direct-looking evidence exists but current extractor misses it | Separate extractor refinement slice before any golden edit |

## Future Evidence-acquisition Handoff

Only after this plan-review is accepted, a future implementation agent may create an evidence artifact. Suggested artifact path:

```text
docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md
```

Required implementation sequence:

1. Load selected candidate table from `docs/code_20260519.csv` only to confirm the five row identities above.
2. For each candidate in order, call `FundDocumentRepository.load_annual_report()` and/or `FundDataExtractor.extract()`.
3. Record repository document identity and source metadata before any field evidence conclusion.
4. Confirm `classified_fund_type == "enhanced_index"` from structured extraction / annual-report identity.
5. Classify `index_profile` using the benchmark-context contract.
6. Classify `tracking_error` using the direct observed disclosure contract.
7. Inventory rejected `tracking_error` mentions only if they are obtained from the repository-loaded annual report.
8. Stop after all five candidates are classified.
9. Produce an evidence artifact with accepted candidates, rejected candidates, blockers, residuals, and no golden edits.

If a candidate exposes anchored direct-looking `tracking_error` disclosure that current extractor suppresses because of broad early-return
behavior, the evidence artifact must route it to `defer_extractor_false_negative`. That is a separate extractor-improvement slice before
any golden edit.

## Future Golden Implementation Handoff

A future golden implementation gate may open only if a reviewed evidence artifact accepts at least one selected-fund candidate.
That later gate, not P16-S1, may own:

- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- targeted golden / extraction score / snapshot / quality gate tests
- documentation updates required by actual changed behavior

Golden rows must be added only from accepted selected-fund evidence. `001548` production `tracking_error` remains blocked unless a
future explicit retry produces new reviewed direct observed evidence. `161725` remains fixture-only and may not be used as production
selected-fund golden support.

## File Ownership

| Stage | Files | Ownership |
|---|---|---|
| P16-S1 plan-review | `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-plan-20260522.md` | This gate only |
| Future evidence acquisition | `docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` | Evidence artifact only unless a reviewed false-negative justifies a separate extractor slice |
| Future extractor refinement | Fund Capability extractor files and targeted extractor tests only | Separate plan/review required before code changes |
| Future golden implementation | Golden answer files and targeted score/snapshot/quality tests | Separate golden gate after accepted evidence |

Service/UI/Engine/renderer/quality gate must not own annual-report source access or source fallback behavior.

## Validation Success Signals

### This Plan Gate

- Only the P16-S1 plan artifact is created.
- No source/test/golden/README/design/control/CSV/RR-13/external-state changes are made.
- `git diff --check HEAD` passes.

### Future Evidence Acquisition

- All five candidates have identity records before field classification.
- Each candidate records report year, report kind, document identity, fund type, selected source row, and source metadata or blocker.
- `index_profile` and `tracking_error` conclusions are separate.
- Every accepted `index_profile` value is tied to benchmark/profile context and complete annual-report anchor.
- Every accepted `tracking_error` value has observed value, period label, annualization support, `source_type="direct_disclosure"`,
  `calculation_method="disclosed"`, parseable value, and complete anchor.
- All source blockers use the five-category taxonomy.
- No golden rows are edited.

### Future Golden Gate

- Opens only after reviewed evidence acceptance.
- Adds production golden rows only for accepted selected-fund evidence.
- Rebuilds strict JSON through the existing golden path.
- Runs targeted golden, extraction snapshot/score, quality gate, relevant extractor tests, ruff, full pytest, and `git diff --check HEAD`.

## Reviewer Rejection Criteria

Reviewers should reject this plan or a future implementation handoff if it:

- treats `161725` as production selected-fund evidence;
- treats `001548` `tracking_error` as unblocked without new reviewed direct observed disclosure;
- skips any of the five candidates without a source blocker;
- changes candidate order without a first-principles reason grounded in allowed inputs;
- edits golden rows during plan-review or evidence acquisition;
- uses target/limit text, manager narrative, benchmark-only tracking error, standard-deviation-only text, ambiguous text, unparseable values,
  or incomplete anchors as accepted `tracking_error` evidence;
- accepts `index_profile` fields outside current benchmark-context semantics;
- bypasses `FundDocumentRepository` / `FundDataExtractor`;
- allows fallback after `schema_drift`, `identity_mismatch`, or `integrity_error`;
- introduces calculated tracking error, external index adapters, methodology/constituents extraction, QDII subtype redesign, E1-E3,
  Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, or tool loop.

## Residuals

| Residual | Destination | Status |
|---|---|---|
| `001548` production `tracking_error` golden rows | Future golden gate only if new direct observed evidence is accepted | Blocked by P15-S1A |
| `161725` enhanced-index tracking-error coverage | Test fixture only | Not production selected-fund evidence |
| Enhanced-index production golden expansion | P16-S1 future evidence acquisition after plan-review | Planned, not executed |
| Source metadata retry for `001548` with `force_refresh=True` | Future evidence retry if selected | Deferred |
| Extractor early-return scope | Future extractor-improvement phase if a selected candidate proves false negative | Deferred |
| Index methodology / constituents extraction | Future source-contract phase | Out of scope |
| Calculated tracking error / external index adapters | Future calculation/data-source phase | Out of scope |
| E1-E3 / Evidence Confirm | Future audit architecture phase | Out of scope |
| RR-13 duplicate `016492` | User / App source | Untouched |

## Final Plan Conclusion

`P16-S1_PLAN_REVIEW_READY`

The next safe action is independent plan review of this artifact. Evidence acquisition and golden implementation remain separate future
gates.
