# Golden Readiness Preflight Plan

日期：2026-05-29

角色：planning worker only。不得 commit、push、创建 PR、merge、release、进入 gateflow、执行 implementation、修改 golden fixture 或做 baseline/golden promotion。

Gate：`golden-readiness preflight gate`

Gate classification：`heavy`

## Plan Fix Notes / Controller Disposition

- MiMo F1：Rejected。`fund_agent/fund/` 在当前仓库实际存在，且 `extraction_score.py`、`quality_gate.py`、`golden_answer.py` 均位于该包；本 plan 继续把 Agent/Fund 层实现路径放在 `fund_agent/fund/golden_readiness_preflight.py`。
- GLM F1：Closed。当前 `reports/golden-answers/golden-answer.json` 是 v1 schema，fund rows 没有 `report_year`；本 gate strict golden coverage 只实现 fund-level 覆盖。`strict_golden_year_not_covered` 与 `strict_golden_partial_coverage` 改为 reserved，等待 golden-answer schema v2 或 correctness coverage contract 后再触发。
- GLM F2 / MiMo F4：Closed。`--preflight-input path.json` 改为 production recommended path，并补充完整 JSON schema；`--fund-artifact` 仅为 shortcut，只允许 `fund_code::report_year::snapshot_path::score_path::quality_gate_path` 五项，其余状态来自 static disposition/defaults；两种输入互斥。
- MiMo F2：Closed。删除不存在的 `docs/reviews/golden-fixture-promotion-state.json` 默认示例；`fixture_promotion_state_path` 是 optional，缺省输出 `fixture_promotion_absent` blocker。
- MiMo F3 / GLM F4：Closed。static disposition manifest 增加 `schema_version`、`source_artifacts`、`accepted_as_of`，并要求写入 output JSON；补充 lifecycle exit criteria，说明何时必须开独立 machine-readable disposition manifest gate。
- GLM F3：Closed。110020 同时保留 `raw_disposition=reviewed_coverage_candidate_input_accepted` 与 `preflight_disposition=reviewed_coverage_candidate`（或 manifest 中映射到 `include_for_later_review`），保证 controller judgment 原始语义可追踪。
- GLM F5：Closed。`tests/ui/test_cli.py` 在当前仓库不存在，本 plan 改为新建该测试文件。
- Resolved item code：Closed。采用 generic `blocker_resolved`，用 `original_blocker_code="bond_risk_evidence_missing"` 与 `fund_code="006597"` 表达基金特定解除项，避免为每只基金扩散 resolved code。

## 真源简述

- `AGENTS.md` 是最高优先级执行规则真源。当前架构边界固定为 `UI -> Service -> Host -> Agent`；当前确定性生产路径仍是 UI 调 Service、Service 调 `fund_agent/fund` Agent 层基金能力的过渡实现。显式参数不得塞进 `extra_payload`；年报访问必须经 `FundDocumentRepository`；不得削弱 FQ0-FQ6；baseline/golden promotion 属高影响 gate。
- `docs/design.md` 当前事实：本项目是确定性 MVP 主链路，`extraction-snapshot`、`extraction-score`、`quality-gate`、strict `golden-answer.json` 都是当前可用质量链路；Host/Agent/dayu runtime 尚未接入，不能为本 gate 新建或绕过边界。
- `docs/implementation-control.md` 当前 Startup Packet：`drawdown_stress NAV-derived metric implementation gate` 已 accepted local validation；006597/2024 的 `credit_risk`、`redemption_share_pressure`、`drawdown_stress` false negative/residual 已通过真实 snapshot/score/quality gate 验证解除；golden promotion 未进入；下一步是非 mutating readiness/residual reconciliation。
- 最新 drawdown_stress NAV-derived metric artifacts：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md`、implementation evidence、GLM/MiMo aggregate deepreviews 均确认 006597/A 2024 使用 `FundNavRepository.load_nav_series()` 的 CSRC EID `accumulated_nav` 生成 max drawdown；latest snapshot `bond_risk_contract_status="satisfied"`，score `score_applicability_issues=[]`，quality gate 无 `bond_risk_evidence_missing`，未修改 score/quality/golden 语义。
- 006597 最新 artifacts：`reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl`、`reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json`、`reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json`。当前 bond blocker 已解除，不应作为 blocker 列出；remaining quality `warn` 只能作为 warning，不证明 ready。
- source provenance / coverage disposition artifacts：`release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md` 接受 110020 source provenance complete/eligible + quality warn + `not_promoted`，017641 complete/eligible + quality block + `not_promoted`；`release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md` 接受 110020 仅为 reviewed coverage candidate input，methodology/constituents/strict golden/reviewed fact freeze 仍残留；`release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md` 接受 QDII hard stop，`096001`/`040046`/`019172`/`021539` 均 provenance eligible、quality block、not promoted，QDII coverage blocked；FOF 为 `data_gap` / `taxonomy_pending`，QDII-FOF 不能算 pure FOF。

## 目标

实现或运行一个 `golden-readiness preflight` 机制，聚合 baseline/golden v1 promotion 所需 blocker 状态，输出：

- 机器可读 `JSON`：全局 pass/block、per-fund readiness、blocker code/severity、owner/next gate、证据 artifact 链接。
- 人类可读 `Markdown`：当前不能 promotion 的原因、已解除项、每个 blocker 的 owner 和下一步 gate。

本 gate 不解除所有 blocker，不做 golden promotion，不修改 golden fixture，不改变 FQ0-FQ6，只把当前状态变成可执行判定。

## 推荐实现范围

优先实现一个只读 preflight 模块和薄封装入口：

- Agent/Fund 层：新增 `fund_agent/fund/golden_readiness_preflight.py`
- Service 层：新增 `fund_agent/services/golden_readiness_preflight_service.py`
- Service exports：更新 `fund_agent/services/__init__.py`
- UI 层：在 `fund_agent/ui/cli.py` 新增 `golden-readiness-preflight` 命令
- Tests：新增 `tests/fund/test_golden_readiness_preflight.py`、`tests/ui/test_cli.py` 入口测试；必要时更新 `tests/README.md`
- Docs：若 CLI 用户入口新增，更新根 `README.md` 的 CLI 命令索引；若 Fund 包公开能力新增，更新 `fund_agent/fund/README.md`；若 tests 目录新增约定，更新 `tests/README.md`

不得新增 `fund_agent/host`、`fund_agent/agent`、dayu 依赖、release readiness、PR/push/merge 逻辑。

## 输入 Contract

CLI/Service request 必须显式声明参数，不使用 `extra_payload`：

- `source_csv: Path`，默认 `docs/code_20260519.csv`。用于校验 selected pool 来源、基金代码/类别基本身份。
- `selected_pool_path: Path | None`。可为当前 `extraction-score` 产出的 `golden_set.json`；为空时从 `source_csv` 和内置当前 disposition manifest 构造候选池。
- `preflight_input_path: Path | None`。Production recommended path。指向完整机器可读 preflight input JSON；如果提供该参数，CLI 不再接受 `--fund-artifact`、`--selected-pool-path`、`--coverage-disposition-path`、`--fixture-promotion-state-path` 等逐项输入，避免双真源。
- `fund_artifacts: tuple[FundArtifactInput, ...]`。每只基金显式传入：
  - `fund_code: str`
  - `report_year: int`
  - `snapshot_path: Path | None`
  - `score_path: Path | None`
  - `quality_gate_path: Path | None`
  - `score_golden_set_path: Path | None`
  - `promotion_state: Literal["not_promoted","promoted_fixture","unknown"]`
  - `raw_disposition: str | None`
  - `preflight_disposition: Literal["reviewed_coverage_candidate","include_for_later_review","replace","needs_taxonomy_gate","needs_evidence_gate","blocked","deferred","unknown"]`
  - `coverage_owner: str`
  - `next_gate: str`
  - `evidence_artifacts: tuple[Path, ...]`
- `coverage_disposition_path: Path | None`。推荐读取一个机器可读 disposition manifest；本 gate 若尚无 manifest，应先在代码内提供静态默认 manifest，内容必须逐条链接已接受 controller judgment artifacts。
- `golden_answer_path: Path | None`，默认 `reports/golden-answers/golden-answer.json`。用于 strict golden fund-level coverage 检查；缺失或不可读必须 fail-closed。当前 v1 JSON 不含 report_year，不能做 year-level coverage 判定。
- `fixture_promotion_state_path: Path | None`。Optional JSON manifest；没有默认文件路径。若缺失，所有候选默认 `promotion_state="not_promoted"` 并输出 `fixture_promotion_absent` blocker。
- `output_dir: Path`，默认 `reports/golden-readiness-preflight/<run_id>/`
- `run_id: str`，显式传入或由 CLI 生成 `golden-readiness-preflight-YYYYMMDD`，不从 extra payload 派生。

`--preflight-input` JSON schema：

```json
{
  "schema_version": "fund-agent.golden-readiness-preflight.input.v1",
  "run_id": "golden-readiness-preflight-20260529",
  "source_csv": "docs/code_20260519.csv",
  "selected_pool_path": null,
  "golden_answer_path": "reports/golden-answers/golden-answer.json",
  "fixture_promotion_state_path": null,
  "coverage_disposition_path": null,
  "output_dir": "reports/golden-readiness-preflight/golden-readiness-preflight-20260529",
  "fund_artifacts": [
    {
      "fund_code": "006597",
      "report_year": 2024,
      "snapshot_path": "reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl",
      "score_path": "reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json",
      "quality_gate_path": "reports/quality-gate-runs/bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json",
      "score_golden_set_path": null,
      "promotion_state": "not_promoted",
      "raw_disposition": "bond_risk_evidence_resolved_not_promoted",
      "preflight_disposition": "include_for_later_review",
      "coverage_owner": "future baseline/golden preflight owner",
      "next_gate": "fixture promotion / strict golden coverage gate",
      "evidence_artifacts": [
        "docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-20260529.md"
      ]
    },
    {
      "fund_code": "110020",
      "report_year": 2024,
      "snapshot_path": "reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/snapshot.jsonl",
      "score_path": "reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/score.json",
      "quality_gate_path": "reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527/quality_gate.json",
      "score_golden_set_path": null,
      "promotion_state": "not_promoted",
      "raw_disposition": "reviewed_coverage_candidate_input_accepted",
      "preflight_disposition": "reviewed_coverage_candidate",
      "coverage_owner": "future index evidence sufficiency gate",
      "next_gate": "index reviewed fact freeze / methodology / constituents evidence gate",
      "evidence_artifacts": [
        "docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md"
      ]
    }
  ]
}
```

Schema validation requirements：

- 顶层必须是 JSON object，`schema_version` 必须精确匹配。
- `fund_artifacts` 必须是数组；每项必须有 `fund_code`、`report_year`、`snapshot_path`、`score_path`、`quality_gate_path` 字段，允许路径值为 `null` 以触发 fail-closed blocker。
- `raw_disposition` 是 controller judgment 原始 terminal/disposition 字符串；`preflight_disposition` 是 preflight enum 映射。二者都写入输出 JSON。
- `evidence_artifacts` 必须是字符串数组；禁止自由 dict 或未声明字段。发现未知字段时抛 `ValueError`，防止形成隐式 `extra_payload`。

输入读取规则：

- `snapshot.jsonl` 只读字段：`fund_code`、`report_year`、`fund_name`、`app_category`、`classified_fund_type`、source provenance fields、`bond_risk_contract_status`、bond risk groups。
- `score.json` 只读字段：`fund_scores`、`fund_quality`、`score_applicability_issues`、`correctness`、`source_csv`、`snapshot_path`。
- `quality_gate.json` 只读字段：`status`、`issues`、`rule_results`。
- strict golden answer JSON v1 只读 `funds[].fund_code` 与 `funds[].records[]`，不得改写。当前 v1 不读取也不推断 `report_year`；year-level coverage 是 reserved。
- coverage disposition 必须来自 accepted controller judgment 对应 manifest 或静态映射，禁止从自然语言文档即兴 regex 推断。若无法可靠归因，输出 Blocking Questions，并把相关 slot 置为 `blocked` 或 `not_evaluated`。

## 输出 Contract

输出目录：

- JSON：`reports/golden-readiness-preflight/<run_id>/golden_readiness_preflight.json`
- Markdown：`reports/golden-readiness-preflight/<run_id>/golden_readiness_preflight.md`

JSON 顶层 schema：

```json
{
  "schema_version": "fund-agent.golden-readiness-preflight.v1",
  "run_id": "golden-readiness-preflight-20260529",
  "generated_at": "ISO-8601",
  "source_csv": "docs/code_20260519.csv",
  "golden_answer_path": "reports/golden-answers/golden-answer.json",
  "static_disposition_manifest": {
    "schema_version": "fund-agent.coverage-disposition.static-current.v1",
    "accepted_as_of": "2026-05-29",
    "source_artifacts": []
  },
  "overall_status": "block",
  "ready_count": 0,
  "blocked_count": 0,
  "deferred_count": 0,
  "not_evaluated_count": 0,
  "rows": [],
  "global_blockers": [],
  "resolved_items": [],
  "blocking_questions": []
}
```

Per-fund readiness row：

```json
{
  "fund_code": "006597",
  "report_year": 2024,
  "fund_name": "国泰利享中短债债券A",
  "app_category": "国内债券类",
  "classified_fund_type": "bond_fund",
  "readiness": "deferred_with_owner",
  "promotion_state": "not_promoted",
  "source_provenance_status": "not_applicable",
  "fallback_eligibility": "not_applicable",
  "quality_gate_status": "warn",
  "strict_golden_coverage": "fund_not_covered",
  "fixture_promotion_state": "absent",
  "raw_disposition": "bond_risk_evidence_resolved_not_promoted",
  "preflight_disposition": "include_for_later_review",
  "blockers": [],
  "warnings": [],
  "resolved_items": [
    {
      "code": "blocker_resolved",
      "original_blocker_code": "bond_risk_evidence_missing",
      "fund_code": "006597",
      "message": "006597 bond_risk_evidence_missing resolved by accepted NAV-derived drawdown metric gate."
    }
  ],
  "owner": "future baseline/golden preflight owner",
  "next_gate": "fixture promotion / strict golden coverage gate",
  "evidence_artifacts": []
}
```

Blocker row：

```json
{
  "code": "qdii_coverage_blocked",
  "severity": "block",
  "scope": "slot",
  "fund_code": "096001",
  "message": "QDII replacement hard stop accepted; candidate quality block after eligible provenance.",
  "owner": "future QDII diagnosis or taxonomy / asset-class fitness gate",
  "next_gate": "QDII diagnosis or explicit QDII deferred-from-v1 disposition gate",
  "evidence_artifacts": [
    "docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md"
  ]
}
```

Allowed readiness enum：

- `ready`：所有 required inputs present；source provenance eligible/not_applicable；quality gate `pass`；strict golden fund-level coverage `covered`；fixture promotion state accepted; no blocker。
- `blocked`：存在 hard blocker，例如 QDII coverage blocked、quality `block`、baseline_blocking issue、source provenance unknown/ineligible、fixture absent 且 v1 要求 promotion、strict golden JSON 缺失或 fund-level 未覆盖。
- `deferred_with_owner`：当前不能 promotion，但已有 accepted disposition 明确 owner 和 next gate，例如 FOF taxonomy pending、110020 reviewed candidate not promoted。
- `not_evaluated`：缺少必要输入或 disposition taxonomy 不可归因；不能 ready。

全局 `overall_status`：

- 只允许 `pass` 或 `block`。
- 任何 row 为 `blocked` / `not_evaluated`，或存在 global blocker，则 `overall_status="block"`。
- `deferred_with_owner` 对 v1 是否 block 由 disposition manifest 明确声明：若 `blocks_v1=true`，全局 block；若已接受 deferred-from-v1 且 owner/revisit condition 完整，可不阻断 v1，但本 gate 当前默认 FOF/QDII/110020 均 `blocks_v1=true`，直到 controller 明确解除。

Markdown 必须包含：

- 真源摘要。
- Overall verdict：`BLOCK` 或 `PASS`。
- “已解除”列表：必须列 `blocker_resolved / original_blocker_code=bond_risk_evidence_missing / fund_code=006597`，且说明不列 blocker。
- Per-fund / per-slot readiness 表。
- Blockers by severity 表。
- Owner / next gate 表。
- Missing input / Blocking Questions 表。
- Non-goals and guardrails。

## Blocker 聚合规则

必须实现的 blocker codes：

- `missing_input_artifact`：required source/snapshot/score/quality/disposition/golden/fixture artifact 缺失；severity `block`；readiness `not_evaluated`。
- `source_provenance_unknown`：fallback_used 但 public provenance 无 `primary_failure_category` 或 `fallback_eligibility=unknown`；severity `block`。
- `source_provenance_ineligible`：fallback_used 且 primary failure category 为 `schema_drift`、`identity_mismatch`、`integrity_error` 或 fallback eligibility 非 eligible；severity `block`。
- `source_provenance_eligible_fallback`：eligible fallback 只解除 source blocker；不是 ready 证明；作为 warning/resolved source item 记录。
- `quality_gate_block`：quality gate `status="block"`；severity `block`。
- `quality_gate_warn`：quality gate `status="warn"`；severity `warn`；不能证明 ready。
- `score_applicability_baseline_blocking`：任一 `score_applicability_issues[].baseline_blocking=true`；severity `block`。
- `blocker_resolved`：用于已解除 blocker 的通用 resolved item；必须携带 `original_blocker_code`、`fund_code`、`evidence_artifacts`。006597 最新 run 中 `score_applicability_issues=[]` 且无 quality `bond_risk_evidence_missing` 时，输出 `code="blocker_resolved"`、`original_blocker_code="bond_risk_evidence_missing"`、`fund_code="006597"`，放入 `resolved_items`，不得列入 blockers。
- `qdii_coverage_blocked`：QDII hard stop 后 `096001`/`040046`/`019172`/`021539` 均 quality block and not_promoted；severity `block`；slot readiness `blocked`。
- `qdii_replacement_hard_stop`：禁止继续自动 QDII probing；severity `block` 或 global guardrail。
- `fof_taxonomy_pending`：FOF pure candidate 缺失，QDII-FOF 不可计为 pure FOF；severity `block` 或 `deferred_with_owner` 且 `blocks_v1=true`。
- `fof_data_gap`：缺 pure FOF repository-verified candidate；severity `block`。
- `reviewed_candidate_not_promoted`：110020 reviewed candidate input accepted but `promotion_disposition=not_promoted`；severity `block` unless a later controller accepts fixture promotion.
- `index_evidence_insufficient`：110020 methodology/constituents/reviewed fact freeze insufficient；severity `block` / `deferred_with_owner`。
- `strict_golden_not_configured`：score correctness unavailable/not_configured 或 no golden path；severity `block` for readiness preflight。
- `strict_golden_fund_not_covered`：candidate fund absent from strict golden answer v1；severity `block`。
- `strict_golden_year_not_covered`：reserved pending golden-answer schema v2；本 gate 不实现、不触发。
- `strict_golden_partial_coverage`：reserved pending golden-answer schema v2 或 future correctness coverage contract；本 gate 不实现、不触发。
- `fixture_promotion_absent`：no accepted fixture promotion manifest/row; severity `block`。
- `fixture_promotion_unknown`：manifest exists but row unknown/inconsistent; severity `block`。

Current expected aggregation:

- 006597：bond blocker resolved；do not list `bond_risk_evidence_missing` as blocker. Still not ready because strict golden coverage and fixture promotion are not accepted; quality warn remains warning only.
- QDII：coverage blocked after hard stop; preserve `096001`/`040046`/`019172`/`021539` as provenance eligible, quality `block`, `not_promoted`; do not run more QDII evidence.
- FOF：`data_gap` / `taxonomy_pending`; QDII-FOF must not count as pure FOF.
- 110020：reviewed coverage candidate only; `not_promoted`; output must preserve `raw_disposition="reviewed_coverage_candidate_input_accepted"` and mapped `preflight_disposition="reviewed_coverage_candidate"` or `include_for_later_review`; methodology/constituents and strict golden/reviewed fact freeze residuals remain.
- Source provenance：eligible fallback removes source unknown blocker only; ineligible/unknown/missing metadata blocks; eligible fallback does not prove ready.
- Quality gate：`block` blocks; `warn` only warns and cannot certify ready.
- Strict golden answer：absence or missing fund blocks readiness even if current quality gate records FQ0 as info. Year-level and partial-field coverage blockers are reserved until golden-answer schema v2 / correctness coverage contract.
- Fixture promotion：absence of accepted promotion state blocks promotion readiness.

## Fail-Closed 规则

- 缺任一 required input artifact，row 不得 `ready`。
- `score_applicability_issues[].baseline_blocking=true` 必须 block。
- coverage disposition 未解除，或 disposition 不可机器归因，必须 block/defer with owner，且默认 `blocks_v1=true`。
- quality gate `block` 必须 block。
- quality gate `warn` 只能进入 warning；不得作为 ready 证据。
- source provenance missing/unknown/ineligible 必须 block；eligible fallback 只消除 source blocker。
- strict golden answer v1 fund-level coverage 不足必须 block；不得沿用 FQ0 info 语义把 promotion readiness 放行。Year-level / partial coverage 本 gate 不触发。
- fixture promotion state 缺失必须 block。
- 若 material blocker taxonomy 无法可靠归因，必须输出 `blocking_questions[]`，并把相关 row 置为 `not_evaluated` 或 `blocked`。

## 代码设计

### Agent/Fund 层模块

新增 `fund_agent/fund/golden_readiness_preflight.py`：

- 模块中文 docstring：说明本模块是 Agent 层基金质量 readiness 聚合能力，只读 snapshot/score/quality/golden/disposition artifacts，不读取 PDF/cache，不调用来源 helper，不执行 promotion。引用模板第 0-7 章和 FQ0-FQ6 promotion readiness 边界。
- Dataclasses / Literals：
  - `ReadinessStatus = Literal["ready","blocked","deferred_with_owner","not_evaluated"]`
  - `PreflightOverallStatus = Literal["pass","block"]`
  - `BlockerSeverity = Literal["block","warn","info"]`
  - `PromotionState = Literal["not_promoted","promoted_fixture","unknown"]`
  - `GoldenReadinessInput`
  - `FundArtifactInput`
  - `ReadinessBlocker`
  - `ReadinessWarning`
  - `ResolvedReadinessItem`
  - `FundReadinessRow`
  - `GoldenReadinessPreflightResult`
- Public API：
  - `run_golden_readiness_preflight(*, source_csv: Path, output_dir: Path, run_id: str, fund_artifacts: Sequence[FundArtifactInput], golden_answer_path: Path | None, fixture_promotion_state_path: Path | None, coverage_disposition_path: Path | None, preflight_input_path: Path | None = None) -> GoldenReadinessPreflightResult`
  - `load_default_current_disposition_manifest() -> CoverageDispositionManifest`
- Private helpers：
  - `_load_json_object(path: Path) -> dict[str, object]`
  - `_load_snapshot_rows(path: Path) -> tuple[Mapping[str, object], ...]`
  - `_derive_source_provenance_state(snapshot_rows) -> SourceProvenanceSummary`
  - `_derive_score_blockers(score_payload) -> tuple[ReadinessBlocker, ...]`
  - `_derive_quality_blockers(quality_payload) -> tuple[ReadinessBlocker, ...]`
  - `_derive_strict_golden_coverage(...)`
  - `_derive_fixture_promotion_state(...)`
  - `_derive_coverage_disposition_blockers(...)`
  - `_aggregate_readiness(row_inputs) -> ReadinessStatus`
  - `_json_payload(result) -> dict[str, object]`
  - `_markdown_payload(result) -> str`

Default current disposition manifest can be code-defined in this module for this gate, but must be explicit and link artifacts:

- manifest object must include `schema_version="fund-agent.coverage-disposition.static-current.v1"`、`accepted_as_of="2026-05-29"`、`source_artifacts` and `entries`。
- active `004393` 2024: `raw_disposition="evaluated_carry_forward_candidate"`、`preflight_disposition="include_for_later_review"`、`not_promoted`, owner `future baseline preflight owner`, blocks_v1 true until fixture/golden promotion accepted.
- enhanced-index `004194` 2024: `raw_disposition="evaluated_carry_forward_candidate"`、`preflight_disposition="include_for_later_review"`、same carry-forward, blocks_v1 true until fixture/golden promotion accepted.
- index `110020` 2024: `raw_disposition="reviewed_coverage_candidate_input_accepted"`、`preflight_disposition="reviewed_coverage_candidate"`、`not_promoted`, owner future index evidence sufficiency gate, blocks_v1 true.
- bond `006597` 2024: `raw_disposition="bond_risk_evidence_resolved_not_promoted"`、`preflight_disposition="include_for_later_review"`；bond evidence gate resolved; owner fixture/golden preflight owner; blocks_v1 true only for strict golden/fixture/quality warnings as applicable, not for bond risk.
- QDII slot: candidates `096001`/`040046`/`019172`/`021539`, `raw_disposition="quality_blocked_after_provenance_hard_stop"`、`preflight_disposition="blocked"`、owner future QDII diagnosis/taxonomy, blocks_v1 true.
- FOF slot: `raw_disposition="data_gap_taxonomy_pending"`、`preflight_disposition="needs_taxonomy_gate"`、owner future FOF taxonomy / pure FOF candidate gate, blocks_v1 true.

注意：该 manifest 是 current accepted disposition state，不是 promotion state。

Static manifest lifecycle exit criteria：

- 任一 controller judgment 改变 coverage disposition、owner、revisit condition、blocks_v1 或 promotion disposition。
- 新 fund 加入候选池，或已有 fund 从候选池移除。
- fixture promotion state 发生变更。
- 需要同时维护 3 个以上条目或跨多 gate 复用 disposition 数据。
- 满足任一条件时，停止扩展代码内 static manifest，开独立 `machine-readable disposition manifest gate`，产出 tracked JSON manifest 后再让 preflight 消费。

Preflight JSON 输出必须把当前使用的 static manifest 原样写入 `static_disposition_manifest`，包括 `schema_version`、`accepted_as_of`、`source_artifacts`、`entries`，以便 controller review 追踪。

### Service 层

新增 `fund_agent/services/golden_readiness_preflight_service.py`：

- `GoldenReadinessPreflightRequest` 显式声明 `source_csv`、`output_dir`、`run_id`、`fund_artifacts`、`golden_answer_path`、`fixture_promotion_state_path`、`coverage_disposition_path`、`preflight_input_path`。
- `GoldenReadinessPreflightService.run(request)` 只做路径后缀/目录校验，然后调用 Fund 层 API。
- 若 `preflight_input_path` 非空，则不得同时传入 shortcut `fund_artifacts` 或其它逐项 manifest 参数；冲突抛 `ValueError`，CLI 转 exit 2。
- 不读取 prompt manifest，不管理 session/run，不接 Host/Agent/dayu。

更新 `fund_agent/services/__init__.py` export。

### CLI 入口

在 `fund_agent/ui/cli.py` 新增：

```text
fund-analysis golden-readiness-preflight \
  --run-id golden-readiness-preflight-20260529 \
  --source-csv docs/code_20260519.csv \
  --golden-answer-path reports/golden-answers/golden-answer.json \
  --output-dir reports/golden-readiness-preflight/golden-readiness-preflight-20260529 \
  --fund-artifact 006597::2024::reports/extraction-snapshots/.../snapshot.jsonl::reports/scoring-runs/.../score.json::reports/quality-gate-runs/.../quality_gate.json
```

Production recommended path:

```text
fund-analysis golden-readiness-preflight \
  --preflight-input docs/reviews/golden-readiness-preflight-input-20260529.json
```

`--preflight-input path.json` 使用上文完整 JSON schema，不允许 free-form extra payload。若同时提供 `--preflight-input` 和单项参数，Service 校验冲突并退出 2。

`--fund-artifact` 只是 shortcut，格式必须为：

```text
fund_code::report_year::snapshot_path::score_path::quality_gate_path
```

解析要求：

- 分隔符固定为 `::`。
- split 后字段数必须精确等于 5，否则 CLI exit 2。
- `fund_code` 必须是 6 位数字；`report_year` 必须是整数。
- 只填这五项；`score_golden_set_path`、promotion state、raw/preflight disposition、owner、next gate、evidence artifacts 均来自 static disposition manifest/defaults。
- shortcut 不支持路径中包含 `::`；如有该需求必须使用 `--preflight-input` JSON。

CLI stdout 只打印：

- `preflight_json: <path>`
- `preflight_md: <path>`
- `overall_status: block|pass`

退出码：

- `0`：preflight 成功生成，即使 `overall_status=block`。
- `1`：IO/JSON/schema 失败。
- `2`：CLI 参数非法。

## 测试计划

新增 `tests/fund/test_golden_readiness_preflight.py`：

- `test_preflight_blocks_missing_required_artifact`：缺 score/quality/golden/fixture 不得 ready，输出 `missing_input_artifact`。
- `test_preflight_marks_006597_bond_blocker_resolved_not_blocker`：给定 latest 006597 score `score_applicability_issues=[]` 和 quality no `bond_risk_evidence_missing`，结果含 resolved item `code="blocker_resolved"`、`original_blocker_code="bond_risk_evidence_missing"`、`fund_code="006597"`，blockers 不含 `bond_risk_evidence_missing`。
- `test_preflight_blocks_baseline_blocking_score_issue`：`baseline_blocking=true` 必须输出 `score_applicability_baseline_blocking`。
- `test_preflight_blocks_quality_block_but_warn_only_warning`：quality `block` -> blocked；quality `warn` -> warning，不得 ready 除非其它条件也满足。
- `test_preflight_blocks_source_provenance_unknown_or_ineligible`：unknown/ineligible fallback fail-closed。
- `test_preflight_records_eligible_fallback_as_non_ready_evidence`：eligible fallback 只移除 source blocker，不产生 ready。
- `test_preflight_blocks_qdii_hard_stop`：四个 QDII rows provenance eligible + quality block + not_promoted -> global `qdii_coverage_blocked`。
- `test_preflight_blocks_fof_taxonomy_pending_and_rejects_qdii_fof_as_pure_fof`。
- `test_preflight_preserves_110020_raw_disposition_and_blocks_not_promoted`：输出保留 `raw_disposition="reviewed_coverage_candidate_input_accepted"`，并映射 `preflight_disposition="reviewed_coverage_candidate"`。
- `test_preflight_blocks_strict_golden_absence_and_fund_miss`。
- `test_preflight_reserves_strict_golden_year_and_partial_coverage_codes`：确认 v1 不触发 `strict_golden_year_not_covered` / `strict_golden_partial_coverage`。
- `test_preflight_blocks_fixture_promotion_absence`。
- `test_preflight_outputs_static_disposition_manifest_metadata`：JSON 包含 `schema_version`、`source_artifacts`、`accepted_as_of`。
- `test_preflight_input_schema_rejects_unknown_fields`。
- `test_preflight_json_schema_and_markdown_paths_written`。

新增 `tests/ui/test_cli.py`：

- CLI 参数校验。
- `golden-readiness-preflight` 输出路径和 overall status。
- `--preflight-input` 与显式参数冲突退出 2。
- `--fund-artifact` 使用 `::` 分隔且字段数必须为 5；错误字段数退出 2。

若新增 README 说明，更新 `tests/README.md` 记录 preflight tests 分层。

## 验证命令

实现 worker 完成后运行：

```bash
uv run ruff check fund_agent/fund/golden_readiness_preflight.py fund_agent/services/golden_readiness_preflight_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/fund/test_golden_readiness_preflight.py tests/ui/test_cli.py
```

```bash
uv run pytest tests/fund/test_golden_readiness_preflight.py tests/ui/test_cli.py -q
```

若 README 或公共 CLI 入口更新，运行：

```bash
uv run pytest tests/fund/test_golden_readiness_preflight.py tests/ui/test_cli.py tests/test_repo_hygiene.py -q
```

建议最终 smoke：

```bash
uv run fund-analysis golden-readiness-preflight \
  --run-id golden-readiness-preflight-20260529 \
  --source-csv docs/code_20260519.csv \
  --golden-answer-path reports/golden-answers/golden-answer.json \
  --output-dir reports/golden-readiness-preflight/golden-readiness-preflight-20260529
```

预期 stdout：

```text
preflight_json: reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json
preflight_md: reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.md
overall_status: block
```

若实现触及更多共享逻辑，升级到：

```bash
uv run ruff check .
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

## Docs / Control 更新

实现接受后才更新：

- `fund_agent/fund/README.md`：增加 golden readiness preflight 作为 Fund 层只读聚合能力，强调不 promotion。
- 根 `README.md`：如果 CLI 成为用户可见命令，增加命令示例和输出路径。
- `tests/README.md`：增加 preflight 测试分层。
- `docs/implementation-control.md`：controller acceptance 后只做短引用，记录 preflight report JSON/Markdown path、overall status、remaining owner，不追加长日志。

本 planning worker 不更新 control doc。

## Stop Conditions

实现或运行时遇到以下情况必须停止并输出 blocker，不得补证或继续 probing：

- 任何输入 artifact 缺失、JSON 非 object、JSONL 行非法。
- source provenance fallback category 为 `schema_drift`、`identity_mismatch`、`integrity_error`，或 eligibility 不可判定。
- QDII 需要新候选、新 evidence run、或继续 automatic probing。
- FOF 只能通过 QDII-FOF 或未验证候选满足。
- 需要修改 score/quality gate 规则、FQ0-FQ6 severity、baseline_blocking 语义。
- 需要修改 golden answer JSON、golden fixtures、fixture promotion state，或把 reports 输出提升为 tracked fixture。
- 需要实现 year-level 或 partial-field strict golden readiness；当前 v1 golden-answer schema 不支持，必须另开 schema v2 / correctness coverage gate。
- 需要直接读取 PDF/cache/source helper，绕过 `FundDocumentRepository`。
- 需要 Host/Agent/dayu/release readiness/PR/push/merge。
- material blocker taxonomy 无法可靠归因；此时写入 `blocking_questions[]`，row 置为 `not_evaluated` 或 `blocked`。

## Blocking Questions

若实现前没有机器可读 fixture promotion manifest，应默认输出 `fixture_promotion_absent` blocker；不要向用户索要后再假装 ready。

若 coverage disposition manifest 仍只能从 Markdown controller judgments 读取，短期可用代码内 static accepted-current-state manifest；中期应另开 gate 把 accepted disposition 转成机器可读 manifest。当前 preflight 不应通过 ad hoc 文档 regex 判定 owner 和 blocker。

若 v1 是否允许 defer FOF/QDII 尚未有 controller accepted decision，本 gate 默认 `blocks_v1=true`，overall status 必须 `block`。

当前 strict golden answer v1 不含 `report_year`，所以本 gate 只能回答“fund 是否存在于 strict golden answer”。若 controller 要求 same-year 或 partial-field promotion readiness，必须先升级 golden-answer schema 或提供 accepted correctness coverage manifest。
