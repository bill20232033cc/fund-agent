"""单基金 quality gate 集成 adapter 测试。"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from fund_agent.fund.quality_gate_integration import run_quality_gate_for_bundle
from tests.services.test_fund_analysis_service import _bundle


def test_run_quality_gate_for_bundle_writes_score_and_gate_without_reextracting(tmp_path: Path) -> None:
    """验证 adapter 基于已抽取 bundle 生成 score/gate 产物。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 adapter 未写出预期产物时抛出。
    """

    source_csv = _source_csv(tmp_path, "110011")
    output_dir = tmp_path / "gate-run"

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=source_csv,
        output_dir=output_dir,
        run_id="fixture-run",
        golden_answer_path=None,
    )

    score_payload = json.loads(result.score_result.score_json_path.read_text(encoding="utf-8"))

    assert result.not_run_reason is None
    assert result.snapshot_path.exists()
    assert result.score_result is not None
    assert result.quality_gate_result is not None
    assert result.quality_gate_result.gate_json_path.exists()
    assert score_payload["fund_scores"][0]["fund_code"] == "110011"
    assert score_payload["golden_set"]["records"] == []


def test_run_quality_gate_for_bundle_not_run_when_fund_absent(tmp_path: Path) -> None:
    """验证基金不在精选池时不伪造 App 类别且不写运行产物。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 adapter 错误继续运行时抛出。
    """

    source_csv = _source_csv(tmp_path, "004393")
    output_dir = tmp_path / "gate-run"

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=source_csv,
        output_dir=output_dir,
        run_id="fixture-run",
        golden_answer_path=None,
    )

    assert result.quality_gate_result is None
    assert result.score_result is None
    assert result.not_run_reason == "fund_code `110011` not found in quality gate source csv"
    assert not output_dir.exists()


def _source_csv(tmp_path: Path, fund_code: str) -> Path:
    """写入测试用精选基金池 CSV。

    Args:
        tmp_path: pytest 临时目录 fixture。
        fund_code: CSV 中的基金代码。

    Returns:
        CSV 路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    source_csv = tmp_path / "selected.csv"
    source_csv.write_text(
        f"基金名称,基金代码,类别\n测试基金,{fund_code},国内股票类\n",
        encoding="utf-8",
    )
    return source_csv


def _bundle_with_code(fund_code: str):
    """构造指定基金代码的结构化数据包。

    Args:
        fund_code: 基金代码。

    Returns:
        结构化数据包。

    Raises:
        无显式抛出。
    """

    return replace(_bundle(), fund_code=fund_code)
