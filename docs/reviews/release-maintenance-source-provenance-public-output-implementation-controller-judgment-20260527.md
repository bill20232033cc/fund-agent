# Controller Judgment: source provenance public-output implementation

> Controller: Codex
> Date: 2026-05-27
> Gate: `source provenance public-output implementation`
> Latest accepted checkpoint before gate: `315c9ef docs: accept source provenance implementation plan`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering implementation | `source provenance public-output implementation plan accepted locally` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted plan artifacts |

## Decision

Accepted.

The implementation matches the accepted narrow slice: Fund-owned deterministic source provenance projection, safe not-applicable default factory on `StructuredFundDataBundle.source_provenance`, production projection from `ParsedAnnualReport.metadata.source`, eight additive snapshot JSONL fields, and a separate `## Source Provenance` summary table.

The implementation does not change `FundDocumentRepository` source strategy, source helpers, downloader/cache/PDF behavior, fallback eligibility, renderer, FQ0-FQ6 policy, default analyze/checklist behavior, Host/Agent/dayu, fund-type logic, extractor logic, golden fixtures, baseline fixtures, or replacement candidates.

## Review Summary

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `PASS` with one low finding | Accepted. Low summary-note precision finding deferred. |
| AgentGLM | `PASS` | Accepted. No material findings. |

## Finding Disposition

| Finding | Source | Status | Judgment |
|---|---|---|---|
| `Source Provenance` summary omission note appears whenever errors exist, even if every errored fund also has records | MiMo F1 | Deferred | The table remains correct and the note is conservative / informational. Defer until an observability cleanup gate; do not spend another implementation loop because no provenance classification or source-safety behavior is affected. |

## Accepted Files

- `fund_agent/fund/source_provenance.py`
- `fund_agent/fund/data_extractor.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_source_provenance.py`
- `tests/fund/test_data_extractor.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/services/test_extraction_score_service.py`
- `tests/README.md`

## Validation

Focused implementation tests:

```text
uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py
67 passed
```

Adjacent compatibility tests:

```text
uv run pytest tests/services/test_extraction_snapshot_service.py tests/services/test_extraction_score_service.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_quality_gate_service.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
112 passed
```

Static / whitespace:

```text
uv run ruff check .
passed

git diff --check
passed
```

## Residual Risks

- Current public repository metadata still does not persist `primary_failure_category`; fallback-backed production rows normally classify as `unknown_public_metadata_absent` / `incomplete`.
- `110020` / 2024 and `017641` / 2024 remain outside the clean denominator until a future evidence gate classifies their new public provenance output.
- `017641` may still be quality-gate `block`; source provenance alone cannot make it baseline-ready.
- Pure FOF coverage, bond baseline-blocking, and reviewed-fact blockers remain open.
- MiMo low summary-note precision finding is deferred to a future observability cleanup gate.

## Next Entry Point

`post-implementation source provenance bounded evidence classification gate`

The next gate may run bounded public CLI evidence for `110020` / 2024 and `017641` / 2024 through public `fund-analysis extraction-snapshot`, `extraction-score`, and `quality-gate` paths only. It must classify rows from public provenance fields and quality outputs; it must not promote durable baseline/golden fixtures, change code, inspect PDF/cache/source helpers, or infer fallback eligibility from downstream success.
