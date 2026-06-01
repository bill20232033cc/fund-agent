# Run Review: Small Baseline Corpus v1 Evaluation

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-small-baseline-corpus-v1-run-20260527.md`
> Accepted plan: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md`
> Controller judgment: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-controller-judgment-20260527.md`
> Verdict: **PASS**

---

## Criterion 1: Did the run satisfy accepted plan scope and prohibitions?

**Verdict: PASS**

The run executed all 15 verifier matrix commands from the accepted plan. Scope compliance:

- No source, tests, README, renderer, FQ0-FQ6, Service/CLI defaults, Host/Agent/dayu, `FundDocumentRepository`, source fallback, extractor, fixture, golden corpus, package config, commit, push, or PR changes.
- `git diff --check`: passed (line 79).
- All bulk outputs under `/tmp/...` or `reports/...` scratch paths.
- Tracked artifact contains only summary, evidence paths, and issue taxonomy.

One minor deviation: the plan specified `checklist 004393 --report-year 2025 --dev-override --quality-gate-policy warn` but the CLI does not support those flags for `checklist`. The worker correctly used the supported command and recorded the deviation (line 25). This is correct handling — the plan assumed CLI parity that does not exist.

No finding.

---

## Criterion 2: Are candidate statuses supported by direct command evidence?

**Verdict: PASS**

Each clean candidate has direct command evidence:

| Candidate | Snapshot | Score | Quality Gate | Evidence |
|-----------|----------|-------|--------------|----------|
| `004393`/2024 | 16 rows, 0 errors | `partially_covered`, 9/9 matches | `warn`, 3 issues | Lines 28, 31, 34 |
| `004194`/2024 | 16 rows, 0 errors | `covered`, 5/5 matches | `warn`, 3 issues | Lines 29, 32, 35 |
| `006597`/2024 | 16 rows, 0 errors | `partially_covered`, 9/9 matches | `block`, 7 issues (35.7% missing) | Lines 30, 33, 36 |

Product smoke commands also ran for `004393`/2024 (analyze + checklist) and the selected-funds batch smoke (3/3 pass). All statuses are directly evidenced.

No finding.

---

## Criterion 3: Is 004393/2025 correctly treated as probe-only?

**Verdict: PASS**

Evidence:

- Line 24: analyze ran with `--dev-override --quality-gate-policy warn`; "recorded only availability/year-scope, not final-judgment semantics."
- Line 25: checklist ran without unsupported dev-override flags; deviation recorded.
- Line 43: status flags are `probe_only`; "repository identity not accepted for baseline."
- Line 43: "Do not consume final-judgment semantics from `--dev-override`; 2024 golden/facts must not be reused for 2025 correctness."
- Line 62: "quality gate info says existing 004393 golden rows do not cover 2025 and other-year golden is not used."

The run correctly treats 2025 as probe-only, records year-scoped golden non-coverage, and does not reuse 2024 facts for 2025 correctness.

No finding.

---

## Criterion 4: Are fallback-blocked and FOF data_gap rows excluded from clean denominator?

**Verdict: PASS**

Evidence:

- Lines 46-49: `110020`, `017641`, `007721`, `017970` all show "Not run by design; clean denominator exclusion" or "data-gap row only."
- Line 55: "Excluded visible rows: 4 unique fund codes / 4 rows for index, QDII, and FOF attempts; plus `004393` / 2025 probe-only row."
- Line 64: "No fallback-blocked or FOF data-gap row was treated as clean denominator."

All exclusions are correctly maintained.

No finding.

---

## Criterion 5: Are golden coverage/correctness observations separated from extraction gaps?

**Verdict: PASS**

Evidence:

- Line 60: "`004194` / 2024 did produce correctness signal in this run (`covered`, 5/5 matches), so it should not be reported as `year_not_covered` for this exact run."
- Line 61: "`006597` / 2024 produced correctness signal (`partially_covered`, 9/9 matches), but quality gate blocked on field missing rate. This is a data/source extraction and bond-lens coverage problem, not a golden mismatch."
- Line 45 (`006597`): "Generic equity-style report confidence would be a false positive because bond-lens facts are materially incomplete."

The run correctly separates golden coverage (which exists for all three clean candidates) from extraction gaps (which are the actual blockers). This is a positive deviation from the plan's expectation that `004194` and `006597` would produce `year_not_covered` — the golden answer JSON actually covers them.

No finding.

---

## Criterion 6: Is the next gate recommendation justified by evidence?

**Verdict: PASS**

The run recommends "more baseline probing / source recovery / taxonomy" (line 68). Justification:

- Clean coverage is 3 candidates / 3 slots, below the 5-10 target (line 56).
- `006597` is quality-gate blocked (35.7% missing field rate) — one clean slot is not viable (line 75).
- `110020` and `017641` remain fallback-blocked with unknown upstream failure categories (lines 70-71).
- FOF remains a data gap (line 72).

This matches the plan's decision rule: "Clean coverage is at or below three clean candidates, covers fewer than half the target fund-type slots, or FOF/index/QDII blockers dominate → more baseline probing / source recovery / taxonomy gate."

The recommendation also includes focused sub-paths: bond extraction priority fixes, tracking-error/turnover fact review, and index/QDII source recovery. These are actionable and evidence-backed.

No finding.

---

## Criterion 7: Are large outputs kept out of tracked artifacts?

**Verdict: PASS**

The tracked artifact contains only:

- Command summary table with status and notes.
- Candidate matrix with status flags, gaps, categories, and evidence paths.
- Clean denominator summary.
- Interpretation notes.
- Next gate recommendation.
- `git diff --check` result.

All bulk outputs (stdout/stderr, snapshot JSONL, score JSON, quality gate JSON/Markdown, smoke reports) are referenced by scratch path only. No large content is embedded in the tracked artifact.

No finding.

---

## Criterion 8: Does any finding block closeout?

**Verdict: PASS — no blocking findings**

No finding in this review blocks closeout, requires a rerun, or requires plan/run artifact correction.

---

## Additional Observations

### Finding I1: Golden coverage broader than plan expected

Evidence: The plan (line 35) expected `004194`/2024 and `006597`/2024 to produce `year_not_covered` / `FQ0/info`. The run found both actually have golden coverage: `004194` is `covered` (5/5 matches), `006597` is `partially_covered` (9/9 matches). The run correctly records this in interpretation notes (lines 60-61).

This is a positive deviation. The golden answer JSON covers more candidates than the plan anticipated, which strengthens the evidence base for a future golden corpus gate.

Severity: **INFO**

---

### Finding I2: `006597` quality-gate `block` driven by missing-field rate, not correctness mismatch

Evidence: Line 36 shows `006597` quality gate is `block` with 7 issues and 35.7% missing rate. Line 45 confirms "Generic equity-style report confidence would be a false positive because bond-lens facts are materially incomplete." Line 61 confirms "This is a data/source extraction and bond-lens coverage problem, not a golden mismatch."

The `block` is correctly attributed to extraction gaps (missing `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`, `investor_return`) rather than golden correctness failure. This means `006597`'s path to viability is extraction improvement, not golden correction.

Severity: **INFO**

---

### Finding I3: `checklist` CLI does not support `--dev-override` / `--quality-gate-policy`

Evidence: Line 25 states "CLI has no `--dev-override` / `--quality-gate-policy` for `checklist`; used supported command and recorded deviation."

The plan assumed CLI flag parity between `analyze` and `checklist`. The worker correctly adapted. This is an implementation fact that future plans should account for — `checklist` has a simpler CLI surface than `analyze`.

Severity: **MINOR** (for future plan accuracy, not for this run's correctness)

---

## Summary

| Finding | Severity | Description |
|---------|----------|-------------|
| I1 | INFO | Golden coverage broader than plan expected (positive deviation) |
| I2 | INFO | `006597` block driven by extraction gaps, not correctness mismatch |
| I3 | MINOR | `checklist` CLI lacks `--dev-override` / `--quality-gate-policy` flags |

---

## Verdict

**PASS**

The run satisfies all 8 review criteria. All 15 verifier matrix commands executed with direct evidence. Clean candidates are correctly evaluated with snapshot, score, and quality-gate data. `004393`/2025 is correctly probe-only with year-scoped golden non-coverage. Fallback-blocked and FOF data-gap rows are excluded from clean denominator. Golden coverage observations are correctly separated from extraction gaps. The next gate recommendation is justified by evidence and matches the plan's decision rules. Large outputs are in scratch paths only. No blocking findings exist.

The run demonstrates a positive deviation: golden coverage is broader than the plan expected, with `004194` and `006597` both having comparable golden rows. The primary blocker for `006597` is extraction field gaps (35.7% missing rate), not golden coverage. The path forward is clear: source recovery for index/QDII, extraction priority fixes for bond, and continued probing for FOF.
