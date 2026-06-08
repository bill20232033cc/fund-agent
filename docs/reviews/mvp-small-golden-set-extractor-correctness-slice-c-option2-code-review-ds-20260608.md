# Code Review

## Scope

- Mode: current changes (Option 2 parser/fixture mechanics mini-slice, role-scoped independent review only)
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: accepted Slice C reconciliation plan checkpoint `2371ad1`
- Output file: `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option2-code-review-ds-20260608.md`
- Included scope:
  - `tests/fund/test_small_golden_set_parser_mechanics.py`
  - `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-option2-implementation-evidence-20260608.md`
- Excluded scope:
  - All production code, extractors, provider/runtime/config, repository/PDF/source/fallback, golden/readiness/quality gate, score-loop, Agent runtime, multi-year runtime
  - Slice A/B/C Option 1 accepted artifacts (reviewed in prior gates)
  - Unrelated untracked workspace files (not part of this mini-slice)
- Parallel review coverage: 无

## Findings

### 1-未修复-低-`_derive_parser_status` 第三分支与最终返回在当前 fixture 数据下不可达

- **入口/函数**: `_derive_parser_status`
- **文件(行号)**: `tests/fund/test_small_golden_set_parser_mechanics.py:246-248`
- **输入场景**: 所有当前 fixture 的 `source_identity.status` 均为 `unmatched_synthetic`，`exact_numeric_correctness_allowed` 均为 `false`。
- **实际分支**: 对于 fixture_status 不在 `{"unavailable", "not_applicable", "deferred_policy"}` 中的字段，第 244 行 `if expected_fields["source_identity"]["status"] != "matched"` 始终为 True，第 245 行 `return "unavailable", "unsupported_unmatched_synthetic_fixture"` 始终执行。第 246–248 行不会被任何当前 fixture 数据触发。
- **预期行为**: 当前行为正确——Option 2 必须对所有字段输出显式降级状态。不可达分支是防御性的 fail-closed 代码，设计意图合理。
- **实际行为**: 两个防御分支（`unsupported_exact_numeric_correctness_disabled` 和 `unsupported_option2_no_correctness_claim`）在当前 fixture 下无法被任何测试覆盖，也无法通过本地确定性命令验证其行为。
- **直接证据**: 所有五行 fixture 的 `expected_fields.json` 均设置 `"source_identity": {"status": "unmatched_synthetic", ...}` 和 `"exact_numeric_correctness_allowed": false`。第 244 行条件对除 `unavailable`/`not_applicable`/`deferred_policy` 外的字段始终成立。
- **影响**: 仅测试覆盖缺口。不影响 Option 2 的正确性或 fail-closed 语义。若未来出现 `status=matched` 且 `exact_numeric_correctness_allowed=true` 的行，第 248 行的 `unsupported_option2_no_correctness_claim` 会正确降级，但该行为未经测试验证。
- **建议改法和验证点**: 当前无需修改代码。若后续 Slice 引入 matched 行，应在对应的 parser mechanics 测试中增加对 `unsupported_exact_numeric_correctness_disabled` 和 `unsupported_option2_no_correctness_claim` 推理路径的覆盖。
- **修复风险（低）**: 无需修复。防御分支本身 fail-closed，不会导致错误接受。
- **严重程度（低）**:

### 2-未修复-低-`not_applicable` 状态在 fixture 数据和测试中均未出现，但枚举已声明

- **入口/函数**: `_derive_parser_status` / `test_parser_mechanics_degrades_unsupported_fields_explicitly`
- **文件(行号)**: `tests/fund/test_small_golden_set_parser_mechanics.py:91` (常量声明), `:242` (分支), `:381-393` (测试)
- **输入场景**: 当前没有任何 field group 的 fixture_status 为 `not_applicable`。
- **实际分支**: `EXPLICIT_DEGRADED_STATUSES` 包含 `not_applicable`，`_derive_parser_status` 第 242 行对其有处理分支，但 `test_parser_mechanics_degrades_unsupported_fields_explicitly` 中 `if/elif/else` 只覆盖 `deferred_policy`、`unavailable` 和 `else`（对应 `expected`），未覆盖 `not_applicable`。
- **预期行为**: 若未来出现 `fixture_status=not_applicable` 的字段，helper 应返回 `("not_applicable", "fixture_status_not_applicable")`。
- **实际行为**: helper 代码路径正确（第 242–243 行会命中），但缺少对应的测试断言。当前不造成错误。
- **直接证据**: 五行 fixture 的 `field_groups` 中无任何 `status: "not_applicable"`；测试 Line 381–393 的 if/elif/else 结构未包含 `not_applicable` 的独立断言。
- **影响**: 测试覆盖缺口。不影响当前行为，不会导致静默成功或错误接受。
- **建议改法和验证点**: 若后续 manifest 或 fixture 引入 `not_applicable` 状态，应在 parser mechanics 测试中增加对应断言。当前无需修改。
- **修复风险（低）**: 无。
- **严重程度（低）**:

## Open Questions

无。

## Residual Risk

- **不可达分支未测试**: `_derive_parser_status` 第 246–248 行在当前 fixture 数据下不可达，对应的 reason 字符串（`unsupported_exact_numeric_correctness_disabled`、`unsupported_option2_no_correctness_claim`）行为未经测试验证。由于所有五行均为 synthetic/unmatched，这在 Option 2 范围内是预期行为，但若未来 matched 行被引入而这些分支行为不正确，parser mechanics 测试不会捕获。
- **`not_applicable` 状态路径未测试**: 枚举已声明，helper 有处理分支，但无 fixture 使用该状态，测试也未覆盖。
- **Scope 合规性**: Option 2 允许的文件列表中包含 `tests/README.md`（若测试命令或 fixture 语义变更），但本次未修改该文件。当前新增测试的命令与现有 Slice A/B/Option 1 测试命令一致，不影响 `tests/README.md` 的现有内容。不构成合规问题。
- **Exact/numeric extractor correctness 仍阻塞**: 所有五行保持 synthetic/unmatched，Option 2 不改变这一事实。这是 accepted residual，不是 Option 2 引入的新风险。

## Verdict

PASS_WITH_NON_BLOCKING_FINDINGS
