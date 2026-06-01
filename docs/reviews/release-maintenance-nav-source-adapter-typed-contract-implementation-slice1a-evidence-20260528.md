# NAV Source Adapter Typed Contract Implementation Slice 1a Evidence

## Scope

- Work unit: NAV repository/source adapter typed contract implementation gate.
- Slice: 1a - Typed Models And Pure Contract Tests only.
- Role: implementation agent; no controller action, no gateflow, no commit, no push, no PR.
- Approved plan artifact: `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`.
- Approved plan commit: `09f0f13`.

## Changed Files

- `fund_agent/fund/data/nav_models.py`
- `fund_agent/fund/data/__init__.py`
- `tests/fund/data/test_nav_repository_contract.py`
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-evidence-20260528.md`

## Implemented Items

- Added NAV Literal domains: `NavType`, `AdjustmentBasis`, `DividendAdjustmentStatus`, `NavIdentityStatus`, `NavCompletenessStatus`, `NavFailureCategory`.
- Added frozen/slotted typed models: `NavSourceMetadata`, `ShareClassMapping`, `FundNavRecord`, `FundNavSeries`.
- Added `NavDataContractError` and alias `NavContractError` with `category`, `message`, `source`, `fund_code`, `cause`.
- Implemented `NavType` / `AdjustmentBasis` compatibility matrix:
  - `unit_nav` / `raw_unit_nav`
  - `accumulated_nav` / `accumulated_nav`
  - `adjusted_nav` / `dividend_adjusted_nav`
  - `total_return_index` / `total_return`
  - `unknown` does not construct a successful series.
- Implemented fail-closed validator invariants for:
  - non-empty records;
  - `record_count == len(records)`;
  - duplicate dates as `integrity_error`;
  - record-level `share_class`, `nav_type`, `adjusted_basis` matching series-level fields;
  - illegal type/basis combinations as `schema_drift`;
  - `adjusted_basis="unknown"` as `adjustment_basis_unknown`;
  - `identity_status="identity_mismatch"` as `identity_mismatch`;
  - non-verified identity forcing `strong_drawdown_evidence_eligible=False`;
  - `requested_code_only` reason mentioning source-returned identity not verified;
  - `raw_unit_nav` forcing strong evidence ineligibility with reason mentioning raw unit NAV, dividend, and total-return basis not proven;
  - no explicit coverage constraints producing `completeness_status="unchecked"`;
  - satisfied explicit constraints producing `completeness_status="complete_enough"`.
- Kept `ShareClassMapping.mapping_evidence` as `tuple[str, ...]` and avoided extractor EvidenceAnchor dependency.
- Added `FundNavRecord.raw_payload` diagnostics-only metadata and excluded it from dataclass equality.
- Re-exported Slice 1a public symbols from `fund_agent/fund/data/__init__.py`.
- Added pure model tests only; no adapter, repository, akshare, SQLite, cache, snapshot, score, quality gate, bond extractor, golden fixture, README, design doc, or control doc changes.

## Validation Results

- `uv run pytest tests/fund/data/test_nav_repository_contract.py -q`
  - Result: pass
  - Output summary: `11 passed in 0.04s`
- `uv run ruff check fund_agent/fund/data/nav_models.py tests/fund/data/test_nav_repository_contract.py fund_agent/fund/data/__init__.py`
  - Result: pass
  - Output summary: `All checks passed!`

No full pytest was run; full validation is reserved for later slice/controller.

## Docs Decision

- README/design/control docs were intentionally not updated in Slice 1a.
- Rationale: this slice only adds typed model contracts and pure tests; approved handoff explicitly deferred README/design/smoke work to later slices.

## Residual Risks

- The typed contract is not wired into `nav_data.py` or repository normalization yet; Slice 1b remains responsible for source adapter metadata and repository normalization.
- Runtime NAV extraction, cache behavior, snapshot schema, score semantics, quality gate semantics, bond extractor behavior, and golden fixtures remain unchanged.
- `drawdown_stress blocker remains unresolved`; this slice does not promote NAV data to strong drawdown evidence and does not解除 any bond-risk blocker.

## Self-check

- Branch: `codex/local-reconciliation`.
- Preflight status: tracked worktree was clean before implementation; only unrelated untracked files were present.
- Scope check: pass. All implementation changes stayed within allowed Slice 1a files.
- Validation check: pass.
- Blocked: no.
