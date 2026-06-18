# Fund Processor/Extractor Truth Sync Review — AgentDS

> **Gate**: Fund Processor/Extractor Architecture Planning Gate
> **Reviewer**: AgentDS
> **Date**: 2026-06-17
> **Scope**: truth-doc consistency audit only; no implementation, fix, commit, push, PR
> **Inputs**: AGENTS.md, docs/docling-architecture-reorientation-20260617.md, docs/design.md (v2.19), docs/implementation-control.md (v2.8-control-compressed), docs/current-startup-packet.md
> **Secondary**: fund_agent/README.md, fund_agent/fund/README.md

---

## Verdict

**TRUTH_SYNC_REVIEW_PASS_NOT_READY**

The four primary truth/control documents are materially consistent on current phase, current gate, non-goals, candidate evidence identity, NOT_READY boundary, and Processor/Extractor future-design-only status. No discussion-meeting statistics, archive-action suggestions, or dayu-agent Fins–specific mechanisms have been erroneously written as current implementation facts. README secondary consistency is acceptable.

Residual risks are confined to wording ambiguity in implementation-control.md line 9, startup-packet input ordering, and AGENTS.md lacking a current-phase pointer — none of which constitute a material truth-source contradiction.

---

## Findings

### Finding 1 — HIGH — implementation-control.md:9 ambiguous wording suggests discussion doc entered truth sync

**File**: `docs/implementation-control.md`, line 9
**Evidence**:

> `docs/docling-architecture-reorientation-20260617.md 已作为架构重定位输入进入真源同步：Docling baseline qualification … 等链路降级为 deferred`

The discussion document itself is explicitly labelled `性质：架构讨论纪要，供后续 gate/phase 决策参考` — it is meeting notes, not a truth source. The sentence structure places the discussion doc as the grammatical subject of 进入真源同步. A future reader could interpret this as the discussion document (with its 367-review-file count, 47,000-line statistics, archive suggestions, and unimplemented code sketches in §3–§4) having been accepted into the truth-source corpus.

**Impact**: Risk that deferred statistics, archive-action suggestions, or unimplemented code patterns from the discussion doc are later cited as accepted truth-source material.

**Recommended裁决**: Reword to make the subject unambiguous — the reorientation decision (Docling downgrade to deferred, mainline switch to Processor/Extractor planning) entered truth sync via design.md v2.19, not the discussion document itself.

---

### Finding 2 — MEDIUM — startup-packet.md:27 gate input list does not distinguish discussion input from truth input

**File**: `docs/current-startup-packet.md`, line 27
**Evidence**:

> `Current gate input: docs/docling-architecture-reorientation-20260617.md; docs/design.md v2.19; docs/implementation-control.md current state; prior Docling/EID HTML/pdfplumber evidence chain as candidate-only historical input.`

The discussion doc is listed first, before design.md and implementation-control.md, without any qualifier marking it as discussion input only. The prior evidence chain is correctly marked `candidate-only historical input`, but the discussion doc receives no such qualifier despite having the same not-truth-source status.

**Impact**: A reader following the gate input list in order could treat the discussion doc's statistics, archive suggestions, and unimplemented code sketches with equal authority to design.md.

**Recommended裁决**: Add an explicit qualifier, e.g. `docs/docling-architecture-reorientation-20260617.md (architecture discussion input, not truth source)`.

---

### Finding 3 — MEDIUM — AGENTS.md contains no reference to current phase or gate

**File**: `AGENTS.md`, entire document
**Evidence**: AGENTS.md is the highest-priority execution rules document (line 7: 所有 Agent 执行规则的唯一权威入口) and first in read order (line 29). It defines the Processor/Extractor boundary rule (line 79) and the four-layer architecture. However, it contains zero reference to the current `Docling architecture reorientation / Fund Processor-Extractor route` phase or the active `Fund Processor/Extractor Architecture Planning Gate`. An agent reading only AGENTS.md would have no awareness of current planning gate constraints.

**Impact**: Discoverability gap. Mitigated by the mandatory read order (AGENTS.md → design.md → implementation-control.md → startup-packet.md), but the highest-priority document is silent on current mainline.

**Recommended裁决**: Consider adding a brief current-phase pointer referencing `docs/current-startup-packet.md` and `docs/implementation-control.md`. Not blocking.

---

### Finding 4 — LOW — design.md §5.4 future chapter-level audit describes 0–10 chapter system with present-tense language before guard clause

**File**: `docs/design.md`, lines 455–498 (§5.4)
**Evidence**: The section describes a 0–10 chapter writing/audit/repair闭环 with present-tense design language (第 1-9 章先独立写作, 第 10 章最终判断必须后置, 第 0 章执行摘要必须最后生成). The guard clause at line 485 correctly states 当前 8 章模板与未来 0-10 章体系的映射尚未裁决, but this comes after ~30 lines of present-tense description.

**Impact**: Low — the guard clause is present. Risk is that a reader skimming the design principles could miss the unresolved-mapping caveat.

**Recommended裁决**: Add a short preamble before the bullet list explicitly stating the 0-10 chapter system is a design candidate with unresolved mapping to current 0-7 template.

---

### Finding 5 — LOW — fund_agent/README.md Processor/Extractor terminology drifts from canonical name

**File**: `fund_agent/README.md`, line 35
**Evidence**: Uses `Processor/Extractor 分派边界` while truth docs consistently use `FundProcessorRegistry` (AGENTS.md:79, design.md:5, implementation-control.md:40, fund_agent/fund/README.md:78).

**Impact**: Minor terminology inconsistency. Does not create a material contradiction.

**Recommended裁决**: Align to `FundProcessorRegistry` or use `FundProcessorRegistry / Extractor 分派边界`.

---

### Finding 6 — INFO — Cross-document consistency matrix: all pass

Verified across all four primary documents plus both READMEs:

| Assertion | AGENTS.md | design.md | impl-ctrl.md | startup-packet | fund_agent/README | fund/fund/README |
|---|---|---|---|---|---|---|
| Current phase: Docling reorientation / Processor-Extractor route | (不在职责范围) | ✓ L5 | ✓ L9 | ✓ L22 | (不在职责范围) | (不在职责范围) |
| Current gate: Fund Processor/Extractor Architecture Planning Gate | (不在职责范围) | ✓ | ✓ L49 | ✓ L23 | (不在职责范围) | (不在职责范围) |
| Gate: heavy, planning only, no implementation | ✓ | ✓ | ✓ L50 | ✓ L24 | (不在职责范围) | (不在职责范围) |
| Docling evidence: candidate-only, not_proven | ✓ L79 | ✓ L5-6 | ✓ L39 | ✓ L25 | ✓ L35 | ✓ L77 |
| Processor/Extractor: future design, not implemented | ✓ L79 | ✓ L5-6 | ✓ L40 | (scope implies) | ✓ L35 | ✓ L78 |
| release/readiness: NOT_READY | (implied) | ✓ L6 | ✓ L9 | ✓ pervasive | (不在职责范围) | (不在职责范围) |
| No live/source/provider/LLM action authorized | (implied) | ✓ | ✓ L50-51 | ✓ L24,L228 | (不在职责范围) | (不在职责范围) |
| EID single-source policy unchanged | ✓ L80-81 | ✓ L5 | ✓ L37 | ✓ L82 | ✓ L34 | ✓ L73-74 |
| Dayu: reference only, not production runtime | ✓ L83 | ✓ L61 | ✓ | (不在职责范围) | ✓ L13 | ✓ L3 |
| Four-layer: UI→Service→Host→Agent | ✓ L91-141 | ✓ L47-57 | ✓ L30 | (不在职责范围) | ✓ L5-8 | (不在职责范围) |
| Docling/pdfplumber/EID HTML not consumable by Service/UI/Host | ✓ L79 | ✓ L43 | ✓ L43 | ✓ L24 | ✓ L35 | ✓ L77 |
| Fallback: not_found/unavailable vs schema_drift/identity_mismatch/integrity_error fail-closed | ✓ L237-246 | ✓ | ✓ | ✓ L82 | ✓ L34 | ✓ L73-74 |

No material contradictions. All truth documents aligned on current state.

---

### Finding 7 — INFO — No discussion-document leakage into truth docs

Verified that none of the following discussion-document content appears as current fact in any truth document:

- Statistics (367 review files, ~47,000 lines, 2.4MB–6.3MB JSON, ~34MB total): absent
- Archive action suggestions (§4.1): absent
- Unimplemented code sketches (§3.3 `FundProcessorRegistry`, `ActiveFundAnnualExtractor`): absent; design.md describes architectural concept without copying code
- dayu-agent Fins–specific mechanisms (BsTenKFormProcessor, priority 200/190/120/100/80, SecPipeline/CnPipeline): absent
- Implementation roadmap steps (§4.2–§4.5): absent as completed actions; referenced only as future direction

---

## Blocking Open Questions

None. All findings are non-blocking wording/clarity issues.

---

## Residual Risks

1. **implementation-control.md line 9 wording ambiguity** (Finding 1): if uncorrected, a future controller or agent could treat discussion-document statistics and archive suggestions as accepted truth-source content.
2. **AGENTS.md phase/gate blindness** (Finding 3): agent entering cold and reading only AGENTS.md would miss current architecture planning gate constraints. Mitigated by mandatory read order but the gap exists.
3. **Discussion doc §5.1 alignment claims not exhaustively verified**: spot-checks of discussion doc claims about AGENTS.md rules were accurate; full claim-by-claim diff was not performed.
