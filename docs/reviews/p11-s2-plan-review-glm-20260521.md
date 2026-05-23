# P11-S2 Plan Review — AgentGLM（2026-05-21）

**Reviewer**: AgentGLM (independent plan reviewer)
**Plan artifact**: `docs/reviews/p11-s2-historical-summary-dedupe-plan-20260521.md`
**Verdict**: `PASS_WITH_FINDINGS`

---

## Review Scope

Independent adversarial review of the P11-S2 historical summary dedupe plan against:

- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md` (full 1633 lines)
- Post-P11 planning: `docs/reviews/post-p11-follow-up-planning-20260521.md`
- Accepted baseline: `00411dc`

Review lens per instructions: evidence safety, Startup Packet / Active Gate Ledger truth preservation, artifact/commit/PR/residual reference integrity, RR-13 human ownership, repo-audit exclusion, source/test/config/product/runtime/design non-modification, line reference accuracy, validation command adequacy, and acceptance criteria completeness.

---

## Line Reference Verification

| Plan claim | Actual content | Verified |
|---|---|---|
| L11-L30: Startup Packet | Startup Packet with current gate `post-P11 follow-up planning accepted`, next `P11-S2 plan/review` | ✅ |
| L32-L39: Active Gate Ledger | 4-row ledger ending with post-P11 planning accepted → P11-S2 | ✅ |
| L73-L80: Active Residuals | RR-13, repo-audit exclusion, historical duplicate rows, future product selection | ✅ |
| L82-L96: Evidence Preservation Rules + Archive/Summarize Strategy | Governing rules for cleanup boundaries | ✅ |
| L160-L172: Historical Snapshot Before P11-S1 | Table with stale "P11-S1 plan accepted" / "P11-S1 implementation" wording | ✅ |
| L205-L216: Section 1.1.2 duplicate rows | Two "Repo hygiene" rows (L210 closed-by-P10, L215 next-is-P10-S1); two "Control doc hygiene" rows (L211 P11-S1-accepted, L216 generic future slice) | ✅ |
| L227-L233: Section 1.3 stale header bullets | "当前 gate: P11-S1 plan accepted", "下一 gate: P11-S1 implementation" | ✅ |
| L234-L264: Detailed chronological evidence under "当前裁决" | Per-phase gate transition evidence with artifacts, commits, PR details, validation counts | ✅ |
| L265: Agent routing note | Not evidence-bearing log; is operational guidance | ✅ |
| L266+: Detailed per-phase status records | P0-P8 historical status, evidence-bearing, not duplicate summary | ✅ |
| L1454: RR-13 `016492` | CSV duplicate, human-owned, no-auto-fix | ✅ |
| L1621-L1632: P10/P11 status log | Post-P9 follow-up through post-P11 planning entries | ✅ |

**All line references verified accurate against `00411dc` baseline.**

---

## Evidence Safety Assessment

The plan correctly distinguishes two operations:

1. **Summarizing stale archive prose** — allowed when exact facts remain in table or archive entry
2. **Deleting evidence** — explicitly prohibited

The plan identifies three categories of target content:
- Stale active-state wording in the pre-P11-S1 historical snapshot (L160-L172): wording says "P11-S1 plan accepted" as current state. **Safe to annotate as historical.**
- Duplicate technical debt rows in section 1.1.2 (L205-L216): two pairs of rows where the first contradicts accepted P10/P11 facts. **Safe to collapse, preserving closed/deferred owners.**
- Stale gate/baseline header in section 1.3 (L227-L233): section title says "当前 Gate" but content is stale. **Safe to rename/annotate.**

The plan explicitly requires preserving:
- Artifact paths, commits, PR references, validation results — ✅
- Residual IDs and owners (RR-13 `016492`) — ✅
- Reviewer limitations — ✅
- Detailed evidence logs (L266+) — ✅

**Evidence safety: adequate.** The Non-goals (L81-L88) and Stop Condition (L140-L144) provide additional guardrails.

---

## Findings

### F1 — MEDIUM: Section 1.3 "summarize" instruction is ambiguous about scope boundary

**Location**: Plan L56-L58 (proposed edit for section 1.3)

**Evidence**: The plan says to "rename or annotate this section as historical baseline before P11-S1 implementation, then summarize only the stale P7-P11 planning prose that duplicates the active archive rows." The phrase "stale P7-P11 planning prose that duplicates the active archive rows" is not precisely defined. The detailed chronological evidence in lines 234-264 contains per-phase entries that each say "当前 gate 为 X，下一 gate 为 Y" — these are historical facts (true at the time of each transition), not "stale prose." The Phase History Index (L41-L57) already has one-row-per-phase summaries, but the detailed evidence in 234-264 contains information NOT in the index (artifact paths, commit hashes, PR URLs, reviewer names, validation counts).

**Risk**: An implementer could interpret "summarize" as permission to shorten or consolidate the detailed evidence bullets (234-264), which would lose artifact paths, commit hashes, and reviewer limitations that are not recoverable from the Phase History Index alone.

**Mitigation in plan**: The plan does require preservation of lines 236-264 (L58: "do not remove the concrete artifact paths, commits, PR #6 details, validation counts, reviewer limitations, or residual owner facts recorded in lines 236 to 264"). This backstop is present but contradicts the "summarize" instruction if both are applied to the same content.

**Recommendation**: Before implementation, clarify that the "summarize" instruction applies ONLY to the section header and introductory bullets (lines 227-233), not to the detailed chronological evidence chain (lines 234-264). The evidence chain should receive only a section-title rename from "当前 Gate" to a historical label, with no content shortening.

### F2 — INFO: Validation `rg` command will match legitimate mentions

**Location**: Plan L96 (first validation command)

**Evidence**: The `rg` pattern `Repo hygiene|Control doc hygiene` will match legitimate uses in:
- Active Residuals table (L79: "Historical duplicate summary rows | P11-S2 plan/review")
- Phase History Index (L55: "P10 | Repo hygiene / release readiness")
- Phase definition table (L188: "P10 | Repo hygiene / release readiness")

After implementation, these terms should still appear. The command is useful for an audit sweep but cannot serve as a binary pass/fail gate without specifying expected match counts or annotated expected output.

**Recommendation**: Either (a) add expected match count annotations, or (b) narrow the pattern to match only stale-specific phrasing like `下一阶段 P10-S1` or `下一 gate.*P11-S1 implementation`, which ARE expected to be removed. The plan's second `rg` command (L97, checking preserved references) is well-targeted and does not have this issue.

### F3 — INFO: Active Residuals post-implementation state not specified

**Location**: Plan L33 (Active Residuals preservation requirement)

**Evidence**: The plan says Active Residuals should "continue to show RR-13, excluded `docs/repo-audit-20260521.md`, historical duplicate summary rows, and future product feature selection ownership." If the dedupe implementation succeeds, the "historical duplicate summary rows" residual should logically be updated (owner changed from "P11-S2 plan/review" to closed/completed) or removed. The plan doesn't specify whether the implementation should also update this residual row.

**Risk**: LOW. If the residual row is left unchanged post-implementation, it will read as stale (pointing to a plan/review gate that has already passed). This is minor archive noise, not a safety issue.

**Recommendation**: Add an explicit acceptance criterion or implementation note specifying the expected post-implementation state of the "historical duplicate summary rows" residual entry.

### F4 — LOW: Plan references "P11-S2 historical summary dedupe plan/review" as current gate but Startup Packet may need post-implementation update

**Location**: Plan L7 (Objective), L125-L126 (Acceptance Criteria)

**Evidence**: The Startup Packet currently says "Next entry point | `P11-S2 historical summary dedupe plan/review`" (L17). After the plan is accepted and implementation begins, the Startup Packet needs to advance to "P11-S2 implementation" or equivalent. The acceptance criteria (L125-L126) correctly say "Startup Packet and Active Gate Ledger remain the current truth and still identify P11-S2 correctly" but don't specify whether this means P11-S2 plan/review or P11-S2 implementation. This is a minor timing ambiguity.

**Risk**: LOW. The Startup Packet update would happen as part of the gate transition, not as part of the implementation itself. The plan's stop condition correctly prevents gate transitions.

---

## Validation Command Assessment

| Command | Assessment |
|---|---|
| `git diff --check` | ✅ Standard whitespace/conflict marker check |
| `rg` stale pattern search (L96) | ⚠️ See F2 — matches legitimate mentions; useful for audit but not binary pass/fail |
| `rg` preserved reference search (L97) | ✅ Well-targeted; checks for `016492`, `RR-13`, `docs/repo-audit-20260521.md`, commit hashes, PR references, `PASS_WITH_FINDINGS`, `388 passed` |
| Python reference existence check (L103-L119) | ✅ Checks 7 required references are present after edits; appropriate for acceptance validation |

**Overall validation adequacy**: Sufficient with F2 addressed. The combination of `git diff --check`, preserved-reference `rg`, and Python existence check covers the critical evidence preservation requirement.

---

## Acceptance Criteria Assessment

| Criterion | Adequate | Notes |
|---|---|---|
| Only implementation-control.md changed | ✅ | Clear scope boundary |
| Startup Packet / Active Gate Ledger remain current truth | ✅ | See F4 for minor timing note |
| Duplicate rows collapsed | ✅ | Specific target rows identified |
| Stale future-state wording handled | ✅ | Clear examples given |
| Evidence preserved | ✅ | Enumerated in detail |
| RR-13 human-owned | ✅ | Explicit |
| repo-audit excluded and unmodified | ✅ | Explicit |
| `git diff --check` passes | ✅ | Standard |

**Missing criterion**: No acceptance criterion requiring the Python reference existence check (L103-L119) to pass. This check is listed under "Optional implementation acceptance check" (L100) but should arguably be mandatory given the evidence preservation requirements.

---

## Non-goals Assessment

All 8 non-goals (L81-L88) are appropriate and correctly exclude source, tests, config, runtime, schema, CLI, Service, Engine, Capability, renderer, quality gate, product behavior, design.md, repo-audit, and gate transitions. No gaps found.

---

## Risks Assessment

The plan identifies 4 risks (L133-L138). All have adequate mitigations. No additional risks identified beyond those covered by findings F1-F4 above.

---

## Verdict

**PASS_WITH_FINDINGS**

The plan is well-structured, correctly scoped to documentation-only cleanup, accurately identifies all stale/duplicate content, preserves required evidence, and maintains appropriate guardrails. The findings are non-blocking:

- F1 (MEDIUM) should be resolved before implementation to prevent accidental evidence loss in section 1.3
- F2 (INFO) should be addressed in validation commands for cleaner acceptance gating
- F3 (INFO) and F4 (LOW) are minor gaps that don't affect implementation safety
