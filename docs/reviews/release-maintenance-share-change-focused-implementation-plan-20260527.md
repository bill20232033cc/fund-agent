# release-maintenance share_change focused implementation plan - 2026-05-27

## Startup Packet recap

- Phase: `release maintenance`.
- Current gate: `baseline coverage / source recovery / taxonomy + bond triage accepted locally`.
- Next entry point: `share_change focused implementation plan + bond-lens contract design choice plan/review`.
- Latest checkpoint supplied by controller: `cd176d0`.
- Current evidence judgment: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-controller-judgment-20260527.md`.

Truth sources for this plan are `AGENTS.md`, current `docs/design.md`, `docs/implementation-control.md` Startup Packet / Current gate / Next entry point, and accepted artifacts. `docs/reviews` is used only as the accepted evidence chain.

## Reconciliation

Baseline triage is accepted locally, but it is not sufficient for golden corpus v1. The accepted field classification is:

| Field | Accepted state | Planning consequence |
| --- | --- | --- |
| `share_change` | `extractor_gap` | Only field ready for a narrow implementation plan. |
| `holdings_snapshot` | `bond_lens_contract_gap` | Needs a future bond-lens evidence contract design gate before implementation. |
| `turnover_rate` | `needs_more_evidence` | No implementation authorized. |
| `holder_structure` | `needs_more_evidence` | No implementation authorized. |
| `investor_return` | `score_contract_gap` | Future score/fallback contract work only. |
| `nav_data` anchor status | `score_contract_gap` | Future external evidence provenance work only. |

The next minimal implementation slice should not try to make 006597 fully quality-gate clean. It should only reduce the confirmed `share_change` extractor gap without weakening quality rules or silently selecting a wrong share class.

## Root cause statement

Accepted evidence path:

- `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-20260527.md`
- Controller acceptance: `docs/reviews/release-maintenance-baseline-coverage-source-taxonomy-bond-triage-evidence-controller-judgment-20260527.md`
- Public CLI snapshot row: `reports/extraction-snapshots/baseline-coverage-triage-006597-2024/snapshot.jsonl`

Root cause:

- For `006597` / `2024`, the public snapshot records `share_change` as `extraction_mode="missing"`, `value_present=false`, `anchor_present=false`.
- The snapshot note is: `§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别`.
- Accepted controller judgment classifies this as `extractor_gap` and says it is the only field ready for a narrow implementation plan.

This is not a quality-gate threshold problem, not a golden-answer promotion problem, and not a source fallback problem. The implementation must improve deterministic share-class column selection or preserve explicit ambiguity when deterministic selection is not possible.

## Current ownership map

Observed ownership from current tracked code:

| Concern | Current file | Planning note |
| --- | --- | --- |
| §8/§10 holdings and share-change extraction | `fund_agent/fund/extractors/holdings_share_change.py` | Primary implementation scope. Current `_select_share_change_value_column()` handles exact fund-code header, single value column, and §2 A/C evidence; ambiguous multi-column tables return missing. |
| Snapshot field projection | `fund_agent/fund/extraction_snapshot.py` | Regression observation scope. Current comparable-value whitelist does not expose `share_change` subfields for correctness comparison, so 006597 golden share-change values appear as `unavailable` in score output. Do not change unless implementation plan review explicitly authorizes a snapshot-comparability extension. |
| Score and fund-quality aggregation | `fund_agent/fund/extraction_score.py` | Regression observation scope. `share_change` is P1 and missing values contribute to P1 failure and missing-field rate. No FQ weakening or priority change. |
| Quality gate | `fund_agent/fund/quality_gate.py` | Regression observation scope. FQ2/FQ2F/FQ4 behavior must remain intact. No threshold or severity changes. |
| Service/CLI | `fund_agent/services/*`, CLI modules | Out of scope. Public commands are used only for validation. |

## Recommended next authorization

Recommendation: authorize implementation next, but only for `share_change`.

Authorization boundary:

- Allowed production file:
  - `fund_agent/fund/extractors/holdings_share_change.py`
- Conditionally allowed production file only if plan review/controller explicitly accepts share-change correctness comparability:
  - `fund_agent/fund/extraction_snapshot.py`
- Allowed focused tests:
  - `tests/fund/extractors/test_holdings_share_change.py`
  - `tests/fund/test_extraction_snapshot.py` only if snapshot projection changes are authorized or if a regression fixture can be added without changing production snapshot contract.
  - `tests/fund/test_extraction_score.py` and `tests/fund/test_quality_gate.py` only for regression assertions that existing P1/FQ behavior is preserved.
- README sync:
  - No README update is expected for a private extractor ambiguity fix with no public command, architecture, or usage change.
  - If implementation changes documented Fund package behavior, update only `fund_agent/fund/README.md` in that future implementation gate.

Forbidden implementation files for this slice:

- Renderer, FQ0-FQ6 rule weakening, `fund_agent/services/*`, CLI defaults, Host/Agent/dayu integration, `FundDocumentRepository`, source fallback, production PDF/cache/source helpers, fixtures/golden corpus, package config, root README, durable baseline corpus files, GitHub state.

## Minimal behavior contract

For `006597` or any multi-share-class bond fund:

1. The extractor must choose a share-change value column only when there is deterministic evidence that the column corresponds to the requested `fund_code`.
2. Deterministic evidence may include:
   - exact current `fund_code` in the §10 value-column header;
   - same-source §2 subordinate fund name / trading-code table proving the current `fund_code` maps to a share-class label, followed by a unique matching §10 value-column header;
   - same-source §2 text proving the current `fund_code` maps to a share-class label, followed by a unique matching §10 value-column header.
3. If deterministic selection succeeds, output must remain an annual-report `ExtractedField` with:
   - `extraction_mode="direct"`;
   - non-empty `beginning_share`, `ending_share`, and computed or disclosed `net_change` when possible;
   - `share_class_column`;
   - `share_class_selection_reason`;
   - §10 table anchor.
4. If deterministic selection fails, the extractor must fail closed:
   - `extraction_mode="missing"`;
   - no anchor;
   - a note that explicitly distinguishes ambiguity from no table, for example current note `§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别`.
5. The implementation must not default to A class, first non-empty column, total-share column, or any column from a different fund code.
6. The implementation must not reduce P1 priority, FQ severity, or missing-field-rate behavior to make a run pass.

## Candidate implementation strategy

Use current extractor structure and extend it conservatively:

1. Add focused failing tests first for the 006597-shaped case using synthetic `ParsedAnnualReport` / `ParsedTable` objects, not production PDF/cache data.
2. Reproduce a multi-class bond share-change table where §10 has several value columns and §2 contains the current `fund_code` to share-class mapping.
3. Generalize existing share-class evidence from A/C-only matching if needed, while preserving current A/C tests:
   - keep exact `fund_code` header matching as highest priority;
   - only use §2 evidence when exactly one class label can be mapped to the current `fund_code`;
   - only select a §10 column when exactly one non-total column matches that class label;
   - return ambiguity if several columns match, no columns match, or any competing fund-code header appears.
4. Preserve existing split-table merge safeguards:
   - same-page adjacent or next-page continuation only;
   - table header/value column count must align;
   - no cross-table or non-adjacent inference.
5. Preserve annual-report repository boundary:
   - tests construct parsed report/table fixtures directly;
   - implementation does not call source helpers, cache paths, downloaders, or PDF parsers directly.

Do not implement broad bond analytics in this slice. The only intended production behavior change is safer §10 share-change column selection and clearer ambiguity preservation.

## Test strategy

Focused unit tests:

- Add / update tests in `tests/fund/extractors/test_holdings_share_change.py`:
  - selects the correct current-code share class when §2 maps a multi-share-class bond fund code to the corresponding §10 column;
  - preserves missing/ambiguity when §2 has no unique mapping;
  - preserves missing/ambiguity when §10 has multiple matching class columns;
  - rejects total-share columns when class-specific columns exist and current class cannot be proven;
  - rejects headers containing another fund code;
  - keeps existing exact fund-code, single-value, split-table, A/C, total-column, and fail-closed tests passing.

Snapshot / score / quality-gate regression:

- Run a bounded 006597 public CLI rerun after implementation:
  - `uv run fund-analysis extraction-snapshot --run-id share-change-focused-006597-2024 --fund-code 006597 --report-year 2024`
  - `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/share-change-focused-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/share-change-focused-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json`
  - `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/share-change-focused-006597-2024/score.json`
- Expected post-fix outcome:
  - `share_change` should be `direct` with an annual-report §10 anchor if deterministic evidence exists in current public extraction output.
  - If deterministic evidence still cannot be proven from public extraction output, `share_change` must remain `missing` with explicit ambiguity, and the slice stops as `needs_more_evidence` rather than guessing.
  - Quality gate may still be `block` because `turnover_rate`, `holder_structure`, and `holdings_snapshot` are intentionally out of scope.
  - No FQ threshold or severity change is acceptable.

Focused commands for implementation gate:

```bash
uv run pytest tests/fund/extractors/test_holdings_share_change.py
uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_holdings_share_change.py
uv run fund-analysis extraction-snapshot --run-id share-change-focused-006597-2024 --fund-code 006597 --report-year 2024
uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/share-change-focused-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/share-change-focused-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json
uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/share-change-focused-006597-2024/score.json
git diff --check
```

Full `uv run pytest` is required if the implementation touches:

- `fund_agent/fund/extraction_snapshot.py`;
- `fund_agent/fund/extraction_score.py`;
- `fund_agent/fund/quality_gate.py`;
- shared extractor models;
- document repository / parsed report models;
- any Service/CLI behavior, which should be avoided in this slice.

## Bond-lens contract design choice

Decision: do not implement `holdings_snapshot` in the `share_change` slice.

Reason:

- Accepted evidence classifies `holdings_snapshot` as `bond_lens_contract_gap`.
- Current `holdings_snapshot` semantics are equity-shaped: stock top holdings and industry distribution.
- Current design/template says `bond_fund` lens should prioritize duration, credit exposure, leverage, liquidity, drawdown, and redemption pressure.
- Changing `holdings_snapshot` for bond funds affects field applicability, snapshot comparability, score denominators, quality-gate interpretation, and template/report evidence contracts. That is larger than the share-change extractor gap.

Future design gate:

- Name: `bond-specific holdings/risk evidence contract plan/review`.
- Objective: decide whether `holdings_snapshot` remains equity-only with a bond-specific replacement field, or becomes a fund-type-dependent evidence slot with bond-risk subfields.
- Required design questions:
  - Which bond facts satisfy the Chapter 3/6 "actual investment behavior / core risk" contract: duration, credit rating mix, bond category mix, leverage, liquidity assets, concentration, drawdown, or other annual-report fields?
  - Which facts are P1 for `bond_fund`, and which are P2 or optional?
  - How should score and quality gate exclude equity-only `top_holdings_status` while preserving strictness for bond-specific risk facts?
  - How should annual-report anchors be represented for bond-risk facts?
  - What is the migration path for existing active/index `holdings_snapshot` tests?

Current `share_change` slice can ignore `holdings_snapshot` because it neither changes the accepted classification nor tries to clear the whole 006597 quality gate.

## Artifact policy

Tracked artifact for this planning task:

- `docs/reviews/release-maintenance-share-change-focused-implementation-plan-20260527.md`

Future implementation evidence should write only a concise tracked evidence artifact under `docs/reviews/`. Bulky public CLI outputs must stay under ignored scratch paths such as:

- `reports/extraction-snapshots/share-change-focused-006597-2024/`
- `/tmp/fund-agent-share-change-focused-20260527/`

No generated JSONL/score/gate output should be promoted as durable baseline, golden corpus, or fixture in this slice.

## Stop conditions

Stop and classify as `needs_more_evidence` or a separate design gate if any of the following occurs:

- The share-change fix requires direct production PDF reads, cache inspection, downloader/source-adapter/helper calls, or direct annual-report file parsing outside public repository/CLI paths.
- The deterministic column choice cannot be proven from parsed annual-report sections/tables already provided to the extractor.
- The fix requires source fallback or `FundDocumentRepository` semantic changes.
- The fix requires FQ0-FQ6 priority, threshold, severity, or default policy changes.
- The fix requires broad bond analytics, bond holdings/risk extraction, or redefining `holdings_snapshot`.
- The fix requires changing Service/CLI defaults, Host/Agent/dayu, renderer, package config, golden corpus, durable fixtures, or explicit-parameter passing through `extra_payload`.
- Public CLI rerun still reports `share_change` missing for 006597 and the note no longer identifies a deterministic next step.

## Verifier matrix

| Stage | Command / check | Required outcome |
| --- | --- | --- |
| Plan closeout | `git diff --check` | pass |
| Unit | `uv run pytest tests/fund/extractors/test_holdings_share_change.py` | pass |
| Focused regression | `uv run pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py` | pass if implementation affects snapshot/score/gate observations or if reviewers request regression proof |
| Lint | `uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_holdings_share_change.py` | pass |
| Public extraction smoke | `uv run fund-analysis extraction-snapshot --run-id share-change-focused-006597-2024 --fund-code 006597 --report-year 2024` | pass, no direct source/cache helper access |
| Public score smoke | `uv run fund-analysis extraction-score --snapshot-path reports/extraction-snapshots/share-change-focused-006597-2024/snapshot.jsonl --errors-path reports/extraction-snapshots/share-change-focused-006597-2024/errors.jsonl --golden-answer-path reports/golden-answers/golden-answer.json` | pass |
| Public gate smoke | `uv run fund-analysis quality-gate --score-path reports/extraction-snapshots/share-change-focused-006597-2024/score.json` | pass command execution; gate may still block for out-of-scope fields |
| Final hygiene | `git diff --check` | pass |

## Acceptance criteria

Implementation may be accepted only if:

- `share_change` deterministic selection behavior is covered by focused tests.
- Existing fail-closed ambiguity tests still pass.
- 006597 public rerun either:
  - produces direct `share_change` with §10 annual-report anchor and deterministic selection reason; or
  - preserves explicit missing/ambiguity with no wrong-column selection and records why implementation cannot safely choose.
- Quality gate strictness is unchanged; any remaining block is attributable to out-of-scope fields or missing public evidence.
- No forbidden modules, fallback semantics, FQ rules, golden corpus, durable fixtures, Service/CLI defaults, renderer, Host/Agent/dayu, package config, or GitHub state are mutated.
- `git diff --check` passes.

Golden corpus v1 remains ineligible until baseline coverage meets the representative target and 006597 has either a clean bond-quality path or an accepted bond-lens contract that explains remaining non-applicable fields.

## Non-goals

- No `turnover_rate` implementation.
- No `holder_structure` implementation.
- No `investor_return` fallback/projection work.
- No `nav_data` external evidence provenance work.
- No `holdings_snapshot` implementation in this slice.
- No renderer changes.
- No FQ0-FQ6 weakening.
- No Service/CLI default changes.
- No Host/Agent/dayu changes.
- No `FundDocumentRepository` or source fallback semantic changes.
- No direct PDF/cache/helper access.
- No golden corpus or durable fixture promotion.
- No explicit parameter tunneling through `extra_payload`.
- No commit, push, PR, or GitHub mutation.

## Blocker status

Planning blocker: none.

Implementation blocker: only if plan review rejects the narrow `share_change` authorization, or if implementation cannot prove deterministic selection from parsed report sections/tables without forbidden evidence access.
