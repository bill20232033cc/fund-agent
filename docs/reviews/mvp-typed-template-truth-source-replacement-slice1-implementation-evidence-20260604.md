# MVP typed template truth-source replacement Slice 1 implementation evidence

## Worker self-check

- Self-check: pass.
- Role: implementation worker only for `MVP typed template truth-source replacement gate`, Slice 1.
- Scope: only `docs/fund-analysis-template-draft.md` and this evidence artifact are allowed.
- No source code, tests, README, design/control/startup, provider/runtime, Agent/Host, commit, push or PR action was performed.

## Changed files

- `docs/fund-analysis-template-draft.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md`

## Implemented plan items

- Added exactly one canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` HTML comment block near the top of `docs/fund-analysis-template-draft.md`.
- The canonical JSON carries stable `id` plus exact `text` for current accepted `must_answer`, `must_not_cover`, and `required_output_items`.
- Included current `preferred_lens`, `audit_focus`, `consumes_chapter_conclusions`, `independent_action_source`, Ch2 `internal_subcontracts`, Ch3 `ch3.must_not_cover.item_04` predicate and allowed contexts, and current required-output missing behavior/reasons.
- Replaced all eight per-chapter structured `CHAPTER_CONTRACT` blocks with short non-authoritative `CHAPTER_CONTRACT_REF` blocks.
- Preserved chapter titles, `CHAPTER_GOAL` blocks, body scaffolding, `ITEM_RULE` blocks, evidence anchor guidance, and audit appendices.
- Preserved public chapter ids `0-7`; Ch2 `performance / attribution / cost` remain internal subcontracts with `public_chapter_id: null`.

## Generation approach

- Used a one-off `uv run python` helper to read current accepted `load_typed_template_contract_manifest()` data and generate strict JSON.
- The helper wrote only the two allowed files: `docs/fund-analysis-template-draft.md` and this artifact.
- Per-chapter structured `CHAPTER_CONTRACT` blocks were mechanically replaced with short non-authoritative `CHAPTER_CONTRACT_REF` blocks.
- An initial attempt with system `python` failed before any write because the non-project environment lacked `httpx`; the successful write used `uv run python`.

## Validation commands and exact results

### Preflight status

Command:

```bash
git status --short
```

Result:

```text
?? docs/reviews/mvp-dayu-host-runtime-governance-adapter-implementation-preflight-20260601.md
?? docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md
?? docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md
?? docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-ds-20260603.md
?? docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-mimo-20260603.md
?? docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-ds-20260603.md
?? docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-mimo-20260603.md
?? docs/reviews/overnight-release-maintenance-deferred-coverage-status-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-decision-20260529.json
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-evidence-review-mimo-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-implementation-evidence-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-ds-20260529.md
?? docs/reviews/release-maintenance-004393-004194-006597-strict-correctness-follow-up-plan-review-mimo-20260529.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260526.md
?? docs/reviews/release-maintenance-comprehensive-audit-report-20260527.md
?? docs/reviews/repo-review-20260526-231040.md
?? docs/reviews/repo-review-20260527-215953.md
?? docs/reviews/repo-review-20260527-225303.md
?? docs/reviews/workspace-ownership-reconciliation-20260531.md
?? docs/superpowers/specs/2026-06-02-template-rebuild-facet-wiring-design.md
?? docs/tmux-agent-memory-store.md
?? reports/manual-llm-smoke/
?? reviews/
?? "\345\256\232\346\200\247\345\210\206\346\236\220\346\250\241\346\235\277.md"
```

Interpretation: unrelated untracked artifacts already existed before this Slice 1 implementation and were not touched.

### Generation helper

Command:

```bash
uv run python - <<'PY'
# one-off helper: read load_typed_template_contract_manifest(), dump canonical JSON,
# insert it into docs/fund-analysis-template-draft.md, and replace eight
# CHAPTER_CONTRACT blocks with CHAPTER_CONTRACT_REF blocks.
PY
```

Result:

```text
wrote docs/fund-analysis-template-draft.md
wrote docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md
chapters [0, 1, 2, 3, 4, 5, 6, 7]
replaced_contract_blocks [0, 1, 2, 3, 4, 5, 6, 7]
```

### Temporary manual JSON parse/equality check

Command:

```bash
uv run python - <<'PY'
# one-off validator:
# 1. extracts exactly one TEMPLATE_CONTRACT_MANIFEST_JSON block;
# 2. parses it with stdlib json;
# 3. checks public ids and chapter ids;
# 4. checks CHAPTER_CONTRACT_REF blocks and no old exact CHAPTER_CONTRACT markers;
# 5. checks no structured contract fields remain outside the canonical JSON block;
# 6. compares JSON projection against current load_template_contract_manifest();
# 7. compares JSON projection against current load_typed_template_contract_manifest();
# 8. checks Ch2 internal subcontracts public_chapter_id null;
# 9. checks Ch3 ch3.must_not_cover.item_04 predicate and allowed_contexts.
PY
```

Result:

```text
PASS canonical_blocks=1
PASS json_parses=True
PASS public_chapter_ids=[0,1,2,3,4,5,6,7]
PASS chapters=8 ids=[0,1,2,3,4,5,6,7]
PASS chapter_contract_refs=8 ids=[0,1,2,3,4,5,6,7] old_chapter_contract_blocks=0
PASS no_structured_contract_fields_outside_canonical_json=True
PASS json_projection_equals_current_untyped_manifest=True
PASS json_projection_equals_current_typed_manifest=True
PASS ch2_internal_subcontracts_public_chapter_id_all_null=True
PASS ch3_item_04_predicate_and_allowed_contexts=True
```

### Diff check

Command:

```bash
git diff --check -- docs/fund-analysis-template-draft.md docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md
```

Result:

```text
```

Exit code: `0`.

Note: the evidence artifact is a new untracked file, so Git's path-limited `diff --check` reports only tracked-file diff content. I also ran a no-index whitespace check for the untracked artifact.

Command:

```bash
git diff --no-index --check /dev/null docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md
```

Result:

```text
```

Exit code: `1`, expected for `git diff --no-index` when files differ; no whitespace warning was printed.

### Final scoped status

Command:

```bash
git status --short -- docs/fund-analysis-template-draft.md docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md
```

Result:

```text
 M docs/fund-analysis-template-draft.md
?? docs/reviews/mvp-typed-template-truth-source-replacement-slice1-implementation-evidence-20260604.md
```

## Non-goals preserved

- No source code, tests, README, design/control/startup, provider/runtime, Agent/Host, renderer, quality gate, baseline/golden, commit, push, PR or external action changes.
- No deterministic `analyze` / `checklist` behavior change.
- No public Ch2 split; public chapter ids remain exactly `0-7`.
- No provider/runtime/live probe.
- No duplicated structured `must_answer`, `must_not_cover`, `required_output_items`, `preferred_lens`, predicates, or missing behavior outside the canonical JSON block.

## Residual risks

- Slice 2 parser does not exist yet, so this slice relies on the temporary manual JSON parse/equality validation above until parser tests are implemented.
- Large JSON in Markdown remains authorability-sensitive; accepted mitigation is strict parser/validation in later slices.
- Existing unrelated untracked artifacts remain in the workspace and must not be staged by this gate.

## Completion status

- Completion status: complete for Slice 1 implementation handoff.
- Stop conditions encountered: none.
