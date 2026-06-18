# Fund Processor/Extractor S2 Truth-sync / Bookkeeping Controller Judgment - 2026-06-18

## Verdict

`ACCEPT_TRUTH_SYNC_BOOKKEEPING_NOT_READY`

## Scope

This was a `fast_path` documentation truth-sync gate. The allowed write surface was:

- `docs/design.md`
- top-level `fund_agent/README.md`
- control-plane bookkeeping in `docs/implementation-control.md`
- startup bookkeeping in `docs/current-startup-packet.md`
- this controller judgment artifact

No code, tests, parser/source behavior, PR state, release/readiness state, artifact deletion, archive, ignore-rule update, live/source acquisition, Docling conversion, pdfplumber export, provider/LLM command, golden promotion or readiness claim was authorized.

## Accepted Facts

- S2 is now the current accepted Fund Processor/Extractor fact for active fund annual parsed reports.
- Active fund annual `ParsedAnnualReport` now enters `FundDataExtractor.extract()` through `FundProcessorRegistry` / `ActiveFundAnnualProcessor` and is projected to `StructuredFundDataBundle`.
- Non-active and unclassified reports still use the direct legacy residual path.
- Docling, pdfplumber full JSON and EID HTML render remain Fund documents internal intermediate/candidate evidence inputs only.
- S2 does not consume Docling/FundDisclosureDocument candidate JSON, does not replace the production parser, does not prove source truth, full field correctness, golden/readiness or release.

## Controller Disposition

Accepted. The stale S1-era wording in `docs/design.md` and top-level `fund_agent/README.md` has been synchronized to the S2 closeout state without expanding scope. Control docs now point the mainline to `Extractor Projection Over Document Representation Planning Gate` as the next planning-only entry point.

## Validation

- `rg` stale wording scan for `尚未接入`, `Fund Processor/Extractor S1`, `已接受未来设计：在 Fund 层建设`, `S1 只建立`, `S1 尚未替换`, and `S1 no-live Processor` over `docs/design.md` and `fund_agent/README.md`
- `git diff --check` over the write surface

## Next Entry Point

`Extractor Projection Over Document Representation Planning Gate`

The next gate is planning-only. It must not implement code, run live/source acquisition, run Docling/pdfplumber/export/provider commands, replace production parser behavior, or claim source truth/readiness/release.
