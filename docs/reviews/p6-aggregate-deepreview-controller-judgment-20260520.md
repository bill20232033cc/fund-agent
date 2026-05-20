# P6 Aggregate Deepreview Controller Judgment - 2026-05-20

## Verdict

P6 aggregate deepreview passed, with a small accepted maintenance fix gate before PR readiness.

Reviewer artifacts:

- `docs/reviews/p6-aggregate-deepreview-mimo-20260520.md`
- `docs/reviews/p6-aggregate-deepreview-glm-20260520.md`

## Reviewer Conclusions

| Reviewer | Conclusion | Material findings |
|---|---|---|
| MiMo | PASS | 4 low-severity maintenance findings |
| GLM | PASS | No material findings; residual risks documented |

Both reviewers verified the core P6 invariants:

- No Service/UI/Engine behavior change.
- No direct PDF/cache/fund document access.
- No `extra_payload` use.
- No renderer-compliance overclaim in FQ5.
- `quality_gate.py` consumes score JSON only.
- Template contracts, ITEM_RULE, programmatic audit, renderer blocks, and FQ5 are deterministic.

## Finding Reconciliation

### P6-AGG-MIMO-001 - accepted for immediate fix

Finding:

- Evidence appendix heading string `"## 证据与出处"` is independently hardcoded in renderer, audit, and chapter splitter.

Controller judgment:

- Accepted. This is low severity but cheap to fix and reduces future contract drift.

Fix direction:

- Promote a single public `EVIDENCE_APPENDIX_HEADING` constant from `fund_agent/fund/template/chapter_blocks.py`.
- Use that constant in renderer and audit.

### P6-AGG-MIMO-002 - accepted for immediate fix

Finding:

- `run_programmatic_audit` docstring omits C2 even though `_CHECKED_RULES` includes C2.

Controller judgment:

- Accepted. This is docstring drift and should be fixed before PR readiness.

### P6-AGG-MIMO-003 - accepted for immediate fix

Finding:

- `_derive_contract_applicability` uses `locals()` to detect the current chapter in an exception path.

Controller judgment:

- Accepted. The behavior is currently safe, but replacing reflection with explicit state is clearer and lower risk.

### P6-AGG-MIMO-004 - partially accepted for immediate fix

Finding:

- `preferred_lens_unresolved_chapter_ids` currently records only the first failed chapter because the function returns immediately.

Controller judgment:

- Accepted in spirit. The immediate fix should avoid `locals()` and make the code capable of collecting all failed chapter ids while preserving current fail-closed semantics.
- Do not rename the public score field in this fix; the field name is already shipped in P6-S5 tests and artifacts.

### P6-AGG-GLM-RISK-004 - accepted for immediate fix

Risk:

- `contracts.py` and `item_rules.py` each maintain their own `_SUPPORTED_FUND_TYPES` tuple that duplicates `FundType`.

Controller judgment:

- Accepted. P6-S5 already moved `extraction_score.py` away from this duplication; contracts and item rules should do the same before PR readiness.

### P6-AGG-GLM-RISK-009 - accepted for immediate fix

Risk:

- `TemplateLensRule.priority` has no closed-set validation.

Controller judgment:

- Accepted. A typo in priority metadata should fail closed with the rest of the template manifest validation.

## Deferred Residual Risks

| Risk | Decision |
|---|---|
| Chapter 0 duplicate R=A+B-C values in structured marker and legacy bullet | Defer to future template cleanup; no current correctness impact |
| Chapter 2/4 lens coverage relies on default fallback for some fund types | Defer to content/lens expansion slice; validation explicitly allows fallback |
| Chapter 1 has no default lens | Keep as fail-closed design; all current `FundType` values are explicitly covered |
| Forbidden marker substring matching can false-positive if renderer later emits broader raw text | Track for future audit precision work; current rendered output verified clean |
| `facets_any` differs between lens metadata and ITEM_RULE evaluator usage | Track as naming/semantic clarity risk; no current behavior issue |
| `load_template_contract_manifest()` validates each call | Defer; current cost is negligible and fail-closed validation is valuable |
| ITEM_RULE not yet wired into programmatic audit | Defer; P6-S4 explicitly scoped evaluator manifest only |

## Next Gate

`P6 aggregate fix`

Owner: AgentCodex.

After fix, run targeted template/audit/quality tests, full suite, ruff, and diff check, then write `docs/reviews/p6-aggregate-fix-20260520.md`.
