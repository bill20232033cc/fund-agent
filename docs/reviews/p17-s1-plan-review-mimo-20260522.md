# P17-S1 tracking_error extractor ambiguity boundary plan review — MiMo（2026-05-22）

## Verdict

`PASS_WITH_FINDINGS`

## Review Target

- `docs/reviews/p17-s1-tracking-error-extractor-ambiguity-boundary-plan-20260522.md`

## Inputs Read

- `AGENTS.md`
- `docs/design.md` v2.1（especially §1.3 and §11）
- `docs/implementation-control.md`（Startup Packet and P17 archive）
- `docs/reviews/design-alignment-review-controller-judgment-20260522.md`
- `fund_agent/fund/extractors/performance.py`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/data_extractor.py`
- `tests/fund/extractors/test_performance.py`

## Design-Boundary Checklist Assessment

Plan must satisfy `docs/design.md` §11. Each item is evaluated below.

| §11 Checklist Item | Verdict | Notes |
|---|---|---|
| §1.3 non-goals not violated | PASS | No all-market comparison, real-time behavior detection, self-calculated thermometer, portfolio management, buy/sell recommendations, or external Dayu Host/Engine/tool-loop runtime dependency introduced. |
| UI / Service / Capability / Runtime / Engine boundaries preserved | PASS | Implementation limited to `performance.py` extractor behavior plus focused extractor tests. UI, Service orchestration, Runtime, Engine, renderer, quality gate, and source orchestration are explicitly no-go. |
| Production annual-report access through `FundDocumentRepository` / `FundDataExtractor` | PASS | Plan explicitly states no direct PDF cache, source adapter, downloader, or concrete fallback helper call. |
| No external Dayu runtime, LLM writing, Evidence Confirm, calculated tracking error, external index adapters, methodology/constituents extraction, or `extra_payload` hidden parameters | PASS | All explicitly listed as non-goals. |
| Success signals verifiable by deterministic tests, ruff, and `git diff --check` | PASS | Validation commands section lists exact pytest, ruff, and diff check commands. |
| No production golden rows, no external data, no calculated tracking error, no unsupported evidence acceptance | PASS | Plan explicitly blocks production golden rows for all six blocked candidates. |

## Findings

### F1 — Note constant `tracking_error_ambiguous` removal or migration is not explicitly stated

**Severity**: Low
**Location**: Plan §Slice 1 item 4, §Slice 2 item 2, current `performance.py:357-358`, `performance.py:494-496`, `performance.py:363-364`

**Issue**: The plan splits `"tracking_error_ambiguous"` into `tracking_error_mixed_actual_and_target` and `tracking_error_table_text_inconsistent`, and the test matrix (item `test_extract_performance_marks_mixed_actual_target_tracking_error_with_specific_note`) replaces the old expectation. However, the plan does not explicitly state whether the literal string `"tracking_error_ambiguous"` should be removed from the codebase entirely or preserved as a legacy fallback. Current code uses it at three call sites: `_has_ambiguous_tracking_error_text` early-return (line 358), `_select_consistent_tracking_error_match` fallback (line 364), and the test at line 233. The plan covers lines 358 and 364 with new note constants, but does not explicitly confirm that all three usages are replaced.

**Risk**: An implementation agent might replace only two of the three usages, leaving a stale `"tracking_error_ambiguous"` in `_select_consistent_tracking_error_match`'s `return None` → mapped to `"tracking_error_ambiguous"` path. This would create inconsistent note semantics.

**Required plan change**: Add an explicit statement in Slice 1 or Slice 2 that all current `"tracking_error_ambiguous"` usages must be replaced by the specific successor notes, and that the literal string `"tracking_error_ambiguous"` must not appear in the final implementation or tests.

### F2 — `tracking_error_manager_narrative` classifier definition is underspecified

**Severity**: Low
**Location**: Plan §Intended Behavior By Blocker Class, row "manager narrative"

**Issue**: The plan defines `tracking_error_manager_narrative` for "narrative about tracking-error management or strategy execution without direct observed value" with the example "基金经理在报告期内加强组合管理，努力降低跟踪误差。" However, the current code has no dedicated manager-narrative classifier. The `_tracking_error_context_is_target_or_ambiguous` helper at `performance.py:587-601` uses the same `_TRACKING_ERROR_NEGATIVE_KEYWORDS` tuple for both target/limit and narrative contexts. The plan does not specify how the implementation should distinguish `tracking_error_manager_narrative` from `tracking_error_target_or_limit` — whether through new keywords, a separate helper, or heuristic sentence-level analysis.

**Risk**: The implementation agent may either (a) merge manager narrative into target/limit (losing the planned semantic distinction) or (b) create an ad-hoc heuristic that is fragile or inconsistent with existing keyword lists.

**Required plan change**: Either specify the distinguishing signal for manager narrative (e.g., new keyword tuple, sentence-pattern heuristic, or absence of target/limit keywords combined with presence of tracking-error keywords) or explicitly mark `tracking_error_manager_narrative` as a residual with owner if the signal cannot be deterministically defined without introducing false positives.

### F3 — `tracking_error_benchmark_only` classifier boundary is ambiguous with existing table extraction

**Severity**: Low
**Location**: Plan §Intended Behavior By Blocker Class, row "benchmark-only"; current `_extract_tracking_error_from_tables` at `performance.py:427-469`

**Issue**: The plan says benchmark-only text (e.g., `业绩比较基准收益率` only) must not become TE and should return `tracking_error_benchmark_only`. However, the current table extraction path (`_extract_tracking_error_from_tables`) looks for a header containing `_TRACKING_ERROR_KEYWORDS` (`跟踪误差`/`跟踪偏离度`) — it would never match a `业绩比较基准收益率` header as tracking error. The text extraction path similarly requires `_TRACKING_ERROR_KEYWORDS` to be present in the line. So the "benchmark-only" blocker class appears to be unreachable through the current extraction logic: a line with only `业绩比较基准收益率` and no `跟踪误差`/`跟踪偏离度` keyword would be filtered out by `_line_has_tracking_error_value` at line 567-584 and never enter the tracking-error extraction path at all.

**Risk**: The test `test_extract_performance_marks_benchmark_only_text_with_specific_note` may be testing an unreachable path, or the implementation agent may add a new entry point that changes extraction semantics unnecessarily.

**Required plan change**: Clarify whether `tracking_error_benchmark_only` is intended to catch (a) lines that contain both `跟踪误差` keyword and `业绩比较基准收益率` but no actual observed TE value, or (b) lines with only `业绩比较基准收益率`. If (b), note that the current extractor already filters these out silently and the blocker note would be a no-op addition. If (a), specify the distinguishing criteria more precisely.

### F4 — `tracking_error_incomplete_anchor` test may require artificial impossible objects

**Severity**: Info
**Location**: Plan §Test Matrix, row `test_extract_performance_marks_incomplete_anchor_with_specific_note`; Plan §Residual Risks And Owners, row "Incomplete-anchor fixture"

**Issue**: The plan already acknowledges this residual risk and says "Implement if natural through current model; otherwise record explicit residual." The current `_build_tracking_error_anchor` at `performance.py:700-735` always produces a valid anchor from either table context (with page_number, table_id, row_label, matched_header) or text context (with section_id and matched_text). The `ParsedAnnualReport` builder always provides `section_id`. So there is no natural way to produce an incomplete anchor through the current model without fabricating an impossible `ParsedAnnualReport` state (e.g., `None` section_id).

**Risk**: Minimal — the plan already handles this as a residual. The finding is informational.

**Required plan change**: None required. The plan's existing residual handling is adequate.

### F5 — Blocker precedence order may not match actual control flow

**Severity**: Info
**Location**: Plan §Slice 2, Recommended blocker precedence

**Issue**: The plan defines a 10-level precedence from most-specific to least-specific blocker. However, the current extractor runs in a specific order: (1) `_has_ambiguous_tracking_error_text` precheck, (2) table extraction, (3) text extraction, (4) `_select_consistent_tracking_error_match` for table/text pair, (5) single-match acceptance. The plan's Slice 2 replaces the broad early-return with "collection/classification that can remember a blocker but still inspect later candidates." This implies the implementation must accumulate blocker notes across multiple extraction stages and then select the highest-precedence one at the end. The plan does not specify the accumulation mechanism — whether through a mutable list, the proposed `_TrackingErrorExtractionOutcome` type, or a separate classification pass.

**Risk**: Low — the plan provides enough structure for a competent implementation agent. However, if the agent accumulates blockers naively (e.g., first-seen wins), the precedence order may not be respected.

**Required plan change**: Optional — could add a brief note that the blocker accumulation should use the precedence table as a selection key (e.g., `min(blockers, key=precedence_index)`) rather than first-seen ordering.

### F6 — Existing test `test_extract_performance_does_not_treat_tracking_error_target_as_observed` note assertion gap

**Severity**: Low
**Location**: Plan §Test Matrix; current `tests/fund/extractors/test_performance.py:192-211`

**Issue**: The plan's test matrix includes `test_extract_performance_marks_tracking_error_target_or_limit_with_specific_note` which asserts `note == "tracking_error_target_or_limit"`. The existing test at line 192-211 currently asserts `extraction_mode == "missing"`, `value is None`, `anchors == ()` but does NOT assert a specific note value. The plan should explicitly state whether the existing test should be updated to assert the new note or kept as-is with the new test added separately.

**Risk**: If the existing test is not updated, it will pass even if the implementation returns an incorrect note (e.g., the generic `"年报未直接披露跟踪误差"` instead of `"tracking_error_target_or_limit"`). The new test covers this, but having the existing test also assert the note would strengthen regression coverage.

**Required plan change**: State explicitly whether existing `test_extract_performance_does_not_treat_tracking_error_target_as_observed` should be updated to add `note == "tracking_error_target_or_limit"` assertion, or whether the new standalone test is considered sufficient.

### F7 — `test_extract_performance_does_not_use_standard_deviation_as_tracking_error` note assertion gap

**Severity**: Low
**Location**: Plan §Test Matrix; current `tests/fund/extractors/test_performance.py:236-254`

**Issue**: Same pattern as F6. The existing standard-deviation test asserts `extraction_mode == "missing"` and `value is None` but does not assert a note. The plan adds `test_extract_performance_marks_standard_deviation_only_with_specific_note` to assert `note == "tracking_error_standard_deviation_only"`. The plan should state whether the existing test should also be updated.

**Risk**: Same as F6 — existing test would pass with wrong note.

**Required plan change**: State explicitly whether existing test should be updated.

## Implementation Scope Confirmation

| Scope Constraint | Status |
|---|---|
| No production golden rows for `001548`, `004194`, `005313`, `017644`, `019918`, `019923` | Confirmed — plan explicitly blocks |
| No external data / source CSV / RR-13 mutation | Confirmed |
| No calculated tracking error | Confirmed |
| No Service/UI/Runtime/Engine/source orchestration creep | Confirmed |
| No `docs/design.md` or `docs/implementation-control.md` edits | Confirmed |
| No README updates unless public contract changes | Confirmed |
| No `extra_payload` hidden parameters | Confirmed |

## Conclusion

The plan is code-generation-ready with seven findings, none of which block plan acceptance. F1, F2, F3, F6, and F7 are implementation clarification items that a competent implementation agent should resolve during implementation; F4 and F5 are informational. The design-boundary checklist passes all six items. The plan correctly preserves all production blockers, does not introduce forbidden runtime/data expansions, and maintains fail-closed semantics for all unsupported tracking-error evidence paths.

**No finding blocks plan acceptance.** The plan may proceed to implementation with the above findings as implementation guidance.
