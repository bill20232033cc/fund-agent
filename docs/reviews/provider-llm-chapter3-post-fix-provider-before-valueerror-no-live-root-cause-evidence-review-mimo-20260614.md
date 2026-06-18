# Code Review

## Scope

- Mode: role-scoped root-cause evidence review
- Gate: `Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence Gate`
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: N/A (artifact review, not diff review)
- Output file: `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-review-mimo-20260614.md`
- Included scope: evidence artifact `docs/reviews/provider-llm-chapter3-post-fix-provider-before-valueerror-no-live-root-cause-evidence-20260614.md`, code paths `chapter_writer.py`, `runner.py`, `evidence_availability.py`, controller judgment, test fixtures
- Excluded scope: live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR commands; code changes; control/design doc updates
- Parallel review coverage: 无

## Findings

### 001-未修复-[低]-evidence artifact 根因措辞精确度

- **入口/函数**: `_required_output_action()` (`fund_agent/fund/chapter_writer.py:1014-1015`)
- **文件(行号)**: evidence artifact "Root-cause Classification" 段落
- **输入场景**: `ch3.required_output.item_01` 的 availability 为 `status="missing"` 且 `item.when_evidence_missing=None`
- **实际分支**: `_required_output_action()` 在 `status != "available" and status is not None` 分支命中，`behavior is None` 触发 `raise ValueError`
- **预期行为**: evidence artifact 根因描述应精确到触发状态为 `missing`（或更广义的 `_MISSING_EVIDENCE_STATUSES`），而非泛称 "non-available"
- **实际行为**: artifact 写 "`ch3.required_output.item_01` can be present in `EvidenceAvailability` with a non-available status"；reproducer B 输出明确显示 `status=missing`。"non-available" 在代码中不是单一状态，`AvailabilityStatus` 有 `missing`、`unavailable`、`not_applicable`、`unreviewed` 四种非 available 状态，均可触发同一 ValueError
- **直接证据**: reproducer B 输出 `req ch3.required_output.item_01 missing fact (...)`；`_required_output_action` 行 1014 `if behavior is None: raise ValueError(...)` 对所有 `_MISSING_EVIDENCE_STATUSES` 统一触发
- **影响**: 不影响根因证明正确性；措辞不够精确可能误导修复范围理解
- **建议改法和验证点**: 根因描述改为 "`ch3.required_output.item_01` can have status in `_MISSING_EVIDENCE_STATUSES` (missing/unavailable/not_applicable/unreviewed) while typed `when_evidence_missing` is None"
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Root-cause Verification

逐环节验证 evidence artifact 声称的根因链路：

| 环节 | 声称 | 代码证据 | 判定 |
| --- | --- | --- | --- |
| 1. `run_agent_body_chapters()` 派生 typed `EvidenceAvailability` | typed 路径调用 `derive_evidence_availability()` | `runner.py:656-657` | VERIFIED |
| 2. `_writer_input()` 成功 | reproducer B 输出 `writer_input_ok ChapterWriterInput` | reproducer B output | VERIFIED |
| 3. `write_chapter()` 在 provider 前构建 required-output plan | `write_chapter()` 行 759 调用 `build_chapter_prompt()` → `_required_output_evidence_plan()`；provider 调用在行 773 | `chapter_writer.py:759,773` | VERIFIED |
| 4. `_required_output_plan_item()` 读取 item_01 availability | 行 952 调用 `_availability_for_required_output()` → `evidence_availability.require()` | `chapter_writer.py:952,988-989` | VERIFIED |
| 5. item_01 status 为 `missing` | reproducer B 输出 `req ch3.required_output.item_01 missing fact ('structured.basic_identity', 'structured.portfolio_managers')` | reproducer B output | VERIFIED |
| 6. `when_evidence_missing=None` | reproducer B 触发 `ValueError typed required output 缺证但未声明 when_evidence_missing：ch3.required_output.item_01`；`_required_output_action` 行 1014 `behavior is None` 分支 | `chapter_writer.py:1014-1015`, reproducer B output | VERIFIED |
| 7. `_required_output_action()` raise ValueError | 行 1015 `raise ValueError(f"typed required output 缺证但未声明 when_evidence_missing：{item.item_id}")` | `chapter_writer.py:1015` | VERIFIED |
| 8. Agent runner 映射为 `blocked_internal_code_bug` / `llm_exception` / `code_bug` | `_terminal_from_exception` → `blocked_internal_code_bug` (行 1414)；`_stop_reason_from_exception` → `llm_exception` (行 1439)；`_failure_category_from_exception` → `code_bug` (行 1481) | `runner.py:1414,1439,1481`, reproducer C output | VERIFIED |
| 9. zero writer/provider calls | reproducer B: `writer_requests 0`；reproducer C: `writer_requests 0`, `attempts 0` | reproducer B, C output | VERIFIED |

## Hypotheses Disposition Verification

| Hypothesis | Artifact disposition | Verification |
| --- | --- | --- |
| `_writer_input()` construction is the remaining failure source | REJECT | VERIFIED. Reproducer B prints `writer_input_ok`; failure is in `write_chapter()` |
| Fund writer prompt/preflight required-output plan raises before provider | ACCEPT | VERIFIED. `build_chapter_prompt()` → `_required_output_evidence_plan()` → `_required_output_action()` raises before `llm_client.generate_chapter()` |
| Provider availability or provider response causes Chapter 3 failure | REJECT | VERIFIED. Live and no-live both have provider request count 0 |
| Prior missing-availability mapping patch should have covered this branch | REJECT | VERIFIED. Prior patch (commit `2bced82`) handles `_availability_for_required_output()` returning `None` with declared `when_evidence_missing`; this branch has non-None requirement with null behavior |
| Service/Agent serialization alone causes the failure | REJECT | VERIFIED. Fund writer raises before Agent mapping |

## Live Shape Match Verification

| Live metadata field | Live value | No-live reproducer C value | Match |
| --- | --- | --- | --- |
| first failed chapter | 3 | task_chapter_id=3 | YES |
| status | failed | task_status=failed | YES |
| stop_reason | llm_exception | stop_reason=llm_exception | YES |
| failure_category | code_bug | failure_category=code_bug | YES |
| terminal_issue_class | ValueError | blocked_reasons contains `ValueError` | YES |
| provider attempt count | 0 | writer_requests=0, attempts=0 | YES |
| runtime operation | writer | writer operation (before provider) | YES |

## Adversarial Failure Pass

- **Could the reproducer be unfaithful to live state?** The reproducer uses `missing_portfolio_managers = ExtractedField(value=None, anchors=(), extraction_mode='missing')` which produces `status="missing"` for `ch3.required_output.item_01`. The live failure metadata does not expose field-level state, but the reproducer output shape (ValueError message, zero provider calls, Agent mapping) exactly matches the live diagnostic shape. The controller judgment confirms the live run has `provider attempt count=0` and `terminal_issue_class=ValueError`.
- **Could there be a different ValueError in the same path?** `_required_output_action()` has exactly one `raise ValueError` (line 1015). The error message `typed required output 缺证但未声明 when_evidence_missing：ch3.required_output.item_01` is unique in the codebase. No other ValueError in `write_chapter()` or `build_chapter_prompt()` can produce the same zero-provider-call shape.
- **Could `_writer_input()` also raise?** Reproducer B proves it does not for the missing-portfolio-managers case. The `_writer_input()` → `build_chapter_writer_input()` path does not call `_required_output_evidence_plan()`.

## Open Questions

- 无。根因链路已被 no-live reproducer 完整证明。

## Residual Risk

| Residual | Impact |
| --- | --- |
| 实际 live projection 中 `basic_identity` 和 `portfolio_managers` 的确切 fact 状态未在安全 runtime artifact 中暴露 | 不影响根因证明；reproduced shape 与 live diagnostic shape 完全匹配 |
| `_MISSING_EVIDENCE_STATUSES` 中其他状态（`unavailable`、`not_applicable`、`unreviewed`）也可能触发同一 ValueError | 修复应覆盖所有 `_MISSING_EVIDENCE_STATUSES`，而非仅 `missing` |
| typed template 中其他 required output item（如 item_02、item_06）是否有类似 null `when_evidence_missing` 风险 | 需在修复 gate 确认；当前 evidence 只证明 item_01 触发 |

## Verdict

**PASS**

Root cause is proven. The no-live reproducer faithfully reproduces the live failure shape:

1. `ch3.required_output.item_01` can have `status in _MISSING_EVIDENCE_STATUSES` when `item.when_evidence_missing=None`
2. `_required_output_action()` raises `ValueError` before provider invocation
3. Agent runner maps it to `blocked_internal_code_bug` / `llm_exception` / `code_bug` with zero writer/provider calls
4. All live metadata fields match: chapter 3, failed, llm_exception, code_bug, ValueError, provider attempt 0

The evidence artifact is sound with one low-severity wording imprecision (finding 001).
