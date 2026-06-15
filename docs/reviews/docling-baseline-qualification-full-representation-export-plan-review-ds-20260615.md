# Docling Baseline Qualification Full Representation Export Plan Review - DS - 2026-06-15

Review target: `docs/reviews/docling-baseline-qualification-full-representation-export-plan-20260615.md`

Verdict: `PASS_WITH_FINDINGS`

| Severity | Evidence | Recommendation | Blocking |
|---|---|---|---|
| Low | Plan §6 puts the harness inside `fund_agent/fund/documents/candidates/representation_export.py`, keeps candidate internals out of public `fund_agent.fund.documents` exports, and forbids Service/UI/Host/renderer/quality-gate access. Plan §7 nevertheless allows the later evidence gate to consume explicit staged PDF paths under `cache/eid-artifact-capture/...` instead of production-shaped `cache/pdf` or `FundDocumentRepository`. This is consistent with the accepted staged-artifact controller judgment, but it is an exception-shaped diagnostic route. | Controller closeout should state that explicit staged paths are accepted only as Fund documents candidate-harness inputs for this evidence chain. They must not become a general parser/file-access pattern, production API, Service/UI/Host input, or replacement for `FundDocumentRepository`. | No |
| Low | Plan §7 defines required evidence records and output artifacts, but does not give an explicit command allowlist for the full export evidence gate comparable to earlier acquisition/capture gates. It says exact command lines must be recorded, and §9 stops if ad hoc script design is needed, which is mostly sufficient but leaves the execution surface implicit. | Before evidence execution, controller should require the accepted harness command or module entrypoint to be named explicitly, including allowed input manifest path and allowed output directory. This can be closed in the implementation plan/evidence closeout. | No |

## Accepted facts

- The plan preserves `NOT_READY` in status, non-goals and final verdict.
- The plan keeps Docling, pdfplumber and EID HTML render as candidate representation routes only.
- The plan does not claim raw XML/XBRL availability, source truth, field correctness, taxonomy compatibility, baseline qualification, production integration or release/readiness.
- The plan preserves EID single-source/no fallback and explicitly forbids Eastmoney, fund-company website, CNINFO and other non-EID fallback.
- S1 is treated as existing reference JSON only.
- S2 is deferred or optional pending provenance decision; S3 is deferred until hash/provenance resolution.
- S4/S5/S6 correctly use accepted staged EID PDF paths and do not rely on production-shaped `cache/pdf`.
- Routing to a narrow candidate-only export harness before evidence export is reasonable: it avoids one-off scripts, forces reproducible manifest/envelope checks and keeps implementation inside Fund documents candidate internals.
- The allowed implementation write set is narrow and avoids production repository/source/cache/parser/Service/Host/UI/quality-gate behavior changes.

## Residuals

- Candidate export harness acceptance is still required before full export evidence.
- Explicit staged path consumption remains a candidate-evidence exception, not a production document-access rule.
- EID HTML render for S4/S5/S6 remains unavailable unless a separate bounded discovery gate accepts render URLs; blocked JSON is the correct default.
- Representation completeness metrics will still not prove field correctness, source truth, Docling baseline qualification or readiness.
