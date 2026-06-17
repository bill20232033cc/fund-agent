# Docling Reference Bundle Producer Determinism Evidence - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism No-live Evidence Gate`
Role: evidence worker
Accepted implementation commit: `8fe0bb4`
Release/readiness: `NOT_READY`
Verdict: `PRODUCER_DETERMINISM_EVIDENCE_ACCEPTED_NOT_READY`

## Allowed Write Set

- `reports/docling-reference-bundle-producer-determinism/20260617/producer_determinism_matrix.json`
- `docs/reviews/docling-reference-bundle-producer-determinism-evidence-20260617.md`

## Evidence Method

The evidence uses synthetic no-live in-memory `RepositoryReferenceBundle`, `RepositoryReferenceCell`, and `RepositoryReferenceTextSpan` objects through the implemented candidate-only helper surfaces.

No PDF, cache, source helper, repository reload, live network, provider, LLM, analyze, checklist, golden, readiness, release, PR, parser, or evidence-wrapper command was used.

## Matrix Facts

Matrix: `reports/docling-reference-bundle-producer-determinism/20260617/producer_determinism_matrix.json`

Accepted assertions:

- same logical input repeated -> same `bundle_content_fingerprint`;
- same logical input with reordered cell order -> same `bundle_content_fingerprint`;
- hash-participating content perturbation (`004393` -> `004394`) -> changed `bundle_content_fingerprint`;
- companion metadata-only mutation (`producer_contract_version`) -> unchanged `bundle_content_fingerprint`;
- blocked reference generation -> `diagnostic_payload_available=false` and `bundle_content_fingerprint=null`;
- prior `13 / 4` and current `10 / 7` residual-closure matrices are not reinterpreted as helper improvement/regression until producer diagnostics exist;
- current `10 / 7` remains blocked evidence, not successful re-evidence.

Key fingerprints:

| Case | Fingerprint / state |
| --- | --- |
| `base` | `7fc0a334b3640d20b2e6018f901589286aac035adad91aa11039d322a056b6dc` |
| `repeat` | `7fc0a334b3640d20b2e6018f901589286aac035adad91aa11039d322a056b6dc` |
| `reordered` | `7fc0a334b3640d20b2e6018f901589286aac035adad91aa11039d322a056b6dc` |
| `companion_metadata_only_change` | `7fc0a334b3640d20b2e6018f901589286aac035adad91aa11039d322a056b6dc` |
| `mutated_hash_participating_content` | `e14e5639a455dbc923770c6158c3be6e59b42be10be9fe01c074c590542f1662` |
| `blocked_missing_diagnostics` | `bundle_content_fingerprint=null`, `diagnostic_payload_available=false` |

## Commands Run

Command:

```text
uv run python - <<'PY'
... synthetic in-memory RepositoryReferenceBundle evidence generation probe ...
PY
```

Result: PASS. The command printed deterministic matrix JSON to stdout; the final JSON artifact was written as the reduced evidence matrix above.

Command:

```text
python -m json.tool reports/docling-reference-bundle-producer-determinism/20260617/producer_determinism_matrix.json
```

Result: PASS.

Command:

```text
python - <<'PY'
... JSON assertions over producer_determinism_matrix.json ...
PY
```

Result: PASS.

Command:

```text
git diff --check -- reports/docling-reference-bundle-producer-determinism/20260617/producer_determinism_matrix.json docs/reviews/docling-reference-bundle-producer-determinism-evidence-20260617.md
```

Result: PASS.

## Non-claims

This evidence does not prove:

- source truth acceptance;
- Docling baseline promotion;
- parser replacement;
- full field correctness;
- golden readiness;
- release readiness;
- PR readiness.

The following remain binding:

- `candidate_only=true`;
- `source_truth_status=not_proven`;
- release/readiness remains `NOT_READY`.

## Residual Risks / Next Gate

- This gate proves deterministic producer diagnostics on synthetic no-live in-memory bundles; it does not prove field correctness or source truth on real annual reports.
- Future residual-closure re-evidence must compare `bundle_content_fingerprint` before interpreting closure-count movement.
- If a future real-artifact evidence gate sees fingerprint/count drift, it must emit a blocked non-comparable verdict instead of interpreting closure-count changes as helper regression or improvement.

Recommended next gate:

`Docling Reference Bundle Producer Determinism Evidence Review Gate`

## Self-check

Self-check: pass.

VERDICT: `PRODUCER_DETERMINISM_EVIDENCE_ACCEPTED_NOT_READY`
