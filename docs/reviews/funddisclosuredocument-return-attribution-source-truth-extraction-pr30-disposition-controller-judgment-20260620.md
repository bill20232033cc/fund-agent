# FundDisclosureDocument return_attribution.v1 Source-truth Direct Extraction PR #30 Disposition Controller Judgment

## Verdict

`ACCEPT_PR30_DISPOSITION_MERGED_NOT_READY`

## Inputs

- PR: #30 `https://github.com/bill20232033cc/fund-agent/pull/30`
- Pre-disposition remote head: `0b1bb8180a058f81e1ffe6b2e0be006897f4de6d`
- Pre-disposition state: draft/open, merge state `CLEAN`, CI `test` success
- Action executed:
  - `gh pr ready 30`
  - `gh pr merge 30 --merge`
- Result: PR #30 merged at `a92687737e7a2a1856394b595410e985baafa9ba`

## Controller Judgment

PR #30 has been marked ready and merged. This completes the external disposition for the `return_attribution.v1` source-truth direct extraction work unit.

This disposition does not authorize source/test behavior changes, additional source-truth field-family extraction, candidate promotion, parser replacement, readiness, release, or any further PR mutation.

## Closed Scope

- `return_attribution.v1` proof-positive source-truth direct extraction is merged through PR #30.
- `product_essence.v1` remains previously merged as proof-positive source-truth direct extraction.
- `manager_profile.v1`, `investor_experience.v1`, `current_stage.v1`, and `core_risk.v1` remain unimplemented for source-truth direct extraction.
- Release/readiness remains `NOT_READY`.

## Next Entry

`FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction Planning Gate`

The next gate must start with planning and review for exactly one remaining field family. It must preserve proof-positive FDD admission, candidate-only fallback, no parser replacement, no `EvidenceSourceKind` expansion, no direct upper-layer candidate consumption, and `NOT_READY`.
