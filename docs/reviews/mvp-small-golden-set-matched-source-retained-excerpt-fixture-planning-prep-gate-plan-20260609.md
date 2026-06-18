# MVP Small Golden Set Matched-Source Retained Excerpt Fixture Planning/Prep Gate Plan

## Gate Metadata

- Work unit: `matched-source retained excerpt fixture planning/prep gate`.
- Classification: `heavy`.
- Date: 2026-06-09.
- Role: AgentCodex planning worker.
- Scope type: planning/prep only.
- Target rows: `004393`, `004194`, `006597`, `110020`, `017641`, all `report_year=2024`.
- Output artifact: `docs/reviews/mvp-small-golden-set-matched-source-retained-excerpt-fixture-planning-prep-gate-plan-20260609.md`.
- Steering amendment: EID is a preferred official registry locator, not a mandatory engineering module or exclusive document source. Fund-company official PDF URLs and CNINFO PDF URLs may be accepted as `official_document_url` when the source identity acceptance policy below is satisfied.

## Current Accepted Facts

- Branch observed: `feat/mvp-llm-incomplete-run-artifacts`.
- Existing unrelated untracked workspace residue exists and is not evidence for this gate.
- Small golden set fixture/evidence planning is accepted at checkpoint `4ebaf0b`.
- Small golden set extractor correctness implementation gate plan is accepted at checkpoint `d05c1c9`.
- Slice A manifest/schema guard is accepted at checkpoint `a94c705`.
- Slice B fixture retention evidence is accepted at checkpoint `ceb418b`.
- Slice C reconciliation plan is accepted at checkpoint `2371ad1`.
- Slice C Option 1 source identity acquisition is accepted at checkpoint `0cc0c14` and found no matched annual-report source identity from that path.
- Slice C Option 2 parser/fixture mechanics is accepted at checkpoint `cb2cf77`; it accepted parser mechanics, metadata normalization, manifest status preservation and explicit unavailable/deferred degradation only.
- Matched annual-report source identity recovery planning/prep gate is accepted at checkpoint `65532ab`.
- Docs-only manual source identity evidence for `004393 / 2024` is accepted at checkpoint `2706f91`.
- Docs-only manual source identity evidence for `004194`, `006597`, `110020` and `017641 / 2024` is accepted at checkpoint `7cc0479`.
- All five source identity recovery manifest rows are `controller_accepted` as docs-only manual source identity evidence.
- No retained field excerpts are accepted.
- No expected values are accepted.
- No row-field unlocks exist.
- No exact, normalized text or numeric correctness acceptance exists.
- Fixtures remain unchanged from Slice C Option 2 synthetic/unmatched mechanics.
- Golden/readiness promotion, quality gate semantic changes, provider/runtime/config changes, live evidence and PR/release external state remain unauthorized.
- EID search/detail metadata can support official registry location, but current phaseflow must not be blocked on EID document extraction when an accepted fund-company official PDF URL or CNINFO official PDF URL satisfies the same source identity anchors.

## First-Principles Boundary

Extractor implementation is not legal yet because extractor correctness requires a same-source chain:

```text
accepted source identity
  -> accepted retained excerpt for one exact row-field sub-key
  -> accepted expected value, unit, period, normalization rule and tolerance
  -> extractor/parser assertion
  -> implementation fix only if a same-source failing test proves root cause
```

The current accepted state stops at docs-only source identity. It proves that the five rows have review-owned annual-report identity metadata, but it does not prove any field text, any expected value, any numeric normalization, or any extractor failure. Therefore this gate may define excerpt intake, retention boundaries, schema and transition rules. It must not read source documents, retain source text, project fixtures, write expected values, modify extractors or assert correctness.

## Allowed Inputs

This planning gate may use only:

- `AGENTS.md`.
- `docs/current-startup-packet.md`.
- `docs/implementation-control.md`.
- `docs/design.md`.
- Accepted planning artifact `docs/reviews/mvp-small-golden-set-matched-source-identity-recovery-planning-prep-gate-plan-20260608.md`.
- Accepted planning artifact `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-20260608.md`.
- Accepted planning artifact `docs/reviews/mvp-small-golden-set-extractor-correctness-slice-c-reconciliation-plan-20260608.md`.
- Existing accepted docs-only source identity facts referenced by current control truth.
- User-supplied instructions in this turn.

## Disallowed Inputs

This planning gate must not use:

- PDFs, annual report folders, local PDF paths, local annual-report caches or parsed report caches.
- Arbitrary untracked files or workspace residue.
- Network, DNS, socket, curl, endpoint probes, provider probes, live LLM, retry or fallback commands.
- `akshare`, EID, source helpers, direct downloaders or `FundDocumentRepository`.
- Generated reports, model summaries, rendered report text, provider artifacts or old live logs as field truth.
- Any source text not explicitly user-provided and accepted by a later excerpt review gate.

## Source Identity Acceptance Policy

This plan separates official registry location from official document identity:

- `official_registry_locator`: a preferred locator to an official disclosure registry or search/detail page. EID is preferred for this field when available, but it is not mandatory and does not by itself become the annual-report source truth.
- `official_document_url`: the actual official PDF/document URL accepted for the row after review. This may be an EID document URL, a fund-company official website/CDN PDF URL, or a CNINFO PDF URL.
- `official_document_id`: stable id or source-safe token derived from the accepted official document URL, announcement id, PDF path token, or registry/document instance id.

Acceptable `official_document_url` origins for the current route:

| Origin | Acceptable? | Conditions |
|---|---:|---|
| EID official PDF/document URL | Yes | Must satisfy the annual-report title, publisher, PDF profile and id/hash rules below. |
| Fund-company official website or CDN PDF URL | Yes | Publisher must be the fund manager or its official disclosure channel; must satisfy the PDF profile and id/hash rules below. |
| CNINFO PDF URL | Yes | CNINFO must be treated as an official disclosure platform; must satisfy title, publication/platform metadata where available, PDF profile and id/hash rules below. |
| EID search/detail result without accepted document URL | Locator only | May support discovery/registry evidence, but cannot be source truth by itself. |
| Search engine result, generic web snippet, rendered report, LLM output | No | Cannot establish official document identity or field truth. |
| Fallback output | No | Current route keeps fallback as non-unlocking source identity evidence. |

Minimum acceptance conditions for a future source identity acceptance decision:

1. The title is a `2024` annual report for the fund, not a quarterly/interim report, prospectus, fund contract or generated summary.
2. The publishing party is the fund manager or an official disclosure platform.
3. PDF section 2, fund profile, or an equivalent user-provided official profile excerpt proves fund code, fund name and share-class code mapping for the target row.
4. The evidence record includes URL, source-safe id and hash. If the agent did not read/hash a PDF in the authorized gate, the hash must be explicitly marked `user_provided` or `not_provided`; it must not be implied.
5. Search results and fallback traces are not source truth. They can only point to a candidate official document that must separately satisfy conditions 1-4.

This policy prevents EID extraction from becoming the current engineering bottleneck. EID remains useful as a preferred official registry locator, while source identity acceptance can proceed from fund-company official PDFs or CNINFO PDFs when the document-level anchors are present.

## Retained Excerpt Minimum Record Schema

Future retained excerpt records must be keyed per row-field sub-key. The stable key is:

```text
fund_code + report_year + field_group + field_name + sub_field
```

For tabular or repeated fields, the key must additionally include `table_id` plus `row_locator`, `metric_id`, `holding_rank`, or an equivalent stable locator. A fund-level identity acceptance never unlocks every field in the fund.

Minimum record schema for a future retained excerpt:

| Field | Required | Meaning |
|---|---:|---|
| `schema_version` | yes | Suggested value: `fund-agent.small_golden_set_retained_excerpt.v1`. |
| `fund_code` | yes | One of the five accepted rows. |
| `report_year` | yes | Must be `2024` for this small set. |
| `source_identity_ref` | yes | Review/controller artifact refs proving matched annual-report source identity. |
| `official_registry_locator` | conditional | Preferred official registry/search/detail locator, for example EID; locator only, not source truth by itself. |
| `official_document_url` | yes | Accepted official PDF/document URL, including EID PDF, fund-company official PDF or CNINFO PDF when accepted by review. |
| `source_document_id` | yes | Stable official document id, announcement id, canonical locator token, or accepted source-safe identifier from identity evidence. |
| `source_document_title` | yes | Annual-report title from accepted identity evidence. |
| `field_group` | yes | One of the field groups listed in the priority matrix. |
| `field_name` | yes | Specific extractor-facing field name. |
| `sub_field` | yes | Specific assertion target, for example `management_fee_rate` or `annual_nav_growth_rate`. |
| `row_field_key` | yes | Deterministic concatenation of row and field identity. |
| `excerpt_id` | yes | Stable id for the retained excerpt record. |
| `excerpt_origin` | yes | Must be `user_provided_excerpt` in the next legal docs-only route, unless a separate authorized repository gate changes this. |
| `excerpt_text` | conditional | Allowed only in a later retained excerpt review gate; absent in this planning gate. |
| `excerpt_text_sha256` | conditional | Required when excerpt text is retained. |
| `excerpt_size_chars` | conditional | Required when excerpt text is retained. |
| `section_or_page_locator` | yes | User-provided section/page/table context or official metadata locator. |
| `table_id` | conditional | Required for table-derived fields. |
| `row_locator` | conditional | Required for table row assertions. |
| `unit_context` | conditional | Required for numeric fields. |
| `period_context` | conditional | Required for period-sensitive fields. |
| `normalization_rule_ref` | conditional | Required before expected values can be accepted. |
| `expected_value_status` | yes | Must remain `not_accepted` in the excerpt intake gate until a separate expected-value review accepts it. |
| `assertion_kind_status` | yes | Must remain `not_allowed` until row-field unlock reaches expected-value acceptance. |
| `copyright_scope` | yes | `minimal_context_only`, `too_broad_blocked`, or `not_retained`. |
| `review_status` | yes | `pending_review`, `reviewed_pass`, `reviewed_blocked`, or `controller_accepted`. |
| `review_artifact_refs` | yes | Plan, review and controller artifacts that accepted the excerpt record. |

## Field Priority Matrix

This matrix defines intake priority only. No source text, expected value, exact assertion, normalized text assertion or numeric assertion is accepted by this gate.

| Fund code | Report year | source_document | report_year | fund_type | benchmark | manager | scale | fee | return | holdings | risk |
|---|---:|---|---|---|---|---|---|---|---|---|---|
| `004393` | 2024 | identity ref only; no value accepted | identity ref only; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted |
| `004194` | 2024 | identity ref only; no value accepted | identity ref only; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted |
| `006597` | 2024 | identity ref only; no value accepted | identity ref only; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted |
| `110020` | 2024 | identity ref only; no value accepted | identity ref only; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted |
| `017641` | 2024 | identity ref only; no value accepted | identity ref only; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted | priority field; no value accepted |

Field group intent:

- `source_document`: link to already accepted annual-report source identity only.
- `report_year`: confirm row/document year consistency only; no source text retained here.
- `fund_type`: prepare classification evidence intake; no classification value accepted yet.
- `benchmark`: prepare exact benchmark text intake; no benchmark value accepted yet.
- `manager`: prepare manager name/role/tenure excerpt intake; no manager value accepted yet.
- `scale`: prepare asset scale value/unit/date context intake; no numeric value accepted yet.
- `fee`: prepare fee sub-field excerpt intake; one fee sub-field must not unlock sibling fee fields.
- `return`: prepare return metric/period/unit excerpt intake; one return metric must not unlock sibling return metrics.
- `holdings`: prepare table row/weight/date intake; one holding row must not unlock the holdings table.
- `risk`: prepare risk metric/source context/threshold semantics intake; one risk sub-field must not unlock sibling risk metrics.

## User-Provided Excerpt Intake Rules

The next legal excerpt intake route is docs-only and user-provided:

1. The user provides a short excerpt or structured metadata for a specific `fund_code + report_year + field_group + field_name + sub_field`.
2. The worker records the provided excerpt in a review artifact only if the excerpt links to an already accepted source identity record.
3. The worker must not open, hash, parse, inspect, OCR or read a PDF or local annual-report file.
4. The worker must not fetch official pages or verify links over network.
5. The worker must not infer omitted values from context, fund code, known public facts, generated text or old logs.
6. The worker must record provenance as `user_provided_excerpt` and keep source identity refs separate from field excerpt refs.
7. The worker must mark `expected_value_status=not_accepted` unless the same authorized gate explicitly includes expected-value review scope.
8. The worker must mark sibling fields as still blocked.

Minimum fields in a user-provided excerpt intake artifact:

- `fund_code`, `report_year`, `field_group`, `field_name`, `sub_field`.
- Accepted source identity refs for that row.
- `official_registry_locator` when available, with EID recorded as preferred locator rather than mandatory source.
- `official_document_url`, allowing EID PDF, fund-company official PDF or CNINFO PDF only after the source identity acceptance policy is satisfied.
- URL/id/hash status, distinguishing `user_provided`, `agent_verified_in_authorized_gate`, `not_provided` and `not_applicable`.
- User-provided excerpt text or user-provided structured excerpt metadata.
- User-provided section/page/table/row locator.
- Approximate excerpt size.
- Copyright scope decision.
- Whether the excerpt is narrow enough for the target sub-field.
- Explicit statement that no expected value is accepted unless a separate expected-value section and review says so.
- Reviewer decision per row-field key: `controller_accepted`, `reviewed_blocked`, `deferred`, or `unavailable`.

## Copyright And Retention Boundaries

- Do not commit full PDFs.
- Do not commit full extracted annual-report text.
- Do not commit whole pages, whole chapters, broad sections, full tables, or repeated excerpts that reconstruct a substantial report section.
- Retain only the smallest excerpt needed for the exact row-field sub-key: table header plus target row and unit/period context, or a short sentence/metadata field when the source is non-tabular.
- Suggested default ceiling: one retained excerpt should stay below 1,000 characters unless a review artifact explains why table header plus target row requires more.
- Suggested aggregate ceiling: each fund should keep retained text materially below a page-equivalent and must not accumulate broad report coverage.
- If a field needs more context than the ceiling allows, mark the row-field as `deferred_retention_scope_too_broad`.
- Prefer official locator/id, checksum, section/page/table/row anchors and short excerpts over raw source text.
- Generated summaries, paraphrases and LLM output cannot replace retained source excerpts.
- User-provided excerpt text may be retained only after an excerpt review accepts that the text is narrow, source-linked and necessary for the row-field.

## Fixture Projection Rules

Fixture projection is not allowed in this planning gate.

Reason:

- Projection would turn review-owned evidence policy into test data.
- Current accepted state has source identity only, not retained field excerpts or expected values.
- A fixture row with `fixture_source_kind=real_minimal_excerpt` would imply source text retention has been accepted; that has not happened.
- A fixture field with `exact`, `normalized_text` or `numeric_percent` would imply expected-value acceptance; that has not happened.

Future projection may occur only after excerpt review acceptance:

| Accepted state | Fixture projection allowed? | Rule |
|---|---:|---|
| Source identity accepted, no field excerpt | No | Preserve existing synthetic/unmatched fixture shape. |
| Source identity accepted plus row-field excerpt accepted | Limited | May project excerpt metadata for that exact row-field key only; expected value still blocked unless separately accepted. |
| Source identity, excerpt and expected value accepted | Limited | May project `assertion_kind` and expected value only for that exact row-field key. |
| Sibling field in same group lacks excerpt | No | Must remain blocked/deferred/unavailable. |
| Retention too broad or source link absent | No | Keep row-field blocked and record reason. |

The future fixture projection must be additive and must not replace the review-owned manifest as truth. It must preserve:

- `promotion_allowed=false`.
- `fallback_invocation=prohibited`.
- `fallback_used=false` for the current unlock route.
- `exact_numeric_correctness_allowed=false` for every row-field without accepted excerpt and expected value.
- Existing Slice C Option 2 synthetic/unmatched mechanics for non-unlocked fields.

## Row-Field Gated Unlock Transitions

Unlocking is per row-field sub-key:

```text
fund_code + report_year + field_group + field_name + sub_field
```

Required transitions:

| State | Evidence required | Allowed next state |
|---|---|---|
| `controller_accepted_source_identity` | Already accepted docs-only annual-report identity for the row | `matched_identity_no_field_excerpt` |
| `matched_identity_no_field_excerpt` | User-provided minimal excerpt accepted for one row-field sub-key | `field_excerpt_accepted_expected_value_blocked` |
| `field_excerpt_accepted_expected_value_blocked` | Expected value, unit, period, normalization rule and tolerance accepted by review/controller | `field_assertion_allowed` |
| `field_assertion_allowed` | Fixture projection and focused test pass without live/PDF/repository/fallback/provider access | `field_fixture_ready` |
| `field_fixture_ready` | Same-source failing test proves root cause | `extractor_implementation_allowed_for_that_root_cause` |
| `extractor_implementation_allowed_for_that_root_cause` | Focused implementation, regression test and review pass | `field_correctness_accepted_locally` |

Blocking rules:

- Source identity acceptance alone does not unlock field assertions.
- Excerpt acceptance alone does not accept expected values.
- Expected-value acceptance for one sub-field does not unlock sibling sub-fields.
- Field fixture readiness does not promote golden/readiness status.
- Extractor implementation remains illegal until a later accepted implementation gate exists and a same-source failing test proves root cause.

## Validation Matrix

This planning/prep gate validation:

| Check | Command or evidence | Expected result |
|---|---|---|
| Branch check | `git branch --show-current` | Current branch recorded. |
| Dirty scope check | `git status --short` | Existing unrelated residue observed and ignored. |
| Required docs read | Required files listed by the assignment | Current accepted facts and boundaries confirmed. |
| Single artifact scope | Changed-file list | Only this planning artifact is changed by this worker. |
| Formatting | `git diff --check -- docs/reviews/mvp-small-golden-set-matched-source-retained-excerpt-fixture-planning-prep-gate-plan-20260609.md` | PASS. |

Future excerpt intake gate validation:

| Check | Expected result |
|---|---|
| Source identity linkage | Every excerpt row-field links to an accepted source identity ref. |
| User-provided origin | Every excerpt origin is explicit and no agent-side PDF/source reading occurred. |
| Size boundary | Excerpt size and aggregate row scope stay within retention limits or are blocked. |
| Row-field key guard | Excerpt acceptance applies only to one exact row-field sub-key. |
| No expected-value leakage | Excerpt artifact does not silently accept expected values. |
| Copyright guard | No full PDF, full page, full chapter, broad table or reconstructed report section is retained. |
| No fixture projection | Projection waits for excerpt review acceptance and, where needed, expected-value acceptance. |

Future fixture projection gate validation:

| Check | Expected result |
|---|---|
| Projection source | Reads accepted review-owned excerpt/expected-value artifacts only. |
| Synthetic preservation | Non-unlocked fields preserve Slice C Option 2 synthetic/unmatched mechanics. |
| Sibling field guard | Accepted sub-field does not unlock sibling sub-fields. |
| Promotion boundary | `promotion_allowed=false` and no golden/readiness promotion remain intact. |
| No live dependency | Tests use local reviewed fixtures only and do not call repository/PDF/network/fallback/provider. |

## Stop Conditions

Stop immediately if any worker needs or attempts:

- PDF reading, hashing, parsing, OCR or local annual-report folder access.
- `FundDocumentRepository`, direct source helper, cache, downloader, EID, akshare, network, DNS, socket, curl, endpoint, fallback, provider or live LLM.
- Arbitrary untracked workspace residue as source text or field truth.
- Extractor, test or fixture modification in this planning gate.
- Expected value acceptance without an explicit expected-value review scope.
- Fixture projection before excerpt review acceptance.
- Any exact, normalized text or numeric correctness claim in this gate.
- Golden/readiness promotion, quality gate semantic change, provider/runtime/config change, Agent runtime expansion, multi-year runtime, score-loop, release, merge, PR creation or mark-ready.
- Retained excerpt scope that is too broad to avoid reconstructing substantial source content.

## Next Gate Options

After this plan is reviewed and accepted, phaseflow should use this ordered route:

1. `control truth reconciliation`: sync the EID-as-preferred-locator policy and allowed official document URL origins into current control truth.
2. `manual evidence intake for all 5 rows`: record official registry locator, accepted `official_document_url`, URL/id/hash status and PDF profile anchors for each row. EID is preferred as locator but not mandatory as document source.
3. `source identity acceptance decision`: decide row by row whether official document identity is accepted. Search result and fallback evidence remain non-unlocking.
4. `retained excerpt fixture for accepted rows only`: accept minimal retained excerpts only for rows whose source identity decision passed, and only for specific row-field sub-keys.
5. `row-field extractor correctness tests`: project accepted row-field excerpts and expected values into tests without changing golden/readiness semantics.
6. `extractor fixes only after same-source failing tests`: modify extractor code only when a same-source failing test proves the root cause.

If no row has accepted source identity, stop and keep exact/numeric correctness blocked. If a row has identity accepted but lacks field excerpts, that row remains `matched_identity_no_field_excerpt` and cannot enter extractor correctness tests.
