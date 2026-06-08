# MVP Small Golden Set Control Truth Reconciliation - EID Locator Policy

## Gate Metadata

- Gate: `control truth reconciliation gate`.
- Classification: `heavy`.
- Date: 2026-06-09.
- Scope: control truth sync only.
- Design truth: `docs/design.md`.
- Control truth: `docs/implementation-control.md`.
- Startup packet: `docs/current-startup-packet.md`.

## Direct Checks

- Branch: `feat/mvp-llm-incomplete-run-artifacts`.
- Dirty state before edits: only existing unrelated untracked residue plus prior in-progress retained-excerpt planning artifact; no source/test/config/runtime files were modified.
- Required documents read:
  - `AGENTS.md`
  - `docs/current-startup-packet.md`
  - `docs/implementation-control.md`
  - `docs/design.md`

## Reconciled Truth

- Matched annual-report source identity recovery planning/prep remains accepted at checkpoint `65532ab`.
- `004393 / 2024` docs-only manual evidence intake remains accepted at checkpoint `2706f91`.
- `004194`, `006597`, `110020`, `017641 / 2024` docs-only manual evidence intake remains accepted at checkpoint `7cc0479`.
- EID is now treated as the preferred official registry locator when available, not as a mandatory automatic extraction source and not as the exclusive source truth.
- `official_document_url` may come from EID, a fund-company official website/CDN PDF, CNINFO PDF or another official/first-party disclosure platform.
- Future source identity acceptance must record:
  - title as a 2024 annual report;
  - publisher as the fund manager or official disclosure platform;
  - PDF section 2 or equivalent official profile anchor proving fund code, fund name and share-class mapping;
  - URL, source-safe id and hash status.
- Search results, LLM summaries, synthetic fixtures, fallback traces and unproven historical outputs remain non-unlocking.
- Exact/numeric extractor correctness remains blocked until a row has accepted matched source identity plus retained row-field excerpt and accepted expected value.

## Updated Control Paths

- `docs/current-startup-packet.md`
  - Current gate now records `control truth reconciliation gate`.
  - Source identity route records EID as preferred locator, not required extraction source.
  - Next entry point records the ordered route from manual evidence intake to closeout.
- `docs/implementation-control.md`
  - Top current status, current gate table and Current Gate section now share the same policy.
  - Next gate classification preserves docs-only manual intake as `standard` and source policy/FDR/PDF/network/retention/promotion changes as `heavy`.

## Phaseflow Route

1. `control truth reconciliation`.
2. `manual evidence intake for all 5 rows`.
3. `source identity acceptance decision`.
4. `retained excerpt fixture for accepted rows only`.
5. `row-field extractor correctness tests`.
6. `extractor fixes only after same-source failing tests`.
7. `closeout gate`.

## Non-Goals Preserved

- No extractor, fixture, provider/default/runtime/budget/config, golden/readiness or quality gate changes.
- No live LLM, endpoint/DNS/curl/socket/provider probe, fallback invocation, `FundDocumentRepository` access, PDF/network acquisition, akshare or EID live access.
- No Chapter calibration, Agent runtime expansion, multi-year runtime, score-loop, PR/release/merge/mark-ready action.
- No cleanup or use of unrelated dirty/untracked files.

## Validation Matrix

| Check | Evidence | Result |
|---|---|---|
| Branch check | `git branch --show-current` | `feat/mvp-llm-incomplete-run-artifacts` |
| Dirty scope check | `git status --short` | Only docs/control files changed by this gate; unrelated untracked residue remains untouched |
| Formatting | `git diff --check -- docs/current-startup-packet.md docs/implementation-control.md docs/reviews/mvp-small-golden-set-control-truth-reconciliation-eid-locator-policy-20260609.md` | Required before checkpoint |
| Scope guard | Changed files | No source, tests, fixtures, provider/runtime/config, golden/readiness files touched |

## Controller Judgment

Accepted, subject to the validation matrix passing. The reconciliation aligns control docs with the latest steering: source identity work should not be blocked on EID automatic extraction. EID remains useful as official registry locator, while official PDF/document identity can be accepted from EID, fund-company official URLs, CNINFO or another official/first-party disclosure platform if the future gate records the required anchors.

Next entry point: `manual evidence intake gate for all 5 rows`.
