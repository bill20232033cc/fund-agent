# PR Re-review

## Scope

- Mode: targeted PR re-review gate
- Gate: `FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Re-review Gate`
- PR: [#34](https://github.com/bill20232033cc/fund-agent/pull/34) `FundDisclosureDocument core_risk source-truth extraction`
- Base: `funddisclosure-current-stage-source-truth`
- Head: `funddisclosure-core-risk-source-truth`
- Reviewed head: `24c6761f9da81110cc303a187680c952a2c98354`
- Merge state: `CLEAN`
- CI `test`: `SUCCESS`
- Output file: `docs/reviews/pr-34-rereview-ds-20260620.md`
- Included scope: only whether Codex F1 is closed by the uncommitted fix in `docs/current-startup-packet.md`, `docs/implementation-control.md`, and fix evidence `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-pr-review-fix-evidence-20260620.md`; whether any new blocker exists inside the same control-doc scope
- Excluded scope: full PR re-review; code, tests, design docs, README; DS review findings F1/F2 (both low severity, non-blocking, already dispositioned in DS artifact)
- Parallel review coverage: 无

## Source Evidence

### Codex F1 (original finding)

Codex F1 reported that active/current control surfaces in `docs/current-startup-packet.md` and `docs/implementation-control.md` contained stale strings:
- `Implementation Gate Completed Locally`
- `pending code review`
- `Code Review Gate` (as active/current next entry)
- `No commit/stage/push/PR`
- `current_stage.v1 Source-truth Direct Extraction Follow-up Push Gate`
- `core_risk.v1 remains unimplemented` (claimed or implied through missing scope)

These pointed a resumed controller/agent to already-completed gates rather than to the current PR review gate for PR 34.

### Fix applied (uncommitted workspace changes)

Files changed:
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-pr-review-fix-evidence-20260620.md` (fix evidence artifact)

### Verification method

Ran exact command from fix evidence:

```
rg -n "Implementation Gate Completed Locally|pending code review|Code Review Gate|No commit/stage/push/PR|current_stage\.v1 Source-truth Direct Extraction Follow-up Push Gate|core_risk\.v1 remains unimplemented|PR Review Re-review Gate|PR 34" docs/current-startup-packet.md docs/implementation-control.md
```

Read active control surfaces (Current Gate table, Next Entry Point, Resume Checklist) and the Active Gate Ledger section to distinguish active/current surfaces from historical entries.

## Findings

### 未发现实质性问题

Codex F1 is fully closed. All six stale strings are removed from active/current control surfaces. The fix evidence claims are verified against direct file content.

### Verification detail

**1. Active/current next entry routes correctly**

All active/current surfaces now route to `FundDisclosureDocument core_risk.v1 Source-truth Direct Extraction PR Review Re-review Gate`:

| File | Line | Surface type |
|---|---|---|
| `docs/current-startup-packet.md` | 23 | Current active gate field |
| `docs/current-startup-packet.md` | 24 | Gate classification / next entry |
| `docs/current-startup-packet.md` | 63 | Next entry point field |
| `docs/current-startup-packet.md` | 228 | Resume checklist item 5 |
| `docs/implementation-control.md` | 10 | Latest control update banner |
| `docs/implementation-control.md` | 51 | Current Gate table |
| `docs/implementation-control.md` | 105 | Next entry point field |
| `docs/implementation-control.md` | 555 | Resume checklist item 5 |

**2. PR 34 metadata recorded**

PR 34 metadata (URL, base, head, reviewed head `24c6761f9da81110cc303a187680c952a2c98354`, mergeState `CLEAN`, CI `test` `SUCCESS`) is recorded consistently in:
- `docs/current-startup-packet.md:24`
- `docs/current-startup-packet.md:63`
- `docs/current-startup-packet.md:228`
- `docs/implementation-control.md:10`
- `docs/implementation-control.md:51`
- `docs/implementation-control.md:105`
- `docs/implementation-control.md:555`

**3. Stale strings absent from active/current surfaces**

| Stale string | Active/current hits | Historical ledger hits | Status |
|---|---|---|---|
| `Implementation Gate Completed Locally` (for core_risk) | 0 | 0 | Gone |
| `pending code review` | 0 | 0 | Gone |
| `No commit/stage/push/PR` | 0 | 0 | Gone |
| `core_risk.v1 remains unimplemented` | 0 | 0 | Gone |
| `Code Review Gate` | 0 | 14 (entries 57, 86, 94, 95, 141-144, 158-161, 168, 175-176) | Only in numbered historical ledger |
| `current_stage.v1 Source-truth Direct Extraction Follow-up Push Gate` | 0 | 1 (entry 182) | Only in numbered historical ledger |

The `Code Review Gate` hits at `implementation-control.md:169, 198, 207, 253-256, 270-273, 280, 287-288` are all numbered entries in the Active Gate Ledger (`## Active Gate Ledger`), which records completed gates for all work units. These are clearly historical—they describe other work units (S3 Extractor Projection, S5 Facade Integration, return_attribution slices, manager_profile slices, investor_experience, current_stage) and are not active/current control or resume checklist entries.

The `current_stage.v1 Source-truth Direct Extraction Follow-up Push Gate` hit at `implementation-control.md:294` is entry 182 in the same historical ledger.

**4. Scope boundary preserved**

Both control docs explicitly maintain:
- Only `core_risk.v1.risk_characteristic_text` is implemented
- Four deferred roles (`liquidation_or_scale_risk`, `tracking_error_or_deviation_risk`, `turnover_or_style_drift_risk`, `concentration_risk`) remain candidate-only/deferred
- No `StructuredFundDataBundle.core_risk`
- No parser replacement, EvidenceSourceKind expansion, Service/UI/Host/renderer/quality-gate consumption
- No readiness, release, mark-ready, or merge authorized
- No PR mutation authorized

**5. No new blocker in control-doc scope**

No new contradiction, stale string, or scope violation was found in either control doc. The active gate name, classification, PR metadata, next entry point, and non-goals are consistent between the Current Gate table, Latest Control Update banner, Next Entry Point field, and Resume Checklist in both files.

**6. DS review context**

The DS PR review (`docs/reviews/pr-34-review-ds-20260620.md`) returned `PR_REVIEW_PASS` with two low-severity findings (shared label config without explicit decoupling guard; `_core_risk_status()` binary model). Neither is a blocking issue for this re-review gate, and both are already dispositioned in the DS artifact. They do not affect the F1 fix assessment.

## Open Questions

无

## Residual Risk

- The fix is uncommitted. If the workspace is lost before commit, the control docs revert to the stale state that triggered Codex F1. Owner: controller / next gate.
- The DS review's two low-severity findings (shared label config, status semantics) remain open at the PR level. They do not block this re-review gate but remain residual for the PR. Owner: DS findings disposition gate.
- Complete `core_risk.v1` source truth (four deferred roles) remains deferred. Owner: future core_risk multi-subvalue gate.

## Verdict

PR_REREVIEW_PASS
