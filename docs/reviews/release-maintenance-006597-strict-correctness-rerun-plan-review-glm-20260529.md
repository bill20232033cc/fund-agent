# 006597 Strict Correctness Rerun / Same-Fund Unavailable Field Review — Plan Review (GLM)

日期：2026-05-30

角色：AgentGLM 独立 plan reviewer。本文是 review artifact，不启动 gateflow / phaseflow，不修改代码、文档、报告、manifest、golden file 或 control doc，不 stage、不 commit、不 push、不 PR、不 merge、不 release、不 promote、不 rerun。

Review target: `docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-20260529.md`

## Verification Criteria Results

### 1. Plan 是否 006597-specific，避免混用旧 multi-fund follow-up state

**Verdict: PASS**

Evidence:
- Plan title、Goal、所有 evidence claims、rerun command、output paths 均明确以 `006597 / 2024` 为唯一 scope。
- Plan §Existing Untracked Follow-Up Artifacts（lines 66-83）列出 7 个旧 untracked artifacts，明确处置为 read-only / unaccepted workspace evidence，不得 stage / delete / rename / edit / silently promote。
- Plan 明确要求 "preferred implementation path is a new 006597-specific evidence artifact and a new 006597-specific rerun output path to avoid mixing old multi-fund follow-up state"（line 83）。
- Non-Goals 排除 `004393` / `004194`（line 20）。
- Stop conditions 明确禁止 "old untracked follow-up artifacts are staged, deleted, or accepted without review/controller judgment"（line 256）。

### 2. Rerun command 是否使用 golden-answer.json，输出到新 006597-specific path

**Verdict: PASS**

Evidence:
- Rerun command（lines 90-95）使用 `--golden-answer-path reports/golden-answers/golden-answer.json`。
- Output path `reports/scoring-runs/strict-correctness-rerun-006597-2024-20260529/` 是新的 006597-specific 目录。
- 确认该输出路径目前不存在（`ls` 返回 exit code 1）。
- Quality gate output 路径 `reports/quality-gate-runs/strict-correctness-rerun-006597-2024-20260529/` 同样是新的 006597-specific 目录。
- 两者均不覆盖 accepted reports（`bond-risk-drawdown-nav-006597-2024-20260529` 路径不变）。
- Plan line 116: "No golden answer, fixture, manifest, snapshot, or runtime file may be edited to make these commands pass."

### 3. 是否清楚区分 cross-fund unavailable 和 same-fund 006597 unavailable

**Verdict: PASS**

Evidence:
- Plan line 128: "Unavailable rows | Exact list and count; distinguish same-fund 006597 unavailable from cross-fund unavailable in the 150-row corpus"。
- Plan lines 156-163: If Same-Fund Unavailable Exists 规则明确只关注 `fund_code=="006597"` 的 `status=unavailable`。
- Plan line 162: "Do not treat cross-fund unavailable rows as 006597 failure."
- Plan result handling 正确分类：cross-fund unavailable 不影响 decision，same-fund unavailable 触发 `blocked_pending_same_fund_unavailable_field_review`。

### 4. 是否保持 fixture_state=absent / promotion_allowed=false / promotion_manifest=false

**Verdict: PASS**

Evidence:
- Plan line 14: "保持 `fixture_state=absent`、`promotion_allowed=false`，直到 separate fixture promotion gate explicitly accepts changes。"
- Clean pass handling（lines 175-179）: decision 只能是 `promotion_prep_candidate`，不是 `promoted`；`promotion_allowed` remains `false`；`fixture_state` remains `absent`。
- Fixture manifest 验证确认当前值：`fixture_state=absent`、`promotion_allowed=false`、`blocks_minimum_v1=true`、`blocks_v1=true`。
- Preflight 确认：`fixture_promotion_state=absent`。
- Stop condition（line 255）: "clean pass is described as `promoted`, `promotion_allowed=true`, or fixture state change" 触发 stop。

### 5. 是否禁止改 golden/fixtures/JSON/runtime/score/quality/FQ0-FQ6/manifests/preflight/control doc

**Verdict: PASS**

Evidence:
- Non-Goals（lines 18-23）明确禁止修改 production code、tests、scripts、runtime、score semantics、quality gate / FQ0-FQ6、snapshot projection、renderer、Service/UI、Host/Agent/dayu。
- 禁止修改 `reports/golden-answers/golden-answer.json`、golden fixtures、fixture manifest、residual manifest、preflight outputs、README、`docs/design.md`、`docs/implementation-control.md`。
- 禁止使用 `extra_payload` 隐藏显式参数。
- Manual verification ledger（line 198）: "`prohibited_action` must say no guessing fixes, no golden edit, no runtime edit inside this gate."
- Mismatch handling（lines 150-154）: "Do not edit golden answer or extractor."
- Validation matrix（lines 217-228）包含 golden/fixture/manifest/runtime diff 检查。
- Line 116: "No golden answer, fixture, manifest, snapshot, or runtime file may be edited to make these commands pass."

### 6. 是否包含 mismatch/unavailable field-level ledger 格式、owner、next_gate、blocks_minimum_v1/full_v1

**Verdict: PASS**

Evidence:
- Plan §Manual Verification Ledger Format（lines 182-199）定义完整字段级台账格式：`fund_code`, `report_year`, `field_name`, `sub_field`, `priority`, `machine_status`, `expected_value_summary`, `actual_value_summary`, `source_anchor`, `machine_reason`, `manual_question`, `owner`, `next_gate`, `blocks_minimum_v1`, `blocks_full_v1`, `prohibited_action`。
- `priority` 必须使用 `docs/design.md` §7.3。
- `owner` 必须命名 future gate owner，不是个人。
- `next_gate` 限定为四个选项（lines 195）。
- `blocks_minimum_v1=true` for unresolved P0 rows and same-fund strict-correctness blockers。
- `blocks_full_v1=true` for all unresolved mismatch / unavailable rows。
- `prohibited_action` 必须声明禁止猜测修复、golden 编辑、runtime 编辑。

### 7. 验证矩阵是否足够

**Verdict: PASS**

Evidence:
- Validation matrix（lines 214-228）覆盖 8 项检查：plan whitespace、plan-only forbidden diff、score output parses (`json.tool`)、quality output parses (`json.tool`)、evidence artifact diff、golden/fixture/manifest diff、runtime diff、reports diff review。
- Lines 229: "`ruff` / `pytest` are not required for docs/evidence-only rerun. They become required only if runtime or test files are changed, which this gate forbids." — 合理，因为本 gate 只运行已有 CLI 命令并写 evidence docs，不修改 Python 代码。
- Line 227: "If Python/runtime changes would be required to run or parse the score, stop and do not implement." — 安全约束。

### 8. 是否遵守 scope 边界

**Verdict: PASS**

Evidence:
- Non-Goals 排除 QDII / FOF / `110020` / `017641` / `004393` / `004194`（line 20）。
- 禁止 `extra_payload`（line 22）。
- Stop conditions 排除 QDII / FOF / `110020` / `004393` / `004194`（line 258）和 Host/Agent/dayu work（line 259）。
- Truth Sources 引用 `AGENTS.md` 四层边界（line 34）。
- 不触及 `FundDocumentRepository` 边界、external source strategy、final judgment、renderer、Service/UI。

### 9. Rerun 命令前提条件是否成立

**Verdict: PASS**

Evidence:
- Snapshot 存在：`reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529/snapshot.jsonl`（22,076 bytes，非空）。
- `errors.jsonl` 存在（0 bytes，空）。
- Golden-answer.json 包含 20 条 006597 reviewed rows。
- 当前 score 是 `coverage_scope=not_configured`，`total_records=0`，所有 correctness counts 为零 — 需要 rerun。
- Not-configured fallback 处理（lines 138-145）: 如果 rerun 仍然 not_configured，decision 是 `blocked_machine_setup_failure`，stop 不改代码。

### 10. Golden row priority map 是否准确

**Verdict: PASS_WITH_FINDINGS** — 见 F1。

## Findings

### F1: fee_schedule P0 字段无 golden rows 未被显式标注（minor, non-blocking）

**Location:** §Expected 006597 Golden Row Priority Map（lines 201-210）

**Plan states:**
- P0 006597 fields in current golden answer: `basic_identity.*`（5）, `benchmark.benchmark_name`（1）, `classified_fund_type.fund_type`（1）, `nav_benchmark_performance.*`（2）, `manager_strategy_text.strategy_summary` + `market_outlook`（2）= 11 rows
- P1: `product_profile.*`（2）, `manager_alignment.*`（2）, `holder_structure.*`（2）, `share_change.*`（3）= 9 rows

**Observed gap:**
- `docs/design.md` §7.3（line 743）定义 P0 包括 `fee_schedule`。
- `reports/golden-answers/golden-answer.json` 006597 rows 不包含任何 `fee_schedule` 字段。
- 这意味着即使 rerun 在 20 条现有 rows 上 clean pass，006597 的 P0 strict correctness coverage 仍然不完整（缺少 `fee_schedule` golden rows）。
- Plan 未在 priority map 或 result handling rules 中显式标注此 gap。

**Assessment:** 不影响本 gate 的核心决策逻辑。Plan 已规定 clean pass 只能是 `promotion_prep_candidate`，`promotion_allowed=false`，所以不会因 clean pass 而错误推进 promotion。但如果 implementation worker 未意识到此 gap，可能在 evidence summary 中遗漏 P0 coverage 不完整的说明。

**Impact:** Low。Clean pass 仍然不会 promotion。但 implementation evidence 应显式记录 fee_schedule P0 golden-row 缺失，以便 controller 在后续 promotion gate 中评估。

**Recommendation:** Implementation worker 在 evidence artifact 中应补充：fee_schedule 是 P0 字段但当前无 006597 golden rows，因此 clean pass 不代表 full P0 coverage。无需修改 plan 本身。

## Cross-Reference: Implementation-Control.md

`docs/implementation-control.md` line 32: Next entry point 为 `006597 same-fund unavailable field review if existing untracked evidence is accepted, otherwise 006597 strict correctness rerun with reports/golden-answers/golden-answer.json`。

Plan 正确对准此 entry point，选择 strict correctness rerun 路径而非 accepting untracked follow-up evidence 路径。

## Cross-Reference: Strict Correctness Decision

`docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-decision-20260529.md` line 34: 006597 `needs_future_gate`，`not_configured`，`total_records=0`，"strict golden correctness score rerun with golden answer"。

Plan 正确继承此前置裁决。

## Cross-Reference: Preflight / Fixture Manifest

| Evidence | Plan claim | Verified value |
|---|---|---|
| Preflight readiness | `deferred_with_owner` | `deferred_with_owner` |
| Preflight blockers | `strict_golden_not_configured`, `fixture_promotion_absent` | Same |
| Bond blocker | Resolved context only | `bond_risk_evidence_missing` in resolved_items |
| Quality gate | `warn` | `warn` |
| Fixture state | `absent` | `absent` |
| promotion_allowed | `false` | `false` |
| blocks_minimum_v1 | `true` | `true` |
| blocks_v1 | `true` | `true` |
| Golden-answer rows | 20 | 20（5 basic_identity + 2 product_profile + 1 benchmark + 1 classified_fund_type + 2 nav_benchmark_performance + 2 manager_strategy_text + 2 manager_alignment + 2 holder_structure + 3 share_change） |

All cross-references verified.

## Plan Quality Assessment

**Strengths:**
- 彻底的 006597-specific scope，正确处理旧 untracked artifacts 为 read-only only
- 完整的 result handling rules：not_configured / mismatch / same-fund unavailable / clean pass 四种场景
- Clean pass 只能是 `promotion_prep_candidate`，不改 fixture state，不改 promotion_allowed
- 详细的 manual verification ledger 格式（16 列）
- 完整的 validation matrix（8 项检查）
- 合理的 stop conditions（10 条）
- 明确的 completion report format
- 正确区分 cross-fund unavailable 和 same-fund unavailable
- Not-configured fallback 处理完整

**One minor gap:** fee_schedule P0 golden-row 缺失未显式标注。

## Conclusion

**PASS_WITH_FINDINGS**

The plan is handoff-ready for implementation. All 10 verification criteria pass. One minor finding (F1): `fee_schedule` is a P0 field per `docs/design.md` §7.3 but has no golden-answer rows for 006597; the plan's priority map does not explicitly call out this gap. This does not affect the gate's decision logic because clean pass remains `promotion_prep_candidate` only, but implementation evidence should note the incomplete P0 coverage.

No blocking issues. The plan correctly:
- Is 006597-specific and does not accept old untracked multi-fund follow-up artifacts
- Uses `reports/golden-answers/golden-answer.json` with new 006597-specific output paths
- Distinguishes cross-fund unavailable from same-fund 006597 unavailable
- Preserves `fixture_state=absent` and `promotion_allowed=false` even on clean pass
- Prohibits golden/fixture/manifest/runtime/FQ/control-doc mutations
- Includes field-level ledger format with owner/next_gate/blocks flags
- Has adequate validation matrix with json.tool, diff check, and forbidden diff
- Correctly skips ruff/pytest for docs/evidence-only rerun
- Respects all scope boundaries (no QDII/FOF/110020/004393/004194/Host-Agent-dayu)

## Artifact Path

`docs/reviews/release-maintenance-006597-strict-correctness-rerun-plan-review-glm-20260529.md`

## Self-check

Self-check: pass
