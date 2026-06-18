# DS Targeted Re-review — 004393 / 2025 Tracked Golden Content Write Plan (Amended)

Date: 2026-06-13

Reviewer role: DS plan reviewer (targeted re-review)

Target: amended `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-20260613.md`

Prior review: `docs/reviews/mvp-004393-2025-tracked-golden-content-write-plan-review-ds-20260613.md` (verdict `PASS_WITH_FINDINGS`, required amendments F1–F3, advisory F4–F5)

Scope: check only whether prior findings F1–F5 and required amendments F1–F3 are resolved or properly routed. Do not re-review the entire plan.

Verdict: `PASS`

## Resolution Check

### F1 (Required) — Live/repository access prerequisite is explicit

**Prior state**: Plan recommended source-body verification gate without addressing the circular dependency that `FundDocumentRepository` access requires live EID/network not yet authorized.

**Amended state**: Resolved.

- Lines 69–73: New explicit prerequisite section before the recommended next gate. Two paths: (a) confirm repository-bounded access without new live access, or (b) include a separately authorized live EID sub-slice. Stop if neither is available.
- Line 77: Verification scope now names `FundDocumentRepository.load_annual_report()` as the access path.
- Line 78: Explicit prohibition on direct filesystem PDF reads without separate authorization.
- Line 119: New validation matrix row `Source-body availability prerequisite` gates verification start on access availability.
- Line 143: New stop condition at the top of the list: stop before verification if no access path exists.
- Line 158: New residual explicitly tracking that source-body access may require separate live authorization.
- Line 172: Recommended next entry reiterates the prerequisite.

The prerequisite correctly acknowledges the AGENTS.md constraint (line 76: "对基金文档的存取，都应该只通过统一的文档仓库接口，禁止直接操作文件系统") and the current control truth's no-live boundary. No circular dependency remains.

**Resolution**: Resolved.

### F2 (Required) — Row-level partial acceptance replaces all-or-nothing blocking

**Prior state**: Stop condition was "Stop if any of the seven candidate rows cannot be matched" — one failure blocked all.

**Amended state**: Resolved.

- Line 81: Verification scope explicitly states "row-level partial acceptance: each row may be verified, deferred or rejected independently; one row mismatch must not block independently verified rows."
- Line 120: Validation matrix row now says "Each row is independently verified, deferred or rejected; verified rows may proceed independently."
- Line 144: Stop condition rewritten to per-row granularity: "Stop for any individual row that cannot be matched … that row must be deferred or rejected independently, while verified rows may proceed independently."

The row-level independence aligns with the design doc's identity contract `(fund_code, report_year, field_name, sub_field)` and the controller judgment's independent per-row dispositions.

**Resolution**: Resolved.

### F3 (Required) — Field-level match criteria are defined

**Prior state**: No match criteria — plan said "verify" and "confirm" without defining what constitutes a match.

**Amended state**: Resolved.

- Lines 87–93: New `Field-level match criteria` subsection with per-field definitions:
  - `fund_name`, `management_company`, `custodian`: whitespace-normalized exact match
  - `fund_code`: exact string match, outer-whitespace trim only
  - `inception_date`: normalized date equality (Chinese date ↔ ISO)
  - `investment_objective`: contiguous substring after whitespace normalization
  - `benchmark_name`: character-exact match after trimming; deviations recorded as mismatch diffs
- Line 120: Validation matrix references "field-level match criteria above."
- Line 144: Stop condition references "field-level criteria above."

Criteria are specific, per-field, and include normalization rules and diff-recording requirements. A verification agent can apply them mechanically; a reviewer can independently confirm match/mismatch judgments.

**Resolution**: Resolved.

### F4 (Advisory) — investment_objective uses normalized verbatim substring rather than full span re-extraction

**Prior state**: Plan treated span-boundary confirmation as mechanical verification, but long-text spans in PDF have no machine-readable boundaries.

**Amended state**: Resolved.

- Line 45: Row disposition now says "confirms the candidate value appears verbatim as a normalized substring" (was "confirms exact source-body span boundaries").
- Line 82: Verification scope: "confirm the candidate value appears verbatim in the source body after whitespace normalization; do not require the verification worker to re-extract or re-litigate full span boundaries."
- Line 92: Match criteria: "source body must contain the candidate value as a contiguous substring after whitespace normalization; this is not a full span re-extraction."
- Line 145: Dedicated stop condition: "Stop … only if the candidate value is not present as a normalized verbatim substring; do not stop solely because full free-text span boundaries are not mechanically recoverable."

The verification is now scoped as a falsifiable check (is the candidate text in the body?) rather than an unbounded re-judgment of span boundaries.

**Resolution**: Resolved.

### F5 (Advisory) — Future write has backup/restore safety and value-level cross-check

**Prior state**: Future JSON rebuild overwrote `golden-answer.json` without backup; no value-level cross-check against the verification artifact.

**Amended state**: Resolved.

- Lines 110–111: Content edit shape now mandates prebuild backup and post-build value-level cross-check with restore-on-failure.
- Line 123: New validation matrix row `Prebuild JSON backup / restore safety`.
- Line 126: Existing content preservation validation upgraded from key-only to key-and-value assertions.
- Line 127: New validation matrix row `Accepted value cross-check` — compares new records against the source-body verification artifact, restores on failure.
- Line 139: Review plan now requires value-level cross-check by reviewers.
- Line 150: New stop condition: "Stop and restore the prebuild `golden-answer.json` if value-level cross-check against the source-body verification artifact fails."

The backup→build→cross-check→restore-on-failure chain closes the transcription-error gap between verification output and implementation write.

**Resolution**: Resolved.

## Additional Observations

No new issues introduced by the amendments. Specific positive checks:

- The plan correctly routes all body access through `FundDocumentRepository.load_annual_report()` (lines 71, 77, 119, 143), consistent with AGENTS.md line 76.
- The plan explicitly prohibits direct filesystem PDF access (line 78), consistent with AGENTS.md line 76 ("禁止直接操作文件系统").
- The plan references the completed reviews at line 34, creating appropriate traceability from findings to amendments.
- The new `Existing content preservation` validation (line 126) is stronger than the original: it now asserts value-level preservation, not just identity-key preservation.

## Unresolved Findings

None. All five prior findings (F1–F5) are resolved. All three required amendments (F1–F3) are applied.

## Conclusion

**Verdict: `PASS`**

All prior findings are resolved. The amended plan correctly gates source-body verification on access availability, adopts row-level partial acceptance, defines per-field match criteria, scopes investment_objective as verbatim substring confirmation, and adds backup/restore safety with value-level cross-check for the future write gate. No new issues found. The plan is ready for controller judgment.
