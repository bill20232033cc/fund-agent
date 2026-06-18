# MiMo Review - Fixture Promotion State / Strict Golden 2025 Promotion Planning Gate

Date: 2026-06-13

Target: `docs/reviews/mvp-fixture-promotion-state-strict-golden-2025-promotion-plan-20260613.md`

Verdict: `REVISE_BEFORE_ACCEPT`

## Scope

This review checked the planning artifact only. It did not modify files and did
not run live EID, network, PDF, FDR, provider, LLM, analyze, checklist,
readiness, release, PR, push, merge, cleanup or promotion commands.

## Blockers

| Finding | Disposition required | Rationale |
|---|---|---|
| The planned future strict golden 2025 answer implementation gate did not decide whether reviewed Markdown or JSON-only evidence is the authoritative upstream for 2025 rows. | Must amend before acceptance. | Current Markdown-to-JSON build path treats Markdown rows without explicit year as legacy 2024, while strict JSON identity requires fund and record `report_year` alignment. A worker could either rebuild 2025 rows as 2024 or hand-edit JSON so that reviewed Markdown is no longer reproducible. |

Required amendment:

- Add an evidence-gate question: decide whether 2025 strict golden answer
  authority is JSON-only accepted evidence or blocked pending a
  Markdown/schema/build-tooling gate that can encode `report_year`.
- Do not open a strict golden 2025 answer write gate until that authority
  question is answered.

## Non-blocking Findings

| Finding | Disposition required | Rationale |
|---|---|---|
| Primary next entry is correct. | Accept. | `Strict golden 2025 answer evidence gate` preserves evidence-first sequencing and avoids direct promotion. |
| Future evidence gate command boundary needs a precise read-only loader command. | Amend. | The plan accepted loader output as evidence but did not initially whitelist the exact read-only command. |
| Fixture promotion `promoted_fixture` authorization should be hardened. | Amend. | Current preflight treats `promoted_fixture` as unblocked; a separate controller judgment and direct evidence should be required before any promoted state. |

## Reviewer Recommendation

Accept the plan only after the amendments above are incorporated. Release and
readiness must remain `NOT_READY`.
