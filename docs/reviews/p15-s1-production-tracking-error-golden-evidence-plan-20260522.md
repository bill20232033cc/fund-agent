# P15-S1 Production Tracking Error Golden Evidence Plan（2026-05-22）

## Verdict

`BLOCKED_NO_REVIEWED_DIRECT_DISCLOSURE_EVIDENCE`

P15-S1 先评估 primary candidate `001548`（天弘上证50ETF联接A，2024 年年报）。当前仓库 artifact 中没有 reviewed direct `tracking_error` disclosure evidence，不能提出生产 golden rows。

推荐下一 implementation gate：

```text
P15-S1A tracking_error source-contract / evidence-acquisition plan-review
```

该后续 gate 只能负责获取或证明可复核直接披露证据；在证据取得前，不得修改 `reports/golden-answers/golden-answer-prefill-reviewed.md`、`reports/golden-answers/golden-answer.json`、`docs/golden-answer-template.md` 或任何测试来“补齐”生产 `tracking_error` golden correctness。

## Evidence Discovery Protocol

本 plan 只使用当前仓库 artifact，且显式排除 `docs/repo-audit-20260521.md`。

已检查输入与证据面：

- `docs/design.md`：设计真源要求证据可审计、生产年报访问经 `FundDocumentRepository`、benchmark-only 不能证明跟踪误差值。
- `docs/implementation-control.md`：当前 gate 为 `P15-S1 production tracking_error golden evidence plan-review`，primary candidate 是 `001548`。
- `docs/reviews/post-p14-follow-up-planning-20260522.md`：P15-S1 必须 stop if no reviewed direct `tracking_error` disclosure evidence。
- `docs/reviews/post-p14-follow-up-plan-review-controller-judgment-20260522.md`：明确 `001548` first、拒绝 benchmark-only evidence。
- `docs/reviews/p14-main-branch-closeout-20260522.md`：P14 只添加 reviewed `001548` `index_profile` production golden rows；`161725` 只是 deterministic fixture。
- `reports/golden-answers/golden-answer-prefill-reviewed.md`：`001548` 只有 `index_profile`、benchmark、investment_objective、strategy_summary 等行，没有 `tracking_error` 行。
- `reports/golden-answers/golden-answer.json`：`001548` strict golden records 中没有 `field_name=tracking_error`。
- `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md`：明确 “No production `tracking_error` golden rows were added”。
- `docs/reviews/p14-s1-code-review-controller-judgment-20260522.md`：明确生产 golden 只增加 reviewed-evidence-backed `001548` `index_profile` rows，未增加生产 `tracking_error` rows。

Rejected source strings observed for `001548`:

| Location | Text class | Decision |
|---|---|---|
| `reports/golden-answers/golden-answer-prefill-reviewed.md`, `001548.product_profile.investment_objective`, source `年报2024 §2 page-6 page-6-table-1` | target / limit text: “年化跟踪误差控制在2%以内” | reject as value proof; this is an investment objective threshold, not observed tracking error |
| `reports/golden-answers/golden-answer-prefill-reviewed.md`, `001548.manager_strategy_text.strategy_summary`, source `年报2024 §4 strategy_summary` | narrative about tracking-error minimization and sources | reject as value proof; no actual observed numeric `tracking_error` value is disclosed |
| `reports/golden-answers/golden-answer-prefill-reviewed.md`, `001548.index_profile.*`, source `年报2024 §2 page-6 page-6-table-0 benchmark` | benchmark context | accept only for `index_profile`; reject for `tracking_error` value proof |

Discovery commands used conceptually by future reviewers:

```bash
rg -n "001548|tracking_error|跟踪误差" --glob '!docs/repo-audit-20260521.md' docs reports tests fund_agent
jq -r '.funds[] | select(.fund_code=="001548") | .records[] | [.field_name,.sub_field,.expected_value] | @tsv' reports/golden-answers/golden-answer.json
```

## Evidence Decision Tree

Acceptance branch for production `tracking_error` golden rows:

1. Fund must be `001548` first unless controller authorizes a different selected-fund candidate.
2. Evidence must be from reviewed current repo artifacts or a future approved evidence-acquisition artifact.
3. Evidence must identify fund code, year, report section, table/page/row or reviewed artifact location.
4. Evidence text must disclose an observed tracking-error value, not only a target, limit, benchmark, standard deviation, return gap, or narrative cause.
5. Accepted value must map to current comparable sub-fields: `value_text`, `period_label`, `annualized`, `source_type`, and any present scalar metadata.
6. Future production annual-report access must be through `FundDocumentRepository` via `FundDataExtractor` / Fund Capability. Service, UI, Engine, renderer, quality gate, and golden tooling must not directly read PDF cache, source adapters, or download helpers.

Blocked branch:

1. If only benchmark evidence exists, stop.
2. If only investment objective target/limit text exists, stop.
3. If only manager narrative mentions minimizing or controlling tracking error, stop.
4. If evidence requires calculating tracking error from fund/index series, stop and route to a calculated tracking-error phase.
5. If evidence requires a new external index adapter, methodology extraction, constituents extraction, QDII subtype policy, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, or tool loop, stop and route to the corresponding future phase.

Current P15-S1 result follows the blocked branch.

## Proposed Rows / Blocker Outcome

No rows are proposed.

Blocked outcome record:

| Field | Value |
|---|---|
| candidate | `001548` |
| fund name | 天弘上证50ETF联接A |
| year | `2024` |
| required field | `tracking_error` |
| required evidence class | reviewed direct observed tracking-error disclosure |
| reviewed artifact status | no `tracking_error` row in reviewed Markdown or strict JSON |
| rejected evidence | target/limit text, benchmark-only text, manager narrative |
| blocker | no exact observed `tracking_error` value, period, annualization status, or source type can be proven |
| decision | do not edit production golden files |
| next gate | `P15-S1A tracking_error source-contract / evidence-acquisition plan-review` |

Shape of rows that may be accepted only after evidence acquisition:

| fund_code | field_name | sub_field | expected_value | confidence | source |
|---|---|---|---|---|---|
| `001548` | `tracking_error` | `value_text` | `<observed value from direct disclosure>` | `high/medium` | `年报2024 §<section> page/table/row <tracking_error>` |
| `001548` | `tracking_error` | `period_label` | `<disclosed period label>` | `high/medium` | same direct disclosure source |
| `001548` | `tracking_error` | `annualized` | `True` or `False` | `high/medium` | same direct disclosure source |
| `001548` | `tracking_error` | `source_type` | `direct_disclosure` | `high` | same direct disclosure source |

## Future File Ownership

No implementation files are owned by this P15-S1 blocker plan.

If a future evidence-acquisition gate finds acceptable direct disclosure, file ownership should be limited to:

| Area | Files | Owner |
|---|---|---|
| reviewed golden Markdown | `reports/golden-answers/golden-answer-prefill-reviewed.md` | future golden implementation agent |
| strict golden JSON | `reports/golden-answers/golden-answer.json` rebuilt through existing `golden-build` path | future golden implementation agent |
| optional template row scaffolding | `docs/golden-answer-template.md`, only if rows are meant to persist in template | future golden implementation agent |
| golden tooling tests | `tests/fund/test_golden_prefill.py`, `tests/fund/test_golden_answer.py` only if current schema/tooling lacks coverage | future golden implementation agent |
| correctness / score validation | `tests/fund/test_extraction_score.py`, `tests/fund/test_extraction_snapshot.py`, `tests/fund/test_quality_gate_integration.py` only if comparable behavior changes | future implementation agent |

Annual-report/source access ownership remains `fund_agent/fund/documents/` and `fund_agent/fund/data_extractor.py` through `FundDocumentRepository`. No future implementation may bypass that boundary.

## Tests And Validation Commands

Current plan artifact validation:

```bash
git diff --check HEAD -- docs/reviews/p15-s1-production-tracking-error-golden-evidence-plan-20260522.md
git status --short --branch
```

Future evidence-backed implementation validation, only if direct disclosure is later proven:

```bash
.venv/bin/python -m pytest tests/fund/test_golden_prefill.py tests/fund/test_golden_answer.py -q
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate_integration.py -q
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py tests/fund/integration/test_p1_sample_matrix.py -q
.venv/bin/python -m ruff check fund_agent tests
.venv/bin/python -m pytest
git diff --check HEAD
```

Expected future success signal:

- `001548` strict golden contains `tracking_error` rows only when source evidence is direct observed disclosure.
- Correctness compares `tracking_error` comparable sub-fields without mismatch.
- No benchmark-only, target-only, or narrative-only evidence enters the `tracking_error` golden denominator.

## Stop Conditions / Rejection Criteria

Reject any implementation or plan that:

- adds `tracking_error` production golden rows for `001548` from benchmark-only evidence;
- treats “年化跟踪误差控制在2%以内” as actual observed tracking error;
- treats tracking-error source/cause narrative as actual observed tracking error;
- calculates tracking error from NAV/index series in this gate;
- introduces external index adapter, methodology extraction, constituents extraction, QDII subtype redesign, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, or tool loop;
- changes `ExtractionMode`, snapshot schema, quality gate severity, Service/UI/API contract, or renderer behavior;
- touches RR-13, `docs/code_20260519.csv`, source CSV files, README, production code, tests, golden files, `docs/design.md`, or `docs/implementation-control.md` during this plan gate;
- reads, edits, stages, cites, publishes, or otherwise uses `docs/repo-audit-20260521.md`.

## Residuals And Owners

| Residual | Owner | Status |
|---|---|---|
| Production `tracking_error` golden correctness for `001548` | `P15-S1A source-contract / evidence-acquisition` | blocked until direct disclosure evidence exists |
| Enhanced-index production golden expansion | future selected-fund/golden expansion | residual; do not force into P15-S1 |
| Calculated tracking error | future data-source/calculation phase | out of scope |
| External index adapter | future source/data phase | out of scope |
| Index methodology / constituents extraction | future source-contract phase | out of scope |
| QDII subtype applicability | future subtype-design phase | out of scope |
| E1-E3 / Evidence Confirm | future audit architecture phase | out of scope |
| RR-13 duplicate `016492` | User / App source | untouched |
| `docs/repo-audit-20260521.md` | Controller / user | excluded |

## Explicit Non-goals

- No production code changes.
- No test changes.
- No golden Markdown, golden JSON, or golden template changes.
- No README changes.
- No `docs/design.md` or `docs/implementation-control.md` changes.
- No commits, pushes, PRs, branch cleanup, or external comments.
- No calculated tracking error.
- No external index data adapter.
- No methodology or constituents extraction.
- No QDII subtype redesign.
- No E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, or tool loop.
- No RR-13 or source CSV work.

## Plan Review Checklist

- [x] Primary candidate `001548` evaluated first.
- [x] Reviewed direct `tracking_error` evidence was required.
- [x] No reviewed direct observed `tracking_error` value was found in current repo artifacts.
- [x] Benchmark-only evidence was explicitly rejected for `tracking_error` value proof.
- [x] Target/limit and narrative evidence were explicitly rejected.
- [x] No production golden rows were proposed.
- [x] Future annual-report/source access remains behind `FundDocumentRepository`.
- [x] Enhanced-index production golden expansion remains a future residual.
- [x] Non-goals exclude calculated tracking error, external index adapter, methodology/constituents extraction, QDII redesign, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, and tool loop.
- [x] `docs/repo-audit-20260521.md`, RR-13, source CSV, production code, tests, golden files, README, design doc, and control doc remain out of scope.
