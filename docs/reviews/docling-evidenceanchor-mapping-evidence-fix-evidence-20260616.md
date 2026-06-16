# Docling EvidenceAnchor Mapping Evidence Fix Evidence - 2026-06-16

Gate: `Docling EvidenceAnchor Mapping Evidence Fix Gate`
Role: fix worker
Release/readiness: `NOT_READY`

## 1. Scope

This artifact records the evidence-document fix after DS/MiMo evidence review.

No code, tests, runtime behavior, source policy, parser, `FundDocumentRepository`, Service, Host, UI, renderer, quality gate, readiness, release, PR, push or merge state was changed.

## 2. Findings Fixed

| Finding | Source | Fix |
| --- | --- | --- |
| DS-F1: aggregate blocked count stated as `23473`, but per-sample blocked totals sum to `23373`. | AgentDS | Corrected total blocked candidate blocks to `23373`. |
| MiMo-F4: zero-yield severity could be quantified more clearly. | AgentMiMo | Added overall mapped yield: `102 / 23475 = 0.43%`. |
| MiMo-F6: missing vs unstable context ratio could be consolidated. | AgentMiMo | Added blocked distribution: `missing_section_context=23363`, `unstable_section_context=10`; missing context is `99.96%` of blocked blocks. |

## 3. Validation

Commands run:

```bash
git diff --check -- docs/reviews/docling-evidenceanchor-mapping-evidence-20260616.md docs/reviews/docling-evidenceanchor-mapping-evidence-fix-evidence-20260616.md
```

Result: pass.

## 4. Final Verdict

```text
VERDICT: FIX_EVIDENCE_UPDATED_NOT_READY
```
