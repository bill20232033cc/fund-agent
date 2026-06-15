# 004393 Field-family Correctness Pilot Controller Judgment - 2026-06-15

Gate: `004393 Field-family Correctness Pilot Evidence Gate`  
Role: controller  
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes the bounded field-family correctness pilot for:

- fund code: `004393`
- fund name: 安信企业价值优选混合A
- report year: `2025`

Reviewed evidence:

- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-evidence-20260615.md`
- `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json`

Review inputs:

- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-evidence-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-evidence-review-mimo-20260615.md`

## 2. Accepted Current Facts

| Fact | Classification | Controller decision |
| --- | --- | --- |
| The evidence worker loaded the annual report through `FundDocumentRepository().load_annual_report("004393", 2025, force_refresh=False)`. | repo/evidence fact | ACCEPT |
| Repository metadata reported source `eid`, source mode `single_source_only`, fallback disabled, fallback unused, parsed cache hit `True`, and PDF path `cache/pdf/004393_2025_annual_report_eid.pdf`. | repo/evidence fact | ACCEPT |
| Reviewed-facts JSON exists at `reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json` with SHA-256 `8ca8071f6c3f3fc96fe41c877c14b90697821f3b6a2272cb2cf8bb2945413beb`. | evidence fact | ACCEPT |
| Docling candidate selected facts matched same-source repository-loaded PDF bbox crop excerpts in 21/21 reviewed facts: 19 exact matches and 2 normalized matches. | evidence fact | ACCEPT |
| pdfplumber comparator rows mismatched same-source PDF crop excerpts in 4/4 selected comparator checks. | evidence fact | ACCEPT_WITH_LIMIT |
| EID HTML render remains blocked/deferred for this sample and is not part of correctness evidence. | evidence fact | ACCEPT |

## 3. Review Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Evidence initially lacked exact extraction command and output path/hash. | DS + MiMo | ACCEPT_FIXED | Evidence artifact now records command, `FACTS` tuple, input files, output path, observed output, and reviewed-facts JSON hash. |
| PDF path and `pdf_cache_hit=False` could be read as direct cache bypass. | DS | ACCEPT_FIXED | Evidence now states the PDF path came from `document.metadata.cache.pdf_path` after repository load succeeded and explains `pdf_cache_hit=False`. |
| Pilot result wording could be confused with candidate `field_correctness_status`. | MiMo | ACCEPT_FIXED | Evidence now says candidate `field_correctness_status` remains `not_proven`; pilot result is a separate bounded evidence conclusion. |
| `manager_alignment` had only two facts. | MiMo | ACCEPT_FIXED | F025 `manager_tenure_start` was added; `manager_alignment` now has three reviewed Docling facts. |
| Docling pass could be overgeneralized. | Controller guardrail | ACCEPT_AS_BOUNDARY | Judgment accepts only selected-fact bounded pilot pass, not full correctness, source truth, production replacement, or readiness. |
| pdfplumber mismatch could be overgeneralized. | Controller guardrail | ACCEPT_AS_BOUNDARY | Judgment limits mismatch to four selected comparator locator/crop checks. |

## 4. Accepted / Rejected / Residual Table

| Item | Status | Controller note |
| --- | --- | --- |
| Accept Docling as candidate-layer field-family pilot pass for selected `004393_2025` facts. | ACCEPT | Evidence supports `21/21` selected Docling facts matching same-source PDF crop excerpts. |
| Accept Docling as full production parser baseline. | REJECT | This gate did not test broad sample coverage, narrative extraction, production repository behavior, source truth, or readiness. |
| Accept Docling as source truth. | REJECT | Candidate artifacts remain non-truth; same-source PDF remains the reference for this pilot. |
| Accept pdfplumber as failed generally. | REJECT | Only four selected comparator locator/crop mismatches were reviewed. |
| Accept EID HTML field correctness. | REJECT | EID HTML current-envelope remains blocked/deferred for this sample. |
| Treat local PDF crop excerpts as sufficient for bounded pilot evidence. | ACCEPT_WITH_RESIDUAL | Stronger than parser agreement, but future broader gates may add visual page review for ambiguous facts. |
| Move to production implementation directly. | REJECT | Must first update control/design truth and plan integration boundaries. |

## 5. Validation

Commands:

```text
git diff --check
uv run python - <<'PY'
import json
from pathlib import Path
from collections import Counter
p = Path("reports/representation-json/004393_field_family_correctness_pilot_reviewed_facts_20260615.json")
data = json.loads(p.read_text())
print(len(data["facts"]))
print(Counter(f["candidate_route"] for f in data["facts"]))
print(Counter((f["candidate_route"], f["match_status"]) for f in data["facts"]))
print(data["repository_load"])
PY
```

Observed results:

```text
git diff --check: PASS
facts: 25
routes: docling_pdf_candidate=21, pdfplumber_pdf_candidate=4
match statuses: docling exact_match=19, docling normalized_match=2, pdfplumber mismatch=4
repository_load: metadata_source=eid, source_mode=single_source_only, fallback_enabled=False, fallback_used=False, pdf_path=cache/pdf/004393_2025_annual_report_eid.pdf, pdf_cache_hit=False, parsed_cache_hit=True, raw_text_len=61863, section_count=8, table_count=88
```

## 6. Residual Risks

| Residual | Status | Next handling |
| --- | --- | --- |
| Pilot covers one fund/year and selected facts only. | accepted residual | Broader baseline qualification requires multi-sample gate. |
| Reference excerpts are local PDF crop text, not human visual screenshots. | accepted residual | Add visual page review only if future facts are ambiguous. |
| Candidate artifacts are report files, not production repository outputs. | accepted residual | Production integration requires explicit planning and implementation gates. |
| EID HTML current-envelope remains blocked. | accepted residual | Separate EID HTML mapping gate required. |
| Candidate `field_correctness_status` remains `not_proven`. | accepted residual | Pilot result must stay separate from candidate artifact truth flags. |

## 7. Next Gate Recommendation

Recommended next gate:

`Docling Baseline Qualification Closeout / Truth-doc Sync Gate`

Purpose:

- Sync control/design truth with the accepted bounded 004393 evidence.
- Preserve `NOT_READY`.
- State that Docling is accepted only as a candidate-layer structural locator and selected field-family pilot pass for 004393/2025.
- Keep production integration, repository behavior change, broad baseline qualification, and parser replacement behind later gates.

Deferred gates:

- `Docling Multi-sample Field-family Correctness Expansion Gate`
- `FundDisclosureDocument Candidate Source Production Integration Planning Gate`
- `EID HTML Current-envelope Mapping Gate`
- `Docling Visual-page Ambiguity Review Gate`

## 8. Final Verdict

`VERDICT: ACCEPT_004393_DOCLING_FIELD_FAMILY_CORRECTNESS_PILOT_PASS_NOT_READY`

Do not proceed directly to production implementation, readiness, release, PR, or parser replacement from this verdict.
