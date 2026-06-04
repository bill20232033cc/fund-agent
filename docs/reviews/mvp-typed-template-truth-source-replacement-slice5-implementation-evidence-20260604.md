# MVP typed template truth-source replacement Slice 5 implementation evidence

## Scope

- Gate: `MVP typed template truth-source replacement gate`
- Slice: Slice 5 Documentation/control sync
- Role: implementation worker, not controller
- Date: 2026-06-04
- Branch observed: `feat/mvp-llm-incomplete-run-artifacts`
- Accepted checkpoints: plan `266e18f`, Slice 1 `3c2b237`, Slice 2 `0263bc2`, Slice 3 `202b396`, Slice 4 `e613876`

## Files changed

- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-typed-template-truth-source-replacement-slice5-implementation-evidence-20260604.md`

No source files, test source files, template JSON, runtime/provider config, golden/readiness artifacts, PR state, release state, or external state were modified.

Unrelated untracked workspace artifacts were observed and intentionally ignored.

## Implementation summary

- Reclassified `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` as the current authored Fund template contract truth source for both untyped and typed projections.
- Documented that `contracts.py` parses/projects/validates the untyped `TemplateContractManifest` from that JSON.
- Documented that `typed_contracts.py` projects/validates typed dataclasses from the same JSON.
- Preserved the explicit non-goals: public chapter ids remain `0-7`; deterministic `analyze/checklist`, renderer output, quality gate, provider/runtime defaults, score/golden/readiness, Agent runtime/tool-loop, multi-year runtime, Ch2 public split, PR/push/release remain unchanged/deferred.
- Kept `docs/implementation-control.md` concise and current-entry focused; fixed one stale line that could have implied the whole current gate did not alter template/manifest authority, narrowing it to Slice 5's docs-only scope.
- Updated `docs/current-startup-packet.md` as a short resume surface matching the control truth.
- Updated `fund_agent/fund/README.md` and `tests/README.md` to align Fund/test documentation with the current template truth-source parser/projection tests.

## Validation

### Required targeted pytest

Command:

```bash
uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q
```

Output:

```text
..............................................                           [100%]
46 passed in 0.61s
```

### Docs self-check

Command:

```bash
uv run python - <<'PY'
from pathlib import Path

files = [
    Path('docs/design.md'),
    Path('docs/implementation-control.md'),
    Path('docs/current-startup-packet.md'),
    Path('fund_agent/fund/README.md'),
    Path('tests/README.md'),
]
texts = {path: path.read_text(encoding='utf-8') for path in files}
required = {
    'docs/design.md': [
        'typed template truth-source replacement',
        'canonical `TEMPLATE_CONTRACT_MANIFEST_JSON`',
        'authored Fund template contract truth source',
        '`contracts.py` 从同一 JSON',
        '`typed_contracts.py` 从同一 JSON',
        'public chapter ids `0-7` 未改变',
        '尚无 Agent runner/tool-loop',
    ],
    'docs/implementation-control.md': [
        'MVP typed template truth-source replacement gate` Slice 5 Documentation/control sync',
        'plan checkpoint `266e18f`',
        'Slice 4 checkpoint `e613876`',
        'canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 已成为 authored Fund template contract truth source',
        '不改变 runtime、score、snapshot、quality gate、golden fixture、golden answer、promotion state、provider defaults、Agent runtime、multi-year runtime、PR/release 或外部状态',
    ],
    'docs/current-startup-packet.md': [
        'MVP typed template truth-source replacement gate` Slice 5 Documentation/control sync',
        'canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` the authored Fund template contract truth source',
        'public chapter ids `0-7`',
        'Agent runtime implementation is not current scope',
        'do not enter phaseflow stabilization, provider/runtime/live probe, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/push/release',
    ],
    'fund_agent/fund/README.md': [
        'canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` 当前是 Fund template contract 的 authored truth source',
        '`fund_agent/fund/template/contracts.py` 解析、投影并验证 untyped `TemplateContractManifest`',
        '`fund_agent/fund/template/typed_contracts.py` 从同一 JSON 投影并验证 typed `TypedChapterContract` dataclasses',
        '公开章节 id 仍严格为 `0-7`',
        '不改变 deterministic `analyze/checklist`、renderer、FQ0-FQ6 quality gate、final judgment、provider/runtime defaults、score/golden/readiness',
    ],
    'tests/README.md': [
        '模板 truth-source parser / untyped projection 测试',
        'typed CHAPTER_CONTRACT projection 测试',
        'template doc canonical JSON parser、untyped projection、typed dataclass projection',
        '不得触发 live provider probe、真实 API key、Host/Agent runtime 或网络',
    ],
}
missing = []
for path, needles in required.items():
    text = texts[Path(path)]
    for needle in needles:
        if needle not in text:
            missing.append(f'{path}: missing {needle}')

forbidden_current = [
    '当前已实现：Agent runtime',
    '当前已实现：Agent runner',
    '当前已实现：multi-year annual evidence runtime',
    '当前已实现：score-loop',
    '当前已实现：golden/readiness',
    '当前入口是 `MVP real LLM',
    '当前入口是 `MVP provider',
    'Current gate | `MVP real LLM',
    'Current gate | `MVP provider',
    'Current gate | `MVP typed template contract aggregate deepreview gate`',
    'Next entry point | Stop at ready-to-open-draft-PR',
]
violations = []
for path, text in texts.items():
    for needle in forbidden_current:
        if needle in text:
            violations.append(f'{path}: forbidden current overclaim {needle}')

if missing or violations:
    print('docs_self_check=FAIL')
    for item in missing + violations:
        print(item)
    raise SystemExit(1)
print('docs_self_check=PASS')
print('checked_files=' + ','.join(str(path) for path in files))
print('required_assertions=' + str(sum(len(v) for v in required.values())))
print('forbidden_current_overclaims=' + str(len(forbidden_current)))
PY
```

Output:

```text
docs_self_check=PASS
checked_files=docs/design.md,docs/implementation-control.md,docs/current-startup-packet.md,fund_agent/fund/README.md,tests/README.md
required_assertions=26
forbidden_current_overclaims=11
```

### Targeted grep checks

Current truth-source statements:

```bash
rg -n 'canonical `TEMPLATE_CONTRACT_MANIFEST_JSON`|authored Fund template contract truth source|contracts\.py.*(untyped|TemplateContractManifest|解析/投影/验证)|typed_contracts\.py.*(same JSON|同一 JSON|typed dataclasses)|public chapter ids `0-7`' docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md tests/README.md
```

Result: exited `0`; matched current truth-source statements in `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`, and `tests/README.md`.

Forbidden current-overclaim grep:

```bash
rg -n 'Current gate \| `MVP typed template contract aggregate deepreview gate`|Next entry point \| Stop at ready-to-open-draft-PR|当前入口是 `MVP real LLM|当前入口是 `MVP provider|当前已实现：Agent runtime|当前已实现：multi-year annual evidence runtime|当前已实现：score-loop|PR/push/release.*已完成' docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md tests/README.md
```

Output:

```text
```

Result: exited `1` because no forbidden current-overclaim matches were found.

Historical sidecar wording containment:

```bash
rg -n 'typed sidecar.*不替换|additive sidecar|尚未替换模板真源|模板真源.*仍未改变|current template truth.*unchanged' docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md tests/README.md
```

Output:

```text
docs/implementation-control.md:414:| `MVP typed template contract Slice 8 Documentation And Control Sync After Accepted Implementation gate` | accepted locally | Implementation/review/controller judgment accepted; docs/control sync promotes Slice 1-7 accepted typed contract facts into current docs as additive sidecar/current typed path facts while preserving template truth, deterministic defaults, provider/runtime defaults, public chapter ids `0-7`, Host business opacity and future-only Agent/runtime/multi-year/score-loop boundaries. DS/MiMo found no blocking findings | Create accepted Slice 8 checkpoint, then start aggregate deepreview for completed typed template implementation slices; no provider/runtime/live probe/Agent runtime/score-loop |
```

Result: exited `0`; the only remaining old sidecar/template-truth-preserved wording is a historical ledger row for the superseded Slice 8 gate, not the current gate/status/startup entry.

### Whitespace / patch check

Required command:

```bash
git diff --check -- docs/design.md docs/implementation-control.md docs/current-startup-packet.md fund_agent/fund/README.md tests/README.md docs/reviews/mvp-typed-template-truth-source-replacement-slice5-implementation-evidence-20260604.md
```

Output:

```text
```

Result: exited `0`.

Note: `docs/reviews/mvp-typed-template-truth-source-replacement-slice5-implementation-evidence-20260604.md` is intentionally untracked before review/controller judgment, so Git's regular diff check does not inspect its content. A supplementary read-only whitespace self-check covered the untracked evidence artifact:

```bash
uv run python - <<'PY'
from pathlib import Path
files = [
    Path('docs/design.md'),
    Path('docs/implementation-control.md'),
    Path('docs/current-startup-packet.md'),
    Path('fund_agent/fund/README.md'),
    Path('tests/README.md'),
    Path('docs/reviews/mvp-typed-template-truth-source-replacement-slice5-implementation-evidence-20260604.md'),
]
issues = []
for path in files:
    for lineno, line in enumerate(path.read_text(encoding='utf-8').splitlines(), start=1):
        if line.endswith((' ', '\t')):
            issues.append(f'{path}:{lineno}: trailing whitespace')
if issues:
    print('whitespace_self_check=FAIL')
    print('\n'.join(issues))
    raise SystemExit(1)
print('whitespace_self_check=PASS')
print('checked_files=' + ','.join(str(path) for path in files))
PY
```

Output:

```text
whitespace_self_check=PASS
checked_files=docs/design.md,docs/implementation-control.md,docs/current-startup-packet.md,fund_agent/fund/README.md,tests/README.md,docs/reviews/mvp-typed-template-truth-source-replacement-slice5-implementation-evidence-20260604.md
```

## Residual risks

- This Slice 5 did not rerun full service/UI/provider/Host suites because the allowed scope is docs/control sync plus the required template contract targeted tests.
- Historical ledger rows still mention the prior additive sidecar/template-truth-preserved state for older accepted gates; current gate/status/startup/design sections now supersede that wording and point to the truth-source replacement gate.
- Prior non-blocking residuals remain future cleanup unless separately authorized: Ch3 single-year availability limitations, Ch7 readiness metadata rendering polish, duplicate `TypedTemplatePathMode` literal cleanup, `TemplateLensRule` naming cleanup, and future multi-year evidence runtime.
