# Docling Controlled Same-source Reference Acquisition Evidence - 2026-06-16

Gate: `Docling Controlled Same-source Reference Acquisition Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`
Evidence verdict: `ACCEPT_ALL_REFERENCES_AVAILABLE_NOT_READY`

## Scope

This evidence executes the accepted bounded acquisition route for S4 `006597 / 2024`, S5 `017641 / 2024`, and S6 `110020 / 2024`.

The evidence used only `FundDocumentRepository` public methods:

1. `get_annual_report_reference_metadata(fund_code, year)` pre-check;
2. `load_annual_report(fund_code, year, force_refresh=True)` only when pre-check was not `available`;
3. `get_annual_report_reference_metadata(fund_code, year)` post-check.

The returned parsed report from `load_annual_report()` was discarded. This evidence did not inspect, quote, compare, serialize or use returned parsed body, sections, tables, text, anchors or PDF paths.

## Command

```bash
uv run python -c 'import asyncio, json, traceback
from fund_agent.fund.documents.repository import FundDocumentRepository
SAMPLES=[("S4","006597",2024),("S5","017641",2024),("S6","110020",2024)]
async def main():
    repo=FundDocumentRepository()
    rows=[]
    for sample_id,fund_code,year in SAMPLES:
        row={"sample_id":sample_id,"fund_code":fund_code,"document_year":year}
        try:
            pre=await repo.get_annual_report_reference_metadata(fund_code, year)
            row["pre_metadata"]=pre.to_dict()
            if pre.status != "available":
                row["acquisition_attempted"]=True
                try:
                    await repo.load_annual_report(fund_code, year, force_refresh=True)
                    row["acquisition_status"]="completed_return_discarded"
                except Exception as exc:
                    row["acquisition_status"]="exception"
                    row["acquisition_exception_class"]=exc.__class__.__name__
                    row["acquisition_exception_message"]=str(exc)
                post=await repo.get_annual_report_reference_metadata(fund_code, year)
                row["post_metadata"]=post.to_dict()
            else:
                row["acquisition_attempted"]=False
                row["acquisition_status"]="skipped_pre_metadata_available"
                row["post_metadata"]=pre.to_dict()
        except Exception as exc:
            row["gate_status"]="unexpected_exception"
            row["exception_class"]=exc.__class__.__name__
            row["exception_message"]=str(exc)
            row["traceback_tail"]=traceback.format_exc().splitlines()[-5:]
        rows.append(row)
    print(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True))
asyncio.run(main())'
```

Command exit: `0`

## Results

| Sample | Fund code | Year | Pre metadata | Acquisition status | Post metadata | Same-source reference proof |
| --- | --- | ---: | --- | --- | --- | --- |
| S4 | `006597` | 2024 | `unsafe_metadata`, reason `selected_source_not_eid` | `completed_return_discarded` | `available` | accepted |
| S5 | `017641` | 2024 | `unsafe_metadata`, reason `source_not_eid` | `completed_return_discarded` | `available` | accepted |
| S6 | `110020` | 2024 | `unsafe_metadata`, reason `source_not_eid` | `completed_return_discarded` | `available` | accepted |

## Accepted Metadata Proof

| Sample | source | selected_source | source_mode | fallback_enabled | fallback_used | report_type | metadata_identity_hash |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S4 | `eid` | `eid` | `single_source_only` | `false` | `false` | `annual_report` | `e6f74fe0902676bf2227c2c7acb00f042d944896cff902b203c6fff5e19ec23f` |
| S5 | `eid` | `eid` | `single_source_only` | `false` | `false` | `annual_report` | `918a36b9ac737117dc66428ed7959bad381c7ff9143d9c9064315cb70d5e79d0` |
| S6 | `eid` | `eid` | `single_source_only` | `false` | `false` | `annual_report` | `a3f33cded28077ededea6038228e3174aadf8e617fb393948fedf31c2f509e26` |

## Raw Output Summary

```json
[
  {
    "sample_id": "S4",
    "fund_code": "006597",
    "document_year": 2024,
    "pre_metadata": {"status": "unsafe_metadata", "reason": "selected_source_not_eid", "metadata": null},
    "acquisition_attempted": true,
    "acquisition_status": "completed_return_discarded",
    "post_metadata": {
      "status": "available",
      "reason": null,
      "metadata": {
        "fund_code": "006597",
        "document_year": 2024,
        "report_type": "annual_report",
        "source": "eid",
        "selected_source": "eid",
        "source_mode": "single_source_only",
        "fallback_enabled": false,
        "fallback_used": false,
        "primary_failure_category": null,
        "metadata_identity_hash": "e6f74fe0902676bf2227c2c7acb00f042d944896cff902b203c6fff5e19ec23f"
      }
    }
  },
  {
    "sample_id": "S5",
    "fund_code": "017641",
    "document_year": 2024,
    "pre_metadata": {"status": "unsafe_metadata", "reason": "source_not_eid", "metadata": null},
    "acquisition_attempted": true,
    "acquisition_status": "completed_return_discarded",
    "post_metadata": {
      "status": "available",
      "reason": null,
      "metadata": {
        "fund_code": "017641",
        "document_year": 2024,
        "report_type": "annual_report",
        "source": "eid",
        "selected_source": "eid",
        "source_mode": "single_source_only",
        "fallback_enabled": false,
        "fallback_used": false,
        "primary_failure_category": null,
        "metadata_identity_hash": "918a36b9ac737117dc66428ed7959bad381c7ff9143d9c9064315cb70d5e79d0"
      }
    }
  },
  {
    "sample_id": "S6",
    "fund_code": "110020",
    "document_year": 2024,
    "pre_metadata": {"status": "unsafe_metadata", "reason": "source_not_eid", "metadata": null},
    "acquisition_attempted": true,
    "acquisition_status": "completed_return_discarded",
    "post_metadata": {
      "status": "available",
      "reason": null,
      "metadata": {
        "fund_code": "110020",
        "document_year": 2024,
        "report_type": "annual_report",
        "source": "eid",
        "selected_source": "eid",
        "source_mode": "single_source_only",
        "fallback_enabled": false,
        "fallback_used": false,
        "primary_failure_category": null,
        "metadata_identity_hash": "a3f33cded28077ededea6038228e3174aadf8e617fb393948fedf31c2f509e26"
      }
    }
  }
]
```

## Interpretation

All three expansion samples now have accepted same-source EID annual-report reference metadata through the repository public boundary.

This unblocks the precondition for a future multi-sample Docling field-family correctness evidence gate. It does not itself perform that correctness review.

## Non-claims

- This is not source truth beyond the metadata fields explicitly shown.
- This is not full field correctness proof.
- This is not Docling value correctness proof.
- This is not taxonomy compatibility proof.
- This is not raw XML/XBRL instance proof.
- This is not production parser replacement.
- This is not Docling baseline promotion.
- This is not readiness/release/PR proof.

## Residuals

| Residual | Owner | Next handling |
| --- | --- | --- |
| Multi-sample Docling field-family correctness remains unexecuted | Controller / evidence owner | Resume multi-sample Docling field-family correctness evidence gate |
| Review-channel residual from planning gate | Controller / agent setup owner | Re-run independent review if channels become available |
| Production integration remains unplanned | Controller / Fund documents owner | Deferred until correctness evidence and baseline disposition |

## Final Verdict

```text
VERDICT: ACCEPT_ALL_REFERENCES_AVAILABLE_NOT_READY
```
