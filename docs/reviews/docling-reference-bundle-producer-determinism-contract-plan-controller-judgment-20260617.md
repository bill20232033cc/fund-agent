# Docling Reference Bundle Producer Determinism Contract Plan Controller Judgment - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism Contract Planning Gate`
Role: controller
Status: `PLAN_REVIEW_COMPLETE_FIX_REQUIRED_NOT_READY`
Verdict: `ACCEPT_PLAN_REVIEW_FINDINGS_READY_FOR_NARROW_PLAN_FIX_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Plan: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`
- DS plan review: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-review-ds-20260617.md`
- MiMo plan review: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-review-mimo-20260617.md`
- Prior accepted diagnostic judgment: `docs/reviews/docling-reference-bundle-comparability-diagnostic-controller-judgment-20260617.md`

## Review Summary

Both reviewers returned `PASS_WITH_FINDINGS_NOT_READY`.

| Reviewer | Blocking findings | Non-blocking findings | Controller disposition |
| --- | ---: | ---: | --- |
| AgentDS | 0 | 4 | Accept findings as plan-fix inputs |
| AgentMiMo | 0 | 4 | Accept findings as plan-fix inputs |

The plan correctly targets the accepted comparability diagnostic root problem: wrapper/reference-bundle construction drift before helper semantics. It preserves candidate-only / `source_truth_status=not_proven` / `NOT_READY` boundaries and does not claim source truth, baseline promotion, parser replacement, full field correctness, release readiness, PR readiness, or golden readiness.

The plan is not ready for implementation handoff until a narrow plan fix resolves the accepted ambiguity and determinism details below.

## Finding Disposition

| Finding | Controller disposition | Required fix |
| --- | --- | --- |
| DS-F1: Slice 4 conditional wrapper ambiguity | `accepted` | Remove conditional implementation ambiguity. Current controller check found no committed standalone evidence wrapper under `scripts`, `fund_agent/fund/documents`, or `tests/fund/documents`; Slice 4 must be rewritten as future evidence-artifact contract requirements, not an implementation slice. |
| MiMo-Fn: Slice4 evidence wrapper contract uncertainty | `accepted` | Same as DS-F1. Record that no committed wrapper is currently identified and that no new production CLI is authorized. |
| MiMo-Fn: validation commands unspecified | `accepted` | Add exact validation commands for the future implementation handoff, including the target source file, target test file, `pytest`, `ruff check`, and `git diff --check`. |
| DS-F2: test file path missing | `accepted` | Specify the target test file. Existing related tests live at `tests/fund/documents/test_docling_source_truth_residual_closure.py`; the fix may either extend that file or name a new deterministic producer test file, but must choose explicitly. |
| DS-F3: fingerprint input range not precise | `accepted` | Add a precise fingerprint input-field list and separate hash-participating content from companion metadata. |
| MiMo-Fn: hash algorithm unspecified | `accepted` | Specify the stable hash algorithm and serialization method for `bundle_content_fingerprint` and `normalized_text_hash`. |
| MiMo-Fn: `raw_text_excerpt` bound not quantified | `accepted` | Specify the excerpt character bound and truncation convention. |
| DS-F4: contract version string uses example wording | `accepted` | Replace example wording with an exact binding version constant/string. |

## Next Gate

Enter `Docling Reference Bundle Producer Determinism Contract Plan Fix Gate`.

Allowed write set:

- `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`

Required fix scope:

1. Apply the accepted finding dispositions above.
2. Preserve the plan's core non-goals and all boundary flags.
3. Do not introduce implementation code, tests, runtime artifacts, design/control doc edits, README edits, commits, push, PR, release, live/network/provider/LLM/analyze/checklist/golden/readiness commands, direct PDF/cache/source-helper access, or repository reload.
4. Keep release/readiness as `NOT_READY`.

After the plan fix, run `git diff --check -- docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md` and return to controller for targeted re-review.

## Controller Self-check

- Current role: controller; this artifact records review disposition only.
- Source of truth: current control docs, prior comparability diagnostic controller judgment, DS review, MiMo review, and local wrapper-path search.
- Scope boundary: controller judgment artifact only; no plan fix, code, tests, runtime, README, design/control sync, commit, push, PR, release, or readiness action.
- Stop condition: implementation handoff is blocked until the plan fix gate resolves accepted findings.
- Next action: dispatch a narrow plan fix worker for the single allowed plan artifact.

VERDICT: `ACCEPT_PLAN_REVIEW_FINDINGS_READY_FOR_NARROW_PLAN_FIX_NOT_READY`
