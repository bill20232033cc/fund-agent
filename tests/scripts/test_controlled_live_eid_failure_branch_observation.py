"""受控 live EID observation helper 的 no-live serializer regression 测试。"""

from __future__ import annotations

from types import SimpleNamespace

from scripts.controlled_live_eid_failure_branch_observation import _safe_report_payload


def test_safe_report_payload_uses_only_current_metadata_fields() -> None:
    """验证成功 payload 不再读取不存在的 identity/integrity metadata 字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: payload 字段不符合当前安全标量契约时抛出。
    """

    report = SimpleNamespace(
        key=SimpleNamespace(
            fund_code="006597",
            year=2024,
            document_kind="annual_report",
        ),
        sections=("section-a", "section-b"),
        tables=("table-a",),
        raw_text="safe scalar text",
        metadata=SimpleNamespace(
            source=SimpleNamespace(
                source="eid",
                selected_source="eid",
                source_mode="single_source_only",
                fallback_enabled=False,
                fallback_used=False,
                primary_failure_category=None,
                discovery_contract_version="eid_fund_v1",
            ),
            cache=SimpleNamespace(
                pdf_cache_hit=False,
                parsed_cache_hit=False,
                source_metadata_present=True,
            ),
        ),
    )

    payload = _safe_report_payload(report)

    assert payload["status"] == "success"
    assert payload["fund_code"] == "006597"
    assert payload["report_year"] == 2024
    assert payload["source"] == "eid"
    assert payload["selected_source"] == "eid"
    assert payload["source_mode"] == "single_source_only"
    assert payload["fallback_enabled"] is False
    assert payload["fallback_used"] is False
    assert payload["discovery_contract_version"] == "eid_fund_v1"
    assert "identity_status" not in payload
    assert "integrity_status" not in payload
