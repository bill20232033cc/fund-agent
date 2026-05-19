# Controller Plan Review - P5-S7 Post-MVP Infra Validation - 2026-05-20

## Verdict

NEEDS PATCH.

The plan has the correct high-level boundary: live thermometer and live PDF/network paths must be explicit and must not enter deterministic tests. However, two details need tightening before implementation.

## Findings

### P5-S7-PR1 - Thermometer Service needs injectable adapter/fetcher for Service tests

Severity: blocking

The plan proposes `ThermometerService.run(...)` but does not define how tests can avoid live network. If the Service constructs `FundThermometerAdapter()` internally without injection, Service tests will either hit the network or need brittle monkeypatching.

Patch requirement:

- `ThermometerService` must accept an optional adapter/factory Protocol in `__init__`.
- Tests must inject a fake adapter or fake factory returning deterministic `ThermometerSnapshot`.
- Production default may still construct `FundThermometerAdapter(cache_dir)`.

### P5-S7-PR2 - CLI unavailable behavior must be explicit

Severity: medium

The plan says unavailable data may exit successfully, but this should be part of the contract. `FundThermometerAdapter` already treats unavailable as a data state rather than an exception. The CLI should mirror that behavior so a smoke command can record upstream unavailability without making the CLI wrapper look broken.

Patch requirement:

- If Service returns `ThermometerSnapshot(unavailable=True)`, CLI exits 0 and prints unavailable fields.
- If Service raises validation or unexpected runtime error, CLI exits non-zero.

### P5-S7-PR3 - `--quality-gate-policy warn` smoke change should be accepted, not optional ambiguous

Severity: medium

The existing smoke command calls `analyze` with default `quality_gate_policy=block`. After P5-S1/P5-S2, a real PDF/network smoke can fail because quality gate blocks output, even if PDF download/parsing reached the intended path. That masks the infrastructure signal P5-S7 wants.

Patch requirement:

- Change smoke command builder to pass `--quality-gate-policy warn` explicitly.
- This is not weakening production defaults; it is an operational smoke command whose purpose is to observe real report rendering path while still recording quality gate issues.
- Tests must assert the explicit policy.

### P5-S7-PR4 - JSON output should not be deferred if CLI is used for automation

Severity: low

The plan says plain text is acceptable and JSON is optional. Since this slice is “infra validation”, machine-readable output is useful and cheap.

Patch requirement:

- Add `--json` to `fund-analysis thermometer`.
- Plain text can remain default, but tests should cover JSON output at least for available and unavailable snapshots.

## Required Plan Patch

Patch the plan with PR1/PR2/PR3/PR4, then re-review.

Next gate: `P5-S7 plan re-review`.
