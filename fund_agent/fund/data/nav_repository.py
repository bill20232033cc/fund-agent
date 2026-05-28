"""基金 NAV typed repository。

本模块位于 Agent 层 Fund data 包内，负责把 source adapter 返回的中文原始
NAV rows 归一化为 `FundNavSeries` typed contract。该边界服务模板第 2 章
「R=A+B-C」和第 6 章「核心风险」的后续路径型指标，但当前 Akshare 单位净值
路径只标记为 raw_unit_nav，不能作为 strong drawdown evidence。
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Final

from fund_agent.fund.data.nav_data import FundNavDataAdapter
from fund_agent.fund.data.nav_models import (
    FundNavRecord,
    FundNavSeries,
    NavDataContractError,
    NavFailureCategory,
    NavSourceMetadata,
    ShareClassMapping,
)

_REQUIRED_DATE_COLUMN: Final[str] = "净值日期"
_REQUIRED_UNIT_NAV_COLUMN: Final[str] = "单位净值"
_OPTIONAL_GROWTH_RATE_COLUMN: Final[str] = "日增长率"
_CURRENT_NAV_TYPE: Final[str] = "unit_nav"
_CURRENT_ADJUSTED_BASIS: Final[str] = "raw_unit_nav"
_DEFAULT_SHARE_CLASS: Final[str] = "A"
_RAW_UNIT_NAV_INELIGIBILITY_REASON: Final[str] = (
    "raw_unit_nav lacks dividend adjustment or total-return basis; source-returned identity "
    "未验证，不能作为 strong drawdown evidence。"
)
_IDENTITY_CODE_KEYS: Final[tuple[str, ...]] = (
    "基金代码",
    "fund_code",
    "code",
    "source_fund_code",
    "returned_fund_code",
)
_IDENTITY_NAME_KEYS: Final[tuple[str, ...]] = (
    "基金名称",
    "fund_name",
    "name",
    "source_fund_name",
    "returned_fund_name",
)


@dataclass(frozen=True, slots=True)
class _NormalizedIdentity:
    """source-returned identity 归一化结果。"""

    returned_fund_code: str | None
    returned_fund_name: str | None


class FundNavRepository:
    """基金 NAV typed repository。

    Repository 是 future drawdown consumer 的唯一 typed 数据边界。它不直接访问
    Akshare、SQLite 或网页 helper，只通过 `FundNavDataAdapter.load_raw_nav_source`
    读取 source adapter DTO，并在本层执行 fail-closed 契约归类。
    """

    def __init__(self, source_adapter: FundNavDataAdapter | None = None) -> None:
        """初始化基金 NAV repository。

        Args:
            source_adapter: NAV source adapter；为空时使用默认 `FundNavDataAdapter`。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._source_adapter = source_adapter or FundNavDataAdapter()

    async def load_nav_series(
        self,
        fund_code: str,
        *,
        share_class: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        minimum_records: int | None = None,
        force_refresh: bool = False,
    ) -> FundNavSeries:
        """加载 typed NAV series。

        Args:
            fund_code: 请求基金代码。
            share_class: 请求份额类别；为空时按当前 fund code 默认映射到 A 类。
            start_date: 调用方要求覆盖的起始日期；为空时不检查。
            end_date: 调用方要求覆盖的结束日期；为空时不检查。
            minimum_records: 调用方要求的最少记录数；为空时不检查。
            force_refresh: 是否强制刷新 source adapter 缓存。

        Returns:
            归一化后的 `FundNavSeries`。

        Raises:
            NavDataContractError: 当 source 不可用、schema 漂移、身份冲突、完整性
                错误或显式完整性约束不满足时抛出。
        """

        normalized_fund_code = _normalize_fund_code(fund_code)
        normalized_share_class = _normalize_share_class(share_class)
        if minimum_records is not None and minimum_records < 1:
            _raise_contract_error(
                category="schema_drift",
                message="minimum_records 必须为正整数。",
                source=None,
                fund_code=normalized_fund_code,
            )
        if start_date is not None and end_date is not None and start_date > end_date:
            _raise_contract_error(
                category="missing_date_range",
                message="start_date 不得晚于 end_date。",
                source=None,
                fund_code=normalized_fund_code,
            )

        try:
            raw_source = await self._source_adapter.load_raw_nav_source(
                normalized_fund_code,
                force_refresh=force_refresh,
            )
        except NavDataContractError:
            raise
        except Exception as exc:
            raise NavDataContractError(
                category="unavailable",
                message=f"NAV source adapter 不可用: {type(exc).__name__}: {exc}",
                source="nav_source_adapter",
                fund_code=normalized_fund_code,
                cause=exc,
            ) from exc

        source_name = str(raw_source.source)
        if not raw_source.records:
            _raise_contract_error(
                category="not_found",
                message="NAV source 返回空 records。",
                source=source_name,
                fund_code=normalized_fund_code,
            )

        identity = _extract_identity(raw_source.records)
        _validate_returned_identity(
            requested_fund_code=normalized_fund_code,
            identity=identity,
            source=source_name,
        )
        source_metadata = NavSourceMetadata(
            source_name=source_name,
            origin_source=str(raw_source.origin_source),
            source_id=normalized_fund_code,
            source_url=None,
            cached=bool(raw_source.cached),
            retrieved_at=_parse_optional_datetime(raw_source.retrieved_at),
            cache_updated_at=_parse_optional_datetime(raw_source.cache_updated_at),
            requested_fund_code=normalized_fund_code,
            returned_fund_code=identity.returned_fund_code,
            returned_fund_name=identity.returned_fund_name,
            failure_category=None,
        )
        share_class_mapping = ShareClassMapping(
            requested_fund_code=normalized_fund_code,
            requested_share_class=normalized_share_class if share_class is not None else None,
            resolved_fund_code=normalized_fund_code,
            resolved_share_class=normalized_share_class,
            mapping_status="requested_code_default_a"
            if share_class is None
            else "requested_share_class_explicit",
            identity_status="requested_code_only",
            mapping_evidence=(
                f"requested fund code {normalized_fund_code} mapped to share class "
                f"{normalized_share_class}; source-returned identity not verified",
            ),
        )
        records = tuple(
            sorted(
                (
                    _normalize_raw_record(
                        raw_record=raw_record,
                        share_class=normalized_share_class,
                        source=source_name,
                        fund_code=normalized_fund_code,
                    )
                    for raw_record in raw_source.records
                ),
                key=lambda record: record.date,
            )
        )

        return FundNavSeries(
            fund_code=normalized_fund_code,
            share_class=normalized_share_class,
            records=records,
            nav_type="unit_nav",
            adjusted_basis="raw_unit_nav",
            dividend_adjustment_status="not_adjusted",
            identity_status="requested_code_only",
            completeness_status="unchecked",
            strong_drawdown_evidence_eligible=False,
            strong_drawdown_ineligibility_reason=_RAW_UNIT_NAV_INELIGIBILITY_REASON,
            source=source_metadata,
            share_class_mapping=share_class_mapping,
            date_range_start=None,
            date_range_end=None,
            record_count=len(records),
            requested_start_date=start_date,
            requested_end_date=end_date,
            minimum_records=minimum_records,
        )


def _normalize_fund_code(fund_code: str) -> str:
    """规范化基金代码。

    Args:
        fund_code: 原始基金代码。

    Returns:
        规范化后的基金代码。

    Raises:
        NavDataContractError: 基金代码为空或不是 6 位数字时抛出。
    """

    normalized = str(fund_code).strip()
    if not normalized or not normalized.isdigit() or len(normalized) != 6:
        _raise_contract_error(
            category="identity_mismatch",
            message=f"基金代码非法: {fund_code!r}",
            source=None,
            fund_code=normalized or None,
        )
    return normalized


def _normalize_share_class(share_class: str | None) -> str:
    """规范化份额类别。

    Args:
        share_class: 原始份额类别；为空时使用当前默认 A 类映射。

    Returns:
        规范化后的份额类别。

    Raises:
        NavDataContractError: 份额类别为空字符串或包含非法字符时抛出。
    """

    if share_class is None:
        return _DEFAULT_SHARE_CLASS
    normalized = share_class.strip().upper()
    if not normalized or not normalized.isalnum():
        _raise_contract_error(
            category="identity_mismatch",
            message=f"份额类别非法: {share_class!r}",
            source=None,
            fund_code=None,
        )
    return normalized


def _normalize_raw_record(
    *,
    raw_record: Mapping[str, object],
    share_class: str,
    source: str,
    fund_code: str,
) -> FundNavRecord:
    """归一化单条中文 raw NAV row。

    Args:
        raw_record: source adapter 返回的单条原始记录。
        share_class: 已解析份额类别。
        source: 数据源名称。
        fund_code: 基金代码。

    Returns:
        typed `FundNavRecord`。

    Raises:
        NavDataContractError: 字段缺失、日期非法、NAV 非法或日增长率非法时抛出。
    """

    if not isinstance(raw_record, Mapping):
        _raise_contract_error(
            category="schema_drift",
            message="NAV raw record 不是 mapping。",
            source=source,
            fund_code=fund_code,
        )
    record_date = _parse_required_date(raw_record, source=source, fund_code=fund_code)
    nav_value = _parse_required_nav_value(raw_record, source=source, fund_code=fund_code)
    raw_change_rate = _parse_optional_growth_rate(raw_record, source=source, fund_code=fund_code)
    return FundNavRecord(
        date=record_date,
        share_class=share_class,
        nav_value=nav_value,
        nav_type=_CURRENT_NAV_TYPE,
        adjusted_basis=_CURRENT_ADJUSTED_BASIS,
        raw_change_rate=raw_change_rate,
        raw_payload=raw_record,
    )


def _parse_required_date(
    raw_record: Mapping[str, object],
    *,
    source: str,
    fund_code: str,
) -> date:
    """解析必需的净值日期。

    Args:
        raw_record: 原始记录。
        source: 数据源名称。
        fund_code: 基金代码。

    Returns:
        `datetime.date` 日期。

    Raises:
        NavDataContractError: 缺少日期或日期不可解析时抛出。
    """

    raw_value = _required_column(raw_record, _REQUIRED_DATE_COLUMN, source=source, fund_code=fund_code)
    if isinstance(raw_value, datetime):
        return raw_value.date()
    if isinstance(raw_value, date):
        return raw_value
    text = str(raw_value).strip()
    if not text:
        _raise_contract_error(
            category="schema_drift",
            message="净值日期为空。",
            source=source,
            fund_code=fund_code,
        )
    try:
        return date.fromisoformat(text)
    except ValueError as exc:
        raise NavDataContractError(
            category="schema_drift",
            message=f"净值日期不可解析: {text!r}",
            source=source,
            fund_code=fund_code,
            cause=exc,
        ) from exc


def _parse_required_nav_value(
    raw_record: Mapping[str, object],
    *,
    source: str,
    fund_code: str,
) -> Decimal:
    """解析必需的单位净值。

    Args:
        raw_record: 原始记录。
        source: 数据源名称。
        fund_code: 基金代码。

    Returns:
        正数 Decimal 单位净值。

    Raises:
        NavDataContractError: 缺少、非数值或非正单位净值时抛出。
    """

    raw_value = _required_column(
        raw_record,
        _REQUIRED_UNIT_NAV_COLUMN,
        source=source,
        fund_code=fund_code,
    )
    nav_value = _parse_decimal(
        raw_value,
        category="schema_drift",
        message_prefix="单位净值",
        source=source,
        fund_code=fund_code,
    )
    if nav_value <= Decimal("0"):
        _raise_contract_error(
            category="integrity_error",
            message=f"单位净值必须为正数: {raw_value!r}",
            source=source,
            fund_code=fund_code,
        )
    return nav_value


def _parse_optional_growth_rate(
    raw_record: Mapping[str, object],
    *,
    source: str,
    fund_code: str,
) -> Decimal | None:
    """解析可选的日增长率。

    Args:
        raw_record: 原始记录。
        source: 数据源名称。
        fund_code: 基金代码。

    Returns:
        日增长率 Decimal；缺失或空值时返回 `None`。

    Raises:
        NavDataContractError: 字段存在但不可解析时抛出。
    """

    if _OPTIONAL_GROWTH_RATE_COLUMN not in raw_record:
        return None
    raw_value = raw_record[_OPTIONAL_GROWTH_RATE_COLUMN]
    if raw_value is None or str(raw_value).strip() == "":
        return None
    return _parse_decimal(
        raw_value,
        category="schema_drift",
        message_prefix="日增长率",
        source=source,
        fund_code=fund_code,
    )


def _required_column(
    raw_record: Mapping[str, object],
    column: str,
    *,
    source: str,
    fund_code: str,
) -> object:
    """读取必需 raw column。

    Args:
        raw_record: 原始记录。
        column: 必需字段名。
        source: 数据源名称。
        fund_code: 基金代码。

    Returns:
        字段值。

    Raises:
        NavDataContractError: 字段缺失或为空时抛出。
    """

    if column not in raw_record:
        _raise_contract_error(
            category="schema_drift",
            message=f"NAV raw record 缺少必需字段 {column!r}。",
            source=source,
            fund_code=fund_code,
        )
    raw_value = raw_record[column]
    if raw_value is None or str(raw_value).strip() == "":
        _raise_contract_error(
            category="schema_drift",
            message=f"NAV raw record 字段 {column!r} 为空。",
            source=source,
            fund_code=fund_code,
        )
    return raw_value


def _parse_decimal(
    raw_value: object,
    *,
    category: NavFailureCategory,
    message_prefix: str,
    source: str,
    fund_code: str,
) -> Decimal:
    """解析 Decimal 数值。

    Args:
        raw_value: 原始数值。
        category: 解析失败时使用的失败分类。
        message_prefix: 错误消息前缀。
        source: 数据源名称。
        fund_code: 基金代码。

    Returns:
        Decimal 数值。

    Raises:
        NavDataContractError: 数值不可解析时抛出。
    """

    try:
        return Decimal(str(raw_value).strip().replace("%", ""))
    except (InvalidOperation, ValueError) as exc:
        raise NavDataContractError(
            category=category,
            message=f"{message_prefix}不可解析为数值: {raw_value!r}",
            source=source,
            fund_code=fund_code,
            cause=exc,
        ) from exc


def _extract_identity(records: list[dict[str, object]]) -> _NormalizedIdentity:
    """从 raw records 中提取 source-returned identity。

    Args:
        records: source adapter 返回的原始记录。

    Returns:
        source-returned identity；当前 Akshare 路径通常为空。

    Raises:
        无显式抛出。
    """

    returned_fund_code = _first_non_empty_value(records, _IDENTITY_CODE_KEYS)
    returned_fund_name = _first_non_empty_value(records, _IDENTITY_NAME_KEYS)
    return _NormalizedIdentity(
        returned_fund_code=returned_fund_code,
        returned_fund_name=returned_fund_name,
    )


def _first_non_empty_value(records: list[dict[str, object]], keys: tuple[str, ...]) -> str | None:
    """读取 records 中第一个非空 identity 字段。

    Args:
        records: source adapter 返回的原始记录。
        keys: 候选字段名。

    Returns:
        第一个非空字段值；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    for record in records:
        for key in keys:
            value = record.get(key)
            if value is not None and str(value).strip():
                return str(value).strip()
    return None


def _validate_returned_identity(
    *,
    requested_fund_code: str,
    identity: _NormalizedIdentity,
    source: str,
) -> None:
    """验证 source-returned identity 是否与请求冲突。

    Args:
        requested_fund_code: 请求基金代码。
        identity: source-returned identity。
        source: 数据源名称。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: source 返回的基金代码与请求冲突时抛出。
    """

    if identity.returned_fund_code is None:
        return
    if identity.returned_fund_code != requested_fund_code:
        _raise_contract_error(
            category="identity_mismatch",
            message=(
                "NAV source returned fund code 与 requested fund code 不匹配: "
                f"{identity.returned_fund_code!r} != {requested_fund_code!r}。"
            ),
            source=source,
            fund_code=requested_fund_code,
        )


def _parse_optional_datetime(value: str | None) -> datetime | None:
    """解析可选 ISO datetime。

    Args:
        value: ISO datetime 字符串；为空时返回 `None`。

    Returns:
        `datetime` 或 `None`。

    Raises:
        NavDataContractError: 字符串存在但不可解析时抛出。
    """

    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError as exc:
        raise NavDataContractError(
            category="schema_drift",
            message=f"NAV source datetime 不可解析: {text!r}",
            source=None,
            fund_code=None,
            cause=exc,
        ) from exc


def _raise_contract_error(
    *,
    category: NavFailureCategory,
    message: str,
    source: str | None,
    fund_code: str | None,
) -> None:
    """抛出 NAV 数据契约错误。

    Args:
        category: 失败分类。
        message: 错误说明。
        source: 数据源名称。
        fund_code: 基金代码。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 始终抛出，用于 fail-closed。
    """

    raise NavDataContractError(
        category=category,
        message=message,
        source=source,
        fund_code=fund_code,
    )


__all__ = ["FundNavRepository"]
