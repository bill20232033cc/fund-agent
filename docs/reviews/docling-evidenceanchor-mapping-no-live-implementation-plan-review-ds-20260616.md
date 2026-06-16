# Docling EvidenceAnchor Mapping No-live Implementation Plan Review — AgentDS

Date: 2026-06-16
Reviewer: AgentDS
Reviewed target: `docs/reviews/docling-evidenceanchor-mapping-no-live-implementation-plan-20260616.md`
Gate: `Docling EvidenceAnchor Mapping No-live Implementation Plan Review Gate`
Release/readiness: `NOT_READY`

## 1. Review Scope

Per plan §16 DS review focus:

- Whether the candidate output model enforces programmatic isolation from production `EvidenceAnchor`.
- Whether S1 parent-table resolution is deterministic enough and rejects ambiguous page/bbox cases.
- Whether S4/S5/S6 tuple resolution is complete and fail-closed.
- Whether section stability and row locator rules are mechanically testable.
- Whether no-live stop-path tests are sufficient for missing parent table, missing section, missing page and ambiguous locator cases.

Extended per review focus in the gate command:

- Does the implementation plan fully carry controller binding constraints?
- Does candidate/production isolation avoid bare production EvidenceAnchor outputs?
- Is module ownership correctly limited to Fund documents candidate internals?
- Are S1 and S4/S5/S6 parent-table resolution strategies deterministic and fail-closed?
- Are section stability and row_locator rules mechanically testable?
- Is the no-live test matrix sufficient and correctly scoped?
- Does the plan avoid production parser replacement, source truth/full correctness/readiness claims and live/provider/source commands?

## 2. Assumptions Tested

| # | Assumption | Verdict |
|---|---|---|
| A1 | Plan carries all six controller binding constraints from DS-F1/F2/F3/F4/MIMO-F1/MIMO-F2/MIMO-F3/MIMO-F4/MIMO-F5/MIMO-F6 | PASS — see §3 |
| A2 | Candidate output model (§6) achieves programmatic isolation from production EvidenceAnchor | PASS — see §4 |
| A3 | Module ownership (§4, §5) correctly limits to Fund documents candidate internals | PASS — see §5 |
| A4 | S1 parent-table resolution (§8) is deterministic and fail-closed for all defined cases | PASS_WITH_FINDING — see DS2-F1 |
| A5 | S4/S5/S6 tuple resolution (§9) is complete and fail-closed | PASS_WITH_FINDING — see DS2-F2 |
| A6 | Section stability rules (§10) are mechanically testable | PASS_WITH_FINDING — see DS2-F3 |
| A7 | Row locator rules (§11) are mechanically testable | PASS |
| A8 | No-live test matrix (§12) is sufficient and correctly scoped | PASS_WITH_FINDING — see DS2-F4 |
| A9 | Plan avoids all forbidden claims and commands (§2, §13, §14, §15) | PASS |
| A10 | Plan is code-generation-ready for implementation | PASS_WITH_FINDINGS |

## 3. Controller Binding Constraint Carry-through

### 3.1 Full mapping of controller constraints to plan sections

| Controller Constraint | Source | Plan Section | Carry-through | Assessment |
|---|---|---|---|---|
| Candidate/production programmatic boundary | DS-F1 disposition | §6 (Candidate Output Model Strategy) | Full | CandidateEvidenceAnchorFields mirrors without subclassing; no to_evidence_anchor method; candidate metadata mandatory; tests assert no bare EvidenceAnchor |
| Module location to Fund documents candidates | DS-F2 / MIMO-F1 disposition | §4 (Future Allowed Write Set), §5 (Module Ownership) | Full | Explicit file paths under `fund_agent/fund/documents/candidates/`; Service/Host/UI/renderer/quality-gate import forbidden |
| S1 parent-table deterministic resolution | DS-F3 / MIMO-F2 disposition | §8 (S1 Full-schema Parent-table Resolution) | Full | 5-step priority-ordered resolution with 4 forbidden heuristics and stop condition |
| S4/S5/S6 section hierarchy verification | DS-F4 disposition | §10 (Section Stability Rules) last paragraph | Full | Explicit check for section hierarchy existence, heading-path fallback, fail-closed default |
| Section stability criteria | MIMO-F3 disposition | §10 (Section Stability Rules) | Full | Three stable conditions, five unstable conditions, explicit stop behavior |
| Table-level row_locator default | MIMO-F4 disposition | §11 (Row Locator Rules) table row | Full | `row_locator=null` for table-level; no ordinal unless separately accepted |
| Test strategy with happy/stop paths | MIMO-F5 disposition | §12 (No-live Test Matrix) | Full | 14 test cases covering S1/S4/S5/S6 happy paths and all required stop paths |
| Paragraph row_locator default | MIMO-F6 disposition | §11 (Row Locator Rules) paragraph row | Full | `row_locator=null` for paragraphs; future semantics require separate gate |

### 3.2 Verdict on constraint carry-through

All controller binding constraints are explicitly mapped to plan sections with verifiable detail. No constraint was dropped, weakened, or reinterpreted. This is the strongest part of the plan.

**PASS.**

## 4. Candidate/Production Isolation Assessment

### 4.1 Programmatic boundary analysis

Plan §6 achieves isolation through three mechanisms:

1. **Type separation**: `CandidateEvidenceAnchorFields` mirrors `EvidenceAnchor` fields but is a distinct type that "must not subclass it."
2. **Wrapper metadata**: `CandidateEvidenceAnchorMapping` wraps fields with `candidate_source="docling"`, `candidate_only=True`, `field_correctness_status="not_proven"` — all mandatory and programmatically checkable.
3. **Negative contract**: Explicitly forbids methods named `to_evidence_anchor`, `as_evidence_anchor`, `to_production_anchor` or equivalent.
4. **Test enforcement**: §6 states "Tests must assert the public mapping API does not return bare `EvidenceAnchor` objects or `list[EvidenceAnchor]`."
5. **Package boundary**: §5 states "must not be imported directly by Service, Host, UI, renderer or quality gate code." Combined with `fund_agent/fund/documents/candidates/` location, the package boundary provides structural isolation.

This is a material improvement over the prior plan's convention-only approach (`candidate_only=true` in `note`). The type system enforces the boundary — code that expects `EvidenceAnchor` will not accept `CandidateEvidenceAnchorFields`. Production evidence store insertion code would need to explicitly convert candidate types, creating a deliberate friction point.

### 4.2 Edge case: what prevents future code from adding a production conversion helper?

The plan explicitly forbids production-admission methods in §6 and limits the write set to `candidates/` in §4. The risk of a future worker adding production conversion in a separate gate is out of scope. The plan correctly constrains this implementation slice.

### 4.3 Source kind in candidate fields

§6 allows `source_kind="annual_report"` inside `CandidateEvidenceAnchorFields` only, with the wrapper type enforcing candidate status. The wrapper carries `candidate_source="docling"` and `candidate_only=True` as distinct metadata. The `source_kind` field inside candidate fields expresses annual-report evidence semantics (consistent with current field semantics), but the wrapper prevents it from being confused with production.

**PASS.**

## 5. Module Ownership Assessment

Plan §4 defines an explicit allowed write set of 6 paths, all under `fund_agent/fund/documents/candidates/` (plus test file and README). §5 explicitly forbids imports from Service, Host, UI, renderer, or quality gate. §5 also declares the module "must not call Docling, parser cache, source helpers, PDF files, live acquisition, FundDocumentRepository, provider/LLM, analyzer or checklist commands."

The recommended API surface (`map_candidate_locator_to_anchor_candidate`, `map_candidate_document_anchor_candidates`) returns candidate types, not bare production types. The `__init__.py` rule restricts exports to test-required symbols only.

Forbidden future writes (§4) explicitly list `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, and all production-layer modules.

**PASS.**

## 6. S1 Parent-table Resolution Assessment

### 6.1 Determinism analysis

Plan §8 defines a strict 5-step priority order:

1. Explicit parent table reference on cell object
2. Structural containment in candidate JSON (cell nested under table node)
3. Explicit shared table identifier
4. Bbox containment — only when exactly one table on same page contains cell bbox
5. Stop with `cannot_resolve_parent_table`

Four heuristics are explicitly forbidden:
- Nearest previous table by document order without structural/bbox proof
- Page-only matching when multiple tables exist
- Heading/table title text similarity
- Synthetic table ids from cell-only metadata

### 6.2 Finding: S1 multi-page table bbox containment is not addressed

- **位置**: §8 step 4 bbox containment rule
- **问题类型**: 切片过粗
- **当前写法**: "allow bbox containment only when exactly one table on the same page contains the cell bbox"
- **反例/失败场景**: A table spans multiple pages in the candidate JSON structure. Its bbox on page N may contain only part of the table, while cells on page N+1 belong to the same logical table but have bbox coordinates on page N+1. If the candidate JSON splits the table into per-page table objects, step 4 works correctly (each page has its own table object). But if the candidate JSON represents the multi-page table as a single object with a page-spanning bbox or multiple page references, step 4's "same page" constraint could fail to match cells to their parent table.
- **为什么有问题**: The coverage evidence (S1: 95 tables, 3493 cells) does not confirm how multi-page tables are represented in S1 candidate JSON. Docling may split tables per-page or maintain a single logical table. Without knowing which, the implementation agent needs to handle both cases or risk `cannot_resolve_parent_table` on valid cell-table relationships.
- **直接证据**: Plan §8 step 4 uses "same page" constraint without addressing multi-page table representation; S1 coverage evidence shows 95 tables across pages but does not document how page-spanning tables are modeled in Docling JSON output.
- **影响**: 实施 Agent 可能对跨页表的 cell 误判为无法解析父表，导致 S1 cell 映射产出低于实际可达水平。
- **建议改法和验证点**:
  1. Implementation agent should first inspect S1 candidate JSON to determine whether tables are per-page or span pages.
  2. If per-page, current rule is sufficient.
  3. If page-spanning, step 4 should be extended: "bbox containment on any page where the table appears, with the same uniqueness constraint."
- **修复风险（低）**: 实施 Agent 第一步检查候选 JSON 即可澄清。
- **严重程度（低）**: 不阻塞本 plan；实施开始时一次检查即可解决。

### 6.3 Stop-path coverage

Plan §8 requires stop-path tests for: ambiguous same-page tables, missing parent links, missing/ambiguous bbox containment. These are explicitly enumerated in the test matrix (§12: S1 cell stop: ambiguous bbox, S1 cell stop: page-only table candidate).

**PASS on determinism. One low-severity finding on multi-page table edge case (DS2-F1).**

## 7. S4/S5/S6 Tuple Resolution Assessment

### 7.1 Completeness analysis

Plan §9 defines tuple-based resolution with five explicit rules:

1. Exact `table_id` match to table entry in same candidate document
2. Confirm `table.page_number`
3. Confirm `cell_index`, `row_start`, `column_start` presence
4. Confirm no duplicate tuple under same `table_id`
5. Emit cell candidate only when all fields present and unique

Three stop reasons: `missing_parent_table_context`, `missing_page_number`, `missing_cell_position`, `ambiguous_cell_tuple`.

### 7.2 Finding: table_id availability in S4/S5/S6 lightweight schema is unvalidated

- **位置**: §9 S4/S5/S6 resolution rules
- **问题类型**: open question 未收敛
- **当前写法**: §9 rules assume S4/S5/S6 candidate JSON tables carry `table_id`. The last paragraph acknowledges the risk: "If future evidence shows S4/S5/S6 have no table entry to match table_id, implementation must fail closed for cell anchors instead of creating table ids from cell tuples."
- **反例/失败场景**: The S4/S5/S6 lightweight schema was produced by runtime-containment Docling conversion. Coverage evidence shows `cell_locator_pct: 100` for all samples, but does not state whether table objects in these schemas carry an explicit `table_id` field. If `table_id` is absent from table objects, rule 1 (exact `table_id` match) fails for every cell, producing zero S4/S5/S6 cell anchors.
- **为什么有问题**: This is honestly acknowledged in the plan (§9 last paragraph), but the test matrix (§12) has a "S4/S5/S6 cell happy path" case that assumes `table_id` is available. If it's not, the implementation agent will discover this at implementation time, not planning time.
- **直接证据**: Plan §9 last paragraph: "If future evidence shows S4/S5/S6 have no table entry to match table_id..."; test matrix §12 lists "S4/S5/S6 cell happy path" as expected to pass; plan §3 "Direct Evidence Inputs" declares bounded accepted facts as "candidate-only", not verification of S4/S5/S6 table schema internals.
- **影响**: 实施 Agent 可能在实现时发现 S4/S5/S6 cell happy path 不可达；如 `table_id` 缺失，需改为全部 fail-closed，测试预期需调整。
- **建议改法和验证点**:
  1. Implementation gate should, as its first verification step, inspect S4/S5/S6 candidate JSON for table `table_id` presence.
  2. If absent, the S4/S5/S6 cell happy path test should change to a stop-path test documenting that cell mapping is blocked by absent `table_id`.
- **修复风险（低）**: 实施开始时一次检查即可解决；plan 已经诚实标注。
- **严重程度（低）**: Plan 已显式承认风险，不是隐藏假设。

**PASS with one deferred finding (DS2-F2).**

## 8. Section Stability Rules Assessment

### 8.1 Mechanical testability

Plan §10 defines:
- **Stable**: explicit section id (1:1 mapping), nearest enclosing section hierarchy (unique parent), normalized heading path (1:1 deterministic mapping)
- **Unstable**: missing section id, multi-match heading path, page-proximity-only, keyword-inferred, fund-analysis template chapter inference
- **Stop behavior**: blocked with `missing_section_context` or `unstable_section_context`; no `section_id=null` anchors; no template chapter id inference

The criteria are binary (stable vs unstable) with explicit classification rules. Each rule is independently testable: given a candidate block with known section context, the implementation must produce a specific stable/unstable verdict. This is mechanically testable.

### 8.2 Finding: Section keyword family list is not specified

- **位置**: §10 section stability rules, stable condition 1 and 3
- **问题类型**: 契约缺失
- **当前写法**: "explicit candidate section id is present and maps one-to-one to a known annual-report section family" and "normalized heading path deterministically maps to one annual-report section family with no multi-match ambiguity"
- **反例/失败场景**: The implementation agent needs a concrete list of "known annual-report section families" to match against. Without this list, the agent must either: (a) extract section names from existing code (e.g., `locate_sections.py`), (b) use the CHAPTER_CONTRACT chapter names from the fund analysis template, or (c) invent its own list. Different choices produce different mapping results.
- **为什么有问题**: "One-to-one mapping to known section family" is the core stability criterion for sections. The set of known families is a dependency that determines mapping yield. The plan defers specifying this set to the implementation agent.
- **直接证据**: Plan §10 references "known annual-report section family" three times without a pointer to where the section family list is defined; `docs/design.md` does not contain a canonical annual-report section family enumeration; existing code in `locate_sections.py` or extractor modules may contain section name patterns but the plan does not reference them.
- **影响**: 实施 Agent 可能选择与现有代码不一致的 section family 列表；不同列表产生不同的稳定/不稳定裁决和映射产出。
- **建议改法和验证点**:
  1. Plan should reference or the implementation gate should specify: the section family list is derived from existing `locate_sections.py` section patterns, OR from the CHAPTER_CONTRACT chapter names, OR from a new explicit enumeration.
  2. The chosen list should be documented in the implementation module's docstring.
- **修复风险（低）**: 实施 Agent 可以从现有代码中提取合理列表。
- **严重程度（低）**: 不阻塞，但增加实施 Agent 决策负担。

**PASS with one low-severity finding (DS2-F3).**

## 9. Row Locator Rules Assessment

Plan §11 defines clear per-anchor-kind rules in table form. Each rule has a specific format string or `null` default:

- Heading: `row_locator=null`
- Paragraph: `row_locator=null`
- Table-level: `row_locator=null`
- Cell: `cell:r<row_start>:c<column_start>:idx<cell_index>` with S1 omission rule
- Derived metric: out of scope

The cell format is parameterized with explicit field names (`row_start`, `column_start`, `cell_index`). The S1 omission rule is deterministic: "S1 may omit idx only when no cell_index exists and row/column are deterministic."

Each rule maps to a testable assertion: given specific input fields, the output `row_locator` must match the expected format string or be `null`.

**PASS.**

## 10. No-live Test Matrix Assessment

### 10.1 Coverage analysis

The test matrix (§12) defines 14 cases. Let me map each to the plan's stop conditions and happy paths:

| Test case | Covers | Assessment |
|---|---|---|
| S1 heading happy path | Heading + section + page | ✓ |
| S1 paragraph happy path | Paragraph + section + page | ✓ |
| S1 table happy path | Table + section + table_id + page | ✓ |
| S1 cell happy path (parent pointer) | Cell + explicit parent link | ✓ |
| S1 cell happy path (bbox) | Cell + unique bbox containment | ✓ |
| S1 cell stop: ambiguous bbox | Stop: cannot_resolve_parent_table | ✓ |
| S1 cell stop: page-only | Stop: multiple tables on page, no proof | ✓ |
| S4/S5/S6 cell happy path | Tuple-based cell mapping | ✓ (assumes table_id available) |
| S4/S5/S6 stop: missing tuple | Stop: missing cell position fields | ✓ |
| S4/S5/S6 stop: duplicate tuple | Stop: ambiguous_cell_tuple | ✓ |
| Missing section stop | Stop: missing/unstable section | ✓ |
| Missing page stop | Stop: missing page for Docling PDF | ✓ |
| Source-kind boundary | No new production source_kind | ✓ |
| Candidate metadata | required fields present | ✓ |
| Production isolation | No bare EvidenceAnchor | ✓ |
| Service/Host/UI containment | Import boundary scan | ✓ |

### 10.2 Finding: No test case for S4/S5/S6 section-hierarchy-absent scenario

- **位置**: §12 test matrix
- **问题类型**: 测试缺口
- **当前写法**: Test matrix has one generic "missing section stop" case, and S4/S5/S6 cell cases assume section context is resolvable.
- **反例/失败场景**: Plan §10 explicitly states: "For S4/S5/S6, the implementation must first verify whether section hierarchy exists in the lightweight candidate object. If it does not exist, it may use deterministic heading-path mapping only when one-to-one; otherwise it must accept low yield and fail closed for affected blocks." The test matrix does not have a dedicated case for this scenario. If S4/S5/S6 lack section hierarchy AND heading-path mapping fails, the implementation would produce blocked records, but this specific path is untested.
- **为什么有问题**: The plan's §10 S4/S5/S6 handling is the most likely low-yield path. Without a dedicated test case, the implementation agent may not implement the section-hierarchy existence check or the heading-path-only fallback correctly.
- **直接证据**: Plan §10 last paragraph describes S4/S5/S6 section-hierarchy handling; plan §12 test matrix has no "S4/S5/S6 section hierarchy absent → heading-path fallback or fail-closed" test case.
- **影响**: S4/S5/S6 section resolution behavior may be untested for the most likely failure mode.
- **建议改法和验证点**:
  1. Add test case: "S4/S5/S6 section hierarchy absent with ambiguous heading-path → blocked with missing_section_context"
  2. Add test case: "S4/S5/S6 section hierarchy absent with deterministic 1:1 heading-path → mapped candidate"
- **修复风险（低）**: 实施 Agent 可在实现时添加。
- **严重程度（低）**: 不阻塞 plan；实施 Agent 可补充。

### 10.3 Test fixture source

The test matrix defines fixture shapes ("explicit section + page locator", "cell links to parent table") but not where concrete fixture data comes from. The implementation agent will need to either:
- Use existing candidate JSON artifacts (S1/S4/S5/S6 coverage JSONs in `reports/docling-full-document-coverage/`)
- Create synthetic fixtures

This is acceptable for a no-live implementation plan — the implementation agent should have access to existing candidate coverage artifacts. The plan does not need to specify exact JSON fixture content.

### 10.4 Coverage target

The 80% single-file coverage target is consistent with `AGENTS.md` §5 testing strategy. The plan allows for a documented residual if 80% is not met, which is pragmatic.

**PASS with one low-severity finding (DS2-F4).**

## 11. Forbidden Claims and Commands Assessment

### 11.1 Production parser replacement

Plan §2 non-goals: "No source/test/runtime behavior change in this planning gate." §4 forbidden writes exclude production modules. §15 stop conditions trigger if "Implementation would return or store bare production EvidenceAnchor objects." The plan consistently avoids parser replacement language.

**PASS.**

### 11.2 Source truth / full correctness / readiness claims

Plan §2 non-goals: "No Docling conversion, live/network/EID/FDR/PDF/source acquisition..." §3: "Bounded accepted facts remain candidate-only... not source truth, full field correctness, production parser replacement, baseline promotion or readiness." §14: "No design truth sync, control truth sync, baseline disposition, release readiness or PR documentation update." §17: "Preserve candidate-only status and NOT_READY."

The final verdict in §18 uses `NOT_READY` consistently. Every section that touches evidence boundaries inserts a `NOT_READY` or `candidate_only` qualifier.

**PASS.**

### 11.3 Live/provider/source commands

Plan §13 validation commands are exclusively no-live pytest and git diff. §13 explicitly forbids "Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge." §15 stop condition: "Any future worker attempts live/source acquisition, Docling conversion, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge commands."

**PASS.**

## 12. Architecture Boundary Assessment

### 12.1 Layering

The plan places mapping logic at the correct layer: `fund_agent/fund/documents/candidates/` — inside Agent layer Fund documents, in the candidate internals subpackage. This is consistent with:
- `AGENTS.md` module boundary rules (Fund documents belong in Agent layer)
- `docs/design.md` §6.1 containment rule (Docling intermediate layer encapsulated in Fund documents)
- Design doc requirement that candidate representations must not be directly consumed by Service/Host/UI/renderer/quality gate

### 12.2 Dependency direction

The plan enforces a narrow dependency graph:
- Mapping module depends on: existing candidate models/locators under `candidates/`
- Mapping module must NOT depend on: Docling runtime, parser cache, source helpers, PDF files, live acquisition, FundDocumentRepository, provider/LLM, analyzer, checklist
- Mapping module must NOT be imported by: Service, Host, UI, renderer, quality gate

This is clean and minimal.

### 12.3 Overcoupling check

The plan avoids coupling candidate mapping to:
- Production EvidenceAnchor schema (uses separate candidate types)
- Production evidence store (no insertion path defined)
- Specific parser (works from abstract candidate locators)
- Service/Host/UI layers (import boundary enforced)

The mapping functions are defined as pure transformations from candidate locators to candidate anchor types. No I/O, no external dependencies.

**PASS across all architecture lenses.**

## 13. Findings

### Findings Table

| ID | Severity | Status | Summary |
|----|----------|--------|---------|
| DS2-F1 | Low | accepted-candidate | S1 multi-page table bbox containment not addressed (§8 step 4) |
| DS2-F2 | Low | deferred-candidate | S4/S5/S6 table_id availability unvalidated (§9 last paragraph) |
| DS2-F3 | Low | accepted-candidate | Section keyword family list not specified (§10 stable conditions) |
| DS2-F4 | Low | accepted-candidate | Test matrix missing S4/S5/S6 section-hierarchy-absent scenario (§12) |

### DS2-F1 — 未修复 — 低 — S1 多页表 bbox 包含未处理

- **位置**: §8 step 4 bbox containment rule
- **问题类型**: 切片过粗
- **当前写法**: "allow bbox containment only when exactly one table on the same page contains the cell bbox"
- **反例/失败场景**: S1 candidate JSON 中跨页表若表示为单对象含跨页 bbox 或多 page reference，step 4 的 "same page" 约束可能导致属于该表的 cell 无法匹配父表。
- **为什么有问题**: coverage evidence 未记录 S1 候选 JSON 中跨页表的表示方式（per-page split vs single logical table），实施 Agent 需要处理两种可能性。
- **直接证据**: Plan §8 step 4 "same page" 约束；S1 coverage 有 95 个表但未记录跨页表表示。
- **影响**: 低 — 实施 Agent 第一次检查 S1 候选 JSON 结构即可解决。
- **建议改法和验证点**: 实施 Agent 应先检查 S1 候选 JSON 中多页表是 per-page 还是跨页表示；如为跨页，step 4 应扩展为 "bbox containment on any page where the table appears."
- **修复风险（低）**:
- **严重程度（低）**:

### DS2-F2 — 未修复 — 低 — S4/S5/S6 table_id 可用性未验证

- **位置**: §9 S4/S5/S6 tuple resolution rules
- **问题类型**: open question 未收敛
- **当前写法**: §9 假定 S4/S5/S6 候选 JSON 中 table 对象携带 `table_id`，最后一段诚实承认 "If future evidence shows S4/S5/S6 have no table entry to match table_id, implementation must fail closed."
- **反例/失败场景**: 若 S4/S5/S6 轻量 schema 中 table 对象无显式 `table_id`，rule 1 对所有 cell 失败，S4/S5/S6 cell 映射产出为零。
- **为什么有问题**: Plan 诚实承认风险，但 §12 test matrix 的 "S4/S5/S6 cell happy path" 假定 `table_id` 可用。若不可用，该测试需改为 stop-path。
- **直接证据**: Plan §9 last paragraph；coverage evidence 未记录 S4/S5/S6 table schema 内部结构。
- **影响**: 低 — 实施 Agent 第一步检查 S4/S5/S6 候选 JSON 即可澄清。
- **建议改法和验证点**: Implementation gate 第一步验证 S4/S5/S6 table `table_id` 存在性；若缺失，cell happy path 测试改为 stop-path 测试。
- **修复风险（低）**:
- **严重程度（低）**:

### DS2-F3 — 未修复 — 低 — Section keyword family 列表未指定

- **位置**: §10 section stability rules
- **问题类型**: 契约缺失
- **当前写法**: "maps one-to-one to a known annual-report section family" 和 "deterministically maps to one annual-report section family" 引用 "known family" 但未指向定义位置。
- **反例/失败场景**: 实施 Agent 需要具体 section family 名称列表来做 1:1 匹配。不同来源（`locate_sections.py`、CHAPTER_CONTRACT、自拟列表）产生不同分类结果和映射产出。
- **为什么有问题**: Section family 列表是 section stability 判定的核心依赖，plan 未指定来源。
- **直接证据**: Plan §10 三次引用 "known annual-report section family" 但无指针；`docs/design.md` 无 canonical section family 枚举。
- **影响**: 低 — 实施 Agent 可从现有代码（`locate_sections.py`）提取合理列表并在实现模块 docstring 中记录。
- **建议改法和验证点**: Plan 或 implementation gate 应指定 section family 列表来源为现有 `locate_sections.py` section patterns。
- **修复风险（低）**:
- **严重程度（低）**:

### DS2-F4 — 未修复 — 低 — 测试矩阵缺少 S4/S5/S6 section-hierarchy-absent 场景

- **位置**: §12 test matrix
- **问题类型**: 测试缺口
- **当前写法**: Test matrix 有一个通用 "Missing section stop" 用例，S4/S5/S6 用例假定 section context 可解析。
- **反例/失败场景**: §10 显式要求 S4/S5/S6 先验证 section hierarchy 存在性，缺失时仅使用 heading-path 映射或 fail-closed。测试矩阵没有专项覆盖此路径。
- **为什么有问题**: 这是 S4/S5/S6 最可能的低产出路径，缺少专项测试意味着该关键行为未被验证。
- **直接证据**: Plan §10 last paragraph；plan §12 test matrix 缺少 "S4/S5/S6 section hierarchy absent" 测试用例。
- **影响**: 低 — 实施 Agent 可在实现时补充。
- **建议改法和验证点**: 添加 "S4/S5/S6 section hierarchy absent with ambiguous heading-path → blocked" 测试用例。
- **修复风险（低）**:
- **严重程度（低）**:

## 14. Accepted / Rewritten / Rejected / Deferred Findings

| Finding | Disposition | Reason |
|---------|-------------|--------|
| DS2-F1 | accepted-candidate | Multi-page table bbox handling is a narrow edge case; resolution requires one-time candidate JSON inspection by implementation agent |
| DS2-F2 | deferred-candidate | Plan already acknowledges the risk; implementation agent's first verification step resolves it |
| DS2-F3 | accepted-candidate | Section family list source is a minor specification gap; implementation agent can extract from existing code |
| DS2-F4 | accepted-candidate | Missing test case is narrow; implementation agent can add during implementation |

## 15. Residuals

| Residual | Owner | Next Handling |
|----------|-------|---------------|
| S1 multi-page table representation in candidate JSON | implementation agent | First verification step in implementation gate |
| S4/S5/S6 table_id field availability in lightweight schema | implementation agent | First verification step in implementation gate |
| Section keyword family canonical list | implementation agent + controller | Implementation gate should record chosen list in module docstring |
| S4/S5/S6 section-hierarchy-absent test case | implementation agent | Add during implementation gate |
| Candidate output model implementation detail (dataclass fields, exact method signatures) | implementation agent | Implementation gate design decisions |
| S4/S5/S6 heading-path mapping yield when section hierarchy absent | implementation agent + future evidence gate | Low yield is an accepted risk documented in plan §10 |

## 16. Open Questions

| # | Question | Recommended owner |
|---|---|---|
| Q1 | Does S1 candidate JSON represent multi-page tables as per-page objects or a single page-spanning object? | Implementation agent (first verification step) |
| Q2 | Do S4/S5/S6 lightweight schema table objects carry an explicit `table_id` field? | Implementation agent (first verification step) |
| Q3 | What is the canonical list of annual-report section families for 1:1 mapping? | Implementation agent (extract from `locate_sections.py` or CHAPTER_CONTRACT) |
| Q4 | Does S4/S5/S6 lightweight schema include section hierarchy, or only flat headings? | Implementation agent (first verification step, follow-through on plan §10) |

## 17. Reviewer Self-Check

- [x] Reviewed target, scope, source of truth and assumptions tested are written
- [x] Findings are evidence-based, adversarial, actionable, and not style/nit/speculation
- [x] Open questions, residual risks, tracking destination are separate from findings
- [x] Conclusion uses an allowed verdict
- [x] Output path is the exact path specified in gate command
- [x] Did not modify source/tests/runtime behavior
- [x] Did not modify control/design/startup docs
- [x] Did not run Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands
- [x] Did not stage, commit, push or open PR

## 18. Final Verdict

```text
VERDICT: PASS_WITH_FINDINGS
```

### Summary

The implementation plan fully carries all controller binding constraints. Candidate/production isolation is programmatic (type-level separation, not convention-only). Module ownership is correctly limited to Fund documents candidate internals. S1 and S4/S5/S6 parent-table resolution strategies are deterministic and fail-closed. Section stability and row_locator rules are mechanically testable. The no-live test matrix is sufficient in scope with one minor gap. The plan thoroughly avoids production parser replacement, source truth/full correctness/readiness claims, and live/provider/source commands.

Four low-severity findings (DS2-F1 through DS2-F4) identify narrow specification gaps that the implementation agent can resolve during implementation. None requires plan rejection or rewrite.

### Final recommendation

Accept this implementation plan and route DS2-F1 through DS2-F4 as informational notes for the `Docling EvidenceAnchor Mapping No-live Implementation Gate`. The plan is code-generation-ready for implementation.
