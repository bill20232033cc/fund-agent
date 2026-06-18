"""FundDisclosureDocument candidate source failure mapping 测试。"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from fund_agent.fund.documents.candidates.fund_disclosure_failure_mapping import (
    PROJECTION_BLOCKERS,
    SOURCE_FAILURE_CODES,
    FundDisclosureFailureContext,
    map_fund_disclosure_failure_to_source_category,
    mapped_fund_disclosure_source_failure_codes,
)


class TestFailureMappingComplete:
    """验证 source failure code 映射闭合。"""

    def test_all_source_failure_codes_are_mapped(self) -> None:
        """所有 source failure code 都能映射到 canonical failure category。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射集合不闭合时抛出。
        """

        assert mapped_fund_disclosure_source_failure_codes() == frozenset(SOURCE_FAILURE_CODES)
        for failure_code in SOURCE_FAILURE_CODES:
            assert map_fund_disclosure_failure_to_source_category(failure_code) in {
                "not_found",
                "unavailable",
                "schema_drift",
                "identity_mismatch",
                "integrity_error",
            }


class TestFailureMappingRedirectUnavailableDecisionTable:
    """验证 redirect_unavailable 总有序决策表。"""

    def test_non_eid_domain_has_priority_over_5xx(self) -> None:
        """非 EID redirect 域名优先判为 identity_mismatch。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 优先级错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "redirect_unavailable",
            FundDisclosureFailureContext(redirect_domain="example.com", http_status=503),
        )

        assert result == "identity_mismatch"

    def test_5xx_maps_to_unavailable(self) -> None:
        """官方域名 5xx 映射为 unavailable。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "redirect_unavailable",
            FundDisclosureFailureContext(redirect_domain="eid.csrc.gov.cn", http_status=502),
        )

        assert result == "unavailable"

    @pytest.mark.parametrize("error_type", ("timeout", "dns", "tls"))
    def test_transport_errors_map_to_unavailable(self, error_type: str) -> None:
        """timeout/DNS/TLS 映射为 unavailable。

        Args:
            error_type: 连接层错误类型。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "redirect_unavailable",
            FundDisclosureFailureContext(
                redirect_domain="eid.csrc.gov.cn",
                error_type=error_type,
            ),
        )

        assert result == "unavailable"

    @pytest.mark.parametrize("http_status", (404, 410))
    def test_4xx_maps_to_not_found(self, http_status: int) -> None:
        """官方域名 404/410 映射为 not_found。

        Args:
            http_status: HTTP 状态码。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "redirect_unavailable",
            FundDisclosureFailureContext(
                redirect_domain="eid.csrc.gov.cn",
                http_status=http_status,
            ),
        )

        assert result == "not_found"

    def test_insufficient_facts_maps_to_unavailable(self) -> None:
        """事实不足时保守映射为 unavailable。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        assert (
            map_fund_disclosure_failure_to_source_category("redirect_unavailable") == "unavailable"
        )


class TestFailureMappingRenderUnavailableDecisionTable:
    """验证 render_unavailable 总有序决策表。"""

    def test_200_empty_body_maps_to_schema_drift(self) -> None:
        """HTTP 200 空 body 映射为 schema_drift。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "render_unavailable",
            FundDisclosureFailureContext(http_status=200, body_empty=True),
        )

        assert result == "schema_drift"

    def test_200_non_html_maps_to_schema_drift(self) -> None:
        """HTTP 200 非 HTML body 映射为 schema_drift。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "render_unavailable",
            FundDisclosureFailureContext(http_status=200, body_empty=False, body_is_html=False),
        )

        assert result == "schema_drift"

    def test_consistent_structure_absence_maps_to_schema_drift(self) -> None:
        """HTML body 稳定缺结构映射为 schema_drift。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "render_unavailable",
            FundDisclosureFailureContext(
                http_status=200,
                body_is_html=True,
                structure_absence_observed_consistently=True,
            ),
        )

        assert result == "schema_drift"

    def test_5xx_maps_to_unavailable(self) -> None:
        """render URL 5xx 映射为 unavailable。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "render_unavailable",
            FundDisclosureFailureContext(http_status=503, render_url_known=True),
        )

        assert result == "unavailable"

    @pytest.mark.parametrize("http_status", (404, 410))
    def test_known_render_url_4xx_maps_to_not_found(self, http_status: int) -> None:
        """已知 render URL 404/410 映射为 not_found。

        Args:
            http_status: HTTP 状态码。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "render_unavailable",
            FundDisclosureFailureContext(http_status=http_status, render_url_known=True),
        )

        assert result == "not_found"

    def test_insufficient_facts_maps_to_unavailable(self) -> None:
        """render facts 不足时保守映射为 unavailable。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "render_unavailable",
            FundDisclosureFailureContext(
                http_status=None,
                body_empty=False,
                body_is_html=True,
                structure_absence_observed_consistently=False,
            ),
        )

        assert result == "unavailable"


class TestFailureMappingSimpleCodes:
    """验证不需要 context 的 source failure code。"""

    @pytest.mark.parametrize(
        ("failure_code", "expected"),
        (
            ("index_unavailable", "unavailable"),
            ("list_row_missing", "not_found"),
            ("identity_mismatch", "identity_mismatch"),
            ("render_domain_mismatch", "identity_mismatch"),
            ("render_structure_missing", "schema_drift"),
            ("locator_unstable", "schema_drift"),
        ),
    )
    def test_simple_code_mapping(self, failure_code: str, expected: str) -> None:
        """简单 source failure code 映射符合 accepted table。

        Args:
            failure_code: candidate source failure code。
            expected: 预期 canonical category。

        Returns:
            无返回值。

        Raises:
            AssertionError: 映射错误时抛出。
        """

        assert map_fund_disclosure_failure_to_source_category(failure_code) == expected  # type: ignore[arg-type]


class TestFailureMappingMixedFacts:
    """验证 accepted plan 中列出的 mixed-fact 组合。"""

    def test_non_eid_redirect_plus_4xx_maps_to_identity_mismatch(self) -> None:
        """非 EID redirect + 4xx 仍映射为 identity_mismatch。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 优先级错误时抛出。
        """

        result = map_fund_disclosure_failure_to_source_category(
            "redirect_unavailable",
            FundDisclosureFailureContext(redirect_domain="example.com", http_status=404),
        )

        assert result == "identity_mismatch"

    def test_all_required_mixed_fact_examples(self) -> None:
        """一次性验证 plan 中剩余 mixed-fact 样例。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 任一样例映射错误时抛出。
        """

        assert (
            map_fund_disclosure_failure_to_source_category(
                "render_unavailable",
                FundDisclosureFailureContext(http_status=404, render_url_known=True),
            )
            == "not_found"
        )
        assert (
            map_fund_disclosure_failure_to_source_category(
                "render_unavailable",
                FundDisclosureFailureContext(http_status=200, body_empty=True),
            )
            == "schema_drift"
        )
        assert (
            map_fund_disclosure_failure_to_source_category(
                "render_unavailable",
                FundDisclosureFailureContext(http_status=200, body_is_html=False),
            )
            == "schema_drift"
        )
        assert (
            map_fund_disclosure_failure_to_source_category(
                "render_unavailable",
                FundDisclosureFailureContext(
                    http_status=200,
                    body_is_html=True,
                    structure_absence_observed_consistently=True,
                ),
            )
            == "schema_drift"
        )
        assert (
            map_fund_disclosure_failure_to_source_category("redirect_unavailable") == "unavailable"
        )
        assert map_fund_disclosure_failure_to_source_category("render_unavailable") == "unavailable"


class TestProjectionBlockerRaisesValueError:
    """验证 projection blocker 不进入 source failure mapping。"""

    @pytest.mark.parametrize("failure_code", PROJECTION_BLOCKERS)
    def test_projection_blocker_raises_value_error(self, failure_code: str) -> None:
        """projection blocker 传入 mapping 时 fail-closed。

        Args:
            failure_code: projection blocker code。

        Returns:
            无返回值。

        Raises:
            AssertionError: 未抛出 ValueError 时抛出。
        """

        with pytest.raises(ValueError):
            map_fund_disclosure_failure_to_source_category(failure_code)  # type: ignore[arg-type]


class TestFailureMappingUnknownCode:
    """验证未知 code fail-closed。"""

    def test_unknown_string_raises_value_error(self) -> None:
        """未知字符串传入 mapping 时抛出 ValueError。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 未抛出 ValueError 时抛出。
        """

        with pytest.raises(ValueError):
            map_fund_disclosure_failure_to_source_category("unexpected_code")  # type: ignore[arg-type]


class TestFailureMappingImportBoundaries:
    """验证 failure mapping import 边界。"""

    def test_mapping_imports_canonical_failure_category_from_documents_models(self) -> None:
        """mapping module 从 documents.models 引入 canonical category。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: import 来源错误时抛出。
        """

        tree = ast.parse(
            Path(
                "fund_agent/fund/documents/candidates/fund_disclosure_failure_mapping.py"
            ).read_text(encoding="utf-8")
        )
        imported = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
            if alias.name == "AnnualReportSourceFailureCategory"
        }

        assert imported == {"fund_agent.fund.documents.models"}

    def test_mapping_does_not_import_evidence_source_kind(self) -> None:
        """mapping module 不依赖 extractor EvidenceSourceKind。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 发现 forbidden import 时抛出。
        """

        tree = ast.parse(
            Path(
                "fund_agent/fund/documents/candidates/fund_disclosure_failure_mapping.py"
            ).read_text(encoding="utf-8")
        )
        modules = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module is not None
        }

        assert "fund_agent.fund.extractors.models" not in modules
