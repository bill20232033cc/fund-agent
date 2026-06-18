# Docling Baseline Qualification Plan Review (MiMo)

Date: 2026-06-15

Reviewer: AgentMiMo (plan review worker only)

Review target: `docs/reviews/docling-baseline-qualification-plan-20260615.md`

Gate: `Docling Baseline Qualification Planning Gate`

## 1. Scope And Source Of Truth

**Reviewed target**: The plan artifact defining evidence gates A-F, sample matrix S1-S6, pass/fail thresholds, stop conditions and verdict criteria for deciding whether Docling qualifies as a baseline candidate for annual-report document representation.

**Source of truth consulted**:
- `AGENTS.md` — execution rules, FundDocumentRepository boundary, EID single-source policy
- `docs/design.md` — current production parser chain, FundDocumentRepository boundary, EvidenceAnchor schema, EID single-source policy, Docling candidate status
- `docs/implementation-control.md` — current gate state, accepted artifacts
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md` — Route A single-sample evidence facts
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-controller-judgment-20260615.md` — accepted mapping/normalization plan facts
- `docs/reviews/bounded-same-report-eid-html-render-discovery-controller-judgment-20260615.md` — accepted EID HTML render discovery facts

**Assumptions tested**:
- S1-S6 sample artifacts are available or acquirable.
- Gate thresholds are achievable given current evidence base.
- The plan preserves all critical project boundaries.
- The plan avoids overclaims beyond baseline candidacy.
- Hidden live/network requirements are explicitly handled.

## 2. Findings

### MIMO-P1-未修复-高-样本矩阵 S2-S6 缺少已证实的本地工件，Gate A 无法执行

- **位置**: §5 Required Sample Matrix, §6 Gate A Runtime Containment / Reproducibility Evidence
- **问题类型**: 不可直接实施
- **当前写法**: Plan 定义六个 fund/year 样本（S1 `004393/2025`, S2 `004393/2024`, S3 `004194/2024`, S4 `006597/2024`, S5 `017641/2024`, S6 `110020/2024`），但当前已接受的 Route A evidence 只覆盖 S1。S2-S6 的本地 PDF 工件、EID acquisition 状态、Docling conversion 可行性均无已接受的 evidence 证明。Gate A Inputs 列出"Existing or future EID-derived local annual-report PDFs inside repository/cache ownership"和"Candidate conversion runner or script defined by a later implementation plan"，但这两个输入都不存在。
- **反例/失败场景**: Implementation agent 启动 Gate A 时发现 S2-S6 没有本地 PDF 或 EID metadata，被迫中断或降低样本规模。最坏情况：agent 用非 EID 来源获取 PDF，违反 EID single-source policy。
- **为什么有问题**: Plan 的核心价值是用六样本矩阵证明 baseline candidacy。如果五分之四的样本工件不存在，plan 的前提假设就不成立。§5 "Expansion rule" 提到"controller-approved EID-only sample acquisition gate"，但该 gate 未定义、未排期、无 owner。这使得整个 plan 处于"先有鸡还是先有蛋"的状态：需要 EID acquisition gate 才能获取样本，但 acquisition gate 不在本 plan scope 内。
- **直接证据**: Route A evidence 只记录 `fund_code=004393, report_year=2025`。§5 扩展规则写"if any fund/year has missing local EID-controlled annual report artifact, the gate may add a replacement only through a controller-approved EID-only sample acquisition gate"——该 acquisition gate 未被定义。
- **影响**: Implementation agent 无法启动 Gate A；或被迫先实现 acquisition gate（超出本 plan scope），导致执行顺序混乱。
- **建议改法和验证点**: Plan 必须显式区分 S1（已有工件）和 S2-S6（需要 acquisition gate），并在 §11 "Recommended First Next Gate" 中把 EID-only sample acquisition 作为第一个必需前置 gate。当前 §11 已提到此 gate，但未说明它是 Gate A 的 blocker。
- **修复风险**: 低（只需在 plan 中显式声明前置依赖）

### MIMO-P2-未修复-高-Gate D 字段正确性阈值依赖不存在的 golden/reviewed 事实基线

- **位置**: §6 Gate D Field Correctness Comparative Evidence, §9 Acceptance Threshold Summary
- **问题类型**: 契约缺失
- **当前写法**: Gate D 要求"Identity fields: 100% exact match or fail-closed; any fund code/year/report type mismatch rejects baseline candidacy"和"High-priority field correctness versus accepted reviewed/golden facts: >= 98% exact/normalized match, 0 critical mismatch"。
- **反例/失败场景**: 除 S1 `004393/2025` 有七行 strict golden 外，S2-S6 都没有 accepted reviewed golden facts。Implementation agent 执行 Gate D 时发现没有比对基准，要么跳过（违反阈值定义），要么伪造基准（违反 evidence discipline）。
- **为什么有问题**: Gate D 的 98% 阈值隐含假设存在全样本 golden 基线。当前事实是只有 `004393/2025` 有七行 strict golden，且不覆盖 Gate D 要求的全部 field families（identity, source document, benchmark, manager, scale, fee, return, holdings, risk, bond top holdings, target fund holdings, QDII risk/exposure, manager holding）。即使 S1 也没有覆盖全部 field families 的 golden。
- **直接证据**: `docs/implementation-control.md` 记录 strict golden 2025 coverage 只有 seven tracked rows for `004393/2025`。§6 Gate D Inputs 列出"Current extractor/golden reviewed field sets where already accepted"——该条件对 S2-S6 不满足。
- **影响**: Gate D 阈值形同虚设，因为没有基线可以比对。Implementation agent 可能错误地跳过比对或用 route agreement 替代 golden truth（违反 §7 Decision rule）。
- **建议改法和验证点**: Gate D 应区分两个层次：(a) identity field 比对（可在三路由间做同源比对，无需 golden），(b) field correctness 比对（需要 golden/reviewed facts）。对于 (b)，plan 应显式声明 golden 基线的当前覆盖状态和不足，并为 S2-S6 定义 golden acquisition 前置 gate 或降低阈值为 "compared against same-report route agreement with explicit manual review queue"。
- **修复风险**: 中（需要调整 Gate D 设计，但不影响 plan 整体结构）

### MIMO-P3-未修复-中-EID-only 样本 acquisition gate 未定义，是所有后续 gate 的隐藏 blocker

- **位置**: §5 Expansion rule, §11 Recommended First Next Gate
- **问题类型**: 范围漂移 / 不可直接实施
- **当前写法**: §5 提到"controller-approved EID-only sample acquisition gate"作为缺失样本的获取机制。§11 推荐下一个 gate 为"Docling Baseline Qualification Runtime Containment And Sample Matrix Acquisition Planning Gate"，但该 gate 的 scope 只是"define exact EID-only sample acquisition status for S1-S6"——它本身也是 planning-only，不执行 acquisition。
- **反例/失败场景**: Plan 被 controller 接受后，implementation agent 需要 S2-S6 的本地 PDF。下一个 recommended gate 只规划 acquisition 状态，不实际获取工件。因此至少需要三个 sequential gates 才能开始 Gate A evidence execution：(1) acquisition status planning, (2) actual EID acquisition, (3) Gate A execution。
- **为什么有问题**: Plan 的 §11 没有显式说明 acquisition planning gate → acquisition execution gate → Gate A 的三步序列。这导致 controller 和 implementation agent 对"下一步是什么"的预期不一致。
- **直接证据**: §11 说"define the approved conversion runner interface and artifact schema"和"preserve no-live/no-conversion boundaries until the controller explicitly authorizes evidence execution"——明确说明 evidence execution 不在下一步。
- **影响**: Plan 被接受后可能产生多轮 planning gate churn，每轮只推进一小步，实际 evidence 距离很远。
- **建议改法和验证点**: §11 应显式声明 gate 依赖链：acquisition planning → acquisition execution → Gate A evidence。如果 acquisition execution 需要单独的 controller authorization gate，应在 plan 中显式声明。
- **修复风险**: 低（只需在 plan 中补充依赖链说明）

### MIMO-P4-未修复-中-Gate E 性能阈值未验证，硬件依赖未声明

- **位置**: §6 Gate E Performance / Cache / Cost Evidence
- **问题类型**: 契约缺失
- **当前写法**: "Cold conversion p95 <= 120 seconds per annual report on current CPU profile, or explicit controller-accepted hardware caveat"。Route A evidence 记录了 S1 的 conversion，但没有记录 conversion time。
- **反例/失败场景**: 如果 Docling 在当前硬件上 cold conversion 需要 180 秒，plan 阈值会 fail，但 plan 没有定义"controller-accepted hardware caveat"的具体条件。Implementation agent 可能因为阈值不现实而把正常结果误判为 `performance_regression`。
- **为什么有问题**: 120 秒阈值没有 evidence 基础。Route A evidence 只记录了 Docling 版本、配置和输出统计，没有 conversion time。阈值应该是 evidence-informed 的，而不是预设的。
- **直接证据**: `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md` 没有记录 conversion time。§6 Gate E "Inputs" 列出"Gate A conversion logs"——这些 logs 不存在，因为 Gate A 尚未执行。
- **影响**: Gate E 可能因为阈值不现实而 fail，导致整个 baseline qualification 失败，即使 Docling 实际性能合理。
- **建议改法和验证点**: Gate E 应使用两步法：(1) 先用 Gate A 的 conversion logs 建立 performance baseline，(2) 再用 baseline 设定合理阈值。或者，plan 应显式声明阈值是 tentative 的，需要在 Gate A evidence 后由 controller 校准。
- **修复风险**: 低（只需调整阈值设定方式）

### MIMO-P5-未修复-低-Gate B 100% 页面奇偶性阈值可能过于严格

- **位置**: §6 Gate B Full-document Coverage Evidence
- **问题类型**: 非最优方案
- **当前写法**: "Page count parity with pdfplumber for every PDF-backed sample: 100%"。
- **反例/失败场景**: 如果 pdfplumber 把一个跨页表格解析为两页，而 Docling 正确地识别为单个表格，页面计数会不一致，但 Docling 的表示实际上更准确。100% 奇偶性要求可能会惩罚正确的表示。
- **为什么有问题**: Gate B 的目标是"prove Docling covers complete annual-report structure"，不是"prove Docling exactly replicates pdfplumber's page counting"。页面奇偶性是 coverage 的代理指标，但 100% 要求把它变成了 pdfplumber 兼容性测试。
- **直接证据**: §7 Comparison Design 说 pdfplumber 的弱点是"Weak section/document representation; not a full semantic document object"——这暗示 Docling 可能在页面表示上与 pdfplumber 不同，且可能更优。
- **影响**: 可能导致 Gate B 在 Docling 表示实际更好的情况下 fail。
- **建议改法和验证点**: 降低阈值为 95%，或显式声明页面奇偶性差异需要分类（Docling 更优 vs Docling 缺失）。
- **修复风险**: 低

### MIMO-P6-未修复-低-Gate F 混合判定（Hybrid Primary）的路由组合语义不明确

- **位置**: §10 Verdict Criteria, `VERDICT: DOCLING_ELIGIBLE_AS_HYBRID_PRIMARY_NOT_READY`
- **问题类型**: 契约缺失
- **当前写法**: "Docling is strongest for PDF page/bbox/table representation, but EID HTML render is required for official rendered-source locators or specific table families. Field correctness passes only when route roles are combined with explicit priority and fail-closed rules."
- **反例/失败场景**: "route roles are combined" 没有定义组合方式。是 logical OR（任一路由成功即可）？logical AND（两路由都需要）？priority（Docling 优先，EID 兜底）？implementation agent 可能自行发明组合逻辑。
- **为什么有问题**: Hybrid disposition 是 plan 的三个主要 verdict 之一。如果组合语义不明确，implementation agent 在后续 implementation planning gate 中需要重新设计，导致 plan handoff 不完整。
- **直接证据**: §7 Decision rule 说"Hybrid disposition is valid only if each route has an explicit role and no consumer bypasses self-owned extractors / EvidenceAnchor / fail-closed classification"——这要求"explicit role"，但 Gate F verdict 没有定义 role。
- **影响**: 如果 plan 被接受为 hybrid verdict，后续 implementation planning gate 需要重新设计路由组合逻辑，增加 churn。
- **建议改法和验证点**: Gate F verdict 应定义至少一个具体的 hybrid routing 模式（如 Docling 作为 PDF representation primary, EID HTML render 作为 official rendered-source locator supplement），或显式声明 hybrid routing design 是后续 gate 的 scope。
- **修复风险**: 低

## 3. Open Questions

| # | Question | Why it matters | Suggested resolution |
|---|---|---|---|
| Q1 | S2-S6 的 EID acquisition 是否已有 evidence 证明某些样本可获取？ | 如果 small-golden five rows 的 2024 版本已有 EID acquisition proof，可以减少 acquisition gate 的 scope | 检查 `docs/design.md` §6.1 "small-golden 五行 ... / 2024 均已有 accepted live EID/FDR acquisition proof" |
| Q2 | Gate D "field families" 的 closed list 是否已定义？ | 如果 field families 没有 closed list，implementation agent 可能自行扩展或缩小比较范围 | 需要在 plan 中定义或引用已接受的 field family 列表 |
| Q3 | Gate A 的 "approved_docling_conversion_runner" 由谁实现？ | 该 runner 是 Gate A 的必要输入，但 plan 没有指定 owner | 需要在 plan 中指定 owner 或在 recommended next gate 中定义 |

## 4. Residual Risks

| Risk | Severity | Owner | Tracking destination |
|---|---|---|---|
| Docling model artifact provenance 仍为 benchmark-only，不是 production acceptance | 中 | Controller / model artifact owner | `Docling Model Artifact Provenance Acceptance Gate` (§12) |
| EID HTML render 无 PDF page numbers，hybrid locator 语义未定义 | 中 | Fund documents / EvidenceAnchor owner | `Hybrid Locator Semantics Planning Gate` (§12) |
| Field correctness 对 S2-S6 无 golden 基线 | 高 | Fund extractor/projection owner | `Docling Field Correctness Comparative Evidence Gate` (§12) |
| EID-only sample acquisition gate 未定义，是 Gate A 的前置 blocker | 高 | Controller / acquisition owner | Acquisition planning gate (§11) |

## 5. Reviewer Self-check

- [x] reviewed target and scope 写清
- [x] source of truth 和 assumptions tested 写清
- [x] findings 是 evidence-based、adversarial、可执行，且没有 style/nit/speculation
- [x] open questions 与 findings 分开
- [x] residual risks 与 findings 分开，有 tracking destination
- [x] conclusion 只能是 `pass`、`pass-with-risks` 或 `fail`
- [x] output path 使用本机系统时钟生成的 timestamp

## 6. Conclusion

**Verdict: `FAIL_REQUIRES_PLAN_FIX`**

**Rationale**: Plan 有两个高严重度 findings (P1, P2) 导致 plan 的核心前提不成立：

1. **P1**: 六样本矩阵中五分之四（S2-S6）没有已证实的本地工件，Gate A 无法执行。Plan 的核心价值是多样本证明，但样本不存在。
2. **P2**: Gate D 字段正确性阈值依赖不存在的 golden/reviewed 事实基线。除 S1 外，没有比对基准。

这两个 findings 意味着 plan 被接受后，implementation agent 无法直接执行任何 evidence gate。Plan 需要先修复样本工件获取和 golden 基线的前置依赖声明，才能作为可执行的 handoff artifact。

**Recommended controller disposition**:

1. 修复 P1：在 plan 中显式声明 S1（已有工件）和 S2-S6（需要 acquisition gate）的分离，并在 §11 中把 EID-only sample acquisition 定义为 Gate A 的必需前置 gate。
2. 修复 P2：在 Gate D 中区分 identity field 比对（无需 golden）和 field correctness 比对（需要 golden），并为 S2-S6 定义 golden acquisition 前置 gate 或降低阈值为 route agreement + manual review。
3. 修复 P3：在 §11 中显式声明 gate 依赖链。
4. P4-P6 为 nonblocking，可在 plan 修复时一并处理。
