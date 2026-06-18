# Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 3 Post-fix Provider-before ValueError No-live Root-cause Evidence Gate`.

This gate localizes the remaining Chapter 3 provider-before `ValueError` accepted by `docs/reviews/provider-llm-chapter3-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`.

No code fix is implemented in this artifact.

## Guardrails

- No live/provider/LLM/network/source/PDF/FDR/analyze/checklist/readiness/release/PR command was run.
- No source/cache/PDF body was read.
- No writer markdown, auditor feedback markdown, raw prompt or provider payload was read.
- EID remains the single operational source path.
- No Eastmoney, fund-company website, CNINFO or fallback path was introduced.
- `release/readiness` remains `NOT_READY`.

## Evidence Reviewed

Truth/control:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

Accepted live evidence:

- `docs/reviews/provider-llm-chapter3-post-fix-bounded-live-re-evidence-controller-judgment-20260614.md`
- `docs/reviews/provider-llm-chapter3-post-fix-bounded-live-re-evidence-20260614.md`
- `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/summary.json`
- `reports/llm-runs/004393-2025-20260613T182423Z-host_run_c1b20382568e4ae/chapters/chapter-03.json`

Code/test paths used for no-live localization:

- `fund_agent/agent/runner.py`
- `fund_agent/fund/chapter_writer.py`
- `fund_agent/fund/evidence_availability.py`
- `docs/fund-analysis-template-draft.md`
- `tests/agent/test_runner.py`
- `tests/fund/test_chapter_facts.py`

## Live Failure Shape To Match

Accepted live metadata states:

- first failed chapter: `3`
- status: `failed`
- terminal state class: writer/provider-before internal failure
- stop reason: `llm_exception`
- failure category: `code_bug`
- terminal issue class: `ValueError`
- provider attempt count: `0`
- runtime operation: `writer`
- `max_output_chars=12000`

The live artifact does not include the `ValueError` message, so no-live evidence must localize the matching code branch without relying on source/PDF bodies.

## No-live Reproducer A: Baseline Does Not Fail

Command shape:

```bash
uv run python - <<'PY'
from tests.agent.test_runner import _projection, _FakeWriter
from fund_agent.agent.runner import AgentRunPolicy, _run_evidence_availability, _writer_input
from fund_agent.fund.chapter_writer import write_chapter

projection = _projection((3,))
policy = AgentRunPolicy(target_chapter_ids=(3,), max_output_chars=12000, typed_template_path='typed_template_contract')
availability = _run_evidence_availability(projection, policy=policy, evidence_availability=None)
writer_input = _writer_input(projection, chapter_id=3, policy=policy, evidence_availability=availability, repair_context=None)
writer = _FakeWriter()
result = write_chapter(writer_input, llm_client=writer)
print(len(writer.requests))
PY
```

Observed facts:

- `_writer_input()` succeeds for the standard no-live `_bundle()` projection.
- `write_chapter()` reaches the fake writer in that baseline shape.
- This falsifies a blanket failure in `_writer_input()` and shows existing happy/adjacent tests are not live-like enough to reproduce the remaining failure.

Two exploratory script errors occurred while printing non-existent test-only attributes (`required_output_evidence_plan` on `ChapterWriterInput`; `failure_category` on `ChapterWriteResult`). They are excluded from root-cause evidence because they occurred after the product call returned and do not match the live failure.

## No-live Reproducer B: Missing Portfolio Managers Matches The Failure

Command:

```bash
uv run python - <<'PY'
from dataclasses import replace
from tests.agent.test_runner import _FakeWriter
from tests.fund.test_chapter_facts import _bundle
from fund_agent.fund.extractors.models import ExtractedField
from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.agent.runner import AgentRunPolicy, _run_evidence_availability, _writer_input
from fund_agent.fund.chapter_writer import write_chapter

missing_portfolio_managers = ExtractedField(value=None, anchors=(), extraction_mode='missing', note='no-live missing portfolio managers')
projection = project_chapter_facts(replace(_bundle(), portfolio_managers=missing_portfolio_managers), chapter_ids=(3,))
policy = AgentRunPolicy(target_chapter_ids=(3,), max_output_chars=12000, typed_template_path='typed_template_contract')
availability = _run_evidence_availability(projection, policy=policy, evidence_availability=None)
for req in availability.requirements:
    if req.requirement_id.startswith('ch3.required_output.'):
        print('req', req.requirement_id, req.status, req.source_kind, req.source_field_ids)
writer_input = _writer_input(projection, chapter_id=3, policy=policy, evidence_availability=availability, repair_context=None)
print('writer_input_ok', type(writer_input).__name__)
writer = _FakeWriter()
try:
    result = write_chapter(writer_input, llm_client=writer)
    print('write_chapter_result', result.status, result.stop_reason)
    print('writer_requests', len(writer.requests))
except Exception as exc:
    print('write_chapter_exception', type(exc).__name__, str(exc))
    print('writer_requests', len(writer.requests))
PY
```

Observed output:

```text
req ch3.required_output.item_01 missing fact ('structured.basic_identity', 'structured.portfolio_managers')
req ch3.required_output.item_02 available fact ('structured.manager_strategy_text',)
req ch3.required_output.item_06 available fact ('structured.manager_alignment',)
req ch3.required_output.item_03 unreviewed derived ('structured.turnover_rate', 'structured.holdings_snapshot', 'synthetic.cross_period_comparison')
req ch3.required_output.item_04 unreviewed derived ('structured.turnover_rate', 'structured.holdings_snapshot', 'synthetic.cross_period_comparison')
req ch3.required_output.item_05 unreviewed derived ('structured.turnover_rate', 'structured.holdings_snapshot', 'synthetic.cross_period_comparison')
writer_input_ok ChapterWriterInput
write_chapter_exception ValueError typed required output 缺证但未声明 when_evidence_missing：ch3.required_output.item_01
writer_requests 0
```

Interpretation:

- `_writer_input()` succeeds.
- The failure occurs in Fund writer prompt/preflight construction before provider/fake-writer invocation.
- `ch3.required_output.item_01` is non-available because it depends on `structured.basic_identity` and `structured.portfolio_managers`.
- The typed template declares `when_evidence_missing=null` for `ch3.required_output.item_01`.
- `_required_output_action()` raises `ValueError` for non-available status without a declared missing-evidence behavior.
- This directly matches the live provider-before `ValueError` shape and explains why the prior patch did not close the path: it handled missing availability mapping with declared `when_evidence_missing`, not present-but-non-available availability for an item with no missing-evidence behavior.

## No-live Reproducer C: Agent Runner Mapping Matches Live Shape

Command:

```bash
uv run python - <<'PY'
from dataclasses import replace
from tests.agent.test_runner import _FakeWriter, _FakeAuditor
from tests.fund.test_chapter_facts import _bundle
from fund_agent.fund.extractors.models import ExtractedField
from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.agent import AgentLLMClients, AgentRunPolicy, run_agent_body_chapters

missing_portfolio_managers = ExtractedField(value=None, anchors=(), extraction_mode='missing', note='no-live missing portfolio managers')
projection = project_chapter_facts(replace(_bundle(), portfolio_managers=missing_portfolio_managers), chapter_ids=(3,))
writer = _FakeWriter()
run = run_agent_body_chapters(
    projection,
    llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
    policy=AgentRunPolicy(target_chapter_ids=(3,), max_output_chars=12000, typed_template_path='typed_template_contract'),
)
task = run.tasks[0]
print('run_status', run.status)
print('writer_requests', len(writer.requests))
print('task_chapter_id', task.chapter_id)
print('task_status', task.status)
print('terminal_state', task.terminal_state)
print('stop_reason', task.stop_reason)
print('failure_category', task.failure_category)
print('attempts', len(task.attempts))
print('blocked_reasons_repr', repr(task.blocked_reasons))
PY
```

Observed output:

```text
run_status blocked
writer_requests 0
task_chapter_id 3
task_status failed
terminal_state blocked_internal_code_bug
stop_reason llm_exception
failure_category code_bug
attempts 0
blocked_reasons_repr ('3:blocked_internal_code_bug:ValueError',)
```

Interpretation:

- The Agent runner maps the Fund writer `ValueError` into the same high-level live shape: Chapter 3 `failed`, `llm_exception`, `code_bug`, provider/fake-writer calls `0`, attempts `0`.
- This proves the live failure is reproducible no-live without provider/network/source/PDF access.

## Root-cause Classification

Root cause:

`ch3.required_output.item_01` can be present in `EvidenceAvailability` with a non-available status, but the typed template sets `when_evidence_missing=null`. `fund_agent/fund/chapter_writer.py` currently treats that combination as a `ValueError` via `_required_output_action()`, which occurs before provider invocation.

Direct code path:

1. `run_agent_body_chapters()` derives typed `EvidenceAvailability`.
2. `_writer_input()` succeeds and passes typed required-output items plus availability to Fund writer.
3. `write_chapter()` builds required-output evidence plan before calling provider.
4. `_required_output_plan_item()` reads `ch3.required_output.item_01` availability.
5. `_required_output_action()` receives `status=missing` and `item.when_evidence_missing=None`.
6. `_required_output_action()` raises `ValueError("typed required output 缺证但未声明 when_evidence_missing：ch3.required_output.item_01")`.
7. Agent runner maps that to `blocked_internal_code_bug` / `llm_exception` / `code_bug` with zero provider attempts.

## Hypotheses Disposition

| Hypothesis | Disposition | Evidence |
| --- | --- | --- |
| `_writer_input()` construction is the remaining failure source. | REJECT for reproduced branch. | Reproducer B prints `writer_input_ok ChapterWriterInput`; failure occurs later in `write_chapter()`. |
| Fund writer prompt/preflight required-output plan raises before provider. | ACCEPT. | Reproducer B raises `ValueError typed required output 缺证但未声明 when_evidence_missing：ch3.required_output.item_01` with `writer_requests 0`. |
| Provider availability or provider response causes Chapter 3 failure. | REJECT. | Live and no-live evidence both have provider/fake-writer request count `0`. |
| Prior missing-availability mapping patch should have covered this branch. | REJECT. | Prior patch covered missing mapping plus declared `when_evidence_missing`; this branch is present mapping plus non-available status and null behavior. |
| Service/Agent serialization alone causes the failure. | REJECT. | Fund writer reproducer raises before Agent mapping; Agent mapping only projects the failure into the live diagnostic shape. |

## Residuals

| Residual | Next action |
| --- | --- |
| Exact live projection field state is not exposed in safe runtime artifacts. | Do not read source/PDF bodies in this gate. The no-live reproducer proves a same-shape root cause; future diagnostic improvement may include safe field-state emission if needed. |
| The implementation policy for `when_evidence_missing=null` plus non-available availability must be chosen explicitly. | Next implementation gate should decide whether to convert this to `block` / fact-gap or require typed-template behavior for item 01. |
| Provider readiness and LLM content quality remain unproven. | Deferred until Chapter 3 reaches provider and accepted draft/conclusion exists. |
| Release/readiness remains `NOT_READY`. | Separate readiness/release gate only. |

## Verdict

VERDICT: ROOT_CAUSE_PROVEN_READY_FOR_NO_LIVE_FIX_IMPLEMENTATION_GATE_NOT_READY

Recommended next gate:

`Provider/LLM Chapter 3 Required-output Item 01 Missing-evidence No-live Fix Implementation Gate`
