# MVP typed template contract Slice 6 Ch0/Ch7 readiness — Code Review (DS)

- **Role**: code review worker only, not controller, not implementation worker
- **Gate**: `MVP typed template contract Slice 6 Ch0 consumes Ch7 with fail-closed required-body readiness implementation gate`
- **Classification**: `heavy`
- **Branch**: `feat/mvp-llm-incomplete-run-artifacts`
- **Review target**: current diff for `final_chapter_assembler.py`, 4 test files, `tests/README.md`

## Sources Read

1. `AGENTS.md` — rule truth
2. `docs/current-startup-packet.md` — startup packet
3. `docs/implementation-control.md` — control truth
4. `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md` — Slice 6 section
5. `docs/reviews/mvp-typed-template-contract-slice6-ch0-ch7-readiness-implementation-evidence-20260603.md` — implementation evidence
6. Full current diff (all 5 changed files)
7. Full `final_chapter_assembler.py` (1259 lines)
8. Full `test_final_chapter_assembler.py` (831 lines)

## Validation

```bash
uv run pytest tests/services/test_final_chapter_assembler.py \
  tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -v
```
**Result**: 112 passed in 1.24s.

```bash
uv run ruff check fund_agent/services tests/services tests/ui
```
**Result**: All checks passed.

```bash
git diff --check
```
**Result**: PASS, no whitespace errors.

## Findings

### Finding 1 — INFORMATIONAL: user-facing report leaks implementation-ish readiness identifiers

**Severity**: informational (non-blocking)

Ch7 markdown rendering (`_render_chapter7_markdown`, line 819–820) embeds typed enum literal values directly into user-facing report text:

```
- **证据/readiness 状态**：accepted_body_chapters；ready；accepted_body_chapters=(1, 2, 3, 4, 5, 6)
```

The values `accepted_body_chapters`, `ready`, `blocked`, `incomplete_body_chapters` are internal `FinalAssemblyEvidenceStatus` / `FinalAssemblyReadinessStatus` enum literals, not Chinese descriptions. The `accepted_body_chapters=(1, 2, 3, 4, 5, 6)` is a raw Python tuple `repr`. The same issue exists in `_chapter7_accepted_conclusion` (line 874): `- **证据/readiness 状态**：{summary.evidence_status}；{summary.readiness_status}`.

The rest of the template outputs Chinese labels (`🟡 需要关注`, `产品画像`, etc.). Raw enum values and tuple reprs are inconsistent with the report's Chinese-first UX.

**Mitigation**: accepted reports only emit the positive arm (`accepted_body_chapters` / `ready`), which reads as acceptable English evidence-status labels. The tuple repr `(1, 2, 3, 4, 5, 6)` is the more visible wart. This is non-blocking because:
- The report is only produced in the accepted path (incomplete returns no markdown)
- The line is evidence-tracking metadata, not core analysis content
- `FinalAssemblyReadiness` docstring marks it as "internal to the current Service assembler" — user-facing rendering polish can be a follow-up gate

**Recommendation**: consider mapping evidence status to Chinese labels (`"正文章节已接受"` / `"正文章节未完整"`) and formatting `accepted_body_chapter_ids` as a natural list rather than a tuple repr in a future UI polish slice.

### Finding 2 — PASS: Ch7 cannot be produced as accepted when required body readiness is incomplete

Verified impossible through three independent guard layers:

1. **`_build_final_assembly_readiness()` → `_validate_orchestration()`**: any missing required chapter, non-accepted status, missing draft, or missing conclusion produces blocking issues. `readiness.status` becomes `"blocked"`.

2. **`_build_chapter7_summary()` guard** (line 615–616): returns `None` when `readiness.status != "ready" or not readiness.chapter7_ready`.

3. **`assemble_final_chapters()` early return** (line 290–291): `if issues: return _incomplete_result(...)` before Ch7 construction is attempted. And the explicit `None` check at lines 298–311 returns incomplete with `chapter7_missing` reason.

Test coverage: `test_missing_required_body_chapter_blocks_ch7_and_ch0` (missing Ch3), `test_incomplete_when_orchestration_not_accepted` (partial/blocked orchestration), `test_incomplete_when_required_chapter_lacks_accepted_conclusion`.

### Finding 3 — PASS: Ch0 cannot be complete when Ch7 is missing/unaccepted

Assembly flow enforces strict ordering:
1. Readiness issues? → incomplete (line 290)
2. Ch7 summary is `None`? → incomplete with `chapter7_missing` (line 298)
3. Ch7 summary validation fails? → incomplete with `chapter7_readiness_mismatch` (line 312)
4. Only after all three pass → Ch0 rendering (line 325)
5. After Ch0 rendering → `_validate_chapter0_action()` cross-check (line 332)

Ch0 rendering itself consumes `chapter7_summary.selected_judgment_label` (line 913), never independently derives action. Test coverage: `test_missing_ch7_blocks_ch0_complete_report` (monkeypatches `_build_chapter7_summary` to return `None`, verifies all outputs are `None`).

### Finding 4 — PASS: Ch0 action equals Ch7 action exactly, no independent derivation

`_render_chapter0_markdown()` uses `chapter7_summary.selected_judgment_label` directly for the `当前动作` line (line 913). No alternative label computation exists anywhere in Ch0 rendering.

`_validate_chapter0_action()` (lines 949–977) adds a defense-in-depth string check: the expected line `f"- **当前动作**：{chapter7_summary.selected_judgment_label}"` must appear verbatim in Ch0 markdown. If absent (e.g., if someone later modifies the renderer), a blocking `chapter0_contract_violation` issue fires. This is fail-closed — the validator can only add blocking issues, never suppress them.

Test: `test_ch0_action_must_equal_ch7_action` verifies the correct action appears and wrong actions (`🟢 值得持有`, `🔴 建议替换`) are absent.

### Finding 5 — PASS: Ch7 summary/bundle carries all required fields

`FinalChapter7Summary` (lines 180–208) includes:
- **action**: `selected_judgment_label` (三选一动作 with emoji)
- **primary reason / core basis**: `core_basis` (1–2 short sentences from decision reasons + body conclusion snippets)
- **largest risk / easiest misread**: `easiest_misread`
- **minimum verification question / next validation plan**: `next_validation_plan`
- **thresholds**: `threshold_events` (升级/降级阈值)
- **evidence/readiness status**: `readiness_status`, `evidence_status`, `accepted_body_chapter_ids`

All fields are rendered into Ch7 markdown (lines 793–822) and Ch7 accepted conclusion (lines 850–882). No field is silently dropped.

### Finding 6 — PASS: existing incomplete `--use-llm` behavior remains fail-closed

`_incomplete_result()` (lines 1226–1258) always sets `report_markdown=None`, `chapter0_markdown=None`, `chapter7_markdown=None`, `chapter7_summary=None`. The `allow_incomplete_debug_markdown` policy flag is the only escape hatch and defaults to `False`.

Service-level test `test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness` verifies: Ch6 blocked → orchestration partial → final assembly incomplete → `report_markdown is None`, `chapter7_markdown is None`, `chapter0_markdown is None`, and `result.report_markdown` raises `ValueError("LLM 分析报告尚未完成")`.

CLI-level test `test_use_llm_incomplete_typed_readiness_empty_stdout_exit_one` verifies: exit code 1, stdout empty, stderr contains `"LLM 分析未完成："`, no `"# 0. 投资要点概览"` in output.

### Finding 7 — PASS: no scope violations

Confirmed diff touches only `final_chapter_assembler.py`, 4 test files, and `tests/README.md`. No changes to:
- Provider/runtime/default/live probe
- Agent runtime/tool-loop
- Score-loop, golden/readiness promotion, quality gate semantics
- Template truth (`docs/fund-analysis-template-draft.md`)
- Deterministic `analyze/checklist` path
- `FundDocumentRepository`, PDF/cache/source helpers

Import boundary test (`test_final_assembler_imports_stay_above_fact_and_source_boundaries`) confirms no forbidden module imports.

### Finding 8 — PASS: test coverage sufficient

New tests added:
| Test | What it verifies |
|---|---|
| `test_ch0_action_must_equal_ch7_action` | Ch0 action label equals Ch7, wrong labels absent |
| `test_missing_required_body_chapter_blocks_ch7_and_ch0` | Missing Ch3 → Ch7/Ch0/Ch7_summary all None, `chapter7_readiness_blocked` fires |
| `test_missing_ch7_blocks_ch0_complete_report` | Monkeypatched Ch7 None → incomplete, `chapter7_missing` fires |
| `test_partial_llm_result_does_not_fallback_to_deterministic_after_typed_readiness` | Ch6 blocked → no deterministic fallback, `chapter7_readiness_blocked` in issues |
| `test_use_llm_incomplete_typed_readiness_empty_stdout_exit_one` | CLI exit 1, stdout empty, no report fragments |

Existing tests updated:
- `test_incomplete_when_orchestration_not_accepted` now also asserts `chapter7_readiness_blocked` alongside `orchestration_not_accepted`

Coverage hits: happy path (accepted), missing body chapter, missing Ch7, partial orchestration, blocked orchestration, missing conclusion, duplicate chapter, sparse/truncated sources, output capping, developer override, identity mismatch, invalid judgment, policy validation, import boundaries, and CLI integration.

### Finding 9 — PASS: `FinalAssemblyReadiness` makes required-body readiness explicit

`_build_final_assembly_readiness()` (lines 476–529):
- Iterates `policy.required_body_chapter_ids` (1–6)
- Each chapter must have `status == "accepted"`, non-None `accepted_draft`, non-None `accepted_conclusion`
- `accepted_body_chapter_ids` tuple contains only chapters meeting all three criteria
- `status` is `"ready"` iff `_validate_orchestration()` produces zero issues
- `chapter7_ready` is locked to `status == "ready"`
- `evidence_status` is `"accepted_body_chapters"` when ready, `"incomplete_body_chapters"` when blocked
- Missing required chapter produces explicit `chapter7_readiness_blocked` issue when not already present

The readiness object is consumed by `_build_chapter7_summary()` (guard) and `_validate_chapter7_summary()` (consistency check), creating a closed loop.

### Finding 10 — CONSIDERATION: `body_conclusions` filter is less strict than readiness filter

```python
# body_conclusions (line 282–287): only checks accepted_conclusion is not None
body_conclusions = tuple(
    conclusion
    for chapter_id in policy.required_body_chapter_ids
    if (result := chapter_map.get(chapter_id)) is not None
    and (conclusion := result.accepted_conclusion) is not None
)

# accepted_body_chapter_ids (line 495–501): checks status + draft + conclusion
accepted_body_chapter_ids = tuple(
    chapter_id for chapter_id in policy.required_body_chapter_ids
    if (result := chapter_map.get(chapter_id)) is not None
    and result.status == "accepted"
    and result.accepted_draft is not None
    and result.accepted_conclusion is not None
)
```

In practice this cannot produce a divergence because `_build_final_assembly_readiness()` runs first and blocks the entire assembly if any required chapter has issues. `body_conclusions` is only used downstream when readiness is `"ready"`, at which point both filters are equivalent. The looser filter is safe because the readiness guard fires first. No action required.

## Final Verdict: PASS

All blocking review points pass. One informational finding (Finding 1: implementation-ish readiness identifiers in user-facing report) is noted for future UI polish but does not block acceptance. The implementation correctly enforces:

- Ch7 readiness requires all body chapters 1–6 accepted with draft and conclusion
- Ch7 cannot be produced when readiness is incomplete
- Ch0 cannot be complete when Ch7 is missing
- Ch0 action equals Ch7 action exactly, with a defense-in-depth string validator
- Ch7 summary carries all required fields (action, basis, risk, verification, thresholds, readiness)
- Incomplete `--use-llm` stays fail-closed with empty stdout
- No scope violations (no provider/runtime/Agent/score/golden/template changes)
- 112 tests pass, ruff clean, import boundaries verified
