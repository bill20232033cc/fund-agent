# Bond Risk Evidence Extractor / Anchor Hardening Slice 1 — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: implementation Slice 1 acceptance
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Slice: `Slice 1 Model Contract`
> Decision: **ACCEPTED LOCALLY**

## Step Self-Check

- Current gate / role: Slice 1 accepted-slice judgment; controller role only.
- Source of truth: accepted plan commit `0a5bac9`, Slice 1 implementation artifact, two code reviews, Slice 1 fix artifact, targeted re-review, focused validation reruns.
- Scope boundary: Slice 1 model contract only; no extractor, bundle, snapshot, score, README, design/control doc, golden promotion, QDII/FOF/110020/release-readiness/Host/Agent/dayu/PR/push/merge work.
- Stop conditions: no blocking finding remains; constant drift is explicitly deferred to Slice 5 with owner.
- Evidence and validation: focused model tests and ruff passed; `git diff --check` passed.
- Next action: create accepted slice commit for Slice 1 files and artifacts, then enter Slice 2 extractor implementation.

## Implemented Scope

Changed files:

- `fund_agent/fund/extractors/models.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-implementation-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-code-review-mimo-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-code-review-ds-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-fix-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-rereview-ds-20260527.md`

Implementation summary:

- Added `bond_risk_evidence.v1` model contract types and constants.
- Added immutable group-level anchor, group record, and contract value dataclasses.
- Added `validate_bond_risk_evidence_value(...)` and helper validators.
- Enforced seven-group completeness, stable anchor id format, accepted/weak anchor requirements, accepted-absence semantics, derived group-id consistency, and contract-status derivation.
- Added focused model contract tests, including accepted Slice 1 fix coverage for edge paths.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-code-review-mimo-20260527.md` | `PASS` |
| AgentDS | `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-code-review-ds-20260527.md` | `PASS` |
| AgentDS targeted re-review | `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-rereview-ds-20260527.md` | accepted findings fixed / deferred correctly |

## Finding Judgment

| Finding | Controller judgment | Status |
|---|---|---|
| MiMo F-1 / DS F1: constants duplicated between `models.py` and `extraction_score.py` | **deferred-with-owner** | Deferred to Slice 5 Score Applicability. Slice 5 must import or cross-check canonical `models.py` contract constants and add a consistency test. |
| MiMo F-2: `weak_group_ids` / `ambiguous_group_ids` inconsistency tests missing | **accepted** | Fixed in Slice 1 fix; targeted re-review `已修复`. |
| MiMo F-3: cross-group anchor rejection test missing | **accepted** | Fixed in Slice 1 fix; targeted re-review `已修复`. |
| MiMo F-4 / DS F2: direct anchor id split in group-anchor validation | **accepted** | Fixed by reusing `_parse_bond_risk_anchor_id(...)`; targeted re-review `已修复`. |
| DS F3: edge-case validation tests missing | **accepted** | Fixed with tests for weak/ambiguous mismatches, cross-group anchor, malformed/wrong anchor id, duplicate group id, invalid status, and invalid strength; targeted re-review `已修复`. |

No finding remains unclassified.

## Validation

Controller reruns:

| Command | Result |
|---|---|
| `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q` | pass: `15 passed` |
| `uv run ruff check fund_agent/fund/extractors/models.py tests/fund/extractors/test_bond_risk_evidence.py` | pass: `All checks passed!` |
| `git diff --check` | pass |

## Residual Risks

| Residual | Owner | Required handling |
|---|---|---|
| Contract constants currently duplicated between `models.py` and `extraction_score.py` | Slice 5 Score Applicability | Import or cross-check canonical model constants and add a consistency test before accepting Slice 5. |
| No extractor/bundle/snapshot/score integration yet | Later approved slices | Proceed in approved slice order; do not claim 006597 blocker解除 from Slice 1 alone. |
| Real `006597` evidence not yet consumed | Slice 2-6 | Must rerun repository smoke, snapshot, score, and quality gate before any blocker-resolution claim. |

## Artifact Disposition For Slice 1 Commit

Stage only:

- `fund_agent/fund/extractors/models.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-implementation-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-code-review-mimo-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-code-review-ds-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-fix-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-rereview-ds-20260527.md`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-controller-judgment-20260527.md`

Do not stage unrelated untracked files.

## Decision

Slice 1 is accepted locally. Proceed to accepted slice commit, then Slice 2 extractor implementation. No push, PR, merge, mark-ready, approval, or golden promotion is authorized.
