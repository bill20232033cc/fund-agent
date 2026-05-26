# Code Review: CHAPTER_CONTRACT Sidecar + Dev-only Report-writing Audit

> Date: 2026-05-26
> Reviewer: independent code reviewer
> Scope: untracked implementation files for Fund-layer executable CHAPTER_CONTRACT sidecar and dev-only report-writing audit
> Verdict: FAIL

## Scope Reviewed

- `fund_agent/fund/template/chapter_contract_constraints.py`
- `fund_agent/fund/report_writing_audit.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/test_report_writing_audit.py`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-evidence-20260526.md`
- related implementation plan and controller judgment artifacts

Gate constraints checked:

- First material slice must cover only `active_fund` / Chapter 3 turnover or style-consistency evidence, insufficient-evidence wording, and unsupported stability claims.
- Implementation must stay in Fund layer and must not alter renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu runtime, document repository, PDF/cache/source helpers, downloaders, or production extractors.

## Findings

### High: Compatible `data_gap` can silently pass without any insufficient-evidence disclosure

Evidence:

- [fund_agent/fund/report_writing_audit.py](/Users/maomao/fund-agent/fund_agent/fund/report_writing_audit.py:328) finds a compatible active Chapter 3 data gap.
- [fund_agent/fund/report_writing_audit.py](/Users/maomao/fund-agent/fund_agent/fund/report_writing_audit.py:356) checks missing required wording only when `stability_claim` is true.
- If the draft omits a positive stability claim but also omits all insufficient-evidence wording, the audit returns no issue.

Reproduction command run locally:

```bash
uv run python - <<'PY'
from fund_agent.fund.report_evidence import REPORT_EVIDENCE_SCHEMA_VERSION, ReportDataGap, ReportEvidenceBundle, ReportPreferredLensProjection, ReportQualityContext
from fund_agent.fund.report_writing_audit import ChapterDraftSurrogate, audit_report_writing_bundle

bundle = ReportEvidenceBundle(
    bundle_id='bundle:test', schema_version=REPORT_EVIDENCE_SCHEMA_VERSION, corpus_id='ad_hoc', fund_code='004393', report_year=2024,
    classified_fund_type='active_fund', type_slot_membership_status='matches_slot', fund_type_slot='active_fund',
    preferred_lens=ReportPreferredLensProjection(fund_type='active_fund', chapters=()), quality_context=ReportQualityContext(),
    review_status='candidate', data_gaps=(ReportDataGap(
        gap_id='gap:test', gap_kind='not_reviewed', chapter_ids=('chapter_3',), failure_category='not_reviewed_in_current_slice',
        reason_code='not_reviewed_in_current_slice', fallback_allowed=False, fallback_used=False,
        required_report_wording='当前证据不足，不能据此判断风格稳定、风格一致或言行一致；下一步最小验证问题：复核换手率。',
        field_path='manager.turnover_rate'),)
)
result = audit_report_writing_bundle(bundle, chapter_drafts=(ChapterDraftSurrogate(chapter_id=3, fund_type_slot='active_fund', markdown='本章仅描述基金经理任职背景。'),))
print(result.summary.issue_count, [issue.failure_category for issue in result.issues])
PY
```

Observed output:

```text
0 []
```

Impact:

This violates the accepted writing-upgrade contract that compatible data gaps must be surfaced through insufficient-evidence wording and a next minimum validation question. A report can omit the required turnover/style evidence, include a compatible data gap in the bundle, and still produce no audit issue as long as it avoids an explicit positive stability phrase. That weakens the core "insufficient evidence 明示" part of this gate.

Recommendation:

When the active Chapter 3 material requirement is satisfied by a compatible `ReportDataGap` rather than a reviewed fact, require the draft to preserve the required insufficiency wording regardless of whether a positive stability claim is present. Keep `unsupported_stability_claim` as an additional issue for positive stability claims, but emit `insufficient_evidence_wording_missing` whenever the gap is not disclosed in the draft.

### High: A fact with a nonexistent anchor id satisfies the evidence requirement

Evidence:

- [fund_agent/fund/report_writing_audit.py](/Users/maomao/fund-agent/fund_agent/fund/report_writing_audit.py:324) accepts `_find_satisfying_fact(...)` as a complete pass.
- [fund_agent/fund/report_writing_audit.py](/Users/maomao/fund-agent/fund_agent/fund/report_writing_audit.py:546) only checks that `fact.source_anchor_ids` is non-empty.
- The audit never verifies those ids exist in `bundle.evidence_anchors`, even though the gate centers evidence anchors and traceability.

Reproduction command run locally:

```bash
uv run python - <<'PY'
from fund_agent.fund.report_evidence import REPORT_EVIDENCE_SCHEMA_VERSION, ReportEvidenceBundle, ReportFact, ReportPreferredLensProjection, ReportQualityContext
from fund_agent.fund.report_writing_audit import ChapterDraftSurrogate, audit_report_writing_bundle

bundle = ReportEvidenceBundle(
    bundle_id='bundle:test', schema_version=REPORT_EVIDENCE_SCHEMA_VERSION, corpus_id='ad_hoc', fund_code='004393', report_year=2024,
    classified_fund_type='active_fund', type_slot_membership_status='matches_slot', fund_type_slot='active_fund',
    preferred_lens=ReportPreferredLensProjection(fund_type='active_fund', chapters=()), quality_context=ReportQualityContext(),
    review_status='candidate', facts=(ReportFact(
        fact_id='fact:manager.turnover_rate', category='manager', field_path='turnover_rate', value={'turnover_rate':'88%'}, unit='percent',
        source_boundary='manual_review', extraction_mode='direct', review_status='reviewed', source_anchor_ids=('anchor:missing',)),),
    evidence_anchors=(),
)
result = audit_report_writing_bundle(bundle, chapter_drafts=(ChapterDraftSurrogate(chapter_id=3, fund_type_slot='active_fund', markdown='年报已复核换手率。'),))
print(result.summary.issue_count, [issue.failure_category for issue in result.issues])
PY
```

Observed output:

```text
0 []
```

Impact:

This allows an untraceable turnover fact to satisfy the CHAPTER_CONTRACT evidence requirement. The result is a false pass for the exact evidence-anchor semantics this sidecar is supposed to make executable. It also means a later dev-only audit consumer could believe Chapter 3 is evidence-backed even when the anchor reference is dangling.

Recommendation:

Pass bundle anchor ids into the requirement check and require every satisfying fact to reference at least one existing `ReportEvidenceAnchor.anchor_id`. If no referenced anchor exists, treat the requirement as missing or emit a dedicated evidence-anchor issue. Add a focused test where `source_anchor_ids` is non-empty but absent from `bundle.evidence_anchors`.

### Medium: `audit_report_writing_records()` can raise on malformed caller-supplied records despite its issue-based contract

Evidence:

- [fund_agent/fund/report_writing_audit.py](/Users/maomao/fund-agent/fund_agent/fund/report_writing_audit.py:214) documents the records helper as consuming caller-supplied JSONL-like records.
- [fund_agent/fund/report_writing_audit.py](/Users/maomao/fund-agent/fund_agent/fund/report_writing_audit.py:225) says unsupported records are expressed as issues with no explicit raise.
- [fund_agent/fund/report_writing_audit.py](/Users/maomao/fund-agent/fund_agent/fund/report_writing_audit.py:450) performs `int(record.get("report_year", 0) or 0)` without guarding `ValueError`.

Reproduction command run locally:

```bash
uv run python -c "from fund_agent.fund.report_writing_audit import audit_report_writing_records; audit_report_writing_records(({'record_type':'bundle','bundle_id':'b','report_year':'bad'},))"
```

Observed output:

```text
ValueError: invalid literal for int() with base 10: 'bad'
```

Impact:

This is dev-only, so it does not affect product defaults, but it weakens the reusable audit-loop contract. A single malformed JSONL-like record can crash the audit instead of producing a deterministic fail-closed issue summary. That is especially risky for maintainer tooling where records are assembled from scratch outputs.

Recommendation:

Add a small coercion helper for `report_year` and any other scalar conversions that can throw. On malformed bundle-like records, return a blocking `ReportWritingAuditIssue` with `failed_closed=True` instead of raising. Add a focused test for malformed `report_year`.

## Boundary Review

No boundary violation found in the reviewed implementation:

- No import or usage of `FundDocumentRepository`, PDF/cache/source helpers, downloaders, production extractors, renderer, Service/CLI default paths, FQ0-FQ6 quality gate, Host/Agent packages, `dayu.host`, or `dayu.engine`.
- New source is limited to `fund_agent/fund/template/chapter_contract_constraints.py` and `fund_agent/fund/report_writing_audit.py`.
- Tests are focused under `tests/fund/...`.

## Tests / Commands Run

```bash
uv run pytest tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Result: `13 passed`.

```bash
uv run pytest tests/fund/template tests/fund/test_report_evidence.py tests/fund/test_report_quality_validation.py
```

Result: `147 passed`.

```bash
uv run ruff check fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Result: `All checks passed!`.

```bash
git diff --no-index --check /dev/null fund_agent/fund/template/chapter_contract_constraints.py
git diff --no-index --check /dev/null fund_agent/fund/report_writing_audit.py
```

Result: no whitespace errors printed. Exit status is `1` because each new file differs from `/dev/null`.

```bash
rg -n "dayu\\.host|dayu\\.engine|FundDocumentRepository|AnnualReportDocumentCache|download|source adapter|quality_gate|quality_gate_policy|FQ0|FQ6|renderer|FundAnalysisService|extra_payload|pdf|cache|extractor" fund_agent/fund/template/chapter_contract_constraints.py fund_agent/fund/report_writing_audit.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_report_writing_audit.py
```

Result: no matches.

Additional targeted reproduction commands for the findings are included under each finding.

Coverage was not run in this review. The worker evidence notes a local coverage collection failure due to an existing numpy import issue.

## Residual Risks

- The claim phrase matcher is intentionally small and Chinese-only; this is acceptable for the first dev-only slice but should remain documented as deterministic surrogate logic, not report-language completeness.
- `must_not_cover` matching is intentionally narrow and only maps a few current-template phrases to deterministic checks; future CHAPTER_CONTRACT expansion will need per-rule matchers or explicit rule ids.
- The sidecar includes deferred Chapter 2 and Chapter 6 config-only requirements. They are not materially enforced in this slice, which matches the accepted plan but should not be interpreted as chapter-wide report quality coverage.
- Per-file coverage for the new modules was not established in this review due to the reported local coverage probe failure.
