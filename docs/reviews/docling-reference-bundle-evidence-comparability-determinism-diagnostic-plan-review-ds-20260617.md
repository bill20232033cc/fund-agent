# Docling Reference Bundle Evidence Comparability and Producer Determinism Diagnostic Plan Review (AgentDS) — 2026-06-17

Gate: `Docling Reference Bundle Evidence Comparability and Producer Determinism Diagnostic Planning Gate`
Role: AgentDS plan review worker only
Verdict: `PASS`
Blocking findings: 0
Non-blocking findings: 3

## Reviewed Artifact

- `docs/reviews/docling-reference-bundle-evidence-comparability-determinism-diagnostic-plan-20260617.md`

## Context Cross-checked

- `AGENTS.md`
- `docs/reviews/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-no-live-reevidence-controller-judgment-20260617.md`
- `reports/docling-reference-bundle-producer-row-hierarchy-benchmark-semantic-label-reevidence/20260617/residual_closure_matrix.json` (current)
- `reports/docling-reference-bundle-enrichment-residual-closure/20260617/residual_closure_matrix.json` (prior)

## Plan Facts Verification (jq)

| Plan Claim | jq Verified |
|---|---|
| Prior: 13 closed / 4 residual | ✅ prior matrix: 13 DSBM + 4 SAR = 17 |
| Current: 10 closed / 7 residual | ✅ current matrix: 10 DSBM + 5 SAR + 2 SBM = 17 |
| Delta: -3 closed | ✅ 13 → 10 |
| Regression: F015, S5-F023, S6-F035 | ✅ jq confirms all 3 went from DSBM → non-DSBM |
| Target seven prior: 3/7 closed | ✅ F015/F020/S4-F015 in prior closed set |
| Target seven current: 2/7 closed | ✅ F020/S4-F015 in current closed set |
| S1 prior: cells=3201, text_spans=8 | ✅ |
| S1 current: cells=3247, text_spans=6 | ✅ |
| S4 prior: cells=2529, text_spans=8 | ✅ |
| S4 current: cells=2561, text_spans=6 | ✅ |
| S5 prior: cells=6739, text_spans=6 | ✅ |
| S5 current: cells=6805, text_spans=6 | ✅ |
| S6 prior: cells=5665, text_spans=8 | ✅ |
| S6 current: cells=5633, text_spans=6 | ✅ |
| S1 §7 section: prior=5 → current=8 | ✅ |
| S1 §8 section: prior=21 → current=12 | ✅ |
| S6 §2 section: prior=9 → current=14 | ✅ |
| All section inference counts differ per sample | ✅ all 4 samples show drift |

All 16 plan factual claims verified against matrix JSON. No factual errors found.

## Regression Row Matched Context Comparison (jq)

| Row | Prior matched_row_label_path | Prior matched_table_context | Current source_layer | Interpretation |
|---|---|---|---|---|
| F015 | `["当期发生的基金应支付的销售服务费", "安信基金"]` | §7, fee-accounting label, C类 context | `same_source_reference_loaded` (SAR) | Text found but enriched predicate rejected; §7 count 5→8 suggests fee table reclassification |
| S5-F023 | `["投资目标"]` | §2, profile label, full text inline | `same_source_text_absent` (SBM) | Text span missing entirely; S5 text_spans = 6 in BOTH runs but span CONTENT changed |
| S6-F035 | `["基金名称"]` | §2, profile label, fund name inline | `same_source_reference_loaded` (SAR) | Text found but context rejected; S6 text_spans 8→6, §2 count 9→14 |

This confirms the plan's diagnostic strategy is well-targeted: the three regression rows have distinct drift patterns that the comparability matrix can surface.

---

## Findings

### F-DS-P1 (Low) — Regression row matched-context comparison has inherent JSON-only limitation

**Plan reference**: Implementation steps 8–9 (line 191–196), diagnostic findings `json_artifacts_insufficient_for_root_cause` (line 145)

**Issue**: The plan correctly acknowledges that JSON artifacts may be insufficient. But it doesn't explicitly connect this to the regression row analysis: for all three regression rows, the **current** matrix has empty `matched_row_label_path`, `matched_column_header_path`, and `matched_table_context` (all `[]`). The diagnostic can compare "prior had this matched context → current has nothing" but cannot show "what raw bundle cell/text_span existed in the current run and why it didn't match."

For F015 (SAR: text found but no match passed), the diagnostic can see the current `source_layer_status=same_source_reference_loaded` — the text exists but no match satisfied the rule. But the bundle's raw cells for that value aren't in the matrix. For S5-F023 (SBM: text absent), the diagnostic can see the text is missing but can't see which text spans DO exist in the current S5 bundle (to check whether the span was dropped or re-labeled).

**Impact**: The diagnostic will correctly classify this as wrapper drift based on count/context differences, but may reach `json_artifacts_insufficient_for_root_cause` for the specific "which producer line changed" question. This is handled gracefully by the plan's stop condition — the evidence worker stops before repository reload.

**Suggested mitigation**: In step 9 (line 196), add an explicit note that regression rows whose current matched paths are empty will have "prior context vs empty current" comparison only, and that this limitation is expected and acceptable for the diagnostic gate.

**Severity**: Low — the plan's existing `json_artifacts_insufficient_for_root_cause` mechanism handles this correctly. The finding is about documentation clarity.

### F-DS-P2 (Low) — S5 text_span_count stayed at 6 while span CONTENT changed

**Plan reference**: Diagnostic question 4 (line 64–67), data line 52

**Issue**: The plan correctly notes S5 text_span_count = 6 in both runs. But S5-F023 regressed from closed→source_body_mismatch, meaning the investment_objective text span existed in prior S5's 6 spans but is absent from current S5's 6 spans. The plan's line 66 says "determine whether current same_source_text_absent is explainable by wrapper text span slicing, label selection, normalization, or section assignment" — which covers this. But the implementation step for comparing text_span_count (step 7) only computes count deltas, not content composition deltas.

**Impact**: The diagnostic will flag S5 as having `text_span_count_delta=0` (no count drift) but the actual drift is in span content composition. The `section_inference_drift` and `matched_context_drift` flags would still fire, so the diagnostic catches it — just not via the text_span_count comparison alone.

**Suggested mitigation**: In step 7 (line 190), add a note: when text_span_count is equal but text-backed rows regressed, flag `text_span_content_drift_suspected` separately from `text_span_count_drift`. Or simply rely on `matched_context_drift` to capture this case.

**Severity**: Low — the plan's other diagnostic dimensions (matched_context_drift, section_inference_drift) will catch this indirectly. The step 7 count comparison alone is insufficient but not the only signal.

### F-DS-P3 (Info) — Plan claims F015 prior matched row as `当期发生的基金应支付的销售服务费 > 安信基金` with `>` separator

**Plan reference**: Line 61

**Issue**: The plan represents F015's prior `matched_row_label_path` as `"当期发生的基金应支付的销售服务费 > 安信基金"`. The actual matrix field is `["当期发生的基金应支付的销售服务费", "安信基金"]` — a JSON array, not a `>`-delimited string. The `>` notation is the plan author's presentation convention.

**Impact**: If the evidence worker reads the plan literally and searches for `">"` in the JSON, they'll find nothing. But the evidence worker should be comparing JSON arrays directly (step 8 says "compare matched row/header/table context arrays exactly"), so this is a documentation-only issue.

**Severity**: Info — presentation convention only. The implementation steps correctly specify exact array comparison.

---

## Plan Assessment

### Strengths

1. **First-principles motivation** (lines 13–14): Clearly articulates why comparability must be established before further re-evidence. This is the correct next step after a regression finding.

2. **Code-generation-ready**: 15 numbered implementation steps (lines 184–205) with exact data structures, keying conventions, and classification logic. An evidence worker can execute these directly.

3. **Diagnostic dimensions are well-chosen**: The 6 diagnostic questions (lines 47–74) cover repository load aggregates, section inference, row-level matched context, text span construction, schema boundary, and drift classification. Each maps to observable JSON fields.

4. **Output schema is comprehensive** (lines 100–153): `comparability_matrix.json` schema covers all comparison dimensions with machine-readable diagnostic findings. Verdict tokens are specific and actionable.

5. **Graceful degradation**: The `json_artifacts_insufficient_for_root_cause` finding (line 145) and the "stop before repository reload" guard (line 89) prevent scope creep.

6. **Boundary preservation**: All NOT_READY, candidate_only, no-source-truth, no-baseline, no-parser-replacement constraints are explicitly preserved in output schema and non-goals.

### Completeness Check

| Requirement | Status |
|---|---|
| Plan explains why diagnostic is needed before re-evidence | ✅ Lines 10–14 |
| Exact input artifacts listed with paths | ✅ Lines 80–88 |
| Exact output artifacts with paths | ✅ Lines 95–96 |
| Output JSON schema defined field-by-field | ✅ Lines 100–153 |
| Markdown report requirements specified | ✅ Lines 162–180 |
| Implementation steps numbered and ordered | ✅ Lines 184–205 |
| Allowed commands listed | ✅ Lines 208–237 |
| Stop conditions enumerated | ✅ Lines 255–265 |
| Non-goals explicit | ✅ Lines 15–25 |
| Diagnostic verdict tokens defined | ✅ Lines 155–160 |
| Validation commands specified | ✅ Lines 225–231 |
| Review gate sequence defined | ✅ Lines 239–253 |
| Completion report format specified | ✅ Lines 267–278 |

---

## Boundary Verification

| Requirement | Status |
|---|---|
| `NOT_READY` preserved | ✅ Plan verdict `HANDOFF_READY_NOT_READY`, output `not_ready: true` |
| `candidate_only=true` preserved | ✅ Output schema line 106 |
| `source_truth_status=not_proven` | ✅ Explicitly stated (line 41), output flag line 107 |
| No baseline promotion | ✅ Non-goals line 17 |
| No source truth acceptance | ✅ Non-goals line 18 |
| No parser replacement | ✅ Non-goals line 19 |
| No full field correctness | ✅ Non-goals line 20 |
| No release/PR readiness | ✅ Non-goals line 21 |
| No live/network/provider/LLM | ✅ Non-goals line 22, Forbidden line 235 |
| No direct PDF/cache/source-helper | ✅ Non-goals line 24, Forbidden line 236 |
| No code/test/runtime/control/design/README edits | ✅ Non-goals line 23 |
| JSON-only first, repository reload only if separately authorized | ✅ Lines 89–90, 114 |
| No stage/commit/push/PR in diagnostic gate | ✅ Non-goals line 23, Forbidden line 237 |
| Prior 13/4 correctly cited | ✅ Line 30 |
| Current 10/7 correctly cited | ✅ Line 32 |
| Delta -3 correctly cited | ✅ Line 33 |
| Regression rows correctly listed | ✅ Lines 35–38 |

---

## Residual Risks

1. The diagnostic may reach `json_artifacts_insufficient_for_root_cause` for the exact producer line that caused drift (F-DS-P1). This is acceptable — the diagnostic gate's primary goal is to establish whether the matrices are comparable, not to fix the producer.
2. S5's text_span_count stability (6→6) masks content composition drift (F-DS-P2). The diagnostic's other dimensions catch this, but the `text_span_count_drift` flag alone would be misleading.
3. After diagnostic completion, a separate gate will be needed to either fix wrapper determinism or authorize a repository-mediated deep diagnostic.

## Self-Check

pass — 16 factual claims verified against matrix JSON via jq, all confirmed. Plan is code-generation-ready with 15 numbered steps, comprehensive output schema, and explicit stop conditions. 3 non-blocking findings (2 Low, 1 Info) are documentation/clarity improvements, not correctness issues. All NOT_READY / candidate-only / no-live / no-source-truth boundaries verified. Plan correctly positions this as a pre-requisite diagnostic before any further re-evidence attempt.

Verdict: `PASS`。Blocking findings: 0。
