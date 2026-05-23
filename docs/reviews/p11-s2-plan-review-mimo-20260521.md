# P11-S2 Historical Summary Dedupe Plan Review — AgentMiMo（2026-05-21）

## Verdict

`PASS_WITH_FINDINGS`

## Scope

Independent adversarial review of `docs/reviews/p11-s2-historical-summary-dedupe-plan-20260521.md`.

Review lens: line reference accuracy, scope safety, evidence preservation, RR-13 / repo-audit exclusion, validation command coverage, acceptance criteria completeness, stop condition adequacy, residual ownership.

## Evidence Reviewed

- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- Post-P11 follow-up planning: `docs/reviews/post-p11-follow-up-planning-20260521.md`
- Plan under review: `docs/reviews/p11-s2-historical-summary-dedupe-plan-20260521.md`
- Accepted baseline: `00411dc`

## Line Reference Verification

All line references in the plan were verified against the current control doc (`00411dc` baseline):

| Plan reference | Actual content | Status |
|---|---|---|
| `:11`–`:30` Startup Packet | Lines 11-30, correct | OK |
| `:32`–`:39` Active Gate Ledger | Lines 32-39, correct | OK |
| `:73`–`:80` Active Residuals | Lines 73-80, correct | OK |
| `:82`–`:96` Evidence Preservation Rules / Archive Strategy | Lines 82-96, correct | OK |
| `:160`–`:172` Historical Snapshot Before P11-S1 | Lines 160-172, correct | OK |
| `:205`–`:216` Duplicate summary rows | Lines 205-216, correct | OK |
| `:227`–`:265` Stale current gate / baseline bullets | Lines 227-265, correct | OK |
| `:266` onward detailed evidence logs | Line 266 onward, correct | OK |
| `:1454` RR-13 duplicate `016492` | Line 1454, correct | OK |
| `:1621`–`:1632` P10/P11 status log | Lines 1621-1632, correct | OK |

No stale or off-by-one line references found.

## Duplicate Row Analysis

The plan correctly identifies the duplicate rows in `1.1.2 当前技术债与后续规划摘要`（lines 205-216）:

- **`Repo hygiene` appears twice**: line 210 says "P10 已通过 PR #6 squash merge 到 `main`"（closed）, line 215 says "下一阶段 P10-S1"（future）. Contradiction confirmed.
- **`Control doc hygiene` appears twice**: line 211 says "P11-S1 plan/review 已接受；下一步文档实现"（stale next-step）, line 216 says "可读性需提升"（generic future）. Duplication confirmed.

Proposed deduplication into one row per category is sound.

## Findings

### F1 — Validation command incomplete for P11-S2 status wording (INFO)

**Severity**: INFO

**Evidence**: The plan's validation `rg` command（line 96-97）searches for stale patterns like `P11-S1 implementation` and `P11-S1 plan accepted`, but does not search for the current gate status `P11-S2` to verify the deduplicated `Control doc hygiene` row was updated with the correct next-step wording. After implementation, the deduplicated row should reference `P11-S2 historical summary dedupe` as the current gate. Without a positive check, an implementer could collapse the rows but leave generic future wording instead of the correct P11-S2 status.

**Recommendation**: Add `P11-S2` to the `rg` validation command as a positive existence check, e.g.:

```bash
rg -n 'P11-S2' docs/implementation-control.md
```

This confirms the deduplicated row was updated with the correct current-state wording.

### F2 — Section 1.3 stale gate wording scope could be tighter (INFO)

**Severity**: INFO

**Evidence**: The plan proposes renaming or annotating `### 1.3 当前 Gate 与基线裁决（2026-05-21）`（lines 227-265）as historical. Lines 229-231 contain the stale bullets:

```
- 当前分支：`main`
- 当前 gate：`P11-S1 plan accepted`
- 下一 gate：`P11-S1 implementation`
```

The plan says "rename or annotate this section as historical baseline before P11-S1 implementation, then summarize only the stale P7-P11 planning prose that duplicates the active archive rows." This is directionally correct but leaves the implementer a choice between two approaches: (a) rename the section heading and mark lines 229-231 as historical, or (b) remove lines 229-231 entirely since the Startup Packet already holds the current truth. Both are valid under the plan, but approach (b) is simpler and less error-prone.

**Recommendation**: Consider specifying that lines 229-231 (the three stale "current gate" bullets) should be removed outright, since the Startup Packet at lines 11-30 is the sole active resume truth. The remaining bulk content in lines 232-265 can be marked historical. This reduces ambiguity for the implementer.

### F3 — Acceptance criteria do not check for "P11-S1 plan accepted" removal from section 1.3 (LOW)

**Severity**: LOW

**Evidence**: The acceptance criteria（line 127）state:

> Old `P10-S1` and `P11-S1 implementation` future-state wording is either explicitly marked historical or removed where duplicated by preserved detailed evidence.

This covers `P10-S1` and `P11-S1 implementation` but does not explicitly mention `P11-S1 plan accepted`（the stale current-gate wording at line 230）. The validation `rg` command does catch it, but the acceptance criteria text should mirror the validation scope for consistency.

**Recommendation**: Add `P11-S1 plan accepted` to the acceptance criteria wording alongside `P10-S1` and `P11-S1 implementation`.

### F4 — Stop condition could explicitly mention Startup Packet / Active Gate Ledger conflict (INFO)

**Severity**: INFO

**Evidence**: The stop condition（line 144）states:

> stop if a required evidence field cannot be preserved from the existing control record, if P10/P11 accepted facts conflict with `Startup Packet` or `Active Gate Ledger`

This is adequate. However, the plan does not mention what happens if the implementation accidentally modifies the Startup Packet or Active Gate Ledger sections（lines 11-39）. The non-goals and acceptance criteria implicitly protect these sections, but an explicit stop condition like "stop if implementation would modify lines 11-39" would add defense-in-depth.

**Recommendation**: Consider adding an explicit stop condition: "stop if implementation edits would touch Startup Packet or Active Gate Ledger sections."

## Positive Observations

1. **Scope safety is well-defined**: Non-goals are comprehensive and match the post-P11 follow-up planning scope. No source, test, config, runtime, design, or repo-audit changes.
2. **Evidence preservation rules are correctly referenced**: The plan cites the exact governing rules at `:82`–`:96` and requires their application.
3. **RR-13 ownership is preserved**: The plan explicitly keeps RR-13 duplicate `016492` as human-owned with no automatic fix.
4. **`docs/repo-audit-20260521.md` exclusion is maintained**: Both in non-goals and in the proposed deduplicated `Repo hygiene` row.
5. **Python reference-existence check is a good safeguard**: The optional validation script checks for required artifact paths, commit hashes, and residual IDs after edits.
6. **Stop conditions are actionable**: The plan stops if non-doc files would change, evidence can't be preserved, or RR-13 would require deciding which row is correct.

## Acceptance Criteria Checklist

| Criterion | Status |
|---|---|
| Only `docs/implementation-control.md` changed | OK — plan scope is correct |
| Startup Packet and Active Gate Ledger remain current truth | OK — explicitly protected |
| Duplicate rows collapsed | OK — lines 205-216 correctly targeted |
| Old future-state wording marked historical or removed | OK — lines 227-265 correctly targeted (see F3 for minor gap) |
| Artifact paths, commits, PR refs, validation results, residual IDs preserved | OK — evidence preservation rules cited |
| RR-13 duplicate `016492` remains human-owned | OK — explicitly stated |
| `docs/repo-audit-20260521.md` excluded | OK — in non-goals and deduplicated row |
| `git diff --check` passes | OK — in validation commands |

## Summary

The plan is sound and ready for implementation. All line references are accurate, scope is safe, evidence preservation is correctly governed, and stop conditions are actionable. The four findings are all INFO/LOW severity — none block implementation. F1 (add `P11-S2` positive check to validation) and F3 (add `P11-S1 plan accepted` to acceptance criteria) are the most useful to fold in before implementation proceeds.
