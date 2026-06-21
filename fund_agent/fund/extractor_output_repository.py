"""Extractor 输出结构化 JSON 仓库。

本模块位于 Agent 层 Fund 能力包，负责把 `StructuredFundDataBundle`
显式保存为按 `fund_code + report_type + year` 组织的稳定 JSON。它不读取
年报仓库、PDF、cache、parser 原始产物、Service、Host 或 LLM。
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timezone
from decimal import Decimal
import json
from pathlib import Path
from typing import Any, Final

from fund_agent.config.paths import DEFAULT_EXTRACTOR_OUTPUT_ROOT
from fund_agent.fund.data_extractor import StructuredFundDataBundle

EXTRACTOR_OUTPUT_SCHEMA_VERSION: Final[str] = "fund-agent.extractor_output.v1"
SUPPORTED_EXTRACTOR_OUTPUT_REPORT_TYPES: Final[tuple[str, ...]] = ("annual_report",)
EXTRACTOR_OUTPUT_FILENAME: Final[str] = "structured_fund_data.json"
_FUND_CODE_LENGTH: Final[int] = 6


@dataclass(frozen=True, slots=True)
class ExtractorOutputIdentity:
    """Extractor 输出仓库记录身份。

    Attributes:
        fund_code: 6 位基金代码。
        report_type: 报告类型；v1 仅支持 `annual_report`。
        report_year: 报告年份。
    """

    fund_code: str
    report_type: str
    report_year: int


@dataclass(frozen=True, slots=True)
class ExtractorOutputRecord:
    """已保存或已加载的 extractor 输出记录。

    Attributes:
        schema_version: 输出 JSON schema 版本。
        identity: 记录身份。
        created_at: 写入时的 UTC ISO-8601 时间戳。
        bundle_payload: `StructuredFundDataBundle` 的 JSON-compatible 投影。
        path: 本地 JSON 文件路径。
    """

    schema_version: str
    identity: ExtractorOutputIdentity
    created_at: str
    bundle_payload: dict[str, object]
    path: Path


class ExtractorOutputRepository:
    """Extractor 输出结构化 JSON 仓库。

    仓库只负责显式 save/load，不给 `FundDataExtractor.extract(...)` 增加隐式副作用。
    JSON 路径固定为 `<root>/<fund_code>/<report_type>/<year>/structured_fund_data.json`。
    """

    def __init__(self, root_dir: Path = DEFAULT_EXTRACTOR_OUTPUT_ROOT) -> None:
        """初始化仓库。

        Args:
            root_dir: extractor output 仓库根目录。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.root_dir = root_dir

    def path_for(self, *, fund_code: str, report_type: str, report_year: int) -> Path:
        """返回指定身份对应的 JSON 文件路径。

        Args:
            fund_code: 6 位基金代码。
            report_type: 报告类型；v1 仅支持 `annual_report`。
            report_year: 报告年份。

        Returns:
            仓库 JSON 文件路径。

        Raises:
            ValueError: 身份字段非法时抛出。
        """

        identity = _validated_identity(
            fund_code=fund_code,
            report_type=report_type,
            report_year=report_year,
        )
        return (
            self.root_dir
            / identity.fund_code
            / identity.report_type
            / str(identity.report_year)
            / EXTRACTOR_OUTPUT_FILENAME
        )

    def save(
        self,
        *,
        bundle: StructuredFundDataBundle,
        report_type: str = "annual_report",
    ) -> ExtractorOutputRecord:
        """保存结构化基金数据包为 JSON。

        Args:
            bundle: `FundDataExtractor.extract(...)` 返回的数据包。
            report_type: 报告类型；v1 仅支持 `annual_report`。

        Returns:
            已保存记录的身份、payload 和路径。

        Raises:
            ValueError: 身份字段非法时抛出。
            TypeError: bundle 中存在不支持的 JSON 值时抛出。
            OSError: 创建目录或写文件失败时抛出。
        """

        identity = _validated_identity(
            fund_code=bundle.fund_code,
            report_type=report_type,
            report_year=bundle.report_year,
        )
        path = self.path_for(
            fund_code=identity.fund_code,
            report_type=identity.report_type,
            report_year=identity.report_year,
        )
        created_at = _utc_now()
        bundle_payload = _bundle_payload(bundle)
        payload = {
            "schema_version": EXTRACTOR_OUTPUT_SCHEMA_VERSION,
            "fund_code": identity.fund_code,
            "report_type": identity.report_type,
            "report_year": identity.report_year,
            "created_at": created_at,
            "bundle": bundle_payload,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return ExtractorOutputRecord(
            schema_version=EXTRACTOR_OUTPUT_SCHEMA_VERSION,
            identity=identity,
            created_at=created_at,
            bundle_payload=bundle_payload,
            path=path,
        )

    def load(
        self,
        *,
        fund_code: str,
        report_type: str,
        report_year: int,
    ) -> ExtractorOutputRecord:
        """加载并校验 extractor 输出 JSON。

        Args:
            fund_code: 6 位基金代码。
            report_type: 报告类型；v1 仅支持 `annual_report`。
            report_year: 报告年份。

        Returns:
            已校验的 extractor 输出记录。

        Raises:
            FileNotFoundError: JSON 文件不存在时抛出。
            ValueError: schema、身份或 bundle payload 非法时抛出。
            json.JSONDecodeError: 文件不是合法 JSON 时抛出。
        """

        expected_identity = _validated_identity(
            fund_code=fund_code,
            report_type=report_type,
            report_year=report_year,
        )
        path = self.path_for(
            fund_code=expected_identity.fund_code,
            report_type=expected_identity.report_type,
            report_year=expected_identity.report_year,
        )
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise ValueError("extractor output JSON 顶层必须是 object")
        _require_schema(payload)
        actual_identity = _identity_from_payload(payload)
        if actual_identity != expected_identity:
            raise ValueError(
                "extractor output identity mismatch: "
                f"expected={expected_identity}, actual={actual_identity}"
            )
        created_at = _required_text(payload, "created_at")
        bundle_payload = payload.get("bundle")
        if not isinstance(bundle_payload, dict):
            raise ValueError("extractor output bundle 必须是 object")
        _require_bundle_identity_matches(bundle_payload, actual_identity)
        return ExtractorOutputRecord(
            schema_version=EXTRACTOR_OUTPUT_SCHEMA_VERSION,
            identity=actual_identity,
            created_at=created_at,
            bundle_payload=dict(bundle_payload),
            path=path,
        )


def _validated_identity(
    *,
    fund_code: str,
    report_type: str,
    report_year: int,
) -> ExtractorOutputIdentity:
    """校验并返回 extractor output 身份。

    Args:
        fund_code: 基金代码。
        report_type: 报告类型。
        report_year: 报告年份。

    Returns:
        已校验身份。

    Raises:
        ValueError: 任一身份字段非法时抛出。
    """

    if len(fund_code) != _FUND_CODE_LENGTH or not fund_code.isdigit():
        raise ValueError("fund_code 必须是 6 位数字")
    if report_type not in SUPPORTED_EXTRACTOR_OUTPUT_REPORT_TYPES:
        raise ValueError("report_type 当前仅支持 annual_report")
    if report_year <= 0:
        raise ValueError("report_year 必须为正整数")
    return ExtractorOutputIdentity(
        fund_code=fund_code,
        report_type=report_type,
        report_year=report_year,
    )


def _bundle_payload(bundle: StructuredFundDataBundle) -> dict[str, object]:
    """把结构化基金数据包转换为 JSON-compatible payload。

    Args:
        bundle: 结构化基金数据包。

    Returns:
        JSON-compatible 字典。

    Raises:
        TypeError: 任一字段存在不支持的 JSON 值时抛出。
    """

    payload = {
        field.name: _jsonable(getattr(bundle, field.name), path=f"bundle.{field.name}")
        for field in fields(bundle)
    }
    return dict(payload)


def _jsonable(value: object, *, path: str) -> object:
    """把当前支持类型转换为 JSON-compatible 值。

    Args:
        value: 待转换值。
        path: 错误定位路径。

    Returns:
        JSON-compatible 值。

    Raises:
        TypeError: 遇到未知对象、非字符串 mapping key 或 bytes 时抛出。
    """

    if value is None or isinstance(value, str | int | float | bool):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes | bytearray):
        raise TypeError(f"{path} 不是支持的 JSON 值类型：{type(value).__name__}")
    if isinstance(value, Mapping):
        return _jsonable_mapping(value, path=path)
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _jsonable(getattr(value, field.name), path=f"{path}.{field.name}")
            for field in fields(value)
        }
    if isinstance(value, Sequence):
        return [
            _jsonable(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        ]
    raise TypeError(f"{path} 不是支持的 JSON 值类型：{type(value).__name__}")


def _jsonable_mapping(value: Mapping[object, object], *, path: str) -> dict[str, object]:
    """转换 mapping 并要求 key 为字符串。

    Args:
        value: 待转换 mapping。
        path: 错误定位路径。

    Returns:
        JSON-compatible 字典。

    Raises:
        TypeError: key 不是字符串或 value 不支持时抛出。
    """

    converted: dict[str, object] = {}
    for key, child in value.items():
        if not isinstance(key, str):
            raise TypeError(f"{path} 包含非字符串 JSON key：{key!r}")
        converted[key] = _jsonable(child, path=f"{path}.{key}")
    return converted


def _require_schema(payload: dict[str, Any]) -> None:
    """校验 extractor output schema 版本。

    Args:
        payload: 顶层 JSON object。

    Returns:
        无返回值。

    Raises:
        ValueError: schema 缺失或不支持时抛出。
    """

    schema_version = payload.get("schema_version")
    if schema_version != EXTRACTOR_OUTPUT_SCHEMA_VERSION:
        raise ValueError("extractor output schema_version 不受支持")


def _identity_from_payload(payload: dict[str, Any]) -> ExtractorOutputIdentity:
    """从顶层 payload 读取并校验身份。

    Args:
        payload: 顶层 JSON object。

    Returns:
        已校验身份。

    Raises:
        ValueError: 身份字段缺失或非法时抛出。
    """

    return _validated_identity(
        fund_code=_required_text(payload, "fund_code"),
        report_type=_required_text(payload, "report_type"),
        report_year=_required_int(payload, "report_year"),
    )


def _require_bundle_identity_matches(
    bundle_payload: dict[str, object],
    identity: ExtractorOutputIdentity,
) -> None:
    """校验 bundle 内部身份与顶层 extractor output 身份一致。

    Args:
        bundle_payload: 顶层 `bundle` payload。
        identity: 已校验的顶层身份。

    Returns:
        无返回值。

    Raises:
        ValueError: bundle 内部基金代码或年份与顶层身份不一致时抛出。
    """

    bundle_fund_code = bundle_payload.get("fund_code")
    bundle_report_year = bundle_payload.get("report_year")
    if bundle_fund_code != identity.fund_code or bundle_report_year != identity.report_year:
        raise ValueError(
            "extractor output bundle identity mismatch: "
            f"top_level={identity.fund_code}/{identity.report_year}, "
            f"bundle={bundle_fund_code}/{bundle_report_year}"
        )


def _required_text(payload: dict[str, Any], key: str) -> str:
    """读取必需字符串字段。

    Args:
        payload: JSON object。
        key: 字段名。

    Returns:
        字段字符串值。

    Raises:
        ValueError: 字段缺失或不是字符串时抛出。
    """

    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"extractor output `{key}` 必须是非空字符串")
    return value


def _required_int(payload: dict[str, Any], key: str) -> int:
    """读取必需整数字段。

    Args:
        payload: JSON object。
        key: 字段名。

    Returns:
        字段整数值。

    Raises:
        ValueError: 字段缺失、不是整数或是 bool 时抛出。
    """

    value = payload.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"extractor output `{key}` 必须是整数")
    return value


def _utc_now() -> str:
    """返回当前 UTC ISO-8601 时间戳。

    Args:
        无。

    Returns:
        UTC 时间戳字符串。

    Raises:
        无显式抛出。
    """

    return datetime.now(timezone.utc).isoformat()
