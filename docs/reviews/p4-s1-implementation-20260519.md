# P4-S1 Implementation Artifact

> 日期：2026-05-19
> Gate：`P4-S1 implementation`
> 结论：实现完成，进入 `P4-S1 code review`。

## Scope

本 slice 实现 Selected Fund Extraction Snapshot + Quality Gate MVP，只记录当前真实抽取质量，不修复 `004393` 分类器或 extractor 缺口。

## Changed Paths

- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/services/extraction_snapshot_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_extraction_snapshot.py`
- `tests/services/test_extraction_snapshot_service.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/implementation-control-p4.md`
- `docs/implementation-control.md`

## Implementation Notes

- Snapshot 核心能力位于 Capability 层 `fund_agent/fund/extraction_snapshot.py`。
- UI 通过 `ExtractionSnapshotService` 调用，不直接依赖 Capability。
- 年报与净值数据只通过 `FundDataExtractor.extract(...)` 进入，不直接读取 PDF、cache 或底层解析文件。
- 输入参数显式建模为 `ExtractionSnapshotRequest`，不使用 `extra_payload`。
- Snapshot 输出 `snapshot.jsonl`、`summary.md`、`errors.jsonl`。
- `004393` 若被识别为 `index_fund`，记录为 known failure，不静默覆盖。
- `016492` 重复只在 summary 标红，不阻断 P4-S1。

## Validation

- `.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/ui/test_cli.py tests/services -q`
  - `13 passed in 0.70s`
- `.venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py tests/ui/test_cli.py tests/services tests/scripts/test_selected_funds_smoke.py -q`
  - `17 passed in 0.39s`
- `.venv/bin/python scripts/selected_funds_smoke.py --limit 1`
  - dry-run passed；确认 `docs/code_20260519.csv` 为 56 条记录、55 个唯一代码、重复代码 `016492`
- `.venv/bin/fund-analysis extraction-snapshot --help`
  - passed
- `git diff --check ...`
  - passed

## Residual Risks

- 未运行真实 `fund-analysis extraction-snapshot --run-id ... --fund-code 004393`，因为会触发真实年报仓库、PDF/network 与净值数据路径；保留给人工 smoke 或后续 P4-S1 review/fix gate。
- P4-S1 仅计算 coverage / traceability 粗粒度统计，不评估 correctness；correctness 留到 P4-S2 golden set。
- `004393` 分类误判仍未修复，按计划进入 P4-S3。
