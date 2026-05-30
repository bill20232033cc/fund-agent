# 110020 Reviewed Coverage Candidate Evidence — Independent Review (GLM)

> Reviewer: AgentGLM, independent evidence reviewer, not controller
> Date: 2026-05-27
> Review target: `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-20260527.md`
> Truth sources: `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted controller judgment `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-controller-judgment-20260527.md`, accepted plan `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-decision-plan-20260527.md`

## Review Scope

1. 挑战 terminal_state：`reviewed_coverage_candidate_input_accepted` 是否合理，或应 `deferred` / `rejected`。
2. 检查 public commands、provenance tuple、quality warning set、strict golden residual 是否符合 plan。
3. 检查 index evidence assessment：`index_profile` sufficient、`tracking_error` sufficient、methodology/constituents insufficient 是否证据同源且不过度推断。
4. 检查 stop conditions 是否有被触发但未处理。
5. 检查 no-promotion / no-generated-tracked / no direct PDF-cache-source-helper / no code/control changes boundary。

## Finding 1: Terminal State 边界判断

**Finding ID**: G1
**Severity**: minor / non-blocking
**Area**: Terminal state classification

`terminal_state = reviewed_coverage_candidate_input_accepted`

Plan 定义了三个候选 terminal state：

| Terminal state | 含义 |
|---|---|
| `reviewed_coverage_candidate_input_accepted` | 110020 may be considered by a later baseline/golden preflight after unresolved risks are carried forward |
| `deferred_pending_reviewed_facts` | Candidate is not rejected, but reviewed facts or index-lens evidence are insufficient |
| `excluded_after_review` | Public evidence makes the row unsuitable for the index coverage slot |

**挑战**：methodology/constituents 被分类为 `insufficient`，而 plan 对 `deferred_pending_reviewed_facts` 的定义是 "reviewed facts or index-lens evidence are insufficient"。按字面读法，`insufficient` 的 index-lens evidence 可触发 `deferred`。

**判定：`reviewed_coverage_candidate_input_accepted` 可辩护，不要求改为 `deferred`**。理由：

1. Plan 定义的三个 index evidence item 中，有两个核心抽取项（`index_profile`、`tracking_error`）均为 `sufficient`，且 source pointer 明确指向 public snapshot/score 产出。
2. methodology/constituents `insufficient` 是预期结果——accepted plan 在 Unresolved Risks 表中已明确标注 "Current accepted evidence proves provenance and quality warn; it does not prove index methodology, constituents, tracking quality, or index-lens evidence sufficiency"。这不是 evidence gate 的新发现，而是被 carry-forward 的已知限制。
3. `deferred_pending_reviewed_facts` 的语义更适合用于 *core* evidence 在 gate 中被新发现为 insufficient 的场景，而非用于预期中已知的 secondary gap。
4. Residual 列表显式 carry-forward 了 methodology/constituents insufficiency，后续 baseline/golden preflight 必须在处理该 residual 后才能推进。

**建议（non-blocking）**：后续 plan 若再定义类似 gate，可在 terminal state 定义中增加注释区分 "expected known insufficiency" 和 "newly discovered insufficiency"，避免此边界歧义。

## Finding 2: Evidence Document 与 Accepted Plan 一致性

**Finding ID**: G2
**Severity**: info
**Area**: CSV identity / HEAD tracking

Evidence document 记录了当前 HEAD `46e4f13`，与 accepted plan 记录的 HEAD `188f150` 不同。Document 在 CSV Identity / Version Note 小节中透明处理了这一点：

- CSV last commit `7596c5e`、mtime `May 19 00:28:41 2026`、size `3213 bytes` 与 accepted plan 一致 ✓
- HEAD 差异由 accepted plan 与 evidence gate 之间的正常 commit 产生，不构成问题 ✓
- Document 明确声明 "this run records current HEAD separately as evidence identity" ✓

**判定**：处理方式正确透明，无问题。

## Check 1: Public Commands

| Plan 要求 | Evidence document 记录 | 判定 |
|---|---|---|
| `extraction-snapshot --force-refresh` + 指定参数 | Command 完整匹配，exit 0 | ✓ |
| `extraction-score` + 指定参数 | Command 完整匹配，exit 0 | ✓ |
| `quality-gate` + 指定参数 | Command 完整匹配，exit 0 | ✓ |
| `git diff --check` | exit 0，no output | ✓ |
| Output paths 在 ignored `reports/extraction-snapshots/` 下 | 符合 | ✓ |
| 仅写一个 tracked artifact | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-20260527.md` | ✓ |

**判定**：所有 public commands 与 accepted plan 完全一致。✓

## Check 2: Provenance Tuple

| Field | Accepted plan value | Evidence observed value | Match |
|---|---|---|---|
| `fund_type_slot` | `index_fund` | `index_fund` | ✓ |
| `source_strategy` | `primary_then_fallback` | `primary_then_fallback` | ✓ |
| `resolved_source_name` | `eastmoney` | `eastmoney` | ✓ |
| `fallback_used` | `true` | `true` | ✓ |
| `primary_failure_category` | `unavailable` | `unavailable` | ✓ |
| `fallback_eligibility` | `eligible` | `eligible` | ✓ |
| `source_provenance_status` | `complete` | `complete` | ✓ |
| `source_provenance_reason` | `fallback_used_primary_failure_category_eligible` | `fallback_used_primary_failure_category_eligible` | ✓ |

**判定**：Provenance tuple 8 字段全部匹配，无回归。✓

## Check 3: Quality Warning Set

| Plan 已知 warning | Evidence 观察到 | 判定 |
|---|---|---|
| FQ2 warn: `turnover_rate` P1 coverage/traceability | 记录一致 | ✓ |
| FQ2F warn: 110020 P1 field failure `turnover_rate` | 记录一致 | ✓ |
| FQ0 info: strict golden not configured | 记录一致 | ✓ |
| 无新增 P0/P1 warning | 显式声明无新增 | ✓ |
| Quality gate status = `warn` | `warn`，非 `block` | ✓ |

**判定**：Quality warning set 完全在 accepted known set 范围内。✓

## Check 4: Strict Golden Residual

- Evidence document 在 Strict Golden Absence Disposition 小节显式记录 correctness oracle 未执行 ✓
- 声明 score 不可用作 golden、fixture、clean denominator 或 report-quality corpus ✓
- 在 Residuals Carried Forward 中再次列出 strict golden absence ✓

**判定**：Strict golden residual 处理正确，未被掩盖或弱化。✓

## Check 5: Index Evidence Assessment

### `index_profile` → sufficient

- **证据同源性**：所有 claim 来源于同一 public CLI 产出链（`extraction-snapshot` → `extraction-score`），source pointer 指向 `snapshot.jsonl` row `field_name=index_profile` 和 `score.md` Field Scores row `profile/index_profile`。
- **推断边界**：Assessment 明确限定 "sufficient for index identity / benchmark-context review, not for methodology or constituents claims"，未将 benchmark context overread 为 methodology evidence。
- **对照 plan 定义**：Plan 说 sufficient 意味着 "Public extracted facts identify the tracked index / benchmark context with traceable evidence and no contradictory type signal"。Evidence document 的分类与此定义一致。
- **判定**：`sufficient` 分类合理，证据同源，未过度推断。✓

### `tracking_error` → sufficient

- **证据同源性**：Claim 基于 `snapshot.jsonl` row `field_name=tracking_error` 和 `score.md` Field Scores row `performance/tracking_error`，属于同一 public CLI 产出链。
- **关键 claim**：`source_type=direct_disclosure`、`calculation_method=disclosed`、`value_text=2%`。这些字段表明 tracking error 来自年报直接披露，不是推断值。
- **边界处理**：`benchmark_identity_status=missing` 被标注为 "residual limitation for later mature baseline/golden preflight"，未因此降级为 insufficient——这是合理的，因为 tracking error 本身的披露证据充分，benchmark identity 是后续 golden preflight 的独立前置条件。
- **对照 plan 定义**：Plan 说 sufficient 意味着 "Public output contains direct observed tracking-error disclosure or an accepted reviewed evidence statement with traceable anchor; the gate can explain whether tracking quality is reviewable"。Evidence document 满足该定义。
- **判定**：`sufficient` 分类合理，证据同源，未过度推断。✓

### Methodology / constituents → insufficient

- **证据同源性**：Claim 基于 `snapshot.jsonl` row `field_name=index_profile` 的 `comparable_values.methodology_availability=benchmark_only` 和 `comparable_values.constituents_availability=benchmark_only`。属于同一 public CLI 产出链。
- **未过度推断**：Document 没有将 benchmark context 文本 overread 为 methodology 或 constituents evidence。Note 明确说 "must not be used as index methodology or constituent evidence"。
- **对照 plan 定义**：Plan 说 insufficient 意味着 "Evidence is absent, generic benchmark text is being overread, or the claim would require direct PDF/cache/source-helper inspection"。当前 snapshot 的 `benchmark_only` 标记证实 evidence 不足以支撑 methodology/constituents claim，分类正确。
- **判定**：`insufficient` 分类正确，证据同源，未试图 overread。✓

**三项评估独立性**：三个 item 分别评估，未合并为单一 "index evidence ok" 声明。每项有独立的 reason 和 source pointer。✓

## Check 6: Stop Conditions

Plan 定义的 stop conditions 逐一核查：

| Stop condition | 是否触发 | 处理 |
|---|---|---|
| Provenance tuple 变化 | 未触发（8/8 match） | N/A |
| Source strategy / resolved source 变化 | 未触发 | N/A |
| Quality 变为 `block` | 未触发（status = `warn`） | N/A |
| 新增 P0/P1 warning | 未触发 | N/A |
| Reviewer `BLOCK` | 不适用于 evidence worker 阶段 | N/A |
| Direct PDF/cache/source-helper 访问 | 未触发 | N/A |
| Promotion 尝试 | 未触发（`not_promoted`） | N/A |
| Index assessment 遗漏或合并 | 未触发（三项独立评估） | N/A |
| Missing tracking 被当作 sufficient | 未触发（tracking evidence IS sufficient via direct disclosure） | N/A |

**判定**：无 stop condition 被触发但未处理。✓

## Check 7: Boundary Compliance

| Boundary 要求 | 状态 |
|---|---|
| No code implementation | ✓ 未修改任何代码文件 |
| No renderer / FQ0-FQ6 / Service / CLI default changes | ✓ |
| No source strategy / `FundDocumentRepository` / source helper changes | ✓ |
| No direct PDF / cache / source-helper inspection | ✓ |
| No Host / Agent / dayu integration | ✓ |
| No durable baseline / clean denominator / fixture / golden promotion | ✓ `promotion_disposition=not_promoted` |
| No `docs/implementation-control.md` update | ✓ |
| No commit / push / PR / merge / GitHub mutation | ✓ |
| Generated outputs under ignored path | ✓ `.gitignore` rule `reports/extraction-snapshots/` |
| Only one tracked artifact written | ✓ |

**判定**：所有 boundary 约束满足。✓

## Summary of Findings

| Finding ID | Severity | Summary | Blocking? |
|---|---|---|---|
| G1 | minor | Terminal state 边界可辩护但有字面歧义：methodology/constituents `insufficient` 与 `deferred_pending_reviewed_facts` 定义字面匹配，但 `reviewed_coverage_candidate_input_accepted` 在上下文中仍为更合理选择 | No |
| G2 | info | HEAD 从 plan 的 `188f150` 前进到 `46e4f13`，CSV identity 不变，处理方式透明正确 | No |

## Verdict

**PASS_WITH_FINDINGS**

Evidence document 与 accepted plan 高度一致：public commands 完全匹配、provenance tuple 无回归、quality warning set 在已知范围内、index evidence assessment 三项独立评估且证据同源无过度推断、所有 stop conditions 未被触发、所有 boundary 约束满足。

两个 finding 均为 non-blocking：G1 是 terminal state 定义的边界语义问题（不影响当前决策正确性），G2 是 HEAD tracking 的信息性记录。

`terminal_state = reviewed_coverage_candidate_input_accepted` 和 `promotion_disposition = not_promoted` 作为本次 evidence gate 的结论可被接受。110020 / 2024 可在 carry-forward 所有 residuals 的前提下进入后续 baseline/golden preflight 考虑。
