# P4 Final Aggregate Deepreview — AgentGLM

> **Reviewer**: AgentGLM (independent)
> **Date**: 2026-05-20
> **Gate**: P4 final aggregate deepreview
> **Previous gate**: P4 readiness reconciliation accepted

---

## Verdict: **PASS**

No blocking findings. P4 accepted functional scope is coherent and meets its declared success signals. The 6 deferred items are tracked with concrete owner labels in both the readiness reconciliation and the control docs. Draft PR readiness requires a scope hygiene pass before `ready-to-open-draft-PR`.

---

## 1. Findings

Ordered by severity.

### F1 [info] f-string without placeholder in test

**File**: `tests/fund/documents/test_cache.py:124`
**Evidence**: `ruff check .` reports `F541 f-string without any placeholders` on `(f"annual_report:110011:2024",)`.
**Severity**: info — source code (`fund_agent/`) passes ruff clean; this is a test-only style issue.
**Recommendation**: Remove `f` prefix before draft PR. One-line fix.

### F2 [info] untracked runtime/infra artifacts in worktree

**Evidence**: `git status` shows untracked `reports/`, `launchd/`, `scripts/`, `report-004393.md`, and older review artifacts not part of P4 scope.
**Severity**: info — these files are not P4 deliverables.
**Recommendation**: Before `ready-to-open-draft-PR`, the controller must explicitly define the PR inclusion set per RR-17:
- Include: 28 modified tracked files (source, tests, README, control docs) + P4 review artifacts under `docs/reviews/`.
- Exclude: `reports/`, `launchd/`, `scripts/`, `report-004393.md`, `.DS_Store`.
- Treat `uv.lock` as a separate scope item: it reflects `pytest-cov` dev dependency from P3-S7, not P4 code changes.

### F3 [info] `extraction_score.py` line count is high

**File**: `fund_agent/fund/extraction_score.py` — 1348 lines
**Severity**: info — the module is coherent and well-structured with clear dataclass boundaries and single-responsibility functions. No domain logic leaks to Service/UI.
**Recommendation**: No action required for P4. Future slices adding more correctness sub-fields may want to split the correctness comparison into a separate module.

---

## 2. Focus Question Answers

### Q1: Are P4 success signals actually met?

**Yes.** Verified:

| Signal | Evidence |
|---|---|
| Tests pass | `171 passed` (full suite) |
| Source lint clean | `ruff check fund_agent/` — All checks passed |
| Whitespace clean | `git diff --check` — no output |
| Snapshot pipeline | `extraction_snapshot.py` reads CSV, calls `FundDataExtractor.extract(...)`, outputs `snapshot.jsonl` + `summary.md` |
| Score pipeline | `extraction_score.py` computes coverage/traceability + `fund_scores` + correctness, outputs `score.json` + `score.md` + `golden_set.json` |
| Quality gate | `quality_gate.py` consumes `score.json`, evaluates P0/P1 field-level + per-fund + correctness, outputs `quality_gate.json` + `quality_gate.md` |
| Golden answer chain | `golden_answer.py` parses reviewed Markdown → strict JSON with validation; `extraction_score.py` consumes it for correctness comparison |
| Fund type fix | `004393` classified as `active_fund` (verified by snapshot and tests) |
| High-impact extractor fixes | 5 fields for `004393` show 100% coverage/traceability in real snapshot |

### Q2: Are deferred risks truly non-blocking and assigned?

**Yes.** All 6 deferred items from readiness reconciliation have concrete owner labels:

| Deferred item | Owner |
|---|---|
| P4-R8 / RR-15: quality gate not attached to `analyze` | `quality gate integration slice` |
| P4-R9: FQ1 App-category branch, FQ4, FQ5 | `quality gate rules slice` |
| RR-16: correctness denominator narrow | `snapshot sub-field exposure slice` |
| `016492` duplicate CSV row | user/App source reconciliation |
| `share_change` multi-share-class | future extractor hardening |
| Completely failed snapshot funds absent from `fund_scores` | snapshot failure accounting |

These are also tracked in `docs/implementation-control-p4.md` risk table (P4-R8, P4-R9) and `docs/implementation-control.md` residual risk table (RR-15, RR-16, RR-17). Not accidentally dropped.

### Q3: Are score.json and quality_gate.json contracts coherent?

**Yes.** Verified by reading both modules end-to-end:

- `extraction_score.py:_score_json_payload()` outputs `field_scores` (list of field-level rows), `fund_scores` (list of per-fund rows), `golden_set`, and `correctness` (with `record_results`).
- `quality_gate.py:_evaluate_score_payload()` reads all three:
  - `_evaluate_field_score()`: P0 fail → FQ2/block, P1 fail → FQ2/warn, low traceability → FQ3/block
  - `_evaluate_fund_score()`: per-fund P0 fail → FQ2F/block with `fund_code`, per-fund P1 fail → FQ2F/warn
  - `_evaluate_correctness()`: correctness unavailable → FQ0/info, mismatch → FQ1/block with expected/actual values

The contract is one-directional and file-based: `score.json` is the sole input to `quality_gate.json`. No circular dependency. No direct filesystem access where repository abstractions are needed — both modules read/write JSONL/JSON at explicit paths.

### Q4: Are layer boundaries respected?

**Yes.** Verified:

- **Capability** (`fund_agent/fund/`): All domain rules live here — extraction, scoring, quality gate, golden answer, analysis engines. `extraction_score.py`, `quality_gate.py`, `golden_answer.py` all declare "Capability 层" in their module docstrings.
- **Service** (`fund_agent/services/`): Thin orchestration only. `ExtractionScoreService.run()` validates request shape and delegates to `run_extraction_score()`. `FundAnalysisService` uses `Protocol` for dependency injection. No domain rules, no direct filesystem access.
- **UI** (`fund_agent/ui/cli.py`): Only input parsing (Typer annotations) and output formatting. Contains `Path` defaults for CLI options but performs no file I/O. No domain logic.
- **No direct filesystem access** where repository abstractions are required. `FundDocumentRepository` is the sole entry for PDF/cache access. P4 modules (`extraction_score`, `quality_gate`, `golden_answer`) operate on explicit file paths, not through repository, which is correct — they process already-produced artifacts, not raw fund documents.

### Q5: Do README/control docs match current behavior?

**Yes.** Verified:

- `README.md` documents all 6 CLI commands (`analyze`, `checklist`, `extraction-snapshot`, `extraction-score`, `golden-prefill`, `golden-build`, `quality-gate`) with correct parameters and output descriptions.
- README correctly notes `checklist` is placeholder, thermometer is not wired to CLI, and real PDF/network smoke is not automated.
- `docs/implementation-control-p4.md` section 10 (status log) matches the readiness reconciliation timeline through 2026-05-20.
- `docs/implementation-control.md` section 5 (residual risks) includes RR-15 through RR-17 with correct owners.
- README does not promise future code beyond explicitly documented "尚未接入" items.

### Q6: Is draft PR readiness blocked?

**Not by code quality**, but by scope hygiene (RR-17):

The worktree contains:
- 28 modified tracked files — these are the P4 deliverables
- ~30 untracked files: runtime outputs (`reports/`), infra scripts (`launchd/`, `scripts/`), historical review artifacts, and `report-004393.md`
- `uv.lock` — dev dependency lock changes from P3-S7

The controller must decide the PR inclusion set before `ready-to-open-draft-PR`. The readiness reconciliation's worktree scope hygiene section provides the framework. This is a process gate, not a code blocker.

---

## 3. Commands Run

```bash
.venv/bin/python -m pytest tests/ -q          # 171 passed in 0.73s
.venv/bin/python -m ruff check fund_agent/     # All checks passed
.venv/bin/python -m ruff check .               # 1 error (test f-string F541)
git diff --check                                # no output (clean)
git status                                      # 28 modified, ~30 untracked
```

Code reading covered:
- `fund_agent/fund/extraction_score.py` (full)
- `fund_agent/fund/quality_gate.py` (full)
- `fund_agent/fund/golden_answer.py` (full)
- `fund_agent/services/extraction_score_service.py` (full)
- `fund_agent/services/fund_analysis_service.py` (first 50 lines)
- `fund_agent/ui/cli.py` (full)
- `fund_agent/fund/template/renderer.py` (first 60 lines)
- `fund_agent/fund/extractors/profile.py` (first 80 lines)
- `fund_agent/fund/analysis/consistency_check.py` (first 50 lines)
- `README.md` (full)
- `docs/design.md` (full)
- `docs/implementation-control.md` (full)
- `docs/implementation-control-p4.md` (full)
- `docs/reviews/p4-readiness-reconciliation-20260520.md` (full)

---

## 4. Accepted Residual Risks

| Risk | Status | Owner |
|---|---|---|
| P4-R8: quality gate not in `analyze` main path | Deferred, tracked | `quality gate integration slice` |
| P4-R9: FQ1 App-category, FQ4, FQ5 unimplemented | Deferred, tracked | `quality gate rules slice` |
| RR-15: quality gate not wired to CLI analyze | Same as P4-R8 | `quality gate integration slice` |
| RR-16: correctness denominator narrow (1 sub-field) | Deferred, tracked | `snapshot sub-field exposure slice` |
| RR-17: draft PR scope hygiene | Pre-PR gate | controller decision |
| `016492` duplicate in CSV | Deferred, non-blocking | user/App source reconciliation |
| `share_change` A/C class ambiguity | Deferred, non-blocking | future extractor hardening |
| Failed snapshot funds absent from `fund_scores` | Deferred, non-blocking | snapshot failure accounting |
| Test f-string lint (F541) | Info, fix before PR | pre-PR cleanup |
