# Docling Baseline Candidate Decision Review - MiMo - 2026-06-15

Verdict: `PASS`

## Findings

No blocking findings.

## Accepted Points

- Baseline wording is scoped to candidate-layer structural locators.
- Docling is not promoted to source truth, field correctness proof, production parser replacement, release/readiness, or public consumption path.
- Route comparison is fair for this decision: Docling's bbox/header-flag advantage is stated; pdfplumber remains a comparator and partial candidate for page + row/column extraction.
- EID HTML remains blocked/not comparable until current-envelope mapping exists.
- `004393_2025` residual is handled correctly; next gate is `004393 Current-envelope Candidate Artifact Refresh Planning Gate`.

## Residual

The wording around pdfplumber was tightened by controller to avoid confusing candidate-layer comparison with production source/parser fallback authorization.
