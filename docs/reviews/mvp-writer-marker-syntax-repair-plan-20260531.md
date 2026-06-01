# MVP writer marker syntax repair plan

日期：2026-05-31

Gate：`MVP writer marker syntax repair gate`

角色：Gateflow planning worker，不是 implementation worker。

## Self-check

- Current gate / role：当前只写 handoff-ready plan artifact；不实现、不 review、不 commit/push/PR/merge/release，不运行真实 provider。
- Source of truth：已读取 `AGENTS.md`、`docs/current-startup-packet.md`、`docs/implementation-control.md`、writer diagnostic narrowing controller judgment / implementation evidence、脱敏 service diagnostic JSON，以及 writer / orchestrator / CLI / tests 相关代码。
- Scope boundary：后续 implementation 只能做最小 marker syntax repair；不得改 golden/fixtures/score/quality gate/final judgment/Host/Agent/dayu/provider auth/config。
- Stop condition：若需要保存 API key、Authorization header、完整 prompt、完整 draft、完整 provider response，或需要放宽 parser、allowed missing reasons、candidate facet 边界，则停止回 controller。
- Evidence and validation：本 gate 以脱敏 scalar/counter/issue prefix 为证据；真实 provider 只在 implementation validation 阶段由授权 worker 运行。
- Next action：plan review 通过后进入最小 implementation；本 artifact 不授权当前 planning worker 执行 provider。

## Handoff readiness

Status：handoff-ready。

Gate classification：heavy。原因是 writer marker contract 属于 provider-backed LLM 报告安全失败语义；分类不确定时按 `AGENTS.md` 选择更重一级。

## Goal / motivation

在 provider config/auth 已验证可用、当前主 blocker 为 chapter 1 writer_parse `prompt_contract.invalid_marker` / issue prefix `writer:invalid_missing_marker` 的前提下，做最小 marker syntax repair，使真实 provider 更稳定输出合法 allowed missing marker。

若真实 provider 仍失败，必须保持精确 fail-closed：失败仍通过 `failure_category`、`failure_subcategory`、chapter/phase/attempt 和脱敏 issue prefix 定位，不输出 partial report，不回退 deterministic。

## Direct evidence

已接受诊断证据：

- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-controller-judgment-20260531.md` 记录最新主 blocker：chapter `1`、phase `writer_parse`、category `prompt_contract`、subcategory `invalid_marker`、issue prefix `writer:invalid_missing_marker`。
- `reports/mvp-local-acceptance/20260531-writer-prompt-contract-diagnostic-narrowing/controller-real-provider-006597-2024-diagnostic.json` 只保存脱敏字段：`invalid_marker_count=1`、`issue_id_prefix_counts={"writer:invalid_missing_marker": 1}`、`response_chars=2054`、`finish_reason=stop`、`required_output_missing_count=0`、`required_structure_missing_count=0`、`unknown_anchor_count=0`。
- 同一 controller judgment 记录 CLI rerun 还观察到 `candidate_facet_assertion`；这是 secondary risk，不是本 gate 放松对象。

代码事实：

- `fund_agent/fund/chapter_writer.py` 的合法 missing marker parser 为 `_MISSING_MARKER_RE = r"<!-- missing:([a-z_]+) -->"`。
- `_invalid_marker_issues()` 会扫描所有 HTML comment；只要 comment payload 包含 `missing` 且整段 comment 不满足合法 missing marker regex，就产生 `writer:invalid_missing_marker:<offset>`，reason=`llm_contract_violation`。
- `_parse_missing_markers()` 只接受 `ChapterFactMissingReason` closed set 且必须在本章 `chapter.missing_reasons` 中；未知 reason 仍 fail-closed，不得在本 gate 放宽。
- 当前 prompt guidance 使用 Markdown code span 展示 `<!-- missing:<reason> -->`，并把可用缺口原因作为 JSON 文本列出。真实模型可能污染 HTML comment 空格、冒号、大小写、placeholder 或 reason 选择。

## Root cause hypothesis and confirmation method

Root cause hypothesis：

1. 当前 prompt 把 HTML comment marker 放在 Markdown code span 中，模型可能复制 code span 外的说明、改写空格、大小写、全角冒号或 placeholder。
2. 当前 guidance 只给 `<!-- missing:<reason> -->` 抽象形式，没有把“必须替换 `<reason>` 为本章 allowed reason 的 exact token”降低到最低认知负担。
3. `writer:invalid_missing_marker` 与 `writer:unknown_missing_reason` 已被脱敏区分；本次真实 evidence 是前者，说明主要问题更可能是 comment 语法污染，而不是 reason 语义放宽需求。

确认方式：

- 使用现有脱敏 evidence 确认类别：只引用 `invalid_marker_count`、`writer:invalid_missing_marker` prefix、chapter/phase/attempt、response length/finish reason，不保存 raw provider response。
- 使用代码同源确认形态范围：从 `_COMMENT_RE`、`_MISSING_MARKER_RE`、`_invalid_marker_issues()` 推导哪些 comment 形态会进入 `writer:invalid_missing_marker`。
- 用单测枚举污染形态确认 parser 仍 fail-closed：空格污染、大小写污染、全角冒号、未替换 placeholder、reason 外包说明、code fence 中 marker 等都必须 blocked。
- 不要求还原真实 provider 的完整 offending marker；当前设计有意不保存 raw response，implementation evidence 只能记录脱敏 class 和复现矩阵。

## Non-goals / hard constraints

- 不修改 golden、fixtures、score、snapshot、quality gate、final judgment、manifest、promotion state。
- 不进入 Host/Agent/dayu，不新增 `fund_agent/host` / `fund_agent/agent`，不引入 `dayu.host` / `dayu.engine`。
- 不 push、不创建/更新 PR、不 merge、不 release、不 mark ready。
- 不保存 API key、Authorization header、完整 prompt、完整 draft、完整 provider response、raw audit response 或 env dump。
- 不放宽 allowed missing reasons，不扩展 `ChapterFactMissingReason`，不把 unknown reason 当合法。
- 不放宽 `_MISSING_MARKER_RE` 或 parser acceptance，不自动修正 marker，不自动补 marker，不 partial accept。
- 不把弱证据、candidate facet 或缺证据包装成通过。
- 默认 deterministic `fund-analysis analyze/checklist` 行为不变。

## Allowed files / modules

后续 implementation worker 只能按需编辑：

- `fund_agent/fund/chapter_writer.py`
- `fund_agent/services/chapter_orchestrator.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_chapter_writer.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/ui/test_cli.py`
- `tests/config/test_llm_config.py`
- `tests/services/test_llm_provider.py`
- `docs/reviews/mvp-writer-marker-syntax-repair-implementation-evidence-20260531.md`
- `reports/mvp-local-acceptance/20260531-writer-marker-syntax-repair/`

README 只在 public/developer-facing 当前用法发生变化时由 controller 明确授权更新；本 gate 预期不需要 README。

## Contract decisions

### 1. Allowed missing marker form stays exact

合法 form 仍然只有：

```text
<!-- missing:<allowed_reason> -->
```

其中：

- `<!--` 与 `-->` 必须是 ASCII HTML comment delimiter。
- `missing` 必须小写。
- `missing` 后必须紧跟 ASCII `:`。
- `<allowed_reason>` 必须替换为本章 `chapter.missing_reasons` 里的 exact token。
- `:` 后不能有空格；reason 后必须是一个空格再接 `-->`。
- marker 内不得出现中文说明、反引号、JSON、Markdown bullet、额外标签或 placeholder。

Implementation 不得修改 parser 来接受更多 form。修复方向只能是 prompt guidance 让模型更容易输出当前 exact form。

### 2. Prompt guidance should avoid Markdown code-span pollution

把 missing marker guidance 从内联 Markdown code span 改成更不易被模型污染的 plain contract block。建议使用明确字段而不是反引号示例：

```text
MISSING_MARKER_EXACT_FORM:
<!-- missing:{reason} -->

MISSING_MARKER_RULES:
- Replace {reason} with one token from ALLOWED_MISSING_REASONS.
- Do not output {reason}.
- Do not add spaces around ":".
- Do not translate "missing".
- Do not wrap the marker in backticks or code fences.
```

如果实现需要给示例/禁例，必须脱敏且使用合成 reason，不使用真实 provider response：

- good example 可用当前 closed-set 的公开枚举值，如 `field_missing`，前提是该 reason 在测试 chapter 的 allowed set 中。
- bad examples 只能是合成污染形态，如 `<!-- missing :field_missing -->`、`<!-- Missing:field_missing -->`、`<!-- missing:{reason} -->`、`` `<!-- missing:field_missing -->` ``。
- evidence artifact 只能写这些合成 examples，不保存真实模型输出。

### 3. Allowed reasons remain closed and chapter-scoped

- `可用缺口原因` 仍来自 `chapter.missing_reasons`。
- Writer prompt 可以把 allowed reasons 以一行 token list 形式放在 marker block 附近，降低模型从 JSON 中复制错 token 的概率。
- 如果 `chapter.missing_reasons` 为空，prompt 必须说明不得输出 missing marker；只能写“未披露 / 数据不足 / 下一步最小验证问题”等缺口表达，但不能断言事实。
- `_parse_missing_markers()` 的 closed-set + chapter allowed set 校验不变。

### 4. Candidate facet stays secondary monitored risk

本 gate 不修、不放松 candidate facet：

- `non_asserted_facets` 仍只能作为候选信息出现。
- `candidate_facet_assertion` 仍是 prompt-contract blocker。
- 如果 marker syntax repair 后真实 provider 首个失败变为 `candidate_facet_assertion`，controller 下一入口应是 `MVP candidate facet assertion repair gate`，而不是把本 gate 视为 pass。

## Implementation slices

### Slice A: writer missing marker guidance repair

Files:

- `fund_agent/fund/chapter_writer.py`
- `tests/fund/test_chapter_writer.py`

Tasks:

1. 在 `build_chapter_prompt()` 中把 missing marker guidance 调整为 explicit contract block。
2. 把 allowed missing reasons 放在 marker guidance 附近，建议使用稳定 token list，而不是只依赖远处 JSON payload。
3. 明确 placeholder 替换规则、禁止空格污染、禁止大小写/翻译/反引号/code fence。
4. 当 allowed missing reasons 为空时，明确不得输出 missing marker。
5. 保持 `_MISSING_MARKER_RE`、`_invalid_marker_issues()`、`_parse_missing_markers()` 行为不变。

Expected assertions:

- prompt 包含 `MISSING_MARKER_EXACT_FORM` 或等价稳定标题。
- prompt 包含 exact form `<!-- missing:{reason} -->` 或明确 placeholder form。
- prompt 包含 allowed missing reason token list。
- prompt 明确禁止输出 `{reason}` placeholder、空格污染、翻译和 code fence。
- parser valid case 仍只接受 exact allowed reason。
- invalid missing marker 仍 blocked with `writer:invalid_missing_marker` / `llm_contract_violation`。
- unknown allowed reason 仍 blocked with `writer:unknown_missing_reason` / `llm_contract_violation`。

### Slice B: diagnostic propagation regression guard

Files:

- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_chapter_orchestrator.py`

Tasks:

1. 不新增 raw diagnostics；只保持现有 `ChapterPromptContractDiagnostic` scalar/counter path。
2. 增加/调整测试确保 invalid missing marker 仍归类为 `failure_subcategory=invalid_marker`，prefix 不包含 raw suffix。
3. 增加测试确保 `candidate_facet_assertion` 仍阻断且 subcategory 不被 marker repair 覆盖。
4. 确保 accepted chapter `failure_subcategory is None`。

Expected assertions:

- `issue_id_prefix_counts == {"writer:invalid_missing_marker": 1}` 或包含该 prefix。
- `invalid_marker_count == 1`。
- raw reason、raw marker、raw prompt、raw draft 不出现在 serialized diagnostic。

### Slice C: CLI and serialization secret-safety guard

Files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `tests/config/test_llm_config.py`
- `tests/services/test_llm_provider.py`

Tasks:

1. CLI scalar behavior不应变化；如现有代码已输出 `first_failed_subcategory`，只补 regression test。
2. 确保 failed `--use-llm` stdout empty，stderr 只包含 safe first-failed scalars。
3. 确保 config/provider error paths 不泄漏 secret、Authorization、Bearer、prompt/draft/provider response。
4. 不新增真实 provider pytest；provider tests 继续用 fake env / MockTransport。

## Test plan

### Writer parser and prompt tests

`tests/fund/test_chapter_writer.py`:

- valid exact missing marker with allowed reason drafts and records `declared_missing_reasons`。
- invalid missing marker spacing blocks：`<!-- missing :field_missing -->`。
- invalid missing marker case blocks：`<!-- Missing:field_missing -->`。
- invalid missing marker fullwidth colon blocks：`<!-- missing：field_missing -->`。
- placeholder not replaced blocks：`<!-- missing:{reason} -->`。
- unknown reason blocks：`<!-- missing:unknown_reason -->`，且不被当作 allowed reason。
- prompt guidance includes exact marker block, allowed reasons, no-code-fence rule, no-placeholder rule。
- prompt guidance for no allowed missing reasons says not to output missing marker。

### Orchestrator subcategory tests

`tests/services/test_chapter_orchestrator.py`:

- invalid missing marker writer result -> `failure_category=prompt_contract` / `failure_subcategory=invalid_marker`。
- serialized diagnostics include `writer:invalid_missing_marker` prefix and `invalid_marker_count=1`。
- serialized diagnostics exclude raw prompt/draft/provider response/Authorization/Bearer/API-key-like values。
- candidate facet assertion remains blocked and monitored as `candidate_facet_assertion`。
- provider timeout remains `llm_timeout` and has no prompt-contract subcategory。

### CLI scalar and serialization secret safety tests

`tests/ui/test_cli.py`:

- incomplete `--use-llm` stderr includes safe `first_failed_subcategory` scalar。
- stdout remains empty on failed `--use-llm`。
- stderr excludes `Authorization`、`Bearer`、`sk-`、`system_prompt`、`user_prompt`、`draft_markdown`、raw provider response wording。

`tests/config/test_llm_config.py` / `tests/services/test_llm_provider.py`:

- existing secret-safety tests must still pass。
- no new provider config/auth behavior is introduced。

## Validation matrix

Implementation worker must run and record:

| Command | Expected |
|---|---|
| `uv run ruff check .` | PASS |
| `uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py tests/config/test_llm_config.py tests/services/test_llm_provider.py -q` | PASS |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | PASS |
| `uv run fund-analysis analyze 006597 --report-year 2024` | PASS, deterministic exit `0` |
| `uv run fund-analysis checklist 006597 --report-year 2024` | PASS, deterministic exit `0` |
| isolated missing-config `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | FAIL-CLOSED, exit `1`, stdout empty, missing config only |
| authorized real provider `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | full 0-7 report exit `0`, or FAIL-CLOSED with sanitized first failed chapter/category/subcategory |
| authorized real provider service diagnostic serialization | safe JSON only; no prompt/draft/raw response |
| secret scan over new docs/reports | PASS; no API key/Auth header/full prompt/full draft/full provider response |

Real provider commands must not run in planning or unit-test workers. They are controller/authorized validation steps only.

## Evidence policy

Allowed evidence under `reports/mvp-local-acceptance/20260531-writer-marker-syntax-repair/`:

- exitcode/stdout/stderr for deterministic analyze/checklist and missing-config smoke。
- real-provider stdout/stderr/exitcode only if run by authorized worker; stdout may be report output only on success, but failure stdout must remain empty。
- sanitized service diagnostic JSON using existing `serialize_chapter_prompt_contract_diagnostics()` shape。
- command labels, exit codes, stdout byte counts, chapter/phase matrix, issue prefix counts, response length scalar, finish reason scalar。

Forbidden evidence:

- API key, Authorization header, Bearer token, env dump。
- full prompt, full draft, full provider response, raw audit response。
- copied live offending marker text from provider output。
- raw candidate facet text beyond existing safe labels already present in code/test fixtures。

## Pass / blocked criteria

Pass criteria:

- All local validations pass。
- Deterministic analyze/checklist remain unchanged and pass。
- Missing-config `--use-llm` still fail-closes before Service execution with stdout empty。
- Parser remains strict: valid allowed missing marker accepted; invalid/unknown markers blocked。
- Real provider `006597 / 2024 --use-llm` either:
  - exits `0` with complete 0-7 report; or
  - exits `1` with stdout empty and precise sanitized failure category/subcategory that is no longer `invalid_marker` from missing marker syntax.

Blocked criteria:

- `writer:invalid_missing_marker` remains the first failure after prompt guidance repair and no additional safe signal narrows it further。
- Any validation requires saving raw provider text, prompt, draft, token, or Authorization header。
- Any implementation proposal needs parser relaxation, allowed missing reason expansion, auto-repair, deterministic fallback, or candidate facet relaxation。
- Real provider first failure becomes `candidate_facet_assertion`; this is a safe fail-closed outcome but blocks smoke acceptance and routes to the next gate。
- Real provider fails with provider runtime/timeout; route back to provider runtime diagnostics rather than broadening prompt/parser。

## Next minimal entry

- If pass with complete 0-7 report：return to `MVP real provider smoke acceptance gate` for controller acceptance and review。
- If first failure is `candidate_facet_assertion`：start `MVP candidate facet assertion repair gate`。
- If first failure is provider timeout/runtime：start provider runtime follow-up gate using existing timeout diagnostics。
- If first failure remains `invalid_marker` with `writer:invalid_missing_marker`：controller should decide whether a second prompt-only marker simplification gate is justified; do not relax parser by default。
