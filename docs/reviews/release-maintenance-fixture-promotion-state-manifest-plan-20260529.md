# Fixture Promotion State Manifest Plan

日期：2026-05-29

角色：AgentCodex planning worker；不是 controller。未启动 `$gateflow` / `/gateflow`，未实现，未创建 fixture promotion state manifest，未修改 runtime / preflight / score / quality / snapshot / golden answer / golden fixture / control doc，未 commit / push / PR / merge / release / golden promotion。

## Worker Self-Check

| 检查项 | 结论 |
|---|---|
| Current gate / role | 当前 work unit 是 `fixture promotion state manifest gate`；本 worker 只产出 handoff-ready plan。 |
| Source of truth | 已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、preflight JSON/Markdown、12-entry residual disposition manifest、residual disposition controller judgment，以及 QDII / FOF / 110020 / 006597 相关 controller judgments。 |
| Scope boundary | 推荐首个实现范围为 `docs/reviews` JSON/evidence only；不让 runtime 或 preflight 消费 manifest。 |
| Stop conditions | 如需 promotion、runtime consumption、QDII probing、strict golden correctness implementation、score/quality/FQ 语义改变、Host/Agent/dayu 或外部 PR/push/release，必须停止并交回 controller。 |
| Evidence and validation | 本计划 artifact 完成后只需 `git diff --check`；后续 manifest gate 需 JSON parser/self-check、两份独立 review、controller judgment。 |
| Next action | 交由 controller 派发 plan review；通过后再由 implementation worker 创建 JSON manifest 和 evidence artifact。 |

## Revision Notes

本次 follow-up 只修订本 plan artifact。修订目标是让 implementation worker 不需要自行选择 row state：

- `fixture_state` 当前行映射改为确定值，不再使用 “A or B”。
- 补充 `global_blockers` schema。
- 补充 12-entry residual manifest 与 10-row preflight join 的 fail-closed 条件。
- 纳入 controller accepted DS findings 1/2/3：确定性 `fixture_state` 推导、具体 blocker reconciliation stop conditions、`blocking_reason` 构造规则。
- 纳入 controller accepted MiMo path-validation clarification：每个非空 source path 必须显式验证磁盘存在。
- 保持 recommended first scope 为 docs/reviews JSON/evidence only，不进入 runtime/preflight consumption。

## Goal

定义一个 handoff-ready、code-generation-ready 的计划，用于产生 machine-readable fixture promotion state manifest。

该 manifest 只描述当前 fund/slot 的 fixture promotion state，明确每个 row 的 `promotion_allowed=false`、阻塞原因、owner、next gate 和证据来源。它不是 promotion manifest，不解除 blocker，不执行 golden corpus promotion，不修改 golden answer fixture 或 promoted fixture。

推荐输出 artifacts：

- `docs/reviews/fixture-promotion-state-manifest-20260529.json`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-evidence-20260529.md`

本计划 artifact 路径：

- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md`

## Direct Evidence

| Evidence | Accepted fact used by this plan |
|---|---|
| `AGENTS.md` | Gate classification rules, no promotion without later independent gate, no QDII probing, explicit params only, no `extra_payload`。 |
| `docs/design.md` | 当前架构仍是确定性 UI -> Service -> `fund_agent/fund` 过渡路径；不得引入 Host/Agent/dayu；FQ0-FQ6、source fallback、FundDocumentRepository 边界保持不变。 |
| `docs/implementation-control.md` | Next entry point 是 `fixture promotion state manifest gate`；classification 是 `heavy`；候选输入限制为 `004393`、`004194`、`006597`，但 promotion 仍禁止。 |
| `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json` / `.md` | 当前 preflight 有 10 个 fund/slot row；`overall_status=block`；fixture state 缺失；`006597` bond blocker 仅为 resolved item，不是 current blocker。 |
| `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` | 12-entry residual manifest：2 个 `GLOBAL` entry 加 10 个 fund/slot entry；所有 entries `promotion_allowed=false`。 |
| `docs/reviews/release-maintenance-golden-readiness-residual-disposition-controller-judgment-20260529.md` | residual disposition accepted；manifest 是 control-plane evidence，不是 promotion manifest，也未被 runtime/preflight 消费。 |
| `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md` | `006597 / 2024` bond risk evidence blocker closed；latest snapshot/score/quality artifacts have no `bond_risk_evidence_missing` blocker。 |
| `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md` | QDII automatic probing stopped；QDII candidates remain provenance-eligible, quality `block`, `not_promoted`。 |
| `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md` | `017641` terminal is `disclosure_data_gap_not_baseline_ready` and `not_promoted`。 |
| `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` | `017641=replace`；FOF slot needs taxonomy gate；`110020` remains include-for-later-review only。 |
| `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md` | `110020` accepted only as reviewed coverage candidate input; methodology / constituents / reviewed fact freeze remain insufficient; `not_promoted`。 |

## Classification And Scope

Gate classification：`heavy`。

理由：该 gate 不改变 runtime 行为，但定义 durable baseline/golden fixture promotion state 的 control-plane schema，属于 baseline/golden promotion 资格判断的前置状态。分类不确定时按 `AGENTS.md` 选择更重一级。

Recommended first implementation scope：

- Only create docs/reviews JSON + evidence artifact.
- Do not change code, tests, runtime, preflight consumption, score policy, quality gate, snapshot generation, renderer, Service/CLI, Host/Agent/dayu.
- Do not create or modify golden answer fixture, golden corpus fixture, promoted fixture, or release readiness artifact.

## Manifest Semantics

The fixture promotion state manifest is a state ledger, not an action ledger.

It answers:

- What is the current fixture state for each fund/slot?
- Why is promotion not allowed?
- Which blocker or residual owns the next action?
- Which preflight, residual disposition, and source artifacts support that state?

It must not answer:

- Which rows are promoted now.
- Which golden answer rows are accepted.
- Which fixture should be mutated.
- Whether golden corpus v1 is ready.

## Schema

Top-level object:

```json
{
  "schema_version": "fund-agent.fixture-promotion-state.v1",
  "accepted_as_of": "2026-05-29",
  "source_preflight_run_id": "golden-readiness-preflight-20260529",
  "source_residual_disposition_manifest": "docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json",
  "promotion_manifest": false,
  "promotion_allowed_default": false,
  "source_artifacts": [],
  "global_blockers": [],
  "entries": []
}
```

Required top-level constraints:

- `promotion_manifest` must be `false`.
- `promotion_allowed_default` must be `false`.
- `entries` must contain exactly the current 10 fund/slot rows from the preflight output.
- The 2 `GLOBAL` residual disposition entries must be represented under `global_blockers`, not mixed into fund/slot `entries`.
- `global_blockers` must contain exactly the current `fixture_promotion_absent` and `qdii_replacement_hard_stop` rows from the residual manifest.

Global blocker object fields:

```json
{
  "scope": "GLOBAL",
  "year": null,
  "blocker": "fixture_promotion_absent",
  "decision": "needs_fixture_promotion_gate",
  "owner": "future fixture promotion gate",
  "next_gate": "produce accepted fixture promotion state manifest",
  "blocking_reason": "No accepted fixture promotion state manifest exists.",
  "evidence_artifacts": [],
  "blocks_v1": true,
  "blocks_minimum_v1": true,
  "promotion_allowed": false
}
```

Global blocker constraints:

- `promotion_allowed` must be `false`.
- `scope` must be `GLOBAL`.
- `year` must be `null`.
- Current valid global blockers are exactly `fixture_promotion_absent` and `qdii_replacement_hard_stop`.
- `qdii_replacement_hard_stop` must keep `blocks_minimum_v1=false` per accepted residual disposition; this does not make any QDII row ready.

Entry object fields:

```json
{
  "fund_code": "006597",
  "slot": null,
  "year": 2024,
  "fixture_state": "absent",
  "promotion_allowed": false,
  "promotion_blockers": [
    "strict_golden_not_configured",
    "fixture_promotion_absent"
  ],
  "blocking_reason": "Fixture state is absent and strict golden correctness remains unresolved.",
  "decision": "needs_fixture_promotion_gate",
  "owner": "future fixture promotion gate + future baseline/golden preflight owner",
  "next_gate": "fixture promotion / strict golden coverage gate",
  "evidence_artifacts": [],
  "source_snapshot_path": "reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl",
  "source_score_path": "reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json",
  "source_quality_gate_path": "reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json"
}
```

Field rules:

| Field | Rule |
|---|---|
| `fund_code` | Six-digit fund code for fund rows; `null` for non-fund slot rows. |
| `slot` | `null` for fund rows; special slot identifier such as `FOF_SLOT` for slot rows. |
| `year` | Report year integer where applicable; current rows use `2024`. |
| `fixture_state` | Enum: `absent`, `not_promoted`, `deferred_from_v1`, `blocked`, `ready_for_future_promotion`, `promoted`. |
| `promotion_allowed` | Must be `false` for every row in this gate. |
| `promotion_blockers` | Current blocker codes from preflight row plus residual-disposition blocker codes when relevant; must not be empty unless future controller explicitly accepts a ready state. |
| `blocking_reason` | Human-readable explanation for why `promotion_allowed=false`. |
| `decision` | Primary residual decision from the 12-entry residual manifest, normalized for fixture state. |
| `owner` | Owner from residual manifest or preflight blocker owner. |
| `next_gate` | Next gate from residual manifest or preflight blocker. |
| `evidence_artifacts` | Controller judgment/report paths supporting the row state. |
| `source_snapshot_path` | Snapshot path from preflight static disposition manifest where applicable; `null` only for slot rows without artifacts. |
| `source_score_path` | Score path from preflight static disposition manifest where applicable. |
| `source_quality_gate_path` | Quality gate path from preflight static disposition manifest where applicable. |

Optional but recommended entry fields:

| Field | Rule |
|---|---|
| `source_score_golden_set_path` | Golden set path from preflight static disposition manifest where applicable. This is source evidence only, not golden promotion. |
| `quality_gate_status` | Copy from preflight row for auditability. |
| `strict_golden_coverage` | Copy from preflight row for auditability; fund-level coverage is not readiness proof. |
| `preflight_readiness` | Copy from preflight row. |
| `preflight_disposition` | Copy from preflight row. |
| `replacement_disposition` | Copy from residual row when present, e.g. `017641=replace`; otherwise `null`. |

Fixture state enum semantics:

| State | Meaning | Allowed in current gate |
|---|---|---|
| `absent` | No accepted fixture promotion state exists for this fund/slot. | Yes |
| `not_promoted` | Prior state explicitly says the item is not promoted. | Yes |
| `deferred_from_v1` | Row remains a full-v1 blocker but is excluded from accepted minimum-v1 path. | Yes |
| `blocked` | Row has quality/source/taxonomy/policy blockers and is not a future promotion candidate under current policy. | Yes |
| `ready_for_future_promotion` | A later controller may use this state only after strict golden/quality/fixture blockers are accepted. | No for current known rows unless controller explicitly upgrades after review. |
| `promoted` | Promotion already occurred. | Forbidden in this gate |

Hard constraint：`promoted` is forbidden, and `promotion_allowed=true` is forbidden unless a later independent promotion gate accepts it. `ready_for_future_promotion` is also forbidden for all current rows in the first manifest because no row has accepted strict-golden/quality/fixture readiness.

Deterministic `fixture_state` derivation rules for this first manifest:

1. If `decision="needs_fixture_promotion_gate"` and preflight `fixture_promotion_state="absent"`, output `fixture_state="absent"`.
2. If `decision="defer_from_v1"`, output `fixture_state="deferred_from_v1"`.
3. `quality_gate_block` must remain in `promotion_blockers` and `blocking_reason`, but it must not change a deferred row into `ready_for_future_promotion`.
4. `fixture_state="ready_for_future_promotion"` is forbidden for every current row.
5. `fixture_state="promoted"` is forbidden for every current row.
6. If a future source row has a different decision/state combination, implementation must stop unless a new gate or explicit controller decision extends this derivation table.

## Consuming The 12-Entry Residual Disposition Manifest

Implementation must consume `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json` as an input source, not as runtime configuration.

Consumption algorithm:

1. Parse the residual manifest.
2. Split entries into:
   - `GLOBAL` entries: exactly 2 current rows, moved into top-level `global_blockers`.
   - fund/slot entries: exactly 10 current rows, joined to preflight rows by `(fund_or_slot, report_year)`.
3. Parse `golden_readiness_preflight.json`.
4. Build a map from preflight `rows[]` by `(fund_code, report_year)`.
5. Build a map from `static_disposition_manifest.entries[]` by `(fund_code, report_year)` for `source_snapshot_path`, `source_score_path`, and `source_quality_gate_path`.
6. For each residual fund/slot entry:
   - derive `fund_code` or `slot`;
   - copy `year`;
   - copy `decision`, `owner`, `next_gate`, `evidence_artifacts`;
   - copy `current_blockers` into `promotion_blockers`;
   - copy source paths from static disposition entry when applicable;
   - set `promotion_allowed=false`.
7. Reconcile with preflight row:
   - keep preflight `fixture_promotion_state` as evidence, but normalize output `fixture_state` according to row decision and blocker status;
   - apply the concrete blocker reconciliation stop conditions below.
8. Validate row count and all required fields before writing evidence.

Fail-closed join conditions:

- If residual manifest entry count is not 12, stop.
- If residual `GLOBAL` entry count is not 2, stop.
- If residual fund/slot entry count is not 10, stop.
- If preflight row count is not 10, stop.
- If any residual fund/slot key is absent from preflight rows, stop.
- If any applicable fund row lacks a static source disposition entry or source path, stop.
- If any non-null `source_snapshot_path`, `source_score_path`, or `source_quality_gate_path` does not exist on disk, stop.
- If `FOF_SLOT` has non-null source snapshot/score/quality paths, stop.
- If any row would derive `promotion_allowed=true`, `fixture_state=promoted`, or `fixture_state=ready_for_future_promotion`, stop.
- If `006597` promotion blockers include `bond_risk_evidence_missing`, stop.

Concrete blocker reconciliation stop conditions:

- For each fund/slot row, if any preflight `blockers[]` item with `severity="block"` is missing from residual `current_blockers`, stop.
- For each fund/slot row, if any residual `current_blockers` item is missing from preflight `blockers[]`, stop unless it is explicitly classified as global/policy-only.
- Current global/policy-only exceptions are limited to top-level `GLOBAL` blockers and metadata fields: `qdii_replacement_hard_stop`, top-level `fixture_promotion_absent`, `policy_status`, and `replacement_disposition`. These exceptions must not be inserted into fund-row blocker reconciliation unless already present in that row's preflight blockers.
- If fund code, slot id, or year mismatches across residual entry, preflight row, and static disposition entry, stop.
- If any join key is duplicate or missing in residual fund/slot entries, preflight rows, or static disposition fund entries, stop.
- If `006597` has `bond_risk_evidence_missing` in current preflight blockers or residual `current_blockers`, stop.
- Warning-only differences do not stop the gate, but implementation evidence must record them with row key, warning code/message, and why they do not alter `promotion_allowed=false`.

Precedence rules:

- Residual disposition manifest decides `decision`, `owner`, `next_gate`, `blocks_minimum_v1`, and promotion policy.
- Preflight output decides current readiness, quality status, strict golden coverage, and current blocker observations.
- Static preflight disposition entries provide source snapshot/score/quality paths.
- Controller judgments provide evidence authority; generated report paths alone are insufficient.

Blocking reason construction:

1. Start from residual manifest `decision_reason`.
2. Append concise summaries of every preflight blocker message for the same row, preserving blocker codes.
3. For `006597`, append explicit context: `bond_risk_evidence_missing` is closed by accepted NAV-derived drawdown metric evidence, but fixture state remains absent and strict golden correctness remains unresolved.
4. For `017641`, append explicit context: prior controller judgment preserves `replacement_disposition=replace`; it remains not baseline/golden ready.
5. For QDII rows, append QDII hard-stop context without implying new probing.
6. For `FOF_SLOT`, append pure FOF taxonomy/data-gap context and state QDII-FOF cannot count as pure FOF.
7. For `110020`, append reviewed-candidate-not-promoted plus methodology/constituents/reviewed fact freeze insufficiency.
8. Implementation evidence must record this generation rule and provide either the generated `blocking_reason` per row or a row-level summary proving the rule was followed.

## Required Current Row Mapping

| fund/slot | fixture_state | promotion_allowed | decision | blockers / reason | source paths |
|---|---|---:|---|---|---|
| `004393 / 2024` | `absent` | false | `needs_fixture_promotion_gate` | fixture state absent; quality warn residual owner still needed | small-baseline snapshot/score/quality paths required |
| `004194 / 2024` | `absent` | false | `needs_fixture_promotion_gate` | fixture state absent; quality warn residual owner still needed | small-baseline snapshot/score/quality paths required |
| `006597 / 2024` | `absent` | false | `needs_fixture_promotion_gate` | fixture state absent; strict golden not configured; bond blocker resolved but does not imply fixture readiness | bond-risk-drawdown-nav snapshot/score/quality paths required |
| `017641 / 2024` | `deferred_from_v1` | false | `defer_from_v1` | quality block; strict golden not covered; replacement disposition preserved | source-provenance-rerun paths required |
| `096001 / 2024` | `deferred_from_v1` | false | `defer_from_v1` | QDII hard stop; quality block; strict golden not covered | QDII candidate paths required |
| `040046 / 2024` | `deferred_from_v1` | false | `defer_from_v1` | QDII hard stop; quality block; strict golden not covered | QDII fallback paths required |
| `019172 / 2024` | `deferred_from_v1` | false | `defer_from_v1` | QDII hard stop; quality block; strict golden not covered | QDII fallback paths required |
| `021539 / 2024` | `deferred_from_v1` | false | `defer_from_v1` | QDII hard stop; quality block; strict golden not covered | QDII fallback paths required |
| `FOF_SLOT / 2024` | `deferred_from_v1` | false | `defer_from_v1` | pure FOF taxonomy/data gap; QDII-FOF cannot count as pure FOF | source paths must be null |
| `110020 / 2024` | `deferred_from_v1` | false | `defer_from_v1` | reviewed candidate only; not promoted; methodology/constituents/reviewed fact freeze insufficient | reviewed-candidate paths required |

Required normalization for current first manifest:

- Use `absent` for `004393`, `004194`, `006597` because the immediate blocker is no accepted fixture promotion state.
- Use `deferred_from_v1` for `017641`, QDII candidates, `FOF_SLOT`, and `110020` because residual disposition excludes them from minimum v1.
- Do not use `not_promoted` as the primary fixture state in the first manifest. Preserve `not_promoted` in `blocking_reason` or optional provenance fields if needed, because current preflight fixture state is `absent` and residual state is `defer_from_v1` for deferred rows.
- Do not use `blocked` as the primary fixture state in the first manifest unless controller explicitly asks to distinguish quality/policy blocked rows from deferred rows. Current accepted residual disposition uses `defer_from_v1` for QDII / FOF / `110020` rows.
- Do not use `ready_for_future_promotion` yet. Even candidate rows are not ready because strict golden, quality residual ownership, or fixture-state acceptance is unresolved.
- Do not use `promoted`.
- Any future changed rows require a new gate or explicit controller decision before implementation changes this mapping.

## 006597 Bond Evidence Handling

The manifest must preserve two facts at once:

1. `006597 / 2024` bond risk evidence is resolved.
2. `006597 / 2024` fixture promotion state is still `absent`, with `promotion_allowed=false`.

Implementation requirements:

- Use the accepted drawdown metric controller judgment as evidence that `bond_risk_evidence_missing` is closed.
- Do not include `bond_risk_evidence_missing` in `promotion_blockers` for `006597`.
- Include `strict_golden_not_configured` and `fixture_promotion_absent` as active promotion blockers.
- If evidence text wants to preserve the phrase `not_promoted`, place it in `blocking_reason` or an optional provenance field; do not make it the primary `fixture_state` for `006597` in this first manifest.
- Point source paths to the latest accepted run:
  - `reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl`
  - `reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`
  - `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`
- The 006597 `source_quality_gate_path` must remain exactly `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`; do not substitute the extraction-snapshot directory quality gate path.
- Evidence artifact must assert that preflight treats `bond_risk_evidence_missing` only as resolved item, not blocker.
- If a latest source artifact regresses and contains current `bond_risk_evidence_missing`, stop and classify `006597` as needing controller decision (`fix_now` or `needs_evidence_gate`), not ready.

## QDII / FOF / 110020 Handling

QDII rows:

- `096001`, `040046`, `019172`, and `021539` become `deferred_from_v1` or `blocked`, never ready.
- They preserve `promotion_allowed=false`, QDII hard-stop owner, and quality-block reason.
- No new QDII probing or evidence run is allowed.

`017641`:

- Preserve prior `replacement_disposition=replace` as evidence context in `blocking_reason` or optional metadata.
- It is not a v1 candidate and must not become `ready_for_future_promotion`.

FOF:

- `FOF_SLOT` becomes `deferred_from_v1` or `blocked`, not ready.
- Source paths are `null`.
- Do not count QDII-FOF as pure FOF.
- Next gate remains pure FOF repository-verified candidate or taxonomy gate.

`110020`:

- Becomes `deferred_from_v1` or `blocked`, not ready.
- Preserve blockers: `strict_golden_not_configured`, `strict_golden_fund_not_covered`, `fixture_promotion_absent`, `reviewed_candidate_not_promoted`, and `index_evidence_insufficient`.
- It remains reviewed coverage candidate input only; no methodology/constituents/reviewed fact freeze proof exists.

## Future Preflight Consumption Decision

Current gate should not make preflight/runtime consume the new manifest.

Decision:

- First implementation scope is docs/reviews JSON/evidence only.
- Future preflight consumption is not required to produce the control-plane state manifest.
- If controller later wants preflight to consume this manifest, open a separate `manifest runtime/preflight consumption gate`.

Future runtime/preflight consumption gate must include:

- typed parser/validator in the appropriate Service or Agent boundary after design review;
- explicit parameters only, no `extra_payload`;
- tests for valid manifest, missing required field, invalid enum, `promotion_allowed=true` rejection, `promoted` rejection, GLOBAL/fund row count mismatch, source path nullability, and 006597 bond blocker regression;
- full `uv run ruff check .`;
- full `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`;
- real preflight rerun proving output is stable or intentionally changed by accepted contract.

## Parser / Validation Test Decision

For the recommended first scope, production parser/validation tests are not required because no code will consume the manifest.

Required validation for JSON-only docs gate:

- `python -m json.tool docs/reviews/fixture-promotion-state-manifest-20260529.json`
- a one-off schema/self-check command recorded in evidence, verifying:
  - top-level schema version;
  - exactly 10 fund/slot entries;
  - exactly 2 global blockers;
  - enum values are valid;
  - no `fixture_state="promoted"`;
  - no `fixture_state="ready_for_future_promotion"` for current rows;
  - all `promotion_allowed=false`;
  - all applicable fund rows have non-null source snapshot/score/quality paths;
  - every non-null `source_snapshot_path`, `source_score_path`, and `source_quality_gate_path` exists on disk;
  - `FOF_SLOT` source paths are null;
  - `006597` does not list `bond_risk_evidence_missing` in `promotion_blockers`;
  - `006597` `source_quality_gate_path` equals `reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`;
  - QDII / FOF / 110020 are not `ready_for_future_promotion`.

If implementation chooses to add reusable parser code or runtime consumption despite this plan, that is a scope change and requires controller approval plus tests.

## Implementation Slices

### Slice A — Manifest JSON

Allowed files:

- `docs/reviews/fixture-promotion-state-manifest-20260529.json`

Tasks:

1. Read preflight JSON and residual disposition manifest.
2. Build `global_blockers` from the 2 residual `GLOBAL` entries.
3. Build 10 `entries` from residual fund/slot entries joined to preflight rows and static source paths.
4. Set all `promotion_allowed=false`.
5. Reject any row that would require `promoted`, `ready_for_future_promotion`, or `promotion_allowed=true`.
6. Preserve `not_promoted` and replacement dispositions as evidence/provenance, not as permission to promote.

### Slice B — Evidence Artifact

Allowed files:

- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-evidence-20260529.md`

Tasks:

1. Record all source reads.
2. Summarize row mapping and source paths.
3. Record schema/self-check output.
4. Explicitly state no promotion occurred.
5. Explicitly state no runtime/preflight consumption occurred.
6. Explicitly state that all non-null source paths exist on disk, with any missing path treated as validation failure.

### Slice C — Reviews And Controller Judgment

Required:

- Two independent reviews.
- Controller judgment accepting or rejecting the manifest.
- If accepted, controller may update control doc in a separate controller action if needed.

## Validation Commands

Plan artifact validation:

```bash
git diff --check -- docs/reviews/release-maintenance-fixture-promotion-state-manifest-plan-20260529.md
```

Future implementation validation:

```bash
python -m json.tool docs/reviews/fixture-promotion-state-manifest-20260529.json
git diff --check -- docs/reviews/fixture-promotion-state-manifest-20260529.json docs/reviews/release-maintenance-fixture-promotion-state-manifest-implementation-evidence-20260529.md
```

Future implementation must also run a schema/self-check script or command and paste the pass/fail summary into evidence.

Full ruff/pytest are not required for JSON/evidence-only scope. They become required if any runtime/preflight parser, Service/Agent code, tests, score/quality/snapshot semantics, or package behavior changes.

## Review Checklist

Reviewers must verify:

- Schema includes required fields: `fund_code` / `slot`, `year`, `fixture_state`, `promotion_allowed`, `promotion_blockers`, `decision`, `owner`, `next_gate`, `evidence_artifacts`, `source_snapshot_path`, `source_score_path`, `source_quality_gate_path`.
- Fixture state enum matches this plan and forbids `promoted`.
- 12-entry residual manifest is consumed correctly: 2 global blockers + 10 fund/slot rows.
- Blocker reconciliation uses concrete stop conditions, not a subjective materiality judgment.
- `blocking_reason` is generated from residual `decision_reason` plus preflight blocker messages and required special context.
- `006597` bond blocker remains resolved but fixture state remains absent/not promoted.
- `006597` primary `fixture_state` is `absent`; any `not_promoted` wording is provenance only.
- Every non-null source snapshot/score/quality path exists on disk.
- QDII / FOF / `110020` are `deferred_from_v1`, not ready.
- No row has `promotion_allowed=true`.
- No deferred row is marked ready.
- No QDII probing or QDII-FOF pure FOF shortcut is introduced.
- No FQ0-FQ6, score, quality, snapshot, runtime/preflight, Host/Agent/dayu, release, PR, push, merge, or golden fixture change is present.

## Stop Conditions

Stop and return to controller if:

- Any row appears to need `promotion_allowed=true`.
- Any row appears to need `fixture_state="promoted"`.
- Any deferred row is proposed as `ready_for_future_promotion`.
- Any applicable source path is missing or points to a different fund/year without controller evidence.
- Any non-null source snapshot/score/quality path does not exist on disk.
- `006597` current blockers include `bond_risk_evidence_missing`.
- QDII probing, FOF taxonomy work, 110020 evidence work, strict golden correctness implementation, runtime/preflight consumption, parser code, score/quality/FQ changes, golden fixture mutation, release readiness, Host/Agent/dayu, PR/push/merge become necessary.
- Dirty worktree ownership is unclear.

## Completion Report Format

Implementation worker final report should include:

- Manifest path.
- Evidence path.
- Row count and global blocker count.
- Summary of `004393` / `004194` / `006597` state.
- Summary that QDII / FOF / `110020` are deferred/blocked and not ready.
- Confirmation that all `promotion_allowed=false`.
- Validation commands and results.
- Open questions or residual risks.

## Open Questions

No blocking open question for the recommended docs/reviews JSON/evidence-only scope.

Non-blocking controller decision for later gate:

- Whether a future preflight should consume this manifest. This plan recommends no for the current gate and, if desired later, a separate runtime/preflight consumption implementation gate with parser tests and full validation.
