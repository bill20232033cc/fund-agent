# MVP Small Golden Set Retained Excerpt Fixture - PDF-only Controller Judgment

## Verdict

`ACCEPTED_LOCAL`.

The `retained excerpt fixture gate for accepted rows only` is accepted locally for the five accepted source-identity rows: `004393`, `004194`, `006597`, `110020`, and `017641`.

## Accepted Artifacts

- Retained excerpt JSON: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`
- Retained excerpt summary: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.md`
- AgentDS review: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-review-ds-20260609.md`
- AgentMiMo review: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-review-mimo-20260609.md`

## Direct Evidence

- `python -m json.tool docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` passed.
- `git diff --check -- docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.md` passed.
- Controller sha256 recomputation matched all five local PDFs under `/Users/maomao/Downloads/基金年报/`.
- Controller boundary check confirmed exactly five rows and only accepted source identity rows from checkpoint `866a12b`.
- AgentMiMo review verdict: `PASS`.
- AgentDS review verdict: `PASS`.

## Residual Finding Judgment

- AgentDS noted incomplete 006597 optional spot-check coverage. Controller performed a supplemental local-PDF-only `pdfplumber` check for 006597 pages 5, 7, 18, 48, 49, and 61. The tables directly supported the retained identity, benchmark, A share units, A net asset, manager dates, fee rates, and top bond holding values. This residual is closed as non-blocking.
- Both reviews noted that retained excerpts use compact `key=value` wording rather than verbatim full text. This is accepted because the gate explicitly retains short field-level excerpts and does not retain full pages or full PDF text. Downstream row-field tests must treat `expected` values plus page/section anchors as the contract.
- 017641 uses `total_share_units` instead of inferred `target_share_units`; this is accepted because the retained value is directly proven by PDF p5 and avoids using an unanchored inferred A-share unit count.

## Boundary Judgment

This gate did not run network, endpoint/DNS/curl/socket/provider probes, live LLM, `FundDocumentRepository` live acquisition, fallback, extractor changes, fixture projection, exact/numeric correctness acceptance, golden/readiness promotion, Chapter calibration, Agent runtime expansion, multi-year runtime, score-loop, release, merge, or mark-ready.

The gate unlocks only the next `row-field extractor correctness test gate after accepted field excerpts`. Extractor fixes remain blocked until same-source failing row-field tests exist in a later authorized gate.

## Next Entry Point

`row-field extractor correctness test gate after accepted retained excerpts`.

Scope for the next gate:

- Write row-field tests only for fields present in `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.
- Use only matched source identity rows and retained field excerpts.
- Keep synthetic/unmatched rows out of correctness.
- Do not fix extractor until tests expose same-source failures and a separate extractor fix gate is opened.
