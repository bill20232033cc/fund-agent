# Fixture Promotion State / Strict Golden 2025 Promotion Planning Gate Plan

Date: 2026-06-13

Gate: `Fixture promotion state / strict golden 2025 promotion planning gate`

Verdict: `PLAN_DRAFT_FOR_REVIEW`

## 1. Gate Question

This gate answers one planning question:

```text
After strict-golden preflight became fund/year-aware, what is the smallest
evidence-first route to handle `004393 / 2025` strict golden answer coverage
and fixture promotion state without editing golden answers, promotion state,
runtime behavior, or readiness/release state in this gate?
```

This gate is planning only. It does not produce or promote a strict golden
answer, does not create a fixture promotion state manifest, and does not claim
release readiness.

## 2. Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-strict-golden-2025-coverage-evidence-controller-judgment-20260612.md`
- `docs/reviews/mvp-strict-golden-year-aware-preflight-implementation-controller-judgment-20260612.md`
- `docs/reviews/release-maintenance-fixture-promotion-state-manifest-controller-judgment-20260529.md`
- `docs/reviews/release-maintenance-strict-golden-correctness-fixture-promotion-controller-judgment-20260529.md`
- `fund_agent/fund/golden_readiness_preflight.py`
- `fund_agent/fund/golden_answer.py`
- `fund_agent/config/paths.py`
- targeted test facts in `tests/fund/test_golden_answer.py` and `tests/fund/test_golden_readiness_preflight.py`

## 3. Fact Separation

### Repo Facts

- `reports/golden-answers/golden-answer.json` is tracked and is the default
  strict golden answer JSON path.
- Current `golden_answer.py` validates strict golden answer identity as
  `fund_code + report_year + field_name + sub_field`.
- Current `golden_answer.py` and tests allow the same fund code to have
  different `report_year` entries, while duplicate same-year field identities
  fail validation.
- Current Markdown-to-JSON build path still treats Markdown rows without an
  explicit year as the legacy 2024 corpus. Therefore a 2025 strict golden answer
  cannot be treated as reproducibly sourced from the current reviewed Markdown
  format unless a separate schema/build-tooling gate accepts how Markdown encodes
  `report_year`, or unless the controller explicitly accepts a JSON-only
  evidence route for 2025 rows.
- Current `golden_readiness_preflight.py` loads strict golden coverage as both
  fund-code coverage and `(fund_code, report_year)` coverage.
- Current `golden_readiness_preflight.py` emits
  `strict_golden_year_not_covered` when a fund exists in strict golden but the
  requested report year is absent.
- Current `golden_readiness_preflight.py` accepts a runtime
  `fixture_promotion_state_path` only if it contains either:
  - `entries[]` rows with `fund_code` and `promotion_state`; or
  - a direct `fund_code -> promotion_state` mapping.
- Current fixture promotion runtime map is fund-code-only:
  `dict[fund_code, PromotionState]`. It does not include `report_year`, and
  current `_derive_fixture_promotion_state()` resolves state by fund code only.
  Therefore current runtime schema cannot safely express "`004393 / 2025` only
  is promoted" while keeping "`004393 / 2024` not promoted".
- Valid current runtime promotion states are `not_promoted`,
  `promoted_fixture`, and `unknown`.
- Current preflight still fails closed as `fixture_promotion_absent` when no
  runtime-consumable fixture promotion state path is provided.

### Truth-doc Facts

- `docs/design.md` states strict golden answer comparison identity is
  `fund_code + report_year + field_name + sub_field`.
- `docs/design.md` states old strict golden JSON missing `report_year` is only
  compatible as the accepted 2024 corpus and must not be reused across years.
- `docs/design.md` states missing same-year golden coverage is
  `year_not_covered` and is retained by the quality gate as `FQ0/info`.
- `docs/current-startup-packet.md` and `docs/implementation-control.md` set the
  current active gate to this planning gate and preserve release/readiness as
  `NOT_READY`.

### Accepted Residuals

- `004393 / 2025` strict golden answer is not accepted as same-year coverage.
- Fixture promotion and strict golden 2025 accepted answer promotion remain
  unresolved.
- Release/readiness remains `NOT_READY`.
- Historical `docs/reviews/fixture-promotion-state-manifest-20260529.json` is
  accepted as a control-plane state description only. Its controller judgment
  says it is not a promotion manifest, did not execute golden promotion, did not
  modify golden fixtures, and was not runtime/preflight-consumed.

## 4. Rejected Routes

| Route | Disposition | Reason |
|---|---|---|
| Directly edit `reports/golden-answers/golden-answer.json` in this gate | REJECT | Planning gate does not authorize golden answer edits. |
| Open a 2025 strict golden answer write gate before deciding JSON-only vs Markdown/build-tooling authority | REJECT | Current Markdown build path is legacy-2024; writing both Markdown and JSON without a source-authority decision can make the JSON non-reproducible. |
| Directly create or modify fixture promotion state in this gate | REJECT | Planning gate does not authorize promotion state edits. |
| Treat historical 2025-unaware 2024 fixture decisions as 2025 readiness proof | REJECT | Strict golden identity is year-aware; 2024 evidence cannot prove 2025 coverage. |
| Treat `fixture-promotion-state-manifest-20260529.json` as runtime promotion approval | REJECT | Its own controller judgment says it is control-plane only and `promotion_allowed=false`. |
| Write `{"fund_code": "004393", "promotion_state": "promoted_fixture"}` under the current parser as 2025-specific promotion | REJECT | Current parser is fund-code-only and would promote the fund identity broadly, not just `004393 / 2025`. |
| Run live EID/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release | REJECT | Current gate is no-live planning only. |
| Claim readiness after resolving only strict golden year coverage | REJECT | Fixture promotion state and release/readiness residuals remain separate. |

## 5. Recommended Next Entry

Primary next entry:

```text
Strict golden 2025 answer evidence gate
```

Rationale:

The next blocker in the causal chain is not fixture promotion state itself. A
runtime-consumable promotion state would be meaningless unless the same-year
strict golden answer identity for `004393 / 2025` is first established or
explicitly rejected/deferred. Therefore the next gate must prove what 2025
golden-answer evidence exists, what is missing, and whether any future write to
strict golden answer JSON is justified.

## 6. Strict Golden 2025 Answer Evidence Gate

Classification: `standard`

Purpose:

1. Prove whether current tracked strict golden answer JSON contains
   `004393 / 2025`.
2. If absent, identify the exact same-year evidence requirement before any
   strict golden answer write can be authorized.
3. Decide whether 2025 strict golden answer authority is:
   - JSON-only accepted evidence for same-year rows; or
   - blocked pending a Markdown/schema/build-tooling gate that can encode
     `report_year` reproducibly.
4. Decide whether a later implementation gate may edit strict golden answer
   artifacts, or whether more evidence intake/tooling is required.
5. Preserve `NOT_READY`.

Allowed write set:

- `docs/reviews/mvp-strict-golden-2025-answer-evidence-20260613.md`
- two independent review artifacts under `docs/reviews/`
- controller judgment under `docs/reviews/`
- `docs/current-startup-packet.md` and `docs/implementation-control.md` after
  controller acceptance

Allowed commands:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
uv run pytest tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py -q
uv run ruff check fund_agent/fund/golden_answer.py fund_agent/fund/golden_readiness_preflight.py tests/fund/test_golden_answer.py tests/fund/test_golden_readiness_preflight.py
```

Allowed read-only checks:

- read `reports/golden-answers/golden-answer.json`;
- read `reports/golden-answers/golden-answer-prefill-reviewed.md`;
- run a read-only identity enumeration command that imports
  `load_golden_answer_json()` and prints only sorted `(fund_code, report_year)`
  identities plus record counts;
- read accepted small-golden/manual evidence artifacts only when the artifact is
  named in the evidence report with path, role, and limitation;
- compute local path size/hash for cited tracked artifacts.

Suggested read-only identity enumeration:

```bash
uv run python -c 'from pathlib import Path; from fund_agent.fund.golden_answer import load_golden_answer_json; funds=load_golden_answer_json(Path("reports/golden-answers/golden-answer.json")); print("\\n".join(f"{f.fund_code},{f.report_year},{len(f.records)}" for f in sorted(funds, key=lambda x: (x.fund_code, x.report_year))))'
```

The evidence artifact must paste the output and state explicitly whether
`004393,2025` is present. This command must not read PDF/cache, untracked report
residue, network, provider, or source acquisition paths.

Disallowed:

- writing golden answer JSON or reviewed Markdown;
- writing fixture promotion state;
- reading arbitrary untracked report residue as proof;
- live EID/network/PDF/FDR/provider/LLM/analyze/checklist/readiness/release/PR;
- source/test/runtime behavior changes;
- fallback/source expansion;
- cleanup, delete, move, archive, import, ignore, stage, commit, push, PR,
  merge, mark-ready.

Evidence questions:

| Question | Direct evidence | Acceptance signal |
|---|---|---|
| Does tracked strict golden answer contain `004393 / 2025`? | JSON loader output or deterministic read-only script using `load_golden_answer_json` | Exact list of `(fund_code, report_year)` identities includes or excludes `004393 / 2025`. |
| If absent, is absence currently expected? | Design/control docs plus previous controller judgments | Absence is classified as `accepted residual`, not extractor/runtime failure. |
| What is the authoritative upstream for 2025 strict golden rows? | `golden_answer.py` Markdown/build behavior, design truth and accepted evidence source limits | Evidence gate chooses `JSON-only accepted evidence`, or routes to Markdown/schema/build-tooling planning before any write. |
| What same-year evidence is required before write authorization? | Golden schema requirements and source limitations | Required rows must include field/sub_field/expected_value/confidence/source with same-year source provenance. |
| Can implementation start immediately after this evidence gate? | Evidence table | Only if same-year 2025 reviewed data exists and is named as accepted evidence; otherwise route to evidence intake. |

## 7. Conditional Follow-up Gates

### 7.1 Strict Golden 2025 Answer Implementation Gate

Open only if the evidence gate proves accepted same-year 2025 reviewed data
exists, decides the authoritative upstream for 2025 rows, and the controller
authorizes a write gate. If the evidence gate cannot accept a JSON-only route,
this implementation gate must not open until a Markdown/schema/build-tooling gate
is accepted.

Allowed future write set:

- `reports/golden-answers/golden-answer.json`
- `reports/golden-answers/golden-answer-prefill-reviewed.md` only if a prior
  evidence/controller judgment accepts how 2025 `report_year` is represented in
  Markdown and reproduced by the build path
- `tests/fund/test_golden_answer.py` only if schema/coverage assertions need a
  targeted 2025 row assertion
- `docs/reviews/` implementation evidence/review/controller artifacts
- control docs after acceptance

Non-goals:

- no fixture promotion state write;
- no runtime/source/test behavior change outside strict golden answer tests;
- no live/provider/LLM/readiness/release;
- no fallback/source expansion.

Acceptance criteria:

- strict JSON validates through `load_golden_answer_json`;
- `004393 / 2025` appears as a same-year identity;
- duplicate same-year identities are absent;
- any new expected values cite accepted same-year source evidence;
- JSON and reviewed Markdown authority do not diverge, or JSON-only authority is
  explicitly accepted by controller judgment with residuals;
- no readiness or promotion claim is made.

### 7.2 Markdown / Golden Answer Schema Build-tooling Planning Gate

Open this gate if the strict golden 2025 answer evidence gate rejects JSON-only
authority or determines that reviewed Markdown must remain the reproducible
upstream for strict golden answer JSON.

Purpose:

- decide how reviewed Markdown encodes `report_year`;
- decide whether `golden_answer.py` should parse year-bearing fund headings,
  table columns or an explicit metadata block;
- preserve legacy 2024 corpus compatibility without implying cross-year reuse;
- produce a later implementation plan for the build path before any 2025 golden
  answer write.

Allowed planning write set:

- one plan artifact under `docs/reviews/`
- two review artifacts under `docs/reviews/`
- one controller judgment under `docs/reviews/`
- control docs after acceptance

Non-goals:

- no golden answer JSON/Markdown edits;
- no source/test/runtime implementation in the planning gate;
- no fixture promotion state edit;
- no readiness/release claim.

### 7.3 Fixture Promotion State Evidence Gate

Open only after strict golden 2025 answer evidence is accepted, and preferably
after the 2025 strict golden answer implementation is accepted if same-year
coverage is required.

Purpose:

- Decide whether a new runtime-consumable fixture promotion state manifest is
  needed, because the historical 2025-05-29 manifest is control-plane only and
  not in current preflight input schema.
- Decide whether fixture promotion identity must be upgraded from
  fund-code-only to `(fund_code, report_year)` before any 2025-specific
  promotion can be represented.
- Decide exact schema and entries without writing the manifest.

Allowed future write set:

- evidence/review/controller artifacts under `docs/reviews/`
- control docs after acceptance

Disallowed:

- manifest write during evidence gate;
- promotion approval;
- readiness/release claim.
- use of `promoted_fixture` for `004393` under current fund-code-only parser as
  proof of `004393 / 2025`-specific promotion.

### 7.4 Fixture Promotion State Implementation Gate

Open only if the fixture promotion state evidence gate accepts a no-parser-change
path with explicit fund-code-only blocking semantics. This path cannot express
2025-specific promotion and must not use `promoted_fixture` for `004393` as a
2025-only state.

Allowed future write set for no-parser-change path:

- one exact new tracked fixture promotion state JSON manifest path fixed by the
  controller judgment before implementation starts, for example
  `docs/reviews/fixture-promotion-state-manifest-20260613.json`;
- exact implementation evidence/review/controller artifact paths under
  `docs/reviews/`;
- `docs/current-startup-packet.md` and `docs/implementation-control.md` after
  controller acceptance.

Disallowed in no-parser-change path:

- `fund_agent/fund/golden_readiness_preflight.py`;
- source/test/runtime behavior changes;
- `promoted_fixture` for `004393` as a 2025-specific state;
- readiness/release claim.

Acceptance criteria:

- manifest uses only current fund-code-only parser semantics;
- rows are explicit and valid;
- `not_promoted` / `unknown` continue to block;
- no `promoted_fixture` row is treated as year-specific;
- release/readiness remains `NOT_READY`.

### 7.5 Fixture Promotion State Schema / Parser Planning Gate

Open this gate instead of 7.4 if 2025-specific promotion must be represented.

Purpose:

- plan a year-aware fixture promotion identity, likely
  `(fund_code, report_year)`, to align with strict golden answer identity;
- define migration/compatibility semantics for existing fund-code-only manifests;
- decide whether the current parser should reject ambiguous 2025-specific
  promotion attempts.

Allowed planning write set:

- one plan artifact under `docs/reviews/`
- two review artifacts under `docs/reviews/`
- one controller judgment under `docs/reviews/`
- control docs after acceptance

Potential implementation write set after this separate plan is accepted:

- `fund_agent/fund/golden_readiness_preflight.py`
- `tests/fund/test_golden_readiness_preflight.py` only for targeted manifest
  parser/consumer coverage;
- `fund_agent/fund/README.md` only if public Fund preflight semantics change;
- `docs/reviews/` implementation evidence/review/controller artifacts;
- control docs after acceptance.

Implementation acceptance criteria:

- year-aware fixture promotion identity is explicit;
- legacy fund-code-only behavior is preserved, rejected, or migrated by an
  accepted rule;
- no row is silently promoted across years;
- `not_promoted` / `unknown` continue to block;
- `promoted_fixture` is used only when a separate promotion approval is accepted
  for the same identity by a named controller judgment path;
- preflight remains fail-closed for missing or unknown state;
- release/readiness remains `NOT_READY` unless a later release-readiness gate
  proves otherwise.

## 8. Validation Matrix For This Planning Gate

This planning gate validates docs hygiene only:

```bash
git status --short
git status --branch --short
git diff --name-only
git diff --check
```

No tests are required for this planning artifact because no source/test/runtime
behavior is changed.

## 9. Deferred Entries

- strict golden 2025 answer implementation gate
- fixture promotion state evidence gate
- fixture promotion state implementation gate
- strict golden 2025 promotion/preflight evidence closeout gate
- release-readiness rollup gate
- additional controlled-live sample evidence gate
- PR/release external-state gate
- provider/LLM readiness gate
- fallback/source expansion gate
- cleanup/ignore/archive gate

## 10. Completion Signal

This planning gate is complete only after:

- this plan is independently reviewed;
- controller judgment accepts/rejects reviewer findings;
- control docs are updated to set the next entry to
  `Strict golden 2025 answer evidence gate`;
- validation commands in section 8 pass.
