# P6-S3 Plan Rereview Controller Judgment - 2026-05-20

## Verdict

P6-S3 plan is accepted for implementation.

The initial plan review in `docs/reviews/plan-review-20260520-142807.md` found three implementation-blocking issues:

1. `required_output_items` did not have a concrete deterministic marker matrix.
2. Adding `C2` conflicted with `docs/design.md` because design still marked all C2 as v2.
3. Shared `chapter_blocks.py` extraction and audit behavior changes were bundled without failure isolation.

The plan has been amended in `docs/reviews/p6-s3-programmatic-contract-audit-plan-20260520.md` to close those blockers.

下一 gate：`P6-S3 implementation`。

## Rereview Evidence

- Required output items now have a binding `Required Item Marker Matrix` covering every manifest item.
- The matrix distinguishes `already-rendered` from `renderer-label-needed`, so implementation can keep renderer edits limited to deterministic labels/placeholders.
- `C2` is explicitly accepted only as a deterministic `CHAPTER_CONTRACT` subset:
  - exact required-item markers
  - exact forbidden markers
  - chapter/contract metadata consistency
- The plan now requires `docs/design.md` 第 5.2 节 to be updated in the implementation slice so design, README, and code do not diverge.
- Implementation is split into:
  - Step A: behavior-preserving `template/chapter_blocks.py` extraction, verified by renderer tests before behavior changes.
  - Step B: contract audit, renderer audit input, minimal marker labels, docs, and tests.

## Accepted Constraints For Implementation

- Do not import `renderer.py` from `audit_programmatic.py`.
- Do not add LLM audit, PDF evidence re-search, Evidence Confirm, ITEM_RULE, quality gate FQ5 changes, Service changes, Engine changes, UI changes, or CLI behavior changes.
- Do not access fund documents directly from filesystem.
- Do not put explicit parameters into `extra_payload`.
- Add only the `renderer-label-needed` markers listed in the plan.
- Preserve the manifest typo `危级/降级阈值` until RR-19 is handled in a separate template cleanup.
- Treat P3 per-chapter evidence as format/structure only, not evidence support validation.
- Treat C2 as deterministic marker/metadata conformance only, not semantic chapter-overreach scoring.

## Required Verification

Implementation must run:

```bash
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_contracts.py tests/fund/template/test_renderer.py -q
.venv/bin/python -m pytest tests/services/test_fund_analysis_service.py tests/ui/test_cli.py tests/fund/integration/test_p3_cli_e2e_matrix.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

Step A must first run:

```bash
.venv/bin/python -m pytest tests/fund/template/test_renderer.py -q
```

and report that no intentional output behavior changed before Step B begins.

## Residual Risks

- The marker audit proves explicit labels/placeholders exist; it does not prove answer quality. That remains LLM audit / Evidence Confirm v2.
- Per-chapter evidence line presence does not prove evidence-to-claim support. That remains E1/E2/E3.
- Renderer output will gain labels for machine auditability. Reviewers should reject any broader prose rewrite not listed in the marker matrix.
