# Docling Baseline Qualification Built-in Representation Handler Implementation Review - DS - 2026-06-15

Verdict: `BLOCKED`

Review inputs:

- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-evidence-20260615.md`

Implementation files reviewed:

- `fund_agent/fund/documents/candidates/representation_handlers.py`
- `fund_agent/fund/documents/candidates/representation_export.py`
- `tests/fund/documents/test_candidate_representation_handlers.py`
- `tests/fund/documents/test_candidate_representation_export.py`
- `fund_agent/fund/README.md`

## Findings

| ID | Severity | Path / line | Reason | Fix |
|---|---|---|---|---|
| DS-IMPL-F1 | High / blocking | `fund_agent/fund/documents/candidates/representation_handlers.py:169`, `fund_agent/fund/documents/candidates/representation_handlers.py:177-183`, `fund_agent/fund/documents/candidates/representation_handlers.py:780-797`; `tests/fund/documents/test_candidate_representation_handlers.py:199-254` | The accepted plan judgment requires Docling to use local artifact/offline/socket-block semantics. The implementation checks that `workspace_root / docling_artifacts_path` exists, but the default converter discards `config` (`_ = config`) and constructs `DocumentConverter()` without binding that path or proving Docling will use only the accepted local artifact directory. Current tests use an injected fake converter and do not verify that the default converter receives, configures, or is constrained to `docling_artifacts_path`. This leaves the later evidence gate able to run against ambient installed/global Docling assets instead of the accepted local artifact path, while still appearing to satisfy the "local artifacts path exists" check. | Bind the default Docling converter to the configured local artifact directory, or fail closed with `docling_model_artifact_unavailable` if the current Docling API cannot be constrained to that path. Add a no-live test that monkeypatches the default Docling import/constructor or converter factory boundary and proves the configured artifact path/offline settings are actually consumed before conversion, not merely checked for existence. |

## Accepted Facts

- Candidate internals remain outside `fund_agent.fund.documents.__all__`; no public documents export was introduced.
- Reviewed files do not modify `FundDocumentRepository`, production source policy, production cache, Service, UI, Host, renderer, quality gate, extractor consumers, `EvidenceAnchor`, or `CHAPTER_CONTRACT`.
- EID HTML render remains blocked candidate output and is not claimed as raw XML/XBRL, source truth, field correctness, taxonomy proof, readiness, or parser replacement.
- No Eastmoney/CNINFO/fund-company fallback route was introduced.
- pdfplumber handler is candidate-internal and tests use fake extractor functions rather than real annual-report PDF body reads.
- No-clobber behavior matches the plan amendment: `reference_existing_json` is read-only and skipped during writes; write-producing `handled` / `blocked` outputs reject existing paths by default; mixed manifests preflight before partial writes; `allow_overwrite` does not rewrite references.

## Validation

No live/network/PDF body/FDR/Docling conversion/provider/LLM/analyze/readiness/release command was run.

No-live validation run:

```text
uv run pytest tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
23 passed in 0.50s
```

```text
uv run ruff check fund_agent/fund/documents/candidates/representation_handlers.py fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py
```

Result:

```text
All checks passed!
```

```text
git diff --check
```

Result: passed with no output.

## Residual Risks

- `--docling-no-socket-block` remains an explicitly exposed escape hatch. It is acceptable only if future evidence gates explicitly authorize it and record why socket blocking was disabled.
- Full S4/S5/S6 representation quality is still unevidenced and must remain deferred until after this blocker is fixed and implementation is accepted.

## Gate Decision

Do not proceed to `Full Representation Export Evidence Gate` yet.

Required before acceptance:

1. Fix DS-IMPL-F1 so the default Docling path is actually constrained to accepted local artifacts or fails closed.
2. Add targeted no-live tests proving the default converter path/offline constraint.
3. Request targeted DS re-review for DS-IMPL-F1.
