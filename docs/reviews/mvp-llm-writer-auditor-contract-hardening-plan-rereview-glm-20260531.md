# MVP LLM writer/auditor contract hardening plan re-review (GLM)

日期：2026-05-31
角色：Gateflow plan re-review specialist (GLM)
Re-review target：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md`
Original review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-review-glm-20260531.md`
MiMo review：`docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-review-mimo-20260531.md`

## Conclusion: PASS

All controller-accepted findings have been fixed in the plan. No remaining unfixed findings. Gate scope correctly limited to contract hardening only; score-loop and acceptance gate work properly excluded.

## Finding status map

| Finding ID | Severity | Original description | Fix location in plan | Verified status |
|---|---|---|---|---|
| MiMo F-001 | blocking | auditor `_audit_contract_markers` aligned with `<!-- required_output:<item> -->` writer protocol | §8.3 line 243-244: "每个 `contract.required_output_items` 必须检查 `<!-- required_output:<exact item> -->`，不得只检查裸 item text"；§9 Slice B lines 411-414: "把 contract required output 审计从裸 item text 改为检查 exact marker"；fix log line 110 | **FIXED** |
| MiMo F-002 | blocking | auditor test helper `_valid_markdown()` update scope included | §9 Slice B tests line 433-434: "更新 `_valid_markdown()` helper：合法章节必须包含每个 `contract.required_output_items` 对应的 `<!-- required_output:<item> -->` marker"；fix log line 112 | **FIXED** |
| MiMo F-003 / GLM N-4 | non-blocking | facet dedup strategy committed to first blocking occurrence per unique facet text | §9 Slice B line 430: "MVP 去重策略固定为 first blocking occurrence per unique facet text"；§12 line 667: "按 first blocking occurrence per unique facet text 去重"；test line 440: `test_non_asserted_facet_reports_first_blocking_occurrence_per_unique_facet`；fix log line 112 | **FIXED** |
| MiMo F-005 / GLM N-3 | non-blocking | explicit Service mapping table for new writer stop reasons, preserving diagnostic category | §8.2 lines 210-219: five-row mapping table, each writer stop reason maps to distinct Service `ChapterRunStopReason`；§9 Slice A lines 360-368: duplicate mapping table with "保留诊断 category" note；§8.2 line 220: "只有现有泛化 marker 格式非法…仍可映射到 `llm_contract_violation`"；fix log line 113 | **FIXED** |
| GLM N-2 | non-blocking | deterministic synthesis of `required_corrections` specified, with sanitized fallback | §8.4 lines 277-283: six-row deterministic mapping (P1→结构段落, C2→required output marker, C2→candidate facet, E1→anchor, llm:parse_failure→行协议, unknown→sanitized fallback)；§9 Slice C line 486: `_required_corrections_from_issues()`；tests lines 503-504: deterministic pattern test + sanitize fallback test；fix log line 116 | **FIXED** |
| GLM N-1 | non-blocking | incomplete/content_filter naming mismatch fixed | §9 Slice A line 343: `INCOMPLETE_FINISH_REASONS` (not `TRUNCATED_FINISH_REASONS`)；§8.2 line 198: `response_incomplete` (not `response_truncated`)；§8.2 line 206: "输出不完整或内容被过滤…`response_incomplete`"；fix log line 115 | **FIXED** |
| MiMo F-004 | non-blocking | real provider smoke command labeled explicitly | §11 line 613: "Real provider smoke command (label: `real-provider-smoke-006597-2024`)"；fix log line 114 | **FIXED** |

## User steering verification

| Steering requirement | Plan compliance | Evidence |
|---|---|---|
| Current gate = contract hardening only | PASS | §3 lines 33-38: current gate scope limited to writer prompt/protocol, parser failure category, auditor line protocol, repair context, timeout classification |
| Next gate = real provider smoke acceptance, not pulled in | PASS | §3 lines 39-42: acceptance 裁决属于下一 gate；§9 Slice D boundary lines 636-637: "是否将 006597/2024 作为 acceptance pass 由下一 gate 裁决" |
| Later gate = score improvement loop, not pulled in | PASS | §4 line 70: explicit non-goal "不实现 score schema、score history、自动 pro-codex repair task generation、pass-rate/evidence-compliance-rate dashboard"；§3 lines 43-46: "当前 gate 只输出可分类 failure reasons；不得实现 score loop" |

## Verification details per finding

### MiMo F-001 verification

Plan now has three layers of alignment between writer protocol and auditor:

1. **Contract specification** (§8.3): explicit mandate that `_audit_contract_markers()` must check `<!-- required_output:<item> -->` exact marker, not bare text.
2. **Slice B exact changes** (§9 Slice B): concrete instruction to change auditor from bare-item-text check to exact-marker check, with fail-closed semantics when marker missing but text present.
3. **Test coverage** (§9 Slice B tests): `test_programmatic_audit_requires_required_output_marker_not_bare_item_text()` explicitly tests the defense-in-depth case where bare text is present but marker is absent.

The alignment gap is closed at specification, implementation, and test levels.

### MiMo F-002 verification

Plan now explicitly lists auditor test helper update in Slice B tests:

- Line 433-434: "更新 `tests/fund/test_chapter_auditor.py` 的 `_valid_markdown()` helper：合法章节必须包含每个 `contract.required_output_items` 对应的 `<!-- required_output:<item> -->` marker，避免测试 helper 与 writer protocol 脱节。"

This resolves the scope gap where the original plan only mentioned writer test helper but not auditor test helper.

### MiMo F-003 / GLM N-4 verification

Plan commits to a single dedup strategy with three reinforcing locations:

1. **Slice B exact changes** (line 430): "first blocking occurrence per unique facet text" with explicit semantics — one issue per unique facet, asserted occurrence still blocking regardless of position.
2. **Calibration guardrails** (§12, line 667): reiterates first-occurrence strategy as allowed calibration.
3. **Test** (line 440): `test_non_asserted_facet_reports_first_blocking_occurrence_per_unique_facet` validates exact dedup behavior.

No ambiguity remains between window-based, first-occurrence, or post-hoc dedup.

### MiMo F-005 / GLM N-3 verification

Plan now provides two complete mapping tables (§8.2 and §9 Slice A) that map each new writer stop reason to a distinct Service `ChapterRunStopReason`, preserving diagnostic category:

- `missing_required_structure` → `missing_required_structure` (not `llm_contract_violation`)
- `missing_required_output_marker` → `missing_required_output_marker`
- `unknown_anchor` → `unknown_anchor`
- `response_too_long` → `response_too_long`
- `response_incomplete` → `response_incomplete`

Only legacy generic violations (marker format, unknown missing reason, forbidden phrases) still map to `llm_contract_violation`. This preserves the diagnostic chain from writer parser through orchestrator to CLI output, which was the core concern of the finding.

### GLM N-2 verification

Plan now specifies `required_corrections` synthesis with six concrete deterministic mapping entries (§8.4 lines 277-283):

- P1 structural headings → fixed correction template
- C2 required output → marker补齐 template
- C2 candidate facet → rewrite template with forbidden assertion verbs
- E1 anchor → anchor correction template
- `llm:parse_failure` → line protocol repair template
- Unknown rules → sanitized issue message fallback with explicit sanitization constraints (no raw response, no draft, no keys/headers/prompts, length limit)

Test coverage includes both deterministic patterns (line 503) and sanitize fallback (line 504).

### GLM N-1 verification

Naming has been corrected throughout:

- Constant renamed from `TRUNCATED_FINISH_REASONS` to `INCOMPLETE_FINISH_REASONS` (§9 Slice A line 343)
- Stop reason renamed from `response_truncated` to `response_incomplete` (§8.2 line 198)
- Description updated: "输出不完整或内容被过滤" (line 206) correctly describes both truncation and content_filter cases
- All mapping tables use `response_incomplete` consistently

The semantic mismatch where `content_filter` was labeled as "truncated" is resolved.

### MiMo F-004 verification

Real provider smoke command is now explicitly labeled in the validation matrix (§11 line 613):

> Real provider smoke command (label: `real-provider-smoke-006597-2024`)

This removes the risk of implementation agents skipping the command when following the validation matrix.

## Self-check

| Check | Result |
|---|---|
| Only read allowed truth/evidence | Yes — plan artifact, original GLM review, MiMo review |
| No code modification | Yes |
| No plan modification | Yes |
| No commit/push/PR/merge | Yes |
| No controller actions | Yes |
| Findings use gateflow format | Yes |
| Artifact path correct | Yes |
| All accepted findings verified | Yes — 7/7 fixed |
| Gate scope not expanded | Yes — contract hardening only, no score-loop, no acceptance pull-in |
