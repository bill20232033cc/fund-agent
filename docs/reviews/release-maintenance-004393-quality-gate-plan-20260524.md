# Release Maintenance 004393 Quality Gate Implementation Plan

## Gate

- Work unit: `004393/2024 quality gate block root-cause investigation`
- Current phase: `release maintenance`
- Current gate: `release-maintenance candidate selection / plan-review`
- Branch: `codex/checklist-host-engine-design`
- Date: 2026-05-24
- Status: code-generation-ready plan artifact
- Handoff input: `docs/reviews/release-maintenance-004393-quality-gate-plan-handoff-20260524-080633.md`

## Goal And Success Signal

Fix the 004393/2024 quality gate block by separating same-source extraction bugs, correctness-normalization/golden decisions, and disclosure-applicability semantics.

Success means a future implementation can prove all of the following without bypassing the quality gate:

- `basic_identity` exposes comparable `management_company`, `custodian`, and `inception_date` values from annual report §2 with evidence anchors.
- `fee_schedule` extracts management fee `1.20%` and custody fee `0.20%` for 004393 from annual report §7.4.10.2 when §2 does not disclose fee rates.
- `holdings_snapshot` treats annual report §8 "all stock investment details" as a valid disclosed equity-holdings source when "top ten" wording is absent, while preserving industry-distribution evidence when disclosed.
- `share_change` can inherit parser-split A/C share-class headers from a directly adjacent §10 header table and extract 004393 A-class values without using fund-code suffix heuristics.
- Benchmark correctness no longer blocks solely because a visual PDF newline split `中债综合` into `中债综 合`; normalization and golden truth are made consistent by an explicit decision below.
- Pre-2026 missing `turnover_rate` is classified as deferred disclosure-applicability policy scope, not as a direct extraction bug fixed by this plan.

## Truth Sources And Guardrails

Current truth is limited to:

- `AGENTS.md`
- current sections of `docs/design.md`
- `docs/implementation-control.md` Startup Packet and current gate
- this work unit handoff artifact

Historical `docs/reviews/` and implementation-control archive entries that mention six-layer, Application, Runtime, or Engine boundaries are historical evidence only.

Architecture guardrails:

- Preserve current `UI -> Service -> Host -> Agent` target boundary.
- Current deterministic mainline remains UI -> Service -> `fund_agent/fund`.
- Do not create placeholder `fund_agent/host` or `fund_agent/agent` packages.
- If a future Host is introduced, it must use `dayu.host`; if an Agent execution kernel/tool loop/runner/ToolRegistry/ToolTrace is introduced, it must use `dayu.engine`. This plan does not introduce either.
- Production annual-report access must go through `FundDocumentRepository` and `FundDataExtractor`; no Service/UI/quality gate/renderer code may directly read PDF files, PDF cache paths, or concrete source helpers.
- No explicit business parameter may be passed through `extra_payload` or a free dict.

## Non-Goals

- Do not bypass, weaken, or special-case the quality gate for 004393.
- Do not derive a proxy turnover rate from trading amount, holdings, average assets, or portfolio turnover math and present it as disclosed `turnover_rate`.
- Do not treat pre-2026 non-mandatory stock-turnover absence as a 004393 direct extraction failure.
- Do not implement `turnover_rate` denominator, scoring, or quality-gate applicability policy in this work unit. That policy is a future Gateflow candidate.
- Do not change final judgment policy. Gate `block/not_run` semantics remain governed by the current Quality Gate / final judgment contract.
- Do not introduce Host/Agent runtime packages, LLM audit, Evidence Confirm execution, calculated tracking error, new external index adapters, or methodology/constituents extraction.
- Do not directly read production PDF/cache/source-helper paths outside repository/extractor boundaries.
- Do not edit README as part of this implementation. The planned source/test changes below do not require README updates.
- Do not edit golden rows by default. Golden changes require a separate controller approval artifact after S0 evidence and relevant extractor tests.
- Do not touch RR-13 duplicate source CSV cleanup, source CSV rows, unrelated golden rows, or unrelated selected-fund pool behavior.

## Direct Evidence Acquisition

Before any source or golden change, implementation must create an evidence artifact under `docs/reviews/` that records direct same-source observations for 004393/2024. The evidence artifact is a work artifact, not production code.

Required evidence route:

- Use `FundDocumentRepository.load_annual_report("004393", 2024, force_refresh=False)` or `FundDataExtractor.extract("004393", 2024, force_refresh=False)`.
- Inspect only `ParsedAnnualReport.get_section_text(...)`, `ParsedAnnualReport.tables`, and extractor output values/anchors.
- Do not open PDF files directly, inspect cache files directly, or call concrete annual-report source helpers.
- If a temporary local script is used, run it from the shell and do not commit it. If reusable test helpers are needed later, add them only in the approved test slice.

Minimum observations to record:

- §2 profile table contains `基金管理人=安信基金管理有限责任公司`, `基金托管人=中国银行股份有限公司`, and `基金合同生效日=2022 年 8 月 8 日` or parser-equivalent labels.
- §7.4.10.2 contains management fee `1.20%` and custody fee `0.20%`, with the table/page/table-id or text row locator used by the extractor.
- §8 contains both industry distribution and "all stock investment details" evidence; record exact parser headers and whether the stock-detail table row count is at least 10.
- §10 parser output splits share-change into a header table and a data table; record adjacency, page/table indexes, inherited headers, and A-class values `27,666,410.41`, `149,565,740.00`, `121,899,329.59`.
- §2 benchmark text contains the same semantic benchmark as golden, and any `中债综 合` vs `中债综合` difference is visual whitespace only.
- §8/§7/§10 inspection must not find a directly disclosed stock turnover-rate row for 004393/2024. Record this as an applicability fact, not as proof of absence by assumption.

Executable one-off evidence command pattern:

```bash
tmp_script="$(mktemp /tmp/004393-evidence-XXXXXX.py)"
cat > "$tmp_script" <<'PY'
import asyncio
from fund_agent.fund.documents import FundDocumentRepository


async def main() -> None:
    repo = FundDocumentRepository()
    report = await repo.load_annual_report("004393", 2024, force_refresh=False)
    print("SECTION §2")
    print(report.get_section_text("§2")[:4000])
    print("SECTION §7")
    print(report.get_section_text("§7")[:5000])
    print("SECTION §8")
    print(report.get_section_text("§8")[:5000])
    print("SECTION §10")
    print(report.get_section_text("§10")[:5000])
    print("TABLES")
    for ordinal, table in enumerate(report.tables):
        headers = " | ".join(str(item) for item in table.headers)
        if any(token in headers for token in ("基金管理人", "托管人", "股票投资", "行业", "份额", "A类", "C类")):
            print(
                {
                    "ordinal": ordinal,
                    "page_number": table.page_number,
                    "table_index": table.table_index,
                    "headers": table.headers,
                    "row_count": len(table.rows),
                }
            )


asyncio.run(main())
PY
uv run python "$tmp_script"
echo "exit_code=$?"
rm -f "$tmp_script"
```

The implementation report must include the exact command(s), exit code, whether repository cache was hit or refreshed, annual-report source metadata, fallback-used status, and the evidence artifact path.

The S0 evidence artifact must include this per-fact checklist, with each item marked `confirmed`, `contradicted`, or `not_observed` and backed by same-source section/table metadata:

| Fact ID | Required same-source observation | Required metadata |
|---|---|---|
| `E-identity-company` | §2 profile table contains `基金管理人=安信基金管理有限责任公司`. | section, table/page/index or text locator, source, cache/fallback status |
| `E-identity-custodian` | §2 profile table contains `基金托管人=中国银行股份有限公司`. | section, table/page/index or text locator, source, cache/fallback status |
| `E-identity-inception` | §2 profile table contains `基金合同生效日=2022 年 8 月 8 日` or parser-equivalent date text. | section, table/page/index or text locator, source, cache/fallback status |
| `E-fee-management` | §7.4.10.2 contains management fee `1.20%`. | section, table/page/index or text locator, source, cache/fallback status |
| `E-fee-custody` | §7.4.10.2 contains custody fee `0.20%`. | section, table/page/index or text locator, source, cache/fallback status |
| `E-holdings-stock-details` | §8 contains an all-stock-investment-details table with stock code/name/quantity/fair value/net-asset-ratio semantics and at least 10 rows. | section, page/index, headers, row count, source, cache/fallback status |
| `E-holdings-industry` | §8 contains industry-distribution evidence independent of stock-holdings details. | section, page/index, headers, row count, source, cache/fallback status |
| `E-share-split-header` | §10 parser output has an adjacent A/C share-class header table and share-change data table. | section, page/index pair, table ordinals, inherited headers, source, cache/fallback status |
| `E-share-values-a` | §10 same-source data supports A-class beginning/ending/net-change values `27,666,410.41`, `149,565,740.00`, `121,899,329.59`. | section, page/index pair, selected column reason, source, cache/fallback status |
| `E-share-class-identity` | §2 same-source text/table explicitly identifies current fund/share class as A class; no fund-code suffix inference. | section, table/page/index or text locator, source, cache/fallback status |
| `E-benchmark-whitespace` | §2 benchmark text is semantically equal to golden and any `中债综 合`/`中债综合` mismatch is visual whitespace. | section, table/page/index or text locator, source, cache/fallback status |
| `E-turnover-deferred` | No directly disclosed stock turnover-rate row was observed in §8/§7/§10 inspection. | inspected sections, locator summary, source, cache/fallback status; classify as deferred applicability only |

## Current Code Evidence

Current code shape observed during planning:

- `fund_agent/fund/extraction_snapshot.py` already whitelists `basic_identity.management_company`, `basic_identity.custodian`, and `basic_identity.inception_date` as comparable subfields.
- `fund_agent/fund/extractors/profile.py` currently builds `basic_identity` from `fund_name`, `fund_code`, `fund_category`, `fund_scale`, and `fund_manager`, so the whitelisted comparable fields remain unavailable.
- `fund_agent/fund/extractors/profile.py` currently extracts `management_fee` and `custody_fee` only through §2 field/table labels.
- `fund_agent/fund/extractors/holdings_share_change.py` currently looks for top-holdings keywords and industry-distribution keywords independently, but fails the whole `holdings_snapshot` if top-holdings table is absent.
- `fund_agent/fund/extractors/holdings_share_change.py` currently rejects multi-column share-change tables unless there is a single value column or exact fund-code header match.
- `fund_agent/fund/extraction_score.py` currently treats `turnover_rate` as a P1 field for coverage/fund-quality missing-rate calculations for active funds.
- `reports/golden-answers/golden-answer-prefill-reviewed.md` already has 004393 basic identity rows for the three comparable fields, skips `fee_schedule`, skips `turnover_rate`, skips `holdings_snapshot`, and includes share-change rows.

## Affected Files And Ownership Boundaries

Future implementation may touch only these areas, by slice:

- Agent/Fund extractors:
  - `fund_agent/fund/extractors/profile.py`
  - `fund_agent/fund/extractors/holdings_share_change.py`
- Agent/Fund scoring and gate:
  - `fund_agent/fund/extraction_snapshot.py` only if snapshot must expose holdings status/source metadata or new comparable fields
  - `fund_agent/fund/extraction_score.py`
  - `fund_agent/fund/quality_gate.py` only if holdings status/source must be validated or reported by the gate
  - `fund_agent/fund/quality_gate_integration.py` only if bundle-to-score integration must pass holdings status/source metadata
- Golden/correctness data, only after the S4 controller approval artifact exists:
  - `reports/golden-answers/golden-answer-prefill-reviewed.md`
  - `reports/golden-answers/golden-answer.json`
- Tests:
  - `tests/fund/extractors/test_profile.py`
  - `tests/fund/extractors/test_holdings_share_change.py`
  - `tests/fund/test_extraction_snapshot.py`
  - `tests/fund/test_extraction_score.py`
  - `tests/fund/test_quality_gate.py`
  - `tests/fund/test_quality_gate_integration.py` if integration behavior changes
  - one focused integration/real-repository test only if it can use existing repository interfaces and does not require direct PDF/cache access

Forbidden for this work unit:

- `fund_agent/host/`
- `fund_agent/agent/`
- direct annual-report source helpers except tests that already own source orchestration behavior
- source CSV files
- runtime/generated report outputs other than validation scratch output ignored by git
- README unless a later controller decision explicitly expands docs scope

## Contract And Schema Decisions

### `basic_identity`

Decision: schema already accepts the desired comparable subfields; implementation is extractor completion, not a new public schema.

Required behavior:

- Add configured table/text labels for `management_company`, `custodian`, and `inception_date` in `profile.py`.
- Populate these keys in `basic_identity.value`.
- Include field-level anchors for each extracted value.
- Keep existing keys and classification behavior unchanged.

Tests must prove:

- Table labels such as `基金管理人`, `基金托管人`, and `基金合同生效日` map to the three fields.
- `build_snapshot_records()` emits comparable values for those keys when present.
- Missing optional labels do not make `basic_identity` missing if existing identity/classification fields are present.

### `fee_schedule`

Decision: §7.4.10.2 fallback is extractor behavior. It also requires golden/correctness fixture updates only after direct evidence confirms the annual-report values and anchors.

Required behavior:

- Prefer direct §2 fee labels when available.
- If either `management_fee` or `custody_fee` is missing from §2, search §7.4.10.2 fee disclosure tables/text.
- Extract management fee and custody fee separately; partial direct extraction should keep the missing side missing only if fallback cannot find it.
- Anchors must point to §7.4.10.2 for fallback-derived values.
- Do not normalize the user-visible fee value beyond trimming parser whitespace and preserving `%`.

Tests must prove:

- §2-only fixture still passes unchanged.
- §7.4.10.2 fallback extracts `1.20%` and `0.20%`.
- If §2 has management fee but §7.4.10.2 has custody fee, output combines both with separate anchors.
- No fee table means `fee_schedule` remains missing with a clear note.

Golden decision:

- Add 004393 `fee_schedule.management_fee=1.20%` and `fee_schedule.custody_fee=0.20%` only in S4 after extractor tests pass, direct evidence is recorded, and controller approval artifact lists the rows.
- If direct evidence shows parser value text includes Chinese explanatory prose, normalize extractor output to the scalar rate and golden to the scalar rate.

### `holdings_snapshot`

Decision: "all stock investment details" is a valid disclosed holdings source for the top-holdings payload when no explicit top-ten table is found. This is not a 004393 special case; it is a semantic table-kind fallback within annual report §8.

Required behavior:

- Rename internal semantics if useful from "top_holdings only" to "stock_holdings source"; preserve existing output key `top_holdings` for compatibility unless controller approves a schema change.
- Search order:
  1. explicit top-ten/heavy-holdings table
  2. all-stock-investment-details table with stock code/name/quantity/fair value/net-asset-ratio semantics
- If all-stock table has more than 10 rows, output the first 10 rows under `top_holdings` and include required machine-readable stock-holdings source/status metadata.
- Preserve industry distribution independently. Industry distribution alone may make the extractor return industry data, but it must not satisfy stock-holdings coverage in snapshot/score/gate semantics.
- Do not silently equate industry distribution with top holdings.

Schema decision:

- Minimal machine-readable contract: keep `top_holdings` and `industry_distribution` keys, and add required status/source keys whenever `holdings_snapshot` is emitted:
  - `top_holdings_status`: `direct_top_ten` / `direct_all_stock_details` / `missing`
  - `top_holdings_source`: `top_ten` / `all_stock_investment_details` / `none`
  - `industry_distribution_status`: existing `direct` / `missing`
- `top_holdings_status` and `top_holdings_source` are not optional metadata. Snapshot/score/gate behavior must read them if the slice claims quality-gate stock-holdings coverage.
- A `holdings_snapshot` with `industry_distribution_status="direct"` and `top_holdings_status="missing"` must not count as stock-holdings coverage. It may count only as industry-distribution evidence if current scoring has a separate concept for that subcoverage.
- If implementation decides snapshot/score/gate integration is too broad for this work unit, S2 must explicitly restrict itself to extractor-visible behavior and unit tests, and the completion report must not claim quality-gate holdings coverage is fixed.
- If implementation decides these keys are too broad, it must stop for controller review before changing output schema differently.

Tests must prove:

- Existing top-ten fixture outputs `top_holdings_status=direct_top_ten` and `top_holdings_source=top_ten`.
- All-stock details fixture outputs first 10 rows and anchors to that table.
- Industry distribution alone does not fabricate `top_holdings` and does not satisfy stock-holdings coverage through snapshot/score/gate if S2 claims gate coverage.
- Holdings snapshot remains traceable with anchors for every extracted table.

### `share_change`

Decision: support parser-split continuation headers only when the previous table is a same-section, directly adjacent, header-only or header-dominant share-class table for the same logical §10 share-change disclosure. Do not use fund-code suffix inference.

Required behavior:

- Introduce a module-level helper that builds a logical share-change table candidate from adjacent parsed tables.
- Continuation is allowed only when:
  - both tables are in or anchored to §10 by page/order evidence;
  - the header table contains share-class labels such as A类/C类 and no unrelated numeric data rows;
  - the following data table contains share-change row labels such as 期初、期末、净变动 or 本期申购赎回净额;
  - combined column count can map headers to row values deterministically.
- Column selection priority remains:
  1. exact fund-code header match if present;
  2. single value column;
  3. strict share-class match only if same-source §2 report evidence directly identifies current fund as that share class;
  4. otherwise fail closed.
- For 004393, the plan expects A-class values only after direct same-source evidence confirms the current share class. Preferred narrow route: inside `holdings_share_change.py`, use `ParsedAnnualReport.get_section_text("§2")` or §2 parsed table evidence to identify explicit `安信企业价值优选混合A` / `A类` identity, then select the A-class column. This route must fail closed when §2 does not explicitly identify A/C class.
- If implementation instead passes profile-derived identity through `fund_agent/fund/data_extractor.py` or another extractor orchestration boundary, that is expanded S2 scope. The implementation agent must stop for controller review before adding that dependency.
- It must not infer A/C from the last digit of the fund code.

Schema decision:

- Preserve existing `share_change` keys:
  - `beginning_share`
  - `ending_share`
  - `net_change`
  - `share_class_column`
  - `share_class_selection_reason`
- Add `share_class_header_source="continued_previous_table"` or encode this in `share_class_selection_reason` such as `continued_header_share_class_match`.
- Anchor should identify the data table and include enough note/table metadata to trace the inherited header table. If the current `EvidenceAnchor` cannot represent two table IDs, include the inherited table ID in `note`; do not change `EvidenceAnchor` schema without controller approval.

Tests must prove:

- Existing single-column and exact-code-header cases continue to pass.
- Split header/data tables extract the A-class values only when same-source §2 text/table evidence explicitly identifies A class.
- Split header/data tables fail closed when A/C class cannot be resolved.
- Split header/data tables fail closed when only fund-code suffix evidence would identify A/C class.
- Non-adjacent or unrelated previous tables do not influence extraction.
- Tables containing other fund-code headers still fail closed unless exact current fund code matches.

### Benchmark Correctness Normalization

Decision: fix this primarily in correctness normalization, and update golden only if direct evidence confirms the current golden text contains an artificial space that should not be preserved as semantic truth.

Rationale:

- Existing extractor already has benchmark newline normalization in `profile.py`.
- The mismatch described for `中债综合` vs `中债综 合` is a visual PDF whitespace artifact, not a semantic benchmark change.
- Correctness comparison should normalize intra-Chinese visual whitespace for benchmark fields so equivalent text does not block.

Required behavior:

- Add field-aware correctness normalization for `benchmark.benchmark_name` and `benchmark.benchmark_text`.
- For benchmark fields only, remove whitespace between adjacent Chinese characters when both sides are not ASCII word boundaries.
- Keep existing ASCII word spacing behavior for English benchmark names.
- Do not apply aggressive whitespace deletion to all fields; it may hide real differences in names, codes, or dates.

Golden decision:

- If direct evidence shows annual report semantic text is `中债综合（全价）指数收益率`, update 004393 golden benchmark to that semantic text only through S4 row-level controller approval.
- If direct evidence shows parser/golden intentionally preserves a visual space elsewhere, normalization may be sufficient and golden can remain unchanged. The implementation report must state the decision.

Tests must prove:

- `中债综 合` and `中债综合` match for benchmark correctness.
- English token spacing remains meaningful.
- Non-benchmark fields do not get this normalization unless explicitly approved.

### `turnover_rate` Disclosure Applicability

Decision: split disclosure-applicability and denominator policy out of the current implementation scope.

Current work-unit behavior:

- S0 may record that §8/§7/§10 inspection did not observe a directly disclosed 004393/2024 stock turnover-rate row.
- S5 may classify any remaining 004393 `turnover_rate` quality-gate block as `deferred_applicability_policy`.
- No source, test, score, denominator, quality-gate, or golden behavior may be changed for `turnover_rate` in this plan.
- Do not derive a proxy turnover rate from trading amount, holdings, average assets, or portfolio turnover math.

Future candidate:

- Candidate name: `turnover_rate disclosure applicability / quality gate denominator policy`.
- Future plan must independently define status vocabulary, extraction/snapshot/score/gate ownership, denominator behavior, 2026+ conservative handling, tests, and regulatory evidence.
- That future candidate must receive its own Gateflow plan/review before any `turnover_rate` source/test/config/runtime behavior changes.

## Implementation Slices

### S0 - Evidence Artifact

Objective: acquire and record direct evidence before code changes.

Allowed files:

- New `docs/reviews/release-maintenance-004393-quality-gate-evidence-YYYYMMDD.md`

Allowed changes:

- Record repository/extractor commands and observations listed in "Direct Evidence Acquisition".
- Record exact command text and command exit code.
- Record annual-report source metadata, whether `metadata.fallback_used` is true/false when available, and whether the repository load used cached content or refreshed content when observable through repository/extractor metadata or logs.
- Complete the per-fact checklist from "Direct Evidence Acquisition"; every required fact must be `confirmed`, `contradicted`, or `not_observed`.
- No source, test, config, README, runtime output, source CSV, or golden data changes.

Validation:

```bash
tmp_script="$(mktemp /tmp/004393-evidence-XXXXXX.py)"
cat > "$tmp_script" <<'PY'
import asyncio
from fund_agent.fund.documents import FundDocumentRepository


async def main() -> None:
    repo = FundDocumentRepository()
    report = await repo.load_annual_report("004393", 2024, force_refresh=False)
    print("SECTION §2")
    print(report.get_section_text("§2")[:4000])
    print("SECTION §7")
    print(report.get_section_text("§7")[:5000])
    print("SECTION §8")
    print(report.get_section_text("§8")[:5000])
    print("SECTION §10")
    print(report.get_section_text("§10")[:5000])
    print("TABLES")
    for ordinal, table in enumerate(report.tables):
        headers = " | ".join(str(item) for item in table.headers)
        if any(token in headers for token in ("基金管理人", "托管人", "股票投资", "行业", "份额", "A类", "C类")):
            print(
                {
                    "ordinal": ordinal,
                    "page_number": table.page_number,
                    "table_index": table.table_index,
                    "headers": table.headers,
                    "row_count": len(table.rows),
                }
            )


asyncio.run(main())
PY
uv run python "$tmp_script"
evidence_exit_code=$?
echo "exit_code=$evidence_exit_code"
rm -f "$tmp_script"
test "$evidence_exit_code" -eq 0
git diff --check
```

Completion signal:

- Evidence artifact exists, includes the exact command, `exit_code=0`, source metadata, fallback/cache status, and confirms or rejects each candidate fact.

Stop conditions:

- Stop if repository cannot load 004393/2024 through `FundDocumentRepository`.
- Stop if direct evidence contradicts the handoff facts.
- Stop if evidence requires direct PDF/cache/source-helper reads to proceed.

### S1 - P0 Extraction And Comparable Fields

Objective: close direct P0 extraction gaps for `basic_identity` and `fee_schedule`.

Prerequisite:

- S0 evidence accepted.

Allowed files:

- `fund_agent/fund/extractors/profile.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py` only if comparable/scoring expectations need focused regression

Exact changes:

- Add profile labels/rules for `management_company`, `custodian`, and `inception_date`.
- Populate those keys in `_build_basic_identity()`.
- Add §7.4.10.2 fee fallback helper(s) in `profile.py`; keep helpers module-level, no nested functions.
- Preserve existing `benchmark`, `index_profile`, and classification call order.
- Add Chinese docstrings for all new helpers and template chapter references where fund-analysis logic is involved.

Required tests:

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
uv run ruff check fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
git diff --check
```

Expected assertions:

- Basic identity table fixture includes the three new fields and anchors.
- Snapshot comparable values include those fields when present.
- Fee fallback extracts `1.20%` and `0.20%` from a §7.4.10.2 fixture.
- Missing §7.4.10.2 fallback does not create fake fees.

Stop conditions:

- Stop if fee fallback needs source-specific PDF metadata outside `ParsedAnnualReport`.
- Stop if adding the basic identity fields requires changing `StructuredFundDataBundle` schema rather than only the dict value.

### S2 - P1 Extraction And Benchmark Correctness

Objective: close `holdings_snapshot`, `share_change`, and benchmark-correctness blockers.

Prerequisite:

- S0 evidence accepted.
- S1 completed or explicitly split by controller.

Allowed files:

- `fund_agent/fund/extractors/holdings_share_change.py`
- `fund_agent/fund/extraction_snapshot.py` only if required to propagate mandatory `top_holdings_status` / `top_holdings_source`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py` only if S2 claims quality-gate stock-holdings coverage and must prevent industry-only coverage from satisfying the gate
- `tests/fund/extractors/test_holdings_share_change.py`
- `tests/fund/test_extraction_snapshot.py` if snapshot status/source propagation is implemented
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_quality_gate.py` only for benchmark mismatch path if quality gate behavior is directly affected

Exact changes:

- Add all-stock-details semantic table detection for §8 holdings.
- Emit required `top_holdings_status` and `top_holdings_source` for `holdings_snapshot`; ensure industry-only evidence does not satisfy stock-holdings coverage if S2 claims snapshot/score/gate coverage.
- Add adjacent-table share-change continuation logic with fail-closed ambiguity handling.
- Implement the preferred same-source A/C identity route in `holdings_share_change.py` using `ParsedAnnualReport.get_section_text("§2")` or §2 parsed table evidence. Do not pass profile-derived identity through `data_extractor.py` unless controller explicitly approves expanded S2 scope.
- Add benchmark-field-only correctness normalization in `extraction_score.py`.
- Do not change fee/basic identity logic in this slice except to resolve mechanical conflicts from S1.

Required tests:

```bash
uv run pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
git diff --check
```

Expected assertions:

- All-stock details works as a stock-holdings source.
- Industry distribution continuation/status is preserved.
- Industry-only evidence leaves `top_holdings_status="missing"` and does not satisfy stock-holdings coverage in snapshot/score/gate if S2 claims gate coverage.
- Split share-change header/data tables extract A-class 004393-like values only with direct class evidence.
- Ambiguous split tables fail closed.
- A/C selection fails closed when only fund-code suffix evidence is available.
- Benchmark correctness matches `中债综 合` vs `中债综合` only for benchmark fields.

Stop conditions:

- Stop if resolving A/C share class requires fund-code suffix inference.
- Stop if resolving A/C share class requires profile-derived identity orchestration through `data_extractor.py`; controller must explicitly expand S2 scope first.
- Stop if holdings output schema needs a breaking rename rather than additive metadata.
- Stop if score/gate changes needed for holdings coverage are larger than required status/source propagation; in that case restrict S2 to extractor-visible behavior and do not claim gate coverage.
- Stop if benchmark normalization would need to become global across all fields.

### S3 - Deferred Turnover Disclosure Applicability Candidate

Objective: keep `turnover_rate` denominator/applicability policy outside this work unit while preserving explicit residual-risk classification.

Prerequisite:

- None for implementation. This is a deferred candidate record only.

Allowed files:

- None in current implementation scope.

Exact changes:

- Do not implement denominator, scoring, quality-gate, extractor, snapshot, or golden changes for `turnover_rate`.
- If 004393 still blocks only on missing `turnover_rate` after S1/S2/S4-approved changes, classify the remaining block as `deferred_applicability_policy` in the implementation report.
- Open or reference a future Gateflow candidate named `turnover_rate disclosure applicability / quality gate denominator policy` if controller asks for tracking.

Required tests:

```bash
git diff --check
```

Expected assertions:

- No code/test/golden diff exists for `turnover_rate`.
- Implementation report classifies any remaining 004393 turnover block as deferred policy scope, not a fixed direct extraction bug.

Stop conditions:

- Stop if a reviewer/controller asks implementation to change `turnover_rate` behavior under this plan; a new plan/review is required first.

### S4 - Golden And Correctness Fixture Update

Objective: define the controller approval gate for any strict golden answer change.

Prerequisite:

- S1/S2 completed and tests pass.
- Direct evidence artifact confirms final values.
- Controller explicitly approves golden changes in a separate approval artifact after reviewing S0 evidence and relevant extractor/correctness test results.

Default state:

- No golden row may be changed by default.
- No `reports/golden-answers/` file may be edited until the approval artifact exists.
- Holdings golden expansion is deferred by default.
- Turnover applicability note/golden changes are deferred by default.

Required approval artifact:

- Path pattern: `docs/reviews/release-maintenance-004393-quality-gate-golden-approval-YYYYMMDD.md`.
- Must list each proposed row with `fund`, `field`, `subfield`, current value, new value, direct evidence locator, and the exact build command.
- Must identify whether the proposed change is a semantic truth correction, a newly evidenced field, or a fixture-format rebuild.
- Must state that unrelated golden rows are out of scope.

Allowed files:

- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- `tests/fund/test_golden_answer.py` only if schema validation needs fixture coverage
- `tests/fund/test_golden_prefill.py` only if prefill mapping needs updates

Exact changes:

- Apply only rows explicitly listed in the controller approval artifact.
- Candidate fee rows may include 004393 `fee_schedule.management_fee=1.20%` and `fee_schedule.custody_fee=0.20%` only if approved row by row.
- Candidate benchmark row may change from `中债综 合` to `中债综合` only if approved row by row as a semantic whitespace correction.
- Do not add `turnover_rate` golden row or applicability note in this work unit unless a later independent turnover plan is accepted.
- Do not add `holdings_snapshot` golden row in this work unit unless the approval artifact explicitly lists the row and evidence. Default is deferred.
- Rebuild strict JSON using the exact build command named in the approval artifact.

Required tests/commands:

```bash
uv run python -m fund_agent.fund.golden_answer reports/golden-answers/golden-answer-prefill-reviewed.md reports/golden-answers/golden-answer.json
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_prefill.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
uv run ruff check tests/fund/test_golden_answer.py tests/fund/test_golden_prefill.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
git diff --check
```

If the module CLI above is not the current build entry point, stop before editing golden and ask the controller to update the approval artifact with the current build command discovered from repository-owned commands/tests.

Stop conditions:

- Stop if the approval artifact is absent.
- Stop if a row is not explicitly listed with fund/field/subfield/current/new/evidence/build command.
- Stop if golden source values are not directly evidenced.
- Stop if strict JSON builder rejects an applicability-only skipped row and changing builder semantics would broaden scope.
- Stop if golden changes would require editing unrelated rows.

### S5 - End-To-End Quality Gate Verification

Objective: prove the root-cause fixes resolve 004393 without weakening gate semantics.

Prerequisite:

- S1/S2 completed.
- S3 recorded as deferred with future candidate owner/scope.
- S4 completed if golden changes are approved.

Allowed files:

- New implementation artifact under `docs/reviews/`
- No additional source/test/golden changes unless a preceding slice left an accepted fix gap.

Required commands:

```bash
uv run pytest tests/fund/extractors/test_profile.py tests/fund/extractors/test_holdings_share_change.py -q
uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
uv run pytest -q
uv run ruff check .
uv lock --check
git diff --check
```

Required 004393 smoke, using repository/extractor boundaries:

```bash
uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block
```

Expected smoke result:

- If S4 golden changes are approved and aligned, `analyze` should not block for S1/S2 root causes.
- If the only remaining original block is `turnover_rate`, classify it as `deferred_applicability_policy`; do not implement denominator/gate policy under this plan.
- If any residual block remains, the implementation report must classify it as:
  - accepted real product/data issue,
  - remaining extraction bug,
  - golden/correctness fixture issue,
  - deferred disclosure applicability policy,
  - or unrelated quality gate rule.

Stop conditions:

- Stop if full suite or ruff fails for reasons not attributable to this work unit.
- Stop if `analyze` still blocks on a root cause claimed fixed by the slice.
- Stop if resolving the remaining block requires broad policy changes outside this plan.

## Validation Matrix

Minimum validation before code review:

```bash
uv run pytest tests/fund/extractors/test_profile.py -q
uv run pytest tests/fund/extractors/test_holdings_share_change.py -q
uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py -q
uv run pytest -q
uv run ruff check .
uv lock --check
git diff --check
```

Minimum 004393 smoke before claiming release-maintenance readiness:

```bash
uv run fund-analysis analyze 004393 --report-year 2024 --quality-gate-policy block
```

Do not claim readiness if:

- any command is skipped without a reason;
- a command fails and no fix/owner is assigned;
- 004393 smoke is not run and no explicit blocker is recorded.

## Review Gates

Plan review must challenge:

- Whether S3 is fully split out and no turnover denominator/gate policy remains in current implementation scope.
- Whether holdings output schema extension is minimal and backward-compatible.
- Whether holdings status/source is required and machine-readable enough for any claimed snapshot/score/gate coverage.
- Whether share-change continuation can be implemented without parser-artifact overfitting.
- Whether share-change A/C selection uses same-source §2 evidence and fails closed without fund-code suffix inference.
- Whether benchmark normalization belongs only in correctness comparison or also extractor output/golden.
- Whether golden updates are blocked behind the required row-level controller approval artifact.
- Whether all annual-report evidence access stays inside repository/extractor boundaries.

Code review must inspect:

- No direct PDF/cache/source helper reads outside `fund_agent/fund/documents`.
- No 004393 hardcoding except test fixtures naming the regression case.
- No fund-code suffix inference for share class.
- No derived turnover proxy.
- No Host/Agent placeholder package creation.
- New functions have Chinese docstrings and relevant template chapter references.
- Tests cover failure paths, not only happy paths.

## Residual Risks

- Parser table shapes may vary across annual reports. Mitigation: implement semantic adjacency/headers and fail closed on ambiguity.
- §7.4.10.2 fee table wording may vary. Mitigation: use label/row semantics, not one exact string.
- Benchmark visual whitespace normalization can hide real text changes if applied too broadly. Mitigation: restrict to benchmark correctness fields.
- Turnover applicability depends on report year and disclosure regime. Mitigation: defer denominator/gate policy to a separate Gateflow candidate and classify any remaining 004393 turnover block as `deferred_applicability_policy`.
- `holdings_snapshot` currently is not a strict golden comparable field. Extraction can be verified by unit/integration tests first; correctness oracle expansion should be a separate explicit decision if needed.
- Real 004393 smoke may still block on unrelated quality gate findings. Mitigation: implementation report must classify each remaining issue by root cause.

## Blocking Questions For Controller

No blocking question prevents S0/S1/S2 planning handoff.

S3 turnover disclosure applicability is deferred to a follow-up Gateflow candidate and is not open for current implementation.

Controller decision required before S4:

- Approve golden changes after evidence and extractor tests in a row-level approval artifact listing fund/field/subfield/current/new/evidence/build command. Without that artifact, S4 performs no golden edits.

## Completion Report Format

Each implementation agent report must include:

- Gate and slice ID.
- Approved plan path.
- Evidence artifact path and direct evidence summary.
- Changed files.
- Exact contract decisions implemented.
- Explicit non-goals preserved.
- Tests and commands run, with pass/fail summary.
- 004393 smoke result if slice reaches S5 or changes quality-gate-affecting behavior.
- Remaining quality gate issues for 004393, classified by root cause.
- Residual risks, each classified as fixed now, covered by later approved slice, deferred to later work unit, tracked by issue/artifact, or requiring user/controller decision.
- Stop status: `ready_for_code_review`, `blocked`, or `needs_controller_decision`.
