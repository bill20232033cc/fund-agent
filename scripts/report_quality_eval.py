"""report-quality 维护者离线校验入口。

本脚本是 maintainer-only / dev-only 工具，只消费调用方显式传入的
report-quality JSONL artifact 或单个 bundle JSON artifact，并调用
`validate_report_quality_jsonl()` / `validate_report_quality_bundle()` 输出
小型 JSON 汇总。它不属于产品 CLI，不读取年报、不调用文档仓库、不触发
extractor、renderer、Service、Host、Agent 或 FQ0-FQ6 质量门控。
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fund_agent.fund.report_quality_validation import (
    ReportQualityValidationResult,
    validate_report_quality_bundle,
    validate_report_quality_jsonl,
)


def main(argv: list[str] | None = None) -> int:
    """执行 report-quality artifact 离线校验。

    Args:
        argv: 命令行参数；为 None 时从系统命令行读取。

    Returns:
        进程退出码。校验成功写出 summary 后返回 0。

    Raises:
        SystemExit: argparse 参数解析失败时抛出。
        FileNotFoundError: 输入文件不存在时由 validator 或本脚本抛出。
        json.JSONDecodeError: bundle JSON 无法解析时抛出。
    """

    args = _parse_args(argv)
    results = _run_validations(
        jsonl_paths=args.jsonl,
        bundle_paths=args.bundle,
        run_id=args.run_id,
    )
    payload = _build_output_payload(results)
    _write_output(args.output, payload)
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    """解析维护者工具命令行参数。

    Args:
        argv: 命令行参数。

    Returns:
        argparse 命名空间。

    Raises:
        SystemExit: 参数缺失或非法时抛出。
    """

    parser = argparse.ArgumentParser(
        description=(
            "Dev-only report-quality validator wrapper. "
            "Consumes explicit JSONL or bundle JSON files and writes summary JSON."
        )
    )
    parser.add_argument(
        "--jsonl",
        action="append",
        default=[],
        type=Path,
        metavar="PATH",
        help="Existing report-quality JSONL artifact path. May be repeated.",
    )
    parser.add_argument(
        "--bundle",
        action="append",
        default=[],
        type=Path,
        metavar="PATH",
        help="Existing single-bundle JSON artifact path. May be repeated.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        metavar="PATH",
        help="Summary JSON output path under caller-chosen scratch space.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional explicit validator run id passed through to both validators.",
    )
    args = parser.parse_args(argv)
    if not args.jsonl and not args.bundle:
        parser.error("at least one --jsonl or --bundle path is required")
    return args


def _run_validations(
    *,
    jsonl_paths: list[Path],
    bundle_paths: list[Path],
    run_id: str | None,
) -> list[ReportQualityValidationResult]:
    """按调用方显式输入运行 validator。

    Args:
        jsonl_paths: JSONL artifact 路径列表。
        bundle_paths: bundle JSON artifact 路径列表。
        run_id: 显式 validator run id。

    Returns:
        每个输入对应的 validator 结果。

    Raises:
        FileNotFoundError: 输入文件不存在时抛出。
        json.JSONDecodeError: bundle JSON 无法解析时抛出。
    """

    results: list[ReportQualityValidationResult] = []
    for jsonl_path in jsonl_paths:
        results.append(validate_report_quality_jsonl(jsonl_path, run_id=run_id))
    for bundle_path in bundle_paths:
        bundle = _load_bundle_json(bundle_path)
        results.append(
            validate_report_quality_bundle(
                bundle,
                source_path=str(bundle_path),
                run_id=run_id,
            )
        )
    return results


def _load_bundle_json(bundle_path: Path) -> dict[str, object]:
    """读取单个 bundle JSON artifact。

    Args:
        bundle_path: bundle JSON 文件路径。

    Returns:
        bundle JSON object。

    Raises:
        FileNotFoundError: 输入文件不存在时抛出。
        json.JSONDecodeError: 文件不是合法 JSON 时抛出。
        TypeError: JSON 顶层不是 object 时抛出。
    """

    with bundle_path.open("r", encoding="utf-8") as file_obj:
        parsed = json.load(file_obj)
    if not isinstance(parsed, dict):
        raise TypeError(f"bundle JSON must be an object: {bundle_path}")
    return parsed


def _build_output_payload(results: list[ReportQualityValidationResult]) -> dict[str, Any]:
    """构造写入磁盘的小型 JSON 汇总。

    Args:
        results: validator 结果列表。

    Returns:
        可 JSON 序列化的汇总 payload。
    """

    issue_counts = Counter[str]()
    total_records = 0
    scoring_ready_record_count = 0
    blocking_count = 0
    material_count = 0
    minor_count = 0
    failed_closed = False

    inputs: list[dict[str, Any]] = []
    for result in results:
        summary = result.summary
        total_records += summary.total_records
        scoring_ready_record_count += summary.scoring_ready_record_count
        blocking_count += summary.blocking_count
        material_count += summary.material_count
        minor_count += summary.minor_count
        failed_closed = failed_closed or summary.failed_closed
        issue_counts.update(dict(summary.error_code_counts))
        inputs.append(_serialize_result(result))

    return {
        "input_count": len(results),
        "summary": {
            "total_records": total_records,
            "blocking_count": blocking_count,
            "material_count": material_count,
            "minor_count": minor_count,
            "error_code_counts": sorted(issue_counts.items()),
            "scoring_ready_record_count": scoring_ready_record_count,
            "failed_closed": failed_closed,
        },
        "inputs": inputs,
    }


def _serialize_result(result: ReportQualityValidationResult) -> dict[str, Any]:
    """序列化单个 validator 结果。

    Args:
        result: validator 结果。

    Returns:
        可 JSON 序列化的单输入结果。
    """

    return {
        "source_path": result.source_path,
        "run_id": result.run_id,
        "schema_version": result.schema_version,
        "summary": asdict(result.summary),
        "issues": [asdict(issue) for issue in result.issues],
    }


def _write_output(output_path: Path, payload: dict[str, Any]) -> None:
    """写出 summary JSON。

    Args:
        output_path: 输出文件路径。
        payload: 输出 payload。

    Returns:
        无返回值。
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    raise SystemExit(main())
