# Post-P7 Residual Design Slice Planning（2026-05-21）

## Current State

Post-P7 repo-level code findings have been reconciled and closed.

Accepted code follow-up commits:

- `58bba13`：PDF/cache/gate/fund_code aggregate fixes
- `26adce7`：`CLAUDE.md` cleanup and post-P7 plan
- `eb32912`：design/control/code reconciliation
- `551442a`：compound fund type evidence
- `55c07dc`：ITEM_RULE facet mapping
- `a303d7f`：document cache concurrency
- `95dd76c`：fund type trigger tightening and cache initialize lock
- `aec9310`：manager extractor partial note
- `18cb94d`：ratio input contract
- `b70effd`：DS repo review reconciliation

Latest verified full suite:

```text
322 passed
```

Tracked worktree is clean. Remaining untracked files are local/generated artifacts outside this planning gate.

## Residual Items

### R1. `must_answer` Audit Consumption

Status: real residual design item.

Current fact:

- `CHAPTER_CONTRACT.must_answer` exists in `fund_agent/fund/template/contracts.py`.
- Programmatic C2 audit currently checks deterministic marker/metadata constraints, `required_output_items`, and `must_not_cover`.
- `must_answer` is semantic. A naive keyword check would create false confidence.

Recommended next slice:

- Name: `P8-S1 must_answer audit contract design`
- Owner: Capability audit/template design
- Goal: decide whether `must_answer` belongs to deterministic C2 markers, LLM audit, evidence confirm, or a hybrid.
- Non-goal: do not add brittle keyword matching for all must_answer questions in one patch.

Acceptance criteria:

- Design artifact explicitly maps each `must_answer` class to one of:
  - deterministic marker
  - structured data availability
  - LLM semantic audit
  - evidence confirm
  - intentionally non-programmatic narrative guidance
- Programmatic audit docs explain what C2 does and does not prove.
- Tests cover at least one deterministic `must_answer` enforcement path if the design assigns any to programmatic audit.

### R2. Renderer `preferred_lens` Application

Status: real residual design item.

Current fact:

- `preferred_lens` is machine-readable and validated.
- `resolve_preferred_lens()` is currently consumed by extraction score / template applicability.
- `render_template_report()` does not inject lens content into report Markdown.

Recommended next slice:

- Name: `P8-S2 renderer preferred_lens application design`
- Owner: Capability template design
- Goal: decide how lens affects report generation without turning the report into pasted meta-instructions.
- Non-goal: do not simply dump lens strings into rendered report.

Acceptance criteria:

- Design defines lens application level:
  - chapter planning only
  - visible section wording
  - item ordering
  - evidence requirements
  - quality gate applicability only
- Renderer tests demonstrate at least two fund types produce intentionally different chapter emphasis while preserving 8章 structure and audit inputs.
- README/design docs distinguish “lens as generation guidance” from “lens as visible report text”.

### R3. EID Schema Error Fallback Policy

Status: explicitly deferred policy item.

Current fact:

- EID is official source and primary.
- Current policy is fail-closed on schema/mismatch to avoid hiding official source drift or wrong report identity behind fallback success.
- Eastmoney remains fallback for unavailable/not-found cases where identity is not contradicted.

Recommended next slice:

- Name: `P8-S3 source fallback policy design`
- Owner: Document repository/source design
- Goal: formalize source error taxonomy and fallback eligibility.

Acceptance criteria:

- Source errors are classified as `unavailable`, `not_found`, `schema_drift`, `identity_mismatch`, `integrity_error`.
- Fallback policy is table-driven and tested.
- Source metadata records when fallback was blocked by fail-closed official-source drift.

### R4. Cheap Quality Gate Rejection Before Expensive Extraction

Status: performance optimization; not correctness blocker.

Current fact:

- `analyze` currently performs extraction before full single-fund quality gate.
- Some not-run/block outcomes could be detected from selected pool membership before extraction.
- Reordering can affect UX and artifact availability.

Recommended next slice:

- Name: `P8-S4 preflight quality gate optimization design`
- Owner: Service/quality gate design
- Goal: define preflight checks that are behavior-preserving and artifact-transparent.

Acceptance criteria:

- `off/warn/block` semantics stay identical from CLI perspective.
- If extraction is skipped, CLI explains that the report was not generated because preflight quality gate failed.
- Tests cover non-selected fund with `block` policy without invoking extractor.

### R5. C2 Marker Granularity

Status: audit enhancement; related to R1.

Current fact:

- C2 deterministic checks use current marker strategy.
- Some required items may share broad markers, limiting independent proof.

Recommended next slice:

- Fold into `P8-S1` unless it becomes a separate implementation slice after audit design.

## Proposed Next Gate

Next gate should be planning-only:

```text
P8-S1 must_answer audit contract design
```

Rationale:

- It addresses the highest-severity remaining DS residual.
- It touches audit semantics and template contracts, so it should start with design and plan review.
- Renderer lens application should come after C2 audit semantics are clear, because lens output can change what audit must verify.

## Verification Baseline

Before opening any P8 implementation slice, preserve this baseline:

```bash
pytest
git diff --check
```

Expected current baseline:

```text
322 passed
tracked worktree clean
```
