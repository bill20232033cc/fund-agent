# MVP writer marker syntax repair plan review (GLM)

日期：2026-05-31

Reviewer：GLM（plan reviewer，不是 implementation worker）

Gate：`MVP writer marker syntax repair gate`

## 审查范围

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-writer-marker-syntax-repair-plan-20260531.md`（本 review 对象）
- `docs/reviews/mvp-writer-prompt-contract-diagnostic-narrowing-controller-judgment-20260531.md`（上一 gate controller judgment）
- `fund_agent/fund/chapter_writer.py`（writer 实现，含 prompt 构造和 marker parser）
- `fund_agent/services/chapter_orchestrator.py`（Service 层编排和诊断）
- `tests/fund/test_chapter_writer.py`、`tests/services/test_chapter_orchestrator.py`、`tests/ui/test_cli.py`（现有测试头部）

未运行真实 provider，未修改代码。

## 结论

**PASS** — 无 blocking findings。

Plan 对齐当前 blocker，root cause 从代码同源推导，安全边界全部保持，prompt repair 方向最小且可测，测试覆盖充分，scope 不触碰 golden/fixtures/score/quality gate/Host/Agent/dayu/PR 状态。

以下为逐项审查结果。

---

## 1. Plan 是否对齐当前 blocker

**对齐。**

上一 gate controller judgment 记录的唯一主 blocker 为：

- chapter `1` / phase `writer_parse` / `prompt_contract.invalid_marker` / issue prefix `writer:invalid_missing_marker`

Plan Goal 明确聚焦此 blocker，不分散到 candidate facet、provider timeout 或 fact gap。Plan §Direct evidence 引用的脱敏诊断字段（`invalid_marker_count=1`、`writer:invalid_missing_marker` prefix、`response_chars=2054`、`finish_reason=stop`）与 controller judgment §Sanitized Matrix Summary 完全一致。

Plan §Candidate facet stays secondary monitored risk 正确将 `candidate_facet_assertion` 保留为 monitored secondary boundary，不将本 gate 视为解决 candidate facet 的入口。

## 2. 是否从代码同源解释 invalid missing marker

**是，代码同源。**

Plan §Direct evidence 引用了三个关键代码事实：

1. `_MISSING_MARKER_RE = r"<!-- missing:([a-z_]+) -->"`（`chapter_writer.py:54`）—— 合法 marker regex。
2. `_invalid_marker_issues()`（`chapter_writer.py:886-918`）扫描所有 HTML comment，对 payload 含 `missing` 且整段 comment 不满足 `_MISSING_MARKER_RE` 的情况产生 `writer:invalid_missing_marker:<offset>` / `llm_contract_violation`。
3. `_parse_missing_markers()`（`chapter_writer.py:1026-1058`）只接受 `ChapterFactMissingReason` closed set 且必须在本章 `chapter.missing_reasons` 中。

经代码验证：

- `_COMMENT_RE = r"<!--\s*([^>]*)-->"`（`chapter_writer.py:55`）确实会匹配所有 HTML comment。
- `_invalid_marker_issues()` 对每个 comment match 检查 `"missing" in payload.lower()` 且 `_MISSING_MARKER_RE.fullmatch(match.group(0)) is None`，准确对应 `writer:invalid_missing_marker` 语义。
- `_parse_missing_markers()` 先检查 `_SUPPORTED_MISSING_REASONS`（从 `ChapterFactMissingReason` Literal 提取的 `frozenset`），再检查 `allowed`（来自 `chapter.missing_reasons`），两层 fail-closed。

Plan §Root cause hypothesis 列举的污染形态（空格、大小写、全角冒号、placeholder 未替换、reason 外包说明）与 `_MISSING_MARKER_RE` 精确匹配规则完全一致。这些形态都会导致 `_MISSING_MARKER_RE.fullmatch()` 返回 `None`，从而进入 `_invalid_marker_issues()` 的 `writer:invalid_missing_marker` 分支。

Plan 不要求还原真实 provider 的完整 offending marker；这是正确的，因为设计有意不保存 raw response，且从 parser regex 同源枚举已足够覆盖所有可能的污染路径。

## 3. 是否坚持不放宽 parser / allowed missing reasons / candidate facet / 安全边界

**坚持。**

Plan 在多处显式声明不放退：

- §Non-goals / hard constraints：「不放宽 `_MISSING_MARKER_RE` 或 parser acceptance，不自动修正 marker，不自动补 marker，不 partial accept。」
- §Non-goals：「不放宽 allowed missing reasons，不扩展 `ChapterFactMissingReason`，不把 unknown reason 当合法。」
- §Contract Decision 1：「Implementation 不得修改 parser 来接受更多 form。修复方向只能是 prompt guidance 让模型更容易输出当前 exact form。」
- §Contract Decision 4：「本 gate 不修、不放松 candidate facet」；「如果 marker syntax repair 后真实 provider 首个失败变为 `candidate_facet_assertion`，controller 下一入口应是 `MVP candidate facet assertion repair gate`，而不是把本 gate 视为 pass。」
- §Block criteria：「Any implementation proposal needs parser relaxation, allowed missing reason expansion, auto-repair, deterministic fallback, or candidate facet relaxation」列为 blocked criteria。

经代码验证，`_MISSING_MARKER_RE`、`_invalid_marker_issues()`、`_parse_missing_markers()` 的行为在 Slice A tasks 中被明确要求保持不变（task 5），且 Slice B 和 Slice C 不涉及 writer parser 修改。

## 4. Prompt repair 方向是否最小且可测，是否避免 Markdown code-span 污染

**最小、可测、避免 code-span 污染。**

Root cause hypothesis 正确指向当前 prompt 的 code-span 污染问题。代码验证：`chapter_writer.py:434` 当前的 prompt 行为：

```python
"声明缺口必须使用 allowed missing marker：`<!-- missing:<reason> -->`；"
```

marker 被包在反引号中，且 `<reason>` 是 placeholder 形式。模型可能：(a) 复制反引号导致 comment 被 `` ` `` 包裹；(b) 不替换 `<reason>` 直接输出 literal text；(c) 在 `missing:` 前后加空格。

Plan §Contract Decision 2 提出的修复方向：

- 用 `MISSING_MARKER_EXACT_FORM:` / `MISSING_MARKER_RULES:` plain contract block 替代反引号示例。
- 把 `{reason}` 占位规则明确化：「Replace {reason} with one token from ALLOWED_MISSING_REASONS. Do not output {reason}.」
- 把 allowed missing reasons 从远处 JSON payload 移到 marker guidance 附近。
- 当 allowed reasons 为空时，明确不得输出 missing marker。

这四个修复点都是 prompt guidance 层面的文本调整，不涉及 parser、data structure 或 behavioral contract 变化。实现范围严格限定在 `build_chapter_prompt()` 中的 prompt 文本构造。

Plan 的 good/bad example 策略也合理：good example 用 closed-set 公开枚举值（如 `field_missing`），bad examples 只用合成污染形态。这与 §Evidence policy 的「不保存真实模型输出」约束一致。

## 5. Tests / validation 是否足够覆盖

**足够。**

### Writer parser and prompt tests（Slice A）

Plan 列举的测试点：

| 测试点 | 覆盖 | 备注 |
|---|---|---|
| valid exact marker with allowed reason | 回归 | 确保 parser 仍接受合法 form |
| spacing pollution (`<!-- missing :field_missing -->`) | 污染形态 | `:` 前空格导致 regex 不匹配 |
| case pollution (`<!-- Missing:field_missing -->`) | 污染形态 | 大写导致 regex 不匹配 |
| fullwidth colon (`<!-- missing：field_missing -->`) | 污染形态 | 全角冒号不在 ASCII `:` 范围 |
| placeholder not replaced (`<!-- missing:{reason} -->`) | 污染形态 | `<reason>` literal 不匹配 `[a-z_]+` |
| unknown reason (`<!-- missing:unknown_reason -->`) | 回归 | `_parse_missing_markers()` 仍阻断 |
| prompt guidance includes exact marker block | 新增 | 验证 prompt 文本包含修复后 guidance |
| prompt no-code-fence rule | 新增 | 验证 prompt 禁止反引号/code fence |
| empty allowed reasons → no missing marker | 新增 | 验证 guidance 禁止输出 marker |

这些测试点覆盖了 `_MISSING_MARKER_RE` 的精确匹配规则和 `_invalid_marker_issues()` 的触发条件。现有 `test_chapter_writer.py` 已有 writer parse 相关测试框架，新增测试可复用。

### Orchestrator subcategory tests（Slice B）

| 测试点 | 覆盖 | 备注 |
|---|---|---|
| invalid marker → `failure_subcategory=invalid_marker` | 回归 | 验证 `_writer_prompt_contract_diagnostic()` 正确映射 |
| serialized diagnostics include `writer:invalid_missing_marker` prefix | 回归 | 验证 `issue_id_prefix_counts` 脱敏 |
| serialized diagnostics exclude raw prompt/draft/response | 安全 | 验证 `serialize_chapter_prompt_contract_diagnostics()` 不泄漏 |
| candidate facet assertion remains blocked | 安全 | 验证 `candidate_facet_assertion` 不被 marker repair 覆盖 |
| provider timeout → `llm_timeout` / no prompt-contract subcategory | 回归 | 确保 timeout 不被错误归为 prompt_contract |

经代码验证，`_writer_prompt_contract_diagnostic()` 中 `invalid_marker_count = sum(prefix_counts.get(prefix, 0) for prefix in _INVALID_MARKER_PREFIXES)` 包含 `"writer:invalid_missing_marker"` prefix，所以 subcategory 映射路径正确。测试覆盖该路径的回归是必要的。

### CLI scalar and secret safety tests（Slice C）

| 测试点 | 覆盖 | 备注 |
|---|---|---|
| failed `--use-llm` stderr includes `first_failed_subcategory` | 回归 | 验证 CLI 输出安全 scalar |
| stdout empty on failed `--use-llm` | 安全 | 验证不输出 partial report |
| stderr excludes secrets | 安全 | 验证不泄漏 Authorization/Bearer/prompt/draft |

Slice C 不引入新行为，只补 regression test。这与 controller judgment 的 CLI evidence 一致：失败时 stdout empty、stderr 只含 safe scalar。

### Validation matrix

Plan §Validation matrix 包含 8 项验证命令，覆盖 ruff、targeted pytest、full coverage、deterministic analyze/checklist、missing-config smoke、authorized real provider、real provider diagnostic serialization 和 secret scan。Real provider commands 明确标注为 controller/authorized validation steps only，不在 planning 或 unit-test workers 执行。

## 6. 是否不碰 golden/fixtures/score/quality gate/Host/Agent/dayu/PR 状态

**不碰。**

Plan §Non-goals / hard constraints 显式排除：

- 不修改 golden、fixtures、score、snapshot、quality gate、final judgment、manifest、promotion state。
- 不进入 Host/Agent/dayu。
- 不 push、不创建/更新 PR、不 merge、不 release、不 mark ready。

Plan §Allowed files / modules 列表只包含 writer、orchestrator、CLI、相关测试和 evidence artifacts，不包含任何 golden、fixture、score 或 Host/Agent/dayu 文件。

## Non-blocking observations

以下为非阻断观察，不影响 PASS 结论：

1. **`{reason}` 占位符语法**：Plan Contract Decision 2 使用 `{reason}` 作为占位符指示。实现时应注意 `{reason}` 在 Python f-string 中的转义；建议使用非花括号形式（如 `<REASON>`）或 raw string 来避免意外格式化。这不是 blocking issue，因为 implementation worker 可以选择任何等价占位符，只要 prompt guidance 语义不变。

2. **`MISSING_MARKER_EXACT_FORM` 标题稳定性**：Plan 建议 prompt 包含 `MISSING_MARKER_EXACT_FORM` 或等价稳定标题。若 implementation 选择不同标题（如中文标题），只要测试断言 prompt 包含该标题即可。标题选择属于实现细节，不影响 contract。

3. **allowed reasons token list 格式**：Plan 建议从 JSON payload 改为稳定 token list。实现时应确保 token list 的格式化方式不会引入模型混淆（如避免 JSON 数组格式 `["field_missing"]`，改用逗号分隔 `field_missing, field_missing2`）。这是实现细节。

4. **空 allowed reasons 边界**：Plan Contract Decision 3 要求「如果 `chapter.missing_reasons` 为空，prompt 必须说明不得输出 missing marker」。这是一个好的约束，测试 plan 也覆盖了此场景。实现时应验证当前测试 fixture 是否有 `missing_reasons` 为空的章节。

5. **测试断言粒度**：Plan §Expected assertions 对 Slice A 的 prompt guidance 断言使用了「prompt 包含」语义。实现时应注意不要过度约束 prompt 的精确文本（如使用 `assert "KEY_PHRASE" in prompt.user_prompt` 而非 `assert prompt.user_prompt == exact_text`），以便后续小调整不需要改测试。

---

**审查完毕。结论：PASS。无 blocking findings。**

📢 Plan review 完成，结论 PASS 无阻断问题，修复方向最小且安全边界完整保持。
