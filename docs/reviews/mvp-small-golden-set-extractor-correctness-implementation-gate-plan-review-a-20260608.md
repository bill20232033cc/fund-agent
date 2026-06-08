# Small Golden Set / Extractor Correctness Implementation Gate Plan Review A

Verdict: `BLOCKED`.

## Findings

- `[high] [A1]` `docs/reviews/mvp-small-golden-set-extractor-correctness-implementation-gate-plan-20260608.md:141` - `source identity` can be self-certified by offline fixture metadata. The accepted planning gate requires source document identity before correctness assertions, and `identity_status=matched` before numeric fields are accepted. The implementation plan must not let `pending_offline_fixture` or synthetic fixture metadata satisfy source identity. Minimal fix: require `matched` or row-level `unavailable`; `matched` must include `source_document_title`, source id or source-safe identifier, `resolved_fund_code`, `resolved_share_class` and `identity_evidence_anchor`, sourced from retained real excerpt anchors or pre-existing offline `FundDocumentRepository` metadata/public provenance. Synthetic fixtures may test parser mechanics but cannot satisfy source identity or numeric correctness.

## Open Questions

None.
