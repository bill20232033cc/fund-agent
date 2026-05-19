"""精选基金池抽取快照 Service 测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from fund_agent.fund.extraction_snapshot import SnapshotRunResult, SelectedFundPoolValidation
from fund_agent.services import ExtractionSnapshotRequest, ExtractionSnapshotService
from fund_agent.services import extraction_snapshot_service


@pytest.mark.asyncio
async def test_extraction_snapshot_service_delegates_explicit_params(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    """验证 Service 以显式参数委托 Capability 层快照能力。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当参数转发或结果不符合契约时抛出。
    """

    calls = []

    async def fake_run_extraction_snapshot(**kwargs):  # type: ignore[no-untyped-def]
        """记录 Service 转发参数并返回固定结果。

        Args:
            kwargs: Service 转发给 Capability 的参数。

        Returns:
            fake 快照运行结果。

        Raises:
            无显式抛出。
        """

        calls.append(kwargs)
        return SnapshotRunResult(
            run_id=kwargs["run_id"],
            output_dir=tmp_path,
            snapshot_path=tmp_path / "snapshot.jsonl",
            summary_path=tmp_path / "summary.md",
            errors_path=tmp_path / "errors.jsonl",
            selected_count=1,
            succeeded_fund_codes=("004393",),
            failed_fund_codes=(),
            record_count=14,
            validation=SelectedFundPoolValidation(missing_rows=(), bad_code_rows=(), duplicate_codes=()),
        )

    monkeypatch.setattr(extraction_snapshot_service, "run_extraction_snapshot", fake_run_extraction_snapshot)
    service = ExtractionSnapshotService()
    request = ExtractionSnapshotRequest(
        fund_code="004393",
        report_year=2024,
        source_csv=Path("docs/code_20260519.csv"),
        run_id="unit-run",
        output_dir=tmp_path,
        force_refresh=True,
        sample_per_category=2,
        limit=3,
    )

    result = await service.run(request)

    assert result.run_id == "unit-run"
    assert len(calls) == 1
    assert calls[0] == {
        "fund_code": "004393",
        "report_year": 2024,
        "source_csv": Path("docs/code_20260519.csv"),
        "run_id": "unit-run",
        "output_dir": tmp_path,
        "force_refresh": True,
        "sample_per_category": 2,
        "limit": 3,
    }


@pytest.mark.asyncio
async def test_extraction_snapshot_service_rejects_invalid_fund_code() -> None:
    """验证 Service 层先拒绝非法显式基金代码。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法基金代码未被拒绝时抛出。
    """

    service = ExtractionSnapshotService()
    request = ExtractionSnapshotRequest(
        fund_code="ABC",
        report_year=2024,
        source_csv=Path("docs/code_20260519.csv"),
        run_id="unit-run",
        output_dir=None,
        force_refresh=False,
    )

    with pytest.raises(ValueError, match="fund_code"):
        await service.run(request)
