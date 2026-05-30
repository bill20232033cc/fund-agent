# Index/QDII Source Recovery And Replacement Plan

> Date: 2026-05-27
> Worker: AgentCodex planning worker
> Gate: `index/QDII source recovery and replacement decision gate`
> Latest accepted checkpoint: `1a28919`
> Scope: plan artifact only. No evidence run, no implementation, no commit, no push, no PR.
> Output path: `docs/reviews/release-maintenance-index-qdii-source-recovery-replacement-plan-20260527.md`

## 1. Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate | `index/QDII source recovery and replacement decision gate` |
| Next entry point | plan/review/controller-judgment for repository-safe source recovery or replacement; evidence only after acceptance |
| Latest accepted checkpoint | `1a28919` |
| Truth sources | `AGENTS.md`; `docs/design.md` current design sections; `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point / Open Residuals; accepted artifacts |
| Accepted control input | baseline coverage recovery decision plan accepted locally; next safe gate is index/QDII source recovery and replacement, not durable baseline/golden preflight |
| Current architecture | `UI -> Service -> Host -> Agent`; deterministic production path remains UI -> Service -> `fund_agent/fund` |
| Annual-report boundary | production annual-report access must go through `FundDocumentRepository` or public Fund/CLI paths that use it internally |
| Source fallback contract | only `not_found` and `unavailable` may be fallback-eligible; `schema_drift`, `identity_mismatch`, and `integrity_error` fail closed |

Allowed in this planning gate:

- Create only this plan artifact under `docs/reviews/`.
- Read `AGENTS.md`, current design/control truth, and accepted review artifacts.
- Run read-only validation commands such as `rg`, `sed`, `git status --short`, `git rev-parse --short HEAD`, and `git diff --check`.
- Define the next evidence gate shape, stop conditions, candidate rules, allowed commands, output policy, and review checklist.

Forbidden in this planning gate:

- No evidence run, production extraction run, source recovery probe, replacement probe, implementation, tests, README sync, commit, push, PR, or GitHub mutation.
- No edits outside this artifact. In particular, do not edit `docs/design.md` or `docs/implementation-control.md`.
- No renderer, FQ0-FQ6, Service, CLI, Host, Agent, Dayu, source strategy, source helper, extractor, `fund_type.py`, golden fixture, or baseline fixture changes.
- No direct PDF/cache/source-helper/downloader access and no bypass of `FundDocumentRepository`.
- No ad hoc web/search candidate discovery.

Verifier matrix for this artifact:

| Check | Command | Expected |
|---|---|---|
| Checkpoint sanity | `git rev-parse --short HEAD` | `1a28919` for this handoff |
| Artifact exists | `test -f docs/reviews/release-maintenance-index-qdii-source-recovery-replacement-plan-20260527.md` | pass |
| Whitespace | `git diff --check` | pass |
| Scope | `git diff --name-only` | only this new plan artifact should be attributable to this task; unrelated pre-existing untracked files remain untouched |

## 2. Current Blockers

Accepted small-baseline and recovery-decision artifacts keep `110020` and `017641` visible but outside the clean denominator:

| Candidate | Slot | Current status | Why it cannot enter clean denominator |
|---|---|---|---|
| `110020` / 2024 | `index_fund` | `fallback_blocked`; accepted evidence says repository identity exists but `fallback_used=True` and original upstream failure category is unknown | Eastmoney fallback may mask `schema_drift`, `identity_mismatch`, or `integrity_error`; without original category, fallback eligibility is unproven |
| `017641` / 2024 | `qdii_fund` | `fallback_blocked`; accepted evidence says repository identity exists but `fallback_used=True` and original upstream failure category is unknown | fallback can hide unsafe source-contract failure; QDII facts cannot be counted as source-safe while the upstream boundary is unknown |

Consequences:

- Both rows remain excluded from clean representative coverage.
- Neither row is `scoring_ready`, `accepted_baseline`, or golden material.
- Their current source state is not equivalent to `repository_verified clean`; it is only visible planning evidence with an unresolved fallback boundary.
- Missing index/QDII coverage remains a dominant blocker for durable baseline/golden gates.

## 3. Next Evidence Gate Shape

The next gate must be evidence-gated, but evidence must not run until this plan passes MiMo review, GLM review, and controller judgment.

### 3.1 Subgate A: Recover Original Upstream Failure Category

Question: can the current public repository-backed path expose the original upstream failure category for `110020` / 2024 and `017641` / 2024 without direct source-helper, PDF, cache, or downloader access?

Procedure for a later accepted evidence worker:

1. Run public CLI extraction only after controller authorization.
2. Inspect only public CLI outputs, generated snapshot/error/summary artifacts, and quality-gate summaries.
3. Classify each candidate into exactly one state:
   - `recovered_eligible`: original upstream category is `not_found` or `unavailable`; fallback is allowed by contract.
   - `recovered_fail_closed`: original upstream category is `schema_drift`, `identity_mismatch`, or `integrity_error`; fallback must remain blocked.
   - `unrecoverable_safe_path`: public repository-backed output does not expose the original category; no direct helper/PDF/cache access is allowed.
   - `repository_run_failed`: public CLI cannot complete and the failure is recorded with exit status and stderr summary only.
4. Do not infer root cause from indirect symptoms such as later extraction gaps, missing fields, or successful fallback content.

Acceptance for current rows:

- `110020` or `017641` may become source-safe only if Subgate A produces `recovered_eligible` with the original category and supporting public-output path.
- `recovered_fail_closed`, `unrecoverable_safe_path`, and `repository_run_failed` all keep the row outside the clean denominator.

### 3.2 Subgate B: Exclude Or Replace

If Subgate A cannot recover an eligible category for a row, the evidence gate must exclude that row or evaluate an approved replacement candidate.

Replacement candidate rules:

- Source of candidate must be either controller-supplied or derived from already accepted artifacts.
- No planning or evidence worker may browse, search, scrape, or select ad hoc replacement candidates.
- Candidate must be `repository_verified` through public Fund/CLI paths.
- Candidate must match the slot exactly:
  - index replacement must classify as `index_fund`;
  - QDII replacement must classify as `qdii_fund`.
- Candidate must have no `unknown`, `probe_only`, or fallback-unknown source boundary.
- Candidate must not depend on QDII-FOF taxonomy assumptions or pure FOF slot counting.
- Candidate must not carry known `baseline_blocking=true` issues into a durable baseline/golden recommendation.

If no approved candidate exists:

- Close replacement probing as `not_run_no_approved_candidates`.
- Keep `110020` and/or `017641` excluded with explicit reasons.
- Stop the gate without ad hoc web/search.

Terminal state `excluded` means the row is intentionally kept outside the clean denominator after Subgate A/B analysis, with a recorded reason such as fail-closed category, unrecoverable safe path, repository run failure, or no approved replacement.

## 4. Allowed Commands And Output Policy For Later Evidence

The commands below are allowed only in a later accepted evidence gate. They are not lightweight read-only checks: they trigger repository access through the public Fund/CLI path and may produce extraction, score, and quality-gate artifacts.

| Purpose | Command shape | Output policy |
|---|---|---|
| Repository-backed snapshot | `uv run fund-analysis extraction-snapshot --run-id index-qdii-source-<code>-2024 --fund-code <code> --report-year 2024` | scratch or ignored `reports/extraction-snapshots/...` only |
| Score produced snapshot | `uv run fund-analysis extraction-score --snapshot-path <snapshot.jsonl> --errors-path <errors.jsonl> --golden-answer-path reports/golden-answers/golden-answer.json` | scratch/ignored score JSON and Markdown only; no golden modification |
| Quality gate produced score | `uv run fund-analysis quality-gate --score-path <score.json>` | scratch/ignored quality-gate JSON/Markdown only |
| Closeout validation | `git diff --check` | required before closeout |

Output rules:

- Large outputs, stdout/stderr, snapshots, errors, scores, golden sets, quality-gate JSON/Markdown, and downloaded/cache artifacts must stay in `/tmp/...` or ignored `reports/...`.
- The only tracked artifact from an evidence gate should be a concise `docs/reviews/` summary containing command status, candidate state, source category if recovered, issue ids, and scratch paths.
- Do not commit PDF/cache/source dumps, generated snapshots, score JSON, quality-gate JSON, golden files, baseline fixtures, or large reports.

## 5. Stop Conditions

Stop immediately and return a blocked/excluded state if any condition occurs:

- Recovering the original upstream failure category requires direct PDF/cache/source-helper/downloader access.
- The recovered category is `schema_drift`, `identity_mismatch`, or `integrity_error`.
- The original fallback category remains unknown after public repository-backed evidence.
- A candidate's document identity, report year, fund code, or report type mismatches requested inputs.
- A replacement candidate is not controller-approved or accepted-artifact-derived.
- A replacement candidate is not `repository_verified`.
- A replacement candidate does not exactly match the required `fund_type_slot`.
- A candidate has `unknown`, `probe_only`, or fallback-unknown source boundary.
- Evidence requires changing source strategy, source helpers, `FundDocumentRepository`, extractor logic, `fund_type.py`, renderer, FQ0-FQ6, Service/CLI, Host/Agent, Dayu, golden fixtures, or baseline fixtures.
- Large generated outputs are about to be tracked.
- The gate is pressured to enter durable baseline/golden promotion before index/QDII source safety is resolved.

## 6. Verification And Review Matrix

Evidence gate validation matrix:

| Area | Required validation | Pass condition |
|---|---|---|
| Startup replay | checkpoint, gate, allowed/forbidden surfaces restated | no mismatch with control doc next entry and this plan |
| Source recovery | public CLI evidence only | original category recovered or explicit `unrecoverable_safe_path` recorded |
| Fallback taxonomy | category mapped to eligibility | only `not_found` / `unavailable` can permit fallback |
| Replacement | candidate provenance and slot exactness | controller-supplied or accepted-derived; `repository_verified`; exact fund type |
| Output policy | tracked vs scratch separation | tracked artifact contains summary/path only |
| Baseline/golden exclusion | no fixture promotion | excluded rows remain outside clean denominator |
| Closeout | `git diff --check` | pass |

Review matrix:

| Reviewer | Focus |
|---|---|
| AgentMiMo | product-methodology safety, clean-denominator discipline, source/fallback false-positive risk, index/QDII representative coverage |
| AgentGLM | repository boundary, failure taxonomy precision, command/output discipline, no indirect evidence, no hidden implementation scope |
| Controller | accept/reject/defer findings, decide whether to authorize evidence run, and record next residual owner |

Required closeout after a later evidence run:

- A tracked closeout artifact under `docs/reviews/` is required.
- The closeout must state per candidate: `recovered_eligible`, `recovered_fail_closed`, `unrecoverable_safe_path`, `repository_run_failed`, `excluded`, `replacement_verified`, or `not_run_no_approved_candidates`.
- The closeout must explicitly answer whether another evidence run is needed. If no approved replacement exists or public outputs cannot recover the upstream category, the correct next state is stop/exclude, not repeated probing.
- MiMo review, GLM review, and controller judgment are required before any next gate can treat a recovered/replaced candidate as clean evidence.

## 7. Hard Prohibitions

This plan does not authorize any of the following:

- renderer changes;
- FQ0-FQ6 quality-gate changes;
- Service or CLI behavior changes;
- Host/Agent package creation or Dayu runtime work;
- source strategy, source helpers, downloader, PDF cache, or `FundDocumentRepository` implementation changes;
- extractor logic changes;
- `fund_type.py` changes;
- golden fixture or baseline fixture changes;
- direct PDF/cache/source-helper reads;
- bypassing `FundDocumentRepository`;
- GitHub mutation of any kind.

## 8. MiMo / GLM Review Checklist

- Does the plan replay phase/gate/next/checkpoint and truth hierarchy correctly?
- Does it keep `110020` and `017641` outside the clean denominator while fallback category is unknown?
- Does it require original upstream failure-category recovery before allowing fallback-based evidence?
- Does it fail closed for `schema_drift`, `identity_mismatch`, and `integrity_error`?
- Does it prohibit direct PDF/cache/source-helper/downloader access?
- Does it treat `extraction-snapshot`, `extraction-score`, and `quality-gate` as real repository/product-path evidence commands, not lightweight read-only probes?
- Does it require replacement candidates to be controller-supplied or accepted-artifact-derived?
- Does it require `repository_verified`, exact `fund_type_slot`, and no unknown fallback boundary for replacements?
- Does it stop when there are no approved candidates, instead of doing ad hoc web/search?
- Does it keep outputs in scratch/ignored paths and tracked artifacts to summaries/paths only?
- Does it prevent renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu/source/extractor/fund-type/golden/baseline scope creep?
- Does it require a later evidence closeout artifact plus MiMo/GLM review and controller judgment?

## 9. Validation For This Artifact

This artifact is planning-only. It was created after reading the Startup Packet / Next Entry Point / Open Residuals, the baseline recovery controller judgment, accepted small-baseline and baseline coverage artifacts, and current design boundary references. No evidence run, source code, tests, README, design doc, control doc, fixture, commit, push, PR, or GitHub mutation is part of this artifact.
