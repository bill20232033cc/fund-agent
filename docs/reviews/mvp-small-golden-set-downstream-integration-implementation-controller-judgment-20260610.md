# MVP Small Golden Set Downstream Integration Implementation Controller Judgment - 2026-06-10

## Gate

EID single-source downstream integration implementation gate.

## Controller Position

ACCEPT.

The implementation satisfies the accepted downstream integration plan: existing extractor outputs for `portfolio_managers` and `risk_characteristic_text` are now carried through the deterministic downstream surfaces without changing source acquisition, fallback policy, live evidence semantics, provider/runtime behavior, golden promotion or quality-gate semantics.

## Source Classification

- Repo fact:
  - `fund_agent/fund/data_extractor.py:232` and `fund_agent/fund/data_extractor.py:235` add explicit bundle fields with missing defaults.
  - `fund_agent/fund/data_extractor.py:343` and `fund_agent/fund/data_extractor.py:344` populate them from existing extractor results.
  - `fund_agent/fund/extraction_snapshot.py:41`, `fund_agent/fund/extraction_snapshot.py:46`, `fund_agent/fund/extraction_snapshot.py:85` and `fund_agent/fund/extraction_snapshot.py:86` expose stable snapshot records and comparable subfields.
  - `fund_agent/fund/report_evidence.py:277` and `fund_agent/fund/report_evidence.py:279` expose the fields in report evidence.
  - `fund_agent/fund/chapter_facts.py:82`, `fund_agent/fund/chapter_facts.py:85`, `fund_agent/fund/chapter_facts.py:309`, `fund_agent/fund/chapter_facts.py:355` and `fund_agent/fund/chapter_facts.py:412` define source ids and chapter mappings.
  - `fund_agent/fund/evidence_availability.py:199`, `fund_agent/fund/evidence_availability.py:247`, `fund_agent/fund/evidence_availability.py:266` and `fund_agent/fund/evidence_availability.py:308` derive availability from the new fields.
  - `tests/fund/test_data_extractor.py:334` and `tests/fund/test_data_extractor.py:355` now verify value-level fan-in from fake parsed annual report tables.
- Truth-doc fact:
  - `docs/design.md` and `docs/implementation-control.md` keep current operational annual-report acquisition as EID single-source MVP and do not authorize Eastmoney, fund-company-site or CNINFO fallback re-entry.
  - `docs/current-startup-packet.md` and `docs/implementation-control.md` route this gate as downstream integration implementation before any separate controlled live EID evidence gate.
- Accepted plan fact:
  - `docs/reviews/mvp-small-golden-set-downstream-integration-planning-gate-plan-20260610.md` requires explicit bundle wiring for `portfolio_managers` and `risk_characteristic_text`, snapshot/report/chapter/evidence availability exposure, and keeping `bond_top_holdings` / `target_fund_holdings` under `holdings_snapshot`.
  - `docs/reviews/mvp-small-golden-set-downstream-integration-planning-gate-controller-judgment-20260610.md` accepts that plan.
- Reviewer opinion:
  - James and Hypatia both found no blocking implementation findings.
  - Both identified weak initial `hasattr` coverage in `tests/fund/test_data_extractor.py`; controller accepted that finding and routed a narrow fix.
- Accepted residual:
  - No live EID failure-branch proof is claimed by this gate.
  - Report-evidence value/anchor-specific assertions may be further hardened later if report evidence becomes a quality blocker; current generic path plus tests are sufficient for this gate.
- Rejected finding:
  - None.
- Deferred candidate:
  - Controlled live EID failure-branch evidence remains a separate authorized gate.
  - Control-doc compression / artifact hygiene remains a separate gate.
  - CI quality warn-only planning remains a separate planning gate.

## Agent Routing and Review Evidence

`AgentDS` and `AgentMiMo` were online but unavailable for current-task review because `/clear` verification failed twice on both panes: both captures retained stale `PR #22` context. Per `init-agents` clear verification rules, no current-task handoff was sent to those panes and their output was not used as evidence.

Two independent subagent reviews were used instead:

- `docs/reviews/mvp-small-golden-set-downstream-integration-implementation-review-james-20260610.md`: PASS, no blocking findings; accepted test-strengthening residual resolved on re-review.
- `docs/reviews/mvp-small-golden-set-downstream-integration-implementation-review-hypatia-20260610.md`: PASS, no blocking findings; accepted test-strengthening residual resolved on re-review.

Implementation evidence:

- `docs/reviews/mvp-small-golden-set-downstream-integration-implementation-evidence-20260610.md`

## Finding Disposition

| Finding | Disposition | Basis |
| --- | --- | --- |
| `StructuredFundDataBundle` lacked `portfolio_managers` and `risk_characteristic_text` downstream visibility. | ACCEPT_FIXED | Plan required explicit bundle fields; repo now exposes and populates both fields from existing extractor outputs. |
| Snapshot/report/chapter/evidence availability did not consume the two fields. | ACCEPT_FIXED | Repo now adds snapshot records, comparable subfields, report evidence specs, chapter field specs and availability specs. |
| `bond_top_holdings` and `target_fund_holdings` could be duplicated as top-level fields. | REJECT_AS_NON_GOAL | Plan and controller judgment require those to remain `holdings_snapshot` sub-shapes; repo did not add top-level fields. |
| `tests/fund/test_data_extractor.py` only checked field existence after extract. | ACCEPT_FIXED | Fix replaced `hasattr` checks with value-level assertions for payloads and anchors; both re-reviews passed. |
| Live EID failure branches remain unproven. | DEFER | This gate was no-live downstream wiring; live evidence requires a separately authorized controlled live gate. |

## Validation

Controller reran the deterministic validation matrix after the follow-up fix:

```bash
uv run pytest tests/fund/test_data_extractor.py -q
```

Result: `10 passed in 0.74s`

```bash
uv run pytest tests/fund/test_extraction_snapshot.py -q
```

Result: `13 passed in 0.74s`

```bash
uv run pytest tests/fund/test_report_evidence.py -q
```

Result: `23 passed in 0.75s`

```bash
uv run pytest tests/fund/test_chapter_facts.py tests/fund/test_evidence_availability.py -q
```

Result: `23 passed in 0.79s`

```bash
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
```

Result: `24 passed in 0.38s`

```bash
uv run ruff check fund_agent/fund/data_extractor.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/report_evidence.py fund_agent/fund/chapter_facts.py fund_agent/fund/evidence_availability.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_report_evidence.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_availability.py
```

Result: `All checks passed!`

```bash
git diff --check -- fund_agent/fund/data_extractor.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/report_evidence.py fund_agent/fund/chapter_facts.py fund_agent/fund/evidence_availability.py tests/fund/test_data_extractor.py tests/fund/test_extraction_snapshot.py tests/fund/test_report_evidence.py tests/fund/test_chapter_facts.py tests/fund/test_evidence_availability.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-downstream-integration-implementation-evidence-20260610.md
```

Result: passed with no output.

## Decision

Accepted as local implementation checkpoint.

Next entry after control-truth sync: controlled live EID failure-branch evidence gate, only under explicit live authorization and the previously accepted live/no-live boundaries.
