# Bond Risk Evidence Extractor / Anchor Hardening Slice 4 Plan Amendment

> Date: 2026-05-27
> Branch: `codex/local-reconciliation`
> Gate: Slice 4 plan amendment
> Role: planning worker
> Status: handoff-ready amendment; no implementation performed

## Source Of Truth

Read inputs:

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice4-implementation-20260527.md`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py` only to locate `FIELD_PRIORITY_BY_NAME`

Root fact:

- `FIELD_PRIORITY_BY_NAME` is defined in `fund_agent/fund/extraction_score.py`.
- `fund_agent/fund/extraction_snapshot.py` does not define `FIELD_PRIORITY_BY_NAME`.
- Original Slice 4 allowed files exclude `fund_agent/fund/extraction_score.py`.
- Original Slice 5 allowed files already include `fund_agent/fund/extraction_score.py`.

## Amendment Decision

Revised Slice 4 should proceed with snapshot schema / row projection only, and defer `bond_risk_evidence` P1 registration in `FIELD_PRIORITY_BY_NAME` to Slice 5.

Do not expand Slice 4 allowed files to include `fund_agent/fund/extraction_score.py`.

Justification from boundary and slicing principles:

- `extraction_snapshot.py` owns field ordering, snapshot row shape, field projection, non-comparable value exposure, first-anchor projection, and structured row metadata.
- `extraction_score.py` owns priority mapping, P0/P1 denominator membership, coverage / traceability aggregation, score applicability, and bond-risk blocker semantics.
- Adding `extraction_score.py` to Slice 4 would merge schema projection and scoring semantics into one slice, weakening the current small-slice boundary after a stop condition.
- Slice 5 already owns score applicability and already allows `extraction_score.py`; it is the correct place to make the P1 denominator change observable and test it.
- The temporary post-Slice-4 state is acceptable only as an intermediate local checkpoint: snapshot can emit `bond_risk_evidence`, but score still treats it as `UNMAPPED` until Slice 5. This must be called out in Slice 4 implementation and review artifacts, and Slice 5 must not be skipped.

## Revised Slice 4

### Allowed Files

Slice 4 allowed files remain:

- `fund_agent/fund/extraction_snapshot.py`
- `tests/fund/test_extraction_snapshot.py`

No other files are allowed in Slice 4.

### Implementation Requirements

Slice 4 must implement only snapshot projection behavior:

- Add `("risk", "bond_risk_evidence")` to `SNAPSHOT_FIELD_ORDER`, preferably immediately after `("holdings", "holdings_snapshot")` so the replacement risk field is adjacent to the field it contextualizes for bond funds.
- Build one `SnapshotRecord` for `bundle.bond_risk_evidence` using the same fund identity, classification, provenance, run metadata, and source CSV conventions as existing extracted-field records.
- Keep `bond_risk_evidence` out of `COMPARABLE_SUB_FIELDS_BY_FIELD`; `comparable_values` must remain `{}` and the field must not enter golden correctness denominator in this slice.
- Project `value_present=True` when `contract_status` is not `missing`; malformed or absent contract values must not be treated as present.
- Project `anchor_present=True` only when there is at least one stable group-level annual-report evidence anchor.
- Preserve first-anchor compatibility fields (`section_id`, `page`, `table_id`, `row_id`) using the first stable anchor when present.
- Expose stable structured snapshot status/group data so Slice 5 can avoid parsing free-form prose. Prefer explicit snapshot fields if the current `SnapshotRecord` schema supports extension in this gate:
  - `bond_risk_contract_status: str | None`
  - `bond_risk_satisfied_groups: tuple[str, ...]`
  - `bond_risk_missing_groups: tuple[str, ...]`
  - `bond_risk_weak_groups: tuple[str, ...]`
  - `bond_risk_ambiguous_groups: tuple[str, ...]`
- If explicit snapshot schema extension is judged too heavy by the implementing worker or reviewer, stop and return to controller. Do not fall back to a prose-only contract that would force Slice 5 to parse `note`.
- The `note` may include stable human-readable tokens for inspection, but it must not be the only machine-readable source for score applicability:
  - `contract_id=bond_risk_evidence.v1`
  - `contract_status=<satisfied|partial|missing>`
  - `satisfied_groups=...`
  - `missing_groups=...`
  - `weak_groups=...`
  - `ambiguous_groups=...`
- Do not edit `FIELD_PRIORITY_BY_NAME` in Slice 4.
- Do not add `bond_risk_evidence` P1 denominator assertions to Slice 4 tests.

### Revised Slice 4 Tests / Validation

Slice 4 tests must prove the temporary state is intentionally limited to snapshot projection:

- A complete bond evidence bundle produces a `bond_risk_evidence` row with:
  - `field_group="risk"`
  - `field_name="bond_risk_evidence"`
  - `value_present=True`
  - `anchor_present=True`
  - first-anchor compatibility fields populated from stable annual-report evidence.
- A partial bond evidence bundle exposes missing / weak / ambiguous groups through structured snapshot fields.
- A missing bond evidence bundle produces `value_present=False` and `anchor_present=False`.
- `bond_risk_evidence` has `comparable_values={}` and is absent from golden correctness comparable fields.
- Existing snapshot rows and ordering remain stable except for the deliberate insertion of `bond_risk_evidence`.
- No test should assert P1 priority, P1 coverage, P1 traceability, score applicability issue suppression, or `FIELD_PRIORITY_BY_NAME` behavior in Slice 4.

Recommended validation commands after Slice 4 implementation:

```bash
uv run pytest tests/fund/test_extraction_snapshot.py -q
uv run ruff check fund_agent/fund/extraction_snapshot.py tests/fund/test_extraction_snapshot.py
```

Optional non-regression validation if time allows:

```bash
uv run pytest tests/fund/test_extraction_score.py -q
```

Expected temporary result after Slice 4:

- Snapshot projection is complete and machine-readable.
- Score may still classify `bond_risk_evidence` as `UNMAPPED`.
- Existing bond-risk applicability blocker remains in force until Slice 5.
- This temporary state is acceptable only because Slice 5 explicitly inherits P1 registration and scoring semantics below.

## Slice 5 Inherited Requirement

Slice 5 must inherit an explicit non-optional requirement:

- Register `bond_risk_evidence` in `FIELD_PRIORITY_BY_NAME` as `P1` in `fund_agent/fund/extraction_score.py`.

This requirement is in addition to the original Slice 5 score applicability work.

Slice 5 must also consume Slice 4 structured snapshot status/group fields rather than parsing free-form `note`. If structured fields are missing, Slice 5 must stop and return to controller or require Slice 4 fix; it must not implement ad hoc prose parsing.

## Revised Slice 5 Tests / Validation

Slice 5 tests must prove final P1 semantics:

- `FIELD_PRIORITY_BY_NAME["bond_risk_evidence"] == "P1"`.
- A complete exact `bond_fund` snapshot record with all seven required groups satisfied has:
  - P1 priority in field score output.
  - 100% coverage for `bond_risk_evidence`.
  - 100% traceability for `bond_risk_evidence`.
  - no `bond_risk_evidence_missing` score applicability issue.
- Missing `bond_risk_evidence` row for an exact `bond_fund` keeps the current all-seven blocker.
- Partial bond evidence emits a blocker whose `required_evidence_groups` remains the full ordered seven-group contract while `missing_evidence_groups` contains only unsatisfied groups.
- Weak or ambiguous groups are unsatisfied for score applicability even when `value_present=True`.
- Anchorless accepted-looking groups are unsatisfied or rejected before score; they must not clear `baseline_blocking`.
- Non-bond funds ignore `bond_risk_evidence` for bond holdings replacement logic.
- Unknown or conflicting fund type remains fail-closed; do not use `bond_risk_evidence` to infer fund type.
- Existing FQ0-FQ6 quality gate thresholds, severities, and meanings remain unchanged.

Recommended validation commands after Slice 5 implementation:

```bash
uv run pytest tests/fund/test_extraction_score.py -q
uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py -q
uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py
```

Final expected result after Slice 5:

- `bond_risk_evidence` is a P1 field for score coverage / traceability.
- Complete evidence can clear the specific `bond_risk_evidence_missing` applicability blocker.
- Partial, weak, ambiguous, malformed, or anchorless evidence remains blocking for the unsatisfied groups.

## Confirmed Non-Goals And Guardrails

- No golden promotion.
- No baseline promotion.
- No FQ0-FQ6 weakening.
- No quality gate semantic weakening.
- No PDF/cache/source helper access.
- No direct production annual-report file access outside `FundDocumentRepository`.
- No source fallback strategy changes.
- No `extra_payload` usage.
- No Service/UI/Host/Agent package changes.
- No `dayu.host` or `dayu.engine` work.
- No renderer changes.
- No golden answer fixture changes.
- No QDII / FOF / `110020` artifact changes.
- No commit, push, PR creation, approval, merge, mark-ready action, or external GitHub mutation.

## Stop Conditions For Controller / Implementation Worker

Stop and return to controller if any of the following occurs:

- Slice 4 cannot expose machine-readable contract status and group fields without a public-contract/schema decision broader than this amendment.
- Slice 5 would need to parse free-form `note` prose to decide contract satisfaction.
- Implementing snapshot projection requires editing `extraction_score.py` before Slice 5.
- Implementing score applicability requires changing Service/UI/Host/Agent, FQ0-FQ6 semantics, source orchestration, PDF/cache helpers, golden fixtures, or baseline fixtures.
- Any validation suggests the temporary post-Slice-4 state changes existing score behavior beyond adding an unmapped snapshot field.
