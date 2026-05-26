# Evidence Review: Subgate 1 Bond Triage

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-20260527.md`
> Controller judgment: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-controller-judgment-20260527.md`
> Verdict: **PASS**

---

## Criterion 1: Did evidence run stay within authorized scope?

**Verdict: PASS**

Line 11 states: "This artifact uses only public CLI outputs, accepted review artifacts, accepted design/template rules, and current tracked extractor/scoring code as evidence. It does not use direct production PDF reads, cache inspection, source-helper/downloader calls, or ad hoc annual-report parsing."

Commands executed (lines 15-20): `extraction-snapshot`, `extraction-score`, `quality-gate`, `git diff --check`. All are from the authorized command list. The `holdings_snapshot` classification references "tracked extractor/scoring code uses stock/top-ten/industry-style holdings signals" (line 41), which is allowed per the plan ("current tracked extractor tests / fixtures, if they already exist").

No forbidden operations observed. No finding.

---

## Criterion 2: Are command results and scratch/tracked boundaries sufficient?

**Verdict: PASS**

- **Command results** (lines 15-20): All 4 commands have exit status, evidence paths, and structured result summaries.
- **Public CLI observations** (lines 24-31): Snapshot 16 records / 0 errors; score correctness `available`, `partially_covered`, 9/9 comparable matches, accuracy 1.0; missing field count 5/14 (35.7%); quality gate `block`, 7 issues.
- **Tracked artifact** (line 56): one artifact under `docs/reviews/`.
- **Scratch paths** (lines 60-61): `/tmp/...` and `reports/extraction-snapshots/...`.
- **Interpretation guard** (line 33): "the score correctness result is only for golden-covered comparable fields. It does not prove that blocked bond fields are correct, available, or inapplicable."

Boundaries are clean. No finding.

---

## Criterion 3: Are field classifications supported by allowed evidence?

**Verdict: PASS**

| Field | Classification | Evidence quality |
|-------|---------------|-----------------|
| `turnover_rate` | `needs_more_evidence` | Snapshot shows `missing`, no value, no anchor, note says §8 did not disclose rule-extractable turnover rate. Public CLI cannot distinguish disclosure absence from extractor limitation. Correct classification. |
| `holder_structure` | `needs_more_evidence` | Snapshot shows `missing`, no value, no anchor, note says §9 did not disclose rule-extractable holder structure. Same reasoning as above. Correct. |
| `holdings_snapshot` | `bond_lens_contract_gap` | Snapshot shows `missing`, no stock holding details; tracked code expects stock/top-ten/industry-style signals; accepted template bond lens emphasizes duration, credit exposure, leverage/liquidity, drawdown. The field name and scoring expectation are equity-shaped while the fund is `bond_fund`. Correct classification — this is a lens contract mismatch, not a simple extractor miss. |
| `share_change` | `extractor_gap` | Snapshot shows `missing`, note says §10 contains multiple share columns and current rules cannot reliably choose the corresponding share class. This is a concrete extractor limitation identified by the extraction attempt itself, not an inference about PDF content. Correct classification. |
| `investor_return` | `score_contract_gap` | Snapshot shows `missing`, §3 does not directly disclose investor return, fallback pending. P2 (not P1 block). Correctly classified as not equity-only and not N/A for bond funds. |
| `nav_data` anchor | `score_contract_gap` | Value present (source `nav_cache`, 1802 records), but anchor absent. Correctly identified as external NAV provenance issue, not annual-report extractor gap. |

All classifications are supported by allowed evidence and align with the plan's triage checklist. No finding.

---

## Criterion 4: Is Track 1B closure compliant?

**Verdict: PASS**

Lines 48-50: "Track 1B status: `not_run_no_approved_candidates`. The controller did not supply replacement candidates for index/QDII/FOF probing. Per the accepted plan and judgment, this worker did not browse, search, or select ad hoc replacement candidates. This track is independently closeable and has no command output."

This complies with the plan's Track 1B specification and the controller judgment's authorized scope. No finding.

---

## Criterion 5: Is next recommendation justified?

**Verdict: PASS**

The recommendation (lines 67-83) proposes "more evidence before authorizing implementation" and suggests splitting future work:

1. First, design/review a bond-lens evidence contract for `holdings_snapshot`.
2. Separately, plan a focused `share_change` ambiguity-handling implementation.
3. Keep `turnover_rate` and `holder_structure` evidence-only until approved source proves fact existence.

This is justified by the field classifications:
- `share_change` has the strongest evidence for a narrow extractor fix (concrete §10 multi-column limitation).
- `holdings_snapshot` points to a bond-lens contract gap that needs design work before extractor changes.
- `turnover_rate` and `holder_structure` are `needs_more_evidence` — implementation would require either direct PDF evidence (forbidden) or an accepted policy decision.
- `investor_return` and `nav_data` are score-contract issues, not P1 blockers.

The recommendation correctly avoids authorizing a big-bang fix and keeps implementation gated behind evidence. No finding.

---

## Criterion 6: Does any finding require artifact correction, rerun, or block closeout?

**Verdict: PASS — no blocking findings**

No finding requires artifact correction, rerun, or blocks closeout.

---

## Additional Observations

### Finding I1: `share_change` classification is the most actionable

Evidence: Line 42 identifies a concrete extractor limitation — "annual report §10 contains multiple share columns and current rules cannot reliably choose the corresponding share class." This is the only field where the extraction attempt itself identified a specific, fixable root cause. The other `needs_more_evidence` fields require either PDF access or policy decisions.

This observation supports the recommendation to prioritize `share_change` as the first implementation slice.

Severity: **INFO**

---

### Finding I2: `holdings_snapshot` bond-lens contract gap has broad implications

Evidence: Line 41 classifies `holdings_snapshot` as `bond_lens_contract_gap` because "the field name and current scoring expectation are equity-holdings shaped, while the fund is `bond_fund`." This suggests the bond lens needs a fundamentally different holdings/risk evidence contract, not just a field-existence fix.

If the bond-lens contract gap is addressed, it may also affect how `turnover_rate` and `holder_structure` are scored for bond funds, potentially resolving some `needs_more_evidence` fields through policy rather than extraction.

Severity: **INFO**

---

### Finding I3: Quality gate still `block` with 7 issues — correctly preserves FQ semantics

Evidence: Line 30 shows quality gate status remains `block` with 7 issues. The evidence artifact does not attempt to weaken or bypass this. Line 89: "Implementation blocker: yes, by design."

This correctly preserves FQ0-FQ6 semantics while the triage determines the right path forward.

Severity: **INFO**

---

## Summary

| Finding | Severity | Description |
|---------|----------|-------------|
| I1 | INFO | `share_change` has strongest evidence for narrow extractor fix |
| I2 | INFO | `holdings_snapshot` bond-lens contract gap may have broad implications for bond scoring |
| I3 | INFO | Quality gate `block` correctly preserved — no FQ weakening attempted |

---

## Verdict

**PASS**

The evidence artifact satisfies all 6 review criteria. The run stayed within authorized public-output scope. Command results and scratch/tracked boundaries are sufficient. All 6 field classifications are supported by allowed evidence with clear rationale. Track 1B closure is compliant. The next recommendation is justified — `share_change` is ready for a focused extractor plan, `holdings_snapshot` needs bond-lens contract design first, and `turnover_rate`/`holder_structure` remain evidence-blocked. No findings require artifact correction, rerun, or block closeout.
