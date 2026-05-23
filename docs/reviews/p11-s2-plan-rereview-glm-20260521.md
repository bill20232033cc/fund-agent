# P11-S2 Plan Re-review — AgentGLM（2026-05-21）

**Reviewer**: AgentGLM (independent plan reviewer)
**Plan artifact**: `docs/reviews/p11-s2-historical-summary-dedupe-plan-20260521.md` (revised)
**Prior review**: `docs/reviews/p11-s2-plan-review-glm-20260521.md`
**Verdict**: `PASS`

---

## Re-review Scope

Targeted re-review of the revised P11-S2 plan against the four findings from the initial GLM review. No new findings sought unless a revision introduced a new issue.

---

## Finding Disposition

### F1 (MEDIUM) — Section 1.3 "summarize" instruction ambiguous about scope boundary

**Original issue**: Plan said "summarize only the stale P7-P11 planning prose that duplicates the active archive rows" without clearly separating the editable header area from the evidence chain at L234-L264.

**Revision**: Plan now splits section 1.3 into two independently scoped blocks:
- L60-L63: "Clean Stale Current Gate And Baseline Bullets" — scoped to L227-L233 only; explicitly lists the three stale bullets (L229-L231) to remove or convert; no "summarize" instruction.
- L65-L68: New separate block for L234-L264 — states "must not be shortened, consolidated, deduplicated, or replaced by a pointer during P11-S2"; only narrow controller-determined wording fixes allowed.

The "summarize" instruction has been entirely removed. The evidence chain now has an explicit do-not-touch rule with a narrow exception gated on controller determination.

**Status**: ✅ RESOLVED

### F2 (INFO) — Validation `rg` command matches legitimate mentions

**Original issue**: `rg` pattern `Repo hygiene|Control doc hygiene` would match legitimate uses in Active Residuals table, Phase History Index, and phase definition table.

**Revision**: Validation commands completely restructured (L104-L111):
- First `rg` replaced with `rg -n 'P11-S2'` — a positive check that active state is visible.
- Stale wording check replaced with `nl -ba | sed -n '205,233p'` — targeted line-range extraction for reviewer inspection, with explicit instruction that the reviewer must confirm absence of unqualified stale wording.
- Preserved-reference `rg` unchanged and still well-targeted.

No broad category-name patterns remain. Judgment on stale wording is now a reviewer responsibility, not a grep result.

**Status**: ✅ RESOLVED

### F3 (INFO) — Active Residuals post-implementation state not specified

**Original issue**: Plan did not specify whether the "historical duplicate summary rows" residual should be updated or closed after successful implementation.

**Revision**: L36-L39 adds "Expected post-implementation state for the Active Residuals row":
- Before acceptance: may remain as-is.
- After acceptance: must be removed or rewritten as closed by P11-S2; must not remain as an open pending residual.

Acceptance criterion L143 added: "The Active Residuals row for historical duplicate summary rows is no longer left as an open pending P11-S2 residual after implementation acceptance; it is removed or closed by P11-S2."

**Status**: ✅ RESOLVED

### F4 (LOW) — Startup Packet gate timing ambiguity

**Original issue**: Unclear whether acceptance criteria meant P11-S2 plan/review or P11-S2 implementation when saying "identify P11-S2 correctly."

**Revision**: Stop condition L161 adds "if the implementation would edit Startup Packet or Active Gate Ledger outside explicit controller-authorized gate bookkeeping." This clarifies that Startup Packet/Active Gate Ledger may only be updated during gate transitions, not during documentation cleanup. Acceptance criterion L138 "identify P11-S2 correctly" is unambiguous — P11-S2 is the current phase regardless of sub-gate.

**Status**: ✅ RESOLVED

### Supplementary: Python reference check now mandatory

**Original review noted**: Python existence check was listed as "Optional" but should be mandatory given evidence preservation requirements.

**Revision**: Section header changed from "Optional implementation acceptance check" to "Mandatory implementation acceptance check" (L113). Acceptance criterion L145 added: "The mandatory Python required-reference check passes."

**Status**: ✅ RESOLVED

---

## Verdict

**PASS**

All four findings from the initial review have been resolved. The revised plan has tighter scope boundaries (F1), cleaner validation commands (F2), explicit post-implementation residual state (F3), and clarified gate/implementation boundary (F4). No new issues introduced by the revision.
