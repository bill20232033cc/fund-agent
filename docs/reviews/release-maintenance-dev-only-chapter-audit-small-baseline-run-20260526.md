# Dev-only Chapter Audit x Small Baseline Run

> Date: 2026-05-26
> Worker: Gate B evidence worker
> Gate: dev-only chapter audit x small baseline corpus evaluation
> Verdict: RUN_READY_WITH_RENDERER_ESCALATION_BLOCKER

## Scope

This run executed the dev-only report-writing audit over manually assembled
`ReportEvidenceBundle` and `ChapterDraftSurrogate` inputs. It did not call
`fund-analysis analyze`, `fund-analysis checklist`, renderer, FQ0-FQ6, Service/CLI,
Host/Agent/dayu, `FundDocumentRepository`, PDF/cache/source helpers, downloaders, or
production extractors.

Large JSON/JSONL evidence was written only to scratch:

```text
/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/
```

Tracked output is limited to this summary.

## Inputs

Read before running:

- `docs/reviews/release-maintenance-dev-only-chapter-audit-small-baseline-readiness-20260526.md`
- `docs/reviews/release-maintenance-chapter-contract-sidecar-audit-implementation-controller-judgment-20260526.md`
- `fund_agent/fund/report_writing_audit.py`
- `fund_agent/fund/template/chapter_contract_constraints.py`
- `docs/reviews/release-maintenance-small-baseline-corpus-candidate-selection-20260526.md`
- `docs/reviews/release-maintenance-small-baseline-real-evaluation-run-20260526.md`

Clean denominator:

- `004393` / 2024 / `active_fund`
- `004194` / 2024 / `enhanced_index`
- `006597` / 2024 / `bond_fund`

Excluded residual rows:

- `110020` / 2024 / `index_fund`: fallback-blocked by `unknown_upstream_failure_category`.
- `017641` / 2024 / `qdii_fund`: fallback-blocked by `unknown_upstream_failure_category`.
- `007721` / 2024 / FOF attempt: `data_gap` / taxonomy pending; QDII-FOF evidence does not fulfill pure FOF.
- `017970` / 2024 / FOF attempt: `data_gap` / taxonomy pending plus fallback-blocked source status.

No candidate is promoted to durable baseline, `scoring_ready`, or accepted fixture.

## Run Summary

| fund_code | report_year | fund_type_slot | audited chapters | material audit executed | issue count | issue taxonomy | false-positive suspicion | required next action | scratch evidence path |
|---|---:|---|---|---|---:|---|---|---|---|
| `004393` | 2024 | `active_fund` | Chapter 3 | yes | 0 | none | low | No immediate fix; positive control for active Chapter 3 material contract. | `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/004393-active-ch3-valid-reviewed-turnover.json` |
| `004393` | 2024 | `active_fund` | Chapter 3 | yes | 2 | `required_evidence_missing=1`, `unsupported_stability_claim=1` | low | Renderer integration design must suppress unsupported stability/style-consistency claims unless reviewed turnover/style evidence exists. | `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/004393-active-ch3-missing-evidence-stability-claim.json` |
| `004393` | 2024 | `active_fund` | Chapter 3 | yes | 0 | none | low with currently supported next-question wording | Renderer integration design may allow insufficient-evidence wording with next minimum validation question. | `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/004393-active-ch3-compatible-datagap-insufficient-wording.json` |
| `004393` | 2024 | `active_fund` | Chapter 3 | yes | 1 | `insufficient_evidence_wording_missing=1` | low | Renderer integration design must preserve required `data_gap` wording; missing wording remains material. | `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/004393-active-ch3-compatible-datagap-missing-wording.json` |
| `004393` | 2024 | `active_fund` | Chapter 3 | yes | 1 | `unsupported_stability_claim=1` | medium; deterministic phrase matcher window is narrow for coordinated question wording | Before renderer integration, either constrain renderer wording to the accepted shape or tune phrase matcher to recognize this question form as non-positive. | `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/004393-active-ch3-compatible-datagap-wording-false-positive-probe.json` |
| `004194` | 2024 | `enhanced_index` | Chapter 2 | no | 0 | none | none; zero issues expected because requirement is deferred `config_only` | Do not treat as tracking-error audit; future chapter coverage or extraction gate is needed before material Chapter 2 enforcement. | `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/004194-enhanced-index-ch2-config-only-visibility.json` |
| `006597` | 2024 | `bond_fund` | Chapter 6 | no | 0 | none | none; zero issues expected because requirement is deferred `config_only` | Do not treat as bond risk facts audit; future chapter coverage or extraction gate is needed before material Chapter 6 enforcement. | `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/006597-bond-ch6-config-only-visibility.json` |

The run covers three `fund_type_slot` values: `active_fund`, `enhanced_index`, and
`bond_fund`. Only `active_fund` Chapter 3 is materially enforced by the current
audit. Chapter 2 enhanced-index and Chapter 6 bond-fund checks prove sidecar visibility
only; they do not prove tracking-error or bond-risk fact auditing.

## Seven-Category Taxonomy

| Category | Evidence samples | Immediate fix? | More evidence needed? | Blocks renderer minimal integration? |
|---|---|---|---|---|
| data/source extraction | `004194` Chapter 2 and `006597` Chapter 6 are config-only; `110020` and `017641` remain fallback-blocked. | no for this Gate B worker | yes before durable baseline or broader chapter enforcement | no for active-only renderer design; yes for broader renderer claims |
| evidence traceability | `004393` reviewed turnover positive control passes only with resolvable anchor; scratch positive control path listed above. | no | no for active Chapter 3 slice | no |
| chapter contract too strict | False-positive probe: coordinated wording `风格稳定性和言行一致性判断是否仍成立？` triggers `unsupported_stability_claim`. | yes before default renderer integration, or constrain renderer wording to accepted shape | no; scratch reproduces it | yes for direct renderer integration without a wording/tuning decision |
| chapter contract too loose | None observed in this run. Active missing evidence and missing wording both produced material issues. | no | yes with more chapter/fund types | no |
| report writing/template gap | Active Chapter 3 needs deterministic wording: either reviewed turnover/style evidence or explicit insufficient-evidence + next minimum validation question. | likely yes in renderer design, not in this worker | no for active Chapter 3 | yes unless scoped to design only |
| validator schema issue | None from `audit_report_writing_bundle`; prior combined JSONL validator limitation remains outside this audit run. | no | yes if future tooling uses combined multi-bundle JSONL | no for this dev-only audit API |
| fund-type taxonomy issue | FOF attempts `007721` / `017970` remain QDII-FOF/type-gap residuals; not in clean denominator. | no in this gate | yes before durable baseline coverage | no for active-only renderer design; yes for corpus expansion |

## Renderer Minimal Integration Decision

This Gate B evidence does not yet prove readiness for renderer minimal integration.

Blocker:

- The active Chapter 3 audit is effective on the required positive/negative controls,
  but the false-positive probe shows the phrase matcher can classify a legitimate
  next-minimum-validation question as an unsupported positive stability claim when the
  wording coordinates `风格稳定性` and `言行一致性`.

Allowed next decisions:

- `contract tuning implementation`: tune the deterministic phrase matcher or constrain the
  allowed renderer wording shape before any default renderer integration.
- `renderer minimal integration design`: only if explicitly scoped as design-only and it
  carries the above blocker forward as a prerequisite before implementation.
- `more chapter coverage`: needed before enhanced-index Chapter 2 or bond Chapter 6 can be
  treated as material audit evidence.

Do not enter product-flow integration, FQ0-FQ6 change, durable baseline fixture promotion,
Host/Agent/dayu work, or default `analyze/checklist` changes based on this run.

## Scratch Files

Key files:

- `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/manifest.json`
- `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/audit-results.jsonl`
- `/tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526/sidecar-constraints-summary.json`
- one JSON file per variant listed in the run summary table.

## Validation

Commands run:

```text
uv run python - <<'PY'
from fund_agent.fund.report_writing_audit import audit_report_writing_bundle
from fund_agent.fund.template.chapter_contract_constraints import constraints_for_chapter
print(audit_report_writing_bundle)
print(len(constraints_for_chapter(3, "active_fund")))
print(len(constraints_for_chapter(2, "enhanced_index")))
print(len(constraints_for_chapter(6, "bond_fund")))
PY
```

```text
rg -n "fund-analysis analyze|fund-analysis checklist|renderer|FQ0|FQ1|FQ2|FQ3|FQ4|FQ5|FQ6|FundDocumentRepository|pdf|cache|source helper|downloader|extractor|dayu|extra_payload" docs/reviews/release-maintenance-dev-only-chapter-audit-small-baseline-run-20260526.md /tmp/fund-agent-dev-only-chapter-audit-small-baseline-20260526
```

```text
git diff --check
```

Results:

- `audit_report_writing_bundle` and `constraints_for_chapter` imported successfully.
- The run used sidecar constraints for active Chapter 3, enhanced-index Chapter 2, and bond Chapter 6.
- Boundary grep matched only this artifact's boundary/prohibition text and scratch metadata; no source,
  tests, README, design, control doc, renderer, Service/CLI, Host/Agent/dayu, repository, PDF/cache/source,
  downloader, extractor, or product quality-gate file was modified.
- `git diff --check` passed.
