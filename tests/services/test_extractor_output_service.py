"""Extractor output Service 测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractor_output_repository import (
    EXTRACTOR_OUTPUT_SCHEMA_VERSION,
    ExtractorOutputIdentity,
    ExtractorOutputRecord,
)
from fund_agent.services.extractor_output_service import (
    ExtractorOutputSaveRequest,
    ExtractorOutputService,
)
from tests.services.test_fund_analysis_service import _bundle


class _FakeExtractor:
    """Service 测试用 fake extractor。"""

    def __init__(self, bundle: StructuredFundDataBundle) -> None:
        """初始化 fake extractor。

        Args:
            bundle: 待返回的结构化基金数据包。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.bundle = bundle
        self.calls: list[tuple[str, int, bool]] = []

    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> StructuredFundDataBundle:
        """记录调用并返回 fake bundle。

        Args:
            fund_code: 基金代码。
            report_year: 报告年份。
            force_refresh: 是否强制刷新。

        Returns:
            fake bundle。

        Raises:
            无显式抛出。
        """

        self.calls.append((fund_code, report_year, force_refresh))
        return self.bundle


class _FakeRepository:
    """Service 测试用 fake repository。"""

    def __init__(self, path: Path) -> None:
        """初始化 fake repository。

        Args:
            path: 返回记录使用的路径。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.path = path
        self.calls: list[tuple[StructuredFundDataBundle, str]] = []

    def save(
        self,
        *,
        bundle: StructuredFundDataBundle,
        report_type: str = "annual_report",
    ) -> ExtractorOutputRecord:
        """记录保存调用并返回 fake record。

        Args:
            bundle: 结构化数据包。
            report_type: 报告类型。

        Returns:
            fake 保存记录。

        Raises:
            无显式抛出。
        """

        self.calls.append((bundle, report_type))
        return ExtractorOutputRecord(
            schema_version=EXTRACTOR_OUTPUT_SCHEMA_VERSION,
            identity=ExtractorOutputIdentity(
                fund_code=bundle.fund_code,
                report_type=report_type,
                report_year=bundle.report_year,
            ),
            created_at="2026-06-21T00:00:00+00:00",
            bundle_payload={"fund_code": bundle.fund_code},
            path=self.path,
        )


@pytest.mark.asyncio
async def test_service_saves_extractor_output_with_injected_dependencies(
    tmp_path: Path,
) -> None:
    """验证 Service 只编排 fake extractor 和 fake repository。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Service 参数转发或依赖边界错误时抛出。
    """

    fake_extractor = _FakeExtractor(_bundle())
    fake_repositories: list[_FakeRepository] = []

    def _repository_factory(root_dir: Path | None) -> _FakeRepository:
        """构造 fake repository 并记录 root_dir。

        Args:
            root_dir: Service 传入的输出根目录。

        Returns:
            fake repository。

        Raises:
            无显式抛出。
        """

        repository = _FakeRepository((root_dir or tmp_path) / "structured_fund_data.json")
        fake_repositories.append(repository)
        return repository

    service = ExtractorOutputService(
        extractor=fake_extractor,
        repository_factory=_repository_factory,
    )

    record = await service.save(
        ExtractorOutputSaveRequest(
            fund_code="110011",
            report_year=2024,
            report_type="annual_report",
            output_root=tmp_path,
            force_refresh=True,
        )
    )

    assert fake_extractor.calls == [("110011", 2024, True)]
    assert len(fake_repositories) == 1
    assert fake_repositories[0].calls == [(fake_extractor.bundle, "annual_report")]
    assert record.path == tmp_path / "structured_fund_data.json"
    assert record.identity.fund_code == "110011"
    assert record.identity.report_type == "annual_report"
    assert record.identity.report_year == 2024


@pytest.mark.asyncio
async def test_service_validates_request_before_extraction(tmp_path: Path) -> None:
    """验证非法请求不会触发 extractor 或 repository。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法请求仍触发依赖调用时抛出。
    """

    fake_extractor = _FakeExtractor(_bundle())
    repository_calls: list[Path | None] = []
    service = ExtractorOutputService(
        extractor=fake_extractor,
        repository_factory=lambda root_dir: repository_calls.append(root_dir) or _FakeRepository(
            tmp_path / "unused.json"
        ),
    )

    with pytest.raises(ValueError, match="fund_code"):
        await service.save(
            ExtractorOutputSaveRequest(
                fund_code="11011",
                report_year=2024,
                report_type="annual_report",
                output_root=tmp_path,
            )
        )
    with pytest.raises(ValueError, match="report_year"):
        await service.save(
            ExtractorOutputSaveRequest(
                fund_code="110011",
                report_year=0,
                report_type="annual_report",
                output_root=tmp_path,
            )
        )
    with pytest.raises(ValueError, match="annual_report"):
        await service.save(
            ExtractorOutputSaveRequest(
                fund_code="110011",
                report_year=2024,
                report_type="quarterly_report",
                output_root=tmp_path,
            )
        )

    assert fake_extractor.calls == []
    assert repository_calls == []


@pytest.mark.asyncio
async def test_service_rejects_extractor_bundle_identity_mismatch(tmp_path: Path) -> None:
    """验证 extractor 返回身份不一致的 bundle 时不写 repository。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: mismatch bundle 被保存时抛出。
    """

    fake_extractor = _FakeExtractor(_bundle())
    repository_calls: list[Path | None] = []
    service = ExtractorOutputService(
        extractor=fake_extractor,
        repository_factory=lambda root_dir: repository_calls.append(root_dir) or _FakeRepository(
            tmp_path / "unused.json"
        ),
    )

    with pytest.raises(RuntimeError, match="bundle identity mismatch"):
        await service.save(
            ExtractorOutputSaveRequest(
                fund_code="004393",
                report_year=2024,
                report_type="annual_report",
                output_root=tmp_path,
            )
        )

    assert fake_extractor.calls == [("004393", 2024, False)]
    assert repository_calls == []
