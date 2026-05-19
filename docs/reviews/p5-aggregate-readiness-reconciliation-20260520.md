# P5 Aggregate Readiness Reconciliation - 2026-05-20

## Verdict

P5 is ready for aggregate deepreview.

P5's main objective was to move the P4 quality loop from offline artifacts into the user-facing report path, then close the highest-risk post-P4 quality gaps without silently expanding report semantics. That objective is met.

Next gate: `P5 aggregate deepreview`.

## Inputs

- Design truth: `docs/design.md`
- Global control doc: `docs/implementation-control.md`
- P4/P5 control doc: `docs/implementation-control-p4.md`
- P5 artifacts:
  - `docs/reviews/p5-s1-quality-gate-integration-plan-20260520.md`
  - `docs/reviews/p5-s1-implementation-20260520.md`
  - `docs/reviews/code-review-20260520-0350.md`
  - `docs/reviews/p5-s1-acceptance-reconciliation-20260520.md`
  - `docs/reviews/p5-s2-quality-gate-rules-plan-20260520.md`
  - `docs/reviews/p5-s2-implementation-20260520.md`
  - `docs/reviews/code-review-p5-s2-20260520.md`
  - `docs/reviews/p5-s2-acceptance-reconciliation-20260520.md`
  - `docs/reviews/p5-s3-snapshot-sub-field-exposure-plan-20260520.md`
  - `docs/reviews/p5-s3-implementation-20260520.md`
  - `docs/reviews/code-review-p5-s3-20260520.md`
  - `docs/reviews/p5-s4-snapshot-failure-accounting-plan-20260520.md`
  - `docs/reviews/p5-s4-implementation-20260520.md`
  - `docs/reviews/code-review-p5-s4-20260520.md`
  - `docs/reviews/p5-s5-share-change-hardening-plan-20260520.md`
  - `docs/reviews/p5-s5-implementation-20260520.md`
  - `docs/reviews/code-review-p5-s5-20260520.md`
  - `docs/reviews/p5-s6-user-app-source-reconciliation-20260520.md`
  - `docs/reviews/p5-s7-post-mvp-infra-validation-plan-20260520.md`
  - `docs/reviews/p5-s7-implementation-20260520.md`
  - `docs/reviews/code-review-p5-s7-20260520.md`

## Slice Status

| Slice | Status | Readiness judgment |
|---|---|---|
| P5-S1 quality gate integration | accepted | `fund-analysis analyze` now runs quality gate by default with `block/warn/off`; Service exposes structured blocked error. |
| P5-S2 quality gate rules | accepted | FQ1 App category conflict, FQ4 missing-rate, FQ5 preferred_lens resolvability are in `score.json`/quality gate. |
| P5-S3 snapshot sub-field exposure | accepted | `comparable_values` expands correctness denominator for whitelisted stable subfields; old snapshot compatibility preserved. |
| P5-S4 snapshot failure accounting | accepted | `errors.jsonl` can enter `score.json.failed_funds`; FQ6 blocks failed funds. |
| P5-S5 share_change hardening | accepted | Multi-share-class tables no longer use first-value fallback; ambiguous tables fail closed. |
| P5-S6 user/App source reconciliation | blocked-on-human / non-blocking | Duplicate `016492` requires user/App source confirmation; no automatic CSV edit. |
| P5-S7 post-MVP infra validation | accepted | Read-only thermometer Service/CLI added; true PDF/network smoke remains explicit opt-in and uses warn policy. |

## Control-Doc Reconciliation

### Design Alignment

- UI remains a thin CLI layer and does not perform fund quality, thermometer, PDF, or domain judgment.
- Service coordinates use cases and does not parse annual reports, score JSON internals, thermometer HTML, or smoke output.
- Capability owns extraction snapshot, score, quality gate, thermometer adapter, preferred_lens, correctness comparison, and share_change domain extraction.
- No explicit parameters were moved into `extra_payload`.
- No fund documents were accessed outside the unified extractor/document repository path.

### Quality Gate Main Path

P5-S1 closed RR-15 / P4-R8. `analyze` no longer silently bypasses quality gate:

- default policy: `block`;
- `warn`: report still renders with gate summary;
- `off`: explicit opt-out.

### Rule Completeness

P5-S2/P5-S4 closed the highest-priority gate accounting gaps:

- App category mismatch can block;
- high missing rate can warn/block by severity;
- preferred_lens resolvability is checked;
- full extraction failures are not lost in `errors.jsonl`.

### Correctness Denominator

P5-S3 partially closes RR-16 by exposing stable subfields through `comparable_values`.

Remaining denominator growth is intentionally future extractor/golden-answer work, not a P5 blocker.

### Extractor Hardening

P5-S5 removed unsafe same-row first-value and A-class fallback heuristics in `share_change`.

The accepted behavior is conservative: exact fund-code header match or a single value column only; ambiguous multi-column tables become missing.

### Post-MVP Infra

P5-S7 closes RR-4 for read-only thermometer Service/CLI access and closes RR-8 for opt-in smoke command hardening.

It intentionally does not close an automatic thermometer-to-valuation mapping because no same-source Capability rule exists.

## Verification Baseline

Latest controller verification:

- `.venv/bin/python -m pytest tests/ -q` -> `200 passed`
- `.venv/bin/python -m ruff check .` -> passed
- `git diff --check` -> passed

Additional P5-S7 smoke:

- `.venv/bin/python -m fund_agent.ui.cli thermometer --json` -> exited 0 and returned a thermometer JSON snapshot.

True PDF/network selected-fund smoke was not run as a required gate. It remains explicit operational validation:

```bash
.venv/bin/python scripts/selected_funds_smoke.py \
  --code 004393 \
  --run \
  --output-dir reports/smoke/p5-s7-004393
```

## Residual Risks And Owners

| Risk | Status | Owner / destination |
|---|---|---|
| RR-13 duplicate `016492` in `docs/code_20260519.csv` | open / human-owned | User/App source confirmation. Not auto-fixed by controller. |
| RR-16 correctness denominator still limited by extractor and golden answer coverage | partially closed | Future correctness/golden set expansion after more stable extractor subfields. |
| Thermometer value to `valuation_state` mapping absent | intentional non-goal | Future Capability/checklist design; must define same-source thresholds before Service can consume. |
| Live PDF/network upstream instability | operational risk | Keep out of ordinary pytest; run explicit smoke when needed and record outputs. |

## Aggregate Deepreview Criteria

P5 aggregate deepreview should focus on:

1. Whether `analyze` quality gate integration can silently skip or overwrite quality artifacts.
2. Whether `score.json` / `quality_gate.json` schemas are internally consistent after S2-S4.
3. Whether `share_change` conservative missing behavior creates any unintended downstream report/audit regression.
4. Whether thermometer Service/CLI respects layer boundaries and does not sneak into investment judgment.
5. Whether README/control docs accurately distinguish deterministic tests from live smoke.

## Gate Decision

P5 aggregate readiness reconciliation is accepted.

Current gate advances to `P5 aggregate deepreview`.
