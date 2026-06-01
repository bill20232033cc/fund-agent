# 004194 P0 Coverage / Index Profile-Only Fixture Decision Implementation Evidence

日期：2026-05-29

角色：AgentCodex implementation/evidence worker。本文记录 Slice 2 docs-only implementation evidence；不是 controller judgment，不启动 `$gateflow` / `/gateflow` / `phaseflow`，不提交、不 push、不 PR、不 merge、不 release、不 promote。

## Changed Files

本 Slice 只新增以下两个 artifact：

- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-20260529.md`
- `docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-implementation-evidence-20260529.md`

未修改 `docs/implementation-control.md`。未修改 runtime code、tests、scripts、reports、manifests、golden answer、fixtures、score、quality gate、snapshot、README、`docs/design.md`、`pyproject.toml`、`uv.lock` 或其它无关 untracked 文件。

## Read-Only Evidence Used

Read-only commands and files used during implementation:

| Evidence / command | Result used |
|---|---|
| `sed -n '1,260p' docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-20260529.md` | Confirmed accepted plan scope, required decision fields, file boundaries, validation commands, and field disposition matrix. |
| `sed -n '1,260p' docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-review-mimo-20260529.md` | Confirmed MiMo `PASS` and independent verification of score counts, five rows, P0 coverage 0, quality warn cause, and forbidden file scope. |
| `sed -n '1,260p' docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-plan-review-glm-20260529.md` | Confirmed GLM `PASS_WITH_FINDINGS`; accepted F1 wording constraint for P16 provenance. |
| `sed -n '720,820p' docs/design.md` | Confirmed §7.3 P0/P1 priority mapping and conditional P1 status for `index_profile` / `tracking_error`; confirmed §7.4 golden coverage and tracking-error prerequisite. |
| `sed -n '1,240p' docs/implementation-control.md` | Confirmed current phase, next entry, heavy classification, accepted route state, and controller-owned control-doc updates. |
| `sed -n '1,260p' docs/reviews/release-maintenance-phase-roadmap-consolidation-20260529.md` | Confirmed Route 1 order and 004194 P0 / index_profile-only decision entry. |
| `sed -n '1,220p' docs/reviews/release-maintenance-004393-partial-coverage-decision-controller-judgment-20260529.md` | Confirmed previous route state and next entry to 004194. |
| `sed -n '1,260p' docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md` and controller judgment | Confirmed upstream 004194 state: `conditional_candidate_pending_p0_coverage_decision`, P0 coverage 0, `fixture_state=absent`, `promotion_allowed=false`. |
| `jq '.correctness | {coverage_scope,total_records,comparable_records,matched_records,mismatched_records,unavailable_records}' reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.json` | Confirmed `covered / 150 / 5 / 5 / 0 / 145`. |
| `jq -r '.correctness.record_results[] | select(.fund_code=="004194") ...' score.json` | Confirmed exactly five 004194 matched rows, all `index_profile.*`, all source `年报2024 §2 page-5 page-5-table-1 benchmark`. |
| `sed -n '1,180p' reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/score.md` | Confirmed human-readable correctness table and exact expected/actual values for the five rows. |
| `jq '.status, .issues' reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024/quality_gate.json` and `quality_gate.md` | Confirmed `status=warn`; issues are FQ2 `tracking_error`, FQ2 `turnover_rate`, and FQ2F failed P1 fields; no FQ1 mismatch. |
| `jq '.rows[] | select(.fund_code=="004194")' reports/golden-readiness-preflight/.../golden_readiness_preflight.json` | Confirmed preflight `deferred_with_owner`, strict coverage `covered`, quality `warn`, fixture state `absent`, blocker `fixture_promotion_absent`. |
| `jq '.entries[] | select(.fund_code=="004194")' docs/reviews/fixture-promotion-state-manifest-20260529.json` | Confirmed `fixture_state=absent`, `promotion_allowed=false`, `blocks_minimum_v1=true`, `blocks_v1=true`. |
| `jq '.records[] | select(.fund_code=="004194")' reports/golden-answers/golden-answer.json` | Confirmed exactly five golden-answer rows for 004194, all `index_profile.*`. |
| `jq -r 'select(.fund_code=="004194") ...' snapshot.jsonl` | Confirmed snapshot `index_profile` values, P0-capable fields, `tracking_error_unparseable`, and missing turnover. |
| `sed -n '1,230p' docs/reviews/p16-s1-enhanced-index-production-golden-candidate-evidence-implementation-20260522.md` | Confirmed P16-S1 `PARTIAL_ACCEPTED_INDEX_PROFILE_ONLY` and 004194 `blocked_no_direct_tracking_error`. |
| `rg -n "P16-S2|BLOCK|blocked|golden|004194|index_profile|tracking_error|direct" docs/reviews/p16-s2* ...` | Confirmed P16-S2 controller judgment `ACCEPTED_BLOCKED_BEFORE_GOLDEN_EDIT_EXTRACTOR_TEXT_DIFF` and no production golden rows added by P16-S2. |
| `rg -n "BLOCKED_NO|direct observed|direct disclosure|tracking_error|target/limit|004194|P15" docs/reviews/p15* ...` | Confirmed P15 direct observed disclosure prerequisite and rejection of target/limit, benchmark-only, narrative, standard deviation, ambiguous, and unparseable evidence. |

One read-only `jq` probe against `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` returned no 004194 entry because that manifest does not contain a direct 004194 entry under the queried path. This did not modify files and did not affect the decision, which relies on preflight and fixture manifest for 004194 fixture state.

## Validation Commands And Results

Required validation before completion:

```bash
git diff --check -- docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-20260529.md docs/reviews/release-maintenance-004194-p0-coverage-index-profile-decision-implementation-evidence-20260529.md
```

Expected：no output.

Actual result：passed, no output.

Forbidden diff check:

```bash
git diff --name-only -- fund_agent tests scripts reports pyproject.toml uv.lock docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json docs/reviews/fixture-promotion-state-manifest-20260529.json
```

Expected：no output. If any forbidden diff appears, stop and report scope breach.

Actual result：passed, no output.

## Forbidden Diff

Status：passed; required forbidden diff command produced no output.

No runtime/test/report/manifest/control-doc mutation was required or authorized.

## Why Ruff / Pytest Not Run

`ruff` and `pytest` were not run because this Slice is docs-only and does not modify Python runtime, tests, reports, score policy, quality gate semantics, snapshot projection, golden answer, fixtures, manifests, package metadata, CLI, renderer, Service/UI, Host/Agent/dayu, or preflight runtime consumption.

Running runtime tests here would add cost without validating the only changed surface: two Markdown decision/evidence artifacts. If any runtime/test/report/manifest diff appears, that is a scope breach for this assignment and should not be validated inside this gate.

## Residual Risks

| Risk | Severity | Owner / next gate |
|---|---|---|
| 004194 has P0 strict correctness coverage `0` | high | future `004194 P0 golden row fact-freeze / strict correctness expansion gate` |
| Current five matched rows validate only `index_profile` benchmark-context scalar rows | high for full fixture; acceptable for diagnostic candidate | future fixture / baseline owner |
| `tracking_error` remains missing / unparseable and blocked for production golden rows | high | P15 / P17 tracking-error direct observed disclosure evidence gate |
| `turnover_rate` remains quality warning | medium | future turnover-rate evidence / extractor gate |
| Methodology and constituents detail are not proven; current rows only say `benchmark_only` | medium | future index evidence owner |
| Performance, cost, manager, holdings, shareholder, and final judgment readiness are not covered by the five rows | high for full fixture | future full fixture promotion-prep gate after P0 expansion |
| Fixture state remains `absent` and `promotion_allowed=false` | expected blocker | future fixture promotion-prep gate |
| Control doc not updated by worker | expected | controller-owned follow-up after reviews |

## Self-Check

- Startup self-check: pass. Treated assignment as worker-only Slice 1 / Slice 2, did not start gateflow/phaseflow, did not commit or mutate external state.
- Pre-edit self-check: pass. Only read evidence before editing; existing unrelated untracked files were noted and left untouched.
- Scope self-check: pass. Wrote only the two allowed Markdown artifact paths.
- GLM F1 wording self-check: pass. Decision artifact states P16-S1 accepted benchmark-context concept, P16-S2 was blocked before golden-row edits, and existing 004194 rows are verified through current scoring.
- Decision self-check: pass. Encoded `decision=index_profile_only_candidate_not_full_fixture_ready`, `minimum_v1_full_fixture_promotion_prep_ready=false`, `index_profile_only_specialized_candidate_allowed=true` only as bounded diagnostic / specialized candidate, `fixture_state_after_gate=absent`, `promotion_allowed=false`, `promotion_manifest=false`, and `tracking_error_production_golden_allowed=false`.
- Evidence self-check: pass. Decision cites `AGENTS.md`, `docs/design.md` §7.3 / §7.4, `docs/implementation-control.md`, accepted plan/reviews, roadmap artifacts, 004393 controller judgment, strict correctness decision/controller judgment, preflight outputs, fixture manifest, 004194 score/snapshot/quality/golden artifacts, `golden-answer.json` 004194 rows, and relevant P15/P16 provenance artifacts.
- Completion validation self-check: pass. `git diff --check` for the two allowed artifact paths passed with no output, and forbidden diff check passed with no output.
