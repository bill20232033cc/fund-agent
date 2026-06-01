# Strict Golden Correctness / Fixture Promotion Plan

日期：2026-05-29

角色：AgentCodex planning worker；不是 controller。本 artifact 只提供 handoff-ready plan，不执行 golden promotion，不修改 promoted golden fixture / golden answer JSON，不提交，不 push / PR / merge / release，不引入 Host / Agent / dayu。

## Worker Self-Check

| 检查项 | 结论 |
|---|---|
| Current gate / role | 当前入口是 `strict golden correctness / fixture promotion gate`；本 worker 只写 plan。 |
| Source of truth | 已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、preflight JSON/Markdown、residual disposition manifest、fixture promotion state manifest、fixture manifest controller judgment、MiMo/DS plan review artifacts，以及 fixture manifest 中 `004393` / `004194` / `006597` / `017641` / `110020` / QDII / FOF entries 的 `source_snapshot_path`、`source_score_path`、`source_quality_gate_path`。 |
| Scope boundary | 推荐本 gate 优先产出 `docs/reviews/` decision/evidence artifact；只在 controller 要求机器可读承接时更新 fixture promotion state manifest；不得改 extractor / score / quality / snapshot / golden fixtures / runtime。 |
| Stop conditions | 任何 promotion、golden answer fixture 修改、quality gate 语义变更、FQ0-FQ6 弱化、QDII probing 重启、FOF taxonomy 例外、Host/Agent/dayu、PR/push/merge/release 都必须停止。 |
| Evidence and validation | docs-only decision artifact 只需 markdown/diff 校验；若更新 JSON manifest，需 JSON schema/self-check；若让 preflight/runtime 消费 manifest，升级为 full ruff、full pytest、preflight rerun。 |
| Next action | 交由 controller 派发 plan review；review 通过后 implementation worker 只写允许文件内的 decision/evidence/manifest update。 |

## Classification

Gate classification：`heavy`。

理由：本 gate 决定 baseline/golden fixture promotion 的前置资格、strict golden correctness 最小契约和 future promotion-prep 状态；即使首选产物是 docs/evidence，也会影响 golden promotion eligibility。按 `AGENTS.md`，baseline/golden promotion、quality gate 语义或 release readiness 相邻工作均使用 heavy。

## Goal

形成 accepted decision：哪些 fund/slot 可以进入 future promotion-prep candidate 决策路径，哪些继续 `blocked` / `deferred`，每项缺什么证据、owner 和 next_gate 是什么。

本 gate 只允许在 decision artifact 的 `decision` 字段表达 candidate 状态；不得把 candidate 状态写入 fixture manifest 的 `fixture_state`。不得把任何 row 标为 `promoted`，不得把 candidate 当成 promotion，且所有 row 必须保持 `promotion_allowed=false`。

## Non-Goals

- 不执行 golden promotion。
- 不修改 `reports/golden-answers/golden-answer.json` 或任何 promoted golden fixture / golden answer fixture。
- 不把 deferred row 改为 ready。
- 不把 quality `warn` 当作 ready 证明；warn 只能进入 residual owner / accepted risk。
- 不削弱 FQ0-FQ6、score correctness、quality gate severity 或 final judgment。
- 不修改 score / quality / snapshot 产物来制造 ready。
- 不重启 QDII probing，不新增 QDII candidate run。
- 不把 QDII-FOF 计作 pure FOF。
- 不进入 release readiness、Host/Agent/dayu、PR/push/merge。
- 不把显式参数塞进 `extra_payload`。
- 不改变 UI -> Service -> Host -> Agent 边界；本 gate 不需要 Host/Agent。

## Direct Evidence Summary

| Evidence | Decision fact |
|---|---|
| `docs/implementation-control.md` | Next entry point 是 `strict golden correctness / fixture promotion gate`，classification 是 `heavy`；当前 golden v1 仍 blocked；fixture state manifest accepted 但不是 promotion manifest。 |
| `reports/golden-readiness-preflight/.../golden_readiness_preflight.json` / `.md` | `overall_status=block`，`ready_count=0`；004393/004194/006597/110020 为 `deferred_with_owner`，017641/QDII/FOF blocked；006597 bond blocker only appears as resolved item。 |
| `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | 所有 entries `promotion_allowed=false`；004393/004194/006597 仍 `needs_fixture_promotion_gate`；017641/QDII/FOF/110020 deferred from minimum v1。 |
| `docs/reviews/fixture-promotion-state-manifest-20260529.json` | `promotion_manifest=false`，`promotion_allowed_default=false`；004393/004194/006597 为 `fixture_state=absent`；017641/QDII/FOF/110020 为 `deferred_from_v1`；所有 entry `promotion_allowed=false`。 |
| `docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md` | Manifest accepted as control-plane state only；no promoted state、no ready state、no runtime/preflight consumption；下一入口要求 strict golden correctness / fixture promotion gate。 |
| `docs/design.md` §7.3-§7.4 | correctness oracle 用 `fund_code + report_year + field_name + sub_field`；基准覆盖不足不能当全域 correctness；FQ0-FQ6 不得削弱。 |
| Source artifacts | 004393/004194 quality `warn`；004393 score-level correctness 仅 9/150 comparable，`coverage_scope=partially_covered`；004194 score-level correctness 5/5 comparable matched，`coverage_scope=covered`；006597 quality `warn`、bond blocker closed but score-level correctness `not_configured`；017641/QDII quality `block`；110020 quality `warn` 但 fund-level `fund_not_covered` / index evidence insufficient；FOF_SLOT 无 source artifacts。 |

## Strict Golden Correctness Minimum Contract

本 gate 必须把 strict correctness 真源拆成两个独立维度，禁止把二者都叫 `strict_golden_coverage` 后混用：

| Dimension | Source field path | 含义 | 对 promotion-prep 的影响 |
|---|---|---|
| Fund-level membership | preflight row `strict_golden_coverage` and fixture manifest `strict_golden_coverage` | golden answer fund-level corpus 是否包含当前 fund/year；当前可能值含 `covered`、`fund_not_covered`、`not_applicable`。 | 只作为 corpus membership gate；`fund_not_covered` 是 hard blocker。它不证明字段级 correctness。 |
| Score-level field comparability | source `score.json` path `correctness.coverage_scope` plus `correctness.comparable_records` / `matched_records` / `mismatched_records` / `unavailable_records` / `record_results[]` | 当前 score run 是否用 strict golden answer JSON 对同年 `fund_code + report_year + field_name + sub_field` 做字段级比对；可能值含 `covered`、`partially_covered`、`fund_not_covered`、`year_not_covered`、`not_configured`、`no_comparable_fields`。 | promotion-prep 决策以此为 strict correctness 主证据；`not_configured`、`fund_not_covered`、`year_not_covered` 或低覆盖 partial 均阻断或转 future gate。 |

Coverage code interpretation：

| Code | Source dimension | Decision rule |
|---|---|---|
| `covered` | fund-level membership | 必要但不充分；必须继续检查 score-level field comparability。 |
| `covered` | score-level field comparability | 可作为较强 candidate 输入，前提是 no mismatch、no quality block、warn residual owner 明确。 |
| `not_configured` | score-level field comparability | 阻断 promotion-prep；006597 当前属于此类，必须用 golden answer JSON 重新 rerun score 后才能评估。 |
| `fund_not_covered` | fund-level membership or score-level field comparability | hard blocker；110020、017641、QDII rows 不得进入 candidate。 |
| `partially_covered` | score-level field comparability | 不得自动升级为 promotion-prep candidate；必须提供字段级 breakdown，特别是 P0/P1/P2 可比覆盖，且由 controller 接受 partial coverage decision。004393 当前默认不 ready。 |

Additional rules：

- 同年同字段明确 mismatch 必须保持 FQ1/block，不得靠 disposition 覆盖。
- `quality_gate_status=warn` 允许进入 candidate review，但不能单独证明 ready；必须记录 warning fields、active owner 或明确 future placeholder owner。
- `quality_gate_status=block` 必须阻断 promotion-prep。
- 当 fund-level membership 与 score-level field comparability 不一致时，以 score-level field comparability 作为 strict correctness 主证据；fund-level `fund_not_covered` 仍是 hard blocker。
- `strict_golden_coverage=covered` 与 `strict_golden_not_configured` 可同时出现于不同来源维度；必须在 decision artifact 中分别列出 `fund_level_membership` 和 `score_level_field_comparability`。

## Fixture Manifest / Preflight / Residual Alignment

Implementation worker 必须做一个只读 join：

1. 以 `docs/reviews/fixture-promotion-state-manifest-20260529.json` 的 10 个 entries 为 row universe。
2. 对每个 entry 校验 preflight row 存在，`fund_code or slot + year` 一致。
3. 对每个 entry 校验 residual disposition row 存在，`promotion_allowed=false` 一致。
4. 对非空 `source_snapshot_path` / `source_score_path` / `source_quality_gate_path` 校验文件存在，且 artifact 内 fund/year 不矛盾。
5. `FOF_SLOT` 的 source paths 必须保持 null；不得为其制造 snapshot/score/quality。
6. 如果 preflight、residual manifest、fixture manifest 对 blocker/owner/next_gate 矛盾，fail closed 并停止，不自行选择较乐观状态。

## Decision Schema

推荐首选 artifact：

- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md`

若 controller 要求机器可读承接，则允许更新或新增：

- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- 或 `docs/reviews/fixture-promotion-state-manifest-20260529-strict-golden-correctness-update.json`

Decision row fields：

| Field | Rule |
|---|---|
| `fund_or_slot` | fund code 或 `FOF_SLOT`。 |
| `year` | 当前均为 2024。 |
| `decision` | Enum：`promotion_prep_ready_candidate` / `conditional_candidate_pending_partial_coverage_decision` / `blocked` / `deferred_from_minimum_v1` / `needs_future_gate`。Candidate 语义只允许写在本字段，不写入 `fixture_state`。 |
| `fixture_state_after_gate` | 必须使用既有 fixture manifest enum：`absent` / `not_promoted` / `deferred_from_v1` / `blocked` / `ready_for_future_promotion` / `promoted`。本 gate 不使用 `ready_for_future_promotion` 或 `promoted`；004393/004194/006597 默认保持 `absent`，deferred rows 保持 `deferred_from_v1`。 |
| `promotion_allowed` | 本 gate 恒为 `false`。 |
| `fund_level_membership` | 从 preflight row / fixture manifest 的 `strict_golden_coverage` 读取。 |
| `score_level_field_comparability` | 从 `source_score_path` 的 `correctness.coverage_scope` 读取，并同时记录 `correctness.comparable_records`、`matched_records`、`mismatched_records`、`unavailable_records`。 |
| `quality_status` | `pass` / `warn` / `block` / `not_evaluated`。 |
| `blockers` | 当前仍阻断 promotion 或 prep 的 blocker codes。 |
| `accepted_residuals` | quality warn / partial coverage 等可进入 future prep 但未解除 promotion 的 residual。 |
| `missing_evidence` | 下一 gate 需要的证据。 |
| `owner` | 后续 owner。 |
| `next_gate` | 后续 gate。 |
| `evidence_paths` | preflight、manifest、source snapshot/score/quality、controller judgments。 |

JSON manifest update constraints：

- `promotion_manifest=false`。
- `promotion_allowed_default=false`。
- Every entry `promotion_allowed=false`。
- No entry `fixture_state="promoted"`。
- Manifest schema remains unchanged in this gate；do not add `promotion-prep-ready` to `fixture_state`。
- Candidate rows must express candidacy only in the decision artifact `decision` field; fixture manifest `fixture_state` remains an existing enum value, normally unchanged from the accepted manifest。
- Deferred/blocked rows must not use candidate language in `fixture_state`。

## Candidate Decision Table

| fund/slot | Current evidence | Decision | Missing evidence / residual | Owner | Next gate |
|---|---|---|---|---|---|
| `004393` | preflight fund-level membership `covered`; fixture `absent`; score-level field comparability `partially_covered` with `correctness.comparable_records=9`, `matched_records=9`, `mismatched_records=0`, `unavailable_records=141`; quality `warn` for `turnover_rate` FQ2/FQ2F plus FQ0 info。 | `conditional_candidate_pending_partial_coverage_decision` by default; not promotion-prep-ready unless this gate also produces field-level breakdown and controller explicitly accepts the low partial coverage。 | Need field-level breakdown from `score.json.correctness.record_results[]`: P0 comparable/total, P1 comparable/total, P2 comparable/total, and list of unavailable P0 fields; turnover-rate warn owner must be recorded. Fixture state remains `absent`; `promotion_allowed=false`。 | future fixture promotion gate + baseline preflight owner。 | partial coverage decision / strict golden fixture promotion review gate。 |
| `004194` | preflight fund-level membership `covered`; fixture `absent`; score-level field comparability `covered` with `correctness.comparable_records=5`, `matched_records=5`, `mismatched_records=0`; quality `warn` for `tracking_error` and `turnover_rate`。 | `promotion_prep_ready_candidate` in decision artifact only; not promoted and fixture state remains `absent` unless controller separately accepts existing-enum manifest update。 | Quality warn owner required for `tracking_error` and `turnover_rate`; `tracking_error` residual additionally requires P15 reviewed direct observed disclosure evidence before adding tracking-error production golden rows; confirm no FQ1/block。 | future fixture promotion gate + baseline preflight owner；P15 reviewed direct evidence owner for `tracking_error`。 | future strict golden fixture promotion review / P15 tracking-error evidence gate。 |
| `006597` | preflight fund-level membership `covered`; fixture `absent`; bond blocker resolved; source score-level field comparability `not_configured` because latest score run has no golden answer input; quality `warn` for turnover/holder/share_change/FQ4; no `bond_risk_evidence_missing`。 | `needs_future_gate`; may be future candidate input, but not promotion-prep-ready in this gate。 | Must rerun extraction score with `reports/golden-answers/golden-answer.json` as golden answer input and then evaluate `score.json.correctness.coverage_scope` / matched / mismatched / unavailable records; keep bond blocker closed but do not use it as promotion proof。 | future baseline/golden preflight owner + fixture promotion gate。 | strict golden correctness score rerun / fixture promotion gate。 |
| `017641` | QDII; source provenance complete via eligible fallback; quality `block` on P0 `manager_strategy_text`; strict golden `fund_not_covered`; prior disposition `replace`。 | `deferred_from_minimum_v1` / blocked for full v1。 | None for minimum v1; future only via QDII diagnosis / replacement policy。 | future QDII diagnosis / replacement owner。 | QDII diagnosis or explicit deferred-from-v1 gate。 |
| `110020` | reviewed coverage candidate input only; quality `warn`; fund-level membership `fund_not_covered` hard blocker and score-level field comparability `not_configured`; blocker `reviewed_candidate_not_promoted` and `index_evidence_insufficient`。 | `deferred_from_minimum_v1`。 | Deferred because `fund_not_covered` is a hard blocker, unlike 006597's rerunnable `not_configured`; needs reviewed fact freeze, methodology evidence, constituents evidence, strict golden fund-level coverage, score-level correctness, and fixture state。 | future index evidence sufficiency gate。 | index reviewed fact freeze / methodology / constituents evidence gate。 |
| `096001` | QDII; source provenance complete; quality `block` on P0 `nav_benchmark_performance` and FQ4; strict golden `fund_not_covered`; hard stop accepted。 | `deferred_from_minimum_v1` / blocked for full v1。 | Future QDII policy/taxonomy only; no probing now。 | future QDII diagnosis or taxonomy / asset-class fitness gate。 | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate。 |
| `040046` | QDII; source provenance complete; quality `block` via FQ4; strict golden `fund_not_covered`; hard stop accepted。 | `deferred_from_minimum_v1` / blocked for full v1。 | Future QDII policy/taxonomy only; no probing now。 | future QDII diagnosis or taxonomy / asset-class fitness gate。 | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate。 |
| `019172` | QDII; source provenance complete; quality `block` on P0 `manager_strategy_text` and FQ4; strict golden `fund_not_covered`; hard stop accepted。 | `deferred_from_minimum_v1` / blocked for full v1。 | Future QDII policy/taxonomy only; no probing now。 | future QDII diagnosis or taxonomy / asset-class fitness gate。 | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate。 |
| `021539` | QDII; source provenance complete; quality `block` via FQ4; strict golden `fund_not_covered`; hard stop accepted。 | `deferred_from_minimum_v1` / blocked for full v1。 | Future QDII policy/taxonomy only; no probing now。 | future QDII diagnosis or taxonomy / asset-class fitness gate。 | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate。 |
| `FOF_SLOT` | no source snapshot/score/quality; strict golden `not_applicable`; blockers `fof_taxonomy_pending`, `fof_data_gap`。 | `deferred_from_minimum_v1` / blocked for full v1。 | repository-verified pure FOF candidate or taxonomy gate；QDII-FOF 不可计入。 | future FOF taxonomy / pure FOF candidate gate。 | pure FOF repository-verified candidate gate。 |

Default candidate outcome for this plan：`004194` is the only stronger promotion-prep candidate in the decision artifact, still with `promotion_allowed=false` and quality warn owners. `004393` is `conditional_candidate_pending_partial_coverage_decision` by default because 9/150 partial coverage is too low to accept without field-level breakdown and controller judgment.

`006597` is a strong future candidate input because bond blocker is closed, but current source score correctness is `not_configured`; this gate must not mark it promotion-prep-ready until strict golden correctness is configured or explicitly accepted by a later reviewed decision.

## Candidate Rules

### Immediate promotion-prep candidate rule

A fund may receive decision `promotion_prep_ready_candidate` only when all conditions hold:

- source snapshot/score/quality paths exist and match fund/year;
- fund-level membership is not `fund_not_covered`;
- score-level field comparability is `covered`, or `partially_covered` only after field-level breakdown and explicit controller partial-coverage acceptance;
- quality status is not `block`;
- no FQ1 block, no baseline-blocking issue, no source fail-closed violation;
- fixture state remains an existing fixture manifest enum value; candidacy is not encoded in `fixture_state`;
- `promotion_allowed=false` remains unchanged;
- quality `warn` fields have active owner or explicitly recorded future placeholder owner / next gate.

### Blocked/deferred rule

A fund/slot must remain blocked or deferred if any condition holds:

- strict golden status is `not_configured` without accepted correctness decision;
- fund-level membership or score-level field comparability is `fund_not_covered`;
- quality status is `block`;
- source artifacts are null where fund artifacts are required;
- row is QDII under accepted hard stop;
- row is FOF_SLOT without repository-verified pure FOF candidate;
- row is `110020` before methodology / constituents / reviewed fact freeze gate.

### 006597 special rule

006597 bond blocker is resolved, so `bond_risk_evidence_missing` must not appear as an active blocker. That only removes the bond blocker. It does not authorize promotion, because strict golden correctness remains `not_configured` in the latest source score. The next evidence step is a score rerun with `reports/golden-answers/golden-answer.json` so the gate can evaluate `score.json.correctness.coverage_scope` and field-level match results.

### 017641 special rule

017641 keeps `replacement_disposition=replace` and quality block disposition. It cannot be promoted or promotion-prep-ready in this gate even though source provenance is complete.

### QDII rule

096001 / 040046 / 019172 / 021539 remain deferred/blocked; do not start new data probing, do not add evidence runs, and do not reinterpret quality block as warn.

### FOF rule

FOF_SLOT remains taxonomy/data gap. No QDII-FOF or overseas mixed fund may satisfy pure FOF coverage without a separate taxonomy gate.

## Allowed Files

Preferred docs/evidence-only implementation:

- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md`
- optional `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-implementation-evidence-20260529.md`

Optional machine-readable update, only if controller approves:

- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- or new `docs/reviews/fixture-promotion-state-manifest-20260529-strict-golden-correctness-update.json`

If a machine-readable update occurs, it must preserve the existing fixture manifest schema and existing `fixture_state` enum. It may add decision/evidence metadata only if controller explicitly approves that schema-compatible addition; it must not write `promotion-prep-ready` to `fixture_state`.

Disallowed files:

- `reports/golden-answers/**`
- promoted golden fixture / golden answer JSON files
- `reports/extraction-snapshots/**`
- `reports/scoring-runs/**`
- `reports/quality-gate-runs/**`
- extractor / score / quality / snapshot / runtime source files
- Host/Agent/dayu packages
- README/control doc unless controller separately asks for state sync after acceptance

## Validation Matrix

| Scope | Commands / checks | Expected result |
|---|---|---|
| Plan artifact only | `git diff --check -- docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-plan-20260529.md` | no whitespace errors。 |
| Decision Markdown only | `git diff --check -- docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md` | no whitespace errors；table includes all 10 rows。 |
| JSON manifest update | `python -m json.tool <manifest> >/tmp/strict_golden_fixture_manifest_check.json` plus self-check script | JSON parses；10 entries；all `promotion_allowed=false`；no `promoted`；manifest schema unchanged；`fixture_state` only uses existing enum values and never `promotion-prep-ready`。 |
| Source artifact alignment | read-only script over manifest paths | all non-null source paths exist；fund/year match；FOF paths null；quality status, fund-level membership, and score-level field comparability match decision table。 |
| Score correctness extraction | read-only script over each `source_score_path` | reads `score.json.correctness.coverage_scope`, `correctness.comparable_records`, `correctness.matched_records`, `correctness.mismatched_records`, `correctness.unavailable_records`, and `correctness.record_results[]`; 004393 partial coverage breakdown includes P0/P1/P2 comparable and unavailable field list before any candidate acceptance。 |
| Runtime/preflight consumption, only if added | `uv run ruff check .`; `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`; rerun `uv run fund-analysis golden-readiness-preflight --run-id golden-readiness-preflight-20260529 --source-csv docs/code_20260519.csv --golden-answer-path reports/golden-answers/golden-answer.json --output-dir reports/golden-readiness-preflight/golden-readiness-preflight-20260529` | Required only if code/preflight consumption changes；not required for docs-only decision。 |

Preflight rerun decision：not required for recommended docs/evidence-only gate, because current preflight output is a point-in-time snapshot and current preflight does not consume residual/fixture manifests. If a manifest is updated but preflight code is unchanged, completion report must record: "manifest updated; preflight does not consume it yet; future runtime/preflight consumption gate must rerun preflight." Required rerun conditions remain changes to `fund_agent/fund/golden_readiness_preflight.py`, CLI, static disposition inputs, runtime consumption, score/quality/snapshot behavior, or preflight output artifacts.

## Review Requirements

- At least two independent plan reviews before implementation.
- At least two independent implementation/evidence reviews after decision artifact or manifest update.
- Controller judgment must explicitly accept or reject:
  - `004393` `conditional_candidate_pending_partial_coverage_decision`, including whether field-level breakdown is sufficient for any later candidate upgrade;
  - `004194` decision-artifact-only `promotion_prep_ready_candidate`, still `promotion_allowed=false` with tracking_error/turnover_rate warn owners;
  - `006597` future candidate but not promotion-prep-ready due to score-level `not_configured` until rerun with golden answer;
  - 017641/QDII/FOF/110020 deferred/blocked states;
  - whether fixture manifest update occurred and still has all `promotion_allowed=false`;
  - whether preflight rerun was not needed or was executed.

## Stop Conditions

Stop and return to controller if:

- any source artifact is missing or fund/year identity mismatches;
- 004393/004194 show any FQ1/block or mismatch not already in evidence;
- 004393 is proposed as `promotion_prep_ready_candidate` without P0/P1/P2 field-level partial coverage breakdown and controller acceptance;
- 006597 is proposed as ready despite `not_configured`;
- 110020 is proposed as candidate despite fund-level `fund_not_covered`;
- any QDII row is proposed for probing or readiness;
- FOF_SLOT receives non-null artifacts without pure FOF taxonomy gate;
- any row is marked `promoted`, `promotion_allowed=true`, or `fixture_state="promotion-prep-ready"`;
- implementation needs to modify runtime, extractor, score, quality, snapshot, golden answer, promoted fixtures, Host/Agent/dayu, release/PR state;
- preflight and manifests disagree in a way not covered by this plan.

## Completion Report Format

Implementation worker final report must include:

```text
Artifact(s):
- <decision artifact path>
- <optional manifest update path>

Decision summary:
- decision-artifact-only stronger candidate: 004194
- conditional candidate pending partial coverage decision: 004393
- future candidate but not ready until score rerun with golden answer: 006597
- deferred/blocked: 017641, 096001, 040046, 019172, 021539, 110020, FOF_SLOT

Guardrails:
- promotion_allowed=false for every row
- no promoted state
- no `promotion-prep-ready` fixture_state; fixture_state schema unchanged
- no golden answer / fixture mutation
- no QDII probing
- no FQ0-FQ6 weakening

Validation:
- <commands/checks and results>
- score correctness field paths checked: `correctness.coverage_scope`, `comparable_records`, `matched_records`, `mismatched_records`, `unavailable_records`, `record_results[]`
- preflight treated as point-in-time unless runtime consumption changes

Residuals:
- 006597 strict golden correctness score rerun with golden answer
- 004393 partial coverage field-level breakdown and controller decision
- 004194 quality warn owners and P15 tracking_error reviewed direct evidence prerequisite
- 110020 methodology/constituents/reviewed fact freeze
- QDII hard stop
- FOF pure candidate taxonomy/data gap
```
