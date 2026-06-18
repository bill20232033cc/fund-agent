# Plan Review B: Matched Source Identity Recovery Planning/Prep Gate

## Findings

### F1 - High - Future PDF/network evidence path can bypass `FundDocumentRepository`

- Location: `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-20260608.md:86-87`, `AGENTS.md`, `docs/design.md`.
- Issue: the plan lists future official PDF/network acquisition evidence as acceptable without requiring it to go through `FundDocumentRepository`.
- Failure scenario: a future worker treats "official PDF/network acquisition evidence" as authorization to write a downloader or read a PDF URL/cache/source helper directly.
- Required fix: remove or rewrite that source category. Any network/PDF acquisition must belong to `matched-source FundDocumentRepository acquisition evidence gate`, record `AnnualReportSourceMetadata` or equivalent repository provenance, source failure classification, fallback eligibility, and `fallback_used=false`.

### F2 - High - New identity state is not mapped to existing evidence contract

- Location: plan `:73-77`, `:203-209`; `fund_agent/fund/report_evidence.py`; `fund_agent/fund/report_quality_validation.py`.
- Issue: the plan uses `identity_status=matched` and `identity_review_status=controller_accepted` as unlock conditions, but the existing evidence bundle uses `verified_annual_report` / `unverified` / `mismatch`; scoring-ready validation also requires `source_failure_category=none`, non-unknown source boundary, and not only `external_official`.
- Impact: exact/numeric correctness can become a parallel truth source that cannot enter the existing quality/golden/readiness evidence chain.
- Required fix: require reuse or explicit mapping to `document_type=annual_report`, `identity_status=verified_annual_report`, `source_boundary`, `source_failure_category=none`, `fallback_allowed=false`, `fallback_used=false`, and `review_artifact_refs`. Future tests should cover `report_quality_validation` source document acceptance/rejection.

### F3 - High - Row-field unlock granularity is insufficient

- Location: plan `:137-148`, `:150-161`, `:203-212`.
- Issue: the plan says "per row-field" but does not require an identity key with `fund_code + report_year + field_name + sub_field`. Composite fields such as `fee`, `return`, `holdings`, and `risk` can be over-unlocked.
- Failure scenario: accepting a management fee rate is interpreted as accepting all `fee`; accepting one top holding row is interpreted as accepting all `holdings`.
- Required fix: unlock keys must include at least `fund_code`, `report_year`, `field_name`, and `sub_field`; tabular fields also need `metric_id`, `table_id`, `row_locator`, or equivalent stable locator. Guard tests must prove unaccepted sub-fields remain blocked.

### F4 - Medium - Manual PDF evidence can be accepted without official locator/id

- Location: plan `:64-66`, `:81-85`, `:107-124`.
- Issue: the plan allows `accepted manual file identity` and `accepted local PDF path` but does not require an official announcement id, official URL, or official metadata locator.
- Impact: checksum proves local file stability, not official disclosure identity.
- Required fix: manual PDF evidence that unlocks exact/numeric assertions must record at least one official locator, official announcement id, or official document id. Local PDF plus checksum alone may only enter a manual review state, not exact/numeric unlock.

### F5 - Medium - Copyright/retention guard does not define excerpt size

- Location: plan `:179-187`, `:211-212`.
- Issue: "minimal excerpts" and "no full PDF text" do not bound excerpt size.
- Required fix: define excerpt boundaries: retain only necessary table header, target row, unit/period context, and short title/metadata; forbid full page, chapter, or whole-table retention unless a separate retention gate accepts it.

## Open Questions

1. Is the future identity manifest an extension of `docs/reviews/mvp-small-golden-set-manifest-20260608.json`, or a new fixture-adjacent identity record with a stable foreign key?
2. Can a manual evidence gate record user-provided official URL/metadata without network verification? If yes, how does the reviewer distinguish user assertion from auditable official locator?
3. If a future heavy gate redefines fallback eligibility, must it still require `primary_failure_category` and repository provenance consistent with the current `source_provenance` contract?

## Verdict

FAIL. Direction is correct, but PDF/network boundaries, identity schema mapping, and row-field unlock granularity are blocking.
