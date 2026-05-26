# Evidence Review: Small Baseline Corpus v1 Evaluation Run

> **Reviewer**: AgentGLM (independent evidence reviewer)
> **Date**: 2026-05-27
> **Review target**: `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-20260527.md`
> **Accepted plan**: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`
> **Controller judgment**: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-controller-judgment-20260527.md`
> **Truth sources**: `AGENTS.md`, `docs/design.md` current design, `docs/implementation-control.md` Startup Packet / current gate / next entry, accepted plan and controller judgment

---

## Findings

### F1 — MINOR: 004393/2025 checklist 命令因 CLI flag 不可用偏离 plan，deviation 记录充分但 plan 命令本身有误

**Evidence**:
- Plan verifier matrix 指定 004393/2025 checklist 命令为 `uv run fund-analysis checklist 004393 --report-year 2025 --dev-override --quality-gate-policy warn`。
- Run 记录："CLI has no `--dev-override` / `--quality-gate-policy` for `checklist`; used supported command and recorded deviation."（Command Summary line 25）
- Run 的 004393/2025 analyze 命令使用了 `--dev-override --quality-gate-policy warn`，说明 analyze 子命令支持这些 flag，但 checklist 子命令不支持。
- 实际 checklist 以默认 quality gate policy 运行，quality gate 返回 `warn`（未阻断），所以观察目标（exit code + quality gate summary + availability）仍被达成。

**Risk**: 若 004393/2025 checklist 的 quality gate 返回了 `block`，默认 policy 会退出码 2 并阻断观察。本次运行中 gate 返回 `warn` 所以未触发，但这是一个潜在的观察盲点。Plan 在后续修订中应校验 verifier matrix 中的 CLI flag 对应子命令是否真实存在。

**Recommendation**: 本次 run 的 deviation 处理正确且充分记录，不阻塞 closeout。后续 plan 编写应在 verifier matrix 中区分 analyze 和 checklist 支持的 flag 差异。

---

### F2 — MINOR: `scripts/report_quality_eval.py` 未执行也未显式记录 "not run"

**Evidence**:
- Plan verifier matrix 包含 `scripts/report_quality_eval.py` 命令（dev-only report-quality validator）。
- Run 的 Command Summary 未列出该命令的执行结果。
- Plan 对该命令的约束是 "Only consumes explicit JSONL/bundle inputs; not product CLI."（Run Procedure step 3: "Run scripts/report_quality_eval.py only over explicit JSONL / bundle JSON inputs already assembled in scratch."）
- Run 未提及是否组装了 JSONL bundle 输入，也未显式声明该脚本为 "not run: no JSONL bundles assembled."

**Risk**: 低风险。该脚本是 dev-only wrapper，需要手动组装的 JSONL 输入，且 plan 将其定位为 optional。但 run artifact 中缺少显式的 "not run" 记录，使得 verifier matrix 的执行完整性无法闭环。

**Recommendation**: 不阻塞 closeout。Run artifact 应补充一行 "scripts/report_quality_eval.py: not run (no JSONL bundles assembled in scratch)" 以闭合 verifier matrix 跟踪。该补充可在 controller judgment 阶段以 note 形式完成，不需要 rerun。

---

### F3 — INFO: Plan 的 golden-missing 预期被实际证据修正；004194/006597 均有 golden coverage

**Evidence**:
- Plan（经 F2 修订后）预期 004194 和 006597 的 score 结果以 `year_not_covered/FQ0/info` 为主。
- Run 实际结果：004194/2024 correctness `available`, `covered`, 5/5 matches；006597/2024 correctness `available`, `partially_covered`, 9/9 matches。
- Run 在 Interpretation Notes 中正确更新了观察："004194 / 2024 did produce correctness signal in this run (covered, 5/5 matches), so it should not be reported as year_not_covered for this exact run."（line 60）

**Risk**: 无。Plan 的预期是基于保守假设，run 以实际证据修正预期是正确的 review-then-observe 行为。Golden coverage 比预期好的事实不影响任何 gate routing 或 decision。

---

### F4 — INFO: 006597 quality-gate `block` 正确识别，候选保留在 evaluation denominator 但被排除出 golden 路径

**Evidence**:
- 006597/2024 quality gate 返回 `block`，7 issues，missing-field rate 35.7%。（Command Summary line 36，Candidate Matrix line 45）
- Run 的 Clean Denominator 计数为 3，包含 006597。（line 53）
- Next Gate Recommendation 明确排除 golden corpus path："Do not enter golden answer corpus v1 yet...one clean slot (006597) is quality-gate blocked."（line 75）

**Risk**: 无。"Clean denominator" 在 plan 中的定义是 "非 fallback-blocked、非 FOF data-gap" 的评估候选集——quality gate block 是后观察结果，不是预排除条件。Run 正确区分了 "evaluation denominator"（含 006597）和 "golden-ready denominator"（排除 006597）。

---

### F5 — INFO: Scope adherence 完整，artifact hygiene 合规

**Evidence**:
- Run scope 声明与 plan Non-Goals 完全对齐：无 renderer/FQ0-FQ6/Service-CLI/Host-Agent-dayu/FundDocumentRepository/extractor/fixture/commit/push/PR 变更。
- 所有 command output 路径均在 scratch roots：`/tmp/...`、`reports/smoke/...`、`reports/extraction-snapshots/...`。
- `git diff --check` passed。（line 79）
- Run artifact 本身是 concise summary，未嵌入大型产物。

**Risk**: 无。

---

### F6 — INFO: Fallback-blocked 和 FOF data-gap 行正确排除，且无 clean denominator 污染

**Evidence**:
- 110020/2024: "Not re-run by this evaluation... clean denominator exclusion."（line 46）
- 017641/2024: "Not re-run by this evaluation... clean denominator exclusion."（line 47）
- 007721/2024: "Not run by design; data-gap row only."（line 48）
- 017970/2024: "Not run by design; data-gap/fallback-blocked row only."（line 49）
- Clean Denominator count: 3 candidates, 3 fund-type slots, 4 excluded rows。（lines 53-56）
- "No fallback-blocked or FOF data-gap row was treated as clean denominator."（line 64）

**Risk**: 无。排除逻辑与 plan Candidate Selection Strategy 完全一致。

---

### F7 — INFO: 004393/2025 probe-only 约束严格遵守

**Evidence**:
- Status flags: `probe_only`; repository identity not accepted for baseline。（line 43）
- "recorded only availability/year-scope, not final-judgment semantics"（line 24）
- "Do not consume final-judgment semantics from `--dev-override`"（Candidate Matrix line 43）
- "2024 golden/facts must not be reused for 2025 correctness"（Candidate Matrix line 43）
- "No snapshot/score run was requested for 2025 in this gate"（Candidate Matrix line 43）
- Quality gate info confirms: "existing 004393 golden rows do not cover 2025 and other-year golden is not used."（Interpretation Notes line 62）
- "No; report-year coverage missing and probe-only."（Candidate Matrix suitable-for-golden column）

**Risk**: 无。Probe-only 约束在 run artifact 的多个位置重复强调。

---

### F8 — INFO: Next gate recommendation 有证据支撑

**Evidence**:
- Run 推荐 "more baseline probing / source recovery / taxonomy" + data-extraction priority subpath。（line 68）
- 对应 plan decision rule: "Clean coverage is at or below three clean candidates, covers fewer than half the target fund-type slots, or FOF/index/QDII blockers dominate."
- 支撑证据：
  - 3/3 clean candidates（低于 5 目标）✓
  - 3/6 fund-type slots（不足一半）✓
  - 006597 quality-gate blocked ✓
  - index/QDII fallback-blocked ✓
  - FOF data-gap ✓
- Run 明确排除 golden corpus path 并给出理由。（line 75）
- 四条具体 next action 均有对应的 command evidence 或 accepted evidence 支撑。（lines 70-73）

**Risk**: 无。

---

## Verdict

**PASS_WITH_FINDINGS**

Run 的执行纪律、观察诚实度和 scope 边界均达到高质量水平。两个 MINOR finding 不阻塞 closeout：

1. **F1**: 004393/2025 checklist CLI flag deviation 已正确记录，无需 rerun，但 plan 未来应校验 flag 对子命令的可用性。
2. **F2**: `scripts/report_quality_eval.py` 未执行且未显式记录 "not run"，应在 controller judgment 中闭合。

| Finding | Severity | Blocks closeout? | Requires rerun? |
|---------|----------|-------------------|-----------------|
| F1: checklist CLI flag deviation | MINOR | No | No |
| F2: report_quality_eval.py not run | MINOR | No | No |
| F3: Golden coverage better than expected | INFO | No | No |
| F4: 006597 block correctly handled | INFO | No | No |
| F5: Scope adherence clean | INFO | No | No |
| F6: Exclusion logic correct | INFO | No | No |
| F7: 004393/2025 probe-only strict | INFO | No | No |
| F8: Next gate recommendation justified | INFO | No | No |

---

## Truth Source Alignment Confirmation

- [x] Run 不违反 `AGENTS.md` 硬约束：无 FundDocumentRepository 直访、无 fallback policy 修改、无 extra_payload、四层边界未突破。
- [x] Run 不违反 `docs/design.md` 非目标：renderer/FQ0-FQ6/Host-Agent/dayu 无变更。
- [x] Run 与 accepted plan scope 一致：所有命令均在 plan verifier matrix 范围内，fallback-blocked/FOF 排除逻辑与 plan 一致。
- [x] Run 不引入新的 source/test/product-flow 变更。
