# Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Fix Evidence - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Section-context Enrichment No-live Implementation Fix Gate`
Fix worker: AgentCodex
Controller: AgentController
Release/readiness: `NOT_READY`

## Scope

This fix evidence covers only controller-accepted findings from implementation review:

- DS finding 01: final stable section span could absorb pages after a later unindexed section.
- MiMo finding 02: duplicate same-page distinct top-level body section nodes were not marked duplicate.

Allowed write set used:

- `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`
- `tests/fund/documents/test_docling_evidence_anchor_mapping.py`

No docs/control/design/README/report/cache/source acquisition/repository/parser/production `EvidenceAnchor`/Service/Host/UI/renderer/quality gate/provider/LLM/readiness/release/PR/push/merge files or actions were changed by the fix worker.

## Fix Summary

- Added later positive section-node pages as section span boundary pages so a supported stable span stops before a later unsupported/unindexed section boundary.
- Preserved open-ended final span only when there is no later section-node boundary.
- Tightened duplicate detection so multiple distinct non-child node IDs for the same annual section fail closed as `duplicate_section_heading`, even on the same page.
- Kept child headings from triggering duplicate-section blocking.
- Added tests for unsupported later-section boundary blocking and same-page duplicate top-level node blocking.

## Validation

Controller re-ran:

```text
uv run pytest tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Result:

```text
36 passed in 0.55s
```

```text
uv run ruff check fund_agent/fund/documents/candidates/evidence_anchor_mapping.py tests/fund/documents/test_docling_evidence_anchor_mapping.py
```

Result:

```text
All checks passed!
```

```text
git diff --check
```

Result: passed.

## Deferred / Rejected Review Findings

| Finding | Disposition | Reason |
| --- | --- | --- |
| Public single-block API rebuilds `SectionIndex` | DEFER | Correctness is unaffected; public API signature remains stable; document-level API builds once as required. |
| Child section heading detection may miss non-dot child headings | DEFER | Current behavior fails closed as duplicate rather than producing mapped output; real-artifact frequency belongs to re-evidence. |
| Performance of per-cell duplicate tuple scan | DEFER | Pre-existing small-scope cost; not part of accepted fix set. |

## Final Status

```text
FIXED_AND_VALIDATED_NO_LIVE_NOT_READY
```
