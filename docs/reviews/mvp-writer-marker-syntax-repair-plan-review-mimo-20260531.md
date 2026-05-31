# MVP writer marker syntax repair plan review (MiMo)

日期：2026-05-31

Gate：`MVP writer marker syntax repair gate`

角色：Plan reviewer，不是 implementation worker。

## Review scope

Review target：`docs/reviews/mvp-writer-marker-syntax-repair-plan-20260531.md`

Source of truth read：
- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- 上一 gate controller judgment：`docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-controller-judgment-20260531.md`
- Writer 代码：`fund_agent/fund/chapter_writer.py`
- Orchestrator 代码：`fund_agent/services/chapter_orchestrator.py`
- CLI 代码：`fund_agent/ui/cli.py`
- 现有测试：`tests/fund/test_chapter_writer.py`、`tests/services/test_chapter_orchestrator.py`、`tests/ui/test_cli.py`

## Review findings

### 1. Plan 是否真正对齐当前 blocker

**PASS。**

Plan 正确识别主 blocker：chapter 1 `writer_parse` / `prompt_contract.invalid_marker` / `writer:invalid_missing_marker`。引用了 controller judgment 的脱敏 diagnostic 证据（`invalid_marker_count=1`、`issue_id_prefix_counts={"writer:invalid_missing_marker": 1}`、`response_chars=2054`、`finish_reason=stop`），并正确区分 `invalid_marker`（本 gate 修复对象）与 `candidate_facet_assertion`（secondary monitored risk，不修不放）。

Plan 正确定位 next entry 为 prompt guidance repair，而非 parser relaxation。

### 2. 是否从代码同源解释 invalid missing marker

**PASS。**

Plan 的 root cause hypothesis 从代码同源推导：

- `_COMMENT_RE = r"<!--\s*([^>]*)-->"` 扫描所有 HTML comment
- `_MISSING_MARKER_RE = r"<!-- missing:([a-z_]+) -->"` 定义合法 missing marker
- `_invalid_marker_issues()` 对包含 `missing` 且不满足 `_MISSING_MARKER_RE.fullmatch()` 的 comment 产生 `writer:invalid_missing_marker`

Plan 明确列出会触发该 issue 的污染形态：空格污染、大小写污染、全角冒号、未替换 placeholder、reason 外包说明、code fence 中 marker。这些均从 regex 行为推导，不依赖 raw provider output。

Plan 有意不保存 raw provider response，confirmation method 使用现有脱敏 evidence + 代码同源推导 + 单测枚举矩阵。这是正确的设计决策。

### 3. 是否坚持不放宽 parser / allowed missing reasons / candidate facet / 安全边界

**PASS。**

Plan 的 Non-goals / hard constraints 明确列出：

- 不放宽 `_MISSING_MARKER_RE` 或 parser acceptance
- 不扩展 `ChapterFactMissingReason`
- 不把 unknown reason 当合法
- 不自动修正 / 补 marker
- 不 partial accept
- 不把弱证据或 candidate facet 包装成通过
- 不修改 golden/fixtures/score/quality gate/Host/Agent/dayu

Contract decisions 第 1 节重申合法 form 只有 `<!-- missing:<allowed_reason> -->` exact form，implementation 不得修改 parser。第 3 节重申 allowed reasons 仍来自 `chapter.missing_reasons` closed set，`_parse_missing_markers()` 的 closed-set + chapter allowed set 校验不变。第 4 节明确 candidate facet 仍为 secondary monitored risk，`candidate_facet_assertion` 仍是 prompt-contract blocker。

### 4. Prompt repair 方向是否最小且可测，是否避免 Markdown code-span 污染

**PASS。**

当前代码问题（`chapter_writer.py:434`）：

```python
"声明缺口必须使用 allowed missing marker：`<!-- missing:<reason> -->`；"
```

该行把 HTML comment marker 放在 Markdown code span（反引号）中，模型可能复制 code span 外的说明、改写空格/大小写/全角冒号。同时 allowed reasons 只在远处 JSON 文本中列出（`chapter_writer.py:449`），模型需要从 JSON payload 中复制 token，增加出错概率。

Plan 提出的修复方向：

- 用 explicit contract block（`MISSING_MARKER_EXACT_FORM` + `MISSING_MARKER_RULES`）替换内联 code span
- 把 allowed missing reasons 放在 marker guidance 附近作为稳定 token list
- 明确 placeholder 替换规则、禁止空格/大小写/翻译/反引号/code fence
- 当 allowed missing reasons 为空时，明确不得输出 missing marker

这是最小修复：只改 prompt guidance 文本，不改 parser、不改 orchestrator、不改 CLI。方向可测：测试只需断言 prompt 包含 `MISSING_MARKER_EXACT_FORM` 或等价标题、包含 exact form、包含 allowed reason token list、包含禁止规则。

Plan 给出的 bad examples 只使用合成污染形态（`<!-- missing :field_missing -->`、`<!-- Missing:field_missing -->` 等），不使用真实 provider 输出，符合 evidence policy。

### 5. Tests/validation 是否足够覆盖

**PASS。**

**Writer parser and prompt tests**（`tests/fund/test_chapter_writer.py`）：

| 测试场景 | 现有覆盖 | Plan 覆盖 |
|---|---|---|
| valid exact missing marker with allowed reason | `test_writer_parses_valid_anchor_and_missing_markers` | 保持 |
| invalid spacing `<!-- missing :field_missing -->` | 无明确覆盖 | Plan 要求新增 |
| invalid case `<!-- Missing:field_missing -->` | `test_writer_rejects_invalid_anchor_marker_spacing_or_case`（只测 anchor） | Plan 要求新增 missing 版本 |
| invalid fullwidth colon `<!-- missing：field_missing -->` | 无覆盖 | Plan 要求新增 |
| placeholder not replaced `<!-- missing:{reason} -->` | 无覆盖 | Plan 要求新增 |
| unknown reason `<!-- missing:unknown_reason -->` | `test_writer_rejects_unknown_missing_reason_marker` | 保持 |
| prompt includes exact marker block / allowed reasons / rules | 部分（`test_repair_context_is_rendered_into_writer_prompt`） | Plan 要求明确断言 `MISSING_MARKER_EXACT_FORM`、allowed token list、no-code-fence、no-placeholder |
| no allowed missing reasons says not to output marker | 无覆盖 | Plan 要求新增 |

现有测试缺少 invalid missing marker 的空格/大小写/全角冒号/placeholder 专项测试。Plan 正确识别了这些 gap 并要求补充。

**Orchestrator subcategory tests**（`tests/services/test_chapter_orchestrator.py`）：

| 测试场景 | 现有覆盖 | Plan 覆盖 |
|---|---|---|
| invalid missing marker → `failure_subcategory=invalid_marker` | `test_writer_unknown_missing_reason_counts_as_invalid_marker_without_raw_suffix` | 保持，plan 要求确认 prefix |
| serialized diagnostics exclude raw prompt/draft/response | 无明确 secret scan 测试 | Plan 要求新增 |
| candidate facet assertion remains blocked | `test_programmatic_candidate_facet_assertion_is_counted_not_accepted` | 保持 |
| accepted chapter `failure_subcategory is None` | `test_accepted_chapter_has_no_failure_category` | 保持 |

**CLI scalar and secret safety tests**（`tests/ui/test_cli.py`）：

| 测试场景 | 现有覆盖 | Plan 覆盖 |
|---|---|---|
| failed `--use-llm` stderr includes safe scalar | `test_use_llm_missing_config_stderr_includes_first_failed_subcategory` | 保持 |
| stdout empty on failed `--use-llm` | 同上 | 保持 |
| stderr excludes Authorization/Bearer/sk-/prompt/draft | 同上（assert `Authorization`/`Bearer` not in stderr） | Plan 要求扩展更多关键词 |

**Validation matrix**：

- `uv run ruff check .` → PASS
- `uv run pytest tests/fund/test_chapter_writer.py tests/services/test_chapter_orchestrator.py tests/ui/test_cli.py tests/config/test_llm_config.py tests/services/test_llm_provider.py -q` → PASS
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` → PASS
- `uv run fund-analysis analyze 006597 --report-year 2024` → PASS, deterministic exit 0
- `uv run fund-analysis checklist 006597 --report-year 2024` → PASS, deterministic exit 0
- isolated missing-config `--use-llm` → FAIL-CLOSED, exit 1, stdout empty
- authorized real provider `--use-llm` → full 0-7 report exit 0, or FAIL-CLOSED with sanitized first failed chapter/category/subcategory
- secret scan over new docs/reports → PASS

Validation matrix 覆盖了 deterministic unchanged、fail-closed、secret safety 和 real provider acceptance。Real provider commands 限制在 controller/authorized validation worker，不在 planning/unit-test worker 运行。

### 6. 是否不碰 golden/fixtures/score/quality gate/Host/Agent/dayu/PR 状态

**PASS。**

- Allowed files 明确列出 8 个文件 + 1 个 evidence artifact + 1 个 evidence 目录
- Non-goals 明确不修改 golden/fixtures/score/snapshot/quality gate/final judgment/manifest/promotion state
- 不进入 Host/Agent/dayu
- 不 push/PR/merge/release
- README 只在 public/developer-facing 变化时更新，本 gate 预期不需要
- Validation matrix 包含 deterministic unchanged 检查

## Non-blocking observations

1. **Prompt guidance change 需要测试断言精确匹配新 prompt 文本**。Plan 在 Slice A expected assertions 中列出了 `MISSING_MARKER_EXACT_FORM` 或等价稳定标题，但未指定具体文本。Implementation worker 需要在修改 prompt 后更新测试断言以匹配新 prompt 文本，这属于正常 implementation 细节，不阻塞 plan。

2. **现有 `test_writer_rejects_invalid_anchor_marker_spacing_or_case` 只测 anchor case 污染**。Plan 要求新增 missing marker 的空格/大小写/全角冒号/placeholder 测试，但未提及是否需要对 anchor marker 补充同类测试。这不是本 gate 范围，但可作为后续 hardening 关注点。

3. **Plan 的 allowed files 列表包含 `tests/config/test_llm_config.py` 和 `tests/services/test_llm_provider.py`**，但 Slice C 说明现有 secret-safety tests must still pass、no new provider config/auth behavior is introduced。这两个文件的 inclusion 合理（regression guard），但 implementation worker 不需要修改它们，只需确保现有测试通过。

## 结论

**PASS。**

Plan 正确对齐当前 blocker（`writer:invalid_missing_marker`），从代码同源解释 root cause，坚持不放宽 parser/allowed reasons/candidate facet 安全边界，prompt repair 方向最小且可测（从 Markdown code-span 改为 explicit contract block），tests/validation 覆盖足够（valid/invalid missing marker、orchestrator subcategory、CLI scalar、secret safety、deterministic unchanged），不碰 golden/fixtures/score/quality gate/Host/Agent/dayu/PR 状态。Gate classification 为 heavy 正确。Plan handoff-ready，可进入 implementation。
