# Golden Readiness Preflight

## 真源摘要

- run_id: `golden-readiness-preflight-20260529`
- source_csv: `docs/code_20260519.csv`
- golden_answer_path: `reports/golden-answers/golden-answer.json`
- strict golden answer v1 仅执行 fund-level coverage；year/partial coverage codes 保留不触发。
- 本 preflight 只读，不执行 fixture promotion、golden promotion、release 或 QDII probing。

## Overall Verdict

**BLOCK**

## 已解除

- `blocker_resolved` / original_blocker_code=`bond_risk_evidence_missing` / fund_code=`006597`: 006597 bond_risk_evidence_missing resolved by accepted NAV-derived drawdown metric gate.

## Per-Fund / Slot Readiness

| fund_code | year | readiness | quality | strict_golden | fixture | disposition |
|---|---:|---|---|---|---|---|
| 004393 | 2024 | deferred_with_owner | warn | covered | absent | include_for_later_review |
| 004194 | 2024 | deferred_with_owner | warn | covered | absent | include_for_later_review |
| 017641 | 2024 | blocked | block | fund_not_covered | absent | include_for_later_review |
| 006597 | 2024 | deferred_with_owner | warn | covered | absent | include_for_later_review |
| 110020 | 2024 | deferred_with_owner | warn | fund_not_covered | absent | reviewed_coverage_candidate |
| 096001 | 2024 | blocked | block | fund_not_covered | absent | blocked |
| 040046 | 2024 | blocked | block | fund_not_covered | absent | blocked |
| 019172 | 2024 | blocked | block | fund_not_covered | absent | blocked |
| 021539 | 2024 | blocked | block | fund_not_covered | absent | blocked |
| FOF_SLOT | 2024 | blocked | not_evaluated | not_applicable | not_applicable | needs_taxonomy_gate |

## Blockers By Severity

| severity | code | scope | fund_code | owner | next_gate | message |
|---|---|---|---|---|---|---|
| block | fixture_promotion_absent | global |  | future fixture promotion gate | produce accepted fixture promotion state manifest | 未提供 accepted fixture promotion state manifest。 |
| block | qdii_replacement_hard_stop | global |  | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | QDII replacement hard stop accepted；禁止继续 automatic QDII probing。 |
| block | fixture_promotion_absent | fund | 004393 | future baseline preflight owner | fixture promotion / strict golden coverage gate | 004393 未发现 accepted fixture promotion state。 |
| block | fixture_promotion_absent | fund | 004194 | future baseline preflight owner | fixture promotion / strict golden coverage gate | 004194 未发现 accepted fixture promotion state。 |
| block | strict_golden_not_configured | fund | 017641 | future baseline preflight owner | quality block disposition / fixture promotion gate | 017641 score correctness 为 not_configured。 |
| block | quality_gate_block | fund | 017641 | future baseline preflight owner | quality block disposition / fixture promotion gate | 017641 quality gate status=block。 |
| block | strict_golden_fund_not_covered | fund | 017641 | future baseline preflight owner | quality block disposition / fixture promotion gate | 017641 不在 strict golden answer v1 fund-level coverage 中。 |
| block | fixture_promotion_absent | fund | 017641 | future baseline preflight owner | quality block disposition / fixture promotion gate | 017641 未发现 accepted fixture promotion state。 |
| block | strict_golden_not_configured | fund | 006597 | future baseline/golden preflight owner | fixture promotion / strict golden coverage gate | 006597 score correctness 为 not_configured。 |
| block | fixture_promotion_absent | fund | 006597 | future baseline/golden preflight owner | fixture promotion / strict golden coverage gate | 006597 未发现 accepted fixture promotion state。 |
| block | strict_golden_not_configured | fund | 110020 | future index evidence sufficiency gate | index reviewed fact freeze / methodology / constituents evidence gate | 110020 score correctness 为 not_configured。 |
| block | strict_golden_fund_not_covered | fund | 110020 | future index evidence sufficiency gate | index reviewed fact freeze / methodology / constituents evidence gate | 110020 不在 strict golden answer v1 fund-level coverage 中。 |
| block | fixture_promotion_absent | fund | 110020 | future index evidence sufficiency gate | index reviewed fact freeze / methodology / constituents evidence gate | 110020 未发现 accepted fixture promotion state。 |
| block | reviewed_candidate_not_promoted | fund | 110020 | future index evidence sufficiency gate | index reviewed fact freeze / methodology / constituents evidence gate | 110020 仅 accepted 为 reviewed coverage candidate input，尚未 promotion。 |
| block | index_evidence_insufficient | fund | 110020 | future index evidence sufficiency gate | index reviewed fact freeze / methodology / constituents evidence gate | 110020 methodology/constituents/reviewed fact freeze 证据仍不足。 |
| block | strict_golden_not_configured | fund | 096001 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 096001 score correctness 为 not_configured。 |
| block | quality_gate_block | fund | 096001 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 096001 quality gate status=block。 |
| block | strict_golden_fund_not_covered | fund | 096001 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 096001 不在 strict golden answer v1 fund-level coverage 中。 |
| block | fixture_promotion_absent | fund | 096001 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 096001 未发现 accepted fixture promotion state。 |
| block | qdii_coverage_blocked | slot | 096001 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | QDII replacement hard stop accepted; candidate quality block after eligible provenance. |
| block | strict_golden_not_configured | fund | 040046 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 040046 score correctness 为 not_configured。 |
| block | quality_gate_block | fund | 040046 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 040046 quality gate status=block。 |
| block | strict_golden_fund_not_covered | fund | 040046 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 040046 不在 strict golden answer v1 fund-level coverage 中。 |
| block | fixture_promotion_absent | fund | 040046 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 040046 未发现 accepted fixture promotion state。 |
| block | qdii_coverage_blocked | slot | 040046 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | QDII replacement hard stop accepted; candidate quality block after eligible provenance. |
| block | strict_golden_not_configured | fund | 019172 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 019172 score correctness 为 not_configured。 |
| block | quality_gate_block | fund | 019172 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 019172 quality gate status=block。 |
| block | strict_golden_fund_not_covered | fund | 019172 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 019172 不在 strict golden answer v1 fund-level coverage 中。 |
| block | fixture_promotion_absent | fund | 019172 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 019172 未发现 accepted fixture promotion state。 |
| block | qdii_coverage_blocked | slot | 019172 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | QDII replacement hard stop accepted; candidate quality block after eligible provenance. |
| block | strict_golden_not_configured | fund | 021539 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 021539 score correctness 为 not_configured。 |
| block | quality_gate_block | fund | 021539 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 021539 quality gate status=block。 |
| block | strict_golden_fund_not_covered | fund | 021539 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 021539 不在 strict golden answer v1 fund-level coverage 中。 |
| block | fixture_promotion_absent | fund | 021539 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | 021539 未发现 accepted fixture promotion state。 |
| block | qdii_coverage_blocked | slot | 021539 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate | QDII replacement hard stop accepted; candidate quality block after eligible provenance. |
| block | fof_taxonomy_pending | slot | FOF_SLOT | future FOF taxonomy / pure FOF candidate gate | pure FOF repository-verified candidate gate | Pure FOF taxonomy pending；QDII-FOF 不可计为 pure FOF。 |
| block | fof_data_gap | slot | FOF_SLOT | future FOF taxonomy / pure FOF candidate gate | pure FOF repository-verified candidate gate | 缺少 repository-verified pure FOF candidate。 |

## Owner / Next Gate

| fund_code | owner | next_gate |
|---|---|---|
| 004393 | future baseline preflight owner | fixture promotion / strict golden coverage gate |
| 004194 | future baseline preflight owner | fixture promotion / strict golden coverage gate |
| 017641 | future baseline preflight owner | quality block disposition / fixture promotion gate |
| 006597 | future baseline/golden preflight owner | fixture promotion / strict golden coverage gate |
| 110020 | future index evidence sufficiency gate | index reviewed fact freeze / methodology / constituents evidence gate |
| 096001 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate |
| 040046 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate |
| 019172 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate |
| 021539 | future QDII diagnosis or taxonomy / asset-class fitness gate | QDII diagnosis or explicit QDII deferred-from-v1 disposition gate |
| FOF_SLOT | future FOF taxonomy / pure FOF candidate gate | pure FOF repository-verified candidate gate |

## Missing Input / Blocking Questions

- 是否产出 accepted fixture promotion state manifest，并由独立 gate 接受？
- pure FOF coverage 是否已有 repository-verified candidate 和 taxonomy gate？
- 110020 是否完成 methodology/constituents/reviewed fact freeze gate？

## Non-goals And Guardrails

- 不修改 score policy、quality gate severity、FQ0-FQ6 或 final judgment。
- 不修改 golden answer JSON、golden fixtures 或 fixture promotion state。
- 不直接访问 PDF/cache/source helper；年报访问边界保持在 FundDocumentRepository。
- 不引入 Host/Agent/dayu、不执行 push/PR/merge/release/golden promotion。
