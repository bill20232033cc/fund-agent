# Evidence Confirm Productionization Release/readiness RR-S3 Provider Semantic Evidence

## Verdict

`RR_S3_PROVIDER_SEMANTIC_EVIDENCE_PASS_NOT_READY`

## Scope

- Work unit: `Evidence Confirm Productionization Release/readiness`
- Gate: `RR-S3 - Provider-backed Semantic Quality Evidence Gate`
- Classification: `heavy`
- User authorization: RR-S3 provider-backed semantic evidence execution only
- Explicitly not authorized: push, PR mutation, mark-ready, merge, request reviewers, release
- Runtime output directory: `reports/live-evidence/evidence-confirm-release-readiness-rr-s3-20260623/`
- Release/readiness state after this evidence: `NOT_READY`

## Implementation Boundary

New Service-owned adapter:

- `fund_agent/services/evidence_confirm_semantic_provider.py`
- `tests/services/test_evidence_confirm_semantic_provider.py`
- `tests/README.md`

Accepted boundary:

- The adapter maps typed `LLMProviderConfig` to the Fund-layer `EvidenceEntailmentClient` Protocol.
- The adapter uses current OpenAI-compatible provider contracts only.
- It does not read `FundDocumentRepository`, PDFs, cache paths, parser artifacts, source helpers, Service analysis objects, UI, Host runtime, renderer or quality gate internals.
- It does not change provider defaults, model defaults, retry defaults, timeout budgets, Evidence Confirm deterministic policy or release state.
- It returns only closed semantic status/reason values: `entailed`, `contradicted`, `insufficient`, `not_applicable`.
- Provider failures and malformed responses fail closed through sanitized `EvidenceSemanticProviderError`.

## Deterministic Validation

Commands:

```bash
uv run pytest tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate_integration.py tests/services/test_evidence_confirm_semantic_provider.py -q
uv run ruff check fund_agent/fund/evidence_confirm_semantic.py fund_agent/services/evidence_confirm_semantic_provider.py tests/fund/test_evidence_confirm_semantic.py tests/services/test_evidence_confirm_semantic_provider.py
git diff --check -- fund_agent/fund/evidence_confirm_semantic.py fund_agent/services/evidence_confirm_semantic_provider.py tests/fund/test_evidence_confirm_semantic.py tests/services/test_evidence_confirm_semantic_provider.py tests/README.md
```

Results:

- `49 passed in 0.68s`
- `ruff`: `All checks passed!`
- `git diff --check`: passed

The no-live tests prove:

- deterministic V2 failures still stop semantic provider execution;
- a deterministic V2 pass can receive injected semantic `entailed`, `contradicted` or `insufficient` judgments;
- provider adapter errors do not leak API key, prompt, excerpt or response body;
- malformed provider content and invalid status/reason pairs fail closed.

## Provider Preflight

Safe config preflight output:

```json
{"api_key_env_var": "FUND_AGENT_LLM_API_KEY", "api_key_present": true, "base_url_host": "api.deepseek.com", "config_status": "ready", "model": "deepseek-v4-flash", "provider": "openai_compatible", "timeout_seconds": 60.0}
```

No API key value, prompt, excerpt, provider body, request body or raw header was printed.

## Provider-backed Semantic Probe

Command shape:

```bash
uv run python - <<'PY'
# Builds build_evidence_entailment_client(load_llm_provider_config_from_env()).
# Sends three bounded synthetic EvidenceEntailmentRequest cases.
# Writes safe JSONL summary only.
PY
```

Runtime evidence:

- `reports/live-evidence/evidence-confirm-release-readiness-rr-s3-20260623/provider-semantic-results.jsonl`

Summary:

```json
{"all_calls_ok": true, "all_matched_expected_status": true, "case_count": 3, "output_path": "reports/live-evidence/evidence-confirm-release-readiness-rr-s3-20260623/provider-semantic-results.jsonl", "statuses": ["entailed", "contradicted", "insufficient"]}
```

Provider result table:

| Case | Expected | Actual | Reason | Matched |
|---|---|---|---|---|
| `entailed-turnover-rate` | `entailed` | `entailed` | `entailed_by_excerpt` | true |
| `contradicted-turnover-rate` | `contradicted` | `contradicted` | `contradicted_by_excerpt` | true |
| `insufficient-peer-comparison` | `insufficient` | `insufficient` | `insufficient_excerpt_support` | true |

This proves the provider-backed semantic adapter can obtain the three required semantic outcomes from the configured OpenAI-compatible provider for bounded claim/excerpt inputs. It does not prove field correctness, report-body rendering, checklist support, annual-period display readiness, PR readiness, merge readiness or release readiness.

## Redaction / Safety Check

Command:

```bash
rg -n "报告期内|年报明确|换手率为120|换手率为50|同类基金|Bearer|api_key|test-secret|provider body|excerpts|claim:" reports/live-evidence/evidence-confirm-release-readiness-rr-s3-20260623/provider-semantic-results.jsonl
```

Result:

- No matches.

The runtime JSONL contains only schema version, case id, provider protocol, model, base URL host, expected/actual closed status, closed reason code and safe message. It does not contain raw prompt, bounded excerpt text, claim text, API key, Authorization header, provider body, response body or PDF/source paths.

## Residuals

| Residual | Owner | Destination |
|---|---|---|
| Release/readiness remains `NOT_READY`; RR-S3 proves provider semantic adapter behavior only. | Controller | RR-S4 through RR-S8 |
| Deterministic V2/source failures remain authoritative and are not overridden by semantic pass. | Evidence Confirm owner | Preserve in RR-S7/RR-S8 readiness disposition |
| Full product CLI deterministic Evidence Confirm can still emit `fail` under `warn` policy. | Evidence Confirm / product owner | Release/readiness disposition |
| Checklist Evidence Confirm support remains intentionally off. | Product owner / Service-CLI owner | RR-S4 |
| Annual-period CLI Evidence Confirm summary display remains unproven. | UI/CLI owner | RR-S5 |
| Report-body Evidence Confirm rendering remains intentionally absent. | Product owner / renderer owner | RR-S6 |
| Visible untracked residue and local-vs-remote divergence remain release/readiness blockers. | Controller / artifact owners | RR-S7 / RR-S8 |
| PR-40 remains draft/open; no push or PR mutation was performed. | Controller | RR-S8 with explicit authorization |

## Decision

RR-S3 provider-backed semantic quality evidence is sufficient for the semantic provider adapter requirement only. It is not sufficient for release/readiness, checklist support, annual-period display, report-body rendering, PR readiness, merge readiness or release readiness.

Proceed to `RR-S4 - Checklist Evidence Confirm CLI/support Gate`. Per accepted plan, default recommendation is Option A: keep checklist Evidence Confirm `off` for this release and write an explicit product-owner/controller deferral artifact.

Do not push, mutate PR-40, mark ready, merge, request reviewers, release, or claim release/readiness.

Completion token: `RR_S3_PROVIDER_SEMANTIC_EVIDENCE_PASS_NOT_READY`
