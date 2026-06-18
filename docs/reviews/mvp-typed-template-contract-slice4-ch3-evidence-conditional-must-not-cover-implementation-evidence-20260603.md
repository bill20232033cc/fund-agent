# MVP typed template contract Slice 4 Ch3 evidence-conditional must_not_cover implementation evidence

## Worker Self-Check

- Role: AgentCodex implementation worker only; did not start full Gateflow workflow.
- Gate: `MVP typed template contract Slice 4 Ch3-first evidence-conditional must_not_cover implementation gate`.
- Classification: `heavy`.
- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Scope: Fund-layer typed programmatic audit for Ch3 evidence-conditional `must_not_cover`, focused tests, README sync and this evidence artifact only.
- Non-goals preserved: no provider/runtime/default/budget/endpoint change, no live provider probe, no Service/Host/CLI change, no Agent runtime/tool-loop implementation, no score/golden/readiness/promotion change, no deterministic analyze/checklist behavior change, no direct document/PDF/cache/source-helper access, no `extra_payload` business params, no commit/push/PR.

## Touched Files

- `fund_agent/fund/chapter_auditor.py`
- `fund_agent/fund/audit/contract_rules.py`
- `fund_agent/fund/template/typed_contracts.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/fund/audit/test_audit_programmatic.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-typed-template-contract-slice4-ch3-evidence-conditional-must-not-cover-implementation-evidence-20260603.md`

## Behavior Summary

- Added typed programmatic enforcement for `ch3.must_not_cover.item_04`.
- The Ch3 style clause now runs only when `EvidenceAvailability` makes its `applies_when` predicate active. The predicate now references the already-derived aggregate `ch3.requirement.actual_behavior_reviewed`, so missing, unavailable or unreviewed actual behavior/style evidence activates the clause fail-closed.
- The old global phrase extraction path now skips the typed Ch3 style clause text, avoiding duplicate enforcement and the previous false positive path for required labels or evidence-gap wording. Other unmapped/plain `must_not_cover` clauses keep the existing phrase extraction behavior.
- Added deterministic allowed-context matching for Slice 0 contexts:
  - required labels such as `言行一致性判断：` and `风格稳定性判断：` pass only when the post-colon text is a gap or non-assertive suffix;
  - explicit evidence-gap statements pass only when they deny inference and do not reverse into a positive/quasi-positive conclusion;
  - quote context is narrow and requires quote introducers, and cannot launder author conclusions;
  - anchor captions and required-output comment markers are treated as metadata, not author conclusions.
- Positive claims such as `言行一致` / `风格稳定` / `风格一致` and quasi-positive claims such as `基本一致` / `未见明显不一致` / `倾向一致` / `变化不大` block under active missing/unreviewed evidence.
- Follow-up fail-closed fix: when a mapped typed evidence-conditional clause is audited but `ChapterWriterInput.evidence_availability` is absent, the Ch3 typed scanner still blocks unsafe positive/quasi-positive claims with the stable clause id. Allowed label/gap exceptions are not enabled without explicit availability.
- Typed C2 issue id is stable and clause-bound: `programmatic:C2:ch3.must_not_cover.item_04`.
- `audit_focus` remains semantic-only and cannot disable programmatic C2/L1/marker/anchor/item-rule/forbidden-advice/missing checks.
- `contract_rules.py` now classifies the Ch3 style clause as `typed_programmatic_evidence_conditional` instead of narrative-only.

## Tests Added Or Updated

- `tests/fund/test_chapter_auditor.py::test_ch3_required_label_allowed_under_missing_evidence`
- `tests/fund/test_chapter_auditor.py::test_ch3_explicit_evidence_gap_statement_allowed`
- `tests/fund/test_chapter_auditor.py::test_ch3_positive_consistency_claim_blocks_when_actual_behavior_unreviewed`
- `tests/fund/test_chapter_auditor.py::test_ch3_positive_consistency_claim_blocks_without_evidence_availability`
- `tests/fund/test_chapter_auditor.py::test_ch3_quasi_positive_consistency_claim_blocks_when_style_evidence_missing`
- `tests/fund/test_chapter_auditor.py::test_audit_focus_cannot_disable_programmatic_must_not_cover`
- `tests/fund/audit/test_audit_programmatic.py::test_typed_must_not_cover_issue_id_uses_clause_id`
- Updated coverage manifest assertion so Ch3 style clause is no longer narrative-only.

## Validation

```bash
uv run pytest tests/fund/test_chapter_auditor.py tests/fund/audit/test_audit_programmatic.py
```

Result: `86 passed in 0.74s`.

```bash
uv run ruff check fund_agent/fund tests/fund
```

Result: `All checks passed!`.

```bash
git diff --check -- fund_agent/fund/README.md fund_agent/fund/audit/contract_rules.py fund_agent/fund/chapter_auditor.py fund_agent/fund/template/typed_contracts.py tests/README.md tests/fund/audit/test_audit_programmatic.py tests/fund/test_chapter_auditor.py
```

Result: exit `0`.

Additional typed sidecar regression check because `typed_contracts.py` predicate mapping changed:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py
```

Result: `16 passed in 0.60s`.

Secret / prompt leak scan over touched implementation, test and README files:

```bash
rg -n "sk-[A-Za-z0-9]|api[_-]?key|Authorization|Bearer|raw provider|raw_provider|provider response|provider request|prompt body|system_prompt|user_prompt|draft body|raw PDF|raw_pdf|FUND_AGENT_LLM_|OPENAI|base_url|model_name" fund_agent/fund/README.md fund_agent/fund/audit/contract_rules.py fund_agent/fund/chapter_auditor.py fund_agent/fund/template/typed_contracts.py tests/README.md tests/fund/audit/test_audit_programmatic.py tests/fund/test_chapter_auditor.py
```

Result: hits are existing field names, fake model names, README safety descriptions, the scan command recorded in this artifact and existing `chapter_auditor.py` LLM request field names only. No API key, Authorization header, raw provider request/response, prompt body, draft body or raw PDF text was found.

## Docs Decision

- Updated `fund_agent/fund/README.md` because Fund-layer auditor behavior now documents the current Ch3 typed evidence-conditional `must_not_cover` path.
- Updated `tests/README.md` because the test scope now includes Ch3 typed must-not-cover allowed contexts, blockers and clause-id identity.

## Residual Risks

- Quote and anchor-caption matching is deterministic and intentionally narrow. It covers Slice 0 categories for Ch3 first, not a general semantic quote engine for every future clause.
- Missing `ChapterWriterInput.evidence_availability` now blocks unsafe Ch3 positive/quasi-positive claims fail-closed, but it intentionally does not allow required-label or evidence-gap exceptions. Future Agent typed audit wiring should make availability explicit so safe degradation can be accepted rather than treated as an unavailable predicate state.
- Current Ch3 availability remains single-year and treats cross-period style evidence as `unreviewed`; multi-year evidence remains future design-only scope.

## Completion Status

Implementation worker scope complete. No blockers. No files staged, committed, pushed or PR-created.
