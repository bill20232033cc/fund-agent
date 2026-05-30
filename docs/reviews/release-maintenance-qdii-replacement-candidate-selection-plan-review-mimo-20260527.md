# QDII Replacement Candidate Selection Plan — MiMo Review

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Gate: `QDII replacement candidate selection plan gate`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-20260527.md`
> Verdict: **PASS**

## Truth Sources Consulted

| Source | Role |
|---|---|
| `AGENTS.md` | Agent 执行规则唯一权威入口 |
| `docs/design.md` v2.2 | 设计真源 |
| `docs/implementation-control.md` Startup Packet / Current Gate | 实施总控 |
| `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` | accepted replacement candidate disposition |
| `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-controller-judgment-20260527.md` | accepted 017641 quality triage |
| `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md` | accepted 017641 public evidence triage |
| `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-20260527.md` | accepted candidate disposition matrix |
| `docs/reviews/release-maintenance-017641-manager-strategy-text-quality-triage-plan-20260527.md` | accepted 017641 quality triage plan |

## Review Checklist

### 1. Startup Packet Replay 正确性

**PASS.**

Plan §1 Startup Packet replay 与 `docs/implementation-control.md` 当前状态完全一致：

| Field | Control doc | Plan §1 | Match |
|---|---|---|---|
| Current phase | `release maintenance` | `release maintenance` | ✓ |
| Current gate | `replacement/exclusion candidate selection accepted locally` | `replacement/exclusion candidate selection accepted locally` | ✓ |
| Next entry point | `QDII replacement candidate selection plan gate; must use init-agents / tmux multi-agent flow` | `QDII replacement candidate selection plan gate; must use init-agents / tmux multi-agent flow` | ✓ |
| Latest accepted checkpoint | branch HEAD after `667eed6 docs: accept replacement candidate disposition` | `667eed6 docs: accept replacement candidate disposition` | ✓ |

Plan 正确声明这是 Startup Packet next entry point，不是 gate switch。Worker 角色正确声明为 planning worker, not controller。

### 2. 017641 Disposition Preservation

**PASS.**

Plan §2 正确保留 accepted controller judgment 中 `017641` / 2024 的全部字段：

| Field | Accepted judgment | Plan §2 | Match |
|---|---|---|---|
| Fund code | `017641` | `017641` | ✓ |
| Report year | `2024` | `2024` | ✓ |
| Slot | `qdii_fund` | `qdii_fund` | ✓ |
| Source provenance | complete; primary_failure_category=unavailable; fallback_eligibility=eligible | 完全一致 | ✓ |
| Quality state | `block` | `block` | ✓ |
| Terminal classification | `disclosure_data_gap_not_baseline_ready` | `disclosure_data_gap_not_baseline_ready` | ✓ |
| Candidate disposition | `replace` | `replace` | ✓ |
| Promotion disposition | `not_promoted` | `not_promoted` | ✓ |

Plan 正确声明 017641 的 accepted reason 是 "P0 `manager_strategy_text` disclosure data gap that is not baseline-ready"，不是 extractor gap，不是 policy issue。Plan 明确禁止将 017641 reinterpret 为 extractor gap 或 policy issue，与 accepted evidence triage controller judgment 的 terminal classification 一致。

### 3. QDII Replacement Selection Criteria

**PASS.**

Plan §3 定义了 7 条选择标准，每条都有明确 requirement：

- **Fund type slot**: 要求 `qdii_fund`，QDII-FOF 需要 separate taxonomy gate accept。足够明确。
- **Report year**: 固定 `2024`，与 017641 同年。可执行。
- **Candidate source identity**: 限定为 `docs/code_20260519.csv` 或已 accepted artifact/list。source-safe。
- **Evidence route**: 限定为 `extraction-snapshot`, `extraction-score`, `quality-gate` 三个 public CLI 路径。符合 AGENTS.md 来源约束。
- **Source provenance**: 要求 primary success 或 complete eligible fallback；`schema_drift`/`identity_mismatch`/`integrity_error` fail-closed。与 AGENTS.md fallback 策略一致。
- **Quality**: 无 P0 quality block；`manager_strategy_text` 不能 P0 fail，除非 separate design/policy gate reclassify。足够明确。
- **Promotion**: 只允许 evidence candidate，禁止 durable baseline/fixture/golden/corpus promotion。与 accepted disposition 一致。

附加约束 "Successful extraction or a populated snapshot is not evidence of source eligibility" 是重要的正确性守卫，防止从结果推导资格。

### 4. Candidate Source Policy

**PASS.**

Plan §4 正确识别：
- 当前 accepted artifacts 不提供 controller-approved QDII replacement candidate。
- 因此下一 gate 必须是 `QDII replacement candidate enumeration plan gate`，不是 direct evidence。
- 推荐的 bounded enumeration method 以 `docs/code_20260519.csv` 为唯一 candidate universe。
- 明确列出候选基金代码（`019172`, `040046` 等）但立即声明 "this list is not an approved replacement list"。没有未经批准的候选被当作 approved。
- 明确要求 MiMo 和 DS/GLM 独立 plan review + controller judgment 才能进入 evidence。

### 5. Future Evidence Matrix

**PASS.**

Plan §5 明确标注 "This gate does not run evidence. The commands below are future command shapes only"。三条命令（snapshot/score/quality-gate）和 closeout validation 都是 future shape，不在本 gate 授权范围内。输出 policy 正确保持 ignored。未来 tracked summary artifact 路径和必录字段都有明确定义。

### 6. Stop Conditions

**PASS.**

Plan §6 覆盖了 review focus 要求的全部 stop condition：

| 要求 | Plan §6 覆盖 | 对应条款 |
|---|---|---|
| Taxonomy ambiguity | ✓ | "Candidate taxonomy is ambiguous, including QDII vs QDII-FOF ambiguity" |
| Source fail-closed | ✓ | "Any fail-closed source category appears: schema_drift, identity_mismatch, or integrity_error" |
| P0 block | ✓ | "Candidate has a P0 quality block" |
| manager_strategy_text | ✓ | "manager_strategy_text remains P0-blocking and no separate design/policy gate has reclassified" |
| Direct PDF/cache/source-helper | ✓ | "Evidence requires direct PDF/cache/source-helper/downloader/source-adapter access" |
| Source strategy/FQ/renderer/Service/Host/Agent/dayu/promotion | ✓ | 第 6-8 条覆盖全部 forbidden scope |
| 新 unexplained P0/P1 | ✓ | "A new unexplained P0/P1 issue appears" |
| 无 accepted plan 即 evidence | ✓ | "The proposed next step enters evidence without an accepted enumeration/selection plan and controller judgment" |

### 7. Scope Drift / Hidden Promotion 检查

**PASS.**

- **Scope drift**: 无。Plan 严格限定为 plan artifact，不包含代码修改、设计变更、implementation-control 更新或 evidence 运行。
- **Hidden promotion**: 无。Plan 在 §3（selection criteria）、§5（future evidence matrix）、§6（stop conditions）和 §8（non-goals）中反复声明 no promotion。
- **Over-reliance on `docs/code_20260519.csv`**: CSV 作为唯一 candidate universe 是合理的 source-safety choice。Plan 没有将 CSV 中的行当作 approved candidates，只是将其作为 bounded enumeration pool。
- **Candidate list treated as approved**: §4 明确声明 "this list is not an approved replacement list"。没有违规。
- **017641 misinterpreted**: §2 正确保留 `disclosure_data_gap_not_baseline_ready` terminal classification，没有误作 extractor gap 或 policy issue。

## Non-Goals Check

Plan §8 正确列出全部 forbidden scope，与 accepted controller judgment 和 AGENTS.md 一致。无遗漏。

## Review Matrix Check

Plan §7 Review matrix 正确指定 MiMo → plan review、DS/GLM → plan review、Controller → judgment、Next gate → enumeration plan 的四步流程。与 control doc 的 init-agents / tmux multi-agent flow 要求一致。

## Validation

Plan §9 仅做 `git diff --check` whitespace validation，符合 plan-artifact-only scope。

## Findings

无 blocking finding。以下为 documentation precision observations（不改变 verdict）：

| # | Severity | Observation | Suggestion |
|---|---|---|---|
| 1 | informational | §4 "Approved inputs for candidate selection are bounded to" 中包含 `docs/code_20260519.csv`，但 CSV 是 candidate universe 不是 approved candidate source。措辞 "Approved inputs" 可能引起歧义。 | 考虑改为 "Candidate universe inputs are bounded to" 或在后文明确区分 universe vs approved。当前后文已有足够澄清，不影响正确性。 |
| 2 | informational | §3 "Candidate source identity" 行说 "must come from `docs/code_20260519.csv` or an already accepted artifact/list that cites the same selected-fund source identity"。后半句 "already accepted artifact/list" 的范围略宽，虽然 §4 的 bounded policy 已经收紧。 | 无需修改，但后续 evidence worker 应具体引用 accepted artifact 路径。 |

## Verdict

**PASS.**

Plan artifact 正确保放 Startup Packet next entry point，保留 `017641` = `replace` / `not_promoted` / `disclosure_data_gap_not_baseline_ready`，selection criteria 明确可执行且 source-safe，candidate source policy 正确要求 enumeration plan 先于 evidence，future evidence matrix 仅为 future shape，stop conditions 完整覆盖全部要求，无 scope drift 或 hidden promotion。
