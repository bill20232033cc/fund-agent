# EC-P2W-1 Warning Disposition Implementation Evidence

Date: 2026-06-22

## Scope Implemented

- Added explicit EC-P2 repository/source/PDF `pathway_status` to `EvidenceConfirmRepositoryRunResult`.
- Preserved strict runner `status` behavior:
  - strict `status` remains `pass` only when reference build passes and V2 is absent or `overall_status=="pass"`;
  - section-only V2 `warn` still keeps strict `status="fail"`.
- Added `pathway_warning_reasons`.
- Added pathway status classification:
  - pass for V2 pass;
  - pass for the exact expected no-blocking E1 `anchor_precision` warning from section-only smoke;
  - fail for repository/source/provenance/materializer failures;
  - fail for V2 fail, blocking issue or unexpected warning.
- Updated authorized live sample safe JSON serialization:
  - `pathway_status`
  - `pathway_warning_reasons`
  - existing strict `status`
  - existing `evidence_confirm_overall_status`
  - `field_correctness_proven=false`
- Updated Fund/test README current-state wording.

## Files Changed

- `fund_agent/fund/evidence_confirm_sources.py`
- `scripts/evidence_confirm_ec_p2_live_sample.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Tests Added / Updated

- Section-smoke V2 `anchor_precision` warning:
  - strict `status=="fail"`;
  - V2 `overall_status=="warn"`;
  - `pathway_status=="pass"`;
  - `pathway_warning_reasons==("v2_anchor_precision_warn_section_only_smoke",)`.
- V2 value mismatch remains `pathway_status=="fail"`.
- Negative provenance remains `pathway_status=="fail"`.
- Materializer failure remains `pathway_status=="fail"`.
- Repository failure safe JSON includes `pathway_status=="fail"` and no warning reasons.

## Validation

All validation below is no-live. No live/PDF/provider/LLM command was executed.

```text
uv run pytest tests/fund/test_evidence_confirm_sources.py -q
38 passed in 0.87s
```

```text
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q
85 passed in 0.87s
```

```text
uv run ruff check fund_agent/fund/evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py tests/fund/test_evidence_confirm_sources.py
All checks passed!
```

```text
git diff --check -- fund_agent/fund/evidence_confirm_sources.py scripts/evidence_confirm_ec_p2_live_sample.py tests/fund/test_evidence_confirm_sources.py fund_agent/fund/README.md tests/README.md
PASS
```

## Not Executed

- Did not run:
  - `uv run python scripts/evidence_confirm_ec_p2_live_sample.py --fund-code 004393 --report-year 2025 --force-refresh`

Reason: live/PDF re-evidence is the next gate after no-live implementation code review and controller judgment.

## Non-Goals Preserved

- No global `anchor_precision` relaxation.
- No semantic entailment Evidence Confirm.
- No Service/UI/renderer/quality-gate integration.
- No repository/source/fallback behavior change.
- No public `EvidenceAnchor` / `EvidenceSourceKind` expansion.
- No readiness/release/PR state change.

## Next Gate

EC-P2W-1 code review.
