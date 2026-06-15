# Docling Baseline Qualification Scope Decision Controller Judgment - 2026-06-16

Gate: `Docling Baseline Qualification Scope Decision Gate`
Controller: AgentController
Release/readiness: `NOT_READY`
Verdict: `SELECT_CONTROLLED_SAME_SOURCE_REFERENCE_ACQUISITION_NOT_READY`

## Scope

This gate selects the next route after accepted S4/S5/S6 `unsafe_metadata` blocked evidence.

The user selected option 2: open a controlled same-source reference acquisition route for S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024`.

This is a route decision only. It does not run live/EID/PDF/source acquisition, does not perform correctness review, does not modify source/tests/runtime behavior, and does not change `FundDocumentRepository`, source policy, parser behavior, EvidenceAnchor schema, Service, Host, UI, renderer, quality gate, provider/LLM route, readiness, release, PR or merge state.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `AGENTS.md` | Rule and boundary truth source |
| `docs/design.md` | Design truth source |
| `docs/current-startup-packet.md` | Current startup/control packet |
| `docs/implementation-control.md` | Current control truth |
| `docs/reviews/docling-same-source-reference-cache-metadata-evidence-controller-judgment-20260616.md` | Accepted blocked metadata evidence |
| `docs/reviews/docling-cache-metadata-evidence-control-sync-controller-judgment-20260616.md` | Control sync into decision gate |

## Accepted Current Facts

| Fact | Status |
| --- | --- |
| `004393 / 2025` Docling bounded pilot | Accepted candidate-layer selected field-family pilot: 21/21 selected facts matched same-source repository-loaded PDF bbox crop excerpts |
| S4 `006597 / 2024` | Candidate JSON exists, but same-source reference proof is blocked; metadata status `unsafe_metadata`, reason `selected_source_not_eid` |
| S5 `017641 / 2024` | Candidate JSON exists, but same-source reference proof is blocked; metadata status `unsafe_metadata`, reason `source_not_eid` |
| S6 `110020 / 2024` | Candidate JSON exists, but same-source reference proof is blocked; metadata status `unsafe_metadata`, reason `source_not_eid` |
| Multi-sample Docling correctness expansion | Still blocked until same-source reference proof is accepted |
| EID public availability for S4/S5/S6 | Not disproven by current metadata evidence |
| Docling baseline | Candidate-only; not production parser replacement |

## Decision

The controller accepts the user's selection of option 2.

Proceed to a planning gate:

```text
Docling Controlled Same-source Reference Acquisition Planning Gate
```

The planning gate must define a bounded acquisition/evidence route for S4/S5/S6 before any live/EID/PDF/source command is executed.

## Binding Requirements For Next Gate

The next planning gate must define:

- exact sample matrix: S4 `006597 / 2024`, S5 `017641 / 2024`, S6 `110020 / 2024`;
- allowed acquisition path through current accepted repository/source boundaries;
- whether the evidence worker may call `FundDocumentRepository.load_annual_report()` and under what refresh/cache policy;
- how to prove `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false`;
- identity checks for `fund_code`, `document_year`, `report_type`, document kind, safe source metadata and document hash/identity fields if available;
- accepted output artifact shape for same-source reference proof;
- stop rules for `schema_drift`, `identity_mismatch`, `integrity_error`, auth/captcha, non-EID source, fallback use or ambiguous metadata;
- non-claims preserving candidate-only status and `NOT_READY`.

## Non-goals

- Do not reintroduce Eastmoney, fund-company website, CNINFO or any non-EID fallback.
- Do not treat current unsafe cache metadata as proof.
- Do not declare EID unavailable for S4/S5/S6.
- Do not run correctness review in the planning gate.
- Do not promote Docling to global baseline.
- Do not replace the production parser.
- Do not change source policy.
- Do not claim source truth, full field correctness, taxonomy compatibility, readiness, release or PR readiness.

## Deferred Routes

| Route | Status |
| --- | --- |
| Narrow to `004393 / 2025` bounded pilot only | Deferred by user selection of option 2 |
| Defer Docling baseline qualification and return to another product mainline | Deferred by user selection of option 2 |
| Direct multi-sample correctness comparison | Still blocked until same-source reference proof is accepted |

## Final Verdict

```text
VERDICT: SELECT_CONTROLLED_SAME_SOURCE_REFERENCE_ACQUISITION_NOT_READY
```
