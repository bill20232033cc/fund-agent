# Next Phase Selection Plan Review（2026-05-22 03:33:44）

## Reviewed Target

`docs/reviews/next-phase-selection-20260522.md`

## Review Scope

Adversarially verify whether selected next gate P13-S1 tracking-error / index-data source contract plan-review is the smallest best-practice next phase and whether the selection artifact is safe to accept.

## Sources Used

| Source | Role |
|---|---|
| `docs/reviews/next-phase-selection-20260522.md` | Reviewed target |
| `docs/design.md` | Design truth |
| `docs/implementation-control.md` | Control truth |
| `docs/reviews/post-p12-release-maintenance-closeout-20260522.md` | Closeout truth |
| `AGENTS.md` | Agent execution rules |
| `fund_agent/fund/template/renderer.py` (grep) | Code fact: tracking error placeholder |
| `fund_agent/fund/analysis/risk_check.py` (grep) | Code fact: tracking error field exists |
| `fund_agent/fund/analysis/alpha_judge.py` (grep) | Code fact: index fund lens statement |

## Assumptions Tested

1. **P13-S1 is the smallest best-practice next phase** — tested against E1-E3, repo-hygiene, and RR-13 candidates.
2. **P13-S1 planning-only is concrete enough to hand to an implementation agent** — tested against the 7 required slices and 9 rejection criteria.
3. **The selection artifact's evidence claims are accurate** — verified against code facts and source documents.
4. **Architecture boundaries, non-goals, and file constraints are safe** — tested against design.md and AGENTS.md.
5. **RR-13 and repo-audit exclusions are correctly handled** — tested against closeout and control truth.

## Findings

### 01-未修复-中-跟踪误差数据来源可行性未在选择阶段验证

- **位置**: Section 5 Recommended P13-S1 Scope, item 1-2; Section 3 Evidence
- **问题类型**: 非最优方案
- **当前写法**: 选择 artifact 假设 tracking error 可从年报/招募说明书/指数公告通过 `FundDocumentRepository` 获取或从基金/指数时间序列计算，但未验证当前年报是否实际披露跟踪误差数值。
- **反例/失败场景**: 如果基金年报不披露跟踪误差数值（只披露基准收益率），P13-S1 plan 可能发现需要从 NAV 时间序列自行计算，这会将 scope 从"数据提取"膨胀为"数据提取 + 计算引擎 + 指数序列适配器"，超出当前 Fund Capability 边界或需要新增外部数据源适配器。
- **为什么有问题**: `renderer.py:576` 明确写"跟踪误差在当前数据契约下保持数据不足"，`risk_check.py:514-521` 显示跟踪误差需要显式提供且缺失时返回 `insufficient_data`。这说明当前代码已经假设跟踪误差是外部输入而非年报提取字段。选择 artifact 的 evidence 表引用了 `p12-s1-item-rule-renderer-audit-compliance-plan` 说"tracking error remains deterministic `数据不足` placeholder until extractors exist"，但没有区分"extractor 可以从年报提取"和"需要计算引擎"两种路径。
- **直接证据**: `renderer.py:576` "跟踪误差在当前数据契约下保持数据不足"；`risk_check.py:181-212` tracking_error 需显式传入；`alpha_judge.py:304` "纯指数基金的核心不是超额收益性质，而是跟踪误差和费率"
- **影响**: P13-S1 plan-review agent 可能花大量时间在 source contract 设计上才发现核心问题是计算路径而非提取路径，导致 plan 不够 code-generation-ready 或需要拆成多个 slice。
- **建议改法和验证点**: 在 Section 5 item 2 的 source path 设计要求中，显式要求 P13-S1 plan 先回答一个前置问题："跟踪误差是年报直接披露字段还是需要从基金/指数净值序列计算？" 如果是后者，plan 必须明确指数序列数据来源和 `FundDocumentRepository` 是否扩展到非年报文档。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 02-未修复-低-P13-S1 plan-review 接受标准只定义了拒绝条件

- **位置**: Section 9 Review Criteria
- **问题类型**: 契约缺失
- **当前写法**: Section 9 列出 9 个拒绝条件（"must reject if any of these are true"），但没有定义正面接受标准。最后一句"should pass only if the implementation can be handed to a coding agent without requiring architectural guessing"过于模糊。
- **反例/失败场景**: plan-review agent 可能满足所有不拒绝条件但产出一个空洞、缺乏具体 slice 边界和 stop condition 的 plan，仍然通过 review。
- **为什么有问题**: 本项目的 phaseflow 约定要求 plan review 有明确的 pass/pass-with-risks/fail verdict。只定义拒绝条件而无接受条件，增加了 plan-review agent 自由裁量空间，可能与 controller 期望不一致。
- **直接证据**: Section 9 只有拒绝条件列表；项目历史中 P12-S1/P12-S2 plan review 均有明确的正面接受标准。
- **影响**: 低。plan-review agent 仍需遵循项目约定的 plan review adversarial posture，但缺少正面标准可能让 review 质量不一致。
- **建议改法和验证点**: 在 Section 9 末尾补充正面接受条件，至少包括：(a) 7 个 slice 均有明确的输入/输出/边界规则；(b) 每个 slice 可独立交给 implementation agent；(c) 所有 stop conditions 覆盖 Section 12 的场景。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 03-未修复-低-index methodology/constituents 的数据来源范围可能超出 FundDocumentRepository

- **位置**: Section 5 item 1 (index methodology summary, index constituents); Section 5 item 2 (source path)
- **问题类型**: 范围漂移
- **当前写法**: Section 5 item 1 要求 plan 回答"index methodology summary if disclosed"和"index constituents or constituent source reference if available"。Section 5 item 2 列出年报/招募说明书/指数公告作为来源路径。
- **反例/失败场景**: 指数编制方法论和成分股通常不在基金年报中披露，而在指数公司（中证指数、国证指数等）的独立公告中。如果 P13-S1 plan 需要引入指数公司数据源，这会超出当前 `FundDocumentRepository` 的年报/招募说明书边界，需要新的 adapter 和 identity/failure taxonomy。
- **为什么有问题**: `FundDocumentRepository` 当前只服务基金年报和招募说明书。引入指数公司数据源是新的外部依赖，应有独立的 source contract 设计，不应被"index-data"的 umbrella scope 吸收。
- **直接证据**: `docs/design.md` 6.1 节数据源表只列年报 PDF、净值序列、基本信息、温度计和严选基金池；无指数编制方法论或成分股数据源。
- **影响**: 低。选择 artifact 已在 Section 5 item 2 要求"any new external index series adapter only after source, cache, identity, and failure taxonomy are designed"，这提供了保护。但如果 P13-S1 plan 将 methodology/constituents 作为必须交付项而非可选项，scope 可能膨胀。
- **建议改法和验证点**: 在 Section 5 item 1 中将"index methodology summary"和"index constituents"标记为条件性交付（"if available from fund prospectus or existing sources"），与 tracking error 的必须交付区分优先级。P13-S1 plan 应先确认这些数据是否可从现有 `FundDocumentRepository` 路径获取，再决定是否引入新来源。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

| # | Question | Why it matters | Suggested resolution |
|---|---|---|---|
| OQ-1 | 跟踪误差在基金年报中是否有直接披露字段，还是必须从净值序列计算？ | 决定 P13-S1 plan 的核心 slice 是"提取器"还是"计算引擎 + 数据适配器" | P13-S1 plan 的第一个前置 slice 应调研 3 只样本指数基金年报，确认跟踪误差披露状态 |
| OQ-2 | index methodology 和 constituents 是否应推迟到 P13-S2 而非 P13-S1？ | 避免 scope 膨胀；tracking error 单独已能移除用户可见的 `数据不足` | 建议 P13-S1 plan 将 methodology/constituents 作为 deferred residual，只做 tracking error + benchmark identity |

## Residual Risks

| Risk | Severity | Suggested tracking |
|---|---|---|
| 跟踪误差计算路径可能需要指数序列外部数据源 | 中 | P13-S1 plan 前置调研 slice |
| index methodology/constituents 可能超出 FundDocumentRepository 当前边界 | 低 | P13-S1 plan scope decision; defer to P13-S2 if needed |
| P13-S1 plan-review 接受标准缺乏正面定义 | 低 | 建议补充到 selection artifact 或由 plan-review agent 自行定义 |

## Architecture Boundary Verification

| Boundary | Status | Evidence |
|---|---|---|
| Fund Capability ownership | ✅ safe | Section 5/7 correctly constrains P13 to Fund Capability |
| `FundDocumentRepository` as sole document entry | ✅ safe | Section 5 item 2, Section 6 non-goals |
| Service/UI not accessing source internals | ✅ safe | Section 6 non-goals, Section 7 disallowed files |
| Dayu non-dependency | ✅ safe | Section 6 non-goals explicitly excludes Dayu Host/Engine/tool loop/runtime |
| LLM non-goals | ✅ safe | Section 6 non-goals explicitly excludes LLM writing, LLM audit, Evidence Confirm |
| E1-E3 separation | ✅ safe | Section 4 candidate comparison defers E1-E3; Section 6 non-goals |
| RR-13 human-owned | ✅ safe | Section 4/6/11/12 all preserve RR-13 as human-owned |
| repo-audit exclusion | ✅ safe | Section 6/7/12 all exclude `docs/repo-audit-20260521.md` |
| deterministic MVP boundaries | ✅ safe | No LLM, no Dayu runtime, no external tool loop |

## Sequencing Verification

| Sequence | Status | Evidence |
|---|---|---|
| maintenance-ready → next phase selection → P13-S1 plan-review | ✅ correct | Section 1 gate/role; control truth Startup Packet |
| P13-S1 planning before implementation | ✅ correct | Section 2 "Selected scope is planning/design only" |
| E1-E3 deferred to separate audit phase | ✅ correct | Section 4 candidate comparison |
| repo-hygiene deferred | ✅ correct | Section 4 candidate comparison |
| design.md/control.md not modified during selection | ✅ correct | Section 6 non-goals |

## File Boundary Verification

| File | Selection gate | P13-S1 plan-review gate | P13 implementation gate |
|---|---|---|---|
| `docs/reviews/next-phase-selection-20260522.md` | ✅ allowed | N/A | N/A |
| `docs/reviews/p13-s1-*.md` | N/A | ✅ allowed | N/A |
| `fund_agent/` | ❌ disallowed | ❌ disallowed | TBD by plan |
| `tests/` | ❌ disallowed | ❌ disallowed | TBD by plan |
| README files | ❌ disallowed | ❌ disallowed | TBD by plan |
| `docs/design.md` | ❌ disallowed | ❌ disallowed | TBD by plan |
| `docs/implementation-control.md` | ❌ disallowed | ❌ disallowed | TBD by plan |
| `docs/repo-audit-20260521.md` | ❌ disallowed | ❌ disallowed | ❌ disallowed |
| RR-13 source data | ❌ disallowed | ❌ disallowed | ❌ disallowed |

## Plan Review Conclusion

**Verdict: `pass-with-risks`**

The selection artifact is structurally sound. P13-S1 is correctly identified as the highest-value next phase, the planning-only gate is appropriately scoped, architecture boundaries are well-defended, RR-13 and repo-audit exclusions are correct, and Dayu/LLM non-goals are explicit. The 7 required plan slices and 9 rejection criteria provide sufficient structure for the plan-review gate.

Two medium/low findings and two open questions remain:

1. **Finding 01 (中)**: The selection artifact assumes tracking error is extractable without verifying whether annual reports actually disclose it. If it requires calculation from index time series, P13-S1 scope may expand beyond a pure source-contract design. This is the strongest challenge to "smallest best-practice next phase" — it does not invalidate the selection but the P13-S1 plan must address this as a前置 question before designing source contracts.

2. **Finding 02 (低)**: Acceptance criteria for P13-S1 plan-review are implicit (rejection-only). Low risk because project conventions and adversarial review posture provide backstop.

3. **Finding 03 (低)**: Index methodology/constituents may exceed `FundDocumentRepository` current scope. Already mitigated by the requirement to design source contracts before adding new adapters.

The artifact is safe to accept with the understanding that the P13-S1 plan-review agent must resolve OQ-1 (tracking error extractability) as its first design question.
