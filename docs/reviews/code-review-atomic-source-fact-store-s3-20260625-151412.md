# Code Review

## Scope

- Mode: gate-scoped current changes review
- Branch or PR: `evidence-confirm-productionization`
- Base: S3 accepted plan and current workspace S3 diff, excluding pre-existing unrelated dirty files
- Output file: `docs/reviews/code-review-atomic-source-fact-store-s3-20260625-151412.md`
- Included scope:
  - `fund_agent/fund/processors/fund_disclosure_processor.py`
  - `tests/fund/processors/test_fund_disclosure_processor.py`
  - `tests/fund/test_data_extractor.py`
  - `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s3-implementation-20260625-150130.md`
- Excluded scope:
  - Pre-existing dirty docs/review artifacts and unrelated untracked files.
  - S4 ChapterFactProvider, S5 Evidence Confirm, live/PDF, product CLI, provider/LLM, PR/remote, tag, release, readiness.
- Parallel review coverage: 无

## Findings

### S3-CR-001-未修复-高-partial child facts can be reported as accepted composite families

- **入口/函数**: `FundDisclosureDocumentProcessor.extract()` -> `_field_families_for_intermediate()` -> `_extract_manager_profile_source_truth()` / `_extract_return_attribution_source_truth()`
- **文件(行号)**: `fund_agent/fund/processors/fund_disclosure_processor.py:1302`, `fund_agent/fund/processors/fund_disclosure_processor.py:2816`, `fund_agent/fund/processors/fund_disclosure_processor.py:2923`, `fund_agent/fund/processors/fund_disclosure_processor.py:2981`, `fund_agent/fund/processors/fund_disclosure_processor.py:3805`, `fund_agent/fund/processors/fund_disclosure_processor.py:4024`, `fund_agent/fund/processors/fund_disclosure_processor.py:4084`
- **输入场景**: proof-positive FDD source-truth route extracts every required top-level family value, but one migrated child fact inside a composite is absent. Example: `manager_strategy_text.strategy_summary` is present, `manager_strategy_text.market_outlook` is absent, while `portfolio_managers`, `turnover_rate`, `manager_alignment`, and `holdings_snapshot` are present.
- **实际分支**: `_composite_value_from_source_facts(..., require_all=False)` returns a composite dict when any child fact exists, filling missing children with `None`. `_build_manager_profile_value_from_source_facts()` then includes the `manager_strategy_text` top-level key. `_manager_profile_status()` checks only whether all `_MANAGER_PROFILE_REQUIRED_TOP_LEVEL` keys exist, so it returns `accepted`. `_manager_profile_source_truth_gaps()` also checks only missing top-level keys, so it emits no child-level gap for `manager_strategy_text.market_outlook`.
- **预期行为**: Per the accepted atomic source fact contract, missing child provenance must produce a gap/status and must not let the derived composite view be treated as fully accepted. A top-level compatibility dict may contain a `None` child, but the family/view status must remain `partial` or carry an explicit child gap until all required child facts satisfy the assembly policy.
- **实际行为**: The family can be marked `accepted` with a compatibility value containing a missing child `None`, and `FundProcessorResult.source_facts` will contain only the present child fact. The same pattern applies to `manager_alignment` and `fee_schedule`: their compatibility values are assembled with `require_all=False`, while `_manager_profile_status()` and `_return_attribution_status()` only check top-level presence.
- **直接证据**:
  - `_composite_value_from_source_facts()` returns a dict with `None` for absent children when `require_all=False` and at least one accepted child exists (`fund_disclosure_processor.py:1324-1337`).
  - `manager_strategy_text` and `manager_alignment` call that helper with `require_all=False` (`fund_disclosure_processor.py:2835-2854`).
  - `_manager_profile_status()` returns `accepted` solely from top-level presence plus no ambiguity (`fund_disclosure_processor.py:2995-2998`).
  - `_manager_profile_source_truth_gaps()` only computes `missing_top_level`; it does not inspect missing child facts inside `manager_strategy_text` or `manager_alignment` (`fund_disclosure_processor.py:2952-2978`).
  - `fee_schedule` also uses `require_all=False` (`fund_disclosure_processor.py:3829-3834`), while `_return_attribution_status()` only checks required top-level keys (`fund_disclosure_processor.py:4097-4100`) and `_return_attribution_source_truth_gaps()` only emits top-level gaps (`fund_disclosure_processor.py:4053-4081`).
  - The new tests cover a partial `manager_strategy_text` only when other top-level groups are also missing (`tests/fund/processors/test_fund_disclosure_processor.py:3062-3124`), so they do not catch the all-top-level-present / missing-child case.
- **影响**: Atomic fact store truth and family compatibility status can diverge silently. Downstream S4/S5 gates may receive an `accepted` composite/family while one child fact has no atomic source fact or anchor, recreating the exact coarse/composite audit ambiguity this work unit is meant to remove.
- **建议改法和验证点**:
  - Add child-completeness checks for migrated composites before deriving family status/gaps.
  - Emit `field_family_partial` gaps with child `source_field_path` such as `manager_strategy_text.market_outlook`, `manager_alignment.employee_holding`, or `fee_schedule.custody_fee` when a required child is absent.
  - Make `accepted` require all required children for the migrated composite policies that are treated as required by the S3/S1 contract; if a composite intentionally allows optional children, encode that policy explicitly and test it.
  - Add regression tests where every top-level group is present but exactly one migrated child is missing, and assert `status == "partial"` plus the missing child gap and absence from `source_facts`.
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 高

## Open Questions

- 无

## Residual Risk

- Review did not run live/PDF, product CLI, provider/LLM, PR/remote, tag, release, or readiness checks.
- S4 ChapterFactProvider and S5 Evidence Confirm behavior remain out of this S3 review scope.
- Existing implementation validation was read from the S3 implementation artifact and pane output; this review focused on static call-path correctness and did not rerun the full validation matrix.

## Conclusion

Verdict: `S3_CODE_REVIEW_BLOCKED_FIX_REQUIRED_NOT_READY`
