# Golden Readiness Preflight Plan Review — MiMo

日期：2026-05-29
Review target: `docs/reviews/release-maintenance-golden-readiness-preflight-plan-20260529.md`
Gate: `golden-readiness preflight gate`
Role: plan review worker only，不改代码、不 commit/push/PR。

## Verdict

**accepted-with-required-fixes**

Plan 目标、scope guardrails、fail-closed 规则、blocker taxonomy 设计方向均正确。但存在 2 个 structural error 和若干 gap 需要在 implementation 前修正。

## Findings (severity DESC)

### F1 [block] 模块路径不存在：`fund_agent/fund/` 不是现有包

Plan 提出新增 `fund_agent/fund/golden_readiness_preflight.py`，但 **`fund_agent/fund/` 目录不存在**。现有 fund 相关模块直接平铺在 `fund_agent/` 下（`extraction_score.py`、`quality_gate.py`、`golden_answer.py` 等），没有 `fund` 子包。

同理 Service 层引用的 `fund_agent/services/` 存在，但 plan 中 CLI 示例路径 `fund_agent/ui/cli.py` 需要确认是否也是正确位置。

**Required change**：将新模块路径改为 `fund_agent/golden_readiness_preflight.py`（平铺于 `fund_agent/`），或先创建 `fund_agent/fund/__init__.py` 并迁移——但后者超出本 gate scope。推荐直接放 `fund_agent/` 下，与 `extraction_score.py`、`quality_gate.py` 同级。

---

### F2 [block] CLI 默认引用不存在的 fixture promotion manifest

CLI 示例使用 `--fixture-promotion-state-path docs/reviews/golden-fixture-promotion-state.json` 作为默认值，但 **该文件不存在**。

Plan 在 Blocking Questions 段落确实提到"若没有机器可读 manifest 则默认 `fixture_promotion_absent`"，但 CLI 示例给人的印象是这个文件是可用的默认输入。如果实现 worker 直接 copy CLI 示例，会导致 IO error 或静默 fallback，两者都违背 plan 自己的 fail-closed 原则。

**Required change**：
- CLI 不应把不存在的文件设为默认值。应改为 `--fixture-promotion-state-path` 为 optional，缺省时走代码内 `fixture_promotion_absent` blocker 逻辑。
- 或者：在实现前先创建一个 minimal valid manifest JSON（只需 `{ "schema_version": "...", "funds": [] }`），然后 CLI 默认指向它。

---

### F3 [warn] 静态 disposition manifest 机器可读性是可接受的临时方案，但需要显式标注 lifecycle

Plan 承认当前没有机器可读 coverage disposition manifest，提出在代码内 hardcode 一个 static manifest。这个方案本身是合理的——它链接了已 accepted 的 controller judgment artifacts，每个条目都可以追溯。

但有两个风险：
1. **无 version/schema 字段**：static manifest 应有 `schema_version`、`generated_from`（列出引用的 judgment artifact 路径）、`accepted_date` 字段，否则未来无法判断 manifest 是否过期。
2. **无 exit criteria**：Plan 说"中期应另开 gate"但没有明确什么条件下结束 static manifest 阶段。建议在 plan 中增加一条：当有 3+ 个 disposition 条目需要更新时，必须先创建机器可读 manifest gate。

**Required change**：static manifest 数据结构增加 `schema_version`、`source_artifacts: list[str]`、`accepted_as_of: str` 字段。在 Blocking Questions 或 Stop Conditions 中增加 lifecycle exit criteria。

---

### F4 [warn] `fund_artifacts` CLI 参数格式缺少 validation 规则

`--fund-artifact 006597:2024:...snapshot.jsonl:...score.json:...quality_gate.json` 用冒号分隔 5 个字段。但：
- Path 中可能包含冒号（虽然当前 paths 不含，但 contract 应明确禁止或用不同分隔符）
- 缺少字段数校验规则（恰好 5 段？还是允许省略 optional paths？）
- Plan 提到 `--preflight-input path.json` 作为替代，但 JSON schema 未给出

**Required change**：明确 `--fund-artifact` 分隔符为 `::`（双冒号）或改用 `--fund-artifact` 多次调用 + positional。给出 `--preflight-input` 的 JSON schema fragment。

---

### F5 [warn] Blocker code `bond_006597_resolved` 是特例硬编码

Plan 为 006597 设计了一个专属 blocker code `bond_006597_resolved`。这引入了一个 per-fund 特例进入通用 taxonomy。如果未来其他 fund 也有类似"某 blocker 已解除"的情况，是复用这个 code 还是新建 `bond_XXXXX_resolved`？

**Suggestion**：改为通用 code `blocker_resolved`，在 `resolved_items` 中用 `fund_code` + `original_blocker_code` 区分。不需要 block，但实现时应避免 per-fund code 硬编码。

---

### F6 [info] Test plan 缺少边界 case

现有 12 个 test cases 覆盖了主要 blocker 路径，但缺少：
- `golden-answer.json` 存在但目标 fund 不在其中（`strict_golden_fund_not_covered` 的正向触发）
- `snapshot.jsonl` 存在但为空文件或只有 header
- `score.json` 缺少 `score_applicability_issues` key（不是空 list，是 key 不存在）
- `quality_gate.json` status 既非 `pass`/`warn`/`block`（unrecognized enum）
- `coverage_disposition_path` 提供了但 JSON schema 不匹配

**Suggestion**：补充 3-5 个 malformed/edge input test，不需要 block。

---

### F7 [info] `overall_status` 语义对 `deferred_with_owner` 的处理需要更明确

Plan 说 `deferred_with_owner` 的 `blocks_v1` 由 disposition manifest 声明，当前默认 `blocks_v1=true`。但 JSON schema 中 `overall_status` 只允许 `pass`/`block`，没有 `deferred` 状态。

这意味着：如果所有 rows 都是 `deferred_with_owner` 且 `blocks_v1=true`，`overall_status=block`——这是正确的。但如果未来 controller 接受某些 defer 不 block v1，`overall_status` 语义是否需要扩展？

**Suggestion**：在 plan 中增加一句声明：`overall_status` 的 `pass` 含义是"所有 required readiness 条件满足或已被 accepted disposition 排除在 v1 scope 之外"。不需要改 schema，只需澄清语义。

---

## 正面确认

1. **输入 contract 设计良好**：显式参数、无 `extra_payload`、Path 类型、fail-closed on missing。这是正确的方向。
2. **输出 schema 清晰**：JSON 顶层 + per-fund row + blocker row 三层结构，枚举值都有定义，machine-parseable。
3. **Blocker taxonomy 覆盖全面**：从 source provenance 到 quality gate 到 strict golden 到 fixture promotion，每个阶段都有对应 code。
4. **006597 bond blocker 归因准确**：verified against actual snapshot/score/quality artifacts——`score_applicability_issues=[]`，quality gate 无 `bond_risk_evidence_missing`，确实 resolved。
5. **QDII hard stop 准确**：四个 QDII fund codes、quality block、not_promoted 均与 consolidation judgment 一致。
6. **110020 状态准确**：reviewed coverage candidate input accepted、not_promoted、methodology/constituents residuals 均与 judgment 一致。
7. **FOF taxonomy_pending 准确**：QDII-FOF 不算 pure FOF 的判断与 consolidation judgment 一致。
8. **Scope guardrails 充分**：不 promotion、不改 FQ0-FQ6、不接 Host/Agent/dayu、不 push/PR/merge。

## Required Changes Summary

| # | Severity | Change |
|---|----------|--------|
| F1 | block | 修正模块路径：`fund_agent/golden_readiness_preflight.py`（平铺），而非 `fund_agent/fund/` |
| F2 | block | CLI 不以不存在的文件为默认值；改为 optional 或先创建 minimal manifest |
| F3 | warn | Static manifest 增加 `schema_version`/`source_artifacts`/`accepted_as_of` 字段 + lifecycle exit criteria |
| F4 | warn | 明确 `--fund-artifact` 分隔符和字段数校验；给出 `--preflight-input` JSON schema |

F1 和 F2 必须在 implementation 前修正。F3 和 F4 可以在 implementation 过程中修正，但必须在测试通过前完成。
