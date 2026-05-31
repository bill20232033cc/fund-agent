# MVP programmatic audit L1 calibration implementation evidence

日期：2026-05-31

Gate：`MVP programmatic audit L1 calibration gate`

角色：Gateflow implementation worker。

## Self-check

- Current gate / role：只实现已批准 plan/review 的最小 implementation；不做 controller judgment、不 commit/push/PR/merge/release。
- Source of truth：已读取 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md`、`docs/fund-analysis-template-draft.md`、本 gate plan、MiMo/GLM plan review、上一 gate controller judgment/evidence，以及相关 `chapter_auditor` / `chapter_writer` / `chapter_orchestrator` / CLI / tests 代码。
- Scope boundary：只修改 L1 diagnostic taxonomy、L1 repair guidance、writer prompt 的短 L1 anchor rule、同源本地测试和本 evidence。未修改 golden、fixtures、score、quality gate、final judgment、Host/Agent/dayu、provider config/auth 或 PR 状态。
- Stop condition：未运行真实 provider；未保存完整 prompt、draft、provider response、raw audit response、API key 或 Authorization header。

## Changed files

- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-programmatic-audit-l1-calibration-implementation-evidence-20260531.md`

## Implemented scope

- 新增安全 subcategory：`l1_numerical_closure`。
- `_SUBCATEGORY_PRECEDENCE` 插入位置：`forbidden_phrase` 之后、`code_bug_other` 之前。理由：L1 需要压过 generic fallback，但不得掩盖 candidate facet 或禁用交易/越界措辞。
- `_audit_prompt_contract_diagnostic()` 统计 `programmatic:L1` prefix count，并只输出安全 prefix 和计数，不输出 line suffix、draft、prompt 或 provider response。
- `_required_correction_from_issue()` 对 L1 增加确定性修复项：公式/百分比闭合断言必须在同句或上下 2 行内放 allowed anchor；无同源事实时删除具体数值闭合断言并写未披露/数据不足/下一步最小验证问题；不得编造 Alpha/Beta/Cost/R 数值。
- L1 修复指令通过 typed `ChapterRepairContext.required_corrections` 传递；没有使用 `extra_payload`。
- Writer prompt 增加一条短 L1 anchor rule，限定第 2 章 R=A+B-C 数字闭环断言的 anchor proximity 和缺事实处理。
- CLI 不改退出码和输出机制；同一 Service fake result 下 first-failed category/subcategory 会透出 `prompt_contract / l1_numerical_closure`，不再落入 `unknown`。

## Slice 3 decision

Slice 3 skipped。代码同源分析显示当前 `_audit_numerical_closure()` 只在同一行同时命中公式模式与具体百分比时触发，且现有同源本地 fixture 能覆盖：

- `A=R-B，因此 Alpha 为 2.10%。` 缺邻近 anchor 继续触发 L1。
- `A-C 后的净超额为 1.20%。` 缺邻近 anchor 继续触发 L1。
- “数据不足”加具体无锚点闭环百分比仍触发 L1。
- 仅解释 `R=A+B-C` 框架、不写具体百分比不触发 L1。

没有发现需要收窄 `_audit_numerical_closure()` 的过严证据，因此本 gate 不改 L1 规则。

## Regression coverage

- Programmatic L1 audit issue 映射为 `failure_subcategory == "l1_numerical_closure"`，diagnostic `primary_subcategory == "l1_numerical_closure"`。
- Diagnostic payload 保留 `programmatic:L1` prefix count，不保存 line suffix、具体公式文本、prompt、draft 或 provider response。
- Candidate facet / forbidden phrase precedence 保持高于 L1。
- Fake writer 首轮输出无锚点 L1，二轮通过 typed repair context 输出邻近 anchor 后 accepted。
- Fake writer repair 后仍保留无锚点数字闭环时 fail-closed，subcategory 保持 `l1_numerical_closure`。
- CLI fake incomplete LLM result 透出 `first_failed_category=prompt_contract` 和 `first_failed_subcategory=l1_numerical_closure`，stdout 为空且不回退 deterministic。
- Auditor unsafe fixtures 保持 fail-closed；missing semantics 未用于放行具体 unsupported percentage。

## Validation

| Command | Result |
|---|---|
| `uv run ruff check fund_agent/fund/chapter_auditor.py fund_agent/fund/chapter_writer.py fund_agent/services/chapter_orchestrator.py tests/fund/test_chapter_auditor.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py` | PASS |
| `uv run pytest tests/fund/test_chapter_auditor.py tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py -q` | PASS, `180 passed` |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS, `1186 passed`, total coverage `91.85%` |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS, exit `0`; deterministic default unchanged |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS, exit `0`; deterministic checklist unchanged |
| isolated missing-config `--use-llm` with LLM env unset | PASS fail-closed, exit `1`, stdout bytes `0`, stderr first line `LLM provider 配置错误：missing FUND_AGENT_LLM_PROVIDER` |
| `git diff --check` | PASS |
| real provider `006597 / 2024 --use-llm` | NOT RUN, left to controller per instruction |

## Secret scan

Scoped scan target:

- modified L1 implementation/test files
- this implementation evidence artifact

Result：PASS. No API key value, bearer token, Authorization header value, full prompt, full draft, provider response body or raw audit response was stored by this gate. Any remaining literal hits in tests/code are field names, fake secret-sanitization strings, or assertions that those labels are not emitted.

## Residual risks / next entry

- Real provider validation remains controller-owned.
- If controller rerun still fails at `programmatic:L1`, the blocker should now be diagnosable as `l1_numerical_closure` rather than `code_bug_other` / `unknown`; next action depends on safe controller diagnostic counters.
- If controller rerun progresses beyond L1, use the next first-failed safe category/subcategory for the following gate.
