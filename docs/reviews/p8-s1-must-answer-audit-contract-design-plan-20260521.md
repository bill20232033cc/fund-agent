# P8-S1 Must Answer Audit Contract Design Plan（2026-05-21）

## Scope

P8-S1 addresses the remaining Post-P7 residual:

> `CHAPTER_CONTRACT.must_answer` is machine-readable in `fund_agent/fund/template/contracts.py`, but current deterministic C2 audit only consumes `required_output_items` and `must_not_cover`.

This is a design-first slice. The goal is not to force every natural-language `must_answer` question into brittle keyword matching. The goal is to make the coverage status of every `must_answer` explicit, auditable, and reviewable while keeping deterministic C2 honest about what it proves.

## Current Code Facts

- `ChapterContract.must_answer` is defined in `fund_agent/fund/template/contracts.py`.
- `ProgrammaticContractRules` currently contains only:
  - `required_items`
  - `forbidden_contents`
- `run_programmatic_audit()` executes `_audit_contract_conformance(...)`, which checks:
  - chapter block metadata
  - required item markers
  - forbidden markers
- `contract_rules.py` currently states that it maintains explicit mappings for deterministic C2 markers and does not perform LLM judgment or semantic inference.
- Programmatic audit is intentionally deterministic and does not call LLM, read PDF/cache, or inspect external documents.

## Design Decision

Introduce an explicit `must_answer` coverage manifest in `fund_agent/fund/audit/contract_rules.py`, but do not make non-programmatic routing part of `ProgrammaticContractRules`.

New model boundary:

- `ContractMustAnswerCoverageRule`: one typed routing rule for one exact `must_answer` question.
- `ContractAuditCoverageManifest`: complete coverage manifest for all current `must_answer` questions.
- `ProgrammaticContractRules`: remains the deterministic C2 runtime rule model for required item markers and forbidden markers.

Every `must_answer` must be classified into exactly one coverage kind:

| Coverage kind | Meaning | Runtime behavior in P8-S1 |
|---|---|---|
| `covered_by_required_item` | The question is currently proven only through an existing `required_output_item` marker | Validate that the linked required item exists and is already covered by required item rules; no duplicate C2 issue |
| `programmatic_marker` | The answer has a stable literal marker distinct from required item coverage | C2 checks marker presence in the chapter body |
| `structured_data_availability` | The answer requires checking structured P1/P2 data presence rather than prose | Routing only in P8-S1; implementation deferred |
| `llm_semantic_audit` | The answer requires semantic judgment | Routing only in P8-S1; future LLM audit consumes it |
| `evidence_confirm` | The answer requires verifying evidence supports the claim | Routing only in P8-S1; future evidence confirm consumes it |
| `narrative_guidance` | The question guides report writing but is not independently machine-verifiable | Routing only in P8-S1; recorded as narrative-only |

This turns the previous hidden gap into a typed contract:

- No `must_answer` can silently disappear from audit design.
- Deterministic checks remain honest about what they prove.
- Future LLM/evidence slices inherit a complete routing table instead of rediscovering scope.

## Architecture Boundaries

- Capability layer owns the manifest and deterministic checks.
- `contracts.py` remains the template contract source.
- `contract_rules.py` owns the audit mapping from contract text to deterministic/non-deterministic coverage.
- `audit_programmatic.py` only executes deterministic checks.
- Renderer, Service, UI, document repository, PDF parser, and data extractors are out of scope.
- No new dependency on LLM, network, PDF, cache, or file system.

## Initial Must Answer Coverage Map

All `question_text` values below must match `ChapterContract.must_answer` exactly. Any implementation classification change must update this plan/review trail first.

### Chapter 0

| question_text | coverage_kind | required_item_text / rationale |
|---|---|---|
| 用一句话定义这只基金到底是什么产品。 | `covered_by_required_item` | 一句话这是什么基金 |
| 给出一个极简基金简介，帮助第一次接触这只基金的读者快速建立产品画像；只保留基金类型、基金经理、管理规模、成立时间中最必要的信息。 | `covered_by_required_item` | 基金简介 |
| 回答当前判断应是值得持有、需要关注还是建议替换。 | `covered_by_required_item` | 当前动作（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换） |
| 回答这只基金当前业绩和运作处在什么状态，但只保留最能支撑当前动作判断的净值表现、超额收益或风险指标。 | `covered_by_required_item` | 当前业绩与运作状态 |
| 回答支撑当前动作的最主要理由，默认压缩成 1 条；只有在第二条判断彼此独立且缺一不可时才允许写第 2 条。 | `covered_by_required_item` | 支撑当前动作的最主要理由 |
| 回答当前最值得盯住的变量是什么；先点出看这类基金时通常最先要看的东西；如果基金还有一个更能决定整份报告判断的特别情况，就把它放到最前面来写。 | `covered_by_required_item` | 当前最值得盯住的变量 |
| 回答当前最大的风险是什么，默认只保留一个主要风险。 | `covered_by_required_item` | 当前最大的风险 |
| 回答下一步最小验证问题是什么，默认先写 1 个最关键问题。 | `covered_by_required_item` | 下一步最小验证问题 |
| 回答什么变化会升级、降级或终止当前动作，优先压缩成 1 个升级阈值和 1 个降级或终止阈值。 | `covered_by_required_item` | 什么变化会升级、降级或终止当前动作 |

### Chapter 1

| question_text | coverage_kind | required_item_text / rationale |
|---|---|---|
| 用最低认知负担定义这只基金到底是什么产品。 | `covered_by_required_item` | 基金类型与分类标签 |
| 说明基金的投资目标和投资策略（从招募说明书和年报§2提取）。 | `covered_by_required_item` | 投资目标（一句话）；投资策略概述 |
| 说明基金的业绩基准是什么，为什么选这个基准。 | `covered_by_required_item` | 业绩基准及合理性 |
| 说明基金的类型分类（按有知有行三维标签：市值×风格×管理方式）。 | `covered_by_required_item` | 基金类型与分类标签 |
| 回答看这类基金时，通常最先要看什么。 | `covered_by_required_item` | 看这类基金最先看什么 |
| 如果基金有一个不太符合常规、却会直接改变你对“这是什么产品”理解的特别情况，要说明它为什么重要。 | `covered_by_required_item` | 会改变产品理解的特别情况（如有） |

### Chapter 2

| question_text | coverage_kind | required_item_text / rationale |
|---|---|---|
| 近 1 年、3 年、5 年的基金净值增长率（R）。 | `covered_by_required_item` | 近 1/3/5 年净值增长率 |
| 同期业绩基准收益率（B）。 | `covered_by_required_item` | 近 1/3/5 年业绩基准收益率 |
| 计算超额收益（A = R - B）。 | `covered_by_required_item` | 超额收益（A = R - B）及稳定性 |
| 判断超额收益是结构性的还是阶段性的。 | `covered_by_required_item` | 超额收益性质判断（结构性 vs 阶段性） |
| 拆解成本 C：管理费 + 托管费 + 销售服务费 + 交易成本（估算）。 | `covered_by_required_item` | 成本拆解（管理费、托管费、交易成本） |
| 判断超额收益是否为正且稳定、是否覆盖成本。 | `covered_by_required_item` | 超额收益（A = R - B）及稳定性；R=A+B-C 综合评估 |

### Chapter 3

| question_text | coverage_kind | required_item_text / rationale |
|---|---|---|
| 基金经理的基本信息（从业年限、管理本基金时间、管理规模）。 | `covered_by_required_item` | 基金经理基本信息 |
| 基金经理宣称的投资策略和风格（从年报§4提取）。 | `covered_by_required_item` | 宣称的投资策略（§4） |
| 基金经理实际的投资行为（从年报§8提取：行业配置、持仓集中度、换手率）。 | `covered_by_required_item` | 实际投资行为（§8） |
| 言行一致性判断：说的和做的一样吗？ | `covered_by_required_item` | 言行一致性判断 |
| 风格稳定性判断：跨期风格是否漂移？ | `covered_by_required_item` | 风格稳定性判断 |
| 利益一致性判断：基金经理是否持有本基金？ | `covered_by_required_item` | 利益一致性判断 |

### Chapter 4

| question_text | coverage_kind | required_item_text / rationale |
|---|---|---|
| 基金产品收益（净值增长率）。 | `covered_by_required_item` | 基金产品收益 vs 投资者实际收益 |
| 投资者实际收益（盈利投资者占比、加权平均收益率）。 | `covered_by_required_item` | 基金产品收益 vs 投资者实际收益；盈利投资者占比 |
| 行为损益 = 投资者实际收益 - 基金产品收益。 | `covered_by_required_item` | 行为损益估算 |
| 份额变动趋势（资金是在追涨还是在抄底？）。 | `covered_by_required_item` | 份额变动趋势 |

### Chapter 5

| question_text | coverage_kind | required_item_text / rationale |
|---|---|---|
| 过去一年最关键的 1-3 个变化（基金经理变更、规模剧变、策略调整、大额申赎等）。 | `covered_by_required_item` | 过去一年最关键的变化（1-3 个） |
| 基金当前大致处在什么阶段（建仓期/稳定期/膨胀期/萎缩期/转型期）。 | `covered_by_required_item` | 基金当前所处阶段 |
| 这些变化有没有改变第 1-4 章的判断。 | `covered_by_required_item` | 变化是否改变前文判断 |
| 为什么偏偏是现在需要关注这只基金。 | `narrative_guidance` | 这是第 5 章“当前阶段”叙事约束，当前模板没有独立输出项；不能用 C2 marker 证明“为什么是现在”的语义质量 |
| 接下来最该跟踪什么。 | `covered_by_required_item` | 接下来最该跟踪的变量 |

### Chapter 6

| question_text | coverage_kind | required_item_text / rationale |
|---|---|---|
| 最关键的风险或否决项（1-2 个最致命的风险）。 | `covered_by_required_item` | 最关键的风险或否决项 |
| 为什么足以改变结论——这个风险推翻了哪条核心假设。 | `covered_by_required_item` | 为什么足以改变结论 |
| 一票否决还是还能跟踪。 | `covered_by_required_item` | 否决 vs 跟踪判断 |
| 下一轮先验证什么。 | `covered_by_required_item` | 下一轮先验证什么 |

### Chapter 7

| question_text | coverage_kind | required_item_text / rationale |
|---|---|---|
| 三选一明确立场：值得持有、需要关注、建议替换。 | `covered_by_required_item` | 最终判断（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换） |
| 为什么现在更适合这个判断，而不是另外两个。 | `covered_by_required_item` | 支撑判断的核心依据（1-2 条） |
| 当前最容易看错的地方是什么。 | `covered_by_required_item` | 当前最容易看错的地方 |
| 下一轮先核实什么（1-2 个最小验证问题）。 | `covered_by_required_item` | 下一轮最小验证计划 |
| 什么变化会升级、降级或终止当前判断。 | `covered_by_required_item` | 危级/降级阈值 |

## Implementation Plan

### S1. Add Coverage Manifest Model

Files:

- `fund_agent/fund/audit/contract_rules.py`
- `tests/fund/audit/test_audit_programmatic.py`

Add:

- `MustAnswerCoverageKind = Literal[...]`
- `ContractMustAnswerCoverageRule`
- `ContractAuditCoverageManifest`
- `load_contract_audit_coverage_manifest()`
- `validate_contract_audit_coverage_manifest(...)`

Fields:

- `chapter_id`
- `question_text`
- `coverage_kind`
- `required_item_text: str | None`
- `markers_any: tuple[str, ...]`
- `rationale`

Validation:

- Every `question_text` must exactly match a `ChapterContract.must_answer`.
- Every manifest `must_answer` must appear exactly once.
- `covered_by_required_item` must point to at least one valid `required_output_item`.
- Every pointed required item must have a `ContractRequiredItemRule`.
- `programmatic_marker` must provide at least one marker.
- Non-programmatic coverage kinds must provide non-empty `rationale` and must not provide markers.
- Unknown chapter IDs and duplicate `(chapter_id, question_text)` pairs fail closed.

### S2. Keep Programmatic Rules Deterministic

Files:

- `fund_agent/fund/audit/contract_rules.py`
- `fund_agent/fund/audit/audit_programmatic.py`
- `tests/fund/audit/test_audit_programmatic.py`

Behavior:

- `ProgrammaticContractRules` keeps `required_items` and `forbidden_contents` as the deterministic C2 model.
- `load_programmatic_contract_rules()` may call `validate_contract_audit_coverage_manifest(...)` so startup fails when `must_answer` coverage drifts.
- Non-programmatic coverage kinds are not exposed as C2 pass proof.
- For `programmatic_marker` coverage rules, add deterministic marker checks only when such rules exist.
- The initial built-in manifest has no `programmatic_marker` rules. Therefore P8-S1 runtime behavior for existing reports remains unchanged.
- If a future rule uses `programmatic_marker`, `_audit_contract_conformance(...)` must emit C2 when the marker is absent.

Important:

- `ProgrammaticAuditResult.checked_rules` remains unchanged: `("P1", "P2", "P3", "C2", "L1", "R1", "R2")`.
- `AuditIssue` schema remains unchanged.
- No `partial/pass-with-warning` audit status is introduced.

### S3. Seed Coverage Manifest Exactly

Files:

- `fund_agent/fund/audit/contract_rules.py`

Implementation must encode the Initial Must Answer Coverage Map above. In this first slice:

- 44 of 45 current questions are `covered_by_required_item`.
- 1 of 45 current questions is `narrative_guidance`.
- 0 current questions are `programmatic_marker`.
- 0 current questions are `structured_data_availability`, `llm_semantic_audit`, or `evidence_confirm`.

This is intentionally conservative: C2 continues to prove marker presence, not answer quality, evidence sufficiency, or semantic reasoning.

### S4. Tests

Required tests:

- `load_contract_audit_coverage_manifest()` validates that every `must_answer` has exactly one coverage rule.
- Removing a `must_answer` coverage rule fails closed.
- A duplicate `must_answer` coverage rule fails closed.
- A `covered_by_required_item` rule pointing to an unknown required item fails closed.
- A `programmatic_marker` rule without markers fails closed.
- A non-programmatic coverage rule with markers fails closed.
- Existing required item missing marker behavior remains unchanged.
- Full audit happy path remains pass.
- If a fixture manifest contains `programmatic_marker`, the missing-marker runtime path emits C2. This can be tested with a local fixture manifest without changing the built-in manifest.

Targeted command:

```bash
pytest tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_contracts.py -q
```

Full verification:

```bash
pytest
git diff --check
```

## Documentation Plan

Update:

- `fund_agent/fund/README.md`
  - Explain that `must_answer` is now routed through explicit coverage kinds.
  - Clarify deterministic C2 still proves only marker/metadata constraints.
- `docs/design.md`
  - In audit section, clarify `must_answer` coverage split: deterministic subset is tracked; semantic/evidence subsets remain future slices.
- `docs/implementation-control.md`
  - Mark P8-S1 design/implementation status after acceptance.

Do not rewrite the full historical phase log.

## Non-Goals

- Do not implement LLM audit.
- Do not implement evidence confirm.
- Do not change renderer output.
- Do not change `CHAPTER_CONTRACT` content.
- Do not introduce a new audit status or severity.
- Do not alter quality gate behavior.

## Acceptance Criteria

- Every current `must_answer` is explicitly classified with exact text.
- Deterministic C2 runtime behavior remains stable for existing reports.
- `ProgrammaticContractRules` remains a deterministic rule model and does not expose non-programmatic coverage as C2 proof.
- Non-programmatic `must_answer` entries are visible in typed rules and cannot silently disappear.
- Targeted tests pass before full suite.
- Full suite remains green before implementation is accepted.

## Open Questions Deferred Out Of S1

1. Should `structured_data_availability` become a P8-S2 audit implementation slice, or should it be folded into quality gate?
2. Should future LLM audit consume the same `ContractMustAnswerCoverageRule` manifest directly, or should it get a separate semantic prompt manifest?
3. Should `ProgrammaticAuditResult` eventually expose non-programmatic coverage counts for observability, or is artifact documentation enough for now?
