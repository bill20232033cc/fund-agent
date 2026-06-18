# Aggregate Deepreview

## Scope

- Mode: aggregate deepreview of accepted S3 slice
- Branch: `post-merge/pr22-origin-main`
- Review range: `293026d..HEAD` (2 commits: `9387224` feat implementation, `2605ef2` closeout)
- Output file: `docs/reviews/extractor-projection-over-document-representation-aggregate-deepreview-mimo-20260618.md`
- Gate: Extractor Projection Over Document Representation Aggregate Deepreview Gate

### Reviewed Artifacts

- Plan: `docs/reviews/extractor-projection-over-document-representation-plan-20260618.md`
- Plan judgment: `docs/reviews/extractor-projection-over-document-representation-plan-controller-judgment-20260618.md`
- Implementation evidence: `docs/reviews/extractor-projection-over-document-representation-implementation-evidence-20260618.md`
- Implementation judgment: `docs/reviews/extractor-projection-over-document-representation-implementation-controller-judgment-20260618.md`
- Code reviews: `extractor-projection-over-document-representation-code-review-20260618-143548.md`, `...-143927.md`
- Code review judgment: `docs/reviews/extractor-projection-over-document-representation-code-review-controller-judgment-20260618.md`
- Accepted slice commit judgment: `docs/reviews/extractor-projection-over-document-representation-accepted-slice-commit-controller-judgment-20260618.md`
- Project instructions: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`

### Implementation Files in Commit `9387224`

| File | Action | Lines |
|---|---|---|
| `fund_agent/fund/processors/contracts.py` | Modified | +116/-2 |
| `fund_agent/fund/processors/fund_disclosure_dispatch.py` | New | 131 |
| `tests/fund/processors/test_fund_disclosure_dispatch.py` | New | 423 |
| `tests/fund/processors/test_registry.py` | Modified | +42 |
| `fund_agent/fund/README.md` | Modified | +1 sentence |

### Control/Evidence Files in Commit `9387224`

- `docs/current-startup-packet.md`, `docs/implementation-control.md`
- 5 review/judgment artifacts listed above

### Excluded from Review

- `fund_agent/fund/data_extractor.py` — confirmed unmodified
- `fund_agent/fund/documents/models.py` — confirmed unmodified
- `fund_agent/fund/extractors/models.py` — confirmed unmodified
- Service/UI/Host/Agent/renderer/quality-gate code
- Whole-repo `ruff format --check` baseline residual
- Live/source acquisition/PDF/Docling/pdfplumber/provider/LLM/readiness/release paths

---

## Specific Check Results

### 1. Pure Processor-Contract/Admission-Helper Slice

**PASS.** Commit `9387224` adds only:
- `FundDisclosureDocumentIntermediate` Protocol (7 properties, no behavior)
- `DisclosureAdmissionDecision` frozen dataclass (4 fields)
- `FAILURE_CLASS_ADMISSION_MAP` Final dict (5 entries)
- `admit_disclosure_intermediate()` pure function (no IO, no registry, no facade, no fallback)

Evidence: `fund_disclosure_dispatch.py:14-21` imports only from `contracts.py`. No import from `data_extractor`, `registry`, `documents/models`, `services`, `ui`, `host`, `agent`. The function body (`fund_disclosure_dispatch.py:101-131`) is pure conditional branching on protocol properties with no downstream calls.

### 2. No Facade / Repository / Models / SourceKind Modification

**PASS.**

| Guardrail | Evidence |
|---|---|
| `FundDataExtractor.extract()` unchanged | `git diff 293026d..HEAD -- fund_agent/fund/data_extractor.py` — no output |
| Repository behavior unchanged | No repository, source acquisition, or live path code in diff |
| `documents/models.py` unchanged | `git diff 293026d..HEAD -- fund_agent/fund/documents/models.py` — no output |
| `EvidenceSourceKind` unchanged | `git diff 293026d..HEAD -- fund_agent/fund/extractors/models.py` — no output |
| Public `EvidenceAnchor.source_kind` unchanged | `EvidenceSourceKind` remains `Literal["annual_report", "external_api", "derived"]`; test `test_no_candidate_only_leaks_to_public_evidence_source_kind` verifies |

### 3. Binding Amendment Branch Order

**PASS.** `fund_disclosure_dispatch.py:101-131`:

```python
# Line 102: failure_class first
if intermediate.failure_class is not None: ...
# Line 112: source_provenance missing second
if intermediate.source_provenance is None: ...
# Line 119: candidate_boundary third
if intermediate.candidate_boundary is not None: ...
# Line 126: satisfied last
return DisclosureAdmissionDecision(admitted=True, gap_code=None, ...)
```

Matches binding amendment precedence exactly. Test `test_failure_class_precedes_missing_provenance_and_candidate_boundary` (line 225) verifies failure_class wins over all others. Test `test_missing_provenance_precedes_candidate_boundary` (line 257) verifies provenance check wins over candidate_boundary.

### 4. Failure Taxonomy Maps Only to Existing Gap Codes

**PASS.** `FAILURE_CLASS_ADMISSION_MAP` (`fund_disclosure_dispatch.py:32-58`) uses only:
- `unsupported_intermediate` (gap code and source boundary) — for `not_found`, `unavailable`
- `candidate_boundary_blocked` (gap code) + `candidate_only` (source boundary) — for `schema_drift`, `identity_mismatch`, `integrity_error`
- `source_provenance_unsafe` (gap code and source boundary) — direct return, not in map

All exist in `FundExtractionGapCode` and `FundExtractionSourceBoundary` type definitions (`contracts.py:43-71`). Test `test_failure_class_map_covers_canonical_categories_and_existing_gap_codes` (line 360) verifies completeness and no new codes.

### 5. Test Coverage of Fail-Closed, No-Promotion, No-Leak, Unsupported

**PASS.**

| Behavioral Requirement | Test | Evidence |
|---|---|---|
| Fail-closed: `candidate_only=False` rejected | `test_candidate_boundary_rejects_candidate_only_false` (line 97) | `pytest.raises(ValueError, match="candidate_only")` |
| Fail-closed: `parser_replacement_authorized=True` rejected | `test_candidate_boundary_rejects_parser_replacement` (line 118) | `pytest.raises(ValueError, match="parser replacement")` |
| Fail-closed: `readiness_status="ready"` rejected | `test_candidate_boundary_rejects_readiness` (line 140) | `pytest.raises(ValueError, match="readiness")` |
| Fail-closed: structural failures block | `test_fail_closed_failure_class_blocks_candidate_boundary` (line 162) | parametrized for `schema_drift`, `identity_mismatch`, `integrity_error` |
| No promotion: candidate blocked | `test_candidate_boundary_is_admitted_but_blocked_from_promotion` (line 288) | `admitted=True, contract_status="blocked"` |
| No leak: `candidate_only` not in `EvidenceSourceKind` | `test_no_candidate_only_leaks_to_public_evidence_source_kind` (line 343) | `get_args(EvidenceSourceKind)` check |
| Default registry unsupported | `test_registry_default_does_not_support_fund_disclosure_document_intermediate` (line 245) | `pytest.raises(UnsupportedFundProcessorError, match="fund_disclosure_document.v1")` |
| Import isolation | `test_admission_helper_source_boundary_imports_stay_isolated` (line 386) | AST parse verifies no forbidden prefix imports |

### 6. README Sync: Current Facts Only

**PARTIAL — evidence below.** The `fund_agent/fund/README.md` diff adds one sentence:

> S3 新增的 `FundDisclosureDocumentIntermediate` 协议和 `fund_disclosure_dispatch.py` admission helper 只定义受控文档表示进入 Processor 边界前的 fail-closed 判定；当前默认 registry 不支持 `fund_disclosure_document.v1`，`FundDataExtractor.extract()` 也不消费该中间态。

This sentence:
- States current implementation fact (protocol + helper exist, registry doesn't support it, facade doesn't consume it)
- Explicitly qualifies "只定义" (only defines) and "当前" (current)
- Does not claim source truth, readiness, parser replacement, or production promotion
- Consistent with AGENTS.md §文档同步 rule: "优先写当前怎么用/当前怎么工作"

The full README context could not be re-read in this session (interrupted). The diff sentence itself is factually correct and scope-bounded. Whether surrounding README context remains aligned is noted as residual risk below.

### 7. Format Baseline Residual Preserved

**PASS.** No broad formatting of unrelated files occurred.

| Command | Result |
|---|---|
| `ruff format --check` on 4 changed implementation/test files | `4 files already formatted` |
| `git diff --check` | no whitespace errors |
| `git status` | clean working tree (all `??` are untracked residue, none staged/modified) |

The whole-repo `ruff format --check fund_agent/ tests/` baseline residual (152 files) is correctly preserved as out-of-scope per controller judgment chain.

### 8. No Undeclared Live/Source/PDF/Docling/Provider/LLM/Readiness/Release Extension

**PASS.** Evidence:

- `git diff 293026d..HEAD` touches only contracts, dispatch helper, tests, README, and control/review docs
- `git status --short` shows no modified files — only untracked residue (`??`) from prior gates
- `fund_disclosure_dispatch.py` imports only from `contracts.py` — no `FundDocumentRepository`, no `pdfplumber`, no `Docling`, no network/IO, no provider/LLM
- `admit_disclosure_intermediate()` takes no IO parameters, performs no file/network access, returns a frozen dataclass
- No `FundDataExtractor` integration, no registry registration, no processor implementation, no fallback logic
- No readiness/release/golden/checklist/analyze commands in the slice

---

## Findings

未发现实质性问题。

All 8 specific checks pass. The implementation correctly follows the accepted plan and binding amendment. The slice remains a pure processor-contract/admission-helper boundary with no facade, repository, source, or readiness expansion.

### Accepted Residual Findings (from prior gate chain)

These were identified in prior reviews and dispositioned as accepted/carry-forward by controller judgments:

| ID | Finding | Disposition | Owner |
|---|---|---|---|
| DS-001/MiMo-001 | `dispatch_key` retained but unused in `admit_disclosure_intermediate()` | Accepted as S3 design boundary; identity cross-check deferred to S4 concrete processor gate | S4 gate |
| DS-002 | Invalid `failure_class` raises raw `KeyError` with no explicit negative test | Accepted as fail-closed for S3; optional wrapped exception or explicit test deferred | S4 gate |
| MiMo-002 | Test-count divergence from plan (13 vs 18) | Non-blocking; all required behavioral assertions covered | — |

---

## Open Questions

无。

---

## Residual Risk

- **README full-context alignment**: 本次 session 未完整重读 `fund_agent/fund/README.md` 全文。diff 中的新增句子事实正确、scope 受控，但 README 全文是否残留旧术语或越界表述未在本次 aggregate deepreview 中验证。建议 controller 在下一个 gate 前做一次 README 全文 alignment spot-check。
- **Format baseline residual**: 全仓 `ruff format --check fund_agent/ tests/` 仍有 152 个 scope-out 文件需格式化。已由 controller judgment chain 确认为 out-of-scope，不阻塞本 gate。
- **No concrete processor**: S3 不实现 `FundDisclosureDocumentProcessor`；`FundDataExtractor.extract()` 不接受 `fund_disclosure_document.v1`。
- **Candidate boundary locked**: `field_correctness_status=not_proven`, `source_truth_status=not_proven`, `parser_replacement_authorized=False`, `readiness_status=not_ready`。
- **No source truth / parser replacement / readiness**: 全部 `NOT_READY`。
- **`dispatch_key` identity cross-check**: 延迟到 S4 具体 processor gate。
- **Invalid `failure_class` error handling**: 当前 `KeyError` fail-closed；可选的 wrapped business exception 延迟到 S4。
