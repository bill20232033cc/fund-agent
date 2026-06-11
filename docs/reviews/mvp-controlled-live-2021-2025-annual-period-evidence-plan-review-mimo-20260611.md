# Controlled live 2021-2025 annual-period evidence plan — MiMo review

> Reviewer: AgentMiMo
> Date: 2026-06-11
> Gate: `controlled live 2021-2025 annual-period evidence planning gate`
> Reviewed artifact: `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-20260611.md`

## Verdict

**ACCEPT_WITH_FINDINGS**

## Validation performed

- Static review only: read `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, and the plan artifact.
- Verified CLI surface: `fund_agent/ui/cli.py:968` `analyze-annual-period` command and its options match plan's E1/E2 commands.
- Verified service implementation: `fund_agent/services/fund_analysis_service.py:745` `analyze_multi_year_annual()` — traced `quality_gate_policy` parameter flow through CLI → `MultiYearAnnualAnalysisRequest` → inner `analyze()` call.
- Verified `FundAnalysisRequest` defaults and `QualityGatePolicy` literal type.
- No live commands were run. No source/test/runtime behavior was modified.

## Focus question analysis

### 1. Is the future live command matrix bounded enough?

**Yes.** E0 (git status), E1 (CLI help), E2 (one bounded live run), E3 (alternate sample policy requiring controller amendment) form a minimal, explicit matrix. The single sample `004393 / 2025 / 2021-2025` is the lowest-risk starting point. E3's "stop and report" on primary sample failure prevents ad hoc data hunting. The matrix is sufficiently bounded for a controlled live gate.

### 2. Does it preserve EID single-source and prevent fallback re-entry?

**Yes.** Stop conditions at E2 explicitly list Eastmoney, fund-company/CDN, CNINFO, fallback invocation, and non-EID source as hard stop triggers. The command does not pass `--force-refresh` (which would still only refresh EID cache, not change source policy). No source expansion is authorized. EID single-source is preserved.

### 3. Is quality-gate-policy warn acceptable as evidence-only control?

**Yes, with a code-level finding.** Using `warn` to let the live evidence run complete even if quality gate blocks is sound evidence-only control — `warn` makes quality gate a data quality signal rather than an execution blocker, without changing the product default `block` behavior.

However, there is an implementation gap: `analyze_multi_year_annual()` (line 778) creates a `FundAnalysisRequest` for the inner `analyze()` call **without forwarding `quality_gate_policy`**, so the inner call defaults to `"block"` regardless of the CLI's `--quality-gate-policy warn`. The CLI-level `--quality-gate-policy warn` is effectively ignored. See Finding F1.

### 4. Is primary sample 004393 / 2025 / 2021-2025 acceptable?

**Yes.** The plan honestly states that only `004393 / 2024` small-golden proof is currently accepted, and the multi-year path plus 2025 are unproven. Using the same fund code minimizes risk. The plan correctly frames this as a "low-risk starting sample" rather than claiming proven equivalence. E3 handles the 2025-not-yet-published scenario. This is acceptable as a first live sample.

### 5. Are stop conditions and evidence artifact schema sufficient for controller judgment?

**Yes.** The year table (year / role / record_status / failure_category / selected_source / source_mode / fallback_enabled / fallback_used / document identity), cross-year fact summary, negative-action checklist, and residual table provide sufficient metadata for controller judgment. The explicit prohibition on raw PDF/report body content in the durable review artifact is correct. Raw stdout/stderr are captured locally for detailed diagnosis if needed.

## Findings

### F1 — `quality_gate_policy` not forwarded to inner analyze (severity: medium)

**Location**: `fund_agent/services/fund_analysis_service.py:778-792`

`analyze_multi_year_annual()` constructs `FundAnalysisRequest` for the inner `analyze()` call without passing `quality_gate_policy`. The field defaults to `"block"`, so the CLI's `--quality-gate-policy warn` has no effect on the actual quality gate execution.

**Impact**: If target-year 2025 quality gate fails (e.g., not in golden pool, FQ block), the command exits `2` even with `--quality-gate-policy warn`. This contradicts the plan's intent (E2 evidence classification: "Exit `2` from quality gate: quality-gate behavior is not source evidence by itself").

**Recommendation**: Either fix the forwarding (`quality_gate_policy=request.quality_gate_policy` in the inner `FundAnalysisRequest`), or update the plan to acknowledge that `warn` only affects CLI-level non-blocking behavior and the inner `analyze()` will still `block`-default. The latter requires adjusting E2's expected exit code logic.

### F2 — `--force-refresh` strategy not addressed (severity: low)

**Location**: Plan E2 command, CLI `cli.py:1009-1011`

The E2 command does not include `--force-refresh`. If a cached EID PDF or parsed report for `004393/2025` already exists from a prior (possibly different metadata) run, the live evidence gate would reuse it rather than performing a fresh live acquisition.

**Impact**: The evidence gate might not actually prove live EID acquisition if a stale cache satisfies the request.

**Recommendation**: Either (a) add `--force-refresh` to the E2 command to guarantee fresh live acquisition, or (b) explicitly state in the plan that cache behavior is part of the evidence (and the year table's `selected_source` / `source_mode` fields will reflect whether cache or live source was used).

### F3 — E2 expected exit code not specified (severity: low)

**Location**: Plan E2 Evidence classification

The plan lists four exit scenarios (exit 0, exit 2, exit 1, prior-year gaps) but does not specify which is the **expected** exit for the primary sample. The execution worker should know the expected baseline.

**Recommendation**: Add an explicit expected outcome, e.g., "Expected: exit 0 with target-year report, subject to EID availability of 2025 annual report for 004393."

### F4 — Year table parsing mechanism not described (severity: low)

**Location**: Plan E2 Evidence Artifact Schema

The year table schema (year / role / record_status / failure_category / selected_source / etc.) is well-defined, but the plan does not describe how these fields are extracted from the CLI output. The CLI outputs target-year Markdown to stdout and multi-year evidence summary to stderr.

**Recommendation**: Specify that the execution worker should parse stderr's multi-year evidence summary (or the structured `MultiYearAnnualAnalysisResult` fields if accessed programmatically) to populate the year table. The plan currently says "capture stdout and stderr" but does not describe the extraction step.

### F5 — `--valuation-state unavailable` rationale not explained (severity: informational)

**Location**: Plan E2 command

The E2 command passes `--valuation-state unavailable`. This is correct for evidence isolation (avoids triggering thermometer auto-mapping), but the plan does not explain this choice.

**Impact**: None. This is a documentation clarity issue.

## Accepted residuals

| Residual | Classification |
|---|---|
| Multi-year path and 2025 live EID acquisition unproven | Accepted — this is the evidence gate's purpose |
| Full cross-year narrative writer/reporting deferred | Accepted — deferred per startup packet |
| Source identity extension deferred | Accepted — deferred per startup packet |
| Coverage measurement residual | Accepted — deferred per startup packet |

## Deferred candidates

| Candidate | Next gate |
|---|---|
| Alternate sample (if primary 2025 not available) | Controller amendment or separately accepted execution matrix |
| `quality_gate_policy` forwarding fix | May be addressed as part of this gate's implementation or a separate fix gate |

## Explicit statement

No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands were run during this review. No source/test/runtime behavior was modified. No design/control/startup docs were modified. No files were staged, committed, pushed, deleted, moved, archived or cleaned.
