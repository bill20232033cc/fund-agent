# FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Aggregate Deepreview Controller Judgment

## Metadata

- Work unit: `FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction`
- Gate: Aggregate Deepreview Gate
- Branch: `funddisclosure-investor-experience-source-truth`
- Reviewed range: `1bf4187..HEAD`
- Accepted slice commit: `8dac1fc`
- Aggregate reviews:
  - `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-aggregate-deepreview-ds-20260620.md`
  - `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-aggregate-deepreview-mimo-20260620.md`
- Code review controller judgment: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-code-review-controller-judgment-20260620.md`
- Artifact path: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-aggregate-deepreview-controller-judgment-20260620.md`

## Verdict

`ACCEPT_AGGREGATE_DEEPREVIEW_READY_FOR_ACCEPTED_DEEPREVIEW_COMMIT_NOT_READY`

Both aggregate deepreviews returned `AGGREGATE_DEEPREVIEW_PASS`. No blocking finding remains.

## Findings

| Finding | Source | Controller decision |
|---|---|---|
| No substantive findings | DS aggregate deepreview | accepted |
| No substantive findings | MiMo aggregate deepreview | accepted |
| `subscription_redemption` / `income_distribution` absence not asserted by a named negative unit test | MiMo residual risk | deferred-with-owner; the current public shape test plus exhaustive `_INVESTOR_EXPERIENCE_REQUIRED_TOP_LEVEL` are sufficient for this slice; a future public-schema expansion gate must add explicit negative tests before exposing those roles |
| Real-report correctness unproven | DS/MiMo residual risk | deferred-with-owner; remains outside this no-live fixture-backed work unit |
| `current_stage.v1` and `core_risk.v1` still unimplemented | DS/MiMo residual risk | deferred-with-owner; next field-family work units remain separate |

## Accepted Scope

The aggregate review confirms the accepted implementation remains within the planned scope:

- proof-positive `investor_experience.v1` direct extraction covers only `investor_return`, `holder_structure` and `share_change`;
- `subscription_redemption` and `income_distribution` remain candidate-only roles and are not public values;
- proof-missing, proof-invalid and candidate-boundary paths stay public missing and candidate-only where applicable;
- direct-route `candidate_evidence` is empty;
- `current_stage.v1` and `core_risk.v1` remain unimplemented and unaffected;
- facade projection maps only the three accepted keys;
- docs/control truth preserve candidate-only / not-proven / `NOT_READY` boundaries;
- no parser replacement, `EvidenceSourceKind` expansion, public `EvidenceAnchor` expansion, Service/UI/Host/renderer/quality-gate consumption, live/provider/LLM work or readiness/release claim was introduced.

## Validation

Aggregate reviewers reproduced or accepted the following validation:

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
175 passed
```

```text
uv run pytest tests/fund/test_data_extractor.py -k disclosure_source_truth_investor_experience
1 passed
```

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py tests/fund/test_data_extractor.py
All checks passed
```

```text
git diff --check 1bf4187..HEAD
passed
```

## Process Note

During the MiMo aggregate review, the reviewer pane attempted to request reads outside `/Users/maomao/fund-agent`. Controller rejected those reads. The accepted MiMo artifact was already written and cites only current-repo evidence. No outside-repo content is accepted as evidence for this gate.

## Next Gate

After the accepted deepreview checkpoint commit, the next entry point is:

`FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Ready-to-open-draft-PR Gate`

Release/readiness remains `NOT_READY`.
