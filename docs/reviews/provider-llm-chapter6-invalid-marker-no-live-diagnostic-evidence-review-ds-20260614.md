# Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence — AgentDS Independent Review

Date: 2026-06-14

Role: AgentDS independent evidence reviewer

Gate: `Provider/LLM Chapter 6 Invalid-marker No-live Diagnostic Evidence Gate`

Target: `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-20260614.md`

Verdict: `ACCEPT`

## 1. Scope

This review artifact is review-only as instructed. It does not modify source, tests, runtime, prompts, README, design docs, control docs, or the target evidence artifact. No live, provider, LLM, network, PDF, FDR, source, acquisition, analyze, checklist, golden, readiness, release, or PR commands were run.

Release/readiness remains: `NOT_READY`

## 2. Evidence Reviewed

| Input | Use |
|---|---|
| `AGENTS.md` | Rule truth, role boundaries, EID single-source/no-fallback policy, `NOT_READY` preservation |
| `docs/current-startup-packet.md` | Active gate, disposition plan checkpoint `6afe67e`, `NOT_READY` preservation |
| `docs/implementation-control.md` | Control truth, gate classification `standard`, D1-D5 evidence only, no implementation/live |
| `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-controller-judgment-20260614.md` | Controller judgment: verdict `ACCEPT_READY_FOR_NO_LIVE_DIAGNOSTIC_EVIDENCE_GATE_NOT_READY`, D1-D5 required evidence questions |
| `docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-20260614.md` | Accepted disposition plan: root-cause classification, evidence gap, D1-D5 validation matrix |
| Target evidence artifact | `docs/reviews/provider-llm-chapter6-invalid-marker-no-live-diagnostic-evidence-20260614.md` |
| `fund_agent/fund/chapter_writer.py` | Full body read for D1-D3 code verification |
| `fund_agent/services/chapter_orchestrator.py` | Targeted reads: `_INVALID_MARKER_PREFIXES`, `_writer_prompt_contract_diagnostic()`, `_writer_issue_id_prefix()`, `_writer_issue_id_prefix_counts()` |
| `fund_agent/agent/runner.py` | Full body read for D4 writer-block terminal behavior verification |
| `fund_agent/agent/repair.py` | Full body read for D4 repair context construction verification |

Not read: writer/auditor/repair markdown bodies, provider payloads, PDF/source/cache bodies, source bodies, final report body, reports safe metadata files.

## 3. Independent Verification

### Q1: Did the evidence artifact stay within allowed no-live/read/write boundaries?

**Finding: YES, within boundaries.**

Commands run were limited to `rg`, `sed`, `git status --branch --short`, focused `uv run pytest`, and fake-input `uv run python -c` snippets. No source, test, runtime, prompt, README, design, or control doc files were modified. No body reads of writer/auditor/repair markdown, provider payloads, PDF/source/cache, or final report body occurred. No live, provider, network, PDF, FDR, source, acquisition, analyze, checklist, golden, readiness, release, or PR commands were run.

EID single-source/no-fallback is preserved. Eastmoney, fund-company, CNINFO, fallback routes remain out of scope. Release/readiness remains `NOT_READY`.

### Q2: Are D1-D3 actually proven by current code/tests/snippet evidence?

**Finding: YES, all three independently verified against current code.**

**D1 — Chapter 6 prompt contract rendering:**

At `fund_agent/fund/chapter_writer.py:698-702`, `_chapter_prompt_fragments()` renders:
- Line 698: `"证据断言只能使用 allowed anchor set 中的 marker：\`<!-- anchor:<anchor_id> -->\`；required_anchor_ids 是允许集合，不要求全量使用。"` — exact anchor marker syntax confirmed.
- Line 699: `"禁止根据 fact_id、source_field_id、source_field_name 或 fact value 自行合成 anchor id"` — no synthesized anchor prohibition confirmed.
- Line 702: `_bond_risk_anchor_contract_prompt(chapter)` — Chapter 6 bond-risk internal/组级 anchor prohibition confirmed.

At `chapter_writer.py:1224-1242`, `_bond_risk_anchor_contract_prompt()` returns exactly: `"bond_risk_evidence 内部/组级 anchors 不是 ChapterEvidenceAnchor，不得写入 \`<!-- anchor:... -->\`；只有"允许 anchors"列表中的 anchor_id 可引用。"` when bond_risk_evidence facts are present.

**D2 — Validator taxonomy:**

At `chapter_writer.py:1660-1692`, `_invalid_marker_issues()`:
- Scans all HTML comments via `_COMMENT_RE`.
- If `"anchor" in payload.lower()` AND `_ANCHOR_MARKER_RE.fullmatch(match.group(0)) is None` → emits `issue_id="writer:invalid_anchor_marker:{offset}"` with `reason="llm_contract_violation"`.
- `_ANCHOR_MARKER_RE` at line 68: `re.compile(r"<!-- anchor:([^<>\s]+) -->")`.

So `<!-- ANCHOR:bad -->` (uppercase ANCHOR, extra space) fails `fullmatch` → `writer:invalid_anchor_marker` / `llm_contract_violation`.

At `chapter_writer.py:1848-1876`, `_parse_anchor_markers()`:
- Uses `_ANCHOR_MARKER_RE.findall(text)` — only processes syntactically valid markers.
- Checks each found anchor_id against `allowed` set from `prompt.allowed_anchor_ids`.
- If `anchor_id not in allowed` → calls `_unknown_anchor_issue()` which returns `reason="unknown_anchor"`.

So `<!-- anchor:unknown-anchor -->` (valid syntax, unauthorized id) → `writer:unknown_anchor` / `unknown_anchor`.

The taxonomy distinction (malformed syntax → `invalid_marker`/`llm_contract_violation`; valid syntax + unauthorized id → `unknown_anchor`) is correct and complete in the current code.

**D3 — Diagnostic payload mapping:**

At `chapter_orchestrator.py:162-167`, `_INVALID_MARKER_PREFIXES`:
```python
("writer:invalid_anchor_marker", "writer:invalid_missing_marker",
 "writer:unknown_missing_reason", "writer:evidence_line_without_anchor_marker")
```

At `chapter_orchestrator.py:1449`:
```python
invalid_marker_count = sum(prefix_counts.get(prefix, 0) for prefix in _INVALID_MARKER_PREFIXES)
```

At `chapter_orchestrator.py:1636-1654`, `_writer_issue_id_prefix()`:
- Splits `issue_id` on `":"`, keeps only first two components. E.g., `"writer:invalid_anchor_marker:5"` → `"writer:invalid_anchor_marker"`.
- Raw offset suffixes are stripped; only the safe prefix enters diagnostic payload.

Confirmed: diagnostics count invalid anchor markers via safe prefix, raw malformed suffix strings are not leaked.

### Q3: Is D4 correctly classified as a proven gap?

**Finding: YES. Gap classification is correct.**

At `fund_agent/agent/runner.py:374-394` (`_run_single_chapter()`):
```python
if writer_result.status == "blocked":
    terminal = _terminal_from_writer_stop_reason(writer_result.stop_reason)
    attempts.append(ChapterAttempt(...))
    return ChapterTask(...)
```

When the writer blocks (including `invalid_marker` / `llm_contract_violation`), the runner returns immediately. It does **not** proceed to audit, does **not** call `decide_repair()`, and does **not** construct `repair_context_from_audit()`. The writer parser block is terminal before audit/repair.

At `fund_agent/agent/repair.py:296-297`, the corrective text for anchor issues is:
```python
return "只使用 allowed anchor marker，删除未知 anchor 或改用 allowed anchor。"
```
This is generic and does not include exact `<!-- anchor:<anchor_id> -->` syntax.

At `fund_agent/fund/chapter_writer.py:1458-1481`, `_repair_context_prompt()` renders a generic message without `invalid_marker`-specific guidance.

Therefore:
- No repair attempt or context is generated for `invalid_marker` today — writer parser block terminates before audit.
- If a future path wanted repair-context correction for `invalid_marker`, it would require a new no-live plan.
- D4 is correctly classified as a proven gap, not a code bug or incomplete evidence claim.

### Q4: Is the recommendation supported?

**Finding: YES. The recommendation to proceed to a narrow no-live fix planning gate is well-supported and appropriately constrained.**

The evidence correctly shows:
- D1-D3: current mechanics (prompt rendering, validator taxonomy, diagnostic mapping) are correct and complete.
- D4: the repair-context gap is real and specific — writer-block terminates before audit/repair, so no `invalid_marker`-specific repair instruction exists.

The recommendation:
- Correctly rejects direct implementation (premature given D4 gap).
- Correctly rejects more live evidence (gap is no-live diagnostic, not another occurrence).
- Correctly rejects parser relaxation (validator taxonomy is correct as-is).
- Correctly rejects source/fallback investigation (blocker is writer prompt-contract marker, not source availability).
- Correctly rejects readiness/release/PR movement.
- Correctly frames the planning decision as: strengthen initial prompt salience vs add writer-block repair/retry path for `invalid_marker` vs both.

This aligns with the controller judgment's constraints (`docs/reviews/provider-llm-chapter6-invalid-marker-live-blocker-disposition-plan-controller-judgment-20260614.md`).

### Q5: Are command results and the failed snippet represented honestly?

**Finding: YES. Honest representation confirmed.**

The evidence artifact explicitly documents:
- The failed first snippet: `ModuleNotFoundError: No module named 'fund_agent.fund.chapter_fact_provider'`
- Explicitly states: "Evidence value: none; corrected immediately using the actual module."
- Separately reports the corrected snippet results as the actual evidence.

No failed output is used as proof. The distinction between failed and corrected runs is transparent.

## 4. Non-blocking Observations

The following are observations only; they do not block acceptance:

1. **D2 table could cite code paths**: The D2 evidence table describes the taxonomy correctly but does not reference specific function names (`_invalid_marker_issues()` at `chapter_writer.py:1660`, `_parse_anchor_markers()` at `chapter_writer.py:1848`). Adding these references would strengthen traceability but is not required for correctness.
2. **D3 `_INVALID_MARKER_PREFIXES` scope**: `_INVALID_MARKER_PREFIXES` includes four prefixes, not just `writer:invalid_anchor_marker`. The evidence table focuses on anchor markers which is correct for the Chapter 6 blocker, but a reader unfamiliar with the code might not realize `writer:invalid_missing_marker` and `writer:unknown_missing_reason` also contribute to `invalid_marker_count`. This does not affect the correctness of the D3 finding.

## 5. Independent Findings Summary

| Review question | Finding | Evidence basis |
|---|---|---|
| Q1: No-live/read/write boundaries | Within boundaries | Command audit, no modifications detected |
| Q2: D1 prompt contract rendering | Proven | `chapter_writer.py:698-702, 1224-1242` |
| Q2: D2 validator taxonomy | Proven | `chapter_writer.py:1660-1692, 1848-1876` |
| Q2: D3 diagnostic payload mapping | Proven | `chapter_orchestrator.py:162-167, 1449, 1636-1654` |
| Q3: D4 gap classification | Proven gap, correctly classified | `runner.py:374-394`, `repair.py:296-297` |
| Q4: Recommendation supported | Supported | Aligned with controller judgment constraints |
| Q5: Failed snippet honesty | Honest | Failed attempt explicitly marked as no-value |

## 6. Final Verdict

`VERDICT: ACCEPT`

The evidence artifact stays within allowed boundaries, D1-D4 are correctly proven against current code, D4 gap classification is accurate, the recommendation is appropriately constrained, and command results are represented honestly. No blocking findings.

Release/readiness remains: `NOT_READY`

Stop after writing this artifact. Do not stage, commit, push, PR, or enter the next gate.
