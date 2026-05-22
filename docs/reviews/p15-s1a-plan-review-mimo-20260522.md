# P15-S1A Plan Review — AgentMiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

P15-S1A plan 可以从 P15-S1 blocker 合理推进到 evidence-acquisition implementation，不存在阻断问题。Findings 均为非阻断观察，可在 implementation 阶段处理。

## Review Scope

- Plan: `docs/reviews/p15-s1a-tracking-error-source-contract-evidence-acquisition-plan-20260522.md`
- P15-S1 blocker plan: `docs/reviews/p15-s1-production-tracking-error-golden-evidence-plan-20260522.md`
- P15-S1 controller judgment: `docs/reviews/p15-s1-plan-review-controller-judgment-20260522.md`
- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`

## Review Criteria Assessment

### 1. Verdict 是否能从 P15-S1 blocker 合理推进到 evidence-acquisition implementation

**PASS**。Verdict `PROCEED_TO_EVIDENCE_ACQUISITION_IMPLEMENTATION` 正确推进：

- P15-S1 已接受 blocker：当前 reviewed artifacts 没有 `001548` direct observed `tracking_error` 值。
- P15-S1A 不直接跳到 golden implementation，而是先获取或证明可复核直接披露证据。
- 计划明确声明 implementation 唯一目标是生成 reviewed evidence artifact，不得先改 production golden rows。
- 若 artifact 仍无 direct observed disclosure，golden gate 继续 blocked。

推进逻辑清晰，不存在过早进入 golden implementation 的风险。

### 2. Source Contract 是否足以证明 direct observed tracking_error disclosure

**PASS**。Source contract 严谨完整：

- Acceptable evidence 要求同时满足 fund_code、report_year、document_kind、access_path、value_text、normalized_value、period_label、annualized、source_type、calculation_method、anchor、provenance 共 12 项字段要求。
- Rejected evidence classes 正确拒绝 7 类不可接受证据：
  - benchmark-only text — 只支持 `index_profile`
  - investment objective target/limit — 例如"年化跟踪误差控制在2%以内"是目标不是观测值
  - manager narrative — 叙述不是数值披露
  - standard deviation columns — 标准差不得误认为跟踪误差
  - calculated value — 属于后续 calculated tracking-error phase
  - ambiguous or conflicting hits — fail closed
  - unparseable percent — 不得入 golden
- Failure classification 区分 source-access failure（沿用既有 taxonomy）和 evidence-level failure（新增 8 类），覆盖完整。
- Stop conditions 覆盖 extractor 不是 direct、只有被拒绝类证据、锚点不完整、需要计算或外部依赖等场景。

### 3. 是否严格遵守 FundDocumentRepository / Fund Capability documents 边界

**PASS**。边界遵守严格：

- Evidence acquisition design 明确链路：`Evidence acquisition helper -> FundDataExtractor.extract() -> FundDocumentRepository.load_annual_report() -> documents layer`。
- 明确声明 Service、UI、Engine、renderer、quality gate、golden tooling 不得直接读取 PDF/cache/source adapter。
- 即使 implementation 增加临时或内部 helper，也必须依赖 `FundDocumentRepository` 或 `FundDataExtractor` 的公开边界。
- File ownership prohibited 列表明确禁止 runtime layers 直接 document access。

### 4. Evidence acquisition design 是否先 artifact、再 review、再另开 golden gate

**PASS**。Golden sequencing 正确：

1. P15-S1A evidence acquisition implementation 生成 reviewed evidence artifact。
2. Plan/review 或 controller judgment 接受该 artifact。
3. 只有 verdict 是 `ACCEPTED_DIRECT_DISCLOSURE` 时，才开启独立 golden implementation gate。
4. 独立 golden gate 才能修改 reviewed Markdown、strict JSON、必要测试和文档。
5. 若 verdict 是 `BLOCKED_NO_DIRECT_DISCLOSURE_EVIDENCE`，production `tracking_error` golden rows 继续 blocked/deferred。

顺序固定，不存在 evidence 和 golden 混在同一 implementation gate 的风险。

### 5. File ownership 和 validation 是否足够明确

**PASS**。File ownership 清晰：

- Allowed：evidence helper、extractor fix（仅当 artifact 证明 false negative）、extractor/evidence tests、document repository tests（仅当边界/provenance 回归）、implementation artifact、package/tests README（仅当新增公共 API 或测试类）。
- Prohibited：production golden、golden template/tooling、selected-fund source data、architecture/control truth、runtime layers、out-of-scope systems。
- Validation commands 具体且分层：evidence implementation 验证和 golden gate 验证分别列出。

## Findings

### F1 — Evidence helper 模块命名建议明确复用意图（INFO）

**Severity**: INFO
**Evidence**: Plan section "File Ownership For Future Implementation" 将 evidence helper 定位为 `fund_agent/fund/tracking_error_evidence.py`。
**Impact**: 当前 scope 限定为 `001548` / 2024，但该模块可能在未来其他基金或年份的 tracking_error 证据获取中复用。命名和接口设计若只考虑单次使用，后续复用时可能需要重构。
**Recommendation**: Implementation 阶段设计 helper 时，默认输入显式为 `fund_code="001548"`、`report_year=2024`，但函数签名应接受通用参数，便于后续复用。不需要在 plan 阶段修改。

### F2 — Evidence inventory 与 extractor 冲突时的 `needs_extractor_or_anchor_fix` 路径需 implementation 细化（INFO）

**Severity**: INFO
**Evidence**: Plan section "Implementation Steps" step 7：若 inventory 找到 direct-looking value 但 extractor 返回 missing，artifact 只能记录 `needs_extractor_or_anchor_fix`，不得直接改 golden。
**Impact**: 这是一个正确的 fail-closed 设计，但 implementation 阶段需要明确：该状态是否需要在 evidence artifact 中触发 extractor fix 作为前置条件，还是仅记录为 residual。
**Recommendation**: Implementation 阶段在 evidence artifact 中明确 `needs_extractor_or_anchor_fix` 的后续 owner 和 resolution path。Plan 阶段无需修改。

### F3 — 证据分类测试覆盖可补充 standard_deviation_only 和 unparseable 场景（LOW）

**Severity**: LOW
**Evidence**: Plan section "Acceptance Tests / Validation Commands" success signal 列出测试覆盖：target/limit、benchmark-only、narrative-only、standard deviation、ambiguous 和 unparseable cases。但 "File Ownership" 表中 `tests/fund/test_tracking_error_evidence.py` 只列出：direct value、target-only、benchmark-only、narrative-only、ambiguous、anchor completeness。
**Impact**: 两处列表不完全一致。File ownership 表遗漏了 `standard_deviation_only` 和 `unparseable` 两个分类的测试覆盖声明。
**Recommendation**: Implementation 阶段确保测试覆盖所有 8 类 evidence-level failure 分类。Plan 阶段无需修改，因为 success signal 已正确列出完整覆盖。

### F4 — `force_refresh` 参数的 reviewer 使用边界可更明确（INFO）

**Severity**: INFO
**Evidence**: Plan section "Implementation Steps" step 1：允许 reviewer 通过显式参数选择 `force_refresh=True` 重新走 repository，但不允许直接指定 PDF/cache 路径。
**Impact**: 当前描述足够清晰，但 implementation 阶段应确保 `force_refresh` 只影响 repository 内部缓存行为，不改变 evidence classification 逻辑。
**Recommendation**: Implementation 阶段在 helper docstring 中明确 `force_refresh` 仅控制 repository 缓存策略，不影响 evidence 分类。Plan 阶段无需修改。

## Non-blocking Observations

1. **Source contract 完整性**：12 项 acceptable evidence 字段要求和 7 类 rejected evidence classes 覆盖全面，没有遗漏明显边界情况。
2. **Failure taxonomy 分层**：source-access failure 沿用既有 `not_found`/`unavailable`/`schema_drift`/`identity_mismatch`/`integrity_error` 分类，evidence-level failure 新增 8 类，两层分类互不冲突。
3. **Non-goals 一致性**：与 P15-S1 controller guardrails 完全一致，没有引入新的 scope creep。
4. **Boundary compliance**：evidence acquisition helper 路径设计正确遵循 `FundDocumentRepository` 边界，不存在泄漏风险。

## Conclusion

P15-S1A plan 通过 review。Verdict 正确从 P15-S1 blocker 推进到 evidence-acquisition implementation；source contract 严谨拒绝所有非直接披露证据类别；边界遵守严格；golden sequencing 固定先 artifact 再 review 再 golden gate；file ownership 和 validation 明确。4 个 INFO/LOW findings 均可在 implementation 阶段处理，不阻断 plan acceptance。
