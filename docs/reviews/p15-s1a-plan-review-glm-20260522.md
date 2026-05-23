# P15-S1A Plan Review — AgentGLM（2026-05-22）

## Reviewer

AgentGLM (independent plan review, phaseflow role)

## Review Target

`docs/reviews/p15-s1a-tracking-error-source-contract-evidence-acquisition-plan-20260522.md`

## Verdict

`PASS_WITH_FINDINGS`

P15-S1A plan 从 P15-S1 blocker 正确推进到 evidence-acquisition implementation，没有跳过证据采集阶段直接进入 golden implementation。Source contract 严格定义了可接受的 direct observed `tracking_error` disclosure 证据，正确拒绝了 benchmark-only、目标/限制、经理 narrative、标准差、calculated value 和歧义候选。边界遵守 FundDocumentRepository / Fund Capability documents 层约束。Evidence acquisition 设计遵循 artifact → review → 另开 golden gate 的顺序。以下 4 条 finding 均不阻断 implementation，但建议 controller 在接受时考虑。

## Inputs

- Plan: `docs/reviews/p15-s1a-tracking-error-source-contract-evidence-acquisition-plan-20260522.md`
- Upstream blocker: `docs/reviews/p15-s1-production-tracking-error-golden-evidence-plan-20260522.md`
- Upstream controller judgment: `docs/reviews/p15-s1-plan-review-controller-judgment-20260522.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Architecture rules: `AGENTS.md`

## Review Focus 1: Verdict Progression

**Assessment: Sound.**

P15-S1 blocker 结论为 `BLOCKED_NO_REVIEWED_DIRECT_DISCLOSURE_EVIDENCE`，确认当前仓库 artifact 中没有 `001548` 的 reviewed direct observed `tracking_error` 值。P15-S1A 正确地将 next step 定位为 evidence-acquisition implementation，而非直接尝试 golden rows：

- Verdict 明确为 `PROCEED_TO_EVIDENCE_ACQUISITION_IMPLEMENTATION`，不是 golden implementation。
- Implementation 目标窄化为：生成 reviewed evidence artifact，证明 `001548` 2024 年报是否存在可复核的 direct observed `tracking_error` 披露。
- Plan 第 9 步明确：只有 reviewed evidence artifact 被接受且 verdict 为 `ACCEPTED_DIRECT_DISCLOSURE` 后，才允许开启独立 golden gate。
- Golden Sequencing 固定 5 步顺序，P15-S1A 本身不改 production golden。

这是从 blocker 推进的最小可验证路径。不继续等待，也不计算 tracking error，而是在仓库边界内做一次系统性证据采集。逻辑成立。

## Review Focus 2: Source Contract Sufficiency

**Assessment: Thorough. All key rejection classes correctly identified.**

### Acceptable Evidence Fields Review

| Field | Assessment |
|---|---|
| `fund_code` = `001548` | 正确，禁止名称外推 |
| `report_year` = `2024` | 正确，绑定年报 |
| `document_kind` = `annual_report` | 正确 |
| `access_path` 经 `FundDocumentRepository` | 正确，强制边界合规 |
| `value_text` | 正确，要求实际披露数值 |
| `normalized_value` | 正确，仅允许从 value_text 解析，禁止 NAV/index 计算 |
| `period_label` | 正确，要求上下文可直接确定，禁止臆断 |
| `annualized` | 正确，要求年报直接支持，无法确定时不得默认 True |
| `source_type` = `direct_disclosure` | 正确 |
| `calculation_method` = `disclosed` | 正确 |
| `anchor` | 正确，表格需 page/table/row，正文需原文行 |
| `provenance` | 正确，要求完整链条 |

### Rejection Classes Review

| Rejected class | Correctness | Rationale |
|---|---|---|
| benchmark-only text | 正确 | 只能支持 `index_profile`，不能证明 `tracking_error` 值 |
| investment objective target/limit | 正确 | "控制在2%以内"是目标不是观测值 |
| manager narrative | 正确 | 定性叙述不是数值披露 |
| standard deviation columns | 正确 | σ(R) / σ(R_b) ≠ σ(R - R_b)，常见混淆风险被正确拦截 |
| calculated value | 正确 | 路由到 future calculated tracking-error phase |
| ambiguous or conflicting hits | 正确 | fail-closed，防止混入不确定值 |
| unparseable percent | 正确 | 防止无法验证的值进入 golden |

### Evidence-Level Failure Classification Review

8 类 failure classification 完整覆盖了从"完全没有提到"到"有候选但不够"的全谱系。每类都明确 action 为 `blocked; no golden`，无 fail-open 缺口。

**唯一值得注意的边界**：`anchor_incomplete` 类别的 action 为 `blocked until anchor is fixed`，而非 `no golden`。这意味着该类别在理论上允许修复 anchor 后重新尝试，而非永久拒绝。这是合理的——anchor 不完整是定位问题而非语义问题——但需确保 implementation 不会把 `anchor_incomplete` 当成软拒绝而放宽后续 golden gate 的标准。

## Review Focus 3: Boundary Compliance

**Assessment: Fully compliant. No boundary leakage detected.**

Evidence acquisition boundary 明确：

```text
Evidence acquisition helper
  -> FundDataExtractor.extract("001548", 2024)
     -> FundDocumentRepository.load_annual_report("001548", 2024)
        -> documents layer source orchestration and cache internals
  -> extract_performance(ParsedAnnualReport)
  -> reviewed evidence artifact
```

- Service、UI、Engine、renderer、quality gate、golden tooling 不得直接读取 PDF/cache/source adapter。
- 即使临时或内部 helper 也必须依赖 `FundDocumentRepository` 或 `FundDataExtractor` 的公开边界。
- Implementation step 5 扫描 `raw_text` 与 `tables` 是访问 `ParsedAnnualReport` 的公开属性，不绕过仓库。
- File ownership 表明确将 Service/UI/Engine/renderer/quality gate 行为变更列为 prohibited。
- Prohibited 列表包含 Dayu runtime、Host、Engine、tool loop、LLM writing 等全部非目标系统。

与 AGENTS.md 硬约束"对基金文档的存取，都应该只通过统一的文档仓库接口"、design.md §6.1 "生产代码不得绕过仓库直接读取 PDF、cache 或具体下载 helper" 完全一致。

## Review Focus 4: Evidence Acquisition Sequencing

**Assessment: Correct. Artifact → Review → Separate golden gate.**

Golden Sequencing 固定 5 步：

1. P15-S1A evidence acquisition implementation → reviewed evidence artifact
2. Plan/review 或 controller judgment 接受 artifact
3. 若 `ACCEPTED_DIRECT_DISCLOSURE` → 开启独立 golden implementation gate
4. 独立 golden gate 才能修改 reviewed Markdown、strict JSON、测试和文档
5. 若 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE` → golden 继续 blocked/deferred

P15-S1A implementation 本身不改 production golden。这一顺序防止了证据不足时提前修改 golden 的风险。

Implementation steps 1-9 的逻辑顺序也合理：
- 先获取 report（step 1-3）
- 运行现有 extractor 作为 primary structured decision（step 4）
- 做独立的关键词 inventory 作为交叉验证（step 5）
- 分类每个 candidate（step 6）
- 冲突时 fail closed（step 7）
- 输出 artifact（step 8）
- 明确后续 golden gate 条件（step 9）

Step 7 的 fail-closed 冲突处理特别值得肯定：当 inventory 找到 direct-looking value 但 extractor 返回 missing 时，artifact 只记录 `needs_extractor_or_anchor_fix`，不直接改 golden。这防止了 reviewer 在证据冲突时做出单方面判断。

## Review Focus 5: File Ownership, Validation, Over-Design, and Fail-Open Risks

**Assessment: Ownership clear. Validation comprehensive. Minimal over-design. No fail-open risk.**

### File Ownership

Allowed 和 prohibited 范围清晰。特别好的是：

- Extractor fix 被标记为 "only if artifact proves a false negative"，防止借 evidence acquisition 名义扩大 extractor 改动范围。
- Document repository tests 只在 "boundary/provenance regression is found" 时允许。
- README 只在 "stable public API is introduced" 时允许。
- Explicit prohibited 列表包含 golden 文件、source CSV、design/control docs、runtime layers、out-of-scope systems。

### Validation Commands

两层验证：
- Evidence implementation 层：extractor tests + evidence tests + repository tests + integration tests + ruff + diff check
- Future golden gate 层：golden prefill/answer tests + snapshot/score/quality gate tests + full suite + ruff + diff check

Success signals 明确且可验证。

### Over-Design Risk

**Low.** Plan 允许 "one-off helper/test" 作为 valid approach（"If the implementation adds no stable public API and only produces a reviewed artifact through a one-off helper/test"），避免强制将临时证据采集代码永久化。8 类 failure classification 表面上偏多，但每类都对应真实区分场景（target vs narrative vs standard deviation），且分类结果是人工 review 的输入而非自动化决策依据。

### Fail-Open Risk

**None detected.** 全链路 fail-closed：
- Identity mismatch → stop
- Source fail-closed categories (schema_drift, identity_mismatch, integrity_error) → no fallback, no golden
- Extractor/inventory conflict → fail closed, record only
- Ambiguous/conflicting → fail closed
- No direct disclosure → blocked
- Unparseable → blocked
- Anchor incomplete → blocked

## Findings

### F1: `anchor_incomplete` failure category 不在 validation success signals 的显式测试列表中

**Severity**: LOW

**Evidence**: Evidence-level failure classification 定义了 `anchor_incomplete` 类别（"有候选值但缺少可复核章节/表格/行锚点"），action 为 `blocked until anchor is fixed`。但 Acceptance Tests / Validation Commands 的 success signals 要求 "tests prove target/limit, benchmark-only, narrative-only, standard deviation, ambiguous and unparseable cases cannot become accepted direct disclosure"，未列出 `anchor_incomplete`。

**Impact**: Implementation 可能只覆盖了 success signals 列出的 6 种 rejection case，遗漏 `anchor_incomplete` 的专属测试。虽然 `anchor_incomplete` 的判定可能通过 anchor 存在性检查隐式覆盖，但显式测试更可靠。

**Recommendation**: 在 success signals 的 rejection-case 列表中显式加入 `anchor_incomplete`：例如 "a candidate with value but missing chapter/table/row anchor cannot become accepted"。

### F2: Implementation steps 未显式处理 `load_annual_report()` 异常或 None 返回路径

**Severity**: LOW

**Evidence**: Implementation steps 1-9 中，step 2 调用 `FundDocumentRepository.load_annual_report()`，step 3 验证 identity。但 steps 没有显式说明当 `load_annual_report()` 抛出异常（网络不可用、PDF 不存在等）或返回 None 时的处理。Failure classification 的 source-level 行覆盖了 `not_found`/`unavailable`/`schema_drift`/`identity_mismatch`/`integrity_error`，stop conditions 也隐式包含了这些情况，但 numbered steps 的执行流缺少明确的异常分支。

**Impact**: Implementation 阶段执行者可能需要自行判断异常映射到哪类 failure category。这不影响正确性（fail-closed 兜底），但增加了 implementation 的歧义成本。

**Recommendation**: 在 step 2 和 step 3 之间显式增加一步："若 `load_annual_report()` 抛出异常或返回 None，按 failure classification 记录对应 source category 并停止，artifact verdict 为 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`。"

### F3: "跟踪偏离度" 与 "跟踪误差" 的同义/异义处理未显式声明

**Severity**: INFO

**Evidence**: Implementation step 5 扫描关键词包含 `跟踪误差`、`跟踪偏离度`，但 plan 未显式说明这两者在 source contract 中是否被视为同一概念。在中国基金年报中，两者常被交替使用，但也存在部分报告将 "跟踪偏离度" 定义为日度差异而 "跟踪误差" 定义为其年化标准差的区分用法。

**Impact**: 不影响 plan 正确性——full keyword inventory 和 candidate classification 机制可以处理任何语义差异。但如果 implementation 将两者简单视为同义词，可能在 edge case 中产生 false positive（将日度偏离度误认为报告期跟踪误差）。

**Recommendation**: 无需修改 plan，但建议 implementation artifact 在分类 candidate 时显式记录 "跟踪偏离度" 命中的上下文语义判定。

### F4: Evidence helper 的生命周期策略未明确（永久模块 vs 一次性工具）

**Severity**: INFO

**Evidence**: File ownership 允许 `fund_agent/fund/tracking_error_evidence.py` 或等价 Fund Capability 模块。Success signals 提到 "If the implementation adds no stable public API and only produces a reviewed artifact through a one-off helper/test"。Plan 同时给出了两种路径：永久模块和一次性 helper/test。

**Impact**: 如果 implementation 选择永久模块路径，需考虑模块的长期维护成本和与其他 Fund Capability 模块的一致性。如果选择一次性路径，需确保测试覆盖仍足够（一次性代码更容易缺乏测试）。

**Recommendation**: 无需修改 plan。Controller 在接受 implementation artifact 时可评估最终选择的生命周期策略是否合理。

## Overall Assessment

P15-S1A plan 在以下方面表现优秀：

1. **正确的推进逻辑**：从 blocker → evidence acquisition → separate golden gate，每步都有明确的 stop condition 和 fail-closed 兜底。
2. **严格的 source contract**：12 字段 acceptable evidence + 7 类 rejected evidence + 8 类 failure classification，覆盖了实际年报中可能出现的所有跟踪误差相关文本形态。
3. **零边界泄漏**：所有年报访问严格遵守 FundDocumentRepository / Fund Capability documents 边界，没有绕过或例外。
4. **Fail-closed 全链路**：从 source failure 到 evidence classification 到 conflict resolution 到 golden decision，每一步都是 blocked 或 fail-closed，没有发现 fail-open 缺口。
5. **精确的 file ownership**：allowed 和 prohibited 范围明确，附带条件限制（如 extractor fix 仅在 false negative proven 时允许）。

2 条 LOW severity finding 是 implementation 阶段的细节完善，不影响 plan 本身的正确性和可执行性。2 条 INFO finding 是实施层面的考量，不构成 risk。

## Residual Verification

| Residual from P15-S1 controller judgment | P15-S1A plan coverage |
|---|---|
| "The next plan must define how to acquire or prove reviewed direct `tracking_error` disclosure evidence" | Plan 定义了 9 步 implementation，包括 repository access、extractor 调用、keyword inventory、candidate classification 和 artifact output |
| "Any future annual-report/source access must go through `FundDocumentRepository`" | Boundary section 和 implementation steps 全部通过 `FundDocumentRepository` |
| "Do not use benchmark-only, target/limit, or narrative evidence as a value proof" | Source contract 7 类 rejected evidence 明确拒绝 |
| "Do not calculate tracking error from NAV/index series" | Rejected evidence class "calculated value" 和 non-goals 明确排除 |
| "Do not introduce external index adapters, methodology/constituents extraction..." | Prohibited files/behaviors 和 non-goals 完整继承 |

## Conclusion

**Verdict: PASS_WITH_FINDINGS.** 4 条 finding（2 LOW + 2 INFO）均不阻断 implementation。Plan 从 blocker 推进到 evidence acquisition 的逻辑正确，source contract 足以证明 direct observed tracking_error disclosure 并正确拒绝不充分证据，边界合规，顺序正确，file ownership 清晰，无 fail-open 风险。
