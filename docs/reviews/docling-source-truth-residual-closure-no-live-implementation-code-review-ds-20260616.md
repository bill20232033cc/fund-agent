# Docling Source-truth Residual Closure No-live Implementation Code Review (AgentDS) - 2026-06-16

Gate: `Docling Source-truth Residual Closure No-live Implementation Gate`
Role: code review worker (AgentDS)
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Inputs Reviewed

Accepted plan:
- `docs/reviews/docling-source-truth-residual-closure-plan-20260616.md`

Controller judgment:
- `docs/reviews/docling-source-truth-residual-closure-plan-controller-judgment-20260616.md`

Implementation evidence:
- `docs/reviews/docling-source-truth-residual-closure-no-live-implementation-evidence-20260616.md`

Changed files:
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`

## 2. Validation Result

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
→ 13 passed in 0.76s

git diff --check
→ (no output, clean)
```

## 3. Findings

### F1: `_normalize_for_match` strips decimal separators, enabling rare false‑positive numeric matches

**Location:** `source_truth_residual_closure.py` line 1309–1310

`_normalize_for_match` removes `[\s,，。．.()（）]` including `.`, which collapses `149698325.51` to `14969832551`. Two numerically different values that differ only in decimal placement would normalize to the same string (e.g. `1496.9832551` → `14969832551`). In practice the disambiguation layers (section/table/row-label/column-header checks) constrain the blast radius, but this is an unnecessary risk in a fail‑closed helper. A delimiter‑aware numeric normalization would be safer.

**Severity:** Low. Mitigated by the required triple‑layer closure (source + processed + fund).

---

### F2: `_has_share_class_context` over‑matches short class labels like `"A"`

**Location:** `source_truth_residual_closure.py` lines 1289–1292

```python
if normalized_value.endswith(normalized_share) and len(normalized_value) > 1:
    return True
```

For `share_class_context="A"`, any normalized column header ending with `"a"` (e.g. English word `"beta"`) would match. In practice Chinese annual‑report column headers use `A类`/`C类`, not Latin words, so the blast radius is negligible. Still worth noting as a fragility in the share‑class matching rule.

**Severity:** Low. No practical attack surface in current Chinese annual‑report domain.

---

### F3: No explicit test for `locator_context_conflict` path

**Location:** `source_truth_residual_closure.py` line 670–671

`_processed_status` returns `locator_context_conflict` when `anchor.section_id != rule.expected_section_id`. All existing tests use matching section IDs. There is no test that asserts a row with `section_id="§8"` and `field_name="fund_code"` (which requires `§2`) produces `blocked_locator_unavailable`. The code path is exercised implicitly by the rule structure but lacks a dedicated assertion.

**Severity:** Low. The logic is straightforward and the path is unreachable in normal operation because the evidence wrapper builds bundles from the same document the candidate came from.

---

### F4: No explicit test for unknown `field_name` → `blocked_rule_missing`

**Location:** `source_truth_residual_closure.py` lines 561–568

If `FIELD_RULES` doesn't contain the field name, `_close_row` returns `blocked_rule_missing` with `fund_layer_status = "semantic_rule_missing"`. This is correct per the plan's required disposition table, but there is no test for it. A one‑line test asserting an unknown field produces `blocked_rule_missing` would complete the coverage.

**Severity:** Low. Straightforward fail‑closed pattern.

---

### F5: `EvidenceAnchor.source_kind` guard is verified twice in `_processed_status` with different anchor keys

**Location:** `source_truth_residual_closure.py` lines 663–667

```python
if anchor.get("evidence_anchor_source_kind") not in (None, _ANNUAL_REPORT_EVIDENCE_SOURCE_KIND):
    return "candidate_metadata_violation"
if anchor.get("source_kind") not in (None, _ANNUAL_REPORT_EVIDENCE_SOURCE_KIND):
    return "candidate_metadata_violation"
```

Two keys check the same semantic contract (`EvidenceAnchor.source_kind == "annual_report"`). The test fixture only sets `source_kind`, never `evidence_anchor_source_kind`. This is duplicate defense, not a bug, but could confuse readers about which key is canonical. The plan uses `EvidenceAnchor.source_kind`; `source_kind` is the canonical field and `evidence_anchor_source_kind` is a belt‑and‑suspenders alias.

**Severity:** Informational. No functional issue.

---

### F6: Aggressive `_normalize_for_match` whitespace‑stripping could join adjacent Chinese characters into false matches

**Location:** `source_truth_residual_closure.py` line 1310

`re.sub(r"[\s,，。．.()（）]+", "", normalized)` strips all whitespace. For labels like `"其中：股票"`, after normalization this becomes `"其中股票"`, which is the correct collapsed form. But for longer text with meaningful whitespace boundaries, it could produce false concatenations. Mitigated by the fact that label matching uses `_contains_any` with `_normalize_for_label` (which only strips whitespace, preserving other characters), and value matching goes through the triple‑layer guard.

**Severity:** Low.

---

## 4. Contract and Boundary Verification

### 4.1 Pure helper boundaries — PASS

| Check | Result |
| --- | --- |
| Does not import `FundDocumentRepository` | Confirmed. No import of repository modules. |
| Does not call Docling | Confirmed. No docling imports. |
| Does not read files | Confirmed. No `open()`, `Path.read_*`, or file I/O. Test `test_pure_helper_boundary_does_not_read_or_call_repository` verifies with monkeypatched `open`. |
| Does not call source helpers | Confirmed. No source‑helper imports. |
| Does not construct production `EvidenceAnchor` | Confirmed. No EvidenceAnchor import. |
| Is candidate‑only (not in public package exports) | Confirmed. Located under `candidates/`, not re‑exported from `fund_agent.fund.documents`. |

### 4.2 Repository/processor/anchor boundary separation — PASS

Output row preserves three distinct identities:

| Identity | Field in output | Source in code | Value in tests |
| --- | --- | --- | --- |
| Repository source | `matched_repository_source_name` | `RepositoryReferenceCell.repository_source_name` | `"eid"` |
| Processor route | `candidate_processor_source_kind` | `candidate_anchor["candidate_source_kind"]` | `"docling_pdf_candidate"` |
| EvidenceAnchor source kind | `evidence_anchor_source_kind` | Hardcoded `_ANNUAL_REPORT_EVIDENCE_SOURCE_KIND` | `"annual_report"` |

Test `test_boundary_fields_keep_repository_processor_and_anchor_kind_separate` asserts they are distinct and non‑overlapping.

### 4.3 S5-F023 and S6-F041 fail‑closed — PASS

**S5-F023 (`investment_objective`):**
- Rule requires `required_row_label_any=("投资目标",)` and `semantic_guard="投资目标"`
- Without source body text in the reference bundle, `_source_matches` returns empty → disposition `source_body_mismatch`, source_status `same_source_text_absent`
- Cannot close without same‑source repository body proof
- Verified by `test_investment_objective_without_same_source_body_stays_mismatch`

**S6-F041 (`benchmark`):**
- Rule has `rejected_row_label_any=("投资目标",)` and `semantic_guard="业绩比较基准"`
- Reference cell with row_label `("投资目标",)` and table_context `("投资目标",)` fails both: rejected by `rejected_row_label_any` AND fails `semantic_guard` (neither row_label nor table_context contains `"业绩比较基准"`)
- Disposition `semantic_assignment_residual`, fund_status `semantic_rule_rejected`
- Cannot close without benchmark‑labeled source context
- Verified by `test_benchmark_guard_keeps_investment_objective_context_residual`

### 4.4 Source / processed / fund status coherence — PASS

Only the triple condition produces `disambiguated_source_body_match`:

```text
source_layer_status  == same_source_reference_loaded  AND
processed_layer_status == locator_context_available   AND
fund_layer_status     == semantic_rule_satisfied
```

Verified failure paths:

| Failure | Disposition | Source status | Processed status | Fund status |
| --- | --- | --- | --- | --- |
| No rule | `blocked_rule_missing` | `blocked_reference_unavailable` | (as computed) | `semantic_rule_missing` |
| No bundle | `blocked_reference_unavailable` | `blocked_reference_unavailable` | (as computed) | `semantic_rule_unresolved` |
| Bad metadata | `blocked_reference_unavailable` | `metadata_violation` | (as computed) | `semantic_rule_unresolved` |
| No source match | `source_body_mismatch` | `same_source_text_absent` | (as computed) | `semantic_rule_unresolved` |
| Insufficient locator | `blocked_locator_unavailable` | `same_source_reference_loaded` | `locator_context_insufficient` | `semantic_rule_unresolved` |
| Semantic rejection | `semantic_assignment_residual` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_rejected` |
| Duplicate residual | `semantic_equivalent_duplicate_residual` | `same_source_reference_loaded` | `locator_context_available` | `semantic_rule_unresolved` |
| Metadata violation | `blocked_candidate_metadata_violation` | `blocked_reference_unavailable` | `candidate_metadata_violation` | `semantic_rule_unresolved` |

Every non‑closure path is explicit and named. No generic `pass` status exists.

### 4.5 Guard flags — PASS

All six non‑proof guard flags are present and asserted:

```python
not_baseline_promotion=True
not_parser_replacement=True
not_release_readiness=True
not_full_field_correctness=True
not_raw_pdf_bbox_truth=True
candidate_only=True
```

Verified by `test_output_guard_flags_are_preserved`. Output rows also carry `source_truth_status = "not_proven"` and `candidate_only = True`.

### 4.6 No incorrect readiness claims — PASS

Implementation evidence document explicitly states:
- `NOT_READY` preserved
- No baseline qualification claimed
- No parser replacement claimed
- No release readiness claimed
- No PR readiness claimed
- No full field correctness claimed
- Evidence matrix JSON deferred to later evidence gate

## 5. Test Coverage Assessment

| Plan §6 requirement | Test | Status |
| --- | --- | --- |
| identity code disambiguation | `test_identity_code_disambiguates_main_code_from_trading_code` | Covered |
| identity name disambiguation | `test_identity_name_closes_only_on_labeled_profile_row` | Covered |
| manager/custodian disambiguation | `test_manager_and_custodian_close_on_labeled_profile_rows` | Covered |
| portfolio parent/child split | `test_portfolio_parent_child_split_uses_row_label_not_value_only` | Covered |
| fixed-income hierarchy rejection | `test_fixed_income_rejects_fair_value_hierarchy_and_accepts_portfolio_row` | Covered |
| benchmark semantic guard | `test_benchmark_guard_keeps_investment_objective_context_residual` | Covered |
| investment-objective mismatch | `test_investment_objective_without_same_source_body_stays_mismatch` | Covered |
| unresolved duplicate | `test_unresolved_expense_duplicate_remains_semantic_equivalent_residual` | Covered |
| boundary fields | `test_boundary_fields_keep_repository_processor_and_anchor_kind_separate` | Covered |
| guard flags | `test_output_guard_flags_are_preserved` | Covered |
| pure helper boundary | `test_pure_helper_boundary_does_not_read_or_call_repository` | Covered |
| missing reference bundle | `test_missing_reference_bundle_blocks_reference_layer` | Covered |
| *(bonus)* candidate truth‑claim guard | `test_candidate_boundary_guard_rejects_truth_claims` | Covered |

All 12 required tests plus 1 extra guard test are present and pass.

Gaps (not blocking):

- No test for `field_name not in FIELD_RULES` → `blocked_rule_missing`
- No test for `section_id` conflict → `locator_context_conflict`
- No test for `source_kind` not in `(None, "annual_report")` → `candidate_metadata_violation`

These paths are straightforward and fail‑closed; the existing 13 tests cover the plan's explicit requirements.

## 6. Production Boundary Check

| Production surface | Touched? |
| --- | --- |
| `FundDocumentRepository` | No |
| `EvidenceAnchor` schema | No |
| Production parser behavior | No |
| Source policy | No |
| Service / UI / Host / Renderer | No |
| Quality gate | No |
| Public package exports (`fund_agent.fund.documents`) | No |

## 7. Conclusion

**PASS_WITH_FINDINGS**

The implementation correctly implements the accepted plan's pure helper contract:

- All three identity layers (source, processed, fund) are independently assessed and fail‑closed.
- S5-F023 and S6-F041 cannot be closed without the required proof.
- `repository_source_name`, processor route identity, and `EvidenceAnchor.source_kind` are cleanly separated.
- No file I/O, repository, Docling, or source‑helper access occurs in the pure helper.
- No production surface was modified.
- No incorrect readiness, baseline, or parser‑replacement claims are made.
- All 13 tests pass; git diff is clean.

Six low‑severity findings are recorded above (F1–F6). None is blocking. The three minor test coverage gaps (F3, F4, section‑id/field‑name edge cases) are not required by the plan's §6 test table and do not affect correctness.

The implementation gate may proceed to the evidence gate when controller accepts.
