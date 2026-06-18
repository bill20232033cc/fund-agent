# Fixture Promotion State Year-aware Schema / Parser Plan

Date: 2026-06-13

Gate: `Fixture Promotion State Year-aware Schema / Parser Planning Gate`

Role: planning worker, not controller

Verdict: `IMPLEMENTATION_REQUIRED_BEFORE_YEAR_SPECIFIC_PROMOTION_PROOF`

Readiness state: `NOT_READY`

Allowed write for this gate: this plan artifact only.

## 1. Goal

Decide whether fixture promotion state must become year-aware before downstream
readiness can continue without misusing fund-code-only promotion state as
`004393 / 2025`-specific promotion proof.

The decision is:

- If downstream readiness needs to count fixture promotion as proof for a
  specific `(fund_code, report_year)`, implementation is required before that
  readiness gate proceeds.
- If controller explicitly defers fixture promotion proof, downstream work may
  continue only by routing around promotion-state claims, preserving
  `NOT_READY`, and keeping any `004393 / 2025 promoted fixture` claim out of
  scope.

## 2. Non-goals

- Do not implement source, test, runtime, golden, fixture, parser, schema or
  README changes in this planning gate.
- Do not promote fixtures.
- Do not edit golden-answer content, fixture content, promotion state files,
  control docs or design docs.
- Do not run live/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/
  release/PR commands.
- Do not cleanup, delete, archive, stage, commit, push, open PR or change
  external state.
- Do not make release/readiness claims.

## 3. Accepted Facts

| Fact | Status | Direct basis |
|---|---|---|
| Current gate is planning-only and release/readiness remains `NOT_READY`. | Accepted | `docs/current-startup-packet.md`; `docs/implementation-control.md` |
| The seven accepted rows are tracked golden content for `004393 / 2025`; fee rows, `turnover_rate`, skipped rows and deferred rows remain excluded. | Accepted | `docs/implementation-control.md`; controller judgment `mvp-004393-2025-fixture-promotion-strict-golden-coverage-evidence-controller-judgment-20260613.md` |
| Strict golden coverage is already year-aware for current tracked JSON surface. | Accepted; no new implementation needed here | `StrictGoldenCoverage.fund_years`; `_load_strict_golden_coverage()`; `_derive_strict_golden_coverage()`; tests `test_preflight_blocks_strict_golden_absence_and_fund_miss` and `test_preflight_accepts_strict_golden_matching_year_and_reserves_partial_code` |
| Current fixture promotion parser is fund-code-only. | Accepted residual | `_load_fixture_promotion_states()` returns `dict[str, PromotionState]`; `_derive_fixture_promotion_state()` looks up `fixture_states.get(artifact.fund_code)` |
| Current fund-code-only fixture promotion state cannot prove `004393 / 2025`-specific promotion. | Blocking for promotion claim only | Accepted controller judgment §2/§5 |
| Current tests cover strict-golden year awareness and promotion absence, but do not cover a same-fund different-year promotion manifest. | Accepted test gap for implementation gate | `tests/fund/test_golden_readiness_preflight.py` |

## 4. Implementation-needed Decision

Implementation is required before any later gate may treat fixture promotion
state as year-specific proof.

Reason:

- `FundArtifactInput` and `CoverageDispositionEntry` already carry
  `report_year`.
- Strict golden coverage already checks exact `(fund_code, report_year)`.
- Fixture promotion currently collapses entries to `fund_code`; a
  fund-code-only promoted state for `004393` would also appear promoted for
  `004393 / 2025` even if the accepted promotion was for another year.
- Therefore, the unsafe state is not missing evidence only; it is a parser and
  identity-contract gap.

Allowed defer condition:

- Controller may defer implementation only if the next readiness path explicitly
  excludes fixture promotion as a proof source, keeps rows blocked/deferred by
  promotion-state residual, and preserves release/readiness as `NOT_READY`.
- Any report, artifact or controller judgment in that defer route must state
  that fixture promotion is not accepted as `004393 / 2025` proof.

## 5. Affected Files If Implementation Is Authorized Later

Required implementation files:

- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py`

Required documentation files if those source/test files are changed:

- `fund_agent/fund/README.md`
- `tests/README.md`

Do not touch `docs/design.md`, `docs/implementation-control.md`,
`docs/current-startup-packet.md`, golden answer files, fixture files or fixture
promotion manifest content in the implementation slice unless a later controller
gate separately authorizes that write.

## 6. Year-aware Fixture Promotion Contract

### 6.1 Manifest Schema

Introduce a year-aware fixture promotion manifest schema:

```json
{
  "schema_version": "fund-agent.fixture-promotion-state.year-aware.v1",
  "accepted_as_of": "YYYY-MM-DD",
  "source_artifacts": ["docs/reviews/...md"],
  "entries": [
    {
      "fund_code": "004393",
      "report_year": 2025,
      "promotion_state": "promoted_fixture",
      "promotion_identity": "fund_year",
      "evidence_artifacts": ["docs/reviews/...md"]
    }
  ]
}
```

Required top-level fields:

- `schema_version`: exactly
  `fund-agent.fixture-promotion-state.year-aware.v1`
- `accepted_as_of`: string
- `source_artifacts`: list of strings
- `entries`: list of objects

Allowed top-level optional field:

- none for the first implementation slice; reject unknown top-level keys to
  avoid implicit extra payload.

Required entry fields:

- `fund_code`: string
- `report_year`: integer
- `promotion_state`: one of `not_promoted`, `promoted_fixture`, `unknown`
- `promotion_identity`: exactly `fund_year`
- `evidence_artifacts`: list of strings

Rationale for `promotion_identity`: schema_version alone does not prevent a
future manifest author from accidentally writing fund-code-only entries under
the year-aware schema version. Requiring `promotion_identity == fund_year` on
every entry makes identity intent explicit per-entry and fails closed on
mismatch.

Allowed entry optional fields:

- none for the first implementation slice; reject unknown entry keys.

Invariants:

- Parser identity key is `(fund_code, report_year)`, not fund code alone.
- Duplicate `(fund_code, report_year)` entries are invalid and must raise
  `ValueError`.
- Same `fund_code` with different `report_year` entries is valid and must not
  collapse.
- `promoted_fixture` is accepted only for exact `(fund_code, report_year)`.
- `unknown` or missing exact year remains blocking.
- Non-digit slot rows continue to return `not_applicable`.

### 6.2 Internal Parser Shape

Replace the current `dict[str, PromotionState] | None` parser result with a
small typed shape, for example:

```python
@dataclass(frozen=True, slots=True)
class FixturePromotionStates:
    """fixture promotion state identity index."""

    fund_year_states: Mapping[tuple[str, int], PromotionState]
    legacy_fund_states: Mapping[str, PromotionState]
```

Implementation detail may use `dict` internally, but public call flow must make
identity scope explicit. Do not keep a plain `dict[str, PromotionState]` as the
only parser output after this change.

### 6.3 Row Derivation Contract

`_derive_fixture_promotion_state()` must:

1. Return `not_applicable` for non-digit `artifact.fund_code`.
2. Return `absent` + blocker `fixture_promotion_absent` when no manifest path or
   no parsed states exist.
3. Check exact key `(artifact.fund_code, artifact.report_year)` first.

Exact mapping after step 3:

| Input condition | `state` output | `promotion_state` output | Blocker code |
|---|---|---|---|
| Exact key value is `promoted_fixture` | `promoted_fixture` | `promoted_fixture` | none |
| Exact key value is `not_promoted` | `not_promoted` | `not_promoted` | `fixture_promotion_absent` |
| Exact key value is `unknown` | `unknown` | `unknown` | `fixture_promotion_unknown` |
| Exact key missing and legacy fund-code state exists | `legacy_fund_only` | `unknown` | `fixture_promotion_legacy_fund_only` |
| Exact key missing and no legacy fund-code state exists | `unknown` | `unknown` | `fixture_promotion_unknown` |

Recommended message for legacy blocker:

```text
004393 fixture promotion state is fund-code-only and cannot prove 004393 / 2025 promotion.
```

## 7. Legacy Fund-code-only Manifest Handling

Decision: keep legacy parsing for diagnostics only; never use legacy fund-code-
only state as year-specific promotion proof.

Legacy accepted inputs:

- Existing `entries` where each entry has `fund_code` and `promotion_state` but
  no `report_year`.
- Existing top-level mapping `{ "004393": "promoted_fixture" }`.

Legacy behavior:

- Parser stores these in `legacy_fund_states`.
- Row derivation emits blocker `fixture_promotion_legacy_fund_only` when a
  target row has only legacy state.
- Output `promotion_state` should be `unknown` for legacy-only exact-year
  evaluation, unless reviewer prefers preserving the raw enum while still
  blocking. The safer default is `unknown`.
- No automatic default to `DEFAULT_REPORT_YEAR`; fund-code-only state is not
  year-aware even for 2024.

Rejected behavior:

- Do not silently translate legacy fund-code-only entries into
  `(fund_code, DEFAULT_REPORT_YEAR)`.
- Do not let legacy `promoted_fixture` satisfy `004393 / 2025`.
- Do not mutate or migrate existing manifest files in this implementation gate.

## 8. Minimal Implementation Slices

### Slice 1: Parser identity and legacy fail-closed handling

Allowed files:

- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py`

Steps:

1. Add `FIXTURE_PROMOTION_STATE_SCHEMA_VERSION =
   "fund-agent.fixture-promotion-state.year-aware.v1"`.
2. Add typed parser result such as `FixturePromotionStates`.
3. Change `_load_fixture_promotion_states()` return type to
   `FixturePromotionStates | None`.
4. For year-aware schema:
   - require top-level schema version;
   - reject unknown top-level and entry keys;
   - require `report_year`;
   - require `promotion_identity == "fund_year"`;
   - reject duplicate `(fund_code, report_year)`;
   - populate `fund_year_states`.
5. For legacy manifests:
   - preserve current accepted shapes;
   - populate `legacy_fund_states`;
   - do not map to any year.
6. Update `_derive_fixture_promotion_state()` to use exact fund-year lookup and
   fail closed on legacy-only identity.
7. Update exactly these type references and call-path handoffs for the new
   parser shape:
   - `run_golden_readiness_preflight()` local `fixture_states`;
   - `_build_readiness_row()` parameter `fixture_states`;
   - `_derive_fixture_promotion_state()` parameter `fixture_states` and internal
     lookup logic.
   Do not change `_derive_strict_golden_coverage()`.

Completion signal:

- Same-fund different-year fixture promotion can be represented without
  collapse.
- Legacy fund-code-only promoted state blocks as `fixture_promotion_legacy_fund_only`.

Stop conditions:

- If implementation requires changing actual fixture/golden files, stop and
  return to controller.
- If existing callers outside `run_golden_readiness_preflight()` depend on the
  old dict shape, stop and route as public contract expansion.

### Slice 2: Targeted tests

Allowed files:

- `tests/fund/test_golden_readiness_preflight.py`

Required tests:

1. `test_preflight_accepts_year_aware_fixture_promotion_matching_year`
   - Build a year-aware promotion manifest with `004393 / 2025` promoted.
   - Use golden answer with `report_year=2025`.
   - Run one artifact for `004393 / 2025`.
   - Assert row fixture state is `promoted_fixture`.
   - Assert no `fixture_promotion_absent`,
     `fixture_promotion_unknown` or `fixture_promotion_legacy_fund_only`
     blocker exists.

2. `test_preflight_rejects_fixture_promotion_wrong_year`
   - Build year-aware manifest with `004393 / 2024` promoted only.
   - Run artifact for `004393 / 2025`.
   - Assert row is not ready because exact promotion year is missing.
   - Assert blocker is `fixture_promotion_unknown` or the final chosen exact
     missing-year blocker.
   - Assert not promoted for `004393 / 2025`.

3. `test_preflight_blocks_legacy_fund_code_only_fixture_promotion`
   - Build legacy manifest `{ "004393": "promoted_fixture" }` or legacy
     entries without `report_year`.
   - Run artifact for `004393 / 2025`.
   - Assert blocker `fixture_promotion_legacy_fund_only`.
   - Assert no ready/pass result is derived from legacy state.

4. `test_preflight_rejects_duplicate_year_aware_fixture_promotion_entry`
   - Build two entries with the same `(fund_code, report_year)`.
   - Assert `ValueError` and message mentions duplicate identity.

5. `test_preflight_rejects_year_aware_fixture_promotion_unknown_field`
   - Add an unknown top-level or entry field.
   - Assert `ValueError` and message mentions unknown field.

6. `test_preflight_rejects_year_aware_fixture_promotion_wrong_identity`
   - Build a year-aware manifest entry using `promotion_identity:
     "fund_code_only"`.
   - Assert `ValueError`.

Optional helper:

- Add `_write_fixture_promotion_state(path, entries, schema_version=...)` test
  helper near existing `_write_golden()`.

Completion signal:

- Tests prove exact year pass, wrong-year block, legacy fail-closed, duplicate
  rejection and unknown-field rejection.

### Slice 3: README sync

Allowed files:

- `fund_agent/fund/README.md`
- `tests/README.md`

Steps:

1. In Fund README, add or update the readiness preflight note to state that
   fixture promotion identity is `(fund_code, report_year)` for year-aware
   manifests and legacy fund-code-only manifests are diagnostic-only, not
   readiness proof.
2. In tests README, add or update the testing convention for readiness/golden
   parser tests: assert value-level identity behavior, not only artifact
   existence.

Stop condition:

- If neither README currently has a relevant section and adding one would
  broaden documentation beyond the implementation surface, record a docs
  residual instead of creating broad docs.

## 9. Targeted Validation Commands

For the later implementation gate only:

```bash
uv run pytest tests/fund/test_golden_readiness_preflight.py -q
```

Expected assertions:

- Existing strict golden year-aware tests still pass.
- Existing fixture promotion absence test still passes.
- New exact `(fund_code, report_year)` promotion test passes.
- New wrong-year and legacy fund-code-only tests fail closed.
- Duplicate and unknown-field schema tests raise `ValueError`.

Optional static check if implementation changes type signatures enough to risk
typing regressions:

```bash
uv run mypy fund_agent/fund/golden_readiness_preflight.py
```

Do not run analyze/checklist/readiness/release/live/provider/LLM/PDF/FDR
commands for this work unit.

## 10. Docs Decision

This planning gate writes no design/control/README changes.

If later implementation touches `fund_agent/fund/golden_readiness_preflight.py`,
README sync is required by project rules unless the implementation artifact
records a precise reason that no relevant README surface exists. The default
plan is to update:

- `fund_agent/fund/README.md`
- `tests/README.md`

Do not update:

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`

Control/design docs remain controller-owned truth surfaces for a later status
sync gate, not this implementation slice.

## 11. Stop Conditions

Planning worker stop conditions:

- Any need to edit source/test/runtime/golden/fixture/control/design docs.
- Any need to run live/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/
  release/PR commands.
- Any ambiguity about whether legacy fund-code-only state may count as
  year-specific proof. Current plan answers no; changing that requires
  controller decision.
- Any proposal to promote fixtures or mutate promotion state content.

Implementation worker stop conditions:

- A required caller or artifact outside the listed affected files depends on
  the old `dict[str, PromotionState]` parser shape.
- Existing fixture promotion manifests in tracked fixtures require migration
  before tests can pass.
- Reviewers require accepting legacy fund-code-only state for 2024. That would
  conflict with the fail-closed identity contract above.
- Test changes require golden-answer or fixture content edits.

## 12. Review Checklist

Plan review should verify:

- The plan does not implement anything in this gate.
- The implementation decision does not claim strict golden coverage needs work.
- The plan clearly separates strict golden year-aware coverage from fixture
  promotion fund-code-only parser residual.
- The contract keys promotion identity by `(fund_code, report_year)`.
- Legacy fund-code-only manifest handling is fail-closed and cannot satisfy
  `004393 / 2025`.
- Implementation slices are small and have exact allowed files.
- Tests check value-level behavior: matching year, wrong year, legacy manifest,
  duplicate identity and unknown fields.
- Docs decision follows repo README trigger rules without touching control/design
  docs.
- Readiness/release remains `NOT_READY`.

Code review for a later implementation should verify:

- No fixture/golden/promotion content was edited.
- No live/provider/analyze/checklist/readiness/release command was introduced.
- Parser rejects unknown fields and duplicate fund-year entries.
- `DEFAULT_REPORT_YEAR` is not used to promote legacy fixture state.
- Output row and blockers make legacy identity residual visible.

## 13. Next Gate Recommendation

Recommended next gate:

```text
Fixture Promotion State Year-aware Schema / Parser Plan Review Gate
```

If the plan is accepted after review, route to a narrow implementation gate for
the files listed in §5. Do not enter readiness/release or fixture promotion
until the year-aware parser implementation is accepted, or until controller
explicitly chooses the defer route that excludes fixture promotion proof and
keeps release/readiness `NOT_READY`.

## 14. Worker Self-check

- Current gate / role: planning worker for
  `Fixture Promotion State Year-aware Schema / Parser Planning Gate`, not
  controller.
- Source of truth: `AGENTS.md`, `docs/current-startup-packet.md`,
  `docs/implementation-control.md`, accepted controller judgment, target source
  and target tests were read.
- Scope boundary: only this plan artifact is written.
- Stop conditions: no blocking question remains for this plan; implementation
  is required only before year-specific promotion proof.
- Evidence and validation: no runtime validation is run in this planning gate;
  later exact command is specified.
- Next action: stop after reporting artifact path and verdict; do not enter
  implementation.

Self-check: pass
