# Controller Judgment: Manual Evidence Intake 004393 2024

## Judgment

Accepted locally with limited scope.

`004393 / 2024` is accepted as review-owned manual annual-report source identity evidence in `docs/reviews` only.

This judgment does not:

- externally verify the EID URLs or PDF content;
- read, parse, hash, or retain PDF files;
- call `FundDocumentRepository`;
- invoke network/source/fallback/akshare/EID tools;
- update fixture projection;
- accept exact/numeric extractor correctness;
- unlock row-field assertions;
- promote golden/readiness or quality gate state.

## Accepted Artifacts

- Intake evidence: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-004393-20260608.md`
- Source payload: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-004393-20260608-source-payload.json`
- Review-owned manifest: `docs/reviews/mvp-small-golden-set-source-identity-recovery-manifest-20260608.json`
- Review A: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-004393-review-a-20260608.md`
- Review B: `docs/reviews/mvp-small-golden-set-manual-evidence-intake-004393-review-b-20260608.md`

## Evidence Basis

User-provided source identity fields:

- `fund_code`: `004393`
- `report_year`: `2024`
- `document_kind`: `annual_report`
- `official_document_url`: `http://eid.csrc.gov.cn/fund/disclose/instance_show_pdf_id.do?instanceid=1248088`
- `official_document_id`: `instanceid=1248088`
- `source_document_title`: `安信企业价值优选混合型证券投资基金2024年年度报告`
- `source_publisher`: `安信基金管理有限责任公司`
- `source_registry`: `中国证监会基金电子披露网站 / EID`
- `publication_date`: `2025-03-28`
- `fund_name`: `安信企业价值优选混合型证券投资基金`
- `share_class`: `A=004393`; other class `C=020964`
- `user_provided_pdf_sha256`: `bc6b0a1ae2f709f4cb4fa501f88ba9c19aa0f37d36758160577c57222e9860bf`
- Source payload SHA256: `3926f237f48cfae0e59b92769039c655e0ba09692d7fb3535288a365e7d8c4d3`

## Review Results

- Review A: PASS.
- Review B: PASS.

No blocking finding remains.

## Controller Decision

Update the review-owned source identity manifest row for `004393 / 2024` to:

- `identity_status=matched`
- `identity_review_status=controller_accepted`
- `source_boundary=manual_review`
- `source_failure_category=none`
- `fallback_allowed=false`
- `fallback_used=false`
- `review_artifact_refs` populated with both reviews
- `controller_judgment_ref` populated with this judgment
- `exact_numeric_correctness_allowed=false`
- `fixture_projection_performed=false`
- `field_unlocks=[]`

All other rows remain `deferred/not_reviewed`.

## Next Entry Point

Stop after local accepted checkpoint unless the user explicitly provides manual evidence for another row or authorizes a later gate:

1. Additional docs-only manual evidence intake for another small golden row.
2. `matched-source retained excerpt fixture gate`.
3. `row-field exact/numeric extractor correctness implementation gate` after field-level excerpts and expected values are accepted.
4. `matched-source FundDocumentRepository acquisition evidence gate`, which remains separately unauthorized.
