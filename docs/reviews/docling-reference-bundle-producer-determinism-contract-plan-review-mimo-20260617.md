# Docling Reference Bundle Producer Determinism Contract Plan Review (MiMo) - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism Contract Planning Gate - plan review`
Role: plan review worker only
Artifact: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`
Review write: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-review-mimo-20260617.md`

## Self-check

- Assigned gate: Docling Reference Bundle Producer Determinism Contract Planning Gate - plan review.
- Scope: review only; no code edits, no commit/push/PR.
- Only allowed file: this review artifact.
- `candidate_only=true`, `source_truth_status=not_proven`, `NOT_READY` preserved.

## Read Order Completed

1. `AGENTS.md`
2. `docs/current-startup-packet.md`
3. `docs/implementation-control.md` (current control sections)
4. `docs/reviews/docling-reference-bundle-comparability-diagnostic-controller-judgment-20260617.md`
5. Target plan: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`

## Review Criteria Assessment

### Criterion 1: Does the plan address the accepted comparability diagnostic root problem?

**PASS.** The plan correctly identifies the root problem as wrapper/reference-bundle construction drift before helper semantics. The "Core Decision" section explicitly states: "The next executable work should be a narrow no-live implementation gate for deterministic reference-bundle producer instrumentation." The plan explicitly rejects closure-count chasing in Non-goals: "No residual-closure re-evidence retry in this gate" and "No attempt to recover `13 / 4` closure count." This aligns with the controller judgment verdict `ACCEPT_COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`.

### Criterion 2: Is the plan handoff-ready and code-generation-ready?

**PARTIAL.** See findings below. The plan provides concrete contracts, sort keys, and slice structure, but has gaps in validation commands, hash algorithm specification, and Slice 4 concreteness.

### Criterion 3: Are affected files/modules, exact allowed changes, non-goals, tests, validation commands, stop conditions, and evidence shape concrete enough?

**PARTIAL.** Affected file is identified (`source_truth_residual_closure.py`). Non-goals and stop conditions are comprehensive. Tests are described semantically but lack exact validation commands. Evidence shape is specified for the future evidence gate.

### Criterion 4: Does it preserve candidate-only, source_truth_status=not_proven, NOT_READY?

**PASS.** The plan explicitly preserves these throughout: "candidate_only=true, source_truth_status=not_proven, and NOT_READY remain binding" in Current Accepted Facts. Every slice validation requires these flags. The boundary is stated in Non-goals, Stop Conditions, and Completion Report Format.

### Criterion 5: Does it avoid prohibited access patterns?

**PASS.** The plan explicitly prohibits: direct PDF/cache/source-helper access, unplanned repository reload, live/network/provider/LLM/analyze/checklist/golden/readiness/release commands. Slice 1 states: "Keep all new helpers file-read free, repository-free, source-helper-free, and candidate-only."

### Criterion 6: Does it keep diagnostics bounded and non-authoritative?

**PASS.** The plan specifies `raw_text_excerpt` as "bounded and non-authoritative" and states it "must not be treated as source truth." Bundle-level fields are declared as "diagnostic metadata only" that "do not prove source truth, field correctness, baseline qualification, readiness, or parser replacement."

### Criterion 7: Does it specify deterministic sorting/fingerprinting strongly enough?

**PARTIAL.** Deterministic sort keys are well-specified for cells and text spans. However, the hash algorithm for `bundle_content_fingerprint` and `normalized_text_hash` is not specified, leaving room for implementation drift. See Finding 3.

### Criterion 8: Does it avoid overbroad scope or future-slice leakage?

**PASS.** The plan explicitly defers: sample expansion, live evidence, full parser benchmark, golden/readiness tests, source truth promotion. The four slices are scoped to a single target file.

## Findings

### MiMo-Fn-未修复-中-验证命令未指定

- Plan位置: "Test Strategy" section and all four slice "Validation" subsections
- 问题类型: 契约缺失
- 计划当前写法: Tests are described semantically (e.g., "Unit tests prove fingerprints are stable under input tuple order variations after deterministic sorting") but no exact validation commands are specified.
- 为什么有问题: A code-generation-ready plan should specify the exact commands the implementation worker runs to verify correctness. The project convention (per implementation-control.md) includes `pytest`, `ruff`, and `git diff --check`. Without explicit commands, the implementation worker must infer the test file path, test markers, and validation suite.
- 直接证据: No `pytest ...`, `ruff check`, or `git diff --check` commands appear in the plan. Existing test file `tests/fund/documents/test_docling_source_truth_residual_closure.py` exists but is not referenced.
- 影响: Implementation worker may run different test subsets, miss boundary tests, or skip linting. Review gate cannot verify that the worker ran the correct validation.
- 建议改法和验证点: Add a "Validation Commands" section or append to each slice:
  ```
  pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -v
  ruff check fund_agent/fund/documents/candidates/source_truth_residual_closure.py
  git diff --check
  ```
  Verification: review artifact confirms these commands were specified.
- 修复风险（低/中/高）: 低
- 严重程度（低/中/高/严重）: 中

### MiMo-Fn-未修复-中-Slice4证据包装契约不确定

- Plan位置: "Slice 4 - Evidence Wrapper Contract Update"
- 问题类型: 不可直接实施
- 计划当前写法: "the no-live evidence wrapper used to generate residual-closure matrices, if it exists as a committed script; otherwise keep this slice as an evidence-artifact generation instruction and do not add a new production CLI."
- 为什么有问题: No committed evidence wrapper script exists in the repository (verified: no matching `.py` or `.sh` under `scripts/`, `tools/`, or `fund_agent/cli/`). The conditional phrasing ("if it exists") makes the slice ambiguous for a code-generation worker. If the script doesn't exist, the slice reduces to documentation-only instructions that cannot be validated by tests.
- 直接证据: `grep -rl "residual_closure\|comparability_matrix\|producer_determinism"` across `scripts/`, `tools/`, `fund_agent/cli/` returned no results. The diagnostic matrix at `reports/docling-reference-bundle-comparability-diagnostic/20260617/` contains JSON but no generation script.
- 影响: Implementation worker cannot implement Slice 4 as code. The slice becomes pure documentation instructions that are not verifiable by automated tests. This creates a gap in the "code-generation-ready" requirement.
- 建议改法和验证点: Rewrite Slice 4 as explicitly documentation-only:
  - Remove the conditional "if it exists" phrasing.
  - State clearly: "No committed evidence wrapper script exists. This slice specifies mandatory evidence-artifact format requirements for the future evidence gate worker. The evidence gate worker must ensure `producer_contract_version`, bundle diagnostics, row diagnostics, and `candidate_only=true` appear in the matrix JSON before reporting closure deltas."
  - Add a validation point: "Future evidence gate review must verify matrix JSON contains required diagnostic fields."
  Verification: Slice 4 is either concrete code (if a wrapper is created) or explicit documentation requirements (if not). No conditional phrasing remains.
- 修复风险（低/中/高）: 低
- 严重程度（低/中/高/严重）: 中

### MiMo-Fn-未修复-低-指纹哈希算法未指定

- Plan位置: "Required Algorithmic Constraints" - `bundle_content_fingerprint` and "Cell-level diagnostic contract" - `normalized_text_hash`
- 问题类型: 契约缺失
- 计划当前写法: "`bundle_content_fingerprint` must be computed from normalized diagnostic payload only, not from Python object identity or dict insertion order." No hash algorithm is named.
- 为什么有问题: Two implementation workers could choose different hash algorithms (SHA256 vs blake2b vs hashlib.md5) or different normalization strategies (JSON serialization vs repr), producing incompatible fingerprints. The plan's determinism goal requires algorithm-level specification.
- 直接证据: The word "hash" appears in the plan but no hash algorithm name (SHA256, blake2b, etc.) or normalization function (e.g., `json.dumps(sort_keys=True)`) is specified.
- 影响: Low — within a single implementation pass this won't cause issues, but cross-run or cross-worker fingerprint comparison could fail silently if the algorithm isn't pinned.
- 建议改法和验证点: Specify the hash algorithm explicitly:
  - `bundle_content_fingerprint`: `hashlib.sha256(json.dumps(diagnostic_payload, sort_keys=True, ensure_ascii=False).encode()).hexdigest()`
  - `normalized_text_hash`: `hashlib.sha256(normalized_text.encode()).hexdigest()` where normalization is defined (strip, collapse whitespace, etc.)
  Verification: implementation uses the specified algorithm; test asserts fingerprint length matches algorithm output (64 chars for SHA256 hex).
- 修复风险（低/中/高）: 低
- 严重程度（低/中/高/严重）: 低

### MiMo-Fn-未修复-低-raw_text_excerpt边界值未量化

- Plan位置: "Cell-level diagnostic contract" and "Text-span diagnostic contract"
- 问题类型: 契约缺失
- 计划当前写法: "`raw_text_excerpt` must be bounded and non-authoritative."
- 为什么有问题: The bound is not quantified. An implementation worker could choose 100 chars, 500 chars, or 1000 chars. Without a specified limit, the "bounded" constraint is subjective.
- 直接证据: The plan uses the word "bounded" but no character count or line count appears.
- 影响: Low — different bounds won't break determinism if the bound is consistent within a run, but cross-evidence comparison could differ.
- 建议改法和验证点: Specify the bound, e.g., "`raw_text_excerpt` is bounded to 200 Unicode characters (code points), truncated with `...` suffix if longer." Test asserts: excerpt length ≤ 203 (200 + 3 for `...`).
- 修复风险（低/中/高）: 低
- 严重程度（低/中/高/严重）: 低

## Non-blocking Observations

1. The plan correctly references `RepositoryReferenceBundle.to_dict()` which exists at line 420 of the target file with the expected fields. The target file and class structure are verified.
2. The plan's sort key specification is strong: `(sample_id, fund_code, document_year, page_number, table_id, row_index, column_index, normalized_text_hash)` for cells and `(sample_id, fund_code, document_year, page_number, section_id, context_label, normalized_text_hash)` for text spans are concrete and implementable.
3. The regression guard tests for `S6-F041`, `S6-F049`, `S6-F050` are well-scoped to specific diagnostic behaviors.
4. The future evidence gate verdict tokens (`PRODUCER_DETERMINISM_EVIDENCE_ACCEPTED_NOT_READY`, etc.) are well-defined and align with the project's verdict token convention.

## Verdict

`PASS_WITH_FINDINGS_NOT_READY`

Blocking finding count: 0
Non-blocking finding count: 4 (2 medium, 2 low)

The plan addresses the correct root problem (wrapper/reference-bundle construction drift), preserves all required boundaries, and is substantially code-generation-ready. The two medium findings (missing validation commands and Slice 4 conditional phrasing) should be addressed before implementation handoff to reduce ambiguity, but they do not block the plan's acceptance as a planning artifact. The two low findings (hash algorithm and excerpt bound) are implementation details that can be resolved during implementation review.

## Self-check: pass
