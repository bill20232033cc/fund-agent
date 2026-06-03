# MVP typed template contract Slice 2 EvidenceAvailability controller judgment

## Judgment

ACCEPTED WITH NON-BLOCKING RESIDUAL RISKS.

The `MVP typed template contract Slice 2 same-source EvidenceAvailability implementation gate` is accepted locally. The implementation adds an additive Fund-layer `EvidenceAvailability` derivation view from same-source `ChapterFactProjection` / `ChapterFactInput` inputs and focused tests without changing current renderer, auditor, CLI, provider runtime, quality gate or fail-closed behavior.

This judgment does not authorize provider/runtime/default changes, live PASS-only probe, Agent runtime implementation, score-loop, golden/readiness changes, template truth replacement, auditor relaxation, deterministic fallback, stdout partial-report behavior or multi-year annual evidence runtime loading.

## Accepted Artifacts

- Implementation evidence: `docs/reviews/mvp-typed-template-contract-slice2-evidence-availability-implementation-evidence-20260603.md`
- DS review: `docs/reviews/mvp-typed-template-contract-slice2-evidence-availability-code-review-ds-20260603.md`
- MiMo review: `docs/reviews/mvp-typed-template-contract-slice2-evidence-availability-code-review-mimo-20260603.md`

Both reviews returned PASS-WITH-RISKS with no blocking findings.

## Accepted Implementation

Touched implementation and documentation files:

- `fund_agent/fund/evidence_availability.py`
- `fund_agent/fund/__init__.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_evidence_availability.py`
- `tests/README.md`

The accepted implementation:

- adds `evidence_availability.v1` dataclasses: `EvidenceAvailability`, `RequirementAvailability`, `EvidenceGapReference`, `AvailabilityStatus` and `EvidenceRequirementId`;
- adds `derive_evidence_availability()` and `derive_chapter_evidence_availability()`;
- derives requirement availability only from `ChapterFactProjection` / `ChapterFactInput`, fact ids, source field ids, evidence anchor ids, fact statuses, missing reasons and typed contract requirement ids;
- keeps `available`, `missing`, `unavailable`, `not_applicable` and `unreviewed` distinct and combines statuses conservatively;
- keeps Ch2 availability under public `chapter_id=2` with internal subcontract ids `performance`, `attribution` and `cost`;
- covers Ch3 manager strategy text, turnover, holdings snapshot, cross-period style evidence, manager alignment and actual behavior aggregate;
- treats current single-year cross-period style evidence as `unreviewed` without loading prior-year documents;
- fails closed on unknown typed contract requirement ids referenced by typed predicates or Ch2 internal subcontracts;
- does not replace or mutate `ChapterFactProjection`;
- does not import repository/PDF/cache/source-helper/Service/Host/provider/retained-report/filesystem/env/dayu/Agent runtime/tool-loop code.

## Controller Disposition Of Findings

| Finding | Reviewer | Controller disposition | Owner |
|---|---|---|---|
| `derive_chapter_evidence_availability()` reconstructs `fund_code` and `report_year` from `fact_id` format and falls back to `unknown` / `0` on malformed or empty facts. | DS and MiMo | Accepted as non-blocking. The primary path is `derive_evidence_availability(projection)`, which uses explicit projection root identity. The single-chapter convenience path is not authorized as a production identity source. Future wiring should prefer the projection-root API or harden this helper before broad use. | Future Service/Agent wiring gate |
| `ch3.required_output.item_01` is not represented in the availability closed set. | DS and MiMo | Accepted as non-blocking. Slice 2 scope explicitly required Ch3 manager strategy, turnover, holdings snapshot, cross-period style evidence, manager alignment and actual behavior. Basic manager info availability can be added or intentionally documented in Slice 3 if required-output missing/degrade needs it. | Slice 3 implementation/review |
| `ch3.required_output.item_04` was called out in one MiMo finding as not explicit in `_RequirementSpec`; however the same review checklist confirms it is included in `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS` and covered by actual behavior aggregate availability. | MiMo | No fix required. Controller records the corrected disposition: `item_04` is covered as derived actual-behavior availability, while future Slice 3/4 may still decide whether item-level granularity should become more explicit. | Slice 3/4 review |
| Static import test is coarse and does not prove transitive dependencies or runtime monkeypatch absence. | DS | Accepted as non-blocking. The module's direct imports are only stdlib plus accepted Fund-layer modules, and runtime derivation is a pure transformation of frozen dataclass inputs. Future hardening can add monkeypatch guards if this path becomes broader. | Future test-hardening gate |
| `EvidenceRequirementId` closed set lives in `evidence_availability.py` while typed predicates store strings. | DS observation | Accepted as non-blocking. Runtime validation catches unknown ids during derivation. A later gate may centralize requirement id definitions if cross-module drift becomes costly. | Future typed contract maintenance |
| `typed_contracts.TemplateLensRule` and `contracts.TemplateLensRule` remain separate same-name classes from Slice 1. | Prior Slice 1 residual | Still non-blocking for Slice 2; no new package-level typed API consumption depends on that class. Resolve before broad Service facade/package-level typed API consumption. | Slice 7 or earlier if needed |

## Validation

Controller independently reran:

```bash
uv run pytest tests/fund/test_evidence_availability.py tests/fund/test_chapter_facts.py tests/fund/template/test_typed_contracts.py
uv run ruff check fund_agent/fund tests/fund
git diff --check -- docs/reviews/mvp-typed-template-contract-slice2-evidence-availability-implementation-evidence-20260603.md fund_agent/fund/evidence_availability.py fund_agent/fund/__init__.py fund_agent/fund/README.md tests/fund/test_evidence_availability.py tests/README.md
```

Results:

- `28 passed`
- `ruff` all checks passed
- `git diff --check` exited `0`

Secret scan over touched files and review artifacts found only existing README safety text and no secret values.

## Next Gate

Start `MVP typed template contract Slice 3 required-output missing/degrade implementation gate`.

Allowed next scope:

- typed missing/degrade behavior for `RequiredOutputItem.when_evidence_missing`;
- writer input or typed adapter that receives typed required output items plus `EvidenceAvailability`;
- support for `render_evidence_gap`, `render_minimum_verification_question`, `delete_if_not_applicable` and `block`;
- fail-closed block before unsupported writing when no safe degrade path exists;
- preservation of current marker policy and allowed missing reasons;
- tests proving missing evidence can satisfy required output only through approved gap/degrade output and that silent deletion requires a typed reason.

Not authorized in Slice 3:

- provider/runtime/default/budget/endpoint changes;
- live PASS-only probe;
- Agent runtime/tool-loop;
- score-loop, golden/readiness, promotion or quality-gate semantic changes;
- deterministic fallback or stdout partial report;
- template truth replacement;
- multi-year annual evidence runtime loading.

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text or raw parsed annual-report text.
