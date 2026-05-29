# Golden Readiness Preflight Implementation — Implementation Review (DS)

日期：2026-05-29

角色：AgentDS implementation reviewer，非 controller，非 implementation worker。

Work unit：`golden-readiness preflight gate`

Reviewed artifacts：
- `fund_agent/fund/golden_readiness_preflight.py`（new, 2619 lines）
- `fund_agent/services/golden_readiness_preflight_service.py`（new, 128 lines）
- `fund_agent/services/__init__.py`（modified）
- `fund_agent/ui/cli.py`（+185 lines）
- `tests/fund/test_golden_readiness_preflight.py`（new, 751 lines）
- `tests/ui/test_cli.py`（+182 lines, ~2080 lines total）
- `README.md`（+27 lines）
- `fund_agent/fund/README.md`（+9 lines）
- `tests/README.md`（+14 lines）

Accepted plan：`docs/reviews/release-maintenance-golden-readiness-preflight-plan-20260529.md`

Implementation evidence：`docs/reviews/release-maintenance-golden-readiness-preflight-implementation-evidence-20260529.md`

Smoke output：`reports/golden-readiness-preflight/golden-readiness-preflight-20260529/golden_readiness_preflight.json` / `.md`

## Verdict

**Accepted** — 1 non-blocking finding. 实现与 accepted plan 一致，验证通过（full ruff + full pytest 959 passed / 91.53% coverage），smoke 输出与 plan 预期一致。

## Preflight

已读取 AGENTS.md、docs/design.md、docs/implementation-control.md、accepted plan、implementation evidence。

Scope check：本 review 只产出本 artifact；不修改 code/tests/evidence；不 commit/push/PR/merge/release/golden promotion。

## Plan Compliance Matrix

| Plan Requirement | Implementation | Status |
|---|---|---|
| Agent/Fund 层 `golden_readiness_preflight.py` | ✅ 2619 行，包含全部 plan dataclasses/Literals/public API | Pass |
| Service 层 `golden_readiness_preflight_service.py` | ✅ 128 行，薄封装，只校验 | Pass |
| Service exports `__init__.py` | ✅ `FundArtifactInput` + `GoldenReadinessPreflightRequest` + `Service` | Pass |
| CLI `golden-readiness-preflight` 命令 | ✅ 含 `--preflight-input` / `--fund-artifact` / 全参数 | Pass |
| 只读 preflight，不 promotion | ✅ 不改 score/golden/fixture/FQ0-FQ6 | Pass |
| 006597 bond blocker resolved, 不列 blocker | ✅ smoke 确认：resolved_item 含 `blocker_resolved:bond_risk_evidence_missing`，blockers 不含 | Pass |
| QDII hard stop | ✅ 4× QDII rows `qdii_coverage_blocked` + global `qdii_replacement_hard_stop` | Pass |
| FOF taxonomy/data gap | ✅ `FOF_SLOT` 含 `fof_taxonomy_pending` + `fof_data_gap`，blocked | Pass |
| 110020 raw/preflight disposition 保留 | ✅ `raw_disposition=reviewed_coverage_candidate_input_accepted`, `preflight=reviewed_coverage_candidate` | Pass |
| Source provenance fail-closed | ✅ ineligible/unknown → `source_provenance_ineligible`/`unknown`；eligible fallback → warning only | Pass |
| Quality warn → warning only | ✅ status=warn → `quality_gate_warn` warning，不 block | Pass |
| Quality block → block | ✅ status=block → `quality_gate_block` | Pass |
| Score baseline_blocking → block | ✅ `score_applicability_baseline_blocking` | Pass |
| strict golden v1 fund-level only | ✅ `fund_not_covered`/`not_configured`；year/partial reserved codes 不触发 | Pass |
| Fixture promotion absent → block | ✅ `fixture_promotion_absent` blocker at both global and per-fund | Pass |
| `--preflight-input` / shortcut 互斥 | ✅ CLI + Service 双重校验，冲突 exit 2 | Pass |
| 缺 artifact → not_evaluated | ✅ `missing_input_artifact` + readiness=`not_evaluated` | Pass |
| 显式参数，无 extra_payload | ✅ 全部 typed dataclass，`_reject_unknown_keys` 拒绝未知字段 | Pass |
| 不绕过 FundDocumentRepository | ✅ 模块不读取年报/PDF/cache/source helper | Pass |
| Host/Agent/dayu 未引入 | ✅ 无相关代码或依赖 | Pass |
| Service 输入 JSON schema 校验 | ✅ `_reject_unknown_keys` + schema version + 字段类型检查 | Pass |
| Static manifest metadata | ✅ `schema_version` + `accepted_as_of` + `source_artifacts` + `lifecycle_semantics` | Pass |
| JSON + Markdown 双输出 | ✅ `golden_readiness_preflight.json` + `.md` | Pass |
| Exit code 0 for block status | ✅ smoke `overall_status=block` 但退出码 0 | Pass |

## Test Coverage Assessment

| Test | Covers | Status |
|---|---|---|
| `test_preflight_blocks_missing_required_artifact` | 缺 artifact → not_evaluated | ✅ |
| `test_preflight_marks_006597_bond_blocker_resolved_not_blocker` | 006597 bond resolved | ✅ |
| `test_preflight_blocks_baseline_blocking_score_issue` | baseline_blocking → block | ✅ |
| `test_preflight_blocks_quality_block_but_warn_only_warning` | quality block/warn 区分 | ✅ |
| `test_preflight_blocks_source_provenance_unknown_or_ineligible` | provenance fail-closed | ✅ |
| `test_preflight_records_eligible_fallback_as_non_ready_evidence` | eligible fallback → warning, not ready | ✅ |
| `test_preflight_blocks_qdii_hard_stop` | QDII hard stop | ✅ |
| `test_preflight_blocks_fof_taxonomy_pending_and_rejects_qdii_fof_as_pure_fof` | FOF slot | ✅ |
| `test_preflight_preserves_110020_raw_disposition_and_blocks_not_promoted` | 110020 disposition | ✅ |
| `test_preflight_blocks_strict_golden_absence_and_fund_miss` | golden coverage | ✅ |
| `test_preflight_reserves_strict_golden_year_and_partial_coverage_codes` | reserved codes 不触发 | ✅ |
| `test_preflight_blocks_fixture_promotion_absence` | fixture promotion | ✅ |
| `test_preflight_outputs_static_disposition_manifest_metadata` | manifest metadata | ✅ |
| `test_preflight_input_schema_rejects_unknown_fields` | unknown field rejection | ✅ |
| `test_preflight_json_schema_and_markdown_paths_written` | JSON/MD 输出 | ✅ |
| `test_default_manifest_preserves_110020_raw_disposition` | manifest 110020 正确性 | ✅ |
| CLI: `test_golden_readiness_preflight_cli_outputs_paths_and_status` | 参数转发 + stdout | ✅ |
| CLI: `test_golden_readiness_preflight_cli_rejects_preflight_input_conflicts` | --preflight-input 互斥 | ✅ |
| CLI: `test_golden_readiness_preflight_cli_rejects_bad_fund_artifact_fields` | --fund-artifact 字段数校验 | ✅ |
| CLI: `test_golden_readiness_preflight_cli_rejects_bad_fund_code` | --fund-artifact fund_code 6位校验 | ✅ |

Plan 要求 14 条 Fund 层测试 + 4 条 CLI 测试 = 18 条；实现提供 16 条 Fund 层 + 4 条 CLI = 20 条。全部 pass。

## Findings

### F1 — `_load_json_object_or_none` Defined But Never Called (Non-Blocking)

**Location**: `fund_agent/fund/golden_readiness_preflight.py:2600–2618`

**Finding**: `_load_json_object_or_none()` 是定义为 private helper 但从未被调用。函数的赋值 `_ = _load_json_object_or_none` (line 2618) 仅用于避免 unused definition 告警。

**Severity**: Trivial。不影响功能、测试和 smoke 输出。可能是为未来的 optional JSON 读取路径预留的工具函数。

**Recommendation**: 如果确实不需要，删除；如果需要保留作为未来 utility，建议添加简短 comment 说明意图。不阻断 acceptance。

## Cross-Check: Smoke Output vs Plan Expected Output

| Plan 预期 | Smoke 实际 | Match |
|---|---|---|
| `overall_status: block` | `"block"` | ✅ |
| 006597 bond blocker resolved, not listed | `resolved_items[0].code=blocker_resolved` / `original_blocker_code=bond_risk_evidence_missing` / blockers 不含 | ✅ |
| QDII 四只 fund provenance eligible + quality block + not_promoted | 全部含 `source_provenance_eligible_fallback` warning + `quality_gate_block` + `qdii_coverage_blocked` | ✅ |
| Global `qdii_replacement_hard_stop` | 存在 | ✅ |
| FOF slot taxonomy pending + data gap | `fof_taxonomy_pending` + `fof_data_gap` | ✅ |
| 110020 raw_disposition 保留 | `reviewed_coverage_candidate_input_accepted` | ✅ |
| JSON 含 `static_disposition_manifest.schema_version` / `accepted_as_of` / `source_artifacts` | 三项全在 | ✅ |
| Output JSON + MD paths written | 两个文件均生成 | ✅ |
| strict_golden_year_not_covered / partial_coverage 不触发 | 输出中无此二 code | ✅ |
| fixture_promotion_absent at global + per-fund | global blocker + per-fund blocker 均有 | ✅ |
| quality_gate_warn as warning only | 004393/004194/006597/110020 均 warn → warning, not blocker | ✅ |

## Boundary Check

| Check | Result |
|---|---|
| CLI 不直接 import `fund_agent.fund.*` | ✅ 只 import 自 `fund_agent.services` 和 `fund_agent.ui` |
| Service 不读取 prompt manifest | ✅ 只调 Fund 层 API |
| Fund 层不读取 PDF/cache/source helper | ✅ 只读 JSON/JSONL artifact |
| 不引入 Host/Agent/dayu | ✅ 无相关代码 |
| 显式参数，无 extra_payload | ✅ 全 typed dataclass |
| `FundArtifactInput` 从 services re-export | ✅ 正确四层边界：Fund 定义 → Service re-export → CLI 消费 |

## Validation Summary

Implementation evidence 记录：
- Focused ruff: All checks passed
- Focused pytest: 59 passed
- Docs/repo hygiene pytest: 70 passed
- Full ruff: All checks passed
- Full pytest + coverage: 959 passed, 91.53% coverage (>> 50% gate)
- Real smoke: `overall_status=block`, stdout paths correct

## Explicit Statement

Controller **可以** accept 当前 implementation 并 proceed to controller judgment。全部 plan requirements 已实现，验证全覆盖，smoke 输出与 plan 预期一致。F1 为 trivial 非阻断建议。
