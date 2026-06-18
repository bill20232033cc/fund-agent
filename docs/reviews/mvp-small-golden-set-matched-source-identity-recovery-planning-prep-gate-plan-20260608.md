# MVP Small Golden Set Matched Annual-Report Source Identity Recovery Planning/Prep Gate Plan

## Gate Metadata

- Work unit: `matched annual-report source identity recovery planning/prep gate`.
- Classification: `heavy`.
- Date: 2026-06-08.
- Controller role: gateflow controller.
- Scope type: planning/prep only.
- Target path: small golden set 5 rows for fund codes `004393`, `110020`, `004194`, `006597`, `017641`, all `report_year=2024`.

## Current Accepted Facts

- Draft PR #22 review/fix/re-review gate is accepted at checkpoint `2b1c804`; PR remains draft external state.
- Slice E first no-live Agent body-chapter mechanics is current code fact.
- `small golden set fixture/evidence planning gate` is accepted at checkpoint `4ebaf0b`.
- `small golden set extractor correctness implementation gate` plan is accepted at checkpoint `d05c1c9`.
- Slice A manifest/schema guard is accepted at checkpoint `a94c705`.
- Slice B synthetic fixture retention is accepted at checkpoint `ceb418b`.
- Slice C reconciliation plan is accepted at checkpoint `2371ad1`.
- Slice C Option 1 source identity acquisition is accepted at checkpoint `0cc0c14` and found no matched annual-report source identity for any of the five rows.
- Slice C Option 2 parser/fixture mechanics is accepted at checkpoint `cb2cf77`; it accepts parser and fixture mechanics only.
- All five rows remain `synthetic/unmatched`.
- Exact/numeric extractor correctness remains blocked.

## First-Principles Problem Statement

Exact/numeric extractor correctness can only be evaluated against same-source evidence. A synthetic or unmatched row can prove parser mechanics, fixture shape, degradation semantics, and guard behavior, but it cannot prove that an extracted benchmark, manager, scale, fee, return, holdings, or risk value is correct for a real fund annual report.

The minimal next product loop is therefore not broader Agent runtime expansion and not golden/readiness promotion. The next route is to recover matched annual-report source identity for the five rows, then unlock exact/numeric assertions one row-field at a time.

## Goal

Define a code-generation-ready route for future gates to record matched annual-report source identity and to row-field gate exact/numeric extractor correctness.

The plan must be sufficient for a future implementation worker to build schema guards, fixture records, and tests without inventing policy.

## Non-Goals

- No source/PDF/network/live acquisition in this gate.
- No `FundDocumentRepository` live access.
- No PDF download, akshare, EID, fallback, endpoint probe, DNS, curl, socket, provider probe, retry, or live LLM.
- No extractor implementation change.
- No provider/default/runtime/budget/config change.
- No exact/numeric correctness acceptance.
- No golden/readiness promotion.
- No Chapter calibration, Agent runtime expansion, multi-year runtime, score-loop, PR/release, merge, or mark-ready action.
- No use of arbitrary untracked workspace residue as source truth.

## Minimum Matched Source Identity Fields

Each future matched row must record the following identity fields before any row-field exact/numeric assertion can unlock:

| Field | Required | Meaning |
|---|---:|---|
| `fund_code` | yes | Requested fund code, e.g. `006597`. |
| `report_year` | yes | Target report year, currently `2024`. |
| `fund_name` | yes | Fund name as shown by the matched source or official metadata. |
| `share_class` | yes | Share class/code/class name when applicable; otherwise explicit `not_applicable` with reason. |
| `source_document_kind` | yes | Must be `annual_report`; quarterly/interim/prospectus documents do not unlock this route. |
| `source_document_year` | yes | Must match `report_year`. |
| `source_document_title` | yes | Official title or user-provided title copied from official metadata. |
| `source_publisher` | yes | Fund company, official disclosure platform, or regulator/exchange disclosure source. |
| `publication_date` | yes | Official publication date, or explicit `unknown` only when another stable official document identifier exists. |
| `source_document_id` | yes | Stable official announcement id, disclosure id, canonical official URL token, or repository-derived document id. A local file identity alone is not sufficient to unlock exact/numeric assertions. |
| `source_locator` | yes | Official URL, announcement metadata locator, repository provenance locator, or retained evidence artifact path. A local PDF path alone is only a manual-review locator. |
| `retrieval_mode` | yes | One of `manual_user_provided_metadata`, `future_authorized_repository`, `future_authorized_repository_compatible_manual_intake`. |
| `retrieval_gate` | yes | Gate artifact that authorized and recorded the source identity. |
| `pdf_sha256` | conditional | Required when a PDF file is retained by an authorized gate; for docs-only manual intake this can only be a user-provided checksum. |
| `metadata_sha256` | conditional | Required when metadata payload is retained as evidence. |
| `identity_evidence_origin` | yes | One of the acceptable evidence origins below. |
| `identity_evidence_anchor` | yes | Metadata field, official announcement page, user-supplied title-page locator, repository-derived anchor, or retained excerpt locator proving code/year/document match. |
| `fallback_used` | yes | Must be explicit. Current planned exact/numeric unlock route requires `false`. |
| `fallback_allowed` | yes | Must be `false` for the current unlock route. |
| `source_failure_category` | yes | Must be `none` for unlock; other categories stay blocked/deferred. |
| `source_boundary` | yes | Must map to existing evidence contract values. `repository_derived` is preferred for unlock; `manual_review` may unlock only with official locator/id and controller acceptance; `external_official` alone is not enough for scoring-ready promotion. |
| `identity_status` | yes | `matched`, `unmatched`, `identity_mismatch`, `unavailable`, `deferred`, or `blocked`. |
| `identity_review_status` | yes | `pending_review`, `reviewed_pass`, `reviewed_blocked`, or `controller_accepted`. |
| `review_artifact_refs` | yes | Review and controller artifacts that accepted the identity. |

## Source Identity Schema And Projection Contract

Future implementation must not create a parallel status truth source. The source identity record must use one primary review-owned manifest and one fixture projection:

- Primary manifest: `docs/reviews/mvp-small-golden-set-source-identity-recovery-manifest-20260608.json` or a later explicitly named review-owned successor.
- Fixture projection: each accepted row may project only the minimal accepted identity fields into `tests/fixtures/fund/small_golden_set/<fund_code>_2024/expected_fields.json`.
- Stable row key: `fund_code + report_year`.
- Stable field unlock key: `fund_code + report_year + field_name + sub_field`; tabular fields must additionally carry `metric_id`, `table_id`, `row_locator`, or an equivalent stable locator.
- `schema_version` for the new manifest must be additive and explicit, e.g. `fund-agent.small_golden_set_source_identity_recovery.v1`.

Required status mapping:

| Current accepted state | Future manifest state | Fixture projection | Existing evidence contract mapping |
|---|---|---|---|
| Manifest `source_document_identity.identity_status=pending_offline_fixture` | `identity_status=unmatched` or `deferred` | `source_identity.status=unmatched_synthetic`; `fixture_source_kind=synthetic`; `exact_numeric_correctness_allowed=false` | No `ReportSourceDocument` unlock. |
| Fixture `source_identity.status=unmatched_synthetic` | `identity_status=unmatched` | Preserve unmatched synthetic shape | No exact/numeric assertion allowed. |
| Accepted official/repository identity, no field excerpt | `identity_status=matched`; `identity_review_status=controller_accepted` | `source_identity.status=matched`; `matched_source_document=true`; field assertions stay blocked until field excerpt acceptance | `ReportSourceDocument.document_type=annual_report`; `identity_status=verified_annual_report`; `source_failure_category=none`; `fallback_allowed=false`; `fallback_used=false`; `review_artifact_refs` populated. |
| Accepted identity plus accepted field excerpt | `identity_status=matched`; field key `controller_accepted` | `fixture_source_kind=real_minimal_excerpt` only for accepted field keys; sibling keys stay blocked | Same `ReportSourceDocument` mapping plus field-level anchor refs. |
| Identity mismatch or unsupported source | `identity_status=identity_mismatch` or `blocked` | Preserve `exact_numeric_correctness_allowed=false` | `ReportSourceDocument.identity_status=mismatch` or no accepted document. |
| Repository/source unavailable | `identity_status=unavailable` or `deferred` | Preserve `exact_numeric_correctness_allowed=false` | `source_failure_category` records the repository failure category; no unlock. |

Future tests must cover both the manifest schema and the fixture projection. At minimum, tests must reject a matched sidecar row that cannot map to `ReportSourceDocument` with `document_type=annual_report`, `identity_status=verified_annual_report`, `source_failure_category=none`, `fallback_allowed=false`, `fallback_used=false`, and populated `review_artifact_refs`.

## Acceptable Evidence Sources

The following can establish matched source identity after a reviewed evidence gate:

1. User-provided official annual-report PDF metadata, if the future gate records an official locator or official document/announcement id, user-provided checksum when available, fund code/name/year match, document title, and reviewer acceptance. The agent must not read the PDF file in a docs-only manual evidence gate.
2. User-provided official annual-report URL, if the future gate records canonical URL, announcement/document id when available, publication date, publisher, and reviewer acceptance.
3. User-provided official announcement metadata, if it includes enough stable fields to prove fund code/name, report year, document kind, publisher, publication date or stable id, and reviewer acceptance.
4. Future separately authorized `FundDocumentRepository` acquisition evidence, if the gate explicitly permits repository/PDF/network access and records the resulting `AnnualReportSourceMetadata` or equivalent provenance.
5. Retained minimal excerpts derived from an already accepted matched source, if each excerpt has a checksum, anchor, and source identity link.

Any future PDF or network acquisition must go through a separately authorized `FundDocumentRepository` acquisition gate or a separately accepted `FundDocumentRepository`-compatible manual intake adapter. Direct downloader, direct PDF URL reads, direct cache/source-helper reads, akshare, EID, or filesystem document reads do not belong to this route.

## Unacceptable Evidence Sources

The following must not unlock matched identity or exact/numeric correctness:

- Synthetic fixture values.
- Generated reports, LLM output, or model summaries.
- Arbitrary untracked workspace residue.
- Fund code plus year alone.
- Parser output without a matched source document id or checksum.
- Cached PDF/text content without provenance and checksum.
- Screenshots or copied snippets without official source identity.
- Non-annual documents such as prospectus, quarterly reports, interim reports, fund contracts, or NAV pages.
- Fallback-derived source identity where `fallback_used=true`, unless a future heavy gate explicitly redefines fallback eligibility for this path and preserves repository provenance, `primary_failure_category`, fallback eligibility, and fail-closed failure categories. Current route treats fallback as non-unlocking.
- Unauthorized live command logs, network traces, source probes, repository loads, PDF downloads, akshare/EID output, curl/DNS/socket/provider probes, or live LLM artifacts.
- Local PDF path and checksum without at least one official locator, official announcement id, or official document id. Such evidence can only enter `manual_review_required`, `deferred`, or `blocked`; it cannot establish matched identity or unlock exact/numeric assertions.

## Manual Evidence Recording Rules

If the user manually provides a PDF, official link, or announcement metadata in a later authorized gate, the worker must write an evidence artifact in `docs/reviews/` before any code fixture changes.

Manual docs-only evidence intake means the agent records metadata supplied by the user or already present in an accepted review artifact. It must not open, parse, hash, read, or inspect a PDF file. If the agent must read or hash a file, that is a separate heavy gate requiring explicit PDF/file access authorization and a `FundDocumentRepository`-compatible intake boundary.

The artifact must include:

- Provider of the manual evidence: `user_provided`.
- Received form: `pdf_path`, `official_url`, `announcement_metadata`, or combined.
- Fund code, fund name, share class, and report year asserted by the evidence.
- Document kind and title.
- Publisher and publication date when available.
- Stable source document id or canonical locator.
- Local file path only when the user explicitly provides a local file; local path alone does not prove official identity.
- User-provided SHA256 for PDF, or metadata payload SHA256 when the metadata payload is retained by this repo. Agent-computed PDF SHA256 requires a separate authorized file-access gate.
- Exact identity anchors: metadata field names, official announcement row, official locator, retained excerpt id, or title-page locator already supplied by the user. Agent-side title-page inspection requires a separate authorized file-access gate.
- Copyright/retention decision for the raw file and any excerpt.
- Reviewer decision for each row: `matched`, `unmatched`, `identity_mismatch`, `unavailable`, `blocked`, or `deferred`.
- Controller judgment linking the evidence artifact to the row.

A user-provided PDF is not trusted merely because it exists locally. For matched identity or exact/numeric unlock, it must have at least one official locator, official announcement id, or official document id, plus reviewer/controller acceptance. Local path plus checksum alone can only support `manual_review_required`, `deferred`, or `blocked`.

## Future Authorization Boundary

This planning/prep gate does not authorize `FundDocumentRepository`, PDF, network, source, fallback, akshare, EID, or live provider access.

Future separate gates may be opened only by explicit user authorization:

1. `matched-source manual evidence intake gate`: docs/evidence only; records user-provided official locator, document id, announcement metadata, and user-provided checksum; no network and no agent-side PDF/file reading.
2. `matched-source FundDocumentRepository acquisition evidence gate`: may call `FundDocumentRepository` and access PDF/network only if explicitly authorized; must preserve repository boundary, `AnnualReportSourceMetadata` or equivalent provenance, source failure classification, fallback eligibility, and `fallback_used=false` for current unlock.
3. `matched-source retained excerpt fixture gate`: may retain minimal excerpts and source identity records after identity is accepted.
4. `row-field exact/numeric extractor correctness implementation gate`: may update assertions/tests only for row-fields whose identity and excerpt anchors have been accepted.

## Row-Field Gated Unlock Rules

Unlocking is per row-field sub-key, not per fund, not per field family, and not per small golden set.

The required unlock key is:

```text
fund_code + report_year + field_name + sub_field
```

For tabular or repeated fields, the key must also include `metric_id`, `table_id`, `row_locator`, or an equivalent stable locator. Examples:

- `006597 + 2024 + fee + management_fee_rate`.
- `006597 + 2024 + return + annual_nav_growth_rate`.
- `006597 + 2024 + holdings + top_holding_weight + table_id + row_locator`.
- `006597 + 2024 + risk + max_drawdown + metric_id`.

Required state transitions:

| Prior state | Required evidence | Allowed next state |
|---|---|---|
| `synthetic/unmatched` row | Accepted matched source identity for the row, backed by official locator/id or repository-derived provenance | `matched_identity_no_field_unlock` |
| `matched_identity_no_field_unlock` | Accepted source excerpt for a specific `field_name + sub_field` key | `field_unlock_pending_expected_value` |
| `field_unlock_pending_expected_value` | Expected value, unit, period, normalization rule, and tolerance reviewed | `field_exact_or_numeric_assertion_allowed` |
| `field_exact_or_numeric_assertion_allowed` | Parser/extractor test implementation passes | `field_correctness_accepted_locally` |

Field-specific requirements:

- `source_document`: must point to accepted matched identity.
- `report_year`: must match source annual-report year.
- `fund_type`: must be supported by source identity plus extracted or reviewed classification evidence.
- `benchmark`: requires exact benchmark text or officially disclosed benchmark field excerpt.
- `manager`: requires manager name and tenure/role source anchor when asserted.
- `scale`: requires asset scale value, unit, and date/period.
- `fee`: requires fee type sub-field, value, unit, and whether it is management/custody/sales/other. Accepting one fee sub-field does not unlock the whole `fee` family.
- `return`: requires return metric sub-field, period, unit, and source context. Accepting one return metric does not unlock other return metrics.
- `holdings`: requires holding name/code when available, weight/value, date/period, table id, and row locator. Accepting one holding row does not unlock other holdings.
- `risk`: requires risk metric sub-field, source section/table, unit/period, and threshold semantics when numeric. Accepting one risk metric does not unlock other risk metrics.

Numeric assertions require:

- Source numeric text.
- Normalization rule.
- Unit and period.
- Explicit tolerance if parsing or formatting can differ.
- Reviewer acceptance.

Exact assertions require:

- Source exact text or controlled normalized text.
- Normalization rule for whitespace, punctuation, full-width/half-width, or share-class suffix.
- Reviewer acceptance.

If any required field evidence is absent, that field remains `availability`, `deferred`, or `unavailable`; it must not silently become exact/numeric correctness.

Future guard tests must prove that an accepted sub-field does not unlock sibling sub-fields in the same field family.

## Copyright And Retention Boundaries

- Do not commit full annual-report PDFs unless a later retention gate explicitly approves it.
- Do not commit full annual-report text extraction.
- Retain only minimal excerpts needed for identity and row-field assertions.
- For each assertion, the retained excerpt should be limited to the necessary table header, target row, unit/period context, and short document title or metadata fields.
- Do not retain whole pages, whole chapters, broad text extraction, or whole tables unless a separate retention gate explicitly accepts that scope.
- Do not accumulate retained excerpts in a way that reconstructs a substantial annual-report section.
- Prefer checksums, official locators, metadata, page/table/row anchors, and short excerpts over raw PDF content.
- If a PDF is user-provided, record checksum and local path, but keep storage/retention separate from correctness acceptance.
- If an excerpt is retained, link it to the accepted source identity and keep it narrow enough to support the asserted field only.
- Generated summaries, paraphrases, or LLM output cannot replace source excerpts.

## Verification Matrix

This planning/prep gate:

| Check | Command or evidence | Expected result |
|---|---|---|
| Branch check | `git branch --show-current` | Non-protected working branch. |
| Dirty scope check | `git status --short` | Only gate-owned docs are staged for this checkpoint; unrelated untracked residue remains untouched. |
| Required docs read | `AGENTS.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/design.md` | Current accepted facts confirmed. |
| Plan completeness | This artifact | Contains minimum identity fields, acceptable/unacceptable evidence, manual recording, future authorization, row-field unlock, retention, validation, stop conditions. |
| Formatting | `git diff --check -- <gate files>` | PASS. |
| Review | Two independent plan reviews | No blocking finding, or findings resolved by plan revision/rereview. |
| Judgment | Controller judgment artifact | Accepts or blocks this plan/prep gate. |

Future implementation gates must add tests equivalent to:

| Future test area | Expected assertion |
|---|---|
| Source identity schema guard | Reject row-field exact/numeric assertion without `identity_status=matched` and `identity_review_status=controller_accepted`. |
| Fallback guard | Reject unlock when `fallback_used=true` unless a future accepted gate explicitly allows it. |
| Existing evidence contract mapping | Reject unlock unless source identity can map to `ReportSourceDocument` with `document_type=annual_report`, `identity_status=verified_annual_report`, `source_failure_category=none`, `fallback_allowed=false`, `fallback_used=false`, and populated `review_artifact_refs`. |
| Row-field guard | Allow exact/numeric assertion only for `field_name + sub_field` keys with accepted anchors; sibling sub-fields remain blocked. |
| Synthetic preservation | Preserve `synthetic/unmatched` status for rows without matched source identity. |
| Manual evidence manifest | Validate user-provided checksum, official locator/id, and anchor fields for user-provided PDF metadata, official link, or metadata. |
| Copyright guard | Ensure retained fixtures do not embed full PDF text, whole pages, whole chapters, broad extracts, or whole tables. |

## Stop Conditions

Stop and ask for controller/user decision if any of the following occurs:

- Any step requires source/PDF/network/live acquisition in this planning/prep gate.
- Any step requires `FundDocumentRepository` live access in this planning/prep gate.
- Any reviewer proposes unlocking exact/numeric correctness from synthetic/unmatched rows.
- Any evidence depends on arbitrary untracked workspace residue.
- Any plan change would alter provider/default/runtime/budget/config.
- Any plan change would promote golden/readiness or quality gate semantics.
- Any source route requires fallback acceptance for exact/numeric unlock.
- Any retention approach requires committing full PDF or broad annual-report text.
- Any route blurs Service/Host/Agent/Fund document access boundaries.
- Any future implementation cannot map source identity to the existing `ReportSourceDocument` and source quality validation contract.
- Any row-field unlock lacks `fund_code + report_year + field_name + sub_field` identity, or a table/repeated-field locator when needed.

## Handoff-Ready Future Gate Queue

1. Open `matched-source manual evidence intake gate` if the user provides official PDF metadata, official links, or announcement metadata.
2. Open `matched-source FundDocumentRepository acquisition evidence gate` only if the user explicitly authorizes repository/PDF/network access.
3. Open `matched-source retained excerpt fixture gate` after one or more rows have accepted matched identity.
4. Open `row-field exact/numeric extractor correctness implementation gate` only for fields whose matched source identity and excerpt anchors are accepted.

Until one of these gates is explicitly authorized, the correct next entry point is to stop this planning/prep route after accepted local checkpoint.
