# MVP typed template truth-source replacement plan

## Worker self-check

- Current gate / role: `MVP typed template truth-source replacement gate`; classification `heavy`; role is planning worker only.
- Actions taken: read required context, branch/status, current template draft, typed contract implementation, writer/auditor/service tests, and accepted controller judgments.
- Actions intentionally not taken: no `/gateflow` or `$gateflow`, no implementation, no review loop, no commit/push/PR, no source/test/template/control doc edit other than this single plan artifact, no provider/runtime/live probe.
- Branch/worktree: current branch is `feat/mvp-llm-incomplete-run-artifacts`; `git status --short` shows multiple unrelated untracked artifacts, including Agent implementation planning artifacts. They are out of scope and must not be staged by this gate.
- Handoff status: code-generation-ready if the controller accepts the implementation decisions below. No blocking question is required before implementation; stop conditions are listed explicitly.

## Goal/motivation

The current accepted typed contract implementation is additive: `typed_contracts.py` projects a typed sidecar from `contracts.py`, while `docs/fund-analysis-template-draft.md` remains the human template draft and does not yet contain the implemented typed mechanisms as the authoritative machine contract.

This gate should replace that additive truth arrangement with a single authored truth source in `docs/fund-analysis-template-draft.md` for the implemented typed mechanisms:

- public chapter ids remain exactly `0-7`;
- current renderer/default deterministic `analyze` and `checklist` behavior remain unchanged;
- current explicit `--use-llm` typed path keeps the same typed inputs and fail-closed behavior;
- `typed_contracts.py` becomes a code projection/validation layer over the template document, not a parallel truth source.

The practical motivation is to remove the current reviewed exact string mapping in code as the de facto stable-id source and make future template edits fail closed at the template truth boundary.

## Non-goals

- No Agent runtime implementation, Agent runner/tool-loop migration, ToolRegistry, ToolTrace, or Agent-side retry/budget implementation.
- No multi-year annual evidence runtime, no prior-year document loading, no quarterly/interim reports.
- No provider budget/default/runtime/endpoint/config change, no provider live probe, no PASS-only timing probe.
- No score-loop, `chapter_generation_score`, golden/readiness promotion, fixture promotion, quality/golden/readiness state change.
- No Ch2 public chapter split; Ch2 `performance / attribution / cost` remains internal typed subcontracts under public `chapter_id=2`.
- No deterministic default `fund-analysis analyze` / `checklist` behavior change, no renderer output change, no FQ0-FQ6 quality gate semantic change.
- No final judgment public contract change and no new “买入/卖出/仓位” behavior.
- No changes to unrelated dirty/untracked artifacts.

## Direct evidence

- `docs/design.md` says typed template contract Slice 1-7 are accepted current implementation facts but are additive and do not replace `docs/fund-analysis-template-draft.md`, `contracts.py`, renderer, quality gate, deterministic defaults, public chapter ids, Agent runtime, multi-year runtime, score-loop, or provider defaults.
- `docs/current-startup-packet.md` records accepted checkpoints through Slice 8 and aggregate deepreview, and explicitly says template truth remains unchanged and public chapter ids remain `0-7`.
- `docs/implementation-control.md` marks the current accepted typed path as additive, with the template truth-source replacement reserved for a separate gate.
- `docs/fund-analysis-template-draft.md` currently contains prose `CHAPTER_CONTRACT` blocks but does not contain stable typed ids, `when_evidence_missing`, Ch2 internal subcontracts, Ch0/Ch7 readiness metadata, or bounded `audit_focus` as machine-readable truth.
- `fund_agent/fund/template/contracts.py` currently owns the untyped machine manifest as Python constants and records `source_path="docs/fund-analysis-template-draft.md"`.
- `fund_agent/fund/template/typed_contracts.py` currently owns typed schema dataclasses plus `_CURRENT_TEXT_MAPPING`, Ch2 internal subcontracts, Ch3 evidence predicate, required-output missing behavior, and audit focus mappings in Python code.
- `fund_agent/fund/evidence_availability.py` derives `evidence_availability.v1` from same-source `ChapterFactProjection` and typed requirement ids, without reading repositories, PDF/cache/source helpers, Service, Host, provider, file system, env, or dayu.
- `fund_agent/fund/chapter_writer.py` consumes typed `RequiredOutputItem.when_evidence_missing` and `EvidenceAvailability` on explicit typed path; Ch2 `block` stops before provider; Ch3 gap/minimum-verification/delete behaviors are tested.
- `fund_agent/fund/chapter_auditor.py` consumes typed Ch3 `ch3.must_not_cover.item_04` evidence-conditional semantics programmatically; `audit_focus` is LLM semantic-only and does not disable programmatic blockers.
- `tests/fund/template/test_typed_contracts.py`, `tests/fund/test_evidence_availability.py`, `tests/fund/test_chapter_writer.py`, `tests/fund/test_chapter_auditor.py`, and `tests/services/test_chapter_orchestrator.py` already encode the accepted typed behavior.
- `docs/reviews/mvp-typed-template-contract-slice8-docs-control-sync-controller-judgment-20260603.md` accepts docs/control sync and preserves the residual: typed sidecar remains additive and any future replacement needs a separate template truth/public contract gate.
- `docs/reviews/mvp-typed-template-contract-aggregate-deepreview-controller-judgment-20260603.md` accepts the implementation family after fixing Ch3 typed must-not-cover bypass; it explicitly preserves no template truth replacement as a non-goal of that completed gate.

## Current/future/deferred classification table

| Item | Classification for this gate | Plan decision |
|---|---|---|
| Public chapter ids `0-7` | Current implemented fact | Preserve exactly; tests fail if any public id is added, removed, split, or reordered. |
| Untyped `ChapterContract` API | Current implemented fact | Keep as public compatibility projection from template doc. |
| `typed_chapter_contract.v1` stable ids | Current implemented fact | Move authored stable ids into template doc; code validates/projects them. |
| Ch2 `performance / attribution / cost` | Current implemented fact | Keep as internal subcontracts under `chapter_id=2`; not public chapters. |
| Ch3 evidence-conditional `must_not_cover.item_04` | Current implemented fact | Author predicate and allowed contexts in template doc; programmatic audit behavior unchanged. |
| `RequiredOutputItem.when_evidence_missing` | Current implemented fact | Author current Ch2/Ch3 missing behavior in template doc; writer behavior unchanged. |
| `EvidenceAvailability` same-source derivation | Current implemented fact | Keep code derivation; it reads typed requirement ids from projected typed manifest. |
| Ch0 consumes Ch7 and cannot independently derive action | Current implemented fact | Author metadata in template doc; final assembly behavior unchanged. |
| `audit_focus` | Current implemented fact | Author closed-set focus values in template doc; semantic-only status remains explicit. |
| Service `typed_template_path="typed_template_contract"` | Current implemented fact | Preserve explicit `--use-llm` path only; no deterministic path change. |
| Template doc as machine truth source | Accepted but unimplemented design for this gate | Implement in this gate after plan acceptance. |
| Agent engine/tool-loop migration | Accepted future design | Deferred; do not implement or document as current runtime. |
| Multi-year annual evidence | Accepted future design | Deferred; keep current single-year availability behavior. |
| Provider runtime calibration | Accepted future evidence/design | Deferred; no live probe or default change. |
| Ch2 public split / `0+9` / `0+10` chapter model | Deferred/rejected for this gate | Explicitly disallow. |
| `source_strength_by_requirement`, full facet wiring, score-loop | Deferred | Do not add schema or tests in this gate. |

## Affected files/modules

Allowed implementation files:

- `docs/fund-analysis-template-draft.md`
- `fund_agent/fund/template/contracts.py`
- `fund_agent/fund/template/typed_contracts.py`
- `fund_agent/fund/template/chapter_contract_constraints.py` only if the public `load_template_contract_manifest()` consumer needs no-behavior-change alignment; current evidence says it should remain a no-change consumer, but it is in regression scope.
- `fund_agent/fund/template/__init__.py` only if exports need no-behavior-change alignment
- `tests/fund/template/test_contracts.py`
- `tests/fund/template/test_typed_contracts.py`
- `tests/fund/template/test_chapter_contract_constraints.py`
- `tests/fund/test_evidence_availability.py`
- `tests/fund/test_chapter_writer.py`
- `tests/fund/test_chapter_auditor.py`
- `tests/services/test_chapter_orchestrator.py`
- `tests/services/test_execution_contract.py` only for no-regression typed path checks
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- implementation/review evidence artifacts under `docs/reviews/`

Files explicitly not allowed unless a reviewer finds a direct regression:

- deterministic renderer implementation;
- default analyze/checklist Service or CLI behavior;
- provider config/runtime/budget code;
- Host/Agent runtime packages;
- score/golden/readiness/promotion artifacts;
- unrelated untracked artifacts currently in the worktree.

## Contract/schema/public-interface implications

- Public chapter ids remain `0,1,2,3,4,5,6,7`; no Ch2 public split and no new chapter matrix rows.
- Existing public imports should keep working: `load_template_contract_manifest()`, `validate_template_contract_manifest()`, `get_chapter_contract()`, `resolve_preferred_lens()`, `load_typed_template_contract_manifest()`, `validate_typed_template_contract_manifest()`, `get_typed_chapter_contract()`.
- `typed_contracts.py` remains the typed schema, projection, and validation layer. It must not own authored stable id mappings, missing-behavior defaults, audit focus, Ch2 internal subcontract definitions, Ch0/Ch7 dependency metadata, or Ch3 evidence predicate as private truth.
- `contracts.py` becomes the adapter from the template document into the existing untyped `TemplateContractManifest`. It may own parsing/validation code, but not authored contract content.
- The template document becomes the sole authored truth source for implemented typed mechanisms. Code-level constants may remain only as closed-set domains, schema versions, validation literals, parser markers, and fallback error messages.
- Deterministic renderer/default analyze/checklist remain behaviorally unchanged because they consume the same untyped `ChapterContract` projection.
- Service explicit typed path remains behaviorally unchanged because it receives the same typed contract projection and same `EvidenceAvailability` semantics.

## Implementation decisions

1. Canonical document format:
   Add one canonical machine-readable block near the top of `docs/fund-analysis-template-draft.md`:

   ```text
   <!--
   TEMPLATE_CONTRACT_MANIFEST_JSON
   { ... strict JSON ... }
   END_TEMPLATE_CONTRACT_MANIFEST_JSON
   -->
   ```

   Use strict JSON and Python `json` parsing, not loose YAML or fuzzy Markdown parsing. This avoids ad hoc string inference and keeps parser failure modes deterministic.

2. Canonical block content:
   The JSON must include the current implemented typed contract data:

   - `schema_version: "typed_chapter_contract.v1"`
   - `template_id: "fund-analysis-template-typed-v1"`
   - `source_template_id: "fund-analysis-template-v1"`
   - `public_chapter_ids: [0,1,2,3,4,5,6,7]`
   - per chapter: `chapter_id`, `title`, `narrative_mode`, typed `must_answer`, typed `must_not_cover`, typed `required_output_items`, `preferred_lens`, `audit_focus`, `consumes_chapter_conclusions`, `independent_action_source`, `internal_subcontracts`
   - Ch3 `ch3.must_not_cover.item_04.applies_when` with predicate id `ch3.evidence.manager_behavior_style_unreviewed`, requirement id `ch3.requirement.actual_behavior_reviewed`, statuses `missing/unavailable/unreviewed`, and allowed contexts `required_label/evidence_gap_statement/quote/anchor_caption`
   - Ch2 internal subcontracts `performance/attribution/cost` exactly as current code defines them, all with `public_chapter_id: null`
   - current missing-evidence behavior for Ch2 and Ch3 required outputs, exactly matching current accepted code

3. Per-chapter prose blocks:
   Replace current duplicated structured `CHAPTER_CONTRACT` pseudo-YAML blocks with short references to the canonical block, for example:

   ```text
   <!--
   CHAPTER_CONTRACT_REF
   chapter_id: 3
   source: TEMPLATE_CONTRACT_MANIFEST_JSON
   END_CHAPTER_CONTRACT_REF
   -->
   ```

   Keep `CHAPTER_GOAL`, chapter body scaffolding, ITEM_RULE comments, and evidence anchor guidance. The structured contract fields should not be duplicated in per-chapter comments after this gate, otherwise the file itself becomes internally ambiguous.

4. `contracts.py` parser:
   Implement deterministic extraction of exactly one `TEMPLATE_CONTRACT_MANIFEST_JSON` block from `docs/fund-analysis-template-draft.md`.

   Parser requirements:
   - fail closed if the block is missing, duplicated, empty, non-JSON, or contains unknown top-level/chapter keys;
   - fail closed if public chapter ids are not exactly `0..7`;
   - fail closed if title/narrative/must_answer/must_not_cover/required_output/preferred_lens/audit_focus are empty where current validation requires non-empty;
   - project the parsed JSON to existing `TemplateContractManifest` and `ChapterContract` dataclasses for legacy callers.

5. `typed_contracts.py` role:
   Keep typed dataclasses and validators. Change `load_typed_template_contract_manifest()` to return typed dataclasses projected from the parsed template JSON.

   Remove or de-author:
   - `_CURRENT_TEXT_MAPPING`
   - `_AUDIT_FOCUS_BY_CHAPTER`
   - `_required_output_missing_behavior()`
   - `_required_output_missing_reason()`
   - `_build_internal_subcontracts()`
   - `_must_not_cover_predicate()`
   - `_must_not_cover_allowed_contexts()`

   These should no longer be authored in code. Equivalent values must come from the template JSON and be validated by `validate_typed_template_contract_manifest()`.

6. `source_manifest` compatibility:
   Preserve `load_typed_template_contract_manifest(source_manifest: TemplateContractManifest | None = None)` for compatibility, but do not use `source_manifest` to author typed fields. If supplied, validate that its untyped projection equals the parsed template document’s untyped projection, then return the canonical typed manifest. This prevents reintroducing a parallel source.

7. Cache and path:
   Use a small `lru_cache` for parsed template document reads if needed. The cache must be clearable in tests or scoped to immutable default path. Reading the template markdown is permitted because this is repository template metadata, not fund annual report data. Production annual report/PDF access rules remain unchanged.

8. Documentation tone:
   Docs must say “current implemented template truth source is `docs/fund-analysis-template-draft.md` canonical JSON block; code projects and validates it.” Do not describe this as future design after implementation.

## Plan-review fix addendum

This addendum resolves the accepted blocking findings and direct high/medium gaps from AgentDS and AgentMiMo before implementation begins.

### Canonical JSON Schema

The canonical block is one strict JSON object. The implementation must reject unknown keys at every object level. Exact top-level keys are:

- `schema_version`: string, exactly `"typed_chapter_contract.v1"`.
- `template_id`: string, exactly `"fund-analysis-template-typed-v1"`.
- `source_template_id`: string, exactly `"fund-analysis-template-v1"`.
- `source_path`: string, exactly `"docs/fund-analysis-template-draft.md"`.
- `public_chapter_ids`: array of integers, exactly `[0,1,2,3,4,5,6,7]`.
- `chapters`: array of eight chapter objects, ordered by `chapter_id`.

Exact chapter object keys are:

- `chapter_id`: integer, one of `0..7`.
- `title`: non-empty string.
- `narrative_mode`: non-empty string.
- `must_answer`: non-empty array of clause objects.
- `must_not_cover`: array of must-not-cover clause objects; can be empty only if the current contract allows empty, which it currently does not for public chapters.
- `required_output_items`: non-empty array of required-output item objects.
- `preferred_lens`: object keyed by lens key. Keys must be exactly current supported lens keys for that chapter, including `default`; values are lens rule objects.
- `audit_focus`: non-empty array of closed-set strings from `AuditFocusLiteral`; semantic-only, never disables programmatic blockers.
- `consumes_chapter_conclusions`: array of public chapter ids; current Ch0 must be `[7]`, other chapters currently `[]`.
- `independent_action_source`: boolean; current Ch0 must be `false` because Ch0 consumes Ch7 and cannot independently derive action.
- `internal_subcontracts`: array of internal subcontract objects; current non-empty only for Ch2.

Per-clause shape:

- `id`: stable authored id, such as `"ch3.must_answer.item_01"`.
- `text`: exact authored Chinese text projected into untyped `contracts.py`.

`must_not_cover` clause shape extends the per-clause shape with:

- `applies_when`: either `null` or an evidence predicate object.
- `allowed_contexts`: array of closed-set strings from `AllowedContextLiteral`; must be empty when `applies_when` is `null`.

Evidence predicate shape:

- `predicate_id`: stable predicate id.
- `requirement_ids`: non-empty array of `EvidenceRequirementId` strings.
- `required_statuses`: non-empty array of closed-set evidence availability statuses.
- `description`: non-empty Chinese description for review/debugging.

`required_output_items` item shape:

- `id`: stable authored item id, such as `"ch2.required_output.item_01"`.
- `text`: exact authored Chinese output label.
- `when_evidence_missing`: `null` or one of `render_evidence_gap`, `render_minimum_verification_question`, `delete_if_not_applicable`, `block`.
- `missing_evidence_reason`: `null` or non-empty Chinese reason. If `when_evidence_missing` is `block`, `render_evidence_gap`, `render_minimum_verification_question`, or `delete_if_not_applicable`, the current gate requires a non-empty reason; no implicit default may be supplied from code.

`preferred_lens` rule shape:

- `fund_type`: the same string as the enclosing key, either a `FundType` value or `default`.
- `statements`: non-empty array of strings.
- `facets_any`: array of strings, empty when not applicable.
- `priority`: `null` or one of `core`, `high`, `medium`, `low`.

Ch2 internal subcontract shape:

- `subcontract_id`: stable internal id; current allowed ids are `performance`, `attribution`, `cost`.
- `title`: non-empty Chinese title.
- `requirement_ids`: non-empty array of clause/output ids present in the same template JSON and in the strict `EvidenceRequirementId` guard.
- `public_chapter_id`: must be `null`; any integer value fails closed because Ch2 subcontracts are not public chapters.

Representative JSON snippet, shortened to one normal chapter, one Ch3 evidence predicate, and one Ch2 internal subcontract:

```json
{
  "schema_version": "typed_chapter_contract.v1",
  "template_id": "fund-analysis-template-typed-v1",
  "source_template_id": "fund-analysis-template-v1",
  "source_path": "docs/fund-analysis-template-draft.md",
  "public_chapter_ids": [0, 1, 2, 3, 4, 5, 6, 7],
  "chapters": [
    {
      "chapter_id": 2,
      "title": "收益从哪里来：R = A + B - C",
      "narrative_mode": "收益→归因→成本",
      "must_answer": [
        {
          "id": "ch2.must_answer.item_01",
          "text": "回答基金过去的收益表现如何。"
        }
      ],
      "must_not_cover": [
        {
          "id": "ch2.must_not_cover.item_01",
          "text": "不把收益表现写成孤立收益率列表。",
          "applies_when": null,
          "allowed_contexts": []
        }
      ],
      "required_output_items": [
        {
          "id": "ch2.required_output.item_01",
          "text": "基金收益表现",
          "when_evidence_missing": "block",
          "missing_evidence_reason": "第 2 章 R=A+B-C 数值与成本判断缺少同源证据时不得生成替代结论。"
        }
      ],
      "preferred_lens": {
        "default": {
          "fund_type": "default",
          "statements": ["用 R=A+B-C 拆分收益来源。"],
          "facets_any": [],
          "priority": null
        },
        "index_fund": {
          "fund_type": "index_fund",
          "statements": ["指数基金优先回答 Beta 暴露、跟踪误差和费率。"],
          "facets_any": ["宽基指数基金", "行业/主题指数基金", "策略指数基金"],
          "priority": "core"
        }
      },
      "audit_focus": ["r_abc", "evidence_anchors"],
      "consumes_chapter_conclusions": [],
      "independent_action_source": false,
      "internal_subcontracts": [
        {
          "subcontract_id": "performance",
          "title": "收益表现",
          "requirement_ids": [
            "ch2.must_answer.item_01",
            "ch2.must_answer.item_02",
            "ch2.required_output.item_01",
            "ch2.required_output.item_02"
          ],
          "public_chapter_id": null
        }
      ]
    },
    {
      "chapter_id": 3,
      "title": "基金经理画像：能力、风格与一致性",
      "narrative_mode": "人→方法→证据",
      "must_answer": [
        {
          "id": "ch3.must_answer.item_01",
          "text": "回答基金经理是谁，以及管理这只基金多久。"
        }
      ],
      "must_not_cover": [
        {
          "id": "ch3.must_not_cover.item_04",
          "text": "没有复核实际持仓、换手率或跨期风格证据时，不判断基金经理实际行为风格、风格稳定性或言行一致。",
          "applies_when": {
            "predicate_id": "ch3.evidence.manager_behavior_style_unreviewed",
            "requirement_ids": ["ch3.requirement.actual_behavior_reviewed"],
            "required_statuses": ["missing", "unavailable", "unreviewed"],
            "description": "第 3 章实际投资行为证据未复核时，只允许输出证据缺口或下一步验证问题。"
          },
          "allowed_contexts": [
            "required_label",
            "evidence_gap_statement",
            "quote",
            "anchor_caption"
          ]
        }
      ],
      "required_output_items": [
        {
          "id": "ch3.required_output.item_06",
          "text": "利益一致性",
          "when_evidence_missing": "render_minimum_verification_question",
          "missing_evidence_reason": "第 3 章利益一致性证据缺失时只能输出下一步最小验证问题。"
        }
      ],
      "preferred_lens": {
        "default": {
          "fund_type": "default",
          "statements": ["先区分基金经理宣称的方法和年报证据能复核的实际行为。"],
          "facets_any": [],
          "priority": null
        }
      },
      "audit_focus": ["manager_consistency", "evidence_anchors"],
      "consumes_chapter_conclusions": [],
      "independent_action_source": false,
      "internal_subcontracts": []
    }
  ]
}
```

The snippet is illustrative; implementation must author the complete current chapter data. It is invalid to infer omitted current values from code.

### Text/id bridging

Decision: use DS Option A.

The JSON carries stable `id` plus exact `text` for every authored `must_answer`, `must_not_cover`, and `required_output_items` entry. `contracts.py` parses the same JSON and projects only the ordered `text` tuples into the existing untyped `ChapterContract` API. `typed_contracts.py` parses the same JSON and projects `id` plus `text` into typed dataclasses.

This removes `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, and `_ChapterTextMapping` as authored truth. Code may still contain closed-set literal domains, schema-version constants, dataclasses, parser markers, and validation helpers, but not a text-to-id mapping or default typed content. Positional ids derived in code are forbidden because they would preserve a hidden parallel truth.

### EvidenceRequirementId coupling

Decision: keep `EvidenceRequirementId` as a strict `Literal` guard in `evidence_availability.py`.

Validation timing:

- Manifest load/projection must fail closed if any template JSON `applies_when.requirement_ids` or Ch2 `internal_subcontracts[].requirement_ids` value is not in `_KNOWN_REQUIREMENT_IDS`.
- `derive_evidence_availability()` keeps its existing `_validate_typed_requirement_ids()` runtime guard as a second line of defense.
- Requirement spec/dependency drift must be checked by tests: every `_CH2_REQUIREMENT_SPECS`, `_CH3_REQUIREMENT_SPECS`, `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID`, `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`, and `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES` id must be present in the projected typed template JSON where it is expected, and every Ch2 subcontract/template predicate id must be derivable by evidence availability.

Tests to add or strengthen:

- malformed template JSON with an unknown requirement id fails at typed manifest load/validation, before writer/auditor/service execution;
- missing a required Ch2 or Ch3 evidence requirement from template JSON fails a cross-validation test rather than surfacing only in a later writer/auditor path;
- current strict Literal values remain unchanged unless a separate evidence-availability contract gate accepts the change.

### chapter_contract_constraints scope

`chapter_contract_constraints.py` is a direct consumer of the public untyped manifest API. It should need no behavior change if `contracts.py` still returns the same `TemplateContractManifest`, but it is explicitly in regression scope.

Implementation rule:

- Do not change its constraint semantics unless the new parser breaks the wrapper comparison.
- If only wording/docstrings become stale, update them to say it wraps the parsed template manifest instead of a Python constant manifest.
- Add or update `tests/fund/template/test_chapter_contract_constraints.py` to prove default constraints still wrap `must_answer` and `must_not_cover` from `load_template_contract_manifest()`, and active/enhanced/bond overlays still resolve after the template JSON replacement.

### CHAPTER_CONTRACT_REF and authorability/tooling

Controller-facing decision for this plan: single canonical JSON is authoritative. Per-chapter `CHAPTER_CONTRACT_REF` blocks should not duplicate structured `must_answer`, `must_not_cover`, `required_output_items`, `preferred_lens`, typed ids, predicates, or missing behavior.

Most robust option: use ref-only blocks with at most a short non-authoritative line such as `summary: see canonical manifest for chapter_id=3`. Do not include clause text summaries, because summaries can drift and the parser cannot prove they match semantics.

Authorability mitigation:

- Implement fail-closed parser errors that include the JSON path, for example `chapters[3].must_not_cover[3].applies_when.requirement_ids[0]`.
- Add a no-provider validation path. Either expose a side-effect-free local check command such as `uv run python -m fund_agent.fund.template.contracts --validate-template-doc`, or document the equivalent pytest command if a module CLI is not added.
- Add tests for missing/duplicated/malformed canonical block and unknown keys, so authors get deterministic failures.

### source_manifest, cache, and exports

`source_manifest` production expectation:

- Preserve `load_typed_template_contract_manifest(source_manifest: TemplateContractManifest | None = None)` for compatibility only.
- Production callers should pass `None`; a non-`None` value is validation-only and must not author typed fields.
- Add a negative test that passes a stale/different `source_manifest` and asserts `ValueError`.

Cache/path strategy:

- Parse from the immutable default repository template path in production.
- If `lru_cache` is used, key it by an explicit path argument and expose a small private cache clear helper for tests, for example `_clear_template_manifest_cache()`.
- Tests that mutate temp template files must use a temp path or clear cache before and after the assertion. Avoid `importlib.reload()` as the cache strategy.
- Reading `docs/fund-analysis-template-draft.md` is allowed as template metadata; this does not weaken the annual report/PDF rule that production fund documents must go through `FundDocumentRepository`.

`__init__.py` export check:

- Current `fund_agent/fund/template/__init__.py` does not re-export `_CURRENT_TEXT_MAPPING`, `_TextIdMapping`, `_ChapterTextMapping`, `_AUDIT_FOCUS_BY_CHAPTER`, or removed helper functions.
- Keep existing public exports stable. Only update `__init__.py` if new public helper exports are intentionally needed; do not export parser internals or cache helpers.

Referenced test-file precheck:

- Before implementation, run `rg --files tests | rg 'test_contracts.py|test_typed_contracts.py|test_chapter_contract_constraints.py|test_evidence_availability.py|test_chapter_writer.py|test_chapter_auditor.py|test_chapter_orchestrator.py|test_execution_contract.py|test_fund_analysis_service_llm.py|test_cli.py|test_renderer.py|test_audit_programmatic.py'`.
- If any referenced file is missing, update the validation matrix to use the actual existing test path or create the focused test file in the relevant implementation slice. Do not claim coverage from a non-existent path.

## Small implementation slices

### Slice 1: Template document canonical contract block

- Allowed files: `docs/fund-analysis-template-draft.md`.
- Exact changes:
  - Add `TEMPLATE_CONTRACT_MANIFEST_JSON` block containing the current accepted typed contract data.
  - Replace each per-chapter structured `CHAPTER_CONTRACT` block with `CHAPTER_CONTRACT_REF`.
  - Keep each `CHAPTER_CONTRACT_REF` non-authoritative and short; do not duplicate clause text, lens rules, predicates, or missing behavior outside the canonical JSON.
  - Keep chapter titles, chapter body scaffolding, ITEM_RULE blocks, evidence anchor appendix, and audit rules appendix.
  - Run the parser/validation command or targeted pytest as soon as Slice 2 parser exists; if Slice 1 is reviewed separately before parser code, include a temporary manual JSON parse/equality check in implementation evidence so the intermediate doc state is not accepted on visual inspection alone.
- Tests to update in later slices; do not change source code in this slice if isolated.
- Stop conditions:
  - Any proposal to renumber chapters, introduce public Ch2 subchapters, or change deterministic report body text.
  - Any uncertainty about current code facts versus future typed design.
- Accepted checkpoint criteria:
  - Template doc has exactly one canonical JSON block.
  - Per-chapter structured contract duplication is removed or converted to references.
  - Public chapters remain 0-7 in the visible template.

### Slice 2: Parse template doc into current untyped manifest

- Allowed files: `fund_agent/fund/template/contracts.py`, `tests/fund/template/test_contracts.py`.
- Exact changes:
  - Add strict JSON-block extraction and parser.
  - `load_template_contract_manifest()` returns the untyped projection from the template doc.
  - Keep `ChapterContract`, `TemplateContractManifest`, `TemplateLensRule`, `get_chapter_contract()`, `resolve_preferred_lens()`, and `validate_template_contract_manifest()` behavior.
  - Add tests for missing/duplicated/malformed JSON block, unknown keys at every level, chapter id drift, stable id/text shape, preferred_lens key/priority validation, cache clearing/path behavior, and current 8-chapter projection.
  - Add or document the local validation command for template authors, either a module command or an equivalent pytest target.
- Docs decision: no docs/control sync yet beyond the template file.
- Stop conditions:
  - Parser needs loose natural-language inference to pass.
  - Tests require changing renderer/default behavior.
- Accepted checkpoint criteria:
  - `tests/fund/template/test_contracts.py` passes.
  - Current untyped manifest values match the previously accepted chapter ids/titles/text/lens data.

### Slice 3: Project typed manifest from template doc

- Allowed files: `fund_agent/fund/template/typed_contracts.py`, `fund_agent/fund/template/__init__.py` if exports require alignment, `tests/fund/template/test_typed_contracts.py`.
- Exact changes:
  - Load typed data from the parsed template document.
  - Keep typed dataclasses and validation.
  - Remove code-authored stable id/text mapping and code-authored missing behavior / audit focus / internal subcontract truth.
  - Preserve Ch2 internal subcontract validation, Ch0/Ch7 dependency validation, audit_focus closed-set validation, and Ch3 evidence predicate validation.
  - Keep `EvidenceRequirementId` as a strict external guard and validate template JSON requirement ids against it during typed manifest load/validation.
  - Keep `source_manifest` compatibility as validation-only; production expectation is `None`.
  - Add tests proving `typed_contracts.py` has no `_CURRENT_TEXT_MAPPING` authored truth, a stale/different `source_manifest` raises `ValueError`, unknown template requirement ids fail closed, and changing template JSON changes the projected typed manifest while malformed values fail closed.
- Stop conditions:
  - Any typed value remains authored only in code without a parser/validation reason.
  - `source_manifest` can still generate typed fields independent of template doc.
- Accepted checkpoint criteria:
  - `tests/fund/template/test_typed_contracts.py` passes.
  - `load_typed_template_contract_manifest()` and `load_template_contract_manifest()` share the same document truth.

### Slice 4: Typed consumers regression

- Allowed files: `tests/fund/template/test_chapter_contract_constraints.py`, `tests/fund/test_evidence_availability.py`, `tests/fund/test_chapter_writer.py`, `tests/fund/test_chapter_auditor.py`, `tests/services/test_chapter_orchestrator.py`, `tests/services/test_execution_contract.py` only if needed.
- Exact changes:
  - Update tests only where they assume code-authored mapping internals.
  - Confirm `chapter_contract_constraints.py` remains a no-change public-manifest consumer; update only stale wording if needed.
  - Add/keep constraints regression proving default wrappers use the same `must_answer` / `must_not_cover` projected from the parsed untyped manifest and overlays still resolve.
  - Preserve assertions for same-source availability, Ch2 block, Ch3 gap/minimum-verification behavior, Ch3 typed must-not-cover issue id, audit_focus semantic-only LLM input, and Service explicit typed path wiring.
  - Add evidence availability cross-validation for `_CH2_REQUIREMENT_SPECS`, `_CH3_REQUIREMENT_SPECS`, `_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID`, `_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS`, and `_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES` against the projected typed manifest.
  - Add at least one end-to-end typed projection regression: template doc -> typed manifest -> `EvidenceAvailability` -> writer/auditor/service typed path.
- Stop conditions:
  - Any consumer must change production behavior to adapt to the doc-source replacement.
  - Any provider/live/API behavior is needed to validate.
- Accepted checkpoint criteria:
  - Typed consumer tests pass with no live provider and no repository/PDF/cache/source helper access.

### Slice 5: Documentation/control sync

- Allowed files: `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `fund_agent/fund/README.md`, `tests/README.md`, evidence artifacts under `docs/reviews/`.
- Exact changes:
  - `docs/design.md`: reclassify template truth-source replacement as current implemented fact after implementation; keep Agent runtime/multi-year/provider/score/golden/readiness as future/deferred.
  - `docs/implementation-control.md`: update current gate ledger/checkpoints and next entry point; do not append a long historical log.
  - `docs/current-startup-packet.md`: update short startup facts and prohibited/deferred actions.
  - `fund_agent/fund/README.md`: say `docs/fund-analysis-template-draft.md` canonical JSON block is the Fund template contract truth source; `contracts.py` / `typed_contracts.py` parse/project/validate.
  - `tests/README.md`: add the template truth-source tests and note no live provider probes.
- Stop conditions:
  - Docs imply Agent runtime, multi-year runtime, provider budget/default/runtime, score-loop, Ch2 public split, deterministic behavior change, quality/golden/readiness promotion, or PR/external state change.
- Accepted checkpoint criteria:
  - Docs/control files describe current/future/deferred states consistently.
  - `git diff --check` passes for changed docs.

## Tests/validation matrix

No live provider probes. No commands that require real API keys. No promotion or readiness workflows.

Template consistency:

```bash
uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py -q
```

Template constraint sidecar regression:

```bash
uv run pytest tests/fund/template/test_chapter_contract_constraints.py -q
```

Typed contract + evidence availability:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py -q
```

Writer/auditor typed path:

```bash
uv run pytest tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py -q
```

Service typed path and explicit contract boundary:

```bash
uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py -q
```

Default deterministic renderer/audit no-regression:

```bash
uv run pytest tests/fund/template/test_renderer.py tests/fund/audit/test_audit_programmatic.py tests/services/test_fund_analysis_service.py -q
```

Full relevant typed family regression:

```bash
uv run pytest tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q
```

Static quality and docs diff check:

```bash
uv run ruff check fund_agent/fund/template/contracts.py fund_agent/fund/template/typed_contracts.py fund_agent/fund/template/chapter_contract_constraints.py tests/fund/template/test_contracts.py tests/fund/template/test_typed_contracts.py tests/fund/template/test_chapter_contract_constraints.py
git diff --check -- docs/fund-analysis-template-draft.md fund_agent/fund/template/contracts.py fund_agent/fund/template/typed_contracts.py fund_agent/fund/README.md tests/README.md docs/design.md docs/implementation-control.md docs/current-startup-packet.md
```

Pre-implementation test-file existence check:

```bash
rg --files tests | rg 'test_contracts.py|test_typed_contracts.py|test_chapter_contract_constraints.py|test_evidence_availability.py|test_chapter_writer.py|test_chapter_auditor.py|test_chapter_orchestrator.py|test_execution_contract.py|test_fund_analysis_service_llm.py|test_cli.py|test_renderer.py|test_audit_programmatic.py'
```

Plan-fix safety check:

```bash
rg -n "Canonical JSON Schema|Text/id bridging|EvidenceRequirementId|chapter_contract_constraints|source_manifest|CHAPTER_CONTRACT_REF|cache|__init__" docs/reviews/mvp-typed-template-truth-source-replacement-plan-20260603.md
```

Optional full CI-style check after review fixes:

```bash
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
```

## Docs/control sync decision

Sync is mandatory because this gate changes the template truth-source status:

- `docs/design.md`: update current implementation facts and remove/add caveats that typed sidecar remains merely additive.
- `docs/implementation-control.md`: update current gate, accepted artifact list, next entry, residuals, and prohibited actions without adding long historical prose.
- `docs/current-startup-packet.md`: make the short resume packet reflect the new truth-source arrangement.
- `fund_agent/fund/README.md`: update Fund package developer manual and examples/description for template contract loading.
- `tests/README.md`: document new template truth-source parser/projection tests.

Do not update the root `README.md` unless implementation changes user-facing commands or report output. This plan does not require that.

## Review gates

Because classification is `heavy`, require:

- Plan review by at least two independent reviewers or controller-recorded reviewer unavailability.
- Implementation code review by at least two independent reviewers.
- Re-review after accepted findings are fixed.
- Aggregate deepreview for the full truth-source replacement diff before local acceptance.
- Controller judgment before any accepted checkpoint or next gate.
- No PR/push/external action without explicit user authorization.

Reviewer focus:

- Is there exactly one authored template contract truth source?
- Does code still preserve public chapter ids `0-7` and current deterministic behavior?
- Did any typed field remain authored in `typed_contracts.py` or `contracts.py` as parallel truth?
- Are malformed template edits fail-closed?
- Are Agent runtime, multi-year runtime, provider runtime, score/golden/readiness, and Ch2 public split still out of scope?

## Stop conditions

Stop and return to controller if:

- The implementation requires changing renderer/default analyze/checklist behavior.
- The implementation requires a provider live run, real API key, network probe, or runtime timeout/default change.
- The implementation requires changing Agent/Host runtime boundaries.
- The template JSON cannot represent current accepted typed fields without adding future-only schema.
- Public chapter ids would not remain exactly `0-7`.
- Ch2 internal subcontracts would become public chapters.
- Existing unrelated untracked artifacts need to be staged or modified.
- Validation failures indicate current accepted typed behavior changes rather than parser/projection bugs.
- Any doc/control update cannot clearly separate current implemented facts, accepted future design, and deferred/rejected content.

## Risks/open questions

- Risk: JSON block plus visible prose could become internally inconsistent. Mitigation: per-chapter structured `CHAPTER_CONTRACT` blocks should be replaced with short non-authoritative `CHAPTER_CONTRACT_REF` entries, not duplicated summaries.
- Risk: the canonical JSON block is large and less pleasant to author by hand. Mitigation: strict schema, JSON-path error messages, no-provider validation command, and focused parser tests; this gate accepts the authorability cost to eliminate code parallel truth.
- Risk: reading a Markdown file at runtime introduces path/caching issues. Mitigation: use a single default path, strict parser, path-keyed `lru_cache` if needed, private cache clear helper for tests, and no `importlib.reload()` cache workaround; this is template metadata, not fund document access.
- Risk: code reviewers may prefer per-chapter JSON blocks for locality. Working assumption: one canonical manifest block is safer because it avoids partial parse ambiguity and cross-chapter dependency scattering. If controller requires locality, keep one canonical manifest and add non-authoritative chapter refs only.
- Risk: tests currently assert typed loader does not mutate current manifest. Update the intent to “typed and untyped projections share the same parsed document truth.”
- Residual risk: strict `EvidenceRequirementId` Literal keeps evidence availability coupling explicit. Drift is intended to fail closed at manifest load/validation and again in `derive_evidence_availability()`.

## Completion report format

Implementation closeout should report:

- Changed files, grouped by template/source/tests/docs/control.
- Truth-source decision: `docs/fund-analysis-template-draft.md` canonical JSON block is the sole authored template contract source; `contracts.py` and `typed_contracts.py` parse/project/validate.
- Public-interface confirmation: chapter ids `0-7`, deterministic renderer/analyze/checklist, Service explicit typed path, and Host business opacity unchanged.
- Validation commands and results, with explicit note that no live provider probes were run.
- Review artifacts and accepted/rejected/deferred findings.
- Dirty worktree note confirming unrelated untracked artifacts were not staged or modified.
- Residuals: Agent runtime, multi-year runtime, provider budget/default/runtime, score-loop, Ch2 public split, quality/golden/readiness promotion remain future/deferred gates.
