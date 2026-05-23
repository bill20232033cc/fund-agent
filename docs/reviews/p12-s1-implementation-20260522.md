# P12-S1 Implementation Report（2026-05-22）

- **Gate**: `P12-S1 implementation`
- **Accepted plan commit**: `aad094f`
- **Plan**: `docs/reviews/p12-s1-item-rule-renderer-audit-compliance-plan-20260522.md`
- **Controller judgment**: `docs/reviews/p12-s1-plan-review-controller-judgment-20260522.md`

## Changed Files

- `fund_agent/fund/template/item_rules.py`
- `fund_agent/fund/template/__init__.py`
- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/audit/audit_programmatic.py`
- `tests/fund/template/test_renderer.py`
- `tests/fund/audit/test_audit_programmatic.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p12-s1-implementation-20260522.md`

No Service/UI/CLI, quality gate behavior, annual-report source/cache/repository, final judgment policy, Host/Engine/runtime/tool loop, LLM, Evidence Confirm, RepairContract, `docs/implementation-control.md`, or `docs/repo-audit-20260521.md` changes were made.

## Contract Decisions Implemented

1. Renderer now derives `item_rule_decisions` from `StructuredFundDataBundle.basic_identity.value["classified_fund_type"]` with `facets=()`.
2. Renderer carries `item_rule_audit_context`:
   - missing identity: `item_rule_decisions=()`, `item_rule_audit_context="identity_missing"`;
   - identity present with valid type: evaluated decisions, `item_rule_audit_context="identity_present"`;
   - identity present with missing/invalid `classified_fund_type`: fail-closed `ValueError`.
3. Triggered ITEM_RULE segments render as deterministic fixed headings plus fixed bullets. Non-triggered conditional segments are deleted whole.
4. Evidence boundaries are preserved without fabricating data:
   - benchmark anchors only support the benchmark-reference bullet;
   - index methodology/constituents stay `数据不足`;
   - tracking error stays a deterministic `数据不足` placeholder until data exists;
   - segment evidence is expressed as fixed `证据边界` bullets, while the existing per-chapter `> 📎 证据` contract remains one line per chapter.
5. Programmatic C2 audit consumes renderer-provided decisions/context and checks only the matching `RenderedChapterBlock.body_markdown`.
6. C2 now fails for identity-present empty decisions, duplicate/unknown/mismatched decisions, missing triggered markers, and present deleted markers. Identity-missing empty decisions skip only the ITEM_RULE missing-decision issue.
7. FQ5 / quality gate behavior is unchanged; README clarifies that FQ5 remains applicability metadata, while rendered ITEM_RULE compliance is checked by programmatic C2 audit.

## Tests Added / Updated

- Renderer tests now cover all six standard fund types for ITEM_RULE segment render/delete matrix.
- Renderer tests verify fixed segment bullets and data-insufficient boundaries for enhanced index.
- Renderer missing-identity test now asserts empty decisions and `identity_missing`.
- Audit tests now cover:
  - identity-present missing decisions;
  - identity-missing missing decisions compatibility;
  - missing triggered segment marker;
  - deleted marker still present;
  - duplicate, unknown and chapter-mismatched decisions;
  - matching-chapter-only marker scope.
- Existing audit helpers that rebuild `ProgrammaticAuditInput` now carry renderer-produced ITEM_RULE decisions/context where full C2 compliance is expected.

## Validation

```bash
pytest tests/fund/template/test_item_rules.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py
# 81 passed in 0.55s

pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
# 43 passed in 0.39s

pytest tests/fund/template/test_item_rules.py tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py tests/fund/integration/test_p3_cli_e2e_matrix.py
# 82 passed in 0.81s

ruff check fund_agent/fund/template fund_agent/fund/audit tests/fund/template tests/fund/audit
# All checks passed

git diff --check
# passed

pytest
# 401 passed in 0.93s
```

## Residual Risks

- ITEM_RULE segment prose remains deterministic MVP template output and does not prove semantic completeness.
- Tracking error and index constituents/methodology remain data-insufficient until dedicated extractors or calculation inputs exist.
- FQ5 still does not parse final report Markdown or claim renderer compliance; that responsibility is the renderer/audit path implemented here.
