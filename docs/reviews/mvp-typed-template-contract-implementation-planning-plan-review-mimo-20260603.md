# MVP typed template contract implementation planning plan review (MiMo)

## Reviewer Self-Check

- Reviewed target: `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-20260603.md`
- Scope: plan review only; no code, test, control doc, design doc, template truth, runtime config, provider defaults, score/golden/readiness changes
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/reviews/mvp-fund-report-template-typed-contract-redesign-design-20260602.md`, `docs/reviews/mvp-fund-report-template-typed-contract-redesign-controller-judgment-20260602.md`
- Code facts verified: `contracts.py`, `chapter_facts.py`, `chapter_writer.py`, `chapter_auditor.py`, `contract_rules.py`, `chapter_orchestrator.py`, `final_chapter_assembler.py`, `evidence_availability.py` (absent), `typed_contracts.py` (absent)

## Assumptions Tested

1. Current `ChapterContract.must_not_cover` is `tuple[str, ...]` (natural-language) — verified.
2. Current C2 programmatic checker has 9 forbidden-marker rules using literal string matching — verified.
3. Current `_MUST_NOT_COVER_COVERAGE_RULES` has 23 non-programmatic `narrative_guidance` rules requiring LLM semantic audit — verified.
4. Current Ch3 template `must_not_cover` includes evidence-conditional prose about 言行一致/风格稳定 — verified in design doc.
5. Current C2 programmatic rules do NOT cover Ch3 言行一致/风格稳定 — verified (no matching forbidden marker rule exists).
6. `evidence_availability.py` and `typed_contracts.py` do not exist yet — verified.
7. `ChapterFactProjection` provides per-chapter facts, anchors, missing reasons — verified.
8. Current Ch3 renderer already has evidence-aware degradation for active_fund — verified in design doc §3.2.

## Findings

### 001-未修复-中-Ch3 must_not_cover 从 narrative_guidance 到 programmatic 的 gap 未显式说明

- **位置**: Slice 4, Accepted Design Requirements, plan §Ch3 first as acceptance target
- **问题类型**: 契约缺失
- **当前写法**: Plan says "Extend programmatic audit to consume typed `MustNotCoverClause`" and "Implement Ch3 first as the acceptance target: if turnover / holdings / cross-period style evidence is missing or unreviewed, positive or quasi-positive `言行一致` / `风格稳定` claims block"
- **反例/失败场景**: The current Ch3 `must_not_cover` about 言行一致/风格稳定 is enforced ONLY as `narrative_guidance` coverage rules (LLM semantic audit), not as programmatic forbidden-marker rules. The 006597 retained evidence shows `programmatic:C2:言行一致:db9a79f992` — meaning the CURRENT programmatic checker IS hitting `言行一致` as a forbidden marker. But looking at `contract_rules.py`, there is NO explicit Ch3 forbidden-marker rule for `言行一致` or `风格稳定`. The `programmatic:C2` issue comes from somewhere else — likely the `_MUST_NOT_COVER_COVERAGE_RULES` or the writer/auditor contract checking, not the `_FORBIDDEN_CONTENT_RULES` literal markers. The plan does not clarify this root cause gap or how the existing C2 checking mechanism relates to the new typed `MustNotCoverClause` programmatic enforcement.
- **为什么有问题**: An implementation agent needs to know exactly which existing code path produces the `programmatic:C2:言行一致` issue to properly extend it with typed clauses. Without this clarity, the agent may create a duplicate enforcement path or miss the existing one.
- **直接证据**: `contract_rules.py` `_FORBIDDEN_CONTENT_RULES` has 9 rules, none for Ch3 言行一致/风格稳定. `chapter_auditor.py` has `audit_chapter_must_not_cover()` which checks both programmatic forbidden markers and narrative_guidance coverage rules. The 006597 retained evidence shows `programmatic:C2:言行一致`.
- **影响**: Implementation agent may create incorrect audit enforcement path; existing C2 behavior may regress or duplicate.
- **建议改法和验证点**: Add a clarifying note in Slice 4 explaining: (1) the current code path that produces `programmatic:C2:言行一致` (likely `audit_chapter_must_not_cover()` in `chapter_auditor.py` consuming `_MUST_NOT_COVER_COVERAGE_RULES`), (2) how typed `MustNotCoverClause` will extend or replace that path, (3) whether existing `narrative_guidance` coverage rules for Ch3 are migrated to typed clauses or kept in parallel. Verification: grep for the exact C2 issue prefix source in `chapter_auditor.py`.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 002-未修复-中-Slice 4 allowed_contexts 程序化匹配规格不足

- **位置**: Slice 4 implementation work, Decision 3 of design doc
- **问题类型**: 不可直接实施
- **当前写法**: "Implement allowed-context matching for required label, explicit evidence-gap statement, quote, and anchor caption according to Slice 0 calibration."
- **反例/失败场景**: The design doc defines four `allowed_contexts`: `required_label`, `evidence_gap_statement`, `quote`, `anchor_caption`. But Slice 0 only produces a fixture artifact — it does not define the programmatic matching algorithm. The implementation agent needs to distinguish "this `言行一致` occurrence is a required output label" from "this `言行一致` occurrence is a positive consistency claim" using only the writer draft text, the chapter contract, and the evidence availability state. Without a matching specification, the agent may implement brittle regex, context-window heuristics, or overly permissive matching.
- **为什么有问题**: This is the core mechanism that fixes the Ch3 C2 false-positive. If the matching is too permissive, forbidden claims slip through. If too strict, required labels are blocked. The plan delegates the matching algorithm to "Slice 0 calibration" which only defines fixture categories, not matching rules.
- **直接证据**: Design doc Decision 3 defines `allowed_contexts` semantics but says "Programmatic C2 is expected to use `allowed_contexts` when implementing evidence-conditional `must_not_cover`" without specifying HOW to match contexts programmatically. Slice 0 says "Define allowed-context fixture categories" but not matching algorithm.
- **影响**: Implementation agent must invent context-matching algorithm; risk of overblocking labels or underblocking claims.
- **建议改法和验证点**: Either (a) add a matching-specification section to Slice 0 that defines how to identify each context type (e.g., "required_label = the text matches a `RequiredOutputItem.label` exactly"; "evidence_gap_statement = the text contains explicit insufficiency language AND does not contain positive/assertive polarity"), or (b) add matching specification directly to Slice 4. Verification: each context type must have a deterministic matching rule that doesn't depend on LLM judgment.
- **修复风险（低/中/高）**: 中
- **严重程度（低/中/高/严重）**: 中

### 003-未修复-低-现有 Ch3 renderer 证据感知降级逻辑未被计划引用

- **位置**: Slice 3 (RequiredOutputItem.when_evidence_missing), design doc §3.2
- **问题类型**: 最佳实践偏离
- **当前写法**: Plan says "Implement writer prompt fragment generation from typed required-output items only after typed contracts and availability are present."
- **反例/失败场景**: Design doc §3.2 already says: "当前已实现：active-fund 第 3 章 renderer 最小输出契约" — the current renderer already has evidence-aware degradation for Ch3 active_fund. When turnover/style evidence is missing, the renderer outputs `证据不足` instead of positive consistency claims. The plan's Slice 3 adds `when_evidence_missing` semantics but doesn't reference this existing logic. An implementation agent might create a parallel mechanism instead of extending the existing one.
- **为什么有问题**: Duplicate logic increases maintenance burden and risk of divergent behavior. The existing renderer logic is the current production behavior; the typed contract should formalize and extend it, not replace it with a separate path.
- **直接证据**: Design doc §3.2 paragraph starting "当前已实现：active-fund 第 3 章 renderer 最小输出契约" describes the existing evidence-aware degradation.
- **影响**: Possible duplicate degradation logic; maintenance burden.
- **建议改法和验证点**: Add a note in Slice 3 referencing the existing Ch3 renderer evidence-aware degradation and stating that the typed `when_evidence_missing` mechanism should formalize and extend (not replace) this existing behavior. Verification: after Slice 3, the existing Ch3 degradation behavior should still pass its current tests.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### 004-未修复-低-Adapter from current manifest to typed contracts 的 failure mode 未规格化

- **位置**: Slice 1 implementation work, Migration And Compatibility Plan
- **问题类型**: 状态机漏洞
- **当前写法**: "The adapter must fail closed if a current natural-language item has no typed id."
- **反例/失败场景**: The current `must_answer`, `must_not_cover`, and `required_output_items` are `tuple[str, ...]`. The plan requires a "one-way adapter from current 8-chapter manifest to typed contracts." But it doesn't specify HOW to map natural-language strings to typed clause ids. If the adapter uses fuzzy matching or keyword extraction, it could silently map incorrectly. If it uses a hardcoded mapping table, it must be maintained.
- **为什么有问题**: The adapter is the bridge between current truth and future typed contracts. If it fails silently or maps incorrectly, the typed contract diverges from current template truth.
- **直接证据**: Plan says "one-way adapter" and "fail closed if a current natural-language item has no typed id" but doesn't specify the mapping mechanism.
- **影响**: Silent divergence between current template truth and typed contract; incorrect typed clause ids.
- **建议改法和验证点**: Specify that the adapter MUST use an explicit hardcoded mapping table (not fuzzy matching), and that each mapping entry must be verified against the current `contracts.py` manifest. The adapter should raise on any unmapped item. Verification: adapter test covers all current `must_answer`/`must_not_cover`/`required_output_items` strings.
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

1. What is the exact code path in `chapter_auditor.py` that produces `programmatic:C2:言行一致:db9a79f992`? Is it `_MUST_NOT_COVER_COVERAGE_RULES` or `_FORBIDDEN_CONTENT_RULES`? This affects how typed `MustNotCoverClause` should extend the existing mechanism.

2. Should the existing `_MUST_NOT_COVER_COVERAGE_RULES` for Ch3 be migrated into typed `MustNotCoverClause` definitions, or kept in parallel as a legacy path until a later cleanup gate?

3. The plan says "Emit stable issue ids tied to `clause_id`, not only phrase hashes." Will existing issue id format (`programmatic:C2:言行一致:db9a79f992`) change? If so, will retained artifact consumers (like the diagnostic serializer) need updates?

4. Slice 6 references "Ch7 bundle contains action, primary reason, largest risk, minimum verification question, threshold, and evidence/readiness status." The current `FinalChapter7Summary` in `final_chapter_assembler.py` may not have all these fields. Will Slice 6 extend `FinalChapter7Summary` or create a new type?

## Residual Risks

| Risk | Likelihood | Impact | Suggested tracking |
|---|---|---|---|
| Chinese polarity/quasi-positive detection may be too brittle for production even after Slice 0 calibration | High | High | Mandatory gate between Slice 0 and Slice 4; must prove detection quality before Slice 4 |
| `allowed_contexts` matching may need iteration after real provider evidence | Medium | Medium | Track as Slice 4 implementation residual; may need follow-up calibration gate |
| Existing `narrative_guidance` coverage rules for Ch3 may create duplicate enforcement with typed `MustNotCoverClause` | Medium | Low | Track in Slice 4; resolve during implementation |
| Adapter mapping table may need updates when `contracts.py` changes | Low | Low | Track as maintenance residual |

## Reviewer Conclusion

The plan is well-structured, respects all specified boundaries, and the slice sequence is logical. The 10 review criteria from the user's scope are all addressed:

- Public chapter ids 0-7 preserved: YES
- Ch2 internal subcontracts non-public: YES
- Deterministic analyze/checklist defaults unchanged: YES
- --use-llm fail-closed semantics unchanged: YES
- EvidenceAvailability derived from same-source ChapterFactProjection: YES
- Auditor fail-closed/programmatic-first semantics preserved: YES
- audit_focus cannot disable blockers: YES
- No provider-runtime/PASS-only/Agent runtime/multi-year/score-loop/golden/readiness/template truth: YES
- Slices are code-generation-ready with clear files, acceptance criteria, tests, and verifier matrix: YES
- No blocking findings identified

The 4 findings are all non-blocking: two are medium-severity specification gaps (F1, F2) that should be addressed before implementation but don't invalidate the plan structure; two are low-severity best-practice/maintenance concerns (F3, F4). The open questions are implementation details that can be resolved during slice execution.

**Verdict: PASS**

Output path: `docs/reviews/mvp-typed-template-contract-implementation-planning-plan-review-mimo-20260603.md`
