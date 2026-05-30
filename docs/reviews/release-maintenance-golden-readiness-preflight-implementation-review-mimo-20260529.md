# Golden Readiness Preflight Implementation Review — MiMo

日期：2026-05-29
Review target: 当前未提交改动（golden-readiness-preflight gate implementation）
Gate: `golden-readiness preflight gate`
Role: implementation reviewer only，不改代码、不 commit/push/PR/merge/release/golden promotion。

## Verdict

**accepted**

Implementation 完整遵循 accepted plan，fail-closed 语义正确，blocker taxonomy 聚合准确，非目标边界未被触碰。59 tests 全部通过，smoke 输出与预期一致。

## Findings (severity DESC)

### F1 [info] 006597 同时存在 `strict_golden_not_configured` blocker 和 `strict_golden_coverage: covered`

Smoke JSON 中 006597 行：
- `strict_golden_coverage: "covered"`（因为 `golden-answer.json` 的 `funds[]` 包含 `006597`）
- blockers 含 `strict_golden_not_configured`（因为 score.json 的 `correctness.status=unavailable`, `coverage_scope=not_configured`）

这不是 bug——`_derive_score_correctness_blockers()` 和 `_derive_strict_golden_coverage()` 是两条独立的检查路径，分别对应 plan 的 `strict_golden_not_configured`（score correctness 未配置）和 `strict_golden_fund_not_covered`（golden answer 未覆盖）。但在人类可读 Markdown 中，同一行同时出现 `strict_golden_coverage: covered` 和 `strict_golden_not_configured` blocker 可能令人困惑。

**影响**：无功能性影响。所有其他 fund（004393、004194 等）也有同样模式（`covered` + `strict_golden_not_configured`），因为当前所有 score.json 的 correctness 都是 `not_configured`。

**Suggestion**：可在 Markdown 的 `strict_golden_coverage` 列显示 `covered/not_configured` 以区分两层状态，但不阻塞 acceptance。

### F2 [info] `_payload_mentions_code` 递归文本匹配存在假阳性可能

`golden_readiness_preflight.py:1975-1995`：`_payload_mentions_code` 在整个 JSON 子树中递归搜索字符串 `code`。如果某个 issue 的 `message` 或其他字段恰好包含 `"bond_risk_evidence_missing"` 文本（非 code 字段），也会触发匹配，导致本应输出 resolved item 的场景被跳过。

**影响**：当前实际 score/quality payload 不包含此文本，实际运行无风险。但这是一个防御性编码 gap。

**Suggestion**：改为只检查 `score_applicability_issues[]` 和 `quality_gate.issues[]` 中每个 dict 的 `reason_code` / `rule_code` 字段，而非全文递归搜索。不阻塞 acceptance。

### F3 [info] `_load_json_object_or_none` 定义后立即赋值 `_ = _load_json_object_or_none`

`golden_readiness_preflight.py:2600-2618`：函数 `_load_json_object_or_none` 定义后被赋值给 `_`，但未被任何代码调用。这是 dead code。

**影响**：无。可能是实现过程中的残留。

**Suggestion**：删除 L2600-2618。不阻塞 acceptance。

## Positive Confirmations

### 1. 只读 preflight，不 promotion

- `golden_readiness_preflight.py` 全文无 write/modify/delete golden fixture 或 promotion state 的代码。
- `_write_outputs` 只写 `reports/golden-readiness-preflight/` 目录下的 JSON/Markdown。
- CLI 不引入 Host/Agent/dayu/release readiness/PR/push/merge。
- Smoke evidence guardrails 段确认未修改 score policy、quality gate、FQ0-FQ6、golden fixtures。

### 2. Fail-closed 语义

| 场景 | 代码位置 | 行为 |
|------|---------|------|
| 缺 snapshot/score/quality | L1375-1407 `_missing_artifact_blockers` | `missing_input_artifact` blocker, readiness `not_evaluated` |
| golden answer 缺失 | L1134-1144 `_derive_global_blockers` | `strict_golden_not_configured` global blocker |
| fixture promotion 缺失 | L1145-1166 `_derive_global_blockers` + L1798-1813 | `fixture_promotion_absent` blocker |
| quality gate `block` | L1688-1701 | `quality_gate_block` blocker |
| quality gate `warn` | L1703-1717 | `quality_gate_warn` warning only，不证明 ready |
| source provenance unknown | L1507-1521 | `source_provenance_unknown` blocker |
| source provenance ineligible | L1523-1540 | `source_provenance_ineligible` blocker |
| score `baseline_blocking=true` | L1604-1616 | `score_applicability_baseline_blocking` blocker |
| preflight input 未知字段 | L789-806 `_reject_unknown_keys` | `ValueError` |
| fund_artifacts 项未知字段 | L739-753 | `ValueError` |

### 3. 006597 bond blocker 不再作为 blocker

- Smoke JSON: 006597 行 `resolved_items` 含 `code=blocker_resolved`, `original_blocker_code=bond_risk_evidence_missing`。
- Smoke JSON: 006597 行 `blockers` 不含 `bond_risk_evidence_missing`。
- 代码 L1318-1321: `if artifact.fund_code == "006597"` 才调用 `_derive_006597_bond_resolved_items`。
- `_derive_006597_bond_resolved_items` (L1936-1972): 先检查 score/quality payload 中是否仍含 `bond_risk_evidence_missing`，若不含才输出 resolved item。
- Test `test_preflight_marks_006597_bond_blocker_resolved_not_blocker` 验证此行为。

### 4. QDII/FOF/110020/source provenance/quality/strict golden/fixture blockers 正确聚合

| Blocker | Smoke 验证 | 代码路径 |
|---------|-----------|---------|
| `qdii_coverage_blocked` | 096001/040046/019172/021539 均有此 blocker | L1879-1890 `_derive_coverage_disposition_blockers` |
| `qdii_replacement_hard_stop` | global_blockers 中存在 | L2079-2093 `_derive_manifest_global_blockers` |
| `fof_taxonomy_pending` + `fof_data_gap` | FOF_SLOT 行有此两个 blocker | L1891-1911 |
| `reviewed_candidate_not_promoted` + `index_evidence_insufficient` | 110020 行有此两个 blocker | L1912-1932 |
| `source_provenance_eligible_fallback` | 017641/110020/096001 等作为 warning | L1541-1556 |
| `quality_gate_block` | 017641/096001/040046/019172/021539 有此 blocker | L1688-1701 |
| `quality_gate_warn` | 004393/004194/006597/110020 作为 warning | L1703-1717 |
| `strict_golden_fund_not_covered` | 017641/110020/096001 等有此 blocker | L1758-1772 |
| `fixture_promotion_absent` | 所有 fund 行 + global blocker | L1145-1166 + L1798-1813 |

### 5. Strict golden answer v1 只 fund-level，不触发 year/partial reserved codes

- `_derive_strict_golden_coverage` (L1721-1773): 只检查 `artifact.fund_code in golden_covered_funds`，不检查 year。
- `RESERVED_STRICT_GOLDEN_CODES = frozenset({"strict_golden_year_not_covered", "strict_golden_partial_coverage"})` 定义于 L43-45。
- Smoke JSON 不含 `strict_golden_year_not_covered` 或 `strict_golden_partial_coverage`。
- Test `test_preflight_reserves_strict_golden_year_and_partial_coverage_codes` 验证此行为。

### 6. `--preflight-input` 与 shortcut 互斥

- CLI L700-706: `_validate_preflight_cli_conflicts` 在调用 Service 前检查。
- Service L95-109: `_validate_request` 再次检查 `preflight_input_path` 与 `fund_artifacts`/`selected_pool_path`/`coverage_disposition_path`/`fixture_promotion_state_path` 冲突。
- CLI test `test_golden_readiness_preflight_cli_rejects_preflight_input_conflicts` 验证 exit 2。
- `--fund-artifact` 格式 `::` 分隔 5 字段：L768-776 解析，test `test_golden_readiness_preflight_cli_rejects_bad_fund_artifact_fields` 验证。

### 7. 显式参数不进 extra_payload

- `_reject_unknown_keys` (L789-806) 在 `_load_preflight_input`、`_fund_artifact_from_json`、`_coverage_entry_from_json`、`_load_coverage_disposition_manifest` 中均被调用。
- Test `test_preflight_input_schema_rejects_unknown_fields` 验证 `extra_payload` key 被拒绝。

### 8. Service/Fund/UI 边界合理

- Fund 层 (`golden_readiness_preflight.py`): 纯数据聚合，只读 artifacts，不调用 Service/Host/Agent。
- Service 层 (`golden_readiness_preflight_service.py`): 只做路径/互斥校验，然后调用 Fund 层 API。
- UI 层 (`cli.py`): 解析 CLI 参数，调用 Service，输出 stdout。
- `__init__.py` export 包含 `FundArtifactInput`、`GoldenReadinessPreflightRequest`、`GoldenReadinessPreflightService`。

### 9. 110020 raw disposition 保留

- Smoke JSON 110020 行: `raw_disposition: "reviewed_coverage_candidate_input_accepted"`, `preflight_disposition: "reviewed_coverage_candidate"`。
- Static manifest 110020 entry: `raw_disposition: "reviewed_coverage_candidate_input_accepted"`, `preflight_disposition: "reviewed_coverage_candidate"`。
- Test `test_preflight_preserves_110020_raw_disposition_and_blocks_not_promoted` 验证。

### 10. Tests 覆盖

- 59 tests 全部通过（focused pytest）。
- 70 tests 全部通过（含 repo hygiene）。
- 959 tests 全部通过（full pytest, coverage 91.53%）。
- ruff 全量检查通过。

### 11. 不触碰非目标

- 未修改 `fund_agent/fund/extraction_score.py`、`quality_gate.py`、`golden_answer.py`。
- 未修改 `reports/golden-answers/golden-answer.json`。
- 未引入 `fund_agent/host`、`fund_agent/agent`、dayu 依赖。
- 未修改 FQ0-FQ6 severity 或 baseline_blocking 语义。
- 未修改 score/quality gate 规则。
- 未直接读取 PDF/cache/source helper。

## 结论

Implementation 完整、准确、可接受。三个 info 级观察项不阻塞 gate。
