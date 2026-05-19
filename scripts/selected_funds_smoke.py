#!/usr/bin/env python3
"""有知有行精选基金池真实路径 smoke 辅助脚本。

该脚本默认只读取 `docs/code_20260519.csv`，校验基金代码、类别和重复项，
并打印将要执行的 `fund-analysis analyze` 命令。只有显式传入 `--run` 时，
才会调用 CLI 触发真实 PDF / network 路径。
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Final, Sequence

DEFAULT_SELECTED_FUNDS_CSV: Final[Path] = Path("docs/code_20260519.csv")
DEFAULT_REPORT_YEAR: Final[int] = 2024
DEFAULT_OUTPUT_DIR: Final[Path] = Path("reports/smoke")
REQUIRED_COLUMNS: Final[tuple[str, ...]] = ("基金名称", "基金代码", "类别")
DEFAULT_CURRENT_STAGE: Final[str] = "真实精选基金池 smoke：仅验证年报下载、解析、报告渲染和程序审计链路。"


@dataclass(frozen=True, slots=True)
class SelectedFund:
    """精选基金池中的单条基金记录。

    Attributes:
        line_number: CSV 中的原始行号。
        name: 基金名称。
        code: 6 位基金代码。
        category: 有知有行 App 内分类。
    """

    line_number: int
    name: str
    code: str
    category: str


@dataclass(frozen=True, slots=True)
class PoolValidation:
    """精选基金池校验结果。

    Attributes:
        missing_rows: 缺少必填字段的行号列表。
        bad_code_rows: 基金代码不是 6 位数字的行号和代码。
        duplicate_codes: 重复出现的基金代码。
    """

    missing_rows: tuple[int, ...]
    bad_code_rows: tuple[tuple[int, str], ...]
    duplicate_codes: tuple[str, ...]

    @property
    def has_errors(self) -> bool:
        """返回是否存在严格模式下应失败的问题。

        Args:
            无。

        Returns:
            存在缺失字段、非法代码或重复代码时返回 `True`。

        Raises:
            无显式抛出。
        """

        return bool(self.missing_rows or self.bad_code_rows or self.duplicate_codes)


@dataclass(frozen=True, slots=True)
class SmokeRecord:
    """单只基金 smoke 执行记录。

    Attributes:
        fund: 被测试的精选基金。
        command: 实际执行命令。
        returncode: 进程退出码。
        duration_seconds: 墙钟耗时秒数。
        stdout_path: 报告 stdout 保存路径。
        stderr_path: stderr 保存路径。
        quality_gate_status: CLI stderr 中的 quality gate 状态。
        started_at: 开始时间。
        finished_at: 结束时间。
    """

    fund: SelectedFund
    command: tuple[str, ...]
    returncode: int
    duration_seconds: float
    stdout_path: Path
    stderr_path: Path
    quality_gate_status: str | None
    started_at: str
    finished_at: str

    def to_jsonable(self) -> dict[str, object]:
        """转换成可写入 JSONL 的结构。

        Args:
            无。

        Returns:
            可 JSON 序列化的执行记录。

        Raises:
            无显式抛出。
        """

        return {
            "fund_name": self.fund.name,
            "fund_code": self.fund.code,
            "category": self.fund.category,
            "line_number": self.fund.line_number,
            "command": list(self.command),
            "returncode": self.returncode,
            "status": "pass" if self.returncode == 0 else "fail",
            "duration_seconds": round(self.duration_seconds, 3),
            "stdout_path": str(self.stdout_path),
            "stderr_path": str(self.stderr_path),
            "quality_gate_status": self.quality_gate_status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """解析命令行参数。

    Args:
        argv: 可选命令行参数序列；为 `None` 时读取 `sys.argv`。

    Returns:
        `argparse.Namespace` 参数对象。

    Raises:
        SystemExit: 参数不合法时由 `argparse` 抛出。
    """

    parser = argparse.ArgumentParser(description="校验并抽样运行有知有行精选基金池 smoke。")
    parser.add_argument("--csv", type=Path, default=DEFAULT_SELECTED_FUNDS_CSV, help="精选基金池 CSV 路径")
    parser.add_argument("--report-year", type=int, default=DEFAULT_REPORT_YEAR, help="年报年份")
    parser.add_argument("--sample-per-category", type=int, default=1, help="每个类别抽样数量")
    parser.add_argument("--limit", type=int, default=None, help="最多执行或打印多少只基金")
    parser.add_argument("--code", action="append", default=None, help="指定基金代码；可重复传入")
    parser.add_argument("--strict", action="store_true", help="发现重复代码等数据质量问题时返回非零退出码")
    parser.add_argument("--run", action="store_true", help="实际运行 fund-analysis analyze；默认只打印命令")
    parser.add_argument("--force-refresh", action="store_true", help="运行 CLI 时强制刷新底层数据")
    parser.add_argument("--fund-analysis-bin", default=None, help="fund-analysis 可执行文件路径")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="smoke 输出目录")
    parser.add_argument("--continue-on-fail", action="store_true", help="单只基金失败后继续执行后续样本")
    return parser.parse_args(argv)


def load_selected_funds(csv_path: Path) -> list[SelectedFund]:
    """读取精选基金池 CSV。

    Args:
        csv_path: CSV 文件路径。

    Returns:
        精选基金记录列表。

    Raises:
        FileNotFoundError: CSV 文件不存在时抛出。
        ValueError: CSV 缺少必需表头时抛出。
    """

    with csv_path.open(encoding="utf-8-sig", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        fieldnames = tuple(reader.fieldnames or ())
        missing_columns = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
        if missing_columns:
            raise ValueError(f"CSV 缺少必需列：{', '.join(missing_columns)}")
        return [
            SelectedFund(
                line_number=line_number,
                name=(row.get("基金名称") or "").strip(),
                code=(row.get("基金代码") or "").strip(),
                category=(row.get("类别") or "").strip(),
            )
            for line_number, row in enumerate(reader, start=2)
        ]


def validate_pool(funds: Sequence[SelectedFund]) -> PoolValidation:
    """校验精选基金池数据质量。

    Args:
        funds: 精选基金记录序列。

    Returns:
        数据质量校验结果。

    Raises:
        无显式抛出。
    """

    missing_rows = tuple(fund.line_number for fund in funds if not fund.name or not fund.code or not fund.category)
    bad_code_rows = tuple((fund.line_number, fund.code) for fund in funds if not _is_valid_fund_code(fund.code))
    code_counts = Counter(fund.code for fund in funds)
    duplicate_codes = tuple(sorted(code for code, count in code_counts.items() if count > 1))
    return PoolValidation(
        missing_rows=missing_rows,
        bad_code_rows=bad_code_rows,
        duplicate_codes=duplicate_codes,
    )


def select_smoke_funds(
    funds: Sequence[SelectedFund],
    *,
    codes: Sequence[str] | None,
    sample_per_category: int,
    limit: int | None,
) -> list[SelectedFund]:
    """按指定代码或类别抽样选择 smoke 基金。

    Args:
        funds: 精选基金记录序列。
        codes: 指定基金代码列表；提供时优先按代码选择。
        sample_per_category: 未指定代码时每个类别抽样数量。
        limit: 最大返回数量。

    Returns:
        待 smoke 的基金记录列表。

    Raises:
        ValueError: 指定代码不存在或抽样数量非法时抛出。
    """

    if sample_per_category < 0:
        raise ValueError("--sample-per-category 不能为负数")
    if limit is not None and limit < 0:
        raise ValueError("--limit 不能为负数")
    if codes:
        selected = _select_by_codes(funds, codes)
    else:
        selected = _select_by_category(funds, sample_per_category)
    if limit is not None:
        return selected[:limit]
    return selected


def build_analyze_command(
    fund: SelectedFund,
    *,
    report_year: int,
    fund_analysis_bin: str,
    force_refresh: bool,
) -> list[str]:
    """构造真实 CLI smoke 命令。

    Args:
        fund: 待分析基金。
        report_year: 年报年份。
        fund_analysis_bin: `fund-analysis` 可执行文件。
        force_refresh: 是否强制刷新底层数据。

    Returns:
        可直接传给 `subprocess.run` 的命令参数列表。

    Raises:
        无显式抛出。
    """

    command = [
        fund_analysis_bin,
        "analyze",
        fund.code,
        "--report-year",
        str(report_year),
        "--equity-position",
        "80%",
        "--actual-style",
        "均衡",
        "--actual-equity-position",
        "70%",
        "--manager-tenure-months",
        "24",
        "--peer-fee-median",
        "1.00%",
        "--investment-amount",
        "10000",
        "--max-tolerable-loss-rate",
        "50%",
        "--valuation-state",
        "unavailable",
        "--quality-gate-policy",
        "warn",
        "--money-horizon",
        "long_enough",
        "--user-money-horizon-years",
        "4",
        "--current-stage",
        DEFAULT_CURRENT_STAGE,
        "--final-judgment",
        "needs_attention",
    ]
    if force_refresh:
        command.append("--force-refresh")
    return command


def resolve_fund_analysis_binary(explicit_binary: str | None) -> str:
    """解析 `fund-analysis` 可执行文件路径。

    Args:
        explicit_binary: 用户显式传入的可执行文件路径。

    Returns:
        可执行文件路径字符串。

    Raises:
        无显式抛出。
    """

    if explicit_binary:
        return explicit_binary
    local_binary = Path(".venv/bin/fund-analysis")
    if local_binary.exists():
        return str(local_binary)
    return "fund-analysis"


def print_summary(funds: Sequence[SelectedFund], validation: PoolValidation) -> None:
    """打印精选基金池概览和数据质量信息。

    Args:
        funds: 精选基金记录序列。
        validation: 数据质量校验结果。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    category_counts = Counter(fund.category for fund in funds)
    unique_codes = {fund.code for fund in funds}
    print(f"records: {len(funds)}")
    print(f"unique_codes: {len(unique_codes)}")
    print("categories:")
    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count}")
    if validation.missing_rows:
        print(f"missing_rows: {', '.join(map(str, validation.missing_rows))}")
    if validation.bad_code_rows:
        rows = ", ".join(f"{line}:{code}" for line, code in validation.bad_code_rows)
        print(f"bad_code_rows: {rows}")
    if validation.duplicate_codes:
        print(f"duplicate_codes: {', '.join(validation.duplicate_codes)}")


def run_smoke_commands(
    selected_funds: Sequence[SelectedFund],
    commands: Sequence[Sequence[str]],
    *,
    output_dir: Path,
    continue_on_fail: bool,
) -> int:
    """顺序执行 smoke 命令并记录 stdout/stderr/JSONL。

    Args:
        selected_funds: 与命令一一对应的基金记录。
        commands: 命令参数序列。
        output_dir: smoke 输出目录。
        continue_on_fail: 单只基金失败后是否继续。

    Returns:
        全部成功返回 0；有失败时返回首个失败退出码。

    Raises:
        无显式抛出。
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "results.jsonl"
    summary_path = output_dir / "summary.md"
    records: list[SmokeRecord] = []
    first_failure = 0
    for fund, command in zip(selected_funds, commands, strict=True):
        stdout_path = output_dir / f"{fund.code}_{_safe_name(fund.name)}.md"
        stderr_path = output_dir / f"{fund.code}_{_safe_name(fund.name)}.stderr.txt"
        print(f"\n$ {' '.join(command)}", flush=True)
        started_at = _utc_now()
        start_time = time.perf_counter()
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        duration_seconds = time.perf_counter() - start_time
        finished_at = _utc_now()
        stdout_path.write_text(completed.stdout, encoding="utf-8")
        stderr_path.write_text(completed.stderr, encoding="utf-8")
        record = SmokeRecord(
            fund=fund,
            command=tuple(command),
            returncode=completed.returncode,
            duration_seconds=duration_seconds,
            stdout_path=stdout_path,
            stderr_path=stderr_path,
            quality_gate_status=_quality_gate_status_from_stderr(completed.stderr),
            started_at=started_at,
            finished_at=finished_at,
        )
        records.append(record)
        with jsonl_path.open("a", encoding="utf-8") as jsonl_file:
            jsonl_file.write(json.dumps(record.to_jsonable(), ensure_ascii=False) + "\n")
        print(f"  -> {'PASS' if completed.returncode == 0 else 'FAIL'} {duration_seconds:.2f}s")
        if completed.returncode != 0:
            first_failure = first_failure or completed.returncode
            if not continue_on_fail:
                break
    _write_summary(summary_path, records)
    print(f"\nsummary: {summary_path}")
    print(f"jsonl: {jsonl_path}")
    return first_failure


def main(argv: Sequence[str] | None = None) -> int:
    """执行精选基金池 smoke 辅助流程。

    Args:
        argv: 可选命令行参数序列。

    Returns:
        进程退出码。

    Raises:
        无显式抛出。
    """

    args = parse_args(argv)
    funds = load_selected_funds(args.csv)
    validation = validate_pool(funds)
    print_summary(funds, validation)
    if args.strict and validation.has_errors:
        return 1
    selected = select_smoke_funds(
        funds,
        codes=args.code,
        sample_per_category=args.sample_per_category,
        limit=args.limit,
    )
    binary = resolve_fund_analysis_binary(args.fund_analysis_bin)
    commands = [
        build_analyze_command(
            fund,
            report_year=args.report_year,
            fund_analysis_bin=binary,
            force_refresh=args.force_refresh,
        )
        for fund in selected
    ]
    print("\nplanned_commands:")
    for command in commands:
        print("  " + " ".join(command))
    if not args.run:
        return 0
    return run_smoke_commands(
        selected,
        commands,
        output_dir=args.output_dir,
        continue_on_fail=args.continue_on_fail,
    )


def _is_valid_fund_code(code: str) -> bool:
    """判断基金代码是否为 6 位数字。

    Args:
        code: 基金代码。

    Returns:
        合法返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    return len(code) == 6 and code.isdigit()


def _select_by_codes(funds: Sequence[SelectedFund], codes: Sequence[str]) -> list[SelectedFund]:
    """按指定基金代码选择记录。

    Args:
        funds: 精选基金记录序列。
        codes: 指定基金代码序列。

    Returns:
        匹配到的基金记录列表。

    Raises:
        ValueError: 任一指定代码不存在时抛出。
    """

    funds_by_code: dict[str, list[SelectedFund]] = defaultdict(list)
    for fund in funds:
        funds_by_code[fund.code].append(fund)
    missing_codes = [code for code in codes if code not in funds_by_code]
    if missing_codes:
        raise ValueError(f"指定基金代码不在精选基金池中：{', '.join(missing_codes)}")
    selected: list[SelectedFund] = []
    for code in codes:
        selected.extend(funds_by_code[code])
    return selected


def _select_by_category(funds: Sequence[SelectedFund], sample_per_category: int) -> list[SelectedFund]:
    """按类别从文件顺序中抽样选择基金。

    Args:
        funds: 精选基金记录序列。
        sample_per_category: 每个类别抽样数量。

    Returns:
        抽样基金记录列表。

    Raises:
        无显式抛出。
    """

    selected: list[SelectedFund] = []
    category_counts: Counter[str] = Counter()
    for fund in funds:
        if category_counts[fund.category] >= sample_per_category:
            continue
        selected.append(fund)
        category_counts[fund.category] += 1
    return selected


def _write_summary(summary_path: Path, records: Sequence[SmokeRecord]) -> None:
    """写入人工可读 smoke 汇总。

    Args:
        summary_path: 汇总 Markdown 路径。
        records: smoke 执行记录序列。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    passed = sum(1 for record in records if record.returncode == 0)
    failed = len(records) - passed
    lines = [
        "# Selected Funds Smoke Summary",
        "",
        f"- total: {len(records)}",
        f"- passed: {passed}",
        f"- failed: {failed}",
        "",
        "| 基金代码 | 基金名称 | 类别 | 进程状态 | Quality Gate | 耗时 | stdout | stderr |",
        "|---|---|---|---|---|---:|---|---|",
    ]
    for record in records:
        status = "PASS" if record.returncode == 0 else f"FAIL({record.returncode})"
        lines.append(
            "| "
            f"{record.fund.code} | "
            f"{record.fund.name} | "
            f"{record.fund.category} | "
            f"{status} | "
            f"{record.quality_gate_status or ''} | "
            f"{record.duration_seconds:.2f}s | "
            f"{record.stdout_path} | "
            f"{record.stderr_path} |"
        )
    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _quality_gate_status_from_stderr(stderr: str) -> str | None:
    """从 CLI stderr 文本中提取 quality gate 状态。

    Args:
        stderr: `fund-analysis analyze` stderr 文本。

    Returns:
        gate 状态文本；未找到时返回 `None`。

    Raises:
        无显式抛出。
    """

    for line in stderr.splitlines():
        if line.startswith("quality_gate_status:"):
            status = line.split(":", 1)[1].strip()
            return status or None
    return None


def _safe_name(value: str) -> str:
    """把基金名称转换为适合文件名的短文本。

    Args:
        value: 原始基金名称。

    Returns:
        文件名安全文本。

    Raises:
        无显式抛出。
    """

    return "".join(char if char.isalnum() else "_" for char in value)[:40].strip("_") or "fund"


def _utc_now() -> str:
    """返回 UTC ISO 时间戳。

    Args:
        无。

    Returns:
        UTC ISO-8601 时间戳。

    Raises:
        无显式抛出。
    """

    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    sys.exit(main())
