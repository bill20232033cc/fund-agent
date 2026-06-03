# MVP typed template truth-source replacement Slice 1 code review

## Reviewer self-check

- Role: AgentMiMo code review worker only.
- Gate: `MVP typed template truth-source replacement gate`, Slice 1.
- Classification: `heavy`.
- Scope: `docs/fund-analysis-template-draft.md` and evidence artifact only.
- No source code, tests, control docs, commit, push, PR or runtime action performed.

## Review targets

- `docs/fund-analysis-template-draft.md` (modified)
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md` (new)
- `docs/reviews/mvp-typed-template-truth-source-replacement-plan-20260603.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-plan-controller-judgment-20260603.md`
- `fund_agent/fund/template/contracts.py`
- `fund_agent/fund/template/typed_contracts.py`

## Findings

No blocking findings. No high or medium findings.

### F1 (LOW) — Evidence artifact generation helper body omitted

The evidence artifact shows the generation helper command with an empty `PY` heredoc body (lines 79-83). The actual helper code was not recorded. This is non-blocking because the validation commands independently reproduce the same checks, but it reduces reproducibility of the generation step.

Severity: LOW.
Recommendation: no action required for Slice 1 checkpoint; if controller requires full reproducibility, the helper script body can be added in a follow-up evidence update.

## Validation commands and exact results

### 1. Exactly one TEMPLATE_CONTRACT_MANIFEST_JSON block

```bash
grep -n 'TEMPLATE_CONTRACT_MANIFEST_JSON' docs/fund-analysis-template-draft.md
```

Result:

```text
6:TEMPLATE_CONTRACT_MANIFEST_JSON
1443:END_TEMPLATE_CONTRACT_MANIFEST_JSON
1542:source: TEMPLATE_CONTRACT_MANIFEST_JSON
1574:source: TEMPLATE_CONTRACT_MANIFEST_JSON
1671:source: TEMPLATE_CONTRACT_MANIFEST_JSON
1777:source: TEMPLATE_CONTRACT_MANIFEST_JSON
1841:source: TEMPLATE_CONTRACT_MANIFEST_JSON
1885:source: TEMPLATE_CONTRACT_MANIFEST_JSON
1923:source: TEMPLATE_CONTRACT_MANIFEST_JSON
1994:source: TEMPLATE_CONTRACT_MANIFEST_JSON
```

PASS: Exactly one opening marker (line 6) and one closing marker (line 1443). The 8 additional occurrences are `source: TEMPLATE_CONTRACT_MANIFEST_JSON` inside CHAPTER_CONTRACT_REF blocks, which is expected non-authoritative referencing.

### 2. JSON parses correctly with stdlib json

```bash
uv run python -c "import json, re; text = open('docs/fund-analysis-template-draft.md').read(); m = re.search(r'<!--\s*\nTEMPLATE_CONTRACT_MANIFEST_JSON\n(.*?)\nEND_TEMPLATE_CONTRACT_MANIFEST_JSON\s*\n-->', text, re.DOTALL); data = json.loads(m.group(1)); print(f'chapters={len(data[\"chapters\"])} ids={[c[\"chapter_id\"] for c in data[\"chapters\"]]}')"
```

Result:

```text
chapters=8 ids=[0, 1, 2, 3, 4, 5, 6, 7]
```

PASS.

### 3. public_chapter_ids and chapters 0-7

PASS: `public_chapter_ids: [0, 1, 2, 3, 4, 5, 6, 7]` and exactly 8 chapters with sequential ids.

### 4. Eight CHAPTER_CONTRACT_REF blocks, no old CHAPTER_CONTRACT blocks

```bash
grep -c 'CHAPTER_CONTRACT_REF' docs/fund-analysis-template-draft.md
grep -c 'CHAPTER_CONTRACT$' docs/fund-analysis-template-draft.md
grep -c 'END_CHAPTER_CONTRACT$' docs/fund-analysis-template-draft.md
```

Result:

```text
16 (8 pairs of CHAPTER_CONTRACT_REF / END_CHAPTER_CONTRACT_REF)
0 (no old CHAPTER_CONTRACT without _REF)
0 (no old END_CHAPTER_CONTRACT without _REF)
```

PASS: Each CHAPTER_CONTRACT_REF block contains exactly 2 lines (`chapter_id: N` and `source: TEMPLATE_CONTRACT_MANIFEST_JSON`), verified non-authoritative.

### 5. No structured contract fields outside canonical JSON

PASS: No `must_answer:`, `must_not_cover:`, `required_output_items:`, `preferred_lens:`, `audit_focus:`, or `_CURRENT_TEXT_MAPPING` found outside the canonical JSON block.

### 6. JSON projection equals current untyped manifest

```bash
uv run python - <<'PY'
# Compare JSON text tuples against load_template_contract_manifest()
PY
```

Result:

```text
PASS JSON projection equals current untyped manifest
```

PASS: All must_answer, must_not_cover, required_output_items text tuples and preferred_lens keys match exactly.

### 7. JSON projection equals current typed manifest

```bash
uv run python - <<'PY'
# Compare JSON id tuples against load_typed_template_contract_manifest()
PY
```

Result:

```text
PASS JSON projection equals current typed manifest
```

PASS: All clause ids, item ids, and internal_subcontract ids match exactly.

### 8. Ch2 internal_subcontracts public_chapter_id all null

```text
PASS Ch2 internal_subcontracts public_chapter_id all null: True
```

PASS: All 3 subcontracts (performance, attribution, cost) have `public_chapter_id: null`.

### 9. Ch3 item_04 predicate and allowed_contexts

```text
PASS Ch3 item_04 predicate_id: ch3.evidence.manager_behavior_style_unreviewed
PASS Ch3 item_04 requirement_ids: ['ch3.requirement.actual_behavior_reviewed']
PASS Ch3 item_04 required_statuses: ['missing', 'unavailable', 'unreviewed']
PASS Ch3 item_04 allowed_contexts: ['required_label', 'evidence_gap_statement', 'quote', 'anchor_caption']
```

PASS.

### 10. Required output missing behavior

```text
PASS Ch2 block items: 7/7
PASS Ch3 render_evidence_gap: 4, render_minimum_verification_question: 1
PASS all when_evidence_missing items have missing_evidence_reason
```

PASS.

### 11. Scoped git status

```bash
git status --short -- docs/fund-analysis-template-draft.md docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md
```

Result:

```text
 M docs/fund-analysis-template-draft.md
?? docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md
```

PASS: Only the two allowed files were touched.

### 12. No source/test/control doc edits

```bash
git diff --stat
```

Result:

```text
docs/fund-analysis-template-draft.md | 1876 ++++++++++++++++++++++++++--------
1 file changed, 1473 insertions(+), 403 deletions(-)
```

PASS: No source code, tests, README, design, implementation-control, or startup-packet files were modified.

## Non-goals preserved

- No source code, tests, README, design/control/startup, provider/runtime, Agent/Host, renderer, quality gate, baseline/golden, commit, push, PR or external action changes.
- No deterministic `analyze` / `checklist` behavior change.
- No public Ch2 split; public chapter ids remain exactly `0-7`.
- No provider/runtime/live probe.
- No duplicated structured contract fields outside the canonical JSON block.

## Scope creep check

PASS: No Agent/runtime/provider/multi-year/score-loop/golden/readiness scope creep detected.

## Verdict

**PASS**

No blocking findings. One LOW finding (evidence artifact helper body omitted) does not block the Slice 1 checkpoint.

The implementation correctly:
1. Adds exactly one canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` block with strict JSON.
2. Carries stable `id` plus exact `text` for all must_answer/must_not_cover/required_output items.
3. Includes preferred_lens, audit_focus, dependencies, Ch2 internal subcontracts, Ch3 predicate, and missing behavior/reasons.
4. Replaces all 8 per-chapter structured `CHAPTER_CONTRACT` blocks with non-authoritative `CHAPTER_CONTRACT_REF` blocks.
5. JSON projection matches both current untyped and typed loaders exactly.
6. Evidence artifact is complete with self-check, changed files, validation results, non-goals, and residuals.

No blocking findings require fix before accepted Slice 1 checkpoint.
