# Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence Review (AgentMiMo)

Date: 2026-06-14

Role: AgentMiMo independent evidence reviewer

Gate: `Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence Gate`

Review target: `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-20260614.md`

## 1. Review Discipline

Read truth/context files first: `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, the accepted disposition plan, the controller judgment, and the two prior reviews.

Read no-live code cited by the evidence artifact: `fund_agent/fund/chapter_writer.py`, `fund_agent/agent/runner.py`, `fund_agent/agent/repair.py`, `fund_agent/services/chapter_orchestrator.py` (diagnostic mapping section only).

Did not read: writer/auditor/repair markdown bodies, provider payloads, PDF/source/cache bodies, source bodies, final report body.

Did not run: live/provider/LLM/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands.

Cross-check contracts from `docs/design.md`, `docs/implementation-control.md` and `docs/current-startup-packet.md` applied.

## 2. Findings

### Finding 1 — Boundary preservation: PASS

The evidence artifact stayed within allowed no-live read/write boundaries. Commands were limited to `rg`, `sed`, `git status --branch --short`, focused `uv run pytest`, and fake-input `uv run python -c` snippets. No source/test/runtime/prompt/README/design/control files were modified. No body reads were performed. No live/provider/network/PDF/FDR/source/acquisition/analyze/checklist/golden/readiness/release/PR commands were run. EID remains single-source/no-fallback. Release/readiness remains `NOT_READY`.

### Finding 2 — D1 prompt rendering: PASS

Code verification confirms `chapter_writer.py` lines 698-701 render exact `<!-- anchor:<anchor_id> -->` syntax, state `required_anchor_ids` is an allowed set (not a required full-use list), and forbid synthesized anchor ids from `fact_id`/`source_field_id`/`source_field_name`/fact value. `_bond_risk_anchor_contract_prompt()` (line 1239-1242) adds Chapter 6 bond-risk internal/组级 anchor prohibition. Focused test `test_ch6_prompt_forbids_synthesized_bond_risk_anchor_ids` passed. Corrected snippet confirmed all D1 booleans `True` with `allowed_anchor_count=8`.

### Finding 3 — D2 validator taxonomy: PASS

Code verification confirms `_invalid_marker_issues()` (line 1660-1692) scans HTML comments via `_COMMENT_RE`, checks for `anchor` in payload, and emits `writer:invalid_anchor_marker:<offset>` with reason `llm_contract_violation` when `_ANCHOR_MARKER_RE.fullmatch()` fails. `_parse_anchor_markers()` (line 1848-1876) separately handles valid `<!-- anchor:<id> -->` markers and emits `_unknown_anchor_issue()` when id is not in the allowed set. The two paths are independent: malformed syntax goes to `invalid_marker`, syntactically-valid-but-unauthorized goes to `unknown_anchor`. Focused tests passed. Corrected snippet confirmed the distinction.

### Finding 4 — D3 diagnostic payload mapping: PASS

Code verification confirms `_writer_prompt_contract_diagnostic()` (line 1422) computes `invalid_marker_count` from `_INVALID_MARKER_PREFIXES` (line 162-163: `"writer:invalid_anchor_marker"`). `_writer_issue_id_prefix_counts()` (line 1616) strips writer issue ids to the first two components, removing raw offsets/ids/suffixes. Focused tests passed. Corrected snippet confirmed `failure_subcategory='invalid_marker'`, `invalid_marker_count=1`, prefix counts include `writer:invalid_anchor_marker`, and serialized diagnostics did not contain raw malformed strings.

### Finding 5 — D4 repair-context specificity: PASS (proven gap)

Code verification confirms the critical finding: `runner.py` line 374 returns immediately when `writer_result.status == "blocked"`, before any audit or repair context generation. `repair_context_from_audit()` is only called at line 580, after a draft reaches audit and `decision.action == "regenerate"`. This means for `invalid_marker` (which blocks at the writer stage), no repair attempt or repair context is ever generated. Corrected snippet confirmed `attempt_count=1`, `repair_decision=None`, `second_writer_request_exists=False`.

The existing repair context renderer (`_repair_context_prompt()`, line 1458-1481) is generic and does not contain exact `<!-- anchor:<anchor_id> -->` syntax instruction for invalid-marker recurrence. The existing audit correction mapping for anchor issues says only "只使用 allowed anchor marker，删除未知 anchor 或改用 allowed anchor", without exact marker syntax.

This is correctly classified as a proven gap: invalid_marker blocks before repair context exists, so no invalid-marker repair context exists today.

### Finding 6 — D5 boundary preservation: PASS

Confirmed as stated in Finding 1.

### Finding 7 — Recommendation classification: PASS

The recommendation to proceed to a narrow no-live fix planning gate is supported. The evidence proves:
- The prompt already contains exact marker syntax and Chapter 6 bond-risk prohibition (D1).
- The validator/parser correctly distinguishes malformed from unauthorized (D2).
- Diagnostics are safely mapped (D3).
- Repair context for invalid_marker does not exist today (D4).

Therefore the fix surface is narrow: either strengthen initial Chapter 6 writer prompt salience, add a writer-block repair/retry path for invalid_marker, or both. Direct implementation is not authorized from this evidence gate. Additional live evidence, parser relaxation, source/fallback work, readiness or PR are all correctly rejected.

### Finding 8 — Failed snippet representation: PASS

The failed snippet with `ModuleNotFoundError: No module named 'fund_agent.fund.chapter_fact_provider'` is documented honestly (Section 3, "First snippet attempt with wrong import path") with explicit evidence value: "none; corrected immediately using the actual module." The failed output is not used as proof; it is a process artifact only.

### Finding 9 — Non-blocking amendment: test count discrepancy

The artifact states "12 passed in 0.84s" for 7 named test functions. This is consistent if some tests are parameterized (e.g., `test_writer_rejects_invalid_anchor_marker_spacing_or_case` likely tests multiple invalid patterns). This is a documentation clarity issue, not an evidence integrity issue. Recommend noting the parameterized count or listing the 12 test IDs for completeness, but this does not block acceptance.

## 3. Review Questions

| Question | Verdict |
|---|---|
| 1. Did the evidence artifact stay within allowed no-live/read/write boundaries? | YES |
| 2. Are D1-D3 actually proven by current code/tests/snippet evidence? | YES |
| 3. Is D4 correctly classified as a proven gap? | YES — invalid_marker blocks before repair context; no invalid-marker repair context exists today |
| 4. Is the recommendation to proceed to a narrow no-live fix planning gate supported? | YES — not direct implementation, more evidence, live evidence, parser relaxation, source/fallback work, readiness or PR |
| 5. Are command results and the failed snippet represented honestly? | YES — failed snippet documented as process artifact with explicit "evidence value: none" |

## 4. Verdict

```text
ACCEPT
```

All five review questions pass. D1-D4 are proven by no-live code, tests and corrected snippets. D4 correctly identifies the gap that invalid_marker blocks before repair context. The recommendation to proceed to a narrow no-live fix planning gate is well-supported. Boundary preservation is confirmed. The failed snippet is represented honestly.

The non-blocking test-count discrepancy (12 passed for 7 named functions) does not affect evidence integrity and is noted for completeness only.

## 5. Stop Condition

Stop after writing this artifact. Do not stage, commit, push, PR or enter next gate.
