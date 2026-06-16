# Docling Reference Bundle Field-spec Plan Re-review — AgentDS — 2026-06-17

Status: FINAL

## Re-review Target

- **Target**: `docs/reviews/docling-reference-bundle-field-spec-plan-20260617.md` (after fix)
- **Prior review**: `docs/reviews/docling-reference-bundle-field-spec-plan-review-ds-20260617.md` (DS-P1–DS-P5)
- **Gate**: `Docling Reference Bundle Field-spec Planning Gate`
- **Re-reviewer role**: AgentDS, re-review worker only. No code, commit, control-doc, or gate transition.

---

## Findings

无阻塞性发现。

经过逐项交叉验证，DS-P1 至 DS-P5 五个发现均已修复。未引入新阻塞性发现。

---

## Prior Finding Disposition Table

| Finding | 严重度 | 原始问题 | 修复位置 | 修复方式 | 处置 |
|---------|--------|---------|---------|---------|------|
| DS-P1 | 中 | `row_hierarchy_path` 默认行为用"may"措辞，导致实施 Agent 对 standalone 行的 hierarchy path 产生歧义 | plan L134 字段定义表；L349–350 coercion contract | "may set"改为"set to"强制规则；增加 else 分支（无法证明时保持 `()` 和 `"unknown"`）；两处一致 | **已修复** |
| DS-P2 | 中 | `column_header_band_path` 消费者侧语义未定义：无优先级、无去重规则、无冲突处理 | plan L255–268 share-class derivation；L284–297 period-context derivation；L412–415 Slice 2 | 明确定义推导优先级（column_header_path > column_header_band_path > row_label_path > table_context）；去重规则（同标签去重不计双重证明）；冲突 fail-closed；`_match_satisfies_rule()` 消费 canonical 字段而非重扫原始路径 | **已修复** |
| DS-P3 | 低 | `_coerce_cell()` 中"may derive table_family"导致 per-cell 分类（低效且同一表内不一致） | plan L346–349 coercion contract | `_coerce_cell()` 显式禁止运行表族分类，缺失时直接设为 `"unknown"`；表族分类归属 bundle/table-level 的 `_classify_bundle_tables()` | **已修复** |
| DS-P4 | 低 | `bounded_neighbor_row_labels` 只说了不能做什么，没说用途，存在 dead code 风险 | plan L136 字段定义；L363–364 diagnostics | 显式标注为 `diagnostic-only / negative-disambiguation context`；明确排除在 Slice 1–3 positive closure 之外 | **已修复** |
| DS-P5 | 低 | 新旧 `table_family` 字段（`required_table_family_any` vs `allowed_table_families`/`rejected_table_families`）共存时优先级缺失 | plan L237–239 consumption by residual closure | 明确定义：新字段非空时忽略旧字段；reject 优先于 allow；旧字段 raw-context 匹配不得覆盖新字段拒绝 | **已修复** |

---

## Core Boundary Re-check

| Boundary | 状态 | 证据 |
|----------|------|------|
| NOT_READY | PASS | L3 `HANDOFF_READY_NOT_READY` |
| candidate-only | PASS | L16 |
| repository-mediated annual-report access | PASS | L25–26；L181 |
| no direct PDF/cache/source-helper access | PASS | L18–19；L484 |
| no live/source acquisition/provider/LLM/analyze | PASS | L20；L456 |
| no source truth acceptance | PASS | L19–20 |
| no baseline promotion | PASS | L21 |
| no parser replacement | PASS | L22 |
| no full field correctness claim | PASS | L23 |
| no release/PR readiness | PASS | L24 |
| no Service/UI/Host/renderer direct parser/PDF/cache access | PASS | L484 |
| pure-helper boundary (no file reads, no repository calls) | PASS | L394 |

所有核心边界保持完整，未因修复引入新的边界违规。

---

## Fail-Closed Behavior Re-check

### S6-F041 (benchmark)

| 检查点 | 状态 | 证据 |
|--------|------|------|
| benchmark 仅在有 benchmark label 时闭合 | PASS | L330 "Remains RESIDUAL unless benchmark-labeled context is proven" |
| investment-objective context 被拒绝 | PASS | L327–328；L413 per-residual 表 |
| section/ proximity/ value equality 不构成证明 | PASS | L329 "Do not close it from investment-objective wording, section proximity, text equality, or expected field name" |
| stop condition 覆盖 | PASS | L476–477 |

S6-F041 的 fail-closed 行为完整且无歧义。

### S6-F049/S6-F050 (equity/stock same-value case)

| 检查点 | 状态 | 证据 |
|--------|------|------|
| 同值不可作为闭合依据 | PASS | L260–262；L413–414 per-residual 表 |
| hierarchy 无法区分时保持 RESIDUAL | PASS | L262 "keep S6-F049 and S6-F050 as RESIDUAL" |
| value equality/field name/row order 被显式排除 | PASS | L254（proof requirement）；L478 stop condition |
| hierarchy 证明要求明确：distinct row_index 或 distinct proven row_hierarchy_path | PASS | L260–261 |
| field-specific hierarchy 定义完整（equity=aggregate, stock=child under equity） | PASS | L265–270 |

S6-F049/S6-F050 的 fail-closed 行为完整且无歧义。

---

## New Blocker Check

对修复后的 plan 全文重新扫描，检查是否因修复引入了新的阻塞性歧义或矛盾：

- DS-P1 修复在 L134（字段定义表）和 L349–350（coercion contract）两处一致，无矛盾。
- DS-P2 修复新增的推导优先级（L255, L284）与 Slice 2 实现指导（L412–415）一致，share-class derivation 和 period-context derivation 的结构对称、可实施。
- DS-P3 修复（L346–348）将 `_coerce_cell()` 的职责收窄为纯数据转换，与 Slice 1 描述一致。`_classify_bundle_tables()` 作为独立步骤引入，无循环依赖。
- DS-P4 修复（L136, L363–364）标注 diagnostic-only 后与 stop conditions 和 per-residual 表无冲突。
- DS-P5 修复（L237–239）优先级规则与 rejected-before-allowed（L237）一致，无矛盾。
- `_coerce_bundle()` 新增约束（L352–353：不从 cell 推断 bundle enrichment_status）是防御性约束，不与任何其他规则冲突。

**结论：未引入新阻塞性发现。**

---

## Residual Risks

| Risk | 严重度 | 说明 |
|------|--------|------|
| `_classify_bundle_tables()` 的具体实现细节（如何从可用字段中提取 table identity、table-level 信号不足时的降级策略）不在本 plan 范围内 | 低 | 属于 Slice 2 实施 gate 的职责；plan 已给出确定性分类规则表和冲突解决优先级，实施有足够指导 |
| `_has_share_class_context()` 的替换/包装方式在 Slice 2 中描述为"may be retained only as an internal derivation helper"，但未给出新 helper 的函数签名 | 低 | plan L412–415 已说明旧 helper 的保留条件和限制；函数签名细节属于实施 gate |
| plan 不授权 JSON 序列化/反序列化规则（L178），若未来 gate 需要规则可配置化，需额外 gate | 低 | 显式非目标，不阻塞本 gate |

无新增中等或以上严重度的 residual risk。

---

## Final Verdict

**PASS**

DS-P1 至 DS-P5 五个发现全部修复。核心边界（NOT_READY、candidate-only、repository-mediated、no source truth、no baseline promotion、no parser replacement、no full correctness、no readiness/release/PR）完整保持。S6-F041 和 S6-F049/S6-F050 的 fail-closed 行为完整且无歧义。未引入新阻塞性发现。

阻塞性发现数：0
