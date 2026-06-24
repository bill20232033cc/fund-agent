# Evidence Confirm Productionization EC-P3 Semantic Entailment Plan

- Gate: plan
- Work unit: Evidence Confirm productionization / EC-P3 semantic entailment
- Date: 2026-06-22
- Classification: heavy
- Goal confirmation: `docs/reviews/evidence-confirm-productionization-ec-p3-semantic-entailment-goal-confirmation-20260622.md`
- Artifact path: `docs/reviews/evidence-confirm-productionization-ec-p3-semantic-entailment-plan-20260622.md`

## Goal

Add a Fund-layer no-live semantic entailment companion contract for Evidence Confirm. The new contract must classify bounded qualitative claims against already materialized same-anchor excerpts while preserving deterministic V2 source/proof/value hard-gate authority.

## Motivation

Current Evidence Confirm V2 proves deterministic auditability dimensions only. Its `value_match` dimension checks normalized material tokens in same-anchor proven excerpts. That is not enough for qualitative claims, because token overlap can still overclaim causality, contradict source context, or convert a cautious source statement into a stronger conclusion. EC-P2 proved the repository/source/PDF pathway for exact sample `004393 / 2025`; it explicitly did not prove semantic entailment. This gate adds the missing no-live semantic contract without provider/live dependency.

## Success Signal

- A new Fund-layer semantic module exists and imports without Service, Host, provider SDK, API-key config, network, renderer, UI, quality-gate, repository, PDF/cache/source-helper or dayu dependencies.
- Semantic results use a stable companion schema such as `evidence_confirm_semantic.v1` and do not mutate `evidence_confirm.v2`.
- Fake-client tests prove `entailed`, `contradicted`, `insufficient`, `not_applicable`, deterministic gate failure, malformed client output and client exception behavior.
- Numeric deterministic mismatch remains blocking even if the fake semantic client returns `entailed`.
- Existing V1/V2 Evidence Confirm tests still pass unchanged.
- Fund README documents the current semantic no-live contract and explicitly states provider/live, Service/UI/renderer/quality-gate integration and release/readiness remain future gates.

## Non-goals / Scope Boundary

This gate must not:

- construct a real provider/LLM client;
- run provider/live/network/PDF commands;
- alter `EvidenceConfirmResultV2`, V2 dimension order, V2 hard-gate semantics or V1 compatibility behavior;
- integrate Service, UI, Host, renderer or quality gate;
- make semantic entailment default-on;
- change repository/source fallback behavior;
- expand `ChapterFactEntry` or infer natural-language claims from `fact.value`;
- prove field correctness, source-truth family correctness, golden promotion, readiness or release;
- mark PR ready, merge, request reviewers, delete branch, or change external issue state.

## Design Document Alignment

- `docs/design.md` currently states Evidence Confirm is Fund-layer no-live V1/V2 helper and does not read repository, PDF/cache/source helper, renderer, CLI, quality gate or readiness paths.
- `fund_agent/fund/evidence_confirm.py` preserves deterministic V1/V2 scoring.
- `docs/current-startup-packet.md` and `docs/implementation-control.md` route current gate to EC-P3 semantic entailment.
- The accepted productionization plan originally numbered semantic entailment as EC-P4. Current control docs supersede the numbering for routing; this plan keeps the semantic scope and records the numbering drift rather than expanding scope.

## First-principles Judgment and Direct Code Evidence

Current facts:

- `ChapterFactEntry` contains `fact_id`, `source_field_id`, `value`, `evidence_anchor_ids`, status, missing metadata and required-by metadata. It does not contain a rendered natural-language claim.
- `EvidenceConfirmReference` contains anchor id, source/proof metadata and excerpt text.
- `EvidenceConfirmResultV2` contains fact-level deterministic hard-gate results.
- `_confirm_fact_v2()` calculates deterministic dimensions only: `anchor_precision`, `source_support`, `missing_evidence`, `proof_boundary`, `value_match`.
- `_dimension_value_match()` uses `_material_tokens()` and `_matched_anchor_ids()`; `_token_matches_excerpt()` performs numeric matching or substring matching.

Judgment:

- Semantic entailment should be an explicit companion layer. It should consume explicit semantic claims supplied by a later Service/renderer gate or by tests, not guess claims from structured fact values.
- The semantic layer should run only after deterministic prerequisites are satisfied for the same fact/anchor surface. It may classify support, but it cannot turn deterministic failures into pass.

## Affected Files / Modules

Implementation slice allowed files:

- Add `fund_agent/fund/evidence_confirm_semantic.py`.
- Add `tests/fund/test_evidence_confirm_semantic.py`.
- Update `fund_agent/fund/README.md`.
- Update `tests/README.md` only if test taxonomy or command guidance changes.

Plan/review/control files:

- `docs/reviews/evidence-confirm-productionization-ec-p3-semantic-entailment-plan-20260622.md`
- plan review / fix / re-review artifacts under `docs/reviews/`
- later controller judgment artifact
- optional control-doc sync after accepted plan or implementation closeout

Forbidden files in this gate unless a later review finding requires a targeted plan fix:

- Service, UI, Host, renderer and quality-gate modules.
- Repository/source/PDF/cache/downloader modules.
- Provider/client/config modules.
- `fund_agent/fund/evidence_confirm.py` public V1/V2 result contracts, except imports in tests if needed. Prefer no production edit to this file.
- `fund_agent/fund/chapter_facts.py`.

## Contract / Schema / Public Interface Changes

Add a new companion schema in `fund_agent/fund/evidence_confirm_semantic.py`:

```python
EVIDENCE_CONFIRM_SEMANTIC_SCHEMA_VERSION = "evidence_confirm_semantic.v1"

EvidenceSemanticStatus = Literal[
    "entailed",
    "contradicted",
    "insufficient",
    "not_applicable",
]
EvidenceSemanticSeverity = Literal["block", "warn", "info"]
EvidenceSemanticOverallStatus = Literal["pass", "warn", "fail", "not_applicable"]
EvidenceSemanticReasonCode = Literal[
    "entailed_by_excerpt",
    "contradicted_by_excerpt",
    "insufficient_excerpt_support",
    "not_applicable",
    "deterministic_gate_failed",
    "missing_claim",
    "missing_bounded_excerpt",
    "malformed_client_result",
    "client_exception",
]
```

Add dataclasses with frozen slots and Chinese docstrings:

- `EvidenceSemanticClaim`
  - `claim_id: str`
  - `fact_id: str`
  - `source_field_id: str`
  - `claim_text: str`
  - `anchor_ids: tuple[str, ...]`
- `EvidenceEntailmentRequest`
  - `claim: EvidenceSemanticClaim`
  - `excerpt_texts: tuple[str, ...]`
- `EvidenceEntailmentJudgment`
  - `status: EvidenceSemanticStatus`
  - `reason_code: EvidenceSemanticReasonCode`
  - `message: str | None = None`
- `EvidenceSemanticClaimResult`
  - `claim_id`
  - `fact_id`
  - `source_field_id`
  - `status`
  - `severity`
  - `reason_code`
  - `matched_anchor_ids`
  - `message`
- `EvidenceSemanticResult`
  - `schema_version`
  - `fund_code`
  - `report_year`
  - `claim_results`
  - `overall_status: EvidenceSemanticOverallStatus`

Add a Protocol:

```python
class EvidenceEntailmentClient(Protocol):
    def judge(self, request: EvidenceEntailmentRequest) -> EvidenceEntailmentJudgment:
        ...
```

Add public function:

```python
def confirm_semantic_entailment(
    *,
    evidence_result: EvidenceConfirmResultV2,
    references: tuple[EvidenceConfirmReference, ...],
    claims: tuple[EvidenceSemanticClaim, ...],
    client: EvidenceEntailmentClient,
) -> EvidenceSemanticResult:
    ...
```

Do not add async, provider transport, retry, timeout or network fields in this gate. Provider lifecycle belongs to a later explicit provider gate.

## State-machine and Data-flow Semantics

Per claim:

1. Find the matching V2 fact result by `(fact_id, source_field_id)`.
2. If no matching fact result exists, return `status="insufficient"`, `severity="block"`, `reason_code="deterministic_gate_failed"`.
3. If deterministic hard gate failed, return `status="insufficient"`, `severity="block"`, `reason_code="deterministic_gate_failed"` without calling the semantic client.
4. If deterministic dimensions `source_support`, `missing_evidence` or `proof_boundary` are not `pass`, return `status="insufficient"`, `severity="block"`, `reason_code="deterministic_gate_failed"` without calling the semantic client.
5. If `value_match` is `fail`, return `status="insufficient"`, `severity="block"`, `reason_code="deterministic_gate_failed"` without calling the semantic client.
6. `anchor_precision` may be `warn`; semantic checking may run, but the result severity cannot be lower than `warn` if the deterministic fact hard gate is `warn`.
7. If `claim_text.strip()` is empty, return `status="not_applicable"`, `severity="info"`, `reason_code="missing_claim"` without calling the client.
8. Bound excerpts to same claim anchor ids using proven `EvidenceConfirmReference` entries that appear in the deterministic fact matched anchors. If no bounded excerpt exists, return `status="insufficient"`, `severity="block"`, `reason_code="missing_bounded_excerpt"` without calling the client.
9. Call `client.judge()` with claim text and bounded excerpt texts only.
10. Validate returned judgment. If the result is not an `EvidenceEntailmentJudgment` or contains invalid literal values, return `status="insufficient"`, `severity="block"`, `reason_code="malformed_client_result"`.
11. If `client.judge()` raises, catch and return `status="insufficient"`, `severity="block"`, `reason_code="client_exception"`; do not leak exception repr details that may contain provider metadata in future gates.
12. Map valid client statuses:
    - `entailed` -> `severity="info"`, or `warn` when deterministic fact hard gate is warn.
    - `contradicted` -> `severity="block"`.
    - `insufficient` -> `severity="warn"`.
    - `not_applicable` -> `severity="info"`.

Aggregate:

- `overall_status="fail"` if any claim result is `status="contradicted"` or `severity="block"`.
- Else `overall_status="warn"` if any claim result is `status="insufficient"` or `severity="warn"`.
- Else `overall_status="pass"` if at least one claim result is `status="entailed"` and no block/warn remains.
- Else `overall_status="not_applicable"`.

The aggregate status is intentionally a gate status, not another semantic support status. Per-claim `status` answers semantic support; aggregate `overall_status` answers whether the semantic gate passes, warns, fails or is not applicable.

## Implementation Decisions

- Keep semantic code in a new module to avoid mutating V2 public schema.
- Use explicit `EvidenceSemanticClaim`; do not infer claim text from `ChapterFactEntry.value`.
- Use deterministic V2 as prerequisite, not as data to be overwritten.
- Preserve stable sorting by `(source_field_id, fact_id, claim_id)`.
- Use only in-memory references supplied to the function.
- Do not call `confirm_projection_evidence_v2()` inside semantic function; caller must pass V2 result explicitly so the contract remains composable and testable.
- Avoid nested functions/classes.
- Add Chinese module/class/function docstrings per `AGENTS.md`.
- Do not add comments unless needed for non-obvious gate ordering.

## Implementation Slices

### Slice EC-P3-S1: Semantic Companion Contract

Objective: add no-live semantic contract and tests.

Allowed files:

- `fund_agent/fund/evidence_confirm_semantic.py`
- `tests/fund/test_evidence_confirm_semantic.py`
- `fund_agent/fund/README.md`
- `tests/README.md` only if needed

Exact allowed changes:

- Add schema constant, literal type aliases, dataclasses, Protocol and `confirm_semantic_entailment()`.
- Add helper functions for deterministic fact lookup, dimension status lookup, reference bounding, judgment validation, severity mapping and aggregate status.
- Add fake clients in tests only.
- Export public names through `__all__` in the new module.
- Document Fund-layer no-live semantic contract in Fund README.

Non-goals:

- Do not modify V2 result dataclasses.
- Do not add real provider, async, network, repository, Service, UI, Host, renderer or quality-gate calls.
- Do not run live commands.

Tests:

- `test_semantic_entailed_passes_after_deterministic_v2_pass`
- `test_semantic_contradicted_blocks`
- `test_semantic_insufficient_warns`
- `test_semantic_not_applicable_for_blank_claim_without_client_call`
- `test_semantic_does_not_call_client_when_deterministic_value_match_fails`
- `test_semantic_does_not_call_client_when_candidate_only_reference_fails_proof_boundary`
- `test_semantic_malformed_client_result_fails_closed`
- `test_semantic_client_exception_fails_closed_without_exception_message`
- `test_semantic_anchor_precision_warn_keeps_warn_severity_for_entailed`
- `test_semantic_aggregate_warns_when_claim_insufficient`
- `test_semantic_module_import_isolated_from_service_provider_host_renderer_quality_gate`

Validation commands:

```bash
uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_semantic.py -q
uv run ruff check fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py
git diff --check -- fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py fund_agent/fund/README.md tests/README.md
```

Expected assertions:

- Existing Evidence Confirm V1/V2 tests still pass.
- New semantic suite proves deterministic failures prevent client calls.
- Import isolation test proves the semantic module source/import graph does not include `fund_agent.services`, `fund_agent.host`, provider modules, repository modules, renderer modules or quality-gate modules.

Completion signal:

- Implementation evidence artifact records changed files, tests and residuals.
- Code review gate can inspect a single semantic module and focused tests without needing Service/provider/live context.

Stop condition:

- If implementation needs a real provider, Service claim projection, renderer text parsing, quality-gate policy or mutation of `EvidenceConfirmResultV2`, stop and route to plan fix before coding.

## Docs Decision

Update `fund_agent/fund/README.md` because Fund package behavior changes. The README must state:

- semantic entailment is no-live and client-protocol-backed only;
- the caller supplies explicit claims, V2 result and references;
- semantic output cannot override deterministic source/proof/value failures;
- provider/live, Service/UI/renderer/quality-gate integration and release/readiness remain future gates.

Update `tests/README.md` only if adding the semantic test file changes test taxonomy or documented focused commands.

Do not update root README or Service/Host/Agent README in this gate because no user workflow, Service/Host/Agent boundary, CLI or product behavior changes.

## Risks and Residuals

| Risk | Classification | Owner / Destination |
|---|---|---|
| No real provider semantic quality is proven | assigned to later work unit | Controlled semantic provider evidence gate |
| No Service/renderer claim extraction exists | assigned to later work unit | Service/UI/renderer integration gate |
| Quality gate cannot consume semantic result yet | assigned to later work unit | Quality-gate integration gate |
| Semantic calibration thresholds are unproven | assigned to later work unit | Provider/calibration or release-readiness gate |
| EC-P3 numbering differs from original program plan | fixed in current planning artifacts | Current control docs and this plan establish active routing |

No unclassified residual risk is allowed at closeout.

## Plan Review Requirements

Run `planreview` on this artifact before implementation. Review must specifically challenge:

- whether explicit `EvidenceSemanticClaim` is the right boundary;
- whether deterministic failure gating is strict enough;
- whether aggregate status semantics are too broad or ambiguous;
- whether the plan is over-designed for no-live fake-client scope;
- whether import-isolation tests are meaningful and not brittle;
- whether the allowed file set is narrow enough.

Accepted findings must be fixed in this plan and re-reviewed before accepted plan commit.

## Completion Report Format

After implementation slice:

- changed files;
- public contract added;
- tests/validation results;
- docs updated;
- code-review findings status;
- residual risks with owner/destination;
- next gate.
