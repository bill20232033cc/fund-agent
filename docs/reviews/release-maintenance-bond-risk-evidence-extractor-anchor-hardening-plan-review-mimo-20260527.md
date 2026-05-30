# Bond Risk Evidence Extractor / Anchor Hardening Plan Review — MiMo

> Date: 2026-05-27
> Role: review worker
> Gate: `bond risk evidence extractor / anchor hardening design gate`
> Reviewed target: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
> Verdict: **PASS**

## Worker Self-Check

### Before Start

- Self-check: pass
- Role confirmed: review worker only, not controller.
- Current gate confirmed: plan review for bond risk evidence extractor / anchor hardening design gate.
- External-state boundary confirmed: no workflow command, no skill, no implementation, no staging, no commit, no PR, no golden promotion.
- Dirty scope confirmed: only pre-existing untracked files; this review writes only the allowed artifact path.

### Before Completion

- Self-check: pass
- Review artifact covers all required review criteria.
- No blocking findings identified.

## Source Of Truth Verification

### AGENTS.md Alignment

- Plan correctly requires Chinese responses, first-principles reasoning, same-source root-cause evidence.
- Plan correctly enforces `FundDocumentRepository` boundary — extractor consumes `ParsedAnnualReport` already loaded through repository; no direct PDF/cache/source-helper access.
- Plan correctly enforces fail-closed fallback for `schema_drift`, `identity_mismatch`, `integrity_error`.
- Plan correctly enforces explicit parameters — `bond_risk_evidence` is an explicit field on `StructuredFundDataBundle`, not hidden in `extra_payload`.
- Plan correctly requires fund type resolution before `preferred_lens` — bond analysis uses bond-lens evidence.
- Plan correctly requires tests to move with implementation boundaries.

### docs/design.md Alignment

- Plan correctly identifies current deterministic MVP path: UI → Service → `fund_agent/fund`.
- Plan correctly does not introduce Host/Agent packages or `dayu.host` / `dayu.engine`.
- Plan correctly preserves FQ0-FQ6 semantics — no threshold, severity, or rule change.
- Plan correctly aligns with bond preferred lens: credit risk, duration, max drawdown, leverage, liquidity, downside experience.

### docs/implementation-control.md Alignment

- Plan correctly positioned within `release maintenance` phase.
- Plan correctly follows the accepted evidence artifact and controller judgment as prerequisite inputs.
- Plan correctly does not enter golden corpus, QDII, FOF, release readiness, or GitHub mutation.

### Code State Verification

Verified against current code:

- `extraction_score.py` lines 114-116: `BOND_RISK_EVIDENCE_CONTRACT_ID`, `BOND_RISK_REPLACEMENT_FIELD_NAME`, `BOND_RISK_EVIDENCE_MISSING_ISSUE_CODE` constants exist and match plan claims.
- `extraction_score.py` lines 148-255: `BOND_RISK_EVIDENCE_GROUPS` with seven groups, all `baseline_blocking=True`, matches plan.
- `extraction_score.py` lines 884-925: `derive_score_applicability_issues` currently emits aggregate missing issue for exact `bond_fund`, matches plan root cause.
- `extraction_score.py` lines 1733-1780: `_bond_risk_evidence_missing_issue` sets all seven groups as `missing_evidence_groups`, matches plan.
- `data_extractor.py` lines 79-123: `StructuredFundDataBundle` has 16 fields, no `bond_risk_evidence`, matches plan claim.
- `extraction_snapshot.py` lines 30-47: `SNAPSHOT_FIELD_ORDER` has 16 entries, no `bond_risk_evidence`, matches plan claim.
- `extractors/models.py` lines 14-34: `EvidenceAnchor` dataclass exists with expected fields, matches plan anchor contract.
- `extractors/models.py` lines 37-51: `ExtractedField` generic dataclass exists, matches plan field placement.
- No existing `BondRiskEvidence` types in `models.py`, confirms this is new work.

## Review Criteria Check

### Motivation

Clear and well-evidenced. Root cause is correctly identified: current scoring excludes equity-style `holdings_snapshot` from bond-fund quality denominators but has no positive replacement record contract. The fix makes real evidence first-class and checkable. No motivation drift observed.

### Architecture Boundaries

- Plan stays within `fund_agent/fund/` boundary.
- No UI/Service/Host/Agent package changes.
- No `dayu.host` or `dayu.engine` introduction.
- Extractor consumes already-parsed `ParsedAnnualReport` from `FundDocumentRepository`.
- Scoring consumes snapshot facts, does not reread annual reports.

### FundDocumentRepository Boundary

Correctly enforced. Extractor receives `ParsedAnnualReport` already loaded; no direct PDF/cache/source-helper calls introduced. Verified in Slice 2 data flow: `ParsedAnnualReport` → group extractors → group records + anchors → `BondRiskEvidenceValue` → `ExtractedField`.

### FQ0-FQ6 Preservation

Explicitly preserved. Quality gate section states "no FQ0-FQ6 semantic change." Score logic changes only affect `bond_risk_evidence_missing` issue emission for unsatisfied groups. `baseline_blocking` remains `True`. No threshold, severity, or rule change.

### No Golden Promotion

Explicitly stated in non-goals. Plan does not enter golden corpus, baseline fixtures, or release readiness.

### Explicit Parameters / No extra_payload

`bond_risk_evidence` is an explicit `ExtractedField[BondRiskEvidenceValue]` on `StructuredFundDataBundle`. No parameters hidden in `extra_payload` or free-form dict.

### Schema/Contract Completeness

- `BondRiskEvidenceValue` schema is fully specified with `schema_version`, `contract_id`, `fund_code`, `report_year`, `groups`, `anchors`, derived id tuples, and `contract_status`.
- `BondRiskEvidenceGroupRecord` schema is fully specified with `group_id`, `status`, `strength`, `summary`, `measurement_kind`, metric fields, `source_anchor_ids`, `na_reason`, `reviewer_note`.
- `BondRiskEvidenceAnchorRef` schema is fully specified with `anchor_id`, `section_id`, `page_number`, `table_id`, `row_locator`, `evidence_role`.
- Type aliases are well-defined: `BondRiskEvidenceStatus`, `BondRiskEvidenceStrength`, `BondRiskEvidenceGroupId`.
- Anchor format `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>` is stable and deterministic.
- Evidence satisfaction rules are explicit: `status in {"accepted", "accepted_absence"}`, compatible `strength`, at least one resolvable anchor.

### Seven Evidence Groups

All seven groups addressed with explicit decisions:

| Group | Decision | Strength | Satisfies? |
|---|---|---|---|
| `duration_rate_risk` | accepted | qualitative_direct | Yes |
| `credit_risk` | accepted | quantitative_direct (preferred) | Yes |
| `leverage_liquidity` | split into roles; strategy text alone = weak | depends on role | Only with actual data |
| `asset_allocation_holdings_mix` | accepted | quantitative_direct | Yes |
| `drawdown_stress` | qualitative intent = weak | qualitative_control_intent | No |
| `redemption_share_pressure` | accepted when class disambiguated | quantitative_direct | Yes (if unambiguous) |
| `convertible_bond_equity_exposure` | accepted_absence | quantitative_absence | Yes |

### Drawdown Qualitative vs Quantitative

Correctly handled. `drawdown_control_intent` alone is `status="weak"`, `strength="qualitative_control_intent"`, and does not satisfy the required group. Group accepted only with `max_drawdown_metric`, `volatility_metric`, or accepted direct stress metric. Safe option selected: weak qualitative text is not enough.

### Leverage Strategy vs Actual Leverage/Repo/Liquidity Data

Correctly handled. `leverage_strategy_text` alone must be `weak` and must not satisfy the group. Satisfaction requires at least one actual leverage/repo/liquidity-risk data anchor, or precise liquidity-risk disclosure plus portfolio liquidity proxy. For `006597`, precise table/row anchors must be normalized before treating as accepted.

### Multi-Share-Class Redemption Pressure

Correctly handled. `status="accepted"` only when share-class selection is deterministic for target fund code or when all-class aggregation is explicitly labelled. Ambiguous class selection produces `status="ambiguous"` and does not satisfy the group. `006597` A share selection uses §2 subordinate fund code/name evidence plus §10 share-change columns.

### Natural score_applicability_issues Behavior

Well-designed. Current behavior: aggregate missing issue for all seven groups. Planned behavior: no issue when all satisfied, partial issue for unsatisfied groups only. This is natural removal by satisfying the contract, not suppression. `baseline_blocking` stays `True` for any emitted issue.

### Implementation Slice Readiness

Seven slices with clear boundaries:

1. **Slice 1 (Model Contract)**: models.py + test. Pure type definitions. Stop: Python version/typing issues.
2. **Slice 2 (Extractor)**: new bond_risk_evidence.py + test. Seven group extractors. Stop: if 006597 leverage/repo rows can't be found.
3. **Slice 3 (Bundle Integration)**: data_extractor.py + test. Add field and call. Stop: if Service/UI params needed.
4. **Slice 4 (Snapshot Projection)**: extraction_snapshot.py + test. Add field row. Stop: if snapshot schema considered heavy.
5. **Slice 5 (Score Applicability)**: extraction_score.py + test. Consume positive record. Stop: if score needs prose parsing.
6. **Slice 6 (Real 006597 Path)**: integration tests. Smoke validation. Stop: if drawdown/leverage can't satisfy.
7. **Slice 7 (Documentation)**: README updates. After code passes.

Each slice has allowed files, invariants, test scenarios, and stop conditions.

### File Ownership

Clear and limited:

- Allowed: `extractors/models.py`, `extractors/bond_risk_evidence.py` (new), `extractors/__init__.py`, `data_extractor.py`, `extraction_snapshot.py`, `extraction_score.py`, corresponding tests, README.
- Not allowed: UI, Service, Host, Agent packages, source orchestration, golden/baseline fixtures, QDII/FOF/110020 artifacts.

### Tests/Validation Coverage

Comprehensive test scenarios described per slice:

- Complete seven-group value validates.
- Missing anchor for accepted group fails validation.
- Weak drawdown-control record not in satisfied ids.
- Explicit absence convertible/equity record is accepted.
- Synthetic table-backed credit risk with row-level anchors.
- Flexible leverage strategy text alone is weak.
- Multi-share-class disambiguation.
- Ambiguous share class stays ambiguous.
- Complete positive record emits no missing issue.
- Weak drawdown emits missing issue only for drawdown_stress.
- Non-bond fund ignores bond_risk_evidence.

Validation matrix includes ruff, pytest with coverage, real network/PDF smoke, rerun snapshot/score/quality-gate.

### Stop Conditions

Every slice has explicit stop conditions:

- Slice 1: Python version/typing issues → ask controller.
- Slice 2: 006597 leverage/repo rows not found → keep weak, report residual.
- Slice 3: Service/UI parameter changes needed → return to controller.
- Slice 4: Snapshot schema extension considered heavy → use note-only, ask controller.
- Slice 5: Score needs prose parsing → return to Slice 4.
- Slice 6: Drawdown/leverage can't satisfy → report residual, don't mark blocker resolved.

### Residual Risk Ownership

Documented:

- Current parser may not expose precise repo/leverage table rows → safe outcome is partial contract.
- Annual report may not contain max drawdown/volatility → safe outcome is weak drawdown_stress.
- Snapshot schema extension → additive only, no removal.
- Field order change → tests assert FQ0-FQ6 effects.
- Real network/PDF smoke is source-dependent → unit tests stay deterministic.

### Overengineering or Under-Specification

Neither. The type model is well-defined with appropriate granularity. The seven group decisions are specific without being over-constrained. The implementation slices are appropriately sized. The snapshot schema extension has a fallback path (note-only) if considered too heavy.

## Findings

No blocking findings.

### Residual Risks (Non-Blocking)

1. **Snapshot schema extension decision**: Plan presents two approaches (explicit dataclass fields vs note-only) and defers the choice to review. This is acceptable for a plan gate — the implementer has clear guidance for both paths. If explicit fields are chosen, it should be documented as a minor schema extension.

2. **Real 006597 drawdown/leverage satisfaction**: The plan honestly acknowledges that `drawdown_stress` and `leverage_liquidity` may remain weak for 006597. This is the correct safe default. The stop condition prevents papering over genuine data limitations.

3. **Coverage threshold**: Validation matrix uses global `--cov-fail-under=50`. New/modified modules should target ≥80% but this is a review target, not a CI gate. Plan correctly documents this distinction per AGENTS.md test strategy.

## Conclusion

**PASS**. The plan is well-structured, evidence-based, and aligned with all source-of-truth documents. It correctly identifies the root cause, defines a complete contract, preserves all existing quality gate semantics, enforces FundDocumentRepository boundaries, and provides clear implementation slices with stop conditions. No blocking findings. Residual risks are appropriately documented and owned.

## Completion Report

- Self-check: pass
- Artifact: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-review-mimo-20260527.md`
- No unrelated files touched/staged
- Verdict: PASS with residual risks documented
