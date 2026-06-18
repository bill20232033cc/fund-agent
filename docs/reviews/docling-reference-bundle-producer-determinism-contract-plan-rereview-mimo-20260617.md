# Docling Reference Bundle Producer Determinism Contract Plan Fix Re-review (MiMo) - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism Contract Plan Fix Re-review Gate`
Role: targeted plan re-review worker only
Target fixed plan: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`
Original DS review: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-review-ds-20260617.md`
Original MiMo review: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-review-mimo-20260617.md`
Controller judgment: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-controller-judgment-20260617.md`

## Self-check

- Assigned gate: targeted plan re-review only.
- Scope: verify accepted findings in controller judgment are fixed in the plan; do not perform new broad review.
- Only allowed write: this re-review artifact.
- Not controller, not implementation worker, no code edits, no commit/push/PR.

## Finding Verification

### DS-F1 / MiMo Slice4 ambiguity

**Controller requirement:** Slice 4 must be rewritten as future evidence-artifact contract requirements, not an implementation slice. Record that no committed wrapper exists.

**Plan current state (lines 249-273):** Section titled "Future Evidence-Artifact Contract Requirements" opens with "This section is not an implementation slice." It states: "Controller check found no committed standalone evidence wrapper under: scripts, fund_agent/fund/documents, tests/fund/documents" and "Therefore the current implementation handoff must not attempt to update a wrapper script, create a production CLI, or add a new evidence command. No new production CLI is authorized in this plan." The section specifies future evidence-artifact requirements and future evidence review validation without conditional phrasing.

**Status: 已修复**

---

### MiMo validation commands / DS-F2 test path

**Controller requirement:** Add exact validation commands (pytest, ruff check, git diff --check) with target source file and target test file.

**Plan current state (lines 278-292):** "Test Strategy" section specifies:
- Target source file: `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- Target test file: `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- Validation commands block:
  ```bash
  uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -q
  uv run ruff check fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
  git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
  ```

**Status: 已修复**

---

### DS-F3 fingerprint input range

**Controller requirement:** Add a precise fingerprint input-field list and separate hash-participating content from companion metadata.

**Plan current state (lines 90-111):** Bundle-level contract section lists:
- Hash-participating content (lines 92-104): `producer_input_mode`, `cell_count`, `text_span_count`, `table_count`, `section_count`, `table_family_counts`, `section_inference_counts`, `section_inference_reason_counts`, `row_hierarchy_role_counts`, `text_semantic_context_counts`, sorted per-cell `normalized_text_hash` values, sorted per-text-span `normalized_text_hash` values.
- Companion metadata not participating (lines 106-111): `reference_bundle_schema_version`, `enrichment_status`, `reference_generation_status`, `producer_contract_version`, `diagnostic_payload_available`.

**Status: 已修复**

---

### MiMo hash algorithm

**Controller requirement:** Specify the stable hash algorithm and serialization method for `bundle_content_fingerprint` and `normalized_text_hash`.

**Plan current state (lines 177-179):** "Required Algorithmic Constraints" section specifies:
- `bundle_content_fingerprint`: `hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()`
- `normalized_text_hash`: `hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()`
- `normalized_text` normalization: converting null to `""`, replacing all Unicode whitespace runs with a single ASCII space, and stripping leading/trailing whitespace.

**Status: 已修复**

---

### MiMo raw_text_excerpt bound

**Controller requirement:** Specify the excerpt character bound and truncation convention.

**Plan current state (lines 143-144):** Cell-level diagnostic contract specifies: "`raw_text_excerpt` must be bounded to the first 200 Unicode code points of the normalized text. If the normalized text is longer than 200 code points, the excerpt must be truncated to 200 code points and suffixed with `...`, for a maximum emitted length of 203 code points." Text-span contract (line 158) references the same convention.

**Status: 已修复**

---

### DS-F4 contract version string

**Controller requirement:** Replace example wording with an exact binding version constant/string.

**Plan current state (lines 115-117):** Uses binding language with exact Python constant:
```python
PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"
```
No "for example" wording remains.

**Status: 已修复**

---

## New Blocker Check

Verifying that the fixes did not introduce new blockers:

1. Slice 4 removal from implementation slices and replacement with "Future Evidence-Artifact Contract Requirements" does not introduce code implementation scope — it explicitly reduces scope. No new blocker.
2. Validation commands use `uv run` prefix consistent with project convention. No new blocker.
3. Fingerprint input field list is precise and consistent with bundle-level contract fields. No new blocker.
4. Hash algorithm specification (SHA256) is a single stable choice. No new blocker.
5. Excerpt bound (200 code points + `...`) is concrete and testable. No new blocker.
6. Contract version string is a binding constant. No new blocker.

**New blocker count: 0**

---

## Final Status Table

| Finding | Source | Status |
| --- | --- | --- |
| DS-F1 / MiMo Slice4 ambiguity | DS + MiMo | 已修复 |
| MiMo validation commands / DS-F2 test path | MiMo + DS | 已修复 |
| DS-F3 fingerprint input range | DS | 已修复 |
| MiMo hash algorithm | MiMo | 已修复 |
| MiMo raw_text_excerpt bound | MiMo | 已修复 |
| DS-F4 contract version string | DS | 已修复 |

---

## Verdict

`REREVIEW_PASS_NOT_READY`

All six accepted findings in the controller judgment are fixed in the plan. No new blockers were introduced by the fixes. The plan is ready for implementation handoff.

Blocking count: 0

## Self-check: pass
