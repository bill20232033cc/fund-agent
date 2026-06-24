# Code Review

## Scope

- Mode: current changes / aggregate deepreview after fix
- Branch or PR: `evidence-confirm-productionization`
- Base: `main` for current changes; focused aggregate review over EC-P3 semantic entailment implementation and accepted after-fix scope
- Review time: `2026-06-22T17:29:05+0800`
- Output file: `docs/reviews/code-review-codex-ec-p3-aggregate-20260622.md`
- Included scope:
  - `fund_agent/fund/evidence_confirm_semantic.py`
  - `tests/fund/test_evidence_confirm_semantic.py`
  - `fund_agent/fund/README.md`
  - `tests/README.md`
  - `docs/reviews/evidence-confirm-productionization-ec-p3-semantic-entailment-plan-20260622.md`
  - `docs/reviews/code-review-20260622-172254.md`
- Excluded scope:
  - unrelated untracked docs/scripts in the working tree
  - provider/live, Service/UI/Host/renderer/quality-gate implementation paths, because this gate explicitly keeps them as later work
- Parallel review coverage: 无

## Findings

未发现实质性问题。

## Evidence Checked

- `confirm_semantic_entailment()` indexes V2 fact results by `(fact_id, source_field_id)` and calls `_confirm_single_claim()` for sorted explicit claims.
- `_confirm_single_claim()` returns `deterministic_gate_failed` before client invocation when the V2 fact result is missing, the V2 hard gate failed, `source_support` / `missing_evidence` / `proof_boundary` are not `pass`, or `value_match` is `fail`.
- `_bounded_excerpts_for_claim()` intersects claim anchors with deterministic `matched_anchor_ids`; the after-fix test `test_semantic_missing_bounded_excerpt_does_not_call_client()` covers the no-excerpt guard and asserts no client call.
- `_severity_for_judgment()` maps `not_applicable` to `info` before applying `hard_gate.status == "warn"`, so anchor_precision warning does not elevate `not_applicable`; `test_semantic_not_applicable_stays_info_under_anchor_precision_warn()` covers this behavior.
- Import-isolation test statically checks the semantic module does not import Service, Host, UI, config, documents, renderer or quality-gate modules.
- Fund README states semantic entailment is no-live, explicit-claim/client-protocol backed, cannot override deterministic V2 failures, and leaves provider/live semantic evidence, Service/UI/renderer/quality-gate integration, default-on policy and release/readiness to later gates.
- The EC-P3 plan and previous review artifact do not claim provider/live, release or readiness completion.

## Validation

- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_semantic.py -q` -> `60 passed`
- `uv run ruff check fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py` -> passed
- `git diff --check -- fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py fund_agent/fund/README.md tests/README.md` -> passed

## Open Questions

- 无

## Residual Risk

- Same-run binding between `EvidenceConfirmResultV2` and the `references` tuple remains a later integration concern because V2 currently carries matched anchor ids, not excerpt hashes or reference identities.
- Provider-backed semantic quality, Service/renderer claim extraction, quality-gate consumption, default-on policy and release/readiness remain later gates.
