# Post-P16 Follow-up Planning（2026-05-22）

## Verdict

`PROCEED_TO_P17-S1_TRACKING_ERROR_EXTRACTOR_AMBIGUITY_BOUNDARY_PLAN_REVIEW`

P16 已经完成增强指数 `index_profile` benchmark-context production golden rows：5 只 selected enhanced-index 候选的 25 条标量 golden rows 已随 PR 10 合入 `main`。P15/P16 同时证明：`001548` 与 5 只增强指数候选均没有可支持 production `tracking_error` golden rows 的 direct observed disclosure evidence。

Post-P16 的根问题不是继续寻找可以“凑”进 golden 的 `tracking_error` 文本，而是让现有 direct-disclosure 抽取边界更稳定：当年报存在目标/限制/叙述/歧义文本时，Capability 应该给出一致、可审计、fail-closed 的 `tracking_error` 缺失状态，避免 broad early-return 或 note 口径漂移影响后续 evidence acquisition / quality denominator 判断。

推荐下一阶段：

```text
P17-S1 tracking_error extractor ambiguity boundary and note consistency
```

该阶段是 Fund Capability 内部的窄口径 extractor hardening。它不添加 production `tracking_error` golden rows，不引入计算型 tracking error，不引入外部指数数据源，不修改设计/总控真源，也不触碰 RR-13。

## Current Gate And Inputs

| Item | State |
|---|---|
| Current gate | `post-P16 follow-up planning` |
| Current branch baseline | `main`, P16 merged through PR 10 |
| P16 merge commit | `6d5a1bd41290e84b69fc490b55d00deb553f52e9` |
| Local closeout commit | `c254d9533e2b3557ec697cb03b3b83a88d63f2a5` |
| Design truth | `docs/design.md` |
| Control truth | `docs/implementation-control.md` |
| Template truth | `docs/fund-analysis-template-draft.md` |
| Accepted P16 closeout | `docs/reviews/p16-main-branch-closeout-20260522.md` |
| Accepted aggregate judgment | `docs/reviews/p16-aggregate-deepreview-controller-judgment-20260522.md` |
| Accepted PR judgment | `docs/reviews/p16-pr-review-controller-judgment-20260522.md` |
| Optional scoped input read | `docs/repo-audit-20260522.md` |

Explicitly excluded and not used:

- `docs/design0522.md`
- `docs/implementation-control0522.md`
- `docs/repo-audit-20260521.md`

## Root Problem After P16

P13-P16 established the direct annual-report disclosure path for `tracking_error`, then repeatedly tested it against production candidates. The observed result is a negative evidence boundary:

- `001548` has no accepted direct observed `tracking_error` disclosure.
- `004194`、`005313`、`017644`、`019918`、`019923` also have no accepted direct observed `tracking_error` disclosure.
- Target/limit text、manager narrative、benchmark-only text、standard-deviation-only text、ambiguous values and incomplete anchors must remain blocked.

从第一性原理看，质量门控的下一步应该降低“错误接受”和“错误沉默”的风险，而不是扩大数据来源：

1. `tracking_error` 是 enhanced-index / index-fund 的关键 P1 字段，但 production evidence 很稀缺。
2. 证据稀缺时，系统最重要的行为是 fail closed 且解释一致。
3. P16 aggregate residual 已记录 extractor early-return / note consistency 是未来 refinement 候选。
4. 该问题位于 Fund Capability documents/extractor 层，能在现有边界内实现并测试。
5. 相比外部指数适配器、计算型 tracking error 或 Evidence Confirm，它不需要发明未来架构。

因此，下一个 implementable work unit 应该先加固 `tracking_error` ambiguity boundary，而不是继续 golden expansion。

## Candidate Table

| Candidate | Decision | First-principles rationale |
|---|---|---|
| P17-S1 `tracking_error` extractor ambiguity boundary and note consistency | **Accept** | 直接处理 P15/P16 后留下的真实质量风险：无直接披露时必须稳定 fail closed，并保留可审计 blocker/note。属于 Fund Capability extractor 责任边界；不需要新数据源、LLM、Dayu、Service/UI/Engine 改造或 golden schema 变更；可用现有 fixture/production-like snippets 做 deterministic tests。 |
| Production `tracking_error` golden rows for `001548` | Reject | P15-S1A 已接受 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`。刷新 provenance 或重读同一文本不会把 target/limit 或 narrative 变成 observed disclosure。继续推进会违反“证据必须可溯源”和“无直接证据不得 golden”的约束。 |
| Production `tracking_error` golden rows for five P16 enhanced-index candidates | Reject | P16-S1 已阻断全部 5 只候选的 `tracking_error`。P16 closeout 明确禁止从 target/limit、manager narrative、benchmark-only 或 incomplete anchors 添加 rows。 |
| Future source-metadata retry with `force_refresh=True` for `001548` | Defer | 可作为 provenance hygiene，但它不解决 product correctness gap；只有在 controller 明确选择 evidence retry 时才值得做。不得把 retry 结果自动升级为 golden evidence。 |
| Composite `benchmark_index_name=null` / `benchmark_component_text` tuple comparable schema | Defer | P16 已用标量 rows 和 tests 保护 composite no-synthesis。null/tuple active golden semantics 需要 schema 设计，blast radius 高于当前 extractor refinement。 |
| Index methodology / constituents extraction | Defer | 长期价值高，但需要新字段契约、anchor 规则、quality denominator 与 README 同步；当前 P16 明确只接受 benchmark-context，不应把 methodology/constituents 混入 follow-up。 |
| Calculated tracking error / external index series | Reject for next phase | 会引入计算语义、外部数据、period alignment、provenance 与 failure taxonomy 新问题。P15/P16 的 root cause 是“缺 direct observed disclosure”，不是缺计算器。 |
| E1-E3 / Evidence Confirm / LLM audit | Defer | 属于未来 audit architecture phase。当前 MVP 主链路确定性，不能为了一个 extractor residual 引入 LLM/Dayu runtime。 |
| Repo-hygiene candidates D-1 / C-1 / C-2 / C-9 | Defer | 有维护价值，但需从当前代码重新验证，不应借 post-P16 product residual gate 处理。`docs/repo-audit-20260522.md` 是 scoped input，不是当前代码事实替代品。 |
| RR-13 duplicate `016492` auto mutation | Reject unless explicitly authorized | RR-13 是 user/app source-owned。不得自动改 CSV 或 source data；只能在用户明确授权后另开数据源修正 gate。 |
| Control/design doc refresh | Defer | 当前任务要求不修改 `docs/design.md` / `docs/implementation-control.md`。P17-S1 也不需要改变分层或设计真源。 |

## Recommended Next Phase

### Name

```text
P17-S1 tracking_error extractor ambiguity boundary and note consistency
```

### Goal

在 Fund Capability 内部加固 `tracking_error` direct-disclosure 抽取边界，使当前抽取器对“目标/限制/叙述/benchmark-only/standard-deviation-only/ambiguous/incomplete-anchor”文本稳定输出 fail-closed 结果，并让 missing reason / note / source_type / calculation_method 口径一致、可测试、可用于后续 evidence acquisition 判断。

该阶段要回答的窄问题：

```text
When annual-report text mentions tracking error without direct observed disclosure, does the extractor consistently reject it
with the right blocker semantics without suppressing a valid direct-looking disclosure elsewhere in the same bounded input?
```

### Non-goals

- 不添加、修改或重建 production golden rows。
- 不把 `001548` 或 5 只 P16 enhanced-index candidates 的 `tracking_error` 状态升级为 accepted。
- 不计算 tracking error。
- 不引入 external index adapter、index series、methodology extraction、constituents extraction。
- 不引入 LLM writing、E1-E3、Evidence Confirm、Dayu Host/Engine/tool loop。
- 不修改 Service/UI/Engine/renderer/quality gate source access boundaries。
- 不修改 `docs/design.md`、`docs/implementation-control.md`、README、selected CSV、RR-13 或外部 GitHub state。

### Owned Files / Modules

Future implementation may own only this narrow write set after plan review acceptance:

| Area | Files / modules | Allowed scope |
|---|---|---|
| Fund Capability extractor | `fund_agent/fund/extractors/` tracking-error related module(s) | Refactor ambiguity/direct-disclosure classification only if current code facts confirm the relevant implementation location. Keep annual-report access through `FundDocumentRepository` / `FundDataExtractor`; do not touch source adapters directly. |
| Fund Capability data model if already present | existing `tracking_error` value / missing-reason types under `fund_agent/fund/` | Only normalize explicit enum/string note semantics if required by tests. No `extra_payload`; all explicit parameters/fields must remain explicit. |
| Tests | existing focused extractor tests under `tests/fund/` | Add fixture snippets for target/limit, narrative, benchmark-only, standard-deviation-only, ambiguous, incomplete-anchor, and direct-looking non-regression cases. |
| Optional docs | `fund_agent/fund/README.md`, `tests/README.md` | Update only if source/test behavior documentation becomes inaccurate under existing README trigger rules. |
| Planning/review artifacts | `docs/reviews/p17-s1-*.md` | Plan, implementation, code review, and controller judgment artifacts only. |

Files/modules not owned:

- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- `docs/golden-answer-template.md`
- `docs/design.md`
- `docs/implementation-control.md`
- root `README.md` unless CLI/user workflow changes, which this phase should avoid
- `docs/code_20260519.csv` or any source CSV
- Service/UI/Engine/renderer/quality gate source orchestration
- external PR/issue/branch state

### Implementation Shape

Future plan-review should require the implementation to inspect current code facts before edits and choose the smallest extractor-only patch. The expected shape is:

1. Identify the current `tracking_error` direct-disclosure extraction/classification function under Fund Capability.
2. Make blocker classification explicit and ordered:
   - direct observed disclosure accepted only when observed value, period, annualization support, `source_type="direct_disclosure"`, `calculation_method="disclosed"`, parseable value, and complete anchor are all present.
   - target/limit/control text is rejected.
   - manager narrative is rejected.
   - benchmark-only text is rejected.
   - standard-deviation-only text is rejected.
   - ambiguous or incomplete-anchor text is rejected.
3. Avoid broad early-return that prevents a later valid direct-looking disclosure in the same bounded section/table from being evaluated.
4. Preserve fail-closed behavior for `schema_drift`、`identity_mismatch`、`integrity_error`; do not let fallback or parsing heuristics rescue them.
5. Keep output shape compatible with current snapshot/quality paths unless tests prove a current note inconsistency requires a targeted model update.

### Required Validation

Minimum future implementation commands:

```bash
.venv/bin/python -m pytest tests/fund/extractors -q
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check HEAD
```

If implementation touches shared dataclasses or comparable extraction, also run:

```bash
.venv/bin/python -m pytest tests/fund -q
.venv/bin/python -m pytest -q
```

No validation may use direct production PDF/cache/source-helper reads. Any production verification, if scoped later, must go through `FundDataExtractor` or `FundDocumentRepository`.

### Success Signals

- Tests prove target/limit/control text does not produce accepted `tracking_error`.
- Tests prove manager narrative does not produce accepted `tracking_error`.
- Tests prove benchmark-only or standard-deviation-only evidence does not produce accepted `tracking_error`.
- Tests prove ambiguous or incomplete-anchor text yields an explicit fail-closed missing/blocker reason.
- Tests prove a valid direct observed disclosure is not suppressed merely because an earlier nearby sentence is target/limit/narrative.
- Existing `index_profile` P16 rows and composite no-synthesis behavior remain unaffected.
- No production `tracking_error` golden rows are added.
- No Service/UI/Engine/renderer/quality gate layer starts reading annual-report source internals.

### Stop Conditions

Stop and produce a blocker artifact before implementation if:

- Current code has no separable `tracking_error` classification boundary and the fix would require broad extractor architecture changes.
- The desired behavior cannot be expressed without changing golden schema, source adapters, repository fallback, Service orchestration, or quality-gate severity.
- The implementation needs direct PDF/cache/source helper access.
- A proposed test relies on indirect evidence rather than a direct observed annual-report snippet.

Stop before merging implementation if:

- Any P15/P16 blocked candidate becomes accepted without new direct observed evidence.
- `tracking_error` rows are added to production golden files.
- `schema_drift`、`identity_mismatch`、`integrity_error` are silently converted into fallback success.
- Explicit parameters are hidden in `extra_payload`.
- RR-13 or selected CSV data must be mutated.

### Residual Risks And Owners

| Residual | Owner / destination | Handling |
|---|---|---|
| `001548` production `tracking_error` golden rows | Future evidence-backed golden gate | Remain blocked unless new direct observed disclosure evidence is accepted. |
| Five P16 enhanced-index production `tracking_error` rows | Future evidence-backed golden gate | Remain blocked; P16 accepted `index_profile` only. |
| Source metadata retry for `001548` | Future provenance hygiene gate | Defer; not a product correctness priority. |
| Composite null/tuple golden semantics | Future golden/comparable schema phase | Defer; P16 scalar rows protect current behavior. |
| Index methodology / constituents extraction | Future source-contract phase | Defer; requires separate field contract and quality denominator plan. |
| Calculated tracking error / external index data | Future data-source/calculation design phase | Reject for immediate next phase; high architecture and evidence blast radius. |
| E1-E3 / Evidence Confirm | Future audit architecture phase | Defer; must not be smuggled into extractor hardening. |
| RR-13 duplicate `016492` | User / App source | Preserve as human-owned; no automatic CSV mutation. |
| Repo hygiene D-1 / C-1 / C-2 / C-9 | Future repo-hygiene phase | Re-verify from current code before any edits. |

## What Must Not Be Touched

For this planning artifact and the recommended next phase, do not touch:

- excluded local drafts: `docs/design0522.md`, `docs/implementation-control0522.md`, `docs/repo-audit-20260521.md`;
- source/golden evidence blocked by P15/P16: no `tracking_error` golden rows for `001548`、`004194`、`005313`、`017644`、`019918`、`019923`;
- RR-13 duplicate `016492` and any source CSV mutation;
- `docs/design.md` and `docs/implementation-control.md` unless a later controller explicitly scopes control/design bookkeeping;
- README files unless source/test behavior changes trigger the existing README rules;
- Service/UI/Engine/renderer/quality gate annual-report access boundaries;
- external GitHub state, including PRs/issues/branches/comments;
- Dayu runtime, Host, Engine, tool loop, external Dayu API, LLM writing, E1-E3, or Evidence Confirm execution;
- any `extra_payload` pattern for explicit parameters.

## Handoff Prompt For Next Plan-review

```text
Gate: P17-S1 tracking_error extractor ambiguity boundary and note consistency.

Use docs/reviews/post-p16-follow-up-planning-20260522.md as the accepted next-phase selection input.

Create docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md.
Do not modify source code, tests, golden files, README, docs/design.md, docs/implementation-control.md, selected CSV, RR-13 data, commit, push, PR, issue, branch, or external state in the plan gate.

The plan must inspect current Fund Capability tracking_error extractor/classification code facts and define a narrow implementation that:
- keeps annual-report access through FundDocumentRepository / FundDataExtractor;
- rejects target/limit/control, manager narrative, benchmark-only, standard-deviation-only, ambiguous, unparseable, and incomplete-anchor text;
- avoids broad early-return that suppresses a later valid direct-looking disclosure in the same bounded input;
- preserves fail-closed behavior for schema_drift, identity_mismatch, and integrity_error;
- adds focused tests without production golden edits.

Do not introduce calculated tracking error, external index adapters, methodology/constituents extraction, QDII subtype redesign, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, or tool loop.
```
