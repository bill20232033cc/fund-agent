# Plan Review: Source Provenance Primary Failure Category Propagation Design

> Reviewer: AgentMiMo
> Date: 2026-05-27
> Timestamp: 20260527-062449
> Reviewed target: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-20260527.md`
> Scope: design/plan review only; no code changes, commits, push, PR, or gate entry

---

## Review Posture

Adversarial plan review. Default assumption: the plan has at least one material issue until evidence proves otherwise.

---

## Truth Sources Consulted

| Source | Relevant sections |
|---|---|
| `AGENTS.md` | 年报来源 fallback 策略、FundDocumentRepository 硬约束、模块边界 |
| `docs/design.md` v2.2 | §6.1 文档仓库层、来源失败分类、公共来源 provenance 输出契约 |
| `docs/implementation-control.md` | Startup Packet、Current Gate、Next Entry Point |
| `fund_agent/fund/documents/models.py` | `AnnualReportSourceMetadata` frozen dataclass (lines 17-117) |
| `fund_agent/fund/documents/sources.py` | `_mark_fallback_used()` (line 767), `_FALLBACK_ELIGIBLE_CATEGORIES` (line 43), `fetch_annual_report_pdf()` fallback path (line 658) |
| `fund_agent/fund/source_provenance.py` | `project_public_source_provenance()` (line 105), classification logic (lines 139-170) |
| `fund_agent/fund/data_extractor.py` | production call `project_public_source_provenance(report.metadata.source)` (line 210) |

---

## Assumptions Tested

1. `AnnualReportSourceMetadata` lacks `primary_failure_category` — **confirmed** (models.py:18-53).
2. `_mark_fallback_used()` only sets `fallback_used=True`, does not preserve failure category — **confirmed** (sources.py:767-780).
3. `project_public_source_provenance()` already accepts optional `primary_failure_category` kwarg and handles `unknown_public_metadata_absent` — **confirmed** (source_provenance.py:105-170).
4. Production `data_extractor.py` calls `project_public_source_provenance(report.metadata.source)` without passing category — **confirmed** (data_extractor.py:210).
5. `AnnualReportSourceFailureCategory` taxonomy already exists in `sources.py` — **confirmed** (sources.py:26-32).
6. Fail-closed categories (`schema_drift`, `identity_mismatch`, `integrity_error`) raise `AnnualReportSourceFallbackBlockedError` before fallback success — **confirmed** (sources.py:650-656).
7. Plan preserves existing public contract and snapshot field schema — **confirmed** (plan §Public Contract, §Bundle And Public Outputs).

---

## Findings

No material findings. The plan is well-structured and evidence-based. The following items are minor implementation-clarification notes, not blockers:

### 1-未修复-[低]-`to_dict()` 手动字段列举需要显式添加新字段

- **位置**: Minimal Data Model Extension, Implementation Files → `models.py`
- **问题类型**: 最佳实践偏离 (minor)
- **当前写法**: Plan says "Update docstring, dataclass field, `to_dict()`, `from_dict()`, and normalization helper"
- **反例/失败场景**: `AnnualReportSourceMetadata.to_dict()` manually enumerates all fields (models.py:68-84) rather than using `dataclasses.asdict()`. Implementation agent might add the dataclass field but forget to add it to `to_dict()`.
- **为什么有问题**: Silent data loss — new field persists in-memory but drops on serialization round-trip through cache.
- **直接证据**: models.py:55-84 shows manual dict construction; `asdict()` is not used.
- **影响**: Cache round-trip loses `primary_failure_category`; old cache behavior exactly matches current behavior so no regression, but new field never persists.
- **建议改法和验证点**: Plan should note that `to_dict()` needs explicit `"primary_failure_category": ...` entry. Test `to_dict()` / `from_dict()` round-trip (already listed in plan) catches this.
- **修复风险（低/中/高）**: 低 — trivial one-line addition, caught by existing round-trip test.
- **严重程度（低/中/高/严重）**: 低

### 2-未修复-[低]-分类字段反序列化规范化策略需明确

- **位置**: Minimal Data Model Extension → "Validate/normalize through a shared helper"
- **问题类型**: 契约缺失 (minor)
- **当前写法**: "Validate/normalize through a shared helper so only the five accepted categories survive deserialization."
- **反例/失败场景**: If cached JSON has `primary_failure_category: "typo_value"`, what exactly happens? Plan says "normalize to None" but does not specify which helper or pattern.
- **为什么有问题**: `from_dict()` uses `_normalize_source_name()` (a module-private helper returning `None` for unrecognized values) for `source` field. Category normalization needs equivalent behavior. Implementation agent must know whether to create `_normalize_failure_category()` or reuse existing enum validation.
- **直接证据**: models.py:100-102 shows the `_normalize_source_name()` pattern for source field.
- **影响**: Minor — implementation agent likely follows existing pattern, but explicit guidance reduces ambiguity.
- **建议改法和验证点**: Note that `_normalize_source_name()` pattern should be followed for category; invalid values → `None`.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 3-未修复-[低]-`_mark_fallback_used` 签名变更未显式说明

- **位置**: Minimal Source-Chain Write
- **问题类型**: 不可直接实施 (minor)
- **当前写法**: "Change `_mark_fallback_used(result, primary_failure_category=...)` or equivalent to set both `fallback_used=True` and `primary_failure_category=<first/primary failure category>`."
- **反例/失败场景**: Current `_mark_fallback_used(result)` signature takes only `result`. The plan says "or equivalent" which is slightly ambiguous — should it be a new kwarg on the existing function, or a new function?
- **为什么有问题**: `sources.py:767-780` shows `_mark_fallback_used` uses `replace()` on a frozen dataclass. Adding a kwarg is the natural extension, but plan should commit to one approach.
- **直接证据**: sources.py:767-780 — current function uses `replace(result, metadata=replace(result.metadata, fallback_used=True))`. Adding `primary_failure_category` follows same `replace()` pattern.
- **影响**: Very minor — implementation agent will likely add kwarg, but "or equivalent" introduces ambiguity.
- **建议改法和验证点**: Commit to `_mark_fallback_used(result, *, primary_failure_category: AnnualReportSourceFailureCategory | None = None)` signature.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

---

## Architecture Boundary Check

| Check | Result |
|---|---|
| FundDocumentRepository source strategy preserved | PASS — no source ordering, eligibility, or downloader changes |
| Fail-closed categories preserved | PASS — `schema_drift`/`identity_mismatch`/`integrity_error` still raise before fallback |
| No direct source helper/PDF/cache access | PASS — projection reads from metadata only |
| No renderer/FQ/default CLI changes | PASS — plan explicitly lists these as non-goals |
| No Host/Agent/dayu changes | PASS — plan explicitly lists these as non-goals |
| Same-source data flow (not inferred from downstream) | PASS — category captured at source-chain decision boundary, not from extraction/score/quality |
| `AnnualReportSourceMetadata` as right owner | PASS — only layer where fallback decision and failure category are logically/temporally adjacent |
| Public projection consumes metadata field | PASS — `project_public_source_provenance()` already has the kwarg; production call site just needs metadata to carry the field |

---

## Negative Test Coverage Check

| Risk | Plan assertion | Verdict |
|---|---|---|
| Missing category → falsely eligible | Tests assert `unknown_public_metadata_absent` | PASS |
| Fail-closed recovered by fallback success | Tests assert `fail_closed` even with populated fields | PASS |
| Source chain fail-closed regression | Tests assert `AnnualReportSourceFallbackBlockedError` | PASS |
| Eligible inferred from success | Tests assert extraction/score cannot change unknown → eligible | PASS |
| Eligible inferred from source name | Tests assert source name alone cannot determine eligibility | PASS |
| Old metadata compatibility | Tests assert missing key → `None` | PASS |
| FQ0-FQ6 no change | Tests assert no score/quality output changes | PASS |
| Renderer/default no change | Tests assert no default CLI behavior change | PASS |

---

## Open Questions

None. All review focus areas are addressed by the plan with sufficient evidence.

---

## Residual Risks

| Risk | Severity | Tracking destination |
|---|---|---|
| Cache schema version bump decision left to maintainers — if they choose not to bump, old caches with missing field persist indefinitely | Low | Implementation gate controller judgment |
| Multi-source chains beyond primary + fallback are out of scope — if introduced later, `primary_failure_category` may need schema evolution | Low | Future provenance-chain schema gate |

---

## Conclusion

**Verdict: PASS**

The plan correctly identifies the core design gap (`AnnualReportSourceMetadata` lacks `primary_failure_category`, making public projection unable to distinguish eligible fallback from unknown). The data flow is sound: capture at source-chain decision boundary → persist in metadata → consume by existing projection → expose through existing snapshot fields. No other layer needs to change. Classification rules are deterministic and align with the existing fail-closed contract. Negative test matrix covers all specified risks. Implementation scope is minimal and code-generation-ready. The three minor findings above are implementation clarifications, not design blockers.

---

Artifact path: `docs/reviews/release-maintenance-source-provenance-primary-failure-category-propagation-design-plan-review-mimo-20260527.md`
