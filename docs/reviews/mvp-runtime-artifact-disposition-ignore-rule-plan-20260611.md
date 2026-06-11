# Runtime Artifact Disposition / Ignore-rule Planning Gate Plan

日期：2026-06-11

角色：AgentCodex planning worker

状态：plan-only；不执行 cleanup、ignore-rule edit、promotion、archive、delete、stage、commit、push、PR、release/readiness 或 live/provider/EID/PDF/FDR/analyze/checklist/golden 命令。

## 1. Scope and Non-goals

Scope:

- 为下一 implementation/disposition gate 产出 code-generation-ready plan。
- 基于当前 `git status --short` 刷新 untracked inventory，并使用已接受 residue disposition index 作为输入，不把旧 inventory 当 live truth。
- 分类 runtime/generated/untracked artifacts，并提出精确 handling options。
- 规划后续 `.gitignore` reviewed implementation gate 的候选 pattern；本 plan 不编辑 `.gitignore`。

Non-goals:

- 不修改 source、tests、runtime behavior、README、`docs/design.md`、control truth 或 `.gitignore`。
- 不删除、移动、归档、清理、ignore、import、stage、promote、commit、push、PR。
- 不运行 release/readiness/live/provider/EID/PDF/FDR/network/analyze/checklist/golden commands。
- 不读取大型 PDF、runtime stdout/stderr 内容或 untracked report 内容；本 plan 只使用路径、大小、mtime、`git status` 与少量文件元数据。
- 不把 arbitrary untracked residue 作为 proof、accepted fixture、product scope 或 release evidence。

## 2. Current Inventory Groups

Truth inputs read:

- `AGENTS.md`
- `docs/design.md` relevant design-boundary sections
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md`
- current `git status --short`
- `.gitignore` metadata only: tracked blob `84ff7385f35b365c455754b900d1201e8be6317c`, size `872`, mtime `Jun 2 05:19:12 2026`

Current status facts:

- Branch: `feat/mvp-llm-incomplete-run-artifacts...origin/feat/mvp-llm-incomplete-run-artifacts [ahead 100]`.
- `git status --short` currently shows only untracked entries.
- `docs/reviews` currently has 35 untracked top-level entries including this plan artifact. This count is a point-in-time status snapshot; the implementation gate must refresh it with live `git status --short docs/reviews`.
- `docs/audit/` currently has one untracked review input file by metadata: `docs/audit/fund-agent-repo-deepreview-20260610.md`, size `50809`.
- `reports/manual-llm-smoke/` currently has 8 untracked files by metadata under two run directories.
- `reviews/` currently has two untracked audit report files by metadata.
- `基金年报/` currently has five untracked PDF files by metadata only.
- `fund_agent/tools` exact source-like residue does not appear in current `git status --short fund_agent/tools`; it was accepted closed by checkpoint `11040bd` and must not re-enter this gate unless a future live status shows it again.
- `scripts/claude_mimo_simple.py` remains a current untracked helper.

Current inventory groups from live `git status --short`:

- Evidence-chain review/audit artifacts: `docs/reviews/*.md`, `docs/reviews/*.json`, `docs/audit/`.
- Research/planning inputs: `docs/learning-roadmap.md`, `docs/next-development-phaseflow.md`, `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md`, `docs/tmux-agent-memory-store.md`, `定性分析模板.md`.
- Scratch/runtime outputs: `reports/manual-llm-smoke/`.
- User-owned local data corpus: `基金年报/`.
- Obsolete duplicate / external review residue: `reviews/`.
- Scratch helper / tooling residue: `scripts/claude_mimo_simple.py`.

## 3. Disposition Table

| Path/group | Category | Evidence | Proposed decision | Owner | Next gate | Blocker |
|---|---|---|---|---|---|---|
| `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-20260611.md` | current-gate plan artifact | Current plan file created by this planning gate and visible in `git status --short docs/reviews` | `stage-current-gate` only after plan review and controller judgment accept it | controller | current planning closeout | No after accepted checkpoint |
| Other untracked `docs/reviews/*.md` and `docs/reviews/*.json` | evidence-chain artifact / possible accepted artifact by exact file | Current live count is 35 including this plan artifact; this row covers the remaining untracked review artifacts after excluding the current-gate plan | `leave-untracked` by default; `promote-through-review` only for exact artifacts mapped to accepted plan/review/controller judgment gates | controller / artifact owner | artifact-specific provenance acceptance gate | Blocks release/readiness until classified or accepted residual owner recorded |
| `docs/audit/` | evidence-chain artifact / review input | metadata shows one `fund-agent-repo-deepreview-20260610.md`; long-run startup treats deepreview input as review input, not truth source | `leave-untracked`; promote only through review-artifact acceptance gate; do not let it override design/control truth | controller / reviewer owner | review-artifact disposition gate | Blocks release/readiness if unclassified |
| `reports/manual-llm-smoke/` | scratch/runtime output / possible live evidence residue | metadata shows 8 files including stdout/stderr/env/run metadata; contents not read | `leave-untracked`; exact run artifacts may be `promote-through-review` only if a reviewed live-evidence gate accepts them; candidate ignore target for repeatable manual smoke output | runtime evidence owner / controller | runtime evidence disposition gate, then optional ignore-rule implementation gate | Blocks release/readiness until accepted disposition; cannot be proof now |
| `基金年报/` | user-owned unknown / local PDF corpus | metadata shows 5 PDF files; contents not read; AGENTS/design require production annual report access through `FundDocumentRepository` | `leave-untracked`; no direct filesystem use for production proof; candidate local-data ignore only if user/controller accepts | user / data artifact owner | data artifact disposition gate | Blocks release/readiness if unclassified; delete/move requires explicit authorization |
| `reviews/` | obsolete duplicate / external review residue | metadata shows two audit report files outside canonical `docs/reviews/` | `leave-untracked`; `archive candidate` or `delete candidate requiring explicit authorization` only after exact owner decision | controller / user | obsolete-duplicate disposition gate | Blocks release/readiness until disposition accepted |
| `docs/learning-roadmap.md` | research input | listed by `git status --short`; not control/design truth | `leave-untracked`; promote only through docs/design/research acceptance gate | user / controller | research-doc disposition gate | Non-blocking for this planning gate; blocks release/readiness if unclassified |
| `docs/next-development-phaseflow.md` | research/planning input | listed by `git status --short`; current control truth is `docs/implementation-control.md` | `leave-untracked`; cannot be treated as control truth unless accepted by controller gate | controller | phaseflow planning disposition gate | Non-blocking here; blocks release/readiness if unclassified |
| `docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md` | research input / candidate design | listed by `git status --short`; design truth remains `docs/design.md` | `leave-untracked`; promote only through design-truth-sync gate | design owner / controller | design candidate disposition gate | Blocker only if cited as current truth without gate |
| `docs/tmux-agent-memory-store.md` | scratch operations note / research input | listed by `git status --short` | `leave-untracked`; archive candidate only after explicit ops artifact gate | controller / agent setup owner | ops artifact disposition gate | Non-blocking here; blocks release/readiness if unclassified |
| `定性分析模板.md` | user-owned unknown / research input | listed by `git status --short`; canonical template truth is `docs/fund-analysis-template-draft.md` | `leave-untracked`; do not promote or cite as template truth without reviewed template gate | user / template owner | template research disposition gate | Non-blocking here; blocks release/readiness if unclassified |
| `scripts/claude_mimo_simple.py` | scratch helper / tooling residue | listed by `git status --short`; not imported or accepted evidence | `leave-untracked`; promote only through tooling support gate; delete candidate requires explicit authorization | user / controller | tooling residue disposition gate | Non-blocking here; blocks release/readiness if unclassified |
| `fund_agent/tools` exact source-like residue | closed source-like residue | current `git status --short fund_agent/tools` shows no entry; control doc says accepted closed by `11040bd` | no action; do not re-enter this gate unless it reappears in live status | controller / implementation owner | none unless reappears | Closed for this exact residue |

## 4. Exact Implementation Options by Category

`leave-untracked`:

- Default for user-owned unknowns, research inputs, unaccepted review inputs, scratch helpers and unclassified runtime outputs.
- Implementation gate action: make no filesystem change; record residual owner and release/readiness blocker status.

`promote-through-review`:

- Only for exact artifacts whose provenance maps to an accepted gate artifact, reviewed evidence, controller judgment or durable fixture requirement.
- Required preconditions: artifact path named in accepted plan/review/controller judgment; MiMo/DS review confirms it is not runtime scratch; controller accepts exact path.
- Candidate groups: selected `docs/reviews/*.md/json`, selected `docs/audit/*` only if converted into accepted review evidence, selected `reports/manual-llm-smoke/*` only under a separate live-evidence acceptance gate.
- Required implementation step before any promotion: read the accepted artifact index or the exact reviewed plan / review / controller judgment that names the path, then record that provenance line in the implementation evidence. If no exact path-level provenance exists, the only allowed decision is `leave-untracked` or `defer`.

`ignore-rule candidate`:

- Only for repeatable generated output that should not be reviewed as source.
- Candidate patterns to consider in a later reviewed implementation gate:
  - `reports/manual-llm-smoke/`
  - `reports/llm-runs/`
  - `**/__pycache__/`
  - `*.py[cod]`
  - `.pytest_cache/`
  - `.ruff_cache/`
  - `htmlcov/`
  - `coverage.xml`
  - local PDF corpus pattern such as `基金年报/` only if user/controller classifies it as local runtime data that should never enter review as source; if it remains a user-owned unknown or possible durable fixture, leave it visible and untracked
- Do not ignore `docs/reviews/` broadly.
- Do not ignore `docs/audit/` broadly until review-artifact policy is decided.
- Do not ignore `reviews/` if the intended decision is archive/delete, because ignore would hide an obsolete duplicate instead of resolving it.

`archive candidate`:

- For evidence-chain artifacts that should remain auditable but not in the active review surface.
- Candidate groups: `reviews/` duplicate audit reports; possibly `docs/audit/` if controller wants a canonical archive location.
- Required preconditions: accepted implementation gate names exact source and destination paths; user/controller authorizes move/archive; post-move status and diff are reviewed.

`delete candidate requiring explicit authorization`:

- Only for obsolete duplicates, disposable runtime outputs or local scratch helpers after owner confirms no evidence value.
- Candidate groups: `reviews/` duplicates, `reports/manual-llm-smoke/` old failed smoke outputs, `scripts/claude_mimo_simple.py`, local PDF corpus only if user explicitly confirms deletion.
- Any `rm`, delete, move-to-trash, cleanup, archive move or generated-output pruning requires separate user authorization or an accepted implementation gate. This plan does not authorize it.

## 5. .gitignore Plan

`.gitignore` implementation must be a later reviewed implementation gate. This planning gate only records candidates; it does not read `.gitignore` contents beyond tracked metadata, does not edit `.gitignore`, and does not claim current ignore coverage.

Later `.gitignore` implementation gate should:

1. Re-read `.gitignore` content and current status.
2. Add only scoped patterns for repeatable generated/runtime outputs.
3. Avoid hiding evidence-chain artifacts before disposition acceptance.
4. After editing, run `git check-ignore -v` against each proposed generated path and confirm no intended review artifact is accidentally ignored.

Exact candidate patterns to evaluate:

```gitignore
reports/manual-llm-smoke/
reports/llm-runs/
**/__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
htmlcov/
coverage.xml
```

Conditional candidate requiring owner decision:

```gitignore
基金年报/
```

This conditional pattern is acceptable only if the next gate classifies that directory as local user/runtime data that should never enter review as source. If it remains user-owned unknown, leave it untracked and visible.

## 6. Release / Readiness Impact and Blockers

- Current untracked residue does not block this plan-only gate because no runtime cleanup or release status is claimed.
- Current untracked residue blocks any future release/readiness cleanliness gate until each group has accepted disposition, explicit residual owner, or authorized cleanup.
- `reports/manual-llm-smoke/`, `基金年报/`, `reviews/`, `docs/audit/` and unaccepted `docs/reviews/*` cannot be treated as release evidence or accepted proof.
- `.gitignore` changes must not be bundled with deletion/archive/promotion. The least risky sequence is disposition acceptance first, ignore-rule implementation second, release/readiness cleanliness third.
- `fund_agent/tools` exact source-like residue is already closed by `11040bd`; it is not a current release/readiness blocker unless it reappears.

## 7. Validation Matrix for Eventual Implementation Gate

The eventual implementation/disposition gate should run only metadata/status validation unless that gate separately authorizes content inspection.

| Check | Command | Purpose | Pass condition |
|---|---|---|---|
| Short status | `git status --short` | Confirm remaining untracked/tracked changes after disposition action | Only accepted current-gate files and accepted residuals remain visible |
| Branch status | `git status --branch --short` | Confirm branch/ahead state and untracked summary | Branch state recorded; no hidden release claim |
| Whitespace check | `git diff --check` | Detect whitespace errors in tracked edits | No errors |
| Changed tracked files | `git diff --name-only` | Confirm implementation touched only authorized files | Only accepted write-set files appear |
| Promotion provenance check | exact `sed`/`rg` over accepted artifact index or controller judgment naming each promoted path | Prevent unreviewed residue promotion | Every promoted file has exact path-level accepted provenance; otherwise it is not promoted |
| Ignore rule proof | `git check-ignore -v <path>` for each implemented pattern target | Confirm ignore pattern applies only to intended generated/runtime outputs | Expected generated path is ignored by exact intended rule; evidence-chain paths are not ignored |
| Staged-file check | `git diff --cached --name-only` and `git status --short` | Confirm no accidental stage | Empty unless implementation gate explicitly authorizes staging |

Additional guardrails:

- If any proposed archive/delete action is accepted, run status before and after and record exact path-level delta.
- If any path is promoted-through-review, record the controller judgment or reviewed plan line that names the exact file.
- Do not run release/readiness/live/provider/EID/PDF/FDR/analyze/checklist/golden commands as part of this disposition validation unless a separate reviewed gate authorizes them.

## 8. Review Checklist for MiMo / DS

MiMo / DS should independently check:

- Does the plan preserve `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md` and `docs/implementation-control.md` truth hierarchy?
- Does any row treat untracked residue as proof, accepted fixture, product scope or release evidence?
- Are evidence-chain artifacts, research inputs, scratch/runtime outputs, candidate durable fixtures, user-owned unknowns, obsolete duplicates and delete candidates separated?
- Are `.gitignore` candidates scoped to generated/runtime outputs, without broadly hiding `docs/reviews/`, `docs/audit/`, source-like residue or user-owned unknowns?
- Is `fund_agent/tools` correctly treated as closed by `11040bd` and excluded from this gate unless it reappears?
- Does every delete/move/archive/cleanup decision require explicit user authorization or an accepted implementation gate?
- Does the validation matrix avoid prohibited live/provider/EID/PDF/FDR/analyze/checklist/golden/release commands?
- Are release/readiness blockers stated as blockers for a future gate, not as current release acceptance?

## 9. Commands Run for This Plan

- `sed -n '1,240p' /Users/maomao/.codex/skills/artifact-disposition/SKILL.md`
- `rg -n "artifact-disposition|mvp-control-doc-compression|untracked residue|residue disposition|fund_agent/tools|11040bd" /Users/maomao/.codex/memories/MEMORY.md`
- `sed -n '640,700p' /Users/maomao/.codex/memories/MEMORY.md`
- `git status --short`
- `git branch --show-current`
- `git log --oneline -n 5`
- `wc -l .gitignore docs/design.md docs/current-startup-packet.md docs/implementation-control.md docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md AGENTS.md`
- `sed -n '1,320p' AGENTS.md`
- `sed -n '1,140p' docs/current-startup-packet.md`
- `sed -n '1,220p' docs/implementation-control.md`
- `sed -n '1,120p' docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `sed -n '1,220p' docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md`
- `stat -f '%N size=%z mtime=%Sm' .gitignore`
- `git ls-files -s .gitignore`
- `rg -n "当前已实现|UI -> Service -> Host -> Agent|FundDocumentRepository|EID|Eastmoney|fallback|--use-llm|Runtime artifact|release|readiness|extra_payload|docs/reviews|runtime" docs/design.md`
- `sed -n '1,220p' docs/design.md`
- `sed -n '620,760p' docs/design.md`
- `sed -n '1080,1248p' docs/design.md`
- `git status --branch --short`
- `git status --short fund_agent/tools scripts/claude_mimo_simple.py`
- `find docs/audit -maxdepth 2 -type f -exec ls -l {} +`
- `find reports/manual-llm-smoke -maxdepth 3 -type f -exec ls -l {} +`
- `find reviews -maxdepth 3 -type f -exec ls -l {} +`
- `find 基金年报 -maxdepth 2 -type f -exec ls -l {} +`
- `git status --short docs/reviews`
- `git status --short docs/reviews | wc -l`
- `ls -l docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-20260611.md`
- `git ls-files --stage docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-20260611.md`

## 10. Residuals

- This plan artifact itself is untracked until a future accepted gate stages or commits it.
- All current untracked residue remains untouched and unaccepted as proof.
- `.gitignore` remains unchanged; current ignore coverage was not evaluated beyond file metadata.
- Any delete, move, archive, cleanup or ignore-rule edit remains blocked on separate user authorization or accepted implementation gate.
- Release/readiness cleanliness remains blocked until disposition outcomes are accepted and validated.
