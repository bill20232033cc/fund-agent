# Golden Readiness Preflight — Aggregate Deepreview (DS)

日期：2026-05-29

角色：AgentDS aggregate deepreview reviewer。不改代码、不 commit/push/PR/merge/release/golden promotion。

Work unit：`golden-readiness preflight gate`

Commit：`c4cd413` — gateflow: accept golden readiness preflight implementation

## Verdict

**Accepted** — 端到端 gate 可接受。两条独立 implementation review（DS + MiMo）均 accept，无 blocking finding。Plan review/re-review chain 完整。实现符合 plan，validation 全覆盖，smoke 输出正确。

## Gate Chain Integrity

| Phase | Artifact | Verdict |
|---|---|---|
| Plan | `release-maintenance-golden-readiness-preflight-plan-20260529.md` | — |
| Plan review: MiMo | `...-plan-review-mimo-20260529.md` | accepted-with-required-fixes (F1 reject, F2/F3/F4 closed) |
| Plan review: GLM | `...-plan-review-glm-20260529.md` | accepted-with-required-fixes (F1-F5 closed) |
| Plan fix | plan updated with all closed fixes | — |
| Plan re-review: MiMo | `...-plan-rereview-mimo-20260529.md` | accepted |
| Plan re-review: GLM | `...-plan-rereview-glm-20260529.md` | accepted |
| Implementation | `golden_readiness_preflight.py` + Service + CLI + tests + docs | — |
| Implementation review: MiMo | `...-implementation-review-mimo-20260529.md` | accepted (3 info findings) |
| Implementation review: DS | `...-implementation-review-ds-20260529.md` | accepted (1 info finding) |
| Commit | `c4cd413` | 14 files, +5501 lines |
| **Aggregate deepreview (this)** | — | **accepted** |

## End-to-End Gate Assessment

### 1. 是否误入 golden promotion？

**否。** 全部代码、测试、smoke 输出均确认为只读 preflight：

- `golden_readiness_preflight.py` 全文无 write/modify/delete golden fixture、promotion state、score policy、FQ0-FQ6 语义的代码
- `_write_outputs` 只写 `reports/golden-readiness-preflight/<run_id>/` 下的 JSON 和 Markdown
- CLI 不引入 Host/Agent/dayu/release readiness/PR/push/merge 逻辑
- Smoke 输出的 `overall_status=block` 确认当前不宣称 ready，且退出码为 0（preflight 生成成功，即使结果是 block）
- 两条 implementation review 均独立确认 non-goal preservation

### 2. 是否误削弱 FQ0-FQ6 或 score/quality/golden fixture？

**否。**

- 未修改 `extraction_score.py`、`quality_gate.py`、`golden_answer.py`
- 未修改 `reports/golden-answers/golden-answer.json`
- 未修改 FQ0-FQ6 severity 或 baseline_blocking 语义
- 未修改 `score_applicability_issues` 生成逻辑
- Strict golden answer v1 只做 fund-level coverage 检查；year-level (`strict_golden_year_not_covered`) 和 partial-field (`strict_golden_partial_coverage`) codes 保留为 reserved，不在当前 preflight 触发
- Quality gate `warn` 只写入 `warnings[]`，不进入 `blockers[]`，不单独导致 `blocked` readiness

### 3. 006597 bond blocker 是否不再列为 blocker？

**是。** 三源确认：

- **代码** (`golden_readiness_preflight.py:1318–1321` + `_derive_006597_bond_resolved_items` at L1936–1972)：当 score `score_applicability_issues=[]` 且 quality gate 不含 `bond_risk_evidence_missing` 时，输出 `ResolvedReadinessItem(code="blocker_resolved", original_blocker_code="bond_risk_evidence_missing", fund_code="006597")`
- **Smoke JSON**：006597 行 `resolved_items[0].code="blocker_resolved"`，`original_blocker_code="bond_risk_evidence_missing"`；`blockers` 不含 `bond_risk_evidence_missing`
- **Test**：`test_preflight_marks_006597_bond_blocker_resolved_not_blocker` 通过

006597 当前 readiness 为 `deferred_with_owner`，blockers 为 `strict_golden_not_configured` + `fixture_promotion_absent`，warnings 为 `quality_gate_warn`。均不是 bond risk blocker 的回归。

### 4. QDII/FOF/110020/source provenance/quality/strict golden/fixture residual 是否有 owner/next_gate/evidence？

**是。** Smoke 输出逐项确认：

| Blocker | Fund | Owner | Next Gate | Evidence |
|---|---|---|---|---|
| `qdii_coverage_blocked` | 096001/040046/019172/021539 | future QDII diagnosis/taxonomy gate | QDII deferred-from-v1 disposition gate | consolidation controller judgment |
| `qdii_replacement_hard_stop` | global | future QDII diagnosis/taxonomy gate | QDII deferred-from-v1 disposition gate | all 4 manifest source artifacts |
| `fof_taxonomy_pending` | FOF_SLOT | future FOF taxonomy gate | pure FOF repository-verified candidate gate | consolidation controller judgment |
| `fof_data_gap` | FOF_SLOT | future FOF taxonomy gate | pure FOF repository-verified candidate gate | consolidation controller judgment |
| `reviewed_candidate_not_promoted` | 110020 | future index evidence sufficiency gate | methodology/constituents/fact freeze gate | 110020 controller judgment |
| `index_evidence_insufficient` | 110020 | future index evidence sufficiency gate | methodology/constituents/fact freeze gate | 110020 controller judgment |
| `fixture_promotion_absent` | all 10 funds + global | future fixture promotion gate | produce accepted manifest | — |
| `strict_golden_not_configured` | all 10 funds | per-fund disposition owner | per-fund next gate | per-fund evidence artifacts |
| `strict_golden_fund_not_covered` | 017641/QDII×4/110020 | per-fund owner | per-fund next gate | per-fund evidence artifacts |

全部 blocker 均有 `owner`、`next_gate`、`evidence_artifacts` 字段，无 dangling blocker。Blocking questions 列出三个需要 controller 决定的问题。

### 5. 110020 raw_disposition 是否保留？

**是。** Static manifest 中 `110020.raw_disposition="reviewed_coverage_candidate_input_accepted"`，`preflight_disposition="reviewed_coverage_candidate"`。Smoke JSON 110020 行两项均正确保留。Test `test_default_manifest_preserves_110020_raw_disposition` 验证。

## Reviewer Consensus

| Finding | DS Review | MiMo Review | Severity |
|---|---|---|---|
| `_load_json_object_or_none` dead code | F1 (non-blocking) | F3 (info) | Trivial — both agree non-blocking |
| `covered` + `strict_golden_not_configured` appearing together | Not listed | F1 (info) | Info — cosmetic in Markdown，不阻塞 |
| `_payload_mentions_code` false positive risk | Not listed | F2 (info) | Info — 当前 payload 无此文本，实际无风险 |

两条 implementation review 无 blocking finding。三方（plan reviews × 2, implementation reviews × 2, aggregate deepreview × 1）均 accept。

## Validation Summary

| Command | Result |
|---|---|
| Focused ruff (new files) | All checks passed |
| Focused pytest (59 tests) | 59 passed |
| Repo hygiene pytest (70 tests) | 70 passed |
| Full ruff | All checks passed |
| Full pytest + coverage | 959 passed, 91.53% coverage (>> 50% gate) |
| Real preflight smoke | `overall_status=block`, JSON + MD written |

## Architecture Boundary Check

- UI (`cli.py`) → 只依赖 `fund_agent.services`，不直接 import `fund_agent.fund`
- Service (`golden_readiness_preflight_service.py`) → 只做校验 + 转发，调用 Agent/Fund 层 API
- Agent/Fund (`golden_readiness_preflight.py`) → 纯数据聚合，只读 artifacts，不调 Service/Host/Agent
- 无 Host/Agent/dayu 依赖
- `FundArtifactInput` 从 Fund 层定义 → Service re-export → CLI 消费，符合四层边界规则
- 无 `extra_payload`：`_reject_unknown_keys` 拒绝未知 JSON 字段

## Control Doc Update Recommendation

`docs/implementation-control.md` 当前 Startup Packet 的 `Current gate` 仍为 `drawdown_stress NAV-derived metric implementation gate accepted local validation`，`Next entry point` 为 `bond risk evidence local readiness reconciliation gate`。本 preflight gate 已实现并 accepted，建议 controller acceptance 后做最小更新：

1. 在 Active Gate Ledger 新增一行 golden readiness preflight gate → accepted locally
2. 在 Accepted Artifacts 表中新增本 gate 的全部 artifacts（plan/reviews/implementation evidence/implementation reviews/aggregate deepreviews）
3. 在 Open Residuals 中记录 preflight 输出的 blocker owners 和 blocking questions 为已知待解决项
4. 更新 `Current gate` / `Next entry point` 为 controller 指定的下一步
5. 不追加长日志；control doc 更新应只压缩到几行 reference + artifact 路径

此更新应等待 controller judgment 后再做，不在本 review scope 内。

## Cross-Review on Prior Gate Leakage

检查本 gate 是否意外引入之前 gate 不应触碰的内容：

- CSRC EID adapter normalization：未修改 `nav_data.py` / `nav_repository.py` ✓
- Drawdown NAV-derived metric：未修改 `nav_metrics.py` / `risk_check.py` ✓
- Bond risk evidence extractor：未修改 extractor 逻辑 ✓
- Score policy：未修改 `extraction_score.py` ✓
- Quality gate：未修改 `quality_gate.py` / FQ0-FQ6 rules ✓
- Golden answer：未修改 `golden-answer.json` ✓
- Source provenance：未修改 `sources.py` / source strategy ✓

## Residual Risks

1. **Static manifest staleness**：代码内 static disposition manifest 在 controller judgment 改变 coverage disposition 时必须同步更新。当前 lifecycle semantics 已记录退出条件，但 manifest 仍靠人工维护。
2. **`_payload_mentions_code` 假阳性**（MiMo F2）：当前 payload 无触发文本，实际运行安全。若未来 score/quality 输出中包含 code 文本在其他字段（如 message），可能误判。
3. **Strict golden coverage vs correctness 两层语义混淆**（MiMo F1）：Markdown 表中 `strict_golden_coverage: covered` 与 `strict_golden_not_configured` blocker 同时存在，因 golden answer JSON 含该 fund 但 score correctness 未配置 golden path。不影响功能但人类阅读可能困惑。
4. **Control doc lag**：control doc 尚未包含本 preflight gate 记录。需 controller acceptance 后更新。

## Explicit Statement

Controller **可以** accept 当前 golden-readiness preflight gate 为 terminal state。Implementation 正确、review 完整、smoke 一致。三条 info-level 观察项均不影响 gate acceptance。Control doc 更新应在 controller acceptance 后以最小增量完成（一行 Active Gate Ledger 条目 + artifact 表扩展）。
