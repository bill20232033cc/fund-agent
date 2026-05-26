# release-maintenance baseline coverage/source/taxonomy/bond triage evidence - 2026-05-27

## Scope recap

- Gate: baseline coverage / source recovery / taxonomy + bond extraction triage.
- Accepted plan: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-20260527.md`.
- Controller judgment: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-plan-controller-judgment-20260527.md`.
- Authorized Track 1A: `006597` / `2024` bond evidence-only triage.
- Authorized Track 1B: close replacement probing as `not_run_no_approved_candidates`; no browsing, no search, no ad hoc candidate selection.

This artifact uses only public CLI outputs, accepted review artifacts, accepted design/template rules, and current tracked extractor/scoring code as evidence. It does not use direct production PDF reads, cache inspection, source-helper/downloader calls, or ad hoc annual-report parsing.

## Command results

| Command | Result | Evidence path |
| --- | --- | --- |
| `uv run fund-analysis extraction-snapshot --run-id baseline-coverage-triage-006597-2024 --fund-code 006597 --report-year 2024` | pass, exit 0 | `/tmp/fund-agent-baseline-coverage-triage-20260527/006597/extraction-snapshot.stdout.txt`; `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/snapshot.jsonl`; `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/errors.jsonl`; `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/summary.md` |
| `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/baseline-coverage-triage-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/baseline-coverage-triage-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json` | pass, exit 0 | `/tmp/fund-agent-baseline-coverage-triage-20260527/006597/extraction-score.stdout.txt`; `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/score.json`; `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/score.md`; `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/golden_set.json` |
| `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/baseline-coverage-triage-006597-2024/score.json` | pass, exit 0; gate status `block`, 7 issues | `/tmp/fund-agent-baseline-coverage-triage-20260527/006597/quality-gate.stdout.txt`; `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/quality_gate.json`; `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/quality_gate.md` |
| `git diff --check` | pass, exit 0 | command output |

## Public CLI observations

- `snapshot.jsonl`: 16 records.
- `errors.jsonl`: 0 records.
- `summary.md`: selected funds 1, succeeded 1, failed 0, snapshot records 16.
- `score.json`: correctness available; coverage scope `partially_covered`; comparable records 9; matched records 9; mismatched records 0; accuracy rate 1.0 for golden-covered comparable fields.
- `score.json`: fund type resolved as `bond_fund`; missing field count 5 / total field count 14; missing field rate 0.35714285714285715.
- `score.json`: P1 failed fields are `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change`.
- `quality_gate.json`: final status `block`.
- `quality_gate.json`: issue taxonomy includes four P1 field warnings, one fund-level P1 failure, one strict-golden informational issue, and one blocking missing-field-rate issue.

Interpretation guard: the score correctness result is only for golden-covered comparable fields. It does not prove that blocked bond fields are correct, available, or inapplicable.

## Field-level classification for 006597 / 2024

| Field | Classification | Allowed evidence source | Rationale | Required next action |
| --- | --- | --- | --- | --- |
| `turnover_rate` | `needs_more_evidence` | Public snapshot note: extraction mode `missing`, no value, no anchor, note says annual report §8 did not disclose a rule-extractable turnover rate; `score.json` marks it P1 failed; accepted design maps turnover to manager consistency/cost analysis. | The allowed public evidence shows the current extractor did not produce a value and the current score treats it as P1. It does not prove whether the annual report contains a bond-applicable turnover fact, whether bond funds should use a different turnover proxy, or whether this P1 expectation is over-broad for bond funds. Under the no-direct-PDF rule, do not infer from absence alone. | More evidence or controller-approved design review for bond turnover applicability before implementation. |
| `holder_structure` | `needs_more_evidence` | Public snapshot note: extraction mode `missing`, no value, no anchor, note says annual report §9 did not disclose rule-extractable institution/individual holder structure; `score.json` marks it P1 failed; accepted design maps holder structure / manager alignment to chapters 3 and 6. | Holder structure is not equity-only in the accepted design, but the public CLI output cannot distinguish actual disclosure absence from extractor limitation. No direct PDF/cache/source inspection is authorized, so the root cause remains unproven. | More evidence or accepted policy decision on bond holder-structure expectation before implementation. |
| `holdings_snapshot` | `bond_lens_contract_gap` | Public snapshot note: extraction mode `missing`, no value, no anchor, note says no rule-extractable stock holding details or industry distribution table; tracked extractor/scoring code uses stock/top-ten/industry-style holdings signals; accepted template bond lens emphasizes bond-specific risk facts such as duration, credit exposure, leverage/liquidity, drawdown, and redemption pressure. | The field name and current scoring expectation are equity-holdings shaped, while the fund is `bond_fund`. The observed block is therefore not just a missing value; it exposes that the bond lens needs a bond-specific holdings/risk evidence contract instead of requiring stock holdings snapshot semantics. | Plan a narrow bond-lens contract slice before extractor work: define which bond holdings/risk facts satisfy this slot and how score/quality gate should evaluate them. |
| `share_change` | `extractor_gap` | Public snapshot note: extraction mode `missing`, no value, no anchor, note says annual report §10 contains multiple share columns and current rules cannot reliably choose the corresponding share class; accepted template Chapter 4 requires share-change trend and bond lens still considers large subscription/redemption events. | Unlike turnover/holder structure, the public CLI note identifies a concrete current-rule limitation: share-class selection ambiguity. The accepted template makes share change relevant to bond investor experience, so this is not field-applicability by fund type. | Candidate for a focused implementation plan after controller approval: resolve share-class selection or expose an ambiguity status without weakening FQ gates. |
| `investor_return` | `score_contract_gap` | Public snapshot note: extraction mode `missing`, no value, no anchor, note says §3 does not directly disclose investor return and fallback is pending a later slice; accepted design says investor return is a Chapter 3 / investor-return evidence concept and defines fallback by share change x NAV estimate; `score.json` classifies it as P2, not a P1 block. | Investor return is not equity-only and must not be marked inapplicable for `bond_fund`. The current result shows a known score/extractor contract gap around direct disclosure vs fallback/projection, but it is not the immediate P1 quality-gate blocker. | Defer to a score-contract / fallback-design slice after baseline blockers are narrowed. Do not treat as bond N/A. |
| `nav_data` anchor status | `score_contract_gap` | Public snapshot: `nav_data` value present, source `nav_cache`, cached true, records 1802, but anchor absent; accepted design treats NAV data as an external NAV adapter/cache source and separately notes source-contract work for non-annual-report evidence. | The data is available, but the evidence anchor is not an annual-report anchor. This is not an extractor gap for annual-report parsing; it is a score/report evidence contract issue for external NAV provenance. | Defer to source-contract/evidence-anchor hardening for external NAV data. Do not use it as a reason to modify annual-report extractor. |

## Track 1B closure

Track 1B status: `not_run_no_approved_candidates`.

The controller did not supply replacement candidates for index/QDII/FOF probing. Per the accepted plan and judgment, this worker did not browse, search, or select ad hoc replacement candidates. This track is independently closeable and has no command output.

## Scratch and tracked artifact policy

Tracked artifact:

- `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-20260527.md`

Scratch / generated evidence paths:

- `/tmp/fund-agent-baseline-coverage-triage-20260527/006597/`
- `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/`

Large CLI outputs remain in scratch/generated report paths. This tracked artifact records only summaries, classifications, and evidence paths.

## Next recommendation

Recommendation: `more evidence` before authorizing implementation.

Reasoning:

- The immediate quality gate block is real, but the blocked fields have mixed root causes.
- `share_change` has the strongest public evidence for a narrow extractor gap.
- `holdings_snapshot` points to a bond-lens contract gap rather than a straightforward missing extractor rule.
- `turnover_rate` and `holder_structure` remain `needs_more_evidence` under the no-direct-PDF constraint.
- `investor_return` and `nav_data` are score/evidence-contract issues, not current P1 bond extraction blockers.

If the controller chooses to proceed despite the residual evidence gap, the safest next plan should split work rather than authorize a big-bang fix:

- first, design/review a bond-lens evidence contract for `holdings_snapshot` and related quality-gate expectations;
- separately, plan a focused `share_change` ambiguity-handling implementation;
- keep `turnover_rate` and `holder_structure` evidence-only until an approved source can prove annual-report fact existence or accepted policy defines bond applicability.

Golden corpus v1 should not be entered from this state because Gate 4 clean coverage is still below target and the 006597 bond row remains quality-gate blocked.

## Blocker status

Execution blocker: none. The authorized public CLI commands completed.

Implementation blocker: yes, by design. The allowed evidence cannot prove annual-report fact existence for `turnover_rate` and `holder_structure`, and the current blocker mixes extractor, bond-lens contract, and score-contract concerns.

## Closeout validation

- `git diff --check`: pass, exit 0.
