# 004393 / 004194 / 006597 Strict Correctness Follow-up Plan

日期：2026-05-29

角色：AgentCodex planning worker；不是 controller。本 artifact 是 code-generation-ready plan，只规划 docs/evidence-first follow-up；不实现、不修改代码、不执行 promotion、不修改 golden answer / golden fixtures / fixture manifest、不改 score / quality / snapshot / FQ0-FQ6。

## Verdict

**PASS - plan ready for implementation worker.**

本 gate 分类为 `heavy`，因为它影响 strict golden correctness、fixture promotion 前置判断和 baseline/golden readiness 资格。计划只允许生成 follow-up evidence / decision artifacts，并对 `006597` 执行一次机器 score rerun；任何 promotion、fixture manifest 更新、golden answer 修改、preflight runtime consumption 或 release/PR 外部状态都不在本 gate 内。

## Truth Sources Read

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md`
- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json`
- `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.md`
- `004393` artifacts: `reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024/snapshot.jsonl`, `score.json`, `quality_gate.json`, `golden_set.json`
- `004194` artifacts: `reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/snapshot.jsonl`, `score.json`, `quality_gate.json`, `golden_set.json`
- `006597` artifacts: `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl`, `errors.jsonl`; `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`, `score.md`, `golden_set.json`; `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`

## Current Evidence Summary

| fund | current decision | evidence summary | follow-up disposition |
|---|---|---|---|
| `004393 / 2024` | `conditional_candidate_pending_partial_coverage_decision` | score-level correctness is only `9/150` comparable; P0 `9/11`, P1 `0/10`, mismatch `0`; quality `warn`; fixture state `absent` | Default **not** eligible for minimum v1 promotion-prep. Only a later controller may accept partial coverage risk after explicit owner / residual decision. |
| `004194 / 2024` | `conditional_candidate_pending_p0_coverage_decision` | score-level `coverage_scope=covered` covers only five `index_profile.*` records; P0 strict correctness coverage is `0`; quality `warn`; fixture state `absent` | Treat only as `index_profile`专项候选. It is **not** a full fixture promotion-prep candidate. |
| `006597 / 2024` | `needs_future_gate` | bond blocker is closed by accepted NAV-derived drawdown metric context, but latest score has `correctness=unavailable / not_configured` because no golden answer path was supplied; quality `warn`; fixture state `absent` | First rerun score with `reports/golden-answers/golden-answer.json`; only after machine result shows mismatch or unavailable records should human verification start. Bond resolved does not imply promotion-ready. |

## Scope And Non-goals

In scope:

- Produce a follow-up decision/evidence artifact for `004393`, `004194`, and `006597`.
- Rerun only `006597` extraction score with the existing snapshot, existing errors file, and existing strict golden answer JSON.
- Optionally rerun `006597` quality gate from the new score output as a read-only consistency check.
- Record exact machine outcomes: correctness status, total/comparable/matched/mismatched/unavailable records, priority breakdown, and quality issues.

Out of scope:

- No golden promotion.
- No golden answer or golden fixture edits.
- No fixture promotion state manifest update.
- No golden readiness residual disposition manifest update.
- No score / quality / snapshot / FQ0-FQ6 semantic changes.
- No QDII / FOF / `110020` work.
- No PDF/cache/source-helper direct access; no source fallback changes.
- No Host / Agent / dayu work.
- No PR, push, merge, release, or external-state mutation.

## Required 006597 Machine Rerun

Run exactly:

```bash
uv run fund-analysis extraction-score \
  --snapshot-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl \
  --errors-path reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/errors.jsonl \
  --golden-answer-path reports/golden-answers/golden-answer.json \
  --output-dir reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529
```

Recommended read-only quality consistency check after the score rerun:

```bash
uv run fund-analysis quality-gate \
  --score-path reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/score.json \
  --output-dir reports/quality-gate-runs/strict-correctness-follow-up-006597-2024-20260529
```

The quality-gate rerun is not a policy change. It must not modify FQ0-FQ6 semantics and must not be used to infer promotion readiness.

## Result Handling Rules

### 004393

- Keep `promotion_allowed=false` and fixture state `absent`.
- Do not treat `strict_golden_coverage=covered` as full correctness readiness.
- Required decision in follow-up artifact: `not_minimum_v1_promotion_prep_by_default`.
- Required residual owner: future partial-coverage / extractor coverage decision gate.
- Escalate only if a controller explicitly accepts P0 `9/11` and P1 `0/10` residual risk with named missing fields and owner.

### 004194

- Keep `promotion_allowed=false` and fixture state `absent`.
- Do not treat five matched `index_profile.*` records as full fixture readiness.
- Required decision in follow-up artifact: `index_profile_only_candidate_not_full_fixture_ready`.
- Required residual owner: P0 strict correctness coverage gate; P15 tracking-error direct-disclosure evidence remains separate.
- Stop if implementation wording suggests `004194` is full `promotion-prep-ready`.

### 006597

- Keep `promotion_allowed=false` and fixture state `absent`.
- First inspect the new score rerun output.
- If `correctness` remains `unavailable` or `not_configured`, classify as machine setup failure / unresolved strict correctness, not a fund evidence failure.
- If `mismatched_records > 0`, open manual evidence confirmation for the mismatched records only; do not edit golden answer in this gate.
- If `unavailable_records > 0`, manually inspect only the unavailable `006597` same-year records after the machine rerun; do not inspect unrelated cross-fund unavailable rows as 006597 failure.
- If all comparable records match and no same-fund unavailable/mismatch remains, record the improved strict correctness status, but still do **not** mark promotion-ready without a separate fixture promotion gate.

## Manifest / Decision / Preflight Answers

| Question | Plan answer | Reason |
|---|---|---|
| Update fixture manifest? | **No.** | `docs/reviews/fixture-promotion-state-manifest-20260529.json` is accepted control-plane evidence. Updating it would be a fixture promotion state gate, and all three rows still have `promotion_allowed=false`. |
| Add machine-readable decision artifact? | **Yes, in implementation.** | Create a new control-plane JSON decision artifact, e.g. `docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json`, plus a short Markdown evidence summary if needed. It must not be runtime/preflight-consumed and must not be a promotion manifest. |
| Rerun preflight? | **No in this gate.** | Current preflight paths and dispositions are static accepted evidence. Rerunning preflight without a separate consumption/path update would not prove new promotion readiness; changing preflight consumption requires a separate gate. |

## Implementation Steps

1. Re-read the three source score JSON files and fixture/preflight rows for `004393`, `004194`, and `006597`.
2. Run the required `006597` extraction-score command above.
3. Inspect `reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/score.json`:
   - `correctness.golden_answer_path`
   - `correctness.total_records`
   - `correctness.comparable_records`
   - `correctness.matched_records`
   - `correctness.mismatched_records`
   - `correctness.unavailable_records`
   - same-fund `record_results[]` for `fund_code=006597`
4. If the score file exists and parses, run the optional quality-gate consistency check.
5. Write machine-readable control-plane decision JSON with one row per fund:
   - `fund_code`, `report_year`, `decision`, `promotion_allowed=false`, `fixture_state=absent`
   - `source_snapshot_path`, `source_score_path`, `source_quality_gate_path`, `source_score_golden_set_path`
   - strict correctness summary fields
   - residual owner and next gate
   - explicit `not_promotion_manifest=true` and `runtime_consumed=false`
6. Write or update a Markdown evidence summary only if needed for human review.
7. Run validation commands from the matrix below.

## Validation Matrix

| Check | Command / method | Expected |
|---|---|---|
| Markdown syntax / whitespace | `git diff --check -- docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md` and later decision artifacts | Pass |
| 006597 score rerun parses | `python -m json.tool reports/scoring-runs/strict-correctness-follow-up-006597-2024-20260529/score.json >/dev/null` | Pass |
| Machine-readable decision parses | `python -m json.tool docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json >/dev/null` | Pass, if artifact is created |
| No fixture/golden mutation | `git diff -- reports/golden-answers docs/reviews/fixture-promotion-state-manifest-20260529.json docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | Empty |
| No code/runtime mutation | `git diff -- fund_agent tests scripts pyproject.toml uv.lock` | Empty |
| Optional quality gate parses | `python -m json.tool reports/quality-gate-runs/strict-correctness-follow-up-006597-2024-20260529/quality_gate.json >/dev/null` | Pass, if quality gate is rerun |
| Full test suite | Not required unless code is changed | If code unexpectedly changes, run `uv run ruff check .` and `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` |

## Stop Conditions

- Stop if any step requires editing `reports/golden-answers/golden-answer.json` or golden fixtures.
- Stop if any step would set `promotion_allowed=true` or change fixture state.
- Stop if any plan/decision wording upgrades partial coverage to full readiness.
- Stop if `006597` bond blocker closure is used as a substitute for strict correctness evidence.
- Stop if preflight rerun or manifest consumption becomes necessary; that is a separate gate.
- Stop if QDII / FOF / `110020` scope is pulled into this follow-up.

## Acceptance Criteria

- `004393` is recorded as not minimum-v1 promotion-prep by default because strict correctness is partial: `9/150`, P0 `9/11`, P1 `0/10`.
- `004194` is recorded as index-profile-only candidate because P0 strict correctness coverage is `0` and only five `index_profile.*` fields matched.
- `006597` score is rerun with `reports/golden-answers/golden-answer.json` before any manual核验.
- Manual核验 is only triggered by machine rerun `mismatch` or same-fund `unavailable`.
- All rows remain `promotion_allowed=false`; no golden / fixture / manifest / preflight / FQ semantics are changed.
