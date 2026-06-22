# EC-P4 Slice 3 Implementation Evidence

## Gate

- Work unit: Evidence Confirm Productionization EC-P4 Service/UI/renderer/quality-gate production integration
- Gate: implementation
- Slice: Slice 3 - CLI/UI Summary and Exit Behavior
- Classification: heavy
- Role: AgentCodex implementation worker only
- Prior accepted slice commit: `1dd08fa gateflow: accept ec-p4 service integration slice 2`
- Artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-slice3-implementation-evidence-20260622.md`

## Changed Files

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `docs/reviews/evidence-confirm-productionization-ec-p4-slice3-implementation-evidence-20260622.md`

## Behavior Summary

- Added analyze-only `--evidence-confirm-policy off|warn|block`.
- Passed the option through `FundAnalysisDeveloperOverrides.evidence_confirm_policy` into `FundAnalysisService.analyze()`.
- Kept checklist without `--evidence-confirm-policy`.
- Added `_echo_evidence_confirm_summary(result)` and call order after `_echo_quality_gate_summary(result)` and before report body output.
- Added `_echo_evidence_confirm_blocked(error)` for `EvidenceConfirmBlockedError`.
- Catches `EvidenceConfirmBlockedError` after `QualityGateBlockedError`, exits `2`, and does not emit report body.
- CLI does not call Fund-layer Evidence Confirm runner or repository/materialization functions.
- Evidence Confirm CLI output is compact: status, policy, checked facts, failed facts, auditability score only.
- Default analyze output remains unchanged and contains no `evidence_confirm_` lines.

## Validation

```text
$ uv run pytest tests/ui/test_cli.py -q
........................................................................ [ 87%]
..........                                                               [100%]
82 passed in 1.41s
```

```text
$ uv run ruff check fund_agent/ui/cli.py tests/ui/test_cli.py
All checks passed!
```

```text
$ rg -n "FundDocumentRepository|download_annual_report|annual_report_source|evidence_confirm_sources|evidence_confirm_production|run_repository_bounded_evidence_confirm|Docling|docling|pdfplumber|parser|provider client" fund_agent/ui/cli.py tests/ui/test_cli.py
tests/ui/test_cli.py:2750:        "FundDocumentRepository",
tests/ui/test_cli.py:2751:        "download_annual_report",
tests/ui/test_cli.py:2752:        "annual_report_source",
tests/ui/test_cli.py:2753:        "evidence_confirm_sources",
tests/ui/test_cli.py:2754:        "evidence_confirm_production",
tests/ui/test_cli.py:2755:        "run_repository_bounded_evidence_confirm",
tests/ui/test_cli.py:2756:        "Docling",
tests/ui/test_cli.py:2757:        "docling",
tests/ui/test_cli.py:2758:        "pdfplumber",
tests/ui/test_cli.py:2787:        "download_annual_report",
tests/ui/test_cli.py:2788:        "annual_report_source",
```

Interpretation: matches are the static-guard forbidden-term lists in `tests/ui/test_cli.py`; `fund_agent/ui/cli.py` has no forbidden Evidence Confirm runner, repository, source helper, parser, Docling or pdfplumber import.

```text
$ git diff --check -- fund_agent/ui/cli.py tests/ui/test_cli.py docs/reviews/evidence-confirm-productionization-ec-p4-slice3-implementation-evidence-20260622.md
<no output>
```

## Docs Decision

- No README, design, control, startup packet, or PR state update in this implementation-worker slice.
- Slice 6 remains the approved docs-sync owner for public documentation wording.

## Residual Risks

- Checklist Evidence Confirm CLI support remains deferred to a later explicit checklist EC slice/gate; classified as assigned to later work unit.
- Public docs for the new analyze developer override flag remain deferred to Slice 6; classified as covered by later approved slice.
- This slice uses fake Service tests only and does not prove live/PDF/provider behavior; classified as covered by prior/later EC-P4 slices and outside Slice 3 scope.

## Verdict

EC_P4_SLICE3_IMPLEMENTATION_READY_FOR_CODE_REVIEW_NOT_READY
