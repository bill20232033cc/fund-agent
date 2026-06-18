# Fixture Promotion Year-aware Parser Downstream Evidence

Date: 2026-06-13

Gate: `Fixture Promotion Year-aware Parser Downstream Evidence Gate`

Verdict: `EVIDENCE_COLLECTED_NOT_READY`

## Scope

This evidence gate is non-live and downstream-only. It verifies that
`run_golden_readiness_preflight()` consumes fixture promotion state through the
accepted exact `(fund_code, report_year)` identity and that legacy fund-code-only
promotion state cannot prove `004393 / 2025` promotion.

No source, tests, runtime behavior, golden-answer content, fixture content,
fixture promotion content, live command, provider command, LLM command,
`analyze`, `checklist`, readiness/release command, PR action, push, merge,
cleanup, delete, archive or external-state action was performed.

## Inputs

- Rule truth: `AGENTS.md`
- Control truth: `docs/implementation-control.md`
- Startup truth: `docs/current-startup-packet.md`
- Design truth: `docs/design.md`
- Accepted implementation checkpoint: `6d8db2f`
- Accepted implementation judgment:
  `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-implementation-controller-judgment-20260613.md`
- Downstream API under evidence:
  `fund_agent/fund/golden_readiness_preflight.py::run_golden_readiness_preflight`

## Preflight Status

Command:

```text
git status --branch --short
```

Relevant output:

```text
## feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 20]
```

Only pre-existing untracked residue was visible. There was no tracked diff before
this evidence artifact.

Command:

```text
git diff --name-only
```

Output: empty.

Command:

```text
git diff --check
```

Output: empty.

## Downstream API Evidence

Command:

```text
uv run python - <<'PY'
...
PY
```

The script used `TemporaryDirectory()` and called
`run_golden_readiness_preflight()` directly with local JSON/JSONL fixtures. It
did not read repository fixture content, promote fixture content or run a CLI
readiness/release command.

Result summary:

```json
[
  {
    "case": "matching_year_promoted",
    "overall_status": "pass",
    "readiness": "ready",
    "strict_golden_coverage": "covered",
    "fixture_promotion_state": "promoted_fixture",
    "promotion_state": "promoted_fixture",
    "blockers": []
  },
  {
    "case": "wrong_year_promoted",
    "overall_status": "pass",
    "readiness": "deferred_with_owner",
    "strict_golden_coverage": "covered",
    "fixture_promotion_state": "unknown",
    "promotion_state": "unknown",
    "blockers": [
      "fixture_promotion_unknown"
    ]
  },
  {
    "case": "legacy_fund_only_promoted",
    "overall_status": "pass",
    "readiness": "deferred_with_owner",
    "strict_golden_coverage": "covered",
    "fixture_promotion_state": "legacy_fund_only",
    "promotion_state": "unknown",
    "blockers": [
      "fixture_promotion_legacy_fund_only"
    ]
  }
]
```

Interpretation:

- Exact `004393 / 2025` year-aware promotion state is consumed downstream and
  produces `fixture_promotion_state=promoted_fixture`,
  `promotion_state=promoted_fixture`, `readiness=ready` and no fixture promotion
  blocker for the row.
- A year-aware `004393 / 2024` promotion entry does not satisfy a `004393 / 2025`
  row. The downstream row keeps `promotion_state=unknown` and emits
  `fixture_promotion_unknown`.
- Legacy fund-code-only `{ "004393": "promoted_fixture" }` does not satisfy a
  `004393 / 2025` row. The downstream row keeps `promotion_state=unknown` and
  emits `fixture_promotion_legacy_fund_only`.

The API result shows `overall_status=pass` for deferred rows because this gate
used the existing carried-forward candidate disposition in a temporary local
preflight setup. The value under evidence is the downstream row identity
projection and blocker routing, not a release/readiness pass.

## Test Evidence

Command:

```text
uv run pytest tests/fund/test_golden_readiness_preflight.py::test_preflight_accepts_year_aware_fixture_promotion_matching_year tests/fund/test_golden_readiness_preflight.py::test_preflight_rejects_fixture_promotion_wrong_year tests/fund/test_golden_readiness_preflight.py::test_preflight_blocks_legacy_fund_code_only_fixture_promotion -q
```

Output:

```text
...                                                                      [100%]
3 passed in 0.46s
```

Assertions covered by the targeted tests:

- matching year-aware fixture promotion outputs
  `fixture_promotion_state=promoted_fixture` and
  `promotion_state=promoted_fixture`.
- wrong-year promotion does not cross years and emits
  `fixture_promotion_unknown`.
- legacy fund-code-only promotion emits `fixture_promotion_legacy_fund_only` and
  cannot prove a specific report year.

## Finding Table

| Finding | Disposition | Evidence |
|---|---|---|
| Downstream preflight rows consume exact year-aware fixture promotion state. | ACCEPT | API temp run and targeted pytest show `004393 / 2025` exact entry produces `promoted_fixture` with no fixture promotion blocker. |
| Wrong-year year-aware promotion cannot satisfy `004393 / 2025`. | ACCEPT | API temp run and targeted pytest show `004393 / 2024` entry leaves the 2025 row `unknown` with `fixture_promotion_unknown`. |
| Legacy fund-code-only promotion cannot satisfy `004393 / 2025`. | ACCEPT | API temp run and targeted pytest show legacy mapping routes to `legacy_fund_only` and `fixture_promotion_legacy_fund_only`. |
| This evidence proves release/readiness. | REJECT | The gate is downstream-only and non-live. It does not promote fixtures, change tracked golden content or run readiness/release commands. |

## Residuals

| Residual | Owner | Next Gate | Blocker |
|---|---|---|---|
| No accepted fixture promotion state manifest/content was created by this gate. | Fixture promotion owner / controller | Fixture promotion content or manifest planning gate, if the controller chooses to pursue promotion. | Blocks any claim that `004393 / 2025` fixture promotion is now accepted content. |
| Release/readiness remains unproven. | Release owner / controller | Release-readiness rollup or readiness-specific gate after accepted content/promotion decisions. | Blocks release/readiness claim. |
| Existing untracked residue remains outside this gate. | Controller / artifact owners | Artifact-specific disposition gates only. | Not changed by this gate. |

## Controller Recommendation

Proceed to DS/MiMo implementation-evidence review for this downstream evidence.
If both reviews pass, the controller may accept this gate with
`ACCEPT_WITH_RESIDUALS_NOT_READY`.

Recommended next entry after acceptance:

`Fixture Promotion Content / Promotion-state Manifest Planning Gate`

Rationale: downstream semantics are now evidenced; the remaining product question
is whether to create or defer an accepted year-aware promotion manifest/content.
