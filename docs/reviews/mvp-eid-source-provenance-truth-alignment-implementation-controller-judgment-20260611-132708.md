# EID Source Provenance Truth Alignment Implementation Controller Judgment

## Scope

- Gate: `EID source provenance truth alignment gate`
- Classification: `standard`
- Judgment time: `2026-06-11 13:27:08`
- Controller role: phaseflow / gateflow controller
- Verdict: `ACCEPT_WITH_RESIDUALS`

## Truth Inputs

- `AGENTS.md`: current source policy is EID single-source; production annual-report access must remain behind `FundDocumentRepository`; fallback/source expansion and live commands require separate reviewed gates.
- `docs/design.md`: design truth still records current EID single-source no-live implementation as accepted current fact, but also retains older wording such as `mode=single_source_only`.
- `docs/implementation-control.md`: current active gate is `EID source provenance truth alignment gate`; `docs/design.md` edits are out of scope for this gate.
- `docs/current-startup-packet.md`: current mainline is EID source provenance truth alignment; live EID/PDF/FDR/network and fallback/source expansion are not authorized.
- Plan: `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-20260611-130159.md`
- Plan controller judgment: `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-controller-judgment-20260611-130744.md`
- Implementation evidence: `docs/reviews/mvp-eid-source-provenance-truth-alignment-implementation-evidence-20260611.md`
- MiMo implementation review: `docs/reviews/mvp-eid-source-provenance-truth-alignment-implementation-review-mimo-20260611-132347.md`
- DS implementation review: `docs/reviews/mvp-eid-source-provenance-truth-alignment-implementation-review-ds-20260611-132446.md`

## Implementation Write Set

Accepted source/test/doc write set:

- `fund_agent/fund/source_provenance.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_source_provenance.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_data_extractor.py`

No `docs/design.md`, root `README.md`, `pyproject.toml`, `.gitignore`, repository/cache/model source, runtime artifact, live evidence, golden/readiness or release-state file was modified by the implementation diff.

## Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `ACCEPT` | Accepted as independent implementation review. No blocking findings. Residuals are deferred below. |
| AgentDS | `ACCEPT` | Accepted as independent implementation review. No blocking findings. Residuals are deferred below. |

Reviewer-channel note: both tmux reviewers initially attempted to write review artifacts despite the review-only handoff. The writes were limited to `docs/reviews/` review artifacts and did not modify source/tests/runtime behavior. Controller rejected further write attempts and collected final direct pane verdicts. This is a process residual for future handoff discipline, not an implementation blocker.

## Acceptance Evidence

- `uv run pytest tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q` -> `97 passed in 0.86s`
- `uv run ruff check fund_agent/fund/source_provenance.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/documents/sources.py tests/fund/test_source_provenance.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py` -> `All checks passed!`
- `rg -n "primary_then_fallback" fund_agent tests --glob '*.py'` -> only `tests/fund/test_source_provenance.py:337` and `tests/fund/test_source_provenance.py:360`, both in the required negative assertion test.
- `git diff --name-only` -> exactly the eight accepted implementation files listed above.
- `git diff --check` -> no output.

## Controller Findings

- ACCEPT: Public provenance schema is now `repository_source_provenance.v2` and adds `selected_source`, `source_mode` and `fallback_enabled`.
  - Basis: `fund_agent/fund/source_provenance.py`; MiMo/DS reviews; focused tests.
- ACCEPT: Current EID metadata path projects current policy as `single_source_only` without emitting `primary_then_fallback`.
  - Basis: `source_provenance.py`; negative assertion test; `rg` result above.
- ACCEPT: Legacy or metadata-absent paths remain `legacy_or_unknown` and do not masquerade as current EID policy.
  - Basis: default and legacy tests in `tests/fund/test_source_provenance.py`; DS review evidence.
- ACCEPT: Snapshot record and summary propagation include the v2 additive fields without changing score semantics.
  - Basis: `fund_agent/fund/extraction_snapshot.py`; `tests/fund/test_extraction_snapshot.py`; `tests/fund/test_extraction_score.py`.
- ACCEPT: `fund_agent/fund/documents/sources.py` change is docstring-only and does not reintroduce fallback/source acquisition.
  - Basis: diff review; MiMo/DS reviews.
- ACCEPT: `fund_agent/fund/README.md` now documents v2 additive public provenance fields and states `source_strategy` is a compatibility alias, not fallback authorization.
  - Basis: README line 196; plan Slice 6.

## Residuals

| Residual | Disposition | Owner / next handling |
|---|---|---|
| `docs/design.md` still contains older v1/current policy wording such as `mode=single_source_only`. | `DEFER` | Separate `design-truth-sync gate`; design doc edits were forbidden in this gate. |
| `fund_agent/fund/README.md` line 73 still uses prose `mode=single_source_only` instead of `source_mode=single_source_only`. | `DEFER` | Include in the same design-truth-sync or documentation consistency gate; non-blocking because README line 196 documents v2 field semantics and no fallback authorization is introduced. |
| `AnnualReportSourceName` still includes `eastmoney`. | `DEFER` | Source-candidate/fallback design scope; not a current production fallback and not modified by this gate. |
| tmux reviewers attempted review artifact writes after review-only handoff. | `ACCEPTED_RESIDUAL` | Future handoffs must restate no-write boundaries and controller owns artifact persistence. Does not invalidate the review content. |

## Final Judgment

`ACCEPT_WITH_RESIDUALS`.

The implementation satisfies the accepted plan and current control truth: public EID source provenance now exposes current EID single-source fields without reintroducing Eastmoney/fund-company/CDN/CNINFO fallback, without live EID/network/PDF/FDR/provider execution, and without modifying out-of-scope source/test/runtime surfaces. The remaining findings are explicitly deferred and do not block this gate.

Next control step: create a local accepted checkpoint for this gate, update `docs/current-startup-packet.md` and `docs/implementation-control.md`, and set the next mainline entry to `LLM execution request validation ordering gate`.
