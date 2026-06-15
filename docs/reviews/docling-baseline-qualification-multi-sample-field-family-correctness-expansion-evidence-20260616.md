# Docling Multi-sample Field-family Correctness Expansion Evidence - 2026-06-16

Gate: `Docling Multi-sample Field-family Correctness Expansion Evidence Gate`
Release/readiness: `NOT_READY`
Verdict: `blocked_not_ready`

## 1. Scope

This evidence gate executed the accepted plan checkpoint `bc82125` using only existing local candidate JSON and accepted reviewed-facts artifacts. It did not run live/network/EID acquisition, `FundDocumentRepository`, PDF parsing, Docling conversion, provider/LLM routes, analyze/checklist/golden/readiness/release/PR/push/merge commands, or source/test/runtime changes.

## 2. Evidence Inputs

- Plan: `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-20260615.md`
- Plan controller judgment: `docs/reviews/docling-baseline-qualification-multi-sample-field-family-correctness-expansion-plan-controller-judgment-20260616.md`
- Manifest: `reports/representation-json/full-representation-export-manifest-20260615.json` sha256 `bab5fcb81126ca501c553e94eafebcd64da2b537930833aaf81c118b648b6349`
- S1 accepted reviewed facts: `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json` sha256 `8ca8071f6c3f3fc96fe41c877c14b90697821f3b6a2272cb2cf8bb2945413beb`
- Evidence JSON: `reports/representation-json/docling_multi_sample_field_family_correctness_reviewed_facts_20260616.json`

## 3. Candidate Input Availability

| Sample | Fund | Year | Docling JSON | Docling output hash | pdfplumber JSON | pdfplumber output hash | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `S1` | `004393` | `2025` | `reports/representation-json/004393_2025_docling_full.json` | `069282b22d7926e93743cc12a8538e43eaf262aa165376d872552a76efac0e49` | `reports/representation-json/004393_2025_pdfplumber_full.json` | `ef1787934e0a8b46bd9b3c8e03a9b760d6c987fd51952739c1f77ac7f24b6ab4` | `present` |
| `S4` | `006597` | `2024` | `reports/representation-json/006597_2024_docling_full.json` | `ee193cc74542fb2792f2baf1984cf288cf9b55bd321ccee43aff7a6e69258307` | `reports/representation-json/006597_2024_pdfplumber_full.json` | `003678ba8c2a50520011ebbe5fa7c9d991c912677353547376cf69f9f1b49370` | `present` |
| `S5` | `017641` | `2024` | `reports/representation-json/017641_2024_docling_full.json` | `7fe3c36eb3cb10108482bbe877bcdbbac7706471137046394d8322ccf77e56d7` | `reports/representation-json/017641_2024_pdfplumber_full.json` | `80d6cdfff2003259c2891db20bc86476b6249cf3fc10bc976ba46a75228f3265` | `present` |
| `S6` | `110020` | `2024` | `reports/representation-json/110020_2024_docling_full.json` | `ce2cbeb348101a21df563be4a60dd57d54ac73a3a14a7454845e7d36d56f86fb` | `reports/representation-json/110020_2024_pdfplumber_full.json` | `8c0d0d94e78da5c44a36dc23650eb4cfca78c475ec2e5db19232c21bd0f3a0cd` | `present` |

Manifest note: for S4/S5/S6, `accepted_input_sha256` in the manifest is the source PDF input artifact hash, not the full JSON output hash. This evidence records output JSON hashes separately and does not treat JSON-vs-PDF hash inequality as a mismatch.

## 4. Same-source Reference Proof

| Sample | Reference route | Status | Reason |
| --- | --- | --- | --- |
| `S1` | accepted same-source reference artifact | `reviewable` | Prior 004393 field-family correctness pilot reused by hash. |
| `S4` | none accepted in this gate | `blocked_reference_unavailable` | No accepted same-source reference artifact was identified; no FDR/PDF/live command was authorized or run. |
| `S5` | none accepted in this gate | `blocked_reference_unavailable` | No accepted same-source reference artifact was identified; no FDR/PDF/live command was authorized or run. |
| `S6` | none accepted in this gate | `blocked_reference_unavailable` | No accepted same-source reference artifact was identified; no FDR/PDF/live command was authorized or run. |

`FundDocumentRepository(force_refresh=False)` was not attempted for S4/S5/S6 in this evidence pass because this gate was executed as no-live/no-PDF/no-FDR evidence. The accepted plan allows blocking when no-live reference proof cannot be established without source/cache internals, direct PDF paths, `force_refresh=True`, or live acquisition. This evidence therefore records `no_no_live_reference_proof` instead of probing repository behavior.

## 5. Reviewed Fact Result

- S1 Docling selected facts reused: `21`; exact `19`, normalized `2`, partial `0`, mismatch `0`.
- S1 pdfplumber comparator facts reused: `4`; mismatch `4`. Comparator results remain diagnostic only.
- Source pilot fact ids `F021`-`F024` are pdfplumber comparator facts and are intentionally excluded from this Docling-only `facts[]` array.
- S4/S5/S6 facts selected: `0`; all blocked before fact selection because no no-live same-source reference proof exists.

## 6. Blocked Claims And Residuals

- `not_source_truth`: existing candidate JSONs are not source truth.
- `not_field_correctness_proof`: S4/S5/S6 field correctness was not reviewed.
- `not_full_field_correctness`: S1 remains bounded; multi-sample expansion is blocked.
- `not_production_parser_replacement`: no production parser replacement is justified.
- `not_readiness_proof`: release/readiness remains `NOT_READY`.
- `no_repository_behavior_change`: no repository, parser, source policy, `EvidenceAnchor`, Service, Host, UI, renderer, quality gate, tests, runtime, or LLM route changed.

## 7. Final Verdict

```text
VERDICT: BLOCKED_INSUFFICIENT_REVIEWABLE_SAMPLE_MATRIX_NOT_READY
```

The candidate artifacts for S4/S5/S6 exist, but candidate existence is not correctness proof. The next gate should establish no-live same-source reference proof for expansion samples or explicitly authorize a bounded reference-acquisition gate before any multi-sample correctness review.
