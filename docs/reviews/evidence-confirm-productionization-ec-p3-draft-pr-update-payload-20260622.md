# EC-P3 Draft PR Update Payload

- Gate: push / update draft PR preparation
- Work unit: Evidence Confirm productionization / EC-P3 semantic entailment
- Date: 2026-06-22
- Target PR: `https://github.com/bill20232033cc/fund-agent/pull/40`
- Artifact path: `docs/reviews/evidence-confirm-productionization-ec-p3-draft-pr-update-payload-20260622.md`

## Remote State Observed

- Branch: `evidence-confirm-productionization`
- Upstream: `origin/evidence-confirm-productionization`
- Local status at preparation time: ahead of upstream; no tracked dirty files
- Existing PR:
  - `number=40`
  - `state=OPEN`
  - `isDraft=true`
  - `headRefOid=f11abb34047fb1e77cabf4483de0a44037344e1a`
  - `mergeStateStatus=CLEAN`
  - prior CI `test=SUCCESS`
- Current PR title before update: `Add Evidence Confirm reference materializer and live repository pathway`
- Current PR body covers EC-P1A and EC-P2 only; it still states semantic entailment is a non-goal.

## Proposed PR Title

```text
Add Evidence Confirm productionization materializer, live pathway, and semantic contract
```

## Proposed PR Body

```markdown
## Scope

This draft PR covers the accepted EC-P1A, EC-P2 and EC-P3 Evidence Confirm productionization slices.

- EC-P1A: no-live Fund-layer annual-report reference materializer from caller-supplied `ParsedAnnualReport` and `ChapterFactProjection`.
- EC-P2: repository-bounded runner that calls only `FundDocumentRepository.load_annual_report(...)`, builds annual-report Evidence Confirm references, classifies repository/source failures, and optionally runs V2 Evidence Confirm.
- EC-P2 authorized live sample script: `scripts/evidence_confirm_ec_p2_live_sample.py` is hard-limited to `004393/2025` and emits safe scalar JSON only.
- EC-P3: no-live Fund-layer semantic entailment companion contract `evidence_confirm_semantic.v1` with explicit `EvidenceSemanticClaim` inputs and injected `EvidenceEntailmentClient` protocol.
- Deterministic V2 remains authoritative: semantic output cannot override deterministic source/proof/value failures.
- Warning disposition: section-only smoke keeps strict `status="fail"` and V2 `evidence_confirm_overall_status="warn"`, while runner-local `pathway_status="pass"` proves only the repository/source/PDF pathway for the exact sample.

## Accepted evidence

- `uv run pytest tests/fund/test_evidence_confirm_sources.py -q` -> 39 passed
- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q` -> 86 passed
- `uv run ruff check fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py` -> passed
- `uv run python scripts/evidence_confirm_ec_p2_live_sample.py --fund-code 004393 --report-year 2025 --force-refresh` -> exit 0, `pathway_status="pass"`, strict `status="fail"`, V2 `warn`, `field_correctness_proven=false`
- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_semantic.py -q` -> 60 passed
- `uv run ruff check fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py` -> passed
- `git diff --check -- fund_agent/fund/evidence_confirm_semantic.py tests/fund/test_evidence_confirm_semantic.py fund_agent/fund/README.md tests/README.md` -> passed

## Non-goals

- No provider-backed semantic quality proof.
- No Service/UI/renderer/quality-gate production integration yet.
- No public `EvidenceSourceKind` / `EvidenceAnchor` expansion.
- No source fallback behavior change.
- No readiness/release promotion.
- PR remains draft; this does not mark ready, merge, or request reviewers.
```

## Execution Boundary

Do not execute the following without explicit authorization:

```bash
git push
gh pr edit 40 --title "Add Evidence Confirm productionization materializer, live pathway, and semantic contract" --body-file <prepared-body-file>
```

## Residuals

- Provider-backed semantic quality remains a later gate.
- Service/UI/renderer/quality-gate production integration remains a later gate.
- Release/readiness remains `NOT_READY`.
- No PR mark-ready, merge or reviewer request is authorized.

## Next Entry Point

After explicit authorization, push existing branch and update draft PR #40 title/body with the payload above.
