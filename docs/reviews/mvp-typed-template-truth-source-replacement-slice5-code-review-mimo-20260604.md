# MVP typed template truth-source replacement Slice 5 code review (AgentMiMo)

## Gate context

- Gate: `MVP typed template truth-source replacement gate`
- Classification: `heavy`
- Slice: Slice 5, Documentation/control sync
- Reviewer: AgentMiMo
- Review date: 2026-06-04
- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Accepted plan: `266e18f`
- Accepted Slice 1: `3c2b237`
- Accepted Slice 2: `0263bc2`
- Accepted Slice 3: `202b396`
- Accepted Slice 4: `e613876`

## Verdict

**PASS** — no blocking findings.

## Scope reviewed

- `docs/design.md` diff
- `docs/implementation-control.md` diff
- `docs/current-startup-packet.md` diff
- `fund_agent/fund/README.md` diff
- `tests/README.md` diff
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice5-implementation-evidence-20260604.md`

Read-only validation commands executed independently:

```text
uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q
46 passed in 0.75s

git diff --check -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md tests/README.md
exit 0, no output

rg for forbidden stale claims:
docs/implementation-control.md:414 only match — historical ledger row for superseded Slice 8 gate, not current gate/status/startup entry. Acceptable.
```

## Review-focus checklist

### 1. Docs reclassify template truth-source replacement as current implemented fact

PASS.

- `docs/design.md` line 5 (status): correctly says "typed template truth-source replacement Slices 1-4 已把...变成当前...authored Fund template contract truth source" and lists what is unchanged.
- `docs/design.md` line 6 (变更摘要 v2.10): correctly describes `contracts.py` and `typed_contracts.py` projecting from the same JSON.
- `docs/design.md` line 176: full section correctly reclassified from "typed template contract additive sidecar" to "typed template truth-source replacement" as current implemented fact.
- `docs/implementation-control.md` line 9: current state correctly describes truth-source replacement as current fact with all checkpoint references.
- `docs/implementation-control.md` lines 52, 117: correctly state the truth-source arrangement.
- `docs/current-startup-packet.md`: correctly updated current gate and phase goal.
- `fund_agent/fund/README.md` line 116: correctly says canonical JSON is authored truth source.
- `tests/README.md` lines 49-50: correctly updated test descriptions.

No file still describes the template truth-source replacement as future design, additive sidecar, or pending gate.

### 2. Docs state docs/fund-analysis-template-draft.md canonical TEMPLATE_CONTRACT_MANIFEST_JSON is the authored truth source

PASS.

Found in all five docs files at the expected locations: `docs/design.md` lines 5, 6, 154, 166, 176, 513; `docs/implementation-control.md` lines 9, 20, 52, 117, 339; `docs/current-startup-packet.md` phase goal and current implementation facts; `fund_agent/fund/README.md` lines 116-119, 379, 388; `tests/README.md` lines 49-50, 245.

### 3. Docs state contracts.py parses/projects/validates untyped, typed_contracts.py projects/validates typed from same JSON

PASS.

- `docs/design.md` line 154: "contracts.py 解析、投影并验证 untyped TemplateContractManifest; typed_contracts.py 从同一 JSON 投影并验证 typed dataclasses".
- `docs/implementation-control.md` line 52: "contracts.py 从该 JSON 解析、投影并验证 untyped TemplateContractManifest; typed_contracts.py 从同一 JSON 投影并验证 typed_chapter_contract.v1 dataclasses".
- `fund_agent/fund/README.md` lines 118-119: correctly describes both modules' roles.
- `tests/README.md` lines 49-50: correctly describes both test files.

### 4. Current gate, checkpoints, and next entry point are concise and correct

PASS.

- `docs/implementation-control.md` line 9: current gate is "Slice 5 Documentation/control sync" with all five checkpoint references. Concise and correct.
- `docs/implementation-control.md` lines 65-72: table correctly shows current gate, classification, status, and next entry point. No long historical append in the current gate section.
- `docs/current-startup-packet.md`: correctly shows gate status and next entry point. Prohibited actions are exhaustive.
- `docs/implementation-control.md` line 117: Gate Objective correctly describes the current gate scope and prohibited actions. No stale "stop at ready-to-open-draft-PR" language in current gate section.

### 5. Fund README and tests README align with current source-of-truth and test coverage

PASS.

- `fund_agent/fund/README.md`: correctly describes `docs/fund-analysis-template-draft.md` canonical JSON as truth source; `contracts.py` and `typed_contracts.py` as parsers/projectors; validation wording updated from "reviewed exact mapping" to "strict parser/projection validation"; non-goals section updated to remove "不替换模板真源" (now replaced by the truth-source replacement being current fact).
- `tests/README.md`: correctly updated `test_contracts.py` description to "template truth-source parser / untyped projection 测试"; correctly updated `test_typed_contracts.py` description to include code-authored truth symbol absence, stale source_manifest, JSON-driven projection, unknown requirement id, and malformed typed values; added combined test command; updated testing rules to include "不得触发 live provider probe、真实 API key、Host/Agent runtime 或网络".

### 6. Docs preserve non-goals/deferred state

PASS.

- Agent runtime: `docs/design.md` line 5 "尚未实现"; `docs/implementation-control.md` line 9 "不得进入...Agent runtime implementation"; `docs/current-startup-packet.md` "Agent runtime implementation is not current scope".
- Multi-year runtime: all docs correctly list as future design.
- Provider/default/runtime/live probe: all docs correctly list as prohibited.
- Score-loop: all docs correctly list as deferred.
- Ch2 public split: all docs correctly preserve "0-7" and Ch2 internal subcontracts.
- Deterministic analyze/checklist behavior: all docs correctly state unchanged.
- Quality/golden/readiness promotion: all docs correctly state no change.
- PR/push/release/external state: `docs/implementation-control.md` line 72 and `docs/current-startup-packet.md` correctly prohibit.
- Public chapter ids 0-7: confirmed unchanged across all docs.

### 7. Evidence validation adequacy

PASS.

- 46 template tests: independently verified pass.
- Docs self-check: 26 required assertions, 11 forbidden overclaims; all pass.
- Targeted grep: current truth-source statements found in all five files; forbidden stale claims absent from current gate/status/startup entries.
- Diff-check: `git diff --check` exit 0.
- Whitespace self-check: exit 0.

## Findings

No blocking findings.

### LOW findings

**L1: Historical Slice 8 ledger row retains "additive sidecar/current typed path facts" wording**

- File: `docs/implementation-control.md` line 414
- The historical `MVP typed template contract Slice 8` ledger row still says "additive sidecar/current typed path facts while preserving template truth". This is accurate for that historical gate but could be read as contradicting the current truth-source replacement fact.
- Impact: none on current gate correctness. Historical ledger rows are evidence chain and should not be rewritten. The current gate/status/startup sections in the same file clearly supersede this wording.
- Recommendation: no change required. If future cleanup is desired, a parenthetical "(superseded by truth-source replacement gate)" could be appended, but this is not blocking.

**L2: docs/design.md date unchanged at 2026-06-02**

- File: `docs/design.md` line 4
- The date remains `2026-06-02` while the version was bumped to `v2.10`. The date likely reflects the original design document date rather than the latest content revision date.
- Impact: none. The version bump to v2.10 and the changed content in status/变更摘要 sections make the current state clear. The date field convention appears to be "document creation date" rather than "last revision date".
- Recommendation: no change required unless the project convention is to update the date on each content revision.

**L3: current-startup-packet.md "do not enter phaseflow stabilization" wording differs slightly from implementation-control.md**

- File: `docs/current-startup-packet.md` next entry point says "do not enter phaseflow stabilization, provider/runtime/live probe, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/push/release".
- File: `docs/implementation-control.md` line 72 says "do not enter phaseflow stabilization, provider/runtime/live probe, Agent runtime implementation, multi-year runtime, score-loop, golden/readiness, PR/push/release".
- The startup-packet omits "implementation" after "Agent runtime" while the control doc includes it. Both are semantically equivalent.
- Impact: none. Both correctly prohibit Agent runtime work.
- Recommendation: no change required. Minor phrasing variance between summary and detailed control doc is acceptable.

## Validation reviewed from evidence

Reviewer independently verified:

1. `uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q` — 46 passed.
2. `git diff --check` on all five docs files — exit 0, no output.
3. Grep for forbidden stale claims — only `docs/implementation-control.md:414` (historical ledger row) matched; all current gate/status/startup entries clean.
4. Grep for required truth-source statements — found in all five files at expected locations.
5. No code, test source, template JSON, runtime/provider config, golden/readiness, PR state, release state, or external state was modified by this slice.

## Residual risks

| Risk | Status | Detail |
|---|---|---|
| Historical ledger rows retain old additive-sidecar wording | Deferred, non-blocking | Evidence chain rows should not be rewritten; current sections supersede them |
| docs/design.md date field not updated | Deferred, non-blocking | Version bump to v2.10 and content changes make current state clear |
| Minor phrasing variance between startup-packet and control doc | Deferred, non-blocking | Semantically equivalent; both correctly prohibit restricted actions |
| Prior Slice 3/4 non-blocking residuals | Deferred, non-blocking | Ch3 single-year availability, Ch7 readiness rendering polish, TypedTemplatePathMode cleanup, TemplateLensRule naming cleanup, multi-year evidence runtime — all remain future cleanup |

No residual is blocking for this Slice 5 docs-only sync gate.

## Conclusion

**PASS.** All seven review-focus items verified. Docs correctly reclassify template truth-source replacement as current implemented fact, state the canonical JSON as the sole authored template contract truth source, describe contracts.py and typed_contracts.py as parsers/projectors from that JSON, keep current gate concise and correct, align Fund/tests READMEs, preserve all non-goals/deferred state, and pass all validation checks. No blocking findings. One LOW finding (historical ledger row wording) is accepted as non-blocking evidence chain.
