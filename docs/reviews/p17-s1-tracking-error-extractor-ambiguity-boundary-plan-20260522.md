# P17-S1 tracking_error extractor ambiguity boundary plan（2026-05-22）

## Verdict

`READY_FOR_P17-S1_PLAN_REVIEW`

本计划建议进入一个窄口径 Fund Capability 实现切片：只加固 `tracking_error` 直接披露抽取器的歧义边界、缺失 note 语义和 focused tests。该切片基于 design alignment reconciliation 后的 `docs/design.md` v2.1 与当前 `main` accepted commits `1bd3677`、`aa7b30f`，不添加 production `tracking_error` golden rows，不扩大数据来源，不计算跟踪误差，不触碰 Service/UI/Engine/renderer/source orchestration，也不修改设计/总控真源。

## Gate

| Item | State |
|---|---|
| Gate | `P17-S1 tracking_error extractor ambiguity boundary plan-review` |
| Artifact | `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md` |
| Role | AgentCodex specialist planning worker, not controller |
| Branch baseline | `main`, local ahead of `origin/main` by accepted docs-only commits `1bd3677` and `aa7b30f` |
| Design baseline | `docs/design.md` v2.1 after design alignment reconciliation |
| Implementation target | Fund Capability `performance.py` tracking-error extractor hardening |

## Inputs Read

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/design-alignment-review-controller-judgment-20260522.md`
- `docs/reviews/post-p16-follow-up-planning-20260522.md`
- `docs/reviews/post-p16-follow-up-plan-review-controller-judgment-20260522.md`
- `fund_agent/fund/extractors/performance.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/data_extractor.py`
- `tests/fund/extractors/test_performance.py`
- Existing focused fixtures under `tests/fixtures/fund/extractors/performance/`

Explicitly not read and not cited:

- `docs/design0522.md`
- `docs/implementation-control0522.md`
- `docs/repo-audit-20260521.md`

## Non-goals

- No source code, test, README, golden, CSV, RR-13, design truth, control truth, commit, branch, PR, issue, push, or external-state edits in this plan gate.
- No production `tracking_error` golden rows for `001548`, `004194`, `005313`, `017644`, `019918`, `019923`.
- No calculated tracking error, external index adapter, index series source, methodology extraction, constituents extraction, QDII subtype redesign, E1-E3, Evidence Confirm, LLM writing, Dayu runtime, Host, Engine, tool loop, source CSV mutation, or `extra_payload` for explicit parameters.
- No direct production PDF/cache/source-helper access. Annual-report access must remain through `FundDocumentRepository` / `FundDataExtractor`.

## Design-Boundary Checklist

This plan must satisfy `docs/design.md` §11:

- §1.3 non-goals are not violated: the slice does not introduce all-market comparison, real-time behavior detection, self-calculated thermometer values, portfolio management, buy/sell or position recommendations, or external Dayu Host/Engine/tool-loop runtime dependency.
- UI / Service / Capability / Runtime / Engine boundaries are preserved: implementation is limited to Fund Capability extractor behavior plus focused extractor tests; UI, Service orchestration, Runtime, Engine, renderer, quality gate, and source orchestration are not implementation targets.
- Production annual-report access remains through `FundDocumentRepository` / `FundDataExtractor`; no direct PDF cache, source adapter, downloader, or concrete fallback helper call is added outside the document repository boundary.
- The slice does not introduce external Dayu runtime, LLM writing, Evidence Confirm execution, calculated tracking error, external index adapters, methodology/constituents extraction, or explicit parameters hidden in `extra_payload`.
- Success signals are verifiable by deterministic tests, ruff, and `git diff --check`; they assert direct-disclosure semantics and blocker notes without incentivizing unsupported evidence acceptance.
- Implementation scope remains unchanged: no production golden rows, no external data, no calculated tracking error, and no promotion of blocked `tracking_error` candidates without reviewed direct observed disclosure evidence.

## Current Code Facts

Design and control facts:

- `docs/design.md:61-73` defines the deterministic chain: `FundDataExtractor.extract()` calls `FundDocumentRepository.load_annual_report()` and then chapter extractors.
- `docs/design.md:420-429` states fund document access is unified through `FundDocumentRepository`; source orchestration/cache/PDF adapters are document-layer internals.
- `docs/design.md:451-465` places `performance.py` in the Fund Capability structured extractor layer and lists direct-disclosed `tracking_error` as `§3/§2` extraction.
- `docs/design.md:559-580` makes `index_profile` and `tracking_error` conditional P1 fields for index/enhanced-index and requires production `tracking_error` golden rows only after reviewed direct observed disclosure evidence.
- `docs/design.md:790-803` records fail-closed source failure taxonomy and the P13/P14/P15 staged direct-disclosure decision.
- `docs/design.md:821-829` requires future plan reviews to check design boundaries, annual-report access boundaries, forbidden runtime/data expansions, and verifiable success signals.
- `docs/implementation-control.md:17-20` sets current gate to P17-S1 plan-review; `docs/implementation-control.md:72-75` records P17-S1 note/early-return/multi-match constraints and preserves P15/P16 no-direct-disclosure blockers.
- `docs/implementation-control.md:128-142` records P15/P16 history: `001548` and five enhanced-index candidates remain blocked for production `tracking_error`, while P16 only accepted `index_profile` benchmark-context rows.
- `docs/reviews/design-alignment-review-controller-judgment-20260522.md` accepts `docs/design.md` v2.1 as the current design truth, keeps P17-S1 as the next gate, rejects broad `tracking_error coverage >= 90%` targets unless restricted to direct observed disclosure evidence, and requires P17-S1 plan/review to include the design-boundary checklist.

Extractor facts:

- `fund_agent/fund/data_extractor.py:113-193` shows `FundDataExtractor` loads annual reports via repository protocol/default `FundDocumentRepository`, then calls `extract_performance(report)`.
- `fund_agent/fund/data_extractor.py:224-249` applies fund-type applicability after extraction; non-index types get missing notes, while `index_fund` / `enhanced_index` preserve extractor output.
- `fund_agent/fund/extractors/models.py:37-51` defines missing-path semantics through `ExtractedField.value=None`, `anchors=()`, `extraction_mode="missing"`, and `note`.
- `fund_agent/fund/extractors/models.py:133-170` defines success-path `TrackingErrorValue` fields, including `source_type` and `calculation_method`; these fields do not exist when `value=None`.
- `fund_agent/fund/extractors/performance.py:344-398` is the top-level tracking-error extractor. It currently runs `_has_ambiguous_tracking_error_text(report)` before table/text extraction; this is the first broad early-return location.
- `fund_agent/fund/extractors/performance.py:357-364` reuses `"tracking_error_ambiguous"` for both line-level actual/target ambiguity and table/text inconsistency.
- `fund_agent/fund/extractors/performance.py:401-424` returns `None` for table/text parse failure or inconsistent values, which is then mapped to `"tracking_error_ambiguous"`.
- `fund_agent/fund/extractors/performance.py:427-469` table extraction silently returns `None` when multiple direct-looking table matches exist (`len(matches) > 1`) or when target/control context is skipped.
- `fund_agent/fund/extractors/performance.py:472-514` text extraction silently returns `None` when multiple text matches exist and also has a second early-return at `fund_agent/fund/extractors/performance.py:494-496` for a line that has both target/control and actual signal.
- `fund_agent/fund/extractors/performance.py:545-564` excludes headers containing `标准差`, protecting standard-deviation columns from direct tracking-error extraction.
- `fund_agent/fund/extractors/performance.py:587-601` currently treats all target/control keywords as one negative/ambiguous class.
- `fund_agent/fund/extractors/performance.py:604-610` starts the actual-signal helper used to classify mixed actual/target lines.

Test facts:

- `tests/fund/extractors/test_performance.py:163-189` covers valid direct text disclosure.
- `tests/fund/extractors/test_performance.py:192-211` covers target/limit text not becoming observed, but does not assert a precise note.
- `tests/fund/extractors/test_performance.py:214-233` covers mixed actual/target ambiguity and expects `"tracking_error_ambiguous"`.
- `tests/fund/extractors/test_performance.py:236-254` covers standard-deviation-only text not becoming tracking error, but does not assert a precise note.
- `tests/fund/extractors/test_performance.py:257-284` covers valid direct table disclosure.
- `tests/fund/extractors/test_performance.py:287-317` covers consistent table/text double disclosure and keeps table anchor.
- `tests/fund/extractors/test_performance.py:320-349` covers table/text conflicting values and currently expects `"tracking_error_ambiguous"`.

## Implementation Slices

### Slice 1: Introduce explicit blocker semantics inside performance extractor

Owned files:

- `fund_agent/fund/extractors/performance.py`

No-go files:

- `fund_agent/fund/documents/**`
- `fund_agent/fund/documents/adapters/**`
- `fund_agent/fund/data/nav_data.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/services/**`
- `fund_agent/ui/**`
- `reports/golden-answers/**`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/code_20260519.csv`

Implementation shape:

1. Add a small private classification result type in `performance.py`, for example `_TrackingErrorExtractionOutcome`, carrying `match: _MatchedTrackingError | None` and `blocker_note: str | None`.
2. Keep helper definitions module-level, with Chinese docstrings. Do not use nested functions/classes.
3. Replace ambiguous boolean / bare `None` paths with deterministic notes. Recommended note constants:
   - `tracking_error_target_or_limit`
   - `tracking_error_manager_narrative`
   - `tracking_error_benchmark_only`
   - `tracking_error_standard_deviation_only`
   - `tracking_error_mixed_actual_and_target`
   - `tracking_error_unparseable`
   - `tracking_error_incomplete_anchor`
   - `tracking_error_table_text_inconsistent`
   - `tracking_error_multi_match`
   - `年报未直接披露跟踪误差`
4. Split the current `"tracking_error_ambiguous"` usage into distinct notes at minimum:
   - mixed actual/target line: `tracking_error_mixed_actual_and_target`
   - table/text inconsistency: `tracking_error_table_text_inconsistent`
5. Missing-path consistency must be expressed through `ExtractedField.note` and `extraction_mode="missing"` only. Do not require `source_type` / `calculation_method` when `value=None`; preserve those success-path fields only for accepted `TrackingErrorValue`.

### Slice 2: Remove broad early-return suppression while preserving fail-closed notes

Owned files:

- `fund_agent/fund/extractors/performance.py`

Implementation shape:

1. Address both early-return locations:
   - top-level precheck at `performance.py:357-358`;
   - text extraction internal return at `performance.py:494-496`.
2. Replace the top-level `_has_ambiguous_tracking_error_text(report)` suppression with collection/classification that can remember a blocker but still inspect later table/text candidates in the same bounded report input.
3. Replace the text extraction internal `return None` on mixed actual/target line with an explicit blocker outcome, then continue scanning later lines for a valid direct-looking disclosure.
4. If a later candidate is accepted, it must still satisfy direct observed disclosure conditions and complete anchor construction; the earlier blocker may be ignored for success or retained only if the current public model has a place to record non-fatal diagnostics. Do not add `extra_payload`.
5. If no valid direct-looking disclosure is found, return the most specific blocker note by precedence.

Recommended blocker precedence:

1. `tracking_error_table_text_inconsistent`
2. `tracking_error_multi_match`
3. `tracking_error_incomplete_anchor`
4. `tracking_error_unparseable`
5. `tracking_error_mixed_actual_and_target`
6. `tracking_error_target_or_limit`
7. `tracking_error_manager_narrative`
8. `tracking_error_benchmark_only`
9. `tracking_error_standard_deviation_only`
10. `年报未直接披露跟踪误差`

This precedence keeps conflicting or unsafe apparent disclosures above generic absence while allowing a later valid direct-looking disclosure to be accepted.

### Slice 3: Make multi-match handling explicit

Owned files:

- `fund_agent/fund/extractors/performance.py`
- `tests/fund/extractors/test_performance.py`

Implementation shape:

1. For multiple direct-looking table matches or text matches where the extractor cannot select one deterministically, return `tracking_error_multi_match` instead of silent `None`.
2. If all candidate values are semantically duplicate and anchored to the same period, implementation may choose one only if deterministic and covered by tests. The conservative default for this slice is fail-closed `tracking_error_multi_match`.
3. If future implementer decides not to change multi-match production behavior, that decision must be recorded as residual in implementation artifact with owner `future extractor selection policy`; however, the plan preference is to implement explicit blocker note now because it is localized and testable.

### Slice 4: Preserve valid direct-disclosure success contract

Owned files:

- `fund_agent/fund/extractors/performance.py`
- `tests/fund/extractors/test_performance.py`

Implementation shape:

Accepted direct disclosure must continue to require:

- parseable percentage value;
- actual direct tracking-error semantic, not target/limit/control, manager narrative, benchmark-only, or standard-deviation-only text;
- period label from text/table row, defaulting only to `报告期` when the disclosure itself is direct-looking;
- annualized boolean from text/header;
- `source_type="direct_disclosure"`;
- `calculation_method="disclosed"`;
- `frequency="annual_report_period"`;
- `provenance_note` stating the value is annual-report direct disclosure and not derived from benchmark return / standard deviation columns;
- an annual-report `EvidenceAnchor` with `row_locator="tracking_error"` and enough section/table context.

Do not introduce calculated fields, external index identity filling, or benchmark-series provenance in this slice.

### Slice 5: Focused tests only

Owned files:

- `tests/fund/extractors/test_performance.py`
- Optional new fixture snippets under `tests/fixtures/fund/extractors/performance/`

No-go test/data files:

- `reports/golden-answers/**`
- `docs/golden-answer-template.md`
- `docs/code_20260519.csv`
- RR-13 data
- production golden JSON/Markdown

Prefer inline `ParsedAnnualReport` / `ParsedTable` builders already present in `test_performance.py` for deterministic snippets. Use new fixture text files only where readability materially improves.

## Intended Behavior By Blocker Class

| Class | Accepted? | Intended note / behavior | Fixture intent |
|---|---:|---|---|
| target / limit / control | No | `tracking_error_target_or_limit`; examples include `控制在`、`不超过`、`力争`、`目标`、`限制`、`最小化` without direct observed value wording | Text: `本基金力争将年化跟踪误差控制在 4.00% 以内。` |
| manager narrative | No | `tracking_error_manager_narrative`; narrative about tracking-error management or strategy execution without direct observed value | `基金经理在报告期内加强组合管理，努力降低跟踪误差。` plus optional percentage unrelated to observed TE |
| benchmark-only | No | `tracking_error_benchmark_only`; benchmark return, benchmark text, or index comparison alone must not become TE | Text/table with `业绩比较基准收益率` only |
| standard-deviation-only | No | `tracking_error_standard_deviation_only`; `净值增长率标准差` / `业绩比较基准收益率标准差` must not be TE | Existing fixture plus note assertion |
| ambiguous / unparseable | No | Mixed actual/target line -> `tracking_error_mixed_actual_and_target`; malformed percent after direct-looking TE -> `tracking_error_unparseable` | Text: actual TE in same line as target; text: `报告期年化跟踪误差为 --%` |
| incomplete anchor | No | `tracking_error_incomplete_anchor`; direct-looking value whose table/text context cannot produce a valid annual-report anchor must fail closed | Construct table match with missing/invalid table context only if current model can represent it; otherwise mark as residual because current builders always create anchors |
| table/text inconsistency | No | `tracking_error_table_text_inconsistent`; do not reuse generic `tracking_error_ambiguous` | Table `0.53%`, text `0.71%` |
| multi-match | No by default | `tracking_error_multi_match`; explicit blocker instead of silent `None` | Two direct-looking rows or two direct-looking lines with different values/periods |
| valid direct-looking disclosure after earlier ambiguous line | Yes | Later direct-looking disclosure should be accepted if parseable and anchored; broad early-return must not suppress it | First line mixed actual/target or target-only, later line `报告期年化跟踪误差为 1.23%。` |

## Test Matrix

Add or update deterministic tests in `tests/fund/extractors/test_performance.py`:

- `test_extract_performance_marks_tracking_error_target_or_limit_with_specific_note`
  - Uses current target-only fixture or inline text.
  - Asserts `missing`, `value is None`, `anchors == ()`, `note == "tracking_error_target_or_limit"`.
- `test_extract_performance_marks_manager_tracking_error_narrative_with_specific_note`
  - Uses a narrative-only line from manager-style language without observed direct TE.
  - Asserts `note == "tracking_error_manager_narrative"`.
- `test_extract_performance_marks_benchmark_only_text_with_specific_note`
  - Uses benchmark return / benchmark tracking language without TE observed disclosure.
  - Asserts `note == "tracking_error_benchmark_only"` or generic no-disclosure only if no TE keyword appears; if TE keyword appears in benchmark-only context, specific note is required.
- `test_extract_performance_marks_standard_deviation_only_with_specific_note`
  - Extends existing standard-deviation-only coverage to assert `note == "tracking_error_standard_deviation_only"`.
- `test_extract_performance_marks_mixed_actual_target_tracking_error_with_specific_note`
  - Replaces/updates current ambiguous expectation from `"tracking_error_ambiguous"` to `"tracking_error_mixed_actual_and_target"`.
- `test_extract_performance_marks_unparseable_direct_tracking_error_with_specific_note`
  - Direct-looking TE line with non-parseable value; asserts `tracking_error_unparseable`.
- `test_extract_performance_marks_incomplete_anchor_with_specific_note`
  - Add only if implementable without artificial impossible objects. If current `ParsedAnnualReport` always provides enough context for text/table anchor, implementation artifact may record incomplete-anchor as residual with owner `future parser malformed-table fixture`.
- `test_extract_performance_marks_table_text_inconsistent_tracking_error_with_specific_note`
  - Updates current table/text conflict test to expect `tracking_error_table_text_inconsistent`.
- `test_extract_performance_marks_multiple_tracking_error_matches_with_specific_note`
  - Two direct-looking values in text or table; asserts `tracking_error_multi_match`.
- `test_extract_performance_accepts_direct_tracking_error_after_earlier_mixed_target_line`
  - Verifies both early-return locations no longer suppress later valid direct disclosure.
- `test_extract_performance_accepts_direct_tracking_error_after_earlier_target_only_line`
  - Guards target-only `continue` behavior and later direct acceptance.
- Existing direct success tests must continue to pass:
  - `test_extract_performance_outputs_direct_tracking_error_when_disclosed`
  - `test_extract_performance_outputs_tracking_error_from_annual_table`
  - `test_extract_performance_keeps_table_match_when_text_discloses_same_tracking_error`

## README / Docs Update Rule

This implementation should not update README files by default. It changes internal extractor blocker notes and focused tests only.

README update is required only if implementation changes public usage, CLI behavior, configuration entry points, or documented Fund package contract. If only `fund_agent/fund/extractors/performance.py` and focused tests change, no README trigger is met.

Do not update `docs/design.md` or `docs/implementation-control.md` in the implementation slice unless a controller explicitly scopes design/control bookkeeping later.

## Validation Commands

Minimum implementation validation:

```bash
.venv/bin/python -m pytest tests/fund/extractors/test_performance.py -q
.venv/bin/python -m pytest tests/fund/extractors -q
.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check HEAD
```

If implementation touches shared extractor models, snapshot serialization, score/quality behavior, or any field comparability path, also run:

```bash
.venv/bin/python -m pytest tests/fund -q
.venv/bin/python -m pytest -q
```

No validation command should read production PDFs/cache/source helpers directly. Any production verification, if separately authorized later, must use `FundDataExtractor` or `FundDocumentRepository`.

## Stop Conditions

Stop before implementation and return a blocker artifact if:

- The change cannot stay inside `fund_agent/fund/extractors/performance.py` plus focused tests.
- The fix requires changing source adapters, PDF/cache helpers, repository fallback, Service/UI/Engine/renderer orchestration, quality-gate severity, golden schema, selected CSV, or RR-13 data.
- A deterministic blocker note requires adding `extra_payload` or hiding explicit parameters in payload blobs.
- A proposed test depends on indirect evidence rather than direct annual-report snippet semantics.
- The implementation would make any blocked production candidate accepted without new reviewed direct observed disclosure evidence.

Stop before merge/acceptance if:

- Production golden files gain `tracking_error` rows for `001548`, `004194`, `005313`, `017644`, `019918`, or `019923`.
- `schema_drift`, `identity_mismatch`, or `integrity_error` source failures can be hidden by fallback success.
- Multi-match or table/text inconsistency becomes silently successful.
- Existing direct-disclosure success contract loses `source_type="direct_disclosure"` or `calculation_method="disclosed"`.
- Any excluded local draft is read/cited as authority.

## Plan-Review Handoff

Plan reviewers must explicitly evaluate the `Design-Boundary Checklist` section above and state whether each checklist item passes, needs revision, or introduces a residual risk. A review that only checks extractor mechanics without checking `docs/design.md` §11 is incomplete for this gate.

Reviewers must also confirm that the implementation scope remains unchanged: no production golden rows, no external data, no calculated tracking error, no unsupported evidence acceptance, and no expansion into Service/UI/Runtime/Engine/source orchestration.

## Residual Risks And Owners

| Residual | Owner | Handling |
|---|---|---|
| Production `tracking_error` rows for `001548` | Future evidence-backed golden gate | Remain blocked until reviewed direct observed disclosure evidence is accepted. |
| Production `tracking_error` rows for `004194`, `005313`, `017644`, `019918`, `019923` | Future evidence-backed golden gate | Remain blocked; P16 accepted `index_profile` benchmark-context only. |
| Incomplete-anchor fixture may be hard to represent with current `ParsedAnnualReport` builders | P17-S1 implementation agent, then controller if unresolved | Implement if natural through current model; otherwise record explicit residual `future parser malformed-table fixture` without fabricating impossible objects. |
| Multi-match deterministic selection policy | P17-S1 implementation agent | Prefer explicit `tracking_error_multi_match`; if deferred, record owner `future extractor selection policy` and keep fail-closed behavior. |
| Calculated tracking error / external index data | Future design phase | Out of scope; do not introduce through this extractor hardening. |
| Methodology / constituents extraction | Future source-contract phase | Out of scope; no field-contract expansion. |
| E1-E3 / Evidence Confirm / LLM audit | Future audit architecture phase | Out of scope; deterministic MVP only. |
| RR-13 duplicate `016492` and selected CSV source data | User/App source owner | No automatic mutation. |

## Handoff Instructions For Implementation Agent

1. Start from this artifact, `docs/reviews/post-p16-follow-up-planning-20260522.md`, and `docs/reviews/post-p16-follow-up-plan-review-controller-judgment-20260522.md`.
2. Confirm `git status --short --branch` and preserve unrelated untracked excluded drafts.
3. Read current `fund_agent/fund/extractors/performance.py` before editing; code may have changed after this plan.
4. Implement only the slices above, preferably in this order: blocker outcome type/constants, dual early-return replacement, multi-match note, tests.
5. Keep annual-report access through existing `ParsedAnnualReport` inputs, `FundDocumentRepository`, and `FundDataExtractor`; do not touch document source adapters or caches.
6. Do not add production golden rows or change selected CSV/RR-13 data.
7. Run the minimum validation commands and report exact outcomes.
8. If incomplete-anchor cannot be represented cleanly, do not invent brittle production code; record it as residual with owner and keep other blocker tests deterministic.
