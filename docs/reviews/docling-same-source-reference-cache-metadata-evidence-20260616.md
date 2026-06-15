# Docling Same-source Reference Cache Metadata Evidence - 2026-06-16

Gate: `Docling Same-source Reference Cache Metadata Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`
Verdict: `BLOCKED_UNSAFE_METADATA_NOT_READY`

## Scope

This evidence gate calls only the accepted metadata-only repository facade:

```text
FundDocumentRepository.get_annual_report_reference_metadata(fund_code, year)
```

It does not call `load_annual_report()`, cache internals, PDF path/body access, parsed report body access, live/network/EID acquisition, Docling conversion, pdfplumber export, manual reference review, provider/LLM, analyze/checklist/golden/readiness/release/PR/push/merge, or correctness review.

## Evidence Command

```text
uv run python -c 'import asyncio, json
from fund_agent.fund.documents.repository import FundDocumentRepository
SAMPLES=[("S4","006597",2024),("S5","017641",2024),("S6","110020",2024)]
async def main():
    repo=FundDocumentRepository()
    rows=[]
    for sample_id, fund_code, year in SAMPLES:
        result=await repo.get_annual_report_reference_metadata(fund_code, year)
        rows.append({"sample_id":sample_id,"fund_code":fund_code,"document_year":year,"result":result.to_dict()})
    print(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True))
asyncio.run(main())'
```

Exit code: `0`

## Result Matrix

| Sample | Fund code | Year | Status | Reason | Metadata returned |
| --- | --- | ---: | --- | --- | --- |
| S4 | `006597` | 2024 | `unsafe_metadata` | `selected_source_not_eid` | `null` |
| S5 | `017641` | 2024 | `unsafe_metadata` | `source_not_eid` | `null` |
| S6 | `110020` | 2024 | `unsafe_metadata` | `source_not_eid` | `null` |

Raw command output:

```json
[
  {
    "document_year": 2024,
    "fund_code": "006597",
    "result": {
      "metadata": null,
      "reason": "selected_source_not_eid",
      "status": "unsafe_metadata"
    },
    "sample_id": "S4"
  },
  {
    "document_year": 2024,
    "fund_code": "017641",
    "result": {
      "metadata": null,
      "reason": "source_not_eid",
      "status": "unsafe_metadata"
    },
    "sample_id": "S5"
  },
  {
    "document_year": 2024,
    "fund_code": "110020",
    "result": {
      "metadata": null,
      "reason": "source_not_eid",
      "status": "unsafe_metadata"
    },
    "sample_id": "S6"
  }
]
```

## Interpretation

The accepted metadata-only contract returns `available` only when local cache metadata satisfies exact identity and current EID single-source/no-fallback policy.

All three expansion samples returned `unsafe_metadata`, so this gate does not establish same-source reference availability for S4/S5/S6.

This does not prove that EID source is unavailable for those funds or years. It only proves that the current local cache metadata cannot be accepted as no-live same-source reference proof for the Docling multi-sample correctness expansion.

## Non-claims

- Not source truth.
- Not field correctness.
- Not full correctness.
- Not Docling baseline promotion.
- Not production parser replacement.
- Not readiness/release proof.
- Not proof that EID lacks public annual reports for these funds.
- Not authorization for live/EID/PDF acquisition.

## Residuals

| Residual | Owner | Handling |
| --- | --- | --- |
| S4/S5/S6 same-source reference proof remains absent | Controller / future evidence gate | Requires controlled same-source reference acquisition or accepted artifact route before correctness review. |
| Local cache metadata is unsafe for S4/S5/S6 | Future cache/evidence owner | Do not treat candidate Docling/pdfplumber JSON as reference proof. |
| Multi-sample correctness expansion remains blocked | Controller | Do not resume correctness review. |

## Next Gate Recommendation

Proceed to a controller decision gate. Viable routes:

1. Keep multi-sample correctness expansion blocked.
2. Authorize a controlled same-source reference acquisition/evidence gate for S4/S5/S6.
3. Narrow the Docling baseline qualification to the accepted `004393 / 2025` pilot and defer broader baseline claims.

Do not proceed directly to correctness review, production parser replacement, Docling baseline promotion, readiness, release, PR, push or merge.

## Final Verdict

```text
VERDICT: BLOCKED_UNSAFE_METADATA_NOT_READY
```
