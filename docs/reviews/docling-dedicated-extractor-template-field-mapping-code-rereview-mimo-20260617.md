# Docling Dedicated Extractor Template-field Mapping Code Re-Review — AgentMiMo 2026-06-17

Gate: `Docling Dedicated Extractor Template-field Mapping No-live Implementation Gate`
Role: AgentMiMo code reviewer
Re-review scope: post-code-review patch (3 new tests + 1 new `__post_init__` guard)
Reviewed files:
- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`

## Patch Delta

| Change | File | Lines |
|---|---|---|
| `CandidateTemplateFieldAnchor.__post_init__` requires `note.startswith("candidate_only:")` | `template_field_extraction.py` | 114–128 |
| Import `CandidateTemplateFieldAnchor` | `test_docling_template_field_extraction.py` | 19 |
| `test_docling_template_field_extractor_rejects_invalid_target_field_paths` | `test_docling_template_field_extraction.py` | 468–481 |
| `test_docling_template_field_extractor_uses_text_label_fallback` | `test_docling_template_field_extraction.py` | 484–504 |
| `test_candidate_template_field_anchor_rejects_non_candidate_note` | `test_docling_template_field_extraction.py` | 507–519 |

## Validation

- `uv run pytest tests/fund/documents/test_docling_template_field_extraction.py -q`: **10 passed**
- `uv run ruff check ...`: **All checks passed!**

## Anchor `note` Prefix Guard

PASS — no new blocker.

`CandidateTemplateFieldAnchor.__post_init__` now raises `ValueError` if `note` does not start with `"candidate_only:"`. This is a structural anti-tampering guard: no code path can construct an anchor that looks like a production `EvidenceAnchor` note.

Existing construction paths already comply:
- `_anchor_for_cell` produces `f"candidate_only:{note}; locator_hash=..."` (line 960)
- `_anchor_for_text_block` produces `f"candidate_only:{note}; source_ref=..."` (line 991)

The guard is purely additive — it cannot break any existing direct/matching path. It only rejects future code that would construct an anchor without the prefix, which is the intended fail-closed behavior.

## New Test: `rejects_invalid_target_field_paths`

PASS — covers three `_validate_target_field_paths` branches:

1. Empty tuple → `"cannot be empty"`
2. Duplicate path → `"duplicates"`
3. Unknown path → `"unsupported"`

Each branch is hit with a distinct `pytest.raises(ValueError, match=...)`. No branch left uncovered.

## New Test: `uses_text_label_fallback`

PASS — exercises `_match_text_label_field`.

Constructs a document with no tables and a single text block `"基金代码：004393"` in `§2`. Asserts:
- `extraction_mode == "direct"`
- `value == "004393"`
- `anchors[0].note.startswith("candidate_only:")`

This confirms the table→text fallback path works and the new anchor prefix guard is satisfied end-to-end.

## New Test: `candidate_template_field_anchor_rejects_non_candidate_note`

PASS — direct guard validation.

Constructs a `CandidateTemplateFieldAnchor` with `note="production-looking-note"` and asserts `ValueError` with `match="candidate_only"`. Confirms the `__post_init__` guard rejects non-candidate notes at construction time.

## Residual Risk Assessment

No new residual risks introduced. The patch tightens a boundary (anchor note prefix) and adds coverage for previously untested paths (text fallback, target_field_paths validation). No production types, integrations, or live dependencies added.

## Verdict

`CODE_REREVIEW_PASS_NOT_READY`
