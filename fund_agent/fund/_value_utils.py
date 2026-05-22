"""Fund Capability 内部结构化值工具。

本模块只服务 `fund_agent.fund` 内部，把 dict/dataclass 结构化抽取值规范化为
可读取子字段的映射；不依赖 Service、Engine、Runtime 或 UI 层。
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Mapping


def value_mapping(value: object) -> Mapping[str, object] | None:
    """把 dict 或 dataclass 结构化值规范化为只读映射。

    Args:
        value: `ExtractedField.value` 原始值，可能是 dict、dataclass 或缺失值。

    Returns:
        可按子字段读取的映射；无法映射时返回 `None`。

    Raises:
        无显式抛出。
    """

    if value is None:
        return None
    if isinstance(value, Mapping):
        return value
    if is_dataclass(value) and not isinstance(value, type):
        return asdict(value)
    return None
