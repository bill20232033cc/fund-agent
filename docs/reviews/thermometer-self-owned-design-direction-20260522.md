# Thermometer self-owned design direction controller judgment（2026-05-22）

## Verdict

`ACCEPTED_AS_DESIGN_DIRECTION`

User decision accepted: the project should develop its own thermometer capability. The previous v2.1 wording treated non-self-calculated thermometer as an explicit non-goal; that is no longer the desired long-term direction. The corrected design position is:

- current code remains a read-only query/cache of the Youzhiyouxing public thermometer page;
- that public-page dependency is transitional, not a durable source of truth;
- a future phase should design and implement a project-owned thermometer calculation/data contract;
- automatic mapping from thermometer values to `valuation_state` remains a separate design problem and must not be silently enabled.

## First-Principles Rationale

A thermometer is a core input for "good price" in the user-facing investment checklist. Depending indefinitely on a public page scrape makes the product brittle because HTML, availability, and upstream presentation choices are outside this project's control. A project-owned thermometer should make the data inputs, formulas, time windows, cache semantics, failure categories, and evidence trail explicit and testable.

At the same time, self-owned thermometer calculation is not equivalent to automatic investment judgment. `valuation_state` affects checklist output and final analysis behavior, so any mapping from raw thermometer metrics to `low / fair / high / unavailable` must be separately specified, deterministic, auditable, and overridable by explicit user input.

## Design Changes

`docs/design.md` is updated to v2.2:

- §1.3 no longer says self-built thermometer is a non-goal.
- §1.3 now says current Youzhiyouxing public-page scraping must not be treated as the long-term thermometer truth.
- §6.3 records current thermometer query as transitional and adds future self-owned thermometer as a design direction.
- §9.0 clarifies the current CLI command is read-only today but should later migrate to the project-owned thermometer contract.
- §10 changes the design decision from "self-built in v3" to "future project-owned thermometer, no permanent public-page dependency".

## Control Impact

`docs/implementation-control.md` should track this as a new design-direction correction after P17-S1 PR readiness. The current draft-PR gate should be paused until the design/control wording is included in the local PR readiness set or the PR scope is explicitly narrowed.

## Non-Goals Preserved

- Do not implement thermometer calculation in this documentation correction.
- Do not change runtime behavior or current CLI output.
- Do not auto-map thermometer data to `valuation_state`.
- Do not introduce external Dayu runtime, LLM audit, Evidence Confirm, or a new Service/UI behavior.
- Do not touch current P17-S1 tracking-error extractor implementation.

## Future Phase Requirements

A future self-owned thermometer phase must define at minimum:

- market/index coverage;
- accepted source datasets and update cadence;
- formulas and percentile/temperature windows;
- cache and stale fallback behavior;
- unavailable / schema drift / identity mismatch / integrity failure taxonomy if external datasets are used;
- deterministic fixtures and tests;
- whether and how a separate `valuation_state` mapping is exposed.
