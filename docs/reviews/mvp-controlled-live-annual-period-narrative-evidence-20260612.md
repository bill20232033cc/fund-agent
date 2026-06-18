# Controlled Live Annual-period Narrative Evidence

Date: 2026-06-12

Gate: `Controlled live annual-period narrative evidence execution gate`

Role: controller execution evidence

User live authorization: `授权live gate` on 2026-06-12

Accepted plan:

- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-plan-20260612.md`
- `docs/reviews/mvp-controlled-live-annual-period-narrative-evidence-plan-controller-judgment-20260612.md`
- Plan accepted at checkpoint `37ec1d8`
- Control sync before execution at checkpoint `385948a`

## 1. Verdict

**LIVE_COMMAND_SUCCEEDED_NOT_READY**

The single accepted live command for `004393 / 2021-2025` exited `0`.

The captured CLI output shows:

- `fund_code: 004393`
- `target_year: 2025`
- `canonical_years: 2025,2024,2023,2022,2021`
- `available_years: 2025,2024,2023,2022,2021`
- `gap_years`: empty / `none`
- `fail_closed_years`: empty / `none`
- `cross_year_fact_count: 3`
- `fallback_year_count: 0`
- five annual source lines with `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false`
- formal annual-period narrative/reporting headings were emitted before the embedded current-year report
- current-year report body headings `# 0` through `# 7` and `## 证据与出处` were present

This is bounded live evidence for one accepted sample only. It does not prove release/readiness, additional sample coverage, provider/LLM readiness, fixture/golden readiness, source-policy expansion or PR readiness.

Release/readiness remains `NOT_READY`.

## 2. Run Identity

| Field | Value |
|---|---|
| `run_id` | `fund-agent-controlled-live-annual-period-narrative-20260612-6iEWGI` |
| Temp capture directory | `/tmp/fund-agent-controlled-live-annual-period-narrative-20260612-6iEWGI` |
| CWD | `/Users/maomao/fund-agent` |
| Branch | `feat/mvp-llm-incomplete-run-artifacts` |
| HEAD before execution | `385948a` |
| Command | `uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh` |
| Exit code | `0` |
| Stdout capture | `/tmp/fund-agent-controlled-live-annual-period-narrative-20260612-6iEWGI/stdout.md` |
| Stderr capture | `/tmp/fund-agent-controlled-live-annual-period-narrative-20260612-6iEWGI/stderr.txt` |
| Stdout bytes | `46287` |
| Stderr bytes | `257` |

The stdout file contains the full generated report and is not promoted into the repository. This artifact records only metadata, section-presence checks and summarized evidence.

`--force-refresh` was used because the accepted plan required the controlled live run not to rely on stale local cache state.

## 3. E0 Status Preflight

| Check | Result |
|---|---|
| `git status --short` | Exit `0`; only pre-existing unrelated untracked residue was visible; no tracked source/test/runtime diff |
| `git status --branch --short` | Exit `0`; branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 189]`; only pre-existing unrelated untracked residue was visible |
| `git diff --name-only` | Exit `0`; no output |
| `git diff --check` | Exit `0`; no output |
| `git rev-parse --short HEAD` | Exit `0`; `385948a` |

The untracked residue was not used as proof and was not modified, deleted, moved, archived, staged or promoted.

## 4. E1 CLI Surface Preflight

Command:

```bash
uv run fund-analysis analyze-annual-period --help
```

Result: exit `0`.

Observed required options:

- `--target-year`
- `--start-year`
- `--valuation-state`
- `--quality-gate-policy`
- `--force-refresh`

## 5. E2 Controlled Live Run

Command:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

Result: exit `0`.

Output capture:

- stdout bytes: `46287`
- stderr bytes: `257`

Stderr quality summary:

- `quality_gate_status: warn`
- `quality_gate_issues: 3`

The quality gate policy was `warn` by accepted evidence-run design. This is acceptable for this live evidence gate and is not a readiness pass.

## 6. Metadata Extraction Method

The evidence check used only CLI metadata/header and heading/source-pattern extraction from the temporary stdout/stderr files:

- `sed -n '1,70p' stdout.md` was used to inspect the metadata header and first formal annual-period headings.
- `rg` extracted metadata fields: `fund_code`, `target_year`, `canonical_years`, `available_years`, `gap_years`, `fail_closed_years`, `cross_year_fact_count`, `fallback_year_count` and `source[YYYY]`.
- `rg -n "^(#|##|###) "` extracted heading presence without copying the full report body.
- A corrected negative `rg` keyword check searched for forbidden source/fallback tokens: `Eastmoney`, `eastmoney`, `CNINFO`, `cninfo`, `基金公司`, `fund-company`, `fund_company`, `fallback_used=true`, `fallback_enabled=true`.
- A source-field `rg` check listed all emitted `selected_source`, `source_mode`, `fallback_enabled` and `fallback_used` fields.

One discarded negative-check command used unsupported `rg` lookahead syntax and exited `2`; it was not used as evidence. The corrected negative keyword check exited `1`, meaning no forbidden keyword or true fallback token was matched.

Observed CLI metadata/source line patterns:

```text
fund_code: 004393
target_year: 2025
canonical_years: 2025,2024,2023,2022,2021
available_years: 2025,2024,2023,2022,2021
gap_years:
fail_closed_years:
cross_year_fact_count: 3
fallback_year_count: 0
source[2025]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2024]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2023]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2022]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
source[2021]: selected_source=eid source_mode=single_source_only fallback_enabled=false fallback_used=false
```

## 7. Year Table

| Year | Availability | Source evidence | Fallback evidence | Classification |
|---|---|---|---|---|
| 2025 | available | `selected_source=eid`; `source_mode=single_source_only` | `fallback_enabled=false`; `fallback_used=false` | accepted live sample evidence |
| 2024 | available | `selected_source=eid`; `source_mode=single_source_only` | `fallback_enabled=false`; `fallback_used=false` | accepted live sample evidence |
| 2023 | available | `selected_source=eid`; `source_mode=single_source_only` | `fallback_enabled=false`; `fallback_used=false` | accepted live sample evidence |
| 2022 | available | `selected_source=eid`; `source_mode=single_source_only` | `fallback_enabled=false`; `fallback_used=false` | accepted live sample evidence |
| 2021 | available | `selected_source=eid`; `source_mode=single_source_only` | `fallback_enabled=false`; `fallback_used=false` | accepted live sample evidence |

No per-year provenance was inferred beyond emitted source lines. All five years emitted source lines.

## 8. Source-policy Summary

| Check | Result |
|---|---|
| EID selected source for all available years | PASS |
| `source_mode=single_source_only` for all available years | PASS |
| `fallback_enabled=false` for all available years | PASS |
| `fallback_used=false` for all available years | PASS |
| `fallback_year_count=0` | PASS |
| `gap_years` empty / `none` | PASS |
| `fail_closed_years` empty / `none` | PASS |
| Forbidden source keyword check | PASS; corrected negative `rg` check found no `Eastmoney`, `CNINFO`, `基金公司`, fund-company token or true fallback token |

## 9. Narrative Section-presence Table

| Expected output surface | Observed heading / marker | Result |
|---|---|---|
| Annual-period report title | `# 多年年报分析（2021-2025）` | PASS |
| Annual coverage/source section | `## 年度覆盖与来源` | PASS |
| Cross-year key changes section | `## 跨年关键变化` | PASS |
| Impact-on-current-judgment section | `## 对当前判断的影响` | PASS |
| Gaps/degradation section | `## 缺口与降级` | PASS |
| Embedded target-year report section | `## 当前年份报告` and `<!-- current_year_report:start -->` | PASS |
| Current-year chapter 0 | `# 0. 投资要点概览` | PASS |
| Current-year chapter 1 | `# 1. 这只基金到底是什么产品` | PASS |
| Current-year chapter 2 | `# 2. R=A+B-C 收益归因` | PASS |
| Current-year chapter 3 | `# 3. 基金经理画像与言行一致性` | PASS |
| Current-year chapter 4 | `# 4. 投资者获得感` | PASS |
| Current-year chapter 5 | `# 5. 当前阶段与关键变化` | PASS |
| Current-year chapter 6 | `# 6. 核心风险与否决项` | PASS |
| Current-year chapter 7 | `# 7. 是否值得持有——最终判断` | PASS |
| Evidence appendix | `## 证据与出处` | PASS |

## 10. Negative-action Checklist

| Boundary | Result |
|---|---|
| Ran only the accepted single sample live command | PASS |
| Did not run provider/LLM/`--use-llm` commands | PASS |
| Did not run golden/readiness/release/PR commands | PASS |
| Did not reintroduce or invoke Eastmoney, fund-company/CDN or CNINFO fallback by command or source-policy change | PASS |
| Did not modify source/tests/runtime/README/design/control docs during execution | PASS |
| Did not stage, commit, push, PR, merge or mark ready during execution | PASS |
| Did not delete, move, archive, import, ignore or promote residue | PASS |
| Did not paste full generated report body, raw PDF text, raw downloaded document content or cache content into this durable artifact | PASS |

## 11. Residuals

| Residual | Classification | Owner | Next handling |
|---|---|---|---|
| `quality_gate_status=warn` and `quality_gate_issues=3` | material residual for readiness; non-blocking for this warn-policy live evidence gate | release/readiness owner | `Live evidence ready-state disposition gate` with explicit `NOT_READY` preservation |
| Single sample only (`004393 / 2021-2025`) | non-blocking residual for this gate; insufficient for broad release/readiness claim | release/evidence owner | additional EID live sample gate only if separately reviewed and authorized |
| Runtime emitted local quality-gate report paths under `reports/quality-gate-runs/` | artifact hygiene residual; not promoted as evidence here | artifact owner/controller | future artifact disposition or cleanup gate only by separate authorization |
| Provider/LLM path untested | deferred; out of scope | provider/runtime owner | live provider / LLM acceptance gate |
| Release/readiness still unproven | blocking residual for release; not a blocker for this evidence gate | release owner/controller | `Live evidence ready-state disposition gate` |

## 12. Acceptance Statement

The controlled live annual-period narrative execution evidence satisfies the accepted single-command matrix for this gate:

- live command succeeded with exit `0`
- five years were available
- EID single-source/no-fallback source lines were emitted for every available year
- `fallback_year_count=0`
- formal annual-period narrative/reporting sections were present
- current-year embedded report headings were present
- quality gate status was captured as `warn`
- no forbidden source/fallback keyword was observed by corrected negative check

Controller acceptance still requires DS and MiMo execution-evidence reviews, final controller judgment and `git diff --check`.

Release/readiness remains `NOT_READY`.
