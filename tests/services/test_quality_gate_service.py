"""报告质量 gate Service 测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from fund_agent.fund.quality_gate import QualityGateResult
from fund_agent.services import QualityGateRequest, QualityGateService
from fund_agent.services import quality_gate_service


def test_quality_gate_service_delegates_explicit_params(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    """验证 Service 显式转发 score 路径和输出目录。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当参数转发不符合契约时抛出。
    """

    calls = []

    def fake_run_quality_gate(**kwargs):  # type: ignore[no-untyped-def]
        """记录 Service 转发参数并返回固定 gate 结果。

        Args:
            kwargs: Service 转发给 Capability 的参数。

        Returns:
            fake gate 结果。

        Raises:
            无显式抛出。
        """

        calls.append(kwargs)
        return QualityGateResult(
            score_path=kwargs["score_path"],
            output_dir=tmp_path,
            gate_json_path=tmp_path / "quality_gate.json",
            gate_markdown_path=tmp_path / "quality_gate.md",
            status="pass",
            issues=(),
        )

    monkeypatch.setattr(quality_gate_service, "run_quality_gate", fake_run_quality_gate)
    service = QualityGateService()
    request = QualityGateRequest(score_path=tmp_path / "score.json", output_dir=tmp_path)

    result = service.run(request)

    assert result.status == "pass"
    assert calls == [{"score_path": tmp_path / "score.json", "output_dir": tmp_path}]


def test_quality_gate_service_rejects_non_json_score(tmp_path: Path) -> None:
    """验证 Service 拒绝非 JSON score 路径。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 score 路径未被拒绝时抛出。
    """

    service = QualityGateService()
    request = QualityGateRequest(score_path=tmp_path / "score.md", output_dir=None)

    with pytest.raises(ValueError, match="json"):
        service.run(request)
