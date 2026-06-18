# MiMo Plan Review: Fixture Promotion Content / Promotion-state Manifest

Review timestamp: 2026-06-13 14:24:54 +0800

Role: MiMo-role plan review worker, not controller

Reviewed target: `docs/reviews/mvp-fixture-promotion-content-manifest-plan-20260613.md`

Verdict: `PASS_WITH_AMENDMENTS`

## Scope

This review is plan review only. It did not edit source, tests, runtime,
golden answers, fixture content, control docs or design docs. It did not run
live/provider/LLM/analyze/checklist/readiness/release/PR commands.

Review focus:

- downstream parser evidence must not be converted into fixture promotion
  content proof;
- manifest scope must remain limited to `004393 / 2025` and the seven accepted
  tracked golden rows;
- fee rows, `turnover_rate`, skipped/deferred rows, other years and other funds
  must remain out of scope;
- release/readiness must remain `NOT_READY`;
- decide whether a narrow implementation gate is justified or whether the
  blocker should be deferred to residual rollup.

## Evidence Reviewed

- `docs/current-startup-packet.md` states the active gate is planning-only,
  allowed writes are plan/review/controller artifacts, fixture promotion
  content/manifest has not been created, and release/readiness remains
  `NOT_READY`.
- `docs/implementation-control.md` states the next gate must decide whether to
  create a reviewed year-aware fixture promotion manifest/content path for
  `004393 / 2025` or defer it to release/readiness residual handling.
- The tracked golden content controller judgment accepts exactly seven
  `004393 / 2025` rows and excludes fee rows, `turnover_rate`, skipped rows and
  deferred rows.
- The strict golden coverage controller judgment accepts the current tracked
  JSON surface as year-aware, but records fixture promotion content as still
  unresolved.
- The year-aware parser implementation judgment accepts exact
  `(fund_code, report_year)` identity, duplicate fail-closed behavior, unknown
  field fail-closed behavior and legacy fund-code-only diagnostic-only behavior.
- The downstream parser evidence controller judgment accepts only row-level
  consumption semantics and explicitly rejects treating that gate as fixture
  promotion content/manifest creation.
- `fund_agent/fund/golden_readiness_preflight.py` validates the year-aware
  manifest schema and derives promotion state from
  `fund_year_states[(fund_code, report_year)]`; legacy fund-code-only state
  routes to `fixture_promotion_legacy_fund_only`.

## Findings

| severity | evidence | recommended disposition |
|---|---|---|
| MEDIUM | The plan's implementation validation matrix checks JSON parsing, `_load_fixture_promotion_states(...)`, targeted parser tests, whitespace and status, but it does not include an explicit current-row-scope assertion for `reports/golden-answers/golden-answer.json`. The plan's own stop condition requires exactly one `004393 / 2025` entry with exactly seven active rows and zero skipped rows, while the parser only proves manifest schema/identity and cannot prove that no fee rows, `turnover_rate`, skipped/deferred rows or other rows were added to the tracked golden surface. | Amend the next implementation gate before handoff: add a read-only validation step and evidence output that parses or inspects `reports/golden-answers/golden-answer.json` and asserts exactly the seven accepted row identities, `skipped_fields == []`, no fee rows, no `turnover_rate`, no skipped/deferred rows, no other year/fund expansion. If this check fails, stop and route back to controller or defer to residual rollup. |
| LOW | The sample manifest entry includes the downstream parser evidence controller judgment in `evidence_artifacts`. The plan also correctly states that downstream parser evidence is not content proof and that the expected closeout content proof is the accepted manifest/content implementation itself. The wording is therefore not a blocker, but the sample can still be misread by an implementation worker as treating parser consumption evidence as promotion content proof. | Amend wording/source-authority notes: downstream parser evidence may be cited only as parser/consumption compatibility evidence. The new manifest JSON plus implementation evidence/reviews/controller judgment are the fixture promotion content proof. Do not allow downstream parser evidence alone to close `fixture_promotion_content_manifest_absent`. |

## Focus Answers

1. Downstream parser evidence is not treated as sufficient content proof in the
   plan's explicit boundary statements. Amendment F2 is needed only to remove
   ambiguity from `evidence_artifacts` wording.
2. The planned scope is correctly limited to `004393 / 2025` and the seven
   accepted tracked rows. Amendment F1 is required so the implementation gate
   validates that this row scope is still true at write time.
3. `NOT_READY` is preserved throughout the plan and aligns with current
   startup/control truth and controller judgments.
4. A narrow implementation gate is justified before residual rollup because the
   current control truth identifies manifest/content absence as the next
   decision point, and the parser/schema/downstream semantics are already
   accepted. If F1/F2 are not accepted, defer as
   `fixture_promotion_content_manifest_absent`.
5. Required amendments are validation/source-authority wording only; no source,
   test, runtime, golden, fixture, design or control edit is authorized by this
   review.

## Validation Notes

- `git status --short` showed existing untracked residue, including the target
  plan artifact. No cleanup or disposition was performed.
- `git diff --check` emitted no whitespace diagnostics.
- `git diff --check --no-index -- /dev/null docs/reviews/mvp-fixture-promotion-content-manifest-plan-20260613.md`
  emitted no whitespace diagnostics; non-zero exit is expected for a new file
  compared with `/dev/null`.

## Conclusion

The plan is safe to send to controller as `PASS_WITH_AMENDMENTS`: proceed to a
narrow implementation gate only after adding the row-scope validation and
clarifying that downstream parser evidence is consumption evidence, not content
proof. Release/readiness remains `NOT_READY`.
