# QDII Replacement Candidate Selection Plan — Adversarial Review (DS)

> Date: 2026-05-27
> Reviewer: AgentDS
> Gate: `QDII replacement candidate selection plan gate`
> Plan under review: `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-20260527.md`
> Verdict: **PASS_WITH_FINDINGS**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `replacement/exclusion candidate selection accepted locally` |
| Next entry point | `QDII replacement candidate selection plan gate` |
| Latest accepted checkpoint | `667eed6 docs: accept replacement candidate disposition` |
| Controller judgment | `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` |
| Truth sources consulted | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Accepted Artifacts, replacement/exclusion controller judgment, `docs/code_20260519.csv` |

## Review Scope

Per review instructions: adversarially challenge next-gate recommendation; check CSV-derived pool misinterpretation risk; check QDII vs QDII-FOF taxonomy discipline; check source provenance/fail-closed, P0 quality, manager_strategy_text, no-promotion stop conditions; check future evidence commands for path consistency, CLI/FundDocumentRepository bypass, and accidental evidence authorization.

## Finding 1 — Pre-populated fund code list creates implicit shortlist risk (MODERATE)

**Evidence**: Plan §4 line 76:

> "The bounded CSV-derived enumeration pool may include non-FOF overseas/QDII rows such as `019172`, `040046`, `096001`, `006282`, `539003`, `000614`, `021539`, `020712`, `007280`, `007360`, `100050`, and `013308`, but this list is not an approved replacement list."

The plan correctly disclaims that this is not an approved list. However, naming 12 specific fund codes in a plan artifact structurally creates what looks like a pre-vetted shortlist. A future worker recovering context from this artifact alone could reasonably interpret these as "the plan author already filtered the CSV for us" and skip the enumeration gate's classification step.

The risk is amplified because the enumeration method (§4 steps 1-5) describes filtering the CSV, but this sentence already performs a de facto filter by listing specific codes. The next worker sees both "these 12 codes" and "go enumerate from CSV" — the two instructions are in tension.

**Controller action**: Either (a) remove the explicit code list from §4 and let the enumeration gate produce its own candidate-order table from CSV, or (b) accept the risk and add a controller judgment note that the enumeration gate must independently verify each code's QDII identity from public outputs before treating it as a candidate, regardless of what this plan artifact lists.

## Finding 2 — `013308` CSV category conflicts with QDII naming (MODERATE)

**Evidence**: `docs/code_20260519.csv` row:

```
易方达恒生科技ETF联接(QDII)A,013308,国内股票类
```

The fund name contains `QDII` and tracks Hang Seng Tech index (HK equities via QDII mechanism). But the CSV `类别` column says `国内股票类` (domestic stock). This is a direct taxonomy conflict.

The plan lists `013308` in the enumerated pool (§4 line 76) based on QDII naming, without flagging the CSV category conflict. Meanwhile, `012348` (天弘恒生科技指数A, also tracking Hang Seng Tech, category `国内股票类`, no QDII in name) is correctly absent from the pool. This asymmetry is defensible (name-based QDII classification is the primary signal) but the CSV category conflict must be explicitly resolved before `013308` can be accepted as a QDII replacement candidate.

**Controller action**: Require the enumeration gate to explicitly resolve `013308`'s fund type classification from public outputs or controller slot decision, documenting why CSV category `国内股票类` does not disqualify it from QDII slot consideration. Do not allow `013308` to silently enter the candidate list.

## Finding 3 — Enumeration method omits source provenance pre-filter (MODERATE)

**Evidence**: Plan §4 steps 2-4 (lines 71-74):

> 2. Keep only rows whose selected-fund identity plausibly belongs to overseas/QDII coverage and exclude the known failed candidate `017641`.
> 3. Exclude QDII-FOF rows unless a taxonomy gate has explicitly accepted QDII-FOF for this QDII replacement slot.
> 4. Produce a candidate-order table only, with no evidence run.

Steps 2 and 3 filter on fund type identity and FOF exclusion. But there is no step requiring source provenance availability as a filter. The plan's own criterion table (§3 line 50) requires:

> "Candidate must have either primary source success or complete eligible fallback provenance."

If the enumeration produces a ranked list where the top candidate has unknown or fail-closed provenance, the evidence gate will immediately hit a stop condition. This wastes a gate cycle.

The enumeration gate should at minimum record whether each candidate's source provenance status is known from existing accepted artifacts (e.g., prior extraction snapshots). For codes never extracted, the enumeration should note `provenance_unknown` as a risk flag in the candidate-order table, so the controller can decide whether to rank provenanced candidates higher.

**Controller action**: Require the enumeration gate's candidate-order table to include a `source_provenance_status` column derived from existing accepted artifacts only (no new evidence runs). Candidates with `provenance_unknown` should carry a risk flag.

## Finding 4 — QDII equity vs QDII bond subtype not addressed for replacement fitness (LOW-MODERATE)

**Evidence**: Plan §2 accepted disposition: `017641` is `qdii_fund` (equity QDII — tracks S&P 500). Plan §4 enumerated pool includes:

- `007360` 易方达中短期美元债债券(QDII) — CSV category `海外债券/稳健类`
- `100050` 富国全球债券(QDII) — CSV category `海外债券/稳健类`

These are QDII bond funds, not QDII equity funds. Replacing an S&P 500 equity QDII with a USD bond QDII would serve a fundamentally different portfolio role. The plan's fund type slot criterion (§3) says `qdii_fund` but `fund_type.py` classification (design.md §6.5) treats `qdii_fund` as a single type without equity/bond subtyping. The current type system does not distinguish QDII equity from QDII bond.

This is not a plan defect per se — the current type system doesn't have the subtype — but the enumeration gate will produce a candidate list where bond QDII funds sit alongside equity QDII funds without the subtype distinction that matters for portfolio replacement fitness.

**Controller action**: Either (a) accept that current `qdii_fund` type granularity is sufficient for this gate and defer subtype to the evidence gate's qualitative assessment, or (b) require the enumeration gate to add a `csv_category` or `asset_class` column so the controller can decide whether bond QDII candidates are in-scope for replacing an equity QDII slot.

## Finding 5 — QDII vs QDII-FOF taxonomy discipline is adequate (INFO)

The plan correctly:
- Excludes QDII-FOF from the pool unless a separate taxonomy gate accepts QDII-FOF (§3, §4 step 3)
- Does not list `007721` (天弘标普500发起(QDII-FOF)A) or `017970` (摩根海外稳健配置混合(QDII-FOF)人民币A) in the enumerated pool
- Stop condition §6 line 99 explicitly blocks ambiguous QDII vs QDII-FOF taxonomy

This discipline is consistent with the controller judgment's FOF disposition (`needs_taxonomy_gate`) and the accepted evidence chain showing FOF as a `data_gap` / taxonomy residual. No finding.

## Finding 6 — Source fail-closed, P0 quality, manager_strategy_text, and no-promotion stop conditions are sufficient (INFO)

Plan §6 stop conditions (lines 97-109) correctly enumerate:
- Source provenance regression or missing provenance → stop (line 100)
- Fail-closed categories `schema_drift`, `identity_mismatch`, `integrity_error` → stop (line 101)
- P0 quality block → stop (line 102)
- `manager_strategy_text` P0-blocking without reclassification gate → stop (line 103)
- Evidence requiring direct PDF/cache/source-helper access → stop (line 104)
- Source strategy or FundDocumentRepository mutation → stop (line 105)
- Renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, extractor, taxonomy, quality weakening → stop (lines 106-108)
- Promotion attempts → stop (line 108)
- Evidence without accepted enumeration/selection plan → stop (line 109)

These stop conditions are comprehensive and correctly map to AGENTS.md fallback strategy (§6.1), design.md fail-closed semantics (§6.1), and the controller judgment's explicit constraints. No finding.

## Finding 7 — Future evidence commands use correct public CLI path, but `--source-csv` flag is unverified (LOW)

**Evidence**: Plan §5 future command shapes (lines 82-87):

```
uv run fund-analysis extraction-snapshot --run-id qdii-replacement-<code>-2024-20260527 --report-year 2024 --fund-code <code> --source-csv docs/code_20260519.csv --output-dir reports/extraction-snapshots/...
```

The commands use the public CLI entry point (`uv run fund-analysis extraction-snapshot`) which routes through UI → Service → fund_agent/fund — this is the correct deterministic path. They do not bypass CLI, directly call internal modules, or access PDF/cache/source-helper.

However, `--source-csv` as a CLI parameter for `extraction-snapshot` is not verified against the current CLI implementation. The plan also uses `--force-refresh` (implied by the provenance requirement) but doesn't list it explicitly. If `--source-csv` doesn't exist or has a different flag name, the evidence worker will fail at command construction time, which is a recoverable failure but wastes a cycle.

The plan explicitly states "This gate does not run evidence" (§5 line 80) and non-goals exclude evidence CLI runs (§8 line 136). No accidental authorization.

**Controller action**: Defer to evidence gate — the evidence worker must verify exact CLI flags before running commands. This is a documentation precision issue, not a plan defect.

## Finding 8 — Next gate recommendation is correct; alternatives do not apply (INFO)

**Challenge**: Is `QDII replacement candidate enumeration plan gate` the correct next step, or should it be reduced-scope / FOF taxonomy / bond evidence / index fact freeze?

**Analysis**:

| Alternative | Why it does not apply |
|---|---|
| Reduced-scope (skip enumeration, directly pick next S&P 500 QDII) | Controller judgment explicitly requires "plan before evidence" and "define valid QDII replacement criteria." Skipping enumeration violates the accepted constraint. |
| FOF taxonomy gate | FOF disposition is `needs_taxonomy_gate` — separate owner, separate slot. Not a substitute for QDII replacement. |
| Bond evidence gate | Bond disposition is `needs_evidence_gate` — separate slot (`006597`), separate owner. Not relevant to QDII replacement. |
| Index fact freeze | Index disposition (`110020`) is `include_for_later_review` — separate slot, separate owner. Not relevant. |

The enumeration gate is the minimal correct next step. It is bounded (CSV only), plan-only (no evidence), and preserves all accepted dispositions. No alternative path avoids it without violating the controller judgment's explicit constraints.

## Summary Matrix

| # | Finding | Severity | Blocking? |
|---|---|---|---|
| F1 | Pre-populated code list creates implicit shortlist risk | MODERATE | No |
| F2 | `013308` CSV category `国内股票类` conflicts with QDII naming | MODERATE | No |
| F3 | Enumeration method omits source provenance pre-filter | MODERATE | No |
| F4 | QDII equity vs QDII bond subtype not addressed | LOW-MODERATE | No |
| F5 | QDII vs QDII-FOF taxonomy discipline adequate | INFO | No |
| F6 | Stop conditions comprehensive and correct | INFO | No |
| F7 | Future evidence CLI path correct; `--source-csv` flag unverified | LOW | No |
| F8 | Next gate recommendation correct; alternatives inapplicable | INFO | No |

## Verdict

**PASS_WITH_FINDINGS** — The plan correctly preserves the Startup Packet next entry point, `017641` accepted disposition, and all controller judgment constraints. The core recommendation (enumeration before evidence) is correct. Four moderate/low findings should be addressed by the controller before or at the enumeration gate; none blocks this plan from proceeding.

No code changes, design doc changes, control doc changes, evidence runs, commits, pushes, or next-gate entry occurred.
