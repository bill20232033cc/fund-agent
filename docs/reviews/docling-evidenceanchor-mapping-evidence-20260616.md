# Docling EvidenceAnchor Mapping Evidence - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records no-live evidence for applying the accepted candidate-only Docling EvidenceAnchor mapping helper to accepted local candidate representation artifacts.

This gate did not run Docling conversion, live/network/EID/FDR/PDF/source acquisition, provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands. It did not change code, source policy, `FundDocumentRepository`, parser behavior, production `EvidenceAnchor` schema, Service, Host, UI, renderer or quality gate behavior.

## 2. Inputs

| Sample | Fund | Year | Schema family | Input path | Input status |
| --- | --- | --- | --- | --- | --- |
| S1-current-envelope | `004393` | `2025` | `S1_full` | `reports/representation-json/004393_2025_docling_current_envelope.json` | accepted candidate envelope |
| S1-full-json | `004393` | `2025` | `S1_full` | `reports/representation-json/004393_2025_docling_full.json` | local full JSON, not current candidate envelope schema |
| S4-full | `006597` | `2024` | `S4_S5_S6_lightweight` | `reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json` | accepted candidate envelope |
| S5-full | `017641` | `2024` | `S4_S5_S6_lightweight` | `reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json` | accepted candidate envelope |
| S6-full | `110020` | `2024` | `S4_S5_S6_lightweight` | `reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json` | accepted candidate envelope |

The S1 full JSON is retained as a schema-shape residual: it is a local full representation JSON, but `project_candidate_representation()` rejects it with `ValueError: unsupported candidate representation schema_version`. Therefore the evidence uses S1 current envelope for direct mapping and records the full JSON as blocked for this mapping gate.

## 3. Mapping Result Matrix

| Sample | Sections | Text blocks | Tables | Cells | Mapped total | Mapped types | Blocked total | Block reasons |
| --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| S1-current-envelope | 25 | 670 | 95 | 3493 | 10 | `heading=10` | 4273 | `missing_section_context=4270`, `unstable_section_context=3` |
| S4-full | 229 | 737 | 96 | 2759 | 33 | `heading=33` | 3788 | `missing_section_context=3786`, `unstable_section_context=2` |
| S5-full | 208 | 856 | 121 | 7060 | 28 | `heading=28` | 8217 | `missing_section_context=8214`, `unstable_section_context=3` |
| S6-full | 222 | 840 | 124 | 5940 | 31 | `heading=31` | 7095 | `missing_section_context=7093`, `unstable_section_context=2` |

Total direct mapped candidate anchors across accepted envelopes: `102`.

Total blocked candidate blocks across accepted envelopes: `23373`.

Mapped anchor type coverage in this evidence: `heading` only.

Overall mapped yield across accepted envelopes: `102 / 23475 = 0.43%`.

Blocked reason distribution across accepted envelopes: `missing_section_context=23363`, `unstable_section_context=10`. Missing section context accounts for `23363 / 23373 = 99.96%` of blocked candidate blocks.

Table/cell anchors were not emitted for these real artifacts because the current mapping helper requires stable annual-report section context before emitting a table/cell candidate anchor. The artifacts currently preserve strong table/cell locator coverage but do not consistently expose section context in the form required by the mapping helper.

## 4. Representative Mapped Samples

| Sample | Section | Page | Block type | Heading text |
| --- | --- | ---: | --- | --- |
| S1-current-envelope | `§1` | 2 | heading | `§1 重要提示及目录` |
| S1-current-envelope | `§2` | 5 | heading | `§2 基金简介` |
| S1-current-envelope | `§3` | 6 | heading | `§3 主要财务指标、基金净值表现及利润分配情况` |
| S1-current-envelope | `§4` | 11 | heading | `§4 管理人报告` |
| S1-current-envelope | `§5` | 15 | heading | `§5 托管人报告` |
| S4-full | `§1` | 2 | heading | `1.1 重要提示` |
| S4-full | `§2` | 5 | heading | `§2 基金简介` |
| S5-full | `§2` | 5 | heading | `§ 2 基金简介` |
| S6-full | `§2` | 5 | heading | `§2  基金简介` |

Every mapped output remains `candidate_only=True`, `candidate_source="docling"`, `field_correctness_status="not_proven"` and `source_truth_status="not_proven"` by construction of the accepted helper.

## 5. Representative Blocked Samples

| Sample | Block type | Reason | Locator summary |
| --- | --- | --- | --- |
| S1-full-json | sample | `unsupported candidate representation schema_version` | `reports/representation-json/004393_2025_docling_full.json` lacks `schema_version=candidate_annual_report_representation.v1` |
| S4-full | heading | `missing_section_context` | cover heading `国泰利享中短债债券型证券投资基金 2024 年年度报告 2024 年 12 月 31 日` |
| S4-full | heading | `missing_section_context` | heading `2.1 基金基本情况` |
| S5-full | heading | `missing_section_context` | cover heading `摩根标普 500 指数型发起式证券投资基金 2024 年年度报告 2024 年 12 月 31 日` |
| S6-full | heading | `missing_section_context` | cover heading `易方达沪深300交易型开放式指数发起式证券投资基金联 接基金` |

The dominant failure mode is section-context shape mismatch: many headings use annual-report numeric prefixes such as `2.1` without explicit `§2` tokens, while table/cell blocks do not yet carry stable section context consumed by the mapping helper.

## 6. Validation Commands

Commands run:

```bash
git status --branch --short
git diff --check
python -m json.tool reports/representation-json/004393_2025_docling_full.json
python -m json.tool reports/representation-json/006597_2024_docling_full.json
python -m json.tool reports/docling-full-document-coverage/20260616/coverage-summary.json
uv run python - <<'PY'
# local JSON load + project_candidate_representation + map_candidate_document_anchor_candidates dry-run
PY
```

Results:

| Check | Result |
| --- | --- |
| branch/status preflight | branch `feat/mvp-llm-incomplete-run-artifacts`, ahead `197`, historical untracked residue present |
| `git diff --check` | pass |
| JSON parsing | inspected local JSON shapes successfully |
| mapping dry-run | S1 current envelope + S4/S5/S6 mapped; S1 full JSON blocked by schema guard |

## 7. Evidence Judgment

This evidence supports:

- the accepted candidate mapping helper is fail-closed on real candidate representation artifacts;
- the helper can emit candidate-only heading anchors where annual-report section context is explicit enough;
- current real artifacts are not sufficient for table/cell EvidenceAnchor candidate yield without section-context enrichment or mapping rule expansion;
- S1 full JSON and S1 current-envelope schema divergence must be dispositioned before full-document S1 mapping evidence can be treated as complete.

This evidence does not support:

- source truth;
- full field correctness;
- table/cell production anchor readiness;
- Docling baseline promotion;
- production parser replacement;
- repository/parser/Service/Host/UI/renderer/quality-gate behavior change;
- readiness, release or PR state.

## 8. Residuals

| Residual | Owner | Recommended next handling |
| --- | --- | --- |
| Table/cell mapping yield is effectively zero on accepted real artifacts. | Fund documents candidate owner | `Docling EvidenceAnchor Mapping Section-context Enrichment Planning Gate` |
| S1 full JSON is not a current candidate envelope schema. | Fund documents candidate owner | Decide whether to regenerate/export full S1 as `candidate_annual_report_representation.v1` or keep current-envelope-only mapping evidence. |
| Section context consumes explicit `§` tokens and closed keyword families, but real headings often use numeric `2.1` etc. | Fund documents candidate owner | Plan deterministic annual-report section normalization before table/cell mapping evidence retry. |
| Candidate anchors remain non-production and non-proof. | Future design/evidence owner | Carry to baseline disposition; do not promote yet. |

## 9. Final Verdict

```text
VERDICT: ACCEPT_PARTIAL_HEADING_ONLY_MAPPING_EVIDENCE_NOT_READY
```
