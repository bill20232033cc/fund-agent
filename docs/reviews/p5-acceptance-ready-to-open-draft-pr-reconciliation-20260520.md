# P5 Acceptance / Ready-to-open-draft-PR Reconciliation - 2026-05-20

## Verdict

P5 is accepted and ready to open a draft PR, pending user authorization for the draft PR gate.

Current gate can advance to `ready-to-open-draft-PR`.

## Acceptance Basis

P5 closed the post-P4 report main-path quality risks:

- P5-S1: `fund-analysis analyze` now runs quality gate by default and supports `block / warn / off`.
- P5-S2: quality gate rules now include App category conflict, missing-rate and preferred_lens checks.
- P5-S3: snapshot exposes whitelisted comparable subfields for correctness denominator.
- P5-S4: full extraction failures enter `score.json.failed_funds` and trigger FQ6.
- P5-S5: `share_change` multi-share-class extraction fails closed unless a single value column or exact fund-code header exists.
- P5-S6: duplicate `016492` source issue is explicitly human-owned and not auto-fixed.
- P5-S7: thermometer read-only Service/CLI is available; true PDF/network smoke remains explicit opt-in and records quality gate status separately.

Aggregate review found five substantive issues, all accepted and fixed:

- block policy could output a report when gate did not run;
- explicit golden answer path typo could disable correctness;
- present parent field with missing whitelisted subfield could become unavailable instead of mismatch;
- A-class fallback could misread non-A share classes;
- smoke PASS could hide quality gate block.

Re-review passed:

- `docs/reviews/p5-aggregate-rereview-controller-acceptance-20260520.md`

## Final Verification

- `.venv/bin/python -m pytest tests/ -q` -> `206 passed`
- `.venv/bin/python -m ruff check .` -> passed
- `git diff --check` -> passed

## PR Inclusion Set

### Code

Include:

- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extractors/holdings_share_change.py`
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/services/__init__.py`
- `fund_agent/services/extraction_score_service.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/thermometer_service.py`
- `fund_agent/ui/cli.py`
- `scripts/selected_funds_smoke.py`

### Tests

Include:

- `tests/fund/extractors/test_holdings_share_change.py`
- `tests/fund/integration/test_p3_cli_e2e_matrix.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/test_quality_gate_integration.py`
- `tests/scripts/test_selected_funds_smoke.py`
- `tests/services/test_extraction_score_service.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/services/test_thermometer_service.py`
- `tests/ui/test_cli.py`

### Docs

Include:

- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control.md`
- `docs/implementation-control-p4.md`

### P5 Review / Control Artifacts

Include:

- `docs/reviews/post-p4-follow-up-planning-20260520.md`
- `docs/reviews/code-review-20260520-0350.md`
- `docs/reviews/code-review-p5-s2-20260520.md`
- `docs/reviews/code-review-p5-s3-20260520.md`
- `docs/reviews/code-review-p5-s4-20260520.md`
- `docs/reviews/code-review-p5-s5-20260520.md`
- `docs/reviews/code-review-p5-s7-20260520.md`
- `docs/reviews/p5-s1-quality-gate-integration-plan-20260520.md`
- `docs/reviews/p5-s1-plan-review-controller-20260520.md`
- `docs/reviews/p5-s1-plan-rereview-controller-20260520.md`
- `docs/reviews/p5-s1-implementation-20260520.md`
- `docs/reviews/p5-s1-acceptance-reconciliation-20260520.md`
- `docs/reviews/p5-s2-quality-gate-rules-plan-20260520.md`
- `docs/reviews/p5-s2-plan-review-controller-20260520.md`
- `docs/reviews/p5-s2-plan-rereview-controller-20260520.md`
- `docs/reviews/p5-s2-implementation-20260520.md`
- `docs/reviews/p5-s2-acceptance-reconciliation-20260520.md`
- `docs/reviews/p5-s3-snapshot-sub-field-exposure-plan-20260520.md`
- `docs/reviews/p5-s3-plan-review-controller-20260520.md`
- `docs/reviews/p5-s3-plan-rereview-controller-20260520.md`
- `docs/reviews/p5-s3-implementation-20260520.md`
- `docs/reviews/p5-s4-snapshot-failure-accounting-plan-20260520.md`
- `docs/reviews/p5-s4-plan-review-controller-20260520.md`
- `docs/reviews/p5-s4-plan-rereview-controller-20260520.md`
- `docs/reviews/p5-s4-implementation-20260520.md`
- `docs/reviews/p5-s5-share-change-hardening-plan-20260520.md`
- `docs/reviews/p5-s5-plan-review-controller-20260520.md`
- `docs/reviews/p5-s5-plan-rereview-controller-20260520.md`
- `docs/reviews/p5-s5-implementation-20260520.md`
- `docs/reviews/p5-s6-user-app-source-reconciliation-20260520.md`
- `docs/reviews/p5-s7-post-mvp-infra-validation-plan-20260520.md`
- `docs/reviews/p5-s7-plan-review-controller-20260520.md`
- `docs/reviews/p5-s7-plan-rereview-controller-20260520.md`
- `docs/reviews/p5-s7-implementation-20260520.md`
- `docs/reviews/p5-aggregate-readiness-reconciliation-20260520.md`
- `docs/reviews/p5-aggregate-deepreview-controller-judgment-20260520.md`
- `docs/reviews/p5-aggregate-rereview-controller-acceptance-20260520.md`
- `docs/reviews/p5-acceptance-ready-to-open-draft-pr-reconciliation-20260520.md`

## Explicitly Excluded From P5 PR

Do not include:

- `docs/reviews/code-review-20260517-0727.md`
- `docs/reviews/p2-full-retrospective-controller-judgment-20260519-0014.md`
- `docs/reviews/p2-full-retrospective-deepreview-glm-20260518-2358.md`
- `docs/reviews/p2-full-retrospective-deepreview-mimo-20260519-0004.md`
- `docs/reviews/pr-1-review-mimo-2026-05-18.md`
- `launchd/`
- `report-004393.md`
- `reports/extraction-snapshots/`
- `reports/quality-gate-runs/`
- `scripts/aliases.zsh`
- `scripts/multi_tail.py`
- `scripts/remind-agentcontroller.sh`
- `scripts/setup-ai-session.sh`
- `scripts/start-tmux-agents.sh`
- `scripts/start-tmux-ai.sh`

These are older review artifacts, local operations helpers, or runtime outputs unrelated to the P5 PR inclusion set.

## Remaining Risks / Owners

| Risk | Status | Owner |
|---|---|---|
| Duplicate `016492` in selected-fund CSV | open | human/user App source confirmation |
| Live PDF/network smoke not run as required gate | accepted | explicit operator smoke only |
| Thermometer-to-valuation mapping absent | accepted | future Capability/checklist design |
| Not-run block failure uses `ValueError` rather than structured quality exception | accepted | future CLI UX refinement |

## Gate Decision

P5 is accepted.

Current gate advances to `ready-to-open-draft-PR`.

Draft PR gate still requires user authorization before push / PR creation.
