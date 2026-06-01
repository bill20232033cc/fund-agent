# MVP LLM writer/auditor contract hardening plan re-review — MiMo

Gate: `MVP LLM writer/auditor contract hardening gate`
Role: plan re-reviewer
Date: 2026-05-31
Reviewed artifact: `docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-20260531.md`
Original review: `docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-review-mimo-20260531.md`

## Conclusion

**PASS**

All controller-accepted findings are fixed in plan. Gate sequencing, scope boundaries, hard constraints, non-goals, and score-loop exclusion are correctly preserved. Plan is handoff-ready and code-generation-ready.

---

## Accepted findings verification

| Finding ID | Original verdict | Plan fix location | Verification |
|---|---|---|---|
| MiMo F-001 | blocking | §8.3 (line 244), §6 fix log (line 110), Slice B exact changes (lines 411-414) | **FIXED** — §8.3 explicitly requires `_audit_contract_markers()` to check `<!-- required_output:<item> -->` exact marker, not bare item text. Slice B repeats the same requirement. Bare item text allowed only as auxiliary context, not pass condition. |
| MiMo F-002 | blocking | Slice B tests (lines 433-434), §6 fix log (line 111) | **FIXED** — Slice B tests explicitly update auditor `tests/fund/test_chapter_auditor.py` `_valid_markdown()` helper to include `<!-- required_output:<item> -->` markers for each `contract.required_output_items`. |
| MiMo F-003 / GLM N-4 | non-blocking | Slice B exact changes (line 430), §6 fix log (line 112) | **FIXED** — Facet dedup strategy committed: "MVP 去重策略固定为 first blocking occurrence per unique facet text". Same facet text multiple occurrences → only first blocking occurrence reported; any asserted occurrence still blocks. |
| MiMo F-004 | non-blocking | Validation matrix (line 613), §6 fix log (line 114) | **FIXED** — Real provider smoke command explicitly labeled: `Real provider smoke command (label: real-provider-smoke-006597-2024)`. |
| MiMo F-005 / GLM N-3 | non-blocking | §8.2 mapping table (lines 212-218), Slice A mapping table (lines 362-368), §6 fix log (line 113) | **FIXED** — Explicit Service mapping table lists all 5 new writer stop reasons → `(blocked, <same_reason>)`. Each preserves diagnostic category. Table present in both §8.2 and Slice A. |
| GLM N-1 | non-blocking | §8.2 (line 198), Slice A (line 343), §6 fix log (line 116) | **FIXED** — Unified naming: `INCOMPLETE_FINISH_REASONS` constant + `response_incomplete` stop reason. No `content_filter` mislabeling as truncation. |
| GLM N-2 | non-blocking | §8.4 deterministic mapping (lines 277-283), Slice C (line 486), §6 fix log (line 117) | **FIXED** — `required_corrections` synthesis is deterministic: explicit mapping for P1 structure, C2 required output, C2 candidate facet, E1 anchor, llm:parse_failure. Unknown rules use sanitized issue message fallback with sensitive content stripped and length bounded. |

---

## Gate sequencing check

| Criterion | Status |
|---|---|
| Current gate = contract hardening only | PASS — §3 (line 35-38) scope matches |
| Next gate = real provider smoke acceptance | PASS — §3 (lines 39-42) defers acceptance裁决 |
| Later gate = score improvement loop | PASS — §3 (lines 43-46) explicitly excludes scoring |
| No score-loop pulled into current gate | PASS — §4 (line 70) prohibits score schema/task generation; §3 (line 42) prevents pulling acceptance gate forward |
| No golden/fixtures/score/quality gate changes | PASS |
| No Gate 5 dayu/Host/Agent | PASS |
| No PR state changes | PASS |
| No secrets/full provider response | PASS |
| Deterministic analyze/checklist unchanged | PASS |

---

## User steering verification

- **"current Gate A is contract hardening only"** — Confirmed. Plan §3 line 35-38 and §4 lines 50-70.
- **"next gate is MVP real provider smoke acceptance gate"** — Confirmed. Plan §3 lines 39-42 explicitly defers acceptance裁决 to next gate.
- **"later gate is MVP chapter generation score loop design gate"** — Confirmed. Plan §3 lines 43-46 and §4 line 70 explicitly exclude score loop.
- **"current plan must not pull score-loop implementation into Gate A"** — Confirmed. §4 line 70: "不实现 `MVP chapter generation score improvement loop gate` 的任何 score schema、score history、自动 pro-codex repair task generation、pass-rate/evidence-compliance-rate dashboard 或持续优化循环。"

---

## Scope / sequencing check

- Writer prompt/protocol → parser fail-closed → auditor line protocol → repair context → timeout classification: correct ordering.
- First fix point is prompt contract, not audit relaxation. PASS.
- Parser fail-closed before auditor is the right design. PASS.
- Repair context is typed explicit (`ChapterRepairContext` dataclass), not extra_payload. PASS.
- Timeout classification separates provider runtime from writer/auditor contract. PASS.
- Bounded retry preserved via existing `max_repair_attempts`. PASS.
- Real smoke is validation-only in this gate, not acceptance裁决. PASS.

---

## Self-check

Self-check: pass

---

Artifact path: `docs/reviews/mvp-llm-writer-auditor-contract-hardening-plan-rereview-mimo-20260531.md`
Conclusion: PASS
Findings: 7/7 accepted findings verified fixed (F-001, F-002, F-003, F-004, F-005, GLM N-1, GLM N-2)
