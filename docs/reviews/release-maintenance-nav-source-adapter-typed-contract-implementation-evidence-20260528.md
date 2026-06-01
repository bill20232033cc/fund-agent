# NAV Source Adapter Typed Contract Implementation Evidence

日期：2026-05-28

## Scope

- Work unit: `NAV repository/source adapter typed contract implementation gate`.
- Slice: Slice 2 - Docs, Design Sync, Real 006597 Smoke Evidence.
- Role: implementation worker, not controller.
- Boundaries: no gateflow start, no review, no commit, no push, no PR, no merge, no release, no golden promotion.
- Control doc: `docs/implementation-control.md` intentionally not edited; controller owns post-closure control update.

## Changed Docs

- `docs/design.md`
  - Added current Fund data typed NAV repository contract near the legacy `NavDataResult` description.
  - Distinguished legacy `NavDataResult` compatibility for `analyze` / `checklist` / snapshot / P1 façade from `FundNavRepository.load_nav_series()` typed boundary.
  - Stated current Akshare / Tiantianfund `单位净值走势` path is `nav_type="unit_nav"`, `adjusted_basis="raw_unit_nav"`, `dividend_adjustment_status="not_adjusted"`, `identity_status="requested_code_only"`, and `strong_drawdown_evidence_eligible=False`.
  - Explicitly did not claim adjusted NAV, cumulative NAV, total-return evidence, or drawdown blocker解除.
- `fund_agent/fund/README.md`
  - Added data-layer description for `FundNavRepository.load_nav_series()` and `FundNavSeries`.
  - Preserved `FundNavDataAdapter.load_nav_data()` as legacy/snapshot/analyze compatible `NavDataResult` entry.
  - Stated raw unit NAV cannot be strong drawdown evidence and does not resolve `drawdown_stress`.
- `tests/README.md`
  - Added `tests/fund/data/test_nav_repository_contract.py` purpose.
  - Clarified deterministic tests use fake adapter and do not require real network.
  - Clarified real 006597 repository smoke is implementation evidence only.

## Real 006597 Smoke

Command intent: load real `006597` only through `FundNavRepository.load_nav_series("006597", minimum_records=30)`.

Access boundary:

- Did not read SQLite directly.
- Did not call Akshare directly.
- Did not bypass adapter/repository.

Note: the one-line command text from the plan was first attempted and failed with Python `SyntaxError` because `async def` cannot appear after a semicolon in the same simple-statement list. This was command syntax only, not repository/source failure. The smoke was rerun with equivalent multi-line `python -c` code and the same repository call.

Smoke JSON:

```json
{
  "fund_code": "006597",
  "share_class": "A",
  "records": 1809,
  "adjusted_basis": "raw_unit_nav",
  "nav_type": "unit_nav",
  "dividend_adjustment_status": "not_adjusted",
  "identity_status": "requested_code_only",
  "strong_drawdown_evidence_eligible": false,
  "source": "nav_cache",
  "origin_source": "akshare",
  "cached": true,
  "cache_updated_at": "2026-05-28 04:04:23.530741+00:00"
}
```

Smoke assertions:

- `fund_code == "006597"`: pass.
- `adjusted_basis == "raw_unit_nav"`: pass.
- `nav_type == "unit_nav"`: pass.
- `dividend_adjustment_status == "not_adjusted"`: pass.
- `identity_status == "requested_code_only"`: pass.
- `strong_drawdown_evidence_eligible is False`: pass.
- Cache provenance preserves `origin_source="akshare"`: pass.

## Validation

```bash
uv run ruff check .
```

Result: pass.

Output summary:

```text
All checks passed!
```

```bash
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

Result: pass.

Output summary:

```text
893 passed in 4.37s
Required test coverage of 50% reached. Total coverage: 92.40%
```

## Docs Decision

The docs were updated only to reflect current implemented code facts:

- Typed NAV repository contract exists in Fund data layer.
- Legacy `NavDataResult` remains compatibility surface.
- Current Akshare path is raw unit NAV only.
- Raw unit NAV and requested-code-only identity are not strong drawdown evidence.

The docs intentionally do not claim:

- adjusted NAV availability;
- cumulative NAV availability;
- total-return basis;
- verified source-returned identity;
- `drawdown_stress` acceptance or blocker解除.

## Non-Goal Preservation

- `docs/implementation-control.md` not edited.
- Snapshot schema not changed.
- Score policy not changed.
- Quality gate / FQ0-FQ6 semantics not changed.
- Bond risk extractor not changed.
- Renderer output not changed.
- Service / CLI behavior not changed.
- Host / Agent / Dayu packages not created or modified.
- Golden / baseline fixtures not promoted.
- Snapshot, score, and quality gate were not rerun because Slice 2 changed only docs/evidence and did not touch those paths.

## Residuals

- `drawdown_stress` blocker remains unresolved.
- Current 006597 typed repository smoke proves raw-unit-only typed path reachability, not adjusted or total-return drawdown evidence.
- Current source identity remains `requested_code_only`; strong drawdown evidence requires future verified identity and accepted adjusted / total-return basis.
- Cache provenance remains limited to existing adapter metadata (`origin_source`, `cache_updated_at`).
