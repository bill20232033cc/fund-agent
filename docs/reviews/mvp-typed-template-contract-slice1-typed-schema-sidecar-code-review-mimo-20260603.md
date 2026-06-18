# MVP typed template contract Slice 1 typed schema sidecar code review — MiMo

## Reviewer

- Role: AgentMiMo independent code reviewer only. Not controller, not implementation worker.
- Gate: `MVP typed template contract Slice 1 typed schema sidecar implementation gate`.
- Classification: `heavy`.

## Sources Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`
- `docs/reviews/mvp-typed-template-contract-implementation-planning-controller-judgment-20260603.md`
- `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-evidence-20260603.md`
- `docs/reviews/mvp-typed-template-contract-slice0-calibration-precondition-controller-judgment-20260603.md`
- `docs/reviews/mvp-typed-template-contract-slice1-typed-schema-sidecar-implementation-evidence-20260603.md`
- `fund_agent/fund/template/typed_contracts.py` (new, full)
- `fund_agent/fund/template/__init__.py` (diff + full)
- `fund_agent/fund/template/contracts.py` (existing, for text mapping verification)
- `tests/fund/template/test_typed_contracts.py` (new, full)
- `fund_agent/fund/README.md` (diff)
- `tests/README.md` (diff)

## Independent Validation

```
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/template/test_contracts.py -v
→ 18 passed in 0.56s

uv run ruff check fund_agent/fund/template tests/fund/template
→ All checks passed!

git diff --check -- fund_agent/fund/template/typed_contracts.py fund_agent/fund/template/__init__.py tests/fund/template/test_typed_contracts.py fund_agent/fund/README.md tests/README.md
→ exit 0, no whitespace issues
```

All results match the controller-provided validation.

## Review Findings

### Finding 1: Exact text mapping verified — PASS

Independently ran the current `contracts.py` manifest for all 8 chapters and compared every `must_answer`, `must_not_cover`, and `required_output_items` string against the `_CURRENT_TEXT_MAPPING` in `typed_contracts.py`. All strings match exactly. The `_assert_exact_text_mapping()` function (line 900-923) enforces tuple equality with no fuzzy/substring/embedding/LLM matching. Text drift will fail closed with a clear `ValueError`.

### Finding 2: Public chapter ids 0-7 preserved — PASS

- `EXPECTED_PUBLIC_CHAPTER_IDS = tuple(range(8))` (line 24).
- `validate_typed_template_contract_manifest()` checks `chapter_ids == EXPECTED_PUBLIC_CHAPTER_IDS` (line 633) and duplicate check (line 635-636).
- `load_typed_template_contract_manifest()` iterates `manifest.chapters` from current `contracts.py` which already produces 8 chapters.
- Test `test_typed_manifest_preserves_public_chapter_ids_0_to_7` asserts the tuple equality.

### Finding 3: Ch2 internal subcontracts not public — PASS

- `_build_internal_subcontracts()` (line 814-861) only returns subcontracts for `chapter_id == 2`.
- `_validate_internal_subcontracts()` (line 1157-1205) rejects non-Ch2 chapters with subcontracts, rejects subcontracts with `public_chapter_id is not None`, and validates the exact subcontract ids `("performance", "attribution", "cost")`.
- Test `test_typed_manifest_rejects_ch2_public_subchapter_ids` covers both the `public_chapter_id` injection and public split injection paths.

### Finding 4: Ch0 consumes Ch7, no independent action — PASS

- `_project_chapter()` sets `consumes_chapter_conclusions=(7,)` when `chapter_id == 0` (line 695) and `independent_action_source=False` for all chapters (line 696).
- `_validate_dependencies()` (line 1108-1134) checks `chapter_id == 0 and 7 not in dependencies` and `chapter_id == 0 and chapter.independent_action_source`.
- Test `test_ch0_consumes_ch7_and_has_no_independent_action_source` covers both positive and negative paths.

### Finding 5: Fail-closed validation coverage — PASS

Validation covers:
- **Schema version**: line 623-624, line 943-944.
- **Duplicate chapter ids**: line 635-636.
- **Unknown dependency ids**: line 1128-1130.
- **Required output item uniqueness**: line 1058-1062.
- **Stable clause/id prefixes**: line 987-988 (`ch{chapter_id}.{field_name}.` prefix), line 1066-1067 (`ch{chapter_id}.required_output.` prefix).
- **Closed audit_focus**: line 1150-1154.
- **Closed evidence statuses**: line 1038-1040.
- **Closed allowed_contexts**: line 1125-1127.
- **Closed missing_evidence_behaviors**: line 1084-1086.
- **Cross-chapter clause id uniqueness**: line 639-645.
- **Ch2 subcontract requirement ids reference real clause/item ids**: line 1179-1205.

### Finding 6: Existing runtime unchanged — PASS

- `typed_contracts.py` imports from `contracts.py` but only reads; does not modify `_CHAPTERS` or any mutable state.
- Test `test_typed_contract_loader_does_not_mutate_current_manifest` explicitly verifies `after_manifest is current_manifest` and content equality before/after typed loader.
- No changes to renderer, auditor, deterministic analyze/checklist, or `--use-llm` behavior.

### Finding 7: No prohibited scope creep — PASS

Verified by diff inspection:
- No provider/runtime/default/budget/endpoint changes.
- No PASS-only live probe code.
- No Agent runtime/tool-loop code.
- No score/golden/readiness changes.
- No direct document/PDF/cache/source-helper access.
- No `extra_payload` or `**kwargs` business params.
- `EvidencePredicate`, `MissingEvidenceBehavior`, and `audit_focus` are data-only schema fields; no enforcement logic.

### Finding 8: Package exports — non-blocking observation

`TemplateLensRule` exists in both `contracts.py` (line 133-147 of `contracts.py`) and `typed_contracts.py` (line 132-147 of `typed_contracts.py`) as separate frozen dataclasses. The `__init__.py` imports `TemplateLensRule` only from `contracts.py` (line 6), so the package-level `fund_agent.fund.template.TemplateLensRule` resolves to the existing `contracts.py` version. The typed version is accessible only via `fund_agent.fund.template.typed_contracts.TemplateLensRule`. This is correct and creates no naming regression at the package level. However, if a future slice imports `TemplateLensRule` from the package expecting the typed version, it would silently get the old one. This is a non-blocking observation for the current slice since no code path does this, and the evidence artifact already notes the typed sidecar is additive.

### Finding 9: Tests sufficient for scope — PASS

8 test functions cover:
1. Public chapter ids 0-7 preservation.
2. Ch2 public subchapter rejection.
3. Ch0/Ch7 dependency and independent action.
4. Required output item id uniqueness.
5. Audit focus closed set and semantic-only assertion.
6. Current manifest non-mutation.
7. Unknown dependency fail-closed.
8. Non-Ch2 internal subcontract rejection.

These match the Slice 1 plan's acceptance criteria. Coverage is focused on the additive schema sidecar boundary as authorized.

### Finding 10: README updates — PASS

- `fund_agent/fund/README.md`: Adds accurate description of `typed_contracts.py` as additive sidecar, correctly states it does not replace template truth, renderer, auditor, or deterministic behavior. No overclaiming.
- `tests/README.md`: Adds `test_typed_contracts.py` entry with accurate test coverage description. No overclaiming.

## Adversarial Failure Analysis

Attempted adversarial scenarios against the implementation:

1. **Inject a chapter with id=8 into typed manifest**: `_validate_typed_chapter_contract` rejects with "不支持的 typed 公开章节 id" at line 945-946.
2. **Remove Ch7 from Ch0 dependencies**: `_validate_dependencies` rejects at line 1131-1132.
3. **Set Ch0 `independent_action_source=True`**: `_validate_dependencies` rejects at line 1133-1134.
4. **Add `public_chapter_id=2` to a Ch2 subcontract**: `_validate_internal_subcontracts` rejects at line 1184-1185.
5. **Add subcontract to Ch3**: `_validate_internal_subcontracts` rejects at line 1172-1173.
6. **Use `"disable_programmatic"` as audit_focus**: `_validate_audit_focus` rejects at line 1153-1154.
7. **Duplicate clause id across chapters**: global check at line 644-645 rejects.
8. **Corrupt a text mapping entry**: `_assert_exact_text_mapping` fails with tuple inequality at line 922-923.

All scenarios fail closed as expected.

## Conclusion

**PASS.**

No blocking findings. The Slice 1 implementation correctly adds the additive typed contract schema sidecar with exact reviewed text mapping, comprehensive fail-closed validation, Ch0/Ch7 dependency, Ch2 internal subcontracts, semantic-only `audit_focus`, and focused tests. Existing runtime is unchanged. One non-blocking observation about `TemplateLensRule` dual-class naming is noted for future slices but does not affect current package-level behavior.

## Secret Safety

This review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
