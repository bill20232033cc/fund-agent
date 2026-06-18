# MVP typed template contract Slice 8 docs/control sync code review — MiMo

## Reviewer

- Role: MiMo independent code reviewer
- Gate: `MVP typed template contract Slice 8 Documentation And Control Sync After Accepted Implementation gate`
- Classification: `heavy`
- Date: 2026-06-03

## Scope

Only workspace diff for:
- `fund_agent/fund/README.md`
- `fund_agent/README.md`
- `tests/README.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/reviews/mvp-typed-template-contract-slice8-docs-control-sync-implementation-evidence-20260603.md` (evidence artifact)

No code, test, runtime, schema, quality gate, score, golden/readiness, provider, Host/Agent/dayu or template truth files were modified.

## Checklist

### 1. Scope boundary — PASS

Git diff confirms only the 6 allowed documentation/control files plus the evidence artifact were touched. No unauthorized files modified.

### 2. Git whitespace — PASS

`git diff --check` exited 0 with no output.

### 3. Verification tests — PASS

```
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py -q
16 passed in 0.40s
```

### 4. Slice 1-7 current additive typed facts accuracy

Each document was checked against the accepted Slice 1-7 implementation evidence and the current codebase state:

| Fact | docs/design.md | current-startup-packet.md | implementation-control.md | fund_agent/README.md | fund_agent/fund/README.md | tests/README.md |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| `typed_chapter_contract.v1` sidecar projection | Y | Y | Y | — | Y | — |
| `evidence_availability.v1` same-source derivation | Y | Y | Y | — | Y | — |
| `RequiredOutputItem.when_evidence_missing` writer path | Y | Y | Y | — | Y | — |
| Ch3 evidence-conditional `must_not_cover` | Y | Y | Y | — | — | — |
| Bounded `audit_focus` (semantic-only, not programmatic blocker) | Y | Y | Y | — | Y | — |
| Ch0/Ch7 readiness metadata | Y | Y | Y | — | — | — |
| Service `typed_template_path` explicit wiring | Y | Y | Y | Y | — | Y |
| Slice 7 `ChapterOrchestrator` typed path wiring | — | — | — | — | — | Y |
| Typed sidecar does NOT replace template truth/renderer/defaults | Y | Y | Y | — | Y | — |
| Public chapter ids remain `0-7` | Y | Y | Y | — | Y | — |

All references are accurate and match the accepted implementation evidence.

### 5. Prohibited claims — must NOT be written as current implementation

| Prohibited claim | design.md | startup-packet.md | impl-control.md | fund_agent/README | fund/README | tests/README |
|------------------|:---------:|:------------------:|:----------------:|:-----------------:|:-----------:|:------------:|
| Agent runtime | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean |
| Multi-year runtime | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean |
| Provider budget/default/runtime change | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean |
| Score-loop | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean |
| Ch2 public split | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean |
| Template truth replacement | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean |
| Deterministic default behavior change | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean | ✅ clean |

All documents correctly preserve the non-goal boundaries. Future architecture language consistently uses "accepted future architecture / design-only / unimplemented" framing.

### 6. Control docs do not advance next gate — PASS

- `docs/current-startup-packet.md`: "Next entry point" reads "Review Slice 8 documentation/control sync evidence and decide acceptance; do not advance to any later gate until controller judgment". No gate advanced.
- `docs/implementation-control.md`: Gate status reads "pending review/controller acceptance". "Next entry point" reads same. No next gate claimed.
- Evidence artifact: correctly records "pending review/controller acceptance".

### 7. Specific concern checks

**design.md status header**: Changed from "template typed contract redesign 已接受为 future design，尚未替换当前模板真源或代码" to "typed template contract 的 additive Fund sidecar...已作为当前实现接受，但尚未替换模板真源、deterministic renderer/checklist/analyze 或 Agent runtime". This accurately promotes Slice 1-7 from "future design" to "current additive implementation" while preserving all non-goals. ✅

**design.md §3.2**: Replaced "已接受的未来设计：typed template contract redesign" with "当前已实现：typed template contract additive sidecar" + "当前已实现：same-source EvidenceAvailability" + "当前已实现：Service explicit typed path wiring" + "仍未实现 / 非目标". All subsections correctly describe current facts and explicitly list non-goals. ✅

**design.md Route C status**: Added two bullet points for Slice 1-6 and Slice 7 accepted facts. Both correctly describe the implementation without overclaiming. ✅

**implementation-control.md guardrails**: Updated "Template typed contract redesign gate" paragraph from pure "future design" to "Slice 1-7 已把其中的 additive typed path 落为当前实现事实". Correctly preserves "当前模板真源、deterministic renderer/default analyze/checklist、quality gate、provider defaults 和 public chapter ids 0-7 仍未改变". ✅

**fund_agent/fund/README.md**: Changed `audit_focus` description from "数据提示" to "闭集语义提示"; updated primitives boundary from "不实现 chapter orchestrator、repair loop..." to "不实现 Service 用例、provider construction..."; added explicit non-goal paragraph for typed sidecar and EvidenceAvailability. All accurate. ✅

**fund_agent/README.md**: Added paragraph explaining `--use-llm` as the only explicit typed template path with Service passing typed inputs to Fund primitives. Updated Fund writer/auditor boundary to include typed required-output items, EvidenceAvailability, and audit_focus in their known inputs. Updated execution_contract description to include `typed_template_path`. All accurate. ✅

**tests/README.md**: Updated `test_fund_analysis_service_llm.py` and `test_chapter_orchestrator.py` descriptions to include typed path coverage. Added `pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py -q` verification command. All accurate. ✅

## Adversarial Failure Pass

### Could any diff text be misread as advancing a future gate?

No. All "accepted future architecture" language is preserved. The only status promotion is Slice 1-7 from "future design" to "current additive implementation" — which is exactly what this gate authorizes.

### Could the typed sidecar be mistaken for template truth replacement?

No. Every document that mentions the typed sidecar explicitly states it does not replace template truth, renderer, quality gate, or deterministic defaults.

### Could `audit_focus` be misread as enabling programmatic override?

No. `fund_agent/fund/README.md` clarifies it is "闭集语义提示" that "不能关闭 programmatic blockers、改变阻断等级或修复预算". Design.md also states "closed-set bounded semantic audit input".

### Is the control doc "next entry point" phrasing safe?

Yes. It says "Review Slice 8 documentation/control sync evidence and decide acceptance; do not advance to any later gate until controller judgment". This is a review/acceptance instruction, not a gate advance.

## Residual Risks

None blocking. The following are informational:

1. `docs/implementation-control.md` header version remains "v2.4 / 2026-06-02" — this is outside this gate's scope to change and does not affect correctness.
2. Evidence artifact worker self-check claims "16 passed in 0.74s" vs actual "16 passed in 0.40s" — minor timing variance, not a factual error in the evidence.

## Conclusion

**Accept — No Blocking Findings.**

All 6 documentation/control files accurately describe Slice 1-7 current additive typed template contract facts. No prohibited claims (Agent runtime, multi-year runtime, provider budget/default/runtime, score-loop, Ch2 public split, template truth replacement, deterministic default behavior change) appear as current implementation. Control docs correctly record Slice 8 status as pending review/controller acceptance without advancing any next gate. Verification tests pass (16/16). Git whitespace check clean.
