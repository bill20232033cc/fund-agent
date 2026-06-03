# Code Review

## Scope

- Mode: current changes
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Base: `main`
- Output file: `docs/reviews/mvp-typed-template-contract-slice4-ch3-evidence-conditional-must-not-cover-code-review-mimo-20260603.md`
- Included scope: `fund_agent/fund/chapter_auditor.py`, `fund_agent/fund/template/typed_contracts.py`, `fund_agent/fund/audit/contract_rules.py`, `tests/fund/test_chapter_auditor.py`, `tests/fund/audit/test_audit_programmatic.py`, `fund_agent/fund/README.md`, `tests/README.md`
- Excluded scope: provider/runtime/default/budget/endpoint, Service/Host/CLI changes, Agent runtime/tool-loop, score/golden/readiness/promotion, deterministic analyze/checklist behavior, direct document/PDF/cache/source-helper access, `extra_payload` business params
- Parallel review coverage: 无

## Findings

未发现实质性问题。

## Review Detail By Focus Area

### 1. Typed MustNotCoverClause + EvidenceAvailability integration is Ch3-first and additive

- `_TYPED_MUST_NOT_COVER_CLAUSE_IDS` only contains `ch3.must_not_cover.item_04` (line 138-140). Ch3-first confirmed.
- `_audit_typed_must_not_cover()` only processes clauses whose `clause_id` is in `_TYPED_MUST_NOT_COVER_CLAUSE_IDS` (line 690). Other clauses untouched.
- `_typed_must_not_cover_clause_texts()` returns the exact text of typed clauses; old global phrase extraction skips these texts (line 655-659).
- `contract_rules.py` reclassifies Ch3 style clause from `narrative_guidance` to `typed_programmatic_evidence_conditional` (line 280-283). `_MUST_NOT_COVER_COVERAGE_KINDS` updated to include the new kind (line 40-42). Validation still enforces no overlap with `_FORBIDDEN_CONTENT_RULES`.
- `_FORBIDDEN_CONTENT_RULES` continues to handle explicit always-forbidden markers (personality/motivation/trading-advice). No overlap with the Ch3 style clause.

### 2. ch3.must_not_cover.item_04 applies from availability predicate and blocks positive/quasi-positive claims

- `_CH3_STYLE_EVIDENCE_UNREVIEWED` predicate in `typed_contracts.py` (line 573-580) references `ch3.requirement.actual_behavior_reviewed` with `required_statuses=("missing", "unavailable", "unreviewed")`. This is the consolidated single-requirement predicate derived from the prior two-requirement version.
- `_typed_must_not_cover_applies()` iterates requirement_ids; for each, if the requirement is `None` (unknown) or its status is in `required_statuses`, returns `True` (fail-closed for unknown).
- `_audit_ch3_style_must_not_cover_clause()` scans line-by-line, sentence-by-sentence, and checks for claim phrases from `_CH3_STYLE_CLAIM_PHRASES` which includes both positive (`言行一致`, `风格稳定`, `风格一致`, `风格保持稳定`, `投资框架稳定`, `说的和做的一样`) and quasi-positive (`基本一致`, `大体一致`, `较为一致`, `倾向一致`, `未见明显不一致`, `没有明显不一致`, `没有明显漂移`, `未见明显漂移`, `变化不大`, `基本稳定`, `相对稳定`, `延续原有风格`).
- Positive claim `"言行一致性判断：言行一致。"` triggers C2 with stable `programmatic:C2:ch3.must_not_cover.item_04` issue id.
- Quasi-positive claim `"风格稳定性判断：未见明显不一致，整体变化不大。"` triggers C2.
- Both test-verified.

### 3. Missing EvidenceAvailability does not create silent pass; unsafe positive/quasi-positive claims fail closed

- When `writer_input.evidence_availability is None`, `_audit_typed_must_not_cover()` calls `_audit_ch3_style_must_not_cover_clause(input_data, clause, allow_contexts=False)` (line 692-693).
- With `allow_contexts=False`, the `_ch3_style_claim_allowed` check is short-circuited: `phrase is None or (False and ...)` evaluates to `phrase is None`, so any non-None phrase passes through and triggers the issue. Required-label, gap-statement, quote, and anchor-caption exceptions are not available.
- Test `test_ch3_positive_consistency_claim_blocks_without_evidence_availability` verifies this with `include_evidence_availability=False`.

### 4. Required_label and evidence_gap_statement allowed contexts are narrow

**Required label** (`_is_required_label_context`):
- Prefix must be in `_CH3_REQUIRED_LABELS` = `("言行一致性判断", "风格稳定性判断", "一致性汇总边界")`.
- Colon must exist and be at index > 0.
- Suffix after colon must be empty or pass `_is_evidence_gap_statement_context` or `_is_non_assertive_label_suffix`.
- `_is_non_assertive_label_suffix` rejects any suffix containing claim phrases from `_CH3_STYLE_CLAIM_PHRASES`.
- `言行一致性判断：言行一致。` correctly blocked: suffix contains `言行一致`.
- `言行一致性判断：证据不足，不能据此判断言行一致。` correctly allowed: suffix is gap-statement context.

**Evidence gap statement** (`_is_evidence_gap_statement_context`):
- Requires both a gap marker (`_EVIDENCE_GAP_MARKERS`) and a denial marker (`_EVIDENCE_GAP_DENIALS`).
- Checks after denial for reversal markers (`_GAP_REVERSAL_MARKERS` = `但/但是/不过/然而/总体/仍/依然`) followed by claim phrases.
- `证据不足，不能据此判断言行一致` allowed: no reversal between denial and claim.
- `证据不足，但未见明显不一致` blocked: `但` reversal followed by quasi-positive claim.

**Quote context** (`_is_quote_context`):
- Requires all claim phrases inside Chinese quotes (`""`) or backticks.
- Requires a quote introducer in current or previous line (`_QUOTE_INTRODUCERS`).
- Suffix after last quote must not contain author conclusion markers (`_AUTHOR_CONCLUSION_MARKERS`) or claim phrases.
- Quote context cannot launder author conclusions.

**Anchor caption**: `_line_is_contract_or_anchor_metadata` skips lines starting with `<!-- required_output:`, `> 📎 证据：`, `>📎 证据：`, or `<!-- anchor:`. These are treated as metadata, not author conclusions.

### 5. Old global phrase extraction no longer duplicates typed Ch3 style clause

- `_audit_must_not_cover()` first calls `_audit_typed_must_not_cover()` (line 654), then computes `typed_clause_texts` (line 655), and skips those texts in the old loop (line 657-659).
- Only clauses whose text matches a typed clause text are skipped. Other `must_not_cover` clauses (Ch0/1/2/3 non-style/4/5/6/7) continue through the old phrase extraction path.
- `_FORBIDDEN_CONTENT_RULES` (personality/motivation/etc.) remain enforced through `_audit_forbidden_content()`, which is a separate path from `_audit_must_not_cover()`.
- Validation in `contract_rules.py` prevents any `must_not_cover` item from being both in `_FORBIDDEN_CONTENT_RULES` and `_MUST_NOT_COVER_COVERAGE_RULES`.

### 6. audit_focus remains semantic-only and cannot disable programmatic blockers

- `audit_chapter_programmatic()` does not reference `input_data.writer_input.chapter.audit_focus` or any focus-related field. Programmatic blockers fire unconditionally.
- `audit_focus` only appears in `_llm_request()` (line 1419) as `DEFAULT_AUDIT_FOCUS` passed to the LLM audit request.
- Test `test_audit_focus_cannot_disable_programmatic_must_not_cover` verifies that C2 fires regardless of focus.

### 7. contract_rules coverage route is consistent with typed programmatic enforcement

- Ch3 style clause coverage changed from `narrative_guidance` to `typed_programmatic_evidence_conditional` in `_MUST_NOT_COVER_COVERAGE_RULES` (line 280-283).
- `_MUST_NOT_COVER_COVERAGE_KINDS` now includes `typed_programmatic_evidence_conditional` (line 40-42).
- Validation still prevents overlap with `_FORBIDDEN_CONTENT_RULES` (line 711-714).
- No clause is simultaneously narrative-only and typed-programmatic in a contradictory way.
- Test `test_contract_audit_coverage_manifest_covers_every_must_not_cover` updated to assert `typed_programmatic_evidence_conditional` for the Ch3 style clause.

### 8. No prohibited dependencies or scope creep

- No provider/runtime/default/live probe, Agent runtime/tool-loop, Service/Host/CLI, score/golden/readiness, deterministic analyze/checklist, direct document/PDF/cache/source-helper access, or `extra_payload` business params.
- All new code is Fund-layer only: `chapter_auditor.py` and `typed_contracts.py` changes.
- `_typed_chapter_contract_for()` calls `get_typed_chapter_contract()` which loads the typed manifest (pure computation, no I/O).
- `EvidenceAvailability` and `RequirementAvailability` are pure data classes; `derive_evidence_availability` is same-source derivation from `ChapterFactProjection`.

### 9. Tests and README/evidence are sufficient and not overclaiming

- 7 new tests in `test_chapter_auditor.py`: required label allowed, gap statement allowed, positive claim blocks (with and without availability), quasi-positive claim blocks, audit_focus cannot disable.
- 1 new test in `test_audit_programmatic.py`: typed issue id uses clause_id, not phrase hash.
- Updated coverage manifest assertion for Ch3 style clause `typed_programmatic_evidence_conditional`.
- README accurately describes Ch3 typed evidence-conditional `must_not_cover` behavior including fail-closed semantics when `EvidenceAvailability` is absent.
- tests/README updated to reflect Ch3 typed must-not-cover test coverage.
- Evidence artifact (`mvp-typed-template-contract-slice4-ch3-evidence-conditional-must-not-cover-implementation-evidence-20260603.md`) is accurate and lists all touched files, tests, validations, and residuals.

## Validation Results

| Command | Result |
|---|---|
| `uv run pytest tests/fund/test_chapter_auditor.py tests/fund/audit/test_audit_programmatic.py` | 86 passed in 0.50s |
| `uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py` | 16 passed in 0.45s |
| `uv run ruff check fund_agent/fund tests/fund` | All checks passed! |
| `git diff --check -- <touched files>` | exit 0 |

## Open Questions

- 无。

## Residual Risk

- `_is_non_assertive_label_suffix` 的短句白名单（`待复核`/`待验证`/`无结论`/`未判断`/`不判断`）是 Ch3 first-slice 的最小集，未来新增 required label 冒号后的安全非断言后缀时需要扩展。当前兜底逻辑（不含 claim phrase 即允许）覆盖了多数安全后缀。
- 引用上下文匹配使用中文引号 `""` 和反引号 `` ` `` 的 span 解析，覆盖 Slice 0 定义的窄场景；未来扩展到 Markdown blockquote 或嵌套引用时需要更新。
- 当前 Ch3 availability 仍为单年投影，跨期风格证据在 `evidence_availability.py` 中保持 `unreviewed`；多年证据仍为 future design-only scope。
- `_typed_chapter_contract_for()` 每次调用 `get_typed_chapter_contract()` 都会重新加载并校验 manifest。在当前单次审计调用场景下可接受；若未来进入批量审计循环，可考虑缓存。
