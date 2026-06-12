# Controller Judgment: Quality Warning Issue Identity Evidence Gate

Date: 2026-06-12

Role: controller

Gate: `Quality warning issue identity evidence gate`

Classification: `standard`

Evidence artifact:

- `docs/reviews/mvp-quality-warning-issue-identity-evidence-20260612.md`

Independent reviews:

- `docs/reviews/mvp-quality-warning-issue-identity-evidence-review-mimo-20260612.md`
- `docs/reviews/mvp-quality-warning-issue-identity-evidence-review-meitner-20260612.md`

Accepted input:

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-quality-warning-issue-root-cause-plan-controller-judgment-20260612.md`
- checkpoint `56c71d9`
- control-sync checkpoint `2c973c9`
- user live authorization for this gate

## 1. Verdict

**ACCEPT_WITH_RESIDUALS_NOT_READY**

The evidence artifact is accepted.

Accepted issue identities:

| # | Rule | Severity | Fund | Field | Reason / scope | Controller disposition |
|---:|---|---|---|---|---|---|
| 1 | `FQ2` | `warn` | `None` | `turnover_rate` | P1 field coverage/traceability failure | ACCEPT as actionable warning identity |
| 2 | `FQ2F` | `warn` | `004393` | `None` | fund-level P1 aggregate derived from `turnover_rate` | ACCEPT as derivative warning identity |
| 3 | `FQ0` | `info` | `004393` | `None` | `year_not_covered` / `year_not_covered` | ACCEPT as golden/readiness coverage residual, not extractor failure |

Release/readiness remains **`NOT_READY`**.

This gate does not implement any source/test/runtime fix and does not authorize PR, push, merge, mark-ready, release, cleanup, fallback/source expansion, provider/LLM, additional live samples, golden promotion or readiness claim.

## 2. Evidence Basis

Accepted evidence facts:

- E1 no-live lineage check could only establish `quality_gate_status=warn` and `quality_gate_issues=3`; it could not establish issue rows or path+hash+size/run identity.
- Path-exists-only use of pre-existing mutable `reports/` residue remains rejected.
- User-authorized E3 one-command live reproduction ran once and exited `0`.
- The live command emitted `quality_gate_status=warn`, `quality_gate_issues=3`, `quality_gate_json=reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.json` and `quality_gate_md=reports/quality-gate-runs/analyze-004393-2025-20260612T090735116031Z/quality_gate.md`.
- The current-gate `quality_gate.json`, `quality_gate.md`, `score.json` and `snapshot.jsonl` paths were captured with size and SHA-256 lineage.
- `score.json` establishes `turnover_rate` as P1 fail with zero coverage and zero traceability, `004393` as P1 fail because `p1_failed_fields=["turnover_rate"]`, and correctness as `coverage_reason=year_not_covered`.
- Static code/test mapping confirms current semantics: P1 field failure produces `FQ2/warn`, P1 fund failure produces `FQ2F/warn`, and `year_not_covered` correctness coverage produces `FQ0/info`.

Evidence hygiene residual accepted:

- stdout/stderr captures were recorded by temp path and size, but not SHA-256 hashed. This does not block this gate because accepted issue identities rest on hashed `quality_gate.json` and `score.json`; future live evidence gates should hash stdout/stderr captures as well.

## 3. Review Finding Disposition

| Finding | Source | Controller disposition | Reason |
|---|---|---|---|
| Issue identities are sufficiently supported | MiMo, Meitner | ACCEPT | Current-gate artifact lineage plus score summary and static rule mapping directly support the three issue identities |
| Path-exists-only residue rejection is correct | MiMo, Meitner | ACCEPT | Matches accepted root-cause planning judgment and AGENTS/control truth constraints |
| `NOT_READY` preserved | MiMo, Meitner | ACCEPT | Evidence artifact does not claim readiness or broader sample/provider/release proof |
| Next mainline should be turnover-rate extraction/traceability root-cause planning | MiMo, Meitner | ACCEPT | The two warn issues share the same actionable `turnover_rate` P1 failure; root-cause planning must precede implementation |
| Strict golden 2025 coverage/promotion should be deferred | MiMo, Meitner | ACCEPT | `FQ0/info year_not_covered` is a golden/readiness coverage residual, not an extractor failure |
| Static code mapping line numbers are approximate | MiMo | ACCEPT_AS_INFO | The cited ranges point to the correct functions/branches and are sufficient for traceability |
| stdout/stderr captures lack SHA-256 hashes | Meitner | ACCEPT_AS_LOW_RESIDUAL | Does not block issue identity acceptance; record as future evidence hygiene improvement |
| DS pane was not usable for this review | Controller | ACCEPT_AS_REVIEW_CHANNEL_RESIDUAL | `AgentDS` pane failed clear verification twice and retained prior task/queued `/clear` residue; no current review task was sent to DS |

## 4. Accepted / Rejected / Deferred

| Item | Disposition | Basis |
|---|---|---|
| Accept `FQ2/warn turnover_rate` issue identity | ACCEPT | current-gate `quality_gate.json` issue row and `score.json` P1 `turnover_rate` fail row |
| Accept `FQ2F/warn 004393` issue identity | ACCEPT | current-gate `quality_gate.json` issue row and `score.json` `p1_failed_fields=["turnover_rate"]` |
| Accept `FQ0/info year_not_covered` issue identity | ACCEPT | current-gate `quality_gate.json` issue row and correctness summary |
| Treat `FQ2F` as separate root cause | REJECT | It is an aggregate derivative of the same P1 `turnover_rate` failure |
| Treat `FQ0/info year_not_covered` as extractor failure | REJECT | It is a strict golden current-year coverage residual |
| Use arbitrary pre-existing `reports/` residue as proof | REJECT | Mutable residue without accepted lineage remains non-proof |
| Claim release/readiness pass | REJECT | `quality_gate_status=warn` and unresolved warning/golden residuals keep readiness `NOT_READY` |
| Implement turnover-rate fix in this gate | REJECT | This was evidence-only |
| Additional live sample coverage | DEFER | Separate controlled live sample gate |
| Strict golden 2025 coverage/promotion | DEFER | Separate golden/readiness planning gate |
| Provider/LLM acceptance | DEFER | Separate provider/LLM gate |
| Cleanup/delete/archive/import/ignore | DEFER | Separate artifact-action gate |
| PR/push/merge/mark-ready/release | DEFER | Separate external-state gate |

## 5. Residuals

| Residual | Owner | Blocks readiness? | Next handling |
|---|---|---|---|
| `turnover_rate` P1 coverage/traceability failure | Fund extractor / traceability owner | Yes | `Turnover rate extraction/traceability root-cause planning gate` |
| `FQ2F` aggregate warning for `004393` | Quality gate + Fund extractor owner | Yes, until underlying P1 failure is dispositioned | Same next gate |
| `FQ0/info year_not_covered` | golden/readiness owner | Yes for readiness/promotion | Deferred `Strict golden 2025 coverage/promotion planning gate` |
| stdout/stderr capture hashes absent | controller/evidence owner | No for this gate | Future live evidence hygiene |
| DS pane clear failure | agent setup/controller | No for issue identity acceptance; affects review-channel robustness | Future agent-channel cleanup before DS handoff |
| broader live sample coverage not proven | release/evidence owner | Yes for broader readiness | separate controlled live sample gate |
| provider/LLM readiness not proven | provider/runtime owner | Yes for LLM readiness | separate provider/LLM gate |

## 6. Verification

| Command | Result |
|---|---|
| `git status --short` | Exit `0`; existing unrelated untracked residue plus current gate artifacts |
| `git status --branch --short` | Exit `0`; branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 199]`; existing unrelated untracked residue plus current gate artifacts |
| `git diff --name-only` | Exit `0`; current gate tracked doc changes only after adding artifacts/control sync |
| `git diff --check` | Exit `0`; no whitespace errors at artifact write checkpoint |

Live command run in this gate:

```bash
uv run fund-analysis analyze-annual-period 004393 --target-year 2025 --start-year 2021 --valuation-state unavailable --quality-gate-policy warn --force-refresh
```

No additional live/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release/PR command was run beyond the accepted one-command live reproduction. No source/test/runtime behavior file was modified.

## 7. Next Entry

Accepted next mainline:

`Turnover rate extraction/traceability root-cause planning gate`

Purpose:

- determine why `turnover_rate` has zero coverage and zero traceability for the current live sample
- separate extractor capability gap, source disclosure absence, mapping/anchor loss, and quality-score interpretation
- produce a code-generation-ready plan before any implementation/fix

Deferred entries:

- `Strict golden 2025 coverage/promotion planning gate`
- additional controlled live sample gate
- provider/LLM readiness gate
- cleanup/delete/archive/import/ignore gate
- PR/push/merge/mark-ready/release external-state gate

## 8. Final State

`Quality warning issue identity evidence gate` is accepted with residuals.

Release/readiness remains **`NOT_READY`**.
