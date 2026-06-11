# Evidence: Research/User-owned/Tooling Residue Metadata

Date: 2026-06-12

Gate: `Research/user-owned/tooling residue metadata evidence gate`

## 0. Worker Self-check

- Role: evidence worker only.
- Accepted plan: `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-plan-20260612.md`.
- Accepted plan controller judgment: `docs/reviews/mvp-research-user-owned-tooling-residue-disposition-plan-controller-judgment-20260612-064354.md`.
- This artifact is metadata-only. No candidate file body was read.
- No cleanup/archive/delete/ignore/import/promote/stage/push/PR/merge/release action was performed.
- No source/test/runtime behavior was changed.
- No live EID/network/PDF/FDR/provider/LLM/extractor/analyze/checklist/golden/readiness/release command was run.

## 1. Authorized Metadata Commands

Commands run for this evidence gate:

- `git status --short`
- `git status --branch --short`
- `git status --short -- docs/learning-roadmap.md docs/next-development-phaseflow.md docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md docs/tmux-agent-memory-store.md reviews scripts/claude_mimo_simple.py 基金年报 定性分析模板.md`
- `find reviews -maxdepth 3 -type f -print | sort`
- `find 基金年报 -maxdepth 2 -type f -print | sort`
- `git diff --check`

No `cat`, `head`, `tail`, `sed`, parser, checksum, PDF reader, Markdown reader, Python reader or report body reader was used on candidate paths.

## 2. Status Seen Value Space

| status_seen | Meaning |
|---|---|
| `untracked_file` | `git status --short -- <path>` listed the path as an untracked file. |
| `untracked_root` | `git status --short -- <path>` listed the path as an untracked root directory. |
| `under_untracked_root` | Path was returned by an authorized `find ... -type f -print | sort` under an untracked root; file body was not read. |

## 3. Evidence Rows

Mandatory non-proof fields apply to every row:

- `body_read=false`
- `not_source_truth=true`
- `not_design_truth=true`
- `not_template_truth=true`
- `not_release_evidence=true`
- `not_readiness_proof=true`

| path | status_seen | initial_category | path_listing_authorized | body_read | not_source_truth | not_design_truth | not_template_truth | not_release_evidence | not_readiness_proof | owner | next_gate |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| `docs/learning-roadmap.md` | `untracked_file` | `research_user_planning_doc` | true | false | true | true | true | true | true | Controller / artifact owner | User/controller disposition after metadata review |
| `docs/next-development-phaseflow.md` | `untracked_file` | `research_user_planning_doc` | true | false | true | true | true | true | true | Controller / artifact owner | User/controller disposition after metadata review |
| `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | `untracked_file` | `research_spec_residue` | true | false | true | true | true | true | true | Design/spec owner | Spec disposition or truth-source decision gate if needed |
| `docs/tmux-agent-memory-store.md` | `untracked_file` | `tooling_agent_ops_note` | true | false | true | true | true | true | true | Controller / agent-ops owner | Tooling disposition gate if needed |
| `reviews/` | `untracked_root` | `top_level_review_audit_root` | true | false | true | true | true | true | true | Controller / review-artifact owner | Top-level review/audit residue follow-up |
| `reviews/audit-report-2025-05-27-v2.md` | `under_untracked_root` | `top_level_review_audit_file` | true | false | true | true | true | true | true | Controller / review-artifact owner | Top-level review/audit residue follow-up |
| `reviews/audit-report-2025-05-27.md` | `under_untracked_root` | `top_level_review_audit_file` | true | false | true | true | true | true | true | Controller / review-artifact owner | Top-level review/audit residue follow-up |
| `scripts/claude_mimo_simple.py` | `untracked_file` | `source_like_tooling_script` | true | false | true | true | true | true | true | Controller / tooling owner | Source-like tooling ownership gate if needed |
| `基金年报/` | `untracked_root` | `user_owned_pdf_corpus_root` | true | false | true | true | true | true | true | User / document owner | PDF corpus ingestion/disposition gate if needed |
| `基金年报/国泰利享中短债债券型证券投资基金2024年年度报告.pdf` | `under_untracked_root` | `user_owned_pdf_corpus_file` | true | false | true | true | true | true | true | User / document owner | PDF corpus ingestion/disposition gate if needed |
| `基金年报/安信企业价值优选混合型证券投资基金2024年年度报告.pdf` | `under_untracked_root` | `user_owned_pdf_corpus_file` | true | false | true | true | true | true | true | User / document owner | PDF corpus ingestion/disposition gate if needed |
| `基金年报/招商中证1000指数增强型证券投资基金2024年年度报告.pdf` | `under_untracked_root` | `user_owned_pdf_corpus_file` | true | false | true | true | true | true | true | User / document owner | PDF corpus ingestion/disposition gate if needed |
| `基金年报/摩根标普500指数型发起式证券投资基金(QDII)2024年年度报告.pdf` | `under_untracked_root` | `user_owned_pdf_corpus_file` | true | false | true | true | true | true | true | User / document owner | PDF corpus ingestion/disposition gate if needed |
| `基金年报/易方达沪深300交易型开放式指数发起式证券投资基金联接基金2024年年度报告.pdf` | `under_untracked_root` | `user_owned_pdf_corpus_file` | true | false | true | true | true | true | true | User / document owner | PDF corpus ingestion/disposition gate if needed |
| `定性分析模板.md` | `untracked_file` | `user_owned_template_research_doc` | true | false | true | true | true | true | true | User / template owner | Template truth-source decision gate only if needed |

## 4. Counts

### 4.1 Candidate Path/root Count

| Metric | Count |
|---|---:|
| candidate paths/roots from accepted plan section 2.2 | 8 |
| candidate files listed directly by `git status --short -- ...` | 6 |
| candidate root directories listed directly by `git status --short -- ...` | 2 |

### 4.2 Listed Files Under Candidate Roots

| Root | File count |
|---|---:|
| `reviews/` | 2 |
| `基金年报/` | 5 |
| total listed files under candidate roots | 7 |

### 4.3 Row Counts By Initial Category

| initial_category | row_count |
|---|---:|
| `research_user_planning_doc` | 2 |
| `research_spec_residue` | 1 |
| `tooling_agent_ops_note` | 1 |
| `top_level_review_audit_root` | 1 |
| `top_level_review_audit_file` | 2 |
| `source_like_tooling_script` | 1 |
| `user_owned_pdf_corpus_root` | 1 |
| `user_owned_pdf_corpus_file` | 5 |
| `user_owned_template_research_doc` | 1 |
| total rows | 15 |

### 4.4 Row Counts By Next Gate

| next_gate | row_count |
|---|---:|
| User/controller disposition after metadata review | 2 |
| Spec disposition or truth-source decision gate if needed | 1 |
| Tooling disposition gate if needed | 1 |
| Top-level review/audit residue follow-up | 3 |
| Source-like tooling ownership gate if needed | 1 |
| PDF corpus ingestion/disposition gate if needed | 6 |
| Template truth-source decision gate only if needed | 1 |
| total rows | 15 |

### 4.5 Missing Or Extra Candidates

| Check | Result |
|---|---|
| Any accepted-plan candidate missing from targeted `git status --short -- ...` | none |
| Any accepted-plan candidate root with missing authorized listing | none |
| Any file under `reviews/` listed but not represented as a row | none |
| Any file under `基金年报/` listed but not represented as a row | none |

## 5. Excluded Groups Re-confirmed

`git status --short` still shows untracked entries under excluded groups. They remain outside this gate:

| Excluded group | Current handling |
|---|---|
| `docs/reviews/` | Excluded as prior review-artifact residue chain. Current status still shows many untracked review artifacts, so a future review/audit follow-up should confirm count drift before any release/readiness claim. |
| `docs/audit/` | Excluded as prior audit input/residue chain. |
| `reports/live-evidence/` | Excluded; metadata classification accepted at `e48b642`. |
| `reports/manual-llm-smoke/` | Excluded; metadata classification accepted at `e48b642`. |

## 6. Residuals And Blockers

| Residual / blocker | Status | Owner | Next gate |
|---|---|---|---|
| Candidate paths remain untracked residue | Blocks readiness claim | Controller / artifact owners | Controller judgment for this evidence gate, then specific disposition gates |
| `reviews/` top-level review/audit ambiguity | Deferred | Controller / review-artifact owner | Top-level review/audit residue follow-up |
| `scripts/claude_mimo_simple.py` source-like tooling risk | Deferred | Controller / tooling owner | Source-like tooling ownership gate if needed |
| `基金年报/` user-owned PDF corpus | Deferred; not production source path | User / document owner | Corpus ingestion/disposition gate if needed |
| design/template truth-source risk from spec/template-like docs | Deferred; not accepted as truth | Design/template owner | Truth-source decision gate if needed |
| excluded `docs/reviews/` count drift | Deferred | Controller | Review/audit residue follow-up before readiness |
| release/readiness | `NOT_READY` | Release owner / controller | Future release-readiness re-evidence after residue disposition |

## 7. Negative Evidence

- No candidate file body was read.
- No PDF file was opened, parsed, checksummed or used as evidence.
- No Python script content was read, imported or executed.
- No Markdown/spec/template body was read or treated as truth.
- No `docs/design.md`, `docs/fund-analysis-template-draft.md`, README, source, tests or runtime file was modified.
- No cleanup/archive/delete/ignore/import/promote/stage/push/PR/merge/release action was performed.
- No live/provider/network/PDF/FDR/LLM/extractor/analyze/checklist/golden/readiness/release command was run.
- No row is accepted as source truth, design truth, template truth, release evidence or readiness proof.

## 8. Validation

| Command | Result |
|---|---|
| `git status --short` | dirty/untracked workspace remains visible, including excluded groups and candidate paths |
| `git status --branch --short` | branch `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts`; ahead count visible; dirty/untracked workspace remains |
| `git status --short -- <candidate paths>` | all 8 accepted-plan candidate paths/roots visible as untracked |
| `find reviews -maxdepth 3 -type f -print \| sort` | 2 file paths listed |
| `find 基金年报 -maxdepth 2 -type f -print \| sort` | 5 file paths listed |
| `git diff --check` | pass |

Self-check: pass.
