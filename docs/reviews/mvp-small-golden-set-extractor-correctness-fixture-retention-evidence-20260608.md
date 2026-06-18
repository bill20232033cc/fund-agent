# MVP Small Golden Set / Extractor Correctness Slice B Fixture Retention Evidence

## Scope

Gate: `small golden set extractor correctness implementation gate` Slice B.

This artifact records offline fixture retention decisions only. It does not accept source identity, exact correctness or numeric correctness for any row. No extractor, provider/default/runtime/budget/config, production golden/readiness, quality gate, score or report golden-answer path was changed.

## Retention Decision Matrix

| fund_code | report_year | fixture_source_kind | retention decision | identity status | exact/numeric correctness allowed |
|---|---:|---|---|---|---|
| `004393` | 2024 | `synthetic` | Retain a minimal synthetic excerpt for parser/fixture-shape mechanics only. No real annual-report text is retained because matched source identity was not established in this slice. | `unmatched_synthetic`; Slice A manifest remains `pending_offline_fixture` | No. Synthetic text cannot satisfy source identity and every field uses `assertion_kind=availability_status`. |
| `110020` | 2024 | `synthetic` | Retain a minimal synthetic excerpt for parser/fixture-shape mechanics only. No real annual-report text is retained because matched source identity was not established in this slice. | `unmatched_synthetic`; Slice A manifest remains `pending_offline_fixture` | No. Synthetic text cannot satisfy source identity and every field uses `assertion_kind=availability_status`. |
| `004194` | 2024 | `synthetic` | Retain a minimal synthetic excerpt for parser/fixture-shape mechanics only. No real annual-report text is retained because matched source identity was not established in this slice. | `unmatched_synthetic`; Slice A manifest remains `pending_offline_fixture` | No. Synthetic text cannot satisfy source identity and every field uses `assertion_kind=availability_status`. |
| `006597` | 2024 | `synthetic` | Retain a minimal synthetic excerpt for parser/fixture-shape mechanics only. No real annual-report text is retained because matched source identity was not established in this slice. | `unmatched_synthetic`; Slice A manifest remains `pending_offline_fixture` | No. Synthetic text cannot satisfy source identity and every field uses `assertion_kind=availability_status`. |
| `017641` | 2024 | `synthetic` | Retain a minimal synthetic excerpt for parser/fixture-shape mechanics only. `holdings` is marked unavailable and `risk` is marked deferred policy to mirror the accepted Slice A manifest. | `unmatched_synthetic`; Slice A manifest remains `pending_offline_fixture` | No. Synthetic text cannot satisfy source identity and every field uses `assertion_kind=availability_status`. |

## Fixture Files

Created local offline fixtures under `tests/fixtures/fund/small_golden_set/`:

- `004393_2024/annual_report_excerpt.txt`
- `004393_2024/expected_fields.json`
- `110020_2024/annual_report_excerpt.txt`
- `110020_2024/expected_fields.json`
- `004194_2024/annual_report_excerpt.txt`
- `004194_2024/expected_fields.json`
- `006597_2024/annual_report_excerpt.txt`
- `006597_2024/expected_fields.json`
- `017641_2024/annual_report_excerpt.txt`
- `017641_2024/expected_fields.json`

Each `expected_fields.json` records:

- `promotion_allowed=false`
- `fallback_invocation=prohibited`
- `fixture_source_kind=synthetic`
- `source_identity.status=unmatched_synthetic`
- `exact_numeric_correctness_allowed=false`
- every field group with `status`, `assertion_kind=availability_status`, `fixture_source_kind=synthetic`, and either `source_anchor` or `unavailable_reason`

## Boundary Evidence

- Source identity: not accepted. No row has matched annual-report identity, source document id, source document title, resolved share class or identity evidence anchor.
- Correctness: not accepted. No row uses `exact`, `normalized_text` or `numeric_percent`; all row fields use `availability_status`.
- Fallback: prohibited by fixture metadata and Slice A manifest. No fallback invocation was run.
- Live/network/provider: no live LLM, endpoint/DNS/curl/socket probe, repository download, PDF read, provider call, akshare call or EID call was run.
- Promotion: `promotion_allowed=false` is preserved in every fixture and the manifest. These fixtures are not production golden/readiness inputs and do not update `reports/golden-answers/` or `reports/golden-readiness-preflight/`.

## Residual Risks

| Risk | Status | Owner |
|---|---|---|
| Real source identity remains unresolved for all five rows. | Open; Slice C must not use these synthetic fixtures for exact/numeric correctness. | Controller / future source-identity worker |
| Synthetic fixtures can only validate metadata shape and parser mechanics. | Accepted for Slice B; they cannot prove extractor correctness against annual reports. | Implementation worker |
| QDII `017641` holdings/risk policy remains incomplete. | Open; `holdings=unavailable` and `risk=deferred_policy` are carried from Slice A. | Future QDII evidence policy gate |
