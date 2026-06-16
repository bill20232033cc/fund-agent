# Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Review — AgentDS

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Review Gate`
Reviewer: AgentDS
Date: 2026-06-16
Release/readiness: `NOT_READY`

## Scope

- **Mode**: current changes (implementation review against plan/controller judgment)
- **Branch**: `feat/mvp-llm-incomplete-run-artifacts`
- **Base**: plan artifact `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-20260616.md` and controller judgment `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-plan-controller-judgment-20260616.md`
- **Output file**: `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-review-ds-20260616.md`
- **Included scope**:
  - `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py` (full diff vs HEAD)
  - `tests/fund/documents/test_docling_evidence_anchor_mapping.py` (full diff vs HEAD)
  - `docs/reviews/docling-evidenceanchor-mapping-section-context-enrichment-no-live-implementation-evidence-20260616.md` (implementation evidence claims)
- **Excluded scope**: source acquisition, repository/cache, parser production, production `EvidenceAnchor`, CHAPTER_CONTRACT, Service/Host/UI/renderer/quality gate, provider/LLM, README/design/control docs, S1 full JSON regeneration
- **Parallel review coverage**: 无 — 本次 review 为主 reviewer 单线走读全部关键路径

## Validation Commands Re-executed

```text
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
→ 34 passed in 0.68s

uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
→ All checks passed!

git diff --check
→ passed
```

实施证据声称的 34 个测试全部通过，ruff 和 git diff --check 均无报错。

## Contract & Requirement Trace

逐项走读计划/controller judgment 中的 binding 要求：

| # | 要求 | 实现位置 | 走读结论 |
|---|------|---------|---------|
| 1 | candidate-only boundary | `CandidateEvidenceAnchorMapping.__post_init__` (L137-145), `CandidateEvidenceAnchorFields.__post_init__` (L90-96) | ✅ `candidate_only=True`, `field_correctness_status="not_proven"`, `source_truth_status="not_proven"` 在 dataclass `__post_init__` 中硬强制，未经通过无法构造 |
| 2 | public API 签名不变 | `map_candidate_document_anchor_candidates` (L172), `map_candidate_locator_to_anchor_candidate` (L241) | ✅ 签名未变；`section_index` 通过新增 private `_map_candidate_locator_to_anchor_candidate` 内部传递 |
| 3 | numeric heading closed-family guard | `_section_candidate_from_numeric_heading` (L1021-1046) | ✅ 顶层 1..10 数字必须通过 `_text_matches_section_family` 闭合族验证；未命中族则 `unsupported_heading_number=True` |
| 4 | TOC exclusion | `_is_toc_section` (L1106-1121), `_build_section_index` body_entries filter (L859) | ✅ 含"目录"/"toc"的 section node 被排除出 body_entries，不作为 span 起点 |
| 5 | duplicate fail-closed | `_duplicate_sections` (L935-953), `safety_reason_for_section` (L393-410) | ✅ 不同 top-level 起始页的同章节标记为 duplicate；page propagation 时通过 safety_reason 阻断 |
| 6 | inter-section monotonic | `_non_monotonic_sections` (L956-975) | ✅ 按 section number 排序后检查 page 倒序，倒序对双方均标记 non_monotonic |
| 7 | same-section child 不独立触发倒序 | `_duplicate_sections` 仅考虑 top_level_pages (L950-952)，`_non_monotonic_sections` 使用 `selected_pages` min over ALL entries | ✅ child heading 不计入 top_level_pages，不触发 duplicate；但其 page 参与 selected_pages min 计算（见 Finding 1） |
| 8 | SectionIndex built once & private | `_build_section_index` 在 `map_candidate_document_anchor_candidates` L190 调用一次，`_SectionIndex` 为 private frozen dataclass (L364-371) | ✅ 文档级 API 只构建一次；单块 API 每次调用构建（合理，无共享上下文） |
| 9 | page propagation & half-open spans | `_span_for_page` (L448-467), `_section_spans` (L978-996) | ✅ `[start, end)` 半开区间，`page >= end_page` 归入下一节；`page == end_page` 正确归属于 next section |
| 10 | table/cell parent inheritance only | `_map_cell` L527 对 table 解析 section，`_section_candidates_from_block` 移除了 `CandidateTableCell` 分支 | ✅ cell 的 section 完全来自 parent table；row/column label 不参与 section 推断 |
| 11 | blocked reason taxonomy | 全模块 grep `reason_code` | ✅ 新增 `unsupported_heading_number`, `duplicate_section_heading`, `section_order_not_monotonic`, `section_span_crosses_multiple_sections`；原有 `missing_section_context`, `unstable_section_context` 等保留不变 |
| 12 | no production EvidenceAnchor | 全模块 import 检查 | ✅ 无 `EvidenceAnchor` import，无生产类型引用 |
| 13 | test adequacy | 34 tests, 覆盖计划所有 fixture | ✅ 见下节详细分析 |
| 14 | S1 full JSON rejection | test `test_s1_full_json_schema_mismatch_remains_rejected` (L906-922) | ✅ `project_candidate_representation` 对 `schema_version: "s1.full.json"` 抛出 `ValueError` |

## Adversarial Failure Pass

沿以下攻击面逐项走读，每个入口至少追踪一个非 happy-path 输入：

### Auth / trust boundary
N/A — 本模块为纯数据映射，无 auth、无 tenant、无网络边界。

### Data loss / corruption / irreversible state
纯函数映射，输入 immutable dataclass，输出新构造的 `CandidateEvidenceAnchorMappingResult`。无共享可变状态，无持久化写入。无风险。

### Empty-state / null / missing inputs

- `_section_candidates_from_texts([])` → `_SectionCandidateExtraction((), False)` — 空输入无候选，后续由 `_resolve_section_id` 经 document section / page propagation / missing_section_context 链路处理 ✅
- `_build_section_index(document)` with `document.sections=()` → 空 body_entries → 空 grouped → 空 spans → `_span_for_page` 永远返回 None → page propagation 返回 `missing_section_context` ✅
- `_section_index_entries` 过滤 `page is None or page <= 0` ✅
- `_positive_pages_for_block` 过滤 `page_number is not None and page_number > 0` 及 table `page_numbers > 0` ✅
- `_page_number` for cell without own page: 回退到 parent_table ✅；parent_table 也无 page → None → `missing_page_number` ✅
- `_normalize_heading_text("   ")` → `""` → `if not normalized: continue` ✅

### Type errors / invalid enum / string values

- `_section_id_from_top_level("abc")` → `int()` raises `ValueError` → return None ✅
- `_section_number("§abc")` → `int("abc")` raises `ValueError` → return `10_000` (fallback sentinel) ✅，此 sentinel 使非法 section 在 `_non_monotonic_sections` 排序中排到最后，不会错误标记其他 section
- `_float_or_none(True)` → `isinstance(True, bool)` → return None ✅ (防止 bool 被当作 1.0)
- `_bbox_contains` 所有坐标可能为 None（via `_float_or_none`）→ 任一为 None 返回 False ✅

### Duplicate / conflicting / already-terminal

- `_duplicate_cell_tuple_exists` 扫描同表所有 cells ✅
- 两个独立 body section node 归一到同一 `§N` 且不同起始页 → `duplicate_section_heading` ✅
- 跨 span 多页 table → `section_span_crosses_multiple_sections` ✅

### Concurrency / ordering / stale state
N/A — 纯函数，无共享状态。

### Observability gaps
`CandidateEvidenceAnchorMappingBlocked` 包含 `reason_code`, `block_type`, `message`, `locator_summary` — 阻断原因可审计 ✅。`CandidateEvidenceAnchorFields.note` 包含完整 candidate-only 元数据 ✅。

### External protocol/API boundary
`_section_candidates_from_texts` 的 keyword matching (L838-841) 使用 `any(keyword in normalized for keyword in keywords)` — 子串匹配，可能误匹配。例如 `§3` 的 keyword "过去三年" 若出现在其他 section 的无关文本中会被提取。这是已有行为（未在本次实现中引入），且多候选触发 `unstable_section_context` 阻断。无新风险。

### Overcoupling
- `_SectionIndex` 为 internal private dataclass，不暴露给调用方 ✅
- `_build_section_index` 仅依赖 `CandidateRepresentationDocument.sections` ✅
- 无跨层穿透 import ✅
- `map_candidate_locator_to_anchor_candidate` 独立调用时自行构建 index，不依赖文档级 API 的共享状态 ✅

### Statically provable performance
- `_duplicate_cell_tuple_exists` 对每个 cell 做 O(N_cells) 扫描 — O(N²) per table。实际 table 中 cell 数量通常 < 1000，不构成实际性能问题。
- `_build_section_index` 在文档级 API 中构建一次，不在 block 循环中重建 ✅
- `map_candidate_locator_to_anchor_candidate` 每次调用重建 index — 单块 API 无共享上下文，属于合理 tradeoff ✅

### Test gaps (仅证明 happy path)
每个测试的 coverage 分析：

| 测试 | 覆盖路径 | 缺失 |
|------|---------|------|
| `test_document_mapping_emits_candidate_wrappers` | happy path: heading/paragraph/table/cell 全部 mapped | 无 |
| `test_s1_cell_can_resolve_parent_by_unique_bbox_containment` | bbox 父表解析 | 无 |
| `test_s1_cell_blocks_ambiguous_bbox_parent_resolution` | 多表 bbox 歧义阻断 | 无 |
| `test_s4_s5_s6_cell_blocks_missing_tuple_member` | missing tuple 阻断 | 无 |
| `test_s4_s5_s6_cell_happy_path_maps_with_exact_tuple` | S4/S5/S6 完整 tuple | 无 |
| `test_s4_s5_s6_cell_blocks_duplicate_tuple` | duplicate tuple 阻断 | 无 |
| `test_s4_s5_s6_maps_without_section_nodes` | 无 section tree 但 heading path 一一映射 | 无 |
| `test_s4_s5_s6_blocks_without_section_nodes_when_heading_path_is_ambiguous` | 无 section tree + 多匹配 → unstable | 无 |
| `test_missing_section_context_blocks_mapping` | 无任何 section 上下文 | 无 |
| `test_unstable_section_context_blocks_mapping` | 多 § heading path | 无 |
| `test_missing_page_blocks_mapping` | 缺页码 | 无 |
| `test_non_docling_candidate_is_blocked` | 非 Docling source | 无 |
| `test_numeric_heading_positive_examples` (4 cases) | 4 种 numeric heading 正向 | 无 |
| `test_unsupported_numeric_heading_patterns_block` (6 cases) | 6 种不支持的数字/中文编号 | 无 |
| `test_toc_section_node_is_excluded_from_body_span_seed` | TOC exclusion | 无 |
| `test_unsafe_toc_body_ambiguity_blocks_as_duplicate` | TOC/body 歧义 → duplicate | 无 |
| `test_duplicate_body_heading_blocks_page_based_propagation` | 重复正文标题 → duplicate | 无 |
| `test_inter_section_monotonic_violation_blocks_affected_span` | 倒序 → non_monotonic | 无 |
| `test_same_section_child_nodes_do_not_break_monotonic_ordering` | child heading 不触发倒序 | 见 Finding 1 |
| `test_page_based_table_inherits_stable_section_span` | page-based 继承 | 无 |
| `test_half_open_section_span_boundary_belongs_to_next_section` | 半开边界归属 | 无 |
| `test_missing_page_without_explicit_section_blocks` | 无 page + 无 section → missing_section_context | 无 |
| `test_cross_section_multi_page_table_blocks` | 跨 span 多页 table → cross_section | 无 |
| `test_cell_inherits_parent_table_section_without_row_or_column_label_inference` | cell 不从 label 推断 section | 无 |
| `test_cover_report_title_heading_without_section_context_is_blocked` | 封面标题 → missing_section_context | 无 |
| `test_s1_full_json_schema_mismatch_remains_rejected` | S1 full JSON 仍然拒绝 | 无 |

## Findings

### 01-未修复-低-`_section_spans` 末 span 无上界，末索引节之后的内容被吸收

- **入口/函数**: `_SectionIndex._span_for_page` → `_section_spans`
- **文件(行号)**: `evidence_anchor_mapping.py:448-467` (span lookup), `978-996` (span construction)
- **输入场景**: 文档最后一个稳定索引章节（按页码排序）之后存在未索引内容（如附录、声明页），且这些页码上的 block 触发 page-based propagation。
- **实际分支**: `_section_spans` 对最后一个 span 设置 `end_page=None`；`_span_for_page` 中 `span.end_page is not None and page >= span.end_page` 条件对 `end_page=None` 永不为 True，末 span 吸收所有 >= start_page 的页码。
- **预期行为**: 超出年报正文范围（§1–§10）的内容应 block 为 `missing_section_context`。
- **实际行为**: 末索引节之后的任何页码被归入末索引节。例如若 §8 是最后一个被索引的节（page 60），§9/§10 因 heading 未被识别而缺失，则 page 100+ 的附录内容会被错误分配到 §8。
- **直接证据**: L994: `next_start = ordered[index + 1][1] if index + 1 < len(ordered) else None` — 末 span 的 `end_page=None`。L465: `if span.end_page is not None and page >= span.end_page: continue` — None end_page 使条件短路，永不跳过。
- **影响**: 若真实文档中部分 §1–§10 section 因 heading 格式未被索引，其后的所有未索引页均被上一索引节吸收。静默错误分配 section，可能导致后续 table/cell 携带错误 `section_id`。
- **建议改法和验证点**: 为末 span 设置一个合理的上界（如 `max_page + 1`，其中 `max_page` 来自 section nodes 或 block pages 的最大页号），或引入哨兵 span 使超界页面返回 None。增加测试：末索引节之后的页面被 page propagation 时应 block 为 `missing_section_context`。
- **修复风险（低/中/高）**: 低 — 增补 span 上界是局部修改，且当前已有 `_span_for_page` 返回 None 时的 `missing_section_context` 处理路径。
- **严重程度（低/中/高/严重）**: 低 — 仅在真实文档中存在未索引的尾置内容时触发，且年报正文 §1–§10 通常覆盖全文档主体。若 §1–§10 全部被索引，此问题不触发。

### 02-未修复-低-`_is_child_section_heading` 仅检测含点号的数字/§ 子标题模式

- **入口/函数**: `_is_child_section_heading`
- **文件(行号)**: `evidence_anchor_mapping.py:1124-1145`
- **输入场景**: Section node 为某顶层节的子标题，但其 heading_text 不含点号模式（如纯文本子标题"股票投资组合"作为 §8 的子节点，section_id 与父节点不同）。
- **实际分支**: `_section_match` 检查 `"." in section_match.group(1)` 和 `_NUMERIC_HEADING_PATTERN` 结合 `"." in normalized.split(" ", 1)[0]`。纯文本子标题不含 § token 和数字前缀 → 两次检查均不命中 → `is_child_heading=False`。
- **预期行为**: 子标题被识别为 child，不计入 `_duplicate_sections` 的 `top_level_pages`。
- **实际行为**: 子标题被当作 top-level entry。若子标题与父标题在 `_section_index_entries` 中归一到同一 `§N` 且页码不同 → `top_level_pages` 含多个不同页码 → `duplicate_section_heading`。
- **直接证据**: L1137-1144: 仅检查 `_ANNUAL_SECTION_PATTERN` 含 "." 或 `_NUMERIC_HEADING_PATTERN` 前缀含 "."。L950-952: `top_level_pages = {entry.page for entry in entries if not entry.is_child_heading}` — false negative child 进入 top_level_pages。
- **影响**: 不产生错误映射（fail-closed → `duplicate_section_heading` 阻断），但阻断原因可能误导排查（实际是子标题未被识别为 child，而非真正重复标题）。
- **建议改法和验证点**: 未来如有证据表明非点号子标题模式在真实 Docling 输出中常见，可扩展 child detection。当前 plan 限定 closed pattern，暂不修改。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低 — fail-closed，不产生错误映射

### 03-未修复-低-`map_candidate_locator_to_anchor_candidate` 每次调用重建 `_SectionIndex`

- **入口/函数**: `map_candidate_locator_to_anchor_candidate` → `_build_section_index`
- **文件(行号)**: `evidence_anchor_mapping.py:263-268`
- **输入场景**: 调用方对同一文档的多个 block 分别调用 `map_candidate_locator_to_anchor_candidate`（而非使用批处理 `map_candidate_document_anchor_candidates`）。
- **实际分支**: L268: `section_index=_build_section_index(document)` — 每次调用都重建完整索引。
- **预期行为**: 单块 API 无共享上下文，重建是唯一选择；文档级 API 已正确实现一次构建。此行为符合设计约束（不改变 public API 签名即可传递 index）。
- **实际行为**: 对同一文档的 N 次单块调用重建 N 次索引。Section 数量通常 < 100，计算开销极小。非性能缺陷，但值得记录。
- **直接证据**: L263-268
- **影响**: 可忽略的性能开销。不影响正确性。
- **建议改法和验证点**: 如未来单块调用成为热路径，可考虑添加 `@lru_cache` 或要求调用方使用文档级 API。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

- **OQ1**: 真实 Docling section node 中，子标题不含点号模式的比例如何？若常见，Finding 02 的 `duplicate_section_heading` 阻断率会高于必要水平。需要 re-evidence gate 的真实 artifact 数据才能判断。
- **OQ2**: 年报末尾附录/声明页的页码分布如何？若 §10 之后仍存在 Docling section nodes 且被 `_section_index_entries` 过滤（因不归入 §1–§10），Finding 01 的末 span 吸收问题才会触发。需要真实 artifact 验证。

## Residual Risk

- **Table/cell yield on real artifacts**: 仍未证明。34 个测试全部使用 synthetic fixtures。真实 Docling 输出的 section 结构、heading 文本格式、TOC 存在形式可能与 synthetic 有差异。re-evidence gate 是必须的。
- **Field correctness**: 仍为 `not_proven`。
- **Source truth**: 仍为 `not_proven`。
- **S1 full JSON**: 仍未被当前 envelope schema 接受，属于已知 deferred residual。
- **Numeric heading normalization 的 false positive 风险**: 闭合关键词族的子串匹配 (`any(keyword in normalized)`) 对短关键词可能产生跨节误匹配。plan 已识别此风险。当前通过 `unstable_section_context`（多候选）和 `unsupported_heading_number`（无候选 + unsupported flag）做 fail-closed 兜底。
- **`_section_candidates_from_texts` keyword matching 无变更**: keyword 子串匹配是已有行为，未在本次实现中修改。真实误匹配率需要真实 artifact 验证。

## Final Verdict

```text
VERDICT: PASS_WITH_FINDINGS_NOT_READY
```

实施严格遵循 plan 和 controller judgment 的全部 binding 要求。34 个测试覆盖了计划中所有 synthetic fixture，ruff/git diff --check 均通过。三个 LOW severity findings 均为设计边界内的已知局限，不阻碍进入 re-evidence gate。release/readiness 维持 `NOT_READY`。
