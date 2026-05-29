# Golden Readiness Residual Disposition Plan

日期：2026-05-29

角色：planning worker；Gateflow-governed handoff specialist，不是 controller。未启动 `$gateflow` / `/gateflow`，未改代码、runtime、score、quality、snapshot、golden answer、golden fixture、fixture promotion state，未 commit / push / PR / merge / release / golden promotion。

## Worker Self-Check

| 检查项 | 结论 |
|---|---|
| Current gate / role | 当前 gate 是 `golden readiness residual disposition gate`；本 worker 只产出 plan artifact，不做 controller acceptance。 |
| Source of truth | 已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、golden readiness preflight controller judgment / implementation evidence / aggregate deepreviews、preflight JSON/Markdown、source provenance / 110020 / 017641 / QDII / consolidation / baseline disposition / replacement selection / drawdown metric controller judgments。 |
| Scope boundary | 允许新增本 plan artifact；不得修改代码、runtime、reports/golden-answers、golden fixture、fixture promotion state、FQ0-FQ6、score/quality/snapshot、Host/Agent/dayu、release/PR 状态。 |
| Stop conditions | 无需向用户提出 blocking question；本 plan 将现有 preflight missing inputs 转为 controller disposition rows 和 next gates。 |
| Evidence and validation | 本 artifact 是 docs/evidence-only；验证为 Markdown review + JSON schema/self-check if later tracked JSON is added。当前不跑 full ruff/pytest。 |
| Next action | 交回 controller 做 plan review / controller judgment；promotion 仍禁止。 |

## Goal

对 `golden-readiness preflight` 的 remaining blockers 做 controller-accepted residual disposition matrix：裁决哪些 blocker 必须先修、哪些可 `defer_from_v1`、owner / next gate 是什么、是否需要 tracked machine-readable disposition JSON。该 gate 不解除 blocker、不 promotion、不修改 golden fixture。

## Direct Evidence

| Evidence | Relevant accepted fact |
|---|---|
| `reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json` / `.md` | `overall_status=block`；`ready_count=0`；global blockers 为 `fixture_promotion_absent` 与 `qdii_replacement_hard_stop`；006597 的 `bond_risk_evidence_missing` 只在 resolved item 中出现。 |
| `docs/reviews/release-maintenance-golden-readiness-preflight-controller-judgment-20260529.md` | Preflight gate accepted；remaining blockers 为 fixture promotion、strict golden correctness、QDII hard stop / quality block、FOF taxonomy/data gap、110020 reviewed-but-not-promoted；无 promotion。 |
| `docs/reviews/release-maintenance-golden-readiness-preflight-aggregate-deepreview-mimo-20260529.md` / `...-ds-20260529.md` | 两份 aggregate deepreview accepted；确认 fail-closed、owner/next_gate/evidence 完整、006597 bond blocker 不再作为 blocker。 |
| `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md` | 110020/017641 source provenance complete + eligible fallback；110020 quality `warn` 只允许进入后续 review，017641 quality `block`。 |
| `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md` | 110020 只达到 `reviewed_coverage_candidate_input_accepted`，`not_promoted`；methodology / constituents / reviewed fact freeze evidence insufficient。 |
| `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md` | 017641 terminal classification 为 `disclosure_data_gap_not_baseline_ready`，`promotion_disposition=not_promoted`；不支持 extractor fix、policy/taxonomy change 或 promotion。 |
| `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` | 017641 accepted disposition 为 `replace`；FOF 为 `needs_taxonomy_gate`；006597 当时为 `needs_evidence_gate`。 |
| `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md` | QDII automatic probing stopped；096001/040046/019172/021539 全部 provenance eligible、quality `block`、`not_promoted`；QDII coverage blocked。 |
| `docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md` | 006597/A 2024 NAV-derived max drawdown accepted；latest score has `score_applicability_issues=[]` and quality gate no `bond_risk_evidence_missing`。 |
| `docs/design.md` §6-§7 | 年报访问必须经 `FundDocumentRepository`；fallback fail-closed；FQ0-FQ6 与 strict golden correctness 不得削弱；quality warn 不等于 ready。 |

## Golden v1 Minimum Viable Scope

推荐 controller disposition：**golden v1 不继续追求 QDII / FOF / 110020 纳入 v1；三者均 `defer_from_v1` 或进入 candidate/evidence gate，但不得阻塞最小 v1 的 fixture-promotion path。**

理由：

- QDII：017641 已裁决 `replace/not_promoted`，四个替代候选均 quality `block` 且 021539 后 hard stop；继续追求 QDII v1 会重开 automatic probing，违反 accepted hard stop。
- FOF：当前只有 `FOF_SLOT`，且 `fof_taxonomy_pending` / `fof_data_gap`；没有 repository-verified pure FOF candidate。QDII-FOF 明确不得算 pure FOF。
- 110020：仅为 reviewed coverage candidate input；methodology、constituents、reviewed fact freeze 与 strict golden/fixture 状态均不足。
- 最小 v1 可先聚焦已有较低风险、fund-level strict golden covered 且 quality 非 block 的 carry-forward candidates：004393、004194，以及 bond blocker 已关闭后的 006597。三者仍必须通过 fixture promotion / strict golden correctness gate；本 gate不允许把它们标为 ready。

## Controller Disposition Decisions

### 1. Fixture Promotion Absent

Decision：`needs_fixture_promotion_gate`。

该 blocker 是 global + per-fund blocker，必须在独立 fixture promotion state manifest gate 中解决。当前 preflight 没有 accepted fixture promotion state manifest，因此所有 fund 的 `promotion_allowed=false`。任何 v1 最小范围也不能绕过该 blocker。

### 2. 004393 / 004194 / 006597 Immediate Fixture Promotion Candidates

Decision：`needs_fixture_promotion_gate`；三者可列为 **immediate fixture promotion gate candidates**，不是 ready。

前提：

- 产生 accepted fixture promotion state manifest，且 manifest 只表示 promotion state，不等同 golden promotion manifest。
- 逐项验证 snapshot / score / quality_gate artifact 路径仍存在、身份为同一 `fund_code + report_year`，且没有 quality `block`、FQ1 mismatch、baseline_blocking issue 或来源 fail-closed violation。
- 004393、004194：当前 quality `warn` 与 strict golden fund-level `covered` 不能直接证明 ready；fixture gate 必须记录 warn issue 的接受依据或 residual owner。
- 006597：必须先保持 `bond_risk_evidence_missing` closed 状态，确认 latest drawdown metric artifact 仍为 accepted source，且 no `bond_risk_evidence_missing` / no `drawdown_stress` missing regression；还必须处理 `strict_golden_not_configured` 与 fixture absent。
- 006597 的 `strict_golden_coverage=covered` 与 `strict_golden_not_configured` 不矛盾：前者只表示基金代码存在于 golden answer manifest 的 fund-level 索引中；后者表示 score correctness 比对尚未配置或缺少同年 reviewed golden rows，仍是最终 golden promotion blocker。
- 三者 promotion 仍需后续 fixture promotion gate 的 two-review + controller judgment；本 plan artifact 中 `promotion_allowed=false`。

### 3. 017641

Decision：primary `defer_from_v1`，并通过 `replacement_disposition=replace` 保留 prior `replace/not_promoted` disposition。

017641 不应保留为 v1 candidate，也不应在本 gate替换为新 QDII row。它 source provenance complete 但 quality `block`，manager_strategy_text public triage accepted terminal `disclosure_data_gap_not_baseline_ready`。quality block 处理方式：不削弱 FQ0-FQ6，不把 QDII quality `block` 当 warn，不做 extractor fix；若未来需要，进入 QDII diagnosis / taxonomy / asset-class fitness gate。`replacement_disposition=replace` 的 entry 不得在后续 gate 中被重新评估为 v1 candidate，除非新的 controller judgment 显式推翻或替代 prior replacement decision。

### 4. QDII 四候选 096001 / 040046 / 019172 / 021539

Decision：primary `defer_from_v1`，并在 `policy_status` 中记录 `blocked_until_qdii_policy_or_asset_class_fitness_gate`。

四候选全部 deferred from v1。当前不需要单独 QDII diagnosis gate 作为 v1 前置；只有 controller 决定未来仍要 QDII coverage 时，才开 `QDII diagnosis or taxonomy / asset-class fitness gate`。本 gate不得重开 automatic probing，不得新增 QDII evidence run。

### 5. FOF_SLOT

Decision：primary `defer_from_v1`，并在 metadata 中记录 future `needs_candidate_gate`。

FOF_SLOT deferred from v1。若未来要纳入 FOF，必须先找 `pure fof_fund` repository-verified candidate，或开 FOF taxonomy gate；QDII-FOF 不得计入 pure FOF，也不得用 taxonomy exception 兜底。

### 6. 110020

Decision：primary `defer_from_v1`，并在 metadata 中记录 future index sufficiency `needs_candidate_gate`。

110020 deferred from v1。若未来要纳入，必须先开 `index reviewed fact freeze / methodology / constituents evidence gate`，冻结 reviewed facts、methodology/constituents 证据、strict golden coverage/correctness 与 fixture state。当前 `reviewed_candidate_not_promoted`、`index_evidence_insufficient`、`strict_golden_not_configured`、`strict_golden_fund_not_covered`、`fixture_promotion_absent` 全部保持 blocker。

### 7. Strict Golden Correctness / Coverage Incomplete

Decision：`needs_fixture_promotion_gate` for 004393/004194/006597 candidates；`defer_from_v1` for 017641/QDII/FOF/110020。

不允许把 quality `warn` 或 strict golden fund-level coverage 当成 ready。Strict golden answer v1 当前只执行 fund-level coverage；score correctness `not_configured` 仍是 blocker，不能通过文档声明解除。

Clarification：`strict_golden_coverage=covered` 表示该基金代码存在于 golden answer manifest 的 fund-level coverage 中；`strict_golden_not_configured` 表示 score correctness 比对尚未配置或缺少同年 reviewed golden rows。两者是独立维度，006597 可同时为 fund-level covered 且仍被 strict golden correctness blocker 阻塞。

### 8. Machine-Readable Disposition Manifest

Decision：需要 tracked machine-readable disposition JSON，作为 **disposition manifest**，不是 promotion manifest。

建议 artifact path：

`docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`

原因：

- 当前 preflight 使用 code-local static disposition manifest；preflight controller judgment 已声明 disposition 改变、candidate add/remove、或跨 gate 复用时必须开 machine-readable manifest gate。
- 本 gate 将 QDII/FOF/110020 从 blocking-v1 path 改为 `defer_from_v1`，并把 004393/004194/006597 列为 immediate fixture promotion candidates；这属于 disposition 变化，不能继续靠 static in-code manifest 隐式维护。
- JSON 不应被 runtime 消费，除非另开 runtime/preflight consumption implementation gate；当前 gate只定义 schema 和 artifact path。

Minimum JSON schema：

```json
{
  "schema_version": "fund-agent.golden-readiness-residual-disposition.v1",
  "accepted_as_of": "2026-05-29",
  "source_preflight_run_id": "golden-readiness-preflight-20260529",
  "source_preflight_artifacts": [
    "reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json",
    "reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.md"
  ],
  "promotion_manifest": false,
  "promotion_allowed_default": false,
  "entries": [
    {
      "fund_or_slot": "GLOBAL",
      "report_year": null,
      "current_blockers": ["fixture_promotion_absent"],
      "decision": "needs_fixture_promotion_gate",
      "decision_reason": "no accepted fixture promotion state manifest exists",
      "policy_status": null,
      "next_required_action": "produce accepted fixture promotion state manifest",
      "replacement_disposition": null,
      "owner": "future fixture promotion gate",
      "next_gate": "produce accepted fixture promotion state manifest",
      "evidence_artifacts": [
        "reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json",
        "docs/reviews/release-maintenance-golden-readiness-preflight-controller-judgment-20260529.md"
      ],
      "blocks_v1": true,
      "blocks_minimum_v1": true,
      "promotion_allowed": false
    },
    {
      "fund_or_slot": "004393",
      "report_year": 2024,
      "current_blockers": ["fixture_promotion_absent"],
      "decision": "needs_fixture_promotion_gate",
      "decision_reason": "immediate fixture promotion candidate, but fixture state and strict golden residuals are not accepted",
      "policy_status": null,
      "next_required_action": "fixture promotion state manifest plus strict golden residual handling",
      "replacement_disposition": null,
      "owner": "future fixture promotion gate",
      "next_gate": "fixture promotion / strict golden coverage gate",
      "evidence_artifacts": [
        "reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json"
      ],
      "blocks_v1": true,
      "blocks_minimum_v1": true,
      "promotion_allowed": false
    },
    {
      "fund_or_slot": "017641",
      "report_year": 2024,
      "current_blockers": [
        "strict_golden_not_configured",
        "quality_gate_block",
        "strict_golden_fund_not_covered",
        "fixture_promotion_absent"
      ],
      "decision": "defer_from_v1",
      "decision_reason": "prior controller judgment preserves replacement disposition; disclosure data gap is not baseline ready",
      "policy_status": "blocked_until_qdii_policy_or_asset_class_fitness_gate",
      "next_required_action": "future QDII diagnosis or explicit deferred-from-v1 controller judgment",
      "replacement_disposition": "replace",
      "owner": "future QDII diagnosis / replacement owner",
      "next_gate": "QDII diagnosis or explicit deferred-from-v1 gate",
      "evidence_artifacts": [
        "docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md",
        "docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md"
      ],
      "blocks_v1": true,
      "blocks_minimum_v1": false,
      "promotion_allowed": false
    }
  ]
}
```

Schema constraints：

- `decision` enum：`fix_now` / `defer_from_v1` / `needs_candidate_gate` / `needs_fixture_promotion_gate` / `blocked_until_policy`。
- `decision` must be a single primary enum value. Do not encode slash-combined values such as `defer_from_v1 / blocked_until_policy` or `defer_from_v1 / needs_candidate_gate`。
- `decision_reason` records the rationale for the primary decision.
- `policy_status` records hard-stop or policy-blocked states such as `blocked_until_qdii_policy_or_asset_class_fitness_gate` without overloading `decision`。
- `next_required_action` records future work such as `needs_candidate_gate`, `needs_taxonomy_gate`, or `strict_golden_correctness_configuration` without overloading `decision`。
- `fund_or_slot` accepts a fund code string or special identifier string. Current special identifiers are `GLOBAL` for cross-fund blockers and `FOF_SLOT` for the unresolved pure FOF coverage slot.
- `report_year` accepts an integer for fund rows and `null` for global / slot-level rows without one report year.
- `replacement_disposition` enum：`replace` / `exclude` / `null`。`replacement_disposition=replace` preserves prior replacement disposition; that entry cannot become a v1 candidate again without a new controller judgment.
- `promotion_allowed` must be `false` for every entry in this gate.
- `blocks_v1` remains `true` for full-v1 blockers unless a later controller judgment explicitly changes the full v1 scope or blocker contract.
- `blocks_minimum_v1` is part of the initial schema. Controller-proposed values for this plan are: GLOBAL fixture `true`; 004393 `true`; 004194 `true`; 006597 `true`; QDII global `false` once deferred; 017641 `false`; 096001 `false`; 040046 `false`; 019172 `false`; 021539 `false`; FOF_SLOT `false`; 110020 `false`。
- `evidence_artifacts` must include controller judgment paths, not only generated reports.

Validation for JSON-only gate：run JSON parser/self-check and schema enum check, e.g. `python -m json.tool <path>` plus a small schema/self-check script or existing JSON validation if implemented. Full ruff/pytest is not required while runtime does not consume it.

If any future gate changes runtime/preflight consumption to read this JSON, required validation escalates to full `uv run ruff check .`, full `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`, and rerun `fund-analysis golden-readiness-preflight` to prove output stability.

## Disposition Output Matrix

`promotion_allowed=false` for all rows. `decision` is a single primary enum value; policy hard stops, future candidate gates, and replacement state are recorded in metadata fields.

| fund/slot | current blockers | decision | decision_reason | policy_status | next_required_action | replacement_disposition | owner | next_gate | evidence_artifacts | blocks_v1 | blocks_minimum_v1 | promotion_allowed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| GLOBAL | `fixture_promotion_absent` | `needs_fixture_promotion_gate` | no accepted fixture promotion state manifest exists | n/a | produce fixture promotion state manifest | n/a | future fixture promotion gate | produce accepted fixture promotion state manifest | preflight JSON/MD; preflight controller judgment | true | true | false |
| GLOBAL | `qdii_replacement_hard_stop` | `blocked_until_policy` | automatic QDII probing stopped after accepted hard stop | `blocked_until_qdii_policy_or_asset_class_fitness_gate` | explicit QDII deferred-from-v1 controller judgment or future QDII diagnosis | n/a | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | consolidation post-021539 judgment; QDII evidence judgments | true | false | false |
| 004393 | `fixture_promotion_absent`; `quality_gate_warn` warning | `needs_fixture_promotion_gate` | immediate fixture candidate, but warn requires accepted residual owner | n/a | fixture promotion state manifest plus strict golden residual handling | n/a | future fixture promotion gate | fixture promotion / strict golden coverage gate | small baseline v1 judgment; source provenance rerun judgment; preflight output | true | true | false |
| 004194 | `fixture_promotion_absent`; `quality_gate_warn` warning | `needs_fixture_promotion_gate` | immediate fixture candidate, but warn requires accepted residual owner | n/a | fixture promotion state manifest plus strict golden residual handling | n/a | future fixture promotion gate | fixture promotion / strict golden coverage gate | small baseline v1 judgment; source provenance rerun judgment; preflight output | true | true | false |
| 006597 | `strict_golden_not_configured`; `fixture_promotion_absent`; `quality_gate_warn` warning | `needs_fixture_promotion_gate` | immediate fixture candidate only if bond blocker remains closed; strict golden score correctness remains unresolved | n/a | latest preflight/snapshot/score/quality validation before fixture candidacy | n/a | future fixture promotion gate + future baseline/golden preflight owner | fixture promotion / strict golden coverage gate | drawdown metric controller judgment; preflight output | true | true | false |
| 017641 | `strict_golden_not_configured`; `quality_gate_block`; `strict_golden_fund_not_covered`; `fixture_promotion_absent` | `defer_from_v1` | prior controller judgment preserves replacement disposition; disclosure data gap is not baseline ready | `blocked_until_qdii_policy_or_asset_class_fitness_gate` | future QDII diagnosis or explicit deferred-from-v1 controller judgment | `replace` | future QDII diagnosis / replacement owner | QDII diagnosis or explicit deferred-from-v1 gate | 017641 public evidence triage judgment; replacement selection judgment; source provenance rerun judgment | true | false | false |
| 096001 | `strict_golden_not_configured`; `quality_gate_block`; `strict_golden_fund_not_covered`; `fixture_promotion_absent`; `qdii_coverage_blocked` | `defer_from_v1` | candidate quality block and QDII coverage hard stop exclude it from minimum v1 | `blocked_until_qdii_policy_or_asset_class_fitness_gate` | future QDII diagnosis or taxonomy / asset-class fitness gate | n/a | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | QDII candidate evidence judgment; consolidation post-021539 judgment | true | false | false |
| 040046 | same QDII blocker set | `defer_from_v1` | candidate quality block and QDII coverage hard stop exclude it from minimum v1 | `blocked_until_qdii_policy_or_asset_class_fitness_gate` | future QDII diagnosis or taxonomy / asset-class fitness gate | n/a | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | QDII fallback 040046 judgment; consolidation post-021539 judgment | true | false | false |
| 019172 | same QDII blocker set | `defer_from_v1` | candidate quality block and QDII coverage hard stop exclude it from minimum v1 | `blocked_until_qdii_policy_or_asset_class_fitness_gate` | future QDII diagnosis or taxonomy / asset-class fitness gate | n/a | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | QDII fallback 019172 judgment; consolidation post-021539 judgment | true | false | false |
| 021539 | same QDII blocker set | `defer_from_v1` | candidate quality block and QDII coverage hard stop exclude it from minimum v1 | `blocked_until_qdii_policy_or_asset_class_fitness_gate` | future QDII diagnosis or taxonomy / asset-class fitness gate | n/a | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | QDII fallback 021539 judgment; consolidation post-021539 judgment | true | false | false |
| FOF_SLOT | `fof_taxonomy_pending`; `fof_data_gap` | `defer_from_v1` | no repository-verified pure FOF candidate; QDII-FOF cannot count as pure FOF | n/a | future pure FOF candidate gate or FOF taxonomy gate | n/a | future FOF taxonomy / pure FOF candidate gate | pure FOF repository-verified candidate gate | replacement selection judgment; consolidation post-021539 judgment; preflight output | true | false | false |
| 110020 | `strict_golden_not_configured`; `strict_golden_fund_not_covered`; `fixture_promotion_absent`; `reviewed_candidate_not_promoted`; `index_evidence_insufficient` | `defer_from_v1` | reviewed coverage candidate input is not promoted and index evidence remains insufficient | n/a | future index reviewed fact freeze / methodology / constituents evidence gate | n/a | future index evidence sufficiency gate | index reviewed fact freeze / methodology / constituents evidence gate | 110020 reviewed coverage candidate judgment; source provenance rerun judgment; preflight output | true | false | false |

## How To Keep 006597 Bond Blocker Closed

The next gates must preserve this invariant:

```text
006597 bond_risk_evidence_missing is closed iff latest accepted 006597 artifacts show:
score_applicability_issues=[],
quality_gate issues contain no reason/code bond_risk_evidence_missing,
snapshot bond_risk_contract_status="satisfied",
all seven bond risk groups satisfied,
and drawdown_stress evidence is quantitative_derived / derived_metric from FundNavRepository accumulated NAV.
```

Required controls:

- Preflight reruns must assert `bond_risk_evidence_missing` is absent from 006597 blockers and present only as resolved item when applicable.
- Fixture promotion gate must validate latest preflight, snapshot, score, and quality artifacts for 006597 before treating it as a fixture candidate. The check must confirm latest artifacts still satisfy the invariant above; if the latest run is unavailable or stale, the gate must either rerun preflight or record a controller-accepted reason for using a later reviewed equivalent artifact set.
- Fixture promotion gate must use the accepted `bond-risk-drawdown-nav-006597-2024-20260529` snapshot/score/quality artifacts or a later reviewed equivalent; no stale small-baseline artifact where 006597 was quality `block` may be used for promotion.
- Any 006597 regression in score/quality/snapshot reclassifies 006597 as `fix_now` or `needs_evidence_gate`, not fixture candidate.
- Do not accept raw-unit NAV, `requested_code_only`, mixed A/C/E/F series, or qualitative “控制回撤” text as strong drawdown evidence.

## Implementation Slices For Controller Handoff

### Slice A — Disposition Manifest Artifact

Allowed files:

- `docs/reviews/golden-readiness-residual-disposition-manifest-20260529.json`
- optional review artifact under `docs/reviews/`

Actions:

- Create tracked JSON with schema above.
- Populate rows from the disposition matrix.
- Keep `promotion_manifest=false` and every `promotion_allowed=false`.
- Do not modify runtime or preflight code.

Validation:

- JSON parse / schema self-check.
- `git diff --check`.
- No full ruff/pytest required because runtime is unchanged.

### Slice B — Controller Judgment / Control Update

Allowed files:

- controller judgment artifact under `docs/reviews/`
- minimal `docs/implementation-control.md` update if controller accepts

Actions:

- Accept or adjust this plan’s disposition matrix.
- Explicitly state whether minimum v1 excludes QDII/FOF/110020.
- Record owner/next_gate for every deferred blocker.
- Keep golden promotion forbidden.

Validation:

- `git diff --check`.
- Full ruff/pytest not required for docs/control-only change.

### Slice C — Future Fixture Promotion Gate

Allowed files to be decided by future accepted plan.

Suggested fixture promotion state manifest path convention:

`docs/reviews/fixture-promotion-state-manifest-{YYYYMMDD}.json`

This fixture promotion state manifest is not a golden promotion manifest. It may only record controller-accepted fixture state for future readiness checks; it must not set `promotion_allowed=true`, alter golden answers, alter fixture contents, change FQ0-FQ6, or modify runtime/preflight behavior unless a later implementation gate explicitly authorizes that scope.

Actions:

- Produce accepted fixture promotion state manifest for only controller-approved candidates.
- Candidate set starts as 004393, 004194, 006597.
- Before 006597 enters fixture candidacy, validate latest preflight/snapshot/score/quality artifacts and preserve the `bond_risk_evidence_missing` closed invariant.
- Treat quality `warn` as residual with owner, not ready proof.
- Rerun preflight after manifest consumption only if runtime/preflight implementation changes or fixture state is consumed by preflight.

Validation:

- If manifest is static/docs-only and not runtime-consumed: JSON schema/self-check + `git diff --check`.
- If runtime/preflight consumes manifest: full ruff, full pytest, rerun preflight.

## Validation Policy

This plan artifact is docs/evidence-only. It did not change Python code, tests, runtime behavior, FQ0-FQ6, score/quality/snapshot generation, source strategy, `FundDocumentRepository`, golden answer, fixture promotion state, Host/Agent/dayu, release/PR state, or reports/golden fixtures. Therefore full `ruff` / `pytest` is not required for this worker artifact; `git diff --check` is sufficient after writing.

If the next gate adds tracked JSON that is not runtime-consumed, require JSON parser + schema/self-check. If the next gate changes runtime/preflight consumption, require full `uv run ruff check .`, full `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`, and rerun golden-readiness preflight.

## Blocking Questions For Controller

None blocking for this planning artifact.

Controller decisions required before implementation:

- Accept minimum golden v1 scope excluding QDII / FOF / 110020, or keep them blocking v1.
- Decide whether to create the tracked disposition JSON in the next gate before fixture promotion.
- Decide whether 004393 / 004194 / 006597 are the initial fixture promotion candidate set.

## Completion Criteria

This plan is handoff-ready when:

- Review confirms every current blocker has one disposition row.
- Controller accepts or edits the minimum v1 scope.
- No row has `promotion_allowed=true`.
- QDII/FOF/110020 deferrals have owners and future gates.
- 006597 bond closure invariant is preserved.
