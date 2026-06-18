# Docling Multi-sample Field-family Correctness Expansion Evidence Review (DS tmux) - 2026-06-16

Gate: `Docling Multi-sample Field-family Correctness Expansion Evidence Gate`
Role: AgentDS evidence review worker
Release/readiness: `NOT_READY`

## Scope

Review the evidence artifacts against the accepted plan (`bc82125`) and DS A1 controller closure. Evaluate: plan fidelity, blocked_not_ready justification, avoidance of candidate-json-as-truth, NOT_READY preservation, and JSON schema/field coherence.

This review does not re-execute evidence, call FDR/PDF/live/EID, or modify any file except this artifact.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-evidence-20260616.md` | Evidence markdown summary under review |
| `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json` | Evidence JSON artifact under review |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md` | Accepted plan |
| `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-controller-judgment-20260616.md` | Controller judgment with DS A1 closure |
| `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json` | Accepted S1 pilot reviewed facts |
| `reports/representation-json/full-representation-export-manifest-20260615.json` | Accepted manifest |

File-system verification (no-live, read-only):

- `004393_2025_docling_full.json`: `069282b22d7926e93743cc12a8538e43eaf262aa165376d872552a76efac0e49` — matches evidence and manifest.
- `004393_2025_docling_current_envelope.json`: `f4ea5e1fa028a364c2286a9244e7d482c4851afbcefb506c5b5b08db4ff02d28` — exists but NOT in manifest.
- `FundDocumentRepository` exists at `fund_agent/fund/documents/repository.py` and is importable.

## Findings

### F1: S1 fact candidate_artifact path inconsistent with input_artifacts and manifest (material)

**What:** The `facts[]` array records `candidate_artifact` as `reports/representation-json/004393_2025_docling_current_envelope.json` for all 21 S1 Docling facts. However:

- `input_artifacts[]` records the verified candidate as `004393_2025_docling_full.json` (hash `069282b...`).
- The manifest only lists `004393_2025_docling_full.json` for S1 docling.
- `_current_envelope.json` has hash `f4ea5e1...` — a different file, not in the manifest, not hash-verified by this evidence gate.

**Why this matters:** The evidence's own input verification checked `_full.json` against the manifest. If a future reader traces a fact's `candidate_artifact` path, they will land on a file that was never hash-verified in this gate, creating a provenance gap. The hash the evidence recorded for S1 docling (`069282b...`) does not match the file referenced in the facts.

**Severity:** Material coherence defect. Since S1 facts are explicitly reused from the accepted pilot reviewed-facts artifact (not re-extracted from either JSON), the practical correctness risk is low — but the artifact path is wrong and must be corrected.

### F2: FundDocumentRepository not attempted for S4/S5/S6 reference availability (material)

**What:** The accepted plan §9 step 6 specifies:

> "Use an accepted same-source reference artifact if available; otherwise use only FundDocumentRepository with no-refresh/no-live intent and force_refresh=False."

The evidence gate correctly identifies that no accepted same-source reference artifact exists for S4/S5/S6, but it does not attempt the second pathway (`FundDocumentRepository` with `force_refresh=False`). All S4/S5/S6 samples show `repository_load.attempted: false`.

**Why this matters:** The DS A1 rewrite and controller closure were specifically designed to provide a bounded, no-live pathway for reference availability proof through `FundDocumentRepository`. By skipping it entirely, the evidence leaves open the question of whether a no-live reference COULD have been obtained for S4/S5/S6. The blocking might still be correct in practice, but the plan compliance is incomplete.

**Mitigation:** The controller judgment §6 residual pre-authorized blocking: "S4/S5/S6 may be blocked if no accepted same-source reference artifact or no-live repository metadata proof exists. Evidence gate should return blocked_not_ready or partial result instead of triggering live acquisition." And the plan uses "may use" (not "must use") for FDR. So the direction is not wrong — but the evidence should document why FDR was not attempted rather than silently skipping it.

### F3: S1 facts correctly reused by hash, not re-extracted (pass)

All 21 S1 Docling facts carry `candidate_locator_status: "reused_from_accepted_pilot"` and `reference_source: "accepted_same_source_reference_artifact"`. Each fact's `review_note` states: "Reused from accepted 004393 bounded pilot. This evidence gate did not re-open PDF/FDR/manual reference review." This correctly implements the plan's requirement for S1 as accepted control sample.

### F4: Candidate JSONs not treated as source truth or correctness proof (pass)

The evidence preserves all boundary flags:

- `not_source_truth: true`
- `not_production_parser_replacement: true`
- `not_full_field_correctness: true`
- `not_readiness_proof: true`
- `candidate_field_correctness_status_remains: "not_proven"`
- Blocked claims include `not_field_correctness_proof` for S4/S5/S6

No fact was selected or reviewed for S4/S5/S6. The evidence markdown §6 explicitly lists `not_source_truth` and `not_field_correctness_proof`.

### F5: NOT_READY and no production parser replacement preserved (pass)

Release/readiness marked `NOT_READY` in both artifacts. All boundary flags set. The evidence markdown §7 verdict is `BLOCKED_INSUFFICIENT_REVIEWABLE_SAMPLE_MATRIX_NOT_READY`. The command exclusion list (`commands_not_run`) correctly records no FDR/PDF/parse/Docling/EID/live/provider/LLM/release/PR activity.

### F6: EID HTML remains blocked/deferred (pass)

All four samples show `eid_html_status: "blocked_deferred"`. The route result for `eid_xbrl_html_render_candidate` is `blocked_deferred` with boundary "Out of scope for this Docling expansion gate." Consistent with plan §6.

### F7: JSON schema field and count coherence (pass with F1 caveat)

**Fact counts:**
- 21 Docling facts total (all S1)
- 0 S4/S5/S6 facts (all blocked before selection)
- Fact IDs: S1-F001 through S1-F020, plus S1-F025 = 21
- Gap F021–F024: explained by 4 pdfplumber comparator facts in the source pilot artifact not carried into this evidence's Docling-only `facts[]` array. Coherent but not documented in the evidence.

**Family counts (S1):**
- `fund_identity_profile`: 5 facts (F001–F005)
- `product_contract_profile`: 3 facts (F006–F008)
- `performance_indicators`: 4 facts (F009–F012)
- `expense_costs`: 3 facts (F013–F015)
- `portfolio_structure`: 3 facts (F016–F018)
- `manager_alignment`: 3 facts (F019, F020, F025)

All families meet or exceed plan minimums. Family counts sum to 21. Family results match (6 families × `pass` for S1, 6 families × `blocked` each for S4/S5/S6).

**Sample results:**
- S1: 6 reviewable, 6 passed — matches `pass` per plan §8.
- S4/S5/S6: 0 reviewable, 6 blocked each — matches `blocked` per plan §8.

**Route results:**
- `docling_pdf_candidate`: 21 reviewed, 21 exact/normalized, result `blocked` (correct — expansion is blocked, S1 pass is reused not new).
- `pdfplumber_pdf_candidate`: 4 reviewed, 0 exact, 4 mismatch, result `diagnostic_only`.
- `eid_xbrl_html_render_candidate`: 0 reviewed, result `blocked_deferred`.

**Hash handling for S4/S5/S6:** The manifest records source PDF hashes, not output JSON hashes, for S4/S5/S6. The evidence correctly records this as `manifest_hash_role: "output_json_hash_recorded_manifest_hash_is_source_pdf_input_hash"` and sets `hash_match_manifest_when_applicable: null`. Not a coherence defect.

### F8: S4/S5/S6 blocking justified by missing same-source reference proof (conditional pass)

The blocking direction is correct. No accepted same-source reference artifacts exist for S4(006597/2024), S5(017641/2024), S6(110020/2024). The evidence correctly refrains from treating candidate JSON presence as proof. However, F2 documents the incomplete FDR pathway.

### F9: pdfplumber comparator scope correctly bounded (pass)

The evidence limits pdfplumber to 4 reused S1 comparator facts, all mismatch, all diagnostic only. The route result boundary states: "Comparator only; 004393 comparator mismatches are not generalized." This matches plan §6.

## Required Fixes

### Fix 1: Correct S1 fact candidate_artifact paths (required before next gate)

Replace all 21 occurrences of `"candidate_artifact": "reports/representation-json/004393_2025_docling_current_envelope.json"` with `"candidate_artifact": "reports/representation-json/004393_2025_docling_full.json"` in the evidence JSON artifact. This aligns the fact-level path with the input_artifacts verification path and the manifest.

### Fix 2: Document FundDocumentRepository non-attempt for S4/S5/S6 (required before next gate)

Add a note in the evidence markdown §4 (Same-source Reference Proof) explaining why `FundDocumentRepository(force_refresh=False)` was not attempted for S4/S5/S6. Acceptable reasons include:
- Evidence scope explicitly excludes FDR execution.
- FDR internal behavior could not be verified as truly no-live without inspecting source/cache internals (which is prohibited).
- Controller pre-authorized blocking in §6 residuals.

The fix should not change the blocked outcome — only document the decision.

## Residuals

| Residual | Owner | Handling |
| --- | --- | --- |
| F021–F024 gap not documented in evidence | Evidence worker | Low: add a note explaining pdfplumber comparator facts excluded from Docling-only facts array. |
| FDR pathway remains untested for no-live reference availability | Controller / next gate | The next gate should either explicitly attempt FDR with `force_refresh=False` and record the result, or explicitly accept that FDR is out of scope for all no-live evidence gates. |
| S4/S5/S6 reference proof deferred | Next evidence gate | Requires either accepted same-source reference artifacts or explicit controller authorization to attempt FDR. |

## Verdict

```text
VERDICT: PASS_WITH_REQUIRED_FIXES_NOT_READY
```

**Basis:**

- The evidence correctly blocks S4/S5/S6 rather than treating candidate JSONs as proof.
- All NOT_READY and boundary flags are correctly preserved.
- No source truth, parser replacement, or production change is claimed.
- S1 facts are correctly reused from accepted pilot.
- EID HTML remains correctly blocked/deferred.
- pdfplumber comparator scope is correctly bounded.

However, two material fixes are required before the next gate can proceed:
1. S1 fact `candidate_artifact` paths must be corrected from `_current_envelope.json` to `_full.json`.
2. The FDR non-attempt for S4/S5/S6 must be documented with rationale.

The blocking direction is not wrong — the fixes improve artifact coherence and plan compliance without reopening the evidence.
