# DS Targeted Re-review — 004393 / 2025 Same-year Reviewed Golden Content Plan

Date: 2026-06-13

Gate: `004393 / 2025 Same-year Reviewed Golden Content Planning Gate`

Reviewer: AgentDS (targeted re-review of amended plan)

Original DS review: `docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-plan-review-ds-20260613.md`

Verdict: `PASS`

## 1. Scope

Targeted re-review of the amended plan artifact against the two blocking findings
(R1, R2) and four non-blocking findings (N1-N4) from the original DS review.
No new scope.

## 2. Finding Disposition

### 2.1 R1 — Candidate Row Input Dependency (original: HIGH, blocking)

Original finding: the evidence gate required candidate rows as input but neither
the planning gate nor the evidence gate produced them, creating a process
deadlock.

Amendment changes:

- **New §5** `Candidate Row Source Contract` — defines a named prerequisite artifact
  (`docs/reviews/mvp-004393-2025-same-year-reviewed-golden-content-candidate-rows-20260613.md`),
  a producer (`Candidate Row Source Preparation Gate` worker or
  controller-authorized owner), required artifact format with explicit
  `golden-answer-metadata` `report_year: 2025`, and boundary rules (under
  `docs/reviews/`, not `reports/golden-answers/`).
- **New §6** `Conditional Next Entry` — two-way branch: absent/invalid → routes to
  preparation gate; present/valid → routes to evidence gate.
- **§14** stop conditions now check candidate row artifact absence and shape
  validity.
- **§15** residuals include a dedicated row for absent/invalid candidate artifact,
  routed to the preparation gate.
- **§16** conditional next entry mirrors §6.

Assessment: **RESOLVED**. The deadlock is eliminated. The plan now defines an
explicit preparation gate as prerequisite with conditional routing. If candidate
rows don't exist, the flow routes to the preparation gate rather than
deadlocking. The preparation gate itself is described at contract level (what it
must produce, format, boundaries) but not planned in detail — this is acceptable
because the conditional routing ensures it will be planned before any attempt to
open the evidence gate without candidate rows.

### 2.2 R2 — Defer Class Conflation (original: MEDIUM, blocking)

Original finding: the defer rule merged "evidence not in report" with "evidence
not yet read" into a single trigger, preventing correct residual routing.

Amendment changes:

- **§10** `Defer classes` table defines three explicit classes:

  | Class | Trigger | Required Residual |
  |---|---|---|
  | `DEFER_NOT_READ` | Evidence gate didn't read enough reviewable same-year evidence | `same-year row pending direct read/review for <field>.<sub_field>` |
  | `DEFER_NOT_DISCLOSED` | Same-year evidence checked, value not disclosed in cited material | `same-year source does not disclose required value for <field>.<sub_field>` |
  | `DEFER_AMBIGUOUS` | Evidence exists but supports multiple plausible values | `same-year value ambiguous for <field>.<sub_field>; requires controller/source-owner clarification` |

- **§10** `Zero-accepted-row disposition` routes back by defer class.
- **§15** residuals include separate entries for each defer class with distinct
  destination gates.

Assessment: **RESOLVED**. The three-way split correctly distinguishes
re-reviewable (NOT_READ), permanently unavailable (NOT_DISCLOSED), and
needs-clarification (AMBIGUOUS) dispositions. Each class has a distinct residual
format and destination gate. Residuals can now be correctly routed to the
appropriate follow-up gate.

### 2.3 N1 — Low-confidence Controller Acknowledgment (original: LOW, non-blocking)

Original finding: low-confidence rows could be accepted with only evidence
artifact rationale, without controller-level scrutiny.

Amendment change in **§10** confidence rules:

> low rows must be deferred unless the evidence artifact records row-specific
> rationale and the controller judgment explicitly acknowledges that exact
> low-confidence row.

Assessment: **ADDRESSED**. The amended text adds two requirements: (1) row-specific
rationale in the evidence artifact, and (2) explicit controller acknowledgment
in the controller judgment. This closes the accumulation-without-scrutiny path
and gives the controller final say on any low-confidence row acceptance.

### 2.4 N2 — Cross-year Structural Attributes (original: LOW, non-blocking)

Original finding: no guidance on structurally stable registration-level fields
(e.g., fund_type, fund_name) that don't change year-over-year.

Amendment: No dedicated structural-attribute rule was added.

Assessment: **NOT EXPLICITLY ADDRESSED, BUT ACCEPTABLY RESOLVED IN PRACTICE**.
The candidate row example in §5 uses `classified_fund_type | fund_type |
active_fund | high | 年报2025 §2 page-<locator>`, demonstrating the expected
pattern: even structural fields must cite the 2025 annual report. This is the
correct conservative position — structural fields cite the current year report
rather than relying on cross-year inheritance. The lack of an explicit exemption
preserves review rigor. The finding was non-blocking and remains non-blocking.

### 2.5 N3 — Temp-path Cleanup Verification (original: LOW, non-blocking)

Original finding: no requirement to verify cleanup after optional build smoke.

Amendment changes:

- **§12** validation matrix: new row `Temp artifact cleanup check, if smoke ran`
  with required result `No temp smoke artifacts remain after the gate`.
- **§12** text: "The evidence artifact must also verify that no temp smoke
  artifacts remain after the smoke."

Assessment: **ADDRESSED**. Cleanup verification is now an explicit validation
matrix row with a required result. The evidence artifact must confirm no temp
smoke artifacts remain.

### 2.6 N4 — Evidence Gate Verification Scope Wording (original: LOW, non-blocking)

Original finding: plan said "verify each row against direct same-year evidence,"
implying primary-source verification capability a no-live gate cannot deliver.

Amendment changes:

- **§12** new `Evidence wording boundary` section:
  - "If the evidence gate does not read the 2025 annual-report body directly, it
    must not claim primary-source verification."
  - "In that case, it may only claim candidate-row source review against the
    candidate artifact and any accepted excerpts/locators present in the reviewed
    source package."
  - "Primary annual-report verification requires an explicitly authorized gate
    that reads the annual-report body through the approved evidence boundary."

Assessment: **ADDRESSED**. The evidence wording boundary section explicitly
constrains what the evidence gate can claim. While §7 retains "verify" as a
purpose verb, §12 now provides a hard boundary: no primary-source verification
claim unless the annual-report body is actually read. The two sections together
correctly express intent (evaluate rows) while constraining claims (don't
overstate capability).

## 3. Amendment Quality Check

No new blockers were introduced by the amendments:

| New element | Assessment |
|---|---|
| §5 Candidate Row Source Contract | Defines prerequisite without over-planning it. Format and boundary rules are clear. |
| §6 Conditional Next Entry | Clean two-way branch. No ambiguity about which path to take. |
| §10 Defer classes table | Three classes are mutually exclusive and exhaustive for the defer cases. Required residual format is specific. |
| §10 Zero-accepted-row disposition | Correctly routes back with per-class residuals. |
| §10 Minimum acceptance criterion | Reasonable minimum bar (≥1 row) for any future content write gate. |
| §10 Alternate source locator guidance | Handles the case where stable page numbering is unavailable. Pragmatic without relaxing evidence standards. |
| §12 Evidence wording boundary | Provides clear, enforceable constraint on evidence gate claims. |
| §13 Reviewer row-editing prohibition | Prevents review-side effects. Good defense-in-depth. |
| §13 Parallelism | Explicitly allows parallel MiMo/DS reviews. No new risk. |
| §9 Exact artifact name pattern table | Removes ambiguity about artifact paths. |

## 4. Original Positive Findings Preservation

All 10 positive findings (P1-P10) from the original review are preserved in the
amended plan. Several are strengthened:

| Finding | Status |
|---|---|
| P1 Historical probe prohibition | Preserved (§11). |
| P2 Source-text inference rejection | Preserved (§10). |
| P3 Tracked-output protection | Strengthened (§9 exact paths, §12 cleanup check). |
| P4 NOT_READY preservation | Preserved (§1, §2, §4, §15). |
| P5 Row-local evidence criteria | Preserved (§10). |
| P6 Reject rules | Preserved (§10). |
| P7 Confidence classification | Strengthened (controller acknowledgment for low). |
| P8 Fallback prohibition | Preserved (§2, §4, §10). |
| P9 Read-as-proof disallow | Preserved (§8). |
| P10 Write set separation | Strengthened (§9 exact path table, §5 candidate row boundary). |

## 5. Residuals

| Residual | Owner | Destination |
|---|---|---|
| Candidate Row Source Preparation Gate is described at contract level but not yet planned in detail. | Controller / preparation gate owner | Planning gate for preparation, if candidate rows are absent. |
| N2 cross-year structural attribute guidance remains implicit. | Evidence gate reviewers | Apply judgment in evidence gate; candidate row example demonstrates expected pattern. |

## 6. Final Recommendation

Both blocking findings (R1, R2) are resolved. All four non-blocking findings
(N1-N4) are addressed. No new blockers were introduced by the amendments. All
original positive findings are preserved.

**Verdict: PASS**. The amended plan is ready for controller judgment. The
evidence gate may open conditional on candidate row availability per §6.
