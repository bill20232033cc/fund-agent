# FundDisclosureDocument S6-A Candidate Evidence Contract Plan

## 1. Gate

- Gate: `FundDisclosureDocument S6-A Candidate Evidence Contract Planning Gate`
- Classification: `heavy` for implementation, because it changes processor contract dataclasses/protocols.
- Trigger: S6 field-family extraction plan was blocked by `docs/reviews/funddisclosuredocument-s6-field-family-extraction-plan-controller-judgment-20260619.md`.

## 2. Goal

Make candidate-only field-family evidence representable inside Fund processor contracts without pretending that it is public annual-report evidence, source truth, parser replacement, or facade-consumable structured facts.

This gate is a prerequisite contract slice. It does not implement section/table keyword extraction.

## 3. Non-goals

- No field-family selector implementation.
- No `FundDataExtractor` projection of candidate-only evidence.
- No change to `EvidenceAnchor.source_kind`.
- No change to `FundFieldFamilyStatus` or `FundProcessorContractStatus` enum values.
- No default production path consumption of `FundDisclosureDocument`.
- No source truth, field correctness, parser replacement, golden/readiness, release, live access, PR mutation, or unrelated cleanup.

## 4. Contract Decisions

### Decision A: admission protocol remains minimal

`FundDisclosureDocumentIntermediate` remains the admission/identity protocol. It must not require content collections.

Reason: admission and failure classification only require identity, provenance, boundary, and failure class. Requiring content on the base protocol would overcouple admission with extraction.

### Decision B: content extraction uses a second protocol

Add a separate `FundDisclosureDocumentContentIntermediate` protocol that extends the admission protocol with:

- `sections`
- `paragraph_blocks`
- `table_blocks`

Add narrow structural protocols for section, paragraph block, table block, and cell locator. These protocols must use only primitive/string/tuple fields already present on concrete `FundDisclosureDocument` objects.

The processor may check this content protocol only after admission and identity checks. If content protocol is absent, extraction helpers must fail closed to normal missing families.

### Decision C: candidate-only evidence is not public EvidenceAnchor

Add `FundCandidateEvidenceRecord` in `fund_agent/fund/processors/contracts.py`.

Required fields:

- `field_family_id: FundFieldFamilyId`
- `source_boundary: Literal["candidate_only"]`
- `source_field_path: str`
- `section_id: str | None`
- `table_id: str | None`
- `block_id: str | None`
- `cell_id: str | None`
- `heading_path: tuple[str, ...]`
- `row_locator: str | None`
- `excerpt: str`
- `locator_stability: str`
- `candidate_only: Literal[True]`
- `field_correctness_status: Literal["not_proven"]`
- `source_truth_status: Literal["not_proven"]`
- `parser_replacement_authorized: Literal[False]`
- `readiness_status: Literal["not_ready"]`

Validation:

- `source_boundary` must be `candidate_only`.
- `candidate_only` must be `True`.
- correctness/source truth/readiness fields must remain `not_proven` / `not_ready`.
- `parser_replacement_authorized` must remain `False`.
- at least one locator identity among `section_id`, `table_id`, `block_id`, `cell_id` must be present.
- `source_field_path` and `excerpt` must be non-empty.

### Decision D: candidate evidence does not satisfy public field-family status

Add an optional field to `FundFieldFamilyResult`:

```python
candidate_evidence: tuple[FundCandidateEvidenceRecord, ...] = ()
```

Rules:

- `candidate_evidence` may exist on a `missing` family.
- Candidate evidence alone must not satisfy `partial` or `accepted`.
- Current invariant remains: `status in {"accepted", "partial"}` requires public `EvidenceAnchor`.
- Current invariant remains: `status == "missing"` requires local gaps.
- `candidate_evidence` must not be copied into `value` by this slice.

Reason: the contract can carry bounded candidate evidence for later review/harness use while preserving the public fact state as missing.

### Decision E: facade projection remains blind and blocked

No S6-A change is made to `_active_processor_result_to_bundle()`.

Because `candidate_evidence` is not in `value`, existing projection cannot accidentally project it. For concrete candidate-boundary inputs, existing admission keeps result-level consumption blocked.

## 5. Implementation Write Set

Allowed files:

- `fund_agent/fund/processors/contracts.py`
- `tests/fund/processors/test_fund_disclosure_processor.py`
- `fund_agent/fund/README.md`
- `docs/design.md`

Do not edit `fund_agent/fund/data_extractor.py` in S6-A unless a test proves the new contract leaks through existing projection. If such a leak is found, stop and open a separate facade leak-fix gate.

## 6. Required Tests

Add or update tests in `tests/fund/processors/test_fund_disclosure_processor.py`:

1. `FundDisclosureDocumentIntermediate` admission-only stub still satisfies the protocol without content collections.
2. `FundDisclosureDocumentContentIntermediate` content-bearing stub satisfies the content protocol.
3. Content protocol absence does not break current processor guard/admission tests.
4. `FundCandidateEvidenceRecord` rejects:
   - non-candidate source boundary,
   - `candidate_only=False`,
   - `field_correctness_status` other than `not_proven`,
   - `source_truth_status` other than `not_proven`,
   - `parser_replacement_authorized=True`,
   - readiness other than `not_ready`,
   - empty locator identity,
   - empty `source_field_path` or `excerpt`.
5. `FundFieldFamilyResult(status="missing")` may carry `candidate_evidence` while retaining a local missing gap.
6. `FundFieldFamilyResult(status="partial")` with candidate evidence but no public `EvidenceAnchor` still raises `ValueError`.
7. Static import-boundary test remains: `fund_disclosure_processor.py` must not import concrete candidate modules, Docling, PDF/cache/source helper, network, provider, Service/UI/Host, renderer, or quality gate modules.

## 7. Documentation Updates

Update docs only after code/tests pass:

- `fund_agent/fund/README.md`: state that S6-A adds an internal candidate-evidence contract only; actual selector extraction and facade consumption remain deferred.
- `docs/design.md`: sync current Processor/Extractor/FundDisclosureDocument wording if stale, while preserving `candidate-only`, `not_proven`, and `NOT_READY`.

## 8. Validation Matrix

Run after implementation:

```bash
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
uv run ruff check fund_agent/fund/processors/contracts.py tests/fund/processors/test_fund_disclosure_processor.py
git diff --check
```

If docs are updated:

```bash
git diff --check -- fund_agent/fund/README.md docs/design.md
```

## 9. Acceptance Criteria

S6-A is accepted only if:

- candidate-only evidence has a typed internal record;
- public `EvidenceAnchor` is not used for candidate-only evidence in this slice;
- candidate evidence does not satisfy `partial` or `accepted`;
- admission-only and content-bearing protocols are separate;
- existing S5 processor/admission behavior remains intact;
- no facade projection consumes candidate evidence;
- release/readiness remains `NOT_READY`.

## 10. Next Gate After Acceptance

If S6-A is accepted, the next gate is:

`FundDisclosureDocument S6-B Single-family Candidate Evidence Selector Planning Gate`

S6-B must choose one field family and provide a concrete reviewed selector mapping before implementation. It must not implement all six families at once unless a later plan review accepts a complete mapping table and ambiguity policy.
