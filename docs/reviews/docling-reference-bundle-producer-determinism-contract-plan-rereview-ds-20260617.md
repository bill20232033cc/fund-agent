# Docling Reference Bundle Producer Determinism Contract Plan Re-review (DS) - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism Contract Plan Fix Re-review Gate`
Role: targeted plan re-review worker only (DS)
Reviewed artifact: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`
Controller judgment: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-controller-judgment-20260617.md`
Re-review artifact: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-rereview-ds-20260617.md`

## Verdict

`REREVIEW_PASS_NOT_READY`

Blocking findings remaining: 0
Newly introduced blockers: 0

---

## Finding Fix Verification

| Finding | Required fix (per controller judgment) | Status | Evidence |
|---|---|---|---|
| DS-F1 / MiMo Slice4 ambiguity | Remove conditional implementation ambiguity; rewrite Slice 4 as future evidence-artifact contract requirements, not an implementation slice; record no committed wrapper exists | **已修复** | Plan has no Slice 4 in implementation slices. §Future Evidence-Artifact Contract Requirements explicitly states "This section is not an implementation slice." Controller check result documented (lines 252–258). "No new production CLI is authorized" stated (line 258). |
| MiMo validation commands / DS-F2 test path | Add exact validation commands; specify target test file | **已修复** | §Test Strategy specifies target test file `tests/fund/documents/test_docling_source_truth_residual_closure.py` (line 284). Exact `pytest`, `ruff check`, and `git diff --check` commands listed (lines 288–293). |
| DS-F3 fingerprint input range | Add precise fingerprint input-field list; separate hash-participating content from companion metadata | **已修复** | §Required Producer Contract → Bundle-level contract contains explicit hash-participating content list (lines 90–103) and companion metadata exclusion list (lines 105–111). |
| MiMo hash algorithm | Specify stable hash algorithm and serialization method for `bundle_content_fingerprint` and `normalized_text_hash` | **已修复** | §Required Algorithmic Constraints specifies `hashlib.sha256(json.dumps(..., sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()` for bundle fingerprint (line 177) and `hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()` for text hash (line 178). Normalization rules defined at line 179. |
| MiMo raw_text_excerpt bound | Specify excerpt character bound and truncation convention | **已修复** | Both cell-level (lines 142–143) and text-span (line 158) diagnostic contracts specify 200 code point bound, "…" truncation suffix, and maximum 203 code points when truncated. |
| DS-F4 contract version string | Replace example wording with exact binding version constant/string | **已修复** | §Bundle-level contract (line 116) declares `PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"`. No "for example" wording remains. |

---

## New Blocker Check

Verified that no new blockers were introduced by the plan fix:

- **Scope**: Slice 1–3 remain scoped to single target file `source_truth_residual_closure.py`. No new implementation slices added. No overreach.
- **Boundary flags**: `candidate_only=true`, `source_truth_status=not_proven`, `NOT_READY` preserved throughout (Non-goals lines 35–47, Stop Conditions lines 344–352, Completion Report Format lines 370–384).
- **Prohibited access**: No direct PDF/cache/source-helper access, no repository reload, no live/network added.
- **Hash specification**: SHA256 with deterministic JSON serialization (`sort_keys=True, separators`) — verifiably deterministic, no accidental non-determinism.
- **Text normalization**: Null → `""`, Unicode whitespace collapse to single ASCII space, strip — deterministic and bounded.
- **Test strategy**: Four test categories (determinism, boundary, diagnostic sufficiency, regression guard) all implementable from specification.
- **Future evidence section**: Clearly marked as non-implementation; no confusion risk for implementation worker.

No new ambiguity, scope expansion, or blocker detected.

---

## Self-check

- Assigned role: targeted plan re-review worker only (DS). Not controller, not implementation worker.
- Scope: verify accepted findings are fixed; no new broad plan review; no code implementation.
- Only allowed output: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-rereview-ds-20260617.md` — ✅ writing this file.
- No code edits: ✅
- No commit/push/PR: ✅
- No gateflow dispatch: ✅

**Self-check: pass**

---

VERDICT: `REREVIEW_PASS_NOT_READY`
