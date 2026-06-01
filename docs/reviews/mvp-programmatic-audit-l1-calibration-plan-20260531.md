# MVP programmatic audit L1 calibration plan

日期：2026-05-31

Gate：`MVP programmatic audit L1 calibration gate`

角色：Gateflow planning worker，不是 implementation worker。

## Self-check

- Current gate / role：只产出 handoff-ready plan artifact；不改代码、不运行真实 provider、不 commit/push/PR/merge/release。
- Source of truth：已读取 `AGENTS.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`、上一 gate controller judgment / implementation evidence、最新安全 diagnostic JSON，以及必要的 `chapter_auditor` / `chapter_writer` / `chapter_orchestrator` / tests 代码。
- Scope boundary：本计划只覆盖 chapter 2 single-chapter programmatic audit `programmatic:L1` 校准、writer repair guidance 和安全诊断 taxonomy；不碰 golden、fixtures、score、quality gate、final judgment、Host/Agent/dayu、provider config/auth、PR 外部状态。
- Stop conditions：不得保存完整 prompt、draft、provider response、raw audit response、API key 或 Authorization header；不得把弱证据包装成 L1 通过；不得放松 candidate facet、证据锚点、ITEM_RULE、交易建议、E2 deferred 或 missing semantics。

## Goal

在 provider config/auth 已验证、chapter 1 已 accepted、当前 blocker 为 chapter 2 `programmatic_audit` issue prefix `programmatic:L1` 的前提下，完成最小 L1 calibration gate：

1. 用代码与安全 evidence 同源定位 `programmatic:L1` 的真实原因。
2. 区分真实 L1 数值/逻辑闭合不合格、audit rule 过严或缺 missing semantics、writer output 缺 L1 所需结构/数值关系、diagnostic taxonomy gap。
3. 修正最小必要实现，使 L1 仍 fail-closed，但诊断和 repair guidance 能精确指向 L1。
4. 真实 provider rerun 只由 controller 执行，并只保存安全摘要。

Gate classification：`heavy`。原因：L1 属于章节审计安全边界，且会影响 provider-backed LLM report 的 fail-closed 分类和 CLI diagnostic surface。

## Direct Evidence

- `docs/current-startup-packet.md`：下一入口为 `MVP programmatic audit L1 calibration gate`；真实 provider smoke 不是 config/auth 问题；chapter 1 已 accepted，chapter 2 first blocker 为 `programmatic_audit` / `programmatic:L1`。
- `docs/implementation-control.md`：当前 gate blocked；最新 service diagnostic 为 chapter 2 `programmatic_audit` with issue prefix `programmatic:L1`，service subcategory `code_bug_other`，CLI category `audit_rule_too_strict`。
- `docs/reviews/mvp-writer-marker-syntax-repair-controller-judgment-20260531.md`：上一 gate 已接受，marker parser/allowed reasons/candidate facet/ITEM_RULE/证据锚点/missing semantics 未放松；下一最小入口要求调查 `programmatic:L1`。
- `reports/mvp-local-acceptance/20260531-writer-marker-syntax-repair/controller-real-provider-006597-2024-diagnostic.json`：安全 JSON 显示 chapter 2 failed，phase `programmatic_audit`，`issue_id_prefix_counts={"programmatic:L1": 2}`，invalid marker / unknown anchor / forbidden phrase / candidate facet / required marker / required structure counts 均为 0，subcategory `code_bug_other`。
- `fund_agent/fund/chapter_auditor.py`：single-chapter L1 当前由 `_audit_numerical_closure()` 实现，匹配 `R=A+B-C` / `A=R-B` / `A-C` 等公式且同一行含百分比时，要求上下各 2 行内存在 `<!-- anchor:`。
- `tests/fund/test_chapter_auditor.py`：现有测试只覆盖“公式+百分比缺邻近 anchor 触发 L1”和“邻近 anchor 不触发 L1”。
- `fund_agent/services/chapter_orchestrator.py`：programmatic audit failed 且 repair_hint 非 `needs_more_facts` 时当前分类为 `prompt_contract`；`programmatic:L1` 未映射到专用 subcategory，因此落入 `code_bug_other`。`audit_rule_too_strict` 当前只表示 programmatic pass 后的 parseable LLM audit fail，不适合默认承载 programmatic L1。
- `fund_agent/services/chapter_orchestrator.py`：`_required_correction_from_issue()` 对 L1 没有专门 correction，repair prompt 只能回传脱敏 message，缺少“公式/百分比断言必须邻近 allowed anchor 或改写为缺口”的确定性指令。

## Root-cause Decision Tree

Implementation worker 必须先用本地 deterministic / fake LLM 构造同源样本，不使用真实 provider 原文，也不保存完整 draft。

1. 真实 L1 数值/逻辑闭合不合格：
   - 判定条件：草稿包含 `R=A+B-C` / `A=R-B` / `A-C` 与百分比数值的闭合断言，但断言附近没有 allowed anchor；或断言使用了不能由 chapter facts 支撑的数值关系。
   - 处理：保持 L1 fail-closed；增加 precise subcategory `l1_numerical_closure`；repair guidance 要求“有同源事实时在同一句或上下 2 行内放 allowed anchor；无同源事实时删除数值闭合断言并写缺口/下一步验证问题”。

2. Audit rule 对真实 provider 输出过严或缺少 missing semantics：
   - 判定条件：本地构造能复现 L1 误报，例如只是在解释公式框架而不是作出数值闭合断言，或明示数据不足但因公式模板文本+百分比语境误触发。
   - 处理：只允许收窄触发条件或加入明确 missing/gap guard；不得允许无锚点的数值闭合断言通过，不得把“数据不足”包装成通过。
   - 分类：不要默认把 programmatic L1 映射成 `audit_rule_too_strict`。若确认为规则误报，应以代码修正规则并用 regression 证明 unsafe case 仍触发 L1。

3. Writer output 缺少 L1 所需结构/数值关系：
   - 判定条件：L1 规则本身合理，但 writer 首轮或 repair 后仍把公式/百分比断言和 anchor 分离，或在无 facts 时输出百分比闭合断言。
   - 处理：补 writer prompt / repair_context 的 L1-specific required correction，而不是放松 auditor。

4. Diagnostic taxonomy gap：
   - 判定条件：安全 diagnostic 只能看到 `programmatic:L1` + `code_bug_other` / CLI `unknown` 或与 service category 不一致，无法指导下一步。
   - 处理：在 Service orchestration diagnostic 中新增 L1 专用 subcategory，例如 `l1_numerical_closure`；CLI first-failed subcategory 应同步输出该值。`audit_rule_too_strict` 保持为 programmatic pass 后 LLM audit fail 的 category，除非另有同源证据和 controller decision 改变其语义。

## Affected Files / Modules

Allowed implementation files:

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/fund/chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/fund/test_chapter_writer.py`
- `tests/ui/test_cli.py` only if CLI first-failed assertions need the new subcategory
- gate evidence under `docs/reviews/` and safe summaries under `reports/mvp-local-acceptance/20260531-programmatic-audit-l1-calibration/`

Explicitly forbidden:

- golden / fixtures / score / quality gate / final judgment / Host / Agent / dayu / provider config/auth / PR state
- deterministic `fund-analysis analyze` and `fund-analysis checklist` default semantics
- complete prompt, draft, provider response or raw audit response persistence

## Implementation Slices

### Slice 1: L1 diagnostic taxonomy

Objective：make `programmatic:L1` diagnosable without changing pass/fail behavior.

Required changes:

- Extend `ChapterFailureSubcategory` with `l1_numerical_closure`.
- In `_audit_prompt_contract_diagnostic()`, count programmatic L1 issues from sanitized prefixes or rule code.
- Extend `_primary_subcategory()` inputs or add a dedicated programmatic-audit classifier so L1 beats `code_bug_other` but does not beat candidate facet / forbidden phrase precedence unless tests require otherwise.
- Preserve payload safety: store only prefix counts and scalar counters, no issue suffix, location raw text, draft, prompt or response.

Tests:

- Programmatic L1 audit issue maps to `failure_subcategory == "l1_numerical_closure"` and diagnostic `primary_subcategory == "l1_numerical_closure"`.
- Diagnostic payload contains `programmatic:L1` count but no line text, anchor id suffix, prompt, draft or provider response.
- Existing candidate facet / forbidden phrase / invalid marker tests still fail closed and keep their precedence.

### Slice 2: L1-specific repair guidance

Objective：make bounded repair capable of correcting true writer-output L1 failures without weakening L1.

Required changes:

- Add an L1 branch to `_required_correction_from_issue()`.
- Correction wording must be deterministic and safe:
  - formula/percentage closure claims must place an allowed anchor marker in the same sentence or within the existing auditor proximity window;
  - if no same-source fact supports the numeric relation, remove the numeric closure claim and write `未披露 / 数据不足 / 下一步最小验证问题`;
  - do not invent Alpha/Beta/Cost/R values.
- If needed, add a short initial writer prompt rule near anchor guidance for chapter 2 R=A+B-C numeric closure, but do not expand prompt with long examples.

Tests:

- `_required_corrections_from_issues()` returns an L1-specific correction for a `programmatic:L1` issue.
- Writer repair prompt carries the L1 correction through typed `ChapterRepairContext`, with no `extra_payload`.
- Fake writer first emits L1 failure, second emits anchored correction; orchestrator accepts after repair.
- Fake writer keeps unanchored numeric closure after repair; orchestrator fails closed with subcategory `l1_numerical_closure`.

### Slice 3: Conditional L1 rule calibration

Objective：only if same-source local reproduction proves current L1 rule is too broad, narrow the rule without weakening safety.

Allowed changes:

- Adjust `_audit_numerical_closure()` trigger conditions only for clearly non-assertive formula mentions or explicit missing/gap wording.
- Keep unsafe examples blocked:
  - `A=R-B，因此 Alpha 为 2.10%。` without nearby anchor must fail.
  - numeric closure with unknown anchor must fail through E1/L1 as applicable.
  - “数据不足” plus a concrete unanchored closure percentage must not pass.

Tests:

- Existing L1 fail/pass tests remain.
- New false-positive fixture passes only when it contains no numeric closure assertion or uses explicit missing semantics without concrete unsupported percentage.
- New unsafe fixture remains fail-closed.

If no overstrict evidence exists, skip Slice 3 and record “rule unchanged; writer/taxonomy only” in implementation evidence.

### Slice 4: CLI/service taxonomy alignment

Objective：remove the service `code_bug_other` vs CLI `audit_rule_too_strict` ambiguity for this blocker.

Required checks:

- Ensure service diagnostic first_failed and chapter matrix expose `subcategory=l1_numerical_closure` for programmatic L1.
- Ensure CLI first-failed summary prints the same subcategory when the same run result is surfaced.
- Do not change CLI exit behavior: incomplete LLM result still exits `1`, stdout empty, no deterministic fallback.

Tests:

- CLI fail-closed test can assert `first_failed_subcategory=l1_numerical_closure` for a fake orchestration result if existing test scaffolding supports it.
- Existing timeout/missing-config CLI tests remain unchanged.

## Validation Plan

No real provider in implementation worker validation.

Required local commands:

| Command | Expected |
|---|---|
| `uv run ruff check fund_agent/fund/chapter_auditor.py fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py` | PASS |
| `uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py -q` | PASS |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS, deterministic default unchanged |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS, deterministic checklist unchanged |
| isolated missing-config `--use-llm` with LLM env unset | fail-closed exit `1`, stdout empty |
| `git diff --check` | PASS |

Evidence artifact must record commands and results, plus whether Slice 3 was skipped or applied.

## Controller Real-provider Rerun Matrix

After implementation review passes, controller may rerun real provider. Store only safe summaries.

| Evidence | Required safe fields | Must not store |
|---|---|---|
| CLI `fund-analysis analyze 006597 --report-year 2024 --use-llm` | exit code, stdout byte count, whether report headings 0-7 are present if success, stderr first-failed scalars | full stdout report, full prompt, full draft, provider response, API key/header |
| Service diagnostic serialization | schema version, orchestration status, first_failed chapter/phase/category/subcategory, issue prefix counts, scalar counters, final assembly status | accepted draft markdown, raw prompt, raw LLM response, raw audit response |
| Secret scan | scan target paths and PASS/FAIL | secret values |

Expected controller interpretations:

- If chapter 2 progresses beyond `programmatic:L1`, this gate can be accepted locally and Gate B remains subject to the next blocker or complete smoke result.
- If chapter 2 still fails `programmatic:L1` but subcategory is `l1_numerical_closure` with safe counters and no `code_bug_other` / `unknown`, calibration is successful but real smoke remains blocked; controller decides whether a narrower writer follow-up is needed.
- If `programmatic:L1` is still `code_bug_other`, `unknown`, or masked as `audit_rule_too_strict` without same-source explanation, this gate is blocked.
- If any complete prompt/draft/provider response is persisted, this gate is blocked even if tests pass.

## Pass / Blocked Criteria

Pass criteria:

- L1 unsafe cases remain fail-closed.
- `programmatic:L1` has a precise safe subcategory, preferably `l1_numerical_closure`, instead of `code_bug_other`.
- Repair context gives a deterministic L1 correction when L1 is writer-correctable.
- Any rule narrowing is backed by same-source local tests and does not pass unanchored numeric closure assertions.
- Deterministic analyze/checklist remain unchanged.
- No forbidden files or external state are modified.
- Implementation evidence and controller rerun evidence do not store full prompt/draft/provider response.

Blocked criteria:

- Root cause relies on indirect inference rather than code/evidence同源。
- L1 is relaxed so unanchored numeric closure, weak evidence, or unsupported percentages pass.
- Missing semantics is used to pass concrete unsupported numeric claims.
- Candidate facet, evidence anchors, ITEM_RULE, trading advice, E2 deferred, missing semantics, quality gate, score, final judgment, golden or Host/Agent/dayu boundaries are modified.
- CLI/service taxonomy remains inconsistent for the same `programmatic:L1` failure.
- Real provider rerun is required for implementation validation, or unsafe raw provider material is saved.

## Docs Decision

No README update is required for taxonomy-only / prompt repair implementation unless the implementation changes documented user-facing CLI behavior beyond exposing a more precise existing first-failed subcategory. If tests are added, no `tests/README.md` change is required unless test running conventions change.

## Review Requirements

Require at least two independent code reviews because this gate touches audit safety semantics and CLI diagnostic taxonomy. Reviewers must specifically check:

- L1 fail-closed boundary.
- Same-source root-cause evidence.
- Diagnostic payload safety.
- No default deterministic behavior changes.
- No forbidden scope changes.

## Next Minimal Entry

After this plan artifact：start `MVP programmatic audit L1 calibration plan review gate`.

After accepted plan/review：start `MVP programmatic audit L1 calibration implementation gate` with the slices above, then code review, fix/re-review, controller real-provider rerun, and controller judgment.
